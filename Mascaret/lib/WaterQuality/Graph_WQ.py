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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from ..Graphic.GraphCommon import GraphCommon


class GraphWaterQ(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None, mod=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.axes = None
        self.list_trac = []
        self.courbeTrac = None
        self.courbes = []

        self.init_ui_common_p()
        self.gui_graph(lay)
        self.init_ui(mod)

    def init_ui(self, mod):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis="both", labelsize=7.0)
        self.axes.grid(True)

        rows = self.mdb.run_query(
            "SELECT id, sigle FROM {schema}.tracer_name WHERE type = %s ORDER BY id",
            fetch=True,
            params=[mod],
            schema=True,
        )

        self.list_trac = []
        for row in rows:
            self.list_trac.append({"id": row[0], "name": row[1]})
            (self.courbeTrac,) = self.axes.plot([], [], zorder=100 - row[0], label=row[1])
            self.courbes.append(self.courbeTrac)

        self.fig.canvas.mpl_connect("pick_event", self.onpick)
        self.init_legende()

    def init_graph(self, config, all_vis=False):
        self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        for t, trac in enumerate(self.list_trac):
            lst = [[], []]
            if config is not None:
                sql = (
                    "SELECT time, value FROM {schema}.laws_wq "
                    "WHERE id_config = %s AND id_trac = %s ORDER BY time"
                )
                rows = self.mdb.run_query(
                    sql,
                    fetch=True,
                    params=[config, trac["id"]],
                    schema=True,
                )
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
        self.init_ui_common_p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis="both", labelsize=7.0)
        self.axes.grid(True)

        for var in self.lst_var:
            (self.courbeTrac,) = self.axes.plot([], [], zorder=100 - var["id"], label=var["name"])
            self.courbes.append(self.courbeTrac)

        self.fig.canvas.mpl_connect("pick_event", self.onpick)
        self.init_legende()

    def init_graph(self, config, all_vis=False):
        self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        for v, var in enumerate(self.lst_var):
            lst = [[], []]
            if config is not None:
                sql = (
                    "SELECT time, value FROM {schema}.laws_meteo "
                    "WHERE id_config = %s AND id_var = %s ORDER BY time"
                )
                rows = self.mdb.run_query(
                    sql,
                    fetch=True,
                    params=[config, var["id"]],
                    schema=True,
                )
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
        self.init_ui_common_p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.fig.canvas.mpl_connect("pick_event", self.onpick)

    def init_mdl(self, mod):
        rows = self.mdb.run_query(
            "SELECT id, sigle FROM {schema}.tracer_name WHERE type = %s ORDER BY id",
            fetch=True,
            params=[mod],
            schema=True,
        )

        self.axes.cla()
        self.axes.tick_params(axis="both", labelsize=7.0)
        self.axes.grid(True)

        self.list_trac = []
        self.courbes = []
        for row in rows:
            self.list_trac.append({"id": row[0], "name": row[1]})
            (self.courbeTrac,) = self.axes.plot([], [], zorder=100 - row[0], label=row[1])
            self.courbes.append(self.courbeTrac)

        self.init_legende()

    def init_graph(self, config, bief, all_vis=False):
        # self.maj_unit_x("s")
        leglines = self.leg.get_lines()
        for t, trac in enumerate(self.list_trac):
            lst = [[], []]
            if config is not None:
                sql = (
                    "SELECT abscissa, value FROM {schema}.init_conc_wq "
                    "WHERE id_config = %s AND bief = %s AND id_trac = %s ORDER BY abscissa"
                )
                rows = self.mdb.run_query(
                    sql,
                    fetch=True,
                    params=[config, bief, trac["id"]],
                    schema=True,
                )
                if len(rows) > 0:
                    lst = list(zip(*rows))

            self.courbes[t].set_data(lst[0], lst[1])

            if all_vis:
                self.courbes[t].set_visible(True)
                leglines[t].set_alpha(1.0)

        self.maj_limites()
