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

from qgis.PyQt.QtWidgets import *

try:
    from matplotlib.backends.backend_qt5agg \
        import FigureCanvasQTAgg as FigureCanvas
except:
    from matplotlib.backends.backend_qt5agg \
        import FigureCanvasQT as FigureCanvas
# ***************************
try:
    from matplotlib.backends.backend_qt5agg \
        import NavigationToolbar2QTAgg as NavigationToolbar
except:
    from matplotlib.backends.backend_qt5agg \
        import NavigationToolbar2QT as NavigationToolbar

from matplotlib import pyplot
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from ..WaterQuality.ClassTableWQ import ClassTableWQ
from datetime import datetime

# **************************************************

try:
    _encoding = QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


class GraphCommon(QWidget):
    def __init__(self, mgis=None):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.dossierPlugin = self.mgis.masplugPath
        self.dossierProjet = self.mgis.repProject
        self.unit = 'date'
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)

        self.tbwq = ClassTableWQ(self.mgis, self.mdb)

        self.courbes = []
        self.gid = 0
        self.coucheProfils = None
        self.liste = {}
        self.position = 0
        self.nom = ''
        self.leg = None
        self.lined = dict()

    def init_ui_common_p(self):
        self.courbes = []

    def init_ui_prof(self, gid):
        """variables in common for profile graphics"""
        self.gid = gid
        self.coucheProfils = self.mgis.coucheProfils
        # try:
        self.liste = self.mdb.select("profiles", "", "abscissa")
        # except:
        #     self.mgis.add_info("Error Select profils")

        self.position = self.liste["gid"].index(self.gid)
        self.feature = {k: v[self.position] for k, v in self.liste.items()}
        self.nom = self.feature['name']

        self.courbes = []

    def gui_graph(self, lay_graph, lay_toolbar=None):
        lay_graph.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        if lay_toolbar is not None:
            lay_toolbar.addWidget(self.toolbar)
        else:
            lay_graph.addWidget(self.toolbar)

    def onpick(self, event):
        legline = event.artist
        btn = event.mouseevent.button
        if btn == 1 and legline in self.lined.keys():
            courbe = self.lined[legline]
            vis = not courbe.get_visible()
            courbe.set_visible(vis)
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)
            self.maj_limites()

    def init_legende(self):
        liste_noms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, liste_noms, loc='upper right',
                                    fancybox=False, shadow=False, fontsize=7.)
        self.leg.get_frame().set_alpha(0.4)
        self.leg.set_zorder(110)
        # self.leg.draggable(True)
        DraggableLegend(self.leg)
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(5)
            legline.set_linewidth(3)
            self.lined[legline] = courbe

    def maj_unit_x(self, unit):
        self.unit = unit
        self.axes.set_xlabel("time ({})".format(unit))
        if self.unit != 'date':
            self.axes.xaxis.set_major_formatter(ticker.ScalarFormatter())
        else:
            self.axes.xaxis.set_major_formatter(
                mdates.DateFormatter('%d-%m-%Y'))

    def maj_courbes(self, courbes):
        for c in courbes.keys():
            self.courbes[c].set_data(courbes[c]["x"], courbes[c]["y"])

        self.maj_limites()

    def maj_limites(self, marge=0.05):
        no_data = True
        mini_x = 999999.
        maxi_x = -999999.
        mini_z = 999999.
        maxi_z = -999999.

        for courbe in self.courbes:
            if courbe.get_visible():
                lx, lz = courbe.get_data()
                lx = [x for x in lx if x is not None]
                lz = [z for z in lz if z is not None]
                if lx and lz:
                    no_data = False
                    mini_x = min(mini_x, min(lx))
                    maxi_x = max(maxi_x, max(lx))
                    mini_z = min(mini_z, min(lz))
                    maxi_z = max(maxi_z, max(lz))

        d = max(abs(mini_z), abs(maxi_z)) * marge
        mini_z -= d
        maxi_z += d

        if no_data:
            if self.unit != 'date':
                self.axes.set_xlim(0., 1.)
                self.axes.set_ylim(0., 1.)
            else:
                self.axes.set_xlim(1., 2.)
                self.axes.set_ylim(1., 2.)
        else:
            self.axes.set_xlim(mini_x, maxi_x)
            self.axes.set_ylim(mini_z, maxi_z)

        self.fig.autofmt_xdate()
        self.canvas.draw()


class DraggableLegend:
    def __init__(self, legend):
        self.legend = legend
        self.gotLegend = False
        self.mouse_x = None
        self.mouse_y = None
        self.legend_x = None
        self.legend_y = None
        legend.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        legend.figure.canvas.mpl_connect('pick_event', self.on_pick)
        legend.figure.canvas.mpl_connect('button_release_event',
                                         self.on_release)
        legend.set_picker(self.my_legend_picker)

    def on_motion(self, evt):
        if self.gotLegend:
            dx = evt.x - self.mouse_x
            dy = evt.y - self.mouse_y
            loc_in_canvas = self.legend_x + dx, self.legend_y + dy
            loc_in_norm_axes = self.legend.parent.transAxes.inverted().transform_point(
                loc_in_canvas)
            self.legend._loc = tuple(loc_in_norm_axes)
            self.legend.figure.canvas.draw()

    def my_legend_picker(self, legend, evt):
        return self.legend.legendPatch.contains(evt)

    def on_pick(self, evt):
        if evt.artist == self.legend:
            bbox = self.legend.get_window_extent()
            self.mouse_x = evt.mouseevent.x
            self.mouse_y = evt.mouseevent.y
            self.legend_x = bbox.xmin
            self.legend_y = bbox.ymin
            self.gotLegend = 1

    def on_release(self, event):
        if self.gotLegend:
            self.gotLegend = False


class GraphCommonNew:
    def __init__(self, wgt=None, lay=None, lay_toolbar=None):
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.gui_graph(wgt, lay, lay_toolbar)
        self.leg_selected = False
        self.data = None
        self.data_to_curve = None
        self.var_x = None
        self.unit_x = "num"
        self.unit_y = None
        self.flood_mark = False
        self.obs = False
        self.update_limites = True
        self.list_var = []
        self.courbes = []
        self.annotation = []
        self.courbeLaisses = []
        self.etiquetteLaisses = []
        self.flag = False
        self.leg = None
        self.lined = dict()
        self.unit = ''

    def init_ui_common_p(self):
        self.list_var = []
        self.courbes = []
        self.annotation = []
        self.courbeLaisses = []

        self.fig.canvas.mpl_connect('button_release_event',
                                    self.graph_off_click)
        self.fig.canvas.mpl_connect('button_press_event', self.graph_on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.graph_on_press)
        self.fig.canvas.mpl_connect('pick_event', self.graph_on_pick)

    def gui_graph(self, wgt, lay_graph, lay_toolbar=None):
        lay_graph.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, wgt)
        if lay_toolbar is not None:
            lay_toolbar.addWidget(self.toolbar)
        else:
            lay_graph.addWidget(self.toolbar)

    def set_data(self, data, data_to_curve, var_x):
        self.data = data
        self.data_to_curve = data_to_curve
        self.var_x = var_x

    def graph_on_pick(self, evt):
        lst_leg = list()
        d_lined = dict()
        for ax in self.ax.values():
            lst_leg.append(ax["legend"])
            for l, c in ax["lined"].items():
                d_lined[l] = c

        art = evt.artist
        if art in lst_leg:
            self.leg_selected = True
        elif art in d_lined.keys():
            btn = evt.mouseevent.button
            if btn == 1:
                courbe = d_lined[art]
                vis = not courbe.get_visible()
                courbe.set_visible(vis)
                if vis:
                    art.set_alpha(1.0)
                    if courbe.get_label() == "Flood marks":
                        for e in self.etiquetteLaisses:
                            e.set_visible(True)
                else:
                    art.set_alpha(0.2)
                    if courbe.get_label() == "Flood marks":
                        for e in self.etiquetteLaisses:
                            e.set_visible(False)
                self.maj_limites()

    def graph_on_click(self, evt):
        if (not self.leg_selected) and self.data:
            self.flag = True
            if evt.button == 1:
                self.affiche_cadre(evt)
                self.fig.canvas.draw()

    def graph_off_click(self, event):
        if (not self.leg_selected) and self.data:
            for a in self.annotation:
                a.set_visible(False)
            self.v_line.set_visible(False)
            self.flag = False
            self.canvas.draw()
        self.leg_selected = False

    def graph_on_press(self, event):
        if (not self.leg_selected) and self.data:
            if event.button == 1 and self.flag:
                self.affiche_cadre(event)

    def affiche_cadre(self, event):
        no_tool = True
        for c in self.toolbar.findChildren(QToolButton):
            if c.isChecked():
                no_tool = False
                break

        if not no_tool or not event.inaxes:
            for a in self.annotation:
                a.set_visible(False)
            self.v_line.set_visible(False)
            self.canvas.draw()
            return

        absc = event.xdata
        if self.unit_x == 'date':
            cur_x = datetime.utcfromtimestamp(
                round((absc) * 24) * 3600)
            # cur_x = datetime.utcfromtimestamp(
            #     round((absc - 719163) * 24) * 3600)
            txt_x = cur_x
        else:
            cur_x = absc
            txt_x = round(cur_x, 0)

        ymin, ymax = self.main_axe.get_ylim()
        annot = self.annotation[0]
        annot.set_text("{}".format(txt_x))
        annot.xytext = (10, 20)
        annot.xy = (absc, ymin)
        annot.set_visible(True)

        idx_c = 0
        for d in self.data:
            for var in d["y_var"]:
                annot = self.annotation[idx_c + 1]
                axe, rg = self.data_to_curve[idx_c]
                curv = self.ax[axe]["curves"][rg]
                if curv.get_visible():
                    if min(d[d["x_var"]]) <= cur_x <= max(d[d["x_var"]]):
                        val_t = min(d[d["x_var"]], key=lambda x: abs(x - cur_x))
                        idx_d = d[d["x_var"]].index(val_t)
                        val = d[var][idx_d]
                        annot.set_text(
                            "{} {}".format(round(val, 3), d["y_unit"]))
                        annot.xy = (absc, val)
                        annot.set_visible(True)
                    else:
                        annot.set_visible(False)
                else:
                    annot.set_visible(False)
                idx_c += 1

        self.v_line.set_xdata(absc)
        self.v_line.set_visible(True)
        self.canvas.draw()

    def init_legende(self, handles=None):
        all_handles, all_noms, all_curves = list(), list(), list()

        ax_max = 0
        for id_ax, ax in self.ax.items():
            if ax["axe"]:
                ax_max = id_ax
                if id_ax == 1:
                    if not handles:
                        handles = ax["curves"]
                else:
                    handles = ax["curves"]
                all_handles.extend(handles)

                liste_noms = []
                for c in ax["curves"]:
                    if c.get_visible():
                        liste_noms.append(c.get_label())
                all_noms.extend(liste_noms)

                all_curves.extend(ax["curves"])

        ax = self.ax[ax_max]
        ax["legend"] = ax["axe"].legend(all_handles, all_noms,
                                        loc='upper right', fancybox=False,
                                        shadow=False, fontsize=7.,
                                        handlelength=4)
        ax["legend"].get_frame().set_alpha(0.4)
        ax["legend"].set_zorder(111 - id_ax)
        ax["legend"].set_draggable(True)

        ax["lined"].clear()
        for legline, courbe in zip(ax["legend"].get_lines(), all_curves):
            legline.set_picker(5)
            legline.set_linewidth(3)
            ax["lined"][legline] = courbe

    def maj_unit_x(self, unit):
        self.unit = unit
        self.main_axe.set_xlabel("time ({})".format(unit))
        if self.unit == 'date':
            self.unit_x = 'date'
            self.main_axe.xaxis.set_major_formatter(
                mdates.DateFormatter('%d-%m-%Y'))
        else:
            self.unit_x = 'num'
            self.main_axe.xaxis.set_major_formatter(ticker.ScalarFormatter())

    def maj_courbes(self, courbes):
        for c in courbes.keys():
            self.courbes[c].set_data(courbes[c]["x"], courbes[c]["y"])
        self.maj_limites()

    def maj_limites(self):
        if self.update_limites:
            fst_x = True
            no_data = True
            for id_ax, ax in self.ax.items():
                if ax["axe"]:
                    fst_z = True
                    for courbe in ax["curves"]:
                        if courbe.get_visible():
                            try:
                                lx, lz = courbe.get_data()
                                lx = [x for x in lx if x is not None]
                                lz = [z for z in lz if z is not None]
                                if lx and lz:
                                    no_data = False
                                    if fst_x:
                                        fst_x = False
                                        mini_x = min(lx)
                                        maxi_x = max(lx)
                                    else:
                                        mini_x = min(mini_x, min(lx))
                                        maxi_x = max(maxi_x, max(lx))

                                    if fst_z:
                                        fst_z = False
                                        mini_z = min(lz) - 1
                                        maxi_z = max(lz) + 1
                                    else:
                                        mini_z = min(mini_z, min(lz) - 1)
                                        maxi_z = max(maxi_z, max(lz) + 1)
                            except AttributeError as e:
                                pass

                    if no_data:
                        ax["axe"].set_ylim(0., 1.)
                    else:
                        ax["axe"].set_ylim(mini_z, maxi_z)

            if no_data:
                self.main_axe.set_xlim(0., 1.)
            else:
                self.main_axe.set_xlim(mini_x, maxi_x)

        self.fig.autofmt_xdate()
        self.canvas.draw()

# class DraggableLegendNew:
#     def __init__(self, axes):
#         self.legend = dict()
#         for ax in axes.values():
#             if ax["legend"]:
#                 self.legend[ax["legend"]] = {"gotLegend": False, "mouse_x": None, "mouse_y": None,
#                                              "legend_x": None, "legend_y": None}
#         # self.legend = legend
#         # self.gotLegend = False
#         # self.mouse_x = None
#         # self.mouse_y = None
#         # self.legend_x = None
#         # self.legend_y = None
#
#         fst = True
#         for leg in self.legend.keys():
#             if fst:
#                 fst = False
#                 leg.figure.canvas.mpl_connect('motion_notify_event', self.lgd_on_motion)
#                 leg.figure.canvas.mpl_connect('pick_event', self.lgd_on_pick)
#                 leg.figure.canvas.mpl_connect('button_release_event', self.lgd_on_release)
#                 leg.set_picker(self.my_legend_picker)
#
#     def my_legend_picker(self, legend, evt):
#         return legend.legendPatch.contains(evt)
#
#     def lgd_on_pick(self, evt):
#         btn = evt.mouseevent.button
#         if btn == 1:
#             art = evt.artist
#             if art in self.legend.keys():
#                 bbox = art.get_window_extent()
#                 param_leg = self.legend[art]
#                 param_leg["mouse_x"] = evt.mouseevent.x
#                 param_leg["mouse_y"] = evt.mouseevent.y
#                 param_leg["legend_x"] = bbox.xmin
#                 param_leg["legend_y"] = bbox.ymin
#                 param_leg["gotLegend"] = 1
# 
#     def lgd_on_release(self, evt):
#         for leg, param in self.legend.items():
#             if param["gotLegend"]:
#                 param["gotLegend"] = False
#
#     def lgd_on_motion(self, evt):
#         for leg, param in self.legend.items():
#             if param["gotLegend"]:
#                 dx = evt.x - param["mouse_x"]
#                 dy = evt.y - param["mouse_y"]
#                 loc_in_canvas = param["legend_x"] + dx, param["legend_y"] + dy
#                 loc_in_norm_axes = leg.parent.transAxes.inverted().transform_point(loc_in_canvas)
#                 leg._loc = tuple(loc_in_norm_axes)
#                 leg.figure.canvas.draw()
