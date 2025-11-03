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

import copy
import datetime
import os
import subprocess
import sys
import time

from qgis.core import QgsTask, QgsMessageLog, Qgis

from ..ClassMessage import ClassMessage
from ..api.ClassAPIMascaret import ClassAPIMascaret

MESSAGE_CATEGORY = "TaskMascaret"


class TaskMascComput(QgsTask):
    """
    Task of the Computing model
    """

    def __init__(self, glb_param):
        super().__init__()

        self.mdb = glb_param["mdb"]
        self.cond_api = glb_param["cond_api"]
        self.run_ = glb_param["run"]
        self.noyau = glb_param["noyau"]
        self.masc = glb_param["masc"]

        self.dossier_file_masc = glb_param["dossier_file_masc"]
        self.base_name = glb_param["basename"]

        self.id_run = None
        self.save_res_struct = None
        # precedent task
        self.par = None
        self.scen = None
        self.cpt_init = False
        self.mess = ClassMessage()
        # Task info
        self.exc_start_time = time.time()
        self.description = "Computing model"

    def log_mess(self, txt, flag, typ="info"):
        """Manage message
        :param txt : (str) text
        :param flag : (str) error flag
        :param typ :(str) message typ
        :return: None
        """
        self.mess.add_mess(flag, typ, txt)
        if typ == "warning":
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Warning)
        elif typ == "critic":
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Critical)
        else:
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Info)

    def add_log_mess(self, obj):
        """
        Add log message to classMessage object
        :param obj : (object) ClassMessage
        :return: None
        """
        fill_d = self.mess.mess_fill_other_obj(obj)
        if fill_d:
            for key, item in fill_d.items():
                if item["type"] == "warning":
                    QgsMessageLog.logMessage(item["message"], MESSAGE_CATEGORY, Qgis.Warning)
                elif item["type"] == "critic":
                    QgsMessageLog.logMessage(item["message"], MESSAGE_CATEGORY, Qgis.Critical)
                else:
                    QgsMessageLog.logMessage(item["message"], MESSAGE_CATEGORY, Qgis.Info)

    def update_inputs(self, up_dict, cpt_init=False):
        """
        Updating class parameters
        :param  up_dict: (dict) new parameters
        :param cpt_init : (boolean) if inialisation phase or not
        :return: None
        """
        self.par = up_dict["par"]
        self.scen = up_dict["scen"]
        self.cpt_init = cpt_init

    def maj_param(self, up_dict):
        """ "
        Updating the information transfer dictionary
        :param  up_dict: (dict) transfer dictionary
        :return : (dict) updated transfer dictionary
        """
        up_dict["id_run"] = self.id_run
        up_dict["save_res_struct"] = self.save_res_struct
        return up_dict

    def run(self):
        """
        Run task
        :return (boolean): True if success, False if error
        """
        if self.cpt_init:
            sceninit = self.scen + "_init"
            self.id_run = self.insert_id_run(self.run_, sceninit)
            finish = self.lance_mascaret(self.base_name + "_init.xcas", self.id_run)

            if not finish:
                self.log_mess("Init Simulation error", "ErrSim", "warning")
                return False

        else:
            cond_casier = False
            if self.par["presenceCasiers"] and self.noyau == "unsteady":
                cond_casier = True
            self.id_run = self.insert_id_run(self.run_, self.scen)
            finish = self.lance_mascaret(
                self.base_name + ".xcas", self.id_run, self.par["presenceTraceurs"], cond_casier
            )
            if not finish:
                self.log_mess("Simulation error", "ErrSim", "warning")
                return False
        QgsMessageLog.logMessage("END Run", MESSAGE_CATEGORY, Qgis.Info)
        return True

    def lance_mascaret(self, fichier_cas, id_run, tracer=False, casier=False):
        """
        Run mascaret

        :param fichier_cas (str): file name of the cas file
        :param id_run (int): run id
        :param tracer (boolean): if tracer is present
        :param casier (boolean): if casier is present
        :return (boolean): True if success, False if error
        """
        self.log_mess("TaskMascComput Begin", "info1")
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
                txt = "{0} platform  doesn't allow to run simulation.".format(test)
                self.log_mess(txt, "ErrPlatform", "critic")
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
            self.log_mess(txt, "InfoRun")
            self.log_mess(txt1, "InfoRun1")
            self.log_mess("TaskMascComput End", "info2")
            return True
        else:
            pwd = os.getcwd()
            os.chdir(self.dossier_file_masc)
            clapi = ClassAPIMascaret(self.masc)
            clapi.fct_main(fichier_cas, tracer, casier)
            mess = ClassMessage()
            mess.load_obj(self.dossier_file_masc)
            self.add_log_mess(mess)
            self.save_res_struct = (copy.deepcopy(clapi.results_api), id_run)
            del clapi

            os.chdir(pwd)
            self.log_mess("TaskMascComput End", "info2")
            return True

    def insert_id_run(self, run_, scen):
        """
        creation run line in runs table
        :param run_: run name
        :param scen: scenario name
        :return (id_run): run id
        """

        maintenant = datetime.datetime.utcnow()
        tab = {run_: {"scenario": scen, "date": "{:%Y-%m-%d %H:%M}".format(maintenant)}}
        listimport = ["run", "scenario", "date"]
        self.mdb.insert("runs", tab, listimport)
        info = self.mdb.select(
            "runs", where="run='{}' AND scenario='{}'".format(run_, scen), list_var=["id"]
        )
        id_run = info["id"][0]
        return id_run
