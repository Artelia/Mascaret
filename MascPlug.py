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


from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    import resources
except ImportError:
    pass
# Import the code for the dialog
from MascPlug_dialog import MascPlugDialog


class MascPlug:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        self.iface = iface
        self.dlg = None
        self.icon_path = ":/plugins/Mascaret/icones/icon_base.png"
        self.namePlug='Mascaret'

    def initGui(self):
        self.action = QAction(QIcon(self.icon_path), QApplication.translate(self.namePlug, self.namePlug),
                              self.iface.mainWindow())
        self.action.setObjectName(self.namePlug)
        QObject.connect(self.action, SIGNAL('triggered()'), self.run)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(QApplication.translate(self.namePlug, self.namePlug), self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(QApplication.translate(self.namePlug, self.namePlug), self.action)

        if self.dlg is not None:
            self.dlg.close()

    def run(self):
        # keep opened only one instance
        if self.dlg is None:
            self.dlg = MascPlugDialog(self.iface)
            QObject.connect(self.dlg, SIGNAL('destroyed(QObject *)'), self.onDestroyed)
        self.dlg.show()
        self.dlg.raise_()
        self.dlg.setWindowState(self.dlg.windowState() & ~Qt.WindowMinimized)
        self.dlg.activateWindow()

    def onDestroyed(self, obj):
        self.dlg = None


