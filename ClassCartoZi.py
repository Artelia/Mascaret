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
from qgis.core import NULL as qgis_null

# from ..Function import data_to_float

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QColor, QBrush
    from qgis.PyQt.QtWidgets import *

from datetime import timedelta
from shapely.wkt import loads as wkt_loads
from scipy import interpolate

D_PARAM = {"z": {"txt": "Water level", "var_profil": "Z", "var_basin": "ZCAS"},
           "char": {"txt": "Hydraulic head", "var_profil": "CHAR", "var_basin": None},
           "test": {"txt": "Test", "var_profil": None, "var_basin": "ZCAS"}}

class ClassCartoZI(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.itm_val, self.itm_warn, self.itm_err = None, None, None

        self.load_error = False
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_carto_zi.ui"), self)

        self.bg_value = QButtonGroup()
        self.bg_value.addButton(self.rb_time, 0)
        self.bg_value.addButton(self.rb_max, 1)
        self.bg_value.addButton(self.rb_min, 2)

        self.bg_value.buttonClicked[int].connect(self.value_changed)
        self.cb_param.currentIndexChanged.connect(self.param_changed)
        self.cb_run.currentIndexChanged.connect(self.run_changed)
        self.cb_scen.currentIndexChanged.connect(self.scen_changed)
        self.cc_profil.toggled.connect(self.enable_user_profil)
        self.cb_qgis_layers.layerChanged.connect(self.user_profil_changed)
        self.bt_rep.clicked.connect(self.get_repository)
        self.bt_export_carto_zi.clicked.connect(self.export_files)

        self.cur_run = None
        self.cur_scen = None
        self.cur_param = None
        self.dict_run = dict()

        self.init_cb_param()
        self.init_cb_run()
        self.init_cb_lay_model()

    def init_cb_lay_model(self):
        excluded_str = ['table="{}"'.format(self.mdb.SCHEMA), "dbname='{}'".format(self.mdb.dbname)]

        l_excl_lay = []
        for lay_id in QgsProject.instance().mapLayers():
            lay = QgsProject.instance().layerTreeRoot().findLayer(lay_id).layer()
            if all(path in os.path.normpath(lay.source()) for path in excluded_str):
                l_excl_lay.append(lay)

        self.cb_qgis_layers.setExceptedLayerList(l_excl_lay)
        self.cb_qgis_layers.setFilters(QgsMapLayerProxyModel.LineLayer)
        self.enable_user_profil()
        self.user_profil_changed()

    def init_cb_param(self):
        self.cb_param.clear()
        for key_param, val_param in D_PARAM.items():
            self.cb_param.addItem(val_param["txt"], key_param)

    def init_cb_run(self):
        self.dict_run = dict()
        rows = self.mdb.run_query(
            "SELECT id, run, scenario FROM {0}.runs "
            "WHERE id in (SELECT DISTINCT id_runs FROM {0}.runs_graph) "
            "ORDER BY date DESC, run ASC, scenario ASC;".format(self.mdb.SCHEMA),
            fetch=True)
        for row in rows:
            if row[1] not in self.dict_run.keys():
                self.dict_run[row[1]] = dict()
            self.dict_run[row[1]][row[2]] = row[0]

        self.cb_run.clear()
        for run in self.dict_run.keys():
            self.cb_run.addItem(run, run)

    def value_changed(self, ib_button):
        if ib_button == 0:
            self.cb_time.setEnabled(True)
        else:
            self.cb_time.setEnabled(False)

    def param_changed(self):
        self.cur_param = self.cb_param.currentData()
        param_info = D_PARAM[self.cur_param]

        if param_info["var_profil"]:
            self.cc_profil.setCheckState(2)
            self.cc_profil.setEnabled(True)
            self.fra_lay_prof.setEnabled(True)
        else:
            self.cc_profil.setCheckState(0)
            self.cc_profil.setEnabled(False)
            self.cc_lay_profil.setCheckState(0)
            self.fra_lay_prof.setEnabled(False)

        if param_info["var_basin"]:
            self.cc_basin.setCheckState(2)
            self.cc_basin.setEnabled(True)
        else:
            self.cc_basin.setCheckState(0)
            self.cc_basin.setEnabled(False)

    def run_changed(self):
        self.cur_run = self.cb_run.currentText()
        if self.cur_run:
            self.cb_scen.clear()

            for nm_scen, id_scen in self.dict_run[self.cur_run].items():
                self.cb_scen.addItem(nm_scen, id_scen)

    def scen_changed(self):
        self.cur_scen = self.cb_scen.currentData()
        if self.cur_scen:
            self.cb_time.clear()

            init_date = None
            sql = "SELECT init_date FROM {0}.runs WHERE id = {1}" \
                  "".format(self.mgis.mdb.SCHEMA, self.cur_scen)
            info = self.mdb.run_query(sql, fetch=True)
            if info:
                init_date = info[0][0]

            sql = "SELECT DISTINCT time FROM {0}.results WHERE id_runs = {1} ORDER BY time" \
                  "".format(self.mgis.mdb.SCHEMA, self.cur_scen)
            l_times = self.mdb.run_query(sql, fetch=True)
            for _time in l_times:
                if init_date:
                    aff = init_date + timedelta(seconds=_time[0])
                    aff = "{:%d/%m/%Y %H:%M:%S}.{:02.0f}".format(aff, aff.microsecond / 10000.0)
                else:
                    aff = str(_time[0])
                self.cb_time.addItem(aff, _time[0])

    def enable_user_profil(self):
        if self.cb_qgis_layers.count() == 0:
            self.cc_lay_profil.setEnabled(False)
            self.cb_qgis_layers.setEnabled(False)
            self.lbl_prof_name.setEnabled(False)
            self.cb_qgis_fields.setEnabled(False)
        else:
            self.cc_lay_profil.setEnabled(self.cc_profil.isChecked())
            self.cb_qgis_layers.setEnabled(self.cc_profil.isChecked())
            self.lbl_prof_name.setEnabled(self.cc_profil.isChecked())
            self.cb_qgis_fields.setEnabled(self.cc_profil.isChecked())

    def user_profil_changed(self):
        self.cb_qgis_fields.setLayer(self.cb_qgis_layers.currentLayer())

    def get_repository(self):
        folder_name_path = QFileDialog.getExistingDirectory(self, "Choose a folder")
        if folder_name_path:
            self.txt_rep.setText(str(folder_name_path))

    def export_files(self):
        if not self.cur_scen:
            QMessageBox.warning(None, "Warning", "Please select a scenario")
            return

        res_profile = self.cc_profil.isChecked()
        res_basin = self.cc_basin.isChecked()
        if not res_profile and not res_basin:
            QMessageBox.warning(None, "Warning", "Please select a layer to export")
            return

        cur_time = None
        if self.bg_value.checkedId() == 0:
            cur_time = self.cb_time.currentData()
        elif self.bg_value.checkedId() == 1:
            cur_time = "max"
        elif self.bg_value.checkedId() == 2:
            cur_time = "min"

        if cur_time is None:
            QMessageBox.warning(None, "Warning", "Please select the time")
            return

        rep_out = str(self.txt_rep.text())
        if not rep_out:
            QMessageBox.warning(None, "Warning", "Please select the files repository")
            return

        profil_file = os.path.join(rep_out, "cartozi_profiles.shp")
        basin_file = os.path.join(rep_out, "cartozi_basins.shp")

        if os.path.exists(profil_file) or os.path.exists(basin_file):
            if QMessageBox.question(None, "Warning",
                                    "Layers already exist. Erase them ?",
                                    QMessageBox.No | QMessageBox.Yes) != QMessageBox.Yes:
                return
            else:
                for _lay_id in QgsProject.instance().mapLayers():
                    _lay = QgsProject.instance().mapLayer(_lay_id)
                    if os.path.normpath(_lay.source()) in [os.path.normpath(profil_file),
                                                           os.path.normpath(basin_file)]:
                        QMessageBox.warning(None, "Warning", "Layers are opened in QGis "
                                                             "and can't be deleted")
                        return

        d_res = get_results(self.mdb, res_profile, res_basin,
                            self.cur_scen, self.cur_param, cur_time)

        if res_profile:
            d_profil = get_db_profiles(self.mdb)
            if self.cc_lay_profil.isChecked():
                user_lay = self.cb_qgis_layers.currentLayer()
                user_field = self.cb_qgis_fields.currentField()
                get_user_profiles(self.mdb, d_profil, user_lay, user_field)
            calc_profiles_values(d_profil, d_res)
            create_profiles_shp(profil_file, d_profil, self.cur_param, cur_time, self.mdb)

        if res_basin:
            d_basin = get_db_basins(self.mdb)
            calc_basins_values(d_basin, d_res)
            create_basins_shp(basin_file, d_basin, self.cur_param, cur_time, self.mdb)

        QMessageBox.information(self, "Information", "Export successful", QMessageBox.Ok)


def create_basins_shp(out_file, d_res, param, time, mdb):
    fld_val = param
    if time in ["min", "max"]:
        fld_val = "{}_{}".format(fld_val, time)

    schema = QgsFields()
    schema.append(QgsField("basinnum", QVariant.Int))
    schema.append(QgsField("name", QVariant.String))
    schema.append(QgsField(fld_val, QVariant.Double, 'double', 10, 2))

    geom_type = QgsWkbTypes.MultiPolygon
    db_crs = QgsCoordinateReferenceSystem("POSTGIS:{}".format(mdb.SRID))
    tc = QgsCoordinateTransformContext()

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"

    if os.path.exists(out_file):
        QgsVectorFileWriter.deleteShapeFile(out_file)

    _writer = QgsVectorFileWriter.create(out_file, schema, geom_type, db_crs, tc, options)

    for id_basin, param_basin in d_res.items():
        ft = QgsFeature(schema)
        ft.setAttribute(0, id_basin)
        ft.setAttribute(1, param_basin["name"])
        ft.setAttribute(2, param_basin["value"])
        ft.setGeometry(QgsGeometry().fromWkt(param_basin["geom"]))
        _writer.addFeature(ft)

    del _writer


def create_profiles_shp(out_file, d_res, param, time, mdb):
    fld_val = param
    if time in ["min", "max"]:
        fld_val = "{}_{}".format(fld_val, time)

    schema = QgsFields()
    schema.append(QgsField("branchnum", QVariant.Int))
    schema.append(QgsField("abscissa", QVariant.Double, 'double', 10, 3))
    schema.append(QgsField("name", QVariant.String))
    schema.append(QgsField(fld_val, QVariant.Double, 'double', 10, 2))

    geom_type = QgsWkbTypes.MultiLineString
    db_crs = QgsCoordinateReferenceSystem("POSTGIS:{}".format(mdb.SRID))
    tc = QgsCoordinateTransformContext()

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "ESRI Shapefile"

    if os.path.exists(out_file):
        QgsVectorFileWriter.deleteShapeFile(out_file)

    _writer = QgsVectorFileWriter.create(out_file, schema, geom_type, db_crs, tc, options)

    for id_br, param_br in d_res.items():
        for pk, param_pk in param_br["lst_pk"].items():
            ft = QgsFeature(schema)
            ft.setAttribute(0, id_br)
            ft.setAttribute(1, pk)
            ft.setAttribute(2, param_pk["name"])
            ft.setAttribute(3, param_pk["value"])
            ft.setGeometry(QgsGeometry().fromWkt(param_pk["geom"]))
            _writer.addFeature(ft)

    del _writer


def calc_profiles_values(d_profil, d_res):
    l_pk = []
    l_val = []
    for pk, val in d_res["profil"]["res"].items():
        l_pk.append(pk)
        l_val.append(val)
    fn_interp = interpolate.interp1d(l_pk, l_val)

    for id_br, param_br in d_profil.items():
        for pk, param_pk in param_br["lst_pk"].items():
            if pk in d_res["profil"]["res"].keys():
                param_pk["value"] = d_res["profil"]["res"][pk]
            else:
                param_pk["value"] = round(float(fn_interp(pk)), 2)


def calc_basins_values(d_basin, d_res):
    for id_basin, param_basin in d_basin.items():
        if id_basin in d_res["basin"]["res"].keys():
            param_basin["value"] = d_res["basin"]["res"][id_basin]
        else:
            param_basin["value"] = None


def get_user_profiles(mdb, d_profil, user_lay, user_field):
    x_form = None

    lay_crs = user_lay.crs()
    db_crs = QgsCoordinateReferenceSystem("POSTGIS:{}".format(mdb.SRID))
    if db_crs != lay_crs:
        x_form = QgsCoordinateTransform(lay_crs, db_crs, QgsCoordinateTransformContext())

    for feat in user_lay.getFeatures():
        l_pk = []

        cur_geom = feat.geometry()
        if x_form:
            cur_geom.transform(x_form)

        for num_br, param_br in d_profil.items():
            geom_br = QgsGeometry().fromWkt(param_br["geom"])
            res = geom_br.intersection(cur_geom)
            if res:
                if res.wkbType() == QgsWkbTypes.Point:
                    l_pk.append([num_br, round(param_br["pk_start"] +
                                               geom_br.lineLocatePoint(res), 2)])

        if len(l_pk) == 1:
            num_br, pk = l_pk[0]
            if d_profil[num_br]["pk_max"] > pk > d_profil[num_br]["pk_min"]:
                if pk not in d_profil[num_br]["lst_pk"].keys():
                    d_profil[num_br]["lst_pk"][pk] = {"name": str(feat[user_field]), "geom": cur_geom.asWkt()}
                    d_profil[num_br]["lst_pk"] = dict(sorted(d_profil[num_br]["lst_pk"].items()))


def get_db_profiles(mdb):
    d_profil = dict()
    rows_br = mdb.run_query("SELECT branch, ST_Length(geom), ST_AsText(ST_LineMerge(geom)) "
                            "FROM {0}.branchs WHERE active IS True ORDER BY branch".format(mdb.SCHEMA), fetch=True)

    total_len = 0.
    for row_br in rows_br:
        d_tmp = {"geom": row_br[2], "length": row_br[1], "pk_start": total_len,
                 "lst_pk": dict(), "pk_min": float(), "pk_max": float()}

        rows_pr = mdb.run_query("SELECT abscissa, name, ST_AsText(geom) FROM {0}.profiles "
                                "WHERE branchnum = {1} AND active IS True "
                                "ORDER BY abscissa".format(mdb.SCHEMA, row_br[0]), fetch=True)
        for row_pr in rows_pr:
            d_tmp["lst_pk"][row_pr[0]] = {"name": row_pr[1], "geom": row_pr[2]}

        d_tmp["pk_min"] = min(d_tmp["lst_pk"].keys())
        d_tmp["pk_max"] = max(d_tmp["lst_pk"].keys())

        d_profil[row_br[0]] = d_tmp
        total_len += row_br[1]

    return d_profil


def get_db_basins(mdb):
    d_basin = dict()

    rows = mdb.run_query("SELECT basinnum, name, ST_AsText(geom) FROM {0}.basins "
                         "WHERE active IS True "
                         "ORDER BY basinnum".format(mdb.SCHEMA), fetch=True)
    for row in rows:
        d_basin[row[0]] = {"name": row[1], "geom": row[2]}

    return d_basin


def get_results(mdb, res_profile, res_basin, scen, param, time):
    d_obj = dict()
    if res_profile:
        d_obj["profil"] = {"var_txt": D_PARAM[param]["var_profil"],
                           "typ_var": "opt",
                           "var_id": None,
                           "res": dict()}

    if res_basin:
        d_obj["basin"] = {"var_txt": D_PARAM[param]["var_basin"],
                          "typ_var": "basin",
                          "var_id": None,
                          "res": dict()}

    for typ_obj, prm_obj in d_obj.items():
        var_id = get_var_id(mdb, prm_obj["typ_var"], prm_obj["var_txt"])
        if var_id is not None:
            prm_obj["var_id"] = var_id

            if time in ["min", "max"]:
                sql = "SELECT pknum, {0}(val) FROM {1}.results " \
                      "WHERE id_runs = {2} AND var = {3} " \
                      "GROUP BY pknum ORDER BY pknum" \
                      "".format(time, mdb.SCHEMA, scen, var_id)
            else:
                sql = "SELECT pknum, val FROM {0}.results " \
                      "WHERE time = {1} AND id_runs = {2} AND var = {3} " \
                      "ORDER BY pknum" \
                      "".format(mdb.SCHEMA, time, scen, var_id)

            rows = mdb.run_query(sql, fetch=True)
            prm_obj["res"] = {r[0]: r[1] for r in rows}

    return d_obj


def get_var_id(mdb, typ_var, var_txt):
    sql = "SELECT id FROM {0}.results_var WHERE type_res = '{1}' AND var = '{2}'" \
          "".format(mdb.SCHEMA, typ_var, var_txt)
    info = mdb.run_query(sql, fetch=True)
    if info:
        return info[0][0]


#
#     def find_db_layer(self):
#         b_lay, p_lay = None, None
#         tree_root = QgsProject.instance().layerTreeRoot()
#         mas_group = tree_root.findGroup("Mas_{}".format(self.mdb.SCHEMA))
#         l_child = mas_group.children()
#         for child in l_child:
#             if (
#                 child.nodeType() == 1
#                 and "dbname='{}'".format(self.mdb.dbname) in child.layer().source()
#             ):
#                 if 'table="{}"."branchs"'.format(self.mdb.SCHEMA) in child.layer().source():
#                     b_lay = child.layer()
#                 if 'table="{}"."profiles"'.format(self.mdb.SCHEMA) in child.layer().source():
#                     p_lay = child.layer()
#
#         return b_lay, p_lay
#
#     def init_cb_branch(self):
#         sql = "SELECT branch, 'Branch ' || branch FROM {0}.branchs WHERE active IS True"
#         l_branch = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
#         for id_branch, nm_branch in l_branch:
#             self.cb_branch.addItem(nm_branch, id_branch)
#
#         self.cc_profil_sel.setEnabled(False)
#         if self.lay_profile.selectedFeatureCount() > 0:
#             self.cc_profil_sel.setEnabled(True)
#             self.cc_profil_sel.setCheckState(2)
#
#     def cur_qgis_layer_changed(self):
#         self.lay_bed = None
#
#         _l = self.cb_qgis_layers.currentLayer()
#         if _l:
#             if _l.type() == 0:
#                 self.lay_bed = _l
#
#         if self.lay_bed:
#             if self.lay_bed.selectedFeatureCount() > 0:
#                 self.cc_bed_sel.setEnabled(True)
#                 self.cc_bed_sel.setCheckState(2)
#             else:
#                 self.cc_bed_sel.setEnabled(False)
#                 self.cc_bed_sel.setCheckState(0)
#         else:
#             self.cc_bed_sel.setEnabled(False)
#             self.cc_bed_sel.setCheckState(0)
#
#     def start_analysis(self):
#         if self.lay_bed.crs() != self.lay_profile.crs():
#             QMessageBox.critical(
#                 self,
#                 "Error",
#                 "The projection of the layer for "
#                 "river beds must be {}".format(self.lay_profile.crs().authid()),
#                 QMessageBox.Ok,
#             )
#             return
#
#         self.d_profiles.clear()
#         self.fra_save.hide()
#
#         mdl = QStandardItemModel()
#         self.itm_val = QStandardItem("Valid")
#         self.itm_val.setFlags(Qt.ItemIsEnabled)
#         self.itm_val.setForeground(QBrush(QColor(60, 155, 60)))
#         self.itm_warn = QStandardItem("Warning")
#         self.itm_warn.setFlags(Qt.ItemIsEnabled)
#         self.itm_warn.setForeground(QBrush(QColor(255, 100, 0)))
#         self.itm_err = QStandardItem("Error")
#         self.itm_err.setFlags(Qt.ItemIsEnabled)
#         self.itm_err.setForeground(QBrush(QColor(255, 0, 0)))
#         for itm in [self.itm_val, self.itm_warn, self.itm_err]:
#             mdl.appendRow(itm)
#         self.tv_analysis.setModel(mdl)
#
#         branch = self.cb_branch.currentData()
#         typ_bed = D_TYP_BED[self.bg_type.checkedId()]
#
#         # Sélection des branches
#         l_branch_geom = []
#         l_ft = self.lay_branch.getFeatures()
#         for ft in l_ft:
#             if ft["branch"] == branch and ft["active"] is True:
#                 l_branch_geom.append(ft.geometry())
#
#         if not l_branch_geom:
#             QMessageBox.critical(
#                 self, "Error", "No geometry found for branch {}".format(branch), QMessageBox.Ok
#             )
#             return
#
#         # Sélection des profils
#         if self.cc_profil_sel.isChecked():
#             l_ft = self.lay_profile.getSelectedFeatures()
#         else:
#             l_ft = self.lay_profile.getFeatures()
#
#         for ft in l_ft:
#             if ft["branchnum"] == branch and ft["active"] is True:
#                 try:
#                     test = [float(x) for x in str(ft["x"]).strip().split(" ")]
#                 except ValueError:
#                     QMessageBox.critical(self, "Error", "There is no points on the profile", QMessageBox.Ok)
#                     return
#                 p = Profile(ft)
#                 self.d_profiles[ft.id()] = p
#
#         if not self.d_profiles:
#             QMessageBox.critical(
#                 self, "Error", "No profiles found for branch {}".format(branch), QMessageBox.Ok
#             )
#             return
#
#         # Sélection des polylignes (beds)
#         if self.cc_bed_sel.isChecked():
#             l_ft = self.lay_bed.getSelectedFeatures()
#         else:
#             l_ft = self.lay_bed.getFeatures()
#
#         if not l_ft:
#             QMessageBox.critical(self, "Error", "No bed polylines found", QMessageBox.Ok)
#             return
#
#         l_bed_geom = []
#         for ft in l_ft:
#             l_bed_geom.append(ft.geometry())
#
#         # Analyse
#         for id_prof, profil in self.d_profiles.items():
#             profil.init_var()
#             profil.intersects_branch(l_branch_geom)
#             profil.intersects_bed(l_bed_geom)
#             profil.validate(typ_bed)
#
#             if profil.status == -1:
#                 idx = self.itm_err.rowCount()
#                 itm = QStandardItem()
#                 itm.setData("{} : {}".format(profil.name, profil.mess), Qt.DisplayRole)
#                 itm.setData(profil.id, Qt.UserRole)
#                 itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
#                 self.itm_err.setChild(idx, itm)
#             elif profil.status == 1:
#                 idx = self.itm_warn.rowCount()
#                 itm = QStandardItem()
#                 itm.setData("{} : {}".format(profil.name, profil.mess), Qt.DisplayRole)
#                 itm.setData(profil.id, Qt.UserRole)
#                 itm.setCheckState(2)
#                 itm.setCheckable(True)
#                 self.itm_warn.setChild(idx, itm)
#             elif profil.status == 2:
#                 idx = self.itm_val.rowCount()
#                 itm = QStandardItem()
#                 itm.setData("{}".format(profil.name), Qt.DisplayRole)
#                 itm.setData(profil.id, Qt.UserRole)
#                 itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
#                 self.itm_val.setChild(idx, itm)
#
#         self.itm_err.setText("Error [{}]".format(self.itm_err.rowCount()))
#         self.tv_analysis.setExpanded(self.tv_analysis.model().indexFromItem(self.itm_err), True)
#         self.itm_warn.setText("Warning [{}]".format(self.itm_warn.rowCount()))
#         self.tv_analysis.setExpanded(self.tv_analysis.model().indexFromItem(self.itm_warn), True)
#         self.itm_val.setText("Valid [{}]".format(self.itm_val.rowCount()))
#
#         self.fra_save.show()
#         self.fra_sel.setEnabled(False)
#
#     def cancel_analysis(self):
#         self.d_profiles.clear()
#         self.fra_save.hide()
#         self.fra_sel.setEnabled(True)
#
#     def save_analysis(self):
#         recs = list()
#
#         l_prof_to_edit = list()
#         for r in range(self.itm_warn.rowCount()):
#             if self.itm_warn.child(r, 0).checkState() == 2:
#                 p = self.d_profiles[self.itm_warn.child(r, 0).data(Qt.UserRole)]
#                 l_prof_to_edit.append(p)
#
#         for id_prof, profil in self.d_profiles.items():
#             if profil.status == 2:
#                 recs.append([*profil.intersections, id_prof])
#             elif profil.status == 1 and id_prof in l_prof_to_edit:
#                 recs.append([*profil.intersections, id_prof])
#
#         sql = "UPDATE {0}.profiles SET left{1}_g = %s, right{1}_g = %s " "WHERE gid = %s;".format(
#             self.mdb.SCHEMA, D_FLD_BED[self.bg_type.checkedId()]
#         )
#         self.mdb.run_query(sql, many=True, list_many=recs)
#
#         self.lay_profile.reload()
#         QMessageBox.information(self, "Information", "Import successful", QMessageBox.Ok)
#         self.cancel_analysis()
#
#
# class Profile:
#     def __init__(self, ft):
#         self.id = ft.id()
#         self.geom = ft.geometry()
#         self.line_xy = ft.geometry().asMultiPolyline()
#         self.name = ft["name"]
#         self.db_bed = [ft["leftminbed"], ft["rightminbed"]]
#         self.db_stock = [ft["leftstock"], ft["rightstock"]]
#         self.lx = [float(x) for x in str(ft["x"]).strip().split(" ")]
#         self.x_start = min(self.lx)
#         self.x_end = max(self.lx)
#         self.lz = [float(z) for z in str(ft["z"]).strip().split(" ")]
#         self.x_branch = float()
#         self.intersections = list()
#         self.status = int()
#         self.mess = str()
#         self.init_var()
#
#     def init_var(self):
#         self.x_branch = None
#         self.intersections.clear()
#         self.status = 0
#         self.mess = ""
#
#     def intersects_branch(self, l_branch_geom):
#         for b_geom in l_branch_geom:
#             res = self.geom.intersection(b_geom)
#             if res:
#                 if res.wkbType() == QgsWkbTypes.Point:
#                     self.x_branch = round(self.geom.lineLocatePoint(res), 2)
#
#     def intersects_bed(self, l_bed_geom):
#         for b_geom in l_bed_geom:
#             res = self.geom.intersection(b_geom)
#             if res:
#                 if res.wkbType() == QgsWkbTypes.Point:
#                     self.intersections.append(round(self.geom.lineLocatePoint(res), 2))
#                 if res.wkbType() == QgsWkbTypes.MultiPoint:
#                     for point in res.parts():
#                         _g = QgsGeometry.fromPointXY(QgsPointXY(point.x(), point.y()))
#                         self.intersections.append(round(self.geom.lineLocatePoint(_g), 2))
#         self.intersections.sort()
#
#     def validate(self, typ_bed):
#         if typ_bed == "bed":
#             self.validate_bed()
#         elif typ_bed == "stock":
#             self.validate_stock()
#
#     def validate_bed(self):
#         nb_inter = len(self.intersections)
#         if nb_inter == 0:
#             self.status = 0
#         elif nb_inter == 1:
#             self.status = -1
#             self.mess = "Only one intersection with the polyline(s)"
#         elif nb_inter == 2:
#             i_start, i_end = self.intersections
#             if self.x_start <= i_start < i_end <= self.x_end:
#                 if i_start < self.x_branch < i_end:
#                     if self.db_stock[0] != qgis_null:
#                         if i_start < self.db_stock[0]:
#                             self.status = 1
#                             self.mess = "Minor River Bed intersects the left current Storage Area"
#                             return
#
#                     if self.db_stock[1] != qgis_null:
#                         if i_end > self.db_stock[1]:
#                             self.status = 1
#                             self.mess = "Minor River Bed intersects the right current Storage Area"
#                             return
#
#                     self.status = 2
#                 else:
#                     self.status = 1
#                     self.mess = "Minor River Bed doesn't contain the branch"
#             else:
#                 self.status = 1
#                 self.mess = "Limit(s) of the Minor River Bed outside the final profile"
#         else:
#             self.status = -1
#             self.mess = "More than two intersections with the polyline(s)"
#
#     def validate_stock(self):
#         if len(self.intersections) == 0:
#             self.status = 0
#         elif len(self.intersections) == 1:
#             inter = self.intersections[0]
#             if not self.db_bed[0] <= inter <= self.db_bed[1]:
#                 if inter <= self.db_bed[0]:
#                     self.intersections = [inter, None]
#                 else:
#                     self.intersections = [None, inter]
#
#                 if self.x_start <= inter <= self.x_end:
#                     self.status = 2
#                 else:
#                     self.status = 1
#                     self.mess = "Limit of the Storage Area outside the final profile"
#             else:
#                 if inter < self.x_branch:
#                     self.intersections = [inter, None]
#                 else:
#                     self.intersections = [None, inter]
#                 self.status = 1
#                 self.mess = "Storage Area intersects the current Minor River Bed"
#         elif len(self.intersections) == 2:
#             i_start, i_end = self.intersections
#             if i_start <= self.db_bed[0] <= self.db_bed[1] <= i_end:
#                 if self.x_start <= i_start < i_end <= self.x_end:
#                     self.status = 2
#                 else:
#                     self.status = 1
#                     self.mess = "Limit of the Storage Area(s) outside the final profile"
#             else:
#                 self.status = 1
#                 if self.db_bed[0] <= i_start <= i_end <= self.db_bed[1]:
#                     self.mess = "Storage Areas intersect the current Minor River Bed"
#                 elif i_start <= self.db_bed[0] <= i_end <= self.db_bed[1]:
#                     self.mess = "Right Storage Area intersects the current Minor River Bed"
#                 elif self.db_bed[0] <= i_start <= self.db_bed[1] <= i_end:
#                     self.mess = "Left Storage Area intersects the current Minor River Bed"
#                 else:
#                     self.mess = (
#                         "Both Storage Areas are in the same side of the current Minor River Bed"
#                     )
#         else:
#             self.status = -1
#             self.mess = "More than two intersections"
