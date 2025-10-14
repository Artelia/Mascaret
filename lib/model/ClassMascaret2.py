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

from qgis.PyQt.QtWidgets import (
                        QInputDialog,
                        QWidget
                    )

# from .ClassCreatModel import ClassCreatModel
from ..Function import TypeErrorModel
from ..Function import copy_dir_to_dir
from ..Structure.ClassLinkFGParam import ClassLinkFGParam
from ..Structure.ClassMobilWeirsParam import ClassMobilWeirsParam

from ..WaterQuality.ClassMascWQ import ClassMascWQ
from ...ui.custom_control import ClassWarningBox
from .Fct_model_file import clear_folder
from .ClassDictRun import ClassDictRun

class ClassMascaret2:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main, rep_run=None):
        self.mgis = main
        self.mdb = self.mgis.mdb

        cl_drun = ClassDictRun(self.mgis, rep_run)


    #     self.iface = self.mgis.iface
    #     if not rep_run:
    #         # default folder
    #         run_folder= os.path.join(self.mgis.masplugPath, "mascaret")
    #     else:
    #         run_folder = rep_run
    #
    #     # if not os.path.isdir(self.run_folder):
    #     #     os.mkdir(self.run_folder)
    #     self.box = ClassWarningBox()
    #     # state list
    #     self.listeState = ["Steady", "Unsteady", "Transcritical unsteady"]
    #     # kernel list
    #     self.Klist = ["steady", "unsteady", "transcritical"]
    #
    #
    #     self.wq = ClassMascWQ(self.mgis, run_folder)
    #     self.cl_lk = ClassLinkFGParam()
    #     self.cl_w = ClassMobilWeirsParam()
    #
    #     self.save_res_struct = None
    #
    #     self.err_model = {}
    #     self.err_model["timeLaw"] = TypeErrorModel("timeLaw", " ERROR : Law Time", stop=True)
    #     self.err_model["lInflowPos"] = TypeErrorModel("lInflowPos", "WARNING : the inflow position")
    #
    #     self.dmodel  = {
    #                 "general": {
    #                     "path_runs":  run_folder,
    #                     "binary_path" : os.path.join(self.mgis.masplugPath, "bin"),
    #                     "template_path" : os.path.join(self.mgis.masplugPath, "template_file"),
    #                     "api" : main.cond_api,
    #                     'dbg' : main.DEBUG
    #                 }
    #     }
    #
    #
    # def fill_dmodel(self, kernel: str, name_run: str) -> bool:
    #     """
    #     Initializes the 'run' dictionary with model parameters and retrieves associated scenarios.
    #     """
    #     # Retrieve model parameters
    #     par = self.get_param_model(kernel)
    #
    #     # Update the run configuration
    #     self.dmodel["run"] = {
    #         "name_run": name_run,
    #         "kernel": kernel,
    #         "event": par["evenement"],
    #         "casier": par["presenceCasiers"],
    #         "repriseCalcul": par["repriseCalcul"],
    #         "link_fg": self.cl_lk.fg_actif_lk(self.mdb) if par["presenceCasiers"] else False,
    #         "weir_fg": self.cl_w.fg_actif_weirs(self.mdb),
    #         "tracer": par["presenceTraceurs"],
    #         "ligInit": par["LigEauInit"],
    #         "autoInit": par["initialisationAuto"]
    #     }
    #
    #     # Retrieve scenarios based on the run configuration
    #     scenarios = self.creat_lscenar(self.dmodel["run"])
    #     if not scenarios:
    #         return False
    #     self.dmodel['scenario'] = scenarios
    #
    #     from pprint import pprint
    #     pprint(self.dmodel)
    #     return True
    #
    # def _devent_scenar(self, name_run):
    #     # Fetch scenarios from the database
    #     scenarios = []
    #     scen_data = self.mdb.select("events", "run", "starttime")
    #
    #     if not scen_data.get("name"):
    #         self.mgis.add_info("Warning: No scenario found.")
    #         return False
    #
    #     for i, scen_name in enumerate(scen_data["name"]):
    #         scen_name = scen_name.strip()
    #
    #         if not self._check_scenar(scen_name, name_run):
    #             self.mgis.add_info(f"Simulation canceled: scenario '{scen_name}' already exists.")
    #             continue
    #
    #         scenarios.append({
    #             "name": scen_name,
    #             "starttime": scen_data["starttime"][i],
    #             "endtime": scen_data.get("endtime", [None])[i]
    #         })
    #     if not scenarios:
    #         self.mgis.add_info(f"Simulation canceled.")
    #         return scenarios
    #
    #     comments = self._fct_comment()
    #     scenarios = [{**d, 'comments': comments} for d in scenarios]
    #     return scenarios
    #
    # def _dclassic_scenar(self,name_run, init):
    #     scenarios = []
    #     # Ask user for scenario name
    #     scen_name, ok = QInputDialog.getText(QWidget(), "Scenario name", "Please input a scenario name:")
    #     scen_name = scen_name.replace("'", " ").replace('"', " ").strip()
    #
    #     if not ok or not self._check_scenar(scen_name,name_run):
    #         self.mgis.add_info(f"Simulation canceled: scenario '{scen_name}' already exists.")
    #         return scenarios
    #
    #     scenarios.append({
    #         "name": scen_name,
    #         "comments": self._fct_comment()
    #     })
    #     if "autoInit"
    #     return scenarios
    #
    # def creat_lscenar(self, drun):
    #     """
    #     Retrieves and validates scenarios based on the run configuration.
    #     Returns a list of valid scenarios or False if none are valid.
    #     """
    #     if drun["event"] and drun["kernel"] != "steady":
    #         scenarios = self._devent_scenar(drun["name_run"])
    #         return scenarios
    #
    #     scenarios = self._dclassic_scenar(drun["name_run"])
    #     return scenarios
    #
    # def get_param_model(self, noyau):
    #     """
    #     Get  model parameters
    #     Args:
    #         :param noyau : (str) kernel
    #     Return :
    #         :return (dict) model  parameters
    #     """
    #     sql = "SELECT parametre, {0} FROM {1}.{2};"
    #     rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
    #     par = {}
    #     for param, valeur in rows:
    #         try:
    #             par[param] = eval(valeur.title())
    #         except Exception:
    #             par[param] = valeur
    #     return par
    #
    # def _fct_comment(self):
    #     """
    #     Fct to add comment
    #     :return (str) comments
    #     """
    #     liste_col = self.mdb.list_columns("runs")
    #     if "comments" in liste_col:
    #         comments, ok = QInputDialog.getText(
    #             QWidget(), "Comments", "if you want to input " "a comment :"
    #         )
    #         if not isinstance(comments, str):
    #             comments = str(comments)
    #         if not ok:
    #             self.mgis.add_info("No comments.", dbg=True)
    #             comments = ""
    #     else:
    #         comments = ""
    #     return comments.replace("'", "''").replace('"', " ")
    #
    # def _check_scenar(self, nom_scen, run):
    #     """Checks if the scenario exists and asks for confirmation to delete existing results.
    #
    #     Returns:
    #         bool: True if we can proceed (no results or deletion confirmed), False otherwise
    #     """
    #     # Retrieve existing scenarios for this run
    #
    #     condition = f"run LIKE '{run}'"
    #     allscen = self.mdb.select_distinct("scenario", "runs", condition)
    #
    #     # If no scenario is found, we can proceed
    #     if not allscen:
    #         return True
    #
    #
    #     scenario_exists = (nom_scen in allscen["scenario"] or
    #                        f"{nom_scen}_init" in allscen["scenario"])
    #
    #     # If the scenario does not exist, we can proceed
    #     if not scenario_exists:
    #         return True
    #
    #     # Ask for confirmation to delete
    #     ok = self.box.yes_no_q(
    #         f"Do you want to remove the {nom_scen} results for a new simulation?"
    #     )
    #
    #     if not ok:
    #         return False
    #
    #     # Delete existing results
    #     self._delete_scenario_results(nom_scen, run)
    #     self.mgis.add_info(f"Deletion of {nom_scen} scenario for {run} is done", dbg=True)
    #
    #     return True
    #
    # def _delete_scenario_results(self, nom_scen, run):
    #     """Deletes all results associated with a scenario."""
    #     # Retrieve the run ID
    #     condition_scenario = f"(scenario LIKE '{nom_scen}' OR scenario LIKE '{nom_scen}_init')"
    #     id_run_query = (
    #         f"SELECT id FROM {self.mdb.SCHEMA}.runs "
    #         f"WHERE run = '{run}' AND {condition_scenario}"
    #     )
    #     id_run_result = self.mdb.run_query(id_run_query, fetch=True)
    #
    #     # Delete from the runs table
    #     condition = f"{condition_scenario} AND run LIKE '{run}'"
    #     self.mdb.delete("runs", condition)
    #
    #     # If no ID is found, stop here
    #     if not id_run_result:
    #         return
    #
    #     id_run = id_run_result[0][0]
    #     condition = f"id_runs = {id_run}"
    #
    #     # Delete result variables
    #     self._delete_results_var(id_run)
    #
    #     # Delete from main tables
    #     for table in ["results_sect", "runs_graph", "runs_plani", "results_by_pk"]:
    #         self.mdb.delete(table, condition)
    #
    #     # Delete from old tables if they exist
    #     self._delete_old_results(id_run)
    #
    # def _delete_results_var(self, id_run):
    #     """Deletes result variables."""
    #     var_query = (
    #         f"SELECT DISTINCT var FROM {self.mdb.SCHEMA}.results "
    #         f"WHERE id_runs = {id_run}"
    #     )
    #     var = self.mdb.run_query(var_query, fetch=True)
    #
    #     if var:
    #         list_var = [str(v[0]) for v in var]
    #         self.mdb.run_query(
    #             f"DELETE FROM {self.mdb.SCHEMA}.results_var "
    #             f"WHERE id IN ({','.join(list_var)}) AND type_res = 'tracer_TRANSPORT_PUR'"
    #         )
    #
    # def _delete_old_results(self, id_run):
    #     """Deletes results from old tables if they exist."""
    #     lst_tab = self.mdb.list_tables()
    #
    #     if "results_val" in lst_tab:
    #         condition = (
    #             f"idruntpk IN (SELECT DISTINCT id_runs FROM {self.mdb.SCHEMA}.results_idx "
    #             f"WHERE id_runs={id_run})"
    #         )
    #         self.mdb.delete("results_val", condition)
    #
    #     for table in ["results_idx", "results_old"]:
    #         if table in lst_tab:
    #             self.mdb.delete(table, f"id_runs = {id_run}")

    def generate_models_folders(self):
        dgeneral = self.dmodel['general']

        # Clear repertoire
        err = clear_folder(dgeneral['path_runs'])
        if err:
            self.mgis.add_info(f"ERROR : {err}",box=True, btype='CRITICAL')

        # generation arbre de repertoire
        # génération des fichiers de modèle

        #

        # if not dgeneral['path_runs']:
        #
        #
        # try:
        #     os.makedirs(path, exist_ok=True)
        # except OSError as e:
        #     raise OSError(f"Failed to create folder at {path}: {e}")
        #
        # clear_folder(dgeneral['path_runs'])
        # self.
        # os.chdir(dgeneral['path_runs'])











