# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
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
comment:

"""

import csv
import datetime
import os, sys
import re
import shutil
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as ETparse

from qgis.PyQt.QtCore import qVersion

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .table_WQ import table_WQ

class class_mascWQ():
    def __init__(self, main, file ):
        """

        :param main: main program
        :param mod: tracer mod
        :param file: repertory Mascaret
        """
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.schema=self.mdb.SCHEMA
        self.iface = self.mgis.iface

        self.tbwq = table_WQ(self.mgis, self.mdb)
        self.dico_phy = self.tbwq.dico_phy
        self.dossierFileMasc=file

        sql = "SELECT {} FROM {}.parametres WHERE parametre = 'modeleQualiteEau'".format('steady',self.schema)
        result = self.mdb.run_query(sql ,fetch=True)

        self.cur_wq_mod =self.tbwq.dico_wq_mod[int(result[0][0])]


    def create_filephy(self):
        """creation .phy file """

        where="type = '{}'".format(self.cur_wq_mod)
        order="id"
        result = self.mdb.select('tracer_physic',where,order)
        entetfr=u": NOMBRE DE PARAMETRES PHYSIQUES"
        entet = u": NUMBER OF PHYSICAL PARAMETERS"
        with open(os.path.join(self.dossierFileMasc, self.cur_wq_mod.lower() + '.phy'), 'w') as fich:
            fich.write('{} {}\n'.format(len(self.dico_phy[ self.cur_wq_mod]['physic']),entet))
            for i,phy in enumerate(self.dico_phy[ self.cur_wq_mod]['physic']):
                idx=result['sigle'].index(phy['sigle'])
                fich.write('{} : {}\n'.format(result['value'][idx],result['text'][idx]))

    def law_tracer(self):

        #id_trac id dans la table tracer name
        #id_config nom loi
        extrem = self.mdb.select('extremities')
        list_loi=[]
        for i,cond in enumerate(extrem['active']):
            if cond :
                list_loi.append(extrem['law_wq'][i])

        if list_loi!=[]:
            where="type = '{}'".format(self.cur_wq_mod)
            order="id"
            list_trac = self.mdb.select('tracer_name',where,order)

            print(list_loi)

            # where = "type = '{}'".format(self.cur_wq_mod)
            # loi_trac = self.mdb.select('tracer_config', where, order)
            # print(loi_trac)

            #header
            # for nom in  list_trac :
            #
            #     print( nom, list_trac[nom])
            # entet=u"# loi_1_tracer\n"+
            #       u"# Temps (s) \n"+
            #       u"         S\n"




# *****************************************
