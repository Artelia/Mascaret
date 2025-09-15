# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          :
                      Class_warningBox
                      Class spinbox inspired by
                      https://www.jdreaver.com/posts/2014-07-28-scientific-notation-spin-box-pyside.html
Date                 : Janvier,2018
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
import re

import numpy as np
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QValidator
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtWidgets import QMessageBox, QDoubleSpinBox
from qgis.PyQt.uic import *

QT_VERSION = [int(v) for v in qVersion().split('.')][0]
# *******************************************************************************
#   Class  warningBox
# *******************************************************************************
class ClassWarningBox:
    """TODO add all select box"""

    def __init__(self):
        pass

    def yes_no_q(self, msg, title=""):
        d = QMessageBox()
        try:
            StandardButton = QMessageBox.StandardButton
        except  AttributeError:
            StandardButton = QMessageBox
        d.setWindowTitle(title)
        d.addButton(StandardButton.Yes)
        d.addButton(StandardButton.No)
        d.setDefaultButton(StandardButton.No)
        d.setText(msg)
        if QT_VERSION > 5:
            ret = d.exec()  # PyQt6
        else:
            ret = d.exec_()  # PyQt5

        if ret == StandardButton.Yes:
            return True
        else:
            return False

    def ok_cancel_q(self, wgt,  msg, title=""):
        if QT_VERSION > 5:
            StandardButton = QMessageBox.StandardButton
        else:
            StandardButton = QMessageBox

        ret = QMessageBox.question(wgt, title, msg,
            StandardButton.Cancel | StandardButton.Ok,)

        if ret == StandardButton.Ok:
            return True
        else:
            return False

    def info(self, msg, title=""):
        QMessageBox.warning(None, title, msg)


# *******************************************************************************
#   Class  ScientificDoubleSpinBox
# *******************************************************************************
_float_re = re.compile(r"(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)")


def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


class FloatValidator(QValidator):
    def validate(self, string, position):
        if QT_VERSION > 5:
            q_valid = QValidator.State
        else:
            q_valid = QValidator
        if valid_float_string(string):
            return q_valid.Acceptable
        if string == "" or string[position - 1] in "e.-+":
            return q_valid.Intermediate
        return q_valid.Invalid

    def fixup(self, text):
        match = _float_re.search(text)
        return match.groups()[0] if match else ""


class ScientificDoubleSpinBox(QDoubleSpinBox):
    """
    Class QDoubleSpinBox with scientific format
    """

    def __init__(self, *args, **kwargs):
        super(ScientificDoubleSpinBox, self).__init__(*args, **kwargs)
        self.setMinimum(-np.inf)
        self.setMaximum(np.inf)
        self.validator = FloatValidator()
        self.setDecimals(1000)

    def validate(self, text, position):
        return self.validator.validate(text, position), text, position

    def fixup(self, text):
        return self.validator.fixup(text)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        return format_float(value)

    def stepBy(self, steps):
        text = self.cleanText()
        groups = _float_re.search(text).groups()
        decimal = float(groups[1])
        decimal += steps
        new_string = "{:g}".format(decimal) + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)


def format_float(value):
    """Modified form of the 'g' format specifier."""
    string = "{:g}".format(value).replace("e+", "e")
    string = re.sub(r"e(-?)0*(\d+)", r"e\1\2", string)
    return string
    # *******************************************************************************


def datetime2QDateTime(date):
    return QDateTime(date.year, date.month, date.day, date.hour, date.minute, date.second)

# *******************************************************************************
# compatible with PyQt5/6
# *******************************************************************************

def _qt_is_checked( item, check_level="any"):
    """
    Utility to check the status of an item, compatible with PyQt5/6
    check_level: "any" (> 0), "full" (== 2), "partial_or_full" (> 1)
    """

    # QTreeWidgetItem ou QTableWidgetItem
    try:
        # Essaye avec argument colonne
        state = item.checkState(0)
    except TypeError:
        # Sinon, essaye sans argument (QStandardItem)
        state = item.checkState()


    try:
        # PyQt6
        if check_level == "any":
            return state != Qt.CheckState.Unchecked
        elif check_level == "full":
            return state == Qt.CheckState.Checked
        elif check_level == "partial_or_full":
            return state in [Qt.CheckState.PartiallyChecked, Qt.CheckState.Checked]
    except AttributeError:
        # PyQt5
        if check_level == "any":
            return int(state) > 0
        elif check_level == "full":
            return int(state) == 2
        elif check_level == "partial_or_full":
            return int(state) > 1

    return False
