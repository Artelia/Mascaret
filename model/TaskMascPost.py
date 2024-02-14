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

MESSAGE_CATEGORY ='TaskMascaret'

class TaskMascPost():
    """Task of postprocessing model"""

    def __init__(self,glb_param):
        super().__init__( )

        self.mdb = glb_param['mdb']
        self.comments = glb_param['comments']
        self.dict_scen = glb_param['dict_scen']
        self.dossier_file_masc = glb_param['dossier_file_masc']
        self.noyau = glb_param['noyau']
        self.dossier_file_masc =  glb_param['dossier_file_masc']
        self.basename =  glb_param['basename']
        self.cond_api = glb_param['cond_api']

        self.cls_res = ClassGetResults(self.mdb, self.dossier_file_masc)
        self.clfile = ClassCreatFilesModels(self.mdb, self.dossier_file_masc)

        self.mess = ClassMessage()
        self.cpt_init = False

        # Task info
        self.exc_start_time = time.time()
        self.description = 'postprocessing model'


    def update_inputs(self,up_dict,  cpt_init = False):
        """
        Updating class parameters
        :param  up_dict: (dict) new parameters
        :param cpt_init : (boolean) if inialisation phase or not
        """
        self.par = up_dict['par']
        self.scen = up_dict['scen']
        self.cpt_init = cpt_init
        self.date_debut = up_dict['date_debut']
        self.id_run = up_dict['id_run']
        self.save_res_struct = up_dict['save_res_struct']

    def maj_param(self, up_dict):
        """"
        Updating the information transfer dictionary
        :param  up_dict: (dict) transfer dictionary
        :return: (dict)
        """
        return  up_dict

    def exit_status_(self,obj):
        exit_status = obj.get_critic_status()
        return exit_status

    def run(self):
        # RUN Model
        if self.cpt_init:

            QgsMessageLog.logMessage('read opt', MESSAGE_CATEGORY, Qgis.Info)
            self.cls_res.lit_opt_new(self.id_run, None, self.basename + "_init", self.comments,
                                     cond_api=self.cond_api, save_res_struct = self.save_res_struct)
            if self.exit_status_(self.cls_res.mess):
                return False
            QgsMessageLog.logMessage('gener lig', MESSAGE_CATEGORY, Qgis.Info)
            self.clfile.opt_to_lig(self.id_run, self.basename)
            if self.exit_status_(self.clfile.mess):
                return False
            tab = {
                "LigEauInit": {
                    "valeur": "true",
                    "balise1": "parametresConditionsInitiales",
                    "balise2": "ligneEau",
                }
            }
            self.clfile.modif_xcas(tab, self.basename + ".xcas")
            QgsMessageLog.logMessage('OK', MESSAGE_CATEGORY, Qgis.Info)
        else:
            cond_casier = False
            if self.par["presenceCasiers"] and  self.noyau == "unsteady":
                cond_casier = True
            self.cls_res.lit_opt_new(
                self.id_run, self.date_debut, self.basename, self.comments,
                self.par["presenceTraceurs"], cond_casier,
                self.cond_api, self.save_res_struct)
            QgsMessageLog.logMessage('read lit', MESSAGE_CATEGORY, Qgis.Info)
            if self.exit_status_(self.cls_res.mess):
                return False
            QgsMessageLog.logMessage('check_mobil_gate', MESSAGE_CATEGORY, Qgis.Info)
            if self.check_mobil_gate():
                self.cls_res.read_mobil_gate_res(self.id_run)
                if self.exit_status_(self.cls_res.mess):
                    return False
        return True

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

    # def finished(self, result):
    #     """
    #     This function is automatically called when the task has
    #     completed (successfully or not).
    #     """
    #     exc_fin_time = time.time()
    #     total = exc_fin_time - self.exc_start_time
    #     if result:
    #         txt_mess = 'Task "{name}" completed\nTotal time: {total} s'.format(name=self.description, total=total)
    #         QgsMessageLog.logMessage(txt_mess,MESSAGE_CATEGORY, Qgis.Success)
    #     else:
    #         txt_mess = 'Task "{name}" echec\nTotal time: {total} s'.format(name=self.description, total=total)
    #         QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Critical)
    #
    # def cancel(self):
    #     exc_fin_time = time.time()
    #     total = exc_fin_time - self.exc_start_time
    #     txt_mess = 'Task "{name}" was canceled \nTask time: {total} s'.format(name=self.description, total=total)
    #     QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Warning)
    #     super().cancel()
