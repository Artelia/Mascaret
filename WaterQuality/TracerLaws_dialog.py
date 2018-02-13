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


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *
import os
from qgis.core import *
from qgis.utils import *
from qgis.gui import *




class TracerLaws_dialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_tracer_laws.ui'), self)

        self.initUI()

        self.ui.actionB_edit.triggered.connect(self.edit_law)
        self.ui.actionB_new.triggered.connect(self.new_law)
        self.ui.b_OK_page2.accepted.connect(self.acceptPage2)
        self.ui.b_OK_page2.rejected.connect(self.rejectPage2)
        self.ui.b_OK_page1.accepted.connect(self.reject)

    def initUI(self):
        self.ui.Law_pages.setCurrentIndex(0)

    def edit_law(self):
        #charger les informations
        #changer de page
        self.ui.Law_pages.setCurrentIndex(1)

    def new_law(self):
        #changer de page
        self.ui.Law_pages.setCurrentIndex(1)

    def acceptPage2(self):
        #save Info
        # modificaito liste page 1
        #change de page
        self.ui.Law_pages.setCurrentIndex(0)

    def rejectPage2(self):
        if self.mgis.DEBUG:
            self.mgis.addInfo("Cancel of Tracer Laws")
        self.ui.Law_pages.setCurrentIndex(0)
