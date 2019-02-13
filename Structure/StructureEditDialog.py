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

from .ClassTableStructure import ClassTableStructure, ctrl_set_value, ctrl_get_value, fill_qcombobox
from .MetBradleyWidget import MetBradleyWidget
from .ClassMethod import ClassMethod

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QIcon
    from qgis.PyQt.QtWidgets import *

class ClassStructureEditDialog(QDialog):
    def __init__(self, mgis, id_struct):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure()
        self.clmeth = ClassMethod(self.mgis)
        self.wgt_met = QWidget()

        self.param_meth_calc = {0: {'name': 'Bradley 72',
                                    'wgt': MetBradleyWidget,
                                    'wgt_param': [self.mgis, '72'],
                                    'ctrl': 'bradley'},
                                1: 'Borda',
                                2: 'Loi de seuil',
                                3: 'Loi d''orifice',
                                4: {'name': 'Bradley 78',
                                    'wgt': MetBradleyWidget,
                                    'wgt_param': [self.mgis, '78'],
                                    'ctrl': 'bradley'}
                                }

        self.id_struct = id_struct
        self.lst_meth_calc = []
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_structure_edit.ui'), self)

        self.cb_met_calc.currentIndexChanged[int].connect(self.change_met_calc)
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)

        if id_struct:
            self.is_loading = True
            sql = "SELECT name, type, method, active FROM {0}.struct_config " \
                  "WHERE id = {1}".format(self.mdb.SCHEMA, self.id_struct)
            rows = self.mdb.run_query(sql, fetch=True)
            self.typ_struct = rows[0][1]

            for m in self.tbst.dico_struc_typ[self.typ_struct]['meth_calc']:
                self.lst_meth_calc.append([m, self.tbst.dico_meth_calc[m]])

            self.lbl_type.setText(self.tbst.dico_struc_typ[self.typ_struct]['name'])
            self.txt_name.setText(rows[0][0])
            self.cc_active.setChecked(rows[0][3])
            fill_qcombobox(self.cb_met_calc, self.lst_meth_calc, val_def=rows[0][2])
            self.is_loading = False

    def change_met_calc(self, idx):
        if not self.is_loading:
            if (QMessageBox.question(self, "Warning", "Save current parameters ?",
                                     QMessageBox.Cancel | QMessageBox.Ok)) == QMessageBox.Ok:
                self.save_struct()
        self.txt_name.setFocus()
        self.met_calc = self.cb_met_calc.itemData(self.cb_met_calc.currentIndex())
        param = self.param_meth_calc[self.met_calc]
        self.wgt_met = param['wgt'](*param['wgt_param'])
        self.sw_input.addWidget(self.wgt_met)
        self.sw_input.setCurrentIndex(1)
        self.sw_input.removeWidget(self.sw_input.widget(0))
        self.display_param_struct()

    def display_param_struct(self):
        sql = "SELECT var, value FROM {0}.struct_param " \
              "WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
        rows = self.mdb.run_query(sql, fetch=True)
        for param, val in rows:
            if param in self.wgt_met.dico_ctrl.keys():
                ctrls = self.wgt_met.dico_ctrl[param]
                for ctrl in ctrls:
                    ctrl_set_value(ctrl, val)

        for tab, param in self.wgt_met.dico_tab.items():
            # tab.setRowCount(0)
            t = param['type']
            sql = "SELECT id_elem FROM {0}.struct_elem " \
                  "WHERE id_config = {1} AND type = {2} ORDER BY id_elem".format(self.mdb.SCHEMA, self.id_struct, t)
            elems = self.mdb.run_query(sql, fetch=True)

            for r, elem in enumerate(elems):
                # tab.insertRow(r)
                for c, col in enumerate(param['col']):
                    sql = "SELECT value FROM {0}.struct_elem_param WHERE id_config = {1} " \
                          "AND id_elem = {2} and var = '{3}'".format(self.mdb.SCHEMA, self.id_struct,
                                                                     elem[0], col['fld'])
                    row = self.mdb.run_query(sql, fetch=True)
                    if len(row) > 0:
                        val = row[0][0]
                    else:
                        val = col['valdef']
                    if col['cb']:
                        cb = QComboBox()
                        fill_qcombobox(cb, col['cb'], val_def=int(val))
                        tab.setCellWidget(r, c, cb)
                    else:
                        itm = QTableWidgetItem()
                        itm.setData(0, val)
                        tab.setItem(r, c, itm)

    def accept_page(self):
        # save Info
        if self.save_struct():
            self.accept()
        else:
            self.reject_page()

    def save_struct(self):
        verif = True
        if verif:
            name = str(self.txt_name.text())
            meth = self.cb_met_calc.itemData(self.cb_met_calc.currentIndex())
            print(meth)
            active = self.cc_active.isChecked()
            sql = "UPDATE {0}.struct_config SET name = '{2}', method = {3}, active = {4} WHERE id = {1}" \
                .format(self.mdb.SCHEMA, self.id_struct, name, meth, active)
            self.mdb.execute(sql)

            sql = "DELETE FROM {0}.struct_param WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_elem WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_elem_param WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)

            for var, ctrls in self.wgt_met.dico_ctrl.items():
                val = float(ctrl_get_value(ctrls[0]))
                sql = "INSERT INTO {0}.struct_param (id_config, var, value) VALUES ({1}, '{2}', {3})" \
                    .format(self.mdb.SCHEMA, self.id_struct, var, val)
                self.mdb.execute(sql)

            for tab, param in self.wgt_met.dico_tab.items():
                type_elem = param['type']
                for r in range(tab.rowCount()):
                    id_elem = eval(param['id'].format(r))
                    sql = "INSERT INTO {0}.struct_elem (id_config, id_elem, type) VALUES ({1}, {2}, {3})" \
                        .format(self.mdb.SCHEMA, self.id_struct, id_elem, type_elem)
                    self.mdb.execute(sql)
                    for c, col in enumerate(param['col']):
                        var = col['fld']
                        if col['cb']:
                            cb = tab.cellWidget(r, c)
                            val = cb.itemData(cb.currentIndex())
                        else:
                            itm = tab.item(r, c)
                            val = itm.data(0)
                        sql = "INSERT INTO {0}.struct_elem_param (id_config, id_elem, var, value) " \
                              "VALUES ({1}, {2}, '{3}', {4})".format(self.mdb.SCHEMA, self.id_struct,
                                                                     id_elem, var, val)
                        self.mdb.execute(sql)

            self.clmeth.create_poly_elem(self.id_struct, self.typ_struct)
            self.clmeth.sav_meth(self.id_struct,meth)
            return True
        else:
            return False

    def reject_page(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Structure")
        self.reject()
