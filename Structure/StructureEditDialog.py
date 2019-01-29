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
        self.tbst = ClassTableStructure(self.mgis, self.mdb)

        self.id_struct = id_struct
        self.lst_meth_calc = []
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_structure_edit.ui'), self)

        ## Gestion des ctrl pour la partie commune
        self.cb_met_calc.currentIndexChanged[int].connect(self.change_met_calc)
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)

        ## Gestion des ctrl pour le form 0 - Pont cadre - Methode Bradley
        self.cb00_met_crea.currentIndexChanged[int].connect(self.sw00_elem.setCurrentIndex)
        self.sb000_nb_trav.valueChanged.connect(self.change_ntrav_bradley)
        fill_qcombobox(self.cb00_orient_mur, [[30, '30°'], [45, '45°'], [60, '60°'], [90, '90°']])
        fill_qcombobox(self.cb00_pente_tal, [[0, '1/1'], [1, '1.5/1'], [2, '2/1']])
        fill_qcombobox(self.cb00_met_crea, [[m, self.tbst.dico_meth_draw[m]]
                                            for m in self.tbst.dico_struc_typ['PC']['meth_draw'][0]])
        self.gb00_form_cul = QButtonGroup()
        self.gb00_form_cul.buttonClicked[int].connect(self.change_opt_culee)
        self.gb00_form_cul.addButton(self.rb00_form_cul0, 0)
        self.rb00_form_cul0.setIcon(QIcon(os.path.join(self.mgis.masplugPath, 'Structure/images/type1.png')))
        self.gb00_form_cul.addButton(self.rb00_form_cul1, 1)
        self.rb00_form_cul1.setIcon(QIcon(os.path.join(self.mgis.masplugPath, 'Structure/images/type2.png')))
        self.gb00_form_cul.addButton(self.rb00_form_cul2, 2)
        self.rb00_form_cul2.setIcon(QIcon(os.path.join(self.mgis.masplugPath, 'Structure/images/type3.png')))


        ## Gestion des ctrl pour le form 1 - Pont cadre - Methode test
        self.cb01_met_crea.currentIndexChanged[int].connect(self.sw01_elem.setCurrentIndex)
        fill_qcombobox(self.cb01_test, [[0, '1/1'], [1, '1.5/1'], [2, '2/1']])
        fill_qcombobox(self.cb01_met_crea, [[m, self.tbst.dico_meth_draw[m]]
                                            for m in self.tbst.dico_struc_typ['PC']['meth_draw'][1]])

        if id_struct:
            sql = "SELECT name, type, method, active FROM {0}.struct_config " \
                  "WHERE id = {1}".format(self.mdb.SCHEMA, self.id_struct)
            rows = self.mdb.run_query(sql, fetch=True)
            self.typ_struct = rows[0][1]
            self.init_controls()

            for m in self.tbst.dico_struc_typ[self.typ_struct]['meth_calc']:
                self.lst_meth_calc.append([m, self.tbst.dico_meth_calc[m]])

            self.lbl_type.setText(self.tbst.dico_struc_typ[self.typ_struct]['name'])
            self.txt_name.setText(rows[0][0])
            if rows[0][3]:
                self.cc_active.setCheckState(2)
            else:
                self.cc_active.setCheckState(0)
            fill_qcombobox(self.cb_met_calc, self.lst_meth_calc, rows[0][2])

            self.display_param_struct()

    def init_controls(self):
        self.dico_wdg_calc = {'PC': {0: 0, 4: 1, 5: 0}}

        self.lnk_ctrl_var = {'PC': {'ZTOPTAB': [self.dsb00_cote_tab, self.dsb01_cote_tab],
                                    'EPAITAB': [self.dsb00_epai_tab, self.dsb01_epai_tab],
                                    'BIAIOUV': [self.dsb00_biai_ouv],
                                    'BIAICUL': [self.dsb00_biai_cul],
                                    'FORMCUL': [self.gb00_form_cul],
                                    'ORIENTM': [self.cb00_orient_mur],
                                    'PENTTAL': [self.cb00_pente_tal, self.cb01_test],
                                    'METBRAD': [self.cb00_met_crea],
                                    'METTEST': [self.cb01_met_crea],
                                    'NBTRAVE': [self.sb000_nb_trav, self.sb010_nb_trav]}
                             }
        for ctrls in self.lnk_ctrl_var[self.typ_struct].values():
            for ctrl in ctrls:
                if ctrl.metaObject().className() == 'QLineEdit':
                    ctrl.editingFinished.connect(self.ctrl_edited)
                if ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
                    ctrl.valueChanged.connect(self.ctrl_edited)
                if ctrl.metaObject().className() == 'QDateTimeEdit':
                    ctrl.dateTimeChanged.connect(self.ctrl_edited)
                if ctrl.metaObject().className() == 'QComboBox':
                    ctrl.currentIndexChanged.connect(self.ctrl_edited)
                if ctrl.metaObject().className() == 'QCheckBox':
                    ctrl.stateChanged.connect(self.ctrl_edited)
                if ctrl.metaObject().className() == 'QButtonGroup':
                    ctrl.buttonClicked.connect(self.ctrl_edited)

        self.dico_tab_elem = {'PC': {self.tab000_trav: {'type': 0,
                                                        'id': '({}*2) + 1',
                                                        'col': [{'fld': 'LARGTRA', 'cb': None, 'valdef': 1.}]},
                                     self.tab000_pile: {'type': 1,
                                                        'id': '({}*2) + 2',
                                                        'col': [{'fld': 'FORMPIL', 'cb': [[f, 'Forme {}'.format(f)] for f in range(1, 9)], 'valdef': 1},
                                                                {'fld': 'LARGPIL', 'cb': None, 'valdef': 1.},
                                                                {'fld': 'BIAIPIL', 'cb': None, 'valdef': 0.}]}
                                     }
                              }

    def ctrl_edited(self):
        src = self.sender()
        val = ctrl_get_value(src)
        for var, ctrls in self.lnk_ctrl_var[self.typ_struct].items():
            if src in ctrls:
                for ctrl in ctrls:
                    if ctrl != src:
                        ctrl_set_value(ctrl, val)

    def display_param_struct(self):
        sql = "SELECT var, value FROM {0}.struct_param " \
              "WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
        rows = self.mdb.run_query(sql, fetch=True)
        for param, val in rows:
            ctrls = self.lnk_ctrl_var[self.typ_struct][param]
            for ctrl in ctrls:
                ctrl_set_value(ctrl, val)

        for tab, param in self.dico_tab_elem[self.typ_struct].items():
            tab.setRowCount(0)
            t = param['type']
            sql = "SELECT id_elem FROM {0}.struct_elem " \
                  "WHERE id_config = {1} AND type = {2} ORDER BY id_elem".format(self.mdb.SCHEMA, self.id_struct, t)
            elems = self.mdb.run_query(sql, fetch=True)

            for r, elem in enumerate(elems):
                tab.insertRow(r)
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
                        fill_qcombobox(cb, col['cb'], int(val))
                        tab.setCellWidget(r, c, cb)
                    else:
                        itm = QTableWidgetItem()
                        itm.setData(0, val)
                        tab.setItem(r, c, itm)

    def change_met_calc(self, idx):
        self.met_calc = self.cb_met_calc.itemData(self.cb_met_calc.currentIndex())
        idx_wgt_calc = self.dico_wdg_calc[self.typ_struct][self.met_calc]
        self.sw_struct.setCurrentIndex(idx_wgt_calc)

    def change_ntrav_bradley(self, v):
        if v < self.tab000_trav.rowCount():
            self.tab000_trav.setRowCount(v)
            self.tab000_pile.setRowCount(v - 1)
        else:
            self.insert_elem(self.tab000_trav, v - 1)
            self.insert_elem(self.tab000_pile, v - 2)

    def change_opt_culee(self, idx):
        if idx == 0:
            self.frm00_orient_mur.hide()
            self.frm00_pente_tal.hide()
        elif idx == 1:
            self.frm00_orient_mur.show()
            self.frm00_pente_tal.hide()
        elif idx == 2:
            self.frm00_orient_mur.hide()
            self.frm00_pente_tal.show()

    def insert_elem(self, tab, row):
        tab.insertRow(row)
        for c, col in enumerate(self.dico_tab_elem[self.typ_struct][tab]['col']):
            if col['cb']:
                cb = QComboBox()
                fill_qcombobox(cb, col['cb'], int(col['valdef']))
                tab.setCellWidget(row, c, cb)
            else:
                itm = QTableWidgetItem()
                itm.setData(0, col['valdef'])
                tab.setItem(row, c, itm)

    def accept_page(self):
        # save Info
        verif = True
        if verif:
            name = str(self.txt_name.text())
            meth = self.cb_met_calc.itemData(self.cb_met_calc.currentIndex())
            active = self.cc_active.isChecked()
            sql = "UPDATE {0}.struct_config SET name = '{2}', method = {3}, active = {4} WHERE id = {1}"\
                .format(self.mdb.SCHEMA, self.id_struct, name, meth, active)
            self.mdb.execute(sql)

            sql = "DELETE FROM {0}.struct_param WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_elem WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_elem_param WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)

            for var, ctrls in self.lnk_ctrl_var[self.typ_struct].items():
                val = float(ctrl_get_value(ctrls[0]))
                sql = "INSERT INTO {0}.struct_param (id_config, var, value) VALUES ({1}, '{2}', {3})"\
                    .format(self.mdb.SCHEMA, self.id_struct, var, val)
                self.mdb.execute(sql)

            id_elem = 0
            for tab, param in self.dico_tab_elem[self.typ_struct].items():
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
        else:
            self.reject_page()
        self.accept()

    def reject_page(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Structure")
        self.reject()

def ctrl_set_value(ctrl, val):
    if ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
        ctrl.setValue(val)
    elif ctrl.metaObject().className() == 'QComboBox':
        ctrl.setCurrentIndex(ctrl.findData(int(val)))
    elif ctrl.metaObject().className() == 'QCheckBox':
        ctrl.setCheckState(Qt.CheckState(val))
    elif ctrl.metaObject().className() == 'QButtonGroup':
        ctrl.button(int(val)).click()

def ctrl_get_value(ctrl):
    val = None
    if ctrl.metaObject().className() == 'QLineEdit':
        val = ctrl.text()
    elif ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
        val = ctrl.value()
    elif ctrl.metaObject().className() == 'QDateTimeEdit':
        val = ctrl.dateTime().toString('yyyy-MM-dd HH:mm:ss')
    elif ctrl.metaObject().className() == 'QComboBox':
        val = int(ctrl.itemData(ctrl.currentIndex()))
    elif ctrl.metaObject().className() == 'QCheckBox':
        val = ctrl.checkState()
    elif ctrl.metaObject().className() == 'QButtonGroup':
        val = ctrl.checkedId()
    return val


def fill_qcombobox(cb, lst, val_def=None):
    cb.blockSignals(True)
    cb.clear()

    if val_def != None:
        if lst[0][0] == val_def:
            cb.blockSignals(False)
    else:
        cb.blockSignals(False)

    for elem in lst:
        cb.addItem(elem[1], elem[0])

    if val_def != None:
        if lst[0][0] != val_def:
            cb.blockSignals(False)
            cb.setCurrentIndex(cb.findData(val_def))