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

import os
import shutil
import sys

from qgis.PyQt.QtCore import qVersion
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.core import QgsApplication
from qgis.gui import *
from qgis.utils import *

from ..Function import TypeErrorModel
from ..Function import str2bool, del_accent, copy_dir_to_dir
from ..Structure.ClassMascStruct import ClassMascStruct
from ..WaterQuality.ClassMascWQ import ClassMascWQ
from ..Structure.ClassPostPreFG import ClassPostPreFG
from ..ui.custom_control import ClassWarningBox


from .ClassCreatFilesModels import ClassCreatFilesModels
from .TaskMascaret import TaskMascaret

import time



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
        self.cond_api = self.mgis.cond_api
        self.save_res_struct = None

        self.err_model = {}
        self.err_model["timeLaw"] = TypeErrorModel("timeLaw", " ERROR : Law Time", stop=True)
        self.err_model["lInflowPos"] = TypeErrorModel("lInflowPos", "WARNING : the inflow position")

        self.clfile = ClassCreatFilesModels(self.mdb, self.dossierFileMasc)


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

    def mascaret_init(self, noyau, run, only_init=False):
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
            return None, None, None, None, None
        # Creation du fichier de la geometrie des casiers uniquement
        #   en non-permanent et si presence des casiers
        if par["presenceCasiers"] and noyau == "unsteady":
            self.clfile.creer_geo_casier()
            exit_status = self.clfile.mess.get_critic_status()
            self.write_mess(self.clfile.mess)
            if exit_status:
                self.mgis.add_info("Compute is cancel.")
                return None, None, None, None, None

        if par["presenceTraceurs"]:
            self.wq.create_filephy()
            # TODO no make with event
            self.wq.law_tracer()
            self.wq.init_conc_tracer()
        if only_init:
            dict_scen, comments = self.creat_dict_scen_only_init(par, noyau)
        else:
            dict_scen, comments = self.creat_dict_scen(par, noyau, run)

        if par["LigEauInit"] and not par["initialisationAuto"] and noyau != "steady":
            dict_scen = self.select_init_run_case(dict_scen)

        # creation Xcas
        dict_lois, dico_loi_struct = self.clfile.creer_xcas(noyau)
        exit_status = self.clfile.mess.get_critic_status()
        self.write_mess(self.clfile.mess)
        if  exit_status:
            return None, None, None, None, None

        return par, dict_scen, comments, dict_lois, dico_loi_struct

    def creat_dict_scen_only_init(self, par, noyau):
        """ Create scen dictionnary if only initialisation
        :param par : parameters
        :param noyau: kernel
        :param run: name run
        """
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
        return dict_scen, ''

    def creat_dict_scen(self, par, noyau, run):
        """ Create scen dictionnary
        :param par : parameters
        :param noyau: kernel
        :param run: name run
        """
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
                return None, None, None, None, None
            comments = self.fct_comment()
            dict_scen = {"name": [scen]}
        return dict_scen, comments


    def print_info(self,txt):
        self.mgis.add_info(txt)

    def connect_task(self, task):
        task.message.connect(self.print_info)

    def mascaret(self, noyau, run):
        """
        creation file and to run mascaret
        :param noyau: kernel
        :param run: name run
        :param only_init: if only intialisation is true
        :return:
        """

        t1 = time.time()
        par, dict_scen,  comments, dict_lois, dico_loi_struct = self.mascaret_init(noyau, run)

        if not par or not dict_scen or not dict_lois :
            self.mgis.add_info("**** Error : Error at initilisation of model")
            return
        dict_task = {
            'mdb' : self.mdb,
             'wq' : self.wq,
             'basename': self.baseName,
             'dossier_file_masc': self.dossierFileMasc,
             'par' : par,
             'dict_scen': dict_scen ,
             'comments' : comments,
             'dict_lois': dict_lois,
             'dico_loi_struct' :dico_loi_struct,
             'noyau' : noyau,
             'run': run,
            'masc' : self,
            'cond_api':self.cond_api
        }
        task_mas =  TaskMascaret('TaskMascaret', dict_task)
        QgsApplication.taskManager().addTask(task_mas)




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

    def fct_only_init(self, noyau, run):
        """
        clean and model file creation
        :param noyau: (str) kernel
        :return:
        """
        par, dict_scen, comments, dict_lois, dico_loi_struct = self.mascaret_init(noyau, run,only_init=True)
        if not par or not dict_scen or not dict_lois :
            self.mgis.add_info("**** Error : Error at file creation of the model")
            return
        idx = 0
        scen = dict_scen["name"][idx]

        init_task = TaskMascInit(self.mdb, self.wq, self.dossierFileMasc,self.baseName, par, noyau,
                                 scen, idx, dict_scen, dict_lois, dico_loi_struct)
        self.connect_task(init_task)
        QgsApplication.taskManager().addTask(init_task)
        init_task.waitForFinished(timeout=0)

        # if noyau == "steady":
        #     self.init_scen_steady(par, dict_lois)
        # elif par["evenement"]:
        #     date_debut = self.init_scen_even(par, dict_lois, idx, dict_scen)
        # else:
        #     # transcritical unsteady hors evenement
        #     self.init_scen_trans_unsteady(par, dict_lois)
        # if self.check_mobil_gate() and noyau == "unsteady":
        #     self.create_mobil_gate_file()
        # # select initial case
        # if noyau != "steady":
        #     dict_scen = self.select_init_run_case(dict_scen)
        #     if dict_scen["id_run_init"][0] != None:
        #         self.clfile.opt_to_lig(dict_scen["id_run_init"][0], self.baseName)

        # delete "initialisationAuto" file
        for file in os.listdir(self.dossierFileMasc):
            if "_init.loi" in file or "_init.xcas" in file:
                path = os.path.join(self.dossierFileMasc, file)
                if os.path.isfile(path):
                    os.remove(path)

        cl = ClassPostPreFG(self.mgis)
        # path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        # 'mascaret'))
        path = self.dossierFileMasc
        path = os.path.join(path, "cli_fg.obj")
        cl.create_cli_fg(path)
        del cl