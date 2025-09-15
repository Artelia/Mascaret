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
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication, QAction
from qgis.PyQt.QtCore import Qt, qVersion

from .MascPlugDialog import MascPlugDialog

QT_VERSION = [int(v) for v in qVersion().split('.')][0]
try:
    if QT_VERSION > 5:
        from . import resourcesQT6
    else:
        from . import resourcesQT5

except ImportError:
    pass


class MascPlug:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.dlg = None
        self.icon_path = ":/plugins/Mascaret/icones/icon_base.png"
        self.name_plug = "Mascaret"

    def initGui(self):
        """initialisation GUI"""
        self.action = QAction(
            QIcon(self.icon_path),
            QApplication.translate(self.name_plug, self.name_plug),
            self.iface.mainWindow(),
        )
        self.action.setObjectName(self.name_plug)

        # QObject.connect(self.action, SIGNAL('triggered()'), self.run)
        self.action.triggered.connect(self.run)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(
            QApplication.translate(self.name_plug, self.name_plug), self.action
        )

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(
            QApplication.translate(self.name_plug, self.name_plug), self.action
        )

        if self.dlg is not None:
            self.dlg.close()

    def run(self):
        # keep opened only one instance
        if self.dlg is None:
            self.dlg = MascPlugDialog(self.iface)
            self.dlg.destroyed.connect(self.on_destroyed)
            # QObject.connect(self.dlg, SIGNAL('destroyed(QObject *)'), self.on_destroyed)
        self.dlg.show()
        self.dlg.raise_()
        if QT_VERSION > 5:
            self.dlg.setWindowState(self.dlg.windowState() & ~Qt.WindowState.WindowMinimized)
        else:
            self.dlg.setWindowState(self.dlg.windowState() & ~Qt.WindowMinimized)
        self.dlg.activateWindow()

    def on_destroyed(self, obj):
        self.dlg = None
