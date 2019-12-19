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
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)
        self.zinc_fg.valueChanged.connect(self.update_min_zinc_fg_max)
        self.cote_max_fg.valueChanged.connect(self.update_min_zinc_fg_max)


        fill_qcombobox(self.cb_dir, [['U', 'haut'], ['D', 'bas']])
        fill_qcombobox(self.cb_var, [['Z', 'Cote'], ['Q', 'Debit']])
        fill_qcombobox(self.cb_loc, [['AV', 'Aval'], ['AM', 'Amont']])
        fill_qcombobox(self.cb_type_t, [[1, 's'],[60, 'min'],[3600, 'h'],[86400, 'jours']])


        self.dico_ctrl = {'VELOFG': [self.vel_fg],
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
                          'TYPE_TIME' :[self.cb_type_t]
                          }

    def accept_page(self):
        # SAVE BD
        self.accept()

    def reject_page(self):
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of FloodGate parameters")
        self.reject()

    def update_min_zinc_fg_max(self):
        self.zinc_fg.setMaximum(self.cote_max_fg.value())
