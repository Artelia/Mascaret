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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

TaskBLUE - A QGIS Task for running multiple Mascaret models in parallel using threads.
This module implements a QgsTask that submits multiple model runs to a thread pool,
collects results and emits signals in the original submission order.

"""
import concurrent.futures
import os
import subprocess
import time
import pprint
import shutil

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal, QObject

from .ClassBLUE import classBLUE
from .ClassMatrix import ClassMatrix

MESSAGE_CATEGORY = 'TaskBlue'


class TaskSignals(QObject):
    model_completed = pyqtSignal(int, dict)
    launch_completed = pyqtSignal(bool)


class TaskBLUE(QgsTask):
    """QGIS Task for running BLUE calculations on multiple scenarios in parallel.

    Submits scenario BLUE computations to a thread pool and collects results,
    emitting progress signals in submission order.
    """

    def __init__(self, description, base_folder, ctrl_type, scens, del_inter_assim, max_workers=None):
        """Initialize BLUE computation task for parallel scenario processing.

        :param description: Task description displayed to user.
        :param base_folder: Base directory containing scenario folders.
        :param ctrl_type: Control type ('ctrlKS' or 'ctrlLaw').
        :param scens: List of scenario identifiers to process.
        :param del_inter_assim: ``True`` to delete intermediate assimilation folders after completion.
        :param max_workers: Maximum number of concurrent worker threads. Auto-calculated if None.
        :return: None.
        """

        super().__init__(description, QgsTask.CanCancel)
        self.signal = TaskSignals()

        self.base_folder = base_folder
        self.scens = scens
        self.ctrl_type = ctrl_type
        self.del_inter_assim = del_inter_assim

        self.exc_start_time = None
        self.error_txt = ''

        # Configure thread-based parallelism
        if max_workers is None:
            max_workers = min(len(scens), (os.cpu_count() or 1))
        self.max_workers = max_workers

        # Ordered queue management
        self.running_futures = {}  # {index: future}
        self.completed_results = {}  # {index: result}
        self.next_to_process = 0  # Next index to process (in-order emission)
        self.next_to_submit = 0  # Next index to submit to executor
        self.total_models = len(scens)
        self.completed_count = 0
        self.executor = None

    def update_params(self, scens, max_workers=None):
        """Update task parameters and max_workers.

        :param scens: List of scenario identifiers to process.
        :param max_workers: Maximum number of parallel workers. Auto-calculated if None.
        :return: None
        """
        self.scens = scens
        self.total_models = len(scens)
        if max_workers is None:
            max_workers = min(len(scens), (os.cpu_count() or 1) * 2)
        self.max_workers = max_workers

    def _submit_next_model(self):
        """Submit the next scenario to the thread pool if resources available.

        :return: ``True`` if a model was submitted, ``False`` if queue is full or all submitted.
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
        """Emit results in order even if completed out-of-order.

        :return: None
        """
        while self.next_to_process in self.completed_results:
            result = self.completed_results.pop(self.next_to_process)
            # Emit the signal for the processed result (in order)
            self.signal.model_completed.emit(self.next_to_process, result)

            self.next_to_process += 1

    def run_blue(self, scen):
        """Execute BLUE calculation for scenario (thread worker).

        Computes BLUE and optionally deletes intermediate assimilation folders on success.

        :param scen: Scenario identifier to process.
        :return: Dict with scenario results: success status, output, errors, timing, and path.
        """
        path_scen = os.path.join(self.base_folder, scen)
        results = {
            'scen': scen,
            'success': False,
            'output': '',
            'error': '',
            'start_time': time.time(),
            'path_run': path_scen,
        }

        try:
            script_dir = os.path.dirname(__file__)
            os.chdir(script_dir)
            process = subprocess.run(
                ["python", "ClassBLUE.py", path_scen, self.ctrl_type],
                shell=True,
                text=True,
                check=True,
                capture_output=True
            )
            results.update({
                'success': True,
                'output': process.stdout,
                'error': process.stderr,
            })
            if self.del_inter_assim:
                target = os.path.join(path_scen, f"run_{self.ctrl_type}")
                if os.path.isdir(target):
                    try:
                        shutil.rmtree(target, ignore_errors=True)
                    except Exception:
                        # Ignore all remaining errors to prevent task crash
                        pass
        except subprocess.CalledProcessError as e:
            results['error'] = f"Process failed with exit code {e.returncode}: {e.stderr}"
        except Exception as e:
            results['error'] = f"Unexpected error: {str(e)}"

        results['execution_time'] = time.time() - results['start_time']
        pprint.pp(results)

        return results

    def run(self):
        """Execute task: manage thread pool and collect BLUE results.

        :return: ``True`` if all calculations succeeded, ``False`` on error or cancellation.
        """
        self.exc_start_time = time.time()

        # try:
        # Create the thread pool executor
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=1
        )
        self.on_message(
            f"Starting {self.total_models} models with {self.max_workers} parallel workers (threads)"
        )
        # Submit the initial workers
        for _ in range(min(self.max_workers, self.total_models)):
            # run_blue is invoked within _submit_next_model
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
            # Small sleep to avoid CPU spin
            time.sleep(0.05)
            # Ensure all results are processed
        self._process_completed_results()

        # Shutdown the pool cleanly
        self.executor.shutdown(wait=True)
        QgsMessageLog.logMessage(f"END Run {not bool(self.error_txt)} {self.error_txt}",
                                 MESSAGE_CATEGORY, Qgis.Info)
        self.signal.launch_completed.emit(not bool(self.error_txt))
        return not bool(self.error_txt)

        # except Exception as e:
        #     self.error_txt = f"Task failed: {str(e)}"
        #     self.signal.launch_completed.emit(False)
        #     return False

    def cancel(self):
        """Cancel task execution and log summary.

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
        """Handle QGIS task cancellation.

        :return: None
        """
        self.cancel()

    def on_message(self, message):
        """Log progress message.

        :param message: Message text to log.
        :type message: str
        :return: None
        """
        QgsMessageLog.logMessage(message, MESSAGE_CATEGORY, Qgis.Info)

    def on_progress(self, completed, total):
        """Log completion progress.

        :param completed: Number of completed scenarios.
        :type completed: int
        :param total: Total number of scenarios.
        :type total: int
        :return: None
        """
        percentage = (completed / total) * 100 if total > 0 else 0
        QgsMessageLog.logMessage(
            f"Progress: {completed}/{total} models ({percentage:.1f}%)",
            MESSAGE_CATEGORY,
            Qgis.Info
        )
