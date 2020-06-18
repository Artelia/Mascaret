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
import json
from . import MasObject as Maso
from copy import deepcopy
from ..Function import read_version
from ..ui.custom_control import ClassWarningBox


# from ..ClassParameterDialog import ClassParameterDialog


class CheckTab():
    def __init__(self, mgis, mdb):
        self.mgis = mgis
        self.mdb = mdb
        self.box = ClassWarningBox()
        # for add table [ 'add_tab': [list_table]]
        # for delete [ ['DEL TAB',[list_table]]
        self.dico_modif = {'3.0.0': {},
                           '3.0.1': {'add_tab': [{'tab': Maso.struct_fg, 'overwrite': False},
                                                 {'tab': Maso.struct_fg_val, 'overwrite': False},
                                                 {'tab': Maso.weirs_mob_val, 'overwrite': False}],
                                     'alt_tab': [{'tab': 'weirs', 'sql': ["ALTER TABLE {0}.weirs ADD COLUMN IF NOT "
                                                                          "EXISTS active_mob boolean;",
                                                                          "ALTER TABLE {0}.weirs ADD COLUMN IF NOT "
                                                                          "EXISTS method_mob text;"]}],
                                     'fct': [lambda: self.update_setting_json()]},
                           '3.0.2': {'add_tab': [{'tab': Maso.results, 'overwrite': False},
                                                 {'tab': Maso.results_sect, 'overwrite': False},
                                                 {'tab': Maso.results_var, 'overwrite': False}],
                                     'fct': [lambda: self.create_var_result(), lambda: self.convert_all_result()],
                                     'del_tab': ['results_float', 'results_int']},
                           }

        self.list_hist_version = ['3.0.0', '3.0.1', '3.0.2']

    def update_adim(self):
        """
        Update admin_tab and check table

        :return:
        """

        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        version = read_version(self.mgis.masplugPath)
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

        if len(self.list_hist_version[pos + 1:pos_fin + 1]) > 0:
            ok = self.box.yes_no_q("WARNING:\n "
                                   "Do you want update tables for {} schema ?\n"
                                   "There is a risk of table corruption.\n "
                                   "Remember to make backup copies if it's important model.".format(self.mdb.SCHEMA))
            if ok:

                for ver in self.list_hist_version[pos + 1:pos_fin + 1]:
                    if ver in self.dico_modif.keys():
                        modif = self.dico_modif[ver]
                        if len(modif) > 0:
                            for proc in ['add_tab', 'alt_tab', 'fct', 'del_tab']:
                                if proc in modif.keys():
                                    if proc != 'fct':
                                        lst_tab = modif[proc]
                                        for tab in lst_tab:
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
            else:
                self.mgis.add_info("********* Cancel of update table ***********")

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
        """
        Apply sql script
        :param tab: table name
        :param lst_sql: sql script list
        :return:
        """
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
        """
        delete table
        :param tab:  table name
        :return:
        """
        try:
            valid = self.mdb.drop_table(tab)
        except:
            valid = False
            self.mgis.add_info('failure!<br>Del table {0}'.format(tab))

        return valid

    def create_var_result(self):

        self.mdb.execute("DELETE FROM {0}.results_var".format(self.mdb.SCHEMA))
        dossier = os.path.join(self.mgis.masplugPath, 'db', 'sql')
        fichparam = os.path.join(dossier, "var.csv")
        liste_value = []
        with open(fichparam, 'r') as file:
            cpt = 0
            for ligne in file:
                if cpt > 0:
                    liste = ligne.replace('\n', '').split(';')
                    liste_value.append([int(liste[0])] + liste[1:])
                cpt += 1
        liste_col = self.mdb.list_columns('results_var')

        var = ",".join(liste_col)
        valeurs = "("
        for k in liste_col:
            valeurs += '%s,'
        valeurs = valeurs[:-1] + ")"

        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                            'results_var',
                                                            var,
                                                            valeurs)
        self.mdb.run_query(sql, many=True, list_many=liste_value)

        # add tracer variable
        info = self.mdb.select('tracer_name', where="type='TRANSPORT_PUR'", list_var=['type', 'text', 'sigle'])
        nbv = len(info['type'])
        if nbv > 0:
            dico = {'var': info['sigle'][0],
                    'type_res': 'tracer_{}'.format('TRANSPORT_PUR'),
                    'name': info['text'][0],
                    'type_var': 'float'}
            self.mdb.check_id_var(dico)

    def convert_all_result(self):
        """ conversion between the previous results table format to the new for all results"""

        rows = self.mdb.run_query("SELECT DISTINCT type_res FROM {0}.results_var".format(self.mdb.SCHEMA), fetch=True)
        lst_typ_res = [r[0] for r in rows]
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs".format(self.mdb.SCHEMA), fetch=True)
        dict_runs = {r[0]: {"run": r[1], "scen": r[2]} for r in rows}

        for typ_res in lst_typ_res:
            rows = self.mdb.run_query(
                "SELECT DISTINCT id_runs FROM {0}.results WHERE var in "
                "(SELECT id FROM {0}.results_var WHERE type_res = '{1}') ".format(self.mdb.SCHEMA, typ_res), fetch=True)
            lst_exist = [r[0] for r in rows]
            for run in dict_runs.keys():
                if run not in lst_exist:
                    self.convert_result(run, typ_res)

        rows = self.mdb.run_query("SELECT DISTINCT id_runs FROM {0}.results_sect".format(self.mdb.SCHEMA), fetch=True)
        lst_exist = [r[0] for r in rows]
        for run in dict_runs.keys():
            if run not in lst_exist:
                self.fill_result_sect(run)

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
        elif typ_res.split('_')[0] == 'tracer':
            tab_src = "resultats"
            col_pknum = "pk"
        elif typ_res in ["struct", "weirs"]:
            return

        row = self.mdb.run_query("SELECT run, scenario FROM {0}.runs WHERE id = {1}".format(self.mdb.SCHEMA, id_run),
                                 fetch=True)
        run_run, run_scen = row[0]

        rows = self.mdb.run_query("SELECT column_name FROM information_schema.columns WHERE table_schema = '{0}' AND "
                                  "table_name = '{1}' AND ordinal_position > (SELECT ordinal_position "
                                  "FROM information_schema.columns WHERE table_schema = '{0}' AND table_name = '{1}' "
                                  "AND column_name = '{2}')".format(self.mdb.SCHEMA, tab_src, col_pknum), fetch=True)

        lst_var_exist = [r[0] for r in rows]
        self.mdb.execute(
            "DELETE FROM {0}.results WHERE results.id_runs = {1} AND results.var IN (SELECT id FROM {0}.results_var "
            "WHERE type_res = '{2}')".format(self.mdb.SCHEMA, id_run, tab_src))

        rows = self.mdb.run_query("SELECT id, var FROM {0}.results_var "
                                  "WHERE type_res = '{2}' ORDER BY id".format(self.mdb.SCHEMA, tab_src, typ_res),
                                  fetch=True)
        if typ_res.split('_')[0] == 'tracer':
            lst_var = [[row[0], 'c{}'.format(r + 1)] for r, row in enumerate(rows)]
        else:
            lst_var = rows

        for id_var, nm_var in lst_var:
            if nm_var.lower() in lst_var_exist:
                sql = "INSERT INTO {0}.results (SELECT {5}, {3}.t, {3}.{4}, {1}, {3}.{2} " \
                      "FROM {0}.{3} WHERE {3}.{2} is Not Null AND {3}.run = '{6}' " \
                      "AND {3}.scenario = '{7}')".format(self.mdb.SCHEMA, id_var, nm_var.lower(), tab_src, col_pknum,
                                                         id_run, run_run, run_scen)
                self.mdb.execute(sql)

    def fill_result_sect(self, id_run):
        """
        fill results section table
        :param id_run: run index
        :return:
        """
        info = self.mdb.select('resultats',
                               where='(run, scenario) = (SELECT run, scenario '
                                     'FROM {}.runs WHERE id= {})'.format(self.mdb.SCHEMA, id_run),
                               order='t',
                               list_var=['pk', 'branche', 'section'])
        lst_id = [id_run for i in range(len(info['pk']))]
        lst_insert = list(set(zip(lst_id, info['pk'], info['branche'], info['section'])))
        col_sect = ['id_runs', 'pk', 'branch', 'section']
        if len(lst_insert) > 0:
            self.mdb.insert_res('results_sect', lst_insert, col_sect)

    def update_setting_json(self):
        """
        update setting in json
        :return:
        """
        name_file = os.path.join(self.mgis.masplugPath, 'settings.json')
        modif = False
        if os.path.isfile(name_file):
            # read
            with open(name_file) as file:
                data = json.load(file)
            # change
            if "cond_api" not in data['mgis'].keys():
                data["cond_api"] = False
                modif = True
            # write
            if modif:
                with open(name_file, 'w') as file:
                    json.dump(data, file)
