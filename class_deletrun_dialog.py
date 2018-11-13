# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
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
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtCore import *
if int(qVersion()[0])<5:   #qt4

    from qgis.PyQt.QtGui import *
else: #qt4
    from qgis.PyQt.QtWidgets import *

from datetime import datetime
import os

from .ui.warningbox import Class_warningBox


class class_deletrun_dialog(QDialog):

    def __init__(self, mgis, iface):
        QDialog.__init__(self)
        self.mgis=mgis
        self.mdb =self.mgis.mdb
        self.iface = iface
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_delete.ui'), self)
        self.box = Class_warningBox(self.mgis)
        self.initGUI()

    def initGUI(self):

        listeCol = self.mdb.listColumns('runs')

        dico = self.mdb.select("runs", "", "date")

        self.listeRuns = []
        self.listeScen = {}
        if 'comments' in listeCol:
            for run, scen, date,comments in zip(dico["run"], dico["scenario"], dico["date"], dico["comments"]):
                if not run in self.listeRuns:
                    self.listeRuns.append(run)
                    self.listeScen[run] = []
                self.listeScen[run].append((scen, date,comments))
        else:
            for run, scen, date in zip(dico["run"], dico["scenario"], dico["date"]):
                if not run in self.listeRuns:
                    self.listeRuns.append(run)
                    self.listeScen[run] = []
                self.listeScen[run].append((scen, date))

        if len(self.listeRuns)>0:
            self.tree = self.ui.treeWidget

            self.parent = {}
            self.child = {}

            for run in self.listeRuns:
                self.parent[run] = QTreeWidgetItem(self.tree)
                self.parent[run].setText(0, run)
                self.parent[run].setFlags(self.parent[run].flags() |
                                          Qt.ItemIsTristate |
                                          Qt.ItemIsUserCheckable)
                i = dico['run'].index(run)

                lbl = QLabel('')
                self.tree.setItemWidget(self.parent[run], 2, lbl)

                self.child[run] = {}
                maxi = datetime(1900, 1, 1, 0, 0)
                if 'comments' in listeCol:
                    for scen, date,comments in self.listeScen[run]:
                        self.child[run][scen] = QTreeWidgetItem(self.parent[run])
                        self.child[run][scen].setFlags(self.child[run][scen].flags() |
                                                       Qt.ItemIsUserCheckable)
                        self.child[run][scen].setText(0, scen)

                        self.child[run][scen].setCheckState(0, Qt.Unchecked)

                        lbl = QLabel("{:%d/%m/%Y %H:%M}".format(date))
                        self.tree.setItemWidget(self.child[run][scen], 1, lbl)

                        maxi = max(maxi, date)
                        lbl = QLabel(comments)
                        self.tree.setItemWidget(self.child[run][scen], 2, lbl)
                else:
                    for scen, date in self.listeScen[run]:
                        self.child[run][scen] = QTreeWidgetItem(self.parent[run])
                        self.child[run][scen].setFlags(self.child[run][scen].flags() |
                                                       Qt.ItemIsUserCheckable)
                        self.child[run][scen].setText(0, scen)

                        self.child[run][scen].setCheckState(0, Qt.Unchecked)

                        lbl = QLabel("{:%d/%m/%Y %H:%M}".format(date))
                        self.tree.setItemWidget(self.child[run][scen], 1, lbl)

                        maxi = max(maxi, date)

                lbl = QLabel("{:%d/%m/%Y %H:%M}".format(maxi))
                self.tree.setItemWidget(self.parent[run], 1, lbl)
        else:
            self.ui.b_delete.setDisabled(True)

        self.ui.b_delete.clicked.connect(self.lancement)
        self.ui.b_cancel.clicked.connect(self.annule)


    def lancement(self):

        selection = {}
        for run in self.listeRuns:
            if self.parent[run].checkState(0) > 0:
                selection[run] = []
                for scen, date in self.listeScen[run]:
                    if self.child[run][scen].checkState(0) > 1:
                        selection[run].append("'{}'".format(scen))

        self.close()

        self.iface.messageBar().clearWidgets()
        progressMessageBar = self.iface.messageBar()
        progress = QProgressBar()
        progress.setMaximum(100)
        progressMessageBar.pushWidget(progress)

        n = len(selection.keys())
        ok = self.box.yes_no_q('Do you want to delete ?')

        if ok:
            for i, (run, scenarios) in enumerate(selection.items()):
                sql = "run = '{0}' AND scenario IN ({1})".format(run,
                                                                 ",".join(scenarios))
                self.mdb.delete("resultats", sql)
                self.mdb.delete("runs", sql)
                if self.mgis.DEBUG:
                    self.mgis.addInfo("Deletion of {0} scenario for {1} is done".format(scenarios, run))


                progress.setValue(i / float(n) * 100)

        self.iface.messageBar().clearWidgets()

    def annule(self):
        self.close()

