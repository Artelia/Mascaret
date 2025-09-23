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
from datetime import timedelta

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.core import NULL as qgis_null
from qgis.gui import *
from qgis.utils import *
from scipy import interpolate

from ..ui.custom_control import ClassWarningBox

D_PARAM = {"z": {"txt": "Water level", "var_profil": "Z", "var_basin": "ZCAS"},
           "char": {"txt": "Hydraulic head", "var_profil": "CHAR", "var_basin": None}}


class ClassCartoZI(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.itm_val, self.itm_warn, self.itm_err = None, None, None

        self.load_error = False
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_carto_zi.ui"), self)
        self.box = ClassWarningBox()

        self.bg_value = QButtonGroup()
        self.bg_value.addButton(self.rb_time, 0)
        self.bg_value.addButton(self.rb_max, 1)
        self.bg_value.addButton(self.rb_min, 2)

        self.bg_value.buttonClicked.connect(self.value_changed)
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

        self.profil_cnt, self.basin_cnt = get_layers_cnt(self.mdb)

        self.init_cb_run()
        self.init_cb_param()
        self.init_cb_lay_model()

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

    def init_cb_param(self):
        self.cb_param.clear()
        for key_param, val_param in D_PARAM.items():
            self.cb_param.addItem(val_param["txt"], key_param)

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

        if self.cur_param:
            self.set_layers_status()

    def param_changed(self):
        self.cur_param = self.cb_param.currentData()
        self.set_layers_status()

    def set_layers_status(self):
        param_info = D_PARAM[self.cur_param]

        if self.cur_scen:
            if self.profil_cnt == 0:
                enable_profil = False
                self.cc_profil.setText("No profile found")
            else:
                if param_info["var_profil"]:
                    if verif_values_exist(self.mdb, self.cur_scen, self.cur_param, "profil"):
                        enable_profil = True
                        self.cc_profil.setText("Profiles")
                    else:
                        enable_profil = False
                        self.cc_profil.setText("Profiles (No results found for the scenario "
                                               "and parameter selected)")
                else:
                    enable_profil = False
                    self.cc_profil.setText("Profiles (Parameter not available)")
        else:
            enable_profil = False
            self.cc_profil.setText("Profiles")

        self.cc_profil.setChecked(enable_profil)
        self.cc_profil.setEnabled(enable_profil)
        self.fra_lay_prof.setEnabled(enable_profil)
        if not enable_profil:
            self.cc_lay_profil.setChecked(enable_profil)


        if self.cur_scen:
            if self.basin_cnt == 0:
                enable_basin = False
                self.cc_basin.setText("No basin found")
            else:
                if param_info["var_basin"]:
                    if verif_values_exist(self.mdb, self.cur_scen, self.cur_param, "basin"):
                        enable_basin = True
                        self.cc_basin.setText("Basins")
                    else:
                        enable_basin = False
                        self.cc_basin.setText("Basins (No results found for the scenario "
                                              "and parameter selected)")
                else:
                    enable_basin = False
                    self.cc_basin.setText("Basins (Parameter not available)")
        else:
            enable_basin = False
            self.cc_basin.setText("Basins")

        self.cc_basin.setChecked(enable_basin)
        self.cc_basin.setEnabled(enable_basin)


    def value_changed(self, v_button):
        ib_button = self.bg_value.id(v_button)
        if ib_button == 0:
            self.cb_time.setEnabled(True)
        else:
            self.cb_time.setEnabled(False)

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
            if self.box.yes_no_q("Layers already exist. Erase them ?", title="Warning"):
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

        if res_basin:
            _lay = QgsVectorLayer(basin_file, "CartoZI basins", "ogr")
            _mlay = QgsProject.instance().addMapLayer(_lay, False)
            QgsProject.instance().layerTreeRoot().insertLayer(0, _mlay)

        if res_profile:
            _lay = QgsVectorLayer(profil_file, "CartoZI profiles", "ogr")
            _mlay = QgsProject.instance().addMapLayer(_lay, False)
            QgsProject.instance().layerTreeRoot().insertLayer(0, _mlay)

        QMessageBox.information(self, "Information", "Export successful")


def get_layers_cnt(mdb):
    sql = "SELECT COUNT(*) FROM {0}.profiles".format(mdb.SCHEMA)
    rows = mdb.run_query(sql, fetch=True)
    profil_cnt = rows[0][0]

    sql = "SELECT COUNT(*) FROM {0}.basins".format(mdb.SCHEMA)
    rows = mdb.run_query(sql, fetch=True)
    basin_cnt = rows[0][0]

    return profil_cnt, basin_cnt


def verif_values_exist(mdb, cur_scen, cur_param, lay):
    if lay == "profil":
        typ_var = "opt"
    else:
        typ_var = "basin"

    var_id = get_var_id(mdb, typ_var, D_PARAM[cur_param]["var_{}".format(lay)])

    cnt_val = 0
    if var_id is not None:
        sql = "SELECT COUNT(*) FROM {0}.results " \
              "WHERE id_runs = {1} AND var = {2} " \
              "".format(mdb.SCHEMA, cur_scen, var_id)
        rows = mdb.run_query(sql, fetch=True)
        cnt_val = rows[0][0]

    if cnt_val == 0:
        return False
    else:
        return True


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
