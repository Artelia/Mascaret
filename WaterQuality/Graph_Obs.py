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

from ..GraphCommon import GraphCommon
from matplotlib.dates import date2num

class GraphObservation(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.init_ui_common_p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        self.courbe,  = self.axes.plot([], [], zorder=99, label="None")
        self.courbes.append(self.courbe)

        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.init_legende()


    def init_graph(self, config):
        self.maj_unit_x("date")
        leglines = self.leg.get_lines()

        lst = [[], []]
        if config is not None:
            self.leg.get_texts()[0].set_text(config[1])
            sql = "SELECT date, valeur FROM {0}.observations " \
                  "WHERE code = '{1}' and type = '{2}' " \
                  "ORDER BY date".format(self.mdb.SCHEMA, config[0], config[1])
            rows = self.mdb.run_query(sql, fetch=True)
            if len(rows) > 0:
                lst = list(zip(*rows))
        else:
            self.leg.get_texts()[0].set_text("None")

        self.courbes[0].set_data([date2num(l) for l in lst[0]], lst[1])
        self.courbes[0].set_visible(True)
        leglines[0].set_alpha(1.0)

        self.maj_limites()

