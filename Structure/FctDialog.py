# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Dialog function for Mascaret for QGIS
Date                 : Avril,2025
copyright            : (C) 2025 by Artelia
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
from qgis.PyQt.QtGui import QIcon


def ctrl_set_value(ctrl, val):
    if ctrl.metaObject().className() == "QSpinBox":
        ctrl.setValue(int(val))
    elif ctrl.metaObject().className() == "QDoubleSpinBox":
        ctrl.setValue(val)
    elif ctrl.metaObject().className() == "QComboBox":
        ctrl.setCurrentIndex(ctrl.findData(val))
        # ctrl.setCurrentIndex(ctrl.findData(int(val)))
    elif ctrl.metaObject().className() == "QCheckBox":
        ctrl.setCheckState(Qt.CheckState(int(val)))
    elif ctrl.metaObject().className() == "QButtonGroup":
        ctrl.button(int(val)).click()


def ctrl_get_value(ctrl):
    val = None
    if ctrl.metaObject().className() == "QLineEdit":
        val = ctrl.text()
    elif ctrl.metaObject().className() in ("QSpinBox", "QDoubleSpinBox"):
        val = ctrl.value()
    elif ctrl.metaObject().className() == "QDateTimeEdit":
        val = ctrl.dateTime().toString("yyyy-MM-dd HH:mm:ss")
    elif ctrl.metaObject().className() == "QComboBox":
        val = ctrl.itemData(ctrl.currentIndex())
        # val = int(ctrl.itemData(ctrl.currentIndex()))
    elif ctrl.metaObject().className() == "QCheckBox":
        val = int(ctrl.checkState())
    elif ctrl.metaObject().className() == "QButtonGroup":
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