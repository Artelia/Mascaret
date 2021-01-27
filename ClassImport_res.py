# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 :  Mascaret
Description          : Mascaret tools for QGIS
Date                 : Juin 2020

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
import datetime

from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ui.custom_control import ClassWarningBox

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *


class ClassImportRes(QDialog):
    def __init__(self, clmas=None):
        QDialog.__init__(self)
        self.clmas = clmas
        self.date = None
        self.comments = ''
        self.path_model = os.path.join(os.path.dirname(__file__), "mascaret")
        self.run = ''
        self.scen = ''
        self.complet = False
        self.box = ClassWarningBox()

        self.ui = loadUi(os.path.join(os.path.dirname(__file__), 'ui/ui_import_res.ui'), self)
        self.txt_path.setText(".")

        self.buttonBox.accepted.connect(self.accept_dialog)
        self.buttonBox.rejected.connect(self.reject)

        self.checkBox.setChecked(False)
        self.mDateTimeEdit.setEnabled(False)
        self.checkBox.stateChanged.connect(self.act_date)
        # self.mDateTimeEdit.dateChanged.connect(self.change_date)
        self.txt_path.setText(self.path_model)

        self.bt_path.clicked.connect(self.path_search)
        self.txt_path.textChanged['QString'].connect(self.path_change)
        self.ed_scen.textChanged['QString'].connect(self.change_scenario)
        self.ed_run.textChanged['QString'].connect(self.change_run)

    def change_run(self):
        run = str(self.ed_run.text())
        self.run = run.replace("'", " ").replace('"', ' ').strip()
        self.ed_run.setText(self.run)

    def change_scenario(self):
        scen = str(self.ed_scen.text())
        self.scen = scen.replace("'", " ").replace('"', ' ').strip()
        self.ed_scen.setText(self.scen)

    def act_date(self):
        act_val = bool(self.checkBox.isChecked())
        if act_val:
            self.mDateTimeEdit.setEnabled(True)
        else:
            self.mDateTimeEdit.setEnabled(False)

    def accept_dialog(self):
        """validation dialog function"""
        if bool(self.checkBox.isChecked()):
            date_time_str = self.mDateTimeEdit.dateTime().toString("yyyy-MM-dd HH:mm:ss.zz")
            self.date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        else:
            self.date = None
        self.comments = str(self.textEdit_com.toPlainText())

        if self.scen.strip() == '' or self.run.strip() == '':
            msg = "Indicate the run and scenario names."
            self.box.info(msg, "Error")
        else:
            if self.clmas.check_scenar(self.scen, self.run):
                self.complet = True
                QDialog.accept(self)

    def path_search(self):
        """search path windows"""

        path = QFileDialog.getExistingDirectory(self, "Choose a folder", self.path_model)
        if path:
            self.path_model = path
            self.txt_path.setText(path)

    def path_change(self, text):
        """ change path"""
        if os.path.isdir(text):
            self.path_model = text
            self.txt_path.setText(text)
