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

class ClassUpdate511:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab


    def update511(self):
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
            new_ver = self.cht.get_version()
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
                valid_add, _ = self.cht.add_tab(tab)
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
            ok = self.cht.box.info(
                "WARNING:\n\n"
                "Check the profiles : \n\n"
                "{}\n\n"
                "because they intersected two branches:\n".format(txt)
            )

        self.mgis.add_info("******")
        return valid