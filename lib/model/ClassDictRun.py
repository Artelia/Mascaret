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

from qgis.PyQt.QtWidgets import (
    QInputDialog,
    QWidget
)
from ..Structure.ClassLinkFGParam import ClassLinkFGParam
from ..Structure.ClassMobilWeirsParam import ClassMobilWeirsParam

from ..WaterQuality.ClassMascWQ import ClassMascWQ
from ...ui.custom_control import ClassWarningBox


class ClassDictRun:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main, rep_run=None):
        self.mgis = main
        self.mdb = self.mgis.mdb
        if not rep_run:
            # default folder
            run_folder = os.path.join(self.mgis.masplugPath, "mascaret")
        else:
            run_folder = rep_run

        # if not os.path.isdir(self.run_folder):
        #     os.mkdir(self.run_folder)
        self.box = ClassWarningBox()

        self.wq = ClassMascWQ(self.mgis, run_folder)
        self.cl_lk = ClassLinkFGParam()
        self.cl_w = ClassMobilWeirsParam()

        self.dmodel = {
            "general": {
                "path_runs": run_folder,
                "binary_path": os.path.join(self.mgis.masplugPath, "bin"),
                "template_path": os.path.join(self.mgis.masplugPath, "template_file"),
                "api": main.cond_api,
                'dbg': main.DEBUG
            }
        }

    def get_dmodel(self):
        return self.dmodel

    def get_dgeneral(self):
        if self.dmodel.get('general'):
            return self.dmodel['general']
        return {}

    def get_drun(self):
        if self.dmodel.get('run'):
            return self.dmodel['run']
        return {}

    def get_lscenar(self):
        if self.dmodel.get('scenario'):
            return self.dmodel['scenario']
        return []

    def fill_drun(self, kernel, name_run):
        # Retrieve model parameters
        par = self.get_param_model(kernel)

        # Update the run configuration
        self.dmodel["run"] = {
            "name_run": name_run,
            "kernel": kernel,
            "event": par["evenement"],
            "casier": par["presenceCasiers"],
            "repriseCalcul": par["repriseCalcul"],
            "link_fg": self.cl_lk.fg_actif_lk(self.mdb) if par["presenceCasiers"] else False,
            "weir_fg": self.cl_w.fg_actif_weirs(self.mdb),
            "tracer": par["presenceTraceurs"],
            "ligInit": par["LigEauInit"],
            "autoInit": par["initialisationAuto"]
        }

    def set_drun(self, new_items):

        for key, item in new_items.items():
            if self.dmodel["run"].get(key):
                self.dmodel["run"][key] = item
            else:
                self.dmodel["run"][key] = item

    def get_events(self):
        scen_data = self.mdb.select("events", "run", "starttime")

        if not scen_data.get("name"):
            self.mgis.add_info("Warning: No scenario found.")
            return {}
        return scen_data

    def get_param_model(self, noyau):
        """
        Get  model parameters
        Args:
            :param noyau : (str) kernel
        Return :
            :return (dict) model  parameters
        """
        sql = "SELECT parametre, {0} FROM {1}.{2};"
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        par = {}
        for param, valeur in rows:
            try:
                par[param] = eval(valeur.title())
            except Exception:
                par[param] = valeur
        return par

    def check_scenar(self, nom_scen, run):
        """Checks if the scenario exists and asks for confirmation to delete existing results.

        Returns:
            bool: True if we can proceed (no results or deletion confirmed), False otherwise
        """
        # Retrieve existing scenarios for this run

        condition = f"run LIKE '{run}'"
        allscen = self.mdb.select_distinct("scenario", "runs", condition)

        # If no scenario is found, we can proceed
        if not allscen:
            return True

        scenario_exists = (nom_scen in allscen["scenario"] or
                           f"{nom_scen}_init" in allscen["scenario"])

        # If the scenario does not exist, we can proceed
        if not scenario_exists:
            return True

        # Ask for confirmation to delete
        ok = self.box.yes_no_q(
            f"Do you want to remove the {nom_scen} results for a new simulation?"
        )

        if not ok:
            return False

        # Delete existing results
        self._delete_scenario_results(nom_scen, run)
        self.mgis.add_info(f"Deletion of {nom_scen} scenario for {run} is done", dbg=True)

        return True

    def _delete_scenario_results(self, nom_scen, run):
        """Deletes all results associated with a scenario."""
        # Retrieve the run ID
        condition_scenario = f"(scenario LIKE '{nom_scen}' OR scenario LIKE '{nom_scen}_init')"
        id_run_query = (
            f"SELECT id FROM {self.mdb.SCHEMA}.runs "
            f"WHERE run = '{run}' AND {condition_scenario}"
        )
        id_run_result = self.mdb.run_query(id_run_query, fetch=True)

        # Delete from the runs table
        condition = f"{condition_scenario} AND run LIKE '{run}'"
        self.mdb.delete("runs", condition)

        # If no ID is found, stop here
        if not id_run_result:
            return

        id_run = id_run_result[0][0]
        condition = f"id_runs = {id_run}"

        # Delete result variables
        self._delete_results_var(id_run)

        # Delete from main tables
        for table in ["results_sect", "runs_graph", "runs_plani", "results_by_pk"]:
            self.mdb.delete(table, condition)

        # Delete from old tables if they exist
        self._delete_old_results(id_run)

    def _delete_results_var(self, id_run):
        """Deletes result variables."""
        var_query = (
            f"SELECT DISTINCT var FROM {self.mdb.SCHEMA}.results "
            f"WHERE id_runs = {id_run}"
        )
        var = self.mdb.run_query(var_query, fetch=True)

        if var:
            list_var = [str(v[0]) for v in var]
            self.mdb.run_query(
                f"DELETE FROM {self.mdb.SCHEMA}.results_var "
                f"WHERE id IN ({','.join(list_var)}) AND type_res = 'tracer_TRANSPORT_PUR'"
            )

    def _delete_old_results(self, id_run):
        """Deletes results from old tables if they exist."""
        lst_tab = self.mdb.list_tables()

        if "results_val" in lst_tab:
            condition = (
                f"idruntpk IN (SELECT DISTINCT id_runs FROM {self.mdb.SCHEMA}.results_idx "
                f"WHERE id_runs={id_run})"
            )
            self.mdb.delete("results_val", condition)

        for table in ["results_idx", "results_old"]:
            if table in lst_tab:
                self.mdb.delete(table, f"id_runs = {id_run}")

    def creat_lscenar(self, data):
        scenarios = []
        drun = self.get_drun()
        if not drun:
            return scenarios
        # Ask user for scenario name
        for scenar in data:
            scen_name = scenar['Scenario Name']
            if not self.check_scenar(scen_name, drun["name_run"]):
                self.mgis.add_info(f"Simulation canceled: scenario '{scen_name}' already exists.")
                continue
            d_scen = {
                "name": scen_name,
                "comments": scenar["Comment"],
                "scenar_init": (scenar["Run init"], scenar["Scenario init"]) if scenar["Run init"] else None,
                "lig_file": scenar["lig file"],
            }
            if drun['event']:
                d_event = self.get_events()
                idx = d_event['name'].index(scen_name)
                d_scen.update({"starttime": d_event["starttime"][idx],
                               "endtime": d_event["endtime"][idx]
                               })

            scenarios.append(d_scen)
        return scenarios

    def fill_lscenario(self, data):
        """
        Initializes the 'run' dictionary with model parameters and retrieves associated scenarios.
        """
        # Retrieve scenarios based on the run configuration
        scenarios = []
        if self.dmodel.get("run"):
            scenarios = self.creat_lscenar(data)
        self.dmodel['scenario'] = scenarios

