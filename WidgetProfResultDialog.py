# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : Dec,2021
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



class WidgetProfResultDialog(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.mgis = parent.mgis
        self.mdb = self.mgis.mdb

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_wdgt_profRes.ui'), self)

        self.ctrl_label = {'z' :  self.label_z,
                      'area' :  self.label_warea_l,
                      'perimeter': self.label_wpermi_l,
                     'width' : self.label_wmirror_l,
                    }
        for key, ctrl_ in self.ctrl_label.items():
            ctrl_.setText('None')

    def change_label(self, dico):
        for key, val in dico.items():
            if val :
                val_d = str(round(val, 2))
            else:
                val_d =  None
            self.ctrl_label[key].setText(val_d)
