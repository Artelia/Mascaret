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
import math as m
import numpy as np
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from shapely.geometry import *


class ClassSeuil:
    def __init__(self, parent):
        self.parent = parent
        self.mgis = self.parent.mgis
        self.mdb = self.parent.mdb
        self.tbst = self.parent.tbst
        self.grav=self.parent.grav


    def seuil(self, id_config, method=''):
        if self.parent.checkprofil(id_config):
            profil = self.parent.get_profil(id_config)
        else:
            msg = "Profile copy isn't found"
            self.mgis.add_info(msg)
            print(msg)
            return

        list_recup = ['FIRSTWD', 'BIAIOUV', 'NBTRAVE', 'TOTALOUV',
                      'TOTALW', 'FORMCUL', 'ORIENTM',
                      'PENTTAL', 'ZTOPTAB', 'EPAITAB', 'BIAICUL',
                      # pile de pont
                      'LARGPIL', 'LONGPIL', 'FORMPIL', 'BIAIPIL',
                      # numeric
                      'MINH', 'PASH', 'MINQ', 'MAXQ', 'PASQ']
        self.param_g = self.parent.get_param_g(list_recup, id_config)
        where = " id_config={} and type=1 ".format(id_config)
        order = "id_elem"
        list_poly_pil = self.parent.select_poly('struct_elem', where, order)['polygon']
        self.param_g['ZPC'] = self.param_g['ZTOPTAB'] - self.param_g['EPAITAB']

        poly_p = self.parent.poly_profil(profil)
        (minx, miny, maxx, maxy) = poly_p.bounds
        list_hn = [miny]
        list_hn += list(np.arange(miny + self.param_g['MINH'], self.param_g['ZPC'], self.param_g['PASH']))
        list_hn.append(self.param_g['ZPC'])

        list_q = list(np.arange(self.param_g['MINQ'], self.param_g['MAXQ'], self.param_g['PASQ']))
        list_q.append(self.param_g['MAXQ'])

        self.param_g['BIAIOUV'] = self.param_g['BIAIOUV'] / 180. * m.pi  # rad
        self.param_g['NBPIL'] = self.param_g['NBTRAVE'] - 1
        list_final = []

