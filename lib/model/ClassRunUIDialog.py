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

from PyQt5.QtWidgets import QLineEdit, QLabel
from qgis.PyQt.QtCore import qVersion, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QHeaderView
)
from qgis.PyQt.uic import loadUi

QT_VERSION = [int(v) for v in qVersion().split('.')][0]


class ClassRunUIDialog(QDialog):


    def __init__(self, mgis, kernel, cldr):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.cldr = cldr
        self.kernel = kernel
        self.lst_event = []
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_run.ui"), self)
        self.setWindowTitle("Running Model")

        self.bt_running.clicked.connect(self.accept_run)

        # state list
        self.dkernel = {"steady": "Steady",
                        "unsteady": "Unsteady",
                        "transcritical": "Transcritical_unsteady",
                        }
        self.le_run.setText(self.dkernel[self.kernel])

        self.cldr.fill_drun(self.kernel, self.dkernel[self.kernel])
        self.drun = self.cldr.get_drun()

        self.without_init_version = True

        if self.drun['event']:
            d_event = self.cldr.get_events()
            if not d_event:
                self.bt_running.setEnable(False)
            self.lst_event = d_event['name']

            self.nb_row = len(self.lst_event)
        else:
            self.nb_row = 1

        if kernel != 'steady' and (not self.drun["autoInit"] and self.drun["ligInit"]):
            self.without_init_version = False

        self.setup_table()

    @staticmethod
    def _fmt_txt(txt):
        return txt.replace("'", "''").replace('"', " ")

    def setup_table(self):
        """Configure table based on selected column version."""
        if self.without_init_version:
            headers = ['Scenario Name', 'Comment']
        else:
            headers = ['Scenario Name', 'Run init', 'Scenario init', 'lig file', 'Comment']

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(self.nb_row)  # Example with 3 rows
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        for row in range(self.table.rowCount()):
            self.add_row_widgets(row)

    def add_row_widgets(self, row):
        """Add widgets to each cell based on column type."""
        # Column 0: Scenario Name (QLineEdit)
        if self.lst_event:
            name_edit = QLabel(self.lst_event[row])
            self.table.setCellWidget(row, 0, name_edit)
        else:
            name_edit = QLineEdit()
            self.table.setCellWidget(row, 0, name_edit)

        if self.without_init_version:
            # Column 1: Comment (QLineEdit)
            comment_edit = QLineEdit()
            self.table.setCellWidget(row, 1, comment_edit)
        else:
            # Column 1: Run init (QComboBox)
            run_init_combo = QComboBox()
            self.fill_cb_run(run_init_combo)
            run_init_combo.currentTextChanged.connect(
                lambda value, r=row: self.up_cb_scenario_init(r, value)
            )
            self.table.setCellWidget(row, 1, run_init_combo)

            # Column 2: Scenario init (QComboBox)
            scenario_init_combo = QComboBox()
            self.fill_cb_init_scenar(scenario_init_combo, run_init_combo.currentText())
            self.table.setCellWidget(row, 2, scenario_init_combo)

            # Column 3: lig file (custom widget)
            lig_widget = LigFileWidget(self)
            lig_widget.setEnabled(False)
            self.table.setCellWidget(row, 3, lig_widget)

            # Column 4: Comment (QLineEdit)
            comment_edit = QLineEdit()
            self.table.setCellWidget(row, 4, comment_edit)

    def fill_cb_init_scenar(self, ctrl, init_run):
        """
        Fill cb_init__scenarcomboBox
        """
        ctrl.clear()
        condition = "run LIKE '{0}'".format(init_run)
        dico_scen = self.mdb.select_distinct("scenario", "runs", condition)
        if dico_scen:
            liste_scen = ["{}".format(v) for v in dico_scen["scenario"]]
        else:
            liste_scen = []
        ctrl.addItems(liste_scen)

    def fill_cb_run(self, ctrl):
        dico_run = self.mdb.select_distinct("run", "runs")
        if dico_run != {} and dico_run is not None:
            liste_run = ["{}".format(v) for v in dico_run["run"]]
        else:
            liste_run = []
        liste_run.append('".lig" File')
        ctrl.addItems(liste_run)

    def up_cb_scenario_init(self, row, value):
        """Update dependent widgets based on 'Run init' selection."""
        scenario_init_combo = self.table.cellWidget(row, 2)
        lig_widget = self.table.cellWidget(row, 3)
        # Update Scenario init options
        scenario_init_combo.clear()
        if value == '".lig" File':
            scenario_init_combo.setEnabled(False)
            lig_widget.setEnabled(True)
        else:
            scenario_init_combo.setEnabled(True)
            self.fill_cb_init_scenar(scenario_init_combo, value)
            lig_widget.setEnabled(False)

    def accept_run(self):
        """Collect data from all rows and print as list of dictionaries."""

        self.cldr.set_drun({"name_run": self._fmt_txt(self.le_run.text())})

        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            row_data["Scenario Name"] = self._fmt_txt(self.table.cellWidget(row, 0).text())

            if self.without_init_version == 2:
                row_data["Comment"] = self._fmt_txt(self.table.cellWidget(row, 1).text())
            else:
                lig_widget = self.table.cellWidget(row, 3)
                if lig_widget.isEnabled():
                    row_data["Run init"] = None
                    row_data["Scenario init"] = None
                    row_data["lig file"] = lig_widget.get_file_info()
                else:
                    row_data["Run init"] = self.table.cellWidget(row, 1).currentText()
                    row_data["Scenario init"] = self.table.cellWidget(row, 2).currentText()
                    row_data["lig file"] = None

                row_data["Comment"] = self._fmt_txt(self.table.cellWidget(row, 4).text())

            data.append(row_data)

        self.cldr.fill_lscenario(data)
        self.close()


class LigFileWidget(QWidget):
    """Custom widget for 'lig file' column with file selection and hidden path."""

    def __init__(self, parent):
        super().__init__(parent)
        self.mgis = parent.mgis
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.file_label = QLabel("No file selected")
        self.select_button = QPushButton("...")
        self.hidden_path = QLabel("")
        self.hidden_path.setVisible(False)

        self.select_button.clicked.connect(self.select_file)

        self.layout.addWidget(self.file_label)
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.hidden_path)

    def select_file(self):
        """Open file dialog and update labels."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", self.mgis.repProject,
                                                   "lig File (*.lig);; File (*)")
        if file_path:
            self.file_label.setText(file_path.split("/")[-1])
            self.hidden_path.setText(file_path)
            self.mgis.up_rep_project(file_path)

            # Ajuster la colonne dynamiquement
            parent_table = self.parent()
            while parent_table and not isinstance(parent_table, QTableWidget):
                parent_table = parent_table.parent()
            if parent_table:
                parent_table.resizeColumnToContents(3)

    def get_file_info(self):
        """Return file name and full path."""
        return {
            "file_name": self.file_label.text() if self.file_label.text() != 'No file selected' else '',
            "file_path": self.hidden_path.text()
        }
