# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2025
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
# import pickle
import json
import os
from ..Function import str2bool,data_to_float,data_to_int
from ..ClassMessage import ClassMessage

class ClassMobilWeirsParam(object):
    def __init__(self):
        """
        Initialize the ClassMobilWeirsParam object.
        - Defines the list of parameters (`lst_param`) for mobile weirs weirs.
        - Sets up default methods (`dmeth`) for mobility handling.
        """
        self.param_fg = {}
        self.list_actif = []
        self.lst_param = {
            # weirs CASIER
            "name": {"desc": "nom du weirs", "desc_en": "name of the weirs", 'typ': 'str'},
            "level": {"desc": "cote de radier (z_crest)", "desc_en": "bottom elevation (z_crest)", 'typ': 'float'},
            "abscissa": {"desc": "pk du weirs", "desc_en": "chainage of the weirs", 'typ': 'float'},
            "branchnum": {"desc": "branch", "desc_en": "branch", 'typ': 'int'},
            "method_mob": {"desc": "mehtode utilisé : (0 ou NULL) ignore, meth_tempo(1), meth_regul(2)",
                           "desc_en": "method used: (0 or NULL) ignore, meth_tempo(1), meth_regul(2), ",
                           "default": "2", 'typ': 'str'},
            # loi impacter par la modification de Singularite(ising)%CoteCrete
            # SINGULARITE_TYPE_ZAMONT_ZAVAL_Q = 1
            # SINGULARITE_TYPE_ZAMONT_Q       = 2
            # SINGULARITE_TYPE_PROFIL_CRETE   = 3
            # SINGULARITE_TYPE_CRETE_COEFF    = 4
            "type": {"desc": "type de weirs, 1:Zamont Zaval Q,2: Zam=f(Q) 3:Crest profile 4:Weir law",
                     "desc_en": "type of weirs, 1:Zamont Zaval Q,2: Zam=f(Q) 3:Crest profile 4:Weir law",
                     'typ': 'int'},
            # methode de régulation
            "DIRFG": {"desc": "direction si D cote monte et section diminue si U seul section diminue",
                      "desc_en": "direction: if D, level rises and section decreases; if U, only section decreases",
                      'typ': 'str'},
            "VELOFGOPEN": {"desc": "vitesse d'ouverture m/s de la vanne", "desc_en": "opening speed of the gate (m/s)",
                           'typ': 'float'},
            "VELOFGCLOSE": {"desc": "vitesse de fermeture m/s de la vanne",
                            "desc_en": "closing speed of the gate (m/s)", 'typ': 'float'},
            "ZMAXFG": {"desc": "valeur Z limite max d'ouverture", "desc_en": "maximum Z limit for opening",
                       'typ': 'float'},
            "ZINITREG": {"desc": "cote initial de la vanne (compris entre ZMAXFG et cote de radier)",
                         "desc_en": "initial gate level (between ZMAXFG and bottom level)", 'typ': 'float'},
            "VREG": {"desc": "Variable regulation Z ou Q", "desc_en": "Regulation variable Z or Q", 'typ': 'str'},
            "PK": {"desc": "PK de la régulation", "desc_en": "Regulation chainage", 'typ': 'float'},
            "VREGCLOS": {"desc": "valeur fermeture de la vanne", "desc_en": "gate closing value", 'typ': 'float'},
            "VREGOPEN": {"desc": "valeur d'ouverture de la vanne", "desc_en": "gate opening value", 'typ': 'float'},
            "CRITDTREG": {"desc": "critère NDTREG ou DTREG", "desc_en": "criterion NDTREG or DTREG", 'typ': 'str'},
            "NDTREG": {"desc": "Tout les N pas temps pour l'application",
                       "desc_en": "Every N time steps for application", 'typ': 'int'},
            "DTREG": {"desc": "Si =0 pas de temps  du calcul, sinn celui indiqué (en s)",
                      "desc_en": "If 0, default time step; otherwise, specified value (s)", 'typ': 'float'},
            "ZINCRFG": {"desc": "max d'incrementation", "desc_en": "maximum increment", 'typ': 'float'},
            "TOLREG": {"desc": "Tolerance sur les variale de regulation",
                       "desc_en": "Tolerance on regulation variables", 'typ': 'float'},
            "VBREAKREG": {"desc": "Valeur de rupture ouvrage", "desc_en": "Break value of structure", 'typ': 'float'},
            "BPERMREG": {"desc": "True Si la rupture est non permanent", "desc_en": "True If break isn't permanent",
                         'typ': 'bool'},
            "ZFINALREG": {"desc": "Cote final weirs après rupture", "desc_en": "Final weir level after break",
                          'typ': 'float'},
            # meth_tempo
            "TIMEZ": {"desc": "Valeur Temps en s", "desc_en": "Time value in seconds", 'typ': 'float'},
            "VALUEZ": {"desc": "Valeur associé à TIME", "desc_en": "Value associated with TIME", 'typ': 'float'},
            "VBREAKT": {"desc": "Valeur de rupture ouvrage", "desc_en": "Break value of structure", 'typ': 'float'},
            "BPERMT": {"desc": "True Si la rupture est non permanent", "desc_en": "True If break isn't permanent",
                       'typ': 'bool'},
            "ZFINALT": {"desc": "Cote final weirs après rupture", "desc_en": "Final weir level after break",
                        'typ': 'float'},
        }

        self.dmeth = {"meth_time": str(1),
                      "meth_regul": str(2),
                      }
        self.mess = ClassMessage()

    def get_param(self, parent=None, file="cli_fg_weirs.obj"):
        """
        Retrieve parameters for mobile weirs.
        - If `parent` is provided, fetch parameters from the database.
        - Otherwise, import parameters from a file.

        :param parent: Parent class (optional).
        :param file: Name of the file to import parameters from (default: "cli_fg_weirs.obj").
        """
        if not parent:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mascaret"))
            path = os.path.join(path, file)
            complet = self.import_cl(path)
        else:
            complet = self.fill_param_to_db(parent.mdb)

        if complet:
            txt = "Import configuration weirs mobile"
            self.mess.add_mess('import_weirs_fg', 'info''warning', txt)
        else:
            txt = "Error when the weirs mobile import"
            self.mess.add_mess('import_weirs_fg', 'warning', txt)

        return self.check_param()

    def create_cli_fg(self, parent=None, file="cli_fg_weirs.obj"):
        """
               Export parameters for mobile weirs.
               :param parent: Parent class (optional).
               :param file: Name of the file to import parameters from (default: "cli_weirs_weirs.obj").
        """
        if not parent:
            txt = "Error No parent"
            self.mess.add_mess('export_weirs_fg', 'critic', txt)
            return False
        complet = self.fill_param_to_db(parent.mdb)
        if not complet :
            return False
        if not self.check_param():
            txt = self.mess.get_mess('chk_weirs_fg')
            if txt != '':
                parent.box.info(txt, 'Error')
            return False
        self.export_cl(file)

    def fill_param_to_db(self, db):
        """
        Populate the `param_fg` dictionary with parameters from the database.
        - Fetches general weirs information from the `weirs` table.
        - Fetches mobility-specific values from the `weirs_mob_val` table.

        :param db: Database object.
        :return: True if parameters are successfully fetched, otherwise False.
        """
        lst_var = ["gid",
                   "name",
                   "z_crest",
                   "abscissa",
                   "method_mob",
                   "branchnum",
                   "type",
                   ]
        sql = (
            "SELECT {1} "
            "FROM {0}.weirs "
            "WHERE active AND type in (1,2,3,4)  AND active_mob "
            "ORDER BY gid;"
        ).format(db.SCHEMA, ", ".join(lst_var))
        rows = db.run_query(sql, fetch=True)
        if rows is None:
            self.param_fg = {}
            txt = "erreur de recuperation base de donnee weirs"
            self.mess.add_mess('impt_weirs_fg1', 'warning', txt)
            return False
        if len(rows) == 0:
            self.param_fg = {}
            return True

        for row in rows:
            id_weirs = row[0]
            if id_weirs not in self.param_fg.keys():
                self.param_fg[id_weirs] = {}
                self.list_actif.append(id_weirs)
            for pos, var in enumerate(lst_var[1:]):
                if var  == 'z_crest':
                    var = 'level'
                self.param_fg[id_weirs][var] = row[pos + 1]

        lst_var = ["id_weirs", "name_var", "value"]
        sql = (
            "SELECT {1} " "FROM {0}.weirs_mob_val " "WHERE id_weirs in ({2}) " "ORDER BY id_weirs;"
        ).format(db.SCHEMA, ", ".join(lst_var), ", ".join([str(v) for v in self.list_actif]))
        rows = db.run_query(sql, fetch=True)
        if rows is None:
            self.param_fg = {}
            txt = "Error reading database weirs_mob_val"
            self.mess.add_mess('impt_weirs_fg2', 'warning', txt)
            return False
        if len(rows) == 0:
            self.param_fg = {}

            txt = "weirs_mob_val not consistent with weirs"
            self.mess.add_mess('impt_weirs_fg3', 'warning', txt)
            return False
        var_tab = [
            "TIMEZ",
            "VALUEZ"]
        lst_id_tab = []
        for row in rows:
            id_weirs = row[0]
            var = row[1]
            if var == 'z_crest':
                var = 'level'
            if var in var_tab:
                lst_id_tab.append(id_weirs)
                self.param_fg[id_weirs].update({var: []})
                continue
            if var in self.lst_param:
                self.param_fg[id_weirs][var] = self.typ_to_val(self.lst_param[var]['typ'], row[2])
            else:
                self.param_fg[id_weirs][var] = row[2]

        lst_id_tab = list(set(lst_id_tab))
        if len(lst_id_tab) > 0 :
            lst_var = ["id_weirs", "name_var", "value", "id_order"]
            sql = (
                "SELECT {1} " "FROM {0}.weirs_mob_val " "WHERE id_weirs in ({2}) AND name_var in ({3})"
                "ORDER BY id_weirs,id_order;"
            ).format(db.SCHEMA, ", ".join(lst_var), ", ".join([str(v) for v in lst_id_tab]),
                                                              ", ".join([f"'{v}'" for v in var_tab]))
            # print(sql)
            rows = db.run_query(sql, fetch=True)
            if not (rows is None or len(rows) == 0):
                for row in rows:
                    id_weirs = row[0]
                    var = row[1]
                    if var in var_tab:
                        self.param_fg[id_weirs][var].append(self.typ_to_val('float',row[2]))

        return True

    @staticmethod
    def typ_to_val(typ, val):
        """
        Convert a value to its specified type.
        :param typ: The target type (e.g., 'bool', 'int', 'float').
        :param val: The value to be converted.
        :return: The converted value.
        """
        if typ =='bool':
            return  str2bool(val)
        elif typ =='int':
            return  data_to_int(val)
        elif typ == 'float':
            return data_to_float(val)
        else:
            return val

    def check_lst_param(self, num,test,dlist):
        """
        Verify that all required variables are present in the `param_fg` dictionary.
        - Ensures that each weirs has the necessary parameters based on its mobility method.
        :param num: weirs number.
        :param test: Dictionary containing the parameters to be tested.
        :return: True if all variables are present, otherwise False.
        """
        lst_test = dlist[test["method_mob"]]
        missing_vars = [var for var in lst_test if var not in test]
        if missing_vars:
            txt = f"The variable <{', '.join(missing_vars)}> wasn't found for weirs {num}.\n"
            for  var in missing_vars:
                try:
                    txt += f"  - {var} : {self.lst_param[var]['desc_en']}\n"
                except KeyError:
                    txt += f"  - {var} : \n"
            self.mess.add_mess('chk_weirs_fg', 'critic', txt)
            return False
        return True

    def check_regul(self, num, test):
        """
            Check the regulation parameters.
            :param num: weirs number.
            :param test: Dictionary containing the parameters to be tested.
            :return: True if the regulation parameters are valid, False otherwise.
        """
        if test["method_mob"] == 2:
            tol = test["TOLREG"]
            if test["VREGOPEN"] - tol < test["VREGCLOS"] + tol:
                    txt = (f"The opening level minus tolerance is lower than the closing level plus tolerance. "
                           f"It should always be higher in this case.\n "
                           f"The issue is for weirs {num}.")
                    self.mess.add_mess('chk_weirs_reg', 'critic', txt)
                    return False
        return True


    def check_param(self):
        """
            Verify that all is OK to run the model.
            :return: True if all is OK, otherwise False.
        """
        dlist = self.create_lst_test()
        for num, test in self.param_fg.items():
            # code-err= 'chk_weirs_fg'
            if not self.check_lst_param(num,test,dlist):
                return False
            # code-err= 'chk_weirs_reg'
            if  not self.check_regul(num,test):
                return False

    def create_lst_test(self):
        """
        Create a dictionnary of required variables for a given mobility method.
        :param meth: Mobility method (e.g., "meth_time", "meth_regul", "meth_fus").
        :return: Dictionnary of list of required variables.
        """
        lst_com = ["name", "level", "abscissa", "branchnum",  "method_mob"]
        lst_reg = ["DIRFG", "VELOFGOPEN", "VELOFGCLOSE", "ZMAXFG", "ZINITREG", "VREG",
                    "PK", "VREGCLOS", "VREGOPEN", "CRITDTREG", "NDTREG", "DTREG", "ZINCRFG", "TOLREG",
                   "VBREAKREG", "BPERMREG", "ZFINALREG"]
        lst_time = ["TIMEZ", "VALUEZ", "VBREAKT", "BPERMT", "ZFINALT", ]

        dlist = { self.dmeth["meth_time"]: lst_com + lst_time,
                  self.dmeth["meth_regul"] :  lst_com + lst_reg,
                  }
        return dlist

    def export_cl(self, name="cli_fg_weirs.obj"):
        """
        Export the `param_fg` dictionary to a JSON file.
        :param name: Name of the output file (default: "cli_fg_weirs.obj").
        """
        with open(name, "w") as file:
            json.dump(self.param_fg, file)
        # if debug, indent=4)

    def import_cl(self, name="cli_fg_weirs.obj"):
        """
        Import parameters from a JSON file into the `param_fg` dictionary.
        :param name: Name of the input file (default: "cli_fg_weirs.obj").
        :return: True if the file is successfully loaded, otherwise False.
        """
        if os.path.isfile(name):
            with open(name, "r") as file:
                obj = json.load(file)

            for key, val in obj.items():
                setattr(self.param_fg, key, val)

            return True
        else:
            self.param_fg = {}
            return False

    def fg_actif_weirs(self, db=None):
        """
        Check if there are any active mobile weirs.
        :return: True if there are active weirs, otherwise False.
        """
        if db:
            sql = f"SELECT EXISTS (SELECT 1 FROM {db.SCHEMA}.weirs WHERE active_mob = TRUE and active= TRUE );"
            row = db.run_query(sql, fetch=True)
            if row:
                return True
            return False
        else:
            if len(self.param_fg.keys()) > 0:
                return True
            return False
