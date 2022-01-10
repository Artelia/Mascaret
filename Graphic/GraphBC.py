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

from .GraphCommon import GraphCommonNew

class GraphBC(GraphCommonNew):
    def __init__(self, wgt=None, lay=None, lay_toolbar=None):
        GraphCommonNew.__init__(self, wgt, lay, lay_toolbar)
        self.list_var = []
        self.annotation = []
        self.annot_var = []
        self.aire = []
        self.v_line = None
        self.data_to_curve = dict()

        self.init_ui()

    def init_ui(self):
        self.init_ui_common_p()

    def init_graph(self, lst_data, x_var, all_vis=True):
        # TODO
        pass
        # self.init_legende()
        #
        # idx = 0
        # for data in lst_data:
        #     for var in data["y_var"]:
        #         axe, rg = self.data_to_curve[idx]
        #         courbe = self.ax[axe]["curves"][rg]
        #         courbe.set_data(data[data["x_var"]], data[var])
        #         courbe.set_visible(True)
        #         idx += 1
        #
        # if all_vis:
        #     for a in [1, 2]:
        #         if self.ax[a]["legend"]:
        #             for lin in self.ax[a]["legend"].get_lines():
        #                 lin.set_alpha(1.0)
        #
        # self.maj_limites()