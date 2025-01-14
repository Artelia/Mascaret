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

from .ClassTableWQ import ClassTableWQ
from ..Function import data_to_float

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
    from qgis.PyQt.QtWidgets import *


class ClassPhysicalParamDialog(QDialog):
    def __init__(self, mgis, mod):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbwq = ClassTableWQ(self.mgis, self.mdb)
        self.dico_phy = self.tbwq.dico_phy
        self.cur_wq_mod = mod

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_physical_param.ui"), self)
        self.ui.btn_val_def.clicked.connect(self.val_def)

        styled_item_delegate = QStyledItemDelegate()
        styled_item_delegate.setItemEditorFactory(ItemEditorFactory())
        self.ui.tab_param.setItemDelegate(styled_item_delegate)

        self.init_ui()

    def init_ui(self):
        model = QStandardItemModel()
        model.insertColumns(0, 4)
        model.setHeaderData(0, 1, "ID", 0)
        model.setHeaderData(1, 1, "Sigle", 0)
        model.setHeaderData(2, 1, "Parameter", 0)
        model.setHeaderData(3, 1, "Value", 0)

        sql = "SELECT id, sigle, text, value FROM {0}.tracer_physic WHERE type = '{1}' ORDER BY id".format(
            self.mdb.SCHEMA, self.cur_wq_mod
        )
        rows = self.mdb.run_query(sql, fetch=True)
        model.insertRows(0, len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                itm = QStandardItem()
                itm.setData(val, 0)
                if c == 3:
                    itm.setData(data_to_float(val), 0)
                    itm.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                    itm.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    itm.setData(val, 0)
                    itm.setFlags(Qt.ItemIsEnabled)
                model.setItem(r, c, itm)

        self.ui.tab_param.setModel(model)
        self.ui.tab_param.hide()
        self.ui.tab_param.resizeColumnsToContents()
        self.ui.tab_param.resizeRowsToContents()
        self.ui.tab_param.setColumnHidden(0, True)
        self.ui.ui.tab_param.show()

    def val_def(self):
        for r, param in enumerate(self.dico_phy[self.cur_wq_mod]["physic"]):
            mdl = self.ui.tab_param.model()
            mdl.item(r, 3).setData(param["value"], 0)


class ItemEditorFactory(QItemEditorFactory):
    # http://doc.qt.io/qt-5/qstyleditemdelegate.html#subclassing-qstyleditemdelegate
    # It is possible for a custom delegate to provide editors without the use of an editor item factory.
    # In this case, the following virtual functions must be reimplemented:
    def __init__(self):
        QItemEditorFactory.__init__(self)

    def createEditor(self, user_type, parent):
        if user_type == QVariant.Double or user_type == 0:
            double_spin_box = QDoubleSpinBox(parent)
            double_spin_box.setDecimals(10)
            double_spin_box.setMinimum(-1000000000.0)  # The default maximum value is 99.99.
            double_spin_box.setMaximum(1000000000.0)  # The default maximum value is 99.99.
            return double_spin_box
        else:
            return ItemEditorFactory.createEditor(user_type, parent)


class MySpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(MySpinBox, self).__init__(parent)
