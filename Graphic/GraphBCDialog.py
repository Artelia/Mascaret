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

import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .GraphBC import GraphBC

from ..HydroLawsDialog import dico_typ_law

class GraphBCDialog(QWidget):
    def __init__(self, mgis, feature, couche):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_visu_law.ui'),self)
        print(str(feature.attributes()))
        print(couche)
        self.wdgt_law = GraphBCLaw(self.mgis)
        self.tabWidget.addTab(self.wdgt_law,
                              'Laws')

        self.wdgt_obs = GraphBCObs(self.mgis)
        self.tabWidget.addTab(self.wdgt_obs,
                               'Observations')
        # print(feature.fieldNameIndex('name'))


class GraphBCLaw(QWidget):
    def __init__(self, mgis):
        QWidget.__init__(self, mgis)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_wdget_bc.ui'),self)
        self.initialising = True
        self.graph_obj = GraphBC(self, self.lay_graph_home)
        # only extremites loi mascaret mais loi corespond 1er chiffre
        #extr_toloi = {0: 6, 1: 1, 2: 2, 3: 4, 4: 5, 5: 4, 8: 3, 6: 6, 7: 7}
        # only weirs
        #abaque_toloi = {1: 6, 2: 4, 5: 2, 6: 5, 7: 5, 8: 7}
        # lateral
        # lat_inflows = self.mdb.select("lateral_inflows", order="abscissa",
        #                               list_var=["name", "method",
        #                                         "firstvalue"])
        # lat_inflows['type'] = []
        # lat_weirs = self.mdb.select("lateral_weirs", order="abscissa",
        #                             list_var=["name"])
        # extremities = self.mdb.select("extremities", "type!=10 ", "active",
        #                               list_var=["name", "type", "method",
        #                                         "firstvalue"])
        # weirs = self.mdb.select("weirs", order="abscissa",
        #                         list_var=["name"])
        # # Structure
        # # dico_str = self.mdb.select('struct_config', "active",
        # #                           "abscissa")
        # # seuils, loi_struct = self.modif_seuil(seuils, dico_str)


class GraphBCObs(QWidget):
    def __init__(self, mgis):
        QWidget.__init__(self,mgis)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_wdget_bc.ui'),self)
        self.initialising = True
        self.graph_obj = GraphBC(self, self.lay_graph_home)
