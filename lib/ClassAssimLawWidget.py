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
    os.path.join(os.path.join(os.path.dirname(__file__), "..", "ui/ui_assimilation_law.ui"))
)


class ClassAssimLawWidget(BASE, FORM_CLASS):
    """
    Class allow to update ks mesh planim of the selected profiles
    """

    def __init__(self, mgis, iface):
        super(ClassAssimLawWidget, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface

        # self.bt_sel_law.setIcon(QIcon(QgsApplication.iconPath("mActionIdentify.svg")))
        # self.bt_sel_law.toggled.connect(self.mgis.main_graph)
        # self.bt_zoom_law.setIcon(QIcon(QgsApplication.iconPath("mActionZoomToSelected.svg")))
        # self.bt_disp_law.setIcon(QIcon(QgsApplication.iconPath("mActionShowSelectedLayers.svg")))

        self.bt_sel_law.hide()
        self.bt_zoom_law.hide()
        self.bt_disp_law.hide()

        self.bt_cancel_law.setIcon(QIcon(QgsApplication.iconPath("mActionCancelAllEdits.svg")))
        self.bt_valid_law.setIcon(QIcon(QgsApplication.iconPath("mActionSaveAllEdits.svg")))

        self.verif_laws()
        # ks_zones_updated = self.verif_ks_zones()
        # if ks_zones_updated:
        #     QMessageBox.warning(None, "Warning", "Definition of some controls zone "
        #                                          "have been automatically upadated.")

        # self.rb_format = QgsWkbTypes.LineGeometry
        # self.rb = QgsRubberBand(iface.mapCanvas(), self.rb_format)
        # self.rb.setColor(Qt.magenta)
        # self.rb.setFillColor(QColor("transparent"))
        # self.rb.setWidth(8)
        # self.rb_visible = True

        self.cur_law = None
        self.d_laws = dict()

        self.load_config()
        self.load_obs()
        self.load_laws()

        self.cc_law_act.toggled.connect(self.change_law_config)
        self.cb_law_fld.currentTextChanged.connect(self.load_obs)
        self.sb_law_seuil.valueChanged.connect(self.change_law_config)
        self.sb_law_sigma.valueChanged.connect(self.change_law_config)
        self.sb_cote_a.valueChanged.connect(self.change_law_config)
        self.sb_cote_b.valueChanged.connect(self.change_law_config)
        self.sb_debit_a.valueChanged.connect(self.change_law_config)
        self.sb_debit_b.valueChanged.connect(self.change_law_config)
        self.sb_debit_lin_a.valueChanged.connect(self.change_law_config)
        self.sb_debit_lin_b.valueChanged.connect(self.change_law_config)

        # self.bt_disp_zone.clicked.connect(self.display_map_rb)
        # self.bt_zoom_zone.clicked.connect(self.zoom_on_zone)
        self.bt_edit_law.clicked.connect(self.enable_input)
        self.bt_cancel_law.clicked.connect(self.cancel_input)
        self.bt_valid_law.clicked.connect(self.save_input)

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
            if row[0] == "ctrlLaw":
                self.cc_law_act.setChecked(row[1])
                self.cb_law_fld.setCurrentText(row[2])
                self.sb_law_seuil.setValue(row[3])
                self.sb_law_sigma.setValue(row[4])
                self.sb_cote_a.setValue(row[5][0][0])
                self.sb_cote_b.setValue(row[5][0][1])
                self.sb_debit_a.setValue(row[5][1][0])
                self.sb_debit_b.setValue(row[5][1][1])
                self.sb_debit_lin_a.setValue(row[5][2][0])
                self.sb_debit_lin_b.setValue(row[5][2][1])

    def load_obs(self):
        mdl = QStandardItemModel()
        mdl.setColumnCount(1)

        sql = "SELECT id, code FROM {0}.observations " \
              "WHERE type = '{1}' " \
              "ORDER BY code"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA,
                                             self.cb_law_fld.currentText()),
                                  fetch=True)
        for row in rows:
            itm = QStandardItem()
            itm.setData(row[1], 0)
            itm.setData(row[0], 32)
            itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            itm.setCheckState(0)
            mdl.appendRow(itm)

        self.lv_law_obs.setModel(mdl)
        self.lv_law_obs.setSpacing(2)
        self.display_law_info()
        self.change_law_config()

    def change_law_config(self):
        sql = "UPDATE {0}.assim_config SET " \
              "active = %s, " \
              "control_var = %s, " \
              "seuil_rejet_misfit = %s, " \
              "iterations_sigma = %s, " \
              "perturbation_val = %s " \
              "WHERE control_type = 'ctrlLaw'".format(self.mdb.SCHEMA)
        recs = [[self.cc_law_act.isChecked(), self.cb_law_fld.currentText(),
                 self.sb_law_seuil.value(), self.sb_law_sigma.value(),
                 [[self.sb_cote_a.value(), self.sb_cote_b.value()],
                  [self.sb_debit_a.value(), self.sb_debit_b.value()],
                  [self.sb_debit_lin_a.value(), self.sb_debit_lin_b.value()]]]]
        self.mdb.run_query(sql.format(self.mdb.SCHEMA), many=True, list_many=recs)

    def verif_laws(self):
        d_tmp = self.mdb.zone_ks()

        sql = "SELECT * FROM {0}.assim_law"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        if not rows:
            recs = [[idx, 0, False, 5., 10., [], [], False, 1., False, 2., 'Toto']
                    for idx in range(len(d_tmp["branch"]))]
            sql = "INSERT INTO {0}.assim_law (id_law, id_type, active, val_min, val_max, " \
                  "lst_obs_h, lst_obs_q, active_a, std_a, active_b, std_b, source_law) " \
                  "VALUES ({1})"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA, ', '.join(["%s"]*len(recs[0]))),
                               many=True, list_many=recs)

    def load_laws(self):
        self.d_laws.clear()

        sql = "SELECT id_law, active, lst_obs_h, lst_obs_q, val_min, val_max, " \
              "active_a, std_a, active_b, std_b FROM {0}.assim_law " \
              "ORDER BY id_law"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        for row in rows:
            self.d_laws[row[0]] = {"law_name": "Law {}".format(row[0]),
                                   "active": row[1],
                                   "prm": {"lst_obs_h": row[2],
                                           "lst_obs_q": row[3],
                                           "val_min": row[4],
                                           "val_max": row[5],
                                           "active_a": row[6],
                                           "std_a": row[7],
                                           "active_b": row[8],
                                           "std_b": row[9]}}

        mdl = QStandardItemModel()
        mdl.setColumnCount(1)
        for id_law, p_law in self.d_laws.items():
            itm = QStandardItem()
            itm.setData(p_law["law_name"], 0)
            itm.setData(id_law, 32)
            itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            # if p_law["auto_del"]:
            #     itm.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))
            if p_law["active"]:
                itm.setCheckState(2)
            else:
                itm.setCheckState(0)
            mdl.appendRow(itm)

        self.lv_law.setIconSize(QSize(14, 14))
        self.lv_law.setModel(mdl)
        self.lv_law.setSpacing(2)
        self.lv_law.model().itemChanged.connect(self.law_status_changed)
        self.lv_law.selectionModel().selectionChanged.connect(self.current_law_changed)

        if self.lv_law.model().rowCount():
            self.lv_law.setCurrentIndex(self.lv_law.model().item(0, 0).index())

    def reload_law(self, id_law):
        sql = "SELECT lst_obs_h, lst_obs_q, val_min, val_max, " \
              "active_a, std_a, active_b, std_b FROM {0}.assim_law " \
              "WHERE id_law = {1}"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA, id_law), fetch=True)
        row = rows[0]
        self.d_laws[id_law]["prm"] = {"lst_obs_h": row[0], "lst_obs_q": row[1],
                                      "val_min": row[2], "val_max": row[3],
                                      "active_a": row[4], "std_a": row[5],
                                      "active_b": row[6], "std_b": row[7]}

    # def zone_selected_from_map(self, selected_abs):
    #     sql = "SELECT id_zone FROM {0}.assim_ks WHERE " \
    #           "abs_min <= {1} AND abs_max > {1}".format(self.mdb.SCHEMA, selected_abs)
    #     row = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
    #     if row:
    #         id_zone_selected = row[0][0]
    #         for row in range(self.lv_zone.model().rowCount()):
    #             itm = self.lv_zone.model().item(row, 0)
    #             if itm.data(32) == id_zone_selected:
    #                 self.lv_zone.setCurrentIndex(itm.index())
    #                 break

    def current_law_changed(self):
        if self.lv_law.selectionModel().hasSelection():
            idxs = self.lv_law.selectionModel().selectedIndexes()
            if idxs:
                idx = idxs[0]
                itm = self.lv_law.model().itemFromIndex(idx)
                self.cur_law = itm.data(32)
            else:
                self.cur_law = None
        else:
            self.cur_law = None

        self.display_law_info()
        # self.draw_zone_rb()

    def display_law_info(self):
        self.gb_law.setTitle("Aucune loi sélectionné")

        if self.cur_law is not None:
            d_law = self.d_laws[self.cur_law]

            self.gb_law.setTitle(d_law["law_name"])
            self.sb_law_min.setValue(d_law["prm"]["val_min"])
            self.sb_law_max.setValue(d_law["prm"]["val_max"])
            self.gb_a_ctrl.setChecked(d_law["prm"]["active_a"])
            self.sb_a_std.setValue(d_law["prm"]["std_a"])
            self.gb_b_ctrl.setChecked(d_law["prm"]["active_b"])
            self.sb_b_std.setValue(d_law["prm"]["std_b"])

            l_obs = d_law["prm"]["lst_obs_{}".format(str(self.cb_law_fld.currentText()).lower())]
            for r in range(self.lv_law_obs.model().rowCount()):
                itm = self.lv_law_obs.model().item(r, 0)
                if itm.data(32) in l_obs:
                    itm.setCheckState(2)
                else:
                    itm.setCheckState(0)

    def law_status_changed(self, itm):
        sql = "UPDATE {0}.assim_law SET active = {1} WHERE id_law = {2}"
        self.mdb.run_query(sql.format(self.mdb.SCHEMA, itm.checkState() == 2, itm.data(32)))

    # def display_map_rb(self):
    #     self.rb_visible = self.bt_disp_zone.isChecked()
    #     self.draw_zone_rb()

    # def draw_zone_rb(self):
    #     self.rb.reset(self.rb_format)
    #     if self.rb_visible and self.cur_zone_ks is not None:
    #         rb_geom = self.d_zone_ks[self.cur_zone_ks]["geom"]
    #         # if self.rubber_format == QgsWkbTypes.PolygonGeometry:
    #         #     rubber_geom = rubber_geom.buffer(10., 18)
    #
    #         self.rb.addGeometry(rb_geom)
    #         self.rb.show()

    # def zoom_on_zone(self):
    #     if self.cur_zone_ks is not None:
    #         ks_geom = self.d_zone_ks[self.cur_zone_ks]["geom"]
    #         ks_bb = ks_geom.boundingBox()
    #         ks_bb = ks_bb.buffered(ks_bb.width() * 0.05)
    #         canvas = self.iface.mapCanvas()
    #         canvas.setExtent(ks_bb)
    #         canvas.refresh()
    #         canvas.waitWhileRendering()

    def enable_input(self):
        self.gb_law.setEnabled(True)
        self.gb_param_law.setEnabled(False)
        # self.bt_sel_zone.setChecked(False)
        self.fra_law_sel.setEnabled(False)

    def disable_input(self):
        self.gb_param_law.setEnabled(True)
        self.fra_law_sel.setEnabled(True)
        self.gb_law.setEnabled(False)

    def cancel_input(self):
        self.disable_input()
        self.display_law_info()

    def save_input(self):
        l_obs = []
        for r in range(self.lv_law_obs.model().rowCount()):
            itm = self.lv_law_obs.model().item(r, 0)
            if itm.checkState() == 2:
                l_obs.append(itm.data(32))

        recs = [[self.sb_law_min.value(), self.sb_law_max.value(),
                 self.gb_a_ctrl.isChecked(), self.sb_a_std.value(),
                 self.gb_b_ctrl.isChecked(), self.sb_b_std.value(),
                 l_obs]]

        sql = "UPDATE {0}.assim_law SET " \
              "val_min = %s, " \
              "val_max = %s, " \
              "active_a = %s, " \
              "std_a = %s, " \
              "active_b = %s, " \
              "std_b = %s, " \
              "lst_obs_{1} = %s " \
              "WHERE id_law = {2}".format(self.mdb.SCHEMA,
                                          str(self.cb_law_fld.currentText()).lower(),
                                          self.cur_law)
        self.mdb.run_query(sql.format(self.mdb.SCHEMA), many=True, list_many=recs)

        self.disable_input()
        self.reload_law(self.cur_law)
        self.display_law_info()

        # if self.lv_law.selectionModel().hasSelection():
        #     idxs = self.lv_law.selectionModel().selectedIndexes()
        #     if idxs:
        #         idx = idxs[0]
        #         itm = self.lv_law.model().itemFromIndex(idx)
        #         itm.setIcon(QIcon())
