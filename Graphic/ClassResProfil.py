# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : September,2021
copyright            : (C) 2021 by Artelia
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

from shapely.geometry import *
from shapely.ops import cascaded_union
import matplotlib.pyplot as plt
import numpy as np
import json


class ClassResProfil:
    """

    """

    def __init__(self, debug=False):
        self.cas_prt = {0: 'minor bed profile',
                        1: 'left major bed profile',
                        2: 'right major bed profile',
                        3: 'left stockage zone',
                        4: 'right stockage zone', }

        self.dico_res = {}
        self.pk = None
        self.plani, self.ksmaj, self.ksmin = None, None, None
        self.debug = debug
        self.branch = None
        self.prof = None
        self.min_bed = None
        self.maj_bed = None
        self.warning_message = ''
        self.lst_pr = []
        self.mdb = None
        self.id_run = None

    def init_cl(self, pk, prof, branch, min_bed, maj_bed, id_run,
                database=None,
                plani=None,
                ksmaj=None,
                ksmin=None,
                zmax=None,
                dico_plani=None,
                ):

        self.pk = pk
        self.id_run = id_run
        self.branch = branch
        self.prof = prof
        self.dico_plani = dico_plani
        self.min_bed = min_bed
        self.maj_bed = maj_bed
        self.warning_message = ''
        self.dico_res = {}
        self.lst_pr = []
        self.zmax = zmax

        if database:
            self.mdb = database
            self.plani, self.ksmaj, self.ksmin = self.get_plani_ks()
        else:
            self.mdb = None
            self.plani, self.ksmaj, self.ksmin = plani, ksmaj, ksmin

    def init_mdb(self, database):
        self.mdb = database

    def get_plani_ks(self):
        """
        Get planimetry value and Strickler coefficient
        :return: plani, ksmaj, ksmin
        """
        plani = None

        rows = self.mdb.select('branchs',
                               where="branch='{}'".format(self.branch),
                               order="zoneabsstart",
                               list_var=['zonenum', 'zoneabsstart',
                                         'zoneabsend', 'planim', 'minbedcoef',
                                         'majbedcoef', 'active'])

        if rows:

            for i, zone in enumerate(rows['zonenum']):
                if rows['zoneabsstart'][i] <= self.pk <= rows['zoneabsend'][i]:
                    plani = rows['planim'][i]
                    ksmaj = rows['minbedcoef'][i]
                    ksmin = rows['majbedcoef'][i]
                    if rows['active'][i]:
                        break

        return plani, ksmaj, ksmin

    def decoup_pr(self, pr, lminor_x, lmaj_x):
        """
        Split profile in :
            minor profile,
            left major profile
            right major profile
            left stockage profile
            right stockage  profile
        :param pr: profile
        :param lminor_x: minor bed zone
        :param lmaj_x: major bed zone
        :return:
        """
        pr_g = []
        pr_d = []
        pr_m = []
        pr_st_g = []
        pr_st_d = []
        for point in pr:
            if point[0] < lminor_x[0]:
                if point[0] < lmaj_x[0]:
                    pr_st_g.append(point)
                else:
                    pr_g.append(point)
            elif point[0] > lminor_x[1]:
                if point[0] > lmaj_x[1]:
                    pr_st_d.append(point)
                else:
                    pr_d.append(point)
            else:
                pr_m.append(point)
        if not pr_m:
            txt = 'Pas de profil lit mineur'
            if self.debug:
                print(txt)
            self.warning_message += txt
            self.warning_message += '\n'
            return [], [], [], [], []
        if not pr_g:
            pr_g = [pr_m[0], pr_m[0]]
        else:
            pr_g = pr_g + [pr_m[0], pr_m[0]]
        if not pr_d:
            pr_d = [pr_m[-1], pr_m[-1]]
        else:
            pr_d = [pr_m[-1], pr_m[-1]] + pr_d
        if not pr_st_g:
            pr_st_g = [pr_g[0], pr_g[0]]
        else:
            pr_st_g = pr_st_g + [pr_g[0], pr_g[0]]
        if not pr_st_d:
            pr_st_d = [pr_d[-1], pr_d[-1]]
        else:
            pr_st_d = [pr_d[-1], pr_d[-1]] + pr_st_d

        return pr_m, pr_g, pr_d, pr_st_g, pr_st_d

    def creat_line_width(self, poly, line, x_fond, z_level):
        """
        Creation linestring with sum of width when MultiLineString
        :param poly: polygone
        :param line: line
        :param x_fond: bottom x
        :param z_level: line level
        :return:
        """

        line = LineString(line)
        geom = line.intersection(poly)
        if geom.is_empty:
            txt = 'Pas d intersection : {}  {}'.format(line, poly)
            if self.debug:
                print(txt)
            self.warning_message += txt
            self.warning_message += '\n'
            line_disc = None
        elif geom.geom_type == 'MultiLineString' \
                or geom.geom_type == 'GeometryCollection':
            id_tmp = 0
            for j, ll in enumerate(geom):
                x, y = ll.xy
                if min(x) <= x_fond <= max(x):
                    id_tmp = j
            l_g = 0
            l_d = 0

            for j, ll in enumerate(geom):
                length = ll.length
                x, y = ll.xy
                if j != id_tmp and max(x) < x_fond:
                    l_g += length
                elif j != id_tmp and min(x) > x_fond:
                    l_d += length
            x, y = geom[id_tmp].xy
            linf = [(x[0] - l_g, z_level), (x[-1] + l_d, z_level)]
            line_disc = LineString(linf)
        elif geom.geom_type == 'LineString':
            line_disc = geom
        else:
            txt = 'Geo type non traite : {}'.format(geom.geom_type)
            if self.debug:
                print(txt)
            self.warning_message += txt
            self.warning_message += '\n'
            line_disc = None

        return line_disc

    def discret_pr_lg(self, pr, x_fond, zmin, zmax, pas=0.1, id_g=0, id_d=-1,
                      cond_pas_z=True):
        """
        vertical descritization
        :param pas : dz in m or nb of plan
        :param cond_pas_z : True si descritization in m or false in plan
        :param id_g : id_am_g id point left
        :param id_d : id_am_d id point right
        :param pr : profile
        :param x_fond : x bottom
        :param zmin : bottom point of the profile
        :param zmax : max level of the profile

        """
        if id_g == id_d:
            return []
        if id_d == -1:
            limit_pr = pr[id_g:]
        else:
            limit_pr = pr[id_g:id_d + 1]

        wow = []
        pzmax = max(zmax, pr[id_g, 1])
        for coord in limit_pr:
            wow.append([coord[0], coord[1]])
            if pzmax < coord[1]:
                pzmax = coord[1]
        wow = [[pr[id_g, 0], pzmax + 1]] + wow
        wow += [[pr[id_d, 0], pzmax + 1]]

        line_pr = LineString(wow)

        poly = Polygon(line_pr)
        lst_line_disc = []

        if not poly.is_valid:
            return lst_line_disc

        if cond_pas_z:
            pasz = pas
        else:
            pasz = (zmax - zmin) / pas

        z_level = zmin

        while z_level + pasz <= zmax:
            # création de line pour découpé

            z_level = z_level + pasz

            line = [(pr[id_g, 0] - 1, z_level), (pr[id_d, 0] + 1, z_level)]
            point_fond = Point([x_fond, z_level])
            line_disc = self.creat_line_width(poly, line, x_fond, z_level)
            if line_disc:
                lst_line_disc.append(line_disc)

        # last line:
        line = [(pr[0, 0] - 1, zmax), (pr[-1, 0] + 1, zmax)]
        line_disc = self.creat_line_width(poly, line, x_fond, zmax)
        if line_disc:
            lst_line_disc.append(line_disc)

        return lst_line_disc, poly

    def print_val(self):
        """
        Print val to check
        :return:
        """

        for key in self.dico_res.keys():
            print('************************')
            print('Profil :', self.cas_prt[key])
            for elem, val in self.dico_res[key].items():
                if elem != 'poly':
                    print('{} , {}'.format(elem, val))

    def get_poly_disc(self, line_disc, pt_bas):
        """
        Generate polygone list of a profile
        :param line_disc: discritzation line
        :param pt_bas: bottom point
        :return:
        """
        # construit plus bas au plus haut
        first_line = list(line_disc[0].coords)
        last_line = list(first_line)
        first_line.append(pt_bas)
        poly_tmp = Polygon(first_line)
        lst_poly = [poly_tmp]

        for line in line_disc[1:]:
            first_line = list(line.coords)
            last_line.reverse()
            tmp_line = first_line + last_line
            poly_tmp = Polygon(tmp_line)
            lst_poly.append(poly_tmp)
            last_line = first_line

        return lst_poly

    def genrete_plani(self, zmax=None):

        pr_m, pr_g, pr_d, pr_st_g, pr_st_d = self.decoup_pr(self.prof,
                                                            self.min_bed,
                                                            self.maj_bed)
        self.lst_pr = [(0, pr_m),
                       (1, pr_g),
                       (2, pr_d),
                       (3, pr_st_g),
                       (4, pr_st_d)]
        self.dico_plani = {}

        for num, prof_tmp in self.lst_pr:
            self.dico_plani[num] = {}
            profile = np.array(prof_tmp)
            if (profile[0] == profile[-1]).all():
                # print('No profile')
                continue
            x_g, z_g = (profile[0, 0], profile[0, 1])
            x_d, z_d = (profile[-1, 0], profile[-1, 1])

            minz = np.min(profile[:, 1])
            id_f = np.where(profile[:, 1] == minz)[0]
            if len(id_f) > 1:
                x_fond = np.mean(profile[id_f, 0])
            else:
                x_fond = profile[id_f[0], 0]
            pt_bas = (x_fond, minz)
            self.dico_plani[num]['pt_bas'] = pt_bas

            if not zmax:
                zmax = max(z_g, z_d)

            line_disc, poly = self.discret_pr_lg(profile, x_fond, minz, zmax,
                                                 pas=self.plani,
                                                 id_g=0, id_d=-1,
                                                 cond_pas_z=True)
            self.dico_plani[num]['lines'] = line_disc
        return self.dico_plani

    def plani_stock(self, dico_zmax, id_run, database):
        self.mdb = database
        prof = self.mdb.select('profiles', order='abscissa', where='active',
                               list_var=['abscissa', 'x', 'z', 'leftminbed',
                                         'rightminbed', 'leftstock',
                                         'rightstock', 'zleftminbed',
                                         'zrightminbed', 'branchnum'])
        point_bas = {}
        list_insert_plani = []
        list_pt_bas = []

        if prof:
            for id, pk in enumerate(prof['abscissa']):
                if pk:
                    try:
                        # **********************************************************

                        x = [float(v) for v in prof['x'][id].split()]
                        z = [float(v) for v in prof['z'][id].split()]
                        profil = list(zip(x, z))

                        min_bed = [prof['leftminbed'][id],
                                   prof['rightminbed'][id]]
                        if prof['leftstock'][id] and \
                                prof['rightstock'][id]:
                            maj_bed = [prof['leftstock'][id],
                                       prof['rightstock'][id]]
                        else:
                            maj_bed = [x[0],
                                       x[-1]]

                        self.init_cl(pk, profil,
                                     prof['branchnum'][id],
                                     min_bed, maj_bed, id_run,
                                     database=self.mdb,
                                     )
                        self.genrete_plani(dico_zmax[str(pk)])

                        point_bas[pk] = {}

                        for id_type, dico in self.dico_plani.items():

                            if 'lines' in dico.keys():
                                for ord, line in enumerate(dico['lines']):
                                    list_insert_plani.append(
                                        [id_run, pk, id_type, ord,
                                         json.dumps(mapping(line))])
                                point_bas[pk][id_type] = dico['pt_bas']

                    except Exception as err:
                        if self.debug:
                            print('Warning Plani', err)
            if self.mdb:
                if point_bas:
                    list_pt_bas = [[id_run, 'opt', 'pt_bas',
                                    json.dumps(point_bas)]]
                self.insert_lst_mdb(list_insert_plani, list_pt_bas)

    def insert_lst_mdb(self, list_insert, point_bas):
        if list_insert:
            col_tab = ['id_runs', 'pknum', 'id_type', 'id_order', 'line']
            var = ",".join(col_tab)
            temp = []
            for k in col_tab:
                if k == 'line':
                    temp.append('ST_GeomFromGeoJSON(%s)')
                else:
                    temp.append('%s')
            valeurs = "({})".format(",".join(temp))
            list_insert2 = []
            for lst in list_insert:
                if lst not in list_insert2:
                    list_insert2.append(lst)
            sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                                "runs_plani",
                                                                var,
                                                                valeurs)
            self.mdb.run_query(sql, many=True, list_many=list_insert2)

        if point_bas:
            col_tab = ['id_runs', 'type_res', 'var', 'val']
            self.mdb.insert_res('runs_graph', point_bas, col_tab)

    def get_results(self):
        """
        get result of "cross section result" :
            mirror width
            wet section
            wet perimeter
            bottom point
            debitance
            discratization level
        :return:
        """
        if self.dico_plani:
            self.dico_res = dict(self.dico_plani)
        else:
            self.dico_res = dict()
        for num, dico in self.dico_res.items():
            if not dico:
                continue
            if not dico['line']:
                continue

            line_disc = dico['line']

            pt_bas = dico['pt_bas']
            if num == 0:
                ks = self.ksmin
            elif num == 1 or num == 2:
                ks = self.ksmaj
            else:
                ks = 0.0

            lst_poly = self.get_poly_disc(line_disc, pt_bas)
            dico['poly'] = []
            dico['area'] = []
            # dico['perimeter'] = []
            dico['width'] = []
            dico['z'] = []
            dico['debitance'] = []
            last_poly = None
            for id, poly in enumerate(lst_poly):
                if id == 0:
                    last_poly = poly
                    (minx, minz, maxx, maxz) = poly.bounds
                    perimeter = poly.length
                    area = poly.area

                    dico['poly'].append(poly)
                    dico['area'].append(area)
                    # dico['perimeter'].append(perimeter)
                    dico['z'].append(maxz)
                    dico['width'].append(line_disc[id].length)
                    dico['debitance'].append(
                        self.debitance(num, ks, perimeter, area))
                else:
                    new_poly = cascaded_union([last_poly, poly])

                    if new_poly.is_valid and not new_poly.is_empty:
                        (minx, minz, maxx, maxz) = new_poly.bounds
                        perimeter = new_poly.length
                        area = new_poly.area
                        dico['poly'].append(new_poly)
                        dico['area'].append(area)
                        # dico['perimeter'].append(perimeter)
                        dico['z'].append(maxz)
                        dico['width'].append(line_disc[id].length)

                        dico['debitance'].append(
                            self.debitance(num, ks, perimeter, area))
                        last_poly = new_poly
            if len(dico['poly']) > 1:
                dico['pr_poly'] = dico['poly'][-1]
                dico['pr_area'] = dico['area'][-1]
                # dico['pr_perimeter'] = dico['perimeter'][-1]
                dico['pr_width'] = dico['width'][-1]
                dico['pr_z'] = dico['z'][-1]
                perimeter = dico['poly'][-1].length
                dico['pr_debitance'] = \
                    self.debitance(num, ks, perimeter,
                                   dico['area'][-1])
            else:
                dico['pr_poly'] = None
                dico['pr_area'] = 0.
                # dico['pr_perimeter'] = 0.
                dico['pr_width'] = 0.
                dico['pr_z'] = 0.

                dico['pr_debitance'] = 0.

    def debitance(self, num, ks, perimeter, area):
        """
         D = K.S.R^2/3
         with K the Strickler coeficient,
         S the wet section and R hydraulic radius
         which is the wet section divided by wet perimeter
        :param num: (int) type  of profile zone
        :param ks: (float) Strickler coeficient
        :param perimeter: (float)wet perimeter
        :param area: (float) wet section
        :return: debitance (float
        """
        if num == 3 or num == 4:
            # No debitance when stockage zone
            return None
        if perimeter > 0:
            debitance = ks * area * (area / perimeter) ** (2 / 3)
        else:
            debitance = 0.0
        return debitance


def get_valeurs(z_level, poly):
    res = {}
    if poly:
        if poly.is_valid and not poly.is_empty:
            (minx, miny, maxx, maxy) = poly.bounds

            if z_level < miny:
                res['z'] = z_level
                res['area'] = None
                res['perimeter'] = None
                res['width'] = None
            else:
                delpoly = Polygon([[minx - 1, z_level], [maxx + 1, z_level],
                                   [maxx + 1, max(z_level + 1, maxy + 1)],
                                   [minx - 1, max(z_level + 1, maxy + 1)],
                                   [minx - 1, z_level]])
                if not delpoly.is_empty:
                    if not poly.is_valid:
                        # Polygone => multiPolygone
                        poly = poly.buffer(0)
                    polyw = poly.difference(delpoly)
                    if not polyw.is_valid:
                        polyw = GeometryCollection()
                else:
                    polyw = GeometryCollection()
                if not polyw.is_empty:
                    (minx, miny, maxx, maxy) = polyw.bounds
                    res['z'] = z_level
                    res['area'] = polyw.area
                    res['perimeter'] = polyw.length
                    res['width'] = maxx - minx
                else:
                    res['z'] = z_level
                    res['area'] = None
                    res['perimeter'] = None
                    res['width'] = None
        else:
            res['z'] = z_level
            res['area'] = None
            res['perimeter'] = None
            res['width'] = None
    else:
        res['z'] = z_level
        res['area'] = None
        res['perimeter'] = None
        res['width'] = None
    return res


if __name__ == '__main__':
    pass
    # **************************************************************
    # **************************************************************

    # min_bed = [300, 520]
    # # maj_bed = [250,570]
    # maj_bed = [300, 520]
    # plani = 1
    # file_av = r'C:\Users\mehdi-pierre.daou\Desktop\ana_schapi\test_visu\31546.45_-_pont_trevoux.csv'
    # with open(file_av) as file:
    #     lp = []
    #     cpt = 0
    #     for line in file:
    #         if cpt != 0:
    #             lst = line.replace('\n', '').split(';')
    #             lp.append((float(lst[0]), float(lst[1])))
    #         cpt += 1
    # pr = lp.copy()
    #
    # pr_av = np.array(pr)
    # fig2 = plt.figure(figsize=(6, 8))
    # ax2 = fig2.add_subplot(111)
    # ax2.plot(pr_av[:, 0], pr_av[:, 1])
    # plt.show()
    #
    # cl_geo = ClassGeoProfil(pr, min_bed ,maj_bed)
    # cl_geo.main()
    # cl_geo.print_val()
