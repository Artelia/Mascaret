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

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from qgis.core import QgsTask,  QgsMessageLog, Qgis
from qgis.core import QgsApplication
import os
import subprocess
import sys
import copy
import datetime

from ..api.ClassAPIMascaret import ClassAPIMascaret
from  ..ClassMessage import ClassMessage
from .TaskMascInit import TaskMascInit
from .TaskMascComput import TaskMascComput
from .TaskMascPost import TaskMascPost


import time

MESSAGE_CATEGORY ='TaskMascaret'

class TaskMascaret(QgsTask):
    message = pyqtSignal(str)

    def __init__(self, description, dico_task):
        super().__init__(description, QgsTask.CanCancel)
        self.mdb = dico_task['mdb']
        self.wq = dico_task['wq']
        self.basename = dico_task['basename']
        self.dossier_file_masc = dico_task['dossier_file_masc']
        self.par = dico_task['par']
        self.dict_scen = dico_task['dict_scen']
        self.comments = dico_task['comments']
        self.dict_lois = dico_task['dict_lois']
        self.dico_loi_struct = dico_task['dico_loi_struct']
        self.run_ = dico_task['run']
        self.noyau = dico_task['noyau']
        self.masc = dico_task['masc']
        self.cond_api = dico_task['cond_api']
        self.comput_task  = None
        self.init_task = None
        self.post_task = None
        self.scen_cur = None

        self.exc_start_time =time.time()
        self.error_txt = ''


    def  run(self):
        self.exc_start_time = time.time()
        try :
            for idx, scen in enumerate(self.dict_scen["name"]):
                self.scen_cur = scen
                self.init_task = TaskMascInit('TaskMascInit',self.mdb, self.wq, self.dossier_file_masc,
                                              self.basename, self.par, self.noyau,
                                              scen, idx, self.dict_scen, self.dict_lois, self.dico_loi_struct)
                self.init_task.run()
                # QgsApplication.taskManager().addTask(self.init_task)
                # self.init_task.waitForFinished(0)
                if self.par["initialisationAuto"] and self.noyau != "steady":
                    txt = "========== Run initialization ========="
                    QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Info)
                    self.comput_task = TaskMascComput(' TaskMascComput_init', self.masc, self.init_task,
                                                      self.mdb, self.cond_api, self.run_, cpt_init=True)
                    self.comput_task.run()
                    # QgsApplication.taskManager().addTask(self.comput_task)
                    # self.comput_task.waitForFinished(0)

                    self.post_task = TaskMascPost('TaskMascPost_init', self.init_task, self.comput_task,
                                                  self.mdb, self.dict_scen, self.comments)
                    self.post_task.run()
                    # QgsApplication.taskManager().addTask(self.post_task)
                    # self.post_task.waitForFinished(0)

                self.comput_task = TaskMascComput(' TaskMascComput', self.masc, self.init_task,
                                                  self.mdb, self.cond_api, self.run_)
                self.comput_task.run()
                # QgsApplication.taskManager().addTask(self.comput_task)
                # self.comput_task.waitForFinished(0)
                self.post_task = TaskMascPost('TaskMascPost', self.init_task, self.comput_task,
                                              self.mdb, self.dict_scen, self.comments)
                self.post_task.run()
                # QgsApplication.taskManager().addTask(self.post_task)
                # self.post_task.waitForFinished(0)
                if self.isCanceled():
                    self.taskTerminated.emit()
                    return False
            self.taskCompleted.emit()
            return True
        except Exception as e:
            self.error_txt = str(e)
            self.taskTerminated.emit()
            return False

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        """
        exc_fin_time = time.time()
        total = exc_fin_time - self.exc_start_time
        if result:
            txt_mess = 'Task "{name}" completed\nTotal time: {total} s'.format(name=self.description, total=total)
            QgsMessageLog.logMessage(txt_mess,MESSAGE_CATEGORY, Qgis.Success)
        else:
            txt_mess = 'Task "{name}" echec\nTotal time: {total} s'.format(name=self.description, total=total)
            QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Critical)


    def cancel(self):
        exc_fin_time = time.time()
        total = exc_fin_time - self.exc_start_time
        txt_mess = 'Task "{name}" was canceled \nTask time: {total} s'.format(name=self.description, total=total)
        QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Warning)
        super().cancel()