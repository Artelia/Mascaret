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
import os

from lib.db import MasObject as Maso


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

            self.mdb.delete("parametres")
            self.mdb.insert_res("parametres", liste_value, liste_col)
        # fix error
        try:
            qry = "DROP TRIGGER IF EXISTS all_up_abs_branchs ON {schema}.branchs;"
            self.mdb.run_query(qry, schema=True)

            lst_fct = [
                "{{schema}}.update_{0}(regclass, regclass)".format(info)
                for info in ["abscisse_profil", "abscisse_point"]
            ]
            lst_fct.append("{schema}.up_abs_branch()")

            qry = ""
            for fct in lst_fct:
                qry += "DROP FUNCTION IF EXISTS {};\n".format(fct)
            self.mdb.run_query(qry, schema=True)

            cl = Maso.class_fct_psql()
            lfct = [cl.pg_all_profil, cl.pg_all_point, cl.pg_up_abs_branch]

            qry = ""
            for mk_sql_fn in lfct:
                qry += mk_sql_fn(local="{schema}")
                qry += "\n"
            clb = Maso.branchs()
            clb.schema = "{schema}"
            qry += clb.pg_all_up_abs_branchs()
            self.mdb.run_query(qry, schema=True)
        except Exception as e:
            self.mgis.add_info("Error update_fct_calc_abs: {}".format(str(e)))
            return False
        # update executable
        if old_vers != "8.4":
            self.mgis.download_bin()

        return True
