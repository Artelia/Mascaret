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

class ClassLinkFGParam(object):
    def __init__(self):
        """
        Initialize the ClassLinkFGParam object.
        - Defines the list of parameters (`lst_param`) for floodgate links.
        - Sets up default methods (`dmeth`) for mobility handling.
        """
        self.param_fg = {}
        self.list_actif = []
        self.lst_param = {
            # LINK CASIER
            "name": {"desc": "nom du link", "desc_en": "name of the link", 'typ': 'str'},
            "level0": {"desc": "cote de radier", "desc_en": "bottom elevation", 'typ': 'float'},
            "crosssection0"
            "abscissa": {"desc": "pk du link", "desc_en": "chainage of the link", 'typ': 'float'},
            "branchnum": {"desc": "branch", "desc_en": "branch", 'typ': 'int'},
            "basinstart": {"desc": "Casier Initial", "desc_en": "Initial basin", 'typ': 'int'},
            "basinend": {"desc": "Casier Final", "desc_en": "Final basin", 'typ': 'int'},
            "method_mob": {"desc": "mehtode utilisé : (0 ou NULL) ignore, meth_tempo(1), meth_regul(2), meth_fus(3)",
                           "desc_en": "method used: (0 or NULL) ignore, meth_tempo(1), meth_regul(2), meth_fus(3)",
                           "default": "2", 'typ': 'str'},
            "type": {"desc": "type de link, 1:weir, 4:culvert", "desc_en": "type of link, 1:weir, 4:culvert",
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
            "USEBASIN": {"desc": "Utilise le casier comme point de regulatinon",
                         "desc_en": "Uses the basin as a regulation point", 'typ': 'bool'},
            "NUMBASINREG": {"desc": "num basin", "desc_en": "basin number", "default": '', 'typ': 'int'},
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
            # meth_fusible
            "METHBREAK": {"desc": "méthode de rupture à un temps donnée time ou valeur régulation regul"
                                  " meth_time(1), meth_val(2)",
                          "desc_en": "break method at a given time or regulation value"
                            " meth_time(1), meth_val(2)", 'typ': 'str'},
            "TIMEFUS": {"desc": "Valeur Temps fusible en s", "desc_en": "Fuse time value in seconds", 'typ': 'float'},
            "WIDTHFUS": {"desc": "Largeur associé à TIME", "desc_en": "Width associated with TIME", 'typ': 'float'},
            "VFUS": {"desc": "Variable regulation Z ou Q seuil fusible",
                     "desc_en": "Regulation variable Z or Q fuse threshold", 'typ': 'str'},
            "VBREAKFUS": {"desc": "Valeur de rupture seuil", "desc_en": "Threshold break value", 'typ': 'float'},
            "TBREAKFUS": {"desc": "Temps de rupture seuil", "desc_en": "Threshold break time", 'typ': 'float'},
            "ZFINALFUS": {"desc": "Cote final weirs", "desc_en": "Final weir level", 'typ': 'float'},
            "USEBASINFUS": {"desc": "Utilise le casier comme point de regulatinon",
                            "desc_en": "Uses the basin as a regulation point", 'typ': 'bool'},
            "NUMBASINFUS": {"desc": "Start or end basin", "desc_en": "Start or end basin", 'typ': 'int'},
            "PKFUS": {"desc": "PK de la régulation", "desc_en": "Regulation chainage", 'typ': 'float'},
        }

        self.dmeth = {"meth_time": str(1),
                      "meth_regul": str(2),
                      "meth_fus": str(3)}
        self.dmeth_fus = {"meth_time": str(1),
                          "meth_val": str(2)}
        self.mess = ClassMessage()

    def get_param(self, parent=None, file="cli_fg_lk.obj"):
        """
        Retrieve parameters for mobile links.
        - If `parent` is provided, fetch parameters from the database.
        - Otherwise, import parameters from a file.

        :param parent: Parent class (optional).
        :param file: Name of the file to import parameters from (default: "cli_fg_lk.obj").
        """
        if not parent:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../mascaret"))
            path = os.path.join(path, file)
            complet = self.import_cl(path)
        else:
            complet = self.fill_param_to_db(parent.mdb)

        if complet:
            txt = "Import configuration links mobile"
            self.mess.add_mess('import_lk_fg', 'info''warning', txt)
        else:
            txt = "Error when the links mobile import"
            self.mess.add_mess('import_lk_fg', 'warning', txt)

        return self.check_param()

    def create_cli_fg(self, parent=None, file="cli_fg_lk.obj"):
        """
               Export parameters for mobile links.
               :param parent: Parent class (optional).
               :param file: Name of the file to import parameters from (default: "cli_fg_lk.obj").
        """
        if not parent:
            txt = "Error No parent"
            self.mess.add_mess('export_lk_fg', 'critic', txt)
            return False
        complet = self.fill_param_to_db(parent.mdb)
        if not complet :
            return False
        if not self.check_param():
            txt = self.mess.get_mess('chk_lk_fg')
            if txt != '':
                parent.box.info(txt, 'Error')
            return False
        self.export_cl(file)

    def fill_param_to_db(self, db):
        """
        Populate the `param_fg` dictionary with parameters from the database.
        - Fetches general link information from the `links` table.
        - Fetches mobility-specific values from the `links_mob_val` table.

        :param db: Database object.
        :return: True if parameters are successfully fetched, otherwise False.
        """
        lst_var = ["gid",
                   "name",
                   "level",
                   "crosssection",
                   "width",
                   "abscissa",
                   "method_mob",
                   "branchnum",
                   "type",
                   "basinstart",
                   "basinend"
                   ]
        sql = (
            "SELECT {1} "
            "FROM {0}.links "
            "WHERE active AND type in (4,1) AND nature=1 AND active_mob "
            "ORDER BY gid;"
        ).format(db.SCHEMA, ", ".join(lst_var))
        rows = db.run_query(sql, fetch=True)
        if rows is None:
            self.param_fg = {}
            txt = "erreur de recuperation base de donnee links"
            self.mess.add_mess('impt_lk_fg1', 'warning', txt)
            return False
        if len(rows) == 0:
            self.param_fg = {}
            return True
        conv_var = {'level':"level0",
                    "crosssection":"CSection0",
                    "width":"width0"}
        for row in rows:
            id_link = row[0]
            if id_link not in self.param_fg.keys():
                self.param_fg[id_link] = {}
                self.list_actif.append(id_link)
            for pos, var in enumerate(lst_var[1:]):
                if var in conv_var:
                    var= conv_var[var]
                self.param_fg[id_link][var] = row[pos + 1]

        lst_var = ["id_links", "name_var", "value"]
        sql = (
            "SELECT {1} " "FROM {0}.links_mob_val " "WHERE id_links in ({2}) " "ORDER BY id_links;"
        ).format(db.SCHEMA, ", ".join(lst_var), ", ".join([str(v) for v in self.list_actif]))
        rows = db.run_query(sql, fetch=True)
        if rows is None:
            self.param_fg = {}
            txt = "Error reading database links_mob_val"
            self.mess.add_mess('impt_lk_fg2', 'warning', txt)
            return False
        if len(rows) == 0:
            self.param_fg = {}

            txt = "links_mob_val not consistent with link"
            self.mess.add_mess('impt_lk_fg3', 'warning', txt)
            return False
        var_tab = [
            "TIMEZ",
            "VALUEZ",
            "TIMEFUS",
            "WIDTHFUS"]
        lst_id_tab = []
        for row in rows:
            id_link = row[0]
            var = row[1]
            if var in var_tab:
                lst_id_tab.append(id_link)
                self.param_fg[id_link].update({var: []})
                continue
            if var in self.lst_param:
                self.param_fg[id_link][var] = self.typ_to_val(self.lst_param[var]['typ'], row[2])
            else:
                self.param_fg[id_link][var] = row[2]

        lst_id_tab = list(set(lst_id_tab))
        if len(lst_id_tab) > 0 :
            lst_var = ["id_links", "name_var", "value", "id_order"]
            sql = (
                "SELECT {1} " "FROM {0}.links_mob_val " "WHERE id_links in ({2}) AND name_var in ({3})"
                "ORDER BY id_links,id_order;"
            ).format(db.SCHEMA, ", ".join(lst_var), ", ".join([str(v) for v in lst_id_tab]),
                                                              ", ".join([f"'{v}'" for v in var_tab]))
            # print(sql)
            rows = db.run_query(sql, fetch=True)
            if not (rows is None or len(rows) == 0):
                for row in rows:
                    id_link = row[0]
                    var = row[1]
                    if var in var_tab:
                        self.param_fg[id_link][var].append(self.typ_to_val('float',row[2]))

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
        - Ensures that each link has the necessary parameters based on its mobility method.
        :param num: Link number.
        :param test: Dictionary containing the parameters to be tested.
        :return: True if all variables are present, otherwise False.
        """
        lst_test = dlist[test["method_mob"]]
        missing_vars = [var for var in lst_test if var not in test]
        if missing_vars:
            txt = f"The variable <{', '.join(missing_vars)}> wasn't found for link {num}.\n"
            for  var in missing_vars:
                try:
                    txt += f"  - {var} : {self.lst_param[var]['desc_en']}\n"
                except KeyError:
                    txt += f"  - {var} : \n"
            self.mess.add_mess('chk_lk_fg', 'critic', txt)
            return False
        return True

    def check_regul(self, num, test):
        """
            Check the regulation parameters.
            :param num: Link number.
            :param test: Dictionary containing the parameters to be tested.
            :return: True if the regulation parameters are valid, False otherwise.
        """
        if test["method_mob"] == 2:
            tol = test["TOLREG"]
            if test["DIRFG"] =='D' and test["VREGOPEN"] - tol <= test["VREGCLOS"] + tol:
                    txt = (f"The opening level minus tolerance is lower than the closing level plus tolerance. "
                           f"It should always be higher in this case.\n "
                           f"The issue is for link {num}.")
                    self.mess.add_mess('chk_lk_reg', 'critic', txt)
                    return False
            elif test["DIRFG"] == 'U' and test["VREGOPEN"] + tol >= test["VREGCLOS"] - tol:
                    txt = (f"The opening level plus tolerance is greater than the closing level minus tolerance. "
                           f"It should always be lower in this case.\n "
                           f"The issue is for link {num}.")
                    self.mess.add_mess('chk_lk_reg', 'critic', txt)
                    return False
        return True


    def check_param(self):
        """
            Verify that all is OK to run the model.
            :return: True if all is OK, otherwise False.
        """
        dlist = self.create_lst_test()
        for num, test in self.param_fg.items():
            # code-err= 'chk_lk_fg'
            if not self.check_lst_param(num,test,dlist):
                return False
            # code-err= 'chk_lk_reg'
            if  not self.check_regul(num,test):
                return False

    def create_lst_test(self):
        """
        Create a dictionnary of required variables for a given mobility method.
        :param meth: Mobility method (e.g., "meth_time", "meth_regul", "meth_fus").
        :return: Dictionnary of list of required variables.
        """
        lst_com = ["name", "level0","CSection0","width0", "abscissa", "branchnum",
                   "basinstart", "basinend", "method_mob"]
        lst_reg = ["DIRFG", "VELOFGOPEN", "VELOFGCLOSE", "ZMAXFG", "ZINITREG", "VREG", "USEBASIN", "NUMBASINREG",
                    "PK", "VREGCLOS", "VREGOPEN", "CRITDTREG", "NDTREG", "DTREG", "ZINCRFG", "TOLREG",
                   "VBREAKREG", "BPERMREG", "ZFINALREG"]
        lst_time = ["TIMEZ", "VALUEZ", "VBREAKT", "BPERMT", "ZFINALT", ]
        lst_fus = ["METHBREAK", "TIMEFUS", "WIDTHFUS", "VFUS", "VBREAKFUS", "TBREAKFUS", "ZFINALFUS", "USEBASINFUS",
                   "NUMBASINFUS", "PKFUS"]

        dlist = { self.dmeth["meth_time"]: lst_com + lst_time,
                  self.dmeth["meth_regul"] :  lst_com + lst_reg,
                  self.dmeth["meth_fus"] : lst_com + lst_fus
                     }
        return dlist

    def export_cl(self, name="cli_fg_lk.obj"):
        """
        Export the `param_fg` dictionary to a JSON file.
        :param name: Name of the output file (default: "cli_fg_lk.obj").
        """
        with open(name, "w") as file:
            json.dump(self.param_fg, file)
        # if debug, indent=4)

    def import_cl(self, name="cli_fg_lk.obj"):
        """
        Import parameters from a JSON file into the `param_fg` dictionary.
        :param name: Name of the input file (default: "cli_fg_lk.obj").
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

    def fg_actif_lk(self, db=None):
        """
        Check if there are any active mobile links.
        :return: True if there are active links, otherwise False.
        """
        if db:
            sql = f"SELECT EXISTS (SELECT 1 FROM {db.SCHEMA}.links WHERE active_mob = TRUE and active= TRUE );"
            row = db.run_query(sql, fetch=True)
            if row:
                return True
            return False
        else:
            if len(self.param_fg.keys()) > 0:
                return True
            return False
