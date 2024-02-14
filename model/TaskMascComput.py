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
import os
import subprocess
import sys
import copy
import datetime

from ..api.ClassAPIMascaret import ClassAPIMascaret
from  ..ClassMessage import ClassMessage

import time

MESSAGE_CATEGORY ='TaskMascaret'

class TaskMascComput(QgsTask):

    def __init__(self, description, cl_mas, init_task, mdb,cond_api, run_, cpt_init = False):
        super().__init__( description, QgsTask.CanCancel)
        self.cl_mas = cl_mas
        self.init_task = init_task
        self.mdb = mdb
        self.cpt_init = cpt_init
        self.cond_api =  cond_api
        self.run_ = run_


        self.id_run = None
        self.save_res_struct = None
        # precedent task
        self.par = None
        self.noyau = None
        self.scen = None
        self.dossier_file_masc = None
        self.base_name  = None
        self.mess = ClassMessage()
        # Task info
        self.exc_start_time = time.time()
        self.description = 'Computing model'


    def write_mess(self, obj):
        txt = obj.message()
        obj.clear_derror()
        return txt

    def get_param_task(self):
        # self.init_task.waitForFinished()
        # QgsMessageLog.logMessage('self.init_task.waitForFinishe {}'.format(""), MESSAGE_CATEGORY, Qgis.Info)
        self.par = self.init_task.par
        self.noyau = self.init_task.noyau
        self.scen = self.init_task.scen
        self.dossier_file_masc = self.init_task.dossier_file_masc
        self.base_name = self.init_task.basename
        QgsMessageLog.logMessage('self.scen {}'.format(self.scen), MESSAGE_CATEGORY, Qgis.Info)

    def run(self):
        self.get_param_task()
        QgsMessageLog.logMessage('self.cpt_init {}'.format(self.cpt_init), MESSAGE_CATEGORY, Qgis.Info)
        if self.cpt_init :
            sceninit = self.scen + "_init"
            self.id_run = self.insert_id_run(self.run_, sceninit)
            QgsMessageLog.logMessage('init avant lance', MESSAGE_CATEGORY, Qgis.Info)
            finish = self.lance_mascaret(self.base_name + "_init.xcas", self.id_run)
            QgsMessageLog.logMessage('finish {}'.format(finish), MESSAGE_CATEGORY, Qgis.Info)
            if not finish:
                self.mess.add_mess("ErrSim", 'Warning', "Init Simulation error")
                self.message.emit(self.write_mess(self.mess))
                self.taskTerminated.emit()
                return False

        else:
            cond_casier = False
            if self.par["presenceCasiers"] and self.noyau == "unsteady":
                cond_casier = True

            self.id_run = self.insert_id_run(self.run_, self.scen)
            QgsMessageLog.logMessage('avant lancemet', MESSAGE_CATEGORY, Qgis.Info)
            finish = self.lance_mascaret(
                self.base_name + ".xcas", self.id_run, self.par["presenceTraceurs"], cond_casier
            )
            if not finish:
                self.mess.add_mess("ErrSim", 'Warning', "Simulation error")
                self.message.emit(self.write_mess(self.mess))
                self.taskTerminated.emit()
                return False
            QgsMessageLog.logMessage('FIN lancemet', MESSAGE_CATEGORY, Qgis.Info)
        self.taskCompleted.emit()
        return True

    def lance_mascaret(self, fichier_cas, id_run, tracer=False, casier=False):
        """
        Run mascaret
        :param fichier_cas:
        :param id_run:
        :param tracer:
        :param casier:
        :return:
        """
        os.chdir(self.dossier_file_masc)
        with open("FichierCas.txt", "w") as fichier:
            fichier.write("'" + fichier_cas + "'\n")
        if not self.cond_api:
            test = sys.platform
            if "linux" in test or test == "cygwin":
                soft = "./mascaret_linux"
            elif test == "win32":
                soft = "mascaret.exe"
            else:
                txt =("{0} platform  doesn't allow to run simulation.".format(test))
                self.mess.add_mess('ErrPlatform', 'critic',  txt)
                return False

            # Linux(2.x and 3.x) ='linux2' or 'linux'
            # Windows = 'win32'
            # Windows / Cygwin = 'cygwin'

            p = subprocess.Popen(
                soft,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            p.wait()
            txt = "{0}".format(p.communicate()[0].decode("utf-8"))
            txt1 = "{0}".format(p.communicate()[1].decode("utf-8"))
            self.mess.add_mess('InfoRun', 'info', txt)
            self.mess.add_mess('InfoRun1', 'info', txt1)
            return True
        else:
            pwd = os.getcwd()
            os.chdir(self.dossier_file_masc)
            clapi = ClassAPIMascaret(self.cl_mas)
            clapi.main(fichier_cas, tracer, casier)
            self.save_res_struct = (copy.deepcopy(clapi.results_api), id_run)
            del clapi

            os.chdir(pwd)
            return True

    def insert_id_run(self, run_, scen):
        """
        creation run line in runs table
        :param run_: run name
        :param scen: scenario name
        :return:
        """
        QgsMessageLog.logMessage('run, scen {} {}'.format(run_, scen), MESSAGE_CATEGORY, Qgis.Info)
        maintenant = datetime.datetime.utcnow()
        tab = {run_: {"scenario": scen, "date": "{:%Y-%m-%d %H:%M}".format(maintenant)}}
        listimport = ["run", "scenario", "date"]
        QgsMessageLog.logMessage('maintenant {}'.format(maintenant), MESSAGE_CATEGORY, Qgis.Info)
        self.mdb.insert("runs", tab, listimport)
        info = self.mdb.select(
            "runs", where="run='{}' AND scenario='{}'".format(run_, scen), list_var=["id"]
        )

        # QgsMessageLog.logMessage("SELECT {4} FROM {0}.{1} {2} {3};".format(self.SCHEMA,"runs",
        #                          "run='{}' AND scenario='{}'".format(run_, scen), "id"), MESSAGE_CATEGORY, Qgis.Info)
        id_run = info["id"][0]
        return id_run


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
