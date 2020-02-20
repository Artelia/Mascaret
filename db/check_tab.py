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
        # for add table [ ['ADD TAB',[list_table]]
        # for delete [ ['DEL TAB',[list_table]]
        self.dico_modif = {'2.9.9': {'admin_tab': ["ALTER TABLE {0}.admin_tab ADD COLUMN "
                                                   "IF NOT EXISTS toto double precision;"]},
                           '3.0.0': {'admin_tab': ["ALTER TABLE {0}.admin_tab DROP COLUMN IF EXISTS toto ;"]}}
        self.list_hist_version = ['0.0.0', '2.9.9', '3.0.0']

    def update_adim(self):
        """
        Update admin_tab and check table

        :return:
        """

        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        version = read_version(self.mgis.masplugPath)
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
                    for key in modif:
                        plante = self.tab_modif(modif[key], key, ver)
                        if not plante:
                            test_gd = False
                        else:
                            self.updat_num_v(key, ver)

                        if key in tabs_no:
                            tabs_no.remove(key)
            if test_gd:
                self.all_version(tabs_no, ver)
            else:
                self.mgis.add_info('ERROR: Update table ************')

    def all_version(self, tabs, version=None):
        if not version:
            version = self.list_hist_version[0]
        for name_tab in tabs:
            self.updat_num_v(name_tab, version)

            #

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

    def tab_modif(self, liste, name, ver):
        """
        Apply changes to table
        :param liste: modification list
        :param name: table name
        :param ver:  table version
        :return: bool : if run = True, if not run = False
        """
        plante = True
        sql = ''
        for req in liste:
            if isinstance(req, list):
                if req[0] == 'ADD TAB':
                    plante = self.add_tab(req[1], ver)
                elif req[0] == 'DEL TAB':
                    plante = self.del_tab(req[1])
            else:
                sql += req.format(self.mdb.SCHEMA) + '\n'
        try:
            self.mdb.execute(sql)
        except:
            plante = False
            self.mgis.add_info('failure! to update the {} table to the {} version '.format(name, ver))
        return plante

    def add_tab(self, tables, version):
        """
        Add table
        :param tables: list of tables
        """
        # tables = [
        #     Maso.struct_fg, Maso.struct_fg_val,
        #     Maso.weirs_mob_val
        # ]
        plante = True
        tables.sort(key=lambda x: x().order)
        for masobj_class in tables:
            try:
                masobj_class.overwrite = True
                obj = self.mdb.process_masobject(masobj_class, 'pg_create_table')
                self.updat_num_v(obj.name, version)
                if self.mgis.DEBUG:
                    self.mgis.add_info('  {0} OK'.format(obj.name))

            except:
                plante = False
                self.mgis.add_info('failure!<br>{0}'.format(masobj_class))

        return plante

    def del_tab(self, tables):
        plante = True
        for tab in tables:
            plante = self.mdb.drop_table(tab)
            self.del_num_v(tab)

        return plante
