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
import csv
import io
from datetime import timedelta

import numpy as np
from matplotlib.dates import date2num
from pandas import pivot_table, DataFrame
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# from .table_WQ import table_WQ
from .Function import data_to_float, data_to_date
from .Graphic.GraphHydro import GraphHydroLaw

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
    from qgis.PyQt.QtWidgets import *

dico_typ_law = {1: {'name': 'Hydrograph Q(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'flowrate', 'code': 'flowrate'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
                    'geom': {'extremities': [1], 'weirs': False,
                             'lateral_inflows': True, 'lateral_weirs': False},
                    'xIsTime': True},
                2: {'name': 'Limnigraph Z(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'level', 'code': 'z'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
                    'geom': {'extremities': [2], 'weirs': [5],
                             'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': True},
                3: {'name': 'Limnihydrograph Z,Q(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'level', 'code': 'z'},
                            {'name': 'flowrate', 'code': 'flowrate'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1, 2], 'tit': 'Various',
                                    'unit': ''}},
                    'geom': {'extremities': [8], 'weirs': False,
                             'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': True},
                4: {'name': 'Rating Curve Z = f(Q)',
                    'var': [{'name': 'flowrate', 'code': 'flowrate'},
                            {'name': 'level', 'code': 'z'}],
                    'graph': {'x': {'var': 0, 'tit': 'Q', 'unit': 'm3/s'},
                              'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
                    'geom': {'extremities': [3, 5], 'weirs': [2],
                             'lateral_inflows': False, 'lateral_weirs': [2]},
                    'xIsTime': False},
                5: {'name': 'Rating Curve Q = f(Z)',
                    'var': [{'name': 'level', 'code': 'z'},
                            {'name': 'flowrate', 'code': 'flowrate'}],
                    'graph': {'x': {'var': 0, 'tit': 'Z', 'unit': 'm'},
                              'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
                    'geom': {'extremities': [4], 'weirs': [6, 7],
                             'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': False},
                6: {'name': 'Weir Zam = f(Q, Zav)',
                    'var': [
                        {'name': 'flowrate', 'code': 'flowrate', 'leg': 'Q'},
                        {'name': 'downstream level', 'code': 'z_downstream',
                         'leg': 'Zdown'},
                        {'name': 'upstream level', 'code': 'z_upstream'}],
                    'graph': {'x': {'var': None, 'tit': None, 'unit': None},
                              'y': {'var': [2], 'tit': 'Zup', 'unit': 'm'}},
                    'geom': {'extremities': [0, 6], 'weirs': [1],
                             'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': False},
                7: {'name': 'Floodgate Zinf, Zsup = f(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'lower level', 'code': 'z_lower'},
                            {'name': 'upper level', 'code': 'z_up'}],

                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1, 2], 'tit': 'Z', 'unit': 'm'}},
                    'geom': {'extremities': [7], 'weirs': [8],
                             'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': True},
                }


class ClassHydroLawsDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.cur_law = None
        self.param_law = None

        self.filling_tab = False
        self.reorder_tab = False

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_hydro_laws.ui'), self)

        # PAGE 1

        self.tree_laws.setColumnWidth(0, 175)
        self.tree_laws.setColumnWidth(1, 100)
        self.tree_laws.setColumnWidth(2, 40)
        self.tree_laws.itemSelectionChanged.connect(self.selected_law_changed)
        self.cb_graph_opt.currentIndexChanged.connect(self.display_graph_home)

        self.ui.actionB_new.triggered.connect(self.new_law)
        self.ui.actionB_edit.triggered.connect(self.edit_law)
        self.ui.actionB_delete.triggered.connect(self.delete_law)
        self.ui.b_OK_page1.accepted.connect(self.reject)

        # PAGE 2

        styled_item_delegate = QStyledItemDelegate()
        styled_item_delegate.setItemEditorFactory(ItemEditorFactory())
        self.ui.tab_sets.setItemDelegate(styled_item_delegate)
        self.ui.tab_sets.sCut_del = QShortcut(QKeySequence("Del"), self)
        self.ui.tab_sets.sCut_del.activated.connect(self.short_cut_row_del)

        self.cc_date_end_auto.toggled.connect(self.enable_date_end)
        self.ui.de_start.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.ui.de_end.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.ui.de_start.dateTimeChanged.connect(self.change_date_start)
        self.ui.de_end.dateTimeChanged.connect(self.change_date_end)

        self.bg_time = QButtonGroup()
        self.bg_time.addButton(self.rb_sec, 0)
        self.bg_time.addButton(self.rb_min, 1)
        self.bg_time.addButton(self.rb_hour, 2)
        self.bg_time.addButton(self.rb_day, 3)
        self.bg_time.addButton(self.rb_date, 4)
        self.bg_time.buttonClicked[int].connect(self.chg_time)

        self.bg_abs = QButtonGroup()
        self.bg_abs.addButton(self.rb_abs_q, 0)
        self.bg_abs.addButton(self.rb_abs_z, 1)
        self.bg_abs.buttonClicked[int].connect(self.chg_abs_weir_zam)

        self.ui.actionB_import.triggered.connect(self.import_law)
        self.ui.actionB_addLine.triggered.connect(self.new_time)
        self.ui.actionB_delLine.triggered.connect(self.delete_time)
        self.b_add_q.clicked.connect(self.new_q)
        self.b_delete_q.clicked.connect(self.delete_q)
        self.b_add_zdown.clicked.connect(self.new_z_av)
        self.b_delete_zdown.clicked.connect(self.delete_z_av)
        self.ui.b_OK_page2.accepted.connect(self.accept_page2)
        self.ui.b_OK_page2.rejected.connect(self.reject_page2)

        self.init_ui()

    def init_ui(self):
        """
        initialize GUI
        :return:
        """
        self.ui.laws_pages.setCurrentIndex(0)
        self.graph_home = GraphHydroLaw(self.mgis, self.ui.lay_graph_home)
        self.graph_edit = GraphHydroLaw(self.mgis, self.ui.lay_graph_edit)
        self.fill_tree_laws()

    ######################################################################
    #
    #                           CONTROLS PAGE 1
    #
    ######################################################################

    def fill_tree_laws(self, id=None):
        """
        fill list laws
        :param id:  id law
        :return:
        """
        self.tree_laws.clear()
        for id_type, elem in dico_typ_law.items():
            sql = "SELECT id, name, geom_obj, active, comment, starttime FROM {0}.law_config " \
                  "WHERE id_law_type = '{1}' " \
                  "ORDER BY name".format(self.mdb.SCHEMA, id_type)
            rows = self.mdb.run_query(sql, fetch=True)
            if rows:
                typ_itm = QTreeWidgetItem()
                typ_itm.setFlags(Qt.ItemIsEnabled)
                typ_itm.setData(0, 32, id_type)
                typ_itm.setText(0, elem['name'])
                self.tree_laws.addTopLevelItem(typ_itm)

                for row in rows:
                    law_itm = QTreeWidgetItem()
                    law_itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    law_itm.setData(0, 32, int(row[0]))
                    law_itm.setText(0, row[1])
                    law_itm.setData(1, 32, row[5])
                    law_itm.setText(1, str(row[2])) if row[
                                                           2] is not None else law_itm.setText(
                        1, '')
                    law_itm.setText(2, str(row[3]))
                    law_itm.setText(3, str(row[4])) if row[
                                                           4] is not None else law_itm.setText(
                        3, '')
                    typ_itm.addChild(law_itm)

                typ_itm.setExpanded(True)

        if id:
            for p in range(self.tree_laws.topLevelItemCount()):
                for c in range(self.tree_laws.topLevelItem(p).childCount()):
                    itm = self.tree_laws.topLevelItem(p).child(c)
                    if itm.data(0, 32) == id:
                        self.tree_laws.setCurrentItem(itm, 0)
                        break
        else:
            self.selected_law_changed()

    def selected_law_changed(self):
        """
        action when select law
        :return:
        """
        self.update_cb_graph_opt()
        self.display_graph_home()

    def update_cb_graph_opt(self):
        """
        update graph
        :return:
        """
        cur_opt = self.cb_graph_opt.currentData()
        self.cb_graph_opt.blockSignals(True)
        self.cb_graph_opt.clear()

        if self.tree_laws.selectedItems():
            itm = self.tree_laws.selectedItems()[0]
            typ_law = itm.parent().data(0, 32)
            param_law = dico_typ_law[typ_law]

            if typ_law == 6:
                self.cb_graph_opt.addItem("Flowrate", 0)
                self.cb_graph_opt.addItem("Downstream level", 1)
                idx = self.cb_graph_opt.findData(cur_opt)
                if idx != -1:
                    self.cb_graph_opt.setCurrentIndex(idx)
                self.frm_graph_opt.show()
            else:
                if param_law['xIsTime']:
                    self.cb_graph_opt.addItem("Time (s)", "time")
                    date_law = itm.data(1, 32)
                    if date_law:
                        self.cb_graph_opt.addItem("Date", "date")
                    idx = self.cb_graph_opt.findData(cur_opt)
                    if idx != -1:
                        self.cb_graph_opt.setCurrentIndex(idx)
                    self.frm_graph_opt.show()
                else:
                    self.frm_graph_opt.hide()

        else:
            self.frm_graph_opt.hide()

        self.cb_graph_opt.blockSignals(False)

    def display_graph_home(self):
        """
        display graph
        :return:
        """
        if self.tree_laws.selectedItems():
            itm = self.tree_laws.selectedItems()[0]
            id_law = itm.data(0, 32)
            typ_law = itm.parent().data(0, 32)
            param_law = dico_typ_law[typ_law]
            graph_opt = self.cb_graph_opt.currentData()

            if typ_law != 6:
                date_ref = None
                if param_law['xIsTime']:
                    if graph_opt == 'date':
                        date_ref = itm.data(1, 32)

                self.graph_home.init_curv(typ_law, param_law, date_ref)
                self.graph_home.init_graph(id_law, date_ref)
            else:
                self.graph_home.init_curv_weir_zam(param_law, id_law, graph_opt)
                self.graph_home.init_graph_weir_zam(id_law)
        else:
            self.graph_home.init_curv()

    def new_law(self):
        """ create new law button"""
        dlg = ClassHydroLawCreateDialog()
        if dlg.exec_():
            self.cur_law = -1
            self.cur_typ = dlg.cb_type.currentData()
            self.param_law = dico_typ_law[self.cur_typ]
            self.display_law_info()

    def edit_law(self):
        """ edit law button"""
        if self.tree_laws.selectedItems():
            itm = self.tree_laws.selectedItems()[0]
            self.cur_law = itm.data(0, 32)
            self.cur_typ = itm.parent().data(0, 32)
            self.param_law = dico_typ_law[self.cur_typ]
            self.display_law_info()

    def delete_law(self):
        """
        delete law button
        :return:
        """
        if self.tree_laws.selectedItems():
            itm = self.tree_laws.selectedItems()[0]
            id_law = itm.data(0, 32)
            name_law = itm.text(0)
            if (QMessageBox.question(self, "Law Settings",
                                     "Delete {} ?".format(name_law),
                                     QMessageBox.Cancel | QMessageBox.Ok)) == QMessageBox.Ok:
                if self.mgis.DEBUG:
                    self.mgis.add_info(
                        "Deletion of {} Hydro Law".format(name_set))
                self.mdb.execute(
                    "DELETE FROM {0}.law_values WHERE id_law = {1}".format(
                        self.mdb.SCHEMA, id_law))
                self.mdb.execute(
                    "DELETE FROM {0}.law_config WHERE id = {1}".format(
                        self.mdb.SCHEMA, id_law))
                self.fill_tree_laws()

    ######################################################################
    #
    #                           INIT PAGE 2
    #
    ######################################################################

    def display_law_info(self):
        """
        fill info law
        :return:
        """
        cur_date = QDateTime(QDate().currentDate(), QTime(0, 0, 0))

        self.filling_tab = True

        if self.ui.tab_sets.model():
            self.ui.tab_sets.model().setRowCount(0)
            self.ui.tab_sets.model().setColumnCount(0)

        self.grp_time.setVisible(self.param_law["xIsTime"])
        self.grp_abs_wzam.setVisible(self.cur_typ == 6)
        self.cc_date_end_auto.setEnabled(self.param_law["xIsTime"])
        self.lbl_type.setText(self.param_law["name"])
        self.cc_date_end_auto.setCheckState(0)

        if self.cur_law == -1:
            self.txt_name.setText('')
            self.update_cb_geom()
            self.cc_act.setCheckState(0)
            self.cc_date_ref.setCheckState(0)
            self.de_start.setDateTime(cur_date)
            self.de_end.setDateTime(cur_date.addDays(1))
            self.txt_comm.setText('')
        else:
            sql = "SELECT name, geom_obj, starttime, endtime, active, comment FROM {0}.law_config " \
                  "WHERE id = '{1}' ORDER BY name".format(self.mdb.SCHEMA,
                                                          self.cur_law)
            rows = self.mdb.run_query(sql, fetch=True)
            row = rows[0]
            self.txt_name.setText(str(row[0])) if row[
                0] else self.txt_name.setText('')
            self.update_cb_geom(row[1])
            self.cc_date_ref.setCheckState(2) if row[
                2] else self.cc_date_ref.setCheckState(0)
            self.de_start.setDateTime(row[2]) if row[
                2] else self.de_start.setDateTime(cur_date)
            self.de_end.setDateTime(row[3]) if row[
                3] else self.de_end.setDateTime(cur_date.addDays(1))
            self.cc_act.setCheckState(2) if row[
                4] else self.cc_act.setCheckState(0)
            self.txt_comm.setText(str(row[5])) if row[
                5] else self.txt_comm.setText('')

        if self.cur_typ != 6:
            self.graph_edit.init_curv(self.cur_typ, self.param_law)
            self.graph_edit.init_graph(self.cur_law)
            self.fill_tab_laws()
            self.frm_btn_classic.show()
            self.frm_btn_weirzam.hide()
        else:
            self.graph_edit.init_curv_weir_zam(self.param_law, self.cur_law)
            self.graph_edit.init_graph_weir_zam(self.cur_law)
            self.fill_tab_laws_weir_zam()
            self.frm_btn_classic.hide()
            self.frm_btn_weirzam.show()
        self.ui.laws_pages.setCurrentIndex(1)

        self.filling_tab = False

    def update_cb_geom(self, vdef=None):
        """
        fill comboBox for the geometries
        :param vdef:
        :return:
        """
        param_table = {'extremities': {'pref': 'Extr. - ', 'rang': 1},
                       'weirs': {'pref': 'Weir - ', 'rang': 3},
                       'lateral_inflows': {'pref': 'Lat. Inf. - ', 'rang': 2},
                       'lateral_weirs': {'pref': 'Lat. Weir - ', 'rang': 4}}

        sql = "SELECT '' as id_obj, 'None' as name_obj, 0 as rg"
        for table, val in self.param_law["geom"].items():
            if not val:
                pass
            elif val:
                sql += " UNION SELECT name, '{2}' || name, {3} FROM {0}.{1}".format(
                    self.mdb.SCHEMA, table,
                    param_table[table]['pref'],
                    param_table[table]['rang'])
            else:
                sql += " UNION SELECT name, '{3}' || name, {4} FROM {0}.{1} " \
                       "WHERE type IN ({2})".format(self.mdb.SCHEMA, table,
                                                    ", ".join(
                                                        [str(v) for v in val]),
                                                    param_table[table]['pref'],
                                                    param_table[table]['rang'])
        sql += " ORDER BY rg, name_obj"

        rows = self.mdb.run_query(sql, fetch=True)

        self.cb_geom.clear()
        for row in rows:
            self.cb_geom.addItem(row[1], row[0])

        if vdef:
            idx = self.cb_geom.findData(vdef)
            if idx != -1:
                self.cb_geom.setCurrentIndex(idx)

    def fill_tab_laws(self):
        """
        fill law table
        :return:
        """
        self.ui.tab_sets.setModel(self.create_tab_model())
        model = self.ui.tab_sets.model()
        for c in range(model.columnCount()):
            self.ui.tab_sets.setColumnHidden(c, False)

        if self.cur_law != -1:
            c = 0
            for var in self.list_var:
                sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} AND id_var = {2} " \
                      "ORDER BY id_order".format(self.mdb.SCHEMA, self.cur_law,
                                                 var[0])
                rows = self.mdb.run_query(sql, fetch=True)

                if c == 0:
                    model.insertRows(0, len(rows))

                for r, row in enumerate(rows):
                    itm = QStandardItem()
                    itm.setData(row[0], 0)
                    model.setItem(r, c, itm)

                if var[1] == 'time' and self.param_law['xIsTime']:
                    c += 5
                else:
                    c += 1

        if self.param_law['xIsTime']:
            self.rb_sec.click()

    def create_tab_model(self):
        """
        Create model table
        :return:
        """
        self.list_var = []
        model = QStandardItemModel()

        n_var = len(self.param_law['var'])
        if self.param_law['xIsTime']:
            model.insertColumns(0, n_var + 4)
        else:
            model.insertColumns(0, n_var)

        cur_col = 0
        for c, col in enumerate(self.param_law['var']):
            if col["name"] == 'time' and self.param_law['xIsTime']:
                for t in range(5):
                    model.setHeaderData(cur_col, 1, col["name"], 0)
                    cur_col += 1
            else:
                model.setHeaderData(cur_col, 1, col["name"], 0)
                cur_col += 1
            self.list_var.append([c, col["name"], cur_col])

        model.itemChanged.connect(self.on_tab_data_change)
        return model

    def fill_tab_laws_weir_zam(self):
        """
        fill the table of weir zam law
        :return:
        """
        self.ui.tab_sets.setModel(self.create_tab_model_weir_zam())
        model = self.ui.tab_sets.model()

        if self.cur_law != -1:
            max_c = len(self.list_z_av)
            cur_r = 1
            cur_c = 0

            sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} AND id_var = 2 " \
                  "ORDER BY id_order".format(self.mdb.SCHEMA, self.cur_law)
            recs = self.mdb.run_query(sql, fetch=True)
            for rec in recs:
                cur_c += 1
                itm = QStandardItem()
                itm.setData(rec[0], 0)
                model.setItem(cur_r, cur_c, itm)

                if cur_c == max_c:
                    cur_c = 0
                    cur_r += 1

        self.rb_abs_q.click()

    def create_tab_model_weir_zam(self):
        """
        Create the table of weir zam law
        :return:
        """
        self.list_q, self.list_z_av = [], []
        model = QStandardItemModel()
        model.insertRow(0)
        model.insertColumn(0)
        model.setHeaderData(0, 1, "", 0)
        model.setHeaderData(0, 2, "", 0)

        itm = QStandardItemGray("", False)
        model.setItem(0, 0, itm)

        rows = self.mdb.run_query(
            "SELECT DISTINCT value FROM {0}.law_values WHERE id_law = {1} AND id_var = 0 "
            "ORDER BY value".format(self.mdb.SCHEMA, self.cur_law), fetch=True)
        self.list_q = [r[0] for r in rows]
        n_q = len(self.list_q)

        rows = self.mdb.run_query(
            "SELECT DISTINCT value FROM {0}.law_values WHERE id_law = {1} AND id_var = 1 "
            "ORDER BY value".format(self.mdb.SCHEMA, self.cur_law), fetch=True)
        self.list_z_av = [r[0] for r in rows]
        n_z_av = len(self.list_z_av)

        model.insertRows(1, n_q)
        model.insertColumns(1, n_z_av)

        for r, q in enumerate(self.list_q):
            model.setHeaderData(r + 1, 2, "Q{}".format(r + 1), 0)
            itm = QStandardItemGray(q)
            model.setItem(r + 1, 0, itm)

        for c, z_av in enumerate(self.list_z_av):
            model.setHeaderData(c + 1, 1, "Zdown{}".format(c + 1), 0)
            itm = QStandardItemGray(z_av)
            model.setItem(0, c + 1, itm)

        model.itemChanged.connect(self.on_weir_zam_tab_data_change)
        return model

    ######################################################################
    #
    #                           TABLEAU
    #
    ######################################################################

    def new_time(self):
        """
        add time
        :return:
        """
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

        f_col = 5 if self.param_law['xIsTime'] else 1
        for c in range(f_col, model.columnCount()):
            model.setItem(r, c, QStandardItem())
        self.ui.tab_sets.scrollToBottom()
        self.filling_tab = False
        self.update_courbe("all")

    def delete_time(self):
        """
        Delete time
        :return:
        """
        if self.ui.tab_sets.selectedIndexes():
            rows = [idx.row() for idx in self.ui.tab_sets.selectedIndexes()]
            rows = list(set(rows))
            rows.sort(reverse=True)

            model = self.ui.tab_sets.model()
            for row in rows:
                model.removeRow(row)
            self.update_courbe("all")

    def short_cut_row_del(self):
        """
        delete line
        :return:
        """
        if self.ui.tab_sets.hasFocus():
            model = self.ui.tab_sets.model()
            selection = self.ui.tab_sets.selectedIndexes()

            if self.cur_typ != 6:
                d = 5 if self.param_law['xIsTime'] else 1
                cols = []
                for idx in selection:
                    if idx.column() >= d:
                        model.item(idx.row(), idx.column()).setData(None, 0)
                        cols.append(idx.column())
                cols = list(set(cols))
                self.update_courbe(cols)
            else:
                for idx in selection:
                    if idx.column() != 0 and idx.row() != 0:
                        model.item(idx.row(), idx.column()).setData(None, 0)
                self.update_graph_weir_zam()

    def on_tab_data_change(self, itm):
        """
        Change data in table
        :param itm: item to change
        :return:
        """
        model = itm.model()
        if self.param_law['xIsTime']:
            if itm.column() < 4:
                cols = "all"
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
                        model.item(itm.row(), 3).setData(itm.data(0) / 86400.,
                                                         0)
                        if not model.item(itm.row(), 4):
                            date_itm = QStandardItem()
                            date_itm.setEditable(False)
                            model.setItem(itm.row(), 4, date_itm)
                        date = self.date_start + timedelta(seconds=itm.data(0))
                        model.item(itm.row(), 4).setData(
                            date.strftime('%d-%m-%Y %H:%M:%S'), 0)
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
                        if not model.item(itm.row(), 4):
                            date_itm = QStandardItem()
                            date_itm.setEditable(False)
                            model.setItem(itm.row(), 4, date_itm)
                        date = self.date_start + timedelta(minutes=itm.data(0))
                        model.item(itm.row(), 4).setData(
                            date.strftime('%d-%m-%Y %H:%M:%S'), 0)
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
                        if not model.item(itm.row(), 4):
                            date_itm = QStandardItem()
                            date_itm.setEditable(False)
                            model.setItem(itm.row(), 4, date_itm)
                        date = self.date_start + timedelta(hours=itm.data(0))
                        model.item(itm.row(), 4).setData(
                            date.strftime('%d-%m-%Y %H:%M:%S'), 0)
                        model.blockSignals(False)
                    elif itm.column() == 3:
                        model.blockSignals(True)
                        if not model.item(itm.row(), 0):
                            model.setItem(itm.row(), 0, QStandardItem())
                        model.item(itm.row(), 0).setData(itm.data(0) * 86400.,
                                                         0)
                        if not model.item(itm.row(), 1):
                            model.setItem(itm.row(), 1, QStandardItem())
                        model.item(itm.row(), 1).setData(itm.data(0) * 1440., 0)
                        if not model.item(itm.row(), 2):
                            model.setItem(itm.row(), 2, QStandardItem())
                        model.item(itm.row(), 2).setData(itm.data(0) * 24., 0)
                        if not model.item(itm.row(), 4):
                            date_itm = QStandardItem()
                            date_itm.setEditable(False)
                            model.setItem(itm.row(), 4, date_itm)
                        date = self.date_start + timedelta(days=itm.data(0))
                        model.item(itm.row(), 4).setData(
                            date.strftime('%d-%m-%Y %H:%M:%S'), 0)
                        model.blockSignals(False)
            elif itm.column() == 4:
                cols = None
            else:
                cols = [itm.column()]
        else:
            if itm.column() == 0:
                cols = "all"
            else:
                cols = [itm.column()]

        if (not self.filling_tab) and (cols is not None):
            model.sort(0)
            idx = itm.index()
            self.ui.tab_sets.scrollTo(idx, 0)
            if (itm.column()) < 4 and (self.cc_date_end_auto.isChecked()):
                self.calcul_date_end()
            self.update_courbe(cols)

    ######################################################################
    #
    #                           TABLEAU WEIR ZAM
    #
    ######################################################################

    def chg_abs_weir_zam(self, v):
        """
        Change absissa for the graph
        :param v:
        :return:
        """
        if not self.filling_tab:
            self.update_graph_weir_zam()

    def new_q(self):
        """
        add new Q value
        :return:
        """
        self.filling_tab = True
        model = self.ui.tab_sets.model()
        r = model.rowCount()
        model.insertRow(r)
        model.setHeaderData(r, 2, "Q{}".format(r), 0)

        if r == 1:
            val = 0.0
        elif r == 2:
            val = model.item(r - 1, 0).data(0) + 1
        else:
            val = 2 * model.item(r - 1, 0).data(0) - model.item(r - 2, 0).data(
                0)
        itm = QStandardItemGray(val)
        model.setItem(r, 0, itm)

        for c in range(1, model.columnCount()):
            model.setItem(r, c, QStandardItem())
        self.ui.tab_sets.scrollToBottom()
        self.filling_tab = False
        self.update_graph_weir_zam()

    def delete_q(self):
        """
        delete q value
        :return:
        """
        if self.ui.tab_sets.selectedIndexes():
            rows = [idx.row() for idx in self.ui.tab_sets.selectedIndexes() if
                    idx.row() > 0]
            rows = list(set(rows))
            rows.sort(reverse=True)

            model = self.ui.tab_sets.model()
            for row in rows:
                model.removeRow(row)
            self.update_graph_weir_zam()

    def new_z_av(self):
        """
        add new Z value
        :return:
        """
        self.filling_tab = True
        model = self.ui.tab_sets.model()
        c = model.columnCount()
        model.insertColumn(c)
        model.setHeaderData(c, 1, "Zdown{}".format(c), 0)

        if c == 1:
            val = 0.0
        elif c == 2:
            val = model.item(0, c - 1).data(0) + 1
        else:
            val = 2 * model.item(0, c - 1).data(0) - model.item(0, c - 2).data(
                0)
        itm = QStandardItemGray(val)
        model.setItem(0, c, itm)

        for r in range(1, model.rowCount()):
            model.setItem(r, c, QStandardItem())

        self.filling_tab = False
        self.update_graph_weir_zam()

    def delete_z_av(self):
        """
        delete z value
        :return:
        """
        if self.ui.tab_sets.selectedIndexes():
            cols = [idx.column() for idx in self.ui.tab_sets.selectedIndexes()
                    if idx.column() > 0]
            cols = list(set(cols))
            cols.sort(reverse=True)

            model = self.ui.tab_sets.model()
            for col in cols:
                model.removeColumn(col)
            self.update_graph_weir_zam()

    def on_weir_zam_tab_data_change(self, itm):
        """
        Change data in table
        :param itm: item to change
        :return:
        """
        model = itm.model()
        model.itemChanged.disconnect()

        err_row, err_col = False, False

        if itm.column() == 0:
            if itm.row() != 1:
                if itm.data(0) < model.item(itm.row() - 1, 0).data(0):
                    err_row = True
            if itm.row() != model.rowCount() - 1:
                if itm.data(0) > model.item(itm.row() + 1, 0).data(0):
                    err_row = True

        if itm.row() == 0:
            if itm.column() != 1:
                if itm.data(0) < model.item(0, itm.column() - 1).data(0):
                    err_col = True
            if itm.column() != model.columnCount() - 1:
                if itm.data(0) > model.item(0, itm.column() + 1).data(0):
                    err_col = True

        if err_row:
            self.correct_order_row(itm)
        if err_col:
            self.correct_order_column(itm)

        model.itemChanged.connect(self.on_weir_zam_tab_data_change)

        if not self.filling_tab:
            self.update_graph_weir_zam()

    def correct_order_row(self, itm):
        """
        change order
        :param itm:  new item
        :return:
        """
        model = itm.model()

        row = itm.row()
        val_q = itm.data(0)
        val_row = [model.item(row, col).data(0) for col in
                   range(1, model.columnCount())]

        model.removeRow(row)

        new_row = 1
        for r in range(1, model.rowCount()):
            if model.item(r, 0).data(0) >= val_q:
                break
            else:
                new_row += 1

        model.insertRow(new_row)

        for r in range(1, model.rowCount()):
            model.setHeaderData(r, 2, "Q{}".format(r), 0)

        itm = QStandardItemGray(val_q)
        model.setItem(new_row, 0, itm)

        for c, v in enumerate(val_row):
            itm = QStandardItem()
            itm.setData(v, 0)
            model.setItem(new_row, c + 1, itm)

    def correct_order_column(self, itm):
        """
        Change ordre to item
        :param itm: item
        :return:
        """
        model = itm.model()

        col = itm.column()
        val_z = itm.data(0)
        val_col = [model.item(row, col).data(0) for row in
                   range(1, model.rowCount())]

        model.removeColumn(col)

        new_col = 1
        for c in range(1, model.columnCount()):
            if model.item(0, c).data(0) >= val_z:
                break
            else:
                new_col += 1

        model.insertColumn(new_col)

        for c in range(1, model.columnCount()):
            model.setHeaderData(c, 1, "Zdown{}".format(c), 0)

        itm = QStandardItemGray(val_z)
        model.setItem(0, new_col, itm)

        for r, v in enumerate(val_col):
            itm = QStandardItem()
            itm.setData(v, 0)
            model.setItem(r + 1, new_col, itm)

    ######################################################################
    #
    #                           IMPORT
    #
    ######################################################################

    def import_law(self):
        """
        fct to import law
        :return:
        """
        file, _ = QFileDialog.getOpenFileName(None, 'File Selection',
                                              self.mgis.repProject,
                                              "File (*.txt *.csv *.loi)")
        if file:
            if file[-4:] == ".loi":
                sep = " "
            else:
                sep = ";"

            if self.cur_typ != 6:
                self.import_file_classic(file, sep)
            else:
                self.import_file_weir_zam(file, sep)

    def import_file_classic(self, file, sep):
        """
        Import file in the gui
        :param file: (str) file name
        :param sep: (str) separator
        :return:
        """
        filein = open(file, "r")

        error = False
        first_ligne = True
        format_time = None
        nb_col = len(self.param_law["var"])

        self.filling_tab = True

        r = 0
        model = self.create_tab_model()
        coef_time = 1.
        for num_ligne, ligne in enumerate(filein):
            if ligne[0] != '#':
                liste = ligne.replace('\n', '').replace('\t',
                                                        ' ').strip().split(sep)
                if self.param_law["xIsTime"] and liste[0] in ["S", "M", "H",
                                                              "J"]:
                    if liste[0] == "M":
                        coef_time = 1. * 60.
                    elif liste[0] == "H":
                        coef_time = 1. * 60. * 60.
                    elif liste[0] == "J":
                        coef_time = 1. * 60. * 60. * 24.
                    continue

                if len(liste) == nb_col:
                    if first_ligne:
                        first_ligne = False
                        if self.param_law["xIsTime"]:
                            val = data_to_float(liste[0])
                            if val is not None:
                                format_time = 'numeric'
                            else:
                                val = data_to_date(liste[0])
                                if val is not None:
                                    format_time = 'date'
                                    date_ref = val
                                    self.ui.cc_date_ref.setCheckState(2)
                                    self.ui.de_start.setDateTime(date_ref)
                                else:
                                    print('e1')
                                    error = True
                                    break

                    model.insertRow(r)
                    for c, val in enumerate(liste):
                        if c == 0:
                            if format_time == 'date':
                                date_tmp = data_to_date(val)
                                delta = date_tmp - date_ref
                                val = delta.total_seconds()
                            elif format_time == 'numeric':
                                val = data_to_float(val) * coef_time

                        itm = QStandardItem()
                        itm.setData(data_to_float(val), 0)
                        if c == 0:
                            model.setItem(r, c, itm)
                        else:
                            if self.param_law["xIsTime"]:
                                model.setItem(r, c + 4, itm)
                            else:
                                model.setItem(r, c, itm)
                    r += 1
                else:
                    print('e2')
                    error = True
                    break
        filein.close()
        self.filling_tab = False

        if not error:
            self.ui.tab_sets.setModel(model)
            if self.cc_date_end_auto.isChecked():
                self.calcul_date_end()
            self.update_courbe("all")
        else:
            #self.mgis.add_info("Import failed ({})".format(file))
            QMessageBox.warning(self, "Error",
                                "Import failed ({})".format(file),
                                QMessageBox.Ok)

    def import_file_weir_zam(self, file, sep=";"):
        """
        Import file in the gui for Weir Zam law
        :param file: (str) file name
        :param sep: (str) separator
        :return:
        """
        filein = open(file, "r")

        error = False
        nb_col = 3

        rows = list()
        for num_ligne, ligne in enumerate(filein):
            if ligne[0] != '#':
                ligne = ligne.replace('\n', '').replace('\t',
                                                        ' ').strip().split(sep)
                if len(ligne) == nb_col:
                    row = [data_to_float(r) for r in ligne]
                    if None in row:
                        print('e2')
                        error = True
                        break
                    else:
                        rows.append([data_to_float(r) for r in row])
                else:
                    print('e1')
                    error = True
                    break

        filein.close()

        if not error:
            self.filling_tab = True

            dico_imp = dict()
            for idx, fld in enumerate(["q", "z_av", "z_am"]):
                dico_imp[fld] = [r[idx] for r in rows]

            df = DataFrame.from_dict(dico_imp)
            piv = pivot_table(df, values="z_am", index=["q"], columns=["z_av"],
                              aggfunc=np.mean)

            self.list_q, self.list_z_av = [], []
            model = QStandardItemModel()
            model.insertRow(0)
            model.insertColumn(0)
            model.setHeaderData(0, 1, "", 0)
            model.setHeaderData(0, 2, "", 0)

            itm = QStandardItemGray("", False)
            model.setItem(0, 0, itm)

            self.list_q = [ax for ax in piv.axes[0]]
            n_q = len(self.list_q)

            self.list_z_av = [ax for ax in piv.axes[1]]
            n_z_av = len(self.list_z_av)

            model.insertRows(1, n_q)
            model.insertColumns(1, n_z_av)

            for r, q in enumerate(self.list_q):
                model.setHeaderData(r + 1, 2, "Q{}".format(r + 1), 0)
                itm = QStandardItemGray(q)
                model.setItem(r + 1, 0, itm)

            for c, z_av in enumerate(self.list_z_av):
                model.setHeaderData(c + 1, 1, "Zdown{}".format(c + 1), 0)
                itm = QStandardItemGray(z_av)
                model.setItem(0, c + 1, itm)

            for r in range(piv.shape[0]):
                for c in range(piv.shape[1]):
                    itm = QStandardItem()
                    itm.setData(float(piv.iat[r, c]), 0)
                    model.setItem(r + 1, c + 1, itm)

            model.itemChanged.connect(self.on_weir_zam_tab_data_change)
            self.ui.tab_sets.setModel(model)

            self.filling_tab = False

            self.rb_abs_q.click()
        else:
            #self.mgis.add_info("Import failed ({})".format(file))
            QMessageBox.warning(self, "Error",
                                "Import failed ({})".format(file),
                                QMessageBox.Ok)

    ######################################################################
    #
    #                           GRAPH
    #
    ######################################################################

    def update_courbe(self, courbes="all"):
        """
        update curve
        :param courbes: curve to update
        :return:
        """
        data = {}

        d = 5 if self.param_law['xIsTime'] else 1
        if courbes == "all":
            courbes = range(d, self.ui.tab_sets.model().columnCount())

        lx = []
        if self.param_law['xIsTime']:
            col_x = self.bg_time.checkedId()
            for r in range(self.ui.tab_sets.model().rowCount()):
                if col_x != 4:
                    lx.append(self.ui.tab_sets.model().item(r, col_x).data(0))
                else:
                    date = self.date_start + timedelta(
                        seconds=self.ui.tab_sets.model().item(r, 0).data(0))
                    lx.append(date2num(date))
        else:
            for r in range(self.ui.tab_sets.model().rowCount()):
                lx.append(self.ui.tab_sets.model().item(r, 0).data(0))

        for crb in courbes:
            ly = []
            for r in range(self.ui.tab_sets.model().rowCount()):
                ly.append(self.ui.tab_sets.model().item(r, crb).data(0))
            data[crb - d] = {"x": lx, "y": ly}

        self.graph_edit.maj_courbes(data)

    def update_graph_weir_zam(self):
        """
        update graph fir weir Zam Law
        :return:
        """
        g = self.graph_edit

        g.axes.cla()
        g.axes.tick_params(axis='both', labelsize=7.)
        g.axes.grid(True)

        g.list_var.clear()
        g.list_z.clear()
        g.courbes.clear()

        var_x = self.bg_abs.checkedId()
        g.axeX = var_x
        g.axeZ = abs(var_x - 1)

        if var_x == 0:
            g.list_z = [self.ui.tab_sets.model().item(0, c).data(0) for c in
                        range(1, self.ui.tab_sets.model().columnCount())]
            prfx_z = "Zdown"
        elif var_x == 1:
            g.list_z = [self.ui.tab_sets.model().item(r, 0).data(0) for r in
                        range(1, self.ui.tab_sets.model().rowCount())]
            prfx_z = "Q"

        for idx, z in enumerate(g.list_z):
            name = "{0} {1} ({2})".format(prfx_z, idx + 1, round(z, 2))
            g.list_var.append({"id": idx, "name": name})
            g.courbe_laws, = g.axes.plot([], [], zorder=100 - idx, label=name)
            g.courbes.append(g.courbe_laws)

        g.init_legende()

        if g.axeX == 0:
            g.maj_lbl_x('Q', 'm3/s')
        elif g.axeX == 1:
            g.maj_lbl_x('Zdown', 'm')
        g.maj_lbl_y('Zup', 'm')

        g.canvas.draw()

        data = {}
        if var_x == 0:
            lx = [self.ui.tab_sets.model().item(r, 0).data(0) for r in
                  range(1, self.ui.tab_sets.model().rowCount())]
            for c in range(1, self.ui.tab_sets.model().columnCount()):
                ly = [self.ui.tab_sets.model().item(r, c).data(0) for r in
                      range(1, self.ui.tab_sets.model().rowCount())]
                data[c - 1] = {"x": lx, "y": ly}
        elif var_x == 1:
            lx = [self.ui.tab_sets.model().item(0, c).data(0) for c in
                  range(1, self.ui.tab_sets.model().columnCount())]
            for r in range(1, self.ui.tab_sets.model().rowCount()):
                ly = [self.ui.tab_sets.model().item(r, c).data(0) for c in
                      range(1, self.ui.tab_sets.model().columnCount())]
                data[r - 1] = {"x": lx, "y": ly}

        g.maj_courbes(data)

    ######################################################################
    #
    #                           DATES
    #
    ######################################################################

    def enable_date_end(self, b):
        """
        enable end date
        :param b: is enable or not
        :return:
        """
        self.de_end.setEnabled(not b)
        if b:
            self.calcul_date_end()

    def calcul_date_end(self):
        if not self.filling_tab:
            model = self.ui.tab_sets.model()
            if model:
                r = model.rowCount() - 1
                if r >= 0:
                    ds = model.item(r, 0).data(0)
                    self.de_end.setDateTime(
                        self.ui.de_start.dateTime().addSecs(ds))

    def change_date_start(self):
        """
        action when start date change
        :return:
        """
        date, time = self.ui.de_start.date().toString(
            'dd-MM-yyyy'), self.ui.de_start.time().toString('HH:mm:ss')
        date_str = "'{} {}'".format(date, time)
        self.date_start = data_to_date(date_str)

        if self.param_law['xIsTime']:
            if self.cc_date_end_auto.isChecked():
                self.calcul_date_end()

            model = self.ui.tab_sets.model()
            if model:
                for r in range(model.rowCount()):
                    if not model.item(r, 4):
                        date_itm = QStandardItem()
                        date_itm.setEditable(True)
                        model.setItem(r, 4, date_itm)
                    date = self.date_start + timedelta(
                        seconds=model.item(r, 0).data(0))
                    model.item(r, 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'),
                                             0)

                if (not self.filling_tab) and (self.bg_time.checkedId() == 4):
                    self.update_courbe("all")

    def change_date_end(self):
        """
        get last date when it changes
        :return:
        """
        date, time = self.ui.de_end.date().toString(
            'dd-MM-yyyy'), self.ui.de_end.time().toString('HH:mm:ss')
        date_str = "'{} {}'".format(date, time)
        self.date_end = data_to_date(date_str)

    def chg_time(self, v):
        """
        Change time unit
        :param v: unit
        :return:
        """
        unit = ['s', 'min', 'h', 'day', 'date']
        for i in range(5):
            if i == v:
                self.ui.tab_sets.setColumnHidden(i, False)
            else:
                self.ui.tab_sets.setColumnHidden(i, True)
                if not self.filling_tab:
                    self.graph_edit.maj_lbl_x("time", unit[v])
                    self.update_courbe("all")

    ######################################################################
    #
    #                           VALIDATION
    #
    ######################################################################

    def accept_page2(self):
        """ action when valide page"""
        name_law = self.ui.txt_name.text() if self.ui.txt_name.text() else None
        if not name_law:
            QMessageBox.warning(self, "Error", "Variable Law Name is needed !",
                                QMessageBox.Ok)
            return

        rows = self.mdb.run_query(
            "SELECT * FROM {0}.law_config WHERE name = '{1}' "
            "AND id <> {2}".format(self.mdb.SCHEMA, name_law, self.cur_law),
            fetch=True)
        if rows:
            QMessageBox.warning(self, "Error",
                                "Law Name '{}' already exists !".format(
                                    name_law), QMessageBox.Ok)
            return

        name_law = "'{}'".format(name_law)
        geom_obj = "'{}'".format(
            self.ui.cb_geom.currentData()) if self.ui.cb_geom.currentIndex() != 0 else 'Null'
        comment = "'{}'".format(
            self.ui.txt_comm.text()) if self.ui.txt_comm.text() else 'Null'
        is_act = self.cc_act.isChecked()

        if self.cc_date_ref.isChecked():
            date_start = "'{} {}'".format(
                self.de_start.date().toString('yyyy-MM-dd'),
                self.de_start.time().toString('HH:mm:ss'))
            date_end = "'{} {}'".format(
                self.de_end.date().toString('yyyy-MM-dd'),
                self.de_end.time().toString('HH:mm:ss'))
        else:
            date_start, date_end = 'Null', 'Null'

        if self.cur_law == -1:
            if self.mgis.DEBUG:
                self.mgis.add_info("Addition of {} Hydro Law".format(name_law))
            self.mdb.execute(
                "INSERT INTO {0}.law_config (name, geom_obj, starttime, endtime, id_law_type, active, comment) "
                "VALUES ({1}, {2}, {3}, {4}, {5}, {6}, {7})".format(
                    self.mdb.SCHEMA, name_law, geom_obj, date_start,
                    date_end, self.cur_typ, is_act, comment))
            res = self.mdb.run_query(
                "SELECT Max(id) FROM {0}.law_config".format(self.mdb.SCHEMA),
                fetch=True)
            self.cur_law = res[0][0]
        else:
            if self.mgis.DEBUG:
                self.mgis.add_info("Editing of {} ".format(name_law))
            self.mdb.execute(
                "UPDATE {0}.law_config SET name = {1}, geom_obj = {2}, starttime = {3}, endtime = {4}, "
                "active = {5}, comment = {6} WHERE id = {7}".format(
                    self.mdb.SCHEMA, name_law, geom_obj, date_start,
                    date_end, is_act, comment, self.cur_law))
            self.mdb.execute(
                "DELETE FROM {0}.law_values WHERE id_law = {1}".format(
                    self.mdb.SCHEMA, self.cur_law))

        # if is_act and self.ui.cb_geom.currentIndex() != 0:
        #     self.mdb.execute(
        #         "UPDATE {0}.law_config SET active = {1} WHERE geom_obj = {2} "
        #         "AND id <> {3}".format(self.mdb.SCHEMA, False, geom_obj,
        #                                self.cur_law))

        if self.cur_typ != 6:
            col = list(range(self.ui.tab_sets.model().columnCount()))
            if self.param_law['xIsTime']:
                del col[1:5]

            recs = []
            for id_var, c in enumerate(col):
                for r in range(self.ui.tab_sets.model().rowCount()):
                    recs.append([self.cur_law, id_var, r,
                                 self.ui.tab_sets.model().item(r, c).data(0)])
        else:
            recs = []
            rg = 0
            for r in range(1, self.ui.tab_sets.model().rowCount()):
                for c in range(1, self.ui.tab_sets.model().columnCount()):
                    recs.append([self.cur_law, 0, rg,
                                 self.ui.tab_sets.model().item(r, 0).data(0)])
                    recs.append([self.cur_law, 1, rg,
                                 self.ui.tab_sets.model().item(0, c).data(0)])
                    recs.append([self.cur_law, 2, rg,
                                 self.ui.tab_sets.model().item(r, c).data(0)])
                    rg += 1

        self.mdb.run_query(
            "INSERT INTO {0}.law_values (id_law, id_var, id_order, value) VALUES (%s, %s, %s, %s)".format(
                self.mdb.SCHEMA), many=True, list_many=recs)

        self.fill_tree_laws(self.cur_law)
        self.ui.laws_pages.setCurrentIndex(0)
        self.graph_edit.init_curv()
        self.tree_laws.setFocus()

    def reject_page2(self):
        """
        action when reject page
        :return:
        """
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Hydro Law Setting")
        self.ui.laws_pages.setCurrentIndex(0)
        self.graph_edit.init_curv()
        self.tree_laws.setFocus()

    def copier(self):
        """copier la zone sélectionnée dans le clipboard
        """
        selection = self.ui.tab_sets.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            col_to_tab  = {col : id for id, col in enumerate(set(columns))}
            nb_col = len(set(columns))
            #colcount = columns[-1] - columns[0] + 1
            #table = [[''] * colcount for _ in range(rowcount)]
            table = [[''] * nb_col for _ in range(rowcount)]

            for index in selection:
                row = index.row() - rows[0]
                # column = index.column() - columns[0]
                column = col_to_tab[index.column()]
                data = index.data()
                table[row][column] = data
            stream = io.StringIO()
            csv.writer(stream).writerows(table)
            qApp.clipboard().setText(stream.getvalue())

    def keyPressEvent(self, event):

        if self.ui.tab_sets.hasFocus():

            # ----------------------------------------------------------------
            # Ctle-C: copier
            if event.key() == Qt.Key_C and (
                        event.modifiers() & Qt.ControlModifier):
                self.copier()
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()
class ItemEditorFactory(QItemEditorFactory):
    def __init__(self):
        QItemEditorFactory.__init__(self)

    def createEditor(self, user_type, parent):
        # print (user_type)
        if user_type == QVariant.Double or user_type == 0:
            double_spin_box = QDoubleSpinBox(parent)
            double_spin_box.setDecimals(10)
            double_spin_box.setMinimum(
                -1000000000.)  # The default maximum value is 99.99.
            double_spin_box.setMaximum(
                1000000000.)  # The default maximum value is 99.99.
            return double_spin_box
        elif user_type == 16:
            date_time_edit = QDateTimeEdit(parent)
            date_time_edit.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
            return date_time_edit
        else:
            return ItemEditorFactory.createEditor(user_type, parent)


class ClassHydroLawCreateDialog(QDialog):
    def __init__(self, parent=None):
        super(ClassHydroLawCreateDialog, self).__init__(parent)

        layout = QFormLayout()

        self.cb_type = QComboBox()
        for id_type, elem in dico_typ_law.items():
            self.cb_type.addItem(elem['name'], id_type)

        self.btn_box = QDialogButtonBox(self)
        self.btn_box.addButton("OK", 0)
        self.btn_box.addButton("Annuler", 1)

        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)

        layout.addRow(QLabel("Type"), self.cb_type)
        layout.addRow(self.btn_box)

        self.setLayout(layout)


class QStandardItemGray(QStandardItem):
    def __init__(self, v, enab=True, parent=None):
        super(QStandardItemGray, self).__init__(parent)

        self.setBackground(QColor("#E9E7E3"))
        self.setData(v, 0)
        if not enab:
            self.setFlags(Qt.ItemIsEnabled)
