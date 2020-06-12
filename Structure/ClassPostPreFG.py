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
from .ClassMethod import ClassMethod
import pickle

class ClassInfoParamFG:
    def __init__(self):
        self.param_fg = {}
        self.link_name_id = {}
        self.list_poly_trav = {}
        self.list_poly_pil ={}
        self.profil = {}
        self.param_g = {}
        self.abac = {}


class ClassPostPreFG:
    def __init__(self, mgis = None):

        self.mgis = mgis
        self.cli = ClassInfoParamFG()

        if not self.mgis:
            self.cli = self.import_cl('cli_fg.obj')
        else:
            self.clmeth = ClassMethod(self.mgis)

    def import_cl(self, name='object.obj'):
        with open(name, 'rb') as file:
            obj = pickle.load(file)
        return obj

    def export_cl(self, obj, name='object.obj'):
        with open(name, 'wb') as file:
            pickle.dump(obj, file)

    def create_cli_fg(self):
        """
        Creation of ClassInfomParamFG (python object save compte data)
        :param mgis:
        :return:
        """
        cli = ClassInfoParamFG()

        # ClassFloodGate
        cli.list_actif = self.clmeth.fg_actif()
        cli.param_fg, cli.link_name_id = self.clmeth.get_param_fg()

        # ClassLaws
        cli.list_poly_trav = {}
        cli.list_poly_pil = {}
        cli.profil = {}
        cli.param_g = {}
        for id_config in cli.list_actif:
            cli.list_poly_trav[id_config] = self.clmeth.select_poly_elem(id_config,0)
            cli.list_poly_pil[id_config] = self.clmeth.select_poly_elem(id_config, 0)
            cli.profil[id_config] = self.clmeth.get_profil(id_config)
            cli.param_g[id_config] = self.clmeth.get_param_g('all', id_config)

        cli.abac = self.clmeth.get_abac('all')

        self.export_cl(cli,"cli_fg")


    def get_profil(self,id_config):
        """
        Get profil coordonnee
        :param id_config: index of hydraulic structure
        """
        if self.mgis:
            if self.clmeth.checkprofil(id_config):
                return self.clmeth.get_profil(id_config)
            else:
                return  None
        else:
            return self.cli.profil[id_config]


    def get_param_fg(self):
        """get variable of the floodgate """
        if self.mgis:
            return self.clmeth.get_param_fg()
        else:
            return self.cli.param_fg,  self.cli.link_name_id

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
            new_dico ={}
            for info in list_recup:
                new_dico[info]= dico[info]
            return new_dico
        else:
            dico = self.cli.param_g[id_config]
            new_dico = {}
            for info in list_recup:
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

