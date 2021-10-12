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

try:
    from qgis.PyQt.QtCore import *
    from qgis.PyQt.QtWidgets import *
    from qgis.PyQt.uic import *

    #
    if int(qVersion()[0]) < 5:  # qt4
        from qgis.PyQt.QtGui import *
    else:  # qt5
        from qgis.PyQt.QtGui import QIcon
        from qgis.PyQt.QtWidgets import *
except:
    pass


class ClassTableStructure:
    def __init__(self):
        self.dico_meth_calc = {0: 'Bradley 72',
                               1: 'Borda',
                               2: 'Weir law',
                               3: 'Orifice law',
                               4: 'Bradley 78'}

        self.dico_meth_draw = {0: 'Method 1',
                               1: 'Method 2',
                               2: 'Method 3',
                               3: 'Method 4',
                               4: 'Method 5'}

        self.dico_struc_typ = {'PC': {'name': 'Beam Bridge',
                                      'param': ['FIRSTWD', 'ZTOPTAB', 'EPAITAB',
                                                'BIAIOUV', 'BIAICUL', 'BIAIPIL',
                                                'FORMCUL', 'ORIENTM', 'PENTTAL',
                                                'FORMPIL', 'METTEST', 'LARGPIL',
                                                'LONGPIL', 'PASH', 'MINH',
                                                'PASQ',
                                                'MINQ', 'MAXQ', 'NBTRAVE',
                                                'METBR72', 'METBR78'],
                                      'meth_calc': [0, 4, 1, 3],
                                      'meth_draw': [[0], [0], [0], [0]]
                                      },
                               'PA': {'name': 'Arch Bridge',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV',
                                                'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [1, 3],
                                      'meth_draw': [[0], [0]]
                                      },
                               'DA': {'name': 'Rectangular Culvert',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV',
                                                'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [1, 3],
                                      'meth_draw': [[0], [0]]
                                      },
                               'BU': {'name': 'Circular Culvert',
                                      'meth_calc': [1, 3],
                                      'meth_draw': [[0], [0]]
                                      }
                               }

        self.dico_typ_elem = {0: 'Spans',
                              1: 'Columns',
                              2: 'Arch'}

    # self.dico_elem_prm = {'LARGTRA': {'name': 'Largeur de la travee', 'unit':
    #                                                                      'm'},
    #                    'FORMPIL': {'name': 'Forme des piles', 'unit': None},
    #                    'LARGPIL': {'name': 'Largeur des piles', 'unit': 'm'},
    #                    'LONGPIL': {'name': 'Longueur des piles', 'unit': 'm'},
    #                    'FORMARC': {'name': 'Forme de l''arche', 'unit': None},
    #                    'ZMINARC': {'name': 'Z bas de l''arche', 'unit': 'm'},
    #                    'ZMAXARC': {'name': 'Z haut de l''arche', 'unit': 'm'},
    #                    'COTERAD': {'name': 'Cote du radier', 'unit': 'm'},
    #                    'HAUTDAL': {'name': 'Hauteur du dalot', 'unit': 'm'},
    #                    'ABSBUSE': {'name': 'Abscisse du centre de la buse',
    #                                                           'unit': 'm'}}

        self.dico_culee_pente_talus = {0: '1/1', 1: '1.5/1', 2: '2/1'}
        self.dico_forme_arche = {1: 'Circular', 2: 'Ellipsoidal'}

        self.dico_law_struct = {
            'Bradley 78':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'},
            'Bradley 72':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'},
            'Borda':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'},
            'Orifice law':
                {0: 'flowrate', 1: 'z_downstream', 2: 'z_upstream'}
        }

        # floodgate
        self.dico_fg = {
            'VELOFG': {'name': 'Temps de fonctionnement', 'unit': 'm/s'},
            'ZMAXFG': {'name': 'Z bute de la vanne', 'unit': 'm'},
            'ZINCRFG': {'name': 'Z d''increment de mouvement', 'unit': 'm'},
            'DIRFG': {'name': 'Sens de fermeture', 'unit': None},
            'DTREG': {'name': 'Pas de temps de régulation', 'unit': 's'},
            'VREG': {'name': 'variable de regulation', 'unit': None},
            'VALREG': {'name': 'Valeur de variable de regulation',
                       'unit': None},
            'TOLREG': {'name': 'Tolerence de regulation', 'unit': None},
            'XPCONT': {'name': 'Abscisse du point de conrole', 'unit': 'm'},
            'BIEFCONT': {'name': 'Bief du point de controle', 'unit': 'm'},
            'LOCCONT': {'name': 'Localisation du point de controle',
                        'unit': 'm'}
            }
        self.dico_vardb_to_var_fg = {'type_fg': 'DIRFG', 'xpos': 'LOCCONT',
                                     'var_reg': 'VREG'}

        self.dico_weirs_mob = {'ZBAS': {'name': 'cotes basse', 'unit': 'm'},
                               'ZHAUT': {'name': 'cotes haute', 'unit': 'm'},
                               'ZREG': {'name': 'cotes d\'exploitation',
                                        'unit': 'm'},
                               'VDESC': {'name': 'vitesses d\’abaissement',
                                         'unit': 'm/s'},
                               'VMONT': {'name': 'vitesses de remontée',
                                         'unit': 'm/s'},
                               'TIME': {'name': 'temps', 'unit': 's'},
                               'ZVAR': {'name': 'cotes de crêtes', 'unit': 'm'}}


def ctrl_set_value(ctrl, val):
    if ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
        ctrl.setValue(val)
    elif ctrl.metaObject().className() == 'QComboBox':
        ctrl.setCurrentIndex(ctrl.findData(val))
        # ctrl.setCurrentIndex(ctrl.findData(int(val)))
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
        val = ctrl.itemData(ctrl.currentIndex())
        # val = int(ctrl.itemData(ctrl.currentIndex()))
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


def update_etat_struct(mdb):
    sql = "SELECT gid FROM {0}.profiles ".format(mdb.SCHEMA)

    rows = mdb.run_query(sql, fetch=True)

    try:
        lst_prof = [var[0] for var in rows]
    except IndexError or TypeError:
        return
    sql = "SELECT DISTINCT id_prof_ori FROM {0}.struct_config " \
          "WHERE active ".format(mdb.SCHEMA)
    rows = mdb.run_query(sql, fetch=True)

    try:
        prof_act = [var[0] for var in rows]
    except IndexError or TypeError:
        prof_act = []

    sql = "SELECT DISTINCT id_prof_ori FROM {0}.struct_config " \
          "WHERE active=false".format(mdb.SCHEMA)
    rows = mdb.run_query(sql, fetch=True)
    try:
        prof_d = [var[0] for var in rows]
    except IndexError or TypeError:
        prof_act = []

    list_udpate = []

    for gid in lst_prof:
        if gid in prof_act:
            list_udpate.append((gid, 2))
        elif gid in prof_d:
            list_udpate.append((gid, 1))
        else:
            list_udpate.append((gid, 0))

    sql = "UPDATE {0}.profiles SET struct= val.state " \
          "FROM ( values {1}) as val(id,state) " \
          "WHERE gid = val.id".format(mdb.SCHEMA,
                                      ','.join(map(str, list_udpate)))

    mdb.run_query(sql)
