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

class GraphCommon(QDialog):
    def __init__(self, mgis=None):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.dossierPlugin = self.mgis.masplugPath
        self.dossierProjet = self.mgis.repProject
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

    def initui_common_p(self):
        self.courbes = []

    def gui_graph(self, lay):
        lay.addWidget(self.canvas)
        lay.addWidget(self.toolbar)

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
