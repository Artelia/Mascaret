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

from .ClassTableStructure import ClassTableStructure, ctrl_set_value, ctrl_get_value, fill_qcombobox

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import *


class StructureFgDialog(QDialog):
    def __init__(self, mgis, id_struct=None):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure()
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/structures/ui_floodgate.ui'), self)
        self.id_struct = id_struct
        self.unitv = 0
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)
        self.zinc_fg.valueChanged.connect(self.update_min_zinc_fg_max)
        self.cote_max_fg.valueChanged.connect(self.update_min_zinc_fg_max)

        fill_qcombobox(self.cb_dir, [['U', 'top'], ['D', 'bottom']])
        fill_qcombobox(self.cb_var, [['Z', 'Water level'], ['Q', 'Flow rate']])
        fill_qcombobox(self.cb_loc, [['AV', 'Downstream'], ['AM', 'Upstream']])

        #

        fill_qcombobox(self.cb_type_t, [[1, 's'], [60, 'min'], [3600, 'h'], [86400, 'jours']])
        fill_qcombobox(self.cb_type_t_vit, [[1, 'm/s'], [60, 'm/min'], [3600, 'm/h']])

        self.dico_ctrl = {'VELOFG': [self.vel_fg],
                          'TYPE_TIME_VELO': [self.cb_type_t_vit],
                          'ZMAXFG': [self.cote_max_fg],
                          'ZINCRFG': [self.zinc_fg],
                          'DIRFG': [self.cb_dir],
                          'DTREG': [self.pas_temps_fg],
                          'VALREG': [self.val_reg],
                          'TOLREG': [self.tol_reg],
                          'XPCONT': [self.abscisse_reg],
                          'BIEFCONT': [self.bief_controle_fg],
                          'VREG': [self.cb_var],
                          'LOCCONT': [self.cb_loc],
                          'TYPE_TIME': [self.cb_type_t]
                          }
        self.display_fg_struct()
        if self.cb_var.currentText() == 'Flow rate':
            fill_qcombobox(self.cb_loc, [['AV', 'Downstream']])
        self.cb_var.currentIndexChanged['QString'].connect(self.cb_var_chang)
        self.cb_type_t_vit.currentIndexChanged.connect(self.cb_change_unitv)

    def accept_page(self):
        # SAVE BD
        fact_t = float(ctrl_get_value(self.dico_ctrl['TYPE_TIME'][0]))
        fact_t_velo = 1 / float(ctrl_get_value(self.dico_ctrl['TYPE_TIME_VELO'][0]))

        for var, ctrls in self.dico_ctrl.items():
            if var == 'TYPE_TIME':
                continue
            elif var == 'TYPE_TIME_VELO':
                val = int(ctrl_get_value(ctrls[0]))
            elif var == 'DTREG':
                val = float(ctrl_get_value(ctrls[0]))
                val = val * fact_t
            elif var == 'VELOFG':
                val = float(ctrl_get_value(ctrls[0]))
                val = val * fact_t_velo
            elif var == 'LOCCONT' or var == 'DIRFG' or var == 'VREG':
                val = ctrl_get_value(ctrls[0])
            else:
                val = float(ctrl_get_value(ctrls[0]))

            if var == 'LOCCONT' or var == 'DIRFG' or var == 'VREG':
                if var == 'LOCCONT':
                    var = 'xpos'
                elif var == 'VREG':
                    var = 'var_reg'
                elif var == 'DIRFG':
                    var = 'type_fg'
                else:
                    var = None
                sql = "UPDATE {0}.struct_fg SET {2} = '{3}'  WHERE id_config = {1} " \
                    .format(self.mdb.SCHEMA, self.id_struct, var, val)
                self.mdb.execute(sql)
            else:
                sql = "SELECT * FROM {0}.struct_fg_val WHERE id_config = {1} AND  name_var = '{2}' " \
                    .format(self.mdb.SCHEMA, self.id_struct, var)
                row = self.mdb.run_query(sql, fetch=True)
                if len(row) > 0:
                    sql = "UPDATE {0}.struct_fg_val SET value = {3} WHERE id_config = {1} AND  name_var = '{2}'" \
                        .format(self.mdb.SCHEMA, self.id_struct, var, val)
                    self.mdb.execute(sql)
                else:

                    sql = "INSERT INTO {0}.struct_fg_val (id_config, id_scen, id_order, name_var, value)" \
                          " VALUES ({1}, {2}, {3},'{4}',{5})" \
                        .format(self.mdb.SCHEMA, self.id_struct, 0, 0, var, val)
                    self.mdb.execute(sql)

        self.accept()

    def cb_change_unitv(self, evt):
        if evt == 0:
            if self.unitv == 1:
                val = float(ctrl_get_value(self.vel_fg))
                val = val / 60
                ctrl_set_value(self.vel_fg, val)
            elif self.unitv == 2:
                val = float(ctrl_get_value(self.vel_fg))
                val = val / 3600
                ctrl_set_value(self.vel_fg, val)
        elif evt == 1:
            if self.unitv == 0:
                val = float(ctrl_get_value(self.vel_fg))
                val = val * 60.
                ctrl_set_value(self.vel_fg, val)
            elif self.unitv == 2:
                val = float(ctrl_get_value(self.vel_fg))
                val = val / 60
                ctrl_set_value(self.vel_fg, val)
        elif evt == 2:
            if self.unitv == 0:
                val = float(ctrl_get_value(self.vel_fg))
                val = val * 3600.
                ctrl_set_value(self.vel_fg, val)
            elif self.unitv == 1:
                val = float(ctrl_get_value(self.vel_fg))
                val = val * 60.
                ctrl_set_value(self.vel_fg, val)
        else:
            pass

        self.unitv = evt

    def reject_page(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of FloodGate parameters")
        self.reject()

    def update_min_zinc_fg_max(self):
        self.zinc_fg.setMaximum(self.cote_max_fg.value())

    def display_fg_struct(self):
        sql = "SELECT  name_var, value FROM {0}.struct_fg_val " \
              "WHERE id_config = {1} ".format(self.mdb.SCHEMA, self.id_struct)
        rows = self.mdb.run_query(sql, fetch=True)
        if len(rows) > 0:
            dico = {}
            for param, val in rows:
                dico[param] = val
            self.dico_ctrl['TYPE_TIME_VELO'][0].blockSignals(True)
            for param in dico.keys():
                if param in self.dico_ctrl.keys():
                    ctrls = self.dico_ctrl[param]
                    if param == 'VELOFG':
                        if 'TYPE_TIME_VELO' in dico.keys():
                            val = dico[param] * dico['TYPE_TIME_VELO']
                        else:
                            val = dico[param]
                    else:
                        val = dico[param]
                    for ctrl in ctrls:
                        ctrl_set_value(ctrl, val)
            if 'TYPE_TIME_VELO' in dico.keys():
                if dico['TYPE_TIME_VELO'] == 3600:
                    self.unitv = 2
                elif dico['TYPE_TIME_VELO'] == 60:
                    self.unitv = 1
                else:
                    self.unitv = 0
            else:
                self.unitv = 0

            self.dico_ctrl['TYPE_TIME_VELO'][0].blockSignals(False)
        # for param, val in rows:
        #     if param in self.dico_ctrl.keys():
        #         ctrls = self.dico_ctrl[param]
        #         for ctrl in ctrls:
        #             ctrl_set_value(ctrl, val)

        rows = self.mdb.select('struct_fg', where='id_config = {0}'.format(self.id_struct),
                               list_var=['type_fg', 'xpos', 'var_reg'])
        for param, val in rows.items():
            param = self.tbst.dico_vardb_to_var_fg[param]
            if param in self.dico_ctrl.keys():
                ctrls = self.dico_ctrl[param]
                for ctrl in ctrls:
                    ctrl_set_value(ctrl, val[0])

    def cb_var_chang(self, text):
        if text.lower() == 'Water level':
            fill_qcombobox(self.cb_loc, [['AV', 'Downstream'], ['AM', 'Upstream']])
        elif text.lower() == 'Flow rate':
            fill_qcombobox(self.cb_loc, [['AV', 'Downstream']])
