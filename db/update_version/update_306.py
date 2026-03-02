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


class ClassUpdate306:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update306(self):
        """add new table law and convert"""
        self.update_tab_306()
        self.add_trigger_update_306()

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
