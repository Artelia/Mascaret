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

if int(qVersion()[0])<5:   #qt4
    from qgis.PyQt.QtGui import *
    try:
        from matplotlib.backends.backend_qt4agg \
            import FigureCanvasQTAgg as FigureCanvas
    except:
        from matplotlib.backends.backend_qt4agg \
            import FigureCanvasQT as FigureCanvas
    # ***************************
    try:
        from matplotlib.backends.backend_qt4agg \
            import NavigationToolbar2QTAgg as NavigationToolbar
    except:
        from matplotlib.backends.backend_qt4agg \
            import NavigationToolbar2QT as NavigationToolbar
else: #qt4
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
# **************************************************

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from .WaterQuality.ClassTableWQ import ClassTableWQ

class GraphCommon(QDialog):
    def __init__(self, mgis=None):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.dossierPlugin = self.mgis.masplugPath
        self.dossierProjet = self.mgis.repProject
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)

        self.tbwq = ClassTableWQ(self.mgis, self.mdb)

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
        if lay_toolbar != None:
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
        listeNoms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, listeNoms, loc='upper right',
                                    fancybox=False, shadow=False, fontsize=7.)
        self.leg.get_frame().set_alpha(0.4)
        self.leg.set_zorder(110)
        #self.leg.draggable(True)
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
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

    def maj_courbes(self, courbes):
        for c in courbes.keys():
            self.courbes[c].set_data(courbes[c]["x"], courbes[c]["y"])

        self.maj_limites()

    def maj_limites(self):
        no_data = True
        miniX = 999999.
        maxiX = -999999.
        miniZ = 999999.
        maxiZ = -999999.

        for courbe in self.courbes:
            if courbe.get_visible():
                lx, lz = courbe.get_data()
                lx = [x for x in lx if x is not None]
                lz = [z for z in lz if z is not None]
                if lx and lz:
                    no_data = False
                    miniX = min(miniX, min(lx))
                    maxiX = max(maxiX, max(lx))
                    miniZ = min(miniZ, min(lz) - 1)
                    maxiZ = max(maxiZ, max(lz) + 1)

        if no_data:
            self.axes.set_xlim(0., 1.)
            self.axes.set_ylim(0., 1.)
        else:
            self.axes.set_xlim(miniX, maxiX)
            self.axes.set_ylim(miniZ, maxiZ)

        self.fig.autofmt_xdate()
        self.canvas.draw()


class DraggableLegend:
    def __init__(self, legend):
        self.legend = legend
        self.gotLegend = False
        legend.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        legend.figure.canvas.mpl_connect('pick_event', self.on_pick)
        legend.figure.canvas.mpl_connect('button_release_event', self.on_release)
        legend.set_picker(self.my_legend_picker)

    def on_motion(self, evt):
        if self.gotLegend:
            dx = evt.x - self.mouse_x
            dy = evt.y - self.mouse_y
            loc_in_canvas = self.legend_x + dx, self.legend_y + dy
            loc_in_norm_axes = self.legend.parent.transAxes.inverted().transform_point(loc_in_canvas)
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






class GraphCommonNew():
    def __init__(self, lay=None, wgt=None):
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.gui_graph(wgt, lay)
        self.leg_selected = False
        self.data = None
        self.var_x = None
        self.unit_x = "num"
        self.unit_y = None

    def init_ui_common_p(self):
        self.list_var = []
        self.courbes = []
        self.annotation = []
        self.fig.canvas.mpl_connect('button_release_event', self.graph_off_click)
        self.fig.canvas.mpl_connect('button_press_event', self.graph_on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.graph_on_press)
        self.fig.canvas.mpl_connect('pick_event', self.graph_on_pick)

    def gui_graph(self, wgt, lay_graph, lay_toolbar=None):
        lay_graph.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, wgt)
        if lay_toolbar != None:
            lay_toolbar.addWidget(self.toolbar)
        else:
            lay_graph.addWidget(self.toolbar)

    def set_data(self, data, var_x):
        self.data = data
        self.var_x = var_x

    def graph_on_pick(self, evt):
        art = evt.artist
        if art == self.leg:
            self.leg_selected = True
        elif art in self.lined.keys():
            btn = evt.mouseevent.button
            if btn == 1:
                courbe = self.lined[art]
                vis = not courbe.get_visible()
                courbe.set_visible(vis)
                if vis:
                    art.set_alpha(1.0)
                else:
                    art.set_alpha(0.2)
                self.maj_limites()

    def graph_on_click(self, evt):
        if (not self.leg_selected) and (self.data):
            self.flag = True
            if evt.button == 1:
                self.affiche_cadre(evt)
                self.fig.canvas.draw()

    def graph_off_click(self, event):
        if (not self.leg_selected) and (self.data):
            for a in self.annotation:
                a.set_visible(False)
            self.v_line.set_visible(False)
            self.flag = False
            self.canvas.draw()
        self.leg_selected = False

    def graph_on_press(self, event):
        if (not self.leg_selected) and (self.data):
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

        if self.unit_x == 'date':
            temp = round((event.xdata - 719163) * 24) * 3600
            decal = datetime.utcfromtimestamp(temp)
            absc = min(self.data[self.var_x], key=lambda x: abs(x - decal))
        else:
            absc = min(self.data[self.var_x], key=lambda x: abs(x - event.xdata))
        idx = self.data[self.var_x].index(absc)

        ymin, ymax = self.axes.get_ylim()
        annot = self.annotation[0]
        annot.set_text("{}".format(absc))
        annot.xytext = (10, 20)
        annot.xy = (absc, ymin)
        annot.set_visible(True)

        for var in self.list_var:
            idx_a = var["id"]
            annot = self.annotation[idx_a + 1]
            if self.data[var["name"]] and self.courbes[idx_a].get_visible():
                val = self.data[var["name"]][idx]
                annot.set_text("{} {}".format(val, self.unit_y))
                annot.xy = (absc, val)
                annot.set_visible(True)
            else:
                annot.set_visible(False)

        self.v_line.set_xdata(absc)
        self.v_line.set_visible(True)
        self.canvas.draw()

    def init_legende(self):
        listeNoms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, listeNoms, loc='upper right',
                                    fancybox=False, shadow=False, fontsize=7.)
        self.leg.get_frame().set_alpha(0.4)
        self.leg.set_zorder(110)
        DraggableLegendNew(self.leg)
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(5)
            legline.set_linewidth(3)
            self.lined[legline] = courbe

    def maj_unit_x(self, unit):
        self.unit = unit
        self.axes.set_xlabel("time ({})".format(unit))
        if self.unit == 'date':
            self.unit_x = 'date'
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        else:
            self.unit_x = 'num'
            self.axes.xaxis.set_major_formatter(ticker.ScalarFormatter())

    def maj_courbes(self, courbes):
        for c in courbes.keys():
            self.courbes[c].set_data(courbes[c]["x"], courbes[c]["y"])
        self.maj_limites()

    def maj_limites(self):
        no_data = True
        miniX = 999999.
        maxiX = -999999.
        miniZ = 999999.
        maxiZ = -999999.

        for courbe in self.courbes:
            if courbe.get_visible():
                lx, lz = courbe.get_data()
                lx = [x for x in lx if x is not None]
                lz = [z for z in lz if z is not None]
                if lx and lz:
                    no_data = False
                    miniX = min(miniX, min(lx))
                    maxiX = max(maxiX, max(lx))
                    miniZ = min(miniZ, min(lz) - 1)
                    maxiZ = max(maxiZ, max(lz) + 1)

        if no_data:
            self.axes.set_xlim(0., 1.)
            self.axes.set_ylim(0., 1.)
        else:
            self.axes.set_xlim(miniX, maxiX)
            self.axes.set_ylim(miniZ, maxiZ)

        self.fig.autofmt_xdate()
        self.canvas.draw()



class DraggableLegendNew:
    def __init__(self, legend):
        self.legend = legend
        self.gotLegend = False
        legend.figure.canvas.mpl_connect('motion_notify_event', self.lgd_on_motion)
        legend.figure.canvas.mpl_connect('pick_event', self.lgd_on_pick)
        legend.figure.canvas.mpl_connect('button_release_event', self.lgd_on_release)
        legend.set_picker(self.my_legend_picker)

    def my_legend_picker(self, legend, evt):
        return self.legend.legendPatch.contains(evt)

    def lgd_on_pick(self, evt):
        btn = evt.mouseevent.button
        if btn == 1:
            art = evt.artist
            if art == self.legend:
                bbox = self.legend.get_window_extent()
                self.mouse_x = evt.mouseevent.x
                self.mouse_y = evt.mouseevent.y
                self.legend_x = bbox.xmin
                self.legend_y = bbox.ymin
                self.gotLegend = 1

    def lgd_on_release(self, evt):
        if self.gotLegend:
            self.gotLegend = False

    def lgd_on_motion(self, evt):
        if self.gotLegend:
            dx = evt.x - self.mouse_x
            dy = evt.y - self.mouse_y
            loc_in_canvas = self.legend_x + dx, self.legend_y + dy
            loc_in_norm_axes = self.legend.parent.transAxes.inverted().transform_point(loc_in_canvas)
            self.legend._loc = tuple(loc_in_norm_axes)
            self.legend.figure.canvas.draw()