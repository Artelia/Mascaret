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
import collections
import math as m
import numpy as np
import os
import sys
import shapely.affinity
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from shapely import wkt
from shapely.geometry import *

import time
from .ClassLaws import ClassLaws
from .ClassTableStructure import ClassTableStructure
from scipy import interpolate


class ClassMethod:
    def __init__(self, mgis):
        self.mgis = mgis
        self.mdb = mgis.mdb
        self.grav = 9.81
        self.epsi = 0.0001
        self.tbst = ClassTableStructure()

    def get_param_g(self, list_recup, id_config):
        """get general parameters"""
        param_g = {}
        for info in list_recup:
            where = "id_config = {0} AND var = '{1}' ".format(id_config, info)
            rows = self.mdb.select('struct_param', where=where, list_var=['value'])
            if rows['value']:
                param_g[info] = rows['value'][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info('{} not specified in struct_param table'.format(info))

        return param_g

    def get_param_elem(self, id_elem, list_recup, id_config):
        """get element parameters"""
        param_elem = {}
        for info in list_recup:
            where = "id_config = {0} AND id_elem= {1} AND var = '{2}' ".format(id_config, id_elem, info)
            rows = self.mdb.select('struct_elem_param', where=where, list_var=['value'])

            if rows['value']:
                param_elem[info] = rows['value'][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info('{} not specified in struct_elem_param table'.format(info))

        return param_elem

    def get_profil(self, id_config):
        """profil coordonnee"""
        where = "id_config = {0}".format(id_config)
        order = "id_order"
        profil = self.mdb.select('profil_struct', where=where, order=order, list_var=['x,z'])
        return profil

    def checkprofil(self, id_config):
        """"check profil if it exists"""
        where = "id_config = {0}".format(id_config)
        profil = self.mdb.select('profil_struct', where=where, list_var=['id_order'])
        if profil['id_order']:
            return True
        else:
            return False

    def poly_pont_cadre(self, param_g, param_elem, x0=None, zmin=-99999, ecart=10):
        """ creation polygone for "pont cadre" """
        if x0 is None:
            x0 = param_g['FIRSTWD']  # point depart
        x1 = x0 + param_elem['LARGTRA']
        z = param_g['ZPC']  # point haut
        zmin_t = zmin - 10
        if zmin < z:
            poly_t = Polygon([[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
        else:
            poly_t = GeometryCollection()

            print('Inconsistent Z for the span')
        return poly_t

    def poly_dalot(self, param_elem, x0):
        """ creation polygone for "pont cadre" """
        x1 = x0 + param_elem['LARGTRA']
        z = param_elem['COTERAD'] + param_elem['HAUTDAL']  # point haut
        zmin = param_elem['COTERAD']
        if zmin < z:
            poly_t = Polygon([[x0, zmin], [x0, z], [x1, z], [x1, zmin], [x0, zmin]])
        else:
            poly_t = GeometryCollection()

            print('Inconsistent Z for the span')
        return poly_t

    def poly_buse(self, param_elem):
        """z_rad cote radier
            x0 x en zero"""
        z_c = param_elem['COTERAD'] + (param_elem['LARGTRA'] / 2)
        x_c = param_elem['ABSBUSE']
        circ = Point([x_c, z_c]).buffer(param_elem['LARGTRA'] / 2)
        return circ


    def poly_arch(self, param_g, param_elem, x0=None, zmin=-99999):
        """ creation polygone for "pont arch" """
        type = param_elem['FORMARC']
        if x0 is None:
            x0 = param_g['FIRSTWD']  # point depart
        x1 = x0 + param_elem['LARG']
        x_c = param_elem['LARG'] / 2. + x0
        z = param_elem['ZMINARC']
        if type == 2: #ellipse
            zmax = param_elem['ZMAXARC']
            # hyp. zmax-z=b/2
            b = 2 * (zmax - z)
            z_c = zmax - b
            frac = m.pow(x0 - x_c, 2) / (1 - m.pow(z - z_c, 2) / m.pow(b, 2))
            a = m.sqrt(frac)
        elif type == 1: #circle
            b = param_elem['LARG'] / 2.
            a = b
            z_c = z
        else:
            poly_t = GeometryCollection()
            msg = 'Unkwnown arch : {}'.format(type)
            if self.mgis.DEBUG:
                self.mgis.add_info(msg)
            print(msg)
            return poly_t

        zmin_t = zmin - 10
        if zmin < z:
            # Let create a circle of radius 1 around center point:
            circ = Point([x_c, z_c]).buffer(1)
            # Let create the ellipse along x and y:
            ell = shapely.affinity.scale(circ, a, b)
            # # If one need to rotate it clockwise along an upward pointing x axis:
            # poly_t = shapely.affinity.rotate(ell, 90 - ellipse[2])
            # # According to the man, a positive value means a anti-clockwise angle,
            # # and a negative one a clockwise angle.
            poly = Polygon([[x_c - a - 1, z - b * 2], [x_c - a - 1, z], [x_c + a + 1, z], [x_c + a + 1, z - b * 2],
                            [x_c - a - 1, z - b * 2]])
            ell = ell.difference(poly)  # demi circle
            poly = Polygon([[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
            poly_t = ell.union(poly)
        else:
            poly_t = GeometryCollection()
            msg = 'Inconsistent Z for the span'
            if self.mgis.DEBUG:
                self.mgis.add_info(msg)
            print(msg)
        return poly_t

    def poly_profil_del(self, profil, zmin=-99999):
        """ creation profile polygone """
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
        """ creation polygone for "pont cadre" """
        x1 = x0 + param_elem['LARG']
        z0 = param_elem['ZMAXELEM']
        z1 = param_elem['ZMAXELEM_P1']  # point haut
        zmin_t = zmin - 10
        if zmin < z1 and zmin < z0:
            poly_t = Polygon([[x0, zmin_t], [x0, z0], [x1, z1], [x1, zmin_t], [x0, zmin_t]])
        else:
            poly_t = GeometryCollection()

            print('Inconsistent Z for the pier')
        return poly_t

    def create_poly_elem(self, id_config, config_type):
        # TODO reactualiser variable
        # get profil
        if self.checkprofil(id_config):
            profil = self.get_profil(id_config)
        else:
            msg = "Profile copy isn't found"
            self.mgis.add_info(msg)
            print(msg)
            return
        zmin = min(profil['z'])
        poly_p = self.poly_profil_del(profil, zmin)
        if poly_p.is_empty:
            msg = 'Profile polygon is empty.'
            if self.mgis.DEBUG:
                self.mgis.add_info(msg)
            print(msg)
            return
        if config_type == 'PC':
            # parametre general
            list_recup = ['EPAITAB', 'ZTOPTAB', 'FIRSTWD']
            param_g = self.get_param_g(list_recup, id_config)
            param_g['ZPC'] = param_g['ZTOPTAB'] - param_g['EPAITAB']
            recup_trav = ['LARGTRA']
            recup_pil = ['FORMPIL', 'LARGPIL', 'LONGPIL']
            recup_p1 = []
        elif config_type == 'PA':
            # parametre general
            list_recup = ['ZTOPTAB', 'FIRSTWD']
            param_g = self.get_param_g(list_recup, id_config)
            recup_trav = ['FORMARC', 'LARGTRA', 'ZMINARC', 'ZMAXARC']
            recup_pil = ['LARGPIL']
            recup_p1 = ['FORMARC','ZMINARC']
        elif config_type == 'DA':
            list_recup = ['ZTOPTAB', 'FIRSTWD']
            param_g = self.get_param_g(list_recup, id_config)
            recup_trav = ['LARGTRA', 'COTERAD', 'HAUTDAL']
            recup_pil = ['LARGPIL']
            recup_p1 = ['COTERAD', 'HAUTDAL']
        elif config_type == 'BU':
            list_recup = ['ZTOPTAB']
            param_g = self.get_param_g(list_recup, id_config)
            param_g['FIRSTWD'] = 0
            recup_trav = ['COTERAD', 'ABSBUSE', 'LARGTRA']

        where = "id_config = {0}".format(id_config)  # type=0 span, =1 bridge peir
        order = "id_elem"
        lid_elem = self.mdb.select('struct_elem', where=where, order=order, list_var=['id_elem', "type"])
        first = True

        width = 0
        width_prec = 0
        width_trav = 0
        sav_zmaxelem = 0
        if not lid_elem["id_elem"]:
            msg = "Not element in table in create_poly_elem function"
            print(msg)
        for i, id_elem in enumerate(lid_elem["id_elem"]):
            # parametre element

            if lid_elem["type"][i] == 1:
                param_elem = self.get_param_elem(id_elem, recup_pil, id_config)
                param_elem['LARG'] = param_elem['LARGPIL']
                if recup_p1:
                    param_p1 = self.get_param_elem(id_elem+1, recup_p1, id_config)
            else:
                param_elem = self.get_param_elem(id_elem, recup_trav, id_config)
                param_elem['LARG'] = param_elem['LARGTRA']
                width_trav += param_elem['LARG']
            if first:
                width = param_g['FIRSTWD']
                first = False
            else:
                width += width_prec
            width_prec = param_elem['LARG']
            if lid_elem["type"][i] != 1:
                # # pont Cadre
                if config_type == 'PC':
                    param_elem['ZMAXELEM'] = param_g['ZPC']
                    sav_zmaxelem = param_elem['ZMAXELEM']
                    poly_elem = self.poly_pont_cadre(param_g, param_elem, width, zmin)
                # pont arc
                elif config_type == 'PA':
                    param_elem['ZMAXELEM'] = param_elem['ZMINARC']
                    sav_zmaxelem = param_elem['ZMAXELEM']
                    poly_elem = self.poly_arch(param_g, param_elem, width, zmin)
                # buse
                elif config_type == 'DA':
                    param_elem['ZMAXELEM'] = param_elem['COTERAD'] + param_elem['HAUTDAL']
                    sav_zmaxelem = param_elem['ZMAXELEM']
                    poly_elem = self.poly_dalot(param_elem, width)
                # buse
                elif config_type == 'BU':
                    poly_elem = self.poly_buse(param_elem)

            else:
                #Attention Arc  hauteur different entre droite et gauchs(aproximation  /|  ) pb seul bradley
                #                                                                     |_|
                if config_type == 'PC':
                    param_elem['ZMAXELEM'] = sav_zmaxelem
                    param_elem['ZMAXELEM_P1'] = param_g['ZPC']
                    poly_elem = self.poly_pil(param_elem, width, zmin)
                elif config_type == 'PA':
                    param_elem['ZMAXELEM'] = sav_zmaxelem
                    param_elem['ZMAXELEM_P1'] = param_p1['ZMINARC']
                    poly_elem = self.poly_pil( param_elem, width, zmin)
                elif config_type == 'DA':
                    param_elem['ZMAXELEM'] = sav_zmaxelem
                    param_elem['ZMAXELEM_P1'] = param_p1['COTERAD'] + param_p1['HAUTDAL']
                    poly_elem = self.poly_pil( param_elem, width, zmin)


            # final
            if not poly_elem.is_empty:
                poly_final = poly_elem.difference(poly_p)
            else:
                poly_final = GeometryCollection()
                msg = 'Element bridge polygon is empty.'
                if self.mgis.DEBUG:
                    self.mgis.add_info(msg)
                print(msg)

            if not poly_final.is_empty:
                # self.draw_test(poly_final, decal_ax=10, xmin=profil['x'][0], xmax=profil['x'][-1])
                # # stock element
                if poly_final.geom_type == 'MultiPolygon':
                    poly_final='Null'
                where = "WHERE id_config = {0}  AND id_elem = {1} ".format(id_config, id_elem)
                sql = """UPDATE {0}.struct_elem SET polygon ='{1}'  {2}""".format(self.mdb.SCHEMA,
                                                                                  poly_final,
                                                                                  where)
                self.mdb.run_query(sql)
        width += width_prec

        # sql = "SELECT * FROM {0}.struct_param WHERE id_config = {1} AND var = 'TOTALOUV'" \
        #     .format(self.mdb.SCHEMA, id_config)
        # row = self.mdb.run_query(sql, fetch=True)
        # if len(row) > 0:
        #     sql = "UPDATE {0}.struct_param SET value = {2} WHERE id_config = {1} AND var = 'TOTALOUV'" \
        #         .format(self.mdb.SCHEMA, id_config, width_trav)
        #     self.mdb.execute(sql)
        # else:
        #     sql = "INSERT INTO {0}.struct_param (id_config, var, value) VALUES ({1}, 'TOTALOUV', {2})" \
        #         .format(self.mdb.SCHEMA, id_config, width_trav)
        #     self.mdb.execute(sql)

        # sql = "INSERT INTO {0}.struct_param(id_config,var,value) VALUES ({1}, 'TOTALOUV', {2});".format(
        #     self.mdb.SCHEMA,
        #     id_config,
        #     width_trav)
        # self.mdb.run_query(sql)

    def select_poly(self, table, where='', order='', var='polygon'):
        """ select polygon
        example:
                where = "id_config = {0} AND id_elem = {1}".format(self.id_config, id_elem)
                toto=self.select_poly('struct_elem',where)
                print(toto)
        """
        list_var=[]
        if where:
            where = " WHERE " + where + " "
        if order:
            order = " ORDER BY " + order
        sql = "SELECT ST_AsText(Polygon)  AS Polygon  FROM {0}.{1} {2} {3};"
        (results, namCol) = self.mdb.run_query(sql.format(self.mdb.SCHEMA, table, where, order), fetch=True, namvar=True)
        cols = [col[0] for col in namCol]
        dico = {}
        for col in cols:
            dico[col] = []
        for row in results:
            for i, val in enumerate(row):
                if val is not None:
                    try:
                        dico[cols[i]].append(wkt.loads(val.strip()))
                    except:
                        dico[cols[i]].append(wkt.loads(val))

        return dico

    def copy_profil(self, gid, id_struct, feature):
        """Profil copy"""
        colonnes = ['id_config', 'id_order', 'x', 'z']
        tab = {'x': [], 'z': []}

        where = "gid = '{0}' ".format(gid)
        feature = self.mdb.select('profiles', where=where, list_var=['x', 'z', 'abscissa', ''])
        tab['x'] = [float(var) for var in feature["x"][0].split()]
        tab['z'] = [float(var) for var in feature["z"][0].split()]

        if len(tab['x']) == 0 or len(tab['z']) == 0:
            self.mgis.add_info("Check if the profile is saved.")
            return

        xz = list(zip(tab['x'], tab['z']))
        values = []
        for order, (x, z) in enumerate(xz):
            values.append([id_struct, order, x, z])

        self.mdb.insert_res('profil_struct', values, colonnes)

        tab = {'abscissa': feature['abscissa'],
               'branchnum': feature['branchnum'],
               'id_config': id_struct}
        self.mdb.update('struct_config', tab, var='id_config')

        # sql = """UPDATE {0}.{1} SET abscissa='{2}', branchnum={3}  WHERE id_config='{4}'"""
        #
        # self.mdb.run_query(sql.format(self.mdb.SCHEMA,
        #                               'struct_config',
        #                               feature['abscissa'],
        #                               feature['branchnum'],
        #                           id_config))

    def coup_poly_h(self, poly, cote):
        """fonction si ligne cote es compris entre le xmin et xmax"""
        msg = None
        (minx, miny, maxx, maxy) = poly.bounds
        delpoly = Polygon([[minx - 1, cote], [maxx + 1, cote],
                           [maxx + 1, maxy + 1], [minx - 1, maxy + 1],
                           [minx - 1, cote]])
        if not delpoly.is_empty:
            polyw = poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"
        else:
            polyw = GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"

        if self.mgis.DEBUG and msg is not None:
            print(msg)
        return polyw

    def coup_poly_h(self, poly, cote):
        """fonction si ligne cote es compris entre le xmin et xmax"""
        msg = None
        (minx, miny, maxx, maxy) = poly.bounds
        delpoly = Polygon([[minx - 1, cote], [maxx + 1, cote],
                           [maxx + 1, maxy + 1], [minx - 1, maxy + 1],
                           [minx - 1, cote]])
        if not delpoly.is_empty:
            polyw = poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"
        else:
            polyw = GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"

        if self.mgis.DEBUG and msg is not None:
            print(msg)
        return polyw

    def coup_poly_v(self, poly, xo, typ='L'):
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

        if self.mgis.DEBUG and msg is not None:
            print(msg)
        return polyw

    def get_abac(self, list_recup):
        """get abac"""
        name_abac = []
        dico_abc = {}
        table = 'struct_abac'
        for metho in list_recup:
            where = "nam_method = '{0}' ".format(metho)
            list_nam = self.mdb.select_distinct("nam_abac", table, where)['nam_abac']

            name_abac += list_nam
            for nam_abc in list_nam:
                sql = "SELECT DISTINCT var FROM {}.{} WHERE nam_method='{}' and nam_abac='{}';".format(
                    self.mdb.SCHEMA, table, metho, nam_abc)

                list_var = self.mdb.run_query(sql, fetch=True, namvar=False)
                dico_abc[nam_abc] = {}
                for var in list_var:
                    dico_abc[nam_abc][var[0]] = []
                    dico_abc[nam_abc]['order_{}'.format(var[0])] = []

                sql = "SELECT  var,value,id_order FROM {}.{} WHERE nam_method='{}' " \
                      "and nam_abac='{}' ORDER by id_order ;".format(self.mdb.SCHEMA, table, metho, nam_abc)
                rows = self.mdb.run_query(sql, fetch=True, namvar=False)

                for row in rows:
                    dico_abc[nam_abc][row[0]].append(row[1])
                    dico_abc[nam_abc]['order_{}'.format(row[0])].append(row[2])

        return dico_abc

    def poly_profil(self, profil):
        """ creation profile polygone """

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

    def get_struct(self):
        """get struct dico"""
        struct_dico = {}
        list_var = ['id', 'name', 'type', 'active', 'method']
        if list_var is not None:
            lvar = ','.join([str(v) for v in list_var])
        else:
            lvar = '*'
        sql = "SELECT {1} FROM {0}.struct_config ORDER BY id;"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA, lvar), fetch=True)
        if rows is None:
            if self.mgis.DEBUG:
                self.mgis.add_info('struct_config is empty')
        for row in rows:
            struct_dico[row[0]] = {'name': row[1],
                                   'type': row[2],
                                   'active': row[3],
                                   'idmethod': row[4],
                                   'method': self.tbst.dico_meth_calc[row[4]]}
        #
        return struct_dico

    def create_law(self, dossier, nom, typel, list_final):
        """creation of law"""

        if list_final == []:
            return
        with open(os.path.join(dossier, nom + '.loi'), 'w') as fich:
            fich.write('# ' + nom + '\n')
            if typel == 6:
                fich.write('# Debit Cote_Aval Cote_Amont\n')
                chaine = ' {flowrate:.3f} {z_downstream:.3f} {z_upstream:.3f}\n'
                info = np.array(list_final)
                # info = info[np.lexsort(([0,1]*info[:,[0,0]]).T)]
                # trie de la colonne 0 à 2
                info = info[info[:, 2].argsort()]  # First sort doesn't need to be stable.
                info = info[info[:, 1].argsort(kind='mergesort')]
                info = info[info[:, 0].argsort(kind='mergesort')]
               # list_final = list(info)
                list_final= self.complete_law(info)

                for val in list_final:
                    dico = {'flowrate': val[0], 'z_downstream': val[1], 'z_upstream': val[2]}
                    fich.write(chaine.format(**dico))

    def complete_law(self, info):
        new_info=[]
        q_unique = np.unique(info[:,0])
        h_unique = np.unique(info[:, 1])
        for deb in q_unique:
            info_tmp = info[np.where(info[:,0]==deb)]
            if len(info_tmp)>1:
                hmax = max(list(info_tmp[:, 1]))
                idmax = list(info_tmp[:, 1]).index(hmax)
                hmin = min(list(info_tmp[:, 1]))
                idmin = list(info_tmp[:, 1]).index(hmin)
                varmax = abs(info_tmp[idmax , 1]-info_tmp[idmax , 2])

                val_tmp=np.interp(h_unique, info_tmp[:, 1], info_tmp[:, 2])

                for i,hau in enumerate(h_unique):
                    valf =  val_tmp[i]
                    if hau > hmax:
                        valf = hau + varmax
                    new_info.append([deb,hau,valf])
        return new_info


    def save_law_st(self, method, id_config, list_val):
        """ stock law in database"""
        self.mdb.delete('struct_laws', where="id_config = '{}'".format(id_config))
        liste_col = self.mdb.list_columns('struct_laws')
        list_insert = []
        list_val = np.array(list_val)
        for j in self.tbst.dico_law_struct[method].keys():
            for i, val in enumerate(list_val[:, j]):
                list_insert.append([id_config, j, i, val])
        var = ",".join(liste_col)

        sql=''
        for a in list_insert:
            valeurs=str(tuple(a))
            sql += "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                                'struct_laws',
                                                                var,
                                                                valeurs)
        self.mdb.run_query(sql)

    def get_list_law(self, id_config):
        liste_f = []

        where = "WHERE id_config={}".format(id_config)
        order = "ORDER BY id_var, id_order "
        sql = "SELECT {4} FROM {0}.{1} {2} {3};"
        tabval = self.mdb.run_query(sql.format(self.mdb.SCHEMA, "struct_laws", where, order, 'id_var , value'),
                                    fetch=True)
        if not tabval:
            return liste_f
        tabval = np.array(tabval)
        nbval = collections.Counter(tabval[:, 0])
        nb = int(nbval[0])

        for i in range(nb):
            list_tmp = []
            for j in nbval.keys():
                list_tmp.append(tabval[int(j) * nb + i, 1])
            liste_f.append(list_tmp)
        return liste_f

    def sav_meth(self, id_config, idmethod,ui):
        self.brad = ClassLaws(self)

        if idmethod == 0 or idmethod == 4: # brad
            self.brad.bradley(id_config, self.tbst.dico_meth_calc[idmethod],ui)
        elif  idmethod == 1: #borda
            self.brad.borda(id_config, self.tbst.dico_meth_calc[idmethod], ui)
        elif idmethod == 3: #orifice
            self.brad.orifice(id_config, self.tbst.dico_meth_calc[idmethod], ui)
        else:
            pass

    def update_etat_struct_prof(self, id_config, active=True, delete=False):
        where = "id = {0}".format(id_config)
        prof = self.mdb.select('struct_config', where=where, list_var=['id_prof_ori'])
        gid = prof['id_prof_ori'][0]
        if active:
            tab = {'table': 'profiles',
                   'schema' : self.mdb.SCHEMA,
                   'gid': gid,
                   'struct': 2}
        elif delete:
            tab = {'table': 'profiles',
                   'schema' : self.mdb.SCHEMA,
                   'gid': gid,
                   'struct': 0}
        else:
            tab = {'table': 'profiles',
                   'schema' : self.mdb.SCHEMA,
                   'gid': gid,
                   'struct': 1}
        # self.mdb.update('profiles', tab, var='gid')

        sql = "UPDATE {schema}.{table} SET struct={struct}  WHERE gid={gid}".format(**tab)
        print(sql)
        self.mdb.run_query(sql)

if __name__ == '__main__':
    pass
