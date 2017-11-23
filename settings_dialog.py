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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from ui.ui_settings_Simple import *
import os

class Settings(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.mgis = parent
        self.mdb = parent.mdb

        self.ui.txt_path_postgres.setText(self.mgis.postgres_path)

        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.reject)

        # set UI according to current variable values
        # General
        self.ui.open_lastChbox.setChecked(self.mgis.open_last_conn)
        self.ui.open_lastChbox_schema.setChecked(self.mgis.open_last_schema)

        self.ui.debugModeChbox.setChecked(self.mgis.DEBUG)
        # DB
        # self.ui.db_loadAllChbox.setChecked(self.mgis.mdb.LOAD_ALL)
        self.ui.actionBt_pathPostgres.triggered.connect(self.pathSearch)
        # self.ui.actionTxt_path_postgres.triggered.connect(self.pathChange)
        self.ui.txt_path_postgres.textChanged['QString'].connect(self.pathChange)

    def acceptDialog(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # General
        self.mgis.open_last_conn = self.ui.open_lastChbox.isChecked()
        self.mgis.open_last_schema= self.ui.open_lastChbox_schema.isChecked()
        self.mgis.DEBUG = self.ui.debugModeChbox.isChecked()
        # Mascaret DB
        self.mgis.mdb.OVERWRITE = True
        self.mgis.mdb.LOAD_ALL=True
        # self.mgis.mdb.LOAD_ALL = self.ui.db_loadAllChbox.isChecked()

        # write settings to json
        self.mgis.writeSettings()
        # print self.mgis.opts

        QApplication.restoreOverrideCursor()
        QDialog.accept(self)


    def pathSearch(self):
        """search path windows"""
        path = QFileDialog.getExistingDirectory(self, "Choose a folder", self.mgis.postgres_path)
        if path:
            self.mgis.postgres_path=path
            self.ui.txt_path_postgres.setText(self.mgis.postgres_path)

    def pathChange(self, text):

        if os.path.isdir(text):
            self.mgis.postgres_path = text
        else:
            self.ui.txt_path_postgres.setText( self.mgis.postgres_path)


