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
from datetime import datetime, timedelta
from matplotlib.dates import date2num
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .Graphic.GraphHydro import GraphHydroLaw
# from .table_WQ import table_WQ
from .Function import data_to_float, data_to_date

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
    from qgis.PyQt.QtWidgets import *

#TODO decorreler le nom de la loi et le nom de l'extremite
dico_typ_law = {1: {'name': 'Hydrograph Q(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'flowrate', 'code': 'flowrate'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
                    'geom':{'extremities': [1], 'weirs': False, 'lateral_inflows': True, 'lateral_weirs': False},
                    'xIsTime': True},
                2: {'name': 'Limnigraph Z(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'level', 'code': 'z'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
                    'geom':{'extremities': [2], 'weirs': [5], 'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': True},
                3: {'name': 'Limnihydrograph Z,Q(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'level', 'code': 'z'},
                            {'name': 'flowrate', 'code': 'flowrate'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1, 2], 'tit': 'Various', 'unit': ''}},
                    'geom':{'extremities': [8], 'weirs': False, 'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': True},
                4: {'name': 'Rating Curve Z = f(Q)',
                    'var': [{'name': 'flowrate', 'code': 'flowrate'},
                            {'name': 'level', 'code': 'z'}],
                    'graph': {'x': {'var': 0, 'tit': 'Q', 'unit': 'm3/s'},
                              'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
                    'geom':{'extremities': [3, 5], 'weirs': [2], 'lateral_inflows': False, 'lateral_weirs': [2]},
                    'xIsTime': False},
                5: {'name': 'Rating Curve Q = f(Z)',
                    'var': [{'name': 'level', 'code': 'z'},
                            {'name': 'flowrate', 'code': 'flowrate'}],
                    'graph': {'x': {'var': 0, 'tit': 'Z', 'unit': 'm'},
                              'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
                    'geom':{'extremities': [4], 'weirs': [6, 7], 'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': False},
                6: {'name': 'Weir Zam = f(Q, Zav)',
                    'var': [{'name': 'flowrate', 'code': 'flowrate'},
                            {'name': 'downstream level', 'code': 'z_downstream'},
                            {'name': 'upstream level', 'code': 'z_upstream'},
                            ],
                    'geom':{'extremities': [0, 6], 'weirs': [1], 'lateral_inflows': False, 'lateral_weirs': False},
                    'graph': None,
                    'xIsTime': False},
                7: {'name': 'Floodgate Zinf, Zsup = f(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'lower level', 'code': 'z_lower'},
                            {'name': 'upper level', 'code': 'z_up'}],

                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1, 2], 'tit': 'Z', 'unit': 'm'}},
                    'geom':{'extremities': [7], 'weirs': [8], 'lateral_inflows': False, 'lateral_weirs': False},
                    'xIsTime': True}
                }


class ClassHydroLawsDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.cur_law = None
        self.param_law = None
        self.filling_tab = False

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_hydro_laws.ui'), self)

        # PAGE 1

        self.tree_laws.setColumnWidth(0, 175)
        self.tree_laws.setColumnWidth(1, 100)
        self.tree_laws.setColumnWidth(2, 40)
        self.tree_laws.itemSelectionChanged.connect(self.display_graph_home)

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

        self.ui.actionB_import.triggered.connect(self.import_csv)
        self.ui.actionB_addLine.triggered.connect(self.new_time)
        self.ui.actionB_delLine.triggered.connect(self.delete_time)
        self.ui.b_OK_page2.accepted.connect(self.accept_page2)
        self.ui.b_OK_page2.rejected.connect(self.reject_page2)

        self.init_ui()


    def init_ui(self):
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
        self.tree_laws.clear()
        for id_type, elem in dico_typ_law.items():
            sql = "SELECT id, name, geom_obj, active, comment FROM {0}.law_config " \
                  "WHERE id_law_type = '{1}' ORDER BY name".format(self.mdb.SCHEMA, id_type)
            rows = self.mdb.run_query(sql, fetch=True)
            if rows:
                typ_itm = QTreeWidgetItem()
                typ_itm.setFlags(Qt.ItemIsEnabled)
                typ_itm.setData(0, 32, id_type)
                typ_itm.setText(0, elem['name'])
                self.tree_laws.addTopLevelItem(typ_itm)

                for row in rows:
                    ouv_itm = QTreeWidgetItem()
                    ouv_itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    ouv_itm.setData(0, 32, int(row[0]))
                    ouv_itm.setText(0, row[1])
                    ouv_itm.setText(1, str(row[2])) if row[2] is not None else ouv_itm.setText(1, '')
                    ouv_itm.setText(2, str(row[3]))
                    ouv_itm.setText(3, str(row[4])) if row[4] is not None else ouv_itm.setText(3, '')

                    typ_itm.addChild(ouv_itm)
                typ_itm.setExpanded(True)

        if id:
            for p in range(self.tree_laws.topLevelItemCount()):
                for c in range(self.tree_laws.topLevelItem(p).childCount()):
                    itm = self.tree_laws.topLevelItem(p).child(c)
                    if itm.data(0, 32) == id:
                        self.tree_laws.setCurrentItem(itm, 0)
                        break
        else:
            self.display_graph_home()


    def display_graph_home(self):
        if self.tree_laws.selectedItems():
            itm = self.tree_laws.selectedItems()[0]
            id_law = itm.data(0, 32)
            typ_law = itm.parent().data(0, 32)
            param_law = dico_typ_law[typ_law]
            self.graph_home.initCurv(typ_law, param_law)
            self.graph_home.initGraph(id_law)
        else:
            self.graph_home.initCurv()


    def new_law(self):
        dlg = ClassHydroLawCreateDialog()
        if dlg.exec_():
            self.cur_law = -1
            self.cur_typ = dlg.cb_type.currentData()
            self.param_law = dico_typ_law[self.cur_typ]
            self.display_law_info()


    def edit_law(self):
        if self.tree_laws.selectedItems():
            itm = self.tree_laws.selectedItems()[0]
            self.cur_law = itm.data(0, 32)
            self.cur_typ = itm.parent().data(0, 32)
            self.param_law = dico_typ_law[self.cur_typ]
            self.display_law_info()


    def delete_law(self):
        if self.tree_laws.selectedItems():
            itm = self.tree_laws.selectedItems()[0]
            id_law = itm.data(0, 32)
            name_law = itm.text(0)
            if (QMessageBox.question(self, "Law Settings", "Delete {} ?".format(name_law),
                                     QMessageBox.Cancel | QMessageBox.Ok)) == QMessageBox.Ok:
                if self.mgis.DEBUG:
                    self.mgis.add_info("Deletion of {} Hydro Law".format(name_set))
                self.mdb.execute("DELETE FROM {0}.law_values WHERE id_law = {1}".format(self.mdb.SCHEMA, id_law))
                self.mdb.execute("DELETE FROM {0}.law_config WHERE id = {1}".format(self.mdb.SCHEMA, id_law))
                self.fill_tree_laws()


    ######################################################################
    #
    #                           INIT PAGE 2
    #
    ######################################################################

    def display_law_info(self):
        cur_date = QDateTime(QDate().currentDate(), QTime(0, 0, 0))

        self.filling_tab = True

        self.grp_time.setVisible(self.param_law["xIsTime"])
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
                  "WHERE id = '{1}' ORDER BY name".format(self.mdb.SCHEMA, self.cur_law)
            rows = self.mdb.run_query(sql, fetch=True)
            row = rows[0]
            self.txt_name.setText(str(row[0])) if row[0] else self.txt_name.setText('')
            self.update_cb_geom(row[1])
            self.cc_date_ref.setCheckState(2) if row[2] else self.cc_date_ref.setCheckState(0)
            self.de_start.setDateTime(row[2]) if row[2] else self.de_start.setDateTime(cur_date)
            self.de_end.setDateTime(row[3]) if row[3] else self.de_end.setDateTime(cur_date.addDays(1))
            self.cc_act.setCheckState(2) if row[4] else self.cc_act.setCheckState(0)
            self.txt_comm.setText(str(row[5])) if row[5] else self.txt_comm.setText('')

        self.graph_edit.initCurv(self.cur_typ, self.param_law)
        self.graph_edit.initGraph(self.cur_law)
        self.fill_tab_laws()
        self.ui.laws_pages.setCurrentIndex(1)

        self.filling_tab = False


    def update_cb_geom(self, vdef=None):
        sql = "SELECT 'None' as name_obj"
        for table, val in self.param_law["geom"].items():
            if val == False:
                pass
            elif val == True:
                sql += " UNION SELECT name FROM {0}.{1}".format(self.mdb.SCHEMA, table)
            else:
                sql += " UNION SELECT name FROM {0}.{1} WHERE type IN ({2})".format(self.mdb.SCHEMA, table,
                                                                                    ", ".join([str(v) for v in val]))
        sql += " ORDER BY name_obj"
        rows = self.mdb.run_query(sql, fetch=True)
        lst_obj = list(set([r[0] for r in rows]))

        self.cb_geom.clear()
        self.cb_geom.addItems(lst_obj)

        if vdef:
            idx = self.cb_geom.findText(vdef)
            if idx != -1:
                self.cb_geom.setCurrentIndex(idx)


    def fill_tab_laws(self):
        self.ui.tab_sets.setModel(self.create_tab_model())
        model = self.ui.tab_sets.model()
        for c in range(model.columnCount()):
            self.ui.tab_sets.setColumnHidden(c, False)

        if self.cur_law != -1:
            c = 0
            for var in self.list_var:
                sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} AND id_var = {2} " \
                      "ORDER BY id_order".format(self.mdb.SCHEMA, self.cur_law, var[0])
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


    ######################################################################
    #
    #                           TABLEAU
    #
    ######################################################################

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

        f_col = 5 if self.param_law['xIsTime'] else 1
        for c in range(f_col, model.columnCount()):
            model.setItem(r, c, QStandardItem())
        self.ui.tab_sets.scrollToBottom()
        self.filling_tab = False
        self.update_courbe("all")


    def delete_time(self):
        if self.ui.tab_sets.selectedIndexes():
            rows = [idx.row() for idx in self.ui.tab_sets.selectedIndexes()]
            rows = list(set(rows))
            rows.sort(reverse=True)
            for row in rows:
                model = self.ui.tab_sets.model()
                model.removeRow(row)
            self.update_courbe("all")


    def short_cut_row_del(self):
        if self.ui.tab_sets.hasFocus():
            d = 5 if self.param_law['xIsTime'] else 1

            cols = []
            model = self.ui.tab_sets.model()
            selection = self.ui.tab_sets.selectedIndexes()
            for idx in selection:
                if idx.column() >= d:
                    model.item(idx.row(), idx.column()).setData(None, 0)
                    cols.append(idx.column())
            cols = list(set(cols))
            self.update_courbe(cols)


    def on_tab_data_change(self, itm):
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
                        model.item(itm.row(), 3).setData(itm.data(0) / 86400., 0)
                        if not model.item(itm.row(), 4):
                            date_itm = QStandardItem()
                            date_itm.setEditable(False)
                            model.setItem(itm.row(), 4, date_itm)
                        date = self.date_start + timedelta(seconds=itm.data(0))
                        model.item(itm.row(), 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'), 0)
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
                        model.item(itm.row(), 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'), 0)
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
                        model.item(itm.row(), 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'), 0)
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
                        if not model.item(itm.row(), 4):
                            date_itm = QStandardItem()
                            date_itm.setEditable(False)
                            model.setItem(itm.row(), 4, date_itm)
                        date = self.date_start + timedelta(days=itm.data(0))
                        model.item(itm.row(), 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'), 0)
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
    #                           IMPORT
    #
    ######################################################################

    def import_csv(self):
        file, _ = QFileDialog.getOpenFileName(None, 'File Selection', self.mgis.repProject,
                                              "File (*.txt *.csv)")
        if file:
            filein = open(file, "r")

            error = False
            first_ligne = True
            format_time = None
            nb_col = len(self.param_law["var"])

            self.filling_tab = True

            r = 0
            model = self.create_tab_model()
            for num_ligne, ligne in enumerate(filein):
                if ligne[0] != '#':
                    liste = ligne.replace('\n', '').replace('\t', ' ').split(";")
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
                            if c == 0 and format_time == 'date':
                                date_tmp = data_to_date(val)
                                delta = date_tmp - date_ref
                                val = delta.total_seconds()

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
                if self.mgis.DEBUG:
                    self.mgis.add_info("Import failed ({})".format(file))


    ######################################################################
    #
    #                           GRAPH
    #
    ######################################################################

    def update_courbe(self, courbes="all"):
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
                    date = self.date_start + timedelta(seconds=self.ui.tab_sets.model().item(r, 0).data(0))
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


    ######################################################################
    #
    #                           DATES
    #
    ######################################################################

    def enable_date_end(self, b):
        self.de_end.setEnabled(not b)
        if b:
            self.calcul_date_end()

    def calcul_date_end(self):
        if not self.filling_tab:
            model = self.ui.tab_sets.model()
            if model:
                r = model.rowCount() - 1
                ds = model.item(r, 0).data(0)
                self.de_end.setDateTime(self.ui.de_start.dateTime().addSecs(ds))

    def change_date_start(self):
        date, time = self.ui.de_start.date().toString('dd-MM-yyyy'), self.ui.de_start.time().toString('HH:mm:ss')
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
                    date = self.date_start + timedelta(seconds=model.item(r, 0).data(0))
                    model.item(r, 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'), 0)

                if (not self.filling_tab) and (self.bg_time.checkedId() == 4):
                    self.update_courbe("all")

    def change_date_end(self):
        date, time = self.ui.de_end.date().toString('dd-MM-yyyy'), self.ui.de_end.time().toString('HH:mm:ss')
        date_str = "'{} {}'".format(date, time)
        self.date_end = data_to_date(date_str)

    def chg_time(self, v):
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
        name_law = self.ui.txt_name.text() if self.ui.txt_name.text() else None
        if not name_law:
            QMessageBox.warning(self, "Error", "Variable Law Name is needed !", QMessageBox.Ok)
            return

        rows = self.mdb.run_query("SELECT * FROM {0}.law_config WHERE name = '{1}' "
                                  "AND id <> {2}".format(self.mdb.SCHEMA, name_law, self.cur_law), fetch=True)
        if rows:
            QMessageBox.warning(self, "Error", "Law Name '{}' already exists !".format(name_law), QMessageBox.Ok)
            return

        name_law = "'{}'".format(name_law)
        geom_obj = "'{}'".format(self.ui.cb_geom.currentText()) if self.ui.cb_geom.currentIndex() != 0 else 'Null'
        comment = "'{}'".format(self.ui.txt_comm.text()) if self.ui.txt_comm.text() else 'Null'
        is_act = self.cc_act.isChecked()

        if self.cc_date_ref.isChecked():
            date_start = "'{} {}'".format(self.de_start.date().toString('yyyy-MM-dd'),
                                          self.de_start.time().toString('HH:mm:ss'))
            date_end = "'{} {}'".format(self.de_end.date().toString('yyyy-MM-dd'),
                                        self.de_end.time().toString('HH:mm:ss'))
        else:
            date_start, date_end = 'Null', 'Null'

        if self.cur_law == -1:
            if self.mgis.DEBUG:
                self.mgis.add_info("Addition of {} Hydro Law".format(name_law))
            self.mdb.execute(
                "INSERT INTO {0}.law_config (name, geom_obj, starttime, endtime, id_law_type, active, comment) "
                "VALUES ({1}, {2}, {3}, {4}, {5}, {6}, {7})".format(self.mdb.SCHEMA, name_law, geom_obj, date_start,
                                                                    date_end, self.cur_typ, is_act, comment))
            res = self.mdb.run_query("SELECT Max(id) FROM {0}.law_config".format(self.mdb.SCHEMA), fetch=True)
            self.cur_law = res[0][0]
        else:
            if self.mgis.DEBUG:
                self.mgis.add_info("Editing of {} ".format(name_law))
            self.mdb.execute(
                "UPDATE {0}.law_config SET name = {1}, geom_obj = {2}, starttime = {3}, endtime = {4}, "
                "active = {5}, comment = {6} WHERE id = {7}".format(self.mdb.SCHEMA, name_law, geom_obj, date_start,
                                                                    date_end, is_act, comment, self.cur_law))
            self.mdb.execute("DELETE FROM {0}.law_values WHERE id_law = {1}".format(self.mdb.SCHEMA, self.cur_law))

        col = list(range(self.ui.tab_sets.model().columnCount()))
        if self.param_law['xIsTime']:
            del col[1:5]

        recs = []
        for id_var, c in enumerate(col):
            for r in range(self.ui.tab_sets.model().rowCount()):
                recs.append([self.cur_law, id_var, r, self.ui.tab_sets.model().item(r, c).data(0)])

        self.mdb.run_query("INSERT INTO {0}.law_values (id_law, id_var, id_order, value) VALUES (%s, %s, %s, %s)".format(
            self.mdb.SCHEMA), many=True, list_many=recs)

        self.fill_tree_laws(self.cur_law)
        self.ui.laws_pages.setCurrentIndex(0)
        self.graph_edit.initCurv()
        self.tree_laws.setFocus()


    def reject_page2(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Hydro Law Setting")
        self.ui.laws_pages.setCurrentIndex(0)
        self.graph_edit.initCurv()
        self.tree_laws.setFocus()




class ItemEditorFactory(QItemEditorFactory):
    def __init__(self):
        QItemEditorFactory.__init__(self)

    def createEditor(self, user_type, parent):
        # print (user_type)
        if user_type == QVariant.Double or user_type == 0:
            double_spin_box = QDoubleSpinBox(parent)
            double_spin_box.setDecimals(10)
            double_spin_box.setMinimum(-1000000000.)  # The default maximum value is 99.99.
            double_spin_box.setMaximum(1000000000.)  # The default maximum value is 99.99.
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