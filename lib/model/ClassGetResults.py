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

import datetime
import json
import os
import re

import pandas as pd

from ..ClassMessage import ClassMessage
from ..Graphic.ClassResProfil import ClassResProfil
from .ClassStockResStruct import ClassStockResStruct


class ClassGetResults:
    """Class for Mascaret model results import and processing."""

    # Constants


    STRUCT_RES_FILE = "res_struct.res"
    WEIRS_RES_FILE = "res_weirs.res"
    LINKS_RES_FILE = "res_links.res"
    OLD_WEIRS_RES_FILE = "Fichier_Crete.csv"

    NAME_FILE = 'mascaret'

    def __init__(self, mdb, dbg=False):
        """
        Initialize the results processor.

        Args:
            mdb: Database manager instance
            dossier_file_masc: Path to Mascaret files directory
            wq: Water quality configuration object
            dbg: Debug mode flag
        """

        self.dbg = dbg
        self.mdb = mdb
        self.mess = ClassMessage()
        self.dico_basinnum = {}
        self.dico_linknum = {}

        self._initialize_basin_link_mapping()
        self.cl_res_str = ClassStockResStruct(self.mdb, self.mess)

    def _initialize_basin_link_mapping(self):
        """Initialize basin and link number mappings between Mascaret and QGIS."""
        basins = self.mdb.select("basins", "active ORDER BY basinnum")
        links = self.mdb.select("links", "active ORDER BY linknum")

        if basins and basins.get("basinnum"):
            self.dico_basinnum = {
                id_mas: num_qgis
                for id_mas, num_qgis in enumerate(basins["basinnum"], 1)
            }

        if links and links.get("linknum"):
            self.dico_linknum = {
                id_mas: num_qgis
                for id_mas, num_qgis in enumerate(links["linknum"], 1)
            }

    def _insert_id_run(self, run, scen):
        """
        Create a new run entry in the runs table.
        Args:
            run: Run name
            scen: Scenario name

        Returns:
            ID of the created run
        """
        maintenant = datetime.datetime.now()
        tab = {run: {"scenario": scen, "date": "{:%Y-%m-%d %H:%M}".format(maintenant)}}
        listimport = ["run", "scenario", "date"]

        self.mdb.insert("runs", tab, listimport)
        info = self.mdb.select(
            "runs", where=f"run='{run}' AND scenario='{scen}'", list_var=["id"]
        )

        return info["id"][0]

    def _check_result_files(self, path):
        """
        Check which result files are present in the directory.

        Args:
            path: Directory path to check

        Returns:
            Tuple of (has_links, has_basins, has_tracer)
        """
        has_links = False
        has_basins = False
        has_tracer = False

        for file in os.listdir(path):
            extension = file.split(".")[-1]
            if extension == "liai_opt":
                has_links = True
            elif extension == "cas_opt":
                has_basins = True
            elif extension == "tra_opt":
                has_tracer = True
        return has_links, has_basins, has_tracer

    def _parse_tracer_variables(self, source, line, type_res):
        """Parse tracer variable definitions."""
        col = []
        var_to_delete = []
        dico_tra = self.mdb.select(
            "tracer_name",
            where=f"type ='{self.wq.cur_wq_mod}'",
            order="id",
            list_var=["sigle", "text"],
        )

        cpt_tracer = 0

        while "[resultats]" not in line:
            parts = line.replace('"', '').replace("NaN", "'NULL'").split(";")

            if parts[1].strip().upper().startswith('C'):
                if self.wq.cur_wq_mod != "TRANSPORT_PUR":
                    var_info = {
                        "var": dico_tra["sigle"][cpt_tracer],
                        "type_res": type_res
                    }
                else:
                    var_info = {
                        "var": dico_tra["sigle"][cpt_tracer],
                        "type_res": type_res,
                        "name": dico_tra["text"][cpt_tracer],
                        "type_var": "float",
                    }
                cpt_tracer += 1
            else:
                var_info = {"var": parts[1].upper(), "type_res": type_res}

            id_var = self.mdb.check_id_var(var_info)

            if parts[1].upper() == "QTOT":
                var_to_delete.append(id_var)

            col.append(id_var if id_var else parts[1])
            line = source.readline()

        return col, var_to_delete

    def _parse_standard_variables(self, source, line, type_res):
        """Parse standard variable definitions."""
        col = []
        var_to_delete = []

        while "[resultats]" not in line:
            parts = line.replace('"', '').replace("NaN", "'NULL'").split(";")
            var_info = {"var": parts[1].upper(), "type_res": type_res}
            id_var = self.mdb.check_id_var(var_info)

            if parts[1].upper() == "QTOT":
                var_to_delete.append(id_var)

            col.append(id_var if id_var else parts[1])
            line = source.readline()

        return col, var_to_delete

    def _process_data_values(self, data, columns):
        """Process and convert data values to appropriate types."""
        dico_val = {key: [] for key in columns}
        int_columns = ["BRANCHE", "SECTION"]

        for row in data:
            for key in dico_val.keys():
                val = row[key]

                if key == "PK":
                    val = round(float(val), 2)
                elif key in int_columns:
                    val = int(val)
                elif key == "BNUM":
                    masc_num = int(re.findall(r"\d+", val)[0])
                    val = float(str(self.dico_basinnum[masc_num]))
                elif key == "LNUM":
                    masc_num = int(re.findall(r"\d+", val)[0])
                    val = float(str(self.dico_linknum[masc_num]))
                else:
                    val = float(val)

                dico_val[key].append(val)

        return dico_val

    def new_read_opt(self, file_path, type_res, init_col=None):
        """
        Read and parse an OPT result file.
        :param file_path: file name
        :param type_res: results type
        :param init_col: first column
        :return: dictionary of values
        """
        if init_col is None:
            init_col = []
        col = []
        var_to_delete = []
        with open(file_path, "r") as source:
            var = source.readline()
            if var.startswith("/*"):
                # comment
                var = source.readline()
            ligne = source.readline()
            if type_res.startswith("tracer"):
                col, var_to_delete = self._parse_tracer_variables(source, ligne, type_res)
            else:
                col, var_to_delete = self._parse_standard_variables(source, ligne, type_res)

            # Build column list
            col_cplt = (init_col if init_col else
                        ["TIME", "BRANCH", "SECTION", "PK"]) + col

            data = pd.read_csv(source, delimiter=";", names=col_cplt)
            data = data.drop_duplicates()

            # Convert to dictionary and process values
            dico_val = self._process_data_values(
                data.to_dict(orient="records"), col_cplt
            )
        # Remove unwanted variables
        for var_id in var_to_delete:
            dico_val.pop(var_id, None)

        return dico_val

    def _compute_zmax(self, val, id_run, list_var, compute_max):
        """Compute maximum water levels."""
        var_info = {"var": "ZMAX", "type_res": "opt"}
        id_zmax = self.mdb.check_id_var(var_info)
        dico_zmax = {}

        if id_zmax in list_var:
            # Use existing ZMAX values
            max_time = val["TIME"][-1]
            for i in range(len(val["TIME"]) - 1, -1, -1):
                if val["TIME"][i] == max_time:
                    dico_zmax[val["PK"][i]] = val[id_zmax][i]
                else:
                    break
        else:
            # Compute from Z values
            var_info = {"var": "Z", "type_res": "opt"}
            id_z = self.mdb.check_id_var(var_info)

            if id_z in list_var and compute_max:
                for pknum in set(val["PK"]):
                    query = (
                        f"SELECT MAX(val) FROM {self.mdb.SCHEMA}.results "
                        f"WHERE var = {id_z} AND id_runs={id_run} "
                        f"AND pknum = {pknum};"
                    )
                    rows = self.mdb.run_query(query, fetch=True)
                    try:
                        dico_zmax[pknum] = rows[0][0]
                    except Exception:
                        dico_zmax[pknum] = None
        return dico_zmax

    def _compute_plani_stock(self, dico_zmax, id_run):
        """Compute planimetric storage."""
        try:
            cl_geo = ClassResProfil()
            dico_zmax_str = {str(k): v for k, v in dico_zmax.items()}
            txt_err = cl_geo.plani_stock(dico_zmax_str, id_run, self.mdb)
            if txt_err:
                self.mess.add_mess("ClGeoPlani", "debug", txt_err)
            del cl_geo
        except Exception as e:
            self.mess.add_mess("ClGeoPlani", "warning", str(e))

    def save_run_graph(self, val, id_run, typ_res, compute_max=True):
        """
        Save graph metadata for visualization.

        Args:
            val: Data values dictionary
            id_run: Run ID
            typ_res: Result type
            compute_max: Whether to compute maximum values
        """

        list_insert = []

        list_var = list(set([k for k in val.keys() if isinstance(k, int)]))
        # delete doublon list(set(my_list))
        list_insert.append([id_run, typ_res, "var", json.dumps(sorted(list_var))])
        list_insert.append([id_run, typ_res, "time", json.dumps(sorted(list(set(val["TIME"]))))])

        pk_key = {"opt": "PK", "basin": "BNUM", "link": "LNUM"}.get(typ_res, "PK")
        if typ_res == "opt":
            dico_zmax = self._compute_zmax(val, id_run, list_var, compute_max)
            if dico_zmax:
                list_insert.append([
                    id_run, typ_res, "zmax", json.dumps(dico_zmax)
                ])
                self._compute_plani_stock(dico_zmax, id_run)

        list_insert.append(
            [id_run, typ_res, "pknum", json.dumps(sorted(list(set(val[pk_key]))))]
        )
        col_tab = ["id_runs", "type_res", "var", "val"]
        if len(list_insert) > 0:
            self.mdb.insert_res("runs_graph", list_insert, col_tab)

    def _update_run_metadata(self, id_run, date_debut, comments, tracer):
        """Update run metadata in database."""
        tab = {id_run: {}}

        if date_debut:
            tab[id_run]["init_date"] = f"{date_debut:%Y-%m-%d %H:%M}"
        if comments:
            tab[id_run]["comments"] = comments
        if tracer:
            tab[id_run]["wq"] = self.wq.cur_wq_mod

        if tab[id_run]:
            self.mdb.update("runs", tab, var="id")

    def _load_opt_results(self, folder, id_run, base_namefile):
        """Load OPT result file."""

        file_path = os.path.join(
            folder, f'{base_namefile}.opt'
        )
        if not os.path.isfile(file_path):
            self.mess.add_mess(
                "LoadOptCas", "warning",
                f"Simulation Error: no opt results found \n {file_path}"
            )
            return
        type_res = 'opt'
        init_col = ["TIME", "BRANCH", "SECTION", "PK"]
        val = self.new_read_opt(file_path, type_res, init_col)
        self.save_new_results(val, id_run)
        self.save_run_graph(val, id_run, type_res)
        del val

    def _load_basin_results(self, folder, id_run, base_namefile):
        """Load basin result file."""
        file_path = os.path.join(
            folder, f'{base_namefile}.cas_opt'
        )

        if not os.path.isfile(file_path):
            self.mess.add_mess(
                "LoadOptCas", "warning",
                "Simulation Error: no basin results found"
            )
            return
        type_res = "basin"
        init_col = ["TIME", "BNUM"]
        val = self.new_read_opt(file_path, type_res, init_col)
        self.save_new_results(val, id_run)
        self.save_run_graph(val, id_run, type_res)
        del val

    def _load_link_results(self, folder, id_run, base_namefile):
        """Load link result file."""
        file_path = os.path.join(
            folder, f'{base_namefile}.liai_opt'
        )

        if not os.path.isfile(file_path):
            self.mess.add_mess(
                "LoadOptLink", "warning",
                "Simulation Error: no link results found"
            )
            return
        type_res = "link"
        init_col = ["TIME", "LNUM"]
        val = self.new_read_opt(file_path, type_res, init_col)
        self.save_new_results(val, id_run)
        self.save_run_graph(val, id_run, type_res)
        del val

    def _load_tracer_results(self, folder, id_run, base_namefile):
        """Load tracer result file."""
        file_path = os.path.join(
            folder, f'{base_namefile}.tra_opt'
        )

        if not os.path.isfile(file_path):
            self.mess.add_mess(
                "LoadOptWQ", "warning",
                "Simulation Error: no tracer results found"
            )
            return

        init_col = ["TIME", "BRANCH", "SECTION", "PK"]
        type_res = f"tracer_{self.wq.cur_wq_mod}"

        val = self.new_read_opt(file_path, type_res, init_col)
        self.save_new_results(val, id_run)
        self.save_run_graph(val, id_run, type_res)
        del val

    def set_results_database(
            self,
            folder,
            id_run,
            date_debut=None,
            base_namefile=None,
            comments="",
            tracer=False,
            casier=False,
            cond_api=False
    ):
        """
        Read opt files and save in results table
        :param id_run: run index
        :param date_debut: initial date
        :param base_namefile: file name without extension
        :param comments: comments
        :param tracer: if tracers are actived
        :param casier: if basins are actived
        :param  cond_api: if api are used
        :param save_res_struct : results when ther are hydraulic structur
        :return:
        """
        if base_namefile is None:
            base_namefile = self.NAME_FILE

        file_path = os.path.join(folder, f'{base_namefile}.opt')
        self.mess.add_mess("LoadOpt1", "info", "Load data ....")
        if not os.path.isfile(file_path):
            txt = f"Simulation Error: there aren't results \n path :{file_path}"
            self.mess.add_mess("LoadOptFile", "critic", txt)
            self.mdb.delete("runs", "id={}".format(id_run))

        self._update_run_metadata(id_run, date_debut, comments, tracer)

        self._load_opt_results(folder, id_run, base_namefile)

        if casier:
            self._load_basin_results(folder, id_run, base_namefile)
            self._load_link_results(folder, id_run, base_namefile)

        if tracer:
            self._load_tracer_results(folder, id_run, base_namefile)

        if cond_api:
            self._load_mobile_struct_results(folder, id_run)

    def _load_mobile_struct_results(self, folder, id_run):

        file_struct = os.path.join(folder, self.STRUCT_RES_FILE)
        file_link = os.path.join(folder, self.LINKS_RES_FILE)
        file_weirs = os.path.join(folder, self.WEIRS_RES_FILE)
        dico_res = {
            "STRUCT_FG": self._read_res_json(file_struct),
            "LINK_FG": self._read_res_json(file_link),
            "WEIRS": self._read_res_json(file_weirs),
        }
        self.cl_res_str.stock_res_api(dico_res, id_run)

        # Import mobile gate old results if available
        crest_file = os.path.join(folder, self.OLD_WEIRS_RES_FILE)
        if os.path.isfile(crest_file):
            self.cl_res_str.read_mobil_gate_res(id_run)

    def _read_res_json(self, struct_file):
        # Import API structure results if available
        dico = {}
        if os.path.isfile(struct_file):
            with open(struct_file, 'r') as file_in:
                dico = json.load(file_in)
        return dico

    def _organize_results(self, val, pk_column):
        """Organize results by PK and variable."""
        d_res = {}
        d_sect = {}
        lpk = val[pk_column]

        for var, values in val.items():
            if isinstance(var, int):
                for tps, pk, value in zip(val["TIME"], lpk, values):
                    key = (pk, var)
                    if key not in d_res:
                        d_res[key] = {"t": [], "v": []}
                    d_res[key]["t"].append(tps)
                    d_res[key]["v"].append(value)

            elif var == "BRANCH":
                init_pk = lpk[0]
                seen_init = False

                for pk, bra, sect in zip(lpk, val["BRANCH"], val["SECTION"]):
                    if pk == init_pk and seen_init:
                        break

                    if bra not in d_sect:
                        d_sect[bra] = {"sect": [], "pk": []}
                    d_sect[bra]["sect"].append(sect)
                    d_sect[bra]["pk"].append(pk)
                    seen_init = True

        return d_res, d_sect

    def _insert_organized_results(self, id_run, d_res):
        """Insert organized results into results_by_pk table."""
        values = [
            [
                id_run,
                pk,
                var,
                "{" + ",".join(str(t) for t in data["t"]) + "}",
                "{" + ",".join(str(v) for v in data["v"]) + "}",
            ]
            for (pk, var), data in d_res.items()
        ]
        if values:
            cols = ['id_runs', 'pknum', 'var', 'time', 'val']
            self.mdb.insert_res("results_by_pk", values, cols)

    def _insert_section_data(self, id_run, d_sect):
        """Insert section data into results_sect table."""
        # Check if data already exists
        existing = self.mdb.select_one(
            "results_sect",
            where=f"id_runs={id_run}",
            list_var=["id_runs"]
        )

        if existing is not None or not d_sect:
            return

        values = [
            [
                id_run,
                bra,
                "{" + ",".join(str(s) for s in data["sect"]) + "}",
                "{" + ",".join(str(p) for p in data["pk"]) + "}",
            ]
            for bra, data in d_sect.items()
        ]

        if values:
            cols = ['id_runs', 'branch', 'section', 'pk']
            self.mdb.insert_res("results_sect", values, cols)

    def save_new_results(self, val, id_run):
        """
        Save values in results table
        :param val: (dict) values
        :param id_run: run index
        :return: True
        """
        val_keys = val.keys()
        pk_column = next((col for col in ["PK", "BNUM", "LNUM"] if col in val), None)
        if not pk_column:
            return False
        # Organize results by (pk, var)
        d_res, d_sect = self._organize_results(val, pk_column)

        # Insert results
        self._insert_organized_results(id_run, d_res)

        # Insert section data
        self._insert_section_data(id_run, d_sect)

        return True
