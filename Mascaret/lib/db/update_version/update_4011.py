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
from lib.db import MasObject as Maso


class ClassUpdate4011:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update4011(self):
        sorti = True
        lst_tab = self.mdb.list_tables()
        err, _ = self.cht.add_tab(Maso.results_idx, False)
        if not err:
            sorti = False
        err, _ = self.cht.add_tab(Maso.results_val, False)
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
