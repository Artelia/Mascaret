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
import json
from matplotlib.patches import Polygon as mpoly
# from shapely.geometry import Polygon as spoly
from shapely import geometry

from ..Graphic.GraphCommon import GraphCommon


class GraphStructure(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.gui_graph(lay)
        self.axes = None
        self.courbes = {}
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.08)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(False)
        self.courbes = {'profil_poly': mpoly([(0., 0.), (0., 0.)], zorder=99,
                                             facecolor='#C8B4A0',
                                             edgecolor='#96785A', alpha=1.,
                                             label='profil'),
                        'ouvrage_poly': None,
                        'profil_line':
                            self.axes.plot([], [], zorder=100, c='#96785A',
                                           label='profil')[0],
                        'elem': []}

        # Dessin du profil
        self.axes.add_patch(self.courbes['profil_poly'])

        # Dessin de l'ouvrage
        # self.courbes['ouvrage_line'], = self.axes.plot([], [], zorder=10, c='black', label='ouvrage')
        self.courbes['ouvrage_poly'] = mpoly([(0., 0.), (0., 0.)], zorder=9,
                                             facecolor='#D1D1D1',
                                             edgecolor='black', alpha=1.,
                                             hatch=None)
        self.axes.add_patch(self.courbes['ouvrage_poly'])

    def init_graph(self, config):
        if config is not None:
            for elem in self.courbes['elem']:
                elem.remove()
            self.courbes['elem'] = []

            param = {}
            sql = "SELECT x, z FROM {0}.profil_struct WHERE id_config = {1} ORDER BY id_order".format(
                self.mdb.SCHEMA,
                config)

            rows = self.mdb.run_query(sql, fetch=True)

            dico_profil = {'x': [r[0] for r in rows], 'z': [r[1] for r in rows]}
            minx, miny, maxx, maxy = min(dico_profil['x']), min(
                dico_profil['z']) - 1, max(dico_profil['x']), max(
                dico_profil['z'])
            dico_profil['x'].insert(0, minx)
            dico_profil['x'].append(maxx)
            dico_profil['z'].insert(0, miny - 100)
            dico_profil['z'].append(miny - 100)
            self.courbes['profil_line'].set_data(dico_profil['x'],
                                                 dico_profil['z'])
            self.courbes['profil_poly'].set_xy(
                [(dico_profil['x'][r], dico_profil['z'][r])
                 for r in range(len(dico_profil['x']))])

            # sql = "SELECT type FROM {0}.struct_config WHERE id = {1} ".format(self.mdb.SCHEMA, config)
            # rows = self.mdb.run_query(sql, fetch=True)
            # typ_struct = rows[0][0]

            sql = "SELECT var, value FROM {0}.struct_param WHERE id_config = {1} " \
                  "AND var IN ('ZTOPTAB', 'EPAITAB', 'FIRSTWD')".format(
                self.mdb.SCHEMA, config)
            rows = self.mdb.run_query(sql, fetch=True)
            if not rows:
                self.courbes['ouvrage_poly'].set_xy([(0., 0.), (0., 0.)])
                self.update_limites(minx, miny, maxx, maxy)
            else:
                for r in rows:
                    param[r[0]] = r[1]

                maxy = param['ZTOPTAB'] + 1
                dico_ouvrage = {'x': [dico_profil['x'][0], dico_profil['x'][0],
                                      dico_profil['x'][-1],
                                      dico_profil['x'][-1]],
                                'z': [miny - 90, param['ZTOPTAB'],
                                      param['ZTOPTAB'], miny - 90]}
                # self.courbes['ouvrage_line'].set_data(dico_ouvrage['x'], dico_ouvrage['z'])
                self.courbes['ouvrage_poly'].set_xy(
                    [(dico_ouvrage['x'][r], dico_ouvrage['z'][r])
                     for r in range(len(dico_ouvrage['x']))])

                sql = "SELECT id_elem, type, ST_AsGeoJSON(polygon) FROM {0}.struct_elem WHERE id_config = {1} " \
                      "AND polygon is Not Null ORDER BY id_elem".format(
                    self.mdb.SCHEMA, config)
                lst_elem = self.mdb.run_query(sql, fetch=True)
                for e, elem in enumerate(lst_elem):
                    if elem[1] == 0:
                        poly = geometry.shape(json.loads(elem[2]))
                        poly_coord = [pt for pt in poly.exterior.coords]
                        self.courbes['elem'].append(mpoly(poly_coord,
                                                          zorder=90 - e,
                                                          facecolor='w',
                                                          edgecolor='black',
                                                          alpha=1.))
                        self.axes.add_patch(self.courbes['elem'][-1])

                self.update_limites(minx, miny, maxx, maxy)

    def update_limites(self, minx, miny, maxx, maxy):
        self.axes.set_xlim((minx, maxx))
        self.axes.set_ylim((miny, maxy))
        self.canvas.draw()
