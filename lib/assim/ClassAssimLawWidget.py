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
from qgis.PyQt.QtCore import pyqtSignal, Qt, QSize
from qgis.PyQt.QtGui import QIcon, QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QMessageBox, QButtonGroup

from qgis.core import QgsApplication, QgsGeometry

FORM_CLASS, BASE = uic.loadUiType(
    os.path.join(os.path.join(os.path.dirname(__file__), "..", "..", "ui/ui_assimilation_law.ui"))
)

D_PVAR = {0: 'perturbationsCote',
          1: 'perturbationsDebit',
          2: 'perturbationsDebitLineique'}


class ClassAssimLawWidget(BASE, FORM_CLASS):
    """
    Class allow to update ks mesh planim of the selected profiles
    """
    display_rb = pyqtSignal()

    def __init__(self, mgis, iface):
        super(ClassAssimLawWidget, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui_loaded = False

        self.bg_perturb_var = QButtonGroup()
        self.bg_perturb_var.addButton(self.rb_cote, 0)
        self.bg_perturb_var.addButton(self.rb_debit, 1)
        self.bg_perturb_var.addButton(self.rb_debit_lin, 2)

        self.bt_reload_laws.setIcon(QIcon(QgsApplication.iconPath("mActionReload.svg")))
        self.bt_zoom_law.setIcon(QIcon(QgsApplication.iconPath("mActionZoomToSelected.svg")))
        self.bt_disp_law.setIcon(QIcon(QgsApplication.iconPath("mActionShowSelectedLayers.svg")))

        self.bt_cancel_law.setIcon(QIcon(QgsApplication.iconPath("mActionCancelAllEdits.svg")))
        self.bt_valid_law.setIcon(QIcon(QgsApplication.iconPath("mActionSaveAllEdits.svg")))

        laws_updated = self.verif_laws()
        if laws_updated:
            QMessageBox.warning(None, "Warning", "Definition of some laws "
                                                 "have been automatically upadated.")

        self.cur_perturb_var = str()
        self.cur_source = str()
        self.cur_law = None
        self.d_laws = dict()

        self.bg_perturb_var.idClicked.connect(self.cur_perturb_var_changed)
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

        self.bt_reload_laws.clicked.connect(self.reload_laws)
        self.bt_disp_law.clicked.connect(self.display_map_rb)
        self.bt_zoom_law.clicked.connect(self.zoom_on_law)
        self.bt_edit_law.clicked.connect(self.enable_input)
        self.bt_cancel_law.clicked.connect(self.cancel_input)
        self.bt_valid_law.clicked.connect(self.save_input)

        self.load_laws()
        self.load_obs()
        self.load_config()

        self.ui_loaded = True

    def load_config(self):
        sql = "SELECT control_type, active, control_var, seuil_rejet_misfit, " \
              "iterations_sigma, perturbation_val, perturbation_act " \
              "FROM {0}.assim_config WHERE control_type = 'ctrlLaw'"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        if not rows:
            recs = [[2, "ctrlLaw", False, "H", 50, 1,
                     ["perturbationsCote", "perturbationsDebit", "perturbationsDebitLineique"],
                     [[1.0, 0.5], [1.1, 6.0], [0.0, 0.0]], "perturbationsCote"]]
            sql = "INSERT INTO {0}.assim_config (id_type, control_type, active, control_var, " \
                  "seuil_rejet_misfit, iterations_sigma, perturbation_var, perturbation_val, " \
                  "perturbation_act) VALUES ({1})"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA,
                                          ', '.join(["%s"]*len(recs[0]))),
                               many=True, list_many=recs)

            sql = "SELECT control_type, active, control_var, seuil_rejet_misfit, " \
                  "iterations_sigma, perturbation_val, perturbation_act " \
                  "FROM {0}.assim_config WHERE control_type = 'ctrlLaw'"
            rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        row = rows[0]
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
        for id_btn, var in D_PVAR.items():
            if var == row[6]:
                self.bg_perturb_var.button(id_btn).click()

    def load_obs(self):
        mdl = QStandardItemModel()
        mdl.setColumnCount(1)

        sql = "SELECT id, code FROM {0}.observations " \
              "WHERE type = '{1}' AND code IN (SELECT code FROM {0}.outputs WHERE active IS True)" \
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
        if self.ui_loaded:
            self.display_law_info()
            self.change_law_config()

    def cur_perturb_var_changed(self, id_var):
        self.cur_perturb_var = D_PVAR[id_var]
        if self.cur_perturb_var in ['perturbationsCote', 'perturbationsDebit']:
            self.cur_source = 'extremities'
        else:
            self.cur_source = 'lateral_inflows'

        for sb in [self.sb_cote_a, self.sb_cote_b, self.sb_debit_a, self.sb_debit_b,
                   self.sb_debit_lin_a, self.sb_debit_lin_b]:
            sb.setEnabled(True)

        if self.cur_perturb_var == 'perturbationsCote':

            self.lbl_typ_law.setText('Limnigraphs')
            for sb in [self.sb_debit_a, self.sb_debit_b, self.sb_debit_lin_a, self.sb_debit_lin_b]:
                sb.setEnabled(False)

        if self.cur_perturb_var == 'perturbationsDebit':
            self.lbl_typ_law.setText('Hydrographs')
            for sb in [self.sb_cote_a, self.sb_cote_b, self.sb_debit_lin_a, self.sb_debit_lin_b]:
                sb.setEnabled(False)

        if self.cur_perturb_var == 'perturbationsDebitLineique':
            self.lbl_typ_law.setText('Laws')
            for sb in [self.sb_cote_a, self.sb_cote_b, self.sb_debit_a, self.sb_debit_b]:
                sb.setEnabled(False)

        self.change_law_config()
        self.display_laws()

    def change_law_config(self):
        if self.ui_loaded:
            sql = "UPDATE {0}.assim_config SET " \
                  "active = %s, " \
                  "control_var = %s, " \
                  "seuil_rejet_misfit = %s, " \
                  "iterations_sigma = %s, " \
                  "perturbation_val = %s, " \
                  "perturbation_act = %s " \
                  "WHERE control_type = 'ctrlLaw'".format(self.mdb.SCHEMA)
            recs = [[self.cc_law_act.isChecked(), self.cb_law_fld.currentText(),
                     self.sb_law_seuil.value(), self.sb_law_sigma.value(),
                     [[self.sb_cote_a.value(), self.sb_cote_b.value()],
                      [self.sb_debit_a.value(), self.sb_debit_b.value()],
                      [self.sb_debit_lin_a.value(), self.sb_debit_lin_b.value()]],
                     self.cur_perturb_var]]
            self.mdb.run_query(sql.format(self.mdb.SCHEMA), many=True, list_many=recs)

    def verif_laws(self):
        laws_updated = False

        sql = "SELECT gid as law_id, name as law_name, 'extremities' as source_law, " \
              "'perturbationsCote' as id_type, geom as geom_obj " \
              "FROM {0}.extremities WHERE active IS True AND type = 2 " \
              "UNION " \
              "SELECT gid as law_id, name as law_name, 'extremities' as source_law, " \
              "'perturbationsDebit' as id_type, geom as geom_obj " \
              "FROM {0}.extremities WHERE active IS True AND type = 1 " \
              "UNION " \
              "SELECT gid as law_id, name as law_name, 'lateral_inflows' as source_law, " \
              "'perturbationsDebitLineique' as id_type, geom as geom_obj " \
              "FROM {0}.lateral_inflows WHERE active IS True " \
              "ORDER BY id_type, law_name"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_calc_law = dict()
        for p_law in rows:
            d_calc_law[(p_law[0], p_law[2], p_law[3])] = {"name": p_law[1], "geom": p_law[4]}

        sql = "SELECT id_law, source_law, id_type, active, auto_del, lst_obs_h, lst_obs_q, " \
              "val_min, val_max, active_a, std_a, active_b, std_b FROM {0}.assim_law"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        if not rows:
            recs = [[p_law[0], p_law[1], p_law[2], False, False, [], [],
                     10., 10., False, 1., False, 1.]
                    for p_law in d_calc_law.keys()]
            sql = "INSERT INTO {0}.assim_law (id_law, source_law, id_type, active, lst_obs_h, " \
                  "lst_obs_q, val_min, val_max, active_a, std_a, active_b, std_b) VALUES ({1})"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA, ', '.join(["%s"]*len(recs[0]))),
                               many=True, list_many=recs)

            sql = "SELECT id_law, source_law, id_type, active, auto_del, lst_obs_h, lst_obs_q, " \
                  "val_min, val_max, active_a, std_a, active_b, std_b FROM {0}.assim_law"
            rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_db_law = {tuple(row[0:3]): row for row in rows}

        if not(len(d_db_law) == len(d_calc_law) and
               all([k in d_db_law.keys() for k in d_calc_law.keys()])):
            recs = []
            for p_law in d_calc_law.keys():
                if p_law in d_db_law.keys():
                    rec = d_db_law[p_law]
                    recs.append(rec)
                else:
                    recs.append(
                        [p_law[0], p_law[1], p_law[2], False, True, [], [],
                         10., 10., False, 1., False, 1.])

            sql = "DELETE FROM {0}.assim_law"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            sql = "INSERT INTO {0}.assim_law (id_law, source_law, id_type, active, auto_del, " \
                  "lst_obs_h, lst_obs_q, val_min, val_max, active_a, std_a, active_b, std_b) " \
                  "VALUES ({1})"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA, ', '.join(["%s"] * len(recs[0]))),
                               many=True, list_many=recs)

            laws_updated = True

        return laws_updated

    def reload_laws(self):
        laws_updated = self.verif_laws()
        if laws_updated:
            QMessageBox.warning(None, "Warning", "Definition of some laws "
                                                 "have been automatically upadated.")
            self.load_laws()

    def load_laws(self):
        self.d_laws.clear()
        self.d_laws = {'perturbationsCote': {},
                       'perturbationsDebit': {},
                       'perturbationsDebitLineique': {}}

        sql = "SELECT gid as law_id, name as law_name, 'extremities' as source_law, " \
              "'perturbationsCote' as id_type, ST_AsText(geom) as wkt_geom " \
              "FROM {0}.extremities WHERE active IS True AND type = 2 " \
              "UNION " \
              "SELECT gid as law_id, name as law_name, 'extremities' as source_law, " \
              "'perturbationsDebit' as id_type, ST_AsText(geom) as wkt_geom " \
              "FROM {0}.extremities WHERE active IS True AND type = 1 " \
              "UNION " \
              "SELECT gid as law_id, name as law_name, 'lateral_inflows' as source_law, " \
              "'perturbationsDebitLineique' as id_type, ST_AsText(geom) as wkt_geom " \
              "FROM {0}.lateral_inflows WHERE active IS True " \
              "ORDER BY id_type, law_name"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_calc_law = dict()
        for p_law in rows:
            d_calc_law[(p_law[0], p_law[2], p_law[3])] = {"name": p_law[1], "geom": p_law[4]}

        sql = "SELECT id_law, source_law, id_type, active, auto_del, lst_obs_h, lst_obs_q, " \
              "val_min, val_max, active_a, std_a, active_b, std_b FROM {0}.assim_law"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        for row in rows:
            id_law = row[0]
            type_law = row[2]
            self.d_laws[type_law][id_law] = {"law_name": d_calc_law[(row[0], row[1], row[2])]["name"],
                                             "geom": QgsGeometry.fromWkt(d_calc_law[(row[0], row[1], row[2])]["geom"]),
                                             "active": row[3],
                                             "auto_del": row[4],
                                             "prm": {"lst_obs_h": row[5],
                                                     "lst_obs_q": row[6],
                                                     "val_min": row[7],
                                                     "val_max": row[8],
                                                     "active_a": row[9],
                                                     "std_a": row[10],
                                                     "active_b": row[11],
                                                     "std_b": row[12]}}

    def display_laws(self):
        mdl = QStandardItemModel()
        mdl.setColumnCount(1)
        for id_law, p_law in self.d_laws[self.cur_perturb_var].items():
            itm = QStandardItem()
            itm.setData(p_law["law_name"], 0)
            itm.setData(id_law, 32)
            itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable)
            if p_law["auto_del"]:
                itm.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))
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

    def refresh_law(self, id_var, id_law):
        sql = "SELECT lst_obs_h, lst_obs_q, val_min, val_max, " \
              "active_a, std_a, active_b, std_b, auto_del FROM {0}.assim_law " \
              "WHERE id_law = {1} AND id_type = '{2}'"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA, id_law, id_var), fetch=True)
        row = rows[0]
        self.d_laws[id_var][id_law]["auto_del"] = row[8]
        self.d_laws[id_var][id_law]["prm"] = {"lst_obs_h": row[0], "lst_obs_q": row[1],
                                              "val_min": row[2], "val_max": row[3],
                                              "active_a": row[4], "std_a": row[5],
                                              "active_b": row[6], "std_b": row[7]}

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
        self.draw_law_rb()

    def display_law_info(self):
        self.gb_law.setTitle("Aucune loi sélectionné")

        if self.cur_law is not None:
            d_law = self.d_laws[self.cur_perturb_var][self.cur_law]
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
        sql = "UPDATE {0}.assim_law SET active = {1} WHERE id_law = {2} and id_type = '{3}'"
        self.mdb.run_query(sql.format(self.mdb.SCHEMA, itm.checkState() == 2,
                                      itm.data(32), self.cur_perturb_var))

    def display_map_rb(self):
        self.draw_law_rb()

    def draw_law_rb(self):
        self.display_rb.emit()

    def zoom_on_law(self):
        if self.cur_law is not None:
            ks_geom = self.d_laws[self.cur_perturb_var][self.cur_law]["geom"]
            ks_bb = ks_geom.boundingBox()
            ks_bb = ks_bb.buffered(2500.)
            canvas = self.iface.mapCanvas()
            canvas.setExtent(ks_bb)
            canvas.refresh()
            canvas.waitWhileRendering()

    def enable_input(self):
        self.gb_law.setEnabled(True)
        self.gb_param_law.setEnabled(False)
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
              "lst_obs_{1} = %s, " \
              "auto_del = False " \
              "WHERE id_law = {2} " \
              "AND source_law = '{3}'".format(self.mdb.SCHEMA,
                                              str(self.cb_law_fld.currentText()).lower(),
                                              self.cur_law,
                                              self.cur_source)
        self.mdb.run_query(sql.format(self.mdb.SCHEMA), many=True, list_many=recs)

        self.disable_input()
        self.refresh_law(self.cur_perturb_var, self.cur_law)
        self.display_law_info()

        if self.lv_law.selectionModel().hasSelection():
            idxs = self.lv_law.selectionModel().selectedIndexes()
            if idxs:
                idx = idxs[0]
                itm = self.lv_law.model().itemFromIndex(idx)
                itm.setIcon(QIcon())
