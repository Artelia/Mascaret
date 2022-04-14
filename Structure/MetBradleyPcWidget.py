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

from .ClassTableStructure import ClassTableStructure, ctrl_get_value, \
    fill_qcombobox

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import *


class MetBradleyPcWidget(QWidget):
    def __init__(self, mgis, met=None, id_struct=None):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure()
        self.ui = loadUi(os.path.join(self.mgis.masplugPath,
                                      'ui/structures/ui_bradley_pc.ui'), self)
        self.id_struct = id_struct

        self.completed = 0
        self.progress = self.ui.progressBar
        self.progress.setValue(0)

        self.dico_pile = ['1', '2', '3', '4', '5_1', '5_2', '6', '7', '8']

        self.frm_orient_mur.hide()
        self.frm_pente_tal.hide()

        self.gb_form_cul = QButtonGroup()
        self.gb_form_cul.addButton(self.rb_form_cul0, 0)
        self.rb_form_cul0.setIcon(QIcon(os.path.join(self.mgis.masplugPath,
                                                     'Structure/images/culees/culee1.png')))
        self.gb_form_cul.addButton(self.rb_form_cul1, 1)
        self.rb_form_cul1.setIcon(QIcon(os.path.join(self.mgis.masplugPath,
                                                     'Structure/images/culees/culee2.png')))
        self.gb_form_cul.addButton(self.rb_form_cul2, 2)
        self.rb_form_cul2.setIcon(QIcon(os.path.join(self.mgis.masplugPath,
                                                     'Structure/images/culees/culee3.png')))

        self.sb_nb_trav.valueChanged.connect(self.change_ntrav)
        self.cb_form_pil.currentIndexChanged.connect(self.update_piles)
        self.dsb_larg_pil.valueChanged.connect(self.update_piles)
        self.dsb_long_pil.valueChanged.connect(self.update_piles)
        self.dsb_h_pas.valueChanged.connect(self.update_min_h_max)
        self.dsb_h_min.valueChanged.connect(self.update_min_h_max)
        self.dsb_q_pas.valueChanged.connect(self.update_min_q_max)
        self.dsb_q_min.valueChanged.connect(self.update_min_q_max)
        self.tab_trav.itemChanged.connect(self.verif_larg_trav)

        if met == '72':
            self.gb_form_cul.buttonClicked[int].connect(self.change_opt_culee)

        fill_qcombobox(self.cb_form_pil,
                       [[f, 'Forme {}'.format(f[0])] for f in self.dico_pile],
                       icn=os.path.join(self.mgis.masplugPath,
                                        'Structure/images/piles/pile{}.png'))
        fill_qcombobox(self.cb_orient_mur,
                       [[30, '30°'], [45, '45°'], [60, '60°']])
        fill_qcombobox(self.cb_pente_tal,
                       [[0, '1/1'], [1, '1.5/1'], [2, '2/1']])

        self.dico_ctrl = {'FIRSTWD': [self.dsb_abs_cul_rg],
                          'ZTOPTAB': [self.dsb_cote_tab],
                          'EPAITAB': [self.dsb_epai_tab],
                          'BIAIOUV': [self.dsb_biai_ouv],
                          'BIAICUL': [self.cc_biai_cul],
                          'BIAIPIL': [self.cc_biai_pil],
                          'FORMCUL': [self.gb_form_cul],
                          'ORIENTM': [self.cb_orient_mur],
                          'PENTTAL': [self.cb_pente_tal],
                          'FORMPIL': [self.cb_form_pil],
                          'LARGPIL': [self.dsb_larg_pil],
                          'LONGPIL': [self.dsb_long_pil],
                          'PASH': [self.dsb_h_pas],
                          'MINH': [self.dsb_h_min],
                          'MAXH': [self.dsb_h_max],
                          'PASQ': [self.dsb_q_pas],
                          'MINQ': [self.dsb_q_min],
                          'MAXQ': [self.dsb_q_max],
                          'NBTRAVE': [self.sb_nb_trav],
                          'COEFDS': [self.dsb_ds],
                          'COEFDO': [self.dsb_do]
                          }

        self.dico_tab = {self.tab_trav: {'type': 0,
                                         'id': '({}*2) + 1',
                                         'col': [{'fld': 'LARGTRA', 'cb': None,
                                                  'valdef': 1.}]},
                         self.tab_pile: {'type': 1,
                                         'id': '({}*2) + 2',
                                         'col': [{'fld': 'FORMPIL',
                                                  'cb': [[f, 'Forme {}'.format(
                                                      f[0])] for f in
                                                         self.dico_pile],
                                                  'valdef': self.cb_form_pil},
                                                 {'fld': 'LARGPIL', 'cb': None,
                                                  'valdef': self.dsb_larg_pil},
                                                 {'fld': 'LONGPIL', 'cb': None,
                                                  'valdef': self.dsb_long_pil}]}
                         }

    def change_ntrav(self, nb_trav):
        nb_pile = max(0, nb_trav - 1)
        nrow_trav = self.tab_trav.rowCount()
        nrow_pile = self.tab_pile.rowCount()
        if nb_trav < nrow_trav:
            self.tab_trav.setRowCount(nb_trav)
        else:
            for t in range(nrow_trav, nb_trav):
                self.insert_elem(self.tab_trav, t)
        if nb_pile < nrow_pile:
            self.tab_pile.setRowCount(nb_pile)
        else:
            for p in range(nrow_pile, nb_pile):
                self.insert_elem(self.tab_pile, p)

    def change_opt_culee(self, idx):
        if idx == 0:
            self.frm_orient_mur.hide()
            self.frm_pente_tal.hide()
        elif idx == 1:
            self.frm_orient_mur.show()
            self.frm_pente_tal.hide()
        elif idx == 2:
            self.frm_orient_mur.hide()
            self.frm_pente_tal.show()

    def insert_elem(self, tab, row):
        tab.insertRow(row)
        for c, col in enumerate(self.dico_tab[tab]['col']):
            if isinstance(col['valdef'], int) or isinstance(col['valdef'],
                                                            float):
                val = col['valdef']
            else:
                val = ctrl_get_value(col['valdef'])

            if col['cb']:
                cb = QComboBox()
                fill_qcombobox(cb, col['cb'], val_def=val)
                tab.setCellWidget(row, c, cb)
            else:
                itm = QTableWidgetItem()
                itm.setData(0, val)
                tab.setItem(row, c, itm)

    def update_piles(self):
        for row in range(self.tab_pile.rowCount()):
            self.tab_pile.cellWidget(row, 0).setCurrentIndex(
                self.cb_form_pil.currentIndex())
            self.tab_pile.item(row, 1).setData(0, self.dsb_larg_pil.value())
            self.tab_pile.item(row, 2).setData(0, self.dsb_long_pil.value())

    def update_min_h_max(self):
        self.dsb_h_max.setMinimum(
            self.dsb_h_min.value() + self.dsb_h_pas.value())

    def update_min_q_max(self):
        self.dsb_q_max.setMinimum(
            self.dsb_q_min.value() + self.dsb_q_pas.value())

    def verif_larg_trav(self, itm):
        if itm.data(0) <= 0.:
            itm.setData(0, 1.)

    def progress_bar(self, val):
        self.completed += val
        if self.completed > 100:
            self.completed = 100
        self.progress.setValue(round(self.completed))
