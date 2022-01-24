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
        self.list_var = []
        self.annotation = []
        self.annot_var = []
        self.courbeLaisses = []
        self.etiquetteLaisses = []
        self.litMineur = None
        self.stockgauche = None
        self.stockdroit = None
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
        self.courbeLaisses = []
        self.courbePlani = []
        self.etiquetteLaisses = []
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

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='pink',
                                 alpha=0.5, lw=1, zorder=80)
        self.litMineur = self.main_axe.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                 alpha=0.3, lw=1, zorder=80)
        self.stockgauche = self.main_axe.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                 alpha=0.3, lw=1, zorder=80)
        self.stockdroit = self.main_axe.add_patch(rect)

        self.aire = []

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

    def init_graph(self, lst_data, x_var, all_vis=True, lais=None):
        self.init_legende()
        self.set_data(lst_data, self.data_to_curve, x_var)

        if lais:
            handles = [c for c in self.ax[1]["curves"]]
            handles.append(
                mlines.Line2D([], [], color='darkcyan', marker='+', linewidth=0,
                              markersize=10, label='Flood marks'))
            self.ax[1]["curves"].append(self.courbeLaisses[0])
            self.init_legende(handles)

        idx = 0
        for data in lst_data:
            for var in data["y_var"]:
                axe, rg = self.data_to_curve[idx]
                courbe = self.ax[axe]["curves"][rg]
                courbe.set_data(data[data["x_var"]], data[var])
                courbe.set_visible(True)
                idx += 1

        if all_vis:
            for a in [1, 2]:
                if self.ax[a]["legend"]:
                    for lin in self.ax[a]["legend"].get_lines():
                        lin.set_alpha(1.0)

        self.maj_limites()

    def init_graph_profil(self, data, x_var, qmaj=0, plani=None):
        self.init_legende()
        self.set_data([{'x_var': 'x', 'y_var': ['ZREF'], 'y_unit': '$m$', 'x': data['x'], 'ZREF': data['ZREF']}],
                      {0: (1, 0)},
                      x_var)
        if plani:
            self.ax[1]["curves"].append(self.courbePlani[0])
            self.init_legende()

        if len(self.ax[1]["curves"]) > 0:
            for i, cb in enumerate(self.ax[1]["curves"]):
                if i == 0:
                    cb.set_data(data["x"], data['ZREF'])
                    cb.set_visible(True)
                elif i == 1:
                    # plani visible or not
                    cb.set_visible(False)
                else:
                    cb.set_visible(False)
        else:
            return

        for patch in self.aire:
            if patch in self.main_axe.patches:
                self.main_axe.patches.remove(patch)

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
        aire = self.main_axe.fill_between(data['x'], temp1, temp2,
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
                    self.main_axe.add_patch(patch)
                else:
                    if gauch <= x <= droit:
                        patch = patches.PathPatch(p,
                                                  facecolor='deepskyblue',
                                                  lw=0)
                        self.aire.append(patch)
                        self.main_axe.add_patch(patch)
                        break

        self.main_axe.collections.remove(aire)
        self.maj_limites()

    def insert_debord_curves(self, dict_debord):
        v = self.list_var[-1]["id"] + 1
        idx = 0

        for (id_debord, var), param_debord in dict_debord.items():
            self.list_var.append({"id": v, "name": var, "clr": "grey"})
            courbe_debord, = self.ax[param_debord["axe"]]["axe"].plot([], [],
                                                                      color="grey",
                                                                      marker='o',
                                                                      markeredgewidth=0,
                                                                      zorder=100 - v,
                                                                      linestyle=
                                                                      MPL_LINE_STYLE[
                                                                          idx + 1],
                                                                      label="overflow level - {0} ".format(
                                                                          id_debord))

            self.ax[param_debord["axe"]]["curves"].append(courbe_debord)
            self.data_to_curve[v] = (
                param_debord["axe"],
                len(self.ax[param_debord["axe"]]["curves"]) - 1)

            annot_var = self.ax[param_debord["axe"]]["axe"].annotate("",
                                                                     xy=(0, 0),
                                                                     ha='left',
                                                                     xytext=(
                                                                         10, 0),
                                                                     textcoords='offset points',
                                                                     va='top',
                                                                     bbox=dict(
                                                                         boxstyle='round, pad=0.5',
                                                                         fc='white',
                                                                         alpha=0.7),
                                                                     color="grey",
                                                                     visible=False,
                                                                     zorder=199 - v)
            self.annotation.append(annot_var)
            idx += 1
            v += 1

        self.maj_limites()

    def insert_obs_curves(self, dict_obs):
        v = self.list_var[-1]["id"] + 1
        idx = 0
        for (id_obs, var), param_obs in dict_obs.items():
            self.list_var.append({"id": v, "name": var, "clr": "grey"})
            courbe_obs, = self.ax[param_obs["axe"]]["axe"].plot([], [],
                                                                color="grey",
                                                                marker='o',
                                                                markeredgewidth=0,
                                                                zorder=100 - v,
                                                                linestyle=
                                                                MPL_LINE_STYLE[
                                                                    idx],
                                                                label="Obs {0} - {1}".format(
                                                                    id_obs,
                                                                    var))

            self.ax[param_obs["axe"]]["curves"].append(courbe_obs)
            self.data_to_curve[v] = (
                param_obs["axe"], len(self.ax[param_obs["axe"]]["curves"]) - 1)

            annot_var = self.ax[param_obs["axe"]]["axe"].annotate("", xy=(0, 0),
                                                                  ha='left',
                                                                  xytext=(
                                                                      10, 0),
                                                                  textcoords='offset points',
                                                                  va='top',
                                                                  bbox=dict(
                                                                      boxstyle='round, pad=0.5',
                                                                      fc='white',
                                                                      alpha=0.7),
                                                                  color="grey",
                                                                  visible=False,
                                                                  zorder=199 - v)
            self.annotation.append(annot_var)
            idx += 1
            v += 1

        self.maj_limites()

    def init_graph_plani(self, dict_plani):
        """ add flood mark in graph"""

        self.clear_plani()
        xfinal = []
        yfinal = []
        for name, param_plani in dict_plani.items():
            if param_plani:
                for line in param_plani['line']:
                    x, y = line.coords.xy
                    xfinal.extend(x)
                    yfinal.extend(y)
                    xfinal.append(None)
                    yfinal.append(None)

        cb, = self.main_axe.plot(xfinal, yfinal,
                                 color="grey",
                                 marker='',
                                 markeredgewidth=0,
                                 zorder=100 - self.list_var[-1]["id"] + 1,
                                 linestyle=MPL_LINE_STYLE[0],
                                 alpha=0.5,
                                 label="planimetry")
        self.courbePlani.append(cb)
        self.courbePlani[0].set_visible(True)

    def clear_plani(self):
        if self.ax[1]["curves"]:
            tmp = []
            for i, cb in enumerate(self.ax[1]["curves"]):
                if cb not in self.courbePlani:
                    tmp.append(cb)
                else:
                    cb.set_visible(False)
            self.ax[1]["curves"] = list(tmp)

        self.courbePlani = []

    def clear_laisse(self):
        """flood mark"""
        if self.ax[1]["curves"]:
            tmp = []
            for i, cb in enumerate(self.ax[1]["curves"]):
                if cb not in self.courbeLaisses:
                    tmp.append(cb)
                else:
                    cb.set_visible(False)
            self.ax[1]["curves"] = list(tmp)

        self.courbeLaisses = []
        for e in self.etiquetteLaisses:
            self.main_axe.texts.remove(e)
        self.etiquetteLaisses = []
        # self.canvas.draw()

    def init_graph_laisse(self, laisses):
        """ add flood mark in graph"""

        self.clear_laisse()

        self.courbeLaisses.append(
            self.main_axe.scatter(laisses['x'], laisses['z'],
                                  color=laisses["couleurs"],
                                  marker='+',
                                  label="Flood marks",
                                  s=80,
                                  linewidth=laisses[
                                      'taille']))

        self.courbeLaisses[0].set_visible(True)
        for x, z, c in zip(laisses['x'], laisses['z'], laisses["couleurs"]):
            temp = self.main_axe.annotate(str(z), xy=(x, z), xytext=(3, 3),
                                          ha='left', va='bottom',
                                          fontsize='x-small',
                                          color=c,
                                          textcoords='offset points',
                                          clip_on=True)

            self.etiquetteLaisses.append(temp)
