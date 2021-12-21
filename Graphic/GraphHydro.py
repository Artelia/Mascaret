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

# dico_typ_law = {1: {'name': 'Hydrograph Q(t)',
#                     'var': [{'name': 'time', 'leg': 'time', 'unit': 's'},
#                             {'name': 'flowrate', 'leg': 'Q', 'unit': 'm3/s'}],
#                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
#                               'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
#                     'xIsTime': True},
#                 2: {'name': 'Rating Curve Z = f(Q)',
#                     'var': [{'name': 'flowrate', 'leg': 'Q', 'unit': 'm3/s'},
#                             {'name': 'z', 'leg': 'z', 'unit': 'm'}],
#                     'graph': {'x': {'var': 0, 'tit': 'Q', 'unit': 'm3/s'},
#                               'y': {'var': [1], 'tit': 'z', 'unit': 'm'}},
#                     'xIsTime': False},
#                 3: {'name': 'Limnihydrograph Z,Q(t)',
#                     'var': [{'name': 'time', 'leg': 'time', 'unit': 's'},
#                             {'name': 'z', 'leg': 'z', 'unit': 'm'},
#                             {'name': 'flowrate', 'leg': 'Q', 'unit': 'm3/s'}],
#                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
#                               'y': {'var': [1, 2], 't it': None, 'unit': None}},
#                     'xIsTime': False}
#                 }

class GraphHydroLaw(GraphCommon):
    """class Dialog GraphLaw"""
    def __init__(self, mgis=None, lay=None, typ_law=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.axes = None
        # self.initUI_common_P()
        # self.GUI_graph(lay)
        # self.initUI()
        # self.initCurv(typ_law)

        self.list_var = []
        self.courbes = []

        self.init_ui_common_p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

    def initCurv(self, typ_law=None, param_law=None):
        self.axes.cla()
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(True)

        self.list_var.clear()
        self.courbes.clear()

        if typ_law:
            self.axeX = param_law['graph']['x']['var']
            for v, var in enumerate(param_law['graph']['y']['var']):
                self.list_var.append({"id": var, "name": param_law['var'][var]['name']})
                self.courbeTrac, = self.axes.plot([], [], zorder=100 - v, label=param_law['var'][var]['name'])
                self.courbes.append(self.courbeTrac)

            self.init_legende()

            self.axes.set_xlabel("{} ({})".format(param_law['graph']['x']['tit'], param_law['graph']['x']['unit']))
            self.axes.set_ylabel("{} ({})".format(param_law['graph']['y']['tit'], param_law['graph']['y']['unit']))

        self.canvas.draw()

    def initGraph(self, id_law, all_vis=False):
        leglines = self.leg.get_lines()

        sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} and id_var = {2} ORDER BY id_order".format(self.mdb.SCHEMA, id_law, self.axeX)
        rows = self.mdb.run_query(sql, fetch=True)
        lst_x = [r[0] for r in rows]

        for v, var in enumerate(self.list_var):
            lst_y = []
            if id_law is not None:
                sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} and id_var = {2} ORDER BY id_order".format(self.mdb.SCHEMA, id_law, var['id'])
                rows = self.mdb.run_query(sql, fetch=True)
                if len(rows) > 0:
                    lst_y = [r[0] for r in rows]

            self.courbes[v].set_data(lst_x, lst_y)

            if all_vis:
                self.courbes[v].set_visible(True)
                leglines[v].set_alpha(1.0)

        self.maj_limites()



