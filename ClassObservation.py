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

import datetime
import os
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


class ClassObservation:
    def __init__(self, main):
        self.mgis = main
        self.mdb = self.mgis.mdb

    def evt_to_obs(self, data_file):

        try:
            obs = {}

            # self.mgis.add_info("{} ".format(dataFile))
            for file in data_file:
                if os.path.isfile(file):
                    with open(file, 'r') as fichier:
                        codes = fichier.readline().strip().split(';')[1:]
                        types = fichier.readline().strip().split(';')[1:]
                        nom_stat = fichier.readline().strip().split(';')[1:]
                        obs = {'code': [], 'date': [], 'type': [], 'comment': [], 'valeur': []}
                        for ligne in fichier:
                            temp = ligne.strip().split(';')
                            for i, val in enumerate(temp[1:]):
                                if float(val) != -99.99:
                                    obs['code'].append("'{}'".format(codes[i]))
                                    obs['date'].append("'{}'".format(self.fmt_date(temp[0])))
                                    obs['type'].append("'{}'".format(types[i]))
                                    obs['comment'].append("'{}'".format(nom_stat[i]))
                                    obs['valeur'].append(val)

                self.mdb.insert2('observations', obs)
                if self.mgis.DEBUG:
                    self.mgis.add_info("File {0} loads".format(file))
            return True
        except Exception as e:
            self.mgis.add_info("Loading to observations is an echec.")
            if self.mgis.DEBUG:
                self.mgis.add_info(repr(e))
            return False

    @staticmethod
    def fmt_date(date):
        return datetime.datetime.strptime(date, '%d/%m/%Y %H:%M')
