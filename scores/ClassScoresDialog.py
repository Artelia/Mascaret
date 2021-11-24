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
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from qgis.PyQt.QtWidgets import *

from .SelectWidget import SelectWidget
from .ScoreParamWidget import ScoreParamWidget
from .ScoreResallWidget import ScoreResallWidget
from .ScoreDistWidget import ScoreDistWidget


class ClassScoresDialog(QDialog):
    """
    GUI Class allow to compute scores
    """

    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.all = True
        self.old_index = 0
        self.lst_runs = []
        self.init_dates = []

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_scores.ui'), self)

        # self.tabscores
        self.bt_close.clicked.connect(self.close)
        self.bt_close.hide()
        self.wgt_select = SelectWidget(self)
        self.tab_select = self.tabscores.addTab(self.wgt_select, 'Scores Selection')

        self.wgt_param = ScoreParamWidget(self, self.all)
        self.tab_param = self.tabscores.addTab(self.wgt_param, 'Scores Parameters')

        self.wgt_res = ScoreResallWidget(self)
        self.tab_res = self.tabscores.addTab(self.wgt_res, 'Scores Results')
        id_res = self.tabscores.indexOf(self.wgt_res)
        self.tabscores.setTabEnabled(id_res, False)

        self.wgt_dist = ScoreDistWidget(self)
        self.tab_dist = self.tabscores.addTab(self.wgt_dist, 'Scores Distribution')
        id_dist = self.tabscores.indexOf(self.wgt_dist)
        self.tabscores.setTabEnabled(id_dist, False)

        self.tabscores.currentChanged.connect(self.change_tab)

    def change_tab(self, index):
        if index != 0:
            if self.old_index == 0:
                self.lst_runs = self.wgt_select.get_selection()
                self.wgt_param.ch_lst_run(self.lst_runs)
                self.wgt_param.all = True
                self.wgt_param.init_gui()
        if index == 3:
            self.wgt_dist.res = self.wgt_param.res
            self.wgt_dist.fill_tab()
        if index == 2:
            self.wgt_res.res = self.wgt_param.res
            self.wgt_res.fill_tab()

        self.old_index = index
