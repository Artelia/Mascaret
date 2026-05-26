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
 *   the Free Software Foundation; either version 2 of the License, or     *
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
            sql = "ALTER TABLE {schema}.results RENAME TO results_old;"
            err = self.mdb.run_query(sql, schema=True)
            if err:
                sorti = False
        info = self.mdb.select_one("results_old")
        if info:
            sql = "SELECT FROM {schema}.results_old"
            # creation results_idx
            sql = (
                'INSERT INTO {schema}.results_idx(id_runs, "time", pknum) '
                'SELECT DISTINCT id_runs,  "time", pknum  FROM {schema}.results_old;'
            )
            err = self.mdb.run_query(sql, schema=True)
            if err:
                sorti = False
            sql = (
                "INSERT INTO {schema}.results_val(idruntpk, var, val) "
                "SELECT idruntpk, var, val   FROM {schema}.results_idx "
                "Inner join  {schema}.results_old "
                "on {schema}.results_old.id_runs = {schema}.results_idx.id_runs "
                "AND {schema}.results_old.time = {schema}.results_idx.time "
                "AND {schema}.results_old.pknum = {schema}.results_idx.pknum;"
            )
            err = self.mdb.run_query(sql, schema=True)
            if err:
                sorti = False
        sql = (
            "CREATE OR REPLACE VIEW {schema}.results "
            'AS SELECT id_runs, "time", pknum,  var, val  FROM {schema}.results_idx \t'
            "Inner join  {schema}.results_val "
            "on {schema}.results_val.idruntpk = {schema}.results_idx.idruntpk;"
        )
        err = self.mdb.run_query(sql, schema=True)
        if err:
            sorti = False
        return sorti
