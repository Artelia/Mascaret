# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2017
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
import math as m
import json

import shapely.affinity
from shapely import wkt
from shapely.geometry import *


class ClassPolygone:
    def __init__(self, debug=False):
        self.debug = debug
        self.msg = ''
        self.epsi = 0.0001

    def poly_pont_cadre(self, param_g, param_elem, x0=None, zmin=-99999):
        """
        Creation polygone for PC : Frame bridge
        :param param_g: dico of general parameters
        :param param_elem: dico of element parameters
        :param x0: origin abscissa
        :param zmin: z min
        :return:  polygon
        """
        """
        Creation polygone for DA : scupper
        :param param_elem: dico of element parameters
        :param x0: origin abscissa
        :return: polygon
        """
        if x0 is None:
            x0 = param_g['FIRSTWD']  # point depart
        x1 = x0 + param_elem['LARGTRA']
        z = param_g['ZPC']  # point haut
        zmin_t = zmin - 10
        if zmin < z:
            poly_t = Polygon(
                [[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
        else:
            poly_t = GeometryCollection()

            print('Inconsistent Z for the span')
        return poly_t

    def poly_dalot(self, param_elem, x0):
        """
        Creation polygone for DA : scupper
        :param param_elem: dico of element parameters
        :param x0: origin abscissa
        :return: polygon
        """
        x1 = x0 + param_elem['LARGTRA']
        z = param_elem['COTERAD'] + param_elem['HAUTDAL']  # point haut
        zmin = param_elem['COTERAD']
        if zmin < z:
            poly_t = Polygon(
                [[x0, zmin], [x0, z], [x1, z], [x1, zmin], [x0, zmin]])
        else:
            poly_t = GeometryCollection()
            print('Inconsistent Z for the span')
        return poly_t

    def poly_buse(self, param_elem):
        """
        creation polygone for BU : buse
        :param param_elem: dico of element parameters
        :return: polygon
        """
        z_c = param_elem['COTERAD'] + (param_elem['LARGTRA'] / 2)
        x_c = param_elem['ABSBUSE']
        circ = Point([x_c, z_c]).buffer(param_elem['LARGTRA'] / 2)
        return circ

    def poly_arch(self, param_g, param_elem, x0=None, zmin=-99999):
        """
        creation polygone for PA : arch bridge
        :param param_elem: dico of general parameter
        :param param_g: dico of general parameters
        :param x0: origin abscissa
        :param zmin: zmin
        :return: polygon
        """
        type = param_elem['FORMARC']
        if x0 is None:
            x0 = param_g['FIRSTWD']  # point depart
        x1 = x0 + param_elem['LARG']
        x_c = param_elem['LARG'] / 2. + x0
        z = param_elem['ZMINARC']
        if type == 2:  # ellipse
            zmax = param_elem['ZMAXARC']
            # hyp. zmax-z=b/2
            b = 2 * (zmax - z)
            z_c = zmax - b
            frac = m.pow(x0 - x_c, 2) / (1 - m.pow(z - z_c, 2) / m.pow(b, 2))
            a = m.sqrt(frac)
        elif type == 1:  # circle
            b = param_elem['LARG'] / 2.
            a = b
            z_c = z
        else:
            poly_t = GeometryCollection()
            msg = 'Unkwnown arch : {}'.format(type)
            if self.debug:
                self.add_info(msg)

            return poly_t

        zmin_t = zmin - 10
        if zmin < z:
            circ = Point([x_c, z_c]).buffer(1)
            ell = shapely.affinity.scale(circ, a, b)
            poly = Polygon(
                [[x_c - a - 1, z - b * 2], [x_c - a - 1, z], [x_c + a + 1, z],
                 [x_c + a + 1, z - b * 2],
                 [x_c - a - 1, z - b * 2]])
            ell = ell.difference(poly)  # demi circle
            poly = Polygon(
                [[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
            poly_t = ell.union(poly)
        else:
            poly_t = GeometryCollection()
            msg = 'Inconsistent Z for the span'
            if self.debug:
                self.add_info(msg)

        return poly_t

    def poly_profil_del(self, profil, zmin=-99999):
        """
        creation profile polygone
        :param profil:  profil data
        :param zmin: z min
        :return: polygon
        """
        zmin_p = zmin - 20
        x0_p = profil['x'][0] - 1  # -1 est pour évité le cas du 0
        z0_p = profil['z'][0]
        liste_poly = [[x0_p, zmin_p], [x0_p, z0_p]]
        for x, z in list(zip(profil['x'], profil['z'])):
            liste_poly.append([x, z])
        liste_poly.append([profil['x'][-1] + 1, profil['z'][-1]])
        liste_poly.append([profil['x'][-1] + 1, zmin_p])
        liste_poly.append([x0_p, zmin_p])
        poly_p = Polygon(liste_poly)
        return poly_p

    def poly_pil(self, param_elem, x0, zmin=-99999):
        """
        creation polygone for Frame bridge PC
        :param param_elem: dico of parameter for an element
        :param x0: origin abscissa
        :param zmin: zmin
        :return: polygon
        """

        x1 = x0 + param_elem['LARG']
        z0 = param_elem['ZMAXELEM']
        z1 = param_elem['ZMAXELEM_P1']  # point haut
        zmin_t = zmin - 10
        if zmin < z1 and zmin < z0:
            poly_t = Polygon(
                [[x0, zmin_t], [x0, z0], [x1, z1], [x1, zmin_t], [x0, zmin_t]])
        else:
            poly_t = GeometryCollection()

            print('Inconsistent Z for the pier')
        return poly_t

    def udpate_polygon_table(self, mdb, poly_final, id_config, id_elem):
        """
        update polygone table
        :param mdb: data base class
        :param poly_final: polygone
        :param id_config: config index
        :param id_elem:  element index
        """
        poly_final = json.dumps(mapping(poly_final))
        where = "WHERE id_config = {0}  AND id_elem = {1} ".format(id_config,
                                                                   id_elem)
        sql = """UPDATE {0}.struct_elem SET polygon =ST_GeomFromGeoJSON('{1}')  {2}""".format(
            mdb.SCHEMA,
            poly_final,
            where)
        mdb.run_query(sql)

    def coup_poly_h(self, poly, cote, typ='U'):
        """
        Cut the polygone horizontaly
        :param poly: polygone to cut
        :param typ : cut side of polygon
        :param cote: z
        :return: new polygon
        """
        msg = None
        (minx, miny, maxx, maxy) = poly.bounds

        if typ == 'U':
            delpoly = Polygon([[minx - 1, cote], [maxx + 1, cote],
                               [maxx + 1, maxy + 1], [minx - 1, maxy + 1],
                               [minx - 1, cote]])
        elif typ == 'D':
            delpoly = Polygon([[minx - 1, miny - 1], [maxx + 1, miny - 1],
                               [maxx + 1, cote], [minx - 1, cote],
                               [minx - 1, miny - 1]])
        else:
            delpoly = GeometryCollection()

        if not delpoly.is_empty:
            if not poly.is_valid:
                # Polygone => multiPolygone
                poly = poly.buffer(0)
            polyw = poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"
        else:
            polyw = GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"

        if self.debug and msg is not None:
            print(msg)
        return polyw

    def coup_poly_v(self, poly, xo, typ='L'):
        """
        Cut the polygone vertically
        :param poly: polygone to cut
        :param xo: abscissa of cut
        :param typ: cut side of polygon
        :return: new polygon
        """
        msg = None
        if type(xo) == list:
            typ = 'LR'
        (minx, miny, maxx, maxy) = poly.bounds
        if typ == 'L':
            delpoly = Polygon([[minx - 1, maxy + 1], [xo, maxy + 1],
                               [xo, miny - 1], [minx - 1, miny - 1],
                               [minx - 1, maxy + 1]])
        elif typ == 'R':
            delpoly = Polygon([[xo, maxy + 1], [maxx + 1, maxy + 1],
                               [maxx + 1, miny - 1], [xo, miny - 1],
                               [xo, maxy + 1]])
        elif typ == 'LR':
            delpoly = Polygon([[minx - 1, maxy + 1], [xo[0], maxy + 1],
                               [xo[0], miny - 1], [minx - 1, miny - 1],
                               [minx - 1, maxy + 1]])

            delpoly_r = Polygon([[xo[1], maxy + 1], [maxx + 1, maxy + 1],
                                 [maxx + 1, miny - 1], [xo[1], miny - 1],
                                 [xo[1], maxy + 1]])
        else:
            delpoly = GeometryCollection()
        if not delpoly.is_empty:
            polyw = poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"
        else:
            polyw = GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"

        if typ == 'LR' and not polyw.is_empty:
            polyw = polyw.difference(delpoly_r)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"

        if self.debug and msg is not None:
            print(msg)
        return polyw

    def poly_profil(self, profil):
        """
        creation profile polygone
        :param profil: profile data
        :return: polygone of profile
        """

        zmax = max(profil['z'])
        zmax = zmax + self.epsi
        x0_p = profil['x'][0]
        z0_p = profil['z'][0]
        liste_poly = [[x0_p, zmax], [x0_p, z0_p]]
        for x, z in list(zip(profil['x'], profil['z'])):
            liste_poly.append([x, z])

        liste_poly.append([profil['x'][-1], zmax])
        liste_poly.append([x0_p, zmax])
        poly_p = Polygon(liste_poly)
        return poly_p

    def poly2_profile(self, profil):
        """
        creation profile polygone
        :param profil: profile data
        :return: polygone of profile
        """
        zmax = max(profil[:, 1])
        liste_poly = []
        if zmax != profil[0, 1]:
            liste_poly.append([profil[0, 0], zmax])
        for x, z in profil:
            liste_poly.append([x, z])
        if zmax != profil[-1, 1]:
            liste_poly.append([profil[-1, 0], zmax])
        liste_poly.append([profil[0, 0], zmax])

        poly_p = Polygon(liste_poly)

        return poly_p

    def add_info(self, txt):
        self.msg += txt + '\n'
