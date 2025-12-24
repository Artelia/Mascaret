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

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QIcon, QColor, QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import QgsApplication, QgsWkbTypes, QgsGeometry
from qgis.gui import QgsRubberBand


FORM_CLASS, BASE = uic.loadUiType(
    os.path.join(os.path.join(os.path.dirname(__file__), "..", "ui/ui_assimilation_ks.ui"))
)


class ClassAssimKsWidget(BASE, FORM_CLASS):
    """
    Class allow to update ks mesh planim of the selected profiles
    """

    def __init__(self, mgis, iface):
        super(ClassAssimKsWidget, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface

        self.bt_sel_zone.setIcon(QIcon(QgsApplication.iconPath("mActionIdentify.svg")))
        self.bt_sel_zone.toggled.connect(self.mgis.main_graph)

        self.bt_reload.setIcon(QIcon(QgsApplication.iconPath("mActionReload.svg")))
        self.bt_zoom_zone.setIcon(QIcon(QgsApplication.iconPath("mActionZoomToSelected.svg")))
        self.bt_disp_zone.setIcon(QIcon(QgsApplication.iconPath("mActionShowSelectedLayers.svg")))
        self.bt_cancel_ks.setIcon(QIcon(QgsApplication.iconPath("mActionCancelAllEdits.svg")))
        self.bt_valid_ks.setIcon(QIcon(QgsApplication.iconPath("mActionSaveAllEdits.svg")))

        ks_zones_updated = self.verif_ks_zones()
        if ks_zones_updated:
            QMessageBox.warning(None, "Warning", "Definition of some controls zone "
                                                 "have been automatically upadated.")

        self.rb_format = QgsWkbTypes.LineGeometry
        self.rb = QgsRubberBand(iface.mapCanvas(), self.rb_format)
        self.rb.setColor(Qt.magenta)
        self.rb.setFillColor(QColor("transparent"))
        self.rb.setWidth(8)
        self.rb_visible = True

        self.cur_zone_ks = None
        self.d_zone_ks = dict()

        self.load_config()
        self.load_obs()
        self.load_zone_ks()

        self.cc_ks_act.toggled.connect(self.change_ks_config)
        self.cb_ks_fld.currentTextChanged.connect(self.load_obs)
        self.sb_ks_seuil.valueChanged.connect(self.change_ks_config)
        self.sb_ks_sigma.valueChanged.connect(self.change_ks_config)
        self.sb_ks_pert_min.valueChanged.connect(self.change_ks_config)
        self.sb_ks_pert_max.valueChanged.connect(self.change_ks_config)

        self.bt_reload.clicked.connect(self.reload_zone_ks)
        self.bt_disp_zone.clicked.connect(self.display_map_rb)
        self.bt_zoom_zone.clicked.connect(self.zoom_on_zone)
        self.bt_edit_zone.clicked.connect(self.enable_input)
        self.bt_cancel_ks.clicked.connect(self.cancel_input)
        self.bt_valid_ks.clicked.connect(self.save_input)

    def load_config(self):
        sql = "SELECT control_type, active, control_var, seuil_rejet_misfit, " \
              "iterations_sigma, perturbation_val FROM {0}.assim_config"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        if not rows:
            recs = [[1, "ctrlKS", False, "H", 500, 1, ["ksMin, 'ksMaj"], [[5], [1]]],
                    [2, "ctrlLaw", False, "H", 50, 1,
                     ["perturbationsCote", "perturbationsDebit", "perturbationsDebitLineigue"],
                     [[1.0, 0.5], [1.1, 6.0], [0.0, 0.0]]]]
            sql = "INSERT INTO {0}.assim_config (id_type, control_type, active, control_var, " \
                  "seuil_rejet_misfit, iterations_sigma, perturbation_var, perturbation_val) VALUES ({1})"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA, ', '.join(["%s"]*8)),
                               many=True, list_many=recs)

            sql = "SELECT control_type, active, control_var, seuil_rejet_misfit, " \
                  "iterations_sigma, perturbation_val FROM {0}.assim_config"
            rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        for row in rows:
            if row[0] == "ctrlKS":
                self.cc_ks_act.setChecked(row[1])
                self.cb_ks_fld.setCurrentText(row[2])
                self.sb_ks_seuil.setValue(row[3])
                self.sb_ks_sigma.setValue(row[4])
                self.sb_ks_pert_min.setValue(row[5][0][0])
                self.sb_ks_pert_max.setValue(row[5][1][0])

    def load_obs(self):
        mdl = QStandardItemModel()
        mdl.setColumnCount(1)

        sql = "SELECT id, code FROM {0}.observations " \
              "WHERE type = '{1}' " \
              "ORDER BY code"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA,
                                             self.cb_ks_fld.currentText()),
                                  fetch=True)
        for row in rows:
            itm = QStandardItem()
            itm.setData(row[1], 0)
            itm.setData(row[0], 32)
            itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            itm.setCheckState(0)
            mdl.appendRow(itm)

        self.lv_ks_obs.setModel(mdl)
        self.lv_ks_obs.setSpacing(2)
        self.display_zone_info()
        self.change_ks_config()

    def change_ks_config(self):
        sql = "UPDATE {0}.assim_config SET " \
              "active = %s, " \
              "control_var = %s, " \
              "seuil_rejet_misfit = %s, " \
              "iterations_sigma = %s, " \
              "perturbation_val = %s " \
              "WHERE control_type = 'ctrlKS'".format(self.mdb.SCHEMA)
        recs = [[self.cc_ks_act.isChecked(), self.cb_ks_fld.currentText(),
                 self.sb_ks_seuil.value(), self.sb_ks_sigma.value(),
                 [[self.sb_ks_pert_min.value()], [self.sb_ks_pert_max.value()]]]]
        self.mdb.run_query(sql.format(self.mdb.SCHEMA), many=True, list_many=recs)

    def verif_ks_zones(self):
        ks_zones_updated = False

        d_calc_ks = self.mdb.zone_ks()

        sql = "SELECT id_zone, branchnum, abs_min, abs_max, active, auto_del, " \
              "lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, " \
              "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        if not rows:
            recs = [[idx, d_calc_ks["branch"][idx],
                     d_calc_ks["zoneabsstart"][idx], d_calc_ks["zoneabsend"][idx],
                     False, False, [], [],
                     False, 1, d_calc_ks["minbedcoef"][idx], d_calc_ks["minbedcoef"][idx],
                     False, 1,  d_calc_ks["majbedcoef"][idx], d_calc_ks["majbedcoef"][idx]]
                    for idx in range(len(d_calc_ks["branch"]))]
            sql = "INSERT INTO {0}.assim_ks (id_zone, branchnum, abs_min, abs_max, active, " \
                  "auto_del, lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, " \
                  "active_maj, std_maj, val_inf_maj, val_sup_maj) VALUES ({1})"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA, ', '.join(["%s"]*len(recs[0]))),
                               many=True, list_many=recs)

            sql = "SELECT id_zone, branchnum, abs_min, abs_max, active, auto_del, " \
                  "lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, " \
                  "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks"
            rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_db_ks = {tuple(row[1:4]): row for row in rows}
        d_verif_ks = {(d_calc_ks["branch"][idx],
                       d_calc_ks["zoneabsstart"][idx],
                       d_calc_ks["zoneabsend"][idx]):
                          (d_calc_ks["minbedcoef"][idx], d_calc_ks["majbedcoef"][idx])
                      for idx in range(len(d_calc_ks["branch"]))}

        if not(len(d_db_ks) == len(d_verif_ks) and
               all([k in d_db_ks.keys() for k in d_verif_ks.keys()])):
            recs = []
            idx_ks = 0
            for id_ks, (min_coef, maj_coef) in d_verif_ks.items():
                if id_ks in d_db_ks.keys():
                    rec = d_db_ks[id_ks]
                    rec[0] = idx_ks
                    recs.append(rec)
                else:
                    recs.append(
                        [idx_ks, *id_ks, False, True, [], [],
                         False, 1, min_coef, min_coef,
                         False, 1, maj_coef, maj_coef])
                idx_ks += 1

            sql = "DELETE FROM {0}.assim_ks"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            sql = "INSERT INTO {0}.assim_ks (id_zone, branchnum, abs_min, abs_max, active, " \
                  "auto_del, lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, " \
                  "active_maj, std_maj, val_inf_maj, val_sup_maj) VALUES ({1})"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA, ', '.join(["%s"] * len(recs[0]))),
                               many=True, list_many=recs)
            ks_zones_updated = True

        sql = "SELECT branchnum, abs_min, abs_max," \
              "val_inf_min, val_sup_min, val_inf_maj, val_sup_maj FROM {0}.assim_ks"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        d_db_ks = {tuple(row[:3]): tuple(row[3:]) for row in rows}

        d_edit = {"val_inf_min": [], "val_sup_min": [],
                  "val_inf_maj": [], "val_sup_maj": []}
        for id_ks, (min_coef, maj_coef) in d_verif_ks.items():
            db_ks = d_db_ks[id_ks]
            if db_ks[0] > min_coef:
                d_edit["val_inf_min"].append([min_coef, *id_ks])
            if db_ks[1] < min_coef:
                d_edit["val_sup_min"].append([min_coef, *id_ks])
            if db_ks[2] > maj_coef:
                d_edit["val_inf_maj"].append([maj_coef, *id_ks])
            if db_ks[3] < maj_coef:
                d_edit["val_sup_maj"].append([maj_coef, *id_ks])

        for fld, recs in d_edit.items():
            if recs:
                sql = "UPDATE {0}.assim_ks SET {1} = %s, active = False, auto_del = True " \
                      "WHERE branchnum = %s AND abs_min = %s AND abs_max = %s"
                self.mdb.run_query(sql.format(self.mdb.SCHEMA, fld),
                                   many=True, list_many=recs)
                ks_zones_updated = True

        return ks_zones_updated

    def reload_zone_ks(self):
        ks_zones_updated = self.verif_ks_zones()
        if ks_zones_updated:
            QMessageBox.warning(None, "Warning", "Definition of some controls zone "
                                                 "have been automatically upadated.")
            self.load_zone_ks()

    def load_zone_ks(self):
        self.d_zone_ks.clear()

        d_calc_ks = self.mdb.zone_ks()
        d_info_ks = {(d_calc_ks["branch"][idx],
                      d_calc_ks["zoneabsstart"][idx],
                      d_calc_ks["zoneabsend"][idx]):
                         {"num_zone": d_calc_ks["branch_zone"][idx],
                          "min_coef": d_calc_ks["minbedcoef"][idx],
                          "maj_coef": d_calc_ks["majbedcoef"][idx],
                          "geom": d_calc_ks["geom"][idx]}
                     for idx in range(len(d_calc_ks["branch"]))}

        sql = "SELECT id_zone, branchnum, abs_min, abs_max, active, auto_del, " \
              "lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, " \
              "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks " \
              "ORDER BY abs_min"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        for row in rows:
            info_ks = d_info_ks[tuple(row[1:4])]
            self.d_zone_ks[row[0]] = {"zone_name": "Zone {}.{}".format(row[1], info_ks["num_zone"]),
                                      "geom": QgsGeometry.fromWkt(info_ks["geom"]),
                                      "min_coef": info_ks["min_coef"],
                                      "maj_coef": info_ks["maj_coef"],
                                      "branch_num": row[1],
                                      "abs_start": row[2],
                                      "abs_end": row[3],
                                      "active": row[4],
                                      "auto_del": row[5],
                                      "prm": {"lst_obs_h": row[6],
                                              "lst_obs_q": row[7],
                                              "active_min": row[8],
                                              "std_min": row[9],
                                              "val_inf_min": row[10],
                                              "val_sup_min": row[11],
                                              "active_maj": row[12],
                                              "std_maj": row[13],
                                              "val_inf_maj": row[14],
                                              "val_sup_maj": row[15]}}

        mdl = QStandardItemModel()
        mdl.setColumnCount(1)
        for id_ks, p_ks in self.d_zone_ks.items():
            itm = QStandardItem()
            itm.setData(p_ks["zone_name"], 0)
            itm.setData(id_ks, 32)
            itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            if p_ks["auto_del"]:
                itm.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))
            if p_ks["active"]:
                itm.setCheckState(2)
            else:
                itm.setCheckState(0)
            mdl.appendRow(itm)

        self.lv_zone.setIconSize(QSize(14, 14))
        self.lv_zone.setModel(mdl)
        self.lv_zone.setSpacing(2)
        self.lv_zone.model().itemChanged.connect(self.zone_status_changed)
        self.lv_zone.selectionModel().selectionChanged.connect(self.current_zone_changed)

        if self.lv_zone.model().rowCount():
            self.lv_zone.setCurrentIndex(self.lv_zone.model().item(0, 0).index())

    def refresh_zone_ks(self, id_zone):
        sql = "SELECT lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, " \
              "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks " \
              "WHERE id_zone = {1}"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA, id_zone), fetch=True)
        row = rows[0]
        self.d_zone_ks[id_zone]["prm"] = {"lst_obs_h": row[0], "lst_obs_q": row[1],
                                          "active_min": row[2], "std_min": row[3],
                                          "val_inf_min": row[4], "val_sup_min": row[5],
                                          "active_maj": row[6], "std_maj": row[7],
                                          "val_inf_maj": row[8], "val_sup_maj": row[9]}

    def zone_selected_from_map(self, selected_abs):
        sql = "SELECT id_zone FROM {0}.assim_ks WHERE " \
              "abs_min <= {1} AND abs_max > {1}".format(self.mdb.SCHEMA, selected_abs)
        row = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        if row:
            id_zone_selected = row[0][0]
            for row in range(self.lv_zone.model().rowCount()):
                itm = self.lv_zone.model().item(row, 0)
                if itm.data(32) == id_zone_selected:
                    self.lv_zone.setCurrentIndex(itm.index())
                    break

    def current_zone_changed(self):
        if self.lv_zone.selectionModel().hasSelection():
            idxs = self.lv_zone.selectionModel().selectedIndexes()
            if idxs:
                idx = idxs[0]
                itm = self.lv_zone.model().itemFromIndex(idx)
                self.cur_zone_ks = itm.data(32)
            else:
                self.cur_zone_ks = None
        else:
            self.cur_zone_ks = None

        self.display_zone_info()
        self.draw_zone_rb()

    def display_zone_info(self):
        self.gb_zone.setTitle("Aucune zone sélectionné")

        if self.cur_zone_ks is not None:
            d_zone = self.d_zone_ks[self.cur_zone_ks]
            self.sb_minor_inf.setMaximum(d_zone["min_coef"])
            self.sb_minor_sup.setMinimum(d_zone["min_coef"])
            self.sb_major_inf.setMaximum(d_zone["maj_coef"])
            self.sb_major_sup.setMinimum(d_zone["maj_coef"])

            self.gb_zone.setTitle(d_zone["zone_name"])
            self.gb_minor.setChecked(d_zone["prm"]["active_min"])
            self.sb_minor_std.setValue(d_zone["prm"]["std_min"])
            self.sb_minor_inf.setValue(d_zone["prm"]["val_inf_min"])
            self.sb_minor_sup.setValue(d_zone["prm"]["val_sup_min"])
            self.gb_major.setChecked(d_zone["prm"]["active_maj"])
            self.sb_major_std.setValue(d_zone["prm"]["std_maj"])
            self.sb_major_inf.setValue(d_zone["prm"]["val_inf_maj"])
            self.sb_major_sup.setValue(d_zone["prm"]["val_sup_maj"])

            l_obs = d_zone["prm"]["lst_obs_{}".format(str(self.cb_ks_fld.currentText()).lower())]
            for r in range(self.lv_ks_obs.model().rowCount()):
                itm = self.lv_ks_obs.model().item(r, 0)
                if itm.data(32) in l_obs:
                    itm.setCheckState(2)
                else:
                    itm.setCheckState(0)

    def zone_status_changed(self, itm):
        sql = "UPDATE {0}.assim_ks SET active = {1} WHERE id_zone = {2}"
        self.mdb.run_query(sql.format(self.mdb.SCHEMA, itm.checkState() == 2, itm.data(32)))

    def display_map_rb(self):
        self.rb_visible = self.bt_disp_zone.isChecked()
        self.draw_zone_rb()

    def draw_zone_rb(self):
        self.rb.reset(self.rb_format)
        if self.rb_visible and self.cur_zone_ks is not None:
            rb_geom = self.d_zone_ks[self.cur_zone_ks]["geom"]
            # if self.rubber_format == QgsWkbTypes.PolygonGeometry:
            #     rubber_geom = rubber_geom.buffer(10., 18)

            self.rb.addGeometry(rb_geom)
            self.rb.show()

    def zoom_on_zone(self):
        if self.cur_zone_ks is not None:
            ks_geom = self.d_zone_ks[self.cur_zone_ks]["geom"]
            ks_bb = ks_geom.boundingBox()
            ks_bb = ks_bb.buffered(ks_bb.width() * 0.05)
            canvas = self.iface.mapCanvas()
            canvas.setExtent(ks_bb)
            canvas.refresh()
            canvas.waitWhileRendering()

    def enable_input(self):
        self.gb_zone.setEnabled(True)
        self.gb_param_ks.setEnabled(False)
        self.bt_sel_zone.setChecked(False)
        self.fra_zone_sel.setEnabled(False)

    def disable_input(self):
        self.gb_param_ks.setEnabled(True)
        self.fra_zone_sel.setEnabled(True)
        self.gb_zone.setEnabled(False)

    def cancel_input(self):
        self.disable_input()
        self.display_zone_info()

    def save_input(self):
        l_obs = []
        for r in range(self.lv_ks_obs.model().rowCount()):
            itm = self.lv_ks_obs.model().item(r, 0)
            if itm.checkState() == 2:
                l_obs.append(itm.data(32))

        recs = [[self.gb_minor.isChecked(), self.sb_minor_std.value(),
                 self.sb_minor_inf.value(), self.sb_minor_sup.value(),
                 self.gb_major.isChecked(), self.sb_major_std.value(),
                 self.sb_major_inf.value(), self.sb_major_sup.value(),
                 l_obs]]

        sql = "UPDATE {0}.assim_ks SET " \
              "active_min = %s, " \
              "std_min = %s, " \
              "val_inf_min = %s, " \
              "val_sup_min = %s, " \
              "active_maj = %s, " \
              "std_maj = %s, " \
              "val_inf_maj = %s, " \
              "val_sup_maj = %s, " \
              "lst_obs_{1} = %s," \
              "auto_del = False " \
              "WHERE id_zone = {2}".format(self.mdb.SCHEMA,
                                           str(self.cb_ks_fld.currentText()).lower(),
                                           self.cur_zone_ks)
        self.mdb.run_query(sql.format(self.mdb.SCHEMA), many=True, list_many=recs)

        self.disable_input()
        self.refresh_zone_ks(self.cur_zone_ks)
        self.display_zone_info()

        if self.lv_zone.selectionModel().hasSelection():
            idxs = self.lv_zone.selectionModel().selectedIndexes()
            if idxs:
                idx = idxs[0]
                itm = self.lv_zone.model().itemFromIndex(idx)
                itm.setIcon(QIcon())
