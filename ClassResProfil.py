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

class ClassResProfil():
    """

    """

    def __init__(self,pk, prof, branch, min_bed, maj_bed,
                 database=None,
                 plani = None,
                 ksmaj = None,
                 ksmin = None
                 ,debug=False):

        self.cas_prt = {0: 'minor profile',
                   1: 'left major profile',
                   2: 'right major profile',
                   3: 'left stockage zone',
                   4: 'right stockage zone', }
        self.dico_res = {}

        self.pk = pk
        self.debug = debug
        self.branch = branch
        self.prof = prof
        self.min_bed = min_bed
        self.maj_bed = maj_bed
        self.warning_message = ''
        if database :
            self.mdb = database
            self.plani, self.ksmaj , self.ksmin = self.get_plani_ks()
        else:
            self.plani, self.ksmaj, self.ksmin = plani, ksmaj,ksmin
        pr_m, pr_g, pr_d, pr_st_g, pr_st_d = self.decoup_pr(prof, min_bed,
                                                            maj_bed)
        self.lst_pr = [(0, pr_m),
                  (1, pr_g),
                  (2, pr_d),
                  (3, pr_st_g),
                  (4, pr_st_d)]



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
                                         'majbedcoef','active'])

        if rows:

            for i, zone in enumerate(rows['zonenum']):
                if rows['zoneabsstart'][i] <= self.pk <= rows['zoneabsend'][i]:
                    plani = rows['planim'][i]
                    ksmaj =  rows['minbedcoef'][i]
                    ksmin =  rows['majbedcoef'][i]
                    if rows['active'][i]:
                        break

        return plani,ksmaj ,ksmin



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
        if pr_m == []:
            txt = 'Pas de profil lit mineur'
            if self.debug :
                print(txt)
            self.warning_message += txt
            self.warning_message += '\n'
            return [], [], [], [], []
        if pr_g == []:
            pr_g = [pr_m[0], pr_m[0]]
        else:
            pr_g = pr_g + [pr_m[0], pr_m[0]]
        if pr_d == []:
            pr_d = [pr_m[-1], pr_m[-1]]
        else:
            pr_d = [pr_m[-1], pr_m[-1]] + pr_d
        if pr_st_g == []:
            pr_st_g = [pr_g[0], pr_g[0]]
        else:
            pr_st_g = pr_st_g + [pr_g[0], pr_g[0]]
        if pr_st_d == []:
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
            if self.debug :
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
            if self.debug :
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
        pzmax = pr[id_g, 1]
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
            pasz = (zmax - zmin) / (pas)

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

    def  get_poly_disc(self, line_disc, pt_bas) :
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

        for num, prof_tmp in self.lst_pr:
            if num == 0:
                ks = self.ksmin
            elif num ==1 or num ==2:
                ks = self.ksmaj
            else:
                ks =0.0
            self.dico_res[num] = {}
            prof = np.array(prof_tmp)
            # ***************
            id_g = 0
            id_d = -1
            if (prof[id_g] == prof[id_d]).all():
                #print('No profile')
                continue
            x_g, z_g = (prof[id_g, 0], prof[id_g, 1])
            x_d, z_d = (prof[id_d, 0], prof[id_d, 1])
            minz = np.min(prof[:, 1])

            # **************************
            larg_miroir = abs(x_g - x_d)
            self.dico_res[num]['larg_miroir'] = larg_miroir

            id_f = np.where(prof[:, 1] == minz)[0]
            if len(id_f) > 1:
                x_fond = np.mean(prof[id_f, 0])
            else:
                x_fond = prof[id_f[0], 0]
            pt_bas = (x_fond, minz)
            self.dico_res[num]['pt_bas'] = pt_bas

            zmax = max(z_g, z_d)

            line_disc, poly = self.discret_pr_lg(prof, x_fond, minz, zmax,
                                                 pas=self.plani,
                                                 id_g=0, id_d=-1,
                                                 cond_pas_z=True)
            self.dico_res[num]['F'] = line_disc
            lst_poly = self.get_poly_disc(line_disc, pt_bas)
            self.dico_res[num]['poly'] = []
            self.dico_res[num]['area'] = []
            self.dico_res[num]['perimeter'] = []
            self.dico_res[num]['width'] = []
            self.dico_res[num]['z'] = []
            self.dico_res[num]['debitance'] = []
            last_poly = None
            for id, poly in enumerate(lst_poly) :
                if id == 0:
                    perimeter = poly.length
                    area = poly.area
                    last_poly = poly
                    self.dico_res[num]['poly'].append(poly)
                    self.dico_res[num]['area'].append(area)
                    self.dico_res[num]['perimeter'].append(perimeter)
                    (minx, minz, maxx, maxz) = poly.bounds
                    self.dico_res[num]['z'].append(maxz)
                    self.dico_res[num]['width'].append(line_disc[id].length)
                    self.dico_res[num]['debitance'].append(
                        self.debitance(num, ks, perimeter, area))
                else:
                    new_poly = cascaded_union([last_poly,poly])
                    if new_poly.is_valid :
                        perimeter = new_poly.length
                        area = new_poly.area
                        self.dico_res[num]['poly'].append(new_poly)
                        self.dico_res[num]['area'].append(area)
                        self.dico_res[num]['perimeter'].append(perimeter)
                        (minx, minz, maxx, maxz) = new_poly.bounds
                        self.dico_res[num]['z'].append(maxz)
                        self.dico_res[num]['width'].append(line_disc[id].length)

                        self.dico_res[num]['debitance'].append(
                            self.debitance(num,ks, perimeter, area))
                        last_poly = new_poly

            self.dico_res[num]['pr_poly'] = self.dico_res[num]['poly'][-1]
            self.dico_res[num]['pr_area'] = self.dico_res[num]['area'][-1]
            self.dico_res[num]['pr_perimeter'] = self.dico_res[num]['perimeter'][-1]
            self.dico_res[num]['pr_width'] = self.dico_res[num]['width'][-1]
            self.dico_res[num]['pr_z'] = self.dico_res[num]['z'][-1]

            self.dico_res[num]['pr_debitance'] =  \
                self.debitance(num, ks, self.dico_res[num]['perimeter'][-1],
                               self.dico_res[num]['area'][-1])


    def debitance(self,num, ks, perimeter, area):
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
        if num ==3 or num ==4:
            # No debitance when stockage zone
            return None
        if perimeter > 0:
            debitance = ks * area * (area / perimeter) ** (2 / 3)
        else:
            debitance = 0.0
        return  debitance



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





