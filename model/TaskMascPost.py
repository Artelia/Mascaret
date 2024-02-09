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
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsTask, QgsMessageLog, Qgis

from ..ClassMessage import ClassMessage

from .ClassGetResults import ClassGetResults
from .ClassCreatFilesModels import ClassCreatFilesModels
import time

MESSAGE_CATEGORY ='TaskMascPost'

class TaskMascPost(QgsTask):
    message = pyqtSignal(str)

    def __init__(self,init_task, comput_task, mdb, dict_scen,  comments):
        super().__init__()
        self.comput_task = comput_task
        self.init_task = init_task
        self.mdb = mdb
        self.comments = comments

        self.dict_scen = dict_scen

        self.dossier_file_masc = None
        self.mess = ClassMessage()


        # Task info
        self.exc_start_time = time.time()
        self.description = 'Computing model'

    def write_mess(self, obj):
        txt = obj.message()
        obj.clear_derror()
        return txt

    def get_precedent_task(self):
        self.init_task.waitForFinished()
        self.comput_task.waitForFinished()

        self.par = self.init_task.par
        self.noyau = self.init_task.noyau
        self.scen = self.init_task.scen
        self.dossier_file_masc = self.init_task.dossier_file_masc
        self.basename = self.init_task.basename
        self.date_debut = self.init_task.date_debut

        self.cpt_init = self.comput_task.cpt_init
        self.id_run = self.comput_task.id_run
        self.cond_api = self.comput_task.cond_api
        self.save_res_struct = self.comput_task.save_res_struct

        self.cls_res = ClassGetResults(self.mdb, self.dossier_file_masc)
        self.clfile = ClassCreatFilesModels(self.mdb, self.dossier_file_masc)

    def exit_status_(self,obj):
        exit_status = obj.get_critic_status()
        if exit_status:
            self.message.emit(self.write_mess(obj))
            self.taskTerminated.emit()
        return exit_status

    def run(self):

        self.get_precedent_task()
        # RUN Model
        if self.cpt_init:
            self.cls_res.lit_opt_new(self.id_run, None, self.basename + "_init", self.comments,
                                     cond_api=self.cond_api, save_res_struct = self.save_res_struct)
            if self.exit_status_(self.cls_res.mess):
                return
            self.clfile.opt_to_lig(self.id_run, self.basename)
            if self.exit_status_(self.clfile.mess):
                return
            tab = {
                "LigEauInit": {
                    "valeur": "true",
                    "balise1": "parametresConditionsInitiales",
                    "balise2": "ligneEau",
                }
            }
            self.clfile.modif_xcas(tab, self.basename + ".xcas")
        else:
            cond_casier = False
            if self.par["presenceCasiers"] and  self.noyau == "unsteady":
                cond_casier = True
            self.cls_res.lit_opt_new(
                self.id_run, self.date_debut, self.basename, self.comments,
                self.par["presenceTraceurs"], cond_casier,
                self.cond_api, self.save_res_struct)
            if self.exit_status_(self.cls_res.mess):
                return

            if self.check_mobil_gate():
                self.cls_res.read_mobil_gate_res(self.id_run)
                if self.exit_status_(self.cls_res.mess):
                    return
        self.taskCompleted.emit()

    def check_mobil_gate(self):
        """
        check if weirs active
        :return:
        """
        info = self.mdb.select(
            "weirs", where="active_mob = true", list_var=["method_mob", "gid", "name"]
        )
        if info:
            if len(info["gid"]) > 0:
                return True

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
