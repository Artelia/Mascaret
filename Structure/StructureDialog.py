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

from .ClassTableStructure import ClassTableStructure
from .GraphStructure import GraphStructure
from .StructureEditDialog import ClassStructureEditDialog
# from ..Function import data_to_float

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
    from qgis.PyQt.QtWidgets import *


class ClassStructureDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure(self.mgis, self.mdb)
        # self.cur_wq_mod = self.tbwq.get_cur_wq_mod()

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_structure.ui'), self)

        self.tree_struct.setColumnWidth(0, 200)
        self.tree_struct.setColumnWidth(1, 100)
        self.tree_struct.setColumnWidth(2, 100)

        self.b_new.clicked.connect(self.new_struct)
        self.b_edit.clicked.connect(self.edit_struct)

        self.init_ui()

    def init_ui(self):
        self.graph_struct = GraphStructure(self.mgis, self.ui.lay_graph)
        self.fill_lst_struct()

    def fill_lst_struct(self, id=None):
        for id_type, elem in self.tbst.dico_struc_typ.items():
            typ_itm = QTreeWidgetItem()
            typ_itm.setFlags(Qt.ItemIsEnabled)
            typ_itm.setData(0, 32, id_type)
            typ_itm.setText(0, elem['name'])
            self.tree_struct.addTopLevelItem(typ_itm)
            sql = "SELECT * FROM {0}.struct_config WHERE type = '{1}' ORDER BY name".format(self.mdb.SCHEMA, id_type)
            rows = self.mdb.run_query(sql, fetch=True)
            for row in rows:
                ouv_itm = QTreeWidgetItem()
                ouv_itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                ouv_itm.setData(0, 32, int(row[0]))
                ouv_itm.setText(0, row[1])
                ouv_itm.setText(1, self.tbst.dico_meth_calc[row[3]])
                ouv_itm.setText(2, str(row[2]))
                typ_itm.addChild(ouv_itm)
            typ_itm.setExpanded(True)

        if id:
            for p in range(self.tree_struct.topLevelItemCount()):
                for c in range(self.tree_struct.topLevelItem(p).childCount()):
                    itm = self.tree_struct.topLevelItem(p).child(c)
                    if itm.data(0, 32) == id:
                        self.tree_struct.setCurrentItem(itm, 0)
                        break
        else:
            self.display_graph()

    def display_graph(self):
        if self.tree_struct.selectedItems():
            itm = self.tree_struct.selectedItems()[0]
            struct = itm.data(0, 32)
            self.graph_struct.initGraph(struct)
        else:
            self.graph_struct.initGraph(None)

    def new_struct(self):
        dlg = ClassStructureEditDialog(self.mgis, None)
        dlg.exec_()
        self.update_cur_item()

    def edit_struct(self):
        if self.tree_struct.selectedItems():
            itm = self.tree_struct.selectedItems()[0]
            id = itm.data(0, 32)
            dlg = ClassStructureEditDialog(self.mgis, id)
            if dlg.exec_():
                self.update_cur_item()

    def update_cur_item(self):
        itm = self.tree_struct.selectedItems()[0]
        id_config = itm.data(0, 32)
        sql = "SELECT name, method FROM {0}.struct_config WHERE id = {1} ORDER BY name".format(self.mdb.SCHEMA, id_config)
        row = self.mdb.run_query(sql, fetch=True)[0]
        itm.setText(0, row[0])
        itm.setText(1, self.tbst.dico_meth_calc[row[1]])