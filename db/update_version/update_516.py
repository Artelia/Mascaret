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
from db import MasObject as Maso

class ClassUpdate516:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update516(self):
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
                valid_add, _ = self.cht.add_tab(tab)
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
        old_vers = self.cht.check_v_masc()
        if old_vers != "8.4":
            ok = self.cht.box.yes_no_q(
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
