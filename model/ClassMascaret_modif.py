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
import csv
import datetime
import gc
import json
import os
import re
import shutil
import subprocess
import sys
import json
import gc
import numpy as np
import copy

from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as et_parse

from qgis.PyQt.QtCore import qVersion
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .Function import TypeErrorModel
from .Function import del_symbol
from .Function import str2bool, del_accent, copy_dir_to_dir
from .Graphic.ClassResProfil import ClassResProfil
from .HydroLawsDialog import dico_typ_law
from .Structure.ClassMascStruct import ClassMascStruct
from .Structure.ClassPostPreFG import ClassPostPreFG
from .WaterQuality.ClassMascWQ import ClassMascWQ
from .api.ClassAPIMascaret import ClassAPIMascaret
from .ui.custom_control import ClassWarningBox
from  ClassMessage import ClassMessage

from ClassCreatFilesModels import ClassCreatFilesModels

from qgis.core import QgsApplication
from TaskMascInit import TaskMascInit
from TaskMascComput import TaskMascComput
from TaskMascPost import TaskMascPost



from qgis.PyQt.QtWidgets import *


class ClassMascaret:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main, rep_run=None):
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.iface = self.mgis.iface
        if not rep_run:
            self.dossierFileMasc = os.path.join(self.mgis.masplugPath, "mascaret")
        else:
            self.dossierFileMasc = rep_run

        if not os.path.isdir(self.dossierFileMasc):
            os.mkdir(self.dossierFileMasc)
        self.dossierFileMascOri = os.path.join(self.mgis.masplugPath, "mascaret_ori")
        self.dossierFile_bin = os.path.join(self.mgis.masplugPath, "bin")
        self.baseName = "mascaret"
        self.box = ClassWarningBox()
        # state list
        self.listeState = ["Steady", "Unsteady", "Transcritical unsteady"]
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]

        self.wq = ClassMascWQ(self.mgis, self.dossierFileMasc)
        self.clmeth = ClassMascStruct(self.mgis)
        self.cond_api = self.mgis.cond_api
        self.save_res_struct = None

        self.err_model = {}
        self.err_model["timeLaw"] = TypeErrorModel("timeLaw", " ERROR : Law Time", stop=True)
        self.err_model["lInflowPos"] = TypeErrorModel("lInflowPos", "WARNING : the inflow position")

        self.mess = ClassMessage()
        self.clfile = ClassCreatFilesModels(self.mdb, self.dossierFileMasc)
        # list ERROR: *****************************************
        #
        # List WARNING :***************************************
        #
        # List INFO: *******************************************
        #
        #
        # List DEBUG:********************************************
        #

    def get_param_model(self, noyau):
        sql = "SELECT parametre, {0} FROM {1}.{2};"
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        par = {}
        for param, valeur in rows:
            try:
                par[param] = eval(valeur.title())
            except:
                par[param] = valeur
        return  par

    def write_mess(self, obj):
        txt = obj.message()
        self.mgis.add_info(txt)
        obj.clear_derror()

    def mascaret_init(self, noyau, run):
        """
              creation file and to run mascaret # TODO Hors task
              :param noyau: kernel
              :param run: name run
              :param only_init: if only intialisation is true
              :return:
        """
        # var
        comments = ""
        dict_scen = {}
        # parameters
        self.mgis.add_info("noyau {}".format(noyau), dbg=True)
        par = self.get_param_model(noyau)
        # geometry
        exit_status = False
        if not par["repriseCalcul"]:
            self.clean_rep()
            self.clfile.creer_geo_ref()
            exit_status = self.clfile.mess.get_critic_status()
            self.write_mess(self.clfile.mess)
        else:
            self.clean_res()
        if  exit_status:
            self.mgis.add_info("Compute is cancel.")
            return
        # Creation du fichier de la geometrie des casiers uniquement
        #   en non-permanent et si presence des casiers
        if par["presenceCasiers"] and noyau == "unsteady":
            self.clfile.creer_geo_casier()
            exit_status = self.clfile.mess.get_critic_status()
            self.write_mess(self.clfile.mess)
            if exit_status:
                self.mgis.add_info("Compute is cancel.")
                return

        if par["presenceTraceurs"]:
            self.wq.create_filephy()
            # TODO no make with event
            self.wq.law_tracer()
            self.wq.init_conc_tracer()

        if par["evenement"] and noyau != "steady":
            dict_scen_tmp = self.mdb.select("events", "run", "starttime")
            listexclu = []
            if len(dict_scen_tmp["name"]) == 0:
                self.mgis.add_info("**** Warning: scenario not found  ***")
            for i, scen in enumerate(dict_scen_tmp["name"]):
                # self.mgis.add_info("scen**************** {}".format(scen))
                scen = scen.strip()
                if not self.check_scenar(scen, run):
                    self.mgis.add_info(
                        "Canceled Simulation because of {0} " "already exists.".format(scen)
                    )
                    listexclu.append(i)
            if listexclu:
                dict_scen = {}
                for key in dict_scen_tmp:
                    value = dict_scen_tmp[key]
                    value = [elt for idx, elt in enumerate(value) if not (idx in listexclu)]
                    dict_scen[key] = value
            else:
                dict_scen = dict_scen_tmp
            comments = self.fct_comment()
        else:
            scen, ok = QInputDialog.getText(
                QWidget(), "Scenario name", "Please input a scenario name :"
            )
            scen = scen.replace("'", " ").replace('"', " ").strip()
            if not ok or not self.check_scenar(scen, run):
                self.mgis.add_info(
                    "Canceled Simulation because of {0} " "already exists.".format(scen)
                )
                return None, None, None, None
            comments = self.fct_comment()
            dict_scen = {"name": [scen]}

        if par["LigEauInit"] and not par["initialisationAuto"] and noyau != "steady":
            dict_scen = self.select_init_run_case(dict_scen)

        return par, dict_scen, comments

    def mascaret(self, noyau, run):
        """
        creation file and to run mascaret
        :param noyau: kernel
        :param run: name run
        :param only_init: if only intialisation is true
        :return:
        """
        par, dict_scen,  comments = self.mascaret_init(noyau, run)
        if not par or not dict_scen :
            self.mgis.add_info("**** Error : Error at initilisation of model")
            return

        for idx, scen in enumerate(dict_scen["name"]):
            init_task = TaskMascInit(self.mdb, self.wq, self.dossierFileMasc, par, noyau, scen, idx, dict_scen)
            QgsApplication.taskManager().addTask(init_task)
            init_task.waitForFinished(timeout=0)

            if par["initialisationAuto"] and noyau != "steady":
                sceninit = scen + "_init"
                self.mgis.add_info("========== Run initialization =========")
                self.mgis.add_info("Run = {} ;  Scenario = {} ; Kernel= {}".format(run, sceninit, noyau))
                cpt_task_init = TaskMascComput(init_task, self.mdb,self.cond_api, cpt_init=True)
                res_task_init = TaskMascPost()
            self.mgis.add_info("========== Run case  =========")
            self.mgis.add_info("Run = {} ;  Scenario = {} ; Kernel= {}".format(run, scen, noyau))
            cpt_task = TaskMascComput(init_task, self.cond_api, self.mdb)
            QgsApplication.taskManager().addTask(cpt_task)
            res_task = TaskMascPost(cpt_task, self.mdb, self.baseName, comments)
            QgsApplication.taskManager().addTask(res_task)
            #res_task.waitForFinished(timeout =0)
            #QgsApplication.taskManager().waitForTasksToFinish()
            pass
            # TODO gere taskrun

    def fct_comment(self):
        liste_col = self.mdb.list_columns("runs")
        if "comments" in liste_col:
            comments, ok = QInputDialog.getText(
                QWidget(), "Comments", "if you want to input " "a comment :"
            )
            if not isinstance(comments, str):
                comments = str(comments)
            if not ok:
                self.mgis.add_info("No comments.", dbg=True)
                comments = ""
        else:
            comments = ""
        return comments.replace("'", "''").replace('"', " ")

    def mascaret_init_old(self, noyau, run, only_init):
        """
        Initial file creation in model
        :param noyau:(str) Mascaret kernel
        :param run:(str) run name
        :param only_init:(bool)  option to write the  model files but it doesn't
                work with 'evenement'
        :return:
        """


        # Creation du fichier de la geometrie des casiers uniquement
        #   en non-permanent et si presence des casiers
        if par["presenceCasiers"] and noyau == "unsteady":
            self.creer_geo_casier()
        if only_init:
            if par["evenement"] and noyau != "steady":
                dict_scen_tmp = self.mdb.select("events", "run", "starttime")
                if len(dict_scen_tmp["name"]) == 0:
                    self.mgis.add_info("**** Warning: scenario not found  ***")
                scen2, ok = QInputDialog.getItem(
                    None, "Select Events", "Select Events", dict_scen_tmp["name"], 0, False
                )
                if ok:
                    id = dict_scen_tmp["name"].index(scen2)
                    dict_scen = {
                        "name": [dict_scen_tmp["name"][id]],
                        "starttime": [dict_scen_tmp["starttime"][id]],
                        "endtime": [dict_scen_tmp["endtime"][id]],
                        "run": [dict_scen_tmp["run"][id]],
                    }

            else:
                dict_scen = {"name": ["test_api"]}
        else:
            if par["evenement"] and noyau != "steady":
                dict_scen_tmp = self.mdb.select("events", "run", "starttime")
                listexclu = []
                if len(dict_scen_tmp["name"]) == 0:
                    self.mgis.add_info("**** Warning: scenario not found  ***")
                for i, scen in enumerate(dict_scen_tmp["name"]):
                    # self.mgis.add_info("scen**************** {}".format(scen))
                    scen = scen.strip()
                    if not self.check_scenar(scen, run):
                        self.mgis.add_info(
                            "Canceled Simulation because of {0} " "already exists.".format(scen)
                        )
                        listexclu.append(i)
                if listexclu:
                    dict_scen = {}
                    for key in dict_scen_tmp:
                        value = dict_scen_tmp[key]
                        value = [elt for idx, elt in enumerate(value) if not (idx in listexclu)]
                        dict_scen[key] = value
                else:
                    dict_scen = dict_scen_tmp
                comments = self.fct_comment()
            else:
                scen, ok = QInputDialog.getText(
                    QWidget(), "Scenario name", "Please input a scenario name :"
                )
                scen = scen.replace("'", " ").replace('"', " ").strip()
                if not ok or not self.check_scenar(scen, run):
                    self.mgis.add_info(
                        "Canceled Simulation because of {0} " "already exists.".format(scen),
                        dbg=True,
                    )
                    return None, None, None, None
                comments = self.fct_comment()
                dict_scen = {"name": [scen]}

        dict_lois, dico_loi_struct = self.creer_xcas(noyau)
        self.mgis.add_info("Xcas file is created.", dbg=True)
        if par["presenceTraceurs"]:
            self.wq.create_filephy()
            self.wq.law_tracer()
            self.wq.init_conc_tracer()

        if dico_loi_struct.keys():
            for name in dico_loi_struct.keys():
                list_final = self.clmeth.get_list_law(dico_loi_struct[name]["id_config"])

                self.clmeth.create_law(
                    self.dossierFileMasc, name, dico_loi_struct[name]["type"], list_final
                )
                self.clmeth.create_law(
                    self.dossierFileMasc, name + "_init", dico_loi_struct[name]["type"], list_final
                )

        self.mgis.add_info("Tracer files are created.", dbg=True)

        if par["LigEauInit"] and not par["initialisationAuto"] and noyau != "steady":
            dict_scen = self.select_init_run_case(dict_scen)

        return par, dict_scen, dict_lois, comments

    def select_init_run_case(self, dict_scen):
        """
        Select initial run case
        :return:
        """
        dico_run = self.mdb.select_distinct("run", "runs")

        if dico_run != {} and dico_run is not None:
            liste_run = ["{}".format(v) for v in dico_run["run"]]
        else:
            liste_run = []
        liste_run.append('".lig" File')
        dict_scen["id_run_init"] = []
        for i, scen in enumerate(dict_scen["name"]):
            case, ok = QInputDialog.getItem(
                None, "Initial run case for {}".format(scen), "Runs", liste_run, 0, False
            )
            if ok:
                if case == '".lig" File':
                    self.copy_lig()
                else:
                    condition = "run LIKE '{0}'".format(case)
                    dico_scen = self.mdb.select_distinct("scenario", "runs", condition)
                    liste_scen = ["{}".format(v) for v in dico_scen["scenario"]]

                    scen2, ok = QInputDialog.getItem(
                        None,
                        "Initial Scenario for {}".format(scen),
                        "Initial Scenario",
                        liste_scen,
                        0,
                        False,
                    )

                    if ok:
                        id_run = self.mdb.run_query(
                            "SELECT id FROM {0}.runs "
                            "WHERE run = '{1}' "
                            "AND scenario = '{2}'".format(self.mdb.SCHEMA, case, scen2),
                            fetch=True,
                        )
                        dict_scen["id_run_init"].append(id_run[0][0])
                        # self.opt_to_lig( id_run[0][0], self.baseName)

                    else:
                        dict_scen["id_run_init"].append(None)
                        self.mgis.add_info("Cancel run : {}".format(scen), dbg=True)
            else:
                dict_scen["id_run_init"].append(None)
                self.mgis.add_info("Cancel run: {}".format(scen), dbg=True)

        return dict_scen

    def copy_lig(self):
        """Load .lig file in run model"""
        if int(qVersion()[0]) < 5:  # qt4
            fichiers = QFileDialog.getOpenFileNames(
                None,
                "File Selection",
                # self.dossierFileMasc,
                self.mgis.repProject,
                "File (*.lig)",
            )

        else:  # qt5
            fichiers, _ = QFileDialog.getOpenFileNames(
                None,
                "File Selection",
                self.mgis.repProject,
                # self.dossierFileMasc,
                "File (*.lig)",
            )

        try:
            fichiers = fichiers[0]
            self.mgis.up_rep_project(fichiers)
        except IndexError:
            self.mgis.add_info("Cancel  init file")
            return

        try:
            shutil.copy(fichiers, os.path.join(self.dossierFileMasc, self.baseName + ".lig"))
        except Exception as e:
            self.mgis.add_info("Error copying file")
            self.mgis.add_info("{}".format(e))

    def clean_rep(self):
        """Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        for i in range(0, len(files)):
            os.remove(os.path.join(self.dossierFileMasc, files[i]))
        copy_dir_to_dir(self.dossierFileMascOri, self.dossierFileMasc)
        if not self.check_exe():
            self.mgis.download_bin()

        copy_dir_to_dir(self.dossierFile_bin, self.dossierFileMasc)

    def check_exe(self):
        """
        Check if exe file exists
        :return:
        """
        if not os.path.isdir(self.dossierFile_bin):
            return False
        test = sys.platform
        if "linux" in test or test == "cygwin":
            soft = "mascaret_linux"
        elif test == "win32":
            soft = "mascaret.exe"
        if not os.path.isfile(os.path.join(self.dossierFile_bin, soft)):
            return False

        return True

    def clean_res(self):
        """Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        listsup = [".opt", ".lig", ".cas_opt", ".liai_opt", ".tra_opt"]
        for i in range(0, len(files)):
            ext = os.path.splitext(files[i])[1]
            # self.mgis.add_info('delet file rr{}rr {}'.format(ext,(ext in listsup)))
            if ext in listsup:
                os.remove(os.path.join(self.dossierFileMasc, files[i]))
                self.mgis.add_info("delete file {}".format(files[i]), dbg=True)

    def del_folder_mas(self):
        """Delete the copy folder"""
        try:
            shutil.rmtree(self.dossierFileMasc)
        except Exception as e:
            self.mgis.add_info(
                "Failed to delete {}. Reason: {}".format(self.dossierFileMasc, e), dbg=True
            )

    def copy_run_file(self, rep):
        """copy run file in "rep" path"""
        try:
            files = os.listdir(self.dossierFileMasc)
            for i in range(0, len(files)):
                shutil.copy2(
                    os.path.join(self.dossierFileMasc, files[i]), os.path.join(rep, files[i])
                )
            return True
        except:
            return False

    def copy_file_model(self, rep, case=None):
        # self.mgis.add_info('{}'.format(rep))
        if case == "xcas":
            file = os.path.join(self.dossierFileMasc, self.baseName + ".xcas")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info("{} not found".format(file))
        elif case == "geo":
            file = os.path.join(self.dossierFileMasc, self.baseName + ".geo")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info("{} not found".format(file))
        elif case == "georef":
            file = os.path.join(self.dossierFileMasc, self.baseName + ".georef")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info("{} not found".format(file))
        elif case == "casier":
            file = os.path.join(self.dossierFileMasc, self.baseName + ".casier")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info("{} not found".format(file))
        else:
            self.mgis.add_info("No file to export")

    def check_scenar(self, nom_scen, run):
        """if true :not exist nomScen and results"""
        # kernel=self.listeState[self.Klist.index(kernel)]
        condition = "run LIKE '{0}'".format(run)
        allscen = self.mdb.select_distinct("scenario", "runs", condition)
        if allscen:
            if nom_scen in allscen["scenario"] or nom_scen + "_init" in allscen["scenario"]:
                info = True
            else:
                info = False

            if info:
                ok = self.box.yes_no_q(
                    "Do you want to remove the {} results for a "
                    "new simulation? ".format(nom_scen)
                )

                if ok:
                    lst_tab = self.mdb.list_tables()
                    # delete case initalization
                    condition = (
                        "(scenario LIKE '{0}' OR  scenario "
                        "LIKE '{0}_init')"
                        " AND run LIKE '{1}' ".format(nom_scen, run)
                    )

                    id_run = self.mdb.run_query(
                        "SELECT id FROM {0}.runs "
                        "WHERE run = '{1}' "
                        "AND (scenario LIKE '{2}' "
                        "OR  scenario "
                        "LIKE '{2}_init') ".format(self.mdb.SCHEMA, run, nom_scen),
                        fetch=True,
                    )
                    self.mdb.delete("runs", condition)
                    # new results
                    if len(id_run) > 0:
                        id_run = id_run[0][0]
                        condition = "id_runs = {}".format(id_run)
                        var = self.mdb.run_query(
                            "SELECT DISTINCT var FROM {0}.results "
                            "WHERE {1} ".format(self.mdb.SCHEMA, condition),
                            fetch=True,
                        )
                        list_var = [str(v[0]) for v in var]
                        if len(list_var) > 0:
                            self.mdb.run_query(
                                "DELETE  FROM {}.results_var "
                                "where id in ({}) and "
                                "type_res = '"
                                "tracer_TRANSPORT_PUR'".format(self.mdb.SCHEMA, ",".join(list_var))
                            )
                        self.mdb.delete("results_sect", condition)
                        self.mdb.delete("runs_graph", condition)
                        self.mdb.delete("runs_plani", condition)

                        self.mdb.delete("results_by_pk", condition)
                        # OLD table
                        if "results_val" in lst_tab:
                            condition_val = (
                                "idruntpk IN "
                                "(SELECT DISTINCT id_runs FROM {0}.results_idx "
                                "where id_runs={1})".format(self.mdb.SCHEMA, id_run)
                            )
                            self.mdb.delete("results_val", condition_val)
                        if "results_idx" in lst_tab:
                            condition = "id_runs = {}".format(id_run)
                            self.mdb.delete("results_idx", condition)
                        if "results_old" in lst_tab:
                            condition = "id_runs = {}".format(id_run)
                            self.mdb.delete("results_old", condition)

                    self.mgis.add_info(
                        "Deletion of {0} scenario for {1} is done".format(nom_scen, run), dbg=True
                    )
                    return True
                else:
                    return False

            else:
                return True
        else:
            return True


