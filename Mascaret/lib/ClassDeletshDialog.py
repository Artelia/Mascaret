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

from ..ui.custom_control import ClassWarningBox, _qt_is_checked

QT_VERSION = [int(v) for v in qVersion().split('.')][0]

class ClassDeletshDialog(QDialog):
    """
    Class allow to delete schema
    """

    def __init__(self, mgis, iface):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_delete_sh.ui"), self)
        self.box = ClassWarningBox()
        self.liste_model = self.mdb.liste_models()
        self.parent = {}
        self.tree = None
        self.init_gui()

    def init_gui(self):
        """
        initialisation GUI
        """
        if len(self.liste_model) > 0:
            if QT_VERSION > 5:
                qt_tris = Qt.ItemFlag.ItemIsAutoTristate
                qt_item_check = Qt.ItemFlag.ItemIsUserCheckable
                qt_ucheck = Qt.CheckState.Unchecked

            else:
                qt_tris = Qt.ItemIsAutoTristate
                qt_item_check = Qt.ItemIsUserCheckable
                qt_ucheck = Qt.Unchecked
            self.tree = self.ui.treeWidget
            for model in self.liste_model:
                self.parent[model] = QTreeWidgetItem(self.tree)
                self.parent[model].setText(0, model)
                self.parent[model].setFlags(self.parent[model].flags() | qt_tris | qt_item_check )
                self.parent[model].setCheckState(0,  qt_ucheck)


        else:
            self.ui.b_delete.setDisabled(True)
        self.ui.b_delete.clicked.connect(self.lancement)
        self.ui.b_cancel.clicked.connect(self.annule)

    def lancement(self):
        """Delete selection function"""
        selection = []
        for model in self.liste_model:
            if _qt_is_checked(self.parent[model], check_level="any"):
                selection.append("{}".format(model))
        self.close()

        self.iface.messageBar().clearWidgets()
        progress_message_bar = self.iface.messageBar()
        progress = QProgressBar()
        progress.setMaximum(100)
        progress_message_bar.pushWidget(progress)

        n = len(selection)
        ok = self.box.yes_no_q("Do you want to delete ?")

        if ok:
            for i, model in enumerate(selection):
                self.mdb.drop_model(model, cascade=True)

                self.mgis.add_info("Deletion of {0} Model is done".format(model))

                progress.setValue(round(i / n * 100))
        else:
            self.mgis.add_info("Droping Model cancelled.")

        self.iface.messageBar().clearWidgets()

    def annule(self):
        """ "Cancel"""
        self.close()
