# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2017
copyright            : (C) 2017 by Artelia
email                :
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import Qt, qVersion
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import QMessageBox

from .ClassTableWQ import ClassTableWQ
from .Graph_WQ import GraphInitConc
from .Init_conc import InitConcDialog
from ...ui.custom_control import _qt_is_checked, get_qt_checked, get_qt_unchecked

QT_VERSION = [int(v) for v in qVersion().split(".")][0]


class ClassTracerInitDialog:
    def __init__(self, obj):
        self.paramTr = obj
        self.mgis = obj.mgis
        self.ui = obj.ui
        self.mdb = self.mgis.mdb
        self.tbwq = ClassTableWQ(self.mgis, self.mdb)
        self.cur_wq_mod = self.tbwq.dico_mod_wq[obj.type]
        self.cur_wq_law = None
        self.filling_tab = False
        self.graph_home = None

        self.ui.actionB_edit.triggered.connect(self.edit_law)
        self.ui.actionB_new.triggered.connect(self.new_law)
        self.ui.actionB_delete.triggered.connect(self.delete_law)
        self.ui.cb_bief_home.currentIndexChanged.connect(self.change_bief_home)
        self.init_ui()

    def init_ui(self):
        self.ui.Law_pages.setCurrentIndex(0)
        self.graph_home = GraphInitConc(self.mgis, self.ui.lay_graph_home)

    def change_module(self, mdl):
        self.cur_wq_mod = self.tbwq.dico_mod_wq[mdl]
        self.cur_wq_law = None
        self.graph_home.init_mdl(self.tbwq.dico_wq_mod[self.cur_wq_mod])
        self.fill_lst_conf()

    def fill_lst_conf(self, id_=None):
        """fill list configuration"""
        qt_check = get_qt_checked()
        qt_ucheck = get_qt_unchecked()

        model = QStandardItemModel()
        model.setColumnCount(2)
        self.ui.lst_laws.setModel(model)
        self.ui.lst_laws.setModelColumn(1)
        self.ui.lst_laws.selectionModel().selectionChanged.connect(self.change_cur_law)
        rows = self.mdb.run_query(
            "SELECT * FROM {schema}.init_conc_config WHERE type = %s ORDER BY name",
            fetch=True,
            params=[self.cur_wq_mod],
            schema=True,
        )

        for i, row in enumerate(rows):
            for j, field in enumerate(row):
                if j != 3:
                    new_itm = QStandardItem(str(row[j]))
                    new_itm.setEditable(False)
                    if j == 1:
                        new_itm.setCheckable(True)
                        if not row[3]:
                            new_itm.setCheckState(qt_ucheck)
                        elif row[3]:
                            new_itm.setCheckState(qt_check)
                    self.ui.lst_laws.model().setItem(i, j, new_itm)

        self.ui.lst_laws.model().itemChanged.connect(self.sel_config_def)

        if id_:
            for r in range(self.ui.lst_laws.model().rowCount()):
                if str(self.ui.lst_laws.model().item(r, 0).text()) == str(id):
                    self.ui.lst_laws.setCurrentIndex(self.ui.lst_laws.model().item(r, 1).index())
                    break
        else:
            self.display_graph_home()
            self.ui.cb_bief_home.clear()

    def change_cur_law(self):
        self.ui.cb_bief_home.clear()
        if self.ui.lst_laws.selectedIndexes():
            line = self.ui.lst_laws.selectedIndexes()[0].row()
            config = int(self.ui.lst_laws.model().item(line, 0).text())

            lst_bief = self.mdb.run_query(
                "SELECT DISTINCT bief FROM {schema}.init_conc_wq "
                "WHERE id_config = %s ORDER BY bief",
                fetch=True,
                params=[config],
                schema=True,
            )
            if len(lst_bief) > 0:
                for bief in lst_bief:
                    self.ui.cb_bief_home.addItem("Bief {}".format(bief[0]), bief[0])
            else:
                self.display_graph_home()

    def change_bief_home(self):
        self.display_graph_home()

    def display_graph_home(self):
        if self.ui.lst_laws.selectedIndexes() and self.ui.cb_bief_home.currentIndex() != -1:
            line = self.ui.lst_laws.selectedIndexes()[0].row()
            config = int(self.ui.lst_laws.model().item(line, 0).text())
            bief = self.ui.cb_bief_home.itemData(self.ui.cb_bief_home.currentIndex())
            self.graph_home.init_graph(config, bief)
        else:
            self.graph_home.init_graph(None, None)

    def sel_config_def(self, itm):
        qt_ucheck = get_qt_unchecked()
        self.ui.lst_laws.model().blockSignals(True)
        for r in range(self.ui.lst_laws.model().rowCount()):
            if r != itm.row():
                self.ui.lst_laws.model().item(r, 1).setCheckState(qt_ucheck)
        self.ui.lst_laws.model().blockSignals(False)

        self.mdb.run_query(
            "UPDATE {schema}.init_conc_config SET active = %s WHERE type = %s",
            params=[False, self.cur_wq_mod],
            schema=True,
        )
        if _qt_is_checked(itm, check_level="full"):
            law_id = int(self.ui.lst_laws.model().item(itm.row(), 0).text())
            self.mdb.run_query(
                "UPDATE {schema}.init_conc_config SET active = %s WHERE id = %s",
                params=[True, law_id],
                schema=True,
            )

    def new_law(self):
        self.cur_wq_law = -1
        dlg = InitConcDialog(self.paramTr, self.cur_wq_law, "")

        if QT_VERSION > 5:
            dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
            ret = dlg.exec()  # PyQt6
        else:
            dlg.setWindowModality(Qt.ApplicationModal)
            ret = dlg.exec_()
            # PyQt5
        if ret:
            self.fill_lst_conf(dlg.cur_wq_law)

    def edit_law(self):
        if self.ui.lst_laws.selectedIndexes():
            line = self.ui.lst_laws.selectedIndexes()[0].row()
            self.cur_wq_law = int(self.ui.lst_laws.model().item(line, 0).text())
            dlg = InitConcDialog(
                self.paramTr, self.cur_wq_law, self.ui.lst_laws.model().item(line, 1).text()
            )
            if QT_VERSION > 5:
                dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
                ret = dlg.exec()  # PyQt6
            else:
                dlg.setWindowModality(Qt.ApplicationModal)
                ret = dlg.exec_()  # PyQt5
            if ret:
                self.fill_lst_conf(dlg.cur_wq_law)

    def delete_law(self):
        # charger les informations
        # changer de page
        if self.ui.lst_laws.selectedIndexes():
            line = self.ui.lst_laws.selectedIndexes()[0].row()
            id_law = self.ui.lst_laws.model().item(line, 0).text()
            name_law = self.ui.lst_laws.model().item(line, 1).text()
            if QT_VERSION > 5:
                ok_button = QMessageBox.StandardButton.Ok
                cancel_button = QMessageBox.StandardButton.Cancel
            else:
                ok_button = QMessageBox.Ok
                cancel_button = QMessageBox.Cancel
            if (
                QMessageBox.question(
                    self.paramTr,
                    "Tracer Initial Concentration",
                    "Delete {} ?".format(name_law),
                    cancel_button | ok_button,
                )
            ) == ok_button:
                self.mgis.add_info("Deletion of {} Tracer Laws".format(name_law), dbg=True)
                self.mdb.delete("init_conc_wq", where="id_config = %s", params=[int(id_law)])
                self.mdb.delete("init_conc_config", where="id = %s", params=[int(id_law)])
                self.fill_lst_conf()
