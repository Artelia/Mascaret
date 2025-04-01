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
            "name": {"desc": "nom du link", 'typ': 'str'},
            "level": {"desc": "cote de radier", 'typ': 'float'},
            "abscissa": {"desc": "pk du link", 'typ': 'float'},
            "branchnum": {"desc": "branch", 'typ': 'int'},
            "basinstart": {"desc": "Casier Initial", 'typ': 'int'},
            "basinend": {"desc": "Casier Final", 'typ': 'int'},
            "method_mob": {"desc": "mehtode utilisé : (0 ou NULL) ignore, meth_tempo(1), meth_regul(2), meth_fus(3)",
                           "default": "2", 'typ': 'str'},
            "type": {"desc": "type de link, 1:weir, 4:culvert",'typ': 'int'},
            # methode de régulation
            "DIRFG": {"desc": "direction si D cote monte et section diminue si U seul section diminue", 'typ': 'str'},
            "VELOFGOPEN": {"desc": "vitesse d'ouverture m/s de la vanne", 'typ': 'float'},
            "VELOFGCLOSE": {"desc": "vitesse de fermeture m/s de la vanne", 'typ': 'float'},
            "ZMAXFG": {"desc": "valeur Z limite max d'ouverture ", 'typ': 'float'},
            "ZINITREG": {"desc": "cote initial de la vanne (compris entre ZMAXFG et cote de radier)", 'typ': 'float'},
            "VREG": {"desc": "Variable regulation Z ou Q", 'typ': 'str'},
            "USEBASIN": {"desc": "Utilise le casier comme point de regulatinon", 'typ': 'bool'},
            "NUMBASINREG": {"desc": "num basin", "default": '', 'typ': 'int'},
            "USEPOINT": {"desc": "Utilise point comme point de regulatinon", 'typ': 'bool'},
            "PK": {"desc": "PK de la régulation", 'typ': 'float'},
            "VREGCLOS": {"desc": "valeur fermeture de la vanne", 'typ': 'float'},
            "VREGOPEN": {"desc": "valeur d'ouverture de la vanne", 'typ': 'float'},
            "CRITDTREG": {"desc": "critère NDTREG ou DTREG", 'typ': 'str'},
            "NDTREG": {"desc": "Tout les N pas temps pour l'application", 'typ': 'int'},
            "DTREG": {"desc": "Si =0 pas de temps  du calcul, sinn celui indiqué (en s)", 'typ': 'float'},
            "ZINCRFG": {"desc": "max d'incrementation", 'typ': 'float'},
            "TOLREG": {"desc": "Tolerance sur les variale de regulation", 'typ': 'float'},
            "VBREAKREG": {"desc": "Valeur de rupture ouvrage", 'typ': 'float'},
            "BPERMREG": {"desc": "Si rupture permanent", 'typ': 'bool'},
            "ZFINALREG": {"desc": "Cote final weirs après rupture", 'typ': 'float'},
            # meth_tempo
            "TIMEZ": {"desc": "Valeur Temps en s", 'typ': 'float'},
            "VALUEZ": {"desc": "Valeur associé à TIME", 'typ': 'float'},
            "VBREAKT": {"desc": "Valeur de rupture ouvrage", 'typ': 'float'},
            "BPERMT": {"desc": "Si rupture permanent", 'typ': 'bool'},
            "ZFINALT": {"desc": "Cote final weirs après rupture", 'typ': 'float'},
            # meth_fusible :TIME, VALUEVAR,
            "METHBREAK": {"desc": "méthode de rupture à un temps donnée time ou valeur régulation regul",
                          'typ': 'float'},
            "TIMEFUS": {"desc": "Valeur Temps fusible en s", 'typ': 'float'},
            "WIDTHFUS": {"desc": "Largeur associé à TIME", 'typ': 'float'},
            "VFUS": {"desc": "Variable regulation Z ou Q seuil fusible", 'typ': 'str'},
            "VBREAKFUS": {"desc": "Valeur de ruputre seuil", 'typ': 'float'},
            "TBREAKFUS": {"desc": "Temps de ruputre seuil", 'typ': 'float'},
            "ZFINALFUS": {"desc": "Cote final weirs", 'typ': 'float'},
            "USEBASINFUS": {"desc": "Utilise le casier comme point de regulatinon", 'typ': 'bool'},
            "NUMBASINFUS": {"desc": "Start or end basin", 'typ': 'int'},
            "USEPOINTFUS": {"desc": "Utilise point comme point de regulatinon", 'typ': 'bool'},
            "PKFUS": {"desc": "PK de la régulation", 'typ': 'float'},

        }

        self.dmeth = {"meth_time": str(1),
                      "meth_regul": str(2),
                      "meth_fus": str(3)}

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
            if complet:
                print("Import configuration links mobile")
            else:
                print("Erreur lors de l'import links mobile")
        else:
            complet = self.fill_param_to_db(parent.mdb)
            if complet:
                parent.add_info("Import configuration links mobile")
            else:
                parent.add_info("Erreur lors de l'import links mobile")

        self.check_lst_param()


    def fill_param_to_db(self, db):
        """
        Populate the `param_fg` dictionary with parameters from the database.
        - Fetches general link information from the `links` table.
        - Fetches mobility-specific values from the `links_mob_val` table.

        :param db: Database object.
        :return: True if parameters are successfully fetched, otherwise False.
        """
        lst_var = ["linknum",
                   "name",
                   "level",
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
            "ORDER BY linknum;"
        ).format(db.SCHEMA, ", ".join(lst_var))
        rows = db.run_query(sql, fetch=True)
        if rows is None:
            self.param_fg = {}
            print("erreur de recuperation base de donnee links")
            return False
        if len(rows) == 0:
            self.param_fg = {}
            return True

        for row in rows:
            id_link = row[0]
            if id_link not in self.param_fg.keys():
                self.param_fg[id_link] = {}
                self.list_actif.append(id_link)
            for pos, var in enumerate(lst_var[1:]):
                self.param_fg[id_link][var] = row[pos + 1]

        lst_var = ["id_links", "name_var", "value"]
        sql = (
            "SELECT {1} " "FROM {0}.links_mob_val " "WHERE id_links in ({2}) " "ORDER BY id_links;"
        ).format(db.SCHEMA, ", ".join(lst_var), ", ".join([str(v) for v in self.list_actif]))
        rows = db.run_query(sql, fetch=True)
        if rows is None:
            self.param_fg = {}
            print("erreur de recuperation base de donnee links_mob_val")
            return False
        if len(rows) == 0:
            self.param_fg = {}
            print("links_mob_val  non coherant avec link")
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
            dico_tmp = {id :{v:[] for v in var_tab} for id in lst_id_tab}
            self.param_fg[id_link].update({v:[] for v in var_tab})
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

    def check_lst_param(self):
        """
        Verify that all required variables are present in the `param_fg` dictionary.
        - Ensures that each link has the necessary parameters based on its mobility method.
        :return: True if all variables are present, otherwise False.
        """
        for num, test in self.param_fg.items():
            lst_test = self.create_lst_test(test["method_mob"])
            for var in lst_test:
                if var not in test:
                    print(f"The variable <{var}> wasn't found for link {num}.")
                    return False
        return True

    def create_lst_test(self, meth):
        """
        Create a list of required variables for a given mobility method.
        :param meth: Mobility method (e.g., "meth_time", "meth_regul", "meth_fus").
        :return: List of required variables.
        """
        lst_com = ["name", "level", "abscissa", "branchnum", "basinstart", "basinend", "method_mob"]
        lst_reg = ["DIRFG", "VELOFGOPEN", "VELOFGCLOSE", "ZMAXFG", "ZINITREG", "VREG", "USEBASIN", "NUMBASINREG",
                   "USEPOINT", "PK", "VREGCLOS", "VREGOPEN", "CRITDTREG", "NDTREG", "DTREG", "ZINCRFG", "TOLREG",
                   "VBREAKREG", "BPERMREG", "ZFINALREG"]
        lst_time = ["TIMEZ", "VALUEZ", "VBREAKT", "BPERMT", "ZFINALT", ]
        lst_fus = ["METHBREAK", "TIMEFUS", "WIDTHFUS", "VFUS", "VBREAKFUS", "TBREAKFUS", "ZFINALFUS", "USEBASINFUS",
                   "NUMBASINFUS", "USEPOINTFUS", "PKFUS"]

        lst_test = []
        if meth == self.dmeth["meth_time"]:
            lst_test = lst_com + lst_time
        elif meth == self.dmeth["meth_regul"]:
            lst_test = lst_com + lst_reg
        elif meth == self.dmeth["meth_fus"]:
            lst_test = lst_com + lst_fus
        return lst_test

    def export_cl(self, name="cli_fg_lk.obj"):
        """
        Export the `param_fg` dictionary to a JSON file.
        :param name: Name of the output file (default: "cli_fg_lk.obj").
        """
        with open(name, "w") as file:
            json.dump(self.param_fg, file)

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

    def fg_actif_lk(self):
        """
        Check if there are any active mobile links.
        :return: True if there are active links, otherwise False.
        """
        if len(self.param_fg.keys()) > 0:
            return True
        return False
