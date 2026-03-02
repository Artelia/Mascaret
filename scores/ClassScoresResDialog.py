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

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ScoreDistWidget import ScoreDistWidget
from .ScoreParamWidget import ScoreParamWidget
from .ScoreResWidget import ScoreResWidget


class ClassScoresResDialog:
    """
    GUI Class allow to compute scores
    """

    def __init__(self, parent):
        self.prt = parent
        self.mgis = parent.mgis
        self.mdb = self.mgis.mdb
        self.tabscores = self.prt.tabscores
        self.all = False

        self.lst_runs = []
        self.init_dates = []

        self.wgt_param = ScoreParamWidget(self, self.all)
        self.tab_param = self.tabscores.addTab(self.wgt_param, "scor_param")

        self.wgt_res = ScoreResWidget(self)
        self.tab_res = self.tabscores.addTab(self.wgt_res, "scor_res")
        id_res = self.tabscores.indexOf(self.wgt_res)
        self.tabscores.setTabEnabled(id_res, False)

        self.wgt_dist = ScoreDistWidget(self)
        self.tab_dist = self.tabscores.addTab(self.wgt_dist, "scor_dist")
        id_dist = self.tabscores.indexOf(self.wgt_dist)
        self.tabscores.setTabEnabled(id_dist, False)

        self.tabscores.currentChanged.connect(self.change_tab)

    def change_tab(self, index):
        if index == 2:
            self.wgt_dist.res = self.wgt_param.res
            self.wgt_dist.fill_tab()
        if index == 1:
            self.wgt_res.res = self.wgt_param.res
            self.wgt_res.fill_tab()

    def clear_scores(self):
        id_dist = self.tabscores.indexOf(self.wgt_dist)
        self.tabscores.setTabEnabled(id_dist, False)
        self.wgt_dist.fill_tab()
        id_res = self.tabscores.indexOf(self.wgt_res)
        self.tabscores.setTabEnabled(id_res, False)
        self.wgt_res.fill_tab()
