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

"""
from qgis.core import Qgis, QgsApplication, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox

from .TaskMascaret3 import TaskMascaret


class MascaretRunner:
    """Class to manage execution of Mascaret tasks.

    A thin wrapper that builds a TaskMascaret, submits it to the QGIS
    task manager and exposes callbacks for messages, progress and per-model completion.
    """

    def __init__(self):
        self.task = None

    def run_mascaret_models(self, task_params, max_workers=None, description="Mascaret Models Execution"):
        """Launch execution of multiple Mascaret models in parallel.

        :param task_params: List of dictionaries containing parameters for each model.
        :type task_params: list
        :param max_workers: Maximum number of parallel workers (None = auto).
        :type max_workers: int or None
        :param description: Description for the QGIS Task.
        :type description: str
        :return: True if the task was created/submitted, False otherwise.
        :rtype: bool

        Example of task_params:
            [
                [{'BASE_NAME': 'mascaret',
                  'RUN_REP': 'Mascaret\\mascaret\\Crue2001_1\\run_init',
                  'has_casier': False,
                  'has_tracer': False,
                  'name': 'init'}, ....],
                ...
            ]
        """
        print('iiiiiiiiiiiii', task_params)
        if not task_params:
            QgsMessageLog.logMessage(
                "No models to run!",
                'TaskMascaret',
                Qgis.Warning
            )
            return False

        # Create the task
        self.task = TaskMascaret(
            description=description,
            task_params=task_params,
            max_workers=max_workers
        )

        # Connect signals to follow progress
        self.task.message.connect(self.on_message)
        self.task.progress_updated.connect(self.on_progress)
        self.task.model_completed.connect(self.on_model_completed)
        use_task = True
        if not use_task:
            for idx, param in enumerate(task_params):
                results = self.task.run_model(param,idx)
                from pprint import pprint
                pprint(results )
        else:
            # Add the task to the QGIS task manager
            task_manager = QgsApplication.taskManager()
            task_id = task_manager.addTask(self.task)
            task_manager.task(task_id)
            QgsMessageLog.logMessage(
                f"Task '{description}' added to task manager with {len(task_params)} models",
                'TaskMascaret',
                Qgis.Info
            )
            print('Send Task', task_id )

        return True

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

    def on_model_completed(self, index, result):
        """Callback invoked when a model finishes (in submission order).

        :param index: Index of the model.
        :type index: int
        :param result: Result dictionary for the model.
        :type result: dict
        :return: None
        """
        if result['success']:
            QgsMessageLog.logMessage(
                f"Model #{index + 1} (ID: {result.get('model_id', index)}) completed successfully",
                'TaskMascaret',
                Qgis.Success
            )

        else:
            QgsMessageLog.logMessage(
                f"Model #{index + 1} (ID: {result.get('model_id', index)}) failed: {result.get('error')}",
                'TaskMascaret',
                Qgis.Critical
            )

