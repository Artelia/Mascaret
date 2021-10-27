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

from pandas.core.frame import DataFrame
from shapely.geometry import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.signal import find_peaks
import pandas as pd
import time


class ClassProfInterp():
    """

    """
    def __init__(self, pk_int, pk_am, pk_av):
        self.dict_prf_loc = {}
        self.dict_prf = {'pr': [],
                         'pr_am': [],
                         'pr_av': [],
                         'pr_am2': [],
                         'pr_av2': []}
        self.pk_int = pk_int
        self.pk_am = pk_am
        self.pk_av = pk_av

        self.typ_disc = 'plan'
        self.dz = None
        self.nplan = 100

    def merge_prof(self, key='pr', id=-1):
        """
        key : 'pr' interpolate profil, 'pr_am' profil amont, 'pr_av' profil aval
        id= numero profile (minor, major ,...) ,-1 global
        """
        dico = {}
        if id == -1:
            dico = self.dict_prf
        else:
            dico = self.dict_prf_loc[id]
        tmp = []
        for pr in dico[key]:
            if pr != None:
                tmp.append(pr.coords[0][0])
            else:
                tmp.append(None)
        df = pd.DataFrame(tmp, columns=['x'])
        order = df.sort_values(["x"]).index.values
        outprof = []
        for i in order:
            line = dico[key][i]
            if line != None:
                points = line.coords[:]
                outprof += points

        if outprof != []:
            prof_final = LineString(outprof)
        else:
            prof_final = None

        return prof_final

    def merge_prof_ss_discr(self, key='pr_am', id=-1):
        """
        permet de merger les profil non discretise
        key : 'pr_am' profil amont, 'pr_av' profil aval
        id= numero profile (minor, major ,...) ,-1 global
        """
        dico = None
        if id == -1:
            dico = self.dict_prf
        else:
            dico = self.dict_prf_loc[id]
        tmp = []
        for pr in dico[key]:
            if pr != None:
                tmp += pr
        df = pd.DataFrame(tmp, columns=['x', 'z'])

        outprof = df.sort_values(["x"]).values.tolist()

        if outprof != []:
            prof_final = LineString(outprof)
        else:
            prof_final = None

        return prof_final

    def calc_profil(self, pr_am_tmp, pr_av_tmp, id_pr):
        """
        Caclul le profil interpolé
        """
        if len(pr_am_tmp) <= 2 and len(pr_av_tmp) <= 2:
            print("{} profile doesn't existe".format(id_pr))
            if id_pr == 0:
                print("Minor bed doesn't existe")
                return 'break'
            else:
                if not id_pr in self.dict_prf_loc.keys():
                    self.dict_prf_loc[id_pr] = {'pr': [],
                                                'pr_am': [],
                                                'pr_av': [],
                                                'pr_am2': [],
                                                'pr_av2': []}
                self.dict_prf_loc[id_pr]['pr'].append(None)
                self.dict_prf_loc[id_pr]['pr_am'].append(None)
                self.dict_prf_loc[id_pr]['pr_av'].append(None)
                self.dict_prf_loc[id_pr]['pr_am2'].append(None)
                self.dict_prf_loc[id_pr]['pr_av2'].append(None)
                return 'continue'
        # 2 est la version non discrétisé
        self.dict_prf_loc[id_pr] = {'pr': [],
                                    'pr_am': [],
                                    'pr_av': [],
                                    'pr_am2': [],
                                    'pr_av2': []}
        prof_min, pr_am_min, pr_av_min = self.interpol_fct_lg(
            self.pk_int,
            pr_am_tmp, pr_av_tmp,
            self.pk_am, self.pk_av)

        self.dict_prf_loc[id_pr]['pr'].append(prof_min)
        self.dict_prf_loc[id_pr]['pr_am'].append(pr_am_min)
        self.dict_prf_loc[id_pr]['pr_av'].append(pr_av_min)
        self.dict_prf_loc[id_pr]['pr_am2'].append(pr_am_tmp)
        self.dict_prf_loc[id_pr]['pr_av2'].append(pr_av_tmp)

        self.dict_prf['pr'] += self.dict_prf_loc[id_pr]['pr']
        self.dict_prf['pr_am'] += self.dict_prf_loc[id_pr]['pr_am']
        self.dict_prf['pr_av'] += self.dict_prf_loc[id_pr]['pr_av']
        self.dict_prf['pr_am2'] += self.dict_prf_loc[id_pr]['pr_am2']
        self.dict_prf['pr_av2'] += self.dict_prf_loc[id_pr]['pr_av2']
        return 'ok'

    def interpol_fct_lg(self, pk_int, pr_am, pr_av, pk_am, pk_av):
        """
        interpolaiton d'un profil

        """
        pr_am = np.array(pr_am)
        pr_av = np.array(pr_av)

        list_points = []
        # calcul point fond
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

        z_f = np.interp(pk_int,
                        [pk_am, pk_av],
                        [z_am_fond, z_av_fond])
        x_f = np.interp(pk_int,
                        [pk_am, pk_av],
                        [x_am_fond, x_av_fond])
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

        z_g = np.interp(pk_int,
                        [pk_am, pk_av],
                        [z0_am, z0_av])
        x_g = np.interp(pk_int,
                        [pk_am, pk_av],
                        [x0_am, x0_av])
        list_points.append((x_g, z_g))

        z_d = np.interp(pk_int,
                        [pk_am, pk_av],
                        [z1_am, z1_av])
        x_d = np.interp(pk_int,
                        [pk_am, pk_av],
                        [x1_am, x1_av])
        list_points.append((x_d, z_d))

        # point caractéristique calculé

        # generation line 10 cm
        if self.typ_disc == 'plan':
            pas = self.nplan
            cond_pas_z = False
        elif self.typ_disc == 'dz':
            self.pas = self.dz
            cond_pas_z = True
        else:
            print('Type de discrétisation non existante')
            return

        am_g = self.discret_pr_lg(pr_am,
                                  x_am_fond, zmin_am,
                                  pas=pas,
                                  id_g=0, id_d=id_am_f[0],
                                  cond_pas_z=cond_pas_z)
        am_d = self.discret_pr_lg(pr_am,
                                  x_am_fond, zmin_am,
                                  pas=pas,
                                  id_g=id_am_f[0], id_d=-1,
                                  cond_pas_z=cond_pas_z)

        av_g = self.discret_pr_lg(pr_av,
                                  x_av_fond, zmin_av,
                                  pas=pas,
                                  id_g=0, id_d=id_av_f[0],
                                  cond_pas_z=cond_pas_z)
        av_d = self.discret_pr_lg(pr_av,
                                  x_av_fond, zmin_av,
                                  pas=pas,
                                  id_g=id_av_f[0], id_d=-1,
                                  cond_pas_z=cond_pas_z)

        list_points_g = []
        list_points_d = []
        if len(am_g) == 0 and len(am_d) == 0 \
                and len(av_g) == 0 and len(av_d) == 0:
            return None, None, None
        # dans le cas où il n'y a pas de profil amont ou aval sur la portion du lit
        # l'interpolation se fait par rapport au point
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

        # interpol gauch
        for line_am, line_av in zip(am_g, av_g):
            line_am = line_am.coords[:]
            line_av = line_av.coords[:]

            z_tmp = np.interp(pk_int,
                              [pk_am, pk_av],
                              [line_am[0][1], line_av[0][1]])
            x_tmp = np.interp(pk_int,
                              [pk_am, pk_av],
                              [line_am[0][0], line_av[0][0]])
            if x_tmp > x_g and z_tmp < z_g:
                list_points_g.append((x_tmp, z_tmp))

        # interpol droit
        for line_am, line_av in zip(am_d, av_d):
            line_am = line_am.coords[:]
            line_av = line_av.coords[:]

            z_tmp = np.interp(pk_int,
                              [pk_am, pk_av],
                              [line_am[-1][1], line_av[-1][1]])
            x_tmp = np.interp(pk_int,
                              [pk_am, pk_av],
                              [line_am[-1][0], line_av[-1][0]])
            if x_tmp < x_d and z_tmp < z_d:
                list_points_d.append((x_tmp, z_tmp))

        # pos traitement
        df_g = pd.DataFrame(list_points_g, columns=['x', 'z'])
        df_d = pd.DataFrame(list_points_d, columns=['x', 'z'])
        prof_final = [(x_g, z_g)] + \
                     df_g.sort_values(["x"]).values.tolist() + \
                     [(x_f, z_f)] + \
                     df_d.sort_values(["x"]).values.tolist() + \
                     [(x_d, z_d)]
        prof_final = LineString(prof_final)
        if prof_final.is_empty:
            prof_final = None

        lp_g = [line.coords[:][0] for line in am_g]
        lp_d = [line.coords[:][1] for line in am_d]
        df_g = pd.DataFrame(lp_g, columns=['x', 'z'])
        df_d = pd.DataFrame(lp_d, columns=['x', 'z'])
        pr_am_disc = [(x0_am, z0_am)] + \
                     df_g.sort_values(["x"]).values.tolist() + \
                     [(x_am_fond, z_am_fond)] + \
                     df_d.sort_values(["x"]).values.tolist() + \
                     [(x1_am, z1_am)]
        # si line est 1 point
        if pr_am_disc[0] == pr_am_disc[-1]:
            pr_am_disc = None
        pr_am_disc = LineString(pr_am_disc)

        lp_g = [line.coords[:][0] for line in av_g]
        lp_d = [line.coords[:][1] for line in av_d]
        df_g = pd.DataFrame(lp_g, columns=['x', 'z'])
        df_d = pd.DataFrame(lp_d, columns=['x', 'z'])
        pr_av_disc = [(x0_av, z0_av)] + \
                     df_g.sort_values(["x"]).values.tolist() + \
                     [(x_av_fond, z_av_fond)] + \
                     df_d.sort_values(["x"]).values.tolist() + \
                     [(x1_av, z1_av)]
        # si line est 1 point
        if pr_av_disc[0] == pr_av_disc[-1]:
            pr_av_disc = None
        pr_av_disc = LineString(pr_av_disc)

        if pr_am_disc.is_empty:
            pr_am_disc = None
        if pr_av_disc.is_empty:
            pr_av_disc = None

            # fig = plt.figure(figsize=(6,8))
        # ax = fig.add_subplot(111)
        # print(pr_am_disc,pr_av_disc)
        # plot_coords(ax,prof_final)
        # plot_coords(ax,pr_am_disc,color='green', label = 'amont')
        # plot_coords(ax,pr_av_disc,color='red', label = 'aval')

        # plt.title("")
        # plt.show()
        # tol=0.001
        # prof_final = prof_final.simplify(tol,preserve_topology=True)
        # pr_am_disc = pr_am_disc.simplify(tol,preserve_topology=True)
        # pr_av_disc = pr_av_disc.simplify(tol,preserve_topology=True)

        return prof_final, pr_am_disc, pr_av_disc

    def find_line_fond(self, geom, point_fond):
        """
        Trouve quelle ligne est axé avec le point du fond
        geom : MultiLineString
        point_fond : Point
        """
        for i, ll in enumerate(geom):
            if point_fond.within(ll):
                return i
        return None

    def discret_pr_lg(self, pr, x_fond, zmin, pas=0.1, id_g=0, id_d=-1,
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

        zmax = max(pr[id_g, 1], pr[id_d, 1])

        print(id_g, id_d)
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

        # fig = plt.figure(figsize=(6,8))
        # ax = fig.add_subplot(111)
        # decoupe chque line
        lst_line_disc = []

        if not poly.is_valid:
            # fig2 = plt.figure(figsize=(6,8))
            # ax2 = fig2.add_subplot(111)
            # plt.title('no valid poly')
            # plot_coords(ax2 , line_pr)
            # plt.show()
            return lst_line_disc

        # fig2 = plt.figure(figsize=(6,8))
        # ax2 = fig2.add_subplot(111)
        # plot_p(ax2 , poly)
        # plt.show()
        if cond_pas_z:
            # si descritisation en cm
            pasz = pas
        else:
            pasz = (zmax - zmin) / (pas)

        z_level = zmin

        while z_level + pasz <= zmax:
            # création de line pour découpé
            z_level = z_level + pasz
            line = [(pr[id_g, 0] - 1, z_level),
                    (pr[id_d, 0] + 1, z_level)]
            point_fond = Point([x_fond, z_level])
            line = LineString(line)
            # fig = plt.figure(figsize=(6,8))
            # ax = fig.add_subplot(111)
            # plot_p(ax,poly)
            # plot_coords(ax,line)
            # plt.title("")
            # plt.show()
            geom = line.intersection(poly)
            if geom.is_empty:
                print('Pas d intersection :', line, poly)
            elif geom.geom_type == 'MultiLineString' \
                    or geom.geom_type == 'GeometryCollection':
                # if geom.is_empty
                # id_tmp = self.find_line_fond(geom,point_fond)
                # car travail seulement moitié
                if id_d == -1:
                    id_tmp = 0
                else:
                    id_tmp = -1

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
                lst_line_disc.append(LineString(linf))
                # plot_coords(ax , LineString(linf))
            elif geom.geom_type == 'LineString':
                lst_line_disc.append(geom)
                # plot_coords(ax , geom)
            else:
                print('Geo type non traite :', geom.geom_type)
        # plot_p(ax , poly)
        # plt.show()
        return lst_line_disc

    def calcul_stat(self, discret=True):
        # -1: total
        #  0: minor
        #  1: left major
        #  2: right major
        #  3: left stock zone
        #  4: right stock zone
        dico_o = {}
        dico_o['total'] = {b: {a: [] for a in ['S', 'P']} for b in
                           ['Amont', 'Aval', 'Interp']}
        dico_o['zone'] = {b: {a: [] for a in ['S', 'P']} for b in
                          ['Amont', 'Aval', 'Interp']}

        # print (self.dict_prf_loc)
        for i in range(-1, 5):
            if i == -1:
                dico = dico_o['total']
            else:
                dico = dico_o['zone']

            if discret:
                pr = self.merge_prof('pr', i)
                pr_am = self.merge_prof('pr_am', i)
                pr_av = self.merge_prof('pr_av', i)
            else:
                pr = self.merge_prof('pr', i)
                pr_am = self.merge_prof_ss_discr('pr_am2', i)
                pr_av = self.merge_prof_ss_discr('pr_av2', i)

            if pr == None and pr_am == None and pr_av == None:
                dico['Interp']['S'].append(0)
                dico['Interp']['P'].append(0)
                dico['Amont']['S'].append(0)
                dico['Amont']['P'].append(0)
                dico['Aval']['S'].append(0)
                dico['Aval']['P'].append(0)
                continue

            zmax_pr, zmax_am, zmax_av = -9999, -9999, -9999
            if pr != None:
                zmax_pr = max([p[1] for p in pr.coords[:]])
            if pr_am != None:
                zmax_am = max([p[1] for p in pr_am.coords[:]])
            if pr_av != None:
                zmax_av = max([p[1] for p in pr_av.coords[:]])

            zmax = max(zmax_pr, zmax_am, zmax_av)
            # if i ==1 :
            #     fig = plt.figure(figsize=(6,8))
            #     ax = fig.add_subplot(111)
            if pr == None:
                dico['Interp']['S'].append(0)
                dico['Interp']['P'].append(0)
            else:
                pr_tmp = pr.coords[:]
                pr = [(pr_tmp[0][0], zmax)] + pr_tmp + [
                    (pr_tmp[-1][0], zmax)]
                poly = Polygon(pr)
                dico['Interp']['S'].append(poly.area)

                dico['Interp']['P'].append(poly.length)
                # if i ==1 :
                #     plot_p(ax,poly,'red','interp')

            if pr_am == None:
                dico['Amont']['S'].append(0)
                dico['Amont']['P'].append(0)
            else:
                pr_tmp = pr_am.coords[:]
                pr_am = [(pr_tmp[0][0], zmax)] + pr_tmp + [
                    (pr_tmp[-1][0], zmax)]
                poly_am = Polygon(pr_am)
                # if i ==1 :
                #     plot_p(ax,poly_am,'blue','amont')
                dico['Amont']['S'].append(poly_am.area)
                dico['Amont']['P'].append(poly_am.length)

            if pr_av == None:
                dico['Aval']['S'].append(0)
                dico['Aval']['P'].append(0)
            else:
                pr_tmp = pr_av.coords[:]
                pr_av = [(pr_tmp[0][0], zmax)] + pr_tmp + [
                    (pr_tmp[-1][0], zmax)]
                poly_av = Polygon(pr_av)
                # if i == 1 :
                #     plot_p(ax,poly_av,'green','aval')

                dico['Aval']['S'].append(poly_av.area)
                dico['Aval']['P'].append(poly_av.length)
                # if i == 1 :
                #     ax.legend(loc = 'upper left')
                #     plt.show()

        # Valeur Theorique et son erreur
        ls = []
        lp = []
        les = []
        lep = []
        cpt = 0
        for surf_am, surf_av, surf, p_am, p_av, p in zip(
                dico_o['zone']['Amont']['S'],
                dico_o['zone']['Aval']['S'],
                dico_o['zone']['Interp']['S'],
                dico_o['zone']['Amont']['P'],
                dico_o['zone']['Aval']['P'],
                dico_o['zone']['Interp']['P'],
                ):
            snew = np.interp(pk_int,
                             [pk_am, pk_av],
                             [surf_am, surf_av])
            pnew = np.interp(pk_int,
                             [pk_am, pk_av],
                             [p_am, p_av])
            if snew != 0:
                es = abs(snew - surf) / snew
            else:
                es = -1
            if pnew != 0:
                ep = abs(pnew - p) / pnew
            else:
                ep = -1
            ls.append(snew)
            lp.append(pnew)
            les.append(es)
            lep.append(ep)
            cpt += 1

        dico_o['zone']['Search'] = {'S': ls, 'P': lp}
        dico_o['zone']['Erreur en fonction Search'] = {'S': les,
                                                       'P': lep}

        return dico_o

    def print_stat(self, dico_stat):
        print("___________________________________")
        print("Calcul pour le profil Total")
        print("___________________________________")
        for typ in dico_stat['total'].keys():
            print('{} :'.format(typ))
            for var in dico_stat['total'][typ].keys():
                print('\t {} : {}'.format(var,
                                          dico_stat['total'][typ][var][
                                              0]))

        print("___________________________________")
        print("Calcul pour le profil par zone")
        print("___________________________________")
        names = ['lit mineur', 'lit majeur gauch', 'lit majeur droit',
                 'zone de stockage gauche', 'zone de stockage droit']
        for typ in dico_stat['zone'].keys():
            print('{} :'.format(typ))
            txt_l = ''
            for var in dico_stat['zone'][typ].keys():
                txt_h = ''
                if var == "S":
                    txt_l += '  {}'.format('Surface')
                if var == "P":
                    txt_l += '  {}'.format('Permiter')
                for i, name in enumerate(names):
                    txt_h += '\t {:>10},'.format(name)
                    txt_l += '\t {:>10},'.format(
                        round(dico_stat['zone'][typ][var][i], 2))
                txt_l += '\n'
            print(txt_h)
            print(txt_l)

def decoup_pr(pr, lminor_x, lmaj_x):
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

def trace_graph(prof_final, pr_am, pr_av, pr_am2, pr_av2, pk_int, pk_am,
                pk_av, cas):

    fig = plt.figure(figsize=(6, 8))
    fig.suptitle(cas, fontsize=16)
    fig.subplots_adjust(hspace=0.4, wspace=0.4)
    linestyle = '-'
    ax = plt.subplot2grid((5, 1), (0, 0), rowspan=2, fig=fig,
                          projection='3d')
    plt_line1 = plot_coords3D(ax, prof_final, pk_int,
                              color='red',
                              label='profil interpol, pk = {:.2f}'.format(
                                  pk_int),
                              style=linestyle)
    plt_line2 = plot_coords3D(ax, pr_am2, pk_am,
                              color='blue',
                              label='profil amont, pk = {:.2f}'.format(
                                  pk_am),
                              style=linestyle)
    plt_line3 = plot_coords3D(ax, pr_av2, pk_av,
                              color='green',
                              label='profil aval, pk = {:.2f}'.format(
                                  pk_av),
                              style=linestyle)
    ax.legend(loc='upper left', bbox_to_anchor=(0.65, 1.25))

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    # ax.set_title(cas)
    # ax_interp = plt.subplot2grid((5, 1), (2, 0), fig=fig)


    # z_min_am = pr_am.bounds[1]
    # z_min_av = pr_av.bounds[1]
    # plt_line_interp, = ax_interp.plot(np.linspace(pk_am,pk_av,10),
    #                     np.linspace(z_min_am,z_min_av,10),
    #                     '+-k')
    # cursor = SnappingCursor(ax_interp,plt_line_interp)
    # fig.canvas.mpl_connect('motion_notify_event', cursor.on_mouse_move)
    ax2d = plt.subplot2grid((5, 1), (2, 0), rowspan=2, fig=fig)
    plt_line1 = plot_coords(ax2d, prof_final,
                            color='red',
                            label='profil interpol, pk = {}'.format(
                                pk_int),
                            style=linestyle)
    plt_line2 = plot_coords(ax2d, pr_am2,
                            color='blue',
                            label='profil amont, pk = {}'.format(pk_am),
                            style=linestyle)
    plt_line3 = plot_coords(ax2d, pr_av2,
                            color='green',
                            label='profil aval, pk = {}'.format(pk_av),
                            style=linestyle)
    # plt_line4 = plot_coords(ax2d ,pr_av2,
    #              color ='green', label = 'profil aval ori, pk = {}'.format(pk_int),
    #              style = 'dashed')
    # plt_line5 = plot_coords(ax2d , pr_am2,
    #                         color='blue', label = 'profil amont ori, pk = {}'.format(pk_am),
    #                          style = 'dashed')


    # fig.set_title(cas)

    plt.show()

def fct_test(pk_int, pk_am, pk_av,
             pr_am, lminor_x_am, lmaj_x_am,
             pr_av, lminor_x_av, lmaj_x_av):

    pr_am_m, pr_am_g, pr_am_d, pr_am_st_g, pr_am_st_d = decoup_pr(pr_am,
                                                                  lminor_x_am,
                                                                  lmaj_x_am)
    pr_av_m, pr_av_g, pr_av_d, pr_av_st_g, pr_av_st_d = decoup_pr(pr_av,
                                                                  lminor_x_av,
                                                                  lmaj_x_av)

    lst_pr = [(0, pr_am_m, pr_av_m),
              (1, pr_am_g, pr_av_g),
              (2, pr_am_d, pr_av_d),
              (3, pr_am_st_g, pr_av_st_g),
              (4, pr_am_st_d, pr_av_st_d)]

    cl = ClassProfInterp(pk_int, pk_am, pk_av)
    for id, pr_am_tmp, pr_av_tmp in lst_pr:
        print('*************** type : {}'.format(id))
        cl.calc_profil(pr_am_tmp, pr_av_tmp, id)
    prof_final = cl.dict_prf_loc[0]['pr'][0]

    prof_final = cl.merge_prof('pr')
    prof_am_disc = cl.merge_prof('pr_am')
    prof_av_disc = cl.merge_prof('pr_av')

    dico_stat = cl.calcul_stat(discret=False)
    cl.print_stat(dico_stat)
    df = pd.DataFrame(np.array(prof_final))
    df.to_csv('test', sep=';')
    tol = 0.1
    prof_final = LineString(prof_final)

    # prof_final = prof_final.simplify(tol,preserve_topology=True)

    pr_am_tmp = LineString(prof_am_disc)
    # pr_am_tmp = pr_am_tmp.simplify(tol,preserve_topology=True)
    pr_av_tmp = LineString(prof_av_disc)
    pr_am_tmp2 = LineString(pr_am)
    pr_av_tmp2 = LineString(pr_av)
    # pr_av_tmp =  pr_av_tmp.simplify(tol,preserve_topology=True)


    return pr_am_tmp, pr_av_tmp, prof_final, pr_am_tmp2, pr_av_tmp2


def plot_p(ax, poly, color='black', label='line',
           style='solid', marker=''):
    x, y = poly.exterior.xy
    ax.plot(x, y, color=color, linestyle=style, marker=marker)


def plot_coords3D(ax, ob, pk, color='grey', label='line',
                  style='solid', marker=''):
    x, z = ob.xy
    y = [pk for i in range(len(x))]
    ax.plot(x, y, z, 'o-', color=color, zorder=1,
            label=label, linestyle=style, marker=marker)


def plot_coords(ax, ob, color='grey', label='line',
                style='solid', marker=''):
    x, y = ob.xy
    ax.plot(x, y, 'o-', color=color,
            linestyle=style, marker=marker,
            zorder=1, label=label)



if __name__ == '__main__':

    # test = 'simple2' #'test_2' #'test_pr_pic_decalX_maj'
    # pk_int = 9.5
    # test = 'reel'
    # pk_int = (31546.45- 29277.29)/2 + 29277.29
    test = 'test_graph1'
    pk_int = 5
    if 'test_pr_pic_decalX_maj' == test:

        pr_am = [(4, 25), (5, 15), (7, 10), (12, 15),
                 (14, 20), (15, 15), (16, 10.), (17, 7.5), (19, 10),
                 (20.5, 5), (22, 10.), (23, 15), (24, 20)]
        pk_am = 0
        lminor_x_am = [4, 24]
        lmaj_x_am = [4, 24]

        pr_av = [(0, 25), (1, 15), (3, 10), (8, 15),
                 (10, 10), (11, 5), (12, 0.), (13.5, -5), (15, 0),
                 (18, 0.), (19, 5), (20, 10)]
        pk_av = 10
        lminor_x_av = [0, 20]
        lmaj_x_av = [0, 20]

    elif 'test_2' == test:
        # seul lit minor OK
        pr_am = [  # (4, 25),(5, 15),(7, 10),(12, 15),
            (14, 20), (15, 15), (16, 10.), (17, 7.5), (19, 10),
            (20.5, 5), (22, 10.), (23, 15), (24, 20)]
        pk_am = 0
        lminor_x_am = [16, 22]
        lmaj_x_am = [14, 24]

        pr_av = [
            (10, 10), (11, 5), (12, 0.), (13.5, -5), (15, 0), (18, 0.),
            (19, 5), (20, 10)]
        pk_av = 10
        lminor_x_av = [11, 18]
        lmaj_x_av = [10, 20]


    elif 'simple' == test:

        pr_am = [(-10, 10), (-7.5, 5), (-5, 0), (-2.5, 5), (0, 10)]
        pk_am = 0
        lminor_x_am = [-10, 0]
        lmaj_x_am = [-10, 0]

        pr_av = [(0, 10), (2.5, 5), (5, 0), (7.5, 5), (10, 10)]
        pk_av = 10
        lminor_x_av = [0, 10]
        lmaj_x_av = [0, 10]
    elif 'simple2' == test:

        pr_am = [(-15, 10), (-12.5, 5),
                 (-10, 10), (-7.5, 5), (-5, 0), (-2.5, 5), (0, 10),
                 (5, 10)]
        pk_am = 0
        lminor_x_am = [-10, 5]
        lmaj_x_am = [-15, 5]

        pr_av = [(-5, 10), (-2.5, 5),
                 (0, 10), (2.5, 5), (5, 0), (7.5, 5), (10, 10),
                 (12.5, 2), (15, 10)]
        pk_av = 10
        lminor_x_av = [-5, 10]
        lmaj_x_av = [-5, 15]


    elif 'simple2bis' == test:

        pr_am = [(-15, 10), (-12.5, 5),
                 (-10, 10), (-7.5, 5), (-5, 0), (-2.5, 5), (0, 10),
                 (2.5, 2), (5, 10)]
        pk_am = 0
        lminor_x_am = [-10, 5]
        lmaj_x_am = [-15, 5]

        pr_av = [(-5, 10), (-2.5, 5),
                 (0, 10), (2.5, 5), (5, 0), (7.5, 5), (10, 10),
                 (12.5, 2), (15, 10)]
        pk_av = 10
        lminor_x_av = [-5, 10]
        lmaj_x_av = [-5, 15]

    elif 'reel' == test:
        file_am = 'amont_29277.29.csv'
        with open(file_am) as file:
            lp = []
            cpt = 0
            for line in file:
                if cpt != 0:
                    lst = line.replace('\n', '').split(';')
                    lp.append((float(lst[0]), float(lst[1])))
                cpt += 1

        pr_am = lp.copy()

        pk_am = 29277.29
        lminor_x_am = [649., 915.]
        lmaj_x_am = [pr_am[0][0],
                     pr_am[-1][0]]  # pas de zone de stockage

        file_av = 'aval_31546.45.csv'
        with open(file_av) as file:
            lp = []
            cpt = 0
            for line in file:
                if cpt != 0:
                    lst = line.replace('\n', '').split(';')
                    lp.append((float(lst[0]), float(lst[1])))
                cpt += 1
        pr_av = lp.copy()
        pk_av = 31546.45
        lminor_x_av = [324., 536.]
        lmaj_x_av = [pr_av[0][0],
                     pr_av[-1][0]]  # pas de zone de stockage
    elif 'test_graph1' == test:
        # pk_int = 2.5
        # même nb de plan
        pr_am = [(0, 10), (1, 5), (5, 0.), (6, 5.), (8, 3.), (9, 5),
                 (10, 10)]
        pr_am = [(-10, 11), (-5, 5), (-2.5, 7)] + pr_am + [(14, 7),
                                                           (16, 5),
                                                           (20, 11)]
        pr_am = [(-20, 11), (-18, 7), (-15, 8)] + pr_am + [(24, 9),
                                                           (26, 8),
                                                           (28, 10),
                                                           (30, 11)]
        pk_am = 0
        lminor_x_am = [0, 10]
        lminor_z_am = [10, 10]
        lminor_fond_am = [(5, 0.)]
        lmaj_x_am = [-10, 20]
        lmaj_z_am = [11, 11]
        lmaj_fond_am = [(-5, 5), (16, 5)]
        lzone_x_am = [-20, 30]
        lzone_z_am = [11, 11]
        lzone_fond_am = [(-18, 7), (26, 8)]

        pr_av = [(0, 10), (1, 5), (5, 0.), (6, 5.), (8, 3.), (9, 5),
                 (10, 10)]
        pr_av = [(-10, 11), (-5, 5), (-2.5, 7)] + pr_av + [(14, 7),
                                                           (16, 5),
                                                           (20, 11)]
        pr_av = [(-20, 11), (-18, 7), (-15, 8)] + pr_av + [(24, 9),
                                                           (26, 8),
                                                           (28, 10),
                                                           (30, 11)]
        pk_av = 10

        lminor_x_av = [0, 10]
        lminor_z_av = [10, 10]
        lminor_fond_av = [(5, 0.)]
        lmaj_x_av = [-10, 20]
        lmaj_z_av = [11, 11]
        lmaj_fond_av = [(-5, 5), (16, 5)]
        lzone_x_av = [-20, 30]
        lzone_z_av = [11, 11]
        lzone_fond_av = [(-18, 7), (26, 8)]

        # ******************************************************************************
    start_time = time.time()
    pr_am_tmp, pr_av_tmp, prof_final, pr_am, pr_av = fct_test(pk_int,
                                                              pk_am,
                                                              pk_av,
                                                              pr_am,
                                                              lminor_x_am,
                                                              lmaj_x_am,
                                                              pr_av,
                                                              lminor_x_av,
                                                              lmaj_x_av)
    # trace_graph(prof_final,pr_am_tmp, pr_av_tmp,pr_am, pr_av,
    #         pk_int,pk_am,pk_av, "cas")
    print("--- %s seconds ---" % (time.time() - start_time))

    # fig = plt.figure(figsize=(6,8))
    # fig.suptitle('test', fontsize=16)
    # fig.subplots_adjust(hspace=0.4, wspace=0.4)
    # linestyle = '-'
    # ax = plt.subplot2grid((1, 1), (0, 0), rowspan=1,fig=fig)
    # plt_line2 = plot_coords(ax , pr_am,
    #                     color='blue', label = 'profil amont, pk = {}'.format(pk_am),
    #                     style=linestyle)
    # ax.legend(loc = 'upper left',bbox_to_anchor=(0.65, 1.25))

    # fig = plt.figure(figsize=(6,8))
    # fig.suptitle("test", fontsize=16)
    # fig.subplots_adjust(hspace=0.4, wspace=0.4)

    # ax = plt.subplot2grid((2, 1), (0, 0), rowspan=2,fig=fig, projection='3d')
    # plt_line1 = plot_coords3D(ax , prof_final, pk_int,
    #                         color ='red', label = 'profil interpol, pk = {:.2f}'.format(pk_int),
    #                         style= '-')
    # plt_line2 = plot_coords3D(ax , pr_am, pk_am,
    #                         color='blue', label = 'profil amont, pk = {:.2f}'.format(pk_am),
    #                         style= '-')
    # plt_line3 = plot_coords3D(ax , pr_av,  pk_av,
    #                         color='green', label = 'profil aval, pk = {:.2f}'.format(pk_av),
    #                         style= '-')
    # x=[lminor_x_am[0],lminor_x_av[0]]
    # y=[pk_am,pk_av]
    # z=[lminor_z_am[0],lminor_z_av[0]]
    # plt_line4 =  ax.plot(x,y, z,  color='black', zorder=1,
    #     label = 'Interpolate point', linestyle='dashed', marker='')
    # x=[lminor_x_am[1],lminor_x_av[1]]
    # y=[pk_am,pk_av]
    # z=[lminor_z_am[1],lminor_z_av[1]]
    # plt_line5 =  ax.plot(x,y, z,  color='black', zorder=1,
    #     label = 'Interpolate point', linestyle='dashed', marker='')
    # x=[lmaj_x_am[0],lmaj_x_av[0]]
    # y=[pk_am,pk_av]
    # z=[lmaj_z_am[0],lmaj_z_av[0]]
    # plt_line6 =  ax.plot(x,y, z,  color='black', zorder=1,
    #     label = 'points caracteristiques', linestyle='dashed', marker='')
    # x=[lmaj_x_am[1],lmaj_x_av[1]]
    # y=[pk_am,pk_av]
    # z=[lmaj_z_am[1],lmaj_z_av[1]]
    # plt_line7b =  ax.plot(x,y, z,  color='black', zorder=1,
    #     label = 'points caracteristiques', linestyle='dashed', marker='')
    # x=[lzone_x_am[0],lzone_x_av[0]]
    # y=[pk_am,pk_av]
    # z=[lzone_z_am[0],lzone_z_av[0]]
    # plt_line6b =  ax.plot(x,y, z,  color='black', zorder=1,
    #     label = 'points caracteristiques', linestyle='dashed', marker='')
    # x=[lzone_x_am[1],lzone_x_av[1]]
    # y=[pk_am,pk_av]
    # z=[lzone_z_am[1],lzone_z_av[1]]
    # plt_line7 =  ax.plot(x,y, z,  color='black', zorder=1,
    #     label = 'points caracteristiques', linestyle='dashed', marker='')

    # x=[lminor_fond_am[0][0],lminor_fond_av[0][0]]
    # y=[pk_am,pk_av]
    # z=[lminor_fond_av[0][1],lminor_fond_av[0][1]]
    # plt_line9 =  ax.plot(x,y, z,  color='grey', zorder=1,
    #     label = 'Interpolate point fond', linestyle='dashed', marker='')
    # x=[lmaj_fond_am[0][0],lmaj_fond_av[0][0]]
    # y=[pk_am,pk_av]
    # z=[lmaj_fond_av[0][1],lmaj_fond_av[0][1]]
    # plt_line10 =  ax.plot(x,y, z,  color='grey', zorder=1,
    #     label = 'Interpolate point fond', linestyle='dashed', marker='')
    # x=[lmaj_fond_am[1][0],lmaj_fond_av[1][0]]
    # y=[pk_am,pk_av]
    # z=[lmaj_fond_av[1][1],lmaj_fond_av[1][1]]
    # plt_line11 =  ax.plot(x,y, z,  color='grey', zorder=1,
    #     label = 'Interpolate point fond', linestyle='dashed', marker='')

    # x=[lzone_fond_am[0][0],lzone_fond_av[0][0]]
    # y=[pk_am,pk_av]
    # z=[lzone_fond_av[0][1],lzone_fond_av[0][1]]
    # plt_line12 =  ax.plot(x,y, z,  color='grey', zorder=1,
    #     label = 'Interpolate point fond', linestyle='dashed', marker='')
    # x=[lzone_fond_am[1][0],lzone_fond_av[1][0]]
    # y=[pk_am,pk_av]
    # z=[lzone_fond_av[1][1],lzone_fond_av[1][1]]
    # plt_line13 =  ax.plot(x,y, z,  color='grey', zorder=1,
    #     label = 'points de fond', linestyle='dashed', marker='')




    # # ax.legend(handles=[plt_line1,
    # #            plt_line2,
    # #            plt_line3,
    # #            plt_line7,
    # #            plt_line13],
    # #           labels=['profil interpol, pk = {:.2f}'.format(pk_int),
    # #               'profil amont, pk = {:.2f}'.format(pk_am),
    # #               'profil aval, pk = {:.2f}'.format(pk_av),
    # #               'points caracteristiques',
    # #               'points de fond',
    # #               ])#,loc = 'upper right')#,bbox_to_anchor=(0.65, 1.25))
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # ax.set_xlabel('X Label')
    # ax.set_ylabel('Y Label')
    # ax.set_zlabel('Z Label')

    # # ax2d = plt.subplot2grid((5, 1), (2, 0), rowspan=2,fig=fig)
    # # plt_line1 = plot_coords(ax2d , prof_final,
    # #             color ='red', label = 'profil interpol, pk = {}'.format(pk_int),
    # #             style=linestyle)
    # # plt_line2 = plot_coords(ax2d , pr_am,
    # #                         color='blue', label = 'profil amont, pk = {}'.format(pk_am),
    # #                         style=linestyle)
    # # plt_line3 = plot_coords(ax2d , pr_av2,
    # #                         color='green', label = 'profil aval, pk = {}'.format(pk_av),
    # #                         style=linestyle)
    # # plt_line4 = plot_coords(ax2d ,pr_av2,
    # #              color ='green', label = 'profil aval ori, pk = {}'.format(pk_int),
    # #              style = 'dashed')
    # # plt_line5 = plot_coords(ax2d , pr_am2,
    # #                         color='blue', label = 'profil amont ori, pk = {}'.format(pk_am),
    # #                          style = 'dashed')


    # plt.show()

