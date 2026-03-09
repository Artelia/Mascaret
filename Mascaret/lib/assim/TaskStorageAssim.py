# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
copyright            : (C) 2017 by Artelia
email                :
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

TaskMascaret - A QGIS Task for running multiple Mascaret models in parallel using threads.
This module implements a QgsTask that submits multiple model runs to a thread pool,
collects results and emits signals in the original submission order.

"""
import concurrent.futures
import os
import subprocess
import json
import time
import pprint
from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal, QObject
from .ClassStorageDB import ClassStorageDB

from .ClassCreatModelAssim import CreatModelAssim

MESSAGE_CATEGORY = 'TaskCreatFAssim'


class TaskSignals(QObject):
    model_completed = pyqtSignal(int, dict)
    launch_completed = pyqtSignal(bool)


class TaskCreatFAssim(QgsTask):
    """QGIS Task for creating assimilation folder structures for multiple scenarios in parallel.

    Submits scenario folder creation jobs to a thread pool and collects results,
    emitting progress signals in submission order.
    """

    def __init__(self, description, task_params, type_ctrl, max_workers=None, mdb =None):
        """Initialize TaskCreatFAssim for parallel assimilation folder creation.

        :param description: Description string for the QGIS task.
        :param task_params: List of scenario identifiers to process.
        :param type_ctrl: Control type ('ctrlKS' or 'ctrlLaw').
        :param max_workers: Maximum number of concurrent worker threads. Auto-calculated if None.
        :return: None.
        """

        super().__init__(description, QgsTask.CanCancel)
        self.signal = TaskSignals()
        self.task_params = task_params
        self.type_ctrl = type_ctrl

        self.exc_start_time = None
        self.error_txt = ''
        self.mdb = mdb
        # Configure thread-based parallelism
        if max_workers is None:
            max_workers = min(len(task_params), (os.cpu_count() or 1))
        self.max_workers = max_workers

        # Ordered queue management
        self.running_futures = {}  # {index: future}
        self.completed_results = {}  # {index: result}
        self.next_to_process = 0  # Next index to process (in-order emission)
        self.next_to_submit = 0  # Next index to submit to executor
        self.total_models = len(task_params)
        self.completed_count = 0
        self.executor = None

    def update_params(self, task_params, max_workers=None):
        """Update the task parameters and optionally max_workers.

        :param task_params: New list of model parameter dicts.
        :param max_workers: New maximum number of parallel workers (optional).
        :return: None
        """
        self.task_params = task_params
        self.total_models = len(task_params)
        if max_workers is None:
            max_workers = min(len(task_params), (os.cpu_count() or 1) * 2)
        self.max_workers = max_workers

    def _submit_next_model(self):
        """Submit the next model to the thread pool if possible.

        :return: True if a model was submitted, False otherwise.
        """
        if self.next_to_submit >= self.total_models:
            return False

        if len(self.running_futures) >= self.max_workers:
            return False

        index = self.next_to_submit

        params = self.task_params[index]
        # Submit the model to the thread pool
        future = self.executor.submit(self.storage_assim, params)
        self.running_futures[index] = future

        self.next_to_submit += 1

        self.on_message(
            f"Launching model (#{index + 1}/{self.total_models}) "
            f"[{len(self.running_futures)}/{self.max_workers} workers active]"
        )

        return True

    def _process_completed_results(self):
        """Process and emit results in submission order even if finished out-of-order.

        This method emits model_completed signals for consecutive results starting at self.next_to_process.
        :return: None
        """
        while self.next_to_process in self.completed_results:
            result = self.completed_results.pop(self.next_to_process)

            # Emit the signal for the processed result (in order)
            self.signal.model_completed.emit(self.next_to_process, result)

            self.next_to_process += 1

    def run(self):
        """Main task execution method - runs multiple models in parallel using threads.

        :return: True if task completed successfully, False otherwise.
        """
        self.exc_start_time = time.time()

        try:
            # Create the thread pool executor
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            )

            self.on_message(
                f"Starting {self.total_models} models with {self.max_workers} parallel workers (threads)"
            )

            # Submit the initial workers
            for _ in range(min(self.max_workers, self.total_models)):
                self._submit_next_model()

            # Main loop: process results as they complete
            while self.running_futures or self.next_to_submit < self.total_models:
                if self.isCanceled():
                    # Shutdown executor without waiting for remaining tasks
                    self.executor.shutdown(wait=False, cancel_futures=True)
                    return False

                # Check for completed futures
                done_indices = []
                for index, future in list(self.running_futures.items()):
                    if future.done():
                        done_indices.append(index)

                        try:
                            result = future.result()

                            # Store the result
                            self.completed_results[index] = result
                            self.completed_count += 1

                            # Emit progress
                            self.on_progress(self.completed_count, self.total_models)

                            # Base message

                            if result['success']:
                                self.on_message(
                                    f"{result.get('output', '')}\n"
                                    f"Creation folder completed for {result.get('scenario', '***')}."
                                    f"{result.get('execution_time', 0):.1f}s"
                                )
                            else:
                                self.error_txt += f"\nScenario {result.get('scenario', '***')}({index + 1}): {result['error']}"
                                self.on_message(f"Scenario {result.get('scenario', '***')} (#{index + 1}) failed")

                            # Process results in order
                            self._process_completed_results()

                        except Exception as e:
                            self.error_txt += f"\nError processing model {index + 1}: {str(e)}"
                            self.on_message(f"Error processing model #{index + 1}")

                # Remove completed futures and submit the next ones
                for index in done_indices:
                    del self.running_futures[index]
                    # Submit the next model if available
                    self._submit_next_model()

                # Small sleep to avoid CPU spin
                time.sleep(0.05)

            # Ensure all results are processed
            self._process_completed_results()

            # Shutdown the pool cleanly
            self.executor.shutdown(wait=True)
            QgsMessageLog.logMessage(f"END Run {not bool(self.error_txt)} {self.error_txt}", MESSAGE_CATEGORY,
                                     Qgis.Info)
            self.signal.launch_completed.emit(not bool(self.error_txt))
            return not bool(self.error_txt)

        except Exception as e:
            self.error_txt = f"Task failed: {str(e)}"
            self.signal.launch_completed.emit(False)
            return False

    def cancel(self):
        """Cancel the task execution and log a summary.

        :return: None
        """
        if self.exc_start_time:
            execution_time = time.time() - self.exc_start_time
            message = (
                f'  Task "{self.description}" was canceled\n'
                f'  Execution time: {execution_time:.2f}s\n'
                f'  Models completed: {self.completed_count}/{self.total_models}'
            )
            QgsMessageLog.logMessage(message, MESSAGE_CATEGORY, Qgis.Warning)
        super().cancel()

    def onCancel(self):
        """Handler called by QGIS when the task is cancelled.

        :return: None
        """
        self.cancel()

    def on_message(self, message):
        """Callback for progress messages.

        :param message: Message text emitted by the task.
        :type message: str
        :return: None
        """
        QgsMessageLog.logMessage(message, MESSAGE_CATEGORY, Qgis.Info)

    def on_progress(self, completed, total):
        """Callback for progress updates.

        :param completed: Number of completed models.
        :type completed: int
        :param total: Total number of models.
        :type total: int
        :return: None
        """
        percentage = (completed / total) * 100 if total > 0 else 0
        QgsMessageLog.logMessage(
            f"Progress: {completed}/{total} models ({percentage:.1f}%)",
            MESSAGE_CATEGORY,
            Qgis.Info
        )

    def get_idrun(self, run_, scen):
        info = self.mdb.select(
            "runs", where="run='{}' AND scenario='{}'".format(run_, scen), list_var=["id"]
        )
        if info.get("id"):
            return info["id"][0]
        return None

    def storage_assim(self, param):
        """
        :param scen: Scenario identifier to process.
        :return: Dict containing creation results including success status, output, errors, and timing.
        """
        scen = param.get("scen_name")
        run =  param.get("run_name")
        # path_scen = os.path.join(self.base_folder, scen)
        # results = {
        #     'scenario': scen,
        #     'success': False,
        #     'output': '',
        #     'error': '',
        #     'start_time': time.time(),
        #     'path_run': path_scen
        # }
        #
        # id_run = self.get_idrun(run_, scen)
        # if not id_run:
        #     results['error'] = f"No run found: {run_},{scen}"
        #
        # if not os.path.isdir(path_scen):
        #     results['error'] = f"Process failed because the folder is not found: {path_scen}"
        #     results['execution_time'] = time.time() - results['start_time']
        #
        #
        # cls_storage = ClassStorageDB(self.mdb, id_run, path_scen, scen, self.type_ctrl)
        # cls_storage.storage_results()
        #


        results['execution_time'] = time.time() - results['start_time']
        pprint.pp(results)


        return results
