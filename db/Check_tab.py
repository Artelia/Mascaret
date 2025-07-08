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
import importlib
import json
import os
import sys
from copy import deepcopy

from . import MasObject as Maso
from ..Function import read_version, fill_zminbed
from ..ui.custom_control import ClassWarningBox


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
            "5.2.1",
            "6.0.0",
            "6.0.1",
            "6.0.2",
            "6.0.3",
            "6.0.4",
            "6.1.0",
            "6.1.1",
            "6.2.0",
            "6.2.1",
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
                    lambda: self.update_version("302"),
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
                "fct": [lambda: self.update_version("306")],
            },
            "3.0.7": {},
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
                    lambda: self.update_version("402"),
                ],
            },
            "4.0.3": {},
            "4.0.4": {},
            "4.0.5": {
                "fct": [lambda: self.update_400(),
                        lambda: self.update_version("402")],
            },
            "4.0.6": {},
            "4.0.7": {},
            "4.0.8": {},
            "4.0.9": {},
            "4.0.10": {},
            "4.0.11": {
                "fct": [lambda: self.update_version("4011")],
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
                    lambda: self.update_version("511"),
                ],
            },
            "5.1.2": {
                "fct": [
                    lambda: self.update_version("512"),
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
                    lambda: self.update_version("515"),
                ],
            },
            "5.1.6": {
                "fct": [
                    lambda: self.update_version("516"),
                ],
            },
            "5.1.7": {
                "fct": [
                    lambda: self.update_version("517"),
                ],
            },
            "5.1.8": {},
            "5.1.9": {},
            "5.1.10": {},
            "5.1.11": {},
            "5.1.12": {},
            "5.1.13": {},
            "5.2.1": {},
            "6.0.0": {},
            "6.0.1": {},
            "6.0.2": {},
            "6.0.3": {},
            "6.0.4": {},
            "6.1.0": {},
            "6.1.1": {},
            "6.2.0": {"fct": [
                lambda: self.update_version("620"),
            ],
            },
            "6.2.1": {},

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

    def check_v_masc(self):
        """
        check_version mascaret
        :return:
        """
        file_path = os.path.join(self.mgis.masplugPath, "bin", "conf.json")
        if os.path.isfile(file_path):
            f = open(file_path, "r")
            jso = json.loads(f.read())
            data = jso["masc_version"]
        else:
            data = ""
        return data

    def update_version(self, version=''):
        """
        Call the update method for a given version.
        """
        base_dir = os.path.dirname(__file__)
        plugin_root = os.path.abspath(os.path.join(base_dir, '..'))
        file_path = os.path.join(base_dir, 'update_version', f'update_{version}.py')
        module_name = f"update_{version}"
        class_name = f"ClassUpdate{version}"
        method_name = f"update{version}"

        if not os.path.isfile(file_path):
            raise RuntimeError(f"Fichier de mise à jour introuvable : {file_path}")

        # Add temporary  the path in root path of the plugin
        if plugin_root not in sys.path:
            sys.path.insert(0, plugin_root)

        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                raise RuntimeError(f"Impossible to load the module : {module_name}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            klass = getattr(module, class_name)
            method = getattr(klass(self), method_name)
            return method()

        except (ModuleNotFoundError, AttributeError) as e:
            raise RuntimeError(f"Update {version} not found or invalid : {e}")

        finally:
            # clear
            if plugin_root in sys.path:
                sys.path.remove(plugin_root)

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
