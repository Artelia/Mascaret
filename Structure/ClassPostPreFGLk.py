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


class ClassInfoParamFG_Lk(object):
    def __init__(self):
        self.param_fg = {}
        self.list_actif = []
        self.lst_param = {
            "name": {"desc": "nom du link"},
            "level": {"desc": "cote de radier"},
            "abscissa": {"desc": "pk du link"},
            "branchnum": {"desc": "branch"},
            "basinstart" : {"desc": "Casier Initial"},
            "basinend" :{"desc": "Casier Final"},
            "method_mob": {"desc": "mehtode utilisé : meth_tempo, meth_regul, ",
                           "default": "meth_regul"},
            "type": {"desc": "type de link, 1:weir, 4:culvert"},
            # methode de régulation
            "DIRFG": {"desc": "direction si D cote monte et section diminue si U seul section diminue",
                      "default": "D"},
            "VELOFGOPEN": {"desc": "vitesse d'ouverture m/s de la vanne",
                           "default":99.0},
            "VELOFGCLOSE": {"desc": "vitesse de fermeture m/s de la vanne",
                           "default": "VELOFGOPEN"},
            "ZMAXFG": {"desc": "valeur Z limite max d'ouverture ",
                       "default": ""},
            "ZINITREG": {"desc": "cote initial de la vanne (compris entre ZMAXFG et cote de radier)",
                         "default":"level"},
            "VREG": {"desc": "Variable regulation Z ou Q",
                     "default": "Z"},
            "USEBASIN" :{"desc": "Utilise le casier comme point de regulatinon",
                     "default": False},
            "NUMBASINREG": {"desc": "Start or end basin",
                         "default": ''},
            "USEPOINT": {"desc": "Utilise point comme point de regulatinon",
                         "default": False},
            "PK": {"desc": "PK de la régulation",
                   "default": "abscissa"},
            "VREGCLOS": {"desc": "valeur fermeture de la vanne",
                         "default": "level"},
            "VREGOPEN": {"desc": "valeur d'ouverture de la vanne",
                         "default": "VREGOPEN"},
            "CRITDTREG": {"desc": "critère NDTREG ou DTREG",
                          "default": "NDTREG"},
            "NDTREG": {"desc": "Tout les N pas temps pour l'application",
                       "default": 1},
            "DTREG": {"desc": "Si =0 pas de temps  du calcul, sinn celui indiqué (en s)",
                      "default": 0},
            "ZINCRFG": {"desc": "max d'incrementation",
                        "default":99999},
            "TOLREG": {"desc": "Tolerance sur les variale de regulation",
                       "default":0.05},
            # meth_tempo
            "TIMEZ": {"desc": "Valeur Temps en s",
                       "default":0},
            "VALUEZ":{"desc": "Valeur associé à TIME",
                       "default":0},
            # meth_fusible :TIME, VALUEVAR,
            "METHBREAK": {"desc": "méthode de rupture à un temps donnée ou valeur régulation",
                      "default": "time"},
            "TIMEFUS": {"desc": "Valeur Temps fusible en s",
                     "default": 0},
            "WIDTHFUS": {"desc": "Largeur associé à TIME",
                       "default": 0},
            "VFUS": {"desc": "Variable regulation Z ou Q seuil fusible",
                     "default": "Z"},
            "VBREAKFUS": {"desc": "Valeur de ruputre seuil",
                     "default": "0"},
            "TBREAKFUS": {"desc": "Temps de ruputre seuil",
                          "default": "0"},
            "ZFINALFUS": {"desc": "Cote final weirs",
                          "default": "0"},
            "USEBASINFUS": {"desc": "Utilise le casier comme point de regulatinon",
                         "default": False},
            "NUMBASINFUS": {"desc": "Start or end basin",
                            "default": ''},
            "USEPOINTFUS": {"desc": "Utilise point comme point de regulatinon",
                         "default": False},
            "PKFUS": {"desc": "PK de la régulation",
                   "default": "abscissa"},

            }

        self.param_meth_reg = [
            "DIRFG",
            "VELOFGOPEN",
            "VELOFGCLOSE",
            "ZMAXFG",
            "ZINITREG",
            "VREG",
            "USEBASIN",
            "NUMBASINREG",
            "USEPOINT",
            "PK",
            "CRITDTREG",
            "NDTREG",
            "DTREG",
            "ZINCRFG",
            "TOLREG"
            ]


    def get_param(self, parent=None, file="cli_fg_lk.obj"):
        """
        Get param of mobil link
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

    def fill_param_to_db(self, db):
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
            try:
                self.param_fg[id_link][var] = float(row[2])
            except ValueError:
                self.param_fg[id_link][var] = row[2]

        if not self.check_param():
            self.param_fg = {}
            return False
        return True

    def check_param(self):
        for num, test in self.param_fg.items():
            for var in self.lst_param.keys():
                if var not in test.keys():
                    print("Le numlink {}  n' a pas toute les valeurs ".format(num))
                    return False
        return True

    def export_cl(self, name="cli_fg_lk.obj"):
        """
        :param obj: object to dump
        :param name: name file
        :return:
        """
        with open(name, "w") as file:
            json.dump(self.param_fg, file)

    def import_cl(self, name="cli_fg_lk.obj"):
        if os.path.isfile(name):
            with open(name, "r") as file:
                obj = json.load(file)

            for key, val in obj.items():
                setattr(self.param_fg, key, val)

            if not self.check_param():
                self.param_fg = {}
                return False
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
