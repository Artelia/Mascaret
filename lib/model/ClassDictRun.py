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
Mascaret - Pre and Postprocessing for Mascaret for QGIS

This module contains helper classes to build run configurations and manage
scenario/result deletion for Mascaret runs.

"""

import os

from qgis.PyQt.QtWidgets import (
    QInputDialog,
    QWidget
)
from ..Structure.ClassLinkFGParam import ClassLinkFGParam
from ..Structure.ClassMobilWeirsParam import ClassMobilWeirsParam
from ..Structure.ClassParamFG import ClassParamFG
from ..WaterQuality.ClassMascWQ import ClassMascWQ
from ...ui.custom_control import ClassWarningBox


class ClassDictRun:
    """Container for model run configuration and Mascaret run utilities.
.

    :param main: Main plugin object exposing paths, DB interface and settings.
    :type main: object
    :param rep_run: Optional custom run folder path. If None, a default under the plugin path is used.
    :type rep_run: str or None
    """

    def __init__(self, main, rep_run=None):
        """Initialize ClassDictRun.

        :param main: Main plugin instance containing configuration and DB access.
        :param rep_run: Optional run folder path. If None defaults to plugin/mascaret folder.
        """
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
        self.cl_fg = ClassParamFG()

        self.dmodel = {
            "general": {
                "path_runs": run_folder,
                "binary_path": os.path.join(self.mgis.masplugPath, "bin"),
                "template_path": os.path.join(self.mgis.masplugPath, "template_file", 'mascaret'),
                "api": main.cond_api,
                'dbg': main.DEBUG,
                "has_new_run_path": False,
            }
        }

    def get_dmodel(self):
        """Return the internal model dictionary.

        :return: Model dictionary.
        :rtype: dict
        """
        return self.dmodel

    def get_dgeneral(self):
        """Return the 'general' section of the model dictionary.

        :return: General configuration dictionary or empty dict if not present.
        :rtype: dict
        """
        if self.dmodel.get('general'):
            return self.dmodel['general']
        return {}

    def set_dgeneral(self, dict):
        """Update the 'general' configuration section with provided items.

        Existing keys are replaced, new keys are added.

        :param dict: Dictionary of keys/values to set into general.
        :type dict: dict
        :return: None
        """
        if self.dmodel.get('general'):
            for key, item in dict.items():
                if self.dmodel['general'].get(key):
                    self.dmodel['general'][key] = item
                else:
                    self.dmodel['general'].update({key: item})

    def get_drun(self):
        """Return the 'run' section of the model dictionary.

        :return: Run configuration dict or empty dict if not present.
        :rtype: dict
        """
        if self.dmodel.get('run'):
            return self.dmodel['run']
        return {}

    def get_lscenar(self):
        """Return the list of scenarios if defined.

        :return: List of scenario dictionaries or empty list.
        :rtype: list
        """
        if self.dmodel.get('scenario'):
            return self.dmodel['scenario']
        return []

    def del_lscenar(self, index):
        """Delete one or multiple scenarios by index.

        :param index: Single integer index or list of indices to remove.
        :type index: int or list
        :return: None
        """
        if self.dmodel.get('scenario'):
            if isinstance(index, list):
                for idx in index:
                    self.dmodel['scenario'].pop(idx)
            elif isinstance(index, int):
                self.dmodel['scenario'].pop(index)

    def get_scenario(self, scen):
        """Return scenario dictionary by scenario name.

        :param scen: Scenario name.
        :type scen: str
        :return: Scenario dict or empty dict if not found.
        :rtype: dict
        """
        id_scen = self.get_id_scenario(scen)
        if id_scen is None:
            return {}
        return self.dmodel['scenario'][id_scen]

    def get_list_name_scenario(self):
        """Return a list of scenario names.

        :return: List of scenario names.
        :rtype: list
        """
        if not self.dmodel.get('scenario'):
            return []
        return [dico["name"] for dico in self.dmodel['scenario']]

    def get_list_type_instance(self, type_inst='all'):
        """
        Iterates through all scenarios and collects instances whose 'name'
        attribute matches the specified type.

        :param type_inst: The instance type/name to filter by
        :type type_inst: str
        :return: A list of instance dictionaries matching the specified type
        :rtype: list
        """
        task_params = []
        dgeneral = self.get_dgeneral()
        drun = self.get_drun()

        # Iterate through all available scenarios
        for scen in self.get_list_name_scenario():
            # Get scenario details
            dscen = self.get_scenario(scen)
            for instance in dscen.get("instances", []):
                if instance.get('name') == type_inst or type_inst == 'all':
                    #add info scenario or general
                    instance.update({
                        "run_name" : drun.get("name_run"),
                        "scen_name": dscen.get("name"),
                        "comments" : dscen.get("comment"),
                        "BASE_NAME": dscen.get("BASE_NAME"),
                        "api": dgeneral.get('api'),
                        "dbg": dgeneral.get('dbg'),
                    })
                    task_params.append(instance)
            # Extract instances matching the specified type
            # task_params.extend(
            #     instance for instance in dscen.get("instances", [])
            #     if instance.get('name') == type_inst or type_inst == 'all'
            # )
        if type_inst == 'all':
            task_params.sort(key=lambda x: x.get('order', 0))

        return task_params

    def fill_drun(self, kernel, name_run):
        """Populate the 'run' configuration based on kernel and DB parameters.

        :param kernel: Kernel type (e.g. 'steady' or 'unsteady').
        :type kernel: str
        :param name_run: Name of the run.
        :type name_run: str
        :return: None
        """
        # Retrieve model parameters
        par = self.get_param_model(kernel)

        # Update the run configuration
        self.dmodel["run"] = {
            "name_run": name_run,
            "kernel": kernel,
            "event": par["evenement"],
            "has_casier": par["presenceCasiers"] if kernel == "unsteady" else False,
            "repriseCalcul": par["repriseCalcul"],
            "has_link_fg": self.cl_lk.fg_actif_lk(self.mdb) if par["presenceCasiers"] else False,
            "has_weir_fg": self.cl_w.fg_actif_weirs(self.mdb) if kernel == "unsteady" else False,
            "has_tracer": par["presenceTraceurs"],
            "has_fg" : self.cl_fg.fg_actif(self.mdb) if kernel == "unsteady" else False,
            "ligInit": par["LigEauInit"],
            "has_run_init": par["initialisationAuto"],
            'has_assimilation': False
        }

    def set_drun(self, new_items):
        """Set or update items in the 'run' configuration.

        :param new_items: Dictionary of items to set in drun.
        :type new_items: dict
        :return: None
        """
        for key, item in new_items.items():
            if self.dmodel["run"].get(key):
                self.dmodel["run"][key] = item
            else:
                self.dmodel["run"][key] = item

    def set_dinstance(self, scen, instance_name, dct_change):
        """Update an instance dictionary inside a scenario.

        :param scen: Scenario name or identifier.
        :type scen: str
        :param instance_name: Name of the instance to update.
        :type instance_name: str
        :param dct_change: Dictionary with changes to apply.
        :type dct_change: dict
        :return: True if update succeeded, False otherwise.
        :rtype: bool
        """
        id_scen = self.get_id_scenario(scen)
        if id_scen is None:
            return False
        id_instance = self.get_id_instance(id_scen, instance_name)
        if id_instance is None:
            return False
        self.dmodel['scenario'][id_scen]['instances'][id_instance].update(dct_change)
        return True

    def get_events(self):
        """Retrieve events from the database for runs.

        :return: Dictionary of event fields or empty dict if none found.
        :rtype: dict
        """
        scen_data = self.mdb.select("events", "run", "starttime")

        if not scen_data.get("name"):
            self.mgis.add_info("Warning: No scenario found.")
            return {}
        return scen_data

    def get_folder(self, scen):
        """Return mapping of instance name -> RUN_REP folder for a scenario.

        :param scen: Scenario name.
        :type scen: str
        :return: Dict mapping instance names to their RUN_REP path.
        :rtype: dict
        """
        d_scen = self.get_scenario(scen)
        if not d_scen.get("instances"):
            return {}

        d_folder = {}
        for instance in d_scen.get("instances"):
            name = instance.get('name')
            if not name:
                continue
            # ref: reference, init: intialisation
            # pertub1,  pertub1_init

            d_folder[name] = instance.get("RUN_REP")

        return d_folder

    def get_id_scenario(self, scen):
        """Get the index of a scenario by name.

        :param scen: Scenario name.
        :type scen: str
        :return: Index of scenario in internal list or None.
        :rtype: int or None
        """
        id_scen = None
        if not self.dmodel.get('scenario'):
            return id_scen
        for idx, dico in enumerate(self.dmodel['scenario']):
            if dico.get("name") == scen:
                id_scen = idx
                break
        return  id_scen

    def get_id_instance(self, id_scen, instance_name):
        """Get the index of an instance by name within a scenario.

        :param id_scen: Scenario index.
        :type id_scen: int
        :param instance_name: Instance name to find.
        :type instance_name: str
        :return: Instance index or None.
        :rtype: int or None
        """
        instances = self.dmodel['scenario'][id_scen].get('instances')
        if id_scen is None or not instances:
            return
        id_instance = None
        for idx, instance in enumerate(instances):
            name = instance.get('name')
            if name == instance_name:
                id_instance = idx
                break

        return id_instance

    def get_param_model(self, noyau):
        """Get model parameters from the database for the specified kernel.

        :param noyau: Kernel name used in the DB query.
        :type noyau: str
        :return: Dictionary of parameters.
        :rtype: dict
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
        """Check if a scenario exists and optionally confirm deletion of existing results.

        :param nom_scen: Scenario name to check.
        :type nom_scen: str
        :param run: Run identifier to check against DB entries.
        :type run: str
        :return: True if safe to proceed (no existing results or user confirmed deletion), False otherwise.
        :rtype: bool
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
        """Delete all database results associated with a scenario.

        :param nom_scen: Scenario name whose results to delete.
        :type nom_scen: str
        :param run: Run identifier.
        :type run: str
        :return: None
        """
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
        """Delete result variable entries related to a run.

        :param id_run: Run id in the database.
        :type id_run: int
        :return: None
        """
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
        """Remove results stored in legacy tables if present.

        :param id_run: Run id to delete legacy results for.
        :type id_run: int
        :return: None
        """
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
        """Create scenario dictionaries for provided input data.

        :param data: Iterable of input rows/dictionaries describing scenarios.
        :type data: list
        :return: List of created scenario dictionaries.
        :rtype: list
        """
        scenarios = []
        drun = self.get_drun()
        dgeneral = self.get_dgeneral()
        path_run = dgeneral["path_runs"]
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
                "BASE_NAME": "mascaret",
                "path_instance": os.path.join(path_run, f"{scen_name}"),
                "instances": []
            }

            if scenar.get("Run init"):
                d_scen.update(
                    {"scenar_init": (scenar["Run init"], scenar["Scenario init"]) if scenar["Run init"] else None,
                     "lig_file": scenar["lig file"],
                     }
                )
            # When events
            if drun['event']:
                d_event = self.get_events()
                idx = d_event['name'].index(scen_name)
                d_scen.update({"starttime": d_event["starttime"][idx],
                               "endtime": d_event["endtime"][idx]
                               })
            # #when init run
            folder_run = os.path.join(d_scen["path_instance"], 'run_ref') if drun['has_assimilation'] else d_scen[
                "path_instance"]
            order = 0
            if drun['has_run_init']:
                d_scen["instances"].append({'name': 'init',
                                            "RUN_REP": os.path.join(folder_run, 'run_init'),
                                            "has_casier": False,
                                            "has_tracer": False,
                                            "starttime": None,
                                            "order" : order,
                                            })
                order += 1
            d_scen["instances"].append({'name': 'ref',
                                        "RUN_REP": folder_run,
                                        # Update var use in API
                                        "has_casier": drun["has_casier"],
                                        "has_tracer": drun["has_tracer"],
                                        "starttime": d_scen.get("starttime") if drun['event'] else None ,
                                        "order": order,
                                        })
            scenarios.append(d_scen)

        return scenarios

    def fill_lscenario(self, data):
        """Initialize the 'scenario' list inside the model dictionary based on input data.

        :param data: Input data used to create scenarios.
        :type data: list
        :return: None
        """
        # Retrieve scenarios based on the run configuration
        scenarios = []
        if self.dmodel.get("run"):
            scenarios = self.creat_lscenar(data)
        self.dmodel['scenario'] = scenarios
