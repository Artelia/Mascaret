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
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .FctDialog import ctrl_set_value, ctrl_get_value, fill_qcombobox
from ...Function import data_to_float
from ...Graphic.GraphCommon import GraphCommon


class ClassMobilObjectMet3Widget(QWidget):
    widget_closed = pyqtSignal()

    def __init__(self, mgis, typ_obj):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_obj = typ_obj
        self.cur_obj = int()
        self.filling_tab = False
        self.graph = None

        self.ui = loadUi(os.path.join(self.mgis.masplugPath,
                                      "ui/structures/ui_mobil_object_met3.ui"),
                         self)

        if self.typ_obj == 'weir':
            self.obj_table = 'weirs'
            self.mob_table = 'weirs_mob_val'
            self.mob_table_id = 'id_weirs'
            self.ui.tit_break.hide()
            self.ui.line_break.hide()
            self.ui.grp_break.hide()
        elif self.typ_obj == 'link':
            self.obj_table = 'links'
            self.mob_table = 'links_mob_val'
            self.mob_table_id = 'id_links'

        self.d_var = {
            "METHBREAK": {"ctrl": self.ui.cb_break_met, "cc": self.ui.cc_method,
                          "vdef": '1', "typ": str},
            "TBREAKFUS": {"ctrl": self.ui.sb_break_time, "cc": None,
                          "vdef": 0., "typ": float},
            "UNITTBREAKFUS": {"ctrl": self.ui.cb_unit_break_time, "cc": None,
                              "vdef": 1, "typ": int},
            "VFUS": {"ctrl": self.ui.cb_var_break, "cc": self.ui.cc_break_var,
                     "vdef": 'Z', "typ": str},
            "USEBASINFUS": {"ctrl": self.ui.cb_typ_control, "cc": self.ui.cc_control,
                            "vdef": False, "typ": to_bool},
            "NUMBASINFUS": {"ctrl": self.ui.cb_basin, "cc": self.ui.cc_control,
                            "vdef": 0, "typ": int},
            "PKFUS": {"ctrl": self.ui.sb_abscissa, "cc": self.ui.cc_control,
                      "vdef": 0., "typ": float},
            "VBREAKFUS": {"ctrl": self.ui.sb_break_lvl, "cc": None,
                          "vdef": 0., "typ": float},
            "ZFINALFUS": {"ctrl": self.ui.sb_after_lvl, "cc": None,
                          "vdef": 0., "typ": float},
            "WRITEFUS": {"ctrl": self.ui.sb_step_write, "cc": self.ui.cc_write,
                         "vdef": 1, "typ": int},
        }

        self.bg_time = QButtonGroup()
        self.bg_time.addButton(self.rb_sec, 0)
        self.bg_time.addButton(self.rb_min, 1)
        self.bg_time.addButton(self.rb_hour, 2)
        self.bg_time.addButton(self.rb_day, 3)
        self.bg_time.buttonClicked[int].connect(self.chg_time)

        self.ui.actionB_addLine.triggered.connect(self.new_time)
        self.ui.actionB_delLine.triggered.connect(self.delete_time)
        self.ui.actionB_import.triggered.connect(self.import_csv)
        self.ui.actionB_delete.triggered.connect(self.clear_table)

        self.ui.tab_sets.sCut_del = QShortcut(QKeySequence("Del"), self)
        self.ui.tab_sets.sCut_del.activated.connect(self.short_cut_row_del)

        styled_item_delegate = QStyledItemDelegate()
        styled_item_delegate.setItemEditorFactory(ItemEditorFactory())
        self.ui.tab_sets.setItemDelegate(styled_item_delegate)

        self.ui.cc_method.toggled.connect(self.enab_method)
        self.ui.cb_break_met.currentIndexChanged.connect(self.method_changed)
        self.ui.cc_write.toggled.connect(self.enab_write)

        #
        self.ui.cc_break_var.toggled.connect(self.enab_variable_break)
        self.ui.cb_var_break.currentIndexChanged.connect(self.variable_break_changed)

        self.ui.cc_control.toggled.connect(self.enab_control)
        self.ui.cb_typ_control.currentIndexChanged.connect(self.control_type_changed)

        self.ui.b_valid.accepted.connect(self.save_input)
        self.ui.b_valid.rejected.connect(self.cancel_input)
        self.init_ui()

    def init_ui(self):
        """initialisation gui"""
        fill_qcombobox(self.ui.cb_break_met, [["1", "Break at a time"],
                                              ["2", "Break at a value"]])

        fill_qcombobox(self.ui.cb_unit_break_time, [[1, "Seconds"],
                                                    [60, "Minutes"],
                                                    [3600, "Hours"],
                                                    [86400, "Days"]])

        fill_qcombobox(self.ui.cb_var_break, [["Z", "Water level"],
                                              ["Q", "Flow rate"]])

        fill_qcombobox(self.ui.cb_typ_control, [[False, "Abscissa"],
                                                [True, "Basin"]])

        mdl = self.create_tab_model()
        self.ui.tab_sets.setModel(mdl)
        self.graph = GraphMobSing(self.mgis, self.ui.lay_graph_m1)

    def enab_write(self, cs):
        self.ui.sb_step_write.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_step_write)

    def enab_method(self, cs):
        self.ui.cb_break_met.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.cb_break_met)

    def method_changed(self, idx):
        if idx == 1:
            self.ui.grp_time.hide()
            self.ui.grp_lvl.show()
        else:
            self.ui.cc_control.setChecked(False)

            self.ui.grp_lvl.hide()
            self.ui.grp_time.show()

    def enab_variable_break(self, cs):
        self.ui.cb_var_break.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.cb_var_break)

    def variable_break_changed(self, idx):
        if idx == 1:
            self.ui.sb_break_lvl.setSuffix(" m³/s")
        else:
            self.ui.sb_break_lvl.setSuffix(" m")

    def enab_control(self, cs):
        self.ui.cb_typ_control.setEnabled(cs)
        self.ui.sb_abscissa.setEnabled(cs)
        self.ui.cb_basin.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.cb_typ_control)
            self.set_def_ctrl_value(self.ui.sb_abscissa)
            self.set_def_ctrl_value(self.ui.cb_basin)

    def control_type_changed(self, idx):
        self.ui.cc_break_var.setChecked(True)
        self.ui.cc_break_var.setChecked(False)
        if idx == 1:
            self.ui.sb_abscissa.hide()
            self.ui.cb_basin.show()
            self.ui.cc_break_var.setEnabled(False)
        else:
            self.ui.cb_basin.hide()
            self.ui.sb_abscissa.show()
            self.ui.cc_break_var.setEnabled(True)

    def create_tab_model(self):
        """create table"""
        model = QStandardItemModel()
        model.insertColumns(0, 5)
        for c in range(4):
            model.setHeaderData(c, 1, "time", 0)

        model.setHeaderData(4, 1, "width (m)", 0)

        model.itemChanged.connect(self.on_tab_data_change)
        return model

    def load_object(self, object_id):
        self.cur_obj = object_id

        if self.typ_obj == 'link':
            sql = "SELECT type, nature, COALESCE(abscissa, 0.) as absc, COALESCE(links.level, 0.) as lvl, " \
                  "basinstart, bas_sta.name, basinend , bas_end.name " \
                  "FROM ({0}.{1} " \
                  "LEFT JOIN {0}.basins as bas_sta on basinstart = bas_sta.basinnum) " \
                  "LEFT JOIN {0}.basins as bas_end on basinend = bas_end.basinnum " \
                  "WHERE links.gid = {2}".format(self.mdb.SCHEMA, self.obj_table, self.cur_obj)
            rows = self.mdb.run_query(sql, fetch=True)
            typ_link, nat_link, cur_abs, cur_z, b_sta_id, b_sta_name, b_end_id, b_end_name = rows[0]

            if str(nat_link) != '2':
                fill_qcombobox(self.ui.cb_basin, [[b_sta_id, b_sta_name]])
                self.d_var["USEBASINFUS"]["vdef"] = False
                self.ui.cb_typ_control.show()
            else:
                fill_qcombobox(self.ui.cb_basin, [[b_sta_id, "Start basin ({})".format(b_sta_name)],
                                                  [b_end_id, "End basin ({})".format(b_end_name)]])
                self.d_var["USEBASINFUS"]["vdef"] = True
                self.ui.cb_typ_control.hide()

            self.d_var["ZFINALFUS"]["vdef"] = cur_z
            self.d_var["PKFUS"]["vdef"] = cur_abs
            self.d_var["NUMBASINFUS"]["vdef"] = b_sta_id

        self.fill_controls()
        self.fill_table()

    def input_def_values(self):
        self.clear_controls()
        for k, prm in self.d_var.items():
            if prm["cc"]:
                prm["cc"].setChecked(False)

    def set_def_ctrl_value(self, ctrl):
        for prm in self.d_var.values():
            if prm["ctrl"] == ctrl:
                if "vdef" in prm.keys():
                    ctrl_set_value(ctrl, prm["vdef"], cc_is_checked=True)
                if "cdef" in prm.keys():
                    ctrl_set_value(ctrl, ctrl_get_value(prm["cdef"], cc_is_checked=True))

    def fill_controls(self):
        """fill table"""
        self.input_def_values()

        if self.cur_obj:
            l_var = list(self.d_var.keys())
            txt_var = "('{}')".format("', '".join(l_var))

            d_rec = dict()
            sql = "SELECT name_var, id_order, value FROM {0}.{1} WHERE {2} = {3} " \
                  "AND name_var IN {4}".format(self.mdb.SCHEMA, self.mob_table,
                                               self.mob_table_id, self.cur_obj, txt_var)
            rows = self.mdb.run_query(sql, fetch=True)
            for (nm_var, rang_var, value) in rows:
                d_rec[nm_var] = {"def": rang_var, "val": value}

            for nm_prm, saved_prm in d_rec.items():
                prm = self.d_var[nm_prm]
                conv_value = prm["typ"](saved_prm["val"])
                if nm_prm == "TBREAKFUS" and "UNITTBREAKFUS" in d_rec.keys():
                    conv_value = conv_value / float(d_rec["UNITTBREAKFUS"]["val"])

                ctrl_set_value(prm["ctrl"], conv_value, cc_is_checked=True)
                if prm["cc"] and saved_prm["def"] == 0:
                    prm["cc"].setChecked(True)

    def clear_controls(self):
        for k, prm in self.d_var.items():
            if prm["cc"]:
                prm["cc"].setChecked(True)
            self.set_def_ctrl_value(prm["ctrl"])

    def unload_object(self):
        self.cur_obj = int()
        self.clear_table()

    def clear_table(self):
        self.filling_tab = True
        mdl = self.ui.tab_sets.model()
        list_id = sorted(range(mdl.rowCount()), reverse=True)
        for num in list_id:
            mdl.removeRow(num)
        self.filling_tab = False

        self.update_courbe()

    def fill_table(self):
        """fill table"""
        self.clear_table()

        if self.cur_obj:
            self.filling_tab = True
            mdl = self.ui.tab_sets.model()
            c = 0
            for var in ["TIMEFUS", "WIDTHFUS"]:
                sql = "SELECT cast(value as float) FROM {0}.{1} " \
                      "WHERE {2} = {3} AND name_var = '{4}' " \
                      "ORDER BY id_order".format(self.mdb.SCHEMA,
                                                 self.mob_table,
                                                 self.mob_table_id,
                                                 self.cur_obj,
                                                 var)

                rows = self.mdb.run_query(sql, fetch=True)

                if var == "TIMEFUS":
                    mdl.insertRows(0, len(rows))
                    for r, row in enumerate(rows):
                        itm = QStandardItem()
                        itm.setData(row[0] / 1.0, 0)
                        mdl.setItem(r, c, itm)
                    c = 4
                else:
                    for r, row in enumerate(rows):
                        itm = QStandardItem()
                        itm.setData(row[0], 0)
                        mdl.setItem(r, c, itm)

        self.filling_tab = False

        self.rb_sec.click()

    def save_input(self):
        try:
            l_var = list(self.d_var.keys())
            l_var.extend(["TIMEFUS", "WIDTHFUS"])
            txt_var = "('{}')".format("', '".join(l_var))

            sql = "DELETE FROM {0}.{1} WHERE {2} = {3} " \
                  "AND name_var IN {4}".format(self.mdb.SCHEMA, self.mob_table,
                                               self.mob_table_id, self.cur_obj, txt_var)

            self.mdb.execute(sql)

            recs = []
            for row in range(self.ui.tab_sets.model().rowCount()):
                recs.append([self.cur_obj, row, "TIMEFUS", self.ui.tab_sets.model().item(row, 0).data(0)])
                recs.append([self.cur_obj, row, "WIDTHFUS", self.ui.tab_sets.model().item(row, 4).data(0)])

            if self.typ_obj == 'link':
                for nm_var, prm in self.d_var.items():
                    idx_time = 0
                    if prm["cc"]:
                        if not prm["cc"].isChecked():
                            idx_time = -1

                    val = ctrl_get_value(prm["ctrl"], cc_is_checked=True)
                    if nm_var == "TBREAKFUS":
                        unit = ctrl_get_value(self.ui.cb_unit_break_time, cc_is_checked=True)
                        val = val * unit

                    recs.append([self.cur_obj, idx_time, nm_var, val])

            sql = "INSERT INTO {0}.{1} ({2}, id_order, name_var, value) " \
                  "VALUES (%s, %s, %s, cast(%s as text))".format(self.mdb.SCHEMA,
                                                                 self.mob_table,
                                                                 self.mob_table_id)

            self.mdb.run_query(sql, many=True, list_many=recs)
            self.clear_table()
            self.widget_closed.emit()

        except Exception:
            self.cancel_input()
            self.mgis.add_info("Cancel of {0} information".format(self.obj_table))

    def cancel_input(self):
        self.clear_table()
        self.widget_closed.emit()

    def chg_time(self, v):
        unit = ["s", "min", "h", "day"]
        for i in range(4):
            if i == v:
                self.ui.tab_sets.setColumnHidden(i, False)
            else:
                self.ui.tab_sets.setColumnHidden(i, True)

        if not self.filling_tab:
            self.graph.maj_unit_x(unit[v])
            self.update_courbe()

    def new_time(self):
        self.filling_tab = True

        mdl = self.ui.tab_sets.model()

        r = mdl.rowCount()
        mdl.insertRow(r)
        itm = QStandardItem()
        if r == 0:
            val = 0.0
        elif r == 1:
            val = mdl.item(r - 1).data(0) + 1
        else:
            val = 2 * mdl.item(r - 1).data(0) - mdl.item(r - 2).data(0)
        itm.setData(val, 0)
        mdl.setItem(r, 0, itm)
        for c in range(4, mdl.columnCount()):
            mdl.setItem(r, c, QStandardItem())
        self.ui.tab_sets.scrollToBottom()
        self.filling_tab = False
        self.update_courbe()

    def delete_time(self):
        if self.ui.tab_sets.selectedIndexes():
            rows = [idx.row() for idx in self.ui.tab_sets.selectedIndexes()]
            rows = list(set(rows))
            rows.sort(reverse=True)
            for row in rows:
                mdl = self.ui.tab_sets.model()
                mdl.removeRow(row)
            self.update_courbe()

    def short_cut_row_del(self):
        """
        cut row
        """
        if self.ui.tab_sets.hasFocus():
            self.filling_tab = True
            mdl = self.ui.tab_sets.model()
            selection = self.ui.tab_sets.selectedIndexes()
            for idx in selection:
                if idx.column() > 3:
                    mdl.item(idx.row(), idx.column()).setData(None, 0)
            self.filling_tab = False

            self.update_courbe()

    def import_csv(self):
        """Import csv file"""
        nb_col = 2
        first_ligne = True
        listf, _ = QFileDialog.getOpenFileNames(
            None, "File Selection", self.mgis.repProject, "File (*.txt *.csv)"
        )
        if listf:
            self.mgis.up_rep_project(listf[0])
            error = False
            self.filling_tab = True
            mdl = self.ui.tab_sets.model()
            r = 0

            filein = open(listf[0], "r")
            for num_ligne, ligne in enumerate(filein):
                if ligne[0] != "#":
                    liste = ligne.replace("\n", "").replace("\t", " ").split(";")
                    if len(liste) == nb_col:
                        if first_ligne:
                            val = data_to_float(liste[0])
                            if val is not None:
                                self.mgis.add_info("Error the value is not float.")
                            first_ligne = False
                        mdl.insertRow(r)
                        for c, val in enumerate(liste):
                            itm = QStandardItem()
                            itm.setData(data_to_float(val), 0)
                            if c == 0:
                                mdl.setItem(r, c, itm)
                            else:
                                mdl.setItem(r, c + 3, itm)
                        r += 1
                    else:
                        # print('e2')
                        error = True
                        break
            filein.close()
            self.filling_tab = False

            if not error:
                self.update_courbe()
            else:
                self.mgis.add_info("Import failed ({})".format(listf[0]), dbg=True)

    def on_tab_data_change(self, itm):
        if itm.column() < 4:
            model = itm.model()
            if itm.data(0) or itm.data(0) == 0.0:
                if itm.column() == 0:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 1):
                        model.setItem(itm.row(), 1, QStandardItem())
                    model.item(itm.row(), 1).setData(itm.data(0) / 60.0, 0)
                    if not model.item(itm.row(), 2):
                        model.setItem(itm.row(), 2, QStandardItem())
                    model.item(itm.row(), 2).setData(itm.data(0) / 3600.0, 0)
                    if not model.item(itm.row(), 3):
                        model.setItem(itm.row(), 3, QStandardItem())
                    model.item(itm.row(), 3).setData(itm.data(0) / 86400.0, 0)
                    model.blockSignals(False)
                elif itm.column() == 1:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 0):
                        model.setItem(itm.row(), 0, QStandardItem())
                    model.item(itm.row(), 0).setData(itm.data(0) * 60.0, 0)
                    if not model.item(itm.row(), 2):
                        model.setItem(itm.row(), 2, QStandardItem())
                    model.item(itm.row(), 2).setData(itm.data(0) / 60.0, 0)
                    if not model.item(itm.row(), 3):
                        model.setItem(itm.row(), 3, QStandardItem())
                    model.item(itm.row(), 3).setData(itm.data(0) / 1440.0, 0)
                    model.blockSignals(False)
                elif itm.column() == 2:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 0):
                        model.setItem(itm.row(), 0, QStandardItem())
                    model.item(itm.row(), 0).setData(itm.data(0) * 3600.0, 0)
                    if not model.item(itm.row(), 1):
                        model.setItem(itm.row(), 1, QStandardItem())
                    model.item(itm.row(), 1).setData(itm.data(0) * 60.0, 0)
                    if not model.item(itm.row(), 3):
                        model.setItem(itm.row(), 3, QStandardItem())
                    model.item(itm.row(), 3).setData(itm.data(0) / 24.0, 0)
                    model.blockSignals(False)
                elif itm.column() == 3:
                    model.blockSignals(True)
                    if not model.item(itm.row(), 0):
                        model.setItem(itm.row(), 0, QStandardItem())
                    model.item(itm.row(), 0).setData(itm.data(0) * 86400.0, 0)
                    if not model.item(itm.row(), 1):
                        model.setItem(itm.row(), 1, QStandardItem())
                    model.item(itm.row(), 1).setData(itm.data(0) * 1440.0, 0)
                    if not model.item(itm.row(), 2):
                        model.setItem(itm.row(), 2, QStandardItem())
                    model.item(itm.row(), 2).setData(itm.data(0) * 24.0, 0)
                    model.blockSignals(False)

            if not self.filling_tab:
                model.sort(0)
                idx = itm.index()
                self.ui.tab_sets.scrollTo(idx, 0)

        if not self.filling_tab:
            self.update_courbe()

    def update_courbe(self):
        data = {}

        col_x = self.bg_time.checkedId()
        lx = []
        ly = []

        for r in range(self.ui.tab_sets.model().rowCount()):
            lx.append(self.ui.tab_sets.model().item(r, col_x).data(0))
            ly.append(self.ui.tab_sets.model().item(r, 4).data(0))

        data[0] = {"x": lx, "y": ly}

        self.graph.maj_courbes(data)


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
            double_spin_box.setMinimum(-1000000000.0)  # The default maximum value is 99.99.
            double_spin_box.setMaximum(1000000000.0)  # The default maximum value is 99.99.
            return double_spin_box
        else:
            return ItemEditorFactory.createEditor(user_type, parent)


class GraphMobSing(GraphCommon):
    """class Dialog"""

    def __init__(self, mgis=None, lay=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.init_ui_common_p()
        self.courbe = {}
        self.axes = None
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis="both", labelsize=7.0)
        self.axes.grid(True)

        self.courbe, = self.axes.plot([], [], zorder=100, label="Width (m)")
        self.courbes.append(self.courbe)

        self.fig.canvas.mpl_connect("pick_event", self.onpick)
        self.init_legende()


def to_bool(txt):
    return txt.lower() == "true"
