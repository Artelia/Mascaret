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
import pickle
import os
from .ClassMethod import ClassMethod


class ClassInfoParamFG(object):
    def __init__(self):
        self.param_fg = {}
        self.link_name_id = {}
        self.list_poly_trav = {}
        self.list_poly_pil = {}
        self.profil = {}
        self.param_g = {}
        self.abac = {}
        self.list_actif = []


class ClassPostPreFG:
    def __init__(self, main=None):

        self.mgis = main
        self.cli = ClassInfoParamFG()

        if not main:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../mascaret'))
            path = os.path.join(path, 'cli_fg.obj')
            self.import_cl(path)
        else:
            self.clmeth = ClassMethod(self.mgis)

    def import_cl(self, name='object.obj'):
        if os.path.isfile(name):
            with open(name, 'rb') as file:
                obj = pickle.load(file)

            for key, val in obj.items():
                setattr(self.cli, key, val)

        else:
            pass

    def export_cl(self, obj, name='object.obj'):
        with open(name, 'wb') as file:
            pickle.dump(obj, file)

    def create_cli_fg(self, name=None):
        """
        Creation of ClassInfomParamFG (python object save compte data)
        :param mgis:
        :return:
        """
        list_actif = self.clmeth.fg_actif()

        if list_actif:
            param_fg, link_name_id = self.clmeth.get_param_fg()
            # ClassLaws
            list_poly_trav = {}
            list_poly_pil = {}
            profil = {}
            param_g = {}

            for id_config in list_actif:
                list_poly_trav[id_config] = self.clmeth.select_poly_elem(id_config, 0)
                list_poly_pil[id_config] = self.clmeth.select_poly_elem(id_config, 1)
                profil[id_config] = self.clmeth.get_profil(id_config)
                param_g[id_config] = self.clmeth.get_param_g('all', id_config)

            dico = {"list_actif": self.clmeth.fg_actif(),
                    "param_fg": param_fg,
                    "link_name_id": link_name_id,
                    "list_poly_trav": list_poly_trav,
                    "list_poly_pil": list_poly_pil,
                    "profil": profil,
                    "param_g": param_g,
                    "abac": self.clmeth.get_abac('all')
                    }
            self.export_cl(dico, name)

    def get_profil(self, id_config):
        """
        Get profil coordonnee
        :param id_config: index of hydraulic structure
        """
        if self.mgis:
            if self.clmeth.checkprofil(id_config):
                return self.clmeth.get_profil(id_config)
            else:
                return None
        else:
            return self.cli.profil[id_config]

    def get_param_fg(self):
        """get variable of the floodgate """
        if self.mgis:
            return self.clmeth.get_param_fg()
        else:
            return self.cli.param_fg, self.cli.link_name_id

    def fg_actif(self):
        """list of  active flood gate"""
        if self.mgis:
            return self.clmeth.fg_actif()
        else:
            return self.cli.list_actif

    def get_param_g(self, list_recup, id_config):
        """
               Get general parameters
               :param list_recup: list of  value to get
               :param id_config: index of hydraulic structure
               :return: dico
               """
        if self.mgis:
            dico = self.clmeth.get_param_g('all', id_config)
            new_dico = {}
            for info in list_recup:
                if info in dico.keys():
                    new_dico[info] = dico[info]
            return new_dico
        else:
            dico = self.cli.param_g[id_config]
            new_dico = {}
            for info in list_recup:
                if info in dico.keys():
                    new_dico[info] = dico[info]
            return new_dico

    def get_abac(self, liste):
        """
        Get abacus
        :param list_recup: list of abacus
        :return: dico with abacus data
        """
        if self.mgis:
            return self.clmeth.get_abac(liste)
        else:
            dico = {}
            for key in liste:
                dico[key] = self.cli.abac[key]
            return dico

    def select_poly_elem(self, id_config, type_conf):
        if self.mgis:
            return self.clmeth.select_poly_elem(id_config, type_conf)

        else:
            if type_conf == 0:
                return self.cli.list_poly_trav[id_config]
            elif type_conf == 1:
                return self.cli.list_poly_pil[id_config]
