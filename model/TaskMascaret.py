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

    def __init__(self, dico_task, ):
        super().__init__()
        self.description = 'TaskMascaret'
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
        self.comput_task  = None
        self.init_task = None
        self.post_task = None
        self.scen_cur = None
        print('ppppppppppppppp')


    def after_init_task(self):
        if self.par["initialisationAuto"] and self.noyau != "steady":
            txt = "========== Run initialization ========="
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Info)
            self.comput_task = TaskMascComput(self, self.init_task, self.mdb, self.cond_api, self.run_, cpt_init=True)
        else:
            self.comput_task = TaskMascComput(self, self.init_task, self.mdb, self.cond_api, self.run_)

        self.comput_task.completed.connect(self.after_cpt_task)
        self.init_task.terminate.connect(self.fct_terminate)
        QgsApplication.taskManager().addTask(self.post_task)

    def after_cpt_task(self):

        self.post_task = TaskMascPost(self.init_task, self.comput_task, self.mdb, self.dict_scen, self.comments)
        if self.comput_task.cpt_init:
            self.post_task.completed.connect(self.after_init_task)

        self.post_task.terminate.connect(self.fct_terminate)
        QgsApplication.taskManager().addTask(self.post_task)


    def fct_terminate(self):
        QgsMessageLog.logMessage('Error for the {} scenario'.format(self.scen_cur), MESSAGE_CATEGORY, Qgis.Critical)

    def  run(self):
        print('oooooooooooooooooooooo')
        for idx, scen in enumerate(self.dict_scen["name"]):
            self.scen_cur = scen
            self.init_task = TaskMascInit(self.mdb, self.wq, self.dossier_file_masc,self.basename, self.par, self.noyau,
                                     scen, idx, self.dict_scen, self.dict_lois, self.dico_loi_struct)
            QgsApplication.taskManager().addTask(self.init_task)
            self.init_task.completed.connect(self.after_init_task)
            self.init_task.terminate.connect(self.fct_terminate)
            QgsMessageLog.logMessage('fin scenario task', MESSAGE_CATEGORY, Qgis.Info)
        return  True

            # print('uuuuuuuuuuuu')
            #
            # if par["initialisationAuto"] and noyau != "steady":
            #     sceninit = scen + "_init"
            #     self.mgis.add_info("========== Run initialization =========")
            #     self.mgis.add_info("Run = {} ;  Scenario = {} ; Kernel= {}".format(run, sceninit, noyau))
            #     cpt_task_init = TaskMascComput(self, init_task, self.mdb,self.cond_api, run, cpt_init=True)
            #     self.connect_task(init_task)
            #     QgsApplication.taskManager().addTask(cpt_task_init)
            #     print('check fin calcul')
            #
            #     res_task_init = TaskMascPost(init_task, cpt_task_init, self.mdb,  dict_scen, comments)
            #     self.connect_task(res_task_init)
            #     QgsApplication.taskManager().addTask(res_task_init)
            #     res_task_init.waitForFinished()
            #     print('check post calcul')
            #
            # #
            # self.mgis.add_info("========== Run case  =========")
            # self.mgis.add_info("Run = {} ;  Scenario = {} ; Kernel= {}".format(run, scen, noyau))
            #
            # cpt_task = TaskMascComput(self, init_task, self.mdb,self.cond_api, run)
            # self.connect_task(cpt_task)
            # QgsApplication.taskManager().addTask(cpt_task)
            # res_task = TaskMascPost(init_task, cpt_task, self.mdb,  dict_scen, comments)
            # self.connect_task(res_task)
            # QgsApplication.taskManager().addTask(res_task)
            # # res_task.waitForFinished()
            # print('fin')
        print("calcul final ", time.time() -t1)