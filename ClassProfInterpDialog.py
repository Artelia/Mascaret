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

from .ClassProfInterp import ClassProfInterp

from qgis.PyQt.QtWidgets import *


class ClassProfInterpDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_interp_profile.ui'),self)
        self.nplan = 100
        self.plani = None
        self.pk_int = None
        self.data = {}
        self.interpol_prof = {}
        self.compute = True

        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)
        self.fct_autdisc()
        self.ch_autdisc.stateChanged.connect(self.fct_autdisc)


    def init_gui(self, nplan,plani,dict_interp, pk_int, err):
        self.pk_int = pk_int
        self.data = dict_interp
        self.plani = plani
        self.sp_nbplan.setValue(nplan)
        self.compute = True


        if len(err.keys())>0 :
            msg_lbl = 'WARNING: \n'
            for key, msg  in err.items():
                msg_lbl += '  - {}\n'.format(msg)
                if key =='plani':
                    self.ch_autdisc.setChecked(False)
                    self.ch_autdisc.setEnabled(False)
                if key =='iderr':
                    self.compute = False
                    msg_lbl += '******* NO COMPUTE *******\n'
                    self.ch_autdisc.hide()
                    self.sp_nbplan.hide()
                    self.lb_disc.hide()
            self.lb_message.setText(msg_lbl)
        else:
            if self.pk_int is None:
                self.compute = False
                msg_lbl = 'WARNING: \n'
                msg_lbl += '  - No find pk interpolation'
                msg_lbl += '******* NO COMPUTE *******\n'

        if self.compute:
            msg_lbl = 'Interoplation between : \n'
            msg_lbl += '  - Upstream Profile : \n'
            msg_lbl += '     - name : {} \n'.format(dict_interp['up']['name'])
            msg_lbl += '     - gid : {} \n'.format(dict_interp['up']['id'])
            msg_lbl += '     - branch : {} \n'.format(dict_interp['up']['branch'])
            msg_lbl += '  - Downstream Profile : \n'
            msg_lbl += '     - name : {} \n'.format(dict_interp['down']['name'])
            msg_lbl += '     - gid : {} \n'.format(dict_interp['down']['id'])
            msg_lbl += '     - branch : {} \n'.format(dict_interp['down']['branch'])
            self.lb_message.setText(msg_lbl)


    def fct_autdisc(self):
        if self.ch_autdisc.isChecked():
            self.lb_disc.setEnabled(False)
            self.sp_nbplan.setEnabled(False)
        else:
            self.lb_disc.setEnabled(True)
            self.sp_nbplan.setEnabled(True)

    def accept_page(self):
        # save Info


        if self.compute :
            nplan_s = self.sp_nbplan.value()
            if self.ch_autdisc.isChecked():
                plani_s = self.plani
            else:
                plani_s = None
            cl_interp = ClassProfInterp(self.data, self.pk_int,
                                        nplan=nplan_s,plani=plani_s)

            cl_interp()

            self.interpol_prof = cl_interp.data['interp']




        self.accept()

    def reject_page(self):
        # print('cancel')
        self.reject()
