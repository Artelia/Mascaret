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
import numpy as np
import json

from pathlib import Path
import traceback
from datetime import datetime
from .ClassCreatModelAssim import CreatModelAssim
from ..model.ClassBCWriter import ClassBCWriter
from ..Function import del_symbol


class ClassAssimDB:
    """Class Assimilation gestion base donneee"""
    XCAS_FILE = "mascaret.xcas"
    XCAS_FILE_INIT = "mascaret_init.xcas"
    DATA_ASSIM_FILE = "data_assim.json"

    def __init__(self, mdb):
        """Initialize the assimilation database handler.

        :param mdb: Database manager instance.
        :return: None.
        """
        self.data = {}
        self.mdb = mdb
        self.update_data_db()
        self.cl_creat_assim = CreatModelAssim()

    def update_data_db(self):
        """Update configuration data from the database.

        Retrieves active assimilation configurations and updates *self.data* with
        ctrlKS and ctrlLaw control types.
        :return: None.
        """
        data_config = self.mdb.select("assim_config", where="active")
        if not data_config:
            self.data = {}
            return

        for idx, ctrl_type in enumerate(data_config['control_type']):
            if ctrl_type == 'ctrlKS':
                self._update_ctrl_ks(idx, data_config)
            elif ctrl_type == 'ctrlLaw':
                self._update_ctrl_law(idx, data_config)

    def _update_ctrl_ks(self, idx, data_config):
        """Update ctrlKS configuration data.

        :param idx: Index in the data_config arrays.
        :param data_config: Configuration data dict containing control types and perturbations.
        :return: None. Modifies *self.data* ctrlKS entry.
        """
        data_ks = self.mdb.select(
            "assim_ks",
            where=f"active and (active_min or active_maj) "
        )
        if not data_ks:
            return

        if 'ctrlKS' not in self.data:
            self.data['ctrlKS'] = {}

        d_perturb = dict(zip(
            data_config['perturbation_var'][idx],
            data_config['perturbation_val'][idx]))
        obs_var = data_config['control_var'][idx]
        self.data['ctrlKS'].update({
            "obs_var": obs_var,
            "seuil_rejet_misfit": data_config['seuil_rejet_misfit'][idx],
            "iterations_sigma": data_config['iterations_sigma'][idx],
            "ksmin_perturb": d_perturb['ksMin'],
            "ksmaj_perturb": d_perturb['ksMaj'],
            'lst_zone': self._build_ks_list(data_ks, obs_var)
        })

    def _build_ks_list(self, data_ks, obs_var):
        """Build the list of Ks coefficient zones.

        :param data_ks: Ks data dict with zone information.
        :param obs_var: Observation variable key ('H' or 'Q').
        :return: List of Ks zone entry dicts.
        """
        list_ks = []

        for idx in range(len(data_ks['id_zone'])):
            if data_ks['active_min'][idx]:
                list_ks.append(self._create_ks_entry(data_ks, idx, 'Ksmin', 'min', obs_var))
            if data_ks['active_maj'][idx]:
                list_ks.append(self._create_ks_entry(data_ks, idx, 'Ksmaj', 'maj', obs_var))

        return list_ks

    def _creat_lst_obs(self, idx, data_ks, obs_var):
        """Create observation list for a given zone and variable.

        :param idx: Index in data_ks arrays.
        :param data_ks: Data dict containing observation references.
        :param obs_var: Observation variable ('H' or 'Q').
        :return: Dict of observation data with keys *id*, *code*, *stderr*, *rejectlimit*,
                 *abscissa*, *zero*.
        """
        d_obs_f = {'id': [], 'code': [], 'stderr': [], 'rejectlimit': [], 'abscissa': [], 'zero': []}
        lst_obs = data_ks[f'lst_obs_{obs_var.lower()}'][idx]

        # Définir les colonnes selon obs_var
        stderr_col = 'obsz_stderr' if obs_var == 'H' else 'obsq_stderr'
        reject_col = 'obsz_rejectlimit' if obs_var == 'H' else 'obsq_rejectlimit'
        if not lst_obs:
            return d_obs_f

        sql = f"""
            SELECT o.id, o.code, out.{stderr_col}, out.{reject_col}, out.abscissa, out.zero
            FROM {self.mdb.SCHEMA}.observations AS o
            JOIN {self.mdb.SCHEMA}.outputs AS out ON out.code = o.code
            WHERE o.id IN ({','.join(map(str, lst_obs))}) AND out.active
        """

        results, nam_col = self.mdb.run_query(sql, fetch=True, arraysize=1, namvar=True)

        if results:
            for row_ in results:
                row = row_[0]
                d_obs_f['id'].append(row[0])
                d_obs_f['code'].append(row[1].strip() if isinstance(row[1], str) else row[1])
                d_obs_f['stderr'].append(row[2])
                d_obs_f['rejectlimit'].append(row[3])
                d_obs_f['abscissa'].append(row[4])
                d_obs_f['zero'].append(row[5])
        return d_obs_f

    def _create_ks_entry(self, data_ks, idx, type_ks, val_type, obs_var):
        """Create a standardized Ks zone entry.

        :param data_ks: Ks data dict containing zone parameters.
        :param idx: Index in the data arrays.
        :param type_ks: Type of Ks zone ('Ksmin' or 'Ksmaj').
        :param val_type: Value type key ('min' or 'maj').
        :param obs_var: Observation variable for filtering.
        :return: Dict containing zone info with observations and reference values.
        """
        d_obs_f = self._creat_lst_obs(idx, data_ks, obs_var)
        # TODO: alert si d_obs_f est vide
        dico_ks = self.mdb.zone_ks()
        ref_min = dico_ks["minbedcoef"][data_ks['id_zone'][idx]]
        ref_maj = dico_ks["majbedcoef"][data_ks['id_zone'][idx]]
        return {
            "num_zone": data_ks['id_zone'][idx],
            "type": type_ks,
            "val_min": data_ks[f'val_inf_{val_type}'][idx],
            "val_max": data_ks[f'val_sup_{val_type}'][idx],
            "std": data_ks[f'std_{val_type}'][idx],
            "lst_obs": d_obs_f,
            'zone_info': {
                "abs_min": data_ks['abs_min'][idx],
                "abs_max": data_ks['abs_max'][idx],
                'branchnum': data_ks['branchnum'][idx],
                'ref_ks_min': ref_min,
                'ref_ks_maj': ref_maj,
            }
        }

    def _update_ctrl_law(self, idx, data_config):
        """Update ctrlLaw configuration data.

        :param idx: Index in the data_config arrays.
        :param data_config: Configuration data dict containing control types and perturbations.
        :return: None. Modifies *self.data* ctrlLaw entry.
        """
        data_law = self.mdb.select(
            "assim_law",
            where=f"active and (active_a or active_b)"
        )
        if not data_law:
            return

        if 'ctrlLaw' not in self.data:
            self.data['ctrlLaw'] = {}

        d_perturb = dict(zip(
            data_config['perturbation_var'][idx],
            data_config['perturbation_val'][idx]))
        obs_var = data_config['control_var'][idx]

        self.data['ctrlLaw'].update({
            "obs_var": obs_var,
            "seuil_rejet_misfit": data_config['seuil_rejet_misfit'][idx],
            "iterations_sigma": data_config['iterations_sigma'][idx],
            "lcote_perturb": d_perturb['perturbationsCote'],
            "ldebit_perturb": d_perturb['perturbationsDebit'],
            "ldebit_lin_perturb": d_perturb['perturbationsDebitLineique'],
            'lst_loi': self._build_law_list(data_law, obs_var)
        })

    def _build_law_list(self, data_law, obs_var):
        """Build the list of hydraulic laws.

        :param data_law: Law data dict with law information.
        :param obs_var: Observation variable key ('H' or 'Q').
        :return: List of law entry dicts.
        """
        list_law = []
        for idx in range(len(data_law['id_law'])):
            if data_law['active_a'][idx]:
                list_law.append(self._create_law_entry(data_law, idx, 'a', obs_var))
            if data_law['active_b'][idx]:
                list_law.append(self._create_law_entry(data_law, idx, 'b', obs_var))
        return list_law

    def get_info_law(self, id_law, source_law):
        """Get law name and type from database.

        :param id_law: Law identifier.
        :param source_law: Source type ('extremities' or 'lateral_inflows').
        :return: Tuple of ``(name, type)`` where *name* is the law name and *type* is
                 the law type code or -1 if not found.
        """
        if source_law == 'extremities':
            sql = f"SELECT name, type FROM {self.mdb.SCHEMA}.extremities WHERE active and gid={id_law}"
        elif source_law == 'lateral_inflows':
            sql = f"SELECT name FROM {self.mdb.SCHEMA}.lateral_inflows WHERE active and gid={id_law}"
        info = self.mdb.run_query(sql, fetch=True)
        if not info:
            return None, -1
        type_loi = -1
        if len(info[0]) > 1:
            type_loi = info[0][1]
        return info[0][0], type_loi

    def _create_law_entry(self, data_law, idx, typ_coef, obs_var):
        """Create a standardized law ctrl entry.

        :param data_law: Law data dict containing law parameters.
        :param idx: Index in the data arrays.
        :param typ_coef: Coefficient type ('a' or 'b').
        :param obs_var: Observation variable for filtering.
        :return: Dict containing law info with observations and reference values.
        """
        d_obs_f = self._creat_lst_obs(idx, data_law, obs_var)

        name_law, type_loi = self.get_info_law(data_law['id_law'][idx], data_law['source_law'][idx])
        return {
            "id_law": data_law['id_law'][idx],
            'source_law': data_law['source_law'][idx],
            "name_law": del_symbol(name_law),
            'type_law': type_loi,
            'type': f'coef{typ_coef.upper()}',
            "std": data_law[f'std_{typ_coef}'][idx],
            "val_min": data_law['val_min'][idx],
            "val_max": data_law['val_max'][idx],
            "lst_obs": d_obs_f,
        }

    def check_assim(self):
        """Check if any assimilation control is active.

        :return: ``True`` if ctrlKS or ctrlLaw is configured, ``False`` otherwise.
        """
        return bool(self.check_assim_ks() or self.check_assim_law())

    def check_assim_ks(self):
        """Check if ctrlKS assimilation is active.

        :return: ``True`` if ctrlKS with zones is configured, ``False`` otherwise.
        """
        cond = bool(self.data.get('ctrlKS'))
        if cond:
            return bool(self.data['ctrlKS'].get("lst_zone"))

    def check_assim_law(self):
        """Check if ctrlLaw assimilation is active.

        :return: ``True`` if ctrlLaw with laws is configured, ``False`` otherwise.
        """
        cond = bool(self.data.get('ctrlLaw'))
        if cond:
            return bool(self.data['ctrlLaw'].get("lst_loi"))
        return cond

    def add_data_dgenerate(self, d_run, d_scen):
        """Extract and store generation instance data from run and scenario dicts.

        :param d_run: Run configuration dict.
        :param d_scen: Scenario dict with instances list.
        :return: None.  *self.data['generate_instance']*.
        """
        path_ref = ''
        path_init = ''
        for idx, instance in enumerate(d_scen['instances']):
            name = instance.get('name')
            if name in 'ref':
                path_ref = instance.get("RUN_REP", '')
            elif name in 'init':
                path_init = instance.get("RUN_REP", '')
            if path_ref != '' and path_init != '':
                break

        self.data['generate_instance'] = {
            'drun': {
                key: d_run[key]
                for key in ["has_casier", "has_tracer", "has_assimilation", "has_run_init"]
            },
            'dscen': {
                "path_instance": d_scen["path_instance"],
                "starttime": d_scen.get("starttime"),
                'name_xcas_init': self.XCAS_FILE_INIT,
                'name_xcas': self.XCAS_FILE,
                "folder_init": os.path.basename(path_init),
                "folder_ref": os.path.basename(path_ref),
            },
        }

    def lst_instance_run_ctrlks(self, d_run, d_scen, order):
        """Build ctrlKS run instances and analysis instance.

        :param d_run: Run configuration dict.
        :param d_scen: Scenario dict (modified in place).
        :param order: Current run-order counter.
        :return: Updated ``(d_scen, order)`` tuple with appended instances.
        """
        if not self.check_assim_ks():
            return d_scen, order

        lst_case, d_obs = self.cl_creat_assim.get_list_cas_ks(self.data)
        d_scen = self.update_obs_assim(d_scen, d_obs, self.data['ctrlKS'].get("obs_var"))

        d_scen, order = self.cl_creat_assim.build_ctrlks_instances(
            lst_case, d_run, d_scen, order,
            xcas_file=self.XCAS_FILE,
            xcas_file_init=self.XCAS_FILE_INIT,
        )
        d_scen, order = self.cl_creat_assim.build_analyse_instance(d_run, d_scen, order, type_assim='ctrlKS',
                                                                   xcas_file=self.XCAS_FILE,
                                                                   xcas_file_init=self.XCAS_FILE_INIT,
                                                                   )
        self.add_data_dgenerate(d_run, d_scen)
        return d_scen, order

    def update_obs_assim(self, d_scen, d_obs, typ_obs):
        """Update scenario dict with observation data.

        :param d_scen: Scenario dict (modified in place).
        :param d_obs: Observation data dict to append.
        :param typ_obs: Observation variable type ('H' or 'Q').
        :return: Updated *d_scen* dict.
        """
        if d_scen.get('obs_assim'):
            d_scen['obs_assim'].append(d_obs)
            d_scen['type_obs_assim'].append(typ_obs)
        else:
            d_scen['obs_assim'] = [d_obs]
            d_scen['type_obs_assim'] = [typ_obs]

        return d_scen

    def lst_instance_run_ctrl_law(self, d_run, d_scen, order):
        """Build ctrlLaw run instances and analysis instance.

        :param d_run: Run configuration dict.
        :param d_scen: Scenario dict (modified in place).
        :param order: Current run-order counter.
        :return: Updated ``(d_scen, order)`` tuple with appended instances.
        """
        if not self.check_assim_law():
            return d_scen, order
        lst_case, d_obs = self.cl_creat_assim.get_list_cas_law(self.data)
        d_scen = self.update_obs_assim(d_scen, d_obs, self.data['ctrlLaw'].get("obs_var"))
        d_scen, order = self.cl_creat_assim.build_ctrl_law_instance(lst_case, d_run, d_scen, order,
                                                                    xcas_file=self.XCAS_FILE,
                                                                    xcas_file_init=self.XCAS_FILE_INIT,
                                                                    )
        d_scen, order = self.cl_creat_assim.build_analyse_instance(d_run, d_scen, order, type_assim='ctrlLaw',
                                                                   xcas_file=self.XCAS_FILE,
                                                                   xcas_file_init=self.XCAS_FILE_INIT,
                                                                   )
        self.add_data_dgenerate(d_run, d_scen)
        return d_scen, order

    def gen_obs_and_data(self, scen, obj_model):
        """Generate observation data and data files for a scenario.

        :param scen: Scenario identifier.
        :param obj_model: Model object with scenario and observation accessors.
        :return: None. Creates observation files in scenario directory.
        """
        path_scen = obj_model.get_event_folder(scen)
        self._export_data(path_scen)
        lst_obs = obj_model.get_obs(scen)
        var_obs = obj_model.get_obs_param(scen)
        self._create_obs_file(path_scen, lst_obs, var_obs)

    def _export_data(self, folder='.'):
        """Export assimilation data to JSON file.

        :param folder: Target directory path. Default is current directory.
        :return: None. Writes ``data_assim.json`` file.
        """
        filename = self.DATA_ASSIM_FILE
        new_data = self.data.copy()
        self._convert_datetime_to_str(new_data)
        with open(os.path.join(folder, filename), "w") as f:
            json.dump(new_data, f, indent=4)

    def _convert_datetime_to_str(self, data):
        """Recursively convert :class:`datetime` objects to ISO strings in place.

        :param data: Dict or list to process recursively.
        :return: None. Modifies *data* in place, converting datetime objects to ISO format.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    self._convert_datetime_to_str(value)
        elif isinstance(data, list):
            for item in data:
                self._convert_datetime_to_str(item)

    def _create_obs_file(self, path_scen, data_obs, var_obs):
        """Create observation files.

        :param path_scen: Path to the scenario directory where the ``Observations``
                          folder will be created if needed.
        :param data_obs: Observation configuration list with code and zero values.
        :param var_obs: Variable observation dict with type_obs, starttime, endtime.
        :return: None. Creates observation boundary condition files.
        """
        path_obs = os.path.join(path_scen, 'Observations')
        os.makedirs(path_obs, exist_ok=True)
        cl_bc = ClassBCWriter(self.mdb, path_obs)
        dict_obs = {}
        for num, obs in enumerate(data_obs):
            typ_crt = var_obs["type_obs"][num]
            for icode, code in enumerate(obs.get('code', [])):
                # decal_z = data_obs.get("zero", [0])[icode]
                dict_tmp = {'type': typ_crt, 'formule': f'{code}[t] + {obs["zero"][icode]}'}
                dict_obs[code] = dict_tmp
        cl_bc.obs_to_file(dict_obs, var_obs['starttime'], var_obs["endtime"])
