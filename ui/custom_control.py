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
import numpy as np
import re

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *

from qgis.PyQt.QtGui import QValidator
from qgis.PyQt.QtWidgets import QMessageBox, QDoubleSpinBox


# *******************************************************************************
#   Class  warningBox
# *******************************************************************************
class ClassWarningBox:
    """TODO add all select box """

    def __init__(self):
        pass

    def yes_no_q(self, msg, title=''):
        d = QMessageBox()
        d.setWindowTitle(title)
        d.addButton(QMessageBox.Yes)
        d.addButton(QMessageBox.No)
        d.setDefaultButton(QMessageBox.No)
        d.setText(msg)
        ret = d.exec_()

        if ret == QMessageBox.Yes:
            return True
        else:
            return False

    def info(self, msg, title=''):
        QMessageBox.warning(None, title, msg)


# *******************************************************************************
#   Class  ScientificDoubleSpinBox
# *******************************************************************************
_float_re = re.compile(r'(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)')


def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


class FloatValidator(QValidator):
    def validate(self, string, position):
        if valid_float_string(string):
            return QValidator.Acceptable
        if string == "" or string[position - 1] in 'e.-+':
            return QValidator.Intermediate
        return QValidator.Invalid

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
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string
    # *******************************************************************************


def datetime2QDateTime(date):
    return QDateTime(date.year, date.month, date.day,
                     date.hour, date.minute, date.second)
