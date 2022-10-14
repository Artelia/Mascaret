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
from ..Function import read_version, fill_zminbed
from ..ui.custom_control import ClassWarningBox
from datetime import datetime
from ..HydroLawsDialog import dico_typ_law


def list_sql(liste):
    """
    list to srting for sql script
    :param liste:
    :return:
    """
    txt = '('
    for t_res in liste:
        txt += "'{}',".format(t_res)
    txt = txt[:-1] + ')'
    return txt


class CheckTab:
    """
    Class update table
    """

    def __init__(self, mgis, mdb):
        self.mgis = mgis
        self.mdb = mdb
        self.box = ClassWarningBox()
        self.list_hist_version = ['0.0.0',
                                  '1.1.3',
                                  '2.0.0 ',
                                  '3.0.0',
                                  '3.0.1',
                                  '3.0.2',
                                  '3.0.3',
                                  '3.0.4',
                                  '3.0.5',
                                  '3.0.6',
                                  '3.0.7',
                                  '3.1.0',
                                  '3.1.1',
                                  '3.1.2',
                                  '4.0.0',
                                  '4.0.1',
                                  '4.0.2',
                                  '4.0.3',
                                  '4.0.4',
                                  '4.0.5',
                                  '4.0.6',
                                  '4.0.7',
                                  '4.0.8',
                                  '4.0.9',
                                  '4.0.10',
                                  '4.0.11',
                                  '4.0.12',
                                  '4.0.13',
                                  '4.0.14',
                                  '5.0.1',
                                  '5.0.2',
                                  '5.0.3',
                                  ]
        self.dico_modif = {'3.0.0': {
            'add_tab': [{'tab': Maso.struct_config, 'overwrite': False},
                        {'tab': Maso.profil_struct, 'overwrite': False},
                        {'tab': Maso.struct_param, 'overwrite': False},
                        {'tab': Maso.struct_elem, 'overwrite': False},
                        {'tab': Maso.struct_elem_param, 'overwrite': False},
                        {'tab': Maso.struct_abac, 'overwrite': False},
                        {'tab': Maso.struct_laws, 'overwrite': False}],
            'fct': [lambda: self.fill_struct()],
            'alt_tab': [{'tab': 'runs',
                         'sql': ["ALTER TABLE {0}.runs ADD COLUMN IF NOT "
                                 "EXISTS comments text;"]}],
        },
            '3.0.1': {'add_tab': [
                {'tab': Maso.struct_fg, 'overwrite': False},
                {'tab': Maso.struct_fg_val, 'overwrite': False},
                {'tab': Maso.weirs_mob_val, 'overwrite': False}],
                'alt_tab': [{'tab': 'weirs', 'sql': [
                    "ALTER TABLE {0}.weirs ADD COLUMN IF NOT "
                    "EXISTS active_mob boolean DEFAULT FALSE;",
                    "ALTER TABLE {0}.weirs ADD COLUMN IF NOT "
                    "EXISTS method_mob text;"]}],
                'fct': [lambda: self.update_setting_json()]},
            '3.0.2': {'add_tab': [
                {'tab': Maso.results_old, 'overwrite': False},
                {'tab': Maso.results_sect, 'overwrite': False},
                {'tab': Maso.results_var, 'overwrite': False},
                {'tab': Maso.runs_graph, 'overwrite': False},
            ],
                'alt_tab': [{'tab': 'runs', 'sql': [
                    "ALTER TABLE {0}.runs ADD COLUMN IF NOT "
                    "EXISTS init_date timestamp "
                    "without time zone;"]},
                            {'tab': 'outputs', 'sql': [
                                "ALTER TABLE {0}.outputs ADD COLUMN IF NOT "
                                "EXISTS active boolean DEFAULT TRUE;"]},
                            ],
                'fct': [lambda: self.create_var_result(),
                        lambda: self.convert_all_result(),
                        lambda: self.fill_init_date_runs()],
            },
            '3.0.3': {},
            '3.0.4': {},
            '3.0.5': {},
            '3.0.6': {
                'add_tab': [{'tab': Maso.visu_flood_marks,
                             'overwrite': False}],

                'alt_tab': [{'tab': 'laws',
                             'sql': [
                                 "ALTER TABLE {0}.laws ADD COLUMN IF NOT "
                                 "EXISTS active boolean NOT NULL DEFAULT TRUE;",
                             ]},
                            {'tab': 'observations',
                             'sql': [
                                 "ALTER TABLE {0}.observations ADD COLUMN IF "
                                 "NOT EXISTS comment text;",
                             ]},
                            {'tab': 'branchs',
                             'sql': [
                                 "UPDATE {0}.branchs SET branch = 1 "
                                 "WHERE branch IS NULL ;",
                                 "UPDATE {0}.branchs SET zonenum = 1 "
                                 "WHERE zonenum IS NULL;",
                                 "ALTER TABLE {0}.branchs ALTER COLUMN branch "
                                 "SET NOT NULL;",
                                 "ALTER TABLE {0}.branchs ALTER COLUMN zonenum "
                                 "SET NOT NULL;",

                             ]},
                            {'tab': 'flood_marks',
                             'sql': [
                                 "ALTER TABLE {0}.flood_marks ADD COLUMN IF "
                                 "NOT EXISTS active boolean NOT NULL "
                                 "DEFAULT TRUE;"]},
                            {'tab': 'outputs',
                             'sql': [
                                 "ALTER TABLE {0}.outputs ADD COLUMN IF NOT "
                                 "EXISTS active boolean NOT NULL "
                                 "DEFAULT TRUE;"]},

                            ],
                'fct': [lambda: self.update_tab_306(),
                        lambda: self.add_trigger_update_306()
                        ],

            },
            '3.0.7': {'fct': [
                lambda: self.update_fct_calc_abs(),
            ]
            },
            '3.1.0': {'del_tab': ['resultats', 'resultats_basin',
                                  'resultats_links']},
            '3.1.1': {},
            '3.1.2': {},
            '4.0.0': {'fct': [
                lambda: self.update_400(),
            ],
                'alt_tab': [{'tab': 'results_old',
                             'sql': [
                                 "CREATE INDEX IF NOT EXISTS "
                                 "results_old_id_runs_pknum "
                                 "ON {0}.results_old(id_runs, pknum);",
                                 "CREATE INDEX IF NOT EXISTS "
                                 "results_old_id_runs_time  "
                                 "ON {0}.results_old(id_runs, time);",
                             ]},
                            {'tab': 'observations',
                             'sql': [
                                 "CREATE INDEX IF NOT EXISTS "
                                 "observations_code_typ  "
                                 "ON {0}.observations(code, type);",
                             ]},
                            ]
            },
            '4.0.1': {},
            '4.0.2': {
                'add_tab': [
                    {'tab': Maso.runs_plani, 'overwrite': False}, ],
                'alt_tab': [{'tab': 'profiles',
                             'sql': [
                                 "ALTER TABLE {0}.profiles ADD COLUMN IF NOT "
                                 "EXISTS  zleftminbed FLOAT;",
                                 "ALTER TABLE {0}.profiles ADD COLUMN IF NOT "
                                 "EXISTS  zrightminbed FLOAT;",
                             ]}, ],
                'fct': [
                    lambda: fill_zminbed(self.mdb),
                    lambda: self.laws_to_new(),
                ],
            },
            '4.0.3': {},
            '4.0.4': {},
            '4.0.5': {'fct': [lambda: self.update_400(),
                              lambda: self.laws_to_new()], },
            '4.0.6': {},
            '4.0.7': {},
            '4.0.8': {},
            '4.0.9': {},
            '4.0.10': {},
            '4.0.11': { 'fct': [lambda: self.update_4011()], },
            '4.0.12': {},
            '4.0.13': {'fct': [lambda: self.change_branchs_chstate_active()], },
            '4.0.14': {},
            '5.0.1': {},
            '5.0.2': {'fct': [lambda: self.change_clone_shema_trigger()], },
            '5.0.3': {},
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
                obj = self.mdb.process_masobject(Maso.admin_tab,
                                                 'pg_create_table')
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

        curent_v_tab = self.get_version()
        try:
            pos = self.list_hist_version.index(curent_v_tab)
        except ValueError as errval:
            self.mgis.add_info('Error: The version {}'.format(errval))
            raise ValueError()

        pos_fin = self.list_hist_version.index(version)
        tabs_no = deepcopy(tabs)

        if len(self.list_hist_version[pos + 1:pos_fin + 1]) > 0:
            ok = self.box.yes_no_q("WARNING:\n "
                                   "Do you want update tables for {} schema ?\n"
                                   "There is a risk of table corruption.\n "
                                   "Remember to make backup copies if it's "
                                   "important model.".format(self.mdb.SCHEMA))
            if ok:
                list_test_ver = []
                for ver in self.list_hist_version[pos + 1:pos_fin + 1]:
                    list_test = []
                    if ver in self.dico_modif.keys():
                        modif = self.dico_modif[ver]
                        if len(modif) > 0:
                            for proc in ['add_tab', 'alt_tab', 'fct',
                                         'del_tab']:
                                test_gd = True
                                if proc in modif.keys():
                                    if proc != 'fct':
                                        lst_tab = modif[proc]
                                        for tab in lst_tab:
                                            if proc == 'add_tab':
                                                valid, tab_name = self.add_tab(
                                                    tab["tab"],
                                                    tab["overwrite"])
                                            elif proc == 'alt_tab':
                                                tab_name = tab["tab"]
                                                valid = self.alt_tab(tab_name,
                                                                     tab["sql"])
                                            elif proc == 'del_tab':
                                                tab_name = tab
                                                valid = self.del_tab(tab_name)
                                            else:
                                                valid = False
                                            # print (proc, tab_name, valid)
                                            if valid:
                                                if proc != 'del_tab':
                                                    self.updat_num_v(tab_name,
                                                                     ver)
                                                else:
                                                    self.del_num_v(tab_name)
                                            else:
                                                test_gd = False
                                            if tab_name in tabs_no:
                                                tabs_no.remove(tab_name)
                                    else:
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
                        self.mgis.add_info('ERROR: Update table ************')
                        self.mgis.add_info('ERROR :{}'.format(tab_name))
                        # if self.mgis.DEBUG:
                        #     self.mgis.add_info('ERROR :{}'.format(tab_name))
                if False not in list_test_ver:
                    tabs = self.mdb.list_tables(self.mdb.SCHEMA)
                    self.all_version(tabs, ver)

            else:
                self.mgis.add_info(
                    "********* Cancel of update table ***********")

    def get_version(self, table=None):
        """ get version"""
        if table:
            info = self.mdb.select('admin_tab',
                                   where="table_ = {}".format(table),
                                   list_var=['version_'])
            curent_v_tab = info['version_'][0]
        else:
            min_ver = self.mdb.select_min('version_', 'admin_tab')
            curent_v_tab = min_ver
        return curent_v_tab

    def all_version(self, tabs, version=None):
        if not version:
            version = self.list_hist_version[0]
        for name_tab in tabs:
            self.updat_num_v(name_tab, version)

    def updat_num_v(self, name_tab, version):
        """
        updat version number
        :return:
        """

        sql = "SELECT * FROM {0}.admin_tab WHERE  table_ = '{1}' " \
            .format(self.mdb.SCHEMA, name_tab)
        row = self.mdb.run_query(sql, fetch=True)
        if len(row) > 0:
            sql = "UPDATE {0}.admin_tab SET version_  = '{1}' " \
                  "WHERE table_ = '{2}';" \
                .format(self.mdb.SCHEMA, version, name_tab)
            self.mdb.execute(sql)
        else:
            sql = "INSERT INTO {0}.admin_tab (table_, version_)" \
                  " VALUES ('{1}', '{2}')".format(self.mdb.SCHEMA, name_tab,
                                                  version)
            self.mdb.execute(sql)

    def del_num_v(self, name_tab):
        """
        delete table in admin_tab
        :param name_tab: table name
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
        :param tab: list of tables
        :param overwrite : overwrite table
        """

        valid = True
        try:
            tab.overwrite = overwrite
            obj = self.mdb.process_masobject(tab, 'pg_create_table')
            if self.mgis.DEBUG:
                self.mgis.add_info('  {0} OK'.format(obj.name))
            return valid, obj.name
        except:
            valid = False
            self.mgis.add_info('failure!<br>Add table {0}'.format(tab))

            return valid, None

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
            if txt_sql != '':
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
        self.mdb.insert_var_to_result_var(dossier)

    def convert_all_result(self):
        """
        conversion between the previous results
        table format to the new for all results
        """
        convert = False
        try:
            rows = self.mdb.run_query(
                "SELECT DISTINCT type_res FROM {0}.results_var".format(
                    self.mdb.SCHEMA),
                fetch=True)
            lst_typ_res = [r[0] for r in rows]
            rows = self.mdb.run_query(
                "SELECT id, run, scenario FROM {0}.runs".format(
                    self.mdb.SCHEMA), fetch=True)
            dict_runs = {r[0]: {"run": r[1], "scen": r[2]} for r in rows}

            for typ_res in lst_typ_res:
                rows = self.mdb.run_query(
                    "SELECT DISTINCT id_runs FROM {0}.results_old WHERE var in "
                    "(SELECT id FROM {0}.results_var WHERE type_res = '{1}') "
                    "".format(self.mdb.SCHEMA, typ_res),
                    fetch=True)
                lst_exist = [r[0] for r in rows]
                for run in dict_runs.keys():
                    if run not in lst_exist:
                        self.convert_result(run, typ_res)

            rows = self.mdb.run_query(
                "SELECT DISTINCT id_runs FROM {0}.results_sect".format(
                    self.mdb.SCHEMA),
                fetch=True)
            lst_exist = [r[0] for r in rows]
            for run in dict_runs.keys():
                if run not in lst_exist:
                    self.fill_result_sect(run)

            # ADD runs_graph
            for id_runs in dict_runs.keys():
                if id_runs not in lst_exist:

                    sql = "SELECT DISTINCT var FROM {0}.results_old WHERE " \
                          "id_runs ={1} ORDER BY var"
                    rows = self.mdb.run_query(
                        sql.format(self.mdb.SCHEMA, id_runs), fetch=True)
                    lst_var = [var[0] for var in rows]

                    sql = "SELECT DISTINCT ON (type_res) id, type_res FROM  " \
                          "{0}.results_var " \
                          "WHERE id IN {1} ORDER BY type_res"
                    rows = self.mdb.run_query(
                        sql.format(self.mdb.SCHEMA, list_sql(lst_var)),
                        fetch=True)
                    lst_typvar = [var[1] for var in rows]
                    lst_var_select = [var[0] for var in rows]
                    list_value = []
                    # comput Zmax if there is Z
                    sql = "SELECT id FROM  {0}.results_var WHERE var='Z';" \
                          "".format(self.mdb.SCHEMA)
                    id_z = self.mdb.run_query(sql, fetch=True)

                    for id_var, type_res in enumerate(lst_typvar):
                        sql = "SELECT id FROM  {0}.results_var WHERE id " \
                              "IN {1} AND type_res = '{2}' " \
                              "ORDER BY type_res".format(self.mdb.SCHEMA,
                                                         list_sql(lst_var),
                                                         type_res)
                        rows = self.mdb.run_query(sql, fetch=True)
                        lst_var2 = [var[0] for var in rows]
                        list_value.append(
                            [id_runs, type_res, 'var', json.dumps(lst_var2)])

                        sql = "SELECT DISTINCT time FROM {0}.results_old " \
                              "WHERE id_runs ={1} " \
                              "AND var = {2} ORDER BY time" \
                              "".format(self.mdb.SCHEMA, id_runs,
                                        lst_var_select[id_var])
                        rows = self.mdb.run_query(sql, fetch=True)
                        lst_time = [var[0] for var in rows]
                        list_value.append(
                            [id_runs, type_res, 'time', json.dumps(lst_time)])

                        sql = "SELECT DISTINCT pknum FROM {0}.results_old " \
                              "WHERE id_runs ={1} " \
                              "AND var = {2} ORDER BY pknum" \
                              "".format(self.mdb.SCHEMA, id_runs,
                                        lst_var_select[id_var])
                        rows = self.mdb.run_query(sql, fetch=True)
                        lst_pknum = [var[0] for var in rows]
                        list_value.append(
                            [id_runs, type_res, 'pknum', json.dumps(lst_pknum)])

                        if type_res == "opt":
                            try:
                                dico_zmax = {}
                                for pknum in lst_pknum:
                                    if id_z[0][0] in lst_var:
                                        sql = "SELECT MAX(val) FROM " \
                                              "{0}.results_old " \
                                              "WHERE var = {2} " \
                                              "AND id_runs={1} AND " \
                                              "pknum ={3};".format(
                                            self.mdb.SCHEMA, id_runs,
                                            id_z[0][0], pknum)
                                        rows = self.mdb.run_query(sql,
                                                                  fetch=True)
                                        dico_zmax[pknum] = rows[0][0]
                                list_value.append([id_runs, 'opt', 'zmax',
                                                   json.dumps(dico_zmax)])
                            except Exception:
                                pass
                    sql = "INSERT INTO " \
                          "{0}.runs_graph(id_runs, type_res,var,val) " \
                          "VALUES (%s,%s,%s, %s); \n".format(self.mdb.SCHEMA)

                    self.mdb.run_query(sql, many=True, list_many=list_value)
            convert = True
        except Exception as e:
            self.mgis.add_info("Error convert_all_result : {}".format(str(e)))
            return False
        if convert:
            # TODO delete table
            # self.mdb.drop_table('resutlats')
            # self.mdb.drop_table('resutlats_basin')
            # self.mdb.drop_table('resultats_links')
            pass
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
        elif typ_res.split('_')[0] == 'tracer':
            tab_src = "resultats"
            col_pknum = "pk"
        elif typ_res in ["struct", "weirs"]:
            return
        else:
            tab_src = None
            col_pknum = None

        row = self.mdb.run_query(
            "SELECT run, scenario FROM {0}.runs WHERE id = {1}".format(
                self.mdb.SCHEMA, id_run),
            fetch=True)
        run_run, run_scen = row[0]

        rows = self.mdb.run_query(
            "SELECT column_name FROM information_schema.columns WHERE "
            "table_schema = '{0}' AND table_name = '{1}' "
            "AND ordinal_position > ("
            "SELECT ordinal_position FROM information_schema.columns "
            "WHERE table_schema = '{0}' AND table_name = '{1}' "
            "AND column_name = '{2}')".format(self.mdb.SCHEMA, tab_src,
                                              col_pknum), fetch=True)

        lst_var_exist = [r[0] for r in rows]
        self.mdb.execute(
            "DELETE FROM {0}.results_old WHERE results_old.id_runs = {1} AND "
            "results_old.var IN (SELECT id FROM {0}.results_var "
            "WHERE type_res = '{2}')".format(self.mdb.SCHEMA, id_run, tab_src))

        rows = self.mdb.run_query("SELECT id, var FROM {0}.results_var "
                                  "WHERE type_res = '{2}' ORDER BY id".format(
            self.mdb.SCHEMA, tab_src, typ_res),
            fetch=True)
        if typ_res.split('_')[0] == 'tracer':
            lst_var = [[row[0], 'c{}'.format(r + 1)] for r, row in
                       enumerate(rows)]
        else:
            lst_var = rows

        for id_var, nm_var in lst_var:
            if nm_var.lower() in lst_var_exist:
                sql = "INSERT INTO {0}.results_old (" \
                      "SELECT {5}, {3}.t, {3}.{4}, {1}, {3}.{2} " \
                      "FROM {0}.{3} WHERE " \
                      "{3}.{2} is Not Null AND {3}.run = '{6}' " \
                      "AND {3}.scenario = '{7}')".format(self.mdb.SCHEMA,
                                                         id_var, nm_var.lower(),
                                                         tab_src, col_pknum,
                                                         id_run, run_run,
                                                         run_scen)
                self.mdb.execute(sql)

    def fill_result_sect(self, id_run):
        """
        fill results section table
        :param id_run: run index
        :return:
        """
        info = self.mdb.select('resultats',
                               where='(run, scenario) = (SELECT run, scenario '
                                     'FROM {}.runs WHERE id= {})'.format(
                                   self.mdb.SCHEMA, id_run),
                               order='t',
                               list_var=['pk', 'branche', 'section'])
        lst_id = [id_run for i in range(len(info['pk']))]
        lst_insert = list(
            set(zip(lst_id, info['pk'], info['branche'], info['section'])))
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
        return True

    def fill_init_date_runs(self):
        """
        fill the initial date in runs tab
        :return:
        """
        try:
            info = self.mdb.select('runs', list_var=["id", "t", 'init_date'])
            for i, id in enumerate(info['id']):
                ltime = info['t'][i]
                init_date = info['init_date'][i]
                if not init_date:
                    ltime = ltime.split(",")
                    init_date = ltime[0].strip()
                    try:
                        date = datetime.strptime(init_date, '%Y-%m-%d %H:%M')
                        init_date = "{:%Y-%m-%d %H:%M:00}".format(date)
                        sql = "UPDATE {0}.runs SET init_date ='{1}' " \
                              "WHERE id ={2}".format(self.mdb.SCHEMA,
                                                     init_date,
                                                     id)
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
            list_col = self.mdb.list_columns('profiles')
            sql = ''
            if 'struct' in list_col:
                sql = "ALTER TABLE {0}.profiles DROP COLUMN " \
                      "IF EXISTS  struct;\n"
            sql += "ALTER TABLE {0}.profiles ADD COLUMN struct integer " \
                   "DEFAULT 0;"
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
            list_tab = ['branchs', 'profiles', 'tracer_lateral_inflows',
                        'lateral_weirs',
                        'lateral_inflows', 'hydraulic_head', 'weirs',
                        'extremities',
                        'links', 'basins', 'outputs', 'flood_marks', 'laws']
            txt = ''
            for tab in list_tab:
                txt += "ALTER TABLE {0}.{1} ALTER COLUMN active " \
                       "SET DEFAULT TRUE;".format(self.mdb.SCHEMA, tab)
                txt += '\n'
                txt += "UPDATE {0}.{1} SET active = TRUE WHERE " \
                       "active IS NULL;".format(self.mdb.SCHEMA, tab)
                txt += '\n'
                txt += "ALTER TABLE {0}.{1} ALTER COLUMN " \
                       "active SET NOT NULL;".format(self.mdb.SCHEMA, tab)
                txt += '\n'
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

            qry = 'DROP TRIGGER IF EXISTS branchs_chstate_active ' \
                  'ON {}.branchs;\n'.format(self.mdb.SCHEMA)
            qry += 'DROP TRIGGER IF EXISTS basins_chstate_active ' \
                   'ON {}.basins;\n'.format(self.mdb.SCHEMA)
            qry += 'DROP TRIGGER IF EXISTS flood_marks_calcul_abscisse ' \
                   'ON {}.flood_marks;\n'.format(self.mdb.SCHEMA)
            qry += 'DROP TRIGGER IF EXISTS flood_marks_calcul_abscisse_flood ' \
                   'ON {}.flood_marks;\n'.format(self.mdb.SCHEMA)
            qry += 'DROP TRIGGER IF EXISTS flood_marks_delete_point_flood ' \
                   'ON {}.flood_marks;\n'.format(self.mdb.SCHEMA)
            qry += '\n'
            cl = Maso.class_fct_psql()
            qry += cl.pg_chstate_branch()
            qry += '\n'
            qry += 'CREATE TRIGGER branchs_chstate_active\n' \
                   ' AFTER UPDATE\n  ON {0}.branchs\n'.format(self.mdb.SCHEMA)
            qry += ' FOR EACH ROW\n' \
                   'WHEN (OLD.active IS DISTINCT FROM NEW.active)\n' \
                   'EXECUTE PROCEDURE chstate_branch();\n'
            qry += '\n'
            qry += cl.pg_chstate_basin()
            qry += '\n'
            qry += 'CREATE TRIGGER basins_chstate_active\n' \
                   ' AFTER UPDATE\n  ON {0}.basins\n'.format(self.mdb.SCHEMA)
            qry += ' FOR EACH ROW\n' \
                   'WHEN (OLD.active IS DISTINCT FROM NEW.active)\n' \
                   'EXECUTE PROCEDURE chstate_basin();\n'
            qry += '\n'
            cl = Maso.flood_marks()
            cl.schema = self.mdb.SCHEMA
            qry += cl.pg_clear_tab()
            qry += '\n'
            qry += cl.pg_calcul_abscisse_flood()
            qry += '\n'
            self.mdb.run_query(qry)
            return True
        except Exception as e:
            self.mgis.add_info(
                "Error add_trigger_update_306: {}".format(str(e)))
            return False

    def update_fct_calc_abs(self):
        try:
            lst_fct = [
                "public.update_abscisse_branch(_tbl_branchs regclass)",
                "public.update_abscisse_point"
                "(_tbl regclass, _tbl_branchs regclass)",
                "public.update_abscisse_profil"
                "(_tbl regclass, _tbl_branchs regclass)",
                "public.abscisse_branch"
                "(_tbl_branchs regclass, id_branch integer)",
                "public.abscisse_point"
                "(_tbl regclass, _tbl_branchs regclass, id_point integer)",
                "public.abscisse_profil"
                "(_tbl regclass, _tbl_branchs regclass, id_prof integer)",
            ]
            qry = ''
            for fct in lst_fct:
                qry += "DROP FUNCTION IF EXISTS {};\n".format(fct)
            self.mdb.run_query(qry)
            self.mdb.add_fct_for_update_pk()
            return True
        except Exception as e:
            self.mgis.add_info("Error update_fct_calc_abs: {}".format(str(e)))
            return False

    def clean_tab_admin(self):
        """
        clean tab in admin
        :return:
        """
        sql = "DELETE FROM {0}.admin_tab WHERE NOT(table_ IN ( " \
              "SELECT table_name FROM information_schema.tables " \
              "WHERE table_schema = '{0}'))".format(self.mdb.SCHEMA)
        self.mdb.run_query(sql)

    def update_400(self):
        """ update 4.0.0 version"""
        try:
            self.clean_tab_admin()
            cl = Maso.class_fct_psql()
            lfct = [cl.pg_clone_schema()]
            qry = ''
            for sql in lfct:
                qry += sql
                qry += '\n'
            self.mdb.run_query(qry)

            return True
        except Exception as e:
            self.mgis.add_info("Error  update_400: {}".format(str(e)))
            return False

    def laws_to_new(self):
        """ add new table law and convert"""
        try:
            lst_tab = self.mdb.list_tables()
            if 'laws' in lst_tab:
                info = self.mdb.select('laws')
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
                if 'id' in info.keys():
                    # law_config
                    tab = {id: {'comment': ''} for id in
                           range(len(info['name']))}
                    cmpt = 1
                    for key, item in info.items():
                        if key in ["z", "flowrate", "time",
                                   "z_upstream", "z_downstream",
                                   "z_lower", "z_up"]:
                            pass
                        elif key in ['starttime', 'endtime']:
                            for id, val in enumerate(item):
                                if val:
                                    tab[id][key] = val.strftime(
                                        "%Y-%m-%d %H:%M:%S")
                                else:
                                    tab[id][key] = None
                        elif key in ['active']:
                            for id, val in enumerate(item):
                                tab[id][key] = val
                        elif key == 'name':
                            for id, val in enumerate(item):
                                if val in [tmp['name'] for tmp in tab.values()
                                           if 'name' is tmp.keys()]:
                                    tab[id]["name"] = val + '{}'.format(cmpt)
                                    cmpt += 1
                                else:
                                    tab[id]["name"] = val
                                tab[id]['geom_obj'] = val
                        elif key == 'type':
                            for id, val in enumerate(item):
                                tab[id]['id_law_type'] = val

                    listimport = ['id', 'name', 'geom_obj', 'starttime',
                                  'endtime',
                                  'id_law_type', 'active', 'comment']

                    if len(tab.keys()) > 0:
                        err = self.mdb.insert("law_config",
                                              tab,
                                              listimport)
                        if len(tab.keys()) > 0:
                            maxk = max(tab.keys())
                            sql = "ALTER SEQUENCE {}.law_config_id_seq " \
                                  "RESTART WITH {};".format(self.mdb.SCHEMA,
                                                            maxk + 1)
                            self.mdb.run_query(sql)
                        if err:
                            self.mgis.add_info(
                                "Error: Insert law_config")
                            self.del_tab("law_config")
                            return False

            if "law_values" not in lst_tab:
                vval, _ = self.add_tab(Maso.law_values, False)
                if not vval:
                    self.mgis.add_info("Error  add table: law_values")
                    return False

                if 'id' in info.keys():
                    # law_value
                    valinsert = {
                        "id_law": [], "id_var": [], "id_order": [], "value": []
                    }
                    for id_loi in range(len(info['name'])):
                        id_type = info['type'][id_loi]
                        lst_var = [tmp['code'] for tmp in
                                   dico_typ_law[id_type]['var']]

                        for id_var, var in enumerate(lst_var):
                            # lst_val = info[conv_dict[var]][id_loi].split()
                            lst_val = info[var][id_loi].split()
                            for id_val, val in enumerate(lst_val):
                                valinsert["id_law"].append(id_loi)
                                valinsert["id_var"].append(id_var)
                                valinsert["id_order"].append(id_val)
                                valinsert["value"].append(float(val))
                    if len(valinsert['id_law']) > 0:
                        err = self.mdb.insert2("law_values", valinsert)
                        if err:
                            self.mgis.add_info(
                                "Error  Insert law_values")
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

        if 'results_old' not in lst_tab:
            sql = 'ALTER TABLE {0}.results RENAME TO results_old;'
            sql = sql.format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                sorti = False
        info = self.mdb.select_one('results_old')
        if info:
            sql = "SELECT FROM {0}.results_old"
            # creation results_idx
            sql = 'INSERT INTO {0}.results_idx(id_runs, "time", pknum) ' \
                  'SELECT DISTINCT id_runs,  "time", pknum  FROM {0}.results_old;'
            sql = sql.format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                sorti = False
            sql = "INSERT INTO {0}.results_val(idruntpk, var, val) " \
                  "SELECT idruntpk, var, val   FROM {0}.results_idx " \
                  "Inner join  {0}.results_old " \
                  "on {0}.results_old.id_runs = {0}.results_idx.id_runs " \
                  "AND {0}.results_old.time = {0}.results_idx.time " \
                  "AND {0}.results_old.pknum = {0}.results_idx.pknum;"
            sql = sql.format(self.mdb.SCHEMA)
            err = self.mdb.run_query(sql)
            if err:
                sorti = False
        sql = 'CREATE OR REPLACE VIEW {0}.results ' \
              'AS SELECT id_runs, "time", pknum,  var, val  FROM {0}.results_idx 	' \
              'Inner join  {0}.results_val ' \
              'on {0}.results_val.idruntpk = {0}.results_idx.idruntpk;'
        sql = sql.format(self.mdb.SCHEMA)
        err = self.mdb.run_query(sql)
        if err:
            sorti = False
        print(sorti)
        return sorti

    def change_branchs_chstate_active(self):
        sql = "DROP TRIGGER IF EXISTS branchs_chstate_active " \
              "ON {0}.branchs; " \
              "CREATE TRIGGER branchs_chstate_active " \
              "AFTER UPDATE OF active ON {0}.branchs " \
              "FOR EACH ROW EXECUTE PROCEDURE public.chstate_branch();".format(self.mdb.SCHEMA)
        self.mdb.run_query(sql)

    def change_clone_shema_trigger(self):
        """ update 5.0.2 version"""
        self.change_branchs_chstate_active()
        qry = "DROP FUNCTION clone_schema(text, text,text, boolean, boolean);"
        try:
            cl = Maso.class_fct_psql()
            lfct = [cl.pg_clone_schema()]
            qry = ''
            for sql in lfct:
                qry += sql
                qry += '\n'
            self.mdb.run_query(qry)

            return True
        except Exception as e:
            self.mgis.add_info("Error  update_502: {}".format(str(e)))
            return False