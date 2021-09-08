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
from .ScoreResWidget import ScoreResWidget
from .ScoreDistWidget import ScoreDistWidget



class ClassScoresDialog(QDialog):
    """
    GUI Class allow to compute scores
    """

    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb


        self.lst_runs =  []

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_scores.ui'), self)

        #self.tabscores
        self.bt_close.clicked.connect(self.close)
        self.wgt_select = SelectWidget(self)
        self.tab_select = self.tabscores.addTab(self.wgt_select,'scor_select')

        self.wgt_param = ScoreParamWidget(self)
        self.tab_param = self.tabscores.addTab(self.wgt_param, 'scor_param')

        self.wgt_res= ScoreResWidget(self)
        self.tab_res = self.tabscores.addTab(self.wgt_res, 'scor_res')

        self.wgt_dist = ScoreDistWidget(self)
        self.tab_dist = self.tabscores.addTab(self.wgt_dist, 'scor_dist')


        self.tabscores.currentChanged.connect(self.change_tab)

        #

    def change_tab(self):
        print(self.tabscores.currentIndex())
        if self.tabscores.currentIndex() != 0 :
            self.lst_runs = self.wgt_select.get_selection()

        print( self.lst_runs)




