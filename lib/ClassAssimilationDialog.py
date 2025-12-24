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

from qgis.PyQt import uic

from .ClassAssimKsWidget import ClassAssimKsWidget
from .ClassAssimLawWidget import ClassAssimLawWidget

# QT_VERSION = [int(v) for v in qVersion().split('.')][0]
#
# try:
#     if QT_VERSION > 5:
#         from . import resourcesQT6
#     else:
#         from . import resourcesQT5
# except ImportError:
#     pass
#
# try:
#     qgis_version = core.QGis.QGIS_VERSION_INT
# except AttributeError:
#     qgis_version = core.Qgis.QGIS_VERSION_INT

FORM_CLASS, BASE = uic.loadUiType(
    os.path.join(os.path.join(os.path.dirname(__file__), "..", "ui/ui_assimilation.ui"))
)


class ClassAssimilationDialog(BASE, FORM_CLASS):
    """
    Class allow to update ks mesh planim of the selected profiles
    """

    def __init__(self, mgis, iface):
        super(ClassAssimilationDialog, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        self.iface = iface

        self.wgt_ks = ClassAssimKsWidget(mgis, iface)
        self.lay_ks.addWidget(self.wgt_ks)

        self.wgt_law = ClassAssimLawWidget(mgis, iface)
        self.lay_law.addWidget(self.wgt_law)

        self.mgis.main_graph()

    def closeEvent(self, event):
        self.wgt_ks.rb.reset(self.wgt_ks.rb_format)
        if self.wgt_ks.bt_sel_zone.isChecked():
            self.wgt_ks.bt_sel_zone.click()
