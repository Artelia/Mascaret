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
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .ui.custom_control import ClassWarningBox
from qgis.PyQt.QtGui import *
from qgis import core

try:
    qgis_version = core.QGis.QGIS_VERSION_INT
except AttributeError:
    qgis_version = core.Qgis.QGIS_VERSION_INT

if qgis_version < 31616:
    FORM_CLASS, BASE = uic.loadUiType(
        os.path.join(os.path.join(os.path.dirname(__file__), 'ui/edit_ks_mesh_plan31000.ui')))
else:
    FORM_CLASS, BASE = uic.loadUiType(
        os.path.join(os.path.join(os.path.dirname(__file__), 'ui/edit_ks_mesh_plan31616.ui')))


class ClassEditKsDialog(BASE, FORM_CLASS):
    """
    Class allow to update ks mesh planim of the selected profiles
    """

    def __init__(self, mgis, iface):

        super(ClassEditKsDialog, self).__init__()
        self.setupUi(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.box = ClassWarningBox()
        self.ctrl_ch = [("mesh", self.ch_mesh, self.dsp_mesh),
                        ("planim", self.ch_planim, self.dsp_planim),
                        ("minbedcoef", self.ch_minbedcoef, self.dsp_minbedcoef),
                        ("majbedcoef", self.ch_majbedcoef, self.dsp_majbedcoef), ]

        self.init_gui()

    def init_gui(self):
        """
              initialisation GUI
        """
        self.chall.stateChanged.connect(self.chall_event)
        self.chall.setChecked(False)

        self.bupdate.clicked.connect(self.lancement)
        self.bcancel.clicked.connect(self.annule)

    def chall_event(self):
        """event change check all"""
        # self.sender()
        val = self.chall.isChecked()
        for var, ctrl, crtl2 in self.ctrl_ch:
            ctrl.setChecked(val)

    def lancement(self):
        """ Delete selection function"""

        tempo = QgsProject.instance().mapLayers().values()
        for couche in tempo:
            if couche.name() == "profiles":
                profil = couche

        if len(profil.selectedFeatures()) == 0:
            self.box.info('Please, selection the profiles', title='Message')
            return

        tab = {}
        lst_name = []
        for feature in profil.selectedFeatures():
            tab[feature["gid"]] = {}
            lst_name.append(feature["name"])
            # print(nom)
            for var, ctrl, crtl2 in self.ctrl_ch:
                if ctrl.isChecked():
                    tab[feature["gid"]][var] = crtl2.value()

        self.mgis.mdb.update('profiles', tab, var="gid")
        if self.mgis.DEBUG:
            self.mgis.add_info('List of profile which were updated :\n {}'.format(','.join(lst_name)))
        ok = self.box.yes_no_q('Do you want to update other profiles ?', title='')
        if ok:
            return

        self.close()

    def closeEvent(self, event):
        QtWidgets.QDockWidget.closeEvent(self, event)
        event.accept()

    def annule(self):
        """"Cancel """
        self.close()
