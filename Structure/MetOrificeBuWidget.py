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
from qgis.PyQt.QtGui import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ClassTableStructure import ClassTableStructure, ctrl_get_value, fill_qcombobox

class MetOrificeBuWidget(QWidget):
    def __init__(self, mgis, id_struct=None):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure()
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, "ui/structures/ui_orifice_bu.ui"), self
        )
        self.id_struct = id_struct

        self.completed = 0
        self.progress = self.ui.progressBar
        self.progress.setValue(0)

        self.sb_nb_trav.valueChanged.connect(self.change_ntrav)
        self.dsb_h_pas.valueChanged.connect(self.update_min_h_max)
        self.dsb_h_min.valueChanged.connect(self.update_min_h_max)
        self.tab_trav.itemChanged.connect(self.verif_param_trav)

        self.dico_ctrl = {
            "ZTOPTAB": [self.dsb_cote_tab],
            "PASH": [self.dsb_h_pas],
            "MINH": [self.dsb_h_min],
            "MAXH": [self.dsb_h_max],
            "PASQ": [self.dsb_q_pas],
            "NBTRAVE": [self.sb_nb_trav],
            "COEFDS": [self.dsb_ds],
            "COEFDO": [self.dsb_do],
        }

        self.dico_tab = {
            self.tab_trav: {
                "type": 0,
                "id": "{} + 1",
                "col": [
                    {"fld": "ABSBUSE", "cb": None, "valdef": 1.0},
                    {"fld": "COTERAD", "cb": None, "valdef": 0.0},
                    {"fld": "LARGTRA", "cb": None, "valdef": 1.0},
                ],
            }
        }

    def change_ntrav(self, nb_trav):
        nrow_trav = self.tab_trav.rowCount()
        if nb_trav < nrow_trav:
            self.tab_trav.setRowCount(nb_trav)
        else:
            for t in range(nrow_trav, nb_trav):
                self.insert_elem(self.tab_trav, t)

    def insert_elem(self, tab, row):
        tab.insertRow(row)
        for c, col in enumerate(self.dico_tab[tab]["col"]):
            if isinstance(col["valdef"], int) or isinstance(col["valdef"], float):
                val = col["valdef"]
            else:
                val = ctrl_get_value(col["valdef"])

            if col["cb"]:
                cb = QComboBox()
                cb.setProperty("row", row)
                tab.setCellWidget(row, c, cb)
                tab.cellWidget(row, c).currentIndexChanged.connect(col["fn"])
                fill_qcombobox(tab.cellWidget(row, c), col["cb"], val_def=val)
            else:
                itm = QTableWidgetItem()
                itm.setData(0, val)
                tab.setItem(row, c, itm)

    def update_min_h_max(self):
        self.dsb_h_max.setMinimum(self.dsb_h_min.value() + self.dsb_h_pas.value())

    def verif_param_trav(self, itm):
        if itm.data(0) <= 0.0:
            itm.setData(0, 1.0)

    def progress_bar(self, val):
        self.completed += val
        if self.completed > 100:
            self.completed = 100
        self.progress.setValue(round(self.completed))
