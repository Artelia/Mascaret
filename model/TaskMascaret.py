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

import time
import traceback

from PyQt5.QtCore import QObject, pyqtSignal
from qgis.core import QgsTask, QgsMessageLog, Qgis

from .TaskMascComput import TaskMascComput
from .TaskMascInit import TaskMascInit
from .TaskMascPost import TaskMascPost

MESSAGE_CATEGORY = "TaskMascaret"


class TaskSignals(QObject):
    message = pyqtSignal(str)


class TaskMascaret(QgsTask):

    def __init__(self, description, dico_task):
        super().__init__(description, QgsTask.CanCancel)
        self.signal = TaskSignals()
        self.dbg = dico_task["dbg"]
        self.mdb = dico_task["mdb"]
        self.wq = dico_task["wq"]
        self.basename = dico_task["basename"]
        self.dossier_file_masc = dico_task["dossier_file_masc"]
        self.par = dico_task["par"]
        self.dict_scen = dico_task["dict_scen"]
        self.comments = dico_task["comments"]
        self.dict_lois = dico_task["dict_lois"]
        self.dico_loi_struct = dico_task["dico_loi_struct"]
        self.run_ = dico_task["run"]
        self.noyau = dico_task["noyau"]
        self.masc = dico_task["masc"]
        self.cond_api = dico_task["cond_api"]
        self.comput_task = None
        self.init_task = None
        self.post_task = None
        self.scen_cur = None
        self.description = description

        self.exc_start_time = time.time()
        self.error_txt = ""

    def run_task(self, task, up_param, cpt_init=None):
        """
        Run Task Mascaret
        Args:
             :param task : (object) task object
             :param up_param : (dict) parameter
             :param  cpt_init : (boolean) If initialization , default None
        """
        if cpt_init:
            task.update_inputs(up_param, cpt_init)
        else:
            task.update_inputs(up_param)
        completed_status = task.run()
        up_param = task.maj_param(up_param)
        self.signal.message.emit(task.mess.message())
        return completed_status, up_param

    def log_mess(self, txt, typ="info"):
        """Manage message
        :param txt : (str) text
        :param typ :(str) message typ
        """
        self.signal.message.emit(txt)
        if typ == "warning":
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Warning)
        elif typ == "critic":
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Critical)
        else:
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Info)

    def run(self):
        """Run Task
        :return boolean
        """
        self.exc_start_time = time.time()
        try:
            gbl_param = {
                "dbg": self.dbg,
                "mdb": self.mdb,
                "dossier_file_masc": self.dossier_file_masc,
                "basename": self.basename,
                "noyau": self.noyau,
                "run": self.run_,
                "comments": self.comments,
                "dict_scen": self.dict_scen,
                "cond_api": self.cond_api,
                "masc": self.masc,
                "waterq": self.wq,
            }
            param_init = {"dict_lois": self.dict_lois, "dico_loi_struct": self.dico_loi_struct}
            self.init_task = TaskMascInit(gbl_param, param_init)
            self.post_task = TaskMascPost(gbl_param)

            self.log_mess("===== BEGIN OF RUN {} =====".format(self.run_))
            for idx, scen in enumerate(self.dict_scen["name"]):
                t0_run = time.time()
                self.init_task.mess.clear_derror()
                self.post_task.mess.clear_derror()
                self.log_mess("************** The current scenario is {} ************".format(scen))
                self.log_mess(
                    "Kernel - Run - scenario : {} - {} - {} ".format(self.noyau, self.run_, scen)
                )
                self.scen_cur = scen
                up_param = {
                    "scen": scen,
                    "idx": idx,
                    "par": self.par,
                    "id_run": None,
                    "save_res_struct": None,
                    "date_debut": None,
                }
                stat, up_param = self.run_task(self.init_task, up_param)
                if not stat:
                    # error ignor scenario
                    self.log_mess(
                        "****** Error : File creation for {}  ******".format(scen), "warning"
                    )
                    continue

                if self.par["initialisationAuto"] and self.noyau != "steady":
                    self.log_mess("===== Run initialization =====")
                    self.comput_task = TaskMascComput(gbl_param)
                    stat, up_param = self.run_task(self.comput_task, up_param, cpt_init=True)
                    if not stat:
                        # error ignor scenario
                        self.log_mess(
                            "****** Error : Computing Initialization  for {}_init  ******".format(
                                scen
                            ),
                            "warning",
                        )
                        continue
                    stat, up_param = self.run_task(self.post_task, up_param, cpt_init=True)
                    if not stat:
                        self.log_mess(
                            "****** Error : Postprocessing Initialization for {}_init  ******".format(
                                scen
                            ),
                            "warning",
                        )
                        continue
                    self.comput_task.mess.clear_derror()
                    tfin_run = time.time()
                    self.log_mess("Initialization Execution time : {} s".format(tfin_run - t0_run))
                    time.sleep(1)
                    self.log_mess("===== End initialization =====")

                    if self.isCanceled():
                        self.log_mess("===== CANCEL RUN {} =====".format(self.run_), "warning")
                        time.sleep(1)
                        self.taskTerminated.emit()
                        return False
                    self.comput_task = TaskMascComput(gbl_param)
                    stat, up_param = self.run_task(self.comput_task, up_param)
                    self.comput_task.mess.clear_derror()
                    if not stat:
                        self.log_mess(
                            "****** Error : Computing for {}  ******".format(scen), "warning"
                        )
                        continue
                    stat, up_param = self.run_task(self.post_task, up_param)
                    if not stat:
                        self.log_mess(
                            "****** Error : Postprocessing for {}  ******".format(scen), "warning"
                        )
                        continue
                    tfin_run = time.time()
                    self.log_mess("Execution time (Init + Run) : {} s".format(tfin_run - t0_run))
                    self.log_mess("************** The End of {} ************".format(scen))
                    if self.isCanceled():
                        self.log_mess("===== CANCEL RUN {} =====".format(self.run_), "warning")
                        time.sleep(1)
                        self.taskTerminated.emit()
                        return False
                tfin_run = time.time()
                self.log_mess(
                    "Execution time (all Run) : {} s".format(tfin_run - self.exc_start_time)
                )
                self.log_mess("===== END OF RUN {} =====".format(self.run_))
                time.sleep(1)
                self.taskCompleted.emit()
                return True
        except Exception as e:
            self.error_txt = str(e)
            if self.dbg:
                error_info = traceback.format_exc()
                self.error_txt = self.error_txt + "\n" + error_info
            self.log_mess(str(e), "critic")
            time.sleep(1)
            self.taskTerminated.emit()
            return False

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        Args:
            :param result :(boolean) result
        """
        exc_fin_time = time.time()
        total = exc_fin_time - self.exc_start_time
        if result:
            txt_mess = 'Task "{name}" completed\nTotal time: {total} s'.format(
                name=self.description, total=total
            )
            QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Success)
        else:
            txt_mess = self.error_txt + "\n"
            txt_mess += 'Task "{name}" echec\nTotal time: {total} s'.format(
                name=self.description, total=total
            )
            QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Critical)

    def cancel(self):
        """
        Cancel task
        """
        exc_fin_time = time.time()
        total = exc_fin_time - self.exc_start_time
        txt_mess = 'Task "{name}" was canceled \nTask time: {total} s'.format(
            name=self.description, total=total
        )
        QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Warning)
        super().cancel()

    def onCancel(self):
        """
        Cancel task
        """
        self.cancel()
