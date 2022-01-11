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

MPL_LINE_STYLE = {0: '-', 1: ':', 2: '--', 3: '-.'}

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

    def init_mdl(self, lst_vars, lst_lbls, lst_colors, lst_line_style, lst_axe,
                 unit_y, title_y=None):
        self.list_var.clear()
        self.annotation.clear()
        self.data_to_curve.clear()

        self.ax = {1: {"axe": None, "curves": [], "labels": [], "lined": {},
                       "legend": None},
                   2: {"axe": None, "curves": [], "labels": [], "lined": {},
                       "legend": None}}

        self.fig.clf()
        self.ax[1]["axe"] = self.fig.add_subplot(111)
        self.main_axe = self.ax[1]["axe"]
        if lst_axe:
            if max(lst_axe) == 2:
                self.ax[2]["axe"] = self.ax[1]["axe"].twinx()

        self.annot_var = self.main_axe.annotate("", xy=(0, 0), ha='left',
                                                xytext=(10, 0),
                                                textcoords='offset points',
                                                va='top',
                                                bbox=dict(
                                                    boxstyle='round, pad=0.5',
                                                    fc='white', alpha=0.7),
                                                color='black', visible=False,
                                                zorder=200)
        self.annotation.append(self.annot_var)
        for v, var in enumerate(lst_vars):
            self.list_var.append({"id": v, "name": var, "clr": lst_colors[v]})
            courbe_var, = self.ax[lst_axe[v]]["axe"].plot([], [],
                                                          color=lst_colors[v],
                                                          linestyle=
                                                          MPL_LINE_STYLE[
                                                              lst_line_style[
                                                                  v]],
                                                          zorder=100 - v,
                                                          label=lst_lbls[v])
            self.ax[lst_axe[v]]["curves"].append(courbe_var)
            self.data_to_curve[v] = (
                lst_axe[v], len(self.ax[lst_axe[v]]["curves"]) - 1)

            annot_var = self.ax[lst_axe[v]]["axe"].annotate("", xy=(0, 0),
                                                            ha='left',
                                                            xytext=(10, 0),
                                                            textcoords='offset points',
                                                            va='top', bbox=dict(
                    boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                                            color=lst_colors[v],
                                                            visible=False,
                                                            zorder=199 - v)
            self.annotation.append(annot_var)

        for id_ax, ax in self.ax.items():
            if ax["axe"]:
                ax["axe"].tick_params(axis='both', labelsize=7.)
                ax["axe"].grid(True, linestyle=MPL_LINE_STYLE[id_ax - 1])

        if title_y:
            for idx in range(2):
                if self.ax[idx + 1]["axe"]:
                    txt_ylabel = r''
                    if title_y[idx] is not None:
                        txt_ylabel += r'{} '.format(title_y[idx])
                        if unit_y[idx] != '':
                            txt_ylabel += r'({}) '.format(unit_y[idx])
                    self.ax[idx + 1]["axe"].set_ylabel(txt_ylabel)

        self.v_line = self.main_axe.axvline(color="black")


    def init_graph_obs(self, data):
        self.init_legende()
        if len(self.ax[1]["curves"]) > 0:
            for i, cb in enumerate(self.ax[1]["curves"]):
                cb.set_data(data["date"], data['val'])
                cb.set_visible(True)

        else:
            return


        self.maj_limites()

    def init_graph_laws(self, data):
        self.init_legende()
        if len(self.ax[1]["curves"]) > 0:
            for i, cb in enumerate(self.ax[1]["curves"]):
                cb.set_data(data["date"], data['val'])
                cb.set_visible(True)

        else:
            return


        self.maj_limites()