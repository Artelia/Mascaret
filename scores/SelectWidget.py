# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : September,2021
copyright            : (C) 2021 by Artelia
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
from datetime import datetime

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ..ui.custom_control import _qt_is_checked

QT_VERSION = [int(v) for v in qVersion().split('.')][0]

class SelectWidget(QWidget):
    """
    Class of selection run and scenarion for compute scores
    """

    def __init__(self, windmain):
        """
        Class constructor
        :param windmain: main windows (parent)
        """
        QWidget.__init__(self)
        self.windmain = windmain.mgis
        self.mdb = self.windmain.mdb
        self.ui = loadUi(os.path.join(self.windmain.masplugPath, "ui/scores/ui_select.ui"), self)

        self.list_id_select = []
        self.listeRuns = []
        self.listeScen = {}

        self.parent = {}
        self.child = {}
        self.dateedit = {}

        self.today = None

        self.init_gui()

    def init_gui(self):
        """
        initialize GUI
        :return:
        """
        if QT_VERSION > 5:
            qt_tris = Qt.ItemFlag.ItemIsAutoTristate
            qt_item_check = Qt.ItemFlag.ItemIsUserCheckable
            qt_ucheck = Qt.CheckState.Unchecked
        else:
            qt_tris = Qt.ItemIsAutoTristate
            qt_item_check = Qt.ItemIsUserCheckable
            qt_ucheck = Qt.Unchecked
        dico = self.mdb.select("runs", "", "date")
        for run, scen, date, comments in zip(
                dico["run"], dico["scenario"], dico["date"], dico["comments"]
        ):
            # filter initialisation
            # if len(scen) >5 :
            #     if scen[-5:] == '_init':
            #         continue
            if run not in self.listeRuns:
                self.listeRuns.append(run)
                self.listeScen[run] = []
            self.listeScen[run].append((scen, date, comments))

        if len(self.listeRuns) > 0:
            for run in self.listeRuns:
                self.parent[run] = QTreeWidgetItem(self.tw_runs)
                self.parent[run].setText(0, run)
                item_flag = self.parent[run]
                item_flag.setFlags(item_flag.flags() | qt_tris | qt_item_check)

                lbl = QLabel("")
                self.tw_runs.setItemWidget(self.parent[run], 3, lbl)
                self.dateedit[run] = {}
                self.child[run] = {}
                maxi = datetime(1900, 1, 1, 0, 0)
                tmps = datetime.today()
                self.today = QDateTime(tmps.year, tmps.month, tmps.day, 00, 00, 00)

                for scen, date, comments in self.listeScen[run]:
                    self.child[run][scen] = QTreeWidgetItem(self.parent[run])
                    item_flag =  self.child[run][scen]
                    item_flag.setFlags(item_flag.flags()  | qt_item_check)
                    item_flag.setText(0, scen)
                    item_flag.setCheckState(0, qt_ucheck)  # qt6
                    lbl = QLabel("{:%d/%m/%Y %H:%M}".format(date))
                    self.tw_runs.setItemWidget(self.child[run][scen], 1, lbl)
                    maxi = max(maxi, date)

                    lbl = QLabel(comments)
                    self.tw_runs.setItemWidget(self.child[run][scen], 2, lbl)

                lbl = QLabel("{:%d/%m/%Y %H:%M}".format(maxi))
                self.tw_runs.setItemWidget(self.parent[run], 1, lbl)

        self.bt_clean.clicked.connect(self.clean)

    def ch_date(self):
        """change color"""
        for run in self.listeRuns:
            for scen, date, comments in self.listeScen[run]:
                if self.dateedit[run][scen].dateTime() != self.today:
                    self.dateedit[run][scen].setStyleSheet("color: Black")

    def clean(self):
        """clean selection"""
        for run in self.listeRuns:

            is_checked = _qt_is_checked(self.parent[run],  check_level="any")
            if QT_VERSION > 5:
                qt_ucheck = Qt.CheckState.Unchecked
            else:
                qt_ucheck = Qt.Unchecked
            if is_checked:
                for scen, date, comments in self.listeScen[run]:
                    self.child[run][scen].setCheckState(0, qt_ucheck)

    def get_selection(self):
        """get selectioned runs"""
        selection = {}
        for run in self.listeRuns:
            if _qt_is_checked(self.parent[run], check_level="any"):
                selection[run] = []
                for scen, date, comments in self.listeScen[run]:
                    if _qt_is_checked(self.child[run][scen],  check_level="partial_or_full"):
                        selection[run].append("'{}'".format(scen))
        list_id_select = self.mdb.get_id_run(selection)
        return list_id_select
