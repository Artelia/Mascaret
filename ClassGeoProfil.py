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

class ClassGeoProfil():
    """

    """

    def __init__(self,prof, min_bed, maj_bed,plani, debug=False):

        self.cas_prt = {0: 'minor profile',
                   1: 'left major profile',
                   2: 'right major profile',
                   3: 'left stockage zone',
                   4: 'right stockage zone', }
        self.dico_res = {}
        self.plani = plani
        self.prof = prof
        self.min_bed = min_bed
        self.maj_bed = maj_bed

        pr_m, pr_g, pr_d, pr_st_g, pr_st_d = self.decoup_pr(prof, min_bed,
                                                            maj_bed)
        self.lst_pr = [(0, pr_m),
                  (1, pr_g),
                  (2, pr_d),
                  (3, pr_st_g),
                  (4, pr_st_d)]

    #
    #
    # def plot_p(self, ax, poly, color='black', label='line',
    #            style='solid', marker=''):
    #     x, y = poly.exterior.xy
    #     ax.plot(x, y, color=color, linestyle=style, marker=marker)
    #
    #
    # def plot_coords3D(self,ax, ob, pk, color='grey', label='line',
    #                   style='solid', marker=''):
    #     x, z = ob.xy
    #     y = [pk for i in range(len(x))]
    #     ax.plot(x, y, z, 'o-', color=color, zorder=1,
    #             label=label, linestyle=style, marker=marker)
    #
    #
    # def plot_coords(self, ax, ob, color='grey', label='line',
    #                 style='solid', marker=''):
    #     x, y = ob.xy
    #     ax.plot(x, y, 'o-', color=color,
    #             linestyle=style, marker=marker,
    #             zorder=1, label=label)

    def decoup_pr(self, pr, lminor_x, lmaj_x):
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
            print('Pas de profil lit mineur')
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

        line = LineString(line)
        geom = line.intersection(poly)
        if geom.is_empty:
            print('Pas d intersection :', line, poly)
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
            print('Geo type non traite :', geom.geom_type)
            line_disc = None

        return line_disc

    def discret_pr_lg(self, pr, x_fond, zmin, zmax, pas=0.1, id_g=0, id_d=-1,
                      cond_pas_z=True):
        """
        descritisation vertical
        pas = dz en m ou nb de plan
        cond_pas_z = True si descritisation en m ou false en plan
        id_g = id_am_g id point g
        id_d = id_am_d id point d
        pr =  profile
        zmin = point bas du profikl
        """
        # ***********

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
            # si descritisation en cm
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

        for key in self.dico_res.keys():
            print('************************')
            print('Profil :', self.cas_prt[key])
            for elem, val in self.dico_res[key].items():
                if elem != 'poly':
                    print('{} , {}'.format(elem, val))

    def  get_poly_disc(self, line_disc, pt_bas) :

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


        # fig2 = plt.figure(figsize=(6, 8))
        # ax2 = fig2.add_subplot(111)
        # color = ['r','b','k','g']
        # idc = 0
        # for poly in lst_poly :
        #     self.plot_p(ax2, poly, color=color[idc])
        #     if idc ==3:
        #         idc = 0
        #     else:
        #         idc += 1
        #
        # plt.show()
        return lst_poly

    def main(self):

        for num, prof_tmp in self.lst_pr:
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
                    last_poly = poly
                    self.dico_res[num]['poly'].append(poly)
                    self.dico_res[num]['area'].append(poly.area)
                    self.dico_res[num]['perimeter'].append(poly.length)
                    (minx, minz, maxx, maxz) = poly.bounds
                    self.dico_res[num]['z'].append(maxz)
                    self.dico_res[num]['width'].append(line_disc[id].length)
                    self.dico_res[num]['debitance'].append(0.0)
                else:
                    new_poly = cascaded_union([last_poly,poly])
                    # Plot each polygon shape directly
                    # if new_poly.geom_type == 'MultiPolygon':
                    #     print('MultiPoly Error mege')
                    # elif new_poly.geom_type == 'Polygon':
                    # geom = new_poly
                    # fig2 = plt.figure(figsize=(6, 8))
                    # ax2 = fig2.add_subplot(111)
                    # ax2.plot(*geom.exterior.xy)
                    # ax2.set_ylim([155.29200009155272, 205.1879980773926])
                    # ax2.set_xlim([0.3999999999999986, 695.6])
                    # plt.show()

                    if new_poly.is_valid :
                        self.dico_res[num]['poly'].append(new_poly)
                        self.dico_res[num]['area'].append(new_poly.area)
                        self.dico_res[num]['perimeter'].append(new_poly.length)
                        (minx, minz, maxx, maxz) = new_poly.bounds
                        self.dico_res[num]['z'].append(maxz)
                        self.dico_res[num]['width'].append(line_disc[id].length)
                        self.dico_res[num]['debitance'].append(0.0)
                        last_poly = new_poly

            self.dico_res[num]['pr_poly'] = self.dico_res[num]['poly'][-1]
            self.dico_res[num]['pr_area'] = self.dico_res[num]['area'][-1]
            self.dico_res[num]['pr_perimeter'] = self.dico_res[num]['perimeter'][-1]
            self.dico_res[num]['pr_width'] = self.dico_res[num]['width'][-1]
            self.dico_res[num]['pr_z'] = self.dico_res[num]['z'][-1]
            self.dico_res[num]['pr_debitance'] = 0.0

            # fig2 = plt.figure(figsize=(6, 8))
            # ax2 = fig2.add_subplot(111)
            #
            # for line_pr in line_disc:
            #     self.plot_coords(ax2, line_pr)
            # ax2.plot(prof[:, 0], prof[:, 1], 'red')
            # ax2.set_title(self.cas_prt[num])
            # plt.show()


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





