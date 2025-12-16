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


class ClassUpdate640:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update640(self):
        self.mgis.add_info("*** Update 6.4.0  ***")
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        # if "assim_config" in tabs:
        #     sql = f"ALTER TABLE {self.mdb.SCHEMA}.assim_config RENAME TO assim_config_old;"
        #     self.mdb.execute(sql)
        # if "assim_ks" in tabs:
        #     sql = f"ALTER TABLE {self.mdb.SCHEMA}.assim_ks RENAME TO assim_ks_old;"
        #     self.mdb.execute(sql)
        # if "assim_law" in tabs:
        #     sql = f"ALTER TABLE {self.mdb.SCHEMA}.assim_law RENAME TO assim_law_old;"
        #     self.mdb.execute(sql)
        lst_add_tab = ["assim_config", "assim_ks", "assim_law"]
        valide = True
        for attr in lst_add_tab:
            if attr not in tabs:
                valid_add, _ = self.cht.add_tab(getattr(Maso, attr))
                if not valid_add:
                    self.mgis.add_info(f"Create  the {attr} table - ERROR")
                    valide = False

        lst_alt = [
            "ALTER TABLE {0}.outputs ADD COLUMN IF NOT EXISTS  obsZ_stdErr DOUBLE PRECISION DEFAULT 0.05;",
            "ALTER TABLE {0}.outputs ADD COLUMN IF NOT EXISTS  obsQ_stdErr DOUBLE PRECISION DEFAULT 10;",
            "ALTER TABLE {0}.outputs ADD COLUMN IF NOT EXISTS  obsQ_rejectLimit DOUBLE PRECISION DEFAULT NULL;",
            "ALTER TABLE {0}.outputs ADD COLUMN IF NOT EXISTS  obsZ_rejectLimit DOUBLE PRECISION DEFAULT NULL;",
        ]
        # Alter colonne value en text
        for sql in lst_alt:
            try:
                self.mdb.execute(sql.format(self.mdb.SCHEMA))
            except Exception :
                self.mgis.add_info(f"Alter  the output table - ERROR")
                valide = False
        return valide