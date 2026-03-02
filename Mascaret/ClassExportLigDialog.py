# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Mascaret
Description          : Mascaret parameters
Date                 : septembre 2017

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

from .Function import del_accent, del_symbolv2
from .model.ClassCreatFilesModels import ClassCreatFilesModels


class ClassExportLigDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_export_lig.ui"), self)

        self.init_gui()

        self.cb_init_run.currentIndexChanged.connect(self.fill_cb_init_cas)
        self.lname_export.editingFinished.connect(self.check_str)
        self.bt_rep.clicked.connect(self.path_search)
        self.bt_ok.accepted.connect(self.accept_dialog)
        self.bt_ok.rejected.connect(self.reject)

        self.clfile = ClassCreatFilesModels(self.mdb, self.mgis.dossier_file_masc, self.mgis.cond_api, self.mgis.DEBUG)

    def init_gui(self):
        """
        Initilize GUI
        """
        self.fill_cb_init_run()
        self.fill_cb_init_cas()
        self.lname_export.setText("mascaret")

    def fill_cb_init_run(self):
        """
        Fill cb_init_run comboBox
        """
        dico_run = self.mdb.select_distinct("run", "runs")
        if dico_run:
            if dico_run != {}:
                liste_run = ["{}".format(v) for v in dico_run["run"]]
            else:
                liste_run = []
        else:
            liste_run = []
        self.cb_init_run.addItems(liste_run)

    def fill_cb_init_cas(self):
        """
        Fill cb_init_cas comboBox
        """
        self.cb_init_scen.clear()
        init_run = self.cb_init_run.currentText()
        condition = "run LIKE '{0}'".format(init_run)
        dico_scen = self.mdb.select_distinct("scenario", "runs", condition)
        if dico_scen:
            liste_scen = ["{}".format(v) for v in dico_scen["scenario"]]
        else:
            liste_scen = []
        self.cb_init_scen.addItems(liste_scen)

    def path_search(self):
        """search path windows"""
        path = QFileDialog.getExistingDirectory(self, "Choose a folder", self.mgis.repProject)
        if path:
            self.txt_rep.setText(path)
        else:
            self.txt_rep.setText('')

    @staticmethod
    def str2bool(s):
        """string to bool"""
        if "True" in s or "TRUE" in s:
            return True
        else:
            return False

    def check_str(self):
        """ check name :
        - delete accent and symbol"""
        self.lname_export.blockSignals(True)
        name = self.lname_export.text().strip()
        name = name.replace(".", "_")
        name = del_symbolv2(name, ["_", "-"])
        name = del_accent(name)
        name = name.replace(" ", "_")
        self.lname_export.setText(name)
        self.lname_export.blockSignals(False)

    def accept_dialog(self):
        """Creation of .lig File"""

        case = self.cb_init_run.currentText()
        scen = self.cb_init_scen.currentText()
        id_run = self.mdb.run_query(
            "SELECT id FROM {0}.runs "
            "WHERE run = '{1}' "
            "AND scenario = '{2}'".format(self.mdb.SCHEMA, case, scen),
            fetch=True,
        )
        if not id_run:
            QMessageBox.warning(
                self, "WARNING", "The (Run,Scenario) couple does not exist."
            )
            return
        id_run = id_run[0][0]
        path_file = self.txt_rep.text()
        if not os.path.isdir(path_file):
            QMessageBox.warning(
                self, "WARNING", "The save folder does not exist."
            )
            return
        basename = self.lname_export.text().strip()
        if basename == "":
            QMessageBox.warning(
                self, "WARNING", "Specify the name file."
            )
            return

        self.clfile.opt_to_lig(id_run, basename, path_file=path_file)
        self.mgis.add_info('The exportation of the .lig file is done')
        self.close()
