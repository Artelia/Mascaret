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
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QColor, QBrush
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.core import NULL as qgis_null
from qgis.gui import *
from qgis.utils import *
from ..ui.custom_control import _qt_is_checked
D_TYP_BED = {0: "bed", 1: "stock"}
D_FLD_BED = {0: "minbed", 1: "stock"}

QT_VERSION = [int(v) for v in qVersion().split('.')][0]

class ClassExtractBedDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.itm_val, self.itm_warn, self.itm_err = None, None, None

        self.load_error = False
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_profiles_bed.ui"), self)
        self.fra_save.hide()

        self.lay_bed = None
        self.lay_branch, self.lay_profile = self.find_db_layer()

        self.d_profiles = dict()

        if not self.lay_branch:
            QMessageBox.critical(self, "Error", "Branches layer not found", QMessageBox.Ok)
            self.load_error = True

        if not self.lay_profile:
            QMessageBox.critical(self, "Error", "Profiles layer not found", QMessageBox.Ok)
            self.load_error = True

        if not self.load_error:
            self.bg_type = QButtonGroup()
            self.bg_type.addButton(self.rb_river_bed, 0)
            self.bg_type.addButton(self.rb_storage_area, 1)

            # self.cb_branch.currentIndexChanged.connect(self.cur_branch_changed)
            self.cb_qgis_layers.currentIndexChanged.connect(self.cur_qgis_layer_changed)
            self.bt_analysis.clicked.connect(self.start_analysis)
            self.bt_cancel.clicked.connect(self.cancel_analysis)
            self.bt_save.clicked.connect(self.save_analysis)

            self.init_cb_branch()
            self.init_cb_lay_model()

    def find_db_layer(self):
        b_lay, p_lay = None, None
        tree_root = QgsProject.instance().layerTreeRoot()
        mas_group = tree_root.findGroup("Mas_{}".format(self.mdb.SCHEMA))
        l_child = mas_group.children()
        for child in l_child:
            if (
                    child.nodeType() == 1
                    and "dbname='{}'".format(self.mdb.dbname) in child.layer().source()
            ):
                if 'table="{}"."branchs"'.format(self.mdb.SCHEMA) in child.layer().source():
                    b_lay = child.layer()
                if 'table="{}"."profiles"'.format(self.mdb.SCHEMA) in child.layer().source():
                    p_lay = child.layer()

        return b_lay, p_lay

    def init_cb_branch(self):
        sql = "SELECT branch, 'Branch ' || branch FROM {0}.branchs WHERE active IS True"
        l_branch = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        for id_branch, nm_branch in l_branch:
            self.cb_branch.addItem(nm_branch, id_branch)

        self.cc_profil_sel.setEnabled(False)
        if self.lay_profile.selectedFeatureCount() > 0:
            self.cc_profil_sel.setEnabled(True)
            self.cc_profil_sel.setChecked(True)

    def init_cb_lay_model(self):
        excluded_str = ['table="{}"'.format(self.mdb.SCHEMA), "dbname='{}'".format(self.mdb.dbname)]

        l_excl_lay = []
        for lay_id in QgsProject.instance().mapLayers():
            lay = QgsProject.instance().layerTreeRoot().findLayer(lay_id).layer()
            if all(path in os.path.normpath(lay.source()) for path in excluded_str):
                l_excl_lay.append(lay)

        self.cb_qgis_layers.setExceptedLayerList(l_excl_lay)
        self.cb_qgis_layers.setFilters(QgsMapLayerProxyModel.LineLayer)

    def cur_qgis_layer_changed(self):
        self.lay_bed = None

        _l = self.cb_qgis_layers.currentLayer()
        if _l:
            if _l.type() == 0:
                self.lay_bed = _l

        if self.lay_bed:
            if self.lay_bed.selectedFeatureCount() > 0:
                self.cc_bed_sel.setEnabled(True)
                self.cc_bed_sel.setChecked(True)
            else:
                self.cc_bed_sel.setEnabled(False)
                self.cc_bed_sel.setChecked(False)
        else:
            self.cc_bed_sel.setEnabled(False)
            self.cc_bed_sel.setChecked(False)

    def start_analysis(self):
        if QT_VERSION > 5:
            ok_button = QMessageBox.StandardButton.Ok
            qt_disr = Qt.ItemDataRole.DisplayRole
            qt_usr = Qt.ItemDataRole.UserRole
            qt_itm_ena = Qt.ItemFlag.ItemIsEnabled
            qt_itm_sel = Qt.ItemFlag.ItemIsSelectable
            qt_check = Qt.CheckState
        else:
            ok_button = QMessageBox.Ok
            qt_disr = Qt.DisplayRole
            qt_usr =  Qt.UserRole
            qt_itm_ena = Qt.ItemIsEnabled
            qt_itm_sel =Qt.ItemIsSelectable
            qt_check = Qt
        if self.lay_bed.crs() != self.lay_profile.crs():
            QMessageBox.critical(
                self,
                "Error",
                "The projection of the layer for "
                "river beds must be {}".format(self.lay_profile.crs().authid()),
                ok_button,
            )
            return

        self.d_profiles.clear()
        self.fra_save.hide()

        mdl = QStandardItemModel()
        self.itm_val = QStandardItem("Valid")
        self.itm_val.setForeground(QBrush(QColor(60, 155, 60)))
        self.itm_warn = QStandardItem("Warning")
        self.itm_warn.setForeground(QBrush(QColor(255, 100, 0)))
        self.itm_err = QStandardItem("Error")
        self.itm_err.setForeground(QBrush(QColor(255, 0, 0)))
        self.itm_val.setFlags(qt_itm_ena)
        self.itm_warn.setFlags(qt_itm_ena)
        self.itm_err.setFlags(qt_itm_ena)


        for itm in [self.itm_val, self.itm_warn, self.itm_err]:
            mdl.appendRow(itm)
        self.tv_analysis.setModel(mdl)

        branch = self.cb_branch.currentData()
        typ_bed = D_TYP_BED[self.bg_type.checkedId()]

        # Sélection des branches
        l_branch_geom = []
        l_ft = self.lay_branch.getFeatures()
        for ft in l_ft:
            if ft["branch"] == branch and ft["active"] is True:
                l_branch_geom.append(ft.geometry())

        if not l_branch_geom:
            QMessageBox.critical(
                self, "Error", "No geometry found for branch {}".format(branch), ok_button
            )
            return

        # Sélection des profils
        if self.cc_profil_sel.isChecked():
            l_ft = self.lay_profile.getSelectedFeatures()
        else:
            l_ft = self.lay_profile.getFeatures()

        for ft in l_ft:
            if ft["branchnum"] == branch and ft["active"] is True:
                try:
                    test = [float(x) for x in str(ft["x"]).strip().split(" ")]
                except ValueError:
                    QMessageBox.critical(self, "Error", "There is no points on the profile", ok_button)
                    return
                p = Profile(ft)
                self.d_profiles[ft.id()] = p

        if not self.d_profiles:
            QMessageBox.critical(
                self, "Error", "No profiles found for branch {}".format(branch), ok_button
            )
            return

        # Sélection des polylignes (beds)
        if self.cc_bed_sel.isChecked():
            l_ft = self.lay_bed.getSelectedFeatures()
        else:
            l_ft = self.lay_bed.getFeatures()

        if not l_ft:
            QMessageBox.critical(self, "Error", "No bed polylines found", ok_button)
            return

        l_bed_geom = []
        for ft in l_ft:
            l_bed_geom.append(ft.geometry())

        # Analyse
        for id_prof, profil in self.d_profiles.items():
            profil.init_var()
            profil.intersects_branch(l_branch_geom)
            profil.intersects_bed(l_bed_geom)
            profil.validate(typ_bed)

        if profil.status == -1:
                idx = self.itm_err.rowCount()
                itm = QStandardItem()
                itm.setData("{} : {}".format(profil.name, profil.mess), qt_disr)
                itm.setData(profil.id, qt_usr)
                itm.setFlags(qt_itm_ena | qt_itm_sel)
                self.itm_err.setChild(idx, itm)
        elif profil.status == 1:
            idx = self.itm_warn.rowCount()
            itm = QStandardItem()
            itm.setData("{} : {}".format(profil.name, profil.mess), qt_disr)
            itm.setData(profil.id, qt_usr)
            itm.setCheckState(qt_check.Checked)
            itm.setCheckable(True)
            self.itm_warn.setChild(idx, itm)
        elif profil.status == 2:
            idx = self.itm_val.rowCount()
            itm = QStandardItem()
            itm.setData("{}".format(profil.name), qt_disr)
            itm.setData(profil.id, qt_usr)
            itm.setFlags(qt_itm_ena | qt_itm_sel)

            self.itm_val.setChild(idx, itm)

        self.itm_err.setText("Error [{}]".format(self.itm_err.rowCount()))
        self.tv_analysis.setExpanded(self.tv_analysis.model().indexFromItem(self.itm_err), True)
        self.itm_warn.setText("Warning [{}]".format(self.itm_warn.rowCount()))
        self.tv_analysis.setExpanded(self.tv_analysis.model().indexFromItem(self.itm_warn), True)
        self.itm_val.setText("Valid [{}]".format(self.itm_val.rowCount()))

        self.fra_save.show()
        self.fra_sel.setEnabled(False)

    def cancel_analysis(self):
        self.d_profiles.clear()
        self.fra_save.hide()
        self.fra_sel.setEnabled(True)

    def save_analysis(self):
        if QT_VERSION > 5:
            qt_usr = Qt.ItemDataRole.UserRole
            ok_bt = QMessageBox.StandardButton.Ok
        else:
            qt_usr = Qt.UserRole
            ok_bt = QMessageBox.Ok
        recs = list()

        l_prof_to_edit = list()
        for r in range(self.itm_warn.rowCount()):
            if _qt_is_checked(self.itm_warn.child(r, 0), check_level="full"):
                p = self.d_profiles[self.itm_warn.child(r, 0).data(qt_usr)]
                l_prof_to_edit.append(p)

        for id_prof, profil in self.d_profiles.items():
            if profil.status == 2:
                recs.append([*profil.intersections, id_prof])
            elif profil.status == 1 and id_prof in l_prof_to_edit:
                recs.append([*profil.intersections, id_prof])

        sql = "UPDATE {0}.profiles SET left{1}_g = %s, right{1}_g = %s " "WHERE gid = %s;".format(
            self.mdb.SCHEMA, D_FLD_BED[self.bg_type.checkedId()]
        )
        self.mdb.run_query(sql, many=True, list_many=recs)

        self.lay_profile.reload()
        QMessageBox.information(self, "Information", "Import successful", ok_bt)
        self.cancel_analysis()


class Profile:
    def __init__(self, ft):
        self.id = ft.id()
        self.geom = ft.geometry()
        self.line_xy = ft.geometry().asMultiPolyline()
        self.name = ft["name"]
        self.db_bed = [ft["leftminbed"], ft["rightminbed"]]
        self.db_stock = [ft["leftstock"], ft["rightstock"]]
        self.lx = [float(x) for x in str(ft["x"]).strip().split(" ")]
        self.x_start = min(self.lx)
        self.x_end = max(self.lx)
        self.lz = [float(z) for z in str(ft["z"]).strip().split(" ")]
        self.x_branch = float()
        self.intersections = list()
        self.status = int()
        self.mess = str()
        self.init_var()

    def init_var(self):
        self.x_branch = None
        self.intersections.clear()
        self.status = 0
        self.mess = ""

    def intersects_branch(self, l_branch_geom):
        for b_geom in l_branch_geom:
            res = self.geom.intersection(b_geom)
            if res:
                if res.wkbType() == QgsWkbTypes.Point:
                    self.x_branch = round(self.geom.lineLocatePoint(res), 2)

    def intersects_bed(self, l_bed_geom):
        for b_geom in l_bed_geom:
            res = self.geom.intersection(b_geom)
            if res:
                if res.wkbType() == QgsWkbTypes.Point:
                    self.intersections.append(round(self.geom.lineLocatePoint(res), 2))
                if res.wkbType() == QgsWkbTypes.MultiPoint:
                    for point in res.parts():
                        _g = QgsGeometry.fromPointXY(QgsPointXY(point.x(), point.y()))
                        self.intersections.append(round(self.geom.lineLocatePoint(_g), 2))
        self.intersections.sort()

    def validate(self, typ_bed):
        if typ_bed == "bed":
            self.validate_bed()
        elif typ_bed == "stock":
            self.validate_stock()

    def validate_bed(self):
        nb_inter = len(self.intersections)
        if nb_inter == 0:
            self.status = 0
        elif nb_inter == 1:
            self.status = -1
            self.mess = "Only one intersection with the polyline(s)"
        elif nb_inter == 2:
            i_start, i_end = self.intersections
            if self.x_start <= i_start < i_end <= self.x_end:
                if i_start < self.x_branch < i_end:
                    if self.db_stock[0] != qgis_null:
                        if i_start < self.db_stock[0]:
                            self.status = 1
                            self.mess = "Minor River Bed intersects the left current Storage Area"
                            return

                    if self.db_stock[1] != qgis_null:
                        if i_end > self.db_stock[1]:
                            self.status = 1
                            self.mess = "Minor River Bed intersects the right current Storage Area"
                            return

                    self.status = 2
                else:
                    self.status = 1
                    self.mess = "Minor River Bed doesn't contain the branch"
            else:
                self.status = 1
                self.mess = "Limit(s) of the Minor River Bed outside the final profile"
        else:
            self.status = -1
            self.mess = "More than two intersections with the polyline(s)"

    def validate_stock(self):
        if len(self.intersections) == 0:
            self.status = 0
        elif len(self.intersections) == 1:
            inter = self.intersections[0]
            if not self.db_bed[0] <= inter <= self.db_bed[1]:
                if inter <= self.db_bed[0]:
                    self.intersections = [inter, None]
                else:
                    self.intersections = [None, inter]

                if self.x_start <= inter <= self.x_end:
                    self.status = 2
                else:
                    self.status = 1
                    self.mess = "Limit of the Storage Area outside the final profile"
            else:
                if inter < self.x_branch:
                    self.intersections = [inter, None]
                else:
                    self.intersections = [None, inter]
                self.status = 1
                self.mess = "Storage Area intersects the current Minor River Bed"
        elif len(self.intersections) == 2:
            i_start, i_end = self.intersections
            if i_start <= self.db_bed[0] <= self.db_bed[1] <= i_end:
                if self.x_start <= i_start < i_end <= self.x_end:
                    self.status = 2
                else:
                    self.status = 1
                    self.mess = "Limit of the Storage Area(s) outside the final profile"
            else:
                self.status = 1
                if self.db_bed[0] <= i_start <= i_end <= self.db_bed[1]:
                    self.mess = "Storage Areas intersect the current Minor River Bed"
                elif i_start <= self.db_bed[0] <= i_end <= self.db_bed[1]:
                    self.mess = "Right Storage Area intersects the current Minor River Bed"
                elif self.db_bed[0] <= i_start <= self.db_bed[1] <= i_end:
                    self.mess = "Left Storage Area intersects the current Minor River Bed"
                else:
                    self.mess = (
                        "Both Storage Areas are in the same side of the current Minor River Bed"
                    )
        else:
            self.status = -1
            self.mess = "More than two intersections"
