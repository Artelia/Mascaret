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
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *


def ctrl_set_value(ctrl, val, cc_is_checked=False):
    """
    Set the value of a Qt control widget.
    :param ctrl (QWidget): The control widget
    :param val (any): The value to set
    :param cc_is_checked (bool): If True, use isChecked for QCheckBox
    :return: None
    """
    if ctrl.metaObject().className() == "QSpinBox":
        ctrl.setValue(int(val))
    elif ctrl.metaObject().className() == "QDoubleSpinBox":
        ctrl.setValue(val)
    elif ctrl.metaObject().className() == "QComboBox":
        ctrl.setCurrentIndex(ctrl.findData(val))
        # ctrl.setCurrentIndex(ctrl.findData(int(val)))
    elif ctrl.metaObject().className() == "QCheckBox":
        if cc_is_checked:
            ctrl.setChecked(val)
        else:
            ctrl.setCheckState(Qt.CheckState(int(val)))
    elif ctrl.metaObject().className() == "QButtonGroup":
        ctrl.button(int(val)).click()


def ctrl_get_value(ctrl, cc_is_checked=False):
    """
    Get the value from a Qt control widget.
    :param ctrl (QWidget): The control widget
    :param cc_is_checked (bool): If True, use isChecked for QCheckBox
    :return: val (any): The value of the control
    """
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
        if cc_is_checked:
            val = ctrl.isChecked()
        else:
            val = int(ctrl.checkState())
    elif ctrl.metaObject().className() == "QButtonGroup":
        val = ctrl.checkedId()
    return val


def fill_qcombobox(cb, lst, val_def=None, icn=None, size=None):
    """
    Fill a QComboBox with items.
    :param cb (QComboBox): The combo box to fill
    :param lst (list): List of [data, display] pairs
    :param val_def (any): Default value to select
    :param icn (str): Icon path format string
    :param size (int): Icon size
    :return: None
    """
    cb.blockSignals(True)
    cb.clear()

    if val_def is not None:
        if lst[0][0] == val_def:
            cb.blockSignals(False)
    else:
        cb.blockSignals(False)
    if size:
        cb.setIconSize(QSize(size, size))
    for elem in lst:
        if icn:
            cb.addItem(QIcon(icn.format(elem[0])), elem[1], elem[0])
        else:
            cb.addItem(elem[1], elem[0])

    if val_def is not None:
        if lst[0][0] != val_def:
            cb.blockSignals(False)
            cb.setCurrentIndex(cb.findData(val_def))
