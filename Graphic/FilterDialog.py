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
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

class ClassFilterDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_filter.ui'),
            self)
        self.meth_filter = None
        self.seuil = None
        self.valid = False
        lst_filter = [('f_pente', 'Slope-based Filter'), ('f_rdp', 'Filter based on Ramer-Douglas-Peucker  Algorithm')]
        #rdp Ramer-Douglas-Peucker  Algorithm
        for elem in lst_filter:
            self.cb_filter.addItem(elem[1], elem[0])
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)

        self.ui.adjustSize()

    def accept_page(self):
        self.meth_filter = self.cb_filter.currentData()
        self.seuil = self.spdouble_seuil.value()
        self.valid = True
        self.accept()

    def reject_page(self):
        self.reject()
