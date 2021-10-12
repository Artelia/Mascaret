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
from .Graph_WQ import GraphWaterQ
from ..Function import data_to_float

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
    from qgis.PyQt.QtWidgets import *


class ClassTracerLawsDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbwq = ClassTableWQ(self.mgis, self.mdb)
        self.cur_wq_mod = self.tbwq.get_cur_wq_mod()
        self.cur_wq_law = None
        self.filling_tab = False
        self.graph_home = None
        self.graph_edit = None
        self.list_trac = []

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_tracer_laws.ui'), self)

        self.ui.tab_laws.sCut_del = QShortcut(QKeySequence("Del"), self)
        self.ui.tab_laws.sCut_del.activated.connect(self.short_cut_row_del)

        self.bg_time = QButtonGroup()
        self.bg_time.addButton(self.rb_sec, 0)
        self.bg_time.addButton(self.rb_min, 1)
        self.bg_time.addButton(self.rb_hour, 2)
        self.bg_time.addButton(self.rb_day, 3)
        self.bg_time.buttonClicked[int].connect(self.chg_time)

        styled_item_delegate = QStyledItemDelegate()
        styled_item_delegate.setItemEditorFactory(ItemEditorFactory())
        self.ui.tab_laws.setItemDelegate(styled_item_delegate)

        self.ui.actionB_edit.triggered.connect(self.edit_law)
        self.ui.actionB_new.triggered.connect(self.new_law)
        self.ui.actionB_delete.triggered.connect(self.delete_law)
        self.ui.actionB_import.triggered.connect(self.import_csv)
        self.ui.actionB_addLine.triggered.connect(self.new_time)
        self.ui.actionB_delLine.triggered.connect(self.delete_time)
        self.ui.b_OK_page2.accepted.connect(self.accept_page2)
        self.ui.b_OK_page2.rejected.connect(self.reject_page2)
        self.ui.b_OK_page1.accepted.connect(self.reject)

        self.init_ui()

    def display_graph_home(self):
        if self.ui.lst_laws.selectedIndexes():
            l = self.ui.lst_laws.selectedIndexes()[0].row()
            config = int(self.ui.lst_laws.model().item(l, 0).text())
            self.graph_home.init_graph(config)
        else:
            self.graph_home.init_graph(None)

    def init_ui(self):
        self.ui.Law_pages.setCurrentIndex(0)
        self.graph_home = GraphWaterQ(self.mgis, self.ui.lay_graph_home,
                                      self.tbwq.dico_wq_mod[self.cur_wq_mod])
        self.graph_edit = GraphWaterQ(self.mgis, self.ui.lay_graph_edit,
                                      self.tbwq.dico_wq_mod[self.cur_wq_mod])
        self.fill_lst_conf()

    def fill_lst_conf(self, id=None):
        model = QStandardItemModel()
        model.setColumnCount(2)
        self.ui.lst_laws.setModel(model)
        self.ui.lst_laws.setModelColumn(1)
        self.ui.lst_laws.selectionModel().selectionChanged.connect(
            self.display_graph_home)

        sql = "SELECT * FROM {0}.tracer_config WHERE type = {1} ORDER BY name".format(
            self.mdb.SCHEMA, self.cur_wq_mod)
        rows = self.mdb.run_query(sql, fetch=True)

        for i, row in enumerate(rows):
            for j, field in enumerate(row):
                new_itm = QStandardItem(str(row[j]))
                new_itm.setEditable(False)
                # new_itm.setCheckable(True)
                # new_itm.setCheckState(0)
                self.ui.lst_laws.model().setItem(i, j, new_itm)

        if id:
            for r in range(self.ui.lst_laws.model().rowCount()):
                if str(self.ui.lst_laws.model().item(r, 0).text()) == str(id):
                    self.ui.lst_laws.setCurrentIndex(
                        self.ui.lst_laws.model().item(r, 1).index())
                    break
        else:
            self.display_graph_home()

    def create_tab_model(self):
        self.list_trac = []
        model = QStandardItemModel()
        model.insertColumns(0, 4)
        for c in range(4):
            model.setHeaderData(c, 1, 'time', 0)

        sql = "SELECT id, sigle FROM {0}.tracer_name WHERE type = '{1}' ORDER BY id".format(
            self.mdb.SCHEMA,
            self.tbwq.dico_wq_mod[
                self.cur_wq_mod])
        rows = self.mdb.run_query(sql, fetch=True)
        model.insertColumns(4, len(rows))
        for r, row in enumerate(rows):
            model.setHeaderData(r + 4, 1, row[1], 0)
            self.list_trac.append([row[0], row[1]])

        model.itemChanged.connect(self.on_tab_data_change)
        return model

    def short_cut_row_del(self):
        if self.ui.tab_laws.hasFocus():
            cols = []
            model = self.ui.tab_laws.model()
            selection = self.ui.tab_laws.selectedIndexes()
            for idx in selection:
                if idx.column() > 3:
                    model.item(idx.row(), idx.column()).setData(None, 0)
                    cols.append(idx.column() - 4)
            cols = list(set(cols))
            self.update_courbe(cols)

    def fill_tab_laws(self):
        self.filling_tab = True
        self.ui.tab_laws.setModel(self.create_tab_model())
        model = self.ui.tab_laws.model()

        if self.cur_wq_law != -1:
            c = 0
            for trac in self.list_trac:
                sql = "SELECT time, value FROM {0}.laws_wq WHERE id_config = {1} AND id_trac = {2} " \
                      "ORDER BY time".format(self.mdb.SCHEMA, self.cur_wq_law,
                                             trac[0])
                rows = self.mdb.run_query(sql, fetch=True)

                if c == 0:
                    model.insertRows(0, len(rows))
                    for r, row in enumerate(rows):
                        itm = QStandardItem()
                        itm.setData(row[0] / 1., 0)
                        model.setItem(r, c, itm)
                    c = 4

                for r, row in enumerate(rows):
                    itm = QStandardItem()
                    itm.setData(row[1], 0)
                    model.setItem(r, c, itm)

                c += 1

        self.filling_tab = False
        self.rb_sec.click()

    def import_csv(self):
        """ import CSV file"""
        nb_col = len(self.list_trac) + 1
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
            filein = open(listf[0], "r")
            r = 0
            for num_ligne, ligne in enumerate(filein):
                if ligne[0] != '#':
                    liste = ligne.split(";")
                    if len(liste) == nb_col:
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
                        error = True
                        break
            filein.close()
            self.filling_tab = False

            if not error:
                self.ui.tab_laws.setModel(model)
                self.update_courbe("all")
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info("Import failed ({})".format(listf[0]))

    def on_tab_data_change(self, itm):
        if itm.column() < 4:
            model = itm.model()
            # model = self.ui.tab_laws.model()
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
                self.ui.tab_laws.scrollTo(idx, 0)
                self.update_courbe("all")
        else:
            if not self.filling_tab:
                idx = itm.index()
                self.update_courbe([idx.column() - 4])

    def update_courbe(self, courbes):
        data = {}
        if courbes == "all":
            courbes = range(self.ui.tab_laws.model().columnCount() - 4)

        col_x = self.bg_time.checkedId()
        lx = []
        for r in range(self.ui.tab_laws.model().rowCount()):
            lx.append(self.ui.tab_laws.model().item(r, col_x).data(0))

        for crb in courbes:
            ly = []
            for r in range(self.ui.tab_laws.model().rowCount()):
                ly.append(self.ui.tab_laws.model().item(r, crb + 4).data(0))
            data[crb] = {"x": lx, "y": ly}

        self.graph_edit.maj_courbes(data)

    def new_law(self):
        # changer de page
        self.cur_wq_law = -1
        self.ui.LawWQ.setText('')
        self.fill_tab_laws()
        self.ui.Law_pages.setCurrentIndex(1)
        self.graph_edit.init_graph(None)

    def edit_law(self):
        # charger les informations
        # changer de page
        if self.ui.lst_laws.selectedIndexes():
            l = self.ui.lst_laws.selectedIndexes()[0].row()
            self.cur_wq_law = int(self.ui.lst_laws.model().item(l, 0).text())
            self.ui.LawWQ.setText(self.ui.lst_laws.model().item(l, 1).text())
            self.fill_tab_laws()
            self.ui.Law_pages.setCurrentIndex(1)
            self.graph_edit.init_graph(self.cur_wq_law)

    def delete_law(self):
        # charger les informations
        # changer de page
        if self.ui.lst_laws.selectedIndexes():
            l = self.ui.lst_laws.selectedIndexes()[0].row()
            id_law = self.ui.lst_laws.model().item(l, 0).text()
            name_law = self.ui.lst_laws.model().item(l, 1).text()
            if (QMessageBox.question(self, "Tracer Laws",
                                     "Delete {} ?".format(name_law),
                                     QMessageBox.Cancel | QMessageBox.Ok)) == QMessageBox.Ok:
                if self.mgis.DEBUG:
                    self.mgis.add_info(
                        "Deletion of {} Tracer Laws".format(name_law))
                self.mdb.execute(
                    "DELETE FROM {0}.laws_wq WHERE id_config = {1}".format(
                        self.mdb.SCHEMA, id_law))
                self.mdb.execute(
                    "DELETE FROM {0}.tracer_config WHERE id = {1}".format(
                        self.mdb.SCHEMA, id_law))
                self.fill_lst_conf()

    def new_time(self):
        self.filling_tab = True
        model = self.ui.tab_laws.model()
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
        self.ui.tab_laws.scrollToBottom()
        self.filling_tab = False
        self.update_courbe("all")

    def delete_time(self):
        if self.ui.tab_laws.selectedIndexes():
            rows = [idx.row() for idx in self.ui.tab_laws.selectedIndexes()]
            rows = list(set(rows))
            rows.sort(reverse=True)
            for row in rows:
                model = self.ui.tab_laws.model()
                model.removeRow(row)
            self.update_courbe("all")

    def chg_time(self, v):
        unit = ['s', 'min', 'h', 'day']
        for i in range(4):
            if i == v:
                self.ui.tab_laws.setColumnHidden(i, False)
            else:
                self.ui.tab_laws.setColumnHidden(i, True)
        if not self.filling_tab:
            self.graph_edit.maj_unit_x(unit[v])
            self.update_courbe("all")

    def accept_page2(self):
        # save Info
        # modificaito liste page 1
        # change de page
        if self.ui.tab_laws.model().rowCount() > 0:
            name_law = str(self.ui.LawWQ.text())
            if self.cur_wq_law == -1:
                if self.mgis.DEBUG:
                    self.mgis.add_info(
                        "Addition of {} Tracer Laws".format(name_law))
                self.mdb.execute(
                    "INSERT INTO {0}.tracer_config (name, type) VALUES ('{1}', {2})".format(
                        self.mdb.SCHEMA, name_law,
                        self.cur_wq_mod))
                res = self.mdb.run_query(
                    "SELECT Max(id) FROM {0}.tracer_config".format(
                        self.mdb.SCHEMA), fetch=True)
                self.cur_wq_law = res[0][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info(
                        "Editing of {} Tracer Laws".format(name_law))
                self.mdb.execute(
                    "UPDATE {0}.tracer_config SET name = '{1}' WHERE id = {2}".format(
                        self.mdb.SCHEMA, name_law,
                        self.cur_wq_law))
                self.mdb.execute(
                    "DELETE FROM {0}.laws_wq WHERE id_config = {1}".format(
                        self.mdb.SCHEMA, self.cur_wq_law))

            recs = []
            for r in range(self.ui.tab_laws.model().rowCount()):
                for c in range(4, self.ui.tab_laws.model().columnCount()):
                    recs.append([self.cur_wq_law, self.list_trac[c - 4][0],
                                 self.ui.tab_laws.model().item(r, 0).data(0),
                                 self.ui.tab_laws.model().item(r, c).data(0)])
            self.mdb.run_query(
                "INSERT INTO {0}.laws_wq (id_config, id_trac, time, value) VALUES (%s, %s, %s, %s)".format(
                    self.mdb.SCHEMA), many=True, list_many=recs)

            self.fill_lst_conf(self.cur_wq_law)
            self.ui.Law_pages.setCurrentIndex(0)
            self.graph_edit.init_graph(None, all_vis=True)
        else:
            self.reject_page2()

    def reject_page2(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Tracer Laws")
        self.ui.Law_pages.setCurrentIndex(0)
        self.graph_edit.init_graph(None, all_vis=True)


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
