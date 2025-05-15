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

from .FctDialog import ctrl_set_value, ctrl_get_value, fill_qcombobox
from ..Graphic.GraphCommon import GraphCommon
from ..Function import data_to_float


class ClassMobilObjectMet2Widget(QWidget):
    widget_closed = pyqtSignal()

    def __init__(self, mgis, typ_obj):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_obj = typ_obj
        self.cur_obj = int()
        self.filling_tab = False
        self.graph = None
        self.lvls = [int(), int()]

        self.ui = loadUi(os.path.join(self.mgis.masplugPath,
                                      "ui/structures/ui_mobil_object_met2.ui"),
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
            self.ui.cc_clapet.hide()

        self.d_var = {
            "DIRFG": {"ctrl": self.ui.cb_dir, "cc": None, "vdef": 'D', "typ": str},
            "VELOFGOPEN": {"ctrl": self.ui.sb_open_vel, "cc": None, "vdef": 1., "typ": float},
            "UNITVELO": {"ctrl": self.ui.cb_unit_open_vel, "cc": None, "vdef": 1, "typ": int},
            "VELOFGCLOSE": {"ctrl": self.ui.sb_close_vel, "cc": self.ui.cc_close_vel,
                            "cdef": self.ui.sb_open_vel, "typ": float},
            "UNITVELC": {"ctrl": self.ui.cb_unit_close_vel, "cc": self.ui.cc_close_vel,
                              "cdef": self.ui.cb_unit_open_vel, "typ": int},
            "ZMAXFG": {"ctrl": self.ui.sb_stop_elev, "cc": None, "vdef": 0., "typ": float},
            "ZINITREG": {"ctrl": self.ui.sb_init_lvl, "cc": self.ui.cc_init_lvl,
                         "vdef": 0., "typ": float},
            "VREG": {"ctrl": self.ui.cb_var_regul, "cc": self.ui.cc_var_regul,
                     "vdef": 'Z', "typ": str},
            "USEBASIN": {"ctrl": self.ui.cb_typ_control, "cc": self.ui.cc_control,
                         "vdef": False, "typ": to_bool},
            "NUMBASINREG": {"ctrl": self.ui.cb_basin, "cc": self.ui.cc_control,
                            "vdef": 0, "typ": int},
            "PK": {"ctrl": self.ui.sb_abscissa, "cc": self.ui.cc_control,
                   "vdef": 0., "typ": float},
            "VREGCLOS": {"ctrl": self.ui.sb_close_lvl, "cc": None, "vdef": 0., "typ": float},
            "VREGOPEN": {"ctrl": self.ui.sb_open_lvl, "cc": self.ui.cc_open_lvl,
                         "cdef": self.ui.sb_close_lvl, "typ": float},
            "CRITDTREG": {"ctrl": self.ui.cb_step_time, "cc": self.ui.cc_step_time,
                          "vdef": 'NDTREG', "typ": str},
            "NDTREG": {"ctrl": self.ui.sb_step_count, "cc": self.ui.cc_step_time,
                       "vdef": 1, "typ": int},
            "DTREG": {"ctrl": self.ui.sb_step_time, "cc": self.ui.cc_step_time,
                      "vdef": 0., "typ": float},
            "ZINCRFG": {"ctrl": self.ui.sb_z_inc, "cc": self.ui.cc_z_inc,
                        "vdef": 999., "typ": float},
            "TOLREG": {"ctrl": self.ui.sb_tol, "cc": self.ui.cc_tol,
                       "vdef": 0.05, "typ": float},
            "VBREAKREG": {"ctrl": self.ui.sb_break_val, "cc": self.ui.cc_break_val,
                          "vdef": 9999., "typ": float},
            "BPERMREG": {"ctrl": self.ui.cc_temp_break, "cc": None,
                         "vdef": False, "typ": to_bool},
            "ZFINALREG": {"ctrl": self.ui.sb_break_lvl, "cc": self.ui.cc_break_lvl,
                          "vdef": 0., "typ": float},
            "CLAPET": {"ctrl": self.ui.cc_clapet, "cc": None,
                         "vdef": False, "typ": to_bool},
        }

        self.ui.cb_dir.currentIndexChanged.connect(self.direction_changed)

        self.ui.cc_close_vel.toggled.connect(self.enab_close_velocity)
        self.ui.sb_open_vel.valueChanged.connect(self.open_velocity_changed)
        self.ui.cb_unit_open_vel.currentIndexChanged.connect(self.open_velocity_unit_changed)

        self.ui.cc_init_lvl.toggled.connect(self.enab_initial_level)

        self.ui.cc_step_time.toggled.connect(self.enab_step_time)
        self.ui.cb_step_time.currentIndexChanged.connect(self.step_time_type_changed)

        self.ui.cc_z_inc.toggled.connect(self.enab_max_increment)
        self.ui.cc_tol.toggled.connect(self.enab_tolerance)

        self.ui.cc_var_regul.toggled.connect(self.enab_variable_regulation)
        self.ui.cb_var_regul.currentIndexChanged.connect(self.variable_regulation_changed)

        self.ui.cc_control.toggled.connect(self.enab_control)
        self.ui.cb_typ_control.currentIndexChanged.connect(self.control_type_changed)

        self.ui.cc_open_lvl.toggled.connect(self.enab_opening_level)
        self.ui.sb_close_lvl.valueChanged.connect(self.close_level_changed)

        self.ui.cc_break_val.toggled.connect(self.enab_breaking_value)
        self.ui.cc_break_lvl.toggled.connect(self.enab_breaking_level)

        self.ui.b_def.clicked.connect(self.input_def_values)
        self.ui.b_valid.accepted.connect(self.save_input)
        self.ui.b_valid.rejected.connect(self.cancel_input)

        self.ui.cb_typ_control.hide()
        self.ui.cb_basin.hide()

        self.init_ui()
        self.clear_controls()

    def init_ui(self):
        """initialisation gui"""
        fill_qcombobox(self.ui.cb_step_time, [["NDTREG", "N Time Step"],
                                              ["DTREG", "Time Step"]])

        fill_qcombobox(self.ui.cb_typ_control, [[False, "Abscissa"],
                                                [True, "Basin"]])

        for cb in [self.ui.cb_unit_close_vel, self.ui.cb_unit_open_vel]:
            fill_qcombobox(cb, [[1, "m/s"],
                                [60, "m/min"],
                                [3600, "m/h"]])

        fill_qcombobox(self.ui.cb_var_regul, [["Z", "Water level"],
                                              ["Q", "Flow rate"]])

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
                break

    def direction_changed(self, idx):
        self.d_var["ZINITREG"]["vdef"] = self.lvls[idx]
        if not self.ui.cc_init_lvl.isChecked():
            self.ui.cc_init_lvl.setChecked(True)
            self.ui.cc_init_lvl.setChecked(False)

    def enab_close_velocity(self, cs):
        self.ui.sb_close_vel.setEnabled(cs)
        self.ui.cb_unit_close_vel.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_close_vel)
            self.set_def_ctrl_value(self.ui.cb_unit_close_vel)

    def open_velocity_changed(self):
        if not self.ui.cc_close_vel.isChecked():
            self.set_def_ctrl_value(self.ui.sb_close_vel)

    def open_velocity_unit_changed(self):
        if not self.ui.cc_close_vel.isChecked():
            self.set_def_ctrl_value(self.ui.cb_unit_close_vel)

    def enab_initial_level(self, cs):
        self.ui.sb_init_lvl.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_init_lvl)

    def close_level_changed(self):
        if not self.ui.cc_open_lvl.isChecked():
            self.set_def_ctrl_value(self.ui.sb_open_lvl)

    def enab_variable_regulation(self, cs):
        self.ui.cb_var_regul.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.cb_var_regul)

    def variable_regulation_changed(self, idx):
        if idx == 1:
            self.ui.sb_open_lvl.setSuffix(" m³/s")
            self.ui.sb_close_lvl.setSuffix(" m³/s")
            self.ui.sb_break_val.setSuffix(" m³/s")
            self.d_var["VREGCLOS"]["vdef"] = 0.
        else:
            self.ui.sb_open_lvl.setSuffix(" m")
            self.ui.sb_close_lvl.setSuffix(" m")
            self.ui.sb_break_val.setSuffix(" m")
            self.d_var["VREGCLOS"]["vdef"] = self.lvls[0]

        self.set_def_ctrl_value(self.ui.sb_close_lvl)

    def enab_control(self, cs):
        self.ui.cb_typ_control.setEnabled(cs)
        self.ui.sb_abscissa.setEnabled(cs)
        self.ui.cb_basin.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.cb_typ_control)
            self.set_def_ctrl_value(self.ui.sb_abscissa)
            self.set_def_ctrl_value(self.ui.cb_basin)

    def enab_opening_level(self, cs):
        self.ui.sb_open_lvl.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_open_lvl)

    def control_type_changed(self, idx):
        self.ui.cc_var_regul.setChecked(True)
        self.ui.cc_var_regul.setChecked(False)
        if idx == 1:
            self.ui.sb_abscissa.hide()
            self.ui.cb_basin.show()
            self.ui.cc_var_regul.setEnabled(False)
        else:
            self.ui.cb_basin.hide()
            self.ui.sb_abscissa.show()
            self.ui.cc_var_regul.setEnabled(True)

    def enab_step_time(self, cs):
        self.ui.cb_step_time.setEnabled(cs)
        self.ui.lbl_step_count.setEnabled(cs)
        self.ui.sb_step_count.setEnabled(cs)
        self.ui.lbl_step_time.setEnabled(cs)
        self.ui.sb_step_time.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.cb_step_time)
            self.set_def_ctrl_value(self.ui.sb_step_count)
            self.set_def_ctrl_value(self.ui.sb_step_time)

    def step_time_type_changed(self, idx):
        if idx == 1:
            self.ui.sb_step_time.setValue(1.)
            self.ui.lbl_step_count.hide()
            self.ui.sb_step_count.hide()
            self.ui.lbl_step_time.show()
            self.ui.sb_step_time.show()
            self.ui.sb_step_count.setValue(0)
        else:
            self.ui.sb_step_count.setValue(1)
            self.ui.lbl_step_time.hide()
            self.ui.sb_step_time.hide()
            self.ui.lbl_step_count.show()
            self.ui.sb_step_count.show()
            self.ui.sb_step_time.setValue(0.)

    def enab_max_increment(self, cs):
        self.ui.sb_z_inc.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_z_inc)

    def enab_tolerance(self, cs):
        self.ui.sb_tol.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_tol)

    def enab_breaking_value(self, cs):
        self.ui.sb_break_val.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_break_val)

    def enab_breaking_level(self, cs):
        self.ui.sb_break_lvl.setEnabled(cs)
        if not cs:
            self.set_def_ctrl_value(self.ui.sb_break_lvl)

    def load_object(self, object_id):
        self.cur_obj = object_id
        if self.cur_obj:

            if self.typ_obj == "weir":
                fill_qcombobox(self.ui.cb_dir, [["D", "bottom"]])

                sql = "SELECT COALESCE(abscissa, 0.) as absc, COALESCE(z_crest, 0.) as lvl FROM {0}.{1} " \
                      "WHERE gid = {2}".format(self.mdb.SCHEMA, self.obj_table, self.cur_obj)
                rows = self.mdb.run_query(sql, fetch=True)
                cur_abs, cur_z = rows[0]
                self.lvls = [cur_z, cur_z]
                self.d_var["ZMAXFG"]["vdef"] = cur_z
                self.d_var["ZINITREG"]["vdef"] = cur_z
                self.d_var["VREGCLOS"]["vdef"] = cur_z
                self.d_var["ZFINALREG"]["vdef"] = cur_z
                self.d_var["USEBASIN"]["vdef"] = False
                self.d_var["PK"]["vdef"] = cur_abs
                self.d_var["NUMBASINREG"]["vdef"] = 0

                fill_qcombobox(self.ui.cb_basin, [[0, "None"]])
                self.ui.cb_typ_control.hide()

            elif self.typ_obj == 'link':
                sql = "SELECT type, nature, COALESCE(abscissa, 0.) as absc, COALESCE(links.level, 0.) as lvl, " \
                      "COALESCE(crosssection, 0.) as cs_l, COALESCE(width, 1.) as w_l, " \
                      "basinstart, bas_sta.name, basinend , bas_end.name " \
                      "FROM ({0}.{1} " \
                      "LEFT JOIN {0}.basins as bas_sta on basinstart = bas_sta.gid) " \
                      "LEFT JOIN {0}.basins as bas_end on basinend = bas_end.gid " \
                      "WHERE links.gid = {2}".format(self.mdb.SCHEMA, self.obj_table, self.cur_obj)
                rows = self.mdb.run_query(sql, fetch=True)
                typ_link, nat_link, cur_abs, cur_z, cs_link, wid_link, \
                    b_sta_id, b_sta_name, b_end_id, b_end_name = rows[0]

                if str(nat_link) != '2':
                    fill_qcombobox(self.ui.cb_basin, [[b_sta_id, b_sta_name]])
                    self.d_var["USEBASIN"]["vdef"] = False
                    self.ui.cb_typ_control.show()
                else:
                    fill_qcombobox(self.ui.cb_basin, [[b_sta_id, "Start basin ({})".format(b_sta_name)],
                                                      [b_end_id, "End basin ({})".format(b_end_name)]])
                    self.d_var["USEBASIN"]["vdef"] = True
                    self.ui.cb_typ_control.hide()

                if str(typ_link) != '4':
                    fill_qcombobox(self.ui.cb_dir, [["D", "bottom"]])
                    self.lvls = [cur_z, cur_z]
                    self.d_var["ZMAXFG"]["vdef"] = cur_z
                    self.d_var["ZINITREG"]["vdef"] = cur_z
                    self.d_var["VREGCLOS"]["vdef"] = cur_z
                    self.d_var["ZFINALREG"]["vdef"] = cur_z
                    self.d_var["PK"]["vdef"] = cur_abs
                    self.d_var["NUMBASINREG"]["vdef"] = b_sta_id
                else:
                    self.lvls = [cur_z, cur_z + (cs_link / wid_link)]
                    fill_qcombobox(self.ui.cb_dir, [["D", "bottom"],
                                                    ["U", "top"]])
                    self.d_var["ZMAXFG"]["vdef"] = cur_z
                    self.d_var["ZINITREG"]["vdef"] = cur_z
                    self.d_var["VREGCLOS"]["vdef"] = cur_z
                    self.d_var["ZFINALREG"]["vdef"] = cur_z
                    self.d_var["PK"]["vdef"] = cur_abs
                    self.d_var["NUMBASINREG"]["vdef"] = b_sta_id

            self.fill_controls()

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
                try:
                    conv_value = prm["typ"](saved_prm["val"])
                except ValueError:
                    conv_value = prm["typ"](float(saved_prm["val"]))

                if nm_prm == "VELOFGOPEN" and "UNITVELO" in d_rec.keys():
                    conv_value = conv_value / float(d_rec["UNITVELO"]["val"])
                if nm_prm == "VELOFGCLOSE" and "UNITVELC" in d_rec.keys():
                    conv_value = conv_value / float(d_rec["UNITVELC"]["val"])

                ctrl_set_value(prm["ctrl"], conv_value, cc_is_checked=True)
                if prm["cc"] and saved_prm["def"] == 0:
                    prm["cc"].setChecked(True)

    def clear_controls(self):
        for k, prm in self.d_var.items():
            if prm["cc"]:
                prm["cc"].setChecked(True)
            self.set_def_ctrl_value(prm["ctrl"])

    def save_input(self):
        recs = []
        l_var = list(self.d_var.keys())
        txt_var = "('{}')".format("', '".join(l_var))

        for nm_var, prm in self.d_var.items():
            idx_time = 0
            if prm["cc"]:
                if not prm["cc"].isChecked():
                    idx_time = -1

            val = ctrl_get_value(prm["ctrl"], cc_is_checked=True)
            if nm_var == "VELOFGOPEN":
                unit = ctrl_get_value(self.ui.cb_unit_open_vel, cc_is_checked=True)
                val = val * unit
            if nm_var == "VELOFGCLOSE":
                unit = ctrl_get_value(self.ui.cb_unit_close_vel, cc_is_checked=True)
                val = val * unit

            recs.append([self.cur_obj, idx_time, nm_var, val])

        sql = "DELETE FROM {0}.{1} WHERE {2} = {3} " \
              "AND name_var IN {4}".format(self.mdb.SCHEMA, self.mob_table,
                                           self.mob_table_id, self.cur_obj, txt_var)

        self.mdb.execute(sql)

        sql = "INSERT INTO {0}.{1} ({2}, id_order, name_var, value) " \
              "VALUES (%s, %s, %s, cast(%s as text))".format(self.mdb.SCHEMA,
                                                             self.mob_table,
                                                             self.mob_table_id)

        self.mdb.run_query(sql, many=True, list_many=recs)

        self.widget_closed.emit()

    def cancel_input(self):
        self.widget_closed.emit()



def to_bool(txt):
    return txt.lower() == "true"
