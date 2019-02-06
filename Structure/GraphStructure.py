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

class GraphStructure(GraphCommon):
    """class Dialog GraphWaterQ"""
    def __init__(self, mgis=None, lay=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.initui_common_p()
        self.gui_graph(lay)
        self.initUI(None)

    def initUI(self, struct):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(False)

        return

        sql = "SELECT id, sigle FROM {0}.tracer_name WHERE type = '{1}' ORDER BY id".format(self.mdb.SCHEMA, struct)
        rows = self.mdb.run_query(sql, fetch=True)

        self.list_trac = []
        for row in rows:
            self.list_trac.append({"id":row[0], "name": row[1]})
            self.courbeTrac, = self.axes.plot([], [], zorder=100-row[0], label=row[1])
            self.courbes.append(self.courbeTrac)

        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.init_legende()

    def initGraph(self, config, all_vis=False):
        return
        self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        for t, trac in enumerate(self.list_trac):
            lst = [[], []]
            if config is not None:
                sql = "SELECT time, value FROM {0}.laws_wq WHERE id_config = {1} and id_trac = {2} ORDER BY time".format(self.mdb.SCHEMA,
                                                                                                                         config,
                                                                                                                         trac["id"])
                rows = self.mdb.run_query(sql, fetch=True)
                if len(rows) > 0:
                    lst = list(zip(*rows))

            self.courbes[t].set_data(lst[0], lst[1])

            if all_vis:
                self.courbes[t].set_visible(True)
                leglines[t].set_alpha(1.0)

        self.maj_limites()
