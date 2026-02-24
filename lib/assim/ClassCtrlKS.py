# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret – CtrlKS assimilation
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

from .ClassModelAssimFct import ModelAssimBase, fmt


class CtrlKs(ModelAssimBase):
    """Handle Strickler-coefficient (Ks) perturbation and instance generation."""

    # ------------------------------------------------------------------
    # xcas manipulation
    # ------------------------------------------------------------------

    def modif_ctrl_ks(self, name_xcas, folder, modif_ks):
        """Apply Ks modifications to an xcas file.

        :param name_xcas: xcas filename.
        :param folder: Directory containing the xcas file.
        :param modif_ks of ``(num_zone, var, ks_value)`` tuples.
        """
        zones = self.get_zone_frot(name_xcas, folder)

        for numz, var, ks_modify in modif_ks:
            zones[var][numz] = ks_modify

        parametres = {
            "loi": "1",
            "nbZone" : (zones["nbZone"]),
            "numBranche": zones["numBranche"],
            "absDebZone": fmt(zones["absDebZone"]),
            "absFinZone": fmt(zones["absFinZone"]),
            "coefLitMin": fmt(zones["coefLitMin"]),
            "coefLitMaj": fmt(zones["coefLitMaj"]),
        }
        self.modif_xcas(parametres, name_xcas, folder)

    # ------------------------------------------------------------------
    # Case-list builder
    # ------------------------------------------------------------------

    def get_list_cas_ks(self, data):
        """Generate the list of Ks perturbation cases.

        :param data: Full assimilation data dict containing a ``'ctrlKS'`` key.
        :return: ``(lst_cas, d_obs)`` where *lst_cas* is a list of case dicts
                 and *d_obs* is the deduplicated observation dict.
        """
        d_ctrlks = data.get("ctrlKS") or data.get("CtrlKS", {})
        lst_cas = []
        lst_obs = []

        for d_zone in d_ctrlks["lst_zone"]:
            zone_info = d_zone["zone_info"]
            val_ksmaj = zone_info["ref_ks_maj"]
            val_ksmin = zone_info["ref_ks_min"]
            typ = d_zone["type"]

            lst_obs.append(d_zone["lst_obs"])

            pertub_list = (
                d_ctrlks["ksmin_perturb"] if typ == "Ksmin" else d_ctrlks["ksmaj_perturb"]
            )
            pertub = pertub_list[0] if pertub_list[0] != 0 else 1

            val_ref = val_ksmin if typ == "Ksmin" else val_ksmaj
            temp_val = val_ref + pertub

            lst_cas.append({
                "num_zone": d_zone["num_zone"],
                "ksmin": temp_val if typ == "Ksmin" else val_ksmin,
                "ksmaj": val_ksmaj if typ == "Ksmin" else temp_val,
                "type": typ,
            })

        d_obs = self._filter_obs(lst_obs)
        return lst_cas, d_obs

    # ------------------------------------------------------------------
    # Instance builders
    # ------------------------------------------------------------------

    def build_ctrlks_instances(
        self,
        lst_case,
        d_run,
        d_scen,
        order,
        xcas_file,
        xcas_file_init,
    ):
        """Append ctrlKS run-instance entries to *d_scen*.

        :param lst_case of Ks perturbation cases.
        :param d_run: Run configuration dict.
        :param d_scen: Scenario dict (modified in place).
        :param order: Current run-order counter.
        :param xcas_file: xcas filename for the main run.
        :param xcas_file_init: xcas filename for the initialisation run.
        :return: Updated ``(d_scen, order)`` tuple.
        """
        folder = os.path.join(d_scen["path_instance"], "run_ctrlKS")
        starttime = d_scen.get("starttime")

        for idx, case in enumerate(lst_case):
            name = f"ctrlKS_pertub{idx}"
            val = case["ksmin"] if case["type"] == "Ksmin" else case["ksmaj"]
            assim_info = {
                "num_pertub": idx,
                "type_case": case["type"],
                "num_zone": case["num_zone"],
                "ks_pertub": val,
            }
            folder_run = os.path.join(
                folder,
                f"pertub{idx}_{case['type']}_{case['num_zone']}_{str(val).replace('.', 'p')}",
            )

            if d_run["has_run_init"]:
                d_scen["instances"].append({
                    "name": f"{name}_init",
                    "name_xcas": xcas_file_init,
                    "RUN_REP": os.path.join(folder_run, "run_init"),
                    "type_ctrl": "ctrlKS",
                    "has_casier": False,
                    "has_tracer": False,
                    "starttime": None,
                    "order": order,
                    "assim_info": assim_info,
                })
                order += 1

            d_scen["instances"].append({
                "name": name,
                "name_xcas": xcas_file,
                "RUN_REP": folder_run,
                "has_casier": d_run["has_casier"],
                "has_tracer": d_run["has_tracer"],
                "has_assim": d_run["has_assimilation"],
                "starttime": starttime,
                "type_ctrl": "ctrlKS",
                "assim_info": assim_info,
                "order": order,
            })
            order += 1

        return d_scen, order

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def lst_instance_run_ctrlks_js(self):
        """Build and persist ctrlKS instance list from loaded JSON data."""
        if not self.data.get("ctrlKS"):
            return

        d_scen = self.data.dscen
        d_run = self.data.drun
        d_scen["instances"] = []
        order = self.data.initial_order()

        lst_case, _ = self.get_list_cas_ks(self.data.raw)
        d_scen, order = self.build_ctrlks_instances(
            lst_case, d_run, d_scen, order,
            xcas_file = d_scen.get("name_xcas", "mascaret.xcas"),
            xcas_file_init = d_scen.get("name_xcas_init", "mascaret_init.xcas"),
        )
        d_scen, order = self.build_analyse_instance(d_run, d_scen, order, type_assim="ctrlKS")

        self.data.dscen = d_scen
        self.export_data_json()

    def fill_assim_folder_ks(self, instance, folder):
        """Apply ks-coefficient perturbation to the instance folder.

        :param instance: Instance dict with ``'assim_info'`` and ``'name_xcas'``.
        :param folder: Target run directory.
        """
        if instance.get("type_ctrl") != "ctrlKS":
            return
        assim_info = instance.get("assim_info")
        if not assim_info:
            return
                
        numz = assim_info['num_zone']
        if assim_info['type_case'] == "Ksmaj":
            var = "coefLitMaj"
        elif assim_info['type_case'] == "Ksmin":
            var = "coefLitMin"
        modif_ks = [(numz, var, assim_info['ks_pertub'])]
        self.modif_ctrl_ks(instance.get('name_xcas', 'mascaret.xcas'), folder, modif_ks)
                    
    def fill_ana_folder_ks(self,instance, folder):
        """Placeholder: fill analysis folder for Ks assimilation.

        .. todo:: Implement folder filling logic.
        """
        if instance.get("type_ctrl") != "ctrlKS":
            return
        modif_ks = []
        for zone in  self.data['ctrlKS']['lst_zone'] :
            if not zone.get('xa'):
                continue
            numz = zone['num_zone']
            if zone ["type"] == "Ksmaj":
                var = "coefLitMaj"
            elif zone["type"] == "Ksmin":
                var = "coefLitMin"

            modif_ks.append((numz, var, zone['xa'][0]))
        if modif_ks:
            print('ooooooooooo0', modif_ks )
            self.modif_ctrl_ks(instance.get('name_xcas', 'mascaret.xcas'), folder, modif_ks)