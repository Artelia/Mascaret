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
import json


class ClassStockResStruct:
    """Class contain  model files creation and run model mascaret"""
    CREST_FILE = "Fichier_Crete.csv"

    def __init__(self, mdb, mess):
        self.mdb = mdb
        self.mess = mess

    def stock_res_api(self, dico, id_run):
        """Stock api results"""


        handlers = {
            "STRUCT_FG": self.res_fg,
            "LINK_FG": self.res_link_fg,
            "WEIRS": self.res_weirs_fg,
        }

        for key, handler in handlers.items():
            if key in dico:
                handler(dico[key], id_run)

    def _insert_results(self, values):
        """Méthode commune pour insérer les résultats dans la base de données"""
        if values:
            cols = ['id_runs', 'pknum', 'var', 'time', 'val']
            self.mdb.insert_res("results_by_pk", values, cols)

    def _insert_graph_data(self, id_run, type_res, dico_pk, dico_time, var_ids, extra_data=None):
        """Méthode commune pour insérer les données de graphique"""
        list_insert = [
            [id_run, type_res, "pknum", json.dumps(dico_pk)],
            [id_run, type_res, "time", json.dumps(dico_time)],
            [id_run, type_res, "var", json.dumps(var_ids)],
        ]

        if extra_data:
            list_insert.extend(extra_data)

        col_tab = ["id_runs", "type_res", "var", "val"]
        self.mdb.insert_res("runs_graph", list_insert, col_tab)

    def _format_results_values(self, d_res, id_run):
        """Formate les résultats pour l'insertion en base"""
        values = []
        for (pk, var), v in d_res.items():
            values.append([
                id_run,
                pk,
                var,
                "{" + ",".join(str(i_t) for i_t in v["t"]) + "}",
                "{" + ",".join(str(i_v) for i_v in v["v"]) + "}",
            ])
        return values

    def _creat_mapping_var(self, var_configs):

        var_ids = []
        for var_name, type_res, name, key in var_configs:
            var_info = {
                "var": var_name,
                "type_res": type_res,
                "name": name,
                "type_var": "float",
            }
            var_ids.append(self.mdb.check_id_var(var_info))

        return var_ids

    def res_weirs_fg(self, dico_res, id_run):
        """Stock flood gate results"""
        if not dico_res:
            return

        var_configs = [
            ("ZSTR", "weirs", "Gate movement", "ZSTR"),
            ("REGVAR", "weirs", "Variable of regulation", "REGVAR"),
            ("STAT_EFF", "weirs", "Weir Erasure Status", "STAT_EFF"),
        ]

        d_res = {}
        dico_pk = {}
        dico_time = {}

        var_ids = self._creat_mapping_var(var_configs)

        for id_w, res_data in dico_res.items():
            dico_pk[id_w] = id_w
            dico_time[id_w] = res_data["TIME"]

            for idx, (_, _, _, key) in enumerate(var_configs):
                d_res[(id_w, var_ids[idx])] = {
                    "t": res_data["TIME"],
                    "v": res_data[key],
                }

        # Insérer les résultats
        values = self._format_results_values(d_res, id_run)
        self._insert_results(values)
        self._insert_graph_data(id_run, "weirs", dico_pk, dico_time, var_ids[:2])

    def res_link_fg(self, dico_res, id_run):
        """Stock flood gate results"""
        if not dico_res:
            return

        # Définir les variables
        var_configs = [
            ("ZLINK", "link_fg", "Gate movement", "ZLINK"),
            ("CSECLINK", "link_fg", "Opening section of Gate for culvert", "CSECLINK"),
            ("WIDTHLINK", "link_fg", "Width link", "WIDTHLINK"),
            ("REGVAR", "link_fg", "Variable of regulation", "REGVAR"),
        ]
        d_res = {}
        dico_pk = {}
        dico_time = {}
        dico_meth = {}

        var_ids = self._creat_mapping_var(var_configs)

        # Traiter les résultats
        for id_link, res_data in dico_res.items():
            dico_pk[id_link] = id_link
            info = self.mdb.select_one("links", where=f"gid={id_link}", list_var=["method_mob"])
            dico_meth[id_link] = info["method_mob"]
            dico_time[id_link] = res_data["TIME"]

            for idx, (_, _, _, key) in enumerate(var_configs):
                d_res[(id_link, var_ids[idx])] = {
                    "t": res_data["TIME"],
                    "v": res_data[key],
                }

        # Insérer les résultats
        values = self._format_results_values(d_res, id_run)
        self._insert_results(values)

        extra_data = [[id_run, "link_fg", "method_mob", json.dumps(dico_meth)]]
        self._insert_graph_data(id_run, "link_fg", dico_pk, dico_time, var_ids, extra_data)

    def res_fg(self, dico_res, id_run):
        """Stock flood gate results"""
        if not dico_res:
            return

        # Définir la variable
        var_info = {
            "var": "ZSTR",
            "type_res": "struct",
            "name": "valve movement",
            "type_var": "float",
        }
        id_var = self.mdb.check_id_var(var_info)

        d_res = {}
        dico_pk = {}
        dico_time = {}

        # Traiter les résultats
        for id_config, res_data in dico_res.items():
            rows = self.mdb.select(
                "struct_config",
                where=f"id={id_config}",
                list_var=["abscissa"]
            )
            pknum = rows["abscissa"][0]
            dico_pk[id_config] = pknum
            dico_time[id_config] = res_data["TIME"]

            d_res[(pknum, id_var)] = {
                "t": res_data["TIME"],
                "v": res_data["ZSTR"],
            }

        # Insérer les résultats
        values = self._format_results_values(d_res, id_run)
        self._insert_results(values)
        self._insert_graph_data(id_run, "struct", dico_pk, dico_time, [id_var])

    def _parse_crest_file(self, file_path):
        """Parse the crest file and return organized data."""
        dico_res = {}

        with open(file_path, 'r') as fich:
            for line in fich:
                parts = line.split()
                if len(parts) <= 1:
                    continue

                name = parts[2].strip()
                if name not in dico_res:
                    dico_res[name] = {"TIME": [], "ZSTR": []}

                dico_res[name]["TIME"].append(float(parts[0].strip()))
                dico_res[name]["ZSTR"].append(float(parts[1].strip()))
        return dico_res

    def _get_weir_pknum(self, name):
        """Get weir pknum from database by name."""
        where = f"name = '{name}'"
        info = self.mdb.select(
            "weirs",
            where=where,
            list_var=["gid", "abscissa"],
            order="gid"
        )

        if not info.get("gid"):
            where = f"name LIKE '{name}%'"
            info = self.mdb.select(
                "weirs",
                where=where,
                list_var=["gid", "abscissa"],
                order="gid"
            )

        return info["gid"][0] if info.get("gid") else None

    def read_mobil_gate_res(self, id_run, folder):
        """
         Read and import mobile gate results.

         Args:
             id_run: Run ID
         """
        file_path = os.path.join(folder)
        if not os.path.isfile(file_path):
            return
        try:
            dico_res = self._parse_crest_file(file_path)
            if not dico_res:
                return
            var_info = {
                "var": "ZSTR",
                "type_res": "weirs",
                "name": "valve movement",
                "type_var": "float",
            }
            id_var = self.mdb.check_id_var(var_info)
            values = []
            dico_pk = {}
            dico_time = {}
            for name, data in dico_res.items():
                pknum = self._get_weir_pknum(name)
                if pknum is None:
                    continue
                values.append([
                    id_run,
                    pknum,
                    id_var,
                    "{" + ",".join(str(t) for t in data["TIME"]) + "}",
                    "{" + ",".join(str(z) for z in data["ZSTR"]) + "}",
                ])

            if values:
                cols = ['id_runs', 'pknum', 'var', 'time', 'val']
                self.mdb.insert_res("results_by_pk", values, cols)
            self._insert_graph_data(id_run, "weirs", dico_pk, dico_time, [id_var])

        except Exception as e:
            txt = "Erreur load of mobil_gate results.\n"
            txt += e
            self.mess.add_mess("RMobGate", "warning", txt)