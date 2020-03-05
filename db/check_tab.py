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
import os
from . import MasObject as Maso
from copy import deepcopy
from ..Function import read_version


class CheckTab():
    def __init__(self, mgis, mdb):
        self.mgis = mgis
        self.mdb = mdb
        # for add table [ 'add_tab': [list_table]]
        # for delete [ ['DEL TAB',[list_table]]
        self.dico_modif = {'2.9.9': {'alt_tab': [{'tab': 'admin_tab', 'sql': ["ALTER TABLE {0}.admin_tab ADD COLUMN "
                                                                              "IF NOT EXISTS toto double precision;"]}]},
                           '3.0.0': {'alt_tab': [{'tab': 'admin_tab', 'sql': ["ALTER TABLE {0}.admin_tab DROP COLUMN "
                                                                              "IF EXISTS toto;"]}]},
                           '3.0.1': {'add_tab': [{'tab': Maso.struct_fg, 'overwrite': False},
                                                 {'tab': Maso.struct_fg_val, 'overwrite': False},
                                                 {'tab': Maso.weirs_mob_val, 'overwrite': False}],
                                     'alt_tab': [{'tab': 'weirs', 'sql': ["ALTER TABLE {0}.weirs ADD COLUMN IF NOT "
                                                                          "EXISTS active_mob boolean;",
                                                                          "ALTER TABLE {0}.weirs ADD COLUMN IF NOT "
                                                                          "EXISTS method_mob text;"]},
                                     {'tab':'runs', 'sql' : ["ALTER TABLE {0}.runs ADD COLUMN IF NOT"
                                                             " EXISTS init_date timestamp without time zone;"]}]},
                           '3.0.2': {'add_tab': [{'tab': Maso.results, 'overwrite': False},
                                                 {'tab': Maso.results_sect, 'overwrite': False},
                                                 {'tab': Maso.results_var, 'overwrite': False}],
                                     'fct': [lambda: self.create_var_result(), lambda: self.convert_all_result()],
                                     'del_tab': ['results_float', 'results_int']},
                           }

        self.list_hist_version = ['0.0.0', '2.9.9', '3.0.0', '3.0.1', '3.0.2']


    def update_adim(self):
        """
        Update admin_tab and check table

        :return:
        """

        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        version = read_version(self.mgis.masplugPath)
        # self.all_version(tabs, version)
        # self.all_version(tabs, '3.0.1')

        if not "admin_tab" in tabs:
            try:
                Maso.admin_tab.overwrite = True
                obj = self.mdb.process_masobject(Maso.admin_tab, 'pg_create_table')
                if self.mgis.DEBUG:
                    self.mgis.add_info('  {0} OK'.format(obj.name))
                tabs.append("admin_tab")
            except:
                self.mgis.add_info('failure!<br>{0}'.format(Maso.admin_tab))
                return
            for name_tab in tabs:
                sql = "INSERT INTO {0}.admin_tab (table_, version_ )" \
                      " VALUES ('{1}', '{2}')" \
                    .format(self.mdb.SCHEMA, name_tab, '0.0.0')
                self.mdb.execute(sql)

        info = self.mdb.select('admin_tab', where="table_ = 'admin_tab'".format(), list_var=['version_'])
        curent_v_tab = info['version_'][0]

        pos = self.list_hist_version.index(curent_v_tab)
        pos_fin = self.list_hist_version.index(version)
        test_gd = True
        tabs_no = deepcopy(tabs)

        for ver in self.list_hist_version[pos + 1:pos_fin + 1]:
            if ver in self.dico_modif.keys():
                modif = self.dico_modif[ver]
                if len(modif) > 0:
                    for proc in ['add_tab', 'alt_tab', 'fct', 'del_tab']:
                        if proc in modif.keys():
                            if proc != 'fct':
                                lst_tab = modif[proc]
                                for tab in lst_tab:
                                    # print(proc)
                                    if proc == 'add_tab':
                                        valid, tab_name = self.add_tab(tab["tab"], tab["overwrite"])
                                    elif proc == 'alt_tab':
                                        tab_name = tab["tab"]
                                        valid = self.alt_tab(tab_name, tab["sql"])
                                    elif proc == 'del_tab':
                                        tab_name = tab
                                        valid = self.del_tab(tab_name)
                                    # print (proc, tab_name, valid)
                                    if valid:
                                        if proc != 'del_tab':
                                            self.updat_num_v(tab_name, ver)
                                        else:
                                            self.del_num_v(tab_name)
                                    else:
                                        test_gd = False
                                    if tab_name in tabs_no:
                                        tabs_no.remove(tab_name)
                            else:
                                lst_fct = modif[proc]
                                for fct in lst_fct:
                                    fct()
            if test_gd:
                self.all_version(tabs_no, ver)
            else:
                self.mgis.add_info('ERROR: Update table ************')


    def all_version(self, tabs, version=None):
        if not version:
            version = self.list_hist_version[0]
        for name_tab in tabs:
            self.updat_num_v(name_tab, version)


    def updat_num_v(self, name_tab, version):
        """
        updat version number
        :param tabs list of tables
        :return:
        """

        sql = "SELECT * FROM {0}.admin_tab WHERE  table_ = '{1}' " \
            .format(self.mdb.SCHEMA, name_tab)
        row = self.mdb.run_query(sql, fetch=True)
        if len(row) > 0:
            sql = "UPDATE {0}.admin_tab SET version_  = '{1}' WHERE table_ = '{2}';" \
                .format(self.mdb.SCHEMA, version, name_tab)
            self.mdb.execute(sql)
        else:
            sql = "INSERT INTO {0}.admin_tab (table_, version_)" \
                  " VALUES ('{1}', '{2}')".format(self.mdb.SCHEMA, name_tab, version)
            self.mdb.execute(sql)


    def del_num_v(self, name_tab):
        """
        delete table in admin_tab
        :param tabs list of tables
        :return:
        """

        sql = "SELECT * FROM {0}.admin_tab WHERE  table_ = '{1}' " \
            .format(self.mdb.SCHEMA, name_tab)
        row = self.mdb.run_query(sql, fetch=True)
        if len(row) > 0:
            sql = "DELETE FROM {0}.admin_tab WHERE table_ = '{1}';" \
                .format(self.mdb.SCHEMA, name_tab)
            self.mdb.execute(sql)


    def add_tab(self, tab, overwrite=True):
        """
        Add table
        :param tables: list of tables
        """

        valid = True
        try:
            tab.overwrite = overwrite
            obj = self.mdb.process_masobject(tab, 'pg_create_table')
            if self.mgis.DEBUG:
                self.mgis.add_info('  {0} OK'.format(obj.name))

        except:
            valid = False
            self.mgis.add_info('failure!<br>Add table {0}'.format(tab))

        return valid, obj.name


    def alt_tab(self, tab, lst_sql):
        valid = True
        txt_sql = ''
        for sql in lst_sql:
            txt_sql += sql.format(self.mdb.SCHEMA) + '\n'

        try:
            if sql != '':
                res = self.mdb.run_query(txt_sql)
                if res is None:
                    valid = False
                    self.mgis.add_info('failure!<br>Alt table {0}'.format(tab))
        except:
            valid = False
            self.mgis.add_info('failure!<br>Alt table {0}'.format(tab))

        return valid


    def del_tab(self, tab):
        try:
            valid = self.mdb.drop_table(tab)
        except:
            valid = False
            self.mgis.add_info('failure!<br>Del table {0}'.format(tab))

        return valid


    def create_var_result(self):
        from ..ClassParameterDialog import ClassParameterDialog
        self.mdb.execute("DELETE FROM {0}.results_var".format(self.mdb.SCHEMA))
        prm = ClassParameterDialog(self.mgis, "steady")
        for v, var in enumerate(prm.variables):
            name = prm.libel_var[v].replace("'", "''")
            if name[:5] == "Basin":
                type_res = "Basin"
            elif name[:4] == "Link":
                type_res = "Link"
            else:
                type_res = "Opt"
            self.mdb.run_query("INSERT INTO {0}.results_var (id, type_res, var, name) "
                               "VALUES ({1}, '{2}', '{3}', '{4}')".format(self.mdb.SCHEMA, v + 1, type_res, var, name))
        self.mdb.run_query("INSERT INTO {0}.results_var (id, type_res, var, name) "
                           "VALUES ({1}, 'Struct', 'ZSTR', 'Z Structure')".format(self.mdb.SCHEMA, v + 2))


    def convert_all_result(self):
        rows = self.mdb.run_query("SELECT DISTINCT type_res FROM {0}.results_var".format(self.mdb.SCHEMA), fetch=True)
        lst_typ_res = [r[0] for r in rows]
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs".format(self.mdb.SCHEMA), fetch=True)
        dict_runs = {r[0]: {"run": r[1], "scen": r[2]} for r in rows}
        for typ_res in lst_typ_res:
            for run in dict_runs.keys():
                self.convert_result(run, typ_res)


    def convert_result(self, run, typ_res):
        if typ_res == "Opt":
            tab_src = "resultats"
            col_pknum = "pk"
        elif typ_res == "Basin":
            tab_src = "resultats_basin"
            col_pknum = "bnum"
        elif typ_res == "Link":
            tab_src = "resultats_links"
            col_pknum = "lnum"
        elif typ_res == "Struct":
            return

        row = self.mdb.run_query("SELECT run, scenario FROM {0}.runs WHERE id = {1}".format(self.mdb.SCHEMA, run), fetch=True)
        run_run, run_scen = row[0]

        rows = self.mdb.run_query("SELECT column_name FROM information_schema.columns WHERE table_schema = '{0}' AND "
                                  "table_name = '{1}' AND ordinal_position > (SELECT ordinal_position "
                                  "FROM information_schema.columns WHERE table_schema = '{0}' AND table_name = '{1}' "
                                  "AND column_name = '{2}')".format(self.mdb.SCHEMA, tab_src, col_pknum), fetch=True)
        lst_var_exist = [r[0] for r in rows]

        self.mdb.execute("DELETE FROM {0}.results WHERE results.id_runs = {1} AND results.var IN (SELECT id FROM {0}.results_var "
                         "WHERE type_res = '{2}')".format(self.mdb.SCHEMA, run, tab_src))

        rows = self.mdb.run_query("SELECT id, var FROM {0}.results_var "
                                  "WHERE type_res = '{2}'".format(self.mdb.SCHEMA, tab_src, typ_res), fetch=True)
        for id_var, nm_var in rows:
            if nm_var.lower() in lst_var_exist:
                sql = "INSERT INTO {0}.results (SELECT {5}, {3}.t, {3}.{4}, {1}, {3}.{2} " \
                      "FROM {0}.{3} WHERE {3}.{2} is Not Null AND {3}.run = '{6}' " \
                      "AND {3}.scenario = '{7}')".format(self.mdb.SCHEMA, id_var, nm_var.lower(), tab_src, col_pknum,
                                                        run, run_run, run_scen)
                self.mdb.execute(sql)

