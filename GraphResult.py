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
from matplotlib import patches
import numpy as np
import matplotlib.lines as mlines

MPL_LINE_STYLE = {0: '-', 1: ':', 2: '--', 3: '-.'}

class GraphResult(GraphCommonNew):
    def __init__(self, wgt=None, lay=None, lay_toolbar=None):
        GraphCommonNew.__init__(self, wgt, lay, lay_toolbar)
        self.axes = None
        self.list_var = []
        self.courbes = []
        self.annotation = []
        self.annot_var = []
        self.courbeLaisses = []
        self.etiquetteLaisses = []
        self.courbeObs = None
        self.litMineur = None
        self.stockgauche = None
        self.stockdroit = None
        self.aire = []
        self.v_line = None

        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.init_ui_common_p()

    def init_mdl(self, lst_vars, lst_lbls, lst_colors, lst_line_style, unit_y, name=None):
        self.axes.cla()
        self.list_var = []
        self.courbes = []
        self.annotation = []
        self.unit_y = unit_y

        self.annot_var = self.axes.annotate("", xy=(0, 0), ha='left', xytext=(10, 0), textcoords='offset points', va='top',
                                            bbox=dict(boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                            color='black', visible=False, zorder=200)
        self.annotation.append(self.annot_var)
        self.courbeLaisses = []
        self.etiquetteLaisses = []
        for v, var in enumerate(lst_vars):
            self.list_var.append({"id": v, "name": var, "clr": lst_colors[v]})
            courbe_var, = self.axes.plot([], [], color=lst_colors[v], linestyle=MPL_LINE_STYLE[lst_line_style[v]], zorder=100 - v, label=lst_lbls[v])
            self.courbes.append(courbe_var)
            annot_var = self.axes.annotate("", xy=(0, 0), ha='left', xytext=(10, 0), textcoords='offset points', va='top',
                                           bbox=dict(boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                           color=lst_colors[v], visible=False, zorder=199 - v)
            self.annotation.append(annot_var)

        self.courbeObs, = self.axes.plot([], [], color='grey', marker='o', markeredgewidth=0, zorder=90, label='Observation')
        self.courbeObs.set_visible(False)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='pink', alpha=0.5, lw=1, zorder=80)
        self.litMineur = self.axes.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green', alpha=0.3, lw=1, zorder=80)
        self.stockgauche = self.axes.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green', alpha=0.3, lw=1, zorder=80)
        self.stockdroit = self.axes.add_patch(rect)

        self.aire = []

        self.axes.tick_params(axis='both', labelsize=7.)

        txt_ylabel = r''
        if name:
            txt_ylabel += r'{} '.format(name)
            if self.unit_y != '':
                txt_ylabel += r'({}) '.format(self.unit_y)
        self.axes.set_ylabel(txt_ylabel)

        self.axes.grid(True)
        self.v_line = self.axes.axvline(color="black")
        #self.init_legende()

    def init_graph(self, lst_data, x_var, all_vis=True, lais=None):
        self.init_legende()
        #self.set_data(data, x_var)
        #handles = None
        if lais:
            handles = [c for c in self.courbes]
            handles.append(mlines.Line2D([], [], color='darkcyan', marker='+', linewidth=0, markersize=10, label='Flood marks'))
            self.courbes.append(self.courbeLaisses[0])
            self.init_legende(handles)

        leglines = self.leg.get_lines()
        idx = 0
        for data in lst_data:
            for var in data["y_var"]:
                self.courbes[idx].set_data(data[data["x_var"]], data[var])
                if all_vis:
                    self.courbes[idx].set_visible(True)
                    leglines[idx].set_alpha(1.0)
                idx += 1

        # for v, var in enumerate(self.list_var):
        #     self.courbes[v].set_data(data[x_var], data[var["name"]])
        #     if all_vis:
        #         self.courbes[v].set_visible(True)
        #         leglines[v].set_alpha(1.0)

        self.maj_limites()

    def init_graph_profil(self, data, x_var, qmaj=0):
        self.init_legende()
        self.set_data(data, x_var)
        if len(self.courbes) > 0:
            for i, cb in enumerate(self.courbes):
                if i == 0:
                    cb.set_data(data["x"], data['ZREF'])
                    cb.set_visible(True)
                else:
                    cb.set_visible(False)
        else:
            return

        for patch in self.aire:
            if patch in self.axes.patches:
                self.axes.patches.remove(patch)

        if data['x'] and data['leftminbed'] and data['rightminbed']:
            self.litMineur.set_x(data['leftminbed'])
            self.litMineur.set_width(data['rightminbed'] - data['leftminbed'])
            self.litMineur.set_visible(True)
        else:
            self.litMineur.set_visible(False)

        if data['x'] and data["leftstock"]:
            mini = min(data['x'])
            self.stockgauche.set_x(mini)
            self.stockgauche.set_width(data['leftstock'] - mini)
            self.stockgauche.set_visible(True)
        else:
            self.stockgauche.set_visible(False)

        if data['x'] and data["rightstock"]:
            self.stockdroit.set_x(data['rightstock'])
            self.stockdroit.set_width(max(data['x']) - data['rightstock'])
            self.stockdroit.set_visible(True)
        else:
            self.stockdroit.set_visible(False)

        temp1 = np.array(data['ZREF'])
        temp2 = np.array(data['Z'])
        aire = self.axes.fill_between(data['x'], temp1, temp2,
                                      where=temp2 >= temp1,
                                      interpolate=True)

        self.aire = []

        for p in aire.get_paths():
            if data['leftminbed'] is not None:
                gauch = data['leftminbed']
            else:
                gauch = min(p.vertices[:, 0])
            if data['rightminbed'] is not None:
                droit = data['rightminbed']
            else:
                droit = max(p.vertices[:, 0])

            for x, y in p.vertices:
                # trace lit mineur

                if qmaj > 0.001:
                    patch = patches.PathPatch(p,
                                              facecolor='deepskyblue',
                                              lw=0)
                    self.aire.append(patch)
                    self.axes.add_patch(patch)
                else:
                    if gauch <= x <= droit:
                        patch = patches.PathPatch(p,
                                                  facecolor='deepskyblue',
                                                  lw=0)
                        self.aire.append(patch)
                        self.axes.add_patch(patch)
                        break

        self.axes.collections.remove(aire)

        self.maj_limites()

    def insert_obs_curves(self, dict_obs):
        v = self.list_var[-1]["id"] + 1
        idx = 0
        for (id_obs, var), param_obs in dict_obs.items():
            self.list_var.append({"id": v, "name": var, "clr": "grey"})
            courbe_obs, = self.axes.plot([], [], color="grey", marker='o', markeredgewidth=0, zorder=100 - v,
                                         linestyle=MPL_LINE_STYLE[idx], label="Obs {0} - {1}".format(id_obs, var))
            self.courbes.append(courbe_obs)
            annot_var = self.axes.annotate("", xy=(0, 0), ha='left', xytext=(10, 0), textcoords='offset points', va='top',
                                           bbox=dict(boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                           color="grey", visible=False, zorder=199 - v)
            self.annotation.append(annot_var)
            idx += 1
            v += 1

        self.maj_limites()

    def clear_laisse(self):
        """flood mark"""
        if self.courbes:
            tmp = []
            for i, cb in enumerate(self.courbes):
                if cb not in self.courbeLaisses:
                    tmp.append(cb)
                else:
                    cb.set_visible(False)
            self.courbes = list(tmp)

        self.courbeLaisses = []
        for e in self.etiquetteLaisses:
            self.axes.texts.remove(e)
        self.etiquetteLaisses = []
        # self.canvas.draw()

    def init_graph_laisse(self, laisses):
        """ add flood mark in graph"""

        self.clear_laisse()

        self.courbeLaisses.append(self.axes.scatter(laisses['x'], laisses['z'],
                                                    color=laisses["couleurs"],
                                                    marker='+',
                                                    label="Flood marks",
                                                    s=80,
                                                    linewidth=laisses[
                                                        'taille']))

        self.courbeLaisses[0].set_visible(True)
        for x, z, c in zip(laisses['x'], laisses['z'], laisses["couleurs"]):
            temp = self.axes.annotate(str(z), xy=(x, z), xytext=(3, 3),
                                      ha='left', va='bottom',
                                      fontsize='x-small',
                                      color=c,
                                      textcoords='offset points', clip_on=True)

            self.etiquetteLaisses.append(temp)

    def clear_obs(self):
        """ clean obs graph"""
        self.courbeObs.set_data([], [])
        self.courbeObs.set_visible(False)
        if self.courbes:
            tmp = []
            for i, cb in enumerate(self.courbes):
                if cb is not self.courbeObs:
                    tmp.append(cb)
            self.courbes = list(tmp)
        self.init_legende()

    def init_graph_obs(self, obs):
        self.courbeObs.set_data(obs['date'], obs['valeur'])
        self.courbeObs.set_visible(True)
        self.courbes.append(self.courbeObs)