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

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QIcon
    from qgis.PyQt.QtWidgets import *


class ClassTableStructure:
    def __init__(self):
        self.structure_default()

    def structure_default(self):
        self.dico_meth_calc = {0: 'Bradley 72',
                               1: 'Borda',
                               2: 'Loi de seuil',
                               3: 'Loi d''orifice',
                               4: 'Bradley 78'}

        self.dico_meth_draw = {0: 'Method 1',
                               1: 'Method 2',
                               2: 'Method 3',
                               3: 'Method 4',
                               4: 'Method 5'}

        self.dico_struc_typ = {'PC': {'name': 'Pont cadre',
                                      'param': ['FIRSTWD', 'ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'BIAIPIL',
                                                'FORMCUL', 'ORIENTM', 'PENTTAL', 'FORMPIL', 'METTEST', 'LARGPIL',
                                                'LONGPIL', 'PASH', 'MINH', 'PASQ',
                                                'MINQ', 'MAXQ', 'NBTRAVE', 'METBR72', 'METBR78'],
                                      'meth_calc': [0, 4],
                                      'meth_draw': [[0], [0]]
                                      },
                               'PA': {'name': 'Pont arche',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [1]
                                      },
                               'DA': {'name': 'Dalot',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [2, 3]
                                      },
                               'BU': {'name': 'Buse',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [1]
                                      }
                               }

        self.dico_struc_prm = {'FIRSTWD': {'name': 'Abscisse du pied de culée RG', 'unit': 'm'},
                               'ZTOPTAB': {'name': 'Cote du haut du tablier du pont', 'unit': 'm'},
                               'EPAITAB': {'name': 'Epaisseur du tablier', 'unit': 'm'},
                               'BIAIOUV': {'name': 'Biais de l''ouvrage', 'unit': '°'},
                               'BIAICUL': {'name': 'Biais des culées par rapport à l''axe du pont', 'unit': 'Y/N'},
                               'BIAIPIL': {'name': 'Biais de la pile par rapport à l''axe du pont', 'unit': 'Y/N'},
                               'FORMCUL': {'name': 'Forme des culées', 'unit': None},
                               'FORMPIL': {'name': 'Forme des piles', 'unit': None},
                               'LARGPIL': {'name': 'Largeur des piles', 'unit': 'm'},
                               'LONGPIL': {'name': 'Longueur des piles', 'unit': 'm'},
                               'ORIENTM': {'name': 'Orientation des murs en aile', 'unit': '°'},
                               'PENTTAL': {'name': 'Pente de talus des culées', 'unit': None},
                               'PASH': {'name': 'Discrétisation de la hauteur pour le calcul de la loi', 'unit': 'm'},
                               'MINH': {'name': 'Hauteur d\'eau minimum pour le calcul de la loi', 'unit': 'm'},
                               'MAXH': {'name': 'Hauteur d\'eau maximum pour le calcul de la loi', 'unit': 'm'},#MDU
                               'PASQ': {'name': 'Discrétisation du débit pour le calcul de la loi', 'unit': ''},
                               'MINQ': {'name': 'Débit minimum pour le calcul de la loi', 'unit': ''},
                               'MAXQ': {'name': 'Débit maximum pour le calcul de la loi', 'unit': ''},
                               'NBTRAVE': {'name': 'Nombre de travées', 'unit': None},
                               "TOTALOUV": {'name': 'Largeur ouverture de travées', 'unit': 'm'},
                               # "TOTALW": {'name': 'Largeur du pont', 'unit': 'm'},
                               'COEFDEB': {'name': 'Coeficient de debitance', 'unit': ''} #MDU
                               }

        self.dico_typ_elem = {0: 'Travee',
                              1: 'Pile',
                              2: 'Arche'}

        self.dico_elem_prm = {'LARGTRA': {'name': 'Largeur de la travee', 'unit': 'm'},
                              'FORMPIL': {'name': 'Forme des piles', 'unit': None},
                              'LARGPIL': {'name': 'Largeur des piles', 'unit': 'm'},
                              'LONGPIL': {'name': 'Longueur des piles', 'unit': 'm'}
                              }

        self.dico_culee_pente_talus = {0: '1/1', 1: '1.5/1', 2: '2/1'}
        self.dico_law_struct = {
            'Bradley 78':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'},
            'Bradley 72':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'},
            'Borda':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'},
            'Loi d''orifice':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'}
        }


def ctrl_set_value(ctrl, val):
    if ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
        ctrl.setValue(val)
    elif ctrl.metaObject().className() == 'QComboBox':
        ctrl.setCurrentIndex(ctrl.findData(int(val)))
    elif ctrl.metaObject().className() == 'QCheckBox':
        ctrl.setCheckState(Qt.CheckState(int(val)))
    elif ctrl.metaObject().className() == 'QButtonGroup':
        ctrl.button(int(val)).click()


def ctrl_get_value(ctrl):
    val = None
    if ctrl.metaObject().className() == 'QLineEdit':
        val = ctrl.text()
    elif ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
        val = ctrl.value()
    elif ctrl.metaObject().className() == 'QDateTimeEdit':
        val = ctrl.dateTime().toString('yyyy-MM-dd HH:mm:ss')
    elif ctrl.metaObject().className() == 'QComboBox':
        val = int(ctrl.itemData(ctrl.currentIndex()))
    elif ctrl.metaObject().className() == 'QCheckBox':
        val = int(ctrl.checkState())
    elif ctrl.metaObject().className() == 'QButtonGroup':
        val = ctrl.checkedId()
    return val


def fill_qcombobox(cb, lst, val_def=None, icn=None):
    cb.blockSignals(True)
    cb.clear()

    if val_def is not None:
        if lst[0][0] == val_def:
            cb.blockSignals(False)
    else:
        cb.blockSignals(False)

    for elem in lst:
        if icn:
            cb.addItem(QIcon(icn.format(elem[0])), elem[1], elem[0])
        else:
            cb.addItem(elem[1], elem[0])

    if val_def is not None:
        if lst[0][0] != val_def:
            cb.blockSignals(False)
            cb.setCurrentIndex(cb.findData(val_def))
