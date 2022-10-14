# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 :  Mascaret
Description          : Mascaret tools for QGIS
Date                 : Juillet 2017

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
import sys
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *


class ClassSettingsDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.mgis = parent
        self.mdb = parent.mdb
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_settings.ui'), self)
        self.ui.txt_path_postgres.setText(self.mgis.postgres_path)

        self.ui.buttonBox.accepted.connect(self.accept_dialog)
        self.ui.buttonBox.rejected.connect(self.reject)

        # set UI according to current variable values
        # General
        self.ui.open_lastChbox.setChecked(self.mgis.open_last_conn)
        self.ui.open_lastChbox_schema.setChecked(self.mgis.open_last_schema)

        # test = sys.platform
        # if test == 'win32':
        #     self.mgis.cond_api = False
        #     self.ui.apiChbox.hide()
        # api
        self.ui.apiChbox.setChecked(self.mgis.cond_api)
        self.ui.taskQChbox.setChecked(self.mgis.task_use)

        self.ui.debugModeChbox.setChecked(self.mgis.DEBUG)
        # DB
        # self.ui.db_loadAllChbox.setChecked(self.mgis.mdb.LOAD_ALL)
        self.ui.actionBt_pathPostgres.triggered.connect(self.path_search)
        # self.ui.actionTxt_path_postgres.triggered.connect(self.path_change)
        self.ui.txt_path_postgres.textChanged['QString'].connect(
            self.path_change)

    def accept_dialog(self):
        """validation dialog function"""
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # General
        self.mgis.open_last_conn = self.ui.open_lastChbox.isChecked()
        self.mgis.open_last_schema = self.ui.open_lastChbox_schema.isChecked()
        self.mgis.cond_api = self.ui.apiChbox.isChecked()
        self.mgis.DEBUG = self.ui.debugModeChbox.isChecked()
        self.mgis.task_use = self.ui.taskQChbox.isChecked()
        # Mascaret DB
        self.mgis.mdb.OVERWRITE = True
        self.mgis.mdb.LOAD_ALL = True
        # self.mgis.mdb.LOAD_ALL = self.ui.db_loadAllChbox.isChecked()
        if self.mgis.cond_api:
            self.mgis.ui.actionStructures_weirs.setEnabled(False)
        else:
            self.mgis.ui.actionStructures_weirs.setEnabled(True)
        # write settings to json
        self.mgis.write_settings()

        QApplication.restoreOverrideCursor()
        QDialog.accept(self)

    def path_search(self):
        """search path windows"""
        path = QFileDialog.getExistingDirectory(self, "Choose a folder",
                                                self.mgis.postgres_path)
        if path:
            self.mgis.postgres_path = path
            self.ui.txt_path_postgres.setText(self.mgis.postgres_path)

    def path_change(self, text):
        """ change path"""
        if os.path.isdir(text):
            self.mgis.postgres_path = text
        else:
            self.ui.txt_path_postgres.setText(self.mgis.postgres_path)
