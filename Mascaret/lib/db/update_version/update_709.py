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


class ClassUpdate709:
    """
    Database update to version 7.0.9.

    Replaces the NULL values of the mobile weirs and links regulation
    variables (DIRFG, CRITDTREG) with their default values.
    Truncates the events start/end dates to the minute.
    """

    def __init__(self, check_tab):
        """
        Initialize the update.
        :param check_tab (Check_tab): Database check object giving access to mdb and mgis
        """
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update709(self):
        """
        Run the 7.0.9 database update.
        :return: (bool) True if all the updates succeeded, otherwise False
        """
        self.mgis.add_info("*** Update 7.0.9  ***", dbg=True)
        valide = True

        # Default values for regulation variables saved as NULL
        # (combo box not containing the loaded value when saving)
        lst_default = [
            ("weirs_mob_val", "DIRFG", "D"),
            ("weirs_mob_val", "CRITDTREG", "NDTREG"),
            ("links_mob_val", "DIRFG", "D"),
            ("links_mob_val", "CRITDTREG", "NDTREG"),
        ]
        for tab, name_var, val_def in lst_default:
            sql = (
                "UPDATE {schema}." + tab + " SET value = %s "
                "WHERE name_var = %s AND value IS NULL;"
            )
            try:
                self.mdb.execute(sql, params=[val_def, name_var], schema=True)
                self.mgis.add_info(f"Clean NULL {name_var} in {tab} - OK", dbg=True)
            except Exception:
                self.mgis.add_info(f"Clean NULL {name_var} in {tab} - ERROR")
                valide = False

        # Events dates truncated to the minute (observation resolution)
        sql = (
            "UPDATE {schema}.events SET "
            "starttime = date_trunc('minute', starttime), "
            "endtime = date_trunc('minute', endtime) "
            "WHERE starttime <> date_trunc('minute', starttime) "
            "OR endtime <> date_trunc('minute', endtime);"
        )
        try:
            self.mdb.execute(sql, schema=True)
            self.mgis.add_info("Truncate events dates to the minute - OK", dbg=True)
        except Exception:
            self.mgis.add_info("Truncate events dates to the minute - ERROR")
            valide = False
        return valide
