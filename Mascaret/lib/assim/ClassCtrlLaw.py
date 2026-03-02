# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret – CtrlLaw assimilation
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
from pathlib import Path

try:
    from .ClassModelAssimFct import ModelAssimBase
except ImportError:
    from ClassModelAssimFct import ModelAssimBase


class CtrlLaw(ModelAssimBase):
    """Handle hydraulic-law (boundary-condition) perturbation and instance generation."""

    # ------------------------------------------------------------------
    # Law-file manipulation
    # ------------------------------------------------------------------

    def modif_ctrl_law(self, name_law, folder, coefs):
        """Apply linear coefficients ``coefA`` / ``coefB`` to a ``.loi`` file.

        Each numeric value *v* in the file is replaced by
        ``round(coefA * v + coefB, 6)``.

        :param name_law: Law filename (e.g. ``'upstream.loi'``).
        :param folder: Directory containing the law file.
        :param coefs: Dict with optional keys ``'coefA'`` (default 1) and ``'coefB'`` (default 0).
        :return: None. Modifies the law file in place.
        """
        coef_a = coefs.get("coefA", 1)
        coef_b = coefs.get("coefB", 0)
        folder = Path(folder)
        file_law = folder / name_law
        file_tmp = folder / f"{file_law}.tmp"

        shutil.copy2(file_law, file_tmp)

        with open(file_tmp, "r") as filein, open(file_law, "w") as fileout:
            cpt = 1
            for line in filein:
                if line.startswith("#"):
                    fileout.write(line)
                    continue
                if cpt == 1:
                    fileout.write(line)
                    cpt += 1
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    parts[1] = round(coef_a * float(parts[1]) + coef_b, 6)
                    fileout.write(" ".join(str(p) for p in parts) + "\n")

        os.remove(file_tmp)

    # ------------------------------------------------------------------
    # Case-list builder
    # ------------------------------------------------------------------
    def get_list_cas_law(self, data):
        """Generate the list of boundary-law perturbation cases.

        :param data: Full assimilation data dict containing a ``'ctrlLaw'`` key.
        :return: ``(lst_cas, d_obs)``:
            - lst_cas: list of case dictionaries
            - d_obs: deduplicated observation dictionary
        """
        d_ctrl_law = data["ctrlLaw"]
        list_law = d_ctrl_law["lst_loi"]

        lst_cas = []
        lst_obs = []

        # Préchargement des perturbations pour éviter les accès répétés dict[]
        perturb_sources = {
            ("extremities", 1): ("perturbationsDebit", d_ctrl_law["ldebit_perturb"]),
            ("extremities", 2): ("perturbationsCote", d_ctrl_law["lcote_perturb"]),
            ("lateral_inflows", None): ("perturbationsDebitLineique",
                                        d_ctrl_law["ldebit_lin_perturb"]),
        }

        for d_loi in list_law:
            lst_obs.append(d_loi["lst_obs"])

            source = d_loi["source_law"]
            type_law_id = d_loi["type_law"]
            loi_type = d_loi["type"]
            name_law = d_loi["name_law"]

            # -----------------------------
            # Détermination du type de loi
            # -----------------------------
            key = (source, type_law_id if source == "extremities" else None)

            if key not in perturb_sources:
                self.add_info(f"Hydraulic law source/type not defined: {source}/{type_law_id}")
                continue

            type_law, perturb_list = perturb_sources[key]

            # -----------------------------
            # Sélection du coefficient A/B
            # -----------------------------
            if loi_type == "coefA":
                pertubf = perturb_list[0] if abs(perturb_list[0]) < 1e6 else 1
                val_coef = 1 + pertubf
            elif loi_type == "coefB":
                pertubf = perturb_list[1] if abs(perturb_list[1]) < 1e6 else 1
                val_coef = 0 + pertubf
            else:
                pertubf = 0
                val_coef = 1
            # -----------------------------
            # Construction du cas
            # -----------------------------
            dnew = d_loi.copy()
            dnew.update({
                "name_law": name_law,
                "type_law": type_law,
                "pertub": pertubf,
                "val_coef": val_coef,
            })

            lst_cas.append(dnew)

        d_obs = self._filter_obs(lst_obs)
        return lst_cas, d_obs

    # ------------------------------------------------------------------
    # Instance builders
    # ------------------------------------------------------------------

    def build_ctrl_law_instance(
            self,
            lst_case,
            d_run,
            d_scen,
            order,
            xcas_file,
            xcas_file_init,
    ):
        """Append ctrlLaw run-instance entries to *d_scen*.

        :param lst_case: List of law perturbation case dicts.
        :param d_run: Run configuration dict.
        :param d_scen: Scenario dict (modified in place).
        :param order: Current run-order counter.
        :param xcas_file: xcas filename for the main run.
        :param xcas_file_init: xcas filename for the initialisation run.
        :return: Updated ``(d_scen, order)`` tuple with appended instances.
        """
        folder = os.path.join(d_scen["path_instance"], "run_ctrlLaw")
        starttime = d_scen.get("starttime")

        for idx, case in enumerate(lst_case):
            name = f"ctrlLaw_pertub{idx}"
            val = case["val_coef"]
            folder_run = os.path.join(
                folder,
                f"pertub{idx}_{case['type']}_{case['name_law']}_{str(val).replace('.', 'p')}",
            )
            assim_info = {
                "num_pertub": idx,
                "type_case": case["type"],
                "name_law": case["name_law"],
                "id_law": case["id_law"],
                "source_law": case["source_law"],
                "coef_pertub": val,
            }

            if d_run["has_run_init"]:
                d_scen["instances"].append({
                    "name": f"{name}_init",
                    "name_xcas": xcas_file_init,
                    "RUN_REP": os.path.join(folder_run, "run_init"),
                    "type_ctrl": "ctrlLaw",
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
                "type_ctrl": "ctrlLaw",
                "assim_info": assim_info,
                "order": order,
            })
            order += 1

        return d_scen, order

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def lst_instance_run_ctrl_law_js(self):
        """Build and persist ctrlLaw instance list from loaded JSON data."""
        if not self.data.get("ctrlLaw"):
            return

        d_scen = self.data.dscen
        d_run = self.data.drun
        d_scen["instances"] = []
        order = self.data.initial_order()

        lst_case, _ = self.get_list_cas_law(self.data.raw)
        d_scen, order = self.build_ctrl_law_instance(
            lst_case, d_run, d_scen, order,
            xcas_file=d_scen.get("name_xcas", "mascaret.xcas"),
            xcas_file_init=d_scen.get("name_xcas_init", "mascaret_init.xcas"),
        )
        d_scen, order = self.build_analyse_instance(d_run, d_scen, order, type_assim="ctrlLaw",
                                                    xcas_file=d_scen.get("name_xcas", "mascaret.xcas"),
                                                    xcas_file_init=d_scen.get("name_xcas_init", "mascaret_init.xcas"),
                                                    )

        self.data.dscen = d_scen
        self.export_data_json()

    def fill_assim_folder_law(self, instance, folder):
        """Apply law-coefficient perturbation to the instance folder.

        :param instance: Instance dict with ``'assim_info'`` and ``'name_xcas'``.
        :param folder: Target run directory.
        :return: None. Modifies the law file in the folder.
        """
        if instance.get("type_ctrl") != "ctrlLaw":
            return

        assim_info = instance.get("assim_info")
        if not assim_info:
            return

        suffix = "_init.loi" if instance["name"].endswith("_init") else ".loi"
        name_law = f"{assim_info['name_law']}{suffix}"
        coefs = {
            "coefA": assim_info["coef_pertub"] if assim_info["type_case"] == "coefA" else 1,
            "coefB": assim_info["coef_pertub"] if assim_info["type_case"] == "coefB" else 0,
        }
        self.modif_ctrl_law(name_law, folder, coefs)

    def fill_ana_folder_law(self, instance, folder):
        """Apply analyzed law coefficients to analysis folder.

        Applies solution law coefficients from assimilation analysis to the instance folder.

        :param instance: Instance dict with ``'assim_info'`` and ``'name_xcas'``.
        :param folder: Target analysis directory.
        :return: None. Applies analyzed coefficients to law file.
        """
        #TODO a test lorsque BLUE loi OK
        if instance.get("type_ctrl") != "ctrlLaw":
            return

        for zone in self.data['ctrlKS']['lst_loi']:
            if not zone.get('xa'):
                continue
            assim_info = instance.get("assim_info")
            if not assim_info:
                return
            coef_a = 1
            coef_b = 0
            # TODO Attention à 'xa' ??????
            xa = zone['xa']
            coef_a = xa[0] if len(xa) > 0 else 1
            coef_b = xa[1] if len(xa) > 1 else 0

            suffix = "_init.loi" if instance["name"].endswith("_init") else ".loi"
            name_law = f"{assim_info['name_law']}{suffix}"

            coefs = {
                "coefA": coef_a,
                "coefB": coef_b,
            }
            self.modif_ctrl_law(name_law, folder, coefs)
