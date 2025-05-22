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
import os
from db import MasObject as Maso

class ClassUpdate512:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update512(self):
        #self.mgis.add_info("*** Update 5.1.2  ***")
        valide = True
        valid = True
        if valide:
            sql = "DROP TRIGGER IF EXISTS basins_chstate_active ON {}.basins;".format(
                self.mdb.SCHEMA
            )
            err1 = self.mdb.run_query(sql)
            tabs_sql = ["basins", Maso.basins]
            obj = Maso.basins()
            obj.schema = self.mdb.SCHEMA
            sql = obj.pg_updat_actv()
            err2 = self.mdb.run_query(sql)
            if err2:
                self.mgis.add_info("Fixe error basins_chstate_active - ERROR")
                valid = False
        if valide:
            lst_tab = self.mdb.list_tables(schema=self.mdb.SCHEMA)
            lst_admin_tab = self.mdb.select("admin_tab", list_var=["table_"])
            if "results_old" in lst_tab:
                self.mdb.drop_table("results_old")
            if "results_old" in lst_admin_tab["table_"]:
                self.mdb.delete("admin_tab", where="table_= 'results_old'")

            if "runs_graph" not in lst_tab:
                valid, tab_name = self.cht.add_tab(Maso.runs_graph, False)
                self.cht.updat_num_v(tab_name, "5.1.2")

            if valide:
                valid = self.cht.update_clone()
                if not valid:
                    self.mgis.add_info("Error to update clone function")
            test = self.mdb.select("parametres", where="parametre ='decentrement'")
            if valid and not len(test["id"]) > 0:
                try:
                    fichparam = os.path.join(self.mgis.dossier_sql, "parametres.csv")
                    # self.run_query(req.format(self.SCHEMA, fichparam))
                    liste_value = []
                    with open(fichparam, "r") as file:
                        for ligne in file:
                            liste_value.append(ligne.replace("\n", "").split(";"))
                    liste_col = self.mdb.list_columns("parametres")
                    var = ",".join(liste_col)
                    valeurs = "("
                    for k in liste_col:
                        valeurs += "%s,"
                    valeurs = valeurs[:-1] + ")"

                    self.mdb.delete("parametres")

                    sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(
                        self.mdb.SCHEMA, "parametres", var, valeurs
                    )

                    self.mdb.run_query(sql, many=True, list_many=liste_value)
                except Exception:
                    valid = False
                    self.mgis.add_info("Error when parameters update")

        return valid
