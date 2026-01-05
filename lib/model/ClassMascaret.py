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
import os
import shutil
from time import sleep
import traceback

from click import launch
from qgis.PyQt.QtCore import qVersion,Qt
from qgis.PyQt.QtWidgets import QInputDialog, QDialog
from qgis.core import Qgis, QgsApplication, QgsMessageLog, QgsTask

from .ClassInitializeModel import ClassInitializeModel
from .ClassDictRun import ClassDictRun
from .ClassRunUIDialog import ClassRunUIDialog

from .TaskMascaret import TaskMascaret


QT_VERSION = [int(v) for v in qVersion().split('.')][0]



class ClassMascaret:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main):
        self.mgis = main
        self.dbg = main.DEBUG
        self.mdb = self.mgis.mdb
        self.iface = self.mgis.iface
        self.listeState = ["Steady", "Unsteady", "Transcritical unsteady"]
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]
        self.obj_model = ClassDictRun(self.mgis)
        self.task_init=None
        self.task_ref= None
        self.limit_core = 1
        self.max_retries = 5
        self.use_task = True

    def mascaret_ui(self):
        # state list

        case, ok = QInputDialog.getItem(None, "Study case", "Kernel", self.listeState, 0, False)
        if not ok:
            return

        kernel = self.Klist[self.listeState.index(case)]
        if self.dbg:
            self.mgis.add_info(f"Kernel {kernel}")

        dlg = ClassRunUIDialog(self.mgis, kernel, self.obj_model)
        if QT_VERSION > 5:
            result = dlg.exec()  # PyQt6
        else:
            result = dlg.exec_()  # PyQt5
        if result == QDialog.Accepted:
            self.launch_run()

    def launch_run(self):
        # creation des repertoires
        clam = ClassInitializeModel(self.mgis, self.obj_model)
        clam.main()

        drun = self.obj_model.get_drun()
        self.limit_core = self.obj_model.get_drun()['limit_core']


        # File d'attente des tasks à exécuter
        self.task_queue = []

        # Construire la séquence de tasks nécessaires
        if drun['has_run_init']:
            self.task_queue.append('init')

        self.task_queue.append('ref')  # Toujours exécuter ref ?

        if drun['has_assimilation']:
            if drun['has_run_init']:
                self.task_queue.append('ctrl_ks_init')
            self.task_queue.append('ctrl_ks_perturb')

        # # Ajouter conditionnellement la 3ème task
        # if self.should_run_third_task():  # Votre condition
        #     self.task_queue.append('third')

        # Lancer la première task de la queue
        self.process_next_task()

    def launch_init_task(self):
        print("Run Init*************")
        task_params_init = self.obj_model.get_list_type_instance('init')
        description = "Mascaret Models Execution, 'init'"

        self.task_init = TaskMascaret(
            description=description,
            task_params=task_params_init,
            max_workers=self.limit_core,
            database=self.mdb,
        )

        if not self.use_task:
            for idx, param in enumerate(task_params_init):
                results = self.task_init.run_model(param, idx)
            # Passer directement à la suivante
            self.process_next_task()
        else:
            self.task_init.taskCompleted.connect(lambda: self.on_task_completed('init'))
            self.task_init.taskTerminated.connect(lambda: self.on_task_failed('init'))

            task_id = self.launch_task(self.task_init, description)

            if not task_id:
                QgsMessageLog.logMessage("Init task failed to launch, skipping...", 'TaskMascaret', Qgis.Warning)
                self.process_next_task()

    def launch_ref_task(self):
        print('Run Ref*************')
        task_params_ref = self.obj_model.get_list_type_instance('ref')

        if not task_params_ref:
            QgsMessageLog.logMessage("No 'ref' model to run.", 'TaskMascaret', Qgis.Warning)
            # Passer à la suivante même si pas de modèle ref
            self.process_next_task()
            return

        description = "Mascaret Models Execution, 'ref'"
        self.task_ref = TaskMascaret(
            description=description,
            task_params=task_params_ref,
            max_workers=self.limit_core,
            database=self.mdb
        )

        if not self.use_task:
            for idx, param in enumerate(task_params_ref):
                results = self.task_ref.run_model(param, idx)
            self.process_next_task()
        else:

            # Connecter les signaux
            self.task_ref.taskCompleted.connect(lambda: self.on_task_completed('ref'))
            self.task_ref.taskTerminated.connect(lambda: self.on_task_failed('ref'))
            task_id = self.launch_task(self.task_ref, description)

            if not task_id:
                QgsMessageLog.logMessage("Ref task failed to launch, skipping...", 'TaskMascaret', Qgis.Warning)
                self.process_next_task()

    def launch_ctrl_ks_init_task(self):
        print('Run Assime Ctrl Ks init *************')
        task_params = self.obj_model.get_list_type_instance_assim("ctrlKS", type_init=True)

        if not task_params:
            QgsMessageLog.logMessage("No 'CtrlKs init' model to run.", 'TaskMascaret', Qgis.Warning)
            # Passer à la suivante même si pas de modèle ref
            self.process_next_task()
            return

        description = "Mascaret Models Execution, CtrlKS init'"
        self.task_ref = TaskMascaret(
            description=description,
            task_params=task_params,
            max_workers=self.limit_core,
            database=None
        )

        if not self.use_task:
            for idx, param in enumerate(task_params):
                results = self.task_ref.run_model(param, idx)
            self.process_next_task()
        else:

            # Connecter les signaux
            self.task_ref.taskCompleted.connect(lambda: self.on_task_completed('ctrlKS_init'))
            self.task_ref.taskTerminated.connect(lambda: self.on_task_failed('ctrlKS_init'))
            task_id = self.launch_task(self.task_ref, description)

            if not task_id:
                QgsMessageLog.logMessage("Ref task failed to launch, skipping...", 'TaskMascaret', Qgis.Warning)
                self.process_next_task()

    def launch_ctrl_ks_pertub_task(self):
        print('Run Assime Ctrl Ks *************')
        task_params = self.obj_model.get_list_type_instance_assim("ctrlKS")

        if not task_params:
            QgsMessageLog.logMessage("No 'CtrlKs pertub' model to run.", 'TaskMascaret', Qgis.Warning)
            # Passer à la suivante même si pas de modèle ref
            self.process_next_task()
            return

        description = "Mascaret Models Execution, CtrlKS pertub'"
        self.task_ref = TaskMascaret(
            description=description,
            task_params=task_params,
            max_workers=self.limit_core,
            database=None
        )

        if not self.use_task:
            for idx, param in enumerate(task_params):
                results = self.task_ref.run_model(param, idx)
            self.process_next_task()
        else:

            # Connecter les signaux
            self.task_ref.taskCompleted.connect(lambda: self.on_task_completed('crtlKS_pertub'))
            self.task_ref.taskTerminated.connect(lambda: self.on_task_failed('crtlKS_pertub'))
            task_id = self.launch_task(self.task_ref, description)

            if not task_id:
                QgsMessageLog.logMessage("Ref task failed to launch, skipping...", 'TaskMascaret', Qgis.Warning)
                self.process_next_task()

    def launch_task(self, task, description="Mascaret Models Execution"):
        print('Launching task...')
        task_manager = QgsApplication.taskManager()

        for attempt in range(self.max_retries):
            try:
                task_id = task_manager.addTask(task)

                if task_id == 0:
                    QgsMessageLog.logMessage(
                        f"Failed to add task (attempt {attempt + 1}/{self.max_retries})",
                        'TaskMascaret',
                        Qgis.Warning
                    )
                    continue

                sleep(0.1)
                retrieved_task = task_manager.task(task_id)

                if retrieved_task is None:
                    QgsMessageLog.logMessage(
                        f"Task not found in manager (attempt {attempt + 1}/{self.max_retries})",
                        'TaskMascaret',
                        Qgis.Warning
                    )
                    continue

                task_status = retrieved_task.status()
                if task_status in (QgsTask.Queued, QgsTask.Running):
                    QgsMessageLog.logMessage(
                        f"Task '{description}' successfully launched (ID: {task_id})",
                        'TaskMascaret',
                        Qgis.Info
                    )
                    print(f'Task launched successfully: {task_id}, Status: {task_status}')
                    return task_id  #  Retourne l'ID au lieu de True
                else:
                    QgsMessageLog.logMessage(
                        f"Task status unexpected: {task_status} (attempt {attempt + 1}/{self.max_retries})",
                        'TaskMascaret',
                        Qgis.Warning
                    )
                    continue

            except Exception as e:
                QgsMessageLog.logMessage(
                    f"Exception during task launch (attempt {attempt + 1}/{self.max_retries}): {str(e)}",
                    'TaskMascaret',
                    Qgis.Critical
                )
                traceback.print_exc()
                return None  # Retourne None en cas d'exception

        # Toutes les tentatives ont échoué
        QgsMessageLog.logMessage(
            f"Failed to launch task after {self.max_retries} attempts",
            'TaskMascaret',
            Qgis.Critical
        )
        return None  # Retourne None si toutes les tentatives échouent

    def on_task_completed(self, completed_task_id, expected_task_id, task_type):
        """Callback universel appelé quand une task se termine"""
        if completed_task_id == expected_task_id:
            # Déconnecter le handler actuel
            task_manager = QgsApplication.taskManager()
            if hasattr(self, '_current_handler'):
                try:
                    task_manager.taskCompleted.disconnect(self._current_handler)
                except:
                    pass  # Déjà déconnecté

            print(f"{task_type} task completed, processing next...")

            # Passer à la task suivante dans la queue
            self.process_next_task()


    def process_next_task(self):
        """Traite la prochaine task dans la queue"""
        if not self.task_queue:
            print("All tasks completed!")
            self.on_all_tasks_completed()
            return

        next_task_type = self.task_queue.pop(0)

        if next_task_type == 'init':
            self.launch_init_task()
        elif next_task_type == 'ref':
            self.launch_ref_task()
        elif next_task_type == 'ctrl_ks_init':
            self.launch_ctrl_ks_init_task()
        elif next_task_type == 'ctrl_ks_perturb':
            self.launch_ctrl_ks_pertub_task()
        # elif next_task_type == 'third':
        #     self.launch_third_task()

    def on_all_tasks_completed(self):
        """Appelé quand toutes les tasks sont terminées"""
        print("=== All tasks completed successfully ===")
        QgsMessageLog.logMessage(
            "All Mascaret tasks completed",
            'TaskMascaret',
            Qgis.Success
        )

    def on_task_completed(self, task_type):
        """Callback appelé quand une task se termine avec succès"""
        print(f"{task_type} task completed successfully, processing next...")
        QgsMessageLog.logMessage(
            f"Task '{task_type}' completed successfully",
            'TaskMascaret',
            Qgis.Info
        )

        # Passer à la task suivante dans la queue
        self.process_next_task()

    def on_task_failed(self, task_type):
        """Callback appelé quand une task échoue"""
        print(f"{task_type} task failed or was terminated, processing next...")
        QgsMessageLog.logMessage(
            f"Task '{task_type}' failed or terminated",
            'TaskMascaret',
            Qgis.Warning
        )

        # Continuer avec la task suivante malgré l'échec
        self.process_next_task()





