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

from matplotlib.patches import Polygon as mpoly

from .ClassMethod import ClassMethod
from ..GraphCommon import GraphCommon


class GraphStructure(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.tmp = ClassMethod(self.mgis)
        self.gui_graph(lay)
        self.initUI()

    def initUI(self):
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis='both', labelsize=7.)
        self.axes.grid(False)
        self.courbes = {'profil_poly': None,
                        'ouvrage_poly': None,
                        'elem': []}

        # Dessin du profil
        # self.courbes['profil_line'], = self.axes.plot([], [], zorder=100, c='#96785A', label='profil')
        self.courbes['profil_poly'] = mpoly([(0., 0.), (0., 0.)], zorder=99, facecolor='#C8B4A0',
                                            edgecolor='#96785A', alpha=1., label='profil')
        self.axes.add_patch(self.courbes['profil_poly'])

        # Dessin de l'ouvrage
        # self.courbes['ouvrage_line'], = self.axes.plot([], [], zorder=10, c='black', label='ouvrage')
        self.courbes['ouvrage_poly'] = mpoly([(0., 0.), (0., 0.)], zorder=9, facecolor='#D1D1D1',
                                             edgecolor='black', alpha=1., hatch=None)
        self.axes.add_patch(self.courbes['ouvrage_poly'])

    def initGraph(self, config):
        if config is not None:
            for elem in self.courbes['elem']:
                elem.remove()
            self.courbes['elem'] = []

            param = {}
            sql = "SELECT x, z FROM {0}.profil_struct WHERE id_config = {1} ORDER BY id_order".format(self.mdb.SCHEMA,
                                                                                                      config)
            rows = self.mdb.run_query(sql, fetch=True)
            dico_profil = {'x': [r[0] for r in rows], 'z': [r[1] for r in rows]}

            sql = "SELECT var, value FROM {0}.struct_param WHERE id_config = {1} " \
                  "AND var IN ('ZTOPTAB', 'EPAITAB', 'FIRSTWD')".format(self.mdb.SCHEMA, config)
            rows = self.mdb.run_query(sql, fetch=True)
            if rows == []:
                self.canvas.draw()
                return
            for r in rows:
                param[r[0]] = r[1]

            minx, miny, maxx, maxy = min(dico_profil['x']), min(dico_profil['z']) - 1, max(dico_profil['x']), param[
                'ZTOPTAB'] + 1
            x_left = param['FIRSTWD']

            sql = "SELECT id_elem, type FROM {0}.struct_elem WHERE id_config = {1} " \
                  "ORDER BY id_elem".format(self.mdb.SCHEMA, config)
            lst_elem = self.mdb.run_query(sql, fetch=True)
            for e, elem in enumerate(lst_elem):
                if elem[1] == 0:
                    sql = "SELECT value FROM {0}.struct_elem_param WHERE id_config = {1} and id_elem = {2} " \
                          "and var = 'LARGTRA'".format(self.mdb.SCHEMA, config, elem[0])
                    larg = self.mdb.run_query(sql, fetch=True)[0][0]
                    self.courbes['elem'].append(mpoly([(x_left, miny - 90),
                                                       (x_left, param['ZTOPTAB'] - param['EPAITAB']),
                                                       (x_left + larg, param['ZTOPTAB'] - param['EPAITAB']),
                                                       (x_left + larg, miny - 90)],
                                                      zorder=90 - e, facecolor='w', edgecolor='black', alpha=1.))
                    self.axes.add_patch(self.courbes['elem'][-1])
                    x_left += larg
                elif elem[1] == 1:
                    sql = "SELECT value FROM {0}.struct_elem_param WHERE id_config = {1} and id_elem = {2} " \
                          "and var = 'LARGPIL'".format(self.mdb.SCHEMA, config, elem[0])
                    larg = self.mdb.run_query(sql, fetch=True)[0][0]
                    x_left += larg

            dico_profil['x'].insert(0, minx)
            dico_profil['x'].append(maxx)
            dico_profil['z'].insert(0, miny - 100)
            dico_profil['z'].append(miny - 100)
            # self.courbes['profil_line'].set_data(dico_profil['x'], dico_profil['z'])
            self.courbes['profil_poly'].set_xy([(dico_profil['x'][r], dico_profil['z'][r])
                                                for r in range(len(dico_profil['x']))])

            dico_ouvrage = {'x': [dico_profil['x'][0], dico_profil['x'][0], dico_profil['x'][-1], dico_profil['x'][-1]],
                            'z': [miny - 90, param['ZTOPTAB'], param['ZTOPTAB'], miny - 90]}
            # self.courbes['ouvrage_line'].set_data(dico_ouvrage['x'], dico_ouvrage['z'])
            self.courbes['ouvrage_poly'].set_xy([(dico_ouvrage['x'][r], dico_ouvrage['z'][r])
                                                 for r in range(len(dico_ouvrage['x']))])

            self.axes.set_xlim((minx, maxx))
            self.axes.set_ylim((miny, maxy))
            self.canvas.draw()

        return
        self.maj_limites()
