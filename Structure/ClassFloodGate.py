# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : Janvier,2020
copyright            : (C) 2020 by Artelia
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
import numpy as np

from .ClassLaws import ClassLaws
from .ClassPostPreFG import ClassPostPreFG
from .ClassTableStructure import ClassTableStructure


def check_time_regul(time, dtreg, param_fg):
    if time % dtreg == 0 and time >= dtreg:
        # force regule même si mouvement pas fini
        param_fg['ZRESI'] = 0
        return True
    elif param_fg['ZRESI'] != 0:
        return True
    return False


class ClassFloodGate:
    """ Class Flood Gate """

    def __init__(self, main):
        self.clapi = main
        self.masc = main.masc
        self.clmas = main.clmas
        self.debug = main.DEBUG
        self.init_var = ClassPostPreFG(main.mgis)
        self.tbst = ClassTableStructure()
        #

        self.model_size = 0
        self.new_z = 99
        self.param_fg = {}
        # resultats du mouvement de la vanne
        self.results_fg_mv = {}

    def init_floogate(self):
        """ Get information for floodgate
        """
        self.model_size, _, _ = self.masc.get_var_size('Model.X')

        self.param_fg, link_name_id = self.init_var.get_param_fg()

        # attention init.loi ou pas
        # connaitrea la relation config et non law
        nb_loi_sing = self.masc.get_var_size("Model.Weir.Name")[0]
        for i in range(nb_loi_sing):
            # numgraph = self.masc.get("Model.Weir.GraphNum", i=id) - 1
            name = self.masc.get("Model.Weir.Name", i=i)
            if name.replace('_init', '') in list(link_name_id.keys()):
                id_config = link_name_id[name]
                # self.param_fg[id_config]['NUMGRAPH'] = numgraph
                self.param_fg[id_config]['NUMGRAPH'] = i

        self.search_sec_control()
        self.info_init_poly()
        self.init_res()

    def init_res(self):
        """ Init. the results dico"""
        self.results_fg_mv = {}
        tini = self.masc.get('Model.InitTime')
        for id_config in self.param_fg.keys():
            self.results_fg_mv[id_config] = {'TIME': [], 'ZSTR': []}
            self.results_fg_mv[id_config]['TIME'].append(tini)
            self.results_fg_mv[id_config]['ZSTR'].append(
                self.param_fg[id_config]['ZOLD'])

    def info_init_poly(self):
        """ Get information of polygones"""
        for id_config in self.param_fg.keys():
            list_poly_trav = self.init_var.select_poly_elem(id_config, 0)
            list_miny = []
            list_maxy = []
            for poly in list_poly_trav:
                (_, miny, _, maxy) = poly.bounds
                list_miny.append(miny)
                list_maxy.append(maxy)
            zmin = min(list_miny)
            zmax = max(list_maxy)
            self.param_fg[id_config]['MINZ0'] = zmin
            self.param_fg[id_config]['MAXZ0'] = zmax

            if self.param_fg[id_config]['DIRFG'] == 'D':
                self.param_fg[id_config]['ZOLD'] = zmin
            elif self.param_fg[id_config]['DIRFG'] == 'U':
                self.param_fg[id_config]['ZOLD'] = zmax

    def update_law_mas(self, id_config, list_q, list_zav, list_zam):
        """
         update information model with api
        :param id_config: index of structure
        :param list_q: list of flow rate
        :param list_zav: list of upstream Z
        :param list_zam: list of downstream Z
        :return
        """
        nbq = len(list_q)
        nbzav = len(list_zav)
        num = self.param_fg[id_config]['NUMGRAPH']
        dim1, dim2_q, dim3 = self.masc.get_var_size("Model.Weir.PtQ", num)
        self.masc.set_var_size('Model.Weir.PtQ', dim1, nbq, dim3, index=num + 1)
        self.masc.set_var_size("Model.Weir.PtZds", dim1, nbzav, dim3,
                               index=num + 1)
        self.masc.set_var_size("Model.Weir.PtZus", dim1, nbq, nbzav,
                               index=num + 1)

        cond_first = True
        for ii, qq in enumerate(list_q):
            self.masc.set("Model.Weir.PtQ", qq, i=num, j=ii, k=0)
            for jj, zav in enumerate(list_zav):
                if cond_first:
                    self.masc.set("Model.Weir.PtZds", zav, i=num, j=jj, k=0)
                self.masc.set("Model.Weir.PtZus", list_zam[ii * nbzav + jj],
                              i=num, j=ii, k=jj)
            cond_first = False

            # self.write("fin.csv",nbq, nbzav,num)

    def write(self, name, nbq, nbzav, num):
        file = open(name, 'w')
        file.write('q;zav;zam\n')
        for ii in range(nbq):
            q = self.masc.get("Model.Weir.PtQ", i=num, j=ii, k=0)
            for jj in range(nbzav):
                zav = self.masc.get("Model.Weir.PtZds", i=num, j=jj, k=0)
                zam = self.masc.get("Model.Weir.PtZus", i=num, j=ii, k=jj)
                file.write('{};{};{}\n'.format(q, zav, zam))
        file.close()

    def finalize(self, tfin):
        if len(self.results_fg_mv) > 0:
            for id_config in self.param_fg.keys():
                self.results_fg_mv[id_config]['TIME'].append(tfin)
                self.results_fg_mv[id_config]['ZSTR'].append(
                    self.param_fg[id_config]['ZOLD'])

    def fg_active(self):
        """ check if floodgate is active"""
        listid = self.fg_actif()
        if listid:
            return True
        return False

    def iter_fg(self, time, dtp):
        """
        Floodgate treatment during an iteration
        :param dtp : time step
        :param time: time

        """
        for id_config in self.param_fg.keys():
            self.regul(id_config, time, self.param_fg[id_config], dtp)

    def regul(self, id_config, time, param_fg, dtp):
        if check_time_regul(time, param_fg['DTREG'], param_fg):

            # debut regule
            new_z = self.cmpt_znew(param_fg, dtp)
            self.fill_results_fg_mv(id_config, time, new_z, param_fg['ZOLD'],
                                    dtp)
            list_final = self.update_law(id_config, param_fg, new_z, True)
            if list_final is None:
                self.clapi.add_info("Error: updating law")
            tab_final = self.sort_law(list_final)
            list_q = np.unique(tab_final[:, 0])
            list_zav = np.unique(tab_final[:, 1])
            list_zam = list(tab_final[:, 2])
            # modification in mascaret model
            self.update_law_mas(id_config, list_q, list_zav, list_zam)
            self.param_fg[id_config]['ZOLD'] = new_z
        else:
            pass

    def sort_law(self, list_final):
        """
        sort the law
        :param list_final: law data
        :return:
        """
        info = np.array(list_final)
        # trie de la colonne 0 à 2
        info = info[
            info[:, 2].argsort()]  # First sort doesn't need to be stable.
        info = info[info[:, 1].argsort(kind='mergesort')]
        info = info[info[:, 0].argsort(kind='mergesort')]
        return info

    def check_regul(self, param_fg):
        """
        :param param_fg:
        :return:  0 : rien,   1: close, 2 open
        """
        # demander confirmation
        # si Hamon < regule  or Haval > regule alors fermer
        # si Hamon > regule or Haval < regule alors ouvrir
        # si qaval > regule  alors  fermer
        # si  qaval < regule  alors ouvrir
        condam = (param_fg['LOCCONT'] == 'AM')
        condav = (param_fg['LOCCONT'] == 'AV')
        val_min = param_fg['VALREG'] - param_fg['TOLREG']
        val_max = param_fg['VALREG'] + param_fg['TOLREG']
        if param_fg['VREG'] == 'Z':
            val_check = self.masc.get('State.Z', param_fg['SECCON'])
        else:
            val_check = self.masc.get('State.Q', param_fg['SECCON'])
        # AM amon AV aval
        if (val_check < val_min and condam) or \
                (val_check > val_max and condav):
            return 1
        elif (val_check < val_min and condav) or \
                (val_check > val_max and condam):
            return 2
        return 0

    def cmpt_znew(self, param_fg, dtp):
        """
        Compute the new Z position of floodgate
        D =monte pour fermer
        U = descent pour fermer
        :param dtp : time step
        :param param_fg: floodgate parameters
        :return:
        """
        # state: 0: rien, 1: close, 2 open
        state, dzf = self.comput_dz_state(param_fg, dtp)
        if state != 0:
            # calcul Znew
            # dz_velo = param_fg['VELOFG'] * param_fg['DTREG']
            # dzf = min(param_fg['ZINCRFG'], dz_velo)
            znew = 99.
            if (param_fg["DIRFG"] == 'D' and state == 1) or \
                    (param_fg["DIRFG"] == 'U' and state == 2):
                znew = param_fg['ZOLD'] + dzf
            elif (param_fg["DIRFG"] == 'D' and state == 2) or \
                    (param_fg["DIRFG"] == 'U' and state == 1):
                znew = param_fg['ZOLD'] - dzf
            # check Znew
            if znew < param_fg['MINZ0']:
                znew = param_fg['MINZ0']
                param_fg['ZRESI'] = 0
            elif znew > param_fg['MAXZ0']:
                znew = param_fg['MAXZ0']
                param_fg['ZRESI'] = 0
            if (param_fg["DIRFG"] == 'D' and znew >= param_fg['ZMAXFG']) or \
                    (param_fg["DIRFG"] == 'U' and znew <= param_fg['ZMAXFG']):
                znew = param_fg['ZMAXFG']
                param_fg['ZRESI'] = 0
        else:
            znew = param_fg['ZOLD']
            param_fg['ZRESI'] = 0

        if param_fg['ZRESI'] != 0:
            param_fg['STATEOLD'] = state
        else:
            param_fg['STATEOLD'] = 0
        return znew

    def comput_dz_state(self, param_fg, dtp):
        """
        Compute Z step and state (open/close)
        :param param_fg: parameter of floodgate
        :param dtp: time step
        :return:
        """
        dz_velo = param_fg['VELOFG'] * dtp
        if param_fg['ZRESI'] != 0:
            state = param_fg['STATEOLD']
            new_resi = param_fg['ZRESI'] - dz_velo
            if new_resi <= 0:
                dzf = param_fg['ZRESI']
                new_resi = 0
            else:
                dzf = dz_velo

            param_fg['ZRESI'] = new_resi
        else:
            state = self.check_regul(param_fg)
            dzf = min(param_fg['ZINCRFG'], dz_velo)
            if dzf < param_fg['ZINCRFG']:
                param_fg['ZRESI'] = param_fg['ZINCRFG'] - dzf
            else:
                param_fg['ZRESI'] = 0

        return state, dzf

    def search_sec_control(self):
        nbbf = self.masc.get_var_size('Model.Connect.FirstNdNum')[0]
        # Local abscissa
        oribf = [self.masc.get('Model.Connect.FirstNdNum', i) - 1
                 for i in range(nbbf)]
        endbf = [self.masc.get('Model.Connect.LastNdNum', i)
                 for i in range(nbbf)]

        # Assign the bief number to each section (piecewise constant list)
        # ibief = [ib+0*i for ib in range(nbbf) for i in range(oribf[ib], endbf[ib])]
        # ibief => connu
        for id_config in self.param_fg.keys():
            ib = int(self.param_fg[id_config]['BIEFCONT']) - 1
            coords = []

            for i in range(oribf[ib], endbf[ib]):
                coords.append(self.masc.get('Model.X', i))
            coords = np.array(coords)
            idx = (np.abs(coords - self.param_fg[id_config]['XPCONT'])).argmin()
            if idx:
                self.param_fg[id_config]['SECCON'] = idx
            else:
                self.clapi.add_info("Regulation point not found.")
            del coords

        del oribf
        del endbf

    def fill_results_fg_mv(self, id_config, time, newz, zold, dt):
        """
        fill the results_fg_mv dico
        :param id_config: configuration id
        :param time: time
        :param newz:  new Z
        :param zold: old Z
        :param dt: step time
        :return:
        """

        if zold == newz:
            self.results_fg_mv[id_config]['TIME'].append(time)
            self.results_fg_mv[id_config]['ZSTR'].append(newz)
        else:
            if (time - dt) not in self.results_fg_mv[id_config]['TIME']:
                self.results_fg_mv[id_config]['TIME'].append(time - dt)
                self.results_fg_mv[id_config]['ZSTR'].append(zold)
            self.results_fg_mv[id_config]['TIME'].append(time)
            self.results_fg_mv[id_config]['ZSTR'].append(newz)

    def update_law(self, id_config, param_fg, new_z, mobil_struct):
        """   Compute new law
                :param id_config: index of hydraulic structure
                :param param_fg : parameters of the floodgate
                :param new_z : new position of floodgate
                :param mobil_struct :moving structure condition
                :return:
                """
        idmethod = param_fg['METH']
        law = ClassLaws(self.clapi.mgis)
        law.init_mobil_param(mobil_struct, param_fg, new_z)
        list_final = None
        if idmethod == 0 or idmethod == 4:  # meth
            pass
        elif idmethod == 1:  # borda
            list_final = law.borda(id_config,
                                   self.tbst.dico_meth_calc[idmethod], None)
        elif idmethod == 3:  # orifice
            list_final = law.orifice(id_config,
                                     self.tbst.dico_meth_calc[idmethod], None)
        else:
            pass
        del law
        return list_final

    def fg_actif(self):
        return self.init_var.fg_actif()
