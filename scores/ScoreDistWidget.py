# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : September,2021
copyright            : (C) 2021 by Artelia
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


class ScoreDistWidget(QWidget):
    def __init__(self, windmain):
        QWidget.__init__(self)
        self.windmain = windmain
        self.mdb = self.windmain.mgis.mdb
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath, 'ui/scores/ui_distib_score.ui'),self)

    # self.table_dist

    def fill_tab(self, ):

        self.table_dist.setModel('test')
        self.table_dist.setColumnWidth(0, 120)
        self.table_dist.setColumnWidth(1, 80)
        self.table_dist.setColumnWidth(2, 120)
        model = self.ui.table_dist.model()

        a = ['toto1', 'toto2']
        b= ['test1, test2']
        for r, row in enumerate(a):
            for c, val in enumerate(b):
                itm = QStandardItem()
                itm.setData(val, 0)
                model.setItem(r, c, itm)



