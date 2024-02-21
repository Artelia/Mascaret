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

from qgis.core import QgsMessageLog, Qgis

from .ClassCreatFilesModels import ClassCreatFilesModels
from .ClassGetResults import ClassGetResults
from ..ClassMessage import ClassMessage

MESSAGE_CATEGORY = 'TaskMascaret'


class TaskMascPost():
    """Task of postprocessing model"""

    def __init__(self, glb_param):
        super().__init__()

        self.mdb = glb_param['mdb']
        self.comments = glb_param['comments']
        self.dict_scen = glb_param['dict_scen']
        self.dossier_file_masc = glb_param['dossier_file_masc']
        self.noyau = glb_param['noyau']
        self.dossier_file_masc = glb_param['dossier_file_masc']
        self.basename = glb_param['basename']
        self.cond_api = glb_param['cond_api']

        self.cls_res = ClassGetResults(self.mdb, self.dossier_file_masc)
        self.clfile = ClassCreatFilesModels(self.mdb, self.dossier_file_masc)

        self.mess = ClassMessage()
        self.cpt_init = False

        # Task info
        self.exc_start_time = time.time()
        self.description = 'postprocessing model'

    def log_mess(self, txt, flag, typ='info'):
        """Manage message
        Args:
            :param txt : (str) text
            :param flag : (str) error flag
            :param typ :(str) message typ
        """
        self.mess.add_mess(flag, typ, txt)
        if typ == 'warning':
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Warning)
        elif typ == 'critic':
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Critical)
        else:
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Info)

    def add_log_mess(self, obj):
        """
        Add log message to classMessage object
        Args:
            :param obj : (object) ClassMessage
        """
        fill_d = self.mess.mess_fill_other_obj(obj)
        if fill_d:
            for key, item in fill_d.items():
                if item['type'] == 'warning':
                    QgsMessageLog.logMessage(item['message'], MESSAGE_CATEGORY, Qgis.Warning)
                elif item['type'] == 'critic':
                    QgsMessageLog.logMessage(item['message'], MESSAGE_CATEGORY, Qgis.Critical)
                else:
                    QgsMessageLog.logMessage(item['message'], MESSAGE_CATEGORY, Qgis.Info)

    def update_inputs(self, up_dict, cpt_init=False):
        """
        Updating class parameters
        Args:
            :param  up_dict: (dict) new parameters
            :param cpt_init : (boolean) if inialization phase or not
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
        Args:
            :param  up_dict: (dict) transfer dictionary
        Return:
            :return: (dict)
        """
        return up_dict

    def exit_status_(self, obj):
        """ if exist status
        Args:
            :param obj :(object)  message class
        Return:
            :return : boolean"""
        exit_status = obj.get_critic_status()
        return exit_status

    def run(self):
        """ Run post
        Return:
            :return boolean
        """
        # RUN Model
        try:
            self.log_mess('TaskMascPost Begin', 'info1')
            if self.cpt_init:

                self.log_mess('Read *_init.opt file', 'info3')
                self.cls_res.lit_opt_new(self.id_run, None, self.basename + "_init", self.comments,
                                         cond_api=self.cond_api, save_res_struct=self.save_res_struct)
                self.add_log_mess(self.cls_res.mess)
                if self.exit_status_(self.cls_res.mess):
                    return False
                self.log_mess('Create *.lig file', 'info4')
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
                self.log_mess('Update Xcas', 'info5')
            else:
                cond_casier = False
                if self.par["presenceCasiers"] and self.noyau == "unsteady":
                    cond_casier = True
                self.log_mess('Read *.opt file', 'info3')
                self.cls_res.lit_opt_new(
                    self.id_run, self.date_debut, self.basename, self.comments,
                    self.par["presenceTraceurs"], cond_casier,
                    self.cond_api, self.save_res_struct)

                self.add_log_mess(self.cls_res.mess)
                if self.exit_status_(self.cls_res.mess):
                    return False

                if self.check_mobil_gate():
                    self.log_mess('Read Mobile Gate', 'info4')
                    self.cls_res.read_mobil_gate_res(self.id_run)
                    self.add_log_mess(self.cls_res.mess)
                    if self.exit_status_(self.cls_res.mess):
                        return False
            self.log_mess('TaskMascPost End', 'info2')
            return True
        except Exception as e:
            self.log_mess(str(e), 'errPost', 'critic')
            return False

    def check_mobil_gate(self):
        """
        check if weirs active
        Return :
            :return: boolean
        """
        info = self.mdb.select(
            "weirs", where="active_mob = true", list_var=["method_mob", "gid", "name"]
        )
        if info:
            if len(info["gid"]) > 0:
                return True

        return False
