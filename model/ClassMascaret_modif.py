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

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
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
        self.nomfichGEO = self.baseName + ".geo"
        self.box = ClassWarningBox()
        # state list
        self.listeState = ["Steady", "Unsteady", "Transcritical unsteady"]
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]
        self.dico_basinnum = {}
        self.dico_linknum = {}
        self.wq = ClassMascWQ(self.mgis, self.dossierFileMasc)
        self.clmeth = ClassMascStruct(self.mgis)
        self.cond_api = self.mgis.cond_api
        self.save_res_struct = None

        self.err_model = {}
        self.err_model["timeLaw"] = TypeErrorModel("timeLaw", " ERROR : Law Time", stop=True)
        self.err_model["lInflowPos"] = TypeErrorModel("lInflowPos", "WARNING : the inflow position")

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

    def mascaret_init(self, noyau, run, only_init):
        """
        Initial file creation in model
        :param noyau:(str) Mascaret kernel
        :param run:(str) run name
        :param only_init:(bool)  option to write the  model files but it doesn't
                work with 'evenement'
        :return:
        """
        comments = ""
        sql = "SELECT parametre, {0} FROM {1}.{2};"
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        par = {}

        for param, valeur in rows:
            try:
                par[param] = eval(valeur.title())
            except:
                par[param] = valeur
        if not par["repriseCalcul"]:
            self.clean_rep()
            self.creer_geo_ref()
            self.mgis.add_info("Geometric file is created.", dbg=True)
            self.mgis.add_info("noyau {}".format(noyau), dbg=True)
        else:
            self.clean_res()

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

        # progressMessageBar = self.iface.messageBar().createMessage(
        #     "Run ...")
        # self.iface.messageBar().pushWidget(progressMessageBar,
        # self.iface.messageBar().INFO)

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

    def init_scen_steady(self, par, dict_lois):
        """
         Initial  files creation  for steady scenario
        :param par: (dict) parameters
        :param dict_lois:  (dict) laws
        :return:
        """

        if par["presenceTraceurs"]:
            if self.wq.dico_phy[self.wq.cur_wq_mod]["meteo"]:
                self.wq.create_filemet()

        for nom, l in dict_lois.items():
            if "valeurperm" not in l.keys():
                continue
            if l["valeurperm"] is None:
                # dictLois.items() extremities liste

                tab = self.get_laws(nom, l["type"])
                if tab:
                    self.creer_loi(nom, tab, l["type"])
                else:
                    self.mgis.add_info("The law for {} is not create.".format(nom))
            else:
                try:
                    liste_ = ["pasTemps", "critereArret", "nbPasTemps", "tempsMax", "tempsInit"]
                    temp_dic = {}
                    for info in liste_:
                        condition = "parametre ='{}'".format(info)
                        dtemp = self.mdb.select_distinct("steady", "parametres", condition)
                        temp_dic[info] = dtemp["steady"][0]
                except Exception as e:
                    self.mgis.add_info("erreur crit")
                    self.mgis.add_info(str(e))
                    return
                # self.mgis.add_info('{}'.format(condition))
                if temp_dic["critereArret"] == 1:
                    tfinal = temp_dic["tempsMax"]
                elif temp_dic["critereArret"] == 2:
                    tfinal = temp_dic["tempsInit"] + temp_dic["pasTemps"] * temp_dic["nbPasTemps"]
                elif temp_dic["critereArret"] == 3:
                    tfinal = 365 * 24 * 3600

                condition = "geom_obj='{0}' AND id_law_type={1} AND active".format(nom, l["type"])
                if l["type"] == 1:
                    tab = {"time": [0, tfinal], "flowrate": [l["valeurperm"]] * 2}
                # no possible to use rating curve (5) with steady.
                #   It's replaced in xcas
                elif l["type"] == 2 or l["type"] == 5:
                    l["type"] = 2
                    tab = {"time": [0, tfinal], "z": [l["valeurperm"]] * 2}
                else:
                    tab = self.get_laws(nom, l["type"])

                if tab:
                    self.creer_loi(nom, tab, l["type"])
                else:
                    self.mgis.add_info("The law for {} is not create.".format(nom))

    def init_scen_even(self, par, dict_lois, i, dict_scen):
        """
        Initial  files creation  for evenment scenario
        :param par:  (dict) parameters
        :param dict_lois: (dict) laws
        :param i: (int) um scenario
        :param dict_scen: (dict)dictionnay of scenarii
        :return:
        """
        # transcritical unsteady evenement
        date_debut = dict_scen["starttime"][i]
        date_fin = dict_scen["endtime"][i]
        duree = int((date_fin - date_debut).total_seconds()) - 3600

        tab = {
            "tempsMax": {"valeur": str(duree), "balise1": "parametresTemporels"},
            "titreCalcul": {
                "valeur": dict_scen["name"][i],
                "balise1": "parametresImpressionResultats",
            },
        }
        self.modif_xcas(tab, self.baseName + ".xcas")
        par["tempsMax"] = duree
        self.mgis.add_info("Xcas file is created.")
        if par["presenceTraceurs"]:
            if self.wq.dico_phy[self.wq.cur_wq_mod]["meteo"]:
                self.wq.create_filemet(typ_time="date", datefirst=date_debut, dateend=date_fin)

        self.obs_to_loi(dict_lois, date_debut, date_fin, par)

        return date_debut

    def init_scen_trans_unsteady(self, par, dict_lois):
        """
        Initial  files creation  for unsteady scenario
        :param par: dict contains the parameters
        :param dict_lois: dict contains the law
        :return:
        """

        if par["presenceTraceurs"]:
            if self.wq.dico_phy[self.wq.cur_wq_mod]["meteo"]:
                self.wq.create_filemet()

        for nom, l in dict_lois.items():
            # dictLois.items() extremities liste

            tab = self.get_laws(nom, l["type"])
            if tab:
                self.creer_loi(nom, tab, l["type"])
                if "time" in tab.keys():
                    initime = round(tab["time"][0], 3)
                    lasttime = round(tab["time"][-1], 3)
                    self.check_timelaw(par, nom, initime, lasttime)
            else:
                self.mgis.add_info("The law for {} is not create.".format(nom))

            self.mgis.add_info("Laws file is created.", dbg=True)

            if "valeurperm" not in l.keys():
                continue

            # nom = nom + "_init"
            if l["valeurperm"] is not None:
                if l["type"] == 1:
                    tab = {"time": [0, 3600], "flowrate": [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 1, init=True)
                elif l["type"] == 2:
                    tab = {"time": [0, 3600], "z": [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 2, init=True)
                elif l["type"] in [4, 5]:
                    self.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    self.mgis.add_info("No initialisation")
            else:
                if l["type"] in [4, 5]:
                    self.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    self.mgis.add_info(
                        "No initialisation because of no valeurperm " "for {} condition".format(nom)
                    )

        return

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

    # return
    def mascaret(self, noyau, run, only_init=False):
        """
        creation file and to run mascaret
        :param noyau: kernel
        :param run: name run
        :param only_init: if only intialisation is true
        :return:
        """
        par, dict_scen, dict_lois, comments = self.mascaret_init(noyau, run, only_init)
        if not par or not dict_scen or not dict_lois:
            return

        if only_init:
            id = 0

            if noyau == "steady":
                self.init_scen_steady(par, dict_lois)
            elif par["evenement"]:
                date_debut = self.init_scen_even(par, dict_lois, id, dict_scen)
            else:
                # transcritical unsteady hors evenement
                self.init_scen_trans_unsteady(par, dict_lois)
            if self.check_mobil_gate() and noyau == "unsteady":
                self.create_mobil_gate_file()
            self.fct_only_init(noyau, dict_scen)
            return

        #
        if self.mgis.task_use:
            self.mgis.task_mas = QgsTask.fromFunction(
                "Run Mascaret",
                self.task_mascaret,
                on_finished=self.completed,
                tup=(par, dict_scen, dict_lois, comments, noyau, run),
            )
            self.mgis.task_mas.taskCompleted.connect(self.del_task_mas)
            self.mgis.task_mas.taskTerminated.connect(self.del_task_mas)
            QgsApplication.taskManager().addTask(self.mgis.task_mas)
        else:
            self.task_mascaret(None, tup=(par, dict_scen, dict_lois, comments, noyau, run))

    def del_task_mas(self):
        """
        Clean tastk_mas variable
        :return:
        """
        del self.mgis.task_mas
        gc.collect()
        self.mgis.task_mas = None

    def completed(self, exception):
        """this is called when run is finished. Exception is not None if run
        raises an exception. Result is the return value of run."""
        message_category = "My tasks from a function"
        if exception is None:
            QgsMessageLog.logMessage("task completed", message_category, Qgis.Info)
        else:
            QgsMessageLog.logMessage(
                "Exception: {}".format(exception), message_category, Qgis.Critical
            )
            raise exception

    def task_mascaret(self, task, tup=None):
        if tup:
            par, dict_scen, dict_lois, comments, noyau, run = tup
        else:
            self.mgis.add_info("no transmitted variable for task_mascaret")
            return

        for i, scen in enumerate(dict_scen["name"]):
            self.clean_res()
            self.mgis.add_info(" *** The current scenario is {} ***".format(scen))
            # initialise file
            date_debut = None
            if noyau == "steady":
                self.init_scen_steady(par, dict_lois)

            elif par["evenement"]:
                date_debut = self.init_scen_even(par, dict_lois, i, dict_scen)
            else:
                # transcritical unsteady hors evenement
                self.init_scen_trans_unsteady(par, dict_lois)
            if self.check_mobil_gate() and noyau == "unsteady":
                self.create_mobil_gate_file()

            # check error and warning:
            self.check_apport()
            arret = False
            for typerr in self.err_model:
                if self.err_model[typerr].status:
                    self.mgis.add_info(self.err_model[typerr].get_alltxt())
                    if self.err_model[typerr].stop:
                        arret = True
            if arret:
                return False

            # RUN Model
            if par["initialisationAuto"] and noyau != "steady":
                # add if name of init. exist previously
                sceninit = scen + "_init"
                if self.check_scenar(sceninit, run):
                    self.mgis.add_info("========== Run initialization =========")
                    self.mgis.add_info(
                        "Run = {} ;  Scenario = {} ; Kernel= {}".format(run, sceninit, noyau)
                    )

                    id_run = self.insert_id_run(run, sceninit)
                    self.lance_mascaret(self.baseName + "_init.xcas", id_run)

                    self.lit_opt_new(id_run, None, self.baseName + "_init", comments)
                    self.mgis.add_info("Auto-initialization Run is done", dbg=True)

                else:
                    self.mgis.add_info(
                        "No Run initialization.\n"
                        " The initial boundaries come "
                        "from {} scenario.".format(sceninit)
                    )
                    return

                self.opt_to_lig(id_run, self.baseName)
                tab = {
                    "LigEauInit": {
                        "valeur": "true",
                        "balise1": "parametresConditionsInitiales",
                        "balise2": "ligneEau",
                    }
                }
                self.modif_xcas(tab, self.baseName + ".xcas")

            elif par["LigEauInit"] and noyau != "steady":
                #    self.select_init_run_case()
                id_run_init = None
                if "id_run_init" in dict_scen.keys():
                    id_run_init = dict_scen["id_run_init"][i]
                if id_run_init is None:
                    self.mgis.add_info("Cancel run because No initial boundaries")
                    continue
                self.opt_to_lig(id_run_init, self.baseName)

            self.mgis.add_info("========== Run case  =========")
            self.mgis.add_info("Run = {} ;  Scenario = {} ; Kernel= {}".format(run, scen, noyau))
            cond_casier = False
            if par["presenceCasiers"] and noyau == "unsteady":
                cond_casier = True

            id_run = self.insert_id_run(run, scen)
            finish = self.lance_mascaret(
                self.baseName + ".xcas", id_run, par["presenceTraceurs"], cond_casier
            )
            if not finish:
                self.mgis.add_info("Simulation error")
                return

            self.lit_opt_new(
                id_run, date_debut, self.baseName, comments, par["presenceTraceurs"], cond_casier
            )

            if self.check_mobil_gate():
                self.read_mobil_gate_res(id_run)

            # if task :
            #     if task.isCanceled():
            #         return
        # #
        self.iface.messageBar().clearWidgets()
        self.mgis.add_info("Simulation finished")
        return

    def import_results(self, run, scen, comments, path, date_debut=None):
        """
        import mascaret resultats
        :param run: (str) run name
        :param scen: (str) scenario name
        :param comments:(str) comments
        :param path: (str) path represitory
        :param date_debut: start time
        :return:
        """

        lia_cond = False
        cas_cond = False
        cond_tra = False

        for file in os.listdir(path):
            if file.split(".")[-1] == "liai_opt":
                lia_cond = True
            elif file.split(".")[-1] == "cas_opt":
                cas_cond = True
            elif file.split(".")[-1] == "tra_opt":
                cond_tra = True

        cond_casier = False
        if lia_cond and cas_cond:
            cond_casier = True

        id_run = self.insert_id_run(run, scen)
        self.lit_opt_new(id_run, date_debut, self.baseName, comments, cond_tra, cond_casier)

        if os.path.isfile(os.path.join(path, "Fichier_Crete.csv")):
            self.read_mobil_gate_res(id_run)

        if os.path.isfile(os.path.join(path, "res_struct.res")):
            with open(os.path.join(path, "res_struct.res"), "r") as filein:
                dico = json.load(filein)
            self.stock_res_api(dico, id_run)

    def fct_only_init(self, noyau, dict_scen):
        """
        clean and model file creation
        :param noyau: (str) kernel
        :return:
        """
        # delete "initialisationAuto" file
        for file in os.listdir(self.dossierFileMasc):
            if "_init.loi" in file or "_init.xcas" in file:
                path = os.path.join(self.dossierFileMasc, file)
                if os.path.isfile(path):
                    os.remove(path)
        # select initial case
        if noyau != "steady":
            dict_scen = self.select_init_run_case(dict_scen)
            if dict_scen["id_run_init"][0] != None:
                self.opt_to_lig(dict_scen["id_run_init"][0], self.baseName)
        cl = ClassPostPreFG(self.mgis)

        # path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        # 'mascaret'))
        path = self.dossierFileMasc
        path = os.path.join(path, "cli_fg.obj")
        cl.create_cli_fg(path)
        del cl

    def lance_mascaret(self, fichier_cas, id_run, tracer=False, casier=False):
        """
        Run mascaret
        :param fichier_cas:
        :param id_run:
        :param tracer:
        :param casier:
        :return:
        """
        os.chdir(self.dossierFileMasc)
        with open("FichierCas.txt", "w") as fichier:
            fichier.write("'" + fichier_cas + "'\n")
        if not self.cond_api:
            test = sys.platform
            if "linux" in test or test == "cygwin":
                soft = "./mascaret_linux"
            elif test == "win32":
                soft = "mascaret.exe"
            else:
                self.mgis.add_info("{0} platform  doesn't allow to run simulation.".format(test))
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
            self.mgis.add_info(txt)
            self.mgis.add_info(txt1)

            return True
        else:
            pwd = os.getcwd()
            os.chdir(self.dossierFileMasc)
            clapi = ClassAPIMascaret(self)
            clapi.main(fichier_cas, tracer, casier)
            self.save_res_struct = (copy.deepcopy(clapi.results_api), id_run)
            del clapi

            os.chdir(pwd)
            return True

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
                        if "results_old" in lst_tab:
                            self.mdb.delete("results_old", condition)

                        self.mdb.delete("results_sect", condition)
                        self.mdb.delete("runs_graph", condition)
                        self.mdb.delete("runs_plani", condition)

                        self.mdb.delete("results_by_pk", condition)
                        if "results_val" in lst_tab:
                            condition_val = (
                                "idruntpk IN "
                                "(SELECT DISTINCT id_runs FROM {0}.results_idx "
                                "where id_runs={1})".format(self.mdb.SCHEMA, id_run)
                            )
                            self.mdb.delete("results_val", condition_val)
                        if "results_idx" in lst_tab:
                            self.mdb.delete("results_idx", condition)

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

    def check_apport(self):
        """checks if the inflow is before the first mesh."""
        #
        apports = self.mdb.select("lateral_inflows", "active", "abscissa")
        for i, numb in enumerate(apports["branchnum"]):
            branches = self.mdb.select_one(
                "visu_branchs",
                "branchnum={}".format(numb),
                "abs_start",
                list_var=["abs_start", "mesh"],
            )

            comp = branches["abs_start"] + branches["mesh"]
            if apports["abscissa"][i] < comp:
                self.err_model["lInflowPos"].add_err(
                    apports["name"][i],
                    "Warning: {} is located before the first mesh."
                    " Ignore in the model".format(apports["name"][i]),
                )
