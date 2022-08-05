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
from shapely.geometry import Point

from .ClassMascStruct import ClassMascStruct
from .ClassMethod import ClassMethod
from .ClassTableStructure import ClassTableStructure, update_etat_struct
from .ClassTableStructure import ctrl_set_value, ctrl_get_value, fill_qcombobox
# Widgets Buse
from .MetBordaBuWidget import MetBordaBuWidget
# Widgets Dalot
from .MetBordaDaWidget import MetBordaDaWidget
# Widgets Pont arche
from .MetBordaPaWidget import MetBordaPaWidget
from .MetBordaPcWidget import MetBordaPcWidget
# Widgets Pont cadre
from .MetBradleyPcWidget import MetBradleyPcWidget
from .MetOrificeBuWidget import MetOrificeBuWidget
from .MetOrificeDaWidget import MetOrificeDaWidget
from .MetOrificePaWidget import MetOrificePaWidget
from .MetOrificePcWidget import MetOrificePcWidget
# FloodGate
from .StructureFgDialog import StructureFgDialog
from .ClassLaws import ClassLaws
import numpy as np

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import *


class ClassStructureEditDialog(QDialog):
    def __init__(self, mgis, id_struct):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure()
        self.clmeth = ClassMethod(self.mgis)
        self.wgt_met = QWidget()

        self.met_calc = None
        self.meth = None

        self.param_meth_calc = {'PC': {0: {'wgt': MetBradleyPcWidget,
                                           'wgt_param': [self.mgis, '72',
                                                         id_struct]},
                                       1: {'wgt': MetBordaPcWidget,
                                           'wgt_param': [self.mgis, id_struct]},
                                       3: {'wgt': MetOrificePcWidget,
                                           'wgt_param': [self.mgis, id_struct]},
                                       4: {'wgt': MetBradleyPcWidget,
                                           'wgt_param': [self.mgis, '78',
                                                         id_struct]}
                                       },
                                'PA': {1: {'wgt': MetBordaPaWidget,
                                           'wgt_param': [self.mgis, id_struct]},
                                       3: {'wgt': MetOrificePaWidget,
                                           'wgt_param': [self.mgis, id_struct]}
                                       },
                                'DA': {1: {'wgt': MetBordaDaWidget,
                                           'wgt_param': [self.mgis, id_struct]},
                                       3: {'wgt': MetOrificeDaWidget,
                                           'wgt_param': [self.mgis, id_struct]}
                                       },
                                'BU': {1: {'wgt': MetBordaBuWidget,
                                           'wgt_param': [self.mgis, id_struct]},
                                       3: {'wgt': MetOrificeBuWidget,
                                           'wgt_param': [self.mgis, id_struct]}
                                       }
                                }

        self.id_struct = id_struct
        self.current_meth = 0
        self.lst_meth_calc = []
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_structure_edit.ui'),
            self)

        self.cb_met_calc.currentIndexChanged[int].connect(self.change_met_calc)
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)
        self.b_up_prof.clicked.connect(self.update_profil)
        self.b_up_prof.setIcon(QIcon(
            os.path.join(self.mgis.masplugPath, 'Structure/images/update.png')))
        self.dico_ctrl_fg = None

        if id_struct:
            self.is_loading = True
            sql = "SELECT name, type, method, active, id_prof_ori,comment FROM {0}.struct_config " \
                  "WHERE id = {1}".format(self.mdb.SCHEMA, self.id_struct)
            rows = self.mdb.run_query(sql, fetch=True)
            self.id_prof_ori = rows[0][4]
            self.typ_struct = rows[0][1]

            for m in self.tbst.dico_struc_typ[self.typ_struct]['meth_calc']:
                self.lst_meth_calc.append([m, self.tbst.dico_meth_calc[m]])

            self.lbl_type.setText(
                self.tbst.dico_struc_typ[self.typ_struct]['name'])
            self.txt_name.setText(rows[0][0])
            self.txt_comm.setText(rows[0][5])
            self.cc_active.setChecked(rows[0][3])
            fill_qcombobox(self.cb_met_calc, self.lst_meth_calc,
                           val_def=rows[0][2])
            self.is_loading = False

            rows = self.mdb.run_query(
                "SELECT gid FROM {0}.profiles".format(self.mdb.SCHEMA),
                fetch=True)

            list_p = [v[0] for v in rows]
            if self.id_prof_ori in list_p:
                self.b_up_prof.setEnabled(True)
            else:
                self.b_up_prof.setEnabled(False)

            # floodgate
            self.init_gui_fg()

    def update_profil(self):
        """
        update zx of profil
        """
        tab = {'x': [], 'z': []}
        where = "gid = '{0}' ".format(self.id_prof_ori)
        feature = self.mdb.select('profiles', where=where,
                                  list_var=['x', 'z', 'abscissa', 'branchnum'])
        tab['x'] = [float(var) for var in feature["x"][0].split()]
        tab['z'] = [float(var) for var in feature["z"][0].split()]

        if len(tab['x']) == 0 or len(tab['z']) == 0:
            self.mgis.add_info("Check if the profile is saved.")
            return

        colonnes = ['id_config', 'id_order', 'x', 'z']
        xz = list(zip(tab['x'], tab['z']))
        values = []
        for order, (x, z) in enumerate(xz):
            values.append([self.id_struct, order, x, z])

        self.mdb.delete('profil_struct',
                        where='id_config = {}'.format(self.id_struct))
        self.mdb.insert_res('profil_struct', values, colonnes)

    def change_met_calc(self, idx):
        if not self.is_loading:
            if (
                    QMessageBox.question(self, "Warning",
                                         "Save current parameters ?",
                                         QMessageBox.Cancel | QMessageBox.Ok)) == QMessageBox.Ok:
                self.save_struct()
        self.txt_name.setFocus()
        self.met_calc = self.cb_met_calc.itemData(
            self.cb_met_calc.currentIndex())
        self.display_fg()
        param = self.param_meth_calc[self.typ_struct][self.met_calc]
        self.wgt_met = param['wgt'](*param['wgt_param'])
        self.sw_input.addWidget(self.wgt_met)
        self.sw_input.setCurrentIndex(1)
        self.sw_input.removeWidget(self.sw_input.widget(0))
        self.display_param_struct()

    def display_param_struct(self):
        sql = "SELECT var, value FROM {0}.struct_param " \
              "WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)
        rows = self.mdb.run_query(sql, fetch=True)
        for param, val in rows:
            if param in self.wgt_met.dico_ctrl.keys():
                ctrls = self.wgt_met.dico_ctrl[param]
                for ctrl in ctrls:
                    if param == 'FORMPIL':
                        val = str(val).replace('.', '_').replace('_0', '')
                    ctrl_set_value(ctrl, val)

        for tab, param in self.wgt_met.dico_tab.items():
            # tab.setRowCount(0)
            t = param['type']
            sql = "SELECT id_elem FROM {0}.struct_elem " \
                  "WHERE id_config = {1} AND type = {2} ORDER BY id_elem".format(
                self.mdb.SCHEMA, self.id_struct, t)
            elems = self.mdb.run_query(sql, fetch=True)

            for r, elem in enumerate(elems):
                # tab.insertRow(r)
                for c, col in enumerate(param['col']):
                    sql = "SELECT value FROM {0}.struct_elem_param WHERE id_config = {1} " \
                          "AND id_elem = {2} and var = '{3}'".format(
                        self.mdb.SCHEMA, self.id_struct,
                        elem[0], col['fld'])
                    row = self.mdb.run_query(sql, fetch=True)
                    if len(row) > 0:
                        val = row[0][0]
                    else:
                        val = ctrl_get_value(col['valdef'])

                    if col['fld'] == 'FORMPIL':
                        val = str(val).replace('.', '_').replace('_0', '')

                    if col['cb']:
                        cb = tab.cellWidget(r, c)
                        ctrl_set_value(cb, val)
                    else:
                        itm = tab.item(r, c)
                        itm.setData(0, val)

            tab.hide()
            tab.resizeColumnsToContents()
            tab.resizeRowsToContents()
            tab.show()

    def accept_page(self):
        # save Info
        if self.save_struct():
            self.clmeth.create_poly_elem(self.id_struct, self.typ_struct)
            active = self.cc_active.isChecked()
            if active:
                self.sav_meth(self.id_struct, self.current_meth, self.wgt_met)
            update_etat_struct(self.mdb)
            self.accept()
            # else:
            #     self.reject_page()

    def save_struct(self):
        self.current_meth = self.cb_met_calc.itemData(
            self.cb_met_calc.currentIndex())
        if self.typ_struct == 'PC':
            verif, msg = self.verif_pc(self.id_struct)
        elif self.typ_struct == 'PA':
            verif, msg = self.verif_pa(self.id_struct)
        elif self.typ_struct == 'DA':
            verif, msg = self.verif_da(self.id_struct)
        elif self.typ_struct == 'BU':
            verif, msg = self.verif_bu(self.id_struct)
        else:
            verif, msg = True, ""

        if verif:
            name = str(self.txt_name.text())
            comm = str(self.txt_comm.toPlainText())
            active = self.cc_active.isChecked()
            if active:
                sql = "SELECT id_prof_ori FROM {0}.struct_config WHERE id = {1}".format(
                    self.mdb.SCHEMA,
                    self.id_struct)
                row = self.mdb.run_query(sql, fetch=True)
                id_profil = row[0][0]
                sql = "UPDATE {0}.struct_config SET active = FALSE WHERE id_prof_ori = {1}".format(
                    self.mdb.SCHEMA,
                    id_profil)
                self.mdb.execute(sql)

            sql = "UPDATE {0}.struct_config SET name = '{2}', method = {3}, active = {4}, comment= '{5}' " \
                  "WHERE id = {1}".format(self.mdb.SCHEMA, self.id_struct, name,
                                          self.current_meth, active, comm)
            self.mdb.execute(sql)

            sql = "DELETE FROM {0}.struct_elem WHERE id_config = {1}".format(
                self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)
            sql = "DELETE FROM {0}.struct_elem_param WHERE id_config = {1}".format(
                self.mdb.SCHEMA, self.id_struct)
            self.mdb.execute(sql)

            for var, ctrls in self.wgt_met.dico_ctrl.items():
                if var == 'FORMPIL':
                    val = float(ctrl_get_value(ctrls[0]).replace('_', '.'))
                else:
                    val = float(ctrl_get_value(ctrls[0]))

                sql = "SELECT * FROM {0}.struct_param WHERE id_config = {1} AND var = '{2}'" \
                    .format(self.mdb.SCHEMA, self.id_struct, var)
                row = self.mdb.run_query(sql, fetch=True)
                if len(row) > 0:
                    sql = "UPDATE {0}.struct_param SET value = {3} WHERE id_config = {1} AND var = '{2}'" \
                        .format(self.mdb.SCHEMA, self.id_struct, var, val)
                    self.mdb.execute(sql)
                else:
                    sql = "INSERT INTO {0}.struct_param (id_config, var, value) VALUES ({1}, '{2}', {3})" \
                        .format(self.mdb.SCHEMA, self.id_struct, var, val)
                    self.mdb.execute(sql)

            for tab, param in self.wgt_met.dico_tab.items():
                type_elem = param['type']
                for r in range(tab.rowCount()):
                    id_elem = eval(param['id'].format(r))
                    sql = "INSERT INTO {0}.struct_elem (id_config, id_elem, type) VALUES ({1}, {2}, {3})" \
                        .format(self.mdb.SCHEMA, self.id_struct, id_elem,
                                type_elem)
                    self.mdb.execute(sql)
                    for c, col in enumerate(param['col']):
                        var = col['fld']
                        if col['cb']:
                            cb = tab.cellWidget(r, c)
                            val = cb.itemData(cb.currentIndex())
                            if var == 'FORMPIL':
                                val = val.replace('_', '.')
                        else:
                            itm = tab.item(r, c)
                            val = itm.data(0)
                        if val is None:
                            val = 'Null'
                        sql = "INSERT INTO {0}.struct_elem_param (id_config, id_elem, var, value) " \
                              "VALUES ({1}, {2}, '{3}', {4})".format(
                            self.mdb.SCHEMA, self.id_struct,
                            id_elem, var, val)
                        self.mdb.execute(sql)

            return True
        else:
            msg_txt = "Erreurs lor de la construction de la structure :"
            for m in msg:
                msg_txt += "\n- {}".format(m)
            QMessageBox.warning(self, 'Error', msg_txt)
            return False

    def reject_page(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Structure")
        self.reject()

    def verif_pc(self, id_struct):
        valid, msg = True, []

        v, m = self.verif_exist_trav()
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_bas_tablier(id_struct)
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_larg_struct(id_struct)
        if not v:
            valid = False
            msg.append(m)

        return valid, msg

    def verif_pa(self, id_struct):
        valid, msg = True, []

        v, m = self.verif_exist_trav()
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_haut_tablier(id_struct)
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_larg_struct(id_struct)
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_z_arche()
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_arche_tab()
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_arche_profil(id_struct)
        if not v:
            valid = False
            msg.append(m)

        return valid, msg

    def verif_da(self, id_struct):
        valid, msg = True, []

        v, m = self.verif_exist_trav()
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_haut_tablier(id_struct)
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_larg_struct(id_struct)
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_radier_tab()
        if not v:
            valid = False
            msg.append(m)

        return valid, msg

    def verif_bu(self, id_struct):
        valid, msg = True, []

        v, m = self.verif_exist_trav()
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_haut_tablier(id_struct)
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_buse_tab()
        if not v:
            valid = False
            msg.append(m)

        v, m = self.verif_buse_intersect()
        if not v:
            valid = False
            msg.append(m)

        return valid, msg

    def verif_exist_trav(self):
        if ctrl_get_value(self.wgt_met.dico_ctrl['NBTRAVE'][0]) < 1.:
            return False, "Aucune travee de saisie"
        else:
            return True, None

    def verif_haut_tablier(self, id_struct):
        sql = "SELECT MIN(z) FROM {0}.profil_struct WHERE id_config = {1}".format(
            self.mdb.SCHEMA, id_struct)
        rows = self.mdb.run_query(sql, fetch=True)
        profil_z_min = rows[0][0]

        cote_tablier = ctrl_get_value(self.wgt_met.dico_ctrl['ZTOPTAB'][0])
        if cote_tablier <= profil_z_min:
            return False, "La cote du tablier est inferieure à la cote minimum du profil"
        else:
            return True, None

    def verif_bas_tablier(self, id_struct):
        sql = "SELECT MIN(z) FROM {0}.profil_struct WHERE id_config = {1}".format(
            self.mdb.SCHEMA, id_struct)
        rows = self.mdb.run_query(sql, fetch=True)
        profil_z_min = rows[0][0]

        cote_bas_tablier = ctrl_get_value(
            self.wgt_met.dico_ctrl['ZTOPTAB'][0]) - ctrl_get_value(
            self.wgt_met.dico_ctrl['EPAITAB'][0])
        if cote_bas_tablier <= profil_z_min:
            return False, "La cote du bas du tablier est inferieure à la cote minimum du profil"
        else:
            return True, None

    def verif_larg_struct(self, id_struct):
        for v, var in enumerate(
                self.wgt_met.dico_tab[self.wgt_met.tab_trav]['col']):
            if var['fld'] == "LARGTRA":
                col_trav = v
                break

        for v, var in enumerate(
                self.wgt_met.dico_tab[self.wgt_met.tab_pile]['col']):
            if var['fld'] == "LARGPIL":
                col_pile = v
                break

        sql = "SELECT MAX(x) FROM {0}.profil_struct WHERE id_config = {1}".format(
            self.mdb.SCHEMA, id_struct)
        rows = self.mdb.run_query(sql, fetch=True)
        profil_x_max = rows[0][0]

        x_fin = ctrl_get_value(self.wgt_met.dico_ctrl['FIRSTWD'][0])
        for r in range(self.wgt_met.tab_trav.rowCount()):
            itm = self.wgt_met.tab_trav.item(r, col_trav)
            x_fin += itm.data(0)
        for r in range(self.wgt_met.tab_pile.rowCount()):
            itm = self.wgt_met.tab_pile.item(r, col_pile)
            x_fin += itm.data(0)

        if x_fin > profil_x_max:
            return False, "La largeur totale de la structure est superieure a la largeur du profil"
        else:
            return True, None

    def verif_z_arche(self):
        arche_err = []
        for r in range(self.wgt_met.tab_trav.rowCount()):
            forme_arche = ctrl_get_value(self.wgt_met.tab_trav.cellWidget(r, 0))
            if forme_arche == 2:
                if self.wgt_met.tab_trav.item(r, 2).data(
                        0) >= self.wgt_met.tab_trav.item(r, 3).data(0):
                    arche_err.append(r + 1)

        if len(arche_err) > 0:
            txt_arche = ""
            for arche in arche_err:
                txt_arche += "{}, ".format(arche)
            return False, "Arche(s) {} : Z haut <= Z bas".format(txt_arche[:-2])
        else:
            return True, None

    def verif_arche_tab(self):
        arche_err = []
        cote_tablier = ctrl_get_value(self.wgt_met.dico_ctrl['ZTOPTAB'][0])
        for r in range(self.wgt_met.tab_trav.rowCount()):
            forme_arche = ctrl_get_value(self.wgt_met.tab_trav.cellWidget(r, 0))
            if forme_arche == 1:
                z_top = self.wgt_met.tab_trav.item(r, 2).data(0) + (
                    self.wgt_met.tab_trav.item(r, 1).data(0) / 2)
            elif forme_arche == 2:
                z_top = self.wgt_met.tab_trav.item(r, 3).data(0)
            if z_top >= cote_tablier:
                arche_err.append(r + 1)

        if len(arche_err) > 0:
            txt_arche = ""
            for arche in arche_err:
                txt_arche += "{}, ".format(arche)
            return False, "Arche(s) {} : Z haut >= Cote du haut du tablier".format(
                txt_arche[:-2])
        else:
            return True, None

    def verif_arche_profil(self, id_struct):
        arche_err = []
        x_tmp = ctrl_get_value(self.wgt_met.dico_ctrl['FIRSTWD'][0])
        nb_arche = ctrl_get_value(self.wgt_met.dico_ctrl['NBTRAVE'][0])

        for r in range(self.wgt_met.tab_trav.rowCount()):
            larg = self.wgt_met.tab_trav.item(r, 1).data(0)
            if r not in [0, nb_arche - 1]:
                forme_arche = ctrl_get_value(
                    self.wgt_met.tab_trav.cellWidget(r, 0))
                if forme_arche == 1:
                    z_top = self.wgt_met.tab_trav.item(r, 2).data(0) + (
                        self.wgt_met.tab_trav.item(r, 1).data(0) / 2)
                elif forme_arche == 2:
                    z_top = self.wgt_met.tab_trav.item(r, 3).data(0)
                sql = "SELECT MAX(z) FROM {0}.profil_struct " \
                      "WHERE id_config = {1} AND x >= {2} AND x <= {3}".format(
                    self.mdb.SCHEMA, id_struct, x_tmp,
                    larg + x_tmp)
                rows = self.mdb.run_query(sql, fetch=True)
                profil_z_max = rows[0][0]
                if profil_z_max >= z_top:
                    arche_err.append(r + 1)
            x_tmp += larg

        if len(arche_err) > 0:
            txt_arche = ""
            for arche in arche_err:
                txt_arche += "{}, ".format(arche)
            return False, "Arche(s) {} : Z haut <= Cote max du profil".format(
                txt_arche[:-2])
        else:
            return True, None

    def verif_radier_tab(self):
        rad_err = []
        cote_tablier = ctrl_get_value(self.wgt_met.dico_ctrl['ZTOPTAB'][0])
        for r in range(self.wgt_met.tab_trav.rowCount()):
            z_top = self.wgt_met.tab_trav.item(r, 0).data(
                0) + self.wgt_met.tab_trav.item(r, 1).data(0)
            if z_top >= cote_tablier:
                rad_err.append(r + 1)

        if len(rad_err) > 0:
            txt_rad = ""
            for rad in rad_err:
                txt_rad += "{}, ".format(rad)
            return False, "Dalot(s) {} : Z haut >= Cote du haut du tablier".format(
                txt_rad[:-2])
        else:
            return True, None

    def verif_buse_tab(self):
        buse_err = []
        cote_tablier = ctrl_get_value(self.wgt_met.dico_ctrl['ZTOPTAB'][0])
        for r in range(self.wgt_met.tab_trav.rowCount()):
            z_top = self.wgt_met.tab_trav.item(r, 1).data(
                0) + self.wgt_met.tab_trav.item(r, 2).data(0)
            if z_top >= cote_tablier:
                buse_err.append(r + 1)

        if len(buse_err) > 0:
            txt_buse = ""
            for buse in buse_err:
                txt_buse += "{}, ".format(buse)
            return False, "Buse(s) {} : Z haut >= Cote du haut du tablier".format(
                txt_buse[:-2])
        else:
            return True, None

    def verif_buse_intersect(self):
        buse_err = []
        for c1 in range(self.wgt_met.tab_trav.rowCount()):
            x_c = self.wgt_met.tab_trav.item(c1, 0).data(0)
            ray = self.wgt_met.tab_trav.item(c1, 2).data(0) / 2
            z_c = self.wgt_met.tab_trav.item(c1, 1).data(0) + ray
            circ1 = Point([x_c, z_c]).buffer(ray)
            for c2 in range(c1 + 1, self.wgt_met.tab_trav.rowCount()):
                x_c = self.wgt_met.tab_trav.item(c2, 0).data(0)
                ray = self.wgt_met.tab_trav.item(c2, 2).data(0) / 2
                z_c = self.wgt_met.tab_trav.item(c2, 1).data(0) + ray
                circ2 = Point([x_c, z_c]).buffer(ray)
                if circ1.intersects(circ2):
                    buse_err.append((c1, c2))

        if len(buse_err) > 0:
            txt_buse = ""
            for buse in buse_err:
                txt_buse += "{}, ".format(buse)
            return False, "Intersection(s) detectee(s) : {}".format(
                txt_buse[:-2])
        else:
            return True, None

    # floodgate
    def init_gui_fg(self):
        """initialisation GUI for floodGate"""

        sql = "SELECT active FROM {0}.struct_fg " \
              "WHERE id_config = {1}".format(self.mdb.SCHEMA, self.id_struct)

        rows = self.mdb.run_query(sql, fetch=True)

        if len(rows) > 0:
            self.fg_active.setChecked(bool(rows[0][0]))
        self.display_fg()

        self.act_active_fg()
        self.fg_active.stateChanged.connect(self.act_active_fg)
        self.b_fg.clicked.connect(self.get_param_fg)

    def act_active_fg(self):
        act_val = bool(self.fg_active.isChecked())
        if act_val:
            self.b_fg.setEnabled(True)
            if self.check_exit_fg():
                sql = "UPDATE {0}.struct_fg SET active = {2}  WHERE id_config = {1} " \
                    .format(self.mdb.SCHEMA, self.id_struct, act_val)
                self.mdb.execute(sql)
            else:
                sql = "INSERT INTO {0}.struct_fg (id_config, id_scen, active, type_fg) VALUES ({1}, {2}, {3}, '{4}')" \
                    .format(self.mdb.SCHEMA, self.id_struct, 0, act_val, 'D')
                self.mdb.execute(sql)
        else:
            self.b_fg.setEnabled(False)
            if self.check_exit_fg():
                sql = "UPDATE {0}.struct_fg SET active = {2}  WHERE id_config = {1} " \
                    .format(self.mdb.SCHEMA, self.id_struct, act_val)
                self.mdb.execute(sql)

    def display_fg(self):
        meth = self.cb_met_calc.itemData(self.cb_met_calc.currentIndex())
        if meth == 4 or meth == 0 or not self.mgis.cond_api:
            self.fg_active.setChecked(False)
            self.fg_active.hide()
            self.b_fg.hide()
        else:
            self.fg_active.show()
            self.b_fg.show()

    def check_exit_fg(self):
        """check if id_config is struct_fg table"""
        if self.id_struct:
            sql = "SELECT * FROM {0}.struct_fg WHERE id_config = {1} " \
                .format(self.mdb.SCHEMA, self.id_struct)
            row = self.mdb.run_query(sql, fetch=True)
            return len(row) > 0
        else:
            return False

    def get_param_fg(self):
        wfg = StructureFgDialog(self.mgis, self.id_struct)
        wfg.exec_()
        del wfg

    def sav_meth(self, id_config, idmethod, ui):
        """
        Compute law
        :param id_config: index of hydraulic structure
        :param idmethod: index of method
        :param ui: gui object
        :return:
        """
        self.meth = ClassLaws(self.mgis)
        if idmethod == 0 or idmethod == 4:  # meth
            list_final = self.meth.bradley(id_config,
                                           self.tbst.dico_meth_calc[idmethod],
                                           ui)
        elif idmethod == 1:  # borda
            list_final = self.meth.borda(id_config,
                                         self.tbst.dico_meth_calc[idmethod], ui)
        elif idmethod == 3:  # orifice
            list_final = self.meth.orifice(id_config,
                                           self.tbst.dico_meth_calc[idmethod],
                                           ui)
        else:
            pass
        self.save_list_final(list_final, id_config,
                             self.tbst.dico_meth_calc[idmethod])
        if ui is not None:
            ui.progress_bar(100)
        self.mgis.add_info(self.meth.msg)

    def save_list_final(self, list_final, id_config, method):
        """
        Save in database the law value
        :param list_final: list of law values
        :param id_config:  index of hydraulic structure
        :param method: mehtod of compute
        :return: nothing
        """
        if not list_final:
            sql = "SELECT name FROM {0}.{1} WHERE id={2}".format(
                self.mdb.SCHEMA, 'struct_config', id_config)

            name = self.mdb.run_query(sql, fetch=True)
            name = name[0][0]

            sql = "UPDATE {0}.{1} SET {2}  WHERE id={3};".format(
                self.mdb.SCHEMA, 'struct_config', 'active=False',
                id_config)
            self.mdb.run_query(sql)

            self.add_info(
                "No values for the law because the coefficients leave application domain of the method.\n"
                "The <<{}>> hydraulic structur is deactivated".format(name))
        else:
            self.save_law_st(method, id_config, list_final)

    def save_law_st(self, method, id_config, list_val):
        """
        Stock law in database
        :param method: mehtod of compute
        :param id_config: index of hydraulic structure
        :param list_val: value list
        :return:
        """
        """ stock law in database"""
        self.mdb.delete('struct_laws',
                        where="id_config = '{}'".format(id_config))
        liste_col = self.mdb.list_columns('struct_laws')
        list_insert = []
        list_val = np.array(list_val)
        for j in self.tbst.dico_law_struct[method].keys():
            for i, val in enumerate(list_val[:, j]):
                list_insert.append([id_config, j, i, val])
        var = ",".join(liste_col)

        sql = ''
        for a in list_insert:
            valeurs = str(tuple(a))
            sql += "INSERT INTO {0}.{1}({2}) VALUES {3};".format(
                self.mdb.SCHEMA,
                'struct_laws',
                var,
                valeurs)
        self.mdb.run_query(sql)
