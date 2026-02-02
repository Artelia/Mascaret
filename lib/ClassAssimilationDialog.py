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
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor

from qgis.core import QgsApplication, QgsWkbTypes, QgsGeometry
from qgis.gui import QgsRubberBand

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
        self.cur_wgt = 'ks'

        self.rb_format = QgsWkbTypes.LineGeometry
        self.rb = QgsRubberBand(iface.mapCanvas(), self.rb_format)

        self.wgt_ks = ClassAssimKsWidget(mgis, iface)
        self.lay_ks.addWidget(self.wgt_ks)
        self.wgt_ks.display_rb.connect(self.display_map_rb)

        self.wgt_law = ClassAssimLawWidget(mgis, iface)
        self.lay_law.addWidget(self.wgt_law)
        self.wgt_law.display_rb.connect(self.display_map_rb)

        self.tab_assim.currentChanged.connect(self.tab_changed)
        self.tab_changed()

        self.mgis.main_graph()

    def tab_changed(self):
        self.rb.reset(self.rb_format)

        if self.tab_assim.currentIndex() == 0:
            self.cur_wgt = 'ks'
            self.rb_format = QgsWkbTypes.LineGeometry
            self.rb = QgsRubberBand(self.iface.mapCanvas(), self.rb_format)
            self.rb.setColor(Qt.magenta)
            self.rb.setFillColor(QColor("transparent"))
            self.rb.setWidth(8)
        else:
            self.cur_wgt = 'law'
            self.rb_format = QgsWkbTypes.PointGeometry
            self.rb = QgsRubberBand(self.iface.mapCanvas(), self.rb_format)
            self.rb.setColor(Qt.magenta)
            self.rb.setFillColor(QColor("transparent"))
            self.rb.setWidth(16)

        self.display_map_rb()

    def display_map_rb(self):
        self.rb.reset(self.rb_format)

        if self.cur_wgt == 'ks':
            wgt = self.wgt_ks
            rb_visible = wgt.bt_disp_zone.isChecked()
            rb_geom = wgt.d_zone_ks[wgt.cur_zone_ks]["geom"]
        elif self.cur_wgt == 'law':
            wgt = self.wgt_law
            rb_visible = wgt.bt_disp_law.isChecked()
            rb_geom = wgt.d_laws[wgt.cur_perturb_var][wgt.cur_law]["geom"]
        else:
            rb_visible = False
            rb_geom = None

        if rb_visible and rb_geom:
            self.rb.addGeometry(rb_geom)
            self.rb.show()

    def closeEvent(self, event):
        self.rb.reset(self.rb_format)
        if self.wgt_ks.bt_sel_zone.isChecked():
            self.wgt_ks.bt_sel_zone.click()
