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

# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import *


# import time


class ClassProfInterp:
    """ """

    def __init__(self, data, pk_int, nplan=100, plani=None, debug=False):
        """
        initialize class
        :param data: dict containing the interpolation data
          data = { 'up': upsteam
                {
                    'prof': Profil,
                    'pk': Pk profil,
                    'minor': minor bed limit,
                    'major': major bed limit,
                },
                'down':downsteam
                { the same     }
                }
        :param pk_int: float , pk interpolation
        :param nplan:  int, number of discretization plan
        """
        self.prf_loc = {}

        self.data = data
        self.data["interp"] = {"prof": None, "minor": None, "major": None, "pk": pk_int}
        self.pk_int = pk_int
        self.pk_am = data["up"]["pk"]
        self.pk_av = data["down"]["pk"]

        self.typ_disc = "plan"
        self.dz = None
        self.nplan = nplan
        self.plani = plani
        self.msg = ""
        self.err = True
        self.debug = debug
        if self.plani is not None:
            self.typ_disc = "autoplan"

    def merge_prof(self, key="prof", id=-1):
        """
        :param key : 'prof' interpolated profile, 'pr_am' upstream profile amont, 'pr_av' downstream profile
        :param id :  profil number (minor, major ,...) ,-1 global
        """
        dico = {}
        if id == -1:
            dico = self.data["interp"]
        else:
            dico = self.prf_loc[id]
        tmp = []
        for pr in dico[key]:
            if pr is not None:
                tmp.append(pr.coords[0][0])
            else:
                tmp.append(None)
        df = pd.DataFrame(tmp, columns=["x"])
        order = df.sort_values(["x"]).index.values
        outprof = []
        for i in order:
            line = dico[key][i]
            if line is not None:
                points = line.coords[:]
                outprof += points

        if outprof:
            prof_final = LineString(outprof)
        else:
            prof_final = None

        return prof_final

    def calc_profil(self, pr_am_tmp, pr_av_tmp, id_pr):
        """
        Caclul the interpolated profile
        :param pr_am_tmp: upstream profile
        :param pr_av_tmp: downstream profile
        :param id_pr: id profile
        :return:
        """
        cas_prt = {
            0: "minor profile",
            1: "left major profile",
            2: "right major profile",
            3: "left stockage zone",
            4: "right stockage zone",
        }
        if len(pr_am_tmp) <= 2 and len(pr_av_tmp) <= 2:
            # print("{} profile doesn't existe".format(id_pr))
            if id_pr == 0:
                # print("Minor bed doesn't existe")
                self.msg += "Minor bed doesn't existe\n"
                self.err = False
                return "break"
            else:
                if self.debug:
                    self.msg += "{}  doesn't existe\n".format(cas_prt[id_pr])
                if id_pr not in self.prf_loc.keys():
                    self.prf_loc[id_pr] = {"prof": []}
                self.prf_loc[id_pr]["prof"].append(None)
                return "continue"
        self.prf_loc[id_pr] = {"prof": []}
        prof_min, limx = self.interpol_fct_lg(pr_am_tmp, pr_av_tmp)

        self.prf_loc[id_pr]["prof"].append(prof_min)
        self.prf_loc[id_pr]["limitx"] = limx
        self.data["interp"]["prof"] += self.prf_loc[id_pr]["prof"]

        return "ok"

    def interpol_fct_lg(self, pr_am, pr_av):
        """

        interpolation of a profile
        :param pr_am: upstream profile
        :param pr_av: downstream profile
        :return:
        """
        pr_am = np.array(pr_am)
        pr_av = np.array(pr_av)

        list_points = []

        # bottom point calculation
        zmin_am = min(pr_am[:, 1])
        zmin_av = min(pr_av[:, 1])
        zmax_am = max(pr_am[:, 1])
        zmax_av = max(pr_av[:, 1])
        id_am_f = np.where(pr_am[:, 1] == zmin_am)[0]
        id_av_f = np.where(pr_av[:, 1] == zmin_av)[0]

        if len(id_am_f) > 1:
            x_am_fond = np.mean(pr_am[id_am_f, 0])
        else:
            x_am_fond = pr_am[id_am_f[0], 0]

        if len(id_av_f) > 1:
            x_av_fond = np.mean(pr_av[id_av_f, 0])
        else:
            x_av_fond = pr_av[id_av_f[0], 0]
        z_am_fond = pr_am[id_am_f[0], 1]
        z_av_fond = pr_av[id_av_f[0], 1]

        z_f = np.interp(self.pk_int, [self.pk_am, self.pk_av], [z_am_fond, z_av_fond])
        x_f = np.interp(self.pk_int, [self.pk_am, self.pk_av], [x_am_fond, x_av_fond])
        list_points.append((x_f, z_f))
        id_am_g = 0
        id_av_g = 0
        id_am_d = -1
        id_av_d = -1
        z0_am = pr_am[id_am_g, 1]
        x0_am = pr_am[id_am_g, 0]
        z1_am = pr_am[id_am_d, 1]
        x1_am = pr_am[id_am_d, 0]

        z0_av = pr_av[id_av_g, 1]
        x0_av = pr_av[id_av_g, 0]
        z1_av = pr_av[id_av_d, 1]
        x1_av = pr_av[id_av_d, 0]

        z_g = np.interp(self.pk_int, [self.pk_am, self.pk_av], [z0_am, z0_av])
        x_g = np.interp(self.pk_int, [self.pk_am, self.pk_av], [x0_am, x0_av])
        list_points.append((x_g, z_g))

        z_d = np.interp(self.pk_int, [self.pk_am, self.pk_av], [z1_am, z1_av])
        x_d = np.interp(self.pk_int, [self.pk_am, self.pk_av], [x1_am, x1_av])
        list_points.append((x_d, z_d))

        # calculated characteristic point
        if self.typ_disc == "plan":
            pas = self.nplan
            cond_pas_z = False
        elif self.typ_disc == "dz":
            pas = self.dz
            cond_pas_z = True
        elif self.typ_disc == "autoplan":
            nplan_am = (zmax_am - zmin_am) / self.plani
            nplan_av = (zmax_av - zmin_av) / self.plani
            pas = max(nplan_am, nplan_av)
            cond_pas_z = False
        else:
            # print('Non-existent discretization type')
            self.msg += "Non-existent discretization type\n"
            self.err = False
            return None, None
        am_g = self.discret_pr_lg(
            pr_am, x_am_fond, zmin_am, pas=pas, id_g=0, id_d=id_am_f[0], cond_pas_z=cond_pas_z
        )
        am_d = self.discret_pr_lg(
            pr_am, x_am_fond, zmin_am, pas=pas, id_g=id_am_f[0], id_d=-1, cond_pas_z=cond_pas_z
        )

        av_g = self.discret_pr_lg(
            pr_av, x_av_fond, zmin_av, pas=pas, id_g=0, id_d=id_av_f[0], cond_pas_z=cond_pas_z
        )
        av_d = self.discret_pr_lg(
            pr_av, x_av_fond, zmin_av, pas=pas, id_g=id_av_f[0], id_d=-1, cond_pas_z=cond_pas_z
        )

        list_points_g = []
        list_points_d = []

        if len(am_g) == 0 and len(am_d) == 0 and len(av_g) == 0 and len(av_d) == 0:
            return None, None
            # in the case where there is no upstream or downstream profile on the portion of the bed
            # the interpolation is done with respect to the point
        if len(am_g) == 0 and len(am_d) == 0:
            line_tmp = LineString([(p[0], p[1]) for p in pr_am])
            am_g = []
            am_d = []
            for i in range(len(av_g)):
                am_g.append(line_tmp)
            for i in range(len(av_d)):
                am_d.append(line_tmp)
        if len(av_g) == 0 and len(av_d) == 0:
            line_tmp = LineString([(p[0], p[1]) for p in pr_av])
            av_g = []
            av_d = []
            for i in range(len(am_g)):
                av_g.append(line_tmp)
            for i in range(len(am_d)):
                av_d.append(line_tmp)

        # left interpol
        for line_am, line_av in zip(am_g, av_g):
            line_am = line_am.coords[:]
            line_av = line_av.coords[:]

            z_tmp = np.interp(self.pk_int, [self.pk_am, self.pk_av], [line_am[0][1], line_av[0][1]])
            x_tmp = np.interp(self.pk_int, [self.pk_am, self.pk_av], [line_am[0][0], line_av[0][0]])
            if x_tmp > x_g and z_tmp < z_g:
                list_points_g.append((x_tmp, z_tmp))

        # right interpol
        for line_am, line_av in zip(am_d, av_d):
            line_am = line_am.coords[:]
            line_av = line_av.coords[:]

            z_tmp = np.interp(
                self.pk_int, [self.pk_am, self.pk_av], [line_am[-1][1], line_av[-1][1]]
            )
            x_tmp = np.interp(
                self.pk_int, [self.pk_am, self.pk_av], [line_am[-1][0], line_av[-1][0]]
            )
            if x_tmp < x_d and z_tmp < z_d:
                list_points_d.append((x_tmp, z_tmp))

        # pos treatment
        df_g = pd.DataFrame(list_points_g, columns=["x", "z"])
        df_d = pd.DataFrame(list_points_d, columns=["x", "z"])
        prof_final = (
                [(x_g, z_g)]
                + df_g.sort_values(["x"]).values.tolist()
                + [(x_f, z_f)]
                + df_d.sort_values(["x"]).values.tolist()
                + [(x_d, z_d)]
        )
        limx = [x_g, x_d]
        prof_final = LineString(prof_final)
        if prof_final.is_empty:
            prof_final = None

        return prof_final, limx

    def discret_pr_lg(self, pr, x_fond, zmin, pas=0.1, id_g=0, id_d=-1, cond_pas_z=True):
        """
         vertical descritization
        :param pr : (numpy.array) profil
         :param x_fond : bottom x value
         :param pas : dz in m or nb of plan
         :param cond_pas_z : True si descritization in m or false in plan
         :param id_g : id_am_g id point left
         :param id_d : id_am_d id point right
         :param zmin : bottom point of the profile

        """

        zmax = max(pr[id_g, 1], pr[id_d, 1])

        if id_g == id_d:
            return []
        if id_d == -1:
            limit_pr = pr[id_g:]
        else:
            limit_pr = pr[id_g: id_d + 1]

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
            pasz = (zmax - zmin) / pas

        z_level = zmin
        if pasz == 0:
            return lst_line_disc

        while z_level + pasz <= zmax and pasz != 0.:
            # line creation for cut
            z_level = z_level + pasz
            line = [(pr[id_g, 0] - 1, z_level), (pr[id_d, 0] + 1, z_level)]
            point_fond = Point([x_fond, z_level])
            line = LineString(line)
            geom = line.intersection(poly)
            if geom.is_empty:
                self.msg += "Pas d intersection : {}  {} \n".format(line, poly)
                # print('Pas d intersection :', line, poly)
            elif geom.geom_type == "MultiLineString" or geom.geom_type == "GeometryCollection":
                if id_d == -1:
                    id_tmp = 0
                else:
                    id_tmp = -1

                l_g = 0
                l_d = 0
                for j, ll in enumerate(geom.geoms):
                    length = ll.length
                    x, y = ll.xy
                    if j != id_tmp and max(x) < x_fond:
                        l_g += length
                    elif j != id_tmp and min(x) > x_fond:
                        l_d += length
                x, y = geom.geoms[id_tmp].xy
                linf = [(x[0] - l_g, z_level), (x[-1] + l_d, z_level)]
                lst_line_disc.append(LineString(linf))
            elif geom.geom_type == "LineString":
                lst_line_disc.append(geom)
            else:
                # print('Geometry type no treatment :', geom.geom_type)
                self.msg += "Geometry type no treatment : {} \n".format(geom.geom_type)
        return lst_line_disc

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
            # print('No profil for the minor bed')
            self.msg += "No profil for the minor bed \n"
            self.err = False
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

    def __call__(self):
        """
        run interpolation
        :return:
        """

        pr_am_m, pr_am_g, pr_am_d, pr_am_st_g, pr_am_st_d = self.decoup_pr(
            self.data["up"]["prof"], self.data["up"]["minor"], self.data["up"]["major"]
        )

        pr_av_m, pr_av_g, pr_av_d, pr_av_st_g, pr_av_st_d = self.decoup_pr(
            self.data["down"]["prof"], self.data["down"]["minor"], self.data["down"]["major"]
        )

        np_pr_am = np.array(pr_am_m)
        np_pr_av = np.array(pr_av_m)
        zmin_am = min(np_pr_am[:, 1])
        zmin_av = min(np_pr_av[:, 1])
        zmax_am = max(np_pr_am[:, 1])
        zmax_av = max(np_pr_av[:, 1])
        if zmax_am == zmin_am:
            # print('Upstream profile is plate')
            self.msg += "Upstream profile is flat\n"
            self.msg += "   x1,z1 : ({},{}) , " "xn, zn : ({},{})\n".format(
                np_pr_am[0, 0], np_pr_am[0, 1], np_pr_am[-1, 0], np_pr_am[-1, 1]
            )
            self.err = False
            return
        if zmax_av == zmin_av:
            # print('Downstream profile is plate')
            self.msg += "Downstream profile is flat\n"
            self.msg += "   x1,z1 : ({},{}) , " "xn, zn : ({},{})\n".format(
                np_pr_av[0, 0], np_pr_av[0, 1], np_pr_av[-1, 0], np_pr_av[-1, 1]
            )
            self.err = False
            return

        lst_pr = [
            (0, pr_am_m, pr_av_m),
            (1, pr_am_g, pr_av_g),
            (2, pr_am_d, pr_av_d),
            (3, pr_am_st_g, pr_av_st_g),
            (4, pr_am_st_d, pr_av_st_d),
        ]
        self.data["interp"]["prof"] = []
        self.data["interp"]["minor"] = [None, None]
        self.data["interp"]["major"] = [None, None]
        g_lim = None
        d_lim = None
        for id, pr_am_tmp, pr_av_tmp in lst_pr:
            # print('*************** type : {}'.format(id))
            self.calc_profil(pr_am_tmp, pr_av_tmp, id)
            if "limitx" in self.prf_loc[id].keys():
                if id == 0:
                    self.data["interp"]["minor"] = self.prf_loc[id]["limitx"]
                if id == 3:
                    g_lim = self.prf_loc[id]["limitx"][0]
                if id == 4:
                    d_lim = self.prf_loc[id]["limitx"][1]

        if g_lim and d_lim:
            self.data["interp"]["major"] = [g_lim, d_lim]

        prof_final = self.merge_prof("prof")

        # prof_final = LineString(prof_final)
        # export csv:
        # df = pd.DataFrame(np.array(prof_final))
        # df.to_csv('test', sep=';')

        self.data["interp"]["prof"] = list(prof_final.coords)
        return


if __name__ == "__main__":
    pass
