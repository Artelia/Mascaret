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
import json
import os
import subprocess
import time
from collections import deque

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal

MESSAGE_CATEGORY = 'TaskMascaret'


class TaskMascaret(QgsTask):
    message = pyqtSignal(str)
    progress_updated = pyqtSignal(int, int)
    model_completed = pyqtSignal(int, dict)

    def __init__(self, description, task_params, max_workers=None):
        """Initialize TaskMascaret.

        :param description: Description string for the QGIS task.
        :param task_params: List of dictionaries with model parameters.
        :param max_workers: Maximum number of concurrent worker threads (optional).
        """
        super().__init__(description, QgsTask.CanCancel)
        self.task_params = task_params

        self.exc_start_time = None
        self.error_txt = ''

        # Configure thread-based parallelism
        if max_workers is None:
            max_workers = min(len(task_params), (os.cpu_count() or 1) * 2)
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
        future = self.executor.submit(self.run_model, params, index)
        self.running_futures[index] = future

        self.next_to_submit += 1

        self.message.emit(
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
            self.model_completed.emit(self.next_to_process, result)

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

            self.message.emit(
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
                            self.progress_updated.emit(self.completed_count, self.total_models)

                            # Base message
                            model_id = result.get('model_id', index)
                            if result['success']:
                                self.message.emit(
                                    f"✓ Model {model_id} (#{index + 1}) completed in "
                                    f"{result.get('execution_time', 0):.1f}s"
                                )
                            else:
                                self.error_txt += f"\nModel {model_id} (#{index + 1}): {result['error']}"
                                self.message.emit(f"✗ Model {model_id} (#{index + 1}) failed")

                            # Process results in order
                            self._process_completed_results()

                        except Exception as e:
                            self.error_txt += f"\nError processing model {index + 1}: {str(e)}"
                            self.message.emit(f"✗ Error processing model #{index + 1}")

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

            return not bool(self.error_txt)

        except Exception as e:
            self.error_txt = f"Task failed: {str(e)}"
            return False

    def finished(self, result):
        """Called when task is completed.

        :param result: True if task was successful, False otherwise.
        :return: None
        """
        execution_time = time.time() - self.exc_start_time

        if result:
            message = (
                f'✓ Task "{self.description}" completed successfully\n'
                f'  Models processed: {self.completed_count}/{self.total_models}\n'
                f'  Total execution time: {execution_time:.2f}s\n'
                f'  Average per model: {execution_time / max(self.completed_count, 1):.2f}s'
            )
            QgsMessageLog.logMessage(message, MESSAGE_CATEGORY, Qgis.Success)
        else:
            message = (
                f'✗ Task "{self.description}" failed\n'
                f'{self.error_txt}\n'
                f'  Models completed: {self.completed_count}/{self.total_models}\n'
                f'  Total execution time: {execution_time:.2f}s'
            )
            QgsMessageLog.logMessage(message, MESSAGE_CATEGORY, Qgis.Critical)

    def cancel(self):
        """Cancel the task execution and log a summary.

        :return: None
        """
        if self.exc_start_time:
            execution_time = time.time() - self.exc_start_time
            message = (
                f' Task "{self.description}" was canceled\n'
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

    def run_model(self, params, index):
        """Run a single Mascaret model instance (thread worker).

        :param params: Dictionary containing model parameters.
        :param index: Index of the model in the task list.
        :return: dict containing model results, outputs, errors and timing.
        """
        results = {
            'model_index': index,
            'success': False,
            'output': '',
            'error': '',
            'start_time': time.time(),
            'path_run': params.get("RUN_REP")
        }

        if not os.path.isdir(params.get("RUN_REP")):
            results['error'] = f"Process failed because the folder is not found: {params.get('RUN_REP')}"
            results['execution_time'] = time.time() - results['start_time']

        try:

            # Change to the script directory
            script_dir = os.path.dirname(__file__)
            os.chdir(script_dir)

            # Create parameter input file (with index to avoid conflicts)
            param_file = os.path.join(params.get("RUN_REP"), f'model_idx{index}.json')
            with open(param_file, 'w') as fp:
                json.dump(params, fp)

            os.chdir(os.path.join("..", "api"))
            process = subprocess.run(
                ["python", "ClassAPIMascaret.py", param_file],
                shell=True,
                text=True,
                check=True,
                capture_output=True
            )

            results.update({
                'success': True,
                'output': process.stdout,
                'error': process.stderr,
                'execution_time': time.time() - results['start_time']
            })

            try:
                if os.path.exists(param_file):
                    os.remove(param_file)
            except OSError as e:
                results['error'] += f"\nWarning: Could not remove temp file: {e}"

            # Check if API ran successfully
            if results['success']:
                # Verify presence of a .opt file to confirm success
                opt_exists = any(f.endswith(".opt") for f in os.listdir(params.get("RUN_REP")))
                if not opt_exists:
                    results['success'] = False
                    raise FileNotFoundError(f"Expected .opt file not found")
                if "Work is done." not in results.get('output', ''):
                    results['success'] = False
                    results['error'] = results.get('output', '')
                    raise Exception(f"ClassAPIMascaret failed")

        except subprocess.CalledProcessError as e:
            results['error'] = f"Process failed with exit code {e.returncode}: {e.stderr}"
            results['execution_time'] = time.time() - results['start_time']
        except Exception as e:
            results['error'] = f"Unexpected error: {str(e)}"
            results['execution_time'] = time.time() - results['start_time']

        # TODO: consider adding creation/copying of associated files and storage
        # if init:
        #   copy .lig files to repository...
        #   add storage
        #   perhaps pass self.mdb to the task
        return results
