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

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from qgis.PyQt.QtWidgets import *

from datetime import datetime


class SelectWidget(QWidget):
    def __init__(self, windmain):
        QWidget.__init__(self)
        self.windmain = windmain.mgis
        self.mdb = self.windmain.mdb
        self.ui = loadUi(
            os.path.join(self.windmain.masplugPath, 'ui/scores/ui_select.ui'),
            self)

        self.list_id_select = []
        self.listeRuns = []
        self.listeScen = {}

        self.parent = {}
        self.child = {}
        self.dateedit = {}

        self.init_gui()

    def init_gui(self):
        """
        initialize GUI
        :return:
        """
        dico = self.mdb.select("runs", "", "date")
        for run, scen, date, comments in zip(dico["run"],
                                             dico["scenario"],
                                             dico["date"],
                                             dico["comments"]):
            if run not in self.listeRuns:
                self.listeRuns.append(run)
                self.listeScen[run] = []
            self.listeScen[run].append((scen, date, comments))

        if len(self.listeRuns) > 0:
            for run in self.listeRuns:
                self.parent[run] = QTreeWidgetItem(self.tw_runs)
                self.parent[run].setText(0, run)
                self.parent[run].setFlags(self.parent[run].flags() |
                                          Qt.ItemIsTristate |
                                          Qt.ItemIsUserCheckable)

                lbl = QLabel('')
                self.tw_runs.setItemWidget(self.parent[run], 3, lbl)
                self.dateedit[run] = {}
                self.child[run] = {}
                maxi = datetime(1900, 1, 1, 0, 0)
                tmps = datetime.today()
                self.today = QDateTime(tmps.year, tmps.month, tmps.day, 00, 00,
                                       00)

                for scen, date, comments in self.listeScen[run]:
                    self.child[run][scen] = QTreeWidgetItem(
                        self.parent[run])
                    self.child[run][scen].setFlags(
                        self.child[run][scen].flags() |
                        Qt.ItemIsUserCheckable)
                    self.child[run][scen].setText(0, scen)

                    self.child[run][scen].setCheckState(0, Qt.Unchecked)

                    lbl = QLabel("{:%d/%m/%Y %H:%M}".format(date))
                    self.tw_runs.setItemWidget(self.child[run][scen], 1, lbl)
                    maxi = max(maxi, date)

                    lbl = QLabel(comments)
                    self.tw_runs.setItemWidget(self.child[run][scen], 2, lbl)

                lbl = QLabel("{:%d/%m/%Y %H:%M}".format(maxi))
                self.tw_runs.setItemWidget(self.parent[run], 1, lbl)

        self.bt_clean.clicked.connect(self.clean)

    def ch_date(self, newdate):
        """ change color"""
        for run in self.listeRuns:
            for scen, date, comments in self.listeScen[run]:
                if self.dateedit[run][scen].dateTime() != self.today:
                    self.dateedit[run][scen].setStyleSheet('color: Black')

    def clean(self):
        """ clean selection"""
        for run in self.listeRuns:
            if self.parent[run].checkState(0) > 0:
                for scen, date, comments in self.listeScen[run]:
                    self.child[run][scen].setCheckState(0, Qt.Unchecked)

    def get_selection(self):
        """ get selectioned runs"""
        selection = {}
        lst_date = []
        for run in self.listeRuns:
            if self.parent[run].checkState(0) > 0:
                selection[run] = []
                for scen, date, comments in self.listeScen[run]:
                    if self.child[run][scen].checkState(0) > 1:
                        selection[run].append("'{}'".format(scen))
        list_id_select = self.mdb.get_id_run(selection)
        return list_id_select
