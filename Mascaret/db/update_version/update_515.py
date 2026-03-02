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


class ClassUpdate515:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update515(self):
        """
        Action update version 5.1.5
        """
        # self.mgis.add_info("*** Update 5.1.5  ***")
        old_vers = self.cht.check_v_masc()
        if old_vers != "8.4":
            ok = self.cht.box.yes_no_q(
                "WARNING:\n "
                "Please note that this 5.1.5 update automatically \n"
                " updates the mascaret executable.\n"
                "Do you want to continue ?"
            )
            if not ok:
                return False

        lst_admin_tab = self.mdb.select("admin_tab", list_var=["table_"])
        if "results_old" in lst_admin_tab["table_"]:
            self.mdb.delete("admin_tab", where="table_= 'results_old'")

        # update csv parameter decentrement
        test = self.mdb.select("parametres", where="parametre ='decentrement'")
        if not len(test["id"]) > 0:
            fichparam = os.path.join(self.mgis.dossier_sql, "parametres.csv")

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
        # fix error
        try:
            qry = "DROP TRIGGER IF EXISTS all_up_abs_branchs ON {0}.branchs;".format(
                self.mdb.SCHEMA
            )
            self.mdb.run_query(qry)

            lst_fct = [
                "{0}.update_{1}(regclass, regclass)".format(self.mdb.SCHEMA, info)
                for info in ["abscisse_profil", "abscisse_point"]
            ]
            lst_fct.append("{0}.up_abs_branch()".format(self.mdb.SCHEMA))

            qry = ""
            for fct in lst_fct:
                qry += "DROP FUNCTION IF EXISTS {};\n".format(fct)
            self.mdb.run_query(qry)

            cl = Maso.class_fct_psql()
            lfct = [cl.pg_all_profil, cl.pg_all_point, cl.pg_up_abs_branch]

            qry = ""
            for sql in lfct:
                qry += sql(self.mdb.SCHEMA)
                qry += "\n"
            clb = Maso.branchs()
            clb.schema = self.mdb.SCHEMA
            qry += clb.pg_all_up_abs_branchs()
            self.mdb.run_query(qry)
        except Exception as e:
            self.mgis.add_info("Error update_fct_calc_abs: {}".format(str(e)))
            return False
        # update executable
        if old_vers != "8.4":
            self.mgis.download_bin()

        return True
