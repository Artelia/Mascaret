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
import traceback


class ClassMobilObjectMet1Widget(QWidget):
    widget_closed = pyqtSignal()

    def __init__(self, mgis, typ_obj):
        """
        Initialize the widget for mobile object method 1.
        :param mgis (object): Main GUI object
        :param typ_obj (str): Type of object ('weir' or 'link')
        """
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_obj = typ_obj
        self.cur_obj = int()
        self.filling_tab = False
        self.graph = None

        self.ui = loadUi(os.path.join(self.mgis.masplugPath,
                                      "ui/structures/ui_mobil_object_met1.ui"),
                         self)
        self.ui.cc_control.hide()
        self.ui.cb_basin.hide()

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
            self.ui.grp_clapet.hide()
            self.ui.cc_temp_break.hide()

        self.d_var = {
            "VBREAKT": {"ctrl": self.ui.sb_break_val, "cc": self.ui.cc_break_val,
                        "vdef": 9999., "typ": float},
            "BPERMT": {"ctrl": self.ui.cc_temp_break, "cc": None,
                       "vdef": False, "typ": to_bool},
            "ZFINALT": {"ctrl": self.ui.sb_break_lvl, "cc": self.ui.cc_break_lvl,
                        "vdef": 0., "typ": float},
            "CLAPETT": {"ctrl": self.ui.cc_clapet, "cc": None,
                        "vdef": False, "typ": to_bool},
            "WRITET": {"ctrl": self.ui.sb_step_write, "cc": self.ui.cc_write,
                       "vdef": 1, "typ": int},
            "USEBASINT": {"ctrl": None, "cc": None,
                          "vdef": False, "typ": to_bool},
            "NUMBASINT": {"ctrl": self.ui.cb_basin, "cc": self.ui.cc_control,
                          "vdef": 0, "typ": int},
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

        self.ui.cc_control.toggled.connect(self.enab_control)
        self.ui.cc_write.toggled.connect(self.enab_write)

        self.ui.cc_break_val.toggled.connect(self.enab_breaking_value)
        self.ui.cc_break_lvl.toggled.connect(self.enab_breaking_level)

        self.ui.b_valid.accepted.connect(self.save_input)
        self.ui.b_valid.rejected.connect(self.cancel_input)
        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface.
        :return: None
        """
        mdl = self.create_tab_model()
        self.ui.tab_sets.setModel(mdl)
        self.graph = GraphMobSing(self.mgis, self.ui.lay_graph_m1)

    def enab_write(self, cs):
        """
        Enable or disable the write step control.
        :param cs (bool): Checked state
        :return: None
        """
        self.ui.sb_step_write.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_step_write)

    def enab_control(self, cs):
        """
        Enable or disable the control basin selection.
        :param cs (bool): Checked state
        :return: None
        """
        self.ui.cb_basin.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.cb_basin)

    def enab_breaking_value(self, cs):
        """
        Enable or disable the breaking value control.
        :param cs (bool): Checked state
        :return: None
        """
        self.ui.sb_break_val.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_break_val)

    def enab_breaking_level(self, cs):
        """
        Enable or disable the breaking level control.
        :param cs (bool): Checked state
        :return: None
        """
        self.ui.sb_break_lvl.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_break_lvl)

    def create_tab_model(self):
        """
        Create the table model for time and value.
        :return: (QStandardItemModel) The table model
        """
        model = QStandardItemModel()
        model.insertColumns(0, 5)
        for c in range(4):
            model.setHeaderData(c, 1, "time", 0)

        model.setHeaderData(4, 1, "Z", 0)

        model.itemChanged.connect(self.on_tab_data_change)
        return model

    def load_object(self, object_id):
        """
        Load the object data into the widget.
        :param object_id (int): Object identifier
        :return: None
        """
        self.cur_obj = object_id
        self.d_var["USEBASINT"]["vdef"] = False
        self.d_var["NUMBASINT"]["vdef"] = 0

        if self.typ_obj == "weir":
            sql = "SELECT COALESCE(z_crest, 0.) FROM {0}.{1} " \
                  "WHERE gid = {2}".format(self.mdb.SCHEMA, self.obj_table, self.cur_obj)
            rows = self.mdb.run_query(sql, fetch=True)
            self.d_var["ZFINALT"]["vdef"] = rows[0][0]
        elif self.typ_obj == 'link':
            sql = "SELECT  nature, COALESCE(links.level, 0.) as lvl, " \
                  "basinstart, bas_sta.name, basinend , bas_end.name " \
                  "FROM ({0}.{1} " \
                  "LEFT JOIN {0}.basins as bas_sta on basinstart = bas_sta.basinnum) " \
                  "LEFT JOIN {0}.basins as bas_end on basinend = bas_end.basinnum " \
                  "WHERE links.gid = {2}".format(self.mdb.SCHEMA, self.obj_table, self.cur_obj)
            rows = self.mdb.run_query(sql, fetch=True)
            nat_link, cur_z, b_sta_id, b_sta_name, b_end_id, b_end_name = rows[0]
            self.d_var["ZFINALT"]["vdef"] = cur_z
            if str(nat_link) == '2':
                fill_qcombobox(self.ui.cb_basin, [[b_sta_id, "Start basin ({})".format(b_sta_name)],
                                                  [b_end_id, "End basin ({})".format(b_end_name)]], val_def=b_sta_id)
                self.d_var["USEBASINT"]["vdef"] = True
                self.d_var["NUMBASINT"]["vdef"] = b_sta_id
                self.ui.cc_control.show()
                self.ui.cb_basin.show()

        self.fill_controls()
        self.fill_table()

    def input_def_values(self):
        """
        Set default values for controls.
        :return: None
        """
        self.clear_controls()
        for k, prm in self.d_var.items():
            if prm["cc"]:
                prm["cc"].setChecked(False)

    def set_def_ctrl_value(self, ctrl):
        """
        Set the default value for a control.
        :param ctrl (QWidget): The control widget
        :return: None
        """
        for prm in self.d_var.values():
            if prm["ctrl"] == ctrl and ctrl:
                if "vdef" in prm.keys():
                    ctrl_set_value(ctrl, prm["vdef"], cc_is_checked=True)
                if "cdef" in prm.keys():
                    ctrl_set_value(ctrl, ctrl_get_value(prm["cdef"], cc_is_checked=True))

    def fill_controls(self):
        """
        Fill the controls with data from the database.
        :return: None
        """
        self.input_def_values()

        if self.cur_obj:
            l_var = list(self.d_var.keys())
            txt_var = "('{}')".format("', '".join(l_var))

            sql = "SELECT name_var, id_order, value FROM {0}.{1} WHERE {2} = {3} " \
                  "AND name_var IN {4}".format(self.mdb.SCHEMA, self.mob_table,
                                               self.mob_table_id, self.cur_obj, txt_var)
            rows = self.mdb.run_query(sql, fetch=True)
            for (nm_var, rang_var, value) in rows:
                prm = self.d_var[nm_var]
                if prm["ctrl"]:
                    conv_value = prm["typ"](value)
                    ctrl_set_value(prm["ctrl"], conv_value, cc_is_checked=True)
                    if prm["cc"] and rang_var == 0:
                        prm["cc"].setChecked(True)

    def clear_controls(self):
        """
        Reset all controls to their default values.
        :return: None
        """
        for k, prm in self.d_var.items():
            if prm["cc"]:
                prm["cc"].setChecked(True)
            self.set_def_ctrl_value(prm["ctrl"])

    def unload_object(self):
        """
        Unload the current object and clear the table.
        :return: None
        """
        self.cur_obj = int()
        self.clear_table()

    def clear_table(self):
        """
        Clear the table of all rows.
        :return: None
        """
        self.filling_tab = True
        mdl = self.ui.tab_sets.model()
        list_id = sorted(range(mdl.rowCount()), reverse=True)
        for num in list_id:
            mdl.removeRow(num)
        self.filling_tab = False

        self.update_courbe()

    def fill_table(self):
        """
        Fill the table with time and value data from the database.
        :return: None
        """
        self.clear_table()

        if self.cur_obj:
            self.filling_tab = True
            mdl = self.ui.tab_sets.model()
            c = 0
            for var in ["TIMEZ", "VALUEZ"]:
                sql = "SELECT cast(value as float) FROM {0}.{1} " \
                      "WHERE {2} = {3} AND name_var = '{4}' " \
                      "ORDER BY id_order".format(self.mdb.SCHEMA,
                                                 self.mob_table,
                                                 self.mob_table_id,
                                                 self.cur_obj,
                                                 var)

                rows = self.mdb.run_query(sql, fetch=True)

                if var == "TIMEZ":
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
        """
        Save the input data to the database.
        :return: None
        """
        try:
            l_var = list(self.d_var.keys())
            l_var.extend(['VALUEZ', 'TIMEZ'])
            txt_var = "('{}')".format("', '".join(l_var))

            sql = "DELETE FROM {0}.{1} WHERE {2} = {3} " \
                  "AND name_var IN {4}".format(self.mdb.SCHEMA, self.mob_table,
                                               self.mob_table_id, self.cur_obj, txt_var)

            self.mdb.execute(sql)

            recs = []
            for row in range(self.ui.tab_sets.model().rowCount()):
                recs.append([self.cur_obj, row, "TIMEZ", self.ui.tab_sets.model().item(row, 0).data(0)])
                recs.append([self.cur_obj, row, "VALUEZ", self.ui.tab_sets.model().item(row, 4).data(0)])

            for nm_var, prm in self.d_var.items():
                idx_time = 0
                if prm["cc"]:
                    if not prm["cc"].isChecked():
                        idx_time = -1
                if nm_var == "USEBASINT":
                    conv_value = self.d_var["USEBASINT"]["vdef"]
                else:
                    conv_value = ctrl_get_value(prm["ctrl"], cc_is_checked=True)

                recs.append([self.cur_obj, idx_time, nm_var,
                             conv_value])
            sql = "INSERT INTO {0}.{1} ({2}, id_order, name_var, value) " \
                  "VALUES (%s, %s, %s, cast(%s as text))".format(self.mdb.SCHEMA,
                                                                 self.mob_table,
                                                                 self.mob_table_id)

            self.mdb.run_query(sql, many=True, list_many=recs)
            self.clear_table()
            self.widget_closed.emit()
        except Exception:
            self.cancel_input()
            error_info = ''
            if self.mgis.DEBUG:
                error_info = '\n' + traceback.format_exc()
            self.mgis.add_info("Cancel of {0} information {1}".format(self.obj_table, error_info))

    def cancel_input(self):
        """
        Cancel the input and close the widget.
        :return: None
        """
        self.clear_table()
        self.widget_closed.emit()

    def chg_time(self, v):
        """
        Change the time unit for the table columns.
        :param v (int): Index of the selected time unit
        :return: None
        """
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
        """
        Add a new time row to the table.
        :return: None
        """
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
        """
        Delete selected time rows from the table.
        :return: None
        """
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
        Clear selected cells in the table.
        :return: None
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
        """
        Import time and value data from a CSV file.
        :return: None
        """
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
        """
        Handle changes in the table data.
        :param itm (QStandardItem): The changed item
        :return: None
        """
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
        """
        Update the plot with the current table data.
        :return: None
        """
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
        """
        Initialize the item editor factory.
        :return: None
        """
        QItemEditorFactory.__init__(self)

    def createEditor(self, user_type, parent):
        """
        Create an editor widget for the given user type.
        :param user_type (QVariant.Type): The type of the data
        :param parent (QWidget): The parent widget
        :return: (QWidget) The editor widget
        """
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
        """
        Initialize the graph for mobile singularity.
        :param mgis (object): Main GUI object
        :param lay (QWidget): Layout widget for the graph
        :return: None
        """
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.init_ui_common_p()
        self.courbe = {}
        self.axes = None
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        """
        Initialize the graph UI.
        :return: None
        """
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis="both", labelsize=7.0)
        self.axes.grid(True)

        self.courbe, = self.axes.plot([], [], zorder=100, label="Z")
        self.courbes.append(self.courbe)

        self.fig.canvas.mpl_connect("pick_event", self.onpick)
        self.init_legende()


def to_bool(txt):
    """
    Convert a string to boolean.
    :param txt (str): Input string
    :return: (bool) True if txt is 'true', False otherwise
    """
    return txt.lower() == "true"
