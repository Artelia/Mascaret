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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import qVersion
from qgis.PyQt.QtGui import QColor, QIcon

from qgis.core import QgsApplication, QgsWkbTypes
from qgis.gui import QgsRubberBand

from .FunctionAssimDialog import reproject_geom_to_project
from .ClassAssimKsWidget import ClassAssimKsWidget
from .ClassAssimLawWidget import ClassAssimLawWidget

QT_VERSION = [int(v) for v in qVersion().split(".")][0]

FORM_CLASS, BASE = uic.loadUiType(
    os.path.join(os.path.join(os.path.dirname(__file__), "..", "..", "ui/ui_assimilation.ui"))
)


class ClassAssimilationDialog(BASE, FORM_CLASS):
    """Main dialog for managing assimilation configuration.

    Provides tabbed interface for Ks coefficient and hydraulic law assimilation
    configuration with map visualization of selected control zones and laws.
    """

    def __init__(self, mgis, iface):
        """Initialize the assimilation configuration dialog.

        :param mgis: Main QGIS interface object.
        :param iface: QGIS interface instance.
        :return: None. Sets up tabs, widgets, and rubber band display.
        """
        super(ClassAssimilationDialog, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        self.iface = iface
        self.cur_wgt = "ks"

        self.rb_format = QgsWkbTypes.LineGeometry
        self.rb = QgsRubberBand(iface.mapCanvas(), self.rb_format)
        self.rb_color_default = QColor("magenta")
        self.rb_color_obs = QColor("cyan")

        self.wgt_ks = ClassAssimKsWidget(mgis, iface)
        self.lay_ks.addWidget(self.wgt_ks)
        self.wgt_ks.display_rb.connect(self.display_map_rb)

        self.wgt_law = ClassAssimLawWidget(mgis, iface)
        self.lay_law.addWidget(self.wgt_law)
        self.wgt_law.display_rb.connect(self.display_map_rb)

        self.tab_assim.currentChanged.connect(self.tab_changed)
        self.tab_changed()

        self.bt_close.setIcon(QIcon(QgsApplication.getThemeIcon("mActionFileExit.svg")))
        self.bt_close.clicked.connect(self.close)

        self.mgis.main_graph()

    def tab_changed(self):
        """Handle tab change between Ks and Law assimilation interfaces."""
        self._reset_rb()
        if self.tab_assim.currentIndex() == 0:
            self.cur_wgt = "ks"
        else:
            self.cur_wgt = "law"
        self.display_map_rb()

    def _rb_width_from_geom_type(self, geom_type):
        """Return rubber band width by geometry type."""
        if geom_type == QgsWkbTypes.PointGeometry:
            return 16
        if geom_type == QgsWkbTypes.LineGeometry:
            return 8
        return 4

    def _reset_rb(self):
        """Reset and clear current rubber band."""
        if self.rb is not None:
            self.rb.reset(self.rb_format)
        self.iface.mapCanvas().refresh()

    def display_map_rb(self):
        """Update rubber band display on map for current selected entity."""
        self._reset_rb()

        if self.cur_wgt == "ks":
            rb_data = self.wgt_ks.get_current_rb_data()
        else:
            rb_data = self.wgt_law.get_current_rb_data()

        if not rb_data:
            return

        rb_geom = rb_data.get("geom")
        rb_geom_crs = rb_data.get("crs")
        if rb_geom is None:
            return

        geom_to_display = reproject_geom_to_project(rb_geom, rb_geom_crs)
        geom_type = QgsWkbTypes.geometryType(geom_to_display.wkbType())
        if geom_type == QgsWkbTypes.UnknownGeometry:
            geom_type = QgsWkbTypes.LineGeometry

        self.rb_format = geom_type
        self.rb = QgsRubberBand(self.iface.mapCanvas(), self.rb_format)
        self.rb.setColor(
            self.rb_color_obs if rb_data.get("is_observation") else self.rb_color_default
        )
        self.rb.setFillColor(QColor("transparent"))
        self.rb.setWidth(self._rb_width_from_geom_type(geom_type))
        self.rb.addGeometry(geom_to_display)
        self.rb.show()

    def closeEvent(self, event):
        """Handle dialog close event.

        Cleans up rubber band and resets zone selection tool on close.
        :param event: Close event object.
        :return: None. Performs cleanup before closing.
        """
        if self.rb is not None:
            self.rb.reset(self.rb_format)
        if self.wgt_ks.bt_sel_zone.isChecked():
            self.wgt_ks.bt_sel_zone.click()
