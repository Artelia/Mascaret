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
from qgis.gui import *
from qgis.utils import *
from shapely.geometry import LineString
from shapely.ops import unary_union, linemerge, substring
from shapely.wkt import loads as wkt_loads

D_TYP_BED = {0: "bed", 1: "stock"}
D_FLD_BED = {0: "minbed", 1: "stock"}


class Profile:
    def __init__(self, row):
        profile_id, profile_name, lst_x, lst_z, lmb, rmb, ls, rs, lmb_g, rmb_g, ls_g, rs_g = row

        self.id = profile_id
        self.name = profile_name
        self.bed = [lmb, rmb]
        self.stock = [ls, rs]
        self.bed_g = [lmb_g, rmb_g]
        self.stock_g = [ls_g, rs_g]
        self.lx_txt = str(lst_x)
        self.lx = [float(x) for x in self.lx_txt.strip().split(" ")]
        self.x_start = min(self.lx)
        self.x_end = max(self.lx)
        self.lz_txt = str(lst_z)
        self.lz = [float(z) for z in self.lz_txt.strip().split(" ")]
        self.status = int()
        self.mess = str()
        self.status = str()
        self.mess = str()


class ClassUpdateBedDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = mgis.iface
        self.itm_val, self.itm_warn, self.itm_err, self.itm_no_val = None, None, None, None

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_bed_update.ui"), self)
        self.fra_save.hide()

        self.lay_profile = self.find_db_layer()
        self.d_profiles = dict()
        self.lst_sel_profiles = list()

        for typ_bed, nm_bed in [
            ["lsa", "Left Storage Area"],
            ["lmrb", "Minor River Bed (Left Bank only)"],
            ["mrb", "Minor River Bed"],
            ["rmrb", "Minor River Bed (Right Bank only)"],
            ["rsa", "Right Storage Area"],
        ]:
            self.cb_typ_bed.addItem(nm_bed, typ_bed)

        self.cb_typ_bed.currentIndexChanged.connect(self.change_typ_bed)
        self.bt_analysis.clicked.connect(self.start_analysis)
        self.bt_cancel.clicked.connect(self.cancel_analysis)
        self.bt_save.clicked.connect(self.save_analysis)

        self.init_cb_branch()
        self.cb_typ_bed.setCurrentIndex(2)

    def find_db_layer(self):
        p_lay = None
        tree_root = QgsProject.instance().layerTreeRoot()
        mas_group = tree_root.findGroup("Mas_{}".format(self.mdb.SCHEMA))
        l_child = mas_group.children()
        for child in l_child:
            if (
                    child.nodeType() == 1
                    and "dbname='{}'".format(self.mdb.dbname) in child.layer().source()
            ):
                if 'table="{}"."profiles"'.format(self.mdb.SCHEMA) in child.layer().source():
                    p_lay = child.layer()

        return p_lay

    def init_cb_branch(self):
        sql = "SELECT branch, 'Branch ' || branch FROM {0}.branchs WHERE active IS True"
        l_branch = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        for id_branch, nm_branch in l_branch:
            self.cb_branch.addItem(nm_branch, id_branch)

        self.cc_profil_sel.setEnabled(False)
        if self.lay_profile:
            if self.lay_profile.selectedFeatureCount() > 0:
                l_ft = self.lay_profile.getSelectedFeatures()
                for ft in l_ft:
                    if ft["active"] is True:
                        self.lst_sel_profiles.append(ft["gid"])

                self.cc_profil_sel.setEnabled(True)
                self.cc_profil_sel.setCheckState(2)

    def change_typ_bed(self):
        typ_bed = self.cb_typ_bed.currentData()
        if typ_bed in ["lmrb", "rmrb", "mrb"]:
            self.cc_null_value.hide()
            self.cc_null_value.setCheckState(0)
        else:
            self.cc_null_value.show()

    def start_analysis(self):
        self.fra_save.hide()

        mdl = QStandardItemModel()
        self.itm_val = QStandardItem("Valid")
        self.itm_val.setFlags(Qt.ItemIsEnabled)
        self.itm_val.setForeground(QBrush(QColor(60, 155, 60)))
        self.itm_warn = QStandardItem("Warning")
        self.itm_warn.setFlags(Qt.ItemIsEnabled)
        self.itm_warn.setForeground(QBrush(QColor(255, 100, 0)))
        self.itm_err = QStandardItem("Error")
        self.itm_err.setFlags(Qt.ItemIsEnabled)
        self.itm_err.setForeground(QBrush(QColor(255, 0, 0)))
        self.itm_no_val = QStandardItem("No data")
        self.itm_no_val.setFlags(Qt.ItemIsEnabled)
        if self.cc_null_value.isChecked():
            self.itm_no_val.setForeground(QBrush(QColor(60, 155, 60)))
        else:
            self.itm_no_val.setForeground(QBrush(QColor(255, 0, 0)))

        if self.cc_null_value.isChecked():
            lst_itm = [self.itm_val, self.itm_no_val, self.itm_warn, self.itm_err]
        else:
            lst_itm = [self.itm_val, self.itm_warn, self.itm_no_val, self.itm_err]

        for itm in lst_itm:
            mdl.appendRow(itm)
        self.tv_analysis.setModel(mdl)

        branch = self.cb_branch.currentData()
        typ_bed = self.cb_typ_bed.currentData()

        # Sélection des profils
        sql = (
            "SELECT gid, name, x, z, leftminbed, rightminbed, leftstock, rightstock, "
            "leftminbed_g, rightminbed_g, leftstock_g, rightstock_g  "
            "FROM {0}.profiles WHERE active IS True AND branchnum = {1}"
        )
        l_profiles = self.mdb.run_query(sql.format(self.mdb.SCHEMA, branch), fetch=True)

        self.d_profiles.clear()
        for row in l_profiles:
            do_profile = True
            p = Profile(row)

            if self.cc_profil_sel.isChecked() and (p.id not in self.lst_sel_profiles):
                do_profile = False

            if do_profile:
                if typ_bed == "lmrb":
                    if p.bed_g[0]:
                        p.status, p.mess = verif_left_bed(p.bed_g[0], p.stock[0], p.lx)
                    else:
                        p.status, p.mess = "n", str()
                elif typ_bed == "rmrb":
                    if p.bed_g[1]:
                        p.status, p.mess = verif_right_bed(p.bed_g[1], p.stock[1], p.lx)
                    else:
                        p.status, p.mess = "n", str()
                elif typ_bed == "mrb":
                    if p.bed_g[0] and p.bed_g[1]:
                        p.status, p.mess = verif_both_bed(p.bed_g, p.stock, p.lx)
                    else:
                        p.status, p.mess = "n", str()
                elif typ_bed == "lsa":
                    if p.stock_g[0]:
                        p.status, p.mess = verif_left_stock(p.stock_g[0], p.bed, p.lx)
                    else:
                        p.status, p.mess = "n", str()
                elif typ_bed == "rsa":
                    if p.stock_g[1]:
                        p.status, p.mess = verif_right_stock(p.stock_g[1], p.bed, p.lx)
                    else:
                        p.status, p.mess = "n", str()

                self.d_profiles[row[0]] = p

        for prof in self.d_profiles.values():
            if prof.status == "e":
                idx = self.itm_err.rowCount()
                itm = QStandardItem()
                itm.setData("{} : {}".format(prof.name, prof.mess), Qt.DisplayRole)
                itm.setData(prof.id, Qt.UserRole)
                itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.itm_err.setChild(idx, itm)
            elif prof.status == "w":
                idx = self.itm_warn.rowCount()
                itm = QStandardItem()
                itm.setData("{} : {}".format(prof.name, prof.mess), Qt.DisplayRole)
                itm.setData(prof.id, Qt.UserRole)
                itm.setCheckState(2)
                itm.setCheckable(True)
                self.itm_warn.setChild(idx, itm)
            elif prof.status == "v":
                idx = self.itm_val.rowCount()
                itm = QStandardItem()
                itm.setData("{}".format(prof.name), Qt.DisplayRole)
                itm.setData(prof.id, Qt.UserRole)
                itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.itm_val.setChild(idx, itm)
            elif prof.status == "n":
                idx = self.itm_no_val.rowCount()
                itm = QStandardItem()
                itm.setData("{}".format(prof.name), Qt.DisplayRole)
                itm.setData(prof.id, Qt.UserRole)
                itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.itm_no_val.setChild(idx, itm)

        self.itm_err.setText("Error [{}]".format(self.itm_err.rowCount()))
        self.tv_analysis.setExpanded(self.tv_analysis.model().indexFromItem(self.itm_err), True)
        self.itm_warn.setText("Warning [{}]".format(self.itm_warn.rowCount()))
        self.tv_analysis.setExpanded(self.tv_analysis.model().indexFromItem(self.itm_warn), True)
        self.itm_val.setText("Valid [{}]".format(self.itm_val.rowCount()))
        if self.cc_null_value.isChecked():
            self.itm_no_val.setText("NULL values (erased) [{}]".format(self.itm_no_val.rowCount()))
        else:
            self.itm_no_val.setText("No data [{}]".format(self.itm_no_val.rowCount()))

        self.fra_save.show()
        self.fra_sel.setEnabled(False)

    def cancel_analysis(self):
        self.d_profiles.clear()
        self.fra_save.hide()
        self.fra_sel.setEnabled(True)

    def save_analysis(self):
        l_prof_to_edit = list()
        branch = self.cb_branch.currentData()
        typ_bed = self.cb_typ_bed.currentData()

        for r in range(self.itm_val.rowCount()):
            p = self.d_profiles[self.itm_val.child(r, 0).data(Qt.UserRole)]
            l_prof_to_edit.append(p)

        for r in range(self.itm_warn.rowCount()):
            if self.itm_warn.child(r, 0).checkState() == 2:
                p = self.d_profiles[self.itm_warn.child(r, 0).data(Qt.UserRole)]
                l_prof_to_edit.append(p)

        if self.cc_null_value.isChecked():
            for r in range(self.itm_no_val.rowCount()):
                p = self.d_profiles[self.itm_no_val.child(r, 0).data(Qt.UserRole)]
                l_prof_to_edit.append(p)

        recs = dict()
        for p in l_prof_to_edit:
            rec = dict()
            if typ_bed == "lmrb":
                rec["leftminbed"] = p.bed_g[0]
            elif typ_bed == "rmrb":
                rec["rightminbed"] = p.bed_g[1]
            elif typ_bed == "mrb":
                rec["leftminbed"] = p.bed_g[0]
                rec["rightminbed"] = p.bed_g[1]
            elif typ_bed == "lsa":
                rec["leftstock"] = p.stock_g[0]
            elif typ_bed == "rsa":
                rec["rightstock"] = p.stock_g[1]

            interp_done = False
            for x in rec.values():
                if x not in p.lx:
                    interp_valid = interpolate_x_val(x, p.lx, p.lz)
                    if not interp_valid:
                        pass
                    else:
                        interp_done = True

            if interp_done:
                rec["x"] = p.lx
                rec["z"] = p.lz

            recs[p.name] = rec

        self.mdb.update("profiles", recs, var="name")

        if typ_bed == "lmrb":
            update_bed_geometry(self.mdb, branch, ["leftminbed"])
        elif typ_bed == "rmrb":
            update_bed_geometry(self.mdb, branch, ["rightminbed"])
        elif typ_bed == "mrb":
            update_bed_geometry(self.mdb, branch, ["leftminbed", "rightminbed"])

        refresh_minor_bed_layer(self.mdb, self.iface)
        QMessageBox.information(self, "Information", "Update successful", QMessageBox.Ok)
        self.cancel_analysis()


def interpolate_x_val(new_x, lx, lz):
    for i, x in enumerate(lx):
        if x > new_x:
            x0, x1 = lx[i - 1: i + 1]
            z0, z1 = lz[i - 1: i + 1]
            new_z = z0 + (z1 - z0) / (x1 - x0) * (new_x - x0)
            lx.insert(i, new_x)
            lz.insert(i, new_z)
            return True

    return False


def verif_both_bed(l_new_x, stock, lx):
    l_status, l_mess = verif_left_bed(l_new_x[0], stock[0], lx)
    r_status, r_mess = verif_right_bed(l_new_x[1], stock[1], lx)

    if l_status == "e":
        return l_status, l_mess

    if r_status == "e":
        return r_status, r_mess

    if l_status == "w":
        return l_status, l_mess

    if r_status == "w":
        return r_status, r_mess

    return "v", str()


def verif_left_bed(new_x, lstock, lx):
    if new_x < min(lx):
        mess = "Left limit of the Minor River Bed is located outside the final profile"
        return "e", mess

    if lstock is not None:
        if new_x <= lstock:
            mess = (
                "Limit(s) of Minor River Bed intersects Storage Area(s). "
                "Storage Area(s) concerned will be erased."
            )
            return "w", mess

    return "v", str()


def verif_right_bed(new_x, rstock, lx):
    if new_x > max(lx):
        mess = "Right limit of the Minor River Bed is located outside the final profile"
        return "e", mess

    if rstock is not None:
        if new_x >= rstock:
            mess = (
                "Limit(s) of Minor River Bed intersects Storage Area(s). "
                "Storage Area(s) concerned will be erased."
            )
            return "w", mess

    return "v", str()


def verif_left_stock(new_x, bed, lx):
    if new_x > bed[1]:
        mess = "Limit of the left Storage Area is located on the right side of the Minor River Bed"
        return "e", mess

    if bed[0] <= new_x <= bed[1]:
        mess = "Limit of the left Storage Area is located inside the Minor River Bed"
        return "e", mess

    if not min(lx) < new_x < max(lx):
        mess = "Limit of the left Storage Area is located outside the final profile"
        return "e", mess

    return "v", str()


def verif_right_stock(new_x, bed, lx):
    if new_x < bed[0]:
        mess = "Limit of the right Storage Area is located on the left side of the Minor River Bed"
        return "e", mess

    if bed[0] <= new_x <= bed[1]:
        mess = "Limit of the right Storage Area is located inside the Minor River Bed"
        return "e", mess

    if not min(lx) < new_x < max(lx):
        mess = "Limit of the right Storage Area is located outside the final profile"
        return "e", mess

    return "v", str()


def refresh_minor_bed_layer(mdb, iface):
    mrb_lay, p_lay = None, None
    tree_root = QgsProject.instance().layerTreeRoot()
    mas_group = tree_root.findGroup("Mas_{}".format(mdb.SCHEMA))
    l_child = mas_group.children()
    for child in l_child:
        if child.nodeType() == 1 and "dbname='{}'".format(mdb.dbname) in child.layer().source():
            if 'table="{}"."visu_minor_river_bed"'.format(mdb.SCHEMA) in child.layer().source():
                mrb_lay = child.layer()
            if 'table="{}"."profiles"'.format(mdb.SCHEMA) in child.layer().source():
                p_lay = child.layer()

    for lay in [mrb_lay, p_lay]:
        if lay:
            lay.reload()
            lay.updateExtents()
            lay.triggerRepaint()

    iface.mapCanvas().refresh()


def update_all_bed_geometry(mdb):
    sql = "SELECT branch, 'Branch ' || branch FROM {0}.branchs WHERE active IS True"
    l_branch = mdb.run_query(sql.format(mdb.SCHEMA), fetch=True)
    for id_branch, nm_branch in l_branch:
        update_bed_geometry(mdb, id_branch, ["leftminbed", "rightminbed"])


def update_bed_geometry(mdb, id_branch, l_typ_bed):
    for typ_bed in l_typ_bed:
        bank = typ_bed.replace("minbed", "")

        sql = (
            "SELECT pr_num, pr_name, pr_id, next_pr_id, pr_pk, next_pr_pk, dist_prj, next_dist_prj, "
            "interp_pt_txt, next_interp_pt_txt, pt_prj_txt, next_pt_prj_txt, "
            "ST_Length(ST_LineSubstring(br_geom, pr_pk, next_pr_pk)), "
            "ST_AsText(ST_LineSubstring(br_geom, pr_pk, next_pr_pk)) "
            "FROM "
            "(SELECT pr_num, pr_name, "
            "pr_id, LEAD(pr_id, 1) OVER (ORDER BY pr_pk) As next_pr_id, "
            "pr_pk, LEAD(pr_pk, 1) OVER (ORDER BY pr_pk) As next_pr_pk, "
            "dist_prj, LEAD(dist_prj, 1) OVER (ORDER BY pr_pk) As next_dist_prj, "
            "ST_AsText(interp_pt) As interp_pt_txt, "
            "LEAD(ST_AsText(interp_pt), 1) OVER (ORDER BY pr_pk) As next_interp_pt_txt, "
            "ST_AsText(pt_prj) As pt_prj_txt, "
            "LEAD(ST_AsText(pt_prj), 1) OVER (ORDER BY pr_pk) As next_pt_prj_txt, "
            "br_geom "
            "FROM "
            "(SELECT *, ST_LineLocatePoint(br_geom, pt_prj) As pr_pk, "
            "ST_Distance(interp_pt, pt_prj) As dist_prj "
            "FROM "
            "(SELECT *, ST_ClosestPoint(br_geom, interp_pt) As pt_prj "
            "FROM "
            "(SELECT ROW_NUMBER() OVER (ORDER BY abscissa) As pr_num, "
            "name as pr_name, pr.gid As pr_id, pr.abscissa As pr_abs, {2} As dist, "
            "ST_LineInterpolatePoint(ST_LineMerge(pr.geom), {2}/ST_LENGTH(pr.geom)) As interp_pt, "
            "ST_LineMerge(pr.geom) As pr_geom, ST_LineMerge(br.geom) As br_geom "
            "FROM {0}.profiles As pr, {0}.branchs As br "
            "WHERE ST_Intersects(ST_LineMerge(br.geom), pr.geom) AND pr.active AND br.active "
            "AND br.branch = {1} ORDER BY abscissa) "
            "As r1) As r2) As r3) As r4"
        )

        rows = mdb.run_query(sql.format(mdb.SCHEMA, id_branch, typ_bed), fetch=True)
        if not rows :
            mdb.run_query(
                "DELETE FROM {0}.visu_minor_river_bed "
                "WHERE bank = '{1}' AND branchnum = {2}".format(mdb.SCHEMA, bank, id_branch)
            )
            return
        recs = list()
        for row in rows:
            (
                pr_num,
                pr_name,
                pr_id,
                next_pr_id,
                pk,
                next_pk,
                start_lmb,
                end_lmb,
                pt_prof,
                next_pt_prof,
                pt_proj,
                next_pt_proj,
                len_troncon,
                troncon,
            ) = row

            l_coords = list()
            if start_lmb and end_lmb:
                l_coords.extend(wkt_loads(pt_prof).coords)
                dist_pt = max([start_lmb, end_lmb])
                g_troncon = wkt_loads(troncon)

                lst_pts, lst_val = list(), list()
                dist = dist_pt
                while dist < len_troncon:
                    pt = g_troncon.interpolate(dist)
                    lst_pts.append(pt)
                    lst_val.append(start_lmb + (end_lmb - start_lmb) / len_troncon * dist)
                    dist += dist_pt

                if len(lst_pts) > 3:
                    g_troncon_buff = LineString(substring(g_troncon, dist_pt, dist - dist_pt))
                    if typ_bed in ["rightminbed"]:
                        g_buff = g_troncon_buff.buffer(
                            -dist_pt * 2.0, cap_style=2, single_sided=True
                        )
                    else:
                        g_buff = g_troncon_buff.buffer(
                            dist_pt * 2.0, cap_style=2, single_sided=True
                        )

                    lst_buff = list()
                    for id_pt, pt in enumerate(lst_pts):
                        buff = pt.buffer(lst_val[id_pt])
                        lst_buff.append(buff)

                    lst_poly = list()
                    for id_buff in range(len(lst_buff) - 1):
                        lst_poly.append(
                            unary_union([lst_buff[id_buff], lst_buff[id_buff + 1]]).convex_hull
                        )

                    poly = unary_union(lst_poly)

                    pl_temp = poly.boundary.intersection(g_buff)
                    if pl_temp.type == "MultiLineString":
                        pl_temp = linemerge(pl_temp)
                        if pl_temp.type == "MultiLineString":
                            line = LineString()
                            for pl in pl_temp.geoms:
                                if pl.length > line.length:
                                    line = pl
                            pl_temp = line
                    pl_coords = list(pl_temp.coords)
                    if typ_bed in ["rightminbed"]:
                        pl_coords.reverse()

                    l_coords.extend(pl_coords)

                l_coords.extend(wkt_loads(next_pt_prof).coords)
                pl_final = LineString(l_coords)
                recs.append([id_branch, pr_name, bank, pl_final.wkt])

        mdb.run_query(
            "DELETE FROM {0}.visu_minor_river_bed "
            "WHERE bank = '{1}' AND branchnum = {2}".format(mdb.SCHEMA, bank, id_branch)
        )
        if recs:
            sql = (
                "INSERT INTO {0}.visu_minor_river_bed (branchnum, profile, bank, geom) "
                "VALUES (%s, %s, %s, ST_GeomFromText(%s))".format(mdb.SCHEMA)
            )
            mdb.run_query(sql, many=True, list_many=recs)
