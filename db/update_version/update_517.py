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
from ClassUpdateBedDialog import update_all_bed_geometry
from db import MasObject as Maso


class ClassUpdate517:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update517(self):
        """
        Update 5.1.7
        """
        # self.mgis.add_info("*** Update 5.1.7  ***")
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        valide = True
        if valide and "visu_minor_river_bed" not in tabs:
            tabs = [Maso.visu_minor_river_bed]
            for tab in tabs:
                valid_add, _ = self.cht.add_tab(tab)
                if not valid_add:
                    self.mgis.add_info("Create  the visu_minor_river_bed table - ERROR")
                    valide = False

        if valide:
            lst_alt = [
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  leftminbed_g FLOAT;",
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  rightminbed_g FLOAT;",
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  leftstock_g FLOAT;",
                "ALTER TABLE {0}.profiles ADD COLUMN IF NOT EXISTS  rightstock_g FLOAT;",
            ]
            for sql in lst_alt:
                self.mdb.execute(sql.format(self.mdb.SCHEMA))
        if valide:
            try:
                update_all_bed_geometry(self.mdb)
            except Exception:
                self.mgis.add_info("erreur update_all_bed_geometry")

        return valide
