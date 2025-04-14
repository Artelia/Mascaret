# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : fevrier, 2020
copyright            : (C) 2020 by Artelia
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
from copy import deepcopy
from datetime import datetime

from . import MasObject as Maso
from ..Function import read_version, fill_zminbed
from ..HydroLawsDialog import dico_typ_law
from ..ui.custom_control import ClassWarningBox
from ..ClassUpdateBedDialog import update_all_bed_geometry


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


class CheckTab:
    """
    Class update table
    """

    def __init__(self, mgis, mdb):
        self.mgis = mgis
        self.mdb = mdb
        self.box = ClassWarningBox()
        self.list_hist_version = [
            "0.0.0",
            "1.1.3",
            "2.0.0 ",
            "3.0.0",
            "3.0.1",
            "3.0.2",
            "3.0.3",
            "3.0.4",
            "3.0.5",
            "3.0.6",
            "3.0.7",
            "3.1.0",
            "3.1.1",
            "3.1.2",
            "4.0.0",
            "4.0.1",
            "4.0.2",
            "4.0.3",
            "4.0.4",
            "4.0.5",
            "4.0.6",
            "4.0.7",
            "4.0.8",
            "4.0.9",
            "4.0.10",
            "4.0.11",
            "4.0.12",
            "4.0.13",
            "4.0.14",
            "5.0.1",
            "5.0.2",
            "5.0.3",
            "5.0.4",
            "5.0.5",
            "5.0.6",
            "5.0.7",
            "5.0.8",
            "5.0.9",
            "5.1.1",
            "5.1.2",
            "5.1.3",
            "5.1.4",
            "5.1.5",
            "5.1.6",
            "5.1.7",
            "5.1.8",
            "5.1.9",
            "5.1.10",
            "5.1.11",
            "5.1.12",
            "5.1.13",
            "6.0.0",
            "6.0.1",
            "6.0.2",
            "6.1.0",
            "6.1.1",
            "6.2.0",
        ]
        self.dico_modif = {
            "3.0.0": {
                "add_tab": [
                    {"tab": Maso.struct_config, "overwrite": False},
                    {"tab": Maso.profil_struct, "overwrite": False},
                    {"tab": Maso.struct_param, "overwrite": False},
                    {"tab": Maso.struct_elem, "overwrite": False},
                    {"tab": Maso.struct_elem_param, "overwrite": False},
                    {"tab": Maso.struct_abac, "overwrite": False},
                    {"tab": Maso.struct_laws, "overwrite": False},
                ],
                "fct": [lambda: self.fill_struct()],
                "alt_tab": [
                    {
                        "tab": "runs",
                        "sql": ["ALTER TABLE {0}.runs ADD COLUMN IF NOT " "EXISTS comments text;"],
                    }
                ],
            },
            "3.0.1": {
                "add_tab": [
                    {"tab": Maso.struct_fg, "overwrite": False},
                    {"tab": Maso.struct_fg_val, "overwrite": False},
                    {"tab": Maso.weirs_mob_val, "overwrite": False},
                ],
                "alt_tab": [
                    {
                        "tab": "weirs",
                        "sql": [
                            "ALTER TABLE {0}.weirs ADD COLUMN IF NOT "
                            "EXISTS active_mob boolean DEFAULT FALSE;",
                            "ALTER TABLE {0}.weirs ADD COLUMN IF NOT " "EXISTS method_mob text;",
                        ],
                    }
                ],
                "fct": [lambda: self.update_setting_json()],
            },
            "3.0.2": {
                "add_tab": [
                    {"tab": Maso.results_old, "overwrite": False},
                    {"tab": Maso.results_sect, "overwrite": False},
                    {"tab": Maso.results_var, "overwrite": False},
                    {"tab": Maso.runs_graph, "overwrite": False},
                ],
                "alt_tab": [
                    {
                        "tab": "runs",
                        "sql": [
                            "ALTER TABLE {0}.runs ADD COLUMN IF NOT "
                            "EXISTS init_date timestamp "
                            "without time zone;"
                        ],
                    },
                    {
                        "tab": "outputs",
                        "sql": [
                            "ALTER TABLE {0}.outputs ADD COLUMN IF NOT "
                            "EXISTS active boolean DEFAULT TRUE;"
                        ],
                    },
                ],
                "fct": [
                    lambda: self.create_var_result(),
                    lambda: self.convert_all_result(),
                    lambda: self.fill_init_date_runs(),
                ],
            },
            "3.0.3": {},
            "3.0.4": {},
            "3.0.5": {},
            "3.0.6": {
                "add_tab": [{"tab": Maso.visu_flood_marks, "overwrite": False}],
                "alt_tab": [
                    {
                        "tab": "laws",
                        "sql": [
                            "ALTER TABLE {0}.laws ADD COLUMN IF NOT "
                            "EXISTS active boolean NOT NULL DEFAULT TRUE;",
                        ],
                    },
                    {
                        "tab": "observations",
                        "sql": [
                            "ALTER TABLE {0}.observations ADD COLUMN IF "
                            "NOT EXISTS comment text;",
                        ],
                    },
                    {
                        "tab": "branchs",
                        "sql": [
                            "UPDATE {0}.branchs SET branch = 1 " "WHERE branch IS NULL ;",
                            "UPDATE {0}.branchs SET zonenum = 1 " "WHERE zonenum IS NULL;",
                            "ALTER TABLE {0}.branchs ALTER COLUMN branch " "SET NOT NULL;",
                            "ALTER TABLE {0}.branchs ALTER COLUMN zonenum " "SET NOT NULL;",
                        ],
                    },
                    {
                        "tab": "flood_marks",
                        "sql": [
                            "ALTER TABLE {0}.flood_marks ADD COLUMN IF "
                            "NOT EXISTS active boolean NOT NULL "
                            "DEFAULT TRUE;"
                        ],
                    },
                    {
                        "tab": "outputs",
                        "sql": [
                            "ALTER TABLE {0}.outputs ADD COLUMN IF NOT "
                            "EXISTS active boolean NOT NULL "
                            "DEFAULT TRUE;"
                        ],
                    },
                ],
                "fct": [lambda: self.update_tab_306(), lambda: self.add_trigger_update_306()],
            },
            "3.0.7": {
                "fct": [
                    lambda: self.update_fct_calc_abs(),
                ]
            },
            "3.1.0": {"del_tab": ["resultats", "resultats_basin", "resultats_links"]},
            "3.1.1": {},
            "3.1.2": {},
            "4.0.0": {
                "fct": [
                    lambda: self.update_400(),
                ],
                "alt_tab": [
                    {
                        "tab": "observations",
                        "sql": [
                            "CREATE INDEX IF NOT EXISTS "
                            "observations_code_typ  "
                            "ON {0}.observations(code, type);",
                        ],
                    },
                ],
            },
            "4.0.1": {},
            "4.0.2": {
                "add_tab": [
                    {"tab": Maso.runs_plani, "overwrite": False},
                ],
                "alt_tab": [
                    {
                        "tab": "profiles",
                        "sql": [
                            "ALTER TABLE {0}.profiles ADD COLUMN IF NOT "
                            "EXISTS  zleftminbed FLOAT;",
                            "ALTER TABLE {0}.profiles ADD COLUMN IF NOT "
                            "EXISTS  zrightminbed FLOAT;",
                        ],
                    },
                ],
                "fct": [
                    lambda: fill_zminbed(self.mdb),
                    lambda: self.laws_to_new(),
                ],
            },
            "4.0.3": {},
            "4.0.4": {},
            "4.0.5": {
                "fct": [lambda: self.update_400(), lambda: self.laws_to_new()],
            },
            "4.0.6": {},
            "4.0.7": {},
            "4.0.8": {},
            "4.0.9": {},
            "4.0.10": {},
            "4.0.11": {
                "fct": [lambda: self.update_4011()],
            },
            "4.0.12": {},
            "4.0.13": {
                "fct": [lambda: self.change_branchs_chstate_active()],
            },
            "4.0.14": {},
            "5.0.1": {},
            "5.0.2": {
                "fct": [lambda: self.change_clone_shema_trigger()],
            },
            "5.0.3": {},
            "5.0.4": {},
            "5.0.5": {
                "fct": [lambda: self.update_505()],
            },
            "5.0.6": {},
            "5.0.7": {},
            '5.0.8': {},
            '5.0.9': {},
            "5.1.1": {
                "fct": [
                    lambda: self.new_branch_tab(),
                ],
            },
            "5.1.2": {
                "fct": [
                    lambda: self.update_512(),
                ]
            },
            "5.1.3": {
                "fct": [
                    lambda: self.update_513(),
                ]
            },
            "5.1.4": {},
            "5.1.5": {
                "fct": [
                    lambda: self.update_515(),
                ],
            },
            "5.1.6": {
                "fct": [
                    lambda: self.update_516(),
                ],
            },
            "5.1.7": {
                "fct": [
                    lambda: self.update_517(),
                ],
            },
            "5.1.8": {},
            "5.1.9": {},
            "5.1.10": {},
            "5.1.11": {},
            "5.1.12": {},
            "5.1.13": {},
            "6.0.0": {},
            "6.0.1": {},
            "6.0.2": {},
            "6.1.0": {},
            "6.1.1": {},
            "6.2.0": {"fct": [
                lambda: self.update_620(),
            ],
            },

            # '3.0.x': { },
        }

    def update_adim(self):
        """
        Update admin_tab and check table

        :return:
        """
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        version = read_version(self.mgis.masplugPath)
        tab_name = None
        if "admin_tab" not in tabs:
            try:
                Maso.admin_tab.overwrite = True
                obj = self.mdb.process_masobject(Maso.admin_tab, "pg_create_table")

                self.mgis.add_info("  {0} OK".format(obj.name), dbg=True)
                tabs.append("admin_tab")
            except Exception:
                self.mgis.add_info("failure!<br>{0}".format(Maso.admin_tab))
                return
            for name_tab in tabs:
                sql = (
                    "INSERT INTO {0}.admin_tab (table_, version_ )"
                    " VALUES ('{1}', '{2}')".format(self.mdb.SCHEMA, name_tab, "0.0.0")
                )
                self.mdb.execute(sql)

        curent_v_tab = self.get_version()
        try:
            pos = self.list_hist_version.index(curent_v_tab)
        except ValueError as errval:
            self.mgis.add_info("Error: The version {}".format(errval))
            raise ValueError()

        pos_fin = self.list_hist_version.index(version)
        tabs_no = deepcopy(tabs)
        if len(self.list_hist_version[pos + 1: pos_fin + 1]) > 0:
            ok = self.box.yes_no_q(
                "WARNING:\n "
                "Do you want update tables for {} schema ?\n"
                "There is a risk of table corruption.\n "
                "Remember to make backup copies if it's "
                "important model.".format(self.mdb.SCHEMA)
            )
            if ok:
                list_test_ver = []
                for ver in self.list_hist_version[pos + 1: pos_fin + 1]:
                    list_test = []
                    if ver in self.dico_modif.keys():
                        self.mgis.add_info("version : {}".format(ver))
                        modif = self.dico_modif[ver]
                        if len(modif) > 0:
                            for proc in ["add_tab", "alt_tab", "fct", "del_tab"]:
                                test_gd = True
                                if proc in modif.keys():
                                    if proc != "fct":
                                        lst_tab = modif[proc]
                                        for tab in lst_tab:
                                            if proc == "add_tab":
                                                # self.mgis.add_info('add_tab {} {}'.format(ver ,tab))
                                                valid, tab_name = self.add_tab(
                                                    tab["tab"], tab["overwrite"]
                                                )
                                            elif proc == "alt_tab":
                                                tab_name = tab["tab"]
                                                # self.mgis.add_info('alt_tab {} {}'.format(ver ,tab))
                                                valid = self.alt_tab(tab_name, tab["sql"])
                                            elif proc == "del_tab":
                                                # self.mgis.add_info('del_tab {} {}'.format(ver, tab))
                                                tab_name = tab
                                                valid = self.del_tab(tab_name)
                                            else:
                                                valid = False
                                            # print (proc, tab_name, valid)
                                            if valid:
                                                if proc != "del_tab":
                                                    self.updat_num_v(tab_name, ver)
                                                else:
                                                    self.del_num_v(tab_name)
                                            else:
                                                test_gd = False
                                            if tab_name in tabs_no:
                                                tabs_no.remove(tab_name)
                                    else:
                                        # self.mgis.add_info('fct_tab {} {}'.format(ver, tab))
                                        lst_fct = modif[proc]
                                        for fct in lst_fct:
                                            test_gd = fct()

                                    list_test.append(test_gd)
                        else:
                            list_test.append(True)
                    if False not in list_test:
                        list_test_ver.append(True)
                        self.all_version(tabs_no, ver)
                    else:
                        list_test_ver.append(False)
                        self.mgis.add_info("ERROR: Update table ************")
                        self.mgis.add_info("ERROR :{}".format(tab_name))
                if False not in list_test_ver:
                    tabs = self.mdb.list_tables(self.mdb.SCHEMA)
                    self.all_version(tabs, ver)

            else:
                self.mgis.add_info("********* Cancel of update table ***********")

    def get_version(self, table=None):
        """get version"""
        if table:
            info = self.mdb.select(
                "admin_tab", where="table_ = {}".format(table), list_var=["version_"]
            )
            curent_v_tab = info["version_"][0]

        else:
            min_ver = self.mdb.select_min("version_", "admin_tab")
            curent_v_tab = min_ver
        return curent_v_tab

    def all_version(self, tabs, version=None, clean=True):
        if not version:
            version = self.list_hist_version[0]
        for name_tab in tabs:
            self.updat_num_v(name_tab, version)
        if clean:
            sql = "SELECT table_ FROM {0}.admin_tab".format(self.mdb.SCHEMA)
            row = self.mdb.run_query(sql, fetch=True)
            for tab in row:
                if tab[0] not in tabs:
                    self.del_num_v(tab[0])

    def updat_num_v(self, name_tab, version):
        """
        updat version number
        :return:
        """

        sql = "SELECT * FROM {0}.admin_tab WHERE  table_ = '{1}' ".format(self.mdb.SCHEMA, name_tab)
        row = self.mdb.run_query(sql, fetch=True)
        if len(row) > 0:
            sql = "UPDATE {0}.admin_tab SET version_  = '{1}' " "WHERE table_ = '{2}';".format(
                self.mdb.SCHEMA, version, name_tab
            )
            self.mdb.execute(sql)
        else:
            sql = "INSERT INTO {0}.admin_tab (table_, version_)" " VALUES ('{1}', '{2}')".format(
                self.mdb.SCHEMA, name_tab, version
            )
            self.mdb.execute(sql)

    def del_num_v(self, name_tab):
        """
        delete table in admin_tab
        :param name_tab: table name
        :return:
        """

        sql = "SELECT * FROM {0}.admin_tab WHERE  table_ = '{1}' ".format(self.mdb.SCHEMA, name_tab)
        row = self.mdb.run_query(sql, fetch=True)
        if len(row) > 0:
            sql = "DELETE FROM {0}.admin_tab WHERE table_ = '{1}';".format(
                self.mdb.SCHEMA, name_tab
            )
            self.mdb.execute(sql)

    def add_tab(self, tab, overwrite=True):
        """
        Add table
        :param tab: list of tables
        :param overwrite : overwrite table
        """

        valid = True
        try:
            tab.overwrite = overwrite
            obj = self.mdb.process_masobject(tab, "pg_create_table")
            self.mgis.add_info("  {0} OK".format(obj.name), dbg=True)
            return valid, obj.name
        except Exception:
            valid = False
            self.mgis.add_info("failure!<br>Add table {0}".format(tab))

            return valid, None

    def alt_tab(self, tab, lst_sql):
        """
        Apply sql script
        :param tab: table name
        :param lst_sql: sql script list
        :return:
        """
        valid = True
        txt_sql = ""
        for sql in lst_sql:
            txt_sql += sql.format(self.mdb.SCHEMA) + "\n"

        try:
            if txt_sql != "":
                res = self.mdb.run_query(txt_sql)
                if res is None:
                    valid = False
                    self.mgis.add_info("failure!<br>Alt table {0}".format(tab))
        except Exception:
            valid = False
            self.mgis.add_info("failure!<br>Alt table {0}".format(tab))

        return valid

    def del_tab(self, tab):
        """
        delete table
        :param tab:  table name
        :return:
        """
        try:
            valid = self.mdb.drop_table(tab)
        except Exception:
            valid = False
            self.mgis.add_info("failure!<br>Del table {0}".format(tab))

        return valid

    def create_var_result(self):
        self.mdb.execute("DELETE FROM {0}.results_var".format(self.mdb.SCHEMA))
        dossier = os.path.join(self.mgis.masplugPath, "db", "sql")
        self.mdb.insert_var_to_result_var(dossier)

    def convert_all_result(self):
        """
        conversion between the previous results
        table format to the new for all results
        """
        convert = False
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
            convert = True
        except Exception as e:
            self.mgis.add_info("Error convert_all_result : {}".format(str(e)))
            return False

        return True

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
            "WHERE type_res = '{2}' ORDER BY id".format(self.mdb.SCHEMA, tab_src, typ_res),
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

    def update_setting_json(self):
        """
        update setting in json
        :return:
        """
        name_file = os.path.join(self.mgis.masplugPath, "settings.json")
        modif = False
        if os.path.isfile(name_file):
            # read
            with open(name_file) as file:
                data = json.load(file)
            # change
            if "cond_api" not in data["mgis"].keys():
                data["cond_api"] = False
                modif = True
            # write
            if modif:
                with open(name_file, "w") as file:
                    json.dump(data, file)
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

    def fill_struct(self):
        """
        add and fill struct column in profiles tab
        :return:
        """
        try:
            self.mdb.insert_abacus_table(self.mgis.dossier_struct)
            list_col = self.mdb.list_columns("profiles")
            sql = ""
            if "struct" in list_col:
                sql = "ALTER TABLE {0}.profiles DROP COLUMN " "IF EXISTS  struct;\n"
            sql += "ALTER TABLE {0}.profiles ADD COLUMN struct integer " "DEFAULT 0;"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            return True
        except Exception as e:
            self.mgis.add_info("Error fill_struct: {}".format(str(e)))
            return False

    def debug_update_vers_meta(self, version=None):
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        if not version:
            version = read_version(self.mgis.masplugPath)
        self.all_version(tabs, version)

    def update_tab_306(self):
        try:
            list_tab = [
                "branchs",
                "profiles",
                "tracer_lateral_inflows",
                "lateral_weirs",
                "lateral_inflows",
                "hydraulic_head",
                "weirs",
                "extremities",
                "links",
                "basins",
                "outputs",
                "flood_marks",
                "laws",
            ]
            txt = ""
            for tab in list_tab:
                txt += "ALTER TABLE {0}.{1} ALTER COLUMN active " "SET DEFAULT TRUE;".format(
                    self.mdb.SCHEMA, tab
                )
                txt += "\n"
                txt += "UPDATE {0}.{1} SET active = TRUE WHERE " "active IS NULL;".format(
                    self.mdb.SCHEMA, tab
                )
                txt += "\n"
                txt += "ALTER TABLE {0}.{1} ALTER COLUMN " "active SET NOT NULL;".format(
                    self.mdb.SCHEMA, tab
                )
                txt += "\n"
                return True
        except Exception as e:
            self.mgis.add_info("Error update_tab_306: {}".format(str(e)))
            return False

    def add_trigger_update_306(self):
        """
        add trigger and fct for 3.0.6 version
        trigger :
        'pg_delete_visu_flood_marks',
        'pg_create_calcul_abscisse_point_flood'
        :return:
        """
        try:
            self.update_fct_calc_abs()
            self.mdb.add_fct_for_visu()

            qry = "DROP TRIGGER IF EXISTS branchs_chstate_active " "ON {}.branchs;\n".format(
                self.mdb.SCHEMA
            )
            qry += "DROP TRIGGER IF EXISTS basins_chstate_active " "ON {}.basins;\n".format(
                self.mdb.SCHEMA
            )
            qry += (
                "DROP TRIGGER IF EXISTS flood_marks_calcul_abscisse "
                "ON {}.flood_marks;\n".format(self.mdb.SCHEMA)
            )
            qry += (
                "DROP TRIGGER IF EXISTS flood_marks_calcul_abscisse_flood "
                "ON {}.flood_marks;\n".format(self.mdb.SCHEMA)
            )
            qry += (
                "DROP TRIGGER IF EXISTS flood_marks_delete_point_flood "
                "ON {}.flood_marks;\n".format(self.mdb.SCHEMA)
            )
            qry += "\n"
            cl = Maso.class_fct_psql()
            qry += cl.pg_chstate_branch()
            qry += "\n"
            qry += (
                "CREATE TRIGGER branchs_chstate_active\n"
                " AFTER UPDATE\n  ON {0}.branchs\n".format(self.mdb.SCHEMA)
            )
            qry += (
                " FOR EACH ROW\n"
                "WHEN (OLD.active IS DISTINCT FROM NEW.active)\n"
                "EXECUTE PROCEDURE chstate_branch();\n"
            )
            qry += "\n"
            qry += cl.pg_chstate_basin()
            qry += "\n"
            qry += (
                "CREATE TRIGGER basins_chstate_active\n"
                " AFTER UPDATE\n  ON {0}.basins\n".format(self.mdb.SCHEMA)
            )
            qry += (
                " FOR EACH ROW\n"
                "WHEN (OLD.active IS DISTINCT FROM NEW.active)\n"
                "EXECUTE PROCEDURE chstate_basin();\n"
            )
            qry += "\n"
            cl = Maso.flood_marks()
            cl.schema = self.mdb.SCHEMA
            qry += cl.pg_clear_tab()
            qry += "\n"
            qry += cl.pg_calcul_abscisse_flood()
            qry += "\n"
            self.mdb.run_query(qry)

            return True
        except Exception as e:
            self.mgis.add_info("Error add_trigger_update_306: {}".format(str(e)))
            return False

    def add_fct_for_update_pk_old(self):
        """add fct psql to compute abscissa"""
        cl = Maso.class_fct_psql()
        lfct = [
            cl.pg_abscisse_profil(self.mdb.SCHEMA),
            cl.pg_all_profil(self.mdb.SCHEMA),
            cl.pg_abscisse_point(self.mdb.SCHEMA),
            cl.pg_all_point(self.mdb.SCHEMA),
        ]
        qry = ""
        for sql in lfct:
            qry += sql()
            qry += "\n"
        self.mdb.run_query(qry)

    def update_fct_calc_abs(self):
        try:
            lst_fct = [
                "public.update_abscisse_branch(_tbl_branchs regclass)",
                "public.update_abscisse_point" "(_tbl regclass, _tbl_branchs regclass)",
                "public.update_abscisse_profil" "(_tbl regclass, _tbl_branchs regclass)",
                "public.abscisse_branch" "(_tbl_branchs regclass, id_branch integer)",
                "public.abscisse_point" "(_tbl regclass, _tbl_branchs regclass, id_point integer)",
                "public.abscisse_profil" "(_tbl regclass, _tbl_branchs regclass, id_prof integer)",
            ]
            qry = ""
            for fct in lst_fct:
                qry += "DROP FUNCTION IF EXISTS {};\n".format(fct)
            self.mdb.run_query(qry)
            self.add_fct_for_update_pk_old()
            return True
        except Exception as e:
            self.mgis.add_info("Error update_fct_calc_abs: {}".format(str(e)))
            return False

    def clean_tab_admin(self):
        """
        clean tab in admin
        :return:
        """
        sql = (
            "DELETE FROM {0}.admin_tab WHERE NOT(table_ IN ( "
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = '{0}'))".format(self.mdb.SCHEMA)
        )
        self.mdb.run_query(sql)

    def update_400(self):
        """update 4.0.0 version"""
        try:
            self.clean_tab_admin()
            cl = Maso.class_fct_psql()
            lfct = [cl.pg_clone_schema()]
            qry = ""
            for sql in lfct:
                qry += sql
                qry += "\n"
            self.mdb.run_query(qry)
            ltabs = self.mdb.list_tables(self.mdb.SCHEMA)
            if "results_old" in ltabs:
                sql = """CREATE INDEX IF NOT EXISTS results_old_id_runs_pknum 
                        ON {0}.results_old(id_runs, pknum);
                        CREATE INDEX IF NOT EXISTS results_old_id_runs_time  
                        ON {0}.results_old(id_runs, time);""".format(
                    self.mdb.SCHEMA
                )
            self.mdb.run_query(qry)

            return True
        except Exception as e:
            self.mgis.add_info("Error  update_400: {}".format(str(e)))
            return False

    def laws_to_new(self):
        """add new table law and convert"""
        try:
            lst_tab = self.mdb.list_tables()
            if "laws" in lst_tab:
                info = self.mdb.select("laws")
            else:
                info = {}
            # conv_dict = {'time': 'time',
            #              'Q': 'flowrate',
            #              'Z': 'z',
            #              'Zup': 'z_upstream',
            #              'Zdown': 'z_downstream',
            #              'Zlow': 'z_lower',
            #              'Zupp': 'z_up',
            #              }

            if "law_config" not in lst_tab:
                vconf, _ = self.add_tab(Maso.law_config, False)
                if not vconf:
                    self.mgis.add_info("Error  add table: law_config")
                    return False
                if "id" in info.keys():
                    # law_config
                    tab = {id: {"comment": ""} for id in range(len(info["name"]))}
                    cmpt = 1
                    for key, item in info.items():
                        if key in [
                            "z",
                            "flowrate",
                            "time",
                            "z_upstream",
                            "z_downstream",
                            "z_lower",
                            "z_up",
                        ]:
                            pass
                        elif key in ["starttime", "endtime"]:
                            for id, val in enumerate(item):
                                if val:
                                    tab[id][key] = val.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    tab[id][key] = None
                        elif key in ["active"]:
                            for id, val in enumerate(item):
                                tab[id][key] = val
                        elif key == "name":
                            for id, val in enumerate(item):
                                if val in [
                                    tmp["name"] for tmp in tab.values() if "name" is tmp.keys()
                                ]:
                                    tab[id]["name"] = val + "{}".format(cmpt)
                                    cmpt += 1
                                else:
                                    tab[id]["name"] = val
                                tab[id]["geom_obj"] = val
                        elif key == "type":
                            for id, val in enumerate(item):
                                tab[id]["id_law_type"] = val

                    listimport = [
                        "id",
                        "name",
                        "geom_obj",
                        "starttime",
                        "endtime",
                        "id_law_type",
                        "active",
                        "comment",
                    ]

                    if len(tab.keys()) > 0:
                        err = self.mdb.insert("law_config", tab, listimport)
                        if len(tab.keys()) > 0:
                            maxk = max(tab.keys())
                            sql = "ALTER SEQUENCE {}.law_config_id_seq " "RESTART WITH {};".format(
                                self.mdb.SCHEMA, maxk + 1
                            )
                            self.mdb.run_query(sql)
                        if err:
                            self.mgis.add_info("Error: Insert law_config")
                            self.del_tab("law_config")
                            return False

            if "law_values" not in lst_tab:
                vval, _ = self.add_tab(Maso.law_values, False)
                if not vval:
                    self.mgis.add_info("Error  add table: law_values")
                    return False

                if "id" in info.keys():
                    # law_value
                    valinsert = {"id_law": [], "id_var": [], "id_order": [], "value": []}
                    for id_loi in range(len(info["name"])):
                        id_type = info["type"][id_loi]
                        lst_var = [tmp["code"] for tmp in dico_typ_law[id_type]["var"]]

                        for id_var, var in enumerate(lst_var):
                            # lst_val = info[conv_dict[var]][id_loi].split()
                            lst_val = info[var][id_loi].split()
                            for id_val, val in enumerate(lst_val):
                                valinsert["id_law"].append(id_loi)
                                valinsert["id_var"].append(id_var)
                                valinsert["id_order"].append(id_val)
                                valinsert["value"].append(float(val))
                    if len(valinsert["id_law"]) > 0:
                        err = self.mdb.insert2("law_values", valinsert)
                        if err:
                            self.mgis.add_info("Error  Insert law_values")
                            self.del_tab("law_values")
                            return False
            return True
        except Exception as e:
            self.mgis.add_info("Error laws_to_new: {}".format(str(e)))
            return False

    def update_4011(self):
        sorti = True
        lst_tab = self.mdb.list_tables()
        err, _ = self.add_tab(Maso.results_idx, False)
        if not err:
            sorti = False
        err, _ = self.add_tab(Maso.results_val, False)
        if not err:
            sorti = False
        if "results_old" not in lst_tab:
            sql = "ALTER TABLE {0}.results RENAME TO results_old;"
            sql = sql.format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                sorti = False
        info = self.mdb.select_one("results_old")
        if info:
            sql = "SELECT FROM {0}.results_old"
            # creation results_idx
            sql = (
                'INSERT INTO {0}.results_idx(id_runs, "time", pknum) '
                'SELECT DISTINCT id_runs,  "time", pknum  FROM {0}.results_old;'
            )
            sql = sql.format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                sorti = False
            sql = (
                "INSERT INTO {0}.results_val(idruntpk, var, val) "
                "SELECT idruntpk, var, val   FROM {0}.results_idx "
                "Inner join  {0}.results_old "
                "on {0}.results_old.id_runs = {0}.results_idx.id_runs "
                "AND {0}.results_old.time = {0}.results_idx.time "
                "AND {0}.results_old.pknum = {0}.results_idx.pknum;"
            )
            sql = sql.format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                sorti = False
        sql = (
            "CREATE OR REPLACE VIEW {0}.results "
            'AS SELECT id_runs, "time", pknum,  var, val  FROM {0}.results_idx 	'
            "Inner join  {0}.results_val "
            "on {0}.results_val.idruntpk = {0}.results_idx.idruntpk;"
        )
        sql = sql.format(self.mdb.SCHEMA)
        err = self.mdb.run_query(sql)
        if err:
            sorti = False
        return sorti

    def change_branchs_chstate_active(self):
        sql = (
            "DROP TRIGGER IF EXISTS branchs_chstate_active "
            "ON {0}.branchs; "
            "CREATE TRIGGER branchs_chstate_active "
            "AFTER UPDATE OF active ON {0}.branchs "
            "FOR EACH ROW EXECUTE PROCEDURE public.chstate_branch();".format(self.mdb.SCHEMA)
        )
        self.mdb.run_query(sql)

    def change_clone_shema_trigger(self):
        """update 5.0.2 version"""

        self.change_branchs_chstate_active()
        valid = self.update_clone()
        if not valid:
            self.mgis.add_info("Error  update_502")

    def update_clone(self):
        """update clone function"""
        try:
            cl = Maso.class_fct_psql()
            lfct = [cl.pg_clone_schema()]
            qry = ""
            for sql in lfct:
                qry += sql
                qry += "\n"
            self.mdb.run_query(qry)
            return True
        except Exception as e:
            self.mgis.add_info("Error update clone function : ".format(str(e)))
            return False

    def update_505(self):
        """update 5.0.5 version"""
        valid = True
        if valid:
            lst_tab = self.mdb.list_tables(schema=self.mdb.SCHEMA)
            if "runs_graph" not in lst_tab:
                valid, tab_name = self.add_tab(Maso.runs_graph, False)
                self.updat_num_v(tab_name, "5.1.2")

        test = self.mdb.select("parametres", where="parametre ='decentrement'")
        if valid and not len(test["id"]) > 0:
            try:
                fichparam = os.path.join(self.mgis.dossier_sql, "parametres.csv")
                # self.run_query(req.format(self.SCHEMA, fichparam))
                liste_value = []
                with open(fichparam, "r") as file:
                    for ligne in file:
                        liste_value.append(ligne.replace("\n", "").split(";"))
                liste_col = self.mdb.list_columns("parametres")
                var = ",".join(liste_col)
                valeurs = "("
                for k in liste_col:
                    valeurs += "%s,"
                valeurs = valeurs[:-1] + ")"

                self.mdb.delete("parametres")

                sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(
                    self.mdb.SCHEMA, "parametres", var, valeurs
                )

                self.mdb.run_query(sql, many=True, list_many=liste_value)
            except Exception:
                valid = False
        return valid

    def new_branch_tab(self):
        """
        updat 5.1.1
        """
        self.mgis.add_info("*** Update 5.1.1  ***")
        valid = True
        check_fill = False

        lst_tab = self.mdb.list_tables(schema=self.mdb.SCHEMA)
        lst_admin_tab = self.mdb.select("admin_tab", list_var=["table_"])
        if "results_old" in lst_tab:
            self.mdb.drop_table("result_old")
        if "results_old" in lst_admin_tab["table_"]:
            self.mdb.delete("admin_tab", where="table_= 'results_old'")
            new_ver = self.get_version()
            if new_ver == "5.1.1":
                return valid

        lst_profil_err = self.mdb.check_valid_profil()
        if valid:
            lst_trigger_b = self.mdb.list_trigger("branchs", self.mdb.SCHEMA)
            #  RENAME old branchs table
            sql = "ALTER TABLE IF EXISTS {0}.branchs RENAME TO branchs_old;".format(self.mdb.SCHEMA)
            sql += "\n"
            sql += "ALTER TABLE IF EXISTS {0}.branchs_old RENAME CONSTRAINT branchs_pkey TO branchs_old_pkey;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "ALTER TABLE IF EXISTS {0}.branchs_old RENAME CONSTRAINT cle_debut TO cle_debut_old;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "ALTER TABLE IF EXISTS {0}.branchs_old RENAME CONSTRAINT cle_fin TO cle_fin_old;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += (
                "ALTER INDEX IF EXISTS {0}.branchs_geom_idx RENAME TO branchs_old_geom_idx;".format(
                    self.mdb.SCHEMA
                )
            )
            sql += "\n"
            sql += "ALTER SEQUENCE IF EXISTS  {0}.branchs_gid_seq RENAME TO branchs_old_gid_seq;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            # delete TRIGGER
            if "branchs_calcul_abscisse" in lst_trigger_b:
                # sql += "DROP TRIGGER IF EXISTS branchs_calcul_abscisse ON {}.branchs_old;".format(self.mdb.SCHEMA)
                sql += "ALTER TABLE {}.branchs_old DISABLE TRIGGER branchs_calcul_abscisse;".format(
                    self.mdb.SCHEMA
                )
                sql += "\n"
            if "branchs_chstate_active" in lst_trigger_b:
                # sql += "DROP TRIGGER IF EXISTS branchs_chstate_active ON {}.branchs_old;".format(self.mdb.SCHEMA)
                sql += "ALTER TABLE {}.branchs_old DISABLE TRIGGER branchs_chstate_active;".format(
                    self.mdb.SCHEMA
                )
            err = self.mdb.run_query(sql)
            if err:
                self.mgis.add_info("Rename table branchs - ERROR")
                self.mgis.add_info("Erreur for rename branchs table to branchs_old")
                valid = False
            else:
                self.mgis.add_info("Rename table branchs - OK")

        if valid:
            # updates column of the profiles table
            vars = [
                ("minbedcoef", "float"),
                ("majbedcoef", "float"),
                ("mesh", "float"),
                ("planim", "float"),
            ]
            sql = ""
            for var, typ in vars:
                sql += "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS {1} {2} ;".format(
                    self.mdb.SCHEMA, var, typ
                )
                sql += "\n"
            err = self.mdb.run_query(sql)
            if err:
                self.mgis.add_info("Adding new columns in profiles table - ERROR")
                valid = False
            else:
                self.mgis.add_info("Adding new columns in profiles table - OK")
        if valid:
            # add fct sql local

            self.mgis.add_info("Adding new local function -")
            err = self.mdb.schema_fct_sql()
            if err:
                self.mgis.add_info("Adding new local function - ERROR")
                valid = False
            else:
                self.mgis.add_info("Adding new local function - OK")

        if valid:
            tabs = [Maso.branchs, Maso.visu_branchs]
            for tab in tabs:
                valid_add, _ = self.add_tab(tab)
            if not valid_add:
                self.mgis.add_info("Create table Branch - ERROR")
                valid = False
            else:
                self.mgis.add_info("Create table Branch - OK")
        lst_trigger_p = self.mdb.list_trigger("profiles", self.mdb.SCHEMA)
        if valid:
            if "profiles_edition" in lst_trigger_p:
                sql = "DROP TRIGGER IF EXISTS profiles_edition ON {}.profiles;".format(
                    self.mdb.SCHEMA
                )
                err = self.mdb.run_query(sql)
            obj = Maso.profiles()
            obj.schema = self.mdb.SCHEMA
            sql = obj.pg_profiles_edition()
            err = self.mdb.run_query(sql)
            if err:
                self.mgis.add_info("Adding new profile trigger - ERROR")
                valid = False
            else:
                self.mgis.add_info("Adding new profile trigger - OK")

        if valid:
            sql = """
CREATE OR REPLACE FUNCTION {0}.insert_new_branch(source_schema text)
    RETURNS void
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
   rec              record;
   geom_b    public.geometry;
   actb boolean;
   startb character varying(30);
   endb character varying(30);
   BEGIN
-- Disable trigger
   EXECUTE 'ALTER TABLE ' ||  quote_ident(source_schema) ||'.branchs DISABLE TRIGGER ALL';
-- creation new table
   FOR rec IN
   EXECUTE 'SELECT DISTINCT branch as id_b  FROM  '||  quote_ident(source_schema) ||'.branchs_old'
   LOOP
        EXECUTE ' SELECT st_multi(ST_Union(geom))  FROM  ' ||  quote_ident(source_schema) ||'.branchs_old  
                WHERE branch=$1 GROUP BY branch' USING rec.id_b INTO geom_b;
        EXECUTE 'SELECT active,startb, endb  FROM ' ||  quote_ident(source_schema) ||'.branchs_old 
                WHERE branch=$1 ORDER BY gid ASC LIMIT 1 ' USING rec.id_b INTO actb, startb, endb;
-- insert value new branch table
        EXECUTE 'INSERT INTO ' ||  quote_ident(source_schema) ||'.branchs(geom,  branch, active,startb, endb) 
                VALUES ($1,$2,$3,$4,$5)' USING geom_b,rec.id_b,actb,startb, endb;
    -- RAISE NOTICE 'test %', rec.id_b;
    END LOOP;
-- Update fille profile table
    EXECUTE 'UPDATE  ' ||  quote_ident(source_schema) ||'.profiles as p 
            SET minbedcoef=(SELECT minbedcoef FROM ' ||  quote_ident(source_schema) ||'.branchs_old AS b 
                            WHERE ST_INTERSECTS(p.geom, b.geom) LIMIT 1)';
    EXECUTE 'UPDATE  ' ||  quote_ident(source_schema) ||'.profiles as p 
            SET majbedcoef=(SELECT majbedcoef FROM ' ||  quote_ident(source_schema) ||'.branchs_old AS b 
                            WHERE ST_INTERSECTS(p.geom, b.geom) LIMIT 1)';
    EXECUTE 'UPDATE  ' ||  quote_ident(source_schema) ||'.profiles as p 
            SET mesh=(SELECT mesh FROM ' ||  quote_ident(source_schema) ||'.branchs_old AS b 
                        WHERE ST_INTERSECTS(p.geom, b.geom) LIMIT 1)';
    EXECUTE 'UPDATE  ' ||  quote_ident(source_schema) ||'.profiles as p 
            SET planim=(SELECT planim FROM ' ||  quote_ident(source_schema) ||'.branchs_old AS b 
                        WHERE ST_INTERSECTS(p.geom, b.geom) LIMIT 1)';
-- Enable trigger
    EXECUTE 'ALTER TABLE ' ||  quote_ident(source_schema) ||'.branchs ENABLE TRIGGER ALL';    
    RETURN;
END;
$BODY$;
            """.format(
                self.mdb.SCHEMA
            )

            err = self.mdb.run_query(sql)
            if err:
                self.mgis.add_info("Create insert_new_branch - ERROR")
                self.mgis.add_info(
                    "Error for the creation of the conversion function "
                    "(branch_old table to new branchs table)"
                )
                valid = False

            else:
                self.mgis.add_info("Create insert_new_branch - OK")

        if valid:
            sql = """SELECT {0}.insert_new_branch('{0}');""".format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                self.mgis.add_info("Fill new branchs table - ERROR")
                valid = False
            else:
                check_fill = True
                self.mgis.add_info("Fill new branchs table - OK")
        if valid:
            # TRIGGER
            sql = "DROP TRIGGER IF EXISTS flood_marks_delete_point_flood ON {}.flood_marks;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS flood_marks_calcul_abscisse_flood ON {}.flood_marks;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS weirs_calcul_abscisse ON {}.weirs;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS tracer_lateral_inflows_calcul_abscisse ON {}.tracer_lateral_inflows;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS profiles_calcul_abscisse ON {}.profiles;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS outputs_calcul_abscisse ON {}.outputs;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS links_calcul_abscisse ON {}.links;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += (
                "DROP TRIGGER IF EXISTS lateral_weirs_calcul_abscisse ON {}.lateral_weirs;".format(
                    self.mdb.SCHEMA
                )
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS lateral_inflows_calcul_abscisse ON {}.lateral_inflows;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS hydraulic_head_calcul_abscisse ON {}.hydraulic_head;".format(
                self.mdb.SCHEMA
            )
            sql += "\n"
            sql += "DROP TRIGGER IF EXISTS basins_chstate_active ON {}.basins;".format(
                self.mdb.SCHEMA
            )

            err1 = self.mdb.run_query(sql)
            if err1:
                self.mgis.add_info(
                    "Delete Trigger functions  using public.calcul_abscisse* functions - ERROR"
                )
                valid = False

        if valid:
            tabs_sql = [
                ("flood_marks", Maso.flood_marks),
                ("weirs", Maso.weirs),
                ("profiles", Maso.profiles),
                ("outputs", Maso.outputs),
                ("links", Maso.links),
                ("lateral_weirs", Maso.lateral_weirs),
                ("lateral_inflows", Maso.lateral_inflows),
                ("hydraulic_head", Maso.hydraulic_head),
                ("tracer_lateral_inflows", Maso.tracer_lateral_inflows),
                ("basins", Maso.basins),
            ]
            sql = ""
            for name, obj_ in tabs_sql:
                obj = obj_()
                obj.schema = self.mdb.SCHEMA
                if name == "flood_marks":
                    sql += getattr(obj, "pg_calcul_abscisse_flood")()
                    sql += getattr(obj, "pg_clear_tab")()
                elif name == "outputs":
                    sql += getattr(obj, "pg_create_calcul_abscisse_outputs")()
                elif name == "basins":
                    sql += getattr(obj, "pg_updat_actv")()
                else:
                    sql += getattr(obj, "pg_create_calcul_abscisse")()
            err2 = self.mdb.run_query(sql)
            if err2:
                self.mgis.add_info("Adding the new Triggers using the local functions - ERROR")
                valid = False
        if valid:
            self.mgis.add_info("Update the Triggers (public to local schema)- OK")

        if valid:
            sql = "DROP TABLE IF EXISTS  {0}.branchs_old;".format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                self.mgis.add_info("Delete branchs_old which is temporary table - ERROR")
        else:
            if not check_fill:
                lst_tab = self.mdb.list_tables()
                if "branchs_old" in lst_tab:
                    sql = "DROP TABLE IF EXISTS  {0}.branchs;".format(self.mdb.SCHEMA)
                    err = self.mdb.run_query(sql)

                sql = "ALTER TABLE IF EXISTS {0}.branchs_old RENAME TO branchs;".format(
                    self.mdb.SCHEMA
                )
                sql += "\n"
                sql += "ALTER TABLE IF EXISTS {0}.branchs RENAME CONSTRAINT branchs_old_pkey TO branchs_pkey;".format(
                    self.mdb.SCHEMA
                )
                sql += "\n"
                sql += "ALTER TABLE IF EXISTS {0}.branchs RENAME CONSTRAINT cle_debut_old TO cle_debut;".format(
                    self.mdb.SCHEMA
                )
                sql += "\n"
                sql += "ALTER TABLE IF EXISTS {0}.branchs  RENAME CONSTRAINT cle_fin_old TO cle_fin;".format(
                    self.mdb.SCHEMA
                )
                sql += "\n"
                sql += "ALTER INDEX IF EXISTS {0}.branchs_old_geom_idx RENAME TO branchs_geom_idx;".format(
                    self.mdb.SCHEMA
                )
                sql += "\n"
                sql += "ALTER SEQUENCE IF EXISTS  {0}.branchs_old_gid_seq RENAME TO branchs_gid_seq;".format(
                    self.mdb.SCHEMA
                )
                err = self.mdb.run_query(sql)
        if len(lst_profil_err) > 0:
            txt = "\n".join([str(ival) for ival in lst_profil_err])
            ok = self.box.info(
                "WARNING:\n\n"
                "Check the profiles : \n\n"
                "{}\n\n"
                "because they intersected two branches:\n".format(txt)
            )

        self.mgis.add_info("******")
        return valid

    def update_512(self):
        self.mgis.add_info("*** Update 5.1.2  ***")
        valide = True
        if valide:
            sql = "DROP TRIGGER IF EXISTS basins_chstate_active ON {}.basins;".format(
                self.mdb.SCHEMA
            )
            err1 = self.mdb.run_query(sql)
            tabs_sql = ["basins", Maso.basins]
            obj = Maso.basins()
            obj.schema = self.mdb.SCHEMA
            sql = obj.pg_updat_actv()
            err2 = self.mdb.run_query(sql)
            if err2:
                self.mgis.add_info("Fixe error basins_chstate_active - ERROR")
                valid = False
        if valide:
            lst_tab = self.mdb.list_tables(schema=self.mdb.SCHEMA)
            lst_admin_tab = self.mdb.select("admin_tab", list_var=["table_"])
            if "results_old" in lst_tab:
                self.mdb.drop_table("results_old")
            if "results_old" in lst_admin_tab["table_"]:
                self.mdb.delete("admin_tab", where="table_= 'results_old'")

            if "runs_graph" not in lst_tab:
                valid, tab_name = self.add_tab(Maso.runs_graph, False)
                self.updat_num_v(tab_name, "5.1.2")

            if valide:
                valid = self.update_clone()
                if not valid:
                    self.mgis.add_info("Error to update clone function")
            test = self.mdb.select("parametres", where="parametre ='decentrement'")
            if valid and not len(test["id"]) > 0:
                try:
                    fichparam = os.path.join(self.mgis.dossier_sql, "parametres.csv")
                    # self.run_query(req.format(self.SCHEMA, fichparam))
                    liste_value = []
                    with open(fichparam, "r") as file:
                        for ligne in file:
                            liste_value.append(ligne.replace("\n", "").split(";"))
                    liste_col = self.mdb.list_columns("parametres")
                    var = ",".join(liste_col)
                    valeurs = "("
                    for k in liste_col:
                        valeurs += "%s,"
                    valeurs = valeurs[:-1] + ")"

                    self.mdb.delete("parametres")

                    sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(
                        self.mdb.SCHEMA, "parametres", var, valeurs
                    )

                    self.mdb.run_query(sql, many=True, list_many=liste_value)
                except Exception:
                    valid = False
                    self.mgis.add_info("Error when parameters update")

        return valid

    def update_513(self):
        """
        Action update version 5.1.3
        """
        self.mgis.add_info("*** Update 5.1.3  ***")
        cl = Maso.class_fct_psql()
        lfct = [cl.pg_create_calcul_abscisse_point_flood(self.mdb.SCHEMA)]
        qry = ""
        for sql in lfct:
            qry += sql
            qry += "\n"
        self.mdb.run_query(qry)

    def update_515(self):
        """
        Action update version 5.1.5
        """
        self.mgis.add_info("*** Update 5.1.5  ***")
        old_vers = self.check_v_masc()
        if old_vers != "8.4":
            ok = self.box.yes_no_q(
                "WARNING:\n "
                "Please note that this 5.1.5 update automatically \n"
                " updates the mascaret executable.\n"
                "Do you want to continue ?"
            )
            if not ok:
                return False

        lst_admin_tab = self.mdb.select("admin_tab", list_var=["table_"])
        if "results_old" in lst_admin_tab["table_"]:
            self.mdb.delete("admin_tab", where="table_= 'results_old'")

        # update csv parameter decentrement
        test = self.mdb.select("parametres", where="parametre ='decentrement'")
        if not len(test["id"]) > 0:
            fichparam = os.path.join(self.mgis.dossier_sql, "parametres.csv")

            liste_value = []
            with open(fichparam, "r") as file:
                for ligne in file:
                    liste_value.append(ligne.replace("\n", "").split(";"))
            liste_col = self.mdb.list_columns("parametres")
            var = ",".join(liste_col)
            valeurs = "("
            for k in liste_col:
                valeurs += "%s,"
            valeurs = valeurs[:-1] + ")"

            self.mdb.delete("parametres")

            sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(
                self.mdb.SCHEMA, "parametres", var, valeurs
            )

            self.mdb.run_query(sql, many=True, list_many=liste_value)
        # fix error
        try:
            qry = "DROP TRIGGER IF EXISTS all_up_abs_branchs ON {0}.branchs;".format(
                self.mdb.SCHEMA
            )
            self.mdb.run_query(qry)

            lst_fct = [
                "{0}.update_{1}(regclass, regclass)".format(self.mdb.SCHEMA, info)
                for info in ["abscisse_profil", "abscisse_point"]
            ]
            lst_fct.append("{0}.up_abs_branch()".format(self.mdb.SCHEMA))

            qry = ""
            for fct in lst_fct:
                qry += "DROP FUNCTION IF EXISTS {};\n".format(fct)
            self.mdb.run_query(qry)

            cl = Maso.class_fct_psql()
            lfct = [cl.pg_all_profil, cl.pg_all_point, cl.pg_up_abs_branch]

            qry = ""
            for sql in lfct:
                qry += sql(self.mdb.SCHEMA)
                qry += "\n"
            clb = Maso.branchs()
            clb.schema = self.mdb.SCHEMA
            qry += clb.pg_all_up_abs_branchs()
            self.mdb.run_query(qry)
        except Exception as e:
            self.mgis.add_info("Error update_fct_calc_abs: {}".format(str(e)))
            return False
        # update executable
        if old_vers != "8.4":
            self.mgis.download_bin()

        return True

    def update_516(self):
        """
        Update 5.1.6
        """
        self.mgis.add_info("*** Update 5.1.6  ***")
        valide = True
        test = ""
        if valide:
            test = "results_sect"
            sql = (
                "ALTER TABLE IF EXISTS {0}.results_sect RENAME TO results_sect_old;\n"
                "ALTER TABLE IF EXISTS {0}.results_sect_old DROP CONSTRAINT IF EXISTS results_sect_pkey;"
            )
            err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            if err:
                self.mgis.add_info("Alter the result_sect table - ERROR")
                valide = False
            else:
                self.mgis.add_info("Alter the result_sect table - OK", dbg=True)

        # OBSERVATION
        if valide:
            sql = (
                "ALTER TABLE IF EXISTS {0}.observations RENAME TO observations_old;\n"
                "ALTER TABLE IF EXISTS {0}.observations DROP CONSTRAINT IF EXISTS observations_pkey;"
            )
            err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            if err:
                self.mgis.add_info("Alter the observations table - ERROR")
                valide = False
            else:
                self.mgis.add_info("Alter the observations table - OK", dbg=True)

        self.mgis.add_info("Create the New results table ", dbg=True)
        if valide:
            test = "create"
            tabs = [Maso.results_by_pk, Maso.results_sect, Maso.observations]
            for tab in tabs:
                valid_add, _ = self.add_tab(tab)
            if not valid_add:
                self.mgis.add_info("Create  the new reuslts table - ERROR")
                valide = False
            else:
                self.mgis.add_info("Create  the new reuslts table - OK", dbg=True)

        if valide:
            test = "fill_res"
            self.mgis.add_info("Fill the New results table", dbg=True)
            sql = "DELETE FROM {0}.results_by_pk;\n"
            sql += (
                'INSERT INTO {0}.results_by_pk (id_runs, pknum, var, "time", val)'
                'SELECT id_runs, pknum, var, array_agg("time" ORDER BY "time"), array_agg(val ORDER BY "time")'
                "FROM {0}.results GROUP BY id_runs, pknum, var;\n"
            )
            err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            if err:
                self.mgis.add_info("Fill the New results table - ERROR")
                valide = False
            else:
                self.mgis.add_info("Fill the New results table - OK", dbg=True)

        if valide:
            test = "fill_res_sec"
            self.mgis.add_info("Fill the New results section table", dbg=True)
            sql = "DELETE FROM {0}.results_sect;\n"
            sql += (
                "INSERT INTO {0}.results_sect (id_runs, branch, pk , section)"
                'SELECT id_runs, branch, array_agg("pk" ORDER BY "pk"), array_agg(section ORDER BY "pk")'
                "FROM {0}.results_sect_old GROUP BY id_runs, branch;\n"
            )
            err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            if err:
                self.mgis.add_info("Fill the New results section table - ERROR")
                valide = False
            else:
                self.mgis.add_info("Fill the New results section table - OK", dbg=True)
        if valide:
            test = "fill_obs"
            self.mgis.add_info("Fill the New observations table", dbg=True)
            sql = "DELETE FROM {0}.observations;\n"
            sql += """INSERT INTO {0}.observations(code,type, comment, valeur, date)
                SELECT code, type,  array_agg(comment ORDER BY date), array_agg(valeur ORDER BY date), 
                array_agg(date ORDER BY date)
                FROM {0}.observations_old GROUP BY code,type;"""
            err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            if err:
                self.mgis.add_info("Fill the New observations table - ERROR")
                valide = False
            else:
                self.mgis.add_info("Fill the New observations table - OK", dbg=True)
        if valide:
            test = "fill_res_view"
            self.mgis.add_info("New View results")
            sql = "DROP VIEW  IF EXISTS {0}.results;\n"
            sql += (
                "CREATE VIEW {0}.results AS SELECT results_by_pk.id_runs, "
                'UNNEST(results_by_pk."time") as time, '
                "results_by_pk.pknum, results_by_pk.var, "
                "UNNEST(results_by_pk.val) as val FROM {0}.results_by_pk;"
            )
            err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            if err:
                self.mgis.add_info("New View results - ERROR")
                valide = False
            else:
                self.mgis.add_info("New View results - OK", dbg=True)
        # back update
        if not valide:
            self.mgis.add_info("Cancel update")
            if test == "fill_res":
                sql = "DROP VIEW  IF EXISTS {0}.results;\n"
                sql += (
                    'CREATE VIEW {0}.results AS SELECT id_runs, "time", pknum,  var, val '
                    "FROM {0}.results_idx Inner join  {0}.results_val "
                    "on {0}.results_val.idruntpk = {0}.results_idx.idruntpk;"
                )

                err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            elif test in ["fill_res", "fill_res_sect", "create", "fill_obs"]:
                if test != "create":
                    t_sec = self.mdb.drop_table("results_sect", cascade=True)
                    t_pk = self.mdb.drop_table("results_by_pk", cascade=True)
                    t_obs = self.mdb.drop_table("observations", cascade=True)
                if t_sec:
                    sql = "ALTER TABLE IF EXISTS {0}.results_sect_old RENAME TO results_sect;\n"
                    sql += (
                        "ALTER TABLE IF EXISTS {0}.results_sect "
                        "ADD CONSTRAINT results_sect_pkey PRIMARY KEY (id_runs, pk, branch);"
                    )
                    err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
                if t_obs:
                    sql = "ALTER TABLE IF EXISTS {0}.observations_old RENAME TO observations;\n"
                    sql += (
                        "ALTER TABLE IF EXISTS {0}.observations "
                        "ADD CONSTRAINT observations_pkey PRIMARY KEY (id);"
                    )
                    err = self.mdb.run_query(sql.format(self.mdb.SCHEMA))
                if not t_pk or not t_sec or not t_obs:
                    err = True

            if err:
                self.mgis.add_info("Back the update - ERROR")
            else:
                self.mgis.add_info("Back the update  - OK")

        if valide:
            self.mgis.add_info("Drop the  tables: results_val, results_idx", dbg=True)
            t_val = self.mdb.drop_table("results_val", cascade=True)
            t_idx = self.mdb.drop_table("results_idx", cascade=True)
            t_sec = self.mdb.drop_table("results_sect_old", cascade=True)
            t_obs = self.mdb.drop_table("observations_old", cascade=True)
            if not t_val or not t_idx or not t_sec:
                if not t_val:
                    ntab = "results_val"
                elif not t_idx:
                    ntab = "results_idx"
                elif not t_sec:
                    ntab = "results_sect_old"
                elif not t_obs:
                    ntab = "observations_old"
                self.mgis.add_info("Drop the  tables {0} - ERROR".format(ntab))
                valide = False
            else:
                self.mgis.add_info("Drop the  tables - OK", dbg=True)

            # corrige_public fct
        if valide:
            valide = self.up_trigger()
            if valide:
                self.mgis.add_info("Update TRIGGER - OK", dbg=True)
            else:
                self.mgis.add_info("Update TRIGGER - ERROR", dbg=True)

        # update executable
        old_vers = self.check_v_masc()
        if old_vers == "8.4":
            ok = self.box.yes_no_q(
                "WARNING:\n "
                "Please note that the mascaret executable is updated. \n"
                "Do you want to continue ?"
            )
            if not ok:
                return False
            self.mgis.download_bin()

        return valide

    def up_trigger(self, ref=True):
        """
        Update trigger in
        :param ref: True if only current schema , False on the database
        """
        try:
            if ref:
                ref_schema = self.mdb.SCHEMA

            sql = """
                  SELECT
                      t.tgname AS trigger_name,
                      t.tgrelid::regclass AS table_name,
                      p.proname AS function_name,
                      n.nspname as shema_name
                  FROM
                      pg_trigger t
                  LEFT JOIN
                      pg_proc p ON t.tgfoid = p.oid
                  JOIN
                      pg_namespace n ON p.pronamespace = n.oid
                  where
                      n.nspname = 'public'"""
            dico = self.mdb.query_todico(sql)
            tabs_sql = {
                "flood_marks": {
                    "obj": Maso.flood_marks,
                    "fct": ["pg_calcul_abscisse_flood", "pg_clear_tab"],
                },
                "weirs": {"obj": Maso.weirs, "fct": ["pg_create_calcul_abscisse"]},
                "profiles": {"obj": Maso.profiles, "fct": ["pg_create_calcul_abscisse"]},
                "outputs": {"obj": Maso.outputs, "fct": ["pg_create_calcul_abscisse_outputs"]},
                "links": {"obj": Maso.links, "fct": ["pg_create_calcul_abscisse"]},
                "lateral_weirs": {"obj": Maso.lateral_weirs, "fct": ["pg_create_calcul_abscisse"]},
                "lateral_inflows": {
                    "obj": Maso.lateral_inflows,
                    "fct": ["pg_create_calcul_abscisse"],
                },
                "hydraulic_head": {
                    "obj": Maso.hydraulic_head,
                    "fct": ["pg_create_calcul_abscisse"],
                },
                "tracer_lateral_inflows": {
                    "obj": Maso.tracer_lateral_inflows,
                    "fct": ["pg_create_calcul_abscisse"],
                },
                "basins": {"obj": Maso.basins, "fct": ["pg_updat_actv"]},
                "branchs": {
                    "obj": Maso.branchs,
                    "fct": ["pg_updat_actv", "pg_all_up_abs_branchs", "pg_branchs_edition"],
                },
            }
            new_dico = {}
            cond = True
            for ntab, ntrigger in zip(dico["table_name"], dico["trigger_name"]):
                name = ntab.split(".")[1]
                schema = ntab.split(".")[0]
                if ref:
                    cond = False
                    if schema == ref_schema:
                        cond = True
                if cond:
                    qry = "DROP TRIGGER IF EXISTS {0} ON {1};\n".format(ntrigger, ntab)
                    self.mdb.run_query(qry)
                    if schema not in new_dico.keys():
                        new_dico[schema] = []
                    new_dico[schema].append(name)

            for schema, names in new_dico.items():
                for name in names:
                    obj = tabs_sql[name]["obj"]()
                    obj.schema = schema
                    sql = ""
                    for fct in tabs_sql[name]["fct"]:
                        sql += getattr(obj, fct)()
                        self.mdb.run_query(sql, be_quiet=True)
            return True
        except Exception:
            return False

    def check_v_masc(self):
        """check_version mascaret"""
        file_path = os.path.join(self.mgis.masplugPath, "bin", "conf.json")
        if os.path.isfile(file_path):
            f = open(file_path, "r")
            jso = json.loads(f.read())
            data = jso["masc_version"]
        else:
            data = ""
        return data

    def update_517(self):
        """
        Update 5.1.7
        """
        self.mgis.add_info("*** Update 5.1.7  ***")
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        valide = True
        if valide and "visu_minor_river_bed" not in tabs:
            tabs = [Maso.visu_minor_river_bed]
            for tab in tabs:
                valid_add, _ = self.add_tab(tab)
            if not valid_add:
                self.mgis.add_info("Create  the visu_minor_river_bed table - ERROR")
                valide = False

        if valide:
            lst_alt = [
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  leftminbed_g FLOAT;",
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  rightminbed_g FLOAT;",
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  leftstock_g FLOAT;",
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  rightstock_g FLOAT;",
            ]
            for sql in lst_alt:
                self.mdb.execute(sql.format(self.mdb.SCHEMA))
        if valide:
            try:
                update_all_bed_geometry(self.mdb)
            except Exception:
                self.mgis.add_info("erreur update_all_bed_geometry")

        return valide

    def update_620(self):
        # TODO
        # add links_mob_val
        # modification link  table
        self.mgis.add_info("*** Update 6.2.0  ***")
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        lst_add_tab = ["links_mob_val"]
        valide = True
        for attr in lst_add_tab:
            if attr not in tabs:
                valid_add, _ = self.add_tab(getattr(Maso, attr))
                if not valid_add:
                    self.mgis.add_info(f"Create  the {attr} table - ERROR")
                    valide = False
        if valide:
            lst_alt = [
                "ALTER TABLE {0}.struct_config ADD COLUMN IF NOT EXISTS  zbreak DOUBLE PRECISION DEFAULT 10000;",
                "ALTER TABLE {0}.struct_config ADD COLUMN IF NOT EXISTS  erase_flag boolean NOT NULL  DEFAULT FALSE;",
                "ALTER TABLE {0}.links ADD COLUMN IF NOT EXISTS method_mob text;",
                "ALTER TABLE {0}.links ADD COLUMN IF NOT EXISTS active_mob BOOLEAN;",
                "ALTER TABLE {0}.weirs ADD COLUMN IF NOT EXISTS erase_flag boolean NOT NULL   DEFAULT FALSE;",
            ]
            # Alter colonne value en text
            for sql in lst_alt:
                self.mdb.execute(sql.format(self.mdb.SCHEMA))
    # Pour les WEIRS convertir

