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
from shapely import wkb
from shapely.geometry import *

from .ClassBradley import ClassBradley
from .ClassTableStructure import ClassTableStructure


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

    def poly_pont_cadre(self, param_g, param_elem, x0=None, zmin=-99999):
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

    def poly_arch(self, param_g, param_elem, x0=None, zmin=-99999, type='circle'):
        """ creation polygone for "pont arch" """
        if x0 is None:
            x0 = param_g['FIRSTWD']  # point depart
        x1 = x0 + param_elem['LARGTRA']
        x_c = param_elem['LARGTRA'] / 2. + x0
        z = param_elem['cotarc']
        if type == 'ellipse':
            zmax = param_elem['cotmax']
            # hyp. zmax-z=b/2
            b = 2 * (zmax - z)
            z_c = zmax - b
            frac = m.pow(x0 - x_c, 2) / (1 - m.pow(z - z_c, 2) / m.pow(b, 2))
            a = m.sqrt(frac)
        elif type == 'circle':
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
            ell = shapely.affinity.scale(circ, int(a), int(b))
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

    def poly_pil(self, param_g, param_elem, x0, zmin=-99999):
        """ creation polygone for "pont cadre" """
        x1 = x0 + param_elem['LARG']
        z = param_g['ZPC']  # point haut
        zmin_t = zmin - 10
        if zmin < z:
            poly_t = Polygon([[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
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
        if config_type == 'PA':
            # parametre general
            list_recup = ['ZTOPTAB', 'FIRSTWD']
            param_g = self.get_param_g(list_recup, id_config)
            recup_trav = ['LARGTRA', 'cotmax', 'cotarc']

        where = "id_config = {0}".format(id_config)  # type=0 span, =1 bridge peir
        order = "id_elem"
        lid_elem = self.mdb.select('struct_elem', where=where, order=order, list_var=['id_elem', "type"])
        first = True
        width = 0
        width_prec = 0
        width_trav = 0

        if not lid_elem["id_elem"]:
            msg = "Not element in table in create_poly_elem function"
            print(msg)
        for i, id_elem in enumerate(lid_elem["id_elem"]):
            # parametre element

            if lid_elem["type"][i] == 1:
                param_elem = self.get_param_elem(id_elem, recup_pil, id_config)
                param_elem['LARG'] = param_elem['LARGPIL']
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
                    poly_elem = self.poly_pont_cadre(param_g, param_elem, width, zmin)
                # pont arc
                if config_type == 'PA':
                    poly_elem = self.poly_arch(param_g, param_elem, width, zmin, type='ellipse')
            else:
                poly_elem = self.poly_pil(param_g, param_elem, width, zmin)

            # print(poly_elem,lid_elem["type"][i])
            # final
            if not poly_elem.is_empty:
                poly_final = poly_elem.difference(poly_p)
            else:
                msg = 'Element bridge polygon is empty.'
                if self.mgis.DEBUG:
                    self.mgis.add_info(msg)
                print(msg)

            if not poly_final.is_empty:
                # self.draw_test(poly_final, decal_ax=10, xmin=profil['x'][0], xmax=profil['x'][-1])
                # # stock element
                where = "WHERE id_config = {0}  AND id_elem = {1} ".format(id_config, id_elem)
                sql = """UPDATE {0}.struct_elem SET polygon ='{1}'  {2}""".format(self.mdb.SCHEMA,
                                                                                  poly_final,
                                                                                  where)
                self.mdb.run_query(sql)
        width += width_prec

        sql = "INSERT INTO {0}.struct_param(id_config,var,value) VALUES ({1}, 'TOTALW', {2});\n".format(self.mdb.SCHEMA,
                                                                                                        id_config,
                                                                                                        width)
        sql += "INSERT INTO {0}.struct_param(id_config,var,value) VALUES ({1}, 'TOTALOUV', {2});".format(
            self.mdb.SCHEMA,
            id_config,
            width_trav)
        self.mdb.run_query(sql)

    def select_poly(self, table, where='', order='', var='polygon'):
        """ select polygon
        example:
                where = "id_config = {0} AND id_elem = {1}".format(self.id_config, id_elem)
                toto=self.select_poly('struct_elem',where)
                print(toto)
        """

        poly_l = self.mdb.select(table, where=where, order=order, list_var=[var])
        list_poly = []
        version = sys.version.split()[0]
        version = version.split('.')[0]
        for poly in poly_l[var]:
            if version==3:
                list_poly.append(wkb.loads(poly,hex=True))
            else:
                list_poly.append(wkb.loads(poly.decode('hex')))
        poly_l[var] = list_poly
        return poly_l

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

    def create_law(self, dossier, nom, type, list_final):
        """creeation of law"""
        with open(os.path.join(dossier, nom + '.loi'), 'w') as fich:
            fich.write('# ' + nom + '\n')
            if type == 6:
                fich.write('# Debit Cote_Aval Cote_Amont\n')
                chaine = ' {flowrate:.3f} {z_downstream:.3f} {z_upstream:.3f}\n'
                info = np.array(list_final)
                # info = info[np.lexsort(([0,1]*info[:,[0,0]]).T)]
                # trie de la colonne 0 à 2
                info = info[info[:, 2].argsort()]  # First sort doesn't need to be stable.
                info = info[info[:, 1].argsort(kind='mergesort')]
                info = info[info[:, 0].argsort(kind='mergesort')]
                list_final = list(info)
                for val in list_final:
                    dico = {'flowrate': val[0], 'z_downstream': val[1], 'z_upstream': val[2]}
                    fich.write(chaine.format(**dico))

    def save_law_st(self, method, id_config, list_val):

        self.mdb.delete('struct_laws', where="id_config = '{}'".format(id_config))
        liste_col = self.mdb.list_columns('struct_laws')
        list_insert = []
        list_val = np.array(list_val)
        for j in self.tbst.dico_law_struct[method].keys():
            for i, val in enumerate(list_val[:, j]):
                list_insert.append([id_config, j, i, val])
        #
        var = ",".join(liste_col)
        valeurs = "("
        for k in liste_col:
            valeurs += '%s,'
        valeurs = valeurs[:-1] + ")"

        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                            'struct_laws',
                                                            var,
                                                            valeurs)

        self.mdb.run_query(sql, many=True, list_many=list_insert)

    def get_list_law(self, id_config):
        where = "WHERE id_config={}".format(id_config)
        order = "ORDER BY id_var, id_order "
        sql = "SELECT {4} FROM {0}.{1} {2} {3};"
        tabval = self.mdb.run_query(sql.format(self.mdb.SCHEMA, "struct_laws", where, order, 'id_var , value'),
                                    fetch=True)
        tabval = np.array(tabval)
        nbval = collections.Counter(tabval[:, 0])
        nb = int(nbval[0])
        nb_val = int(len(nbval.keys()))
        liste_f = []
        for i in range(nb):
            list_tmp = []
            for j in nbval.keys():
                list_tmp.append(tabval[int(j) * nb + i, 1])
            liste_f.append(list_tmp)
        return liste_f

    # def main(self):
    #     self.brad=ClassBradley(self)
    #     struct_dico = self.get_struct()
    #     for id_config in struct_dico:
    #         dico_st = struct_dico[id_config]
    #         if dico_st["active"]:
    #             if dico_st['idmethod'] == 0 or dico_st['idmethod'] == 4:
    #                 listf =  self.brad.bradley(method=dico_st['method'])
    #                 self.save_law_st(dico_st['method'], id_config, listf)
    #             elif dico_st['idmethod'] == 2:
    #                 pass
    #             else:
    #                 pass

    def sav_meth(self, id_config, idmethod):
        self.brad = ClassBradley(self)
        if idmethod == 0 or idmethod == 4:
            self.brad.bradley(id_config, self.tbst.dico_meth_calc[idmethod])
        elif idmethod == 2:
            pass
        else:
            pass


if __name__ == '__main__':
    pass
