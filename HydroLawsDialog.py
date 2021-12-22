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
                            {'name': 'flowrate', 'code': 'Q'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
                    'xIsTime': True},
                2: {'name': 'Limnigraph Z(t)',
                    'var': [{'name': 'time', 'code': 'time', 'unit': 's'},
                            {'name': 'level', 'code': 'Z', 'unit': 'm'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
                    'xIsTime': True},
                3: {'name': 'Limnihydrograph Z,Q(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'level', 'code': 'Z'},
                            {'name': 'flowrate', 'code': 'Q'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1, 2], 'tit': 'Various', 'unit': ''}},
                    'xIsTime': True},
                4: {'name': 'Rating Curve Z = f(Q)',
                    'var': [{'name': 'flowrate', 'code': 'Q'},
                            {'name': 'level', 'code': 'Z'}],
                    'graph': {'x': {'var': 0, 'tit': 'Q', 'unit': 'm3/s'},
                              'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
                    'xIsTime': False},
                5: {'name': 'Rating Curve Q = f(Z)',
                    'var': [{'name': 'level', 'code': 'Z'},
                            {'name': 'flowrate', 'code': 'Q'}],
                    'graph': {'x': {'var': 0, 'tit': 'Z', 'unit': 'm'},
                              'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
                    'xIsTime': False},
                6: {'name': 'Weir Zam = f(Q, Zav)',
                    'var': [{'name': 'flowrate', 'code': 'Q'},
                            {'name': 'upstream level', 'code': 'Zup'},
                            {'name': 'downstream', 'code': 'Zdown', 'unit': 'm'}],
                    'graph': None,
                    'xIsTime': False},
                7: {'name': 'Floodgate Zinf, Zsup = f(t)',
                    'var': [{'name': 'time', 'code': 'time'},
                            {'name': 'lower level', 'code': 'Zlow'},
                            {'name': 'upper level', 'code': 'Zupp'}],
                    'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                              'y': {'var': [1, 2], 'tit': 'Z', 'unit': 'm'}},
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
                    ouv_itm.setText(1, str(row[2]))
                    ouv_itm.setText(2, str(row[3]))
                    ouv_itm.setText(3, str(row[4]))

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
                    self.mgis.addInfo("Deletion of {} Hydro Law".format(name_set))
                self.mdb.execute("DELETE FROM {0}.law_values WHERE id_law = {1}".format(self.mdb.SCHEMA, id_law))
                self.mdb.execute("DELETE FROM {0}.law_config WHERE id = {1}".format(self.mdb.SCHEMA, id_law))
                self.fill_tree_laws()


    def display_law_info(self):
        cur_date = QDateTime(QDate().currentDate(), QTime(0, 0, 0))

        self.grp_time.setVisible(self.param_law["xIsTime"])
        self.cc_date_end_auto.setEnabled(self.param_law["xIsTime"])
        self.lbl_type.setText(self.param_law["name"])
        self.cc_date_end_auto.setCheckState(0)

        if self.cur_law == -1:
            self.txt_name.setText('')
            self.txt_geom.setText('')
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
            self.txt_geom.setText(str(row[1])) if row[1] else self.txt_geom.setText('')
            self.cc_date_ref.setCheckState(2) if row[2] else self.cc_date_ref.setCheckState(0)
            self.de_start.setDateTime(row[2]) if row[2] else self.de_start.setDateTime(cur_date)
            self.de_end.setDateTime(row[3]) if row[3] else self.de_start.setDateTime(cur_date.addDays(1))
            self.cc_act.setCheckState(2) if row[4] else self.cc_act.setCheckState(0)
            self.txt_comm.setText(str(row[5])) if row[5] else self.txt_comm.setText('')

        self.fill_tab_laws()
        # self.graph_edit.initGraph(self.cur_set)
        self.ui.laws_pages.setCurrentIndex(1)









    def change_date_start(self):
        date, time = self.ui.de_start.date().toString('dd-MM-yyyy'), self.ui.de_start.time().toString('HH:mm:ss')
        date_str = "'{} {}'".format(date, time)
        self.date_start = data_to_date(date_str)

        if self.param_law['xIsTime']:
            model = self.ui.tab_sets.model()
            if model:
                for r in range(model.rowCount()):
                    if not model.item(r, 4):
                        date_itm = QStandardItem()
                        date_itm.setEditable(True)
                        model.setItem(r, 4, date_itm)
                    date = self.date_start + timedelta(seconds=model.item(r, 0).data(0))
                    model.item(r, 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'), 0)
                #     model.item(r, 4).setData(QDateTime(date), 0)
                # if self.bg_time.checkedId() == 4:
                #     self.update_courbe("all")

    def change_date_end(self):
        date, time = self.ui.de_end.date().toString('dd-MM-yyyy'), self.ui.de_end.time().toString('HH:mm:ss')
        date_str = "'{} {}'".format(date, time)
        self.date_end = data_to_date(date_str)

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

    def short_cut_row_del(self):
        if self.ui.tab_sets.hasFocus():
            cols = []
            model = self.ui.tab_sets.model()
            selection = self.ui.tab_sets.selectedIndexes()
            for idx in selection:
                if idx.column() > 4:
                    model.item(idx.row(), idx.column()).setData(None, 0)
                    cols.append(idx.column() - 5)
            cols = list(set(cols))
            self.update_courbe(cols)

    def fill_tab_laws(self):
        self.filling_tab = True
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

        self.filling_tab = False

        if self.param_law['xIsTime']:
            self.rb_sec.click()

    def import_csv(self):
        nb_col = 7
        first_ligne = True
        if int(qVersion()[0]) < 5:  # qt4
            listf = QFileDialog.getOpenFileNames(None, 'File Selection', self.mgis.repProject,
                                                 "File (*.txt *.csv *.met)")

        else:  # qt5
            listf, _ = QFileDialog.getOpenFileNames(None, 'File Selection', self.mgis.repProject,
                                                    "File (*.txt *.csv *.met)")

        if listf:
            error = False
            self.filling_tab = True
            model = self.create_tab_model()
            r = 0

            filein = open(listf[0], "r")
            for num_ligne, ligne in enumerate(filein):
                if ligne[0] != '#':
                    liste = ligne.replace('\n', '').replace('\t', ' ').split(";")
                    if len(liste) == nb_col:
                        if first_ligne:
                            val = data_to_float(liste[0])
                            if val is not None:
                                typ_time = 'num'
                            else:
                                val = data_to_date(liste[0])
                                if val is not None:
                                    typ_time = 'date'
                                    date_ref = val
                                    self.ui.cb_date.setCheckState(2)
                                    date_ref_str = datetime.strftime(date_ref, '%Y-%m-%d %H:%M:%S')
                                    self.ui.de_date.setDateTime(
                                        QDateTime().fromString(date_ref_str, 'yyyy-MM-dd HH:mm:ss'))
                                else:
                                    print('e1')
                                    error = True
                                    break
                            first_ligne = False
                        model.insertRow(r)
                        for c, val in enumerate(liste):
                            if c == 0 and typ_time == 'date':
                                date_tmp = data_to_date(val)
                                delta = date_tmp - date_ref
                                val = delta.total_seconds()
                            itm = QStandardItem()
                            itm.setData(data_to_float(val), 0)
                            if c == 0:
                                model.setItem(r, c, itm)
                            else:
                                model.setItem(r, c + 4, itm)
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
                    self.mgis.addInfo("Import failed ({})".format(listf[0]))

    def on_tab_data_change(self, itm):
        if not self.param_law['xIsTime']:
            return
        if itm.column() < 5:
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
                    if not model.item(itm.row(), 4):
                        date_itm = QStandardItem()
                        date_itm.setEditable(False)
                        model.setItem(itm.row(), 4, date_itm)
                    date = self.date_start + timedelta(seconds=itm.data(0))
                    # model.item(itm.row(), 4).setData(QDateTime(date), 0)
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
                    # model.item(itm.row(), 4).setData(QDateTime(date), 0)
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
                    # model.item(itm.row(), 4).setData(QDateTime(date), 0)
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
                    # model.item(itm.row(), 4).setData(QDateTime(date), 0)
                    model.item(itm.row(), 4).setData(date.strftime('%d-%m-%Y %H:%M:%S'), 0)
                    model.blockSignals(False)
                # elif itm.column() == 4:
                #     model.blockSignals(True)
                #     time_sec = -itm.data(0).secsTo(self.ui.de_start.dateTime())
                #     if not model.item(itm.row(), 0):
                #         model.setItem(itm.row(), 0, QStandardItem())
                #     model.item(itm.row(), 0).setData(time_sec, 0)
                #     if not model.item(itm.row(), 1):
                #         model.setItem(itm.row(), 1, QStandardItem())
                #     model.item(itm.row(), 1).setData(time_sec / 60., 0)
                #     if not model.item(itm.row(), 2):
                #         model.setItem(itm.row(), 2, QStandardItem())
                #     model.item(itm.row(), 2).setData(time_sec / 3600., 0)
                #     if not model.item(itm.row(), 3):
                #         model.setItem(itm.row(), 3, QStandardItem())
                #     model.item(itm.row(), 3).setData(time_sec / 86400., 0)
                #     model.blockSignals(False)

            if not self.filling_tab:
                model.sort(0)
                idx = itm.index()
                self.ui.tab_sets.scrollTo(idx, 0)
                # self.update_courbe("all")

                # elif itm.column() > 4:
                #     if not self.filling_tab:
                #         idx = itm.index()
                #         self.update_courbe([idx.column() - 5])

    def update_courbe(self, courbes):
        data = {}
        if courbes == "all":
            courbes = range(self.ui.tab_sets.model().columnCount() - 5)

        col_x = self.bg_time.checkedId()
        lx = []
        for r in range(self.ui.tab_sets.model().rowCount()):
            if col_x != 4:
                lx.append(self.ui.tab_sets.model().item(r, col_x).data(0))
            else:
                date = self.date_ref + timedelta(seconds=self.ui.tab_sets.model().item(r, 0).data(0))
                # lx.append(date)
                lx.append(date2num(date))

        for crb in courbes:
            ly = []
            for r in range(self.ui.tab_sets.model().rowCount()):
                ly.append(self.ui.tab_sets.model().item(r, crb + 5).data(0))
            data[crb] = {"x": lx, "y": ly}

        self.graph_edit.majCourbes(data)



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
        for c in range(5, model.columnCount()):
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

    def chg_time(self, v):
        unit = ['s', 'min', 'h', 'day', 'date']
        for i in range(5):
            if i == v:
                self.ui.tab_sets.setColumnHidden(i, False)
            else:
                self.ui.tab_sets.setColumnHidden(i, True)
                # if not self.filling_tab:
                #     self.graph_edit.majUnitX(unit[v])
                #     self.update_courbe("all")

    def accept_page2(self):
        # save Info
        # modificaito liste page 1
        # change de page
        name_set = str(self.ui.txt_name.text())
        if self.ui.cb_date.isChecked():
            date, time = self.ui.de_date.date().toString('yyyy-MM-dd'), self.ui.de_date.time().toString('HH:mm:ss')
            date_set = "'{} {}'".format(date, time)
        else:
            date_set = 'Null'
        if self.cur_set == -1:
            if self.mgis.DEBUG:
                self.mgis.addInfo("Addition of {} Meteo Setting".format(name_set))
            self.mdb.execute("INSERT INTO {0}.meteo_config (name, starttime, active) VALUES ('{1}', {2}, 'f')".format(
                self.mdb.SCHEMA, name_set, date_set))
            res = self.mdb.run_query("SELECT Max(id) FROM {0}.meteo_config".format(self.mdb.SCHEMA), fetch=True)
            self.cur_set = res[0][0]
        else:
            if self.mgis.DEBUG:
                self.mgis.addInfo("Editing of {} Meteo Setting".format(name_set))
            self.mdb.execute(
                "UPDATE {0}.meteo_config SET name = '{1}', starttime = {2} WHERE id = {3}".format(self.mdb.SCHEMA,
                                                                                                  name_set, date_set,
                                                                                                  self.cur_set))
            self.mdb.execute("DELETE FROM {0}.laws_meteo WHERE id_config = {1}".format(self.mdb.SCHEMA, self.cur_set))

        recs = []
        for r in range(self.ui.tab_sets.model().rowCount()):
            for c in range(5, self.ui.tab_sets.model().columnCount()):
                recs.append([self.cur_set, self.list_var[c - 5][0], self.ui.tab_sets.model().item(r, 0).data(0),
                             self.ui.tab_sets.model().item(r, c).data(0)])

        self.mdb.run_query("INSERT INTO {0}.laws_meteo (id_config, id_var, time, value) VALUES (%s, %s, %s, %s)".format(
            self.mdb.SCHEMA), many=True, listMany=recs)

        self.fill_lst_conf(self.cur_set)
        self.ui.laws_pages.setCurrentIndex(0)
        self.graph_edit.initGraph(None, all_vis=True)

    def reject_page2(self):
        if self.mgis.DEBUG:
            self.mgis.addInfo("Cancel of Meteo Setting")
        self.ui.laws_pages.setCurrentIndex(0)
        # self.graph_edit.initGraph(None, all_vis=True)


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