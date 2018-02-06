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
"""

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import datetime
import os

class Class_observation():

    def __init__(self,main):
        self.mgis=main
        self.mdb=self.mgis.mdb

    def fmtDate(self,date):
        return (datetime.datetime.strptime(date, '%d/%m/%Y %H:%M'))

    def evtTOobs(self,dataFile):

        try:
            obs = {}

            # self.mgis.addInfo("{} ".format(dataFile))
            for file in dataFile:
                if os.path.isfile(file):
                    with open(file, 'r') as fichier:
                        codes = fichier.readline().strip().split(';')[1:]
                        types = fichier.readline().strip().split(';')[1:]
                        # nomStat = fichier.readline().strip().split(';')[1:]
                        obs = {'code': [], 'date': [], 'type': [], 'valeur': []}
                        for ligne in fichier:
                            temp = ligne.strip().split(';')
                            for i, val in enumerate(temp[1:]):
                                if val > -99.9:
                                    obs['code'].append("'{}'".format(codes[i]))
                                    obs['date'].append("'{}'".format(self.fmtDate(temp[0])))
                                    obs['type'].append("'{}'".format(types[i]))
                                    obs['valeur'].append(val)

                self.mdb.insert2('observations', obs)
                if self.mgis.DEBUG:
                     self.mgis.addInfo("File {0} loads".format(file))
            return True
        except Exception, e:
            self.mgis.addInfo("Loading to observations is an echec.")
            if self.mgis.DEBUG:
                self.mgis.addInfo(repr(e))
            return False
