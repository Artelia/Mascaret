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

import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.figure import Figure
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *

if int(qVersion()[0]) < 5:  # qt4
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
else:  # qt4
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
from ..GraphCommon import DraggableLegend

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

    def init_ui_common__p(self):
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
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

    def maj_courbes(self, courbes):
        for c in courbes.keys():
            self.courbes[c].set_data(courbes[c]["x"], courbes[c]["y"])

        self.maj_limites()

    def maj_limites(self):
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
                    mini_z = min(mini_z, min(lz) - 1)
                    maxi_z = max(maxi_z, max(lz) + 1)

        if no_data:
            self.axes.set_xlim(0., 1.)
            self.axes.set_ylim(0., 1.)
        else:
            self.axes.set_xlim(mini_x, maxi_x)
            self.axes.set_ylim(mini_z, maxi_z)

        self.fig.autofmt_xdate()
        self.canvas.draw()


class GraphWaterQ(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None, mod=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.init_ui_common__p()
        self.gui_graph(lay)
        self.init_ui(mod)

    def init_ui(self, mod):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        sql = "SELECT id, sigle FROM {0}.tracer_name WHERE type = '{1}' ORDER BY id".format(self.mdb.SCHEMA, mod)
        rows = self.mdb.run_query(sql, fetch=True)

        self.list_trac = []
        for row in rows:
            self.list_trac.append({"id": row[0], "name": row[1]})
            self.courbeTrac, = self.axes.plot([], [], zorder=100 - row[0], label=row[1])
            self.courbes.append(self.courbeTrac)

        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.init_legende()

    def init_graph(self, config, all_vis=False):
        self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        for t, trac in enumerate(self.list_trac):
            lst = [[], []]
            if config is not None:
                sql = "SELECT time, value FROM {0}.laws_wq " \
                      "WHERE id_config = {1} and id_trac = {2}" \
                      " ORDER BY time".format(self.mdb.SCHEMA, config, trac["id"])
                rows = self.mdb.run_query(sql, fetch=True)
                if len(rows) > 0:
                    lst = list(zip(*rows))

            self.courbes[t].set_data(lst[0], lst[1])

            if all_vis:
                self.courbes[t].set_visible(True)
                leglines[t].set_alpha(1.0)

        self.maj_limites()


class GraphMeteo(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None, lst_var=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.lst_var = lst_var
        self.init_ui_common__p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        for var in self.lst_var:
            self.courbeTrac, = self.axes.plot([], [], zorder=100 - var["id"], label=var["name"])
            self.courbes.append(self.courbeTrac)

        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.init_legende()

    def init_graph(self, config, all_vis=False):
        self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        for v, var in enumerate(self.lst_var):
            lst = [[], []]
            if config is not None:
                sql = "SELECT time, value FROM {0}.laws_meteo " \
                      "WHERE id_config = {1} and id_var = {2} " \
                      "ORDER BY time".format(self.mdb.SCHEMA, config, var["id"])
                rows = self.mdb.run_query(sql, fetch=True)
                if len(rows) > 0:
                    lst = list(zip(*rows))

            self.courbes[v].set_data(lst[0], lst[1])

            if all_vis:
                self.courbes[v].set_visible(True)
                leglines[v].set_alpha(1.0)

        self.maj_limites()


class GraphInitConc(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.init_ui_common__p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

    def init_mdl(self, mod):
        sql = "SELECT id, sigle FROM {0}.tracer_name WHERE type = '{1}' ORDER BY id".format(self.mdb.SCHEMA, mod)
        rows = self.mdb.run_query(sql, fetch=True)

        self.axes.cla()
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        self.list_trac = []
        self.courbes = []
        for row in rows:
            self.list_trac.append({"id": row[0], "name": row[1]})
            self.courbeTrac, = self.axes.plot([], [], zorder=100 - row[0], label=row[1])
            self.courbes.append(self.courbeTrac)

        self.init_legende()

    def init_graph(self, config, bief, all_vis=False):
        # self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        for t, trac in enumerate(self.list_trac):
            lst = [[], []]
            if config is not None:
                sql = "SELECT abscissa, value FROM {0}.init_conc_wq " \
                      "WHERE id_config = {1} and bief = {2} and id_trac = {3} ORDER BY abscissa".format(self.mdb.SCHEMA,
                                                                                                        config,
                                                                                                        bief,
                                                                                                        trac["id"])
                rows = self.mdb.run_query(sql, fetch=True)
                if len(rows) > 0:
                    lst = list(zip(*rows))

            self.courbes[t].set_data(lst[0], lst[1])

            if all_vis:
                self.courbes[t].set_visible(True)
                leglines[t].set_alpha(1.0)

        self.maj_limites()
