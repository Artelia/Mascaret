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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, Qt, QSize, qVersion
from qgis.PyQt.QtGui import QIcon, QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QMessageBox, QButtonGroup

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
    os.path.join(os.path.join(os.path.dirname(__file__), "..", "..", "ui/ui_assimilation_law.ui"))
)
QT_VERSION = [int(v) for v in qVersion().split(".")][0]
D_PVAR = {0: "perturbationsCote", 1: "perturbationsDebit", 2: "perturbationsDebitLineique"}


class ClassAssimLawWidget(BASE, FORM_CLASS):
    """Widget for managing hydraulic law assimilation configuration.

    Allows users to define and edit hydraulic law control parameters for
    limnigraphs, hydrographs, and lateral inflow laws.
    """

    display_rb = pyqtSignal()

    def __init__(self, mgis, iface):
        """Initialize the law assimilation widget.

        :param mgis: Main QGIS interface object.
        :param iface: QGIS interface instance.
        :return: None.
        """
        super(ClassAssimLawWidget, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        apply_tooltips_from_json(self, "assim_law_widget.json")
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui_loaded = False
        self._updating_law_ui = False

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

        self.bg_perturb_var = QButtonGroup()
        self.bg_perturb_var.addButton(self.rb_cote, 0)
        self.bg_perturb_var.addButton(self.rb_debit, 1)
        self.bg_perturb_var.addButton(self.rb_debit_lin, 2)

        self.bt_reload_laws.setIcon(QIcon(QgsApplication.iconPath("mActionReload.svg")))
        self.bt_zoom_law.setIcon(QIcon(QgsApplication.iconPath("mActionZoomToSelected.svg")))
        self.bt_disp_law.setIcon(QIcon(QgsApplication.iconPath("mActionShowSelectedLayers.svg")))

        self.bt_clr_warn_law.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))

        laws_updated = self.verif_laws()
        if laws_updated:
            QMessageBox.warning(
                None, "Warning", "Definition of some laws " "have been automatically upadated."
            )

        self.cur_perturb_var = str()
        self.cur_source = str()
        self.cur_law = None
        self.cur_obs_law = None
        self.last_selection_kind = None
        self.d_laws = dict()
        self.d_obs_law = dict()

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
        self.bt_clr_warn_law.clicked.connect(self.clear_warning_law)

        self.connect_law_auto_save()
        self.set_direct_edit_mode()

        self.load_laws()
        self.load_obs()
        self.load_config()

        self.ui_loaded = True

    def set_direct_edit_mode(self):
        """Configure direct editing mode with automatic save."""
        self.gb_law.setEnabled(True)
        self.gb_param_law.setEnabled(True)
        self.fra_law_sel.setEnabled(True)
        self.update_law_edit_state()

    def is_current_law_editable(self):
        """Return True only if current law is selected and checked."""
        if self.cur_law is None or not self.lv_law.selectionModel().hasSelection():
            return False

        idxs = self.lv_law.selectionModel().selectedIndexes()
        if not idxs:
            return False

        item = self.lv_law.model().itemFromIndex(idxs[0])
        return item is not None and item.checkState() == self.qt_check_stat.Checked

    def update_law_edit_state(self):
        """Enable or disable law edit frame depending on current selection state."""

        editable = self.is_current_law_editable()
        self.fra_law_edit.setEnabled(editable)

    def connect_law_auto_save(self):
        """Connect editable law widgets to automatic save."""
        self.sb_law_min.valueChanged.connect(self.on_law_field_changed)
        self.sb_law_max.valueChanged.connect(self.on_law_field_changed)
        self.gb_a_ctrl.toggled.connect(self.on_law_field_changed)
        self.sb_a_std.valueChanged.connect(self.on_law_field_changed)
        self.gb_b_ctrl.toggled.connect(self.on_law_field_changed)
        self.sb_b_std.valueChanged.connect(self.on_law_field_changed)

    def on_law_field_changed(self, *_):
        """Save the current law after any user change."""
        if self._updating_law_ui or not self.is_current_law_editable():
            return
        self.save_input()

    def load_config(self):
        """Load law assimilation configuration from database.

        Retrieves or creates default ctrlLaw configuration with observation variables,
        thresholds, sigma iterations, and perturbation values for law coefficients.
        :return: None. Updates UI widgets with loaded configuration.
        """
        sql = (
            "SELECT control_type, active, control_var, seuil_rejet_misfit, "
            "iterations_sigma, perturbation_val, perturbation_act "
            "FROM {0}.assim_config WHERE control_type = 'ctrlLaw'"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        if not rows:
            recs = [
                [
                    2,
                    "ctrlLaw",
                    False,
                    "H",
                    50,
                    1,
                    ["perturbationsCote", "perturbationsDebit", "perturbationsDebitLineique"],
                    [[1.0, 0.5], [1.1, 6.0], [0.0, 0.0]],
                    "perturbationsCote",
                ]
            ]
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
                "iterations_sigma, perturbation_val, perturbation_act "
                "FROM {0}.assim_config WHERE control_type = 'ctrlLaw'"
            )
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
        """Load available observations for the current observation variable."""

        mdl = QStandardItemModel()
        mdl.setColumnCount(1)
        self.d_obs_law.clear()

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
            sql.format(self.mdb.SCHEMA, self.cb_law_fld.currentText()), fetch=True
        )

        for row in rows:
            obs_geom = QgsGeometry.fromWkt(row[2]) if row[2] else None
            self.d_obs_law[row[0]] = {
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

        self.lv_law_obs.setModel(mdl)
        self.lv_law_obs.setSpacing(2)
        self.lv_law_obs.model().itemChanged.connect(self.on_law_field_changed)
        self.lv_law_obs.clicked.connect(self.on_lv_clicked)

        self.cur_obs_law = None
        if self.last_selection_kind == "obs":
            self.last_selection_kind = None

        if self.ui_loaded:
            self.display_law_info()
            self.change_law_config()

    def on_lv_clicked(self):
        sender = self.sender()
        if sender == self.lv_law:
            self.current_law_changed()
        elif sender == self.lv_law_obs:
            self.current_obs_changed()

    def cur_perturb_var_changed(self, id_var):
        """Handle change in perturbation variable type (limnigraphy, hydrography, etc.).

        :param id_var: Index identifying the perturbation variable type.
        :return: None. Updates UI to show relevant parameters and laws.
        """
        self.cur_perturb_var = D_PVAR[id_var]
        if self.cur_perturb_var in ["perturbationsCote", "perturbationsDebit"]:
            self.cur_source = "extremities"
        else:
            self.cur_source = "lateral_inflows"

        for sb in [
            self.sb_cote_a,
            self.sb_cote_b,
            self.sb_debit_a,
            self.sb_debit_b,
            self.sb_debit_lin_a,
            self.sb_debit_lin_b,
        ]:
            sb.setEnabled(True)

        if self.cur_perturb_var == "perturbationsCote":

            self.lbl_typ_law.setText("Limnigraphs")
            for sb in [
                self.sb_debit_a,
                self.sb_debit_b,
                self.sb_debit_lin_a,
                self.sb_debit_lin_b,
            ]:
                sb.setEnabled(False)

        if self.cur_perturb_var == "perturbationsDebit":
            self.lbl_typ_law.setText("Hydrographs")
            for sb in [
                self.sb_cote_a,
                self.sb_cote_b,
                self.sb_debit_lin_a,
                self.sb_debit_lin_b,
            ]:
                sb.setEnabled(False)

        if self.cur_perturb_var == "perturbationsDebitLineique":
            self.lbl_typ_law.setText("Laws")
            for sb in [self.sb_cote_a, self.sb_cote_b, self.sb_debit_a, self.sb_debit_b]:
                sb.setEnabled(False)

        self.change_law_config()
        self.display_laws()

    def change_law_config(self):
        """Update law configuration in database when form values change.

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
                "perturbation_val = %s, "
                "perturbation_act = %s "
                "WHERE control_type = 'ctrlLaw'"
            )
            recs = [
                [
                    self.cc_law_act.isChecked(),
                    self.cb_law_fld.currentText(),
                    self.sb_law_seuil.value(),
                    self.sb_law_sigma.value(),
                    [
                        [self.sb_cote_a.value(), self.sb_cote_b.value()],
                        [self.sb_debit_a.value(), self.sb_debit_b.value()],
                        [self.sb_debit_lin_a.value(), self.sb_debit_lin_b.value()],
                    ],
                    self.cur_perturb_var,
                ]
            ]
            self.mdb.run_query(sql, many=True, list_many=recs, schema=True)

    def verif_laws(self):
        """Verify and update law definitions against current model geometry.

        Synchronizes database laws with active laws (extremities and lateral inflows)
        from the model, creates missing entries, and flags outdated entries.
        :return: ``True`` if laws were updated, ``False`` otherwise.
        """
        laws_updated = False

        sql = (
            "SELECT gid as law_id, name as law_name, 'extremities' as source_law, "
            "'perturbationsCote' as id_type, geom as geom_obj "
            "FROM {0}.extremities WHERE active IS True AND type = 2 "
            "UNION "
            "SELECT gid as law_id, name as law_name, 'extremities' as source_law, "
            "'perturbationsDebit' as id_type, geom as geom_obj "
            "FROM {0}.extremities WHERE active IS True AND type = 1 "
            "UNION "
            "SELECT gid as law_id, name as law_name, 'lateral_inflows' as source_law, "
            "'perturbationsDebitLineique' as id_type, geom as geom_obj "
            "FROM {0}.lateral_inflows WHERE active IS True "
            "ORDER BY id_type, law_name"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_calc_law = dict()
        for p_law in rows:
            d_calc_law[(p_law[0], p_law[2], p_law[3])] = {"name": p_law[1], "geom": p_law[4]}

        sql = (
            "SELECT id_law, source_law, id_type, active, auto_del, lst_obs_h, lst_obs_q, "
            "val_min, val_max, active_a, std_a, active_b, std_b FROM {0}.assim_law"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        if not rows:
            recs = [
                [
                    p_law[0],
                    p_law[1],
                    p_law[2],
                    False,
                    False,
                    [],
                    [],
                    0.0,
                    1000.0,
                    False,
                    0.2,
                    False,
                    5.0,
                ]
                for p_law in d_calc_law.keys()
            ]
            sql = (
                "INSERT INTO {0}.assim_law (id_law, source_law, id_type, "
                "active, auto_del, lst_obs_h, lst_obs_q, val_min, val_max, "
                "active_a, std_a, active_b, std_b) VALUES ({1})"
            )
            self.mdb.run_query(
                sql.format(self.mdb.SCHEMA, ", ".join(["%s"] * len(recs[0]))),
                many=True,
                list_many=recs,
            )

            sql = (
                "SELECT id_law, source_law, id_type, active, auto_del, lst_obs_h, lst_obs_q, "
                "val_min, val_max, active_a, std_a, active_b, std_b FROM {0}.assim_law"
            )
            rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_db_law = {tuple(row[0:3]): row for row in rows}

        if not (
            len(d_db_law) == len(d_calc_law)
            and all([k in d_db_law.keys() for k in d_calc_law.keys()])
        ):
            recs = []
            for p_law in d_calc_law.keys():
                if p_law in d_db_law.keys():
                    rec = d_db_law[p_law]
                    recs.append(rec)
                else:
                    recs.append(
                        [
                            p_law[0],
                            p_law[1],
                            p_law[2],
                            False,
                            True,
                            [],
                            [],
                            0.0,
                            1000.0,
                            False,
                            0.0,
                            False,
                            0.0,
                        ]
                    )

            sql = "DELETE FROM {0}.assim_law"
            self.mdb.run_query(sql.format(self.mdb.SCHEMA))
            sql = (
                "INSERT INTO {0}.assim_law (id_law, source_law, id_type, active, auto_del, "
                "lst_obs_h, lst_obs_q, val_min, val_max, active_a, std_a, active_b, std_b) "
                "VALUES ({1})"
            )
            self.mdb.run_query(
                sql.format(self.mdb.SCHEMA, ", ".join(["%s"] * len(recs[0]))),
                many=True,
                list_many=recs,
            )

            laws_updated = True

        return laws_updated

    def reload_laws(self):
        """Reload laws by verifying and refreshing from database.

        Checks law definitions and reloads the law list if updates were made.
        :return: None. Updates law list if verification detected changes.
        """
        laws_updated = self.verif_laws()
        if laws_updated:
            QMessageBox.warning(
                None, "Warning", "Definition of some laws " "have been automatically upadated."
            )
            self.load_laws()

    def load_laws(self):
        """Load and organize all hydraulic laws from database by type.

        Retrieves laws organized by perturbation type (perturbationsCote, perturbationsDebit,
        perturbationsDebitLineique) and stores their geometries and parameters.
        :return: None. Populates *self.d_laws* dictionary.
        """
        self.d_laws.clear()
        self.d_laws = {
            "perturbationsCote": {},
            "perturbationsDebit": {},
            "perturbationsDebitLineique": {},
        }
        # Geg SIRD of the sources table for PostGIS
        sql_srid = (
            "SELECT f_table_name, srid "
            "FROM geometry_columns "
            "WHERE f_table_schema = %s "
            "AND f_table_name IN ('extremities', 'lateral_inflows')"
        )
        srid_rows = self.mdb.run_query(sql_srid, fetch=True, params=[self.mdb.SCHEMA])
        d_srid = {
            row[0]: QgsCoordinateReferenceSystem(f"EPSG:{row[1]}") for row in srid_rows if row[1]
        }

        sql = (
            "SELECT gid as law_id, name as law_name, 'extremities' as source_law, "
            "'perturbationsCote' as id_type, ST_AsText(geom) as wkt_geom "
            "FROM {0}.extremities WHERE active IS True AND type = 2 "
            "UNION "
            "SELECT gid as law_id, name as law_name, 'extremities' as source_law, "
            "'perturbationsDebit' as id_type, ST_AsText(geom) as wkt_geom "
            "FROM {0}.extremities WHERE active IS True AND type = 1 "
            "UNION "
            "SELECT gid as law_id, name as law_name, 'lateral_inflows' as source_law, "
            "'perturbationsDebitLineique' as id_type, ST_AsText(geom) as wkt_geom "
            "FROM {0}.lateral_inflows WHERE active IS True "
            "ORDER BY id_type, law_name"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        d_calc_law = dict()
        for p_law in rows:
            d_calc_law[(p_law[0], p_law[2], p_law[3])] = {"name": p_law[1], "geom": p_law[4]}

        sql = (
            "SELECT id_law, source_law, id_type, active, auto_del, lst_obs_h, lst_obs_q, "
            "val_min, val_max, active_a, std_a, active_b, std_b FROM {0}.assim_law"
        )
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)

        for row in rows:
            id_law = row[0]
            source_law = row[1]
            type_law = row[2]
            self.d_laws[type_law][id_law] = {
                "law_name": d_calc_law[(row[0], row[1], row[2])]["name"],
                "source_law": source_law,
                "geom": QgsGeometry.fromWkt(d_calc_law[(row[0], row[1], row[2])]["geom"]),
                "crs": d_srid.get(source_law, QgsCoordinateReferenceSystem()),
                "active": row[3],
                "auto_del": row[4],
                "prm": {
                    "lst_obs_h": row[5],
                    "lst_obs_q": row[6],
                    "val_min": row[7],
                    "val_max": row[8],
                    "active_a": row[9],
                    "std_a": row[10],
                    "active_b": row[11],
                    "std_b": row[12],
                },
            }

    def law_status_changed(self, item):
        """Handle law checkbox state change and persist active flag."""
        if item is None:
            return

        id_law = item.data(32)
        if id_law is None:
            return

        is_active = item.checkState() == self.qt_check_stat.Checked
        law_data = self.d_laws.get(self.cur_perturb_var, {}).get(id_law, {})
        source_law = law_data.get("source_law", self.cur_source)

        sql = (
            "UPDATE {schema}.assim_law SET active = %s "
            "WHERE id_law = %s AND source_law = %s AND id_type = %s"
        )
        recs = [[is_active, id_law, source_law, self.cur_perturb_var]]
        self.mdb.run_query(sql, many=True, list_many=recs, schema=True)

        if id_law in self.d_laws.get(self.cur_perturb_var, {}):
            self.d_laws[self.cur_perturb_var][id_law]["active"] = is_active

        self.display_laws()
        self.draw_law_rb()
        self.update_law_edit_state()

    def display_law_info(self):
        """Display current law parameters and associated observations."""
        self._updating_law_ui = True
        try:
            if self.cur_law is None:
                return

            law = self.d_laws.get(self.cur_perturb_var, {}).get(self.cur_law)
            if not law:
                return

            prm = law["prm"]
            self.sb_law_min.setValue(float(prm["val_min"]))
            self.sb_law_max.setValue(float(prm["val_max"]))
            self.gb_a_ctrl.setChecked(bool(prm["active_a"]))
            self.sb_a_std.setValue(float(prm["std_a"]))
            self.gb_b_ctrl.setChecked(bool(prm["active_b"]))
            self.sb_b_std.setValue(float(prm["std_b"]))

            obs_key = "lst_obs_h" if self.cb_law_fld.currentText().lower() == "h" else "lst_obs_q"
            selected_obs = set(prm.get(obs_key, []))

            model = self.lv_law_obs.model()
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
            self._updating_law_ui = False

    def draw_law_rb(self):
        """Trigger map rubber band refresh."""
        self.display_rb.emit()

    def display_map_rb(self):
        """Refresh map rubber band display from current law selection context."""
        self.draw_law_rb()

    def get_current_rb_data(self):
        """Return current rubber band context for map display."""
        if not self.bt_disp_law.isChecked() or not self.last_selection_kind:
            return None

        if self.last_selection_kind == "law" and self.cur_law is not None:
            d_law = self.d_laws.get(self.cur_perturb_var, {}).get(self.cur_law, {})
            return {
                "geom": d_law.get("geom"),
                "crs": d_law.get("crs"),
                "is_observation": False,
            }

        if self.last_selection_kind == "obs" and self.cur_obs_law is not None:
            d_obs = self.d_obs_law.get(self.cur_obs_law, {})
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

    def zoom_on_law(self):
        """Zoom map to last selected element (law or observation)."""
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

    def save_input(self):
        """Save edited law parameters to database."""
        if self.cur_law is None or self._updating_law_ui or not self.is_current_law_editable():
            return

        l_obs = []
        for r in range(self.lv_law_obs.model().rowCount()):
            itm = self.lv_law_obs.model().item(r, 0)
            if itm.checkState() == 2:
                l_obs.append(itm.data(32))

        recs = [
            [
                self.sb_law_min.value(),
                self.sb_law_max.value(),
                self.gb_a_ctrl.isChecked(),
                self.sb_a_std.value(),
                self.gb_b_ctrl.isChecked(),
                self.sb_b_std.value(),
                l_obs,
            ]
        ]

        sql = (
            "UPDATE {schema}.assim_law SET "
            "val_min = %s, "
            "val_max = %s, "
            "active_a = %s, "
            "std_a = %s, "
            "active_b = %s, "
            "std_b = %s, "
            "auto_del = False "
            "WHERE id_law = %s "
            "AND source_law = %s"
        )
        if str(self.cb_law_fld.currentText()).lower() == "h":
            sql = sql.replace("auto_del = False ", "lst_obs_h = %s, auto_del = False ")
        else:
            sql = sql.replace("auto_del = False ", "lst_obs_q = %s, auto_del = False ")

        recs = [vals + [self.cur_law, self.cur_source] for vals in recs]
        self.mdb.run_query(sql, many=True, list_many=recs, schema=True)

        self.refresh_law(self.cur_perturb_var, self.cur_law)
        self.display_law_info()

        if self.lv_law.selectionModel().hasSelection():
            idxs = self.lv_law.selectionModel().selectedIndexes()
            if idxs:
                idx = idxs[0]
                itm = self.lv_law.model().itemFromIndex(idx)
                itm.setIcon(QIcon())

    def clear_warning_law(self):
        """Clear auto-delete warning flags for all laws."""
        sql = "UPDATE {schema}.assim_law SET auto_del = False"
        self.mdb.run_query(sql, schema=True)
        self.load_laws()
        self.display_laws()

    def display_laws(self):
        """Display laws for current perturbation variable in the list view."""
        model = QStandardItemModel()
        model.setColumnCount(1)

        laws = self.d_laws.get(self.cur_perturb_var, {})
        sorted_laws = sorted(laws.items(), key=lambda x: str(x[1].get("law_name", "")).lower())

        for law_id, law_data in sorted_laws:
            item = QStandardItem()
            item.setData(law_data["law_name"], 0)
            item.setData(law_id, 32)
            item.setFlags(self.qt_itm_ena | self.qt_itm_sel | self.qt_item_check)
            item.setCheckState(
                self.qt_check_stat.Checked
                if law_data.get("active")
                else self.qt_check_stat.Unchecked
            )
            if law_data.get("auto_del"):
                item.setIcon(QIcon(QgsApplication.iconPath("mIconWarning.svg")))
            model.appendRow(item)

        self.lv_law.setIconSize(QSize(14, 14))
        self.lv_law.setModel(model)
        self.lv_law.setSpacing(2)
        self.lv_law.model().itemChanged.connect(self.law_status_changed)
        self.lv_law.clicked.connect(self.on_lv_clicked)

        if self.lv_law.model().rowCount():
            self.lv_law.setCurrentIndex(self.lv_law.model().item(0, 0).index())
        else:
            self.cur_law = None

        self.last_selection_kind = None
        self.draw_law_rb()
        self.update_law_edit_state()

    def current_law_changed(self):
        """Handle law selection change in the law list view."""
        self.cur_law = None
        if self.lv_law.selectionModel().hasSelection():
            indexes = self.lv_law.selectionModel().selectedIndexes()
            if indexes:
                item = self.lv_law.model().itemFromIndex(indexes[0])
                self.cur_law = item.data(32)

        if self.cur_law is not None:
            self.last_selection_kind = "law"
            self.cur_obs_law = None
            self.lv_law_obs.clearSelection()
        elif self.last_selection_kind == "law":
            self.last_selection_kind = None

        self.display_law_info()
        self.update_law_edit_state()
        self.draw_law_rb()

    def current_obs_changed(self):
        """Handle observation selection change in lv_law_obs."""
        self.cur_obs_law = None
        if self.lv_law_obs.selectionModel().hasSelection():
            indexes = self.lv_law_obs.selectionModel().selectedIndexes()
            if indexes:
                item = self.lv_law_obs.model().itemFromIndex(indexes[0])
                self.cur_obs_law = item.data(32)

        if self.cur_obs_law is not None:
            self.last_selection_kind = "obs"
        elif self.last_selection_kind == "obs":
            self.last_selection_kind = None

        self.draw_law_rb()

    def refresh_law(self, id_type, id_law):
        """Refresh one law parameter block from database."""
        sql = (
            "SELECT source_law, lst_obs_h, lst_obs_q, val_min, val_max, "
            "active_a, std_a, active_b, std_b "
            "FROM {schema}.assim_law "
            "WHERE id_law = %s AND id_type = %s"
        )
        rows = self.mdb.run_query(sql, fetch=True, params=[id_law, id_type], schema=True)
        if not rows:
            return

        row = rows[0]
        if id_law not in self.d_laws.get(id_type, {}):
            return

        self.d_laws[id_type][id_law]["source_law"] = row[0]
        self.d_laws[id_type][id_law]["prm"] = {
            "lst_obs_h": row[1],
            "lst_obs_q": row[2],
            "val_min": row[3],
            "val_max": row[4],
            "active_a": row[5],
            "std_a": row[6],
            "active_b": row[7],
            "std_b": row[8],
        }
