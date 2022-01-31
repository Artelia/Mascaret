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

from .GraphCommon import GraphCommon
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import timedelta


class GraphHydroLaw(GraphCommon):
    """class Dialog GraphLaw"""

    def __init__(self, mgis=None, lay=None, typ_law=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.axes = None

        self.list_var = []
        self.list_z = []
        self.courbes = []
        self.old_xlim = None

        self.init_ui_common_p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        """
        initialize GUI
        :return:
        """
        self.axes = self.fig.add_subplot(111)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.fig.canvas.mpl_connect('draw_event', self.draw_event)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

    def draw_event(self, event):
        """
        draw event
        :param event:
        :return:
        """
        if len(self.courbes) > 0:

            new_xlim = self.axes.get_xlim()
            if self.unit in ('date', 'datehhmm'):
                if self.old_xlim == new_xlim:
                    return
                self.old_xlim = new_xlim
                xmin, xmax = new_xlim
                if (xmax - xmin) < 2:
                    self.maj_lbl_x("time", 'datehhmm')
                else:
                    self.maj_lbl_x("time", 'date')
                self.canvas.draw()

    def init_curv(self, typ_law=None, param_law=None, date_ref=None):
        """
        initialize curve
        :param typ_law: law type
        :param param_law: parameters law
        :param date_ref: reference date
        :return:
        """
        self.axes.cla()
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        self.list_var.clear()
        self.list_z.clear()
        self.courbes.clear()

        if typ_law:
            self.axeX = param_law['graph']['x']['var']
            for v, var in enumerate(param_law['graph']['y']['var']):
                self.list_var.append(
                    {"id": var, "name": param_law['var'][var]['name']})
                self.courbe_laws, = self.axes.plot([], [], zorder=100 - v,
                                                   label=param_law['var'][var][
                                                       'name'])
                self.courbes.append(self.courbe_laws)

            self.init_legende()
            if date_ref:
                self.maj_lbl_x("time", "date")
            else:
                self.maj_lbl_x(param_law['graph']['x']['tit'],
                               param_law['graph']['x']['unit'])
            self.maj_lbl_y(param_law['graph']['y']['tit'],
                           param_law['graph']['y']['unit'])

        self.maj_limites()
        self.canvas.draw()

    def init_graph(self, id_law, date_ref=None, all_vis=False):
        """
        update law curve
        :param id_law: id law
        :param date_ref: reference date
        :param all_vis:  bool display all curve
        :return:
        """
        leglines = self.leg.get_lines()

        sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} and id_var = {2} ORDER BY id_order".format(
            self.mdb.SCHEMA, id_law, self.axeX)
        rows = self.mdb.run_query(sql, fetch=True)
        if date_ref:
            lst_x = [mdates.date2num(date_ref + timedelta(seconds=r[0])) for r
                     in rows]
        else:
            lst_x = [r[0] for r in rows]

        for v, var in enumerate(self.list_var):
            lst_y = []
            if id_law is not None:
                sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} and id_var = {2} ORDER BY id_order".format(
                    self.mdb.SCHEMA, id_law, var['id'])
                rows = self.mdb.run_query(sql, fetch=True)
                if len(rows) > 0:
                    lst_y = [r[0] for r in rows]

            self.courbes[v].set_data(lst_x, lst_y)

            if all_vis:
                self.courbes[v].set_visible(True)
                leglines[v].set_alpha(1.0)

        self.maj_limites()

    def init_curv_weir_zam(self, param_law=None, id_law=None, var_x=0):
        """

        :param param_law: dict() parameter law
        :param id_law: id law
        :param var_x: varaible abscissa
        :return:
        """
        self.axes.cla()
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        self.list_var.clear()
        self.list_z.clear()
        self.courbes.clear()
        self.axeX = var_x
        self.axeZ = abs(var_x - 1)

        if id_law:
            sql = "SELECT DISTINCT value FROM {0}.law_values WHERE id_law = {1} AND id_var = {2} " \
                  "ORDER BY value".format(self.mdb.SCHEMA, id_law, self.axeZ)
            rows = self.mdb.run_query(sql, fetch=True)
            self.list_z = [r[0] for r in rows]

            for idx, z in enumerate(self.list_z):
                name = "{0} {1} ({2})".format(
                    param_law['var'][self.axeZ]['leg'], idx + 1, round(z, 2))
                self.list_var.append({"id": idx, "name": name})
                self.courbe_laws, = self.axes.plot([], [], zorder=100 - idx,
                                                   label=name)
                self.courbes.append(self.courbe_laws)

            self.init_legende()

            if self.axeX == 0:
                self.maj_lbl_x('Q', 'm3/s')
            elif self.axeX == 1:
                self.maj_lbl_x('Zdown', 'm')
            self.maj_lbl_y(param_law['graph']['y']['tit'],
                           param_law['graph']['y']['unit'])

        self.canvas.draw()

    def init_graph_weir_zam(self, id_law, all_vis=False):
        """
          update weir law curve
        :param id_law: id law
        :param all_vis:  bool display all curve
        :return:
        """
        leglines = self.leg.get_lines()

        lst_x_ref = None

        for idx, z in enumerate(self.list_z):
            sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} AND id_var = {2} AND id_order IN " \
                  "(SELECT id_order FROM {0}.law_values WHERE id_law = {1} AND id_var = {3} AND value = {4}) " \
                  "ORDER BY id_order".format(self.mdb.SCHEMA, id_law, self.axeX,
                                             self.axeZ, z)
            rows = self.mdb.run_query(sql, fetch=True)
            lst_x = [r[0] for r in rows]

            sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} AND id_var = 2 AND id_order IN " \
                  "(SELECT id_order FROM {0}.law_values WHERE id_law = {1} AND id_var = {3} AND value = {4}) " \
                  "ORDER BY id_order".format(self.mdb.SCHEMA, id_law, self.axeX,
                                             self.axeZ, z)
            rows = self.mdb.run_query(sql, fetch=True)
            lst_y = [r[0] for r in rows]

            if not lst_x_ref:
                lst_x_ref = lst_x
            else:
                if lst_x_ref != lst_x:
                    break

            self.courbes[idx].set_data(lst_x, lst_y)

            if all_vis:
                self.courbes[idx].set_visible(True)
                leglines[idx].set_alpha(1.0)

        self.maj_limites()

    def init_graph_obs(self, data, param_law, all_vis=False):
        """
         update observation curve
        :param data: dict() data
        :param param_law: dict() law parameters
        :param all_vis: bool display all curve
        :return:
        """
        leglines = self.leg.get_lines()

        for v, var in enumerate(self.list_var):
            self.courbes[v].set_data(
                [mdates.date2num(date_) for date_ in data["date"]], data['val'])

            if all_vis:
                self.courbes[v].set_visible(True)
                leglines[v].set_alpha(1.0)
        self.init_legende()
        self.maj_lbl_x("time", "date")

        self.maj_lbl_y(param_law['graph']['y']['tit'],
                       param_law['graph']['y']['unit'])

        self.maj_limites()
        self.canvas.draw()

    def maj_lbl_x(self, var, unit):
        """
        Update x label
        :param var: variable
        :param unit:  unit
        :return:
        """
        self.unit = unit
        if unit in ("date", "datehhmm"):
            self.axes.set_xlabel("date")
        else:
            if unit:
                self.axes.set_xlabel("{} ({})".format(var, unit))
            else:
                self.axes.set_xlabel("{}".format(var))

        if unit == "date":
            self.axes.xaxis.set_major_formatter(
                mdates.DateFormatter('%d-%m-%Y'))
        elif unit == "datehhmm":
            self.axes.xaxis.set_major_formatter(
                mdates.DateFormatter('%d-%m-%Y %H:%M'))
        else:
            self.axes.xaxis.set_major_formatter(ticker.ScalarFormatter())

    def maj_lbl_y(self, var, unit):
        """
        Update y label
        :param var: variable
        :param unit:  unit
        :return:
        """
        if unit:
            self.axes.set_ylabel("{} ({})".format(var, unit))
        else:
            self.axes.set_ylabel("{}".format(var))
