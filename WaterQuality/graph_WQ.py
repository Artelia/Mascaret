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


from matplotlib.widgets import RectangleSelector, SpanSelector, Cursor
from matplotlib.ticker import FormatStrFormatter
from matplotlib import gridspec, patches
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.image as mpimg
import matplotlib.lines as mlines

from datetime import datetime
import numpy as np
import sys, os

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

    def initUI_common_P(self):
        self.courbes = []

    def GUI_graph(self, lay):
        lay.addWidget(self.canvas)
        lay.addWidget(self.toolbar)


class GraphWaterQ(GraphCommon):
    """class Dialog GraphWaterQ"""
    def __init__(self, mgis=None, lay=None, mod=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.initUI_common_P()
        self.GUI_graph(lay)
        self.initUI(mod)


    def initUI(self, mod):
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        self.axes.set_xlabel("time (s)")

        sql = "SELECT id, sigle FROM {0}.tracer_name WHERE type = '{1}' ORDER BY id".format(self.mdb.SCHEMA, mod)
        rows = self.mdb.run_query(sql, fetch=True)

        self.list_trac = []
        for row in rows:
            self.list_trac.append({"id":row[0], "name": row[1]})
            self.courbeTrac, = self.axes.plot([], [], zorder=100-row[0], label=row[1])
            self.courbes.append(self.courbeTrac)

        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.initLegende()


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
            self.majLimites()


    def initLegende(self):
        listeNoms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, listeNoms, loc='upper right',
                                    fancybox=False, shadow=False)
        self.leg.get_frame().set_alpha(0.4)
        self.leg.set_zorder(110)
        self.leg.draggable(True)
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(5)
            legline.set_linewidth(3)
            self.lined[legline] = courbe


    def initGraph(self, config, all_vis=False):
        leglines = self.leg.get_lines()
        for t, trac in enumerate(self.list_trac):
            if config is not None:
                sql = "SELECT time, value FROM {0}.laws_wq WHERE id_config = {1} and id_trac = {2} ORDER BY time".format(self.mdb.SCHEMA,
                                                                                                                         config,
                                                                                                                         trac["id"])
                rows = self.mdb.run_query(sql, fetch=True)
                lst = list(zip(*rows))
            else:
                lst = [[], []]

            self.courbes[t].set_data(lst[0], lst[1])

            if all_vis:
                self.courbes[t].set_visible(True)
                leglines[t].set_alpha(1.0)

        self.majLimites()


    def majCourbes(self, courbes):
        for c in courbes.keys():
            self.courbes[c].set_data(courbes[c]["x"], courbes[c]["y"])
        self.majLimites()


    def majLimites(self):
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

        self.canvas.draw()


