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
 This module provides a dialog UI to configure and launch Mascaret runs.
"""
import os

from qgis.PyQt.QtWidgets import QLineEdit, QLabel
from qgis.PyQt.QtCore import qVersion, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QDialog,
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
from ..Function import del_accent, del_symbolv2
from ...ui.custom_control import ClassWarningBox

QT_VERSION = [int(v) for v in qVersion().split('.')][0]


class ClassRunUIDialog(QDialog):
    """Dialog to configure and start one or many Mascaret runs.

    The dialog builds a scenario table depending on kernel and options,
    collects user inputs and updates the provided obj_model with run settings.
    """
    def __init__(self, mgis, kernel, obj_model):
        """Initialize the run dialog and populate UI widgets.

        :param mgis: Main plugin object with settings and DB access.
        :param kernel: Kernel identifier.
        :param obj_model: Model configuration object.
        """
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.obj_model = obj_model
        self.kernel = kernel
        self.lst_event = []

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_run.ui"), self)
        self.setWindowTitle("Running Model")
        self.box = ClassWarningBox()

        self.bt_running.clicked.connect(self.accept_run)
        self.bt_path.clicked.connect(self.path_search)

        # state list
        self.dkernel = {"steady": "Steady",
                        "unsteady": "Unsteady",
                        "transcritical": "Transcritical_unsteady",
                        }
        self.le_run.setText(self.dkernel[self.kernel])

        self.obj_model.fill_drun(self.kernel, self.dkernel[self.kernel])
        self.drun = self.obj_model.get_drun()
        self.default_run_path = self.obj_model.dmodel["general"]["path_runs"]
        self.run_path = self.default_run_path
        self.lbl_path.setText(self.run_path)
        self.hide_layout(self.lay_path)

        self.sp_core.setMaximum(os.cpu_count())
        self.sp_core.setValue(int(os.cpu_count() * 0.75))

        self.without_init_version = True

        if self.drun['event']:
            d_event = self.obj_model.get_events()
            if not d_event:
                self.bt_running.setEnabled(False)
                self.lst_event = []
            else:
                self.lst_event = d_event['name']

            self.nb_row = len(self.lst_event)
        else:
            self.nb_row = 1

        if kernel != 'steady' and (not self.drun["has_run_init"] and self.drun["ligInit"]):
            self.without_init_version = False

        self.setup_table()

    @staticmethod
    def _fmt_txt(txt):
        """Escape quotes in user-provided text.

        :param txt: Input text.
        :type txt: str
        :return: Formatted text safe for SQL or display.
        :rtype: str
        """
        return txt.replace("'", "''").replace('"', " ")

    @staticmethod
    def _fmt_name(txt):
        """Normalize a name: remove accents and disallowed symbols.

        :param txt: Input name string.
        :type txt: str
        :return: Sanitized name string.
        :rtype: str
        """
        txt = del_accent(txt)
        txt = del_symbolv2(txt, exclud=['_', '-'])
        return txt.strip()

    def path_search(self):
        """Open a directory selection dialog and update the run path.

        :return: None
        """
        # Search path (Windows)
        path_ = QFileDialog.getExistingDirectory(self, "Choose a folder", self.run_path)
        if os.path.isdir(path_):
            self.lbl_path.setText(path_)
            self.run_path = path_
        else:
            self.lbl_path.setText('')
            self.run_path = self.default_run_path


    def setup_table(self):
        """Configure the scenario table columns and row count based on selected options.

        :return: None
        """
        if self.without_init_version:
            headers = ['Scenario Name', 'Comment']
        else:
            headers = ['Scenario Name', 'Run init', 'Scenario init', 'lig file', 'Comment']

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(self.nb_row)  # number of rows based on events or single row
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        for row in range(self.table.rowCount()):
            self.add_row_widgets(row)

    def add_row_widgets(self, row):
        """Add widgets to each table cell according to column types.

        :param row: Row index to populate.
        :type row: int
        :return: None
        """
        # Column 0: Scenario Name (QLineEdit or QLabel for events)
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
        """Populate the 'Scenario init' combobox for a given initial run selection.

        :param ctrl: The QComboBox control to populate.
        :param init_run: Selected initial run name or '.lig' marker.
        :return: None
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
        """Populate the 'Run init' combobox with available runs and a '.lig' option.

        :param ctrl: The QComboBox control to populate.
        :return: None
        """
        dico_run = self.mdb.select_distinct("run", "runs")
        if dico_run != {} and dico_run is not None:
            liste_run = ["{}".format(v) for v in dico_run["run"]]
        else:
            liste_run = []
        liste_run.append('".lig" File')
        ctrl.addItems(liste_run)

    def up_cb_scenario_init(self, row, value):
        """Update dependent widgets when 'Run init' selection changes.

        Enables or disables the Scenario init combobox and lig-file widget.

        :param row: Row index where the change occurred.
        :param value: Newly selected run init value.
        :return: None
        """
        # Update Scenario init options
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

    def check_run_scenar_exist(self, run, nom_scen):
        condition = f"run LIKE '{run}'"
        allscen = self.mdb.select_distinct("scenario", "runs", condition)
        if allscen:
            if nom_scen in allscen["scenario"] or f"{nom_scen}_init" in allscen["scenario"]:
                info = True
            else:
                info = False

    def check_scenar(self, run, nom_scen):
        """if true :not exist nomScen and results"""
        # kernel=self.listeState[self.Klist.index(kernel)]

        if not self.check_run_scenar_exist(run, nom_scen) and \
            not self.check_run_scenar_exist(run, f'{nom_scen}_init'):
            return False

        ok = self.box.yes_no_q(
            f"Do you want to remove the {nom_scen} results for a "
            "new simulation? "
        )

        if not ok:
            return True

        # delete case initalization
        condition = (
            f"(scenario LIKE '{nom_scen}' OR  scenario "
            f"LIKE '{nom_scen}_init')"
            f" AND run LIKE '{run}' "
        )

        id_run = self.mdb.run_query(
            f"SELECT id FROM {self.mdb.SCHEMA}.runs "
            f"WHERE run = '{run}' "
            f"AND (scenario LIKE '{nom_scen}' "
            f"OR  scenario "
            f"LIKE '{nom_scen}_init') ",
            fetch=True,
        )
        self.mdb.delete("runs", condition)
        # new results
        if len(id_run) > 0:
            id_run = id_run[0][0]
            condition = "id_runs = {}".format(id_run)
            var = self.mdb.run_query(
                f"SELECT DISTINCT var FROM {self.mdb.SCHEMA}.results WHERE {condition} ",
                fetch=True,
            )
            list_var = [str(v[0]) for v in var]
            if len(list_var) > 0:
                self.mdb.run_query(
                    f"DELETE  FROM {self.mdb.SCHEMA}.results_var "
                    f'where id in ({",".join(list_var)}) and '
                    f"type_res = '"
                    f"tracer_TRANSPORT_PUR'"
                )
            self.mdb.delete("results_sect", condition)
            self.mdb.delete("runs_graph", condition)
            self.mdb.delete("runs_plani", condition)
            self.mdb.delete("results_by_pk", condition)

        self.mgis.add_info(
            "Deletion of {0} scenario for {1} is done".format(nom_scen, run), dbg=True
        )
        return False

    def hide_layout(self,layout):
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.hide()

    def accept_run(self):
        """Collect data from table rows, update obj_model and close dialog.

        :return: None
        """
        if self.default_run_path != self.run_path :
            self.obj_model.set_dgeneral({"path_runs":self.run_path,
                                         "has_new_run_path": True})

        self.obj_model.set_drun({'limit_core' : self.sp_core.value()})
        name_run = self._fmt_name(self.le_run.text())
        if name_run == '':
            self.box.info(f"Run name is required.", title="Warning")
            return


        data = []
        for row in range(self.table.rowCount()):
            row_data = {}

            name_scen = self._fmt_name(self.table.cellWidget(row, 0).text())
            name_scen = name_scen.strip()
            row_data["Scenario Name"] = name_scen
            if name_scen == '':
                self.box.info(f"Scenario name is required for the {row} row.", title="Warning")
                return

            if self.without_init_version :
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

            if self.check_scenar(name_run, name_scen, ):
                self.box.info(f"Scenario {name_scen} is existing "
                              f"for the {row} row.", title="Warning")
                return

            data.append(row_data)

        self.obj_model.set_drun({"name_run": name_run})
        self.obj_model.fill_lscenario(data)

        self.accept()


class LigFileWidget(QWidget):
    """Widget used in the table to pick a .lig file and store its path."""

    def __init__(self, parent):
        """Create widget with file label, select button and hidden full-path label.

        :param parent: Parent dialog instance providing mgis and other context.
        """
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
        """Open a file dialog to select a .lig file and update labels/parent project.

        :return: None
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", self.mgis.repProject,
                                                   "lig File (*.lig);; File (*)")
        if file_path:
            self.file_label.setText(file_path.split("/")[-1])
            self.hidden_path.setText(file_path)
            self.mgis.up_rep_project(file_path)

            # Adjust the column width dynamically
            parent_table = self.parent()
            while parent_table and not isinstance(parent_table, QTableWidget):
                parent_table = parent_table.parent()
            if parent_table:
                parent_table.resizeColumnToContents(3)

    def get_file_info(self):
        """Return the displayed file name and the full file path.

        :return: dict with keys 'file_name' and 'file_path'.
        :rtype: dict
        """
        return {
            "file_name": self.file_label.text() if self.file_label.text() != 'No file selected' else '',
            "file_path": self.hidden_path.text()
        }

