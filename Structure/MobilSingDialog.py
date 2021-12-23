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
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ..Graphic.GraphCommon import DraggableLegend, GraphCommon
from ..Function import data_to_float, str2bool
from .ClassTableStructure import ctrl_set_value, ctrl_get_value, fill_qcombobox


class ClassMobilSingDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.dico_meth1 = [{"id": 1, "name": 'TIME'},
                           {"id": 2, "name": 'ZVAR'}]
        self.id = 0
        self.cur_set = None
        self.filling_tab = False
        self.graph_edit = None

        self.ui = loadUi(os.path.join(self.mgis.masplugPath,
                                      'ui/structures/ui_mobil_sing.ui'), self)

        self.dico_ctrl = {'ZBAS': [self.sb_zbas],
                          'ZHAUT': [self.sb_zhaut],
                          'ZREG': [self.sb_zreg],
                          'VDESC': [self.sb_vd],
                          'VMONT': [self.sb_va],
                          'UNITVD': [self.cb_uvb],
                          'UNITVH': [self.cb_uvh]
                          }
        self.unitvd = 0
        self.unitvh = 0
        self.edit_type = 'table'  # 'var'
        self.name_cur = None

        fill_qcombobox(self.cb_method, [['1', 'Method 1'], ['2', 'Method 2']])
        self.cb_method.currentIndexChanged['QString'].connect(
            self.cb_change_meth)

        fill_qcombobox(self.cb_uvb, [[1, 'm/s'], [60, 'm/min'], [3600, 'm/h']])
        fill_qcombobox(self.cb_uvh, [[1, 'm/s'], [60, 'm/min'], [3600, 'm/h']])

        self.cb_uvb.currentIndexChanged.connect(self.cb_change_unitvd)
        self.cb_uvh.currentIndexChanged.connect(self.cb_change_unitvh)

        styled_item_delegate = QStyledItemDelegate()
        styled_item_delegate.setItemEditorFactory(ItemEditorFactory())
        self.ui.tab_sets.setItemDelegate(styled_item_delegate)

        self.bg_time = QButtonGroup()
        self.bg_time.addButton(self.rb_sec, 0)
        self.bg_time.addButton(self.rb_min, 1)
        self.bg_time.addButton(self.rb_hour, 2)
        self.bg_time.addButton(self.rb_day, 3)
        self.bg_time.buttonClicked[int].connect(self.chg_time)

        self.ui.b_OK_page2.accepted.connect(self.accept_page2)
        self.ui.b_OK_page2.rejected.connect(self.reject_page2)
        self.ui.b_OK_page1.accepted.connect(self.accept_page1)
        self.ui.b_OK_page1.rejected.connect(self.reject)
        self.ui.b_OK_page3.accepted.connect(self.accept_page3)
        self.ui.b_OK_page3.rejected.connect(self.reject_page3)
        self.ui.actionB_edit.triggered.connect(self.edit_set)

        self.ui.actionB_addLine.triggered.connect(self.new_time)
        self.ui.actionB_delLine.triggered.connect(self.delete_time)

        self.ui.actionB_import.triggered.connect(self.import_csv)
        self.ui.actionB_delete.triggered.connect(self.clear_tab)

        self.ui.tab_sets.sCut_del = QShortcut(QKeySequence("Del"), self)
        self.ui.tab_sets.sCut_del.activated.connect(self.short_cut_row_del)

        self.lst_sets.clicked.connect(self.select_list)

        self.init_ui()

    def cb_change_unitvd(self, evt):
        val = 0
        if evt == 0:
            if self.unitvd == 1:
                val = float(ctrl_get_value(self.sb_vd))
                val = val / 60
                ctrl_set_value(self.sb_vd, val)
            elif self.unitvd == 2:
                val = float(ctrl_get_value(self.sb_vd))
                val = val / 3600
                ctrl_set_value(self.sb_vd, val)
        elif evt == 1:
            if self.unitvd == 0:
                val = float(ctrl_get_value(self.sb_vd))
                val = val * 60.
                ctrl_set_value(self.sb_vd, val)
            elif self.unitvd == 2:
                val = float(ctrl_get_value(self.sb_vd))
                val = val / 60
                ctrl_set_value(self.sb_vd, val)
        elif evt == 2:
            if self.unitvd == 0:
                val = float(ctrl_get_value(self.sb_vd))
                val = val * 3600.
                ctrl_set_value(self.sb_vd, val)
            elif self.unitvd == 1:
                val = float(ctrl_get_value(self.sb_vd))
                val = val * 60.
                ctrl_set_value(self.sb_vd, val)
        else:
            pass

        self.unitvd = evt

    def cb_change_unitvh(self, evt):
        if evt == 0:
            if self.unitvh == 1:
                val = float(ctrl_get_value(self.sb_va))
                val = val / 60
                ctrl_set_value(self.sb_va, val)
            elif self.unitvh == 2:
                val = float(ctrl_get_value(self.sb_va))
                val = val / 3600
                ctrl_set_value(self.sb_va, val)
        elif evt == 1:
            if self.unitvh == 0:
                val = float(ctrl_get_value(self.sb_va))
                val = val * 60.
                ctrl_set_value(self.sb_va, val)
            elif self.unitvh == 2:
                val = float(ctrl_get_value(self.sb_va))
                val = val / 60
                ctrl_set_value(self.sb_va, val)
        elif evt == 2:
            if self.unitvh == 0:
                val = float(ctrl_get_value(self.sb_va))
                val = val * 3600.
                ctrl_set_value(self.sb_va, val)
            elif self.unitvh == 1:
                val = float(ctrl_get_value(self.sb_va))
                val = val * 60.
                ctrl_set_value(self.sb_va, val)
        else:
            pass

        self.unitvh = evt

    def cb_change_meth(self, text):
        if text == 'Method 1':
            self.edit_type = 'table'

        if text == 'Method 2':
            self.edit_type = 'var'
        else:
            self.edit_type = 'table'

        val = ctrl_get_value(self.cb_method)

        sql = "UPDATE {0}.weirs SET method_mob = '{1}' WHERE name = '{2}'" \
            .format(self.mdb.SCHEMA, val, self.name_cur)
        self.mdb.execute(sql)

    def select_list(self, itm):
        self.name_cur = self.ui.lst_sets.model().item(itm.row(), 1).text()
        self.ui.bt_edit.setDisabled(False)
        self.ui.cb_method.setDisabled(False)

        rows = self.mdb.select('weirs',
                               where="name = '{0}'".format(self.name_cur),
                               list_var=['method_mob', 'gid'])
        if rows:
            self.id = rows['gid'][0]
            ctrl_set_value(self.cb_method, rows['method_mob'][0])

    def import_csv(self):
        """ Import csv file"""
        nb_col = 2
        first_ligne = True
        if int(qVersion()[0]) < 5:  # qt4
            listf = QFileDialog.getOpenFileNames(None, 'File Selection',
                                                 self.mgis.repProject,
                                                 "File (*.txt *.csv )")

        else:  # qt5
            listf, _ = QFileDialog.getOpenFileNames(None, 'File Selection',
                                                    self.mgis.repProject,
                                                    "File (*.txt *.csv)")

        if listf:
            error = False
            self.filling_tab = True
            model = self.create_tab_model()
            r = 0

            filein = open(listf[0], "r")
            for num_ligne, ligne in enumerate(filein):
                if ligne[0] != '#':
                    liste = ligne.replace('\n', '').replace('\t', ' ').split(
                        ";")
                    if len(liste) == nb_col:
                        if first_ligne:
                            val = data_to_float(liste[0])
                            if val is not None:
                                self.mgis.add_info(
                                    "Error the value is not float.")
                            first_ligne = False
                        model.insertRow(r)
                        for c, val in enumerate(liste):
                            itm = QStandardItem()
                            itm.setData(data_to_float(val), 0)
                            if c == 0:
                                model.setItem(r, c, itm)
                            else:
                                model.setItem(r, c + 3, itm)
                        r += 1
                    else:
                        # print('e2')
                        error = True
                        break
            filein.close()
            self.filling_tab = False

            if not error:
                self.ui.tab_sets.setModel(model)
                self.update_courbe("all")
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info("Import failed ({})".format(listf[0]))

    def on_tab_data_change(self, itm):
        if itm.column() < 4:
            model = itm.model()
            if itm.data(0) or itm.data(0) == .0:
                if itm.column() == 0:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 1):
                        model.setItem(itm.row(), 1, QStandardItem())
                    model.item(itm.row(), 1).setData(itm.data(0) / 60., 0)
                    if not model.item(itm.row(), 2):
                        model.setItem(itm.row(), 2, QStandardItem())
                    model.item(itm.row(), 2).setData(itm.data(0) / 3600., 0)
                    if not model.item(itm.row(), 3):
                        model.setItem(itm.row(), 3, QStandardItem())
                    model.item(itm.row(), 3).setData(itm.data(0) / 86400., 0)
                    model.blockSignals(False)
                elif itm.column() == 1:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 0):
                        model.setItem(itm.row(), 0, QStandardItem())
                    model.item(itm.row(), 0).setData(itm.data(0) * 60., 0)
                    if not model.item(itm.row(), 2):
                        model.setItem(itm.row(), 2, QStandardItem())
                    model.item(itm.row(), 2).setData(itm.data(0) / 60., 0)
                    if not model.item(itm.row(), 3):
                        model.setItem(itm.row(), 3, QStandardItem())
                    model.item(itm.row(), 3).setData(itm.data(0) / 1440., 0)
                    model.blockSignals(False)
                elif itm.column() == 2:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 0):
                        model.setItem(itm.row(), 0, QStandardItem())
                    model.item(itm.row(), 0).setData(itm.data(0) * 3600., 0)
                    if not model.item(itm.row(), 1):
                        model.setItem(itm.row(), 1, QStandardItem())
                    model.item(itm.row(), 1).setData(itm.data(0) * 60., 0)
                    if not model.item(itm.row(), 3):
                        model.setItem(itm.row(), 3, QStandardItem())
                    model.item(itm.row(), 3).setData(itm.data(0) / 24., 0)
                    model.blockSignals(False)
                elif itm.column() == 3:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 0):
                        model.setItem(itm.row(), 0, QStandardItem())
                    model.item(itm.row(), 0).setData(itm.data(0) * 86400., 0)
                    if not model.item(itm.row(), 1):
                        model.setItem(itm.row(), 1, QStandardItem())
                    model.item(itm.row(), 1).setData(itm.data(0) * 1440., 0)
                    if not model.item(itm.row(), 2):
                        model.setItem(itm.row(), 2, QStandardItem())
                    model.item(itm.row(), 2).setData(itm.data(0) * 24., 0)
                    model.blockSignals(False)

            if not self.filling_tab:
                model.sort(0)
                idx = itm.index()
                self.ui.tab_sets.scrollTo(idx, 0)
                self.update_courbe("all")
        elif itm.column() == 4:
            if not self.filling_tab:
                idx = itm.index()
                self.update_courbe([idx.column() - 4])

    def create_tab_model(self):
        """ create table"""
        model = QStandardItemModel()
        model.insertColumns(0, 5)
        for c in range(4):
            model.setHeaderData(c, 1, 'time', 0)

        model.setHeaderData(4, 1, "Z", 0)

        model.itemChanged.connect(self.on_tab_data_change)
        return model

    def accept_page1(self):
        self.accept()

    def accept_page2(self):

        try:
            recs = []

            for num in range(self.ui.tab_sets.model().rowCount()):
                recs.append([self.id, num, 'TIME',
                             self.ui.tab_sets.model().item(num, 0).data(0)])
                recs.append([self.id, num, 'ZVAR',
                             self.ui.tab_sets.model().item(num, 4).data(0)])

            rows = self.mdb.select('weirs_mob_val',
                                   where="id_weirs = {0}".format(self.id),
                                   list_var=['name_var'])

            if rows:
                if 'ZVAR' in rows['name_var']:
                    sql = "DELETE FROM {0}.weirs_mob_val " \
                          "WHERE id_weirs = {1} AND name_var='ZVAR';\n".format(
                        self.mdb.SCHEMA, self.id)

                    sql += "DELETE FROM {0}.weirs_mob_val " \
                           "WHERE id_weirs = {1} AND name_var='TIME'".format(
                        self.mdb.SCHEMA, self.id)

                    self.mdb.execute(sql)

            sql = "INSERT INTO {0}.weirs_mob_val (id_weirs, id_order, name_var, value) VALUES (%s, %s, %s, %s)".format(
                self.mdb.SCHEMA)

            self.mdb.run_query(sql, many=True, list_many=recs)

            self.ui.weirs_pages.setCurrentIndex(0)
        except:
            self.reject_page2()
            self.mgis.add_info("Cancel of gate information")

    def accept_page3(self):
        try:
            for var, ctrls in self.dico_ctrl.items():
                val = float(ctrl_get_value(ctrls[0]))
                if var == 'UNITVD':
                    val = int(ctrl_get_value(self.dico_ctrl['UNITVD'][0]))
                elif var == 'UNITVH':
                    val = int(ctrl_get_value(self.dico_ctrl['UNITVH'][0]))
                elif var == 'VDESC':
                    fact_t = int(ctrl_get_value(self.dico_ctrl['UNITVD'][0]))
                    val = val / fact_t
                elif var == 'VMONT':
                    fact_t = int(ctrl_get_value(self.dico_ctrl['UNITVH'][0]))
                    val = val / fact_t
                else:
                    val = float(ctrl_get_value(ctrls[0]))

                sql = "SELECT * FROM {0}.weirs_mob_val WHERE id_weirs= {1} AND  name_var = '{2}' " \
                    .format(self.mdb.SCHEMA, self.id, var)
                row = self.mdb.run_query(sql, fetch=True)

                if len(row) > 0:
                    sql = "UPDATE {0}.weirs_mob_val SET value = {3} WHERE id_weirs = {1} AND  name_var = '{2}'" \
                        .format(self.mdb.SCHEMA, self.id, var, val)
                    self.mdb.execute(sql)
                else:

                    sql = "INSERT INTO {0}.weirs_mob_val (id_weirs, id_order, name_var, value)" \
                          " VALUES ({1}, {2}, '{3}',{4})" \
                        .format(self.mdb.SCHEMA, self.id, 0, var, val)
                    self.mdb.execute(sql)

                self.ui.weirs_pages.setCurrentIndex(0)
        except:
            self.reject_page3()
            self.mgis.add_info("Cancel of gate information")

    def reject_page2(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Weirs tab")
        self.ui.weirs_pages.setCurrentIndex(0)

    def reject_page3(self):

        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Weirs tab")
        self.ui.weirs_pages.setCurrentIndex(0)

    def delete_time(self):
        if self.ui.tab_sets.selectedIndexes():
            rows = [idx.row() for idx in self.ui.tab_sets.selectedIndexes()]
            rows = list(set(rows))
            rows.sort(reverse=True)
            for row in rows:
                model = self.ui.tab_sets.model()
                model.removeRow(row)
            self.update_courbe("all")

    def chg_time(self, v):
        unit = ['s', 'min', 'h', 'day']
        for i in range(4):
            if i == v:
                self.ui.tab_sets.setColumnHidden(i, False)
            else:
                self.ui.tab_sets.setColumnHidden(i, True)

        if not self.filling_tab:
            self.graph_edit.maj_unit_x(unit[v])
            self.update_courbe("all")

    def new_time(self):
        self.filling_tab = True

        model = self.ui.tab_sets.model()

        r = model.rowCount()
        model.insertRow(r)
        itm = QStandardItem()
        if r == 0:
            val = 0.0
        elif r == 1:
            val = model.item(r - 1).data(0) + 1
        else:
            val = 2 * model.item(r - 1).data(0) - model.item(r - 2).data(0)
        itm.setData(val, 0)
        model.setItem(r, 0, itm)
        for c in range(4, model.columnCount()):
            model.setItem(r, c, QStandardItem())
        self.ui.tab_sets.scrollToBottom()
        self.filling_tab = False
        self.update_courbe("all")

    def sel_config_def(self, itm):
        """
        Select configuration
        """
        self.ui.lst_sets.model().blockSignals(True)
        self.ui.lst_sets.model().blockSignals(False)
        # get value lst_sets
        name = str(self.ui.lst_sets.model().item(itm.row(), 1).text())

        if itm.checkState() == 2:
            sql = "UPDATE {0}.weirs SET active_mob = 't' WHERE name = '{1}'".format(
                self.mdb.SCHEMA, name)
            self.mdb.run_query(sql)
        else:
            sql = "UPDATE {0}.weirs SET active_mob = 'f' WHERE name = '{1}'".format(
                self.mdb.SCHEMA, name)
            self.mdb.run_query(sql)

    def init_ui(self):
        """initialisation gui"""
        self.delete_useless_data()
        self.ui.weirs_pages.setCurrentIndex(0)
        self.graph_edit = GraphMobSing(self.mgis, self.ui.lay_graph_edit,
                                       self.id, self.dico_meth1)
        self.fill_lst_conf()
        self.ui.bt_edit.setDisabled(True)
        self.ui.cb_method.setDisabled(True)

    def delete_useless_data(self):
        sql = "DELETE  FROM {0}.weirs_mob_val WHERE id_weirs IN " \
              "(SELECT DISTINCT id_weirs FROM {0}.weirs_mob_val " \
              "where id_weirs not in (SELECT gid FROM {0}.weirs));"
        self.mdb.run_query(sql.format(self.mdb.SCHEMA))

    def fill_lst_conf(self, id=None):
        """ fill configuration list"""
        model = QStandardItemModel()
        model.setColumnCount(2)
        self.ui.lst_sets.setModel(model)
        self.ui.lst_sets.setModelColumn(1)

        sql = "SELECT active_mob,name FROM {0}.weirs WHERE active='t' ORDER BY name".format(
            self.mdb.SCHEMA)
        rows = self.mdb.run_query(sql, fetch=True)

        if rows is not None:
            for i, row in enumerate(rows):
                for j, field in enumerate(row):
                    if j != 2:
                        new_itm = QStandardItem(str(row[j]))
                        new_itm.setEditable(False)
                        if j == 1:
                            new_itm.setCheckable(True)
                            if not row[0]:
                                new_itm.setCheckState(0)
                            elif row[0]:
                                new_itm.setCheckState(2)
                        self.ui.lst_sets.model().setItem(i, j, new_itm)

            self.ui.lst_sets.model().itemChanged.connect(self.sel_config_def)

        if id:
            for r in range(self.ui.lst_sets.model().rowCount()):
                if str(self.ui.lst_sets.model().item(r, 0).text()) == str(id):
                    self.ui.lst_sets.setCurrentIndex(
                        self.ui.lst_sets.model().item(r, 1).index())
                    break

    def clear_tab(self):
        model = self.ui.tab_sets.model()
        list_id = sorted(range(model.rowCount()), reverse=True)
        for num in list_id:
            model.removeRow(num)
        self.update_courbe("all")

    def short_cut_row_del(self):
        """
        cut row
        """
        if self.ui.tab_sets.hasFocus():
            cols = []
            model = self.ui.tab_sets.model()
            selection = self.ui.tab_sets.selectedIndexes()
            for idx in selection:
                if idx.column() > 3:
                    model.item(idx.row(), idx.column()).setData(None, 0)
                    cols.append(idx.column() - 4)
            cols = list(set(cols))
            self.update_courbe(cols)

    def edit_set(self):
        if self.ui.lst_sets.selectedIndexes():
            l = self.ui.lst_sets.selectedIndexes()[0].row()
            self.cur_set = self.ui.lst_sets.model().item(l, 1).text()

            if self.edit_type == 'table':
                self.fill_tab_sets()
                self.ui.weirs_pages.setCurrentIndex(1)
                self.graph_edit.init_graph(self.cur_set)
            else:
                self.display_method2()
                self.ui.weirs_pages.setCurrentIndex(2)

    def display_method2(self):
        sql = "SELECT  name_var, value FROM {0}.weirs_mob_val " \
              "WHERE id_weirs = {1} ".format(self.mdb.SCHEMA, self.id)

        rows = self.mdb.run_query(sql, fetch=True)
        if len(rows) > 0:
            dico = {}
            for param, val in rows:
                dico[param] = val
            for ctrl in self.dico_ctrl['UNITVD'] + self.dico_ctrl['UNITVH']:
                ctrl.blockSignals(True)

            for param in dico.keys():
                if param in self.dico_ctrl.keys():
                    ctrls = self.dico_ctrl[param]
                    if param == 'VDESC':
                        if 'UNITVD' in dico.keys():
                            val = dico[param] * dico['UNITVD']
                        else:
                            val = dico[param]
                    elif param == 'VMONT':
                        if 'UNITVH' in dico.keys():
                            val = dico[param] * dico['UNITVH']
                        else:
                            val = dico[param]
                    else:
                        val = dico[param]

                    for ctrl in ctrls:
                        ctrl_set_value(ctrl, val)
            for ctrl in self.dico_ctrl['UNITVD'] + self.dico_ctrl['UNITVH']:
                ctrl.blockSignals(False)
            if 'UNITVH' in dico.keys():
                if dico['UNITVH'] == 3600:
                    self.unitvh = 2
                elif dico['UNITVH'] == 60:
                    self.unitvh = 1
                else:
                    self.unitvh = 0
            if 'UNITVD' in dico.keys():
                if dico['UNITVD'] == 3600:
                    self.unitvd = 2
                elif dico['UNITVD'] == 60:
                    self.unitvd = 1
                else:
                    self.unitvd = 0

        else:
            # default value TODO
            for param in self.dico_ctrl.keys():
                ctrls = self.dico_ctrl[param]
                for ctrl in ctrls:
                    ctrl_set_value(ctrl, 0.0)

    def fill_tab_sets(self):
        """ fill table"""
        self.filling_tab = True
        self.ui.tab_sets.setModel(self.create_tab_model())
        model = self.ui.tab_sets.model()

        if self.cur_set != -1:
            c = 0
            for var in self.dico_meth1:
                sql = "SELECT value FROM {0}.weirs_mob_val " \
                      "WHERE id_weirs = {1} and name_var = '{2}' " \
                      "ORDER BY id_order".format(self.mdb.SCHEMA, self.id,
                                                 var["name"])
                rows = self.mdb.run_query(sql, fetch=True)

                if var['id'] == 1:
                    model.insertRows(0, len(rows))
                    for r, row in enumerate(rows):
                        itm = QStandardItem()
                        itm.setData(row[0] / 1., 0)
                        model.setItem(r, c, itm)
                    c = 4
                else:
                    for r, row in enumerate(rows):
                        itm = QStandardItem()
                        itm.setData(row[0], 0)
                        model.setItem(r, c, itm)

        self.filling_tab = False
        self.rb_sec.click()

    def update_courbe(self, courbes):
        data = {}
        if courbes == "all":
            courbes = range(self.ui.tab_sets.model().columnCount() - 4)

        col_x = self.bg_time.checkedId()
        lx = []
        for r in range(self.ui.tab_sets.model().rowCount()):
            lx.append(self.ui.tab_sets.model().item(r, col_x).data(0))

        ly = []
        for r in range(self.ui.tab_sets.model().rowCount()):
            ly.append(self.ui.tab_sets.model().item(r, 4).data(0))
        data[0] = {"x": lx, "y": ly}

        self.graph_edit.maj_courbes(data)


class ItemEditorFactory(QItemEditorFactory):
    # http://doc.qt.io/qt-5/qstyleditemdelegate.html#subclassing-qstyleditemdelegate
    #     It is possible for a custom delegate to provide editors
    # without the use of an editor item factory. In this case, the following virtual
    # functions must be reimplemented:
    def __init__(self):
        QItemEditorFactory.__init__(self)

    def createEditor(self, user_type, parent):
        if user_type == QVariant.Double or user_type == 0:
            double_spin_box = QDoubleSpinBox(parent)
            double_spin_box.setDecimals(10)
            double_spin_box.setMinimum(
                -1000000000.)  # The default maximum value is 99.99.
            double_spin_box.setMaximum(
                1000000000.)  # The default maximum value is 99.99.
            return double_spin_box
        else:
            return ItemEditorFactory.createEditor(user_type, parent)


class MySpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(MySpinBox, self).__init__(parent)

        # def textFromValue(self, value):
        #     print ("value : {}".format(value))
        #     if (value == None):
        #         return str("")
        #     else:
        #         return str(value)
        #
        # def valueFromText(self, text):
        #     print ("txt : {}".format(text))
        #     if (text.toLower() == str("")):
        #         return None
        #     else:
        #         return text.toFloat()
        #
        # def validate(self, text, pos):
        #     return QValidator.Acceptable


class GraphMobSing(GraphCommon):
    """class Dialog """

    def __init__(self, mgis=None, lay=None, id_weirs=None, lst_var=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.id = id_weirs
        self.lst_var = lst_var
        self.init_ui_common_p()
        self.courbe = {}
        self.axes = None
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        self.courbe, = self.axes.plot([], [], zorder=100, label='Z')
        self.courbes.append(self.courbe)

        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.init_legende()

    def init_graph(self, all_vis=False):
        self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        lst_graph = []
        for var in self.lst_var:

            sql = "SELECT value FROM {0}.weirs_mob_val " \
                  "WHERE id_weirs = {1} and name_var = '{2}' " \
                  "ORDER BY id_order".format(self.mdb.SCHEMA, self.id,
                                             var["name"])

            rows = self.mdb.run_query(sql, fetch=True)

            if len(rows) > 0:
                lst_graph.append(rows[0])

        if len(lst_graph) > 1:
            self.courbes.set_data(lst_graph[0], lst_graph[1])

            if all_vis:
                self.courbes.set_visible(True)
                leglines.set_alpha(1.0)

            self.maj_limites()
