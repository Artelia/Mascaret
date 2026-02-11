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
import json
import os
import subprocess
import time
import pprint

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal,QObject

from .ClassBLUE import classBLUE
from .ClassMatrix import ClassMatrix

MESSAGE_CATEGORY = 'TaskBlue'

class TaskSignals(QObject):
    model_completed = pyqtSignal(int, dict)
    launch_completed = pyqtSignal(bool)

class TaskBLUE(QgsTask):
    def __init__(self, description, base_folder):
        try:
            super().__init__(description, QgsTask.CanCancel)

            self.base_folder = base_folder
            self.executor = None
            self.error_txt = ''
            self.signal = TaskSignals()
            self.total_models = 0
            self.next_to_submit = 0
            self.scens = []
            self.max_workers = 1
            self.running_futures = {}
        except Exception as e:
            print(e)
            raise ValueError(e)


    def update_params(self, scens):
        """Update the task parameters and optionally max_workers.

        :param task_params: New list of model parameter dicts.
        :param max_workers: New maximum number of parallel workers (optional).
        :return: None
        """
        # self.task_params = task_params
        self.scens = scens
        self.total_models = len(self.scens)
        # if max_workers is None:
        #     max_workers = min(len(task_params), (os.cpu_count() or 1) * 2)
        # self.max_workers = max_workers

    def _submit_next_model(self):
        """Submit the next model to the thread pool if possible.

        :return: True if a model was submitted, False otherwise.
        """
        if self.next_to_submit >= self.total_models:
            return False

        if len(self.running_futures) >= self.max_workers:
            return False

        index = self.next_to_submit
        scen = self.scens[index]

        # Submit the model to the thread pool
        future = self.executor.submit(self.run_blue, scen)
        self.running_futures[index] = future

        self.next_to_submit += 1

        self.on_message(
            f"Calculating blue for scenario (#{index + 1}/{self.total_models}) "
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

    def run_blue(self, scen):
        # M = ClassMatrix(self.base_folder)
        # M.build_all_matrix()
        print('in_run_blue')
        path_scen = os.path.join(self.base_folder, scen)
        results = {
            'scen': scen,
            'success': False,
            'output': '',
            'error': '',
            'start_time': time.time(),
            'path_run': path_scen,
        }
        print('in run_blue', results)
        print(path_scen)
        try:
            script_dir = os.path.dirname(__file__)
            os.chdir(os.path.join(script_dir,"..", "assim"))

            process = subprocess.run(
                ["python", "ClassBLUE.py", path_scen],
                shell=True,
                text=True,
                check=True,
                capture_output=True
            )
            # print(process.stdout, 'uuu')
            results.update({
                'success': True,
                'output': process.stdout,
                'error': process.stderr,
                'execution_time': time.time() - results['start_time'],
            })
            # try:
            #     Blue = classBLUE(os.path.join(self.base_folder, scen))
            # except Exception as e:
            #     results['error'] += e
            # Blue.compute_BLUE()
            # Blue.store_results()
            # results['success'] = True
            pprint.pp(results)

        except subprocess.CalledProcessError as e:
            results['error'] = f"Process failed with exit code {e.returncode}: {e.stderr}"
            results['execution_time'] = time.time() - results['start_time']
        except Exception as e:
            results['error'] = f"Unexpected error: {str(e)}"
            results['execution_time'] = time.time() - results['start_time']

        pprint.pp(results)

        return results
        # pass

    def run(self):
        try:
            # Create the thread pool executor
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=1
            )
            self.on_message(
                f"Starting BLUE calculation for assimilation"
            )
            # Submit the initial workers
            for _ in range(min(self.max_workers, self.total_models)):
                # Dans submit_next_model est fait le run_blue
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
                            print(result)

                            # Store the result
                            self.completed_results[index] = result
                            self.completed_count += 1

                            # Emit progress
                            self.on_progress(self.completed_count, self.total_models)

                            # Base message
                            # model_id = result.get('model_id', index)
                            if result['success']:
                                self.on_message(
                                    f"Scenario {result['scen']} :\n"
                                    "Blue calculation done in "
                                    f"{result.get('execution_time', 0):.1f}s"
                                )
                            else:
                                self.error_txt += f"\nProblem with blue calculation: {result['error']}"
                                self.on_message(f"Problem with blue calculation:")

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

                # Ensure all results are processed
                self._process_completed_results()

                # Shutdown the pool cleanly
                self.executor.shutdown(wait=True)
                QgsMessageLog.logMessage(f"END Run {not bool(self.error_txt)} {self.error_txt}",
                                         MESSAGE_CATEGORY, Qgis.Info)
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
        QgsMessageLog.logMessage(message, 'TaskMascaret', Qgis.Info)

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
            'TaskMascaret',
            Qgis.Info
        )
