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

from .ClassTableWQ import ClassTableWQ
from .Graph_WQ import GraphMeteo
from ..Function import data_to_float, data_to_date

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
    from qgis.PyQt.QtWidgets import *


class ClassMeteoDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbwq = ClassTableWQ(self.mgis, self.mdb)
        self.dico_var = self.tbwq.dico_meteo
        self.cur_set = None
        self.filling_tab = False
        self.graph_home = None
        self.graph_edit = None
        self.date_ref = None
        self.list_var = []

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_meteo.ui'),
                         self)
        self.ui.de_date.hide()
        self.ui.de_date.setDisplayFormat("dd/MM/yyyy HH:mm:ss")

        self.ui.tab_sets.sCut_del = QShortcut(QKeySequence("Del"), self)
        self.ui.tab_sets.sCut_del.activated.connect(self.short_cut_row_del)

        self.bg_time = QButtonGroup()
        self.bg_time.addButton(self.rb_sec, 0)
        self.bg_time.addButton(self.rb_min, 1)
        self.bg_time.addButton(self.rb_hour, 2)
        self.bg_time.addButton(self.rb_day, 3)
        self.bg_time.addButton(self.rb_date, 4)
        self.bg_time.buttonClicked[int].connect(self.chg_time)

        styled_item_delegate = QStyledItemDelegate()
        styled_item_delegate.setItemEditorFactory(ItemEditorFactory())
        self.ui.tab_sets.setItemDelegate(styled_item_delegate)

        self.ui.actionB_edit.triggered.connect(self.edit_set)
        self.ui.actionB_new.triggered.connect(self.new_set)
        self.ui.actionB_delete.triggered.connect(self.delete_set)
        self.ui.actionB_import.triggered.connect(self.import_csv)
        self.ui.actionB_addLine.triggered.connect(self.new_time)
        self.ui.actionB_delLine.triggered.connect(self.delete_time)
        self.ui.b_OK_page2.accepted.connect(self.accept_page2)
        self.ui.b_OK_page2.rejected.connect(self.reject_page2)
        self.ui.b_OK_page1.accepted.connect(self.reject)
        self.ui.cb_date.stateChanged.connect(self.check_date_ref)
        self.ui.de_date.dateTimeChanged.connect(self.change_date_ref)

        self.init_ui()

    def display_graph_home(self):
        """ Display graph"""
        if self.ui.lst_sets.selectedIndexes():
            l = self.ui.lst_sets.selectedIndexes()[0].row()
            config = int(self.ui.lst_sets.model().item(l, 0).text())
            self.graph_home.init_graph(config)
        else:
            self.graph_home.init_graph(None)

    def init_ui(self):
        """initialisation gui"""
        self.ui.meteo_pages.setCurrentIndex(0)
        self.graph_home = GraphMeteo(self.mgis, self.ui.lay_graph_home,
                                     self.dico_var)
        self.graph_edit = GraphMeteo(self.mgis, self.ui.lay_graph_edit,
                                     self.dico_var)
        self.fill_lst_conf()

    def fill_lst_conf(self, id=None):
        """ fill configuration list"""
        model = QStandardItemModel()
        model.setColumnCount(2)
        self.ui.lst_sets.setModel(model)
        self.ui.lst_sets.setModelColumn(1)
        self.ui.lst_sets.selectionModel().selectionChanged.connect(
            self.display_graph_home)

        sql = "SELECT * FROM {0}.meteo_config ORDER BY name".format(
            self.mdb.SCHEMA)
        rows = self.mdb.run_query(sql, fetch=True)

        for i, row in enumerate(rows):
            for j, field in enumerate(row):
                if j != 3:
                    new_itm = QStandardItem(str(row[j]))
                    new_itm.setEditable(False)
                    if j == 1:
                        new_itm.setCheckable(True)
                        if not row[3]:
                            new_itm.setCheckState(0)
                        elif row[3]:
                            new_itm.setCheckState(2)
                    self.ui.lst_sets.model().setItem(i, j, new_itm)

        self.ui.lst_sets.model().itemChanged.connect(self.sel_config_def)

        if id:
            for r in range(self.ui.lst_sets.model().rowCount()):
                if str(self.ui.lst_sets.model().item(r, 0).text()) == str(id):
                    self.ui.lst_sets.setCurrentIndex(
                        self.ui.lst_sets.model().item(r, 1).index())
                    break
        else:
            self.display_graph_home()

    def sel_config_def(self, itm):
        """
        Select configuration
        """
        self.ui.lst_sets.model().blockSignals(True)
        for r in range(self.ui.lst_sets.model().rowCount()):
            if r != itm.row():
                self.ui.lst_sets.model().item(r, 1).setCheckState(0)
        self.ui.lst_sets.model().blockSignals(False)

        sql = "UPDATE {0}.meteo_config SET active = 'f'".format(self.mdb.SCHEMA)
        self.mdb.run_query(sql)
        if itm.checkState() == 2:
            id = str(self.ui.lst_sets.model().item(itm.row(), 0).text())
            sql = "UPDATE {0}.meteo_config SET active = 't' WHERE id = {1}".format(
                self.mdb.SCHEMA, id)
            self.mdb.run_query(sql)

    def check_date_ref(self, state):
        """ check reference date"""
        if state == 0:
            self.ui.de_date.hide()
            self.ui.rb_date.hide()
            if self.bg_time.checkedId() == 4:
                self.rb_sec.click()
        else:
            self.ui.de_date.show()
            self.ui.rb_date.show()

    def change_date_ref(self):
        """ change reference date """
        date, time = self.ui.de_date.date().toString(
            'dd-MM-yyyy'), self.ui.de_date.time().toString('HH:mm:ss')
        date_str = "'{} {}'".format(date, time)
        self.date_ref = data_to_date(date_str)
        model = self.ui.tab_sets.model()
        if model:
            for r in range(model.rowCount()):
                if not model.item(r, 4):
                    date_itm = QStandardItem()
                    date_itm.setEditable(False)
                    model.setItem(r, 4, date_itm)
                date = self.date_ref + timedelta(
                    seconds=model.item(r, 0).data(0))
                model.item(r, 4).setData(str(date), 0)
            if self.bg_time.checkedId() == 4:
                self.update_courbe("all")

    def create_tab_model(self):
        """ create table"""
        self.list_var = []
        model = QStandardItemModel()
        model.insertColumns(0, 11)
        for c in range(5):
            model.setHeaderData(c, 1, 'time', 0)
        for c in range(5, 11):
            model.setHeaderData(c, 1, self.dico_var[c - 5]["name"], 0)
            self.list_var.append(
                [self.dico_var[c - 5]["id"], self.dico_var[c - 5]["name"]])

        model.itemChanged.connect(self.on_tab_data_change)
        return model

    def short_cut_row_del(self):
        """
        cut row
        """
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

    def fill_tab_sets(self):
        """ fill table"""
        self.filling_tab = True
        self.ui.tab_sets.setModel(self.create_tab_model())
        model = self.ui.tab_sets.model()

        if self.cur_set != -1:
            c = 0
            for var in self.list_var:
                sql = "SELECT time, value FROM {0}.laws_meteo WHERE id_config = {1} AND id_var = {2} " \
                      "ORDER BY time".format(self.mdb.SCHEMA, self.cur_set,
                                             var[0])
                rows = self.mdb.run_query(sql, fetch=True)

                if c == 0:
                    model.insertRows(0, len(rows))
                    for r, row in enumerate(rows):
                        itm = QStandardItem()
                        itm.setData(row[0] / 1., 0)
                        model.setItem(r, c, itm)
                    c = 5

                for r, row in enumerate(rows):
                    itm = QStandardItem()
                    itm.setData(row[1], 0)
                    model.setItem(r, c, itm)

                c += 1

        self.filling_tab = False
        self.rb_sec.click()

    def import_csv(self):
        """ Import csv file"""
        nb_col = 7
        typ_time = ''
        first_ligne = True
        if int(qVersion()[0]) < 5:  # qt4
            listf = QFileDialog.getOpenFileNames(None, 'File Selection',
                                                 self.mgis.repProject,
                                                 "File (*.txt *.csv *.met)")

        else:  # qt5
            listf, _ = QFileDialog.getOpenFileNames(None, 'File Selection',
                                                    self.mgis.repProject,
                                                    "File (*.txt *.csv *.met)")

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
                                typ_time = 'num'
                            else:
                                val = data_to_date(liste[0])
                                if val is not None:
                                    typ_time = 'date'
                                    date_ref = val
                                    self.ui.cb_date.setCheckState(2)
                                    date_ref_str = datetime.strftime(date_ref,
                                                                     '%Y-%m-%d %H:%M:%S')
                                    self.ui.de_date.setDateTime(
                                        QDateTime().fromString(date_ref_str,
                                                               'yyyy-MM-dd HH:mm:ss'))
                                else:
                                    # print('e1')
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
                    if not model.item(itm.row(), 4):
                        date_itm = QStandardItem()
                        date_itm.setEditable(False)
                        model.setItem(itm.row(), 4, date_itm)
                    date = self.date_ref + timedelta(seconds=itm.data(0))
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
                    date = self.date_ref + timedelta(minutes=itm.data(0))
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
                    date = self.date_ref + timedelta(hours=itm.data(0))
                    model.item(itm.row(), 4).setData(
                        date.strftime('%d-%m-%Y %H:%M:%S'), 0)
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
                    date = self.date_ref + timedelta(days=itm.data(0))
                    model.item(itm.row(), 4).setData(
                        date.strftime('%d-%m-%Y %H:%M:%S'), 0)
                    model.blockSignals(False)

            if not self.filling_tab:
                model.sort(0)
                idx = itm.index()
                self.ui.tab_sets.scrollTo(idx, 0)
                self.update_courbe("all")
        elif itm.column() > 4:
            if not self.filling_tab:
                idx = itm.index()
                self.update_courbe([idx.column() - 5])

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
                date = self.date_ref + timedelta(
                    seconds=self.ui.tab_sets.model().item(r, 0).data(0))
                # lx.append(date)
                lx.append(date2num(date))

        for crb in courbes:
            ly = []
            for r in range(self.ui.tab_sets.model().rowCount()):
                ly.append(self.ui.tab_sets.model().item(r, crb + 5).data(0))
            data[crb] = {"x": lx, "y": ly}

        self.graph_edit.maj_courbes(data)

    def new_set(self):
        # changer de page
        self.cur_set = -1
        self.ui.txt_name.setText('')
        self.ui.cb_date.setCheckState(0)
        date = QDateTime(QDate().currentDate(), QTime(0, 0, 0))
        self.ui.de_date.setDateTime(date)
        self.fill_tab_sets()
        self.ui.meteo_pages.setCurrentIndex(1)
        self.graph_edit.init_graph(None)

    def edit_set(self):
        # charger les informations
        # changer de page
        if self.ui.lst_sets.selectedIndexes():
            l = self.ui.lst_sets.selectedIndexes()[0].row()
            self.cur_set = int(self.ui.lst_sets.model().item(l, 0).text())
            self.ui.txt_name.setText(self.ui.lst_sets.model().item(l, 1).text())
            date_str = str(self.ui.lst_sets.model().item(l, 2).text())
            if date_str == 'None':
                self.ui.cb_date.setCheckState(0)
                date = QDateTime(QDate().currentDate(), QTime(0, 0, 0))
            else:
                self.ui.cb_date.setCheckState(2)
                date = QDateTime().fromString(date_str, 'yyyy-MM-dd HH:mm:ss')
            self.ui.de_date.setDateTime(date)
            self.fill_tab_sets()
            self.ui.meteo_pages.setCurrentIndex(1)
            self.graph_edit.init_graph(self.cur_set)

    def delete_set(self):
        # charger les informations
        # changer de page
        if self.ui.lst_sets.selectedIndexes():
            l = self.ui.lst_sets.selectedIndexes()[0].row()
            id_set = self.ui.lst_sets.model().item(l, 0).text()
            name_set = self.ui.lst_sets.model().item(l, 1).text()
            if (QMessageBox.question(self, "Meteo Settings",
                                     "Delete {} ?".format(name_set),
                                     QMessageBox.Cancel | QMessageBox.Ok)) == QMessageBox.Ok:
                if self.mgis.DEBUG:
                    self.mgis.add_info(
                        "Deletion of {} Meteo Setting".format(name_set))
                self.mdb.execute(
                    "DELETE FROM {0}.laws_meteo WHERE id_config = {1}".format(
                        self.mdb.SCHEMA, id_set))
                self.mdb.execute(
                    "DELETE FROM {0}.meteo_config WHERE id = {1}".format(
                        self.mdb.SCHEMA, id_set))
                self.fill_lst_conf()

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
        if not self.filling_tab:
            self.graph_edit.maj_unit_x(unit[v])
            self.update_courbe("all")

    def accept_page2(self):
        # save Info
        # modificaito liste page 1
        # change de page
        name_set = str(self.ui.txt_name.text())
        if self.ui.cb_date.isChecked():
            date, time = self.ui.de_date.date().toString(
                'yyyy-MM-dd'), self.ui.de_date.time().toString('HH:mm:ss')
            date_set = "'{} {}'".format(date, time)
        else:
            date_set = 'Null'
        if self.cur_set == -1:
            if self.mgis.DEBUG:
                self.mgis.add_info(
                    "Addition of {} Meteo Setting".format(name_set))
            self.mdb.execute(
                "INSERT INTO {0}.meteo_config (name, starttime, active) VALUES ('{1}', {2}, 'f')".format(
                    self.mdb.SCHEMA, name_set, date_set))
            res = self.mdb.run_query(
                "SELECT Max(id) FROM {0}.meteo_config".format(self.mdb.SCHEMA),
                fetch=True)
            self.cur_set = res[0][0]
        else:
            if self.mgis.DEBUG:
                self.mgis.add_info(
                    "Editing of {} Meteo Setting".format(name_set))
            self.mdb.execute(
                "UPDATE {0}.meteo_config SET name = '{1}', starttime = {2} WHERE id = {3}".format(
                    self.mdb.SCHEMA,
                    name_set, date_set,
                    self.cur_set))
            self.mdb.execute(
                "DELETE FROM {0}.laws_meteo WHERE id_config = {1}".format(
                    self.mdb.SCHEMA, self.cur_set))

        recs = []
        for r in range(self.ui.tab_sets.model().rowCount()):
            for c in range(5, self.ui.tab_sets.model().columnCount()):
                recs.append([self.cur_set, self.list_var[c - 5][0],
                             self.ui.tab_sets.model().item(r, 0).data(0),
                             self.ui.tab_sets.model().item(r, c).data(0)])

        self.mdb.run_query(
            "INSERT INTO {0}.laws_meteo (id_config, id_var, time, value) VALUES (%s, %s, %s, %s)".format(
                self.mdb.SCHEMA), many=True, list_many=recs)

        self.fill_lst_conf(self.cur_set)
        self.ui.meteo_pages.setCurrentIndex(0)
        self.graph_edit.init_graph(None, all_vis=True)

    def reject_page2(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Meteo Setting")
        self.ui.meteo_pages.setCurrentIndex(0)
        self.graph_edit.init_graph(None, all_vis=True)


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
