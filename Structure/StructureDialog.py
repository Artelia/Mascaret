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
from .StructureCreateDialog import ClassStructureCreateDialog

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
        self.tbst = ClassTableStructure()

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_structure.ui'), self)

        self.graph_struct = None

        self.tree_struct.setColumnWidth(0, 200)
        self.tree_struct.setColumnWidth(1, 100)
        self.tree_struct.setColumnWidth(2, 100)
        self.tree_struct.itemSelectionChanged.connect(self.display_graph)

        self.b_new.clicked.connect(self.new_struct)
        self.b_edit.clicked.connect(self.edit_struct)
        self.b_delete.clicked.connect(self.del_struct)

        self.init_ui()

    def init_ui(self):
        self.graph_struct = GraphStructure(self.mgis, self.ui.lay_graph)
        self.fill_lst_struct()

    def fill_lst_struct(self, id=None):
        rows = self.mdb.run_query(
            "SELECT gid, name FROM {0}.profiles".format(self.mdb.SCHEMA),
            fetch=True)
        dico_profil = {r[0]: r[1] for r in rows}
        self.tree_struct.clear()
        for id_type, elem in self.tbst.dico_struc_typ.items():
            typ_itm = QTreeWidgetItem()
            typ_itm.setFlags(Qt.ItemIsEnabled)
            typ_itm.setData(0, 32, id_type)
            typ_itm.setText(0, elem['name'])
            self.tree_struct.addTopLevelItem(typ_itm)
            sql = "SELECT id, name, id_prof_ori, method, comment,active FROM {0}.struct_config " \
                  "WHERE type = '{1}' ORDER BY name".format(self.mdb.SCHEMA,
                                                            id_type)
            rows = self.mdb.run_query(sql, fetch=True)
            for row in rows:
                ouv_itm = QTreeWidgetItem()
                ouv_itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                ouv_itm.setData(0, 32, int(row[0]))
                ouv_itm.setText(0, row[1])
                ouv_itm.setData(1, 32, int(row[2]))
                if row[2] in dico_profil.keys():
                    ouv_itm.setText(1, dico_profil[row[2]])
                else:
                    ouv_itm.setText(1, "#deleted")
                if not row[5]:
                    ouv_itm.setText(3, 'Deactivated')
                else:
                    ouv_itm.setText(3, '')
                if row[3] is not None:
                    ouv_itm.setText(2, self.tbst.dico_meth_calc[row[3]])
                ouv_itm.setText(4, str(row[4]))

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
            self.graph_struct.init_graph(struct)
            # print ("drawing struct : ", struct)
        else:
            self.graph_struct.init_graph(None)

    def new_struct(self):
        dlg = ClassStructureCreateDialog(self.mgis, None)
        if dlg.exec_():
            id = dlg.id_struct
            self.fill_lst_struct(id)
            self.edit_struct()

    def edit_struct(self):
        if self.tree_struct.selectedItems():
            itm = self.tree_struct.selectedItems()[0]
            id = itm.data(0, 32)
            dlg = ClassStructureEditDialog(self.mgis, id)
            dlg.exec_()
            self.fill_lst_struct(id)

    def del_struct(self):
        if self.tree_struct.selectedItems():
            itm = self.tree_struct.selectedItems()[0]
            id_struct = itm.data(0, 32)

            sql = "DELETE FROM {0}.profil_struct WHERE id_config = {1}".format(
                self.mdb.SCHEMA, id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_elem_param WHERE id_config = {1}".format(
                self.mdb.SCHEMA, id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_elem WHERE id_config = {1}".format(
                self.mdb.SCHEMA, id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_param WHERE id_config = {1}".format(
                self.mdb.SCHEMA, id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_config WHERE id = {1}".format(
                self.mdb.SCHEMA, id_struct)
            self.mdb.execute(sql)
            self.fill_lst_struct()
