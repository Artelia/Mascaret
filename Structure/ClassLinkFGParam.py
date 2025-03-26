# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2017
copyright            : (C) 2017 by Artelia
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
        Get param of mobil link
        :param parent: parent class
        :param file: name file
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
            # print(self.param_fg)
            if complet:
                parent.add_info("Import configuration links mobile")
            else:
                parent.add_info("Erreur lors de l'import links mobile")

        self.check_lst_param()


    def fill_param_to_db(self, db):
        """
        Read parameters in database
        TODO attention au méthode peut provoquer des modifications

        :param db: database object
        :return:
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

        for row in rows:
            id_link = row[0]
            var = row[1]
            if var in self.lst_param:
                self.param_fg[id_link][var] = self.typ_to_val(self.lst_param[var]['typ'], row[2])
            else:
                self.param_fg[id_link][var] = row[2]
            # try:
            #     self.param_fg[id_link][var] = float(row[2])
            # except ValueError:
            #     self.param_fg[id_link][var] = row[2]

        return True

    def typ_to_val(self, typ, val):
        """

        :param typ: type of the value
        :param val: Value
        :return:  return the value with the good type
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
        Check if all variables
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
        Creation of test list allowing to check the variables
        :param meth:
        :return:
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
        To Generate json file parameters
        :param obj: object to dump
        :param name: name file
        :return:
        """
        with open(name, "w") as file:
            json.dump(self.param_fg, file)

    def import_cl(self, name="cli_fg_lk.obj"):
        """
        Load parameter
        :param name: Name file
        :return:
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
        Check if there is mobil links
        """
        if len(self.param_fg.keys()) > 0:
            return True
        return False
