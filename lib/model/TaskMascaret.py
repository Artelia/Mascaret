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
from pathlib import Path
import shutil
import datetime
import traceback

from qgis.core import Qgis, QgsMessageLog, QgsTask
from qgis.PyQt.QtCore import pyqtSignal,QObject

from .ClassGetResults import ClassGetResults

MESSAGE_CATEGORY = 'TaskMascaret'

class TaskSignals(QObject):
    model_completed = pyqtSignal(int, dict)
    launch_completed = pyqtSignal(bool)

class TaskMascaret(QgsTask):


    def __init__(self, description, task_params, max_workers=None, database=None):
        """Initialize TaskMascaret.

        :param description: Description string for the QGIS task.
        :param task_params: List of dictionaries with model parameters.
        :param max_workers: Maximum number of concurrent worker threads (optional).
        """

        super().__init__(description, QgsTask.CanCancel)
        self.signal = TaskSignals()

        self.task_params = task_params
        self.mdb = database

        self.exc_start_time = None
        self.error_txt = ''

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
        future = self.executor.submit(self.run_model, params, index)
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
                            model_id = result.get('model_id', index)
                            if result['success']:
                                self.on_message(
                                    f"{result.get('output', '')}\n"
                                    f"Model {model_id} (#{index + 1}) completed in "
                                    f"{result.get('execution_time', 0):.1f}s"
                                )
                            else:
                                self.error_txt += f"\nModel {model_id} (#{index + 1}): {result['error']}"
                                self.on_message(f"Model {model_id} (#{index + 1}) failed")

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
            QgsMessageLog.logMessage(f"END Run {not bool(self.error_txt)} {self.error_txt}", MESSAGE_CATEGORY, Qgis.Info)
            self.signal.launch_completed.emit(not bool(self.error_txt))
            return not bool(self.error_txt)

        except Exception as e:
            self.error_txt = f"Task failed: {str(e)}"
            self.signal.launch_completed.emit(False)
            return False

    # def finished(self, result):
    #     """Called when task is completed.
    #
    #     :param result: True if task was successful, False otherwise.
    #     :return: None
    #     """
    #     pass
    #     # execution_time = time.time() - self.exc_start_time
    #     # if result:
    #     #     message = (
    #     #         f'  Task "{self.description}" completed successfully\n'
    #     #         f'  Models processed: {self.completed_count}/{self.total_models}\n'
    #     #         f'  Total execution time: {execution_time:.2f}s\n'
    #     #         f'  Average per model: {execution_time / max(self.completed_count, 1):.2f}s'
    #     #     )
    #     #     QgsMessageLog.logMessage(message, MESSAGE_CATEGORY, Qgis.Success)
    #     # else:
    #     #     message = (
    #     #         f'  Task "{self.description}" failed\n'
    #     #         f'{self.error_txt}\n'
    #     #         f'  Models completed: {self.completed_count}/{self.total_models}\n'
    #     #         f'  Total execution time: {execution_time:.2f}s'
    #     #     )
    #     #     QgsMessageLog.logMessage(message, MESSAGE_CATEGORY, Qgis.Critical)

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


    def create_json_param(self, folder, filname, params):
        # Create parameter input file (with index to avoid conflicts)
        param_file = os.path.join(folder,filname)
        lst_param_api = ['name','name_xcas',"RUN_REP", "BASE_NAME","has_tracer","has_casier"]
        d_json = {key : item for key, item in params.items() if key in lst_param_api}
        with open(param_file, 'w') as fp:
            json.dump(d_json, fp)
        return param_file

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



            param_file = self.create_json_param(params.get("RUN_REP"), f'model_idx{index}.json', params)

            os.chdir(os.path.join(script_dir,"..", "api"))

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
                'execution_time': time.time() - results['start_time'],
            })

            try:
                if os.path.exists(param_file):
                    os.remove(param_file)
            except OSError as e:
                results['error'] += f"\nWarning: Could not remove temp file: {e}"

            ## Check if API ran successfully
            if results['success']:
                # Verify presence of a .opt file to confirm success
                opt_exists = any(f.endswith(".opt") for f in os.listdir(params.get("RUN_REP")))
                if not opt_exists:
                    results['success'] = False
                    raise FileNotFoundError(f"Expected .opt file not found, {params.get('RUN_REP')} ")
                if "Work is done." not in results.get('output', ''):
                    results['success'] = False
                    results['error'] = results.get('output', '')
                    raise Exception(f"ClassAPIMascaret failed")
                if params.get('name') == 'init':
                    if not self._copy_lig_files(params.get("RUN_REP")):
                        results['success'] = False
                        raise Exception(f"No .lig files found #{index}")

                results_save = self._save_db(params)
                results['idrun'] = results_save['idrun']
                results['output'] = f"{results['output']}\n{results_save['output']}"
                if not  results_save['success'] and self.mdb:
                    results['success'] = False
                    raise Exception(f"Error save Results #{index} \n {results_save['error']}")
                results['save_time'] = results_save["save_time"]

        except subprocess.CalledProcessError as e:
            results['error'] = f"Process failed with exit code {e.returncode}: {e.stderr}"
            results['execution_time'] = time.time() - results['start_time']
        except Exception as e:
            results['error'] = f"Unexpected error: {str(e)}"
            results['execution_time'] = time.time() - results['start_time']

        return results

    def _copy_lig_files(self, folder):
        """
        Copy all .lig files from the current directory to parent directory.
        :folder : str, current working directory
        :return: List of paths to the copied files
        """
        current_dir = Path(folder)
        # Find all .lig files in current directory
        lig_files = list(current_dir.glob('*.lig'))

        # Check if any .lig files were found
        if not lig_files:
            return False
        # Copy all .lig files
        try:
            for source_file in lig_files:
                destination_file = current_dir.parent / source_file.name
                shutil.copy2(source_file, destination_file)
        except Exception:
            return False
        return True

    def _save_db(self, params):

        results = {
            'idrun': None,
            'success': False,
            'output': '',
            'error':'',
            'start_time': time.time(),
            'save_time' :0
        }
        name_run =  params.get("run_name")
        name_scen = params.get("scen_name")
        file_name = params.get("BASE_NAME")
        if params.get('name') == 'init':
            file_name = f"{file_name}_init"
            name_scen = f"{name_scen}_init"
        if not self.mdb:
            results = {
                'output': f'No save results {name_run} - {name_scen}',
                'save_time': time.time() - results['start_time'],
            }
            return results
        try:
            id_run = self.insert_id_run(self.mdb, name_run, name_scen)
            results.update({'id_run': id_run})


            cls_res = ClassGetResults(self.mdb, dbg=params.get("dbg", False))

            cls_res.set_results_database(
                    params.get("RUN_REP"),
                    id_run,
                    params.get("starttime"),
                    file_name,
                    comments= params.get("comments"),
                    tracer=params.get("has_tracer"),
                    casier=params.get("has_casier"),
                    cond_api=params.get("api"),
            )

            results.update({'output': cls_res.mess.message()})
            if cls_res.mess.get_critic_status():
                results.update({'save_time': time.time() - results['start_time']})
                return  results
        except Exception as err:
            results.update({'error':f'{str(err)}\n {traceback.format_exc()}',
                           'save_time': time.time() - results['start_time']})
            return results

        results.update({'success': True,
                        'save_time': time.time() - results['start_time'],
                        })
        return results

    def insert_id_run(self, mdb, run_, scen):
        """
        creation run line in runs table
        :param run_: run name
        :param scen: scenario name
        :return (id_run): run id
        """
        maintenant = datetime.datetime.now()
        tab = {run_: {"scenario": scen, "date": "{:%Y-%m-%d %H:%M}".format(maintenant)}}
        listimport = ["run", "scenario", "date"]
        mdb.insert("runs", tab, listimport)
        info = mdb.select(
            "runs", where="run='{}' AND scenario='{}'".format(run_, scen), list_var=["id"]
        )
        id_run = info["id"][0]
        return id_run
