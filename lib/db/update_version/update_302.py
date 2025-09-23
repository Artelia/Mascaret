# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : Aprile, 2025
copyright            : (C) 2025 by Artelia
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
import json
import os
from datetime import datetime


def list_sql(liste):
    """
    list to srting for sql script
    :param liste:
    :return:
    """
    txt = "("
    for t_res in liste:
        txt += "'{}',".format(t_res)
    txt = txt[:-1] + ")"
    return txt


class ClassUpdate302:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update302(self):
        """add new table law and convert"""
        self.create_var_result()
        self.convert_all_result()
        self.fill_init_date_runs()

    def create_var_result(self):
        self.mdb.execute("DELETE FROM {0}.results_var".format(self.mdb.SCHEMA))
        dossier = os.path.join(self.mgis.masplugPath, "sql")
        self.mdb.insert_var_to_result_var(dossier)

    def convert_all_result(self):
        """
        conversion between the previous results
        table format to the new for all results
        """

        try:
            rows = self.mdb.run_query(
                "SELECT DISTINCT type_res FROM {0}.results_var".format(self.mdb.SCHEMA), fetch=True
            )

            lst_typ_res = [r[0] for r in rows]
            rows = self.mdb.run_query(
                "SELECT id, run, scenario FROM {0}.runs".format(self.mdb.SCHEMA), fetch=True
            )
            dict_runs = {r[0]: {"run": r[1], "scen": r[2]} for r in rows}
            for typ_res in lst_typ_res:
                rows = self.mdb.run_query(
                    "SELECT DISTINCT id_runs FROM {0}.results_old WHERE var in "
                    "(SELECT id FROM {0}.results_var WHERE type_res = '{1}') "
                    "".format(self.mdb.SCHEMA, typ_res),
                    fetch=True,
                )
                lst_exist = [r[0] for r in rows]
                for run in dict_runs.keys():
                    if run not in lst_exist:
                        self.convert_result(run, typ_res)

            rows = self.mdb.run_query(
                "SELECT DISTINCT id_runs FROM {0}.results_sect".format(self.mdb.SCHEMA), fetch=True
            )
            lst_exist = [r[0] for r in rows]
            for run in dict_runs.keys():
                if run not in lst_exist:
                    self.fill_result_sect(run)

            # ADD runs_graph
            for id_runs in dict_runs.keys():
                if id_runs not in lst_exist:
                    sql = (
                        "SELECT DISTINCT var FROM {0}.results_old WHERE "
                        "id_runs ={1} ORDER BY var"
                    )
                    rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA, id_runs), fetch=True)
                    lst_var = [var[0] for var in rows]

                    sql = (
                        "SELECT DISTINCT ON (type_res) id, type_res FROM  "
                        "{0}.results_var "
                        "WHERE id IN {1} ORDER BY type_res"
                    )
                    rows = self.mdb.run_query(
                        sql.format(self.mdb.SCHEMA, list_sql(lst_var)), fetch=True
                    )
                    lst_typvar = [var[1] for var in rows]
                    lst_var_select = [var[0] for var in rows]
                    list_value = []
                    # comput Zmax if there is Z
                    sql = "SELECT id FROM  {0}.results_var WHERE var='Z';" "".format(
                        self.mdb.SCHEMA
                    )
                    id_z = self.mdb.run_query(sql, fetch=True)

                    for id_var, type_res in enumerate(lst_typvar):
                        sql = (
                            "SELECT id FROM  {0}.results_var WHERE id "
                            "IN {1} AND type_res = '{2}' "
                            "ORDER BY type_res".format(self.mdb.SCHEMA, list_sql(lst_var), type_res)
                        )
                        rows = self.mdb.run_query(sql, fetch=True)
                        lst_var2 = [var[0] for var in rows]
                        list_value.append([id_runs, type_res, "var", json.dumps(lst_var2)])

                        sql = (
                            "SELECT DISTINCT time FROM {0}.results_old "
                            "WHERE id_runs ={1} "
                            "AND var = {2} ORDER BY time"
                            "".format(self.mdb.SCHEMA, id_runs, lst_var_select[id_var])
                        )
                        rows = self.mdb.run_query(sql, fetch=True)
                        lst_time = [var[0] for var in rows]
                        list_value.append([id_runs, type_res, "time", json.dumps(lst_time)])

                        sql = (
                            "SELECT DISTINCT pknum FROM {0}.results_old "
                            "WHERE id_runs ={1} "
                            "AND var = {2} ORDER BY pknum"
                            "".format(self.mdb.SCHEMA, id_runs, lst_var_select[id_var])
                        )
                        rows = self.mdb.run_query(sql, fetch=True)
                        lst_pknum = [var[0] for var in rows]
                        list_value.append([id_runs, type_res, "pknum", json.dumps(lst_pknum)])

                        if type_res == "opt":
                            try:
                                dico_zmax = {}
                                for pknum in lst_pknum:
                                    if id_z[0][0] in lst_var:
                                        sql = (
                                            "SELECT MAX(val) FROM "
                                            "{0}.results_old "
                                            "WHERE var = {2} "
                                            "AND id_runs={1} AND "
                                            "pknum ={3};".format(
                                                self.mdb.SCHEMA, id_runs, id_z[0][0], pknum
                                            )
                                        )
                                        rows = self.mdb.run_query(sql, fetch=True)
                                        dico_zmax[pknum] = rows[0][0]
                                list_value.append([id_runs, "opt", "zmax", json.dumps(dico_zmax)])
                            except Exception:
                                pass
                    sql = (
                        "INSERT INTO "
                        "{0}.runs_graph(id_runs, type_res,var,val) "
                        "VALUES (%s,%s,%s, %s); \n".format(self.mdb.SCHEMA)
                    )

                    self.mdb.run_query(sql, many=True, list_many=list_value)
        except Exception as e:
            self.mgis.add_info("Error convert_all_result : {}".format(str(e)))
            return False

        return True

    def fill_init_date_runs(self):
        """
        fill the initial date in runs tab
        :return:
        """
        try:
            info = self.mdb.select("runs", list_var=["id", "t", "init_date"])
            for i, id in enumerate(info["id"]):
                ltime = info["t"][i]
                init_date = info["init_date"][i]
                if not init_date:
                    ltime = ltime.split(",")
                    init_date = ltime[0].strip()
                    try:
                        date = datetime.strptime(init_date, "%Y-%m-%d %H:%M")
                        init_date = "{:%Y-%m-%d %H:%M:00}".format(date)
                        sql = "UPDATE {0}.runs SET init_date ='{1}' " "WHERE id ={2}".format(
                            self.mdb.SCHEMA, init_date, id
                        )
                        self.mdb.run_query(sql)
                    except ValueError:
                        pass
            return True
        except Exception as e:
            self.mgis.add_info("Error fill_init_date_runs: {}".format(str(e)))
            return False

    def convert_result(self, id_run, typ_res):
        """
        conversion between the previous results table format to the new
        :param id_run: run index
        :param typ_res: result type
        :return:
        """

        if typ_res == "opt":
            tab_src = "resultats"
            col_pknum = "pk"
        elif typ_res == "basin":
            tab_src = "resultats_basin"
            col_pknum = "bnum"
        elif typ_res == "link":
            tab_src = "resultats_links"
            col_pknum = "lnum"
        elif typ_res.split("_")[0] == "tracer":
            tab_src = "resultats"
            col_pknum = "pk"
        elif typ_res in ["struct", "weirs"]:
            return
        else:
            tab_src = None
            col_pknum = None

        row = self.mdb.run_query(
            "SELECT run, scenario FROM {0}.runs WHERE id = {1}".format(self.mdb.SCHEMA, id_run),
            fetch=True,
        )
        run_run, run_scen = row[0]

        rows = self.mdb.run_query(
            "SELECT column_name FROM information_schema.columns WHERE "
            "table_schema = '{0}' AND table_name = '{1}' "
            "AND ordinal_position > ("
            "SELECT ordinal_position FROM information_schema.columns "
            "WHERE table_schema = '{0}' AND table_name = '{1}' "
            "AND column_name = '{2}')".format(self.mdb.SCHEMA, tab_src, col_pknum),
            fetch=True,
        )

        lst_var_exist = [r[0] for r in rows]
        self.mdb.execute(
            "DELETE FROM {0}.results_old WHERE results_old.id_runs = {1} AND "
            "results_old.var IN (SELECT id FROM {0}.results_var "
            "WHERE type_res = '{2}')".format(self.mdb.SCHEMA, id_run, tab_src)
        )

        rows = self.mdb.run_query(
            "SELECT id, var FROM {0}.results_var "
            "WHERE type_res = '{1}' ORDER BY id".format(self.mdb.SCHEMA, typ_res),
            fetch=True,
        )
        if typ_res.split("_")[0] == "tracer":
            lst_var = [[row[0], "c{}".format(r + 1)] for r, row in enumerate(rows)]
        else:
            lst_var = rows

        for id_var, nm_var in lst_var:
            if nm_var.lower() in lst_var_exist:
                sql = (
                    "INSERT INTO {0}.results_old ("
                    "SELECT {5}, {3}.t, {3}.{4}, {1}, {3}.{2} "
                    "FROM {0}.{3} WHERE "
                    "{3}.{2} is Not Null AND {3}.run = '{6}' "
                    "AND {3}.scenario = '{7}')".format(
                        self.mdb.SCHEMA,
                        id_var,
                        nm_var.lower(),
                        tab_src,
                        col_pknum,
                        id_run,
                        run_run,
                        run_scen,
                    )
                )
                self.mdb.execute(sql)

    def fill_result_sect(self, id_run):
        """
        fill results section table
        :param id_run: run index
        :return:
        """
        info = self.mdb.select(
            "resultats",
            where="(run, scenario) = (SELECT run, scenario "
                  "FROM {}.runs WHERE id= {})".format(self.mdb.SCHEMA, id_run),
            order="t",
            list_var=["pk", "branche", "section"],
        )
        lst_id = [id_run for i in range(len(info["pk"]))]
        lst_insert = list(set(zip(lst_id, info["pk"], info["branche"], info["section"])))
        col_sect = ["id_runs", "pk", "branch", "section"]
        if len(lst_insert) > 0:
            self.mdb.insert_res("results_sect", lst_insert, col_sect)
