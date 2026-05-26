# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : mars,2026
copyright            : (C) 2017 by Artelia
email                :
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, Qt, QSize, qVersion
from qgis.PyQt.QtGui import QIcon, QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import (
    QgsApplication,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsWkbTypes,
    QgsDistanceArea,
    QgsProject,
    QgsUnitTypes,
)

from .FunctionAssimDialog import reproject_geom_to_project
from .tooltips.tooltips import apply_tooltips_from_json

FORM_CLASS, BASE = uic.loadUiType(
    os.path.join(os.path.join(os.path.dirname(__file__), "..", "..", "ui/ui_assimilation_ks.ui"))
)
QT_VERSION = [int(v) for v in qVersion().split(".")][0]


class ClassAssimKsWidget(BASE, FORM_CLASS):
    """Widget for managing Strickler coefficient (Ks) assimilation configuration.

    Allows users to define and edit Ks control zones and observation parameters.
    """

    display_rb = pyqtSignal()

    def __init__(self, mgis, iface):
        """Initialize the Ks assimilation widget.

        :param mgis: Main QGIS interface object.
        :param iface: QGIS interface instance.
        :return: None.
        """
        super(ClassAssimKsWidget, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        apply_tooltips_from_json(self, "assim_ks_widget.json")
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui_loaded = False
        self._updating_zone_ui = False
        if QT_VERSION > 5:
            self.qt_itm_ena = Qt.ItemFlag.ItemIsEnabled
            self.qt_itm_sel = Qt.ItemFlag.ItemIsSelectable
            self.qt_item_check = Qt.ItemFlag.ItemIsUserCheckable
            self.qt_check_stat = Qt.CheckState
        else:
            # QT5
            self.qt_itm_ena = Qt.ItemIsEnabled
            self.qt_itm_sel = Qt.ItemIsSelectable
            self.qt_item_check = Qt.ItemIsUserCheckable
            self.qt_check_stat = Qt

        self.bt_sel_zone.setIcon(QIcon(QgsApplication.iconPath("mActionIdentify.svg")))
        self.bt_sel_zone.toggled.connect(self.mgis.main_graph)

        self.bt_reload_ks.setIcon(QIcon(QgsApplication.iconPath("mActionReload.svg")))
        self.bt_zoom_zone.setIcon(QIcon(QgsApplication.iconPath("mActionZoomToSelected.svg")))
        self.bt_disp_zone.setIcon(QIcon(QgsApplication.iconPath("mActionShowSelectedLayers.svg")))
        self.bt_clr_warn_ks.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))

        ks_zones_updated = self.verif_ks_zones()
        if ks_zones_updated:
            QMessageBox.warning(
                None,
                "Warning",
                "Definition of some controls zone " "have been automatically upadated.",
            )

        self.cur_zone_ks = None
        self.cur_obs_ks = None
        self.last_selection_kind = None
        self.d_zone_ks = dict()
        self.d_obs_ks = dict()

        self.cc_ks_act.toggled.connect(self.change_ks_config)
        self.cb_ks_fld.currentTextChanged.connect(self.load_obs)
        self.sb_ks_seuil.valueChanged.connect(self.change_ks_config)
        self.sb_ks_sigma.valueChanged.connect(self.change_ks_config)
        self.sb_ks_pert_min.valueChanged.connect(self.change_ks_config)
        self.sb_ks_pert_maj.valueChanged.connect(self.change_ks_config)

        self.bt_reload_ks.clicked.connect(self.reload_zone_ks)
        self.bt_disp_zone.clicked.connect(self.display_map_rb)
        self.bt_zoom_zone.clicked.connect(self.zoom_on_zone)
        self.bt_clr_warn_ks.clicked.connect(self.clear_warning_ks)

        self.connect_zone_auto_save()
        self.set_direct_edit_mode()

        self.load_config()
        self.load_obs()
        self.load_zone_ks()

        self.ui_loaded = True

    def set_direct_edit_mode(self):
        """Configure direct editing mode with automatic save."""
        self.gb_zone.setEnabled(True)
        self.gb_param_ks.setEnabled(True)
        self.fra_zone_sel.setEnabled(True)
        self.update_ks_edit_state()

    def is_current_zone_editable(self):
        """Return True only if current zone is selected and checked."""
        if self.cur_zone_ks is None or not self.lv_zone.selectionModel().hasSelection():
            return False

        idxs = self.lv_zone.selectionModel().selectedIndexes()
        if not idxs:
            return False

        item = self.lv_zone.model().itemFromIndex(idxs[0])
        return item is not None and item.checkState() == self.qt_check_stat.Checked

    def update_ks_edit_state(self):
        """Enable or disable the Ks edit frame depending on current zone state."""
        editable = self.is_current_zone_editable()
        self.fra_ks_edit.setEnabled(editable)

    def connect_zone_auto_save(self):
        """Connect editable zone widgets to automatic save."""
        self.gb_minor.toggled.connect(self.on_zone_field_changed)
        self.sb_minor_std.valueChanged.connect(self.on_zone_field_changed)
        self.sb_minor_inf.valueChanged.connect(self.on_zone_field_changed)
        self.sb_minor_sup.valueChanged.connect(self.on_zone_field_changed)

        self.gb_major.toggled.connect(self.on_zone_field_changed)
        self.sb_major_std.valueChanged.connect(self.on_zone_field_changed)
        self.sb_major_inf.valueChanged.connect(self.on_zone_field_changed)
        self.sb_major_sup.valueChanged.connect(self.on_zone_field_changed)

    def on_zone_field_changed(self, *_):
        """Save the current zone after any user change."""
        if self._updating_zone_ui or not self.is_current_zone_editable():
            return
        self.save_input()

    def load_config(self):
        """Load Ks assimilation configuration from database.

        Retrieves or creates default ctrlKS configuration with observation variables,
        thresholds, sigma iterations, and perturbation values.
        :return: None. Updates UI widgets with loaded configuration.
        """
        sql = (
            "SELECT control_type, active, control_var, seuil_rejet_misfit, "
            "iterations_sigma, perturbation_val "
            "FROM {0}.assim_config WHERE control_type = 'ctrlKS'"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        if not rows:
            recs = [[1, "ctrlKS", False, "H", 500, 1, ["ksMin", "ksMaj"], [[5], [1]], None]]
            sql = (
                "INSERT INTO {0}.assim_config (id_type, control_type, active, control_var, "
                "seuil_rejet_misfit, iterations_sigma, perturbation_var, perturbation_val, "
                "perturbation_act) VALUES ({1})"
            )
            self.mdb.run_query(
                sql.format(self.mdb.SCHEMA, ", ".join(["%s"] * len(recs[0]))),
                many=True,
                list_many=recs,
            )

            sql = (
                "SELECT control_type, active, control_var, seuil_rejet_misfit, "
                "iterations_sigma, perturbation_val "
                "FROM {0}.assim_config WHERE control_type = 'ctrlKS'"
            )
            rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        row = rows[0]
        self.cc_ks_act.setChecked(row[1])
        self.cb_ks_fld.setCurrentText(row[2])
        self.sb_ks_seuil.setValue(row[3])
        self.sb_ks_sigma.setValue(row[4])
        self.sb_ks_pert_min.setValue(row[5][0][0])
        self.sb_ks_pert_maj.setValue(row[5][1][0])

    def load_obs(self):
        """Load available observations for the current observation variable.

        Populates the observation list view with active observations matching
        the current control variable (H or Q).
        :return: None. Updates observation list and display.
        """
        mdl = QStandardItemModel()
        mdl.setColumnCount(1)
        self.d_obs_ks.clear()

        sql_srid = (
            "SELECT f_table_name, srid "
            "FROM geometry_columns "
            "WHERE f_table_schema = %s "
            "AND f_table_name IN ('outputs')"
        )
        srid_rows = self.mdb.run_query(sql_srid, fetch=True, params=[self.mdb.SCHEMA])
        d_srid = {
            row[0]: QgsCoordinateReferenceSystem(f"EPSG:{row[1]}") for row in srid_rows if row[1]
        }

        sql = (
            "SELECT obs.id, obs.code, ST_AsText(out.geom) "
            "FROM {0}.observations obs "
            "JOIN {0}.outputs out ON out.code = obs.code "
            "WHERE obs.type = '{1}' "
            "AND out.active IS True "
            "ORDER BY obs.code"
        )
        rows = self.mdb.run_query(
            sql.format(self.mdb.SCHEMA, self.cb_ks_fld.currentText()), fetch=True
        )

        for row in rows:
            obs_geom = QgsGeometry.fromWkt(row[2]) if row[2] else None
            self.d_obs_ks[row[0]] = {
                "code": row[1],
                "geom": obs_geom,
                "crs": d_srid.get("outputs", QgsCoordinateReferenceSystem()),
            }

            itm = QStandardItem()
            itm.setData(row[1], 0)
            itm.setData(row[0], 32)
            itm.setFlags(self.qt_itm_ena | self.qt_itm_sel | self.qt_item_check)
            itm.setCheckState(self.qt_check_stat.Unchecked)
            mdl.appendRow(itm)

        self.lv_ks_obs.setModel(mdl)
        self.lv_ks_obs.setSpacing(2)
        self.lv_ks_obs.model().itemChanged.connect(self.on_zone_field_changed)
        self.lv_ks_obs.clicked.connect(self.on_lv_clicked)

        self.cur_obs_ks = None
        if self.last_selection_kind == "obs":
            self.last_selection_kind = None

        self.display_zone_info()
        self.change_ks_config()

    def on_lv_clicked(self):
        sender = self.sender()
        if sender == self.lv_zone:
            self.current_zone_changed()
        elif sender == self.lv_ks_obs:
            self.current_obs_changed()

    def change_ks_config(self):
        """Update Ks configuration in database when form values change.

        Persists changes to active state, control variable, and perturbation values.
        :return: None. Updates database configuration.
        """
        if self.ui_loaded:
            sql = (
                "UPDATE {schema}.assim_config SET "
                "active = %s, "
                "control_var = %s, "
                "seuil_rejet_misfit = %s, "
                "iterations_sigma = %s, "
                "perturbation_val = %s "
                "WHERE control_type = 'ctrlKS'"
            )
            recs = [
                [
                    self.cc_ks_act.isChecked(),
                    self.cb_ks_fld.currentText(),
                    self.sb_ks_seuil.value(),
                    self.sb_ks_sigma.value(),
                    [[self.sb_ks_pert_min.value()], [self.sb_ks_pert_maj.value()]],
                ]
            ]
            self.mdb.run_query(sql, many=True, list_many=recs, schema=True)

    def verif_ks_zones(self):
        """Verify and update Ks zone definitions against current model geometry.

        Synchronizes database zones with calculated bed coefficient zones from the model,
        creates missing zones, and updates reference coefficients as needed.
        :return: ``True`` if zones were updated, ``False`` otherwise.
        """
        ks_zones_updated = False

        d_calc_ks = self.mdb.zone_ks()

        sql = (
            "SELECT id_zone, branchnum, abs_min, abs_max, active, auto_del, "
            "lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, "
            "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        if not rows:
            recs = [
                [
                    idx,
                    d_calc_ks["branch"][idx],
                    d_calc_ks["zoneabsstart"][idx],
                    d_calc_ks["zoneabsend"][idx],
                    False,
                    False,
                    [],
                    [],
                    False,
                    1,
                    d_calc_ks["minbedcoef"][idx],
                    d_calc_ks["minbedcoef"][idx],
                    False,
                    1,
                    d_calc_ks["majbedcoef"][idx],
                    d_calc_ks["majbedcoef"][idx],
                ]
                for idx in range(len(d_calc_ks["branch"]))
            ]
            sql = (
                "INSERT INTO {0}.assim_ks (id_zone, branchnum, abs_min, abs_max, active, "
                "auto_del, lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, "
                "active_maj, std_maj, val_inf_maj, val_sup_maj) VALUES ({1})"
            )
            self.mdb.run_query(
                sql.format(self.mdb.SCHEMA, ", ".join(["%s"] * len(recs[0]))),
                many=True,
                list_many=recs,
            )

            sql = (
                "SELECT id_zone, branchnum, abs_min, abs_max, active, auto_del, "
                "lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, "
                "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks"
            )
            rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_db_ks = {tuple(row[1:4]): row for row in rows}
        d_verif_ks = {
            (
                d_calc_ks["branch"][idx],
                d_calc_ks["zoneabsstart"][idx],
                d_calc_ks["zoneabsend"][idx],
            ): (
                d_calc_ks["minbedcoef"][idx],
                d_calc_ks["majbedcoef"][idx],
            )
            for idx in range(len(d_calc_ks["branch"]))
        }

        if not (
            len(d_db_ks) == len(d_verif_ks)
            and all([k in d_db_ks.keys() for k in d_verif_ks.keys()])
        ):
            recs = []
            idx_ks = 0
            for id_ks, (min_coef, maj_coef) in d_verif_ks.items():
                if id_ks in d_db_ks.keys():
                    rec = d_db_ks[id_ks]
                    rec[0] = idx_ks
                    recs.append(rec)
                else:
                    recs.append(
                        [
                            idx_ks,
                            *id_ks,
                            False,
                            True,
                            [],
                            [],
                            False,
                            2,
                            min_coef,
                            min_coef,
                            False,
                            3,
                            maj_coef,
                            maj_coef,
                        ]
                    )
                idx_ks += 1

            sql = "DELETE FROM {0}.assim_ks"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            sql = (
                "INSERT INTO {0}.assim_ks (id_zone, branchnum, abs_min, abs_max, active, "
                "auto_del, lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, "
                "active_maj, std_maj, val_inf_maj, val_sup_maj) VALUES ({1})"
            )
            self.mdb.run_query(
                sql.format(self.mdb.SCHEMA, ", ".join(["%s"] * len(recs[0]))),
                many=True,
                list_many=recs,
            )
            ks_zones_updated = True

        sql = (
            "SELECT branchnum, abs_min, abs_max,"
            "val_inf_min, val_sup_min, val_inf_maj, val_sup_maj FROM {0}.assim_ks"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        d_db_ks = {tuple(row[:3]): tuple(row[3:]) for row in rows}

        d_edit = {"val_inf_min": [], "val_sup_min": [], "val_inf_maj": [], "val_sup_maj": []}
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
                sql = (
                    "UPDATE {0}.assim_ks SET {1} = %s, active = False, auto_del = True "
                    "WHERE branchnum = %s AND abs_min = %s AND abs_max = %s"
                )
                self.mdb.run_query(sql.format(self.mdb.SCHEMA, fld), many=True, list_many=recs)
                ks_zones_updated = True

        return ks_zones_updated

    def reload_zone_ks(self):
        """Reload Ks zones by verifying and refreshing from database.

        Checks zone definitions and reloads the zone list if updates were made.
        :return: None. Updates zone list if verification detected changes.
        """
        ks_zones_updated = self.verif_ks_zones()
        if ks_zones_updated:
            QMessageBox.warning(
                None,
                "Warning",
                "Definition of some controls zone " "have been automatically upadated.",
            )
            self.load_zone_ks()

    def load_zone_ks(self):
        """Load and display Ks control zones from database.

        Populates the zone list view with all configured zones including their
        active status and any auto-deletion flags.
        :return: None. Updates zone list view and sets up signal connections.
        """
        self.d_zone_ks.clear()
        # Get SIRD of the sources table for PostGIS
        sql_srid = (
            "SELECT f_table_name, srid "
            "FROM geometry_columns "
            "WHERE f_table_schema = %s "
            "AND f_table_name IN ('branchs')"
        )
        srid_rows = self.mdb.run_query(sql_srid, fetch=True, params=[self.mdb.SCHEMA])
        d_srid = {
            row[0]: QgsCoordinateReferenceSystem(f"EPSG:{row[1]}") for row in srid_rows if row[1]
        }

        d_calc_ks = self.mdb.zone_ks()
        d_info_ks = {
            (
                d_calc_ks["branch"][idx],
                d_calc_ks["zoneabsstart"][idx],
                d_calc_ks["zoneabsend"][idx],
            ): {
                "num_zone": d_calc_ks["branch_zone"][idx],
                "min_coef": d_calc_ks["minbedcoef"][idx],
                "maj_coef": d_calc_ks["majbedcoef"][idx],
                "geom": d_calc_ks["geom"][idx],
            }
            for idx in range(len(d_calc_ks["branch"]))
        }

        sql = (
            "SELECT id_zone, branchnum, abs_min, abs_max, active, auto_del, "
            "lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, "
            "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks "
            "ORDER BY abs_min"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        for row in rows:
            info_ks = d_info_ks[tuple(row[1:4])]
            self.d_zone_ks[row[0]] = {
                "zone_name": "Zone {}.{}".format(row[1], info_ks["num_zone"]),
                "geom": QgsGeometry.fromWkt(info_ks["geom"]),
                "crs": d_srid.get("branchs", QgsCoordinateReferenceSystem()),
                "min_coef": info_ks["min_coef"],
                "maj_coef": info_ks["maj_coef"],
                "branch_num": row[1],
                "abs_start": row[2],
                "abs_end": row[3],
                "active": row[4],
                "auto_del": row[5],
                "prm": {
                    "lst_obs_h": row[6],
                    "lst_obs_q": row[7],
                    "active_min": row[8],
                    "std_min": row[9],
                    "val_inf_min": row[10],
                    "val_sup_min": row[11],
                    "active_maj": row[12],
                    "std_maj": row[13],
                    "val_inf_maj": row[14],
                    "val_sup_maj": row[15],
                },
            }

        mdl = QStandardItemModel()
        mdl.setColumnCount(1)
        for id_ks, p_ks in self.d_zone_ks.items():
            itm = QStandardItem()
            itm.setData(p_ks["zone_name"], 0)
            itm.setData(id_ks, 32)
            itm.setFlags(self.qt_itm_ena | self.qt_itm_sel | self.qt_item_check)
            if p_ks["auto_del"]:
                itm.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))
            if p_ks["active"]:
                itm.setCheckState(self.qt_check_stat.Checked)
            else:
                itm.setCheckState(self.qt_check_stat.Unchecked)
            mdl.appendRow(itm)

        self.lv_zone.setIconSize(QSize(14, 14))
        self.lv_zone.setModel(mdl)
        self.lv_zone.setSpacing(2)
        self.lv_zone.model().itemChanged.connect(self.zone_status_changed)
        self.lv_zone.clicked.connect(self.on_lv_clicked)

        if self.lv_zone.model().rowCount():
            self.lv_zone.setCurrentIndex(self.lv_zone.model().item(0, 0).index())
        else:
            self.cur_zone_ks = None

        self.last_selection_kind = None
        self.draw_zone_rb()
        self.update_ks_edit_state()

    def refresh_zone_ks(self, id_zone):
        """Refresh parameter data for a specific Ks zone from database.

        :param id_zone: Zone identifier to refresh.
        :return: None. Updates *self.d_zone_ks* for the given zone.
        """
        sql = (
            "SELECT lst_obs_h, lst_obs_q, active_min, std_min, val_inf_min, val_sup_min, "
            "active_maj, std_maj, val_inf_maj, val_sup_maj FROM {0}.assim_ks "
            "WHERE id_zone = {1}"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA, id_zone), fetch=True)
        row = rows[0]
        self.d_zone_ks[id_zone]["prm"] = {
            "lst_obs_h": row[0],
            "lst_obs_q": row[1],
            "active_min": row[2],
            "std_min": row[3],
            "val_inf_min": row[4],
            "val_sup_min": row[5],
            "active_maj": row[6],
            "std_maj": row[7],
            "val_inf_maj": row[8],
            "val_sup_maj": row[9],
        }

    def zone_selected_from_map(self, selected_abs):
        """Select a Ks zone based on abscissa location from map interaction.

        :param selected_abs: Abscissa value of the selected location on the branch.
        :return: None. Updates current zone selection in list view.
        """
        sql = "SELECT id_zone FROM {schema}.assim_ks WHERE abs_min <= %s AND abs_max > %s"
        row = self.mdb.run_query(sql, fetch=True, params=[selected_abs, selected_abs], schema=True)
        if row:
            id_zone_selected = row[0][0]
            for row in range(self.lv_zone.model().rowCount()):
                itm = self.lv_zone.model().item(row, 0)
                if itm.data(32) == id_zone_selected:
                    self.lv_zone.setCurrentIndex(itm.index())
                    break

    def current_zone_changed(self):
        """Handle zone selection change in the zone list view.

        :return: None. Updates current zone, displays zone info, and draws representation.
        """
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

        if self.cur_zone_ks is not None:
            self.last_selection_kind = "zone"
            self.cur_obs_ks = None
            self.lv_ks_obs.clearSelection()
        elif self.last_selection_kind == "zone":
            self.last_selection_kind = None

        self.display_zone_info()
        self.update_ks_edit_state()
        self.draw_zone_rb()

    def current_obs_changed(self):
        """Handle observation selection change in lv_ks_obs."""
        self.cur_obs_ks = None
        if self.lv_ks_obs.selectionModel().hasSelection():
            idxs = self.lv_ks_obs.selectionModel().selectedIndexes()
            if idxs:
                itm = self.lv_ks_obs.model().itemFromIndex(idxs[0])
                self.cur_obs_ks = itm.data(32)

        if self.cur_obs_ks is not None:
            self.last_selection_kind = "obs"
        elif self.last_selection_kind == "obs":
            self.last_selection_kind = None

        self.draw_zone_rb()

    def get_current_rb_data(self):
        """Return current rubber band context for map display."""
        if not self.bt_disp_zone.isChecked() or not self.last_selection_kind:
            return None

        if self.last_selection_kind == "zone" and self.cur_zone_ks is not None:
            d_zone = self.d_zone_ks.get(self.cur_zone_ks, {})
            return {
                "geom": d_zone.get("geom"),
                "crs": d_zone.get("crs"),
                "is_observation": False,
            }

        if self.last_selection_kind == "obs" and self.cur_obs_ks is not None:
            d_obs = self.d_obs_ks.get(self.cur_obs_ks, {})
            return {
                "geom": d_obs.get("geom"),
                "crs": d_obs.get("crs"),
                "is_observation": True,
            }

        return None

    def _get_last_selected_geom(self):
        """Return geometry and CRS for current zoom context."""
        rb_data = self.get_current_rb_data()
        if not rb_data:
            return None, None
        return rb_data.get("geom"), rb_data.get("crs")

    def zoom_on_zone(self):
        """Zoom map to last selected element (zone or observation)."""
        geom, geom_crs = self._get_last_selected_geom()
        if geom is None:
            return

        geom_to_display = reproject_geom_to_project(geom, geom_crs)
        if geom_to_display.isEmpty():
            return

        canvas = self.iface.mapCanvas()
        crs = canvas.mapSettings().destinationCrs()
        da = QgsDistanceArea()
        da.setSourceCrs(crs, QgsProject.instance().transformContext())
        is_degree = da.lengthUnits() == QgsUnitTypes.DistanceDegrees

        if geom_to_display.type() == QgsWkbTypes.PointGeometry:
            point = geom_to_display.asPoint()
            pad = 0.0005 if is_degree else 20.0

            rect = QgsRectangle(point.x() - pad, point.y() - pad, point.x() + pad, point.y() + pad)
        else:
            rect = geom_to_display.boundingBox()
            pad = max(rect.width(), rect.height()) * 0.05
            if pad <= 0:
                pad = 0.0005 if is_degree else 20.0
            rect = rect.buffered(pad)

        canvas.setExtent(rect)
        canvas.refresh()

    def clear_warning_ks(self):
        """Clear auto-delete warning flags for all Ks zones.

        Sets auto_del to False for all zones marked with warning icon and refreshes
        the zone list view to remove warning icons.
        :return: None. Updates database and refreshes zone display.
        """
        sql = "UPDATE {schema}.assim_ks SET auto_del = False"
        self.mdb.run_query(sql, schema=True)
        self.load_zone_ks()

    def display_map_rb(self):
        """Refresh map rubber band display from current Ks selection context."""
        self.draw_zone_rb()

    def zone_status_changed(self, item):
        """Handle zone checkbox state change and persist active flag."""
        if item is None:
            return

        id_zone = item.data(32)
        if id_zone is None:
            return

        is_active = item.checkState() == self.qt_check_stat.Checked
        sql = "UPDATE {schema}.assim_ks SET active = %s WHERE id_zone = %s"
        self.mdb.run_query(sql, many=True, list_many=[[is_active, id_zone]], schema=True)

        if id_zone in self.d_zone_ks:
            self.d_zone_ks[id_zone]["active"] = is_active

        self.update_ks_edit_state()
        self.draw_zone_rb()

    def display_zone_info(self):
        """Display current zone parameters and associated observations."""
        self._updating_zone_ui = True
        try:
            if self.cur_zone_ks is None or self.cur_zone_ks not in self.d_zone_ks:
                return

            prm = self.d_zone_ks[self.cur_zone_ks]["prm"]
            self.gb_minor.setChecked(bool(prm["active_min"]))
            self.sb_minor_std.setValue(float(prm["std_min"]))
            self.sb_minor_inf.setValue(float(prm["val_inf_min"]))
            self.sb_minor_sup.setValue(float(prm["val_sup_min"]))

            self.gb_major.setChecked(bool(prm["active_maj"]))
            self.sb_major_std.setValue(float(prm["std_maj"]))
            self.sb_major_inf.setValue(float(prm["val_inf_maj"]))
            self.sb_major_sup.setValue(float(prm["val_sup_maj"]))

            obs_key = "lst_obs_h" if self.cb_ks_fld.currentText().lower() == "h" else "lst_obs_q"
            selected_obs = set(prm.get(obs_key, []))

            model = self.lv_ks_obs.model()
            if model is not None:
                for row in range(model.rowCount()):
                    itm = model.item(row, 0)
                    if itm is None:
                        continue
                    obs_id = itm.data(32)
                    itm.setCheckState(
                        self.qt_check_stat.Checked
                        if obs_id in selected_obs
                        else self.qt_check_stat.Unchecked
                    )
        finally:
            self._updating_zone_ui = False

    def save_input(self):
        """Save edited zone parameters to database."""
        if (
            self.cur_zone_ks is None
            or self._updating_zone_ui
            or not self.is_current_zone_editable()
        ):
            return

        model = self.lv_ks_obs.model()
        obs_ids = []
        if model is not None:
            for row in range(model.rowCount()):
                itm = model.item(row, 0)
                if itm is not None and itm.checkState() == self.qt_check_stat.Checked:
                    obs_ids.append(itm.data(32))

        if self.cb_ks_fld.currentText().lower() == "h":
            sql = (
                "UPDATE {schema}.assim_ks SET "
                "active_min = %s, std_min = %s, val_inf_min = %s, val_sup_min = %s, "
                "active_maj = %s, std_maj = %s, val_inf_maj = %s, val_sup_maj = %s, "
                "lst_obs_h = %s, auto_del = False "
                "WHERE id_zone = %s"
            )
        else:
            sql = (
                "UPDATE {schema}.assim_ks SET "
                "active_min = %s, std_min = %s, val_inf_min = %s, val_sup_min = %s, "
                "active_maj = %s, std_maj = %s, val_inf_maj = %s, val_sup_maj = %s, "
                "lst_obs_q = %s, auto_del = False "
                "WHERE id_zone = %s"
            )
        recs = [
            [
                self.gb_minor.isChecked(),
                self.sb_minor_std.value(),
                self.sb_minor_inf.value(),
                self.sb_minor_sup.value(),
                self.gb_major.isChecked(),
                self.sb_major_std.value(),
                self.sb_major_inf.value(),
                self.sb_major_sup.value(),
                obs_ids,
                self.cur_zone_ks,
            ]
        ]
        self.mdb.run_query(sql, many=True, list_many=recs, schema=True)

        self.refresh_zone_ks(self.cur_zone_ks)
        self.display_zone_info()

        if self.lv_zone.selectionModel().hasSelection():
            idxs = self.lv_zone.selectionModel().selectedIndexes()
            if idxs:
                self.lv_zone.model().itemFromIndex(idxs[0]).setIcon(QIcon())

    def draw_zone_rb(self):
        """Trigger map rubber band refresh."""
        self.display_rb.emit()
