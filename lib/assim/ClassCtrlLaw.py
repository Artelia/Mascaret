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
        :param folder: Directory containing *name_law*.
        :param coefs with optional keys ``'coefA'`` (default 1) and
                      ``'coefB'`` (default 0).
        """
        coef_a = coefs.get("coefA", 1)
        coef_b = coefs.get("coefB", 0)

        file_law = os.path.join(folder, name_law)
        file_tmp = f"{file_law}.tmp"
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

        :param data: Full assimilation data dict containing a ``'CtrlLaw'`` key.
        :return: ``(lst_cas, d_obs)`` where *lst_cas* is a list of case dicts
                 and *d_obs* is the deduplicated observation dict.
        """
        d_ctrl_law = data["CtrlLaw"]
        lst_cas = []
        lst_obs = []

        for d_loi in d_ctrl_law["lst_loi"]:
            lst_obs.append(d_loi["lst_obs"])
            name_law = d_loi["name_law"]

            source = d_loi["source_law"]
            type_law_id = d_loi["type_law"]

            if source == "extremities":
                if type_law_id == 1:
                    type_law = "perturbationsDebit"
                    pertub = d_ctrl_law["ldebit_perturb"]
                elif type_law_id == 2:
                    type_law = "perturbationsCote"
                    pertub = d_ctrl_law["lcote_perturb"]
                else:
                    self.add_info(f"Unknown type_law '{type_law_id}' for extremities")
                    continue
            elif source == "lateral_inflows":
                type_law = "perturbationsDebitLineique"
                pertub = d_ctrl_law["ldebit_lin_perturb"]
            else:
                self.add_info(f"Hydraulic law source '{source}' not defined")
                continue

            if d_loi["type"] == "coefA":
                pertubf = pertub[0]
            elif d_loi["type"] == "coefB":
                pertubf = pertub[1]
            else:
                pertubf = 0

            pertubf = pertubf if abs(pertubf) < 1e6 else 1

            temp_values = []
            val = d_loi["val_min"]
            while val < d_loi["val_max"]:
                temp_values.append(round(val, 3))
                val += pertubf
            temp_values.append(d_loi["val_max"])

            for temp_val in temp_values:
                if (temp_val == 1 and d_loi["type"] == "coefA") or (temp_val == 0):
                    continue

                dnew = d_loi.copy()
                dnew.update({
                    "name_law": name_law,
                    "type_law": type_law,
                    "pertub": pertubf,
                    "val_coef": temp_val,
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

        :param lst_case of law perturbation cases.
        :param d_run: Run configuration dict.
        :param d_scen: Scenario dict (modified in place).
        :param order: Current run-order counter.
        :param xcas_file: xcas filename for the main run.
        :param xcas_file_init: xcas filename for the initialisation run.
        :return: Updated ``(d_scen, order)`` tuple.
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
        if not self.data.get("CtrlLaw"):
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
                                                    xcas_file=self.XCAS_FILE,
                                                    xcas_file_init=self.XCAS_FILE_INIT
                                                    )

        self.data.dscen = d_scen
        self.export_data_json()

    def fill_assim_folder_law(self, instance, folder):
        """Apply law-coefficient perturbation to the instance folder.

        :param instance: Instance dict with ``'assim_info'`` and ``'name_xcas'``.
        :param folder: Target run directory.
        """
        if instance.get("type_ctrl") != "ctrlLaw":
            return

        assim_info = instance.get("assim_info")
        if not assim_info:
            return

        is_init = instance["name"].endswith("_init")
        suffix = "_init.loi" if is_init else ".loi"
        name_law = f"{assim_info['name_law']}{suffix}"
        coefs = {
            "coefA": assim_info["coef_pertub"] if assim_info["type_case"] == "coefA" else 1,
            "coefB": assim_info["coef_pertub"] if assim_info["type_case"] == "coefB" else 0,
        }
        self.modif_ctrl_law(name_law, folder, coefs)

    def fill_analyse_law(self):
        # read data_asssim
        # copie_  run_ref
        # data.get("lst_zone")
        # name_law = f'{assim_info["name_law"]}_init.loi' if name.endswith(
        #     '_init') else f'{assim_info["name_law"]}.loi'
        # coefs = {'coefA': assim_info['coef_pertub'] if assim_info['type_case'] == 'coefA' else 1,
        #          'coefB': assim_info['coef_pertub'] if assim_info['type_case'] == 'coefB' else 0,
        #          }
        # d_law ={}
        # for law in data.get("lst_loi"):
        #    d_law['nom'] = {'coefA': 1, 'coefB': 1}
        #
        # for name_law, coefs in d_law.items():
        #   modif_ctrl_law( name_law, folder, coefs)
        pass
