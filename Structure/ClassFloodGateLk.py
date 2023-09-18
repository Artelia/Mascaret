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
from .ClassPostPreFGLk import ClassInfoParamFG_Lk


def check_time_regul(time, dtreg, param_fg):
    if time % dtreg == 0 and time >= dtreg:
        # force regule même si mouvement pas fini
        param_fg['ZRESI'] = 0
        return True
    elif param_fg['ZRESI'] != 0:
        return True
    return False


class ClassFloodGateLk:
    """ Class Flood Gate """

    def __init__(self, main):
        self.clapi = main
        self.masc = main.masc
        self.clmas = main.clmas
        self.debug = main.DEBUG
        self.model_size = 0
        self.size_link = 0
        self.new_z = 99
        self.cl_fg_l = ClassInfoParamFG_Lk()
        print(main.mgis)
        self.cl_fg_l.get_param(parent=main.mgis)
        self.actif_mobil_lk = self.cl_fg_l.fg_actif_lk()
        self.param_fg = self.cl_fg_l.param_fg
        # resultats du mouvement de la vanne
        self.results_fg_lk_mv = {}

    def init_fg_links(self):
        """ Get information for floodgate
        """
        # Get Section
        self.search_sec_control()
        self.search_link_to_param_fg()
        print( self.param_fg)

        # self.init_res()

    def init_res(self):
        """ Init. the results dico"""
        self.results_fg_lk_mv = {}
        tini = self.masc.get('Model.InitTime')
        for id_config in self.param_fg.keys():
            self.results_fg_lk_mv[id_config] = {'TIME': [], 'ZSTR': []}
            self.results_fg_lk_mv[id_config]['TIME'].append(tini)
            self.results_fg_lk_mv[id_config]['ZSTR'].append(
                self.param_fg[id_config]['ZOLD'])


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
        if len(self.results_fg_lk_mv) > 0:
            for id_config in self.param_fg.keys():
                self.results_fg_lk_mv[id_config]['TIME'].append(tfin)
                self.results_fg_lk_mv[id_config]['ZSTR'].append(
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
        self.model_size, _, _ = self.masc.get_var_size('Model.X')
        coords = []
        for i in range(self.model_size):
            coords.append(self.masc.get('Model.X', i))
        coords = np.array(coords)
        for id_lk in self.param_fg.keys():
            # 2 valeur
            # 'PK' regule
            # 'abscissa' pk link
            idx = (np.abs(coords - self.param_fg[id_lk]['PK'])).argmin()
            if idx:
                self.param_fg[id_lk]['SECCON'] = idx
            else:
                self.clapi.add_info("Regulation point not found for numlink {}.".format(id_lk))
        del coords

    def search_link_to_param_fg(self):
        self.size_link, _, _ = self.masc.get_var_size('Model.Link.Kind')
        lst_info = []
        coords = []
        for id_mas_lk in range(self.size_link):
            nature = self.masc.get('Model.Link.Kind', id_mas_lk)
            typ = self.masc.get('Model.Link.Type', id_mas_lk)
            if nature == 1 and typ in [1, 4]:  # narure 1: basin-reach, typ 1 weirs, 4 culvert
                abs = self.masc.get('Model.Link.StoR.Abscissa', id_mas_lk)
                lst_info.append(id_mas_lk)
                coords.append(abs)
        coords = np.array(coords)
        for id_lk in self.param_fg.keys():
            idx = (np.abs(coords - self.param_fg[id_lk]['abscissa'])).argmin()
            if idx:
                id_mas = lst_info[idx]
                self.param_fg[id_lk]['id_mas'] = id_mas
                # variable qui bougera
                self.param_fg[id_lk]['level'] = self.masc.get("Model.Link.Level", id_mas)
                self.param_fg[id_lk]['CSection'] = self.masc.get("Model.Link.CSection", id_mas)
                # conserv variable initial
                self.param_fg[id_lk]['CSection0'] = self.masc.get("Model.Link.CSection", id_mas)
                self.param_fg[id_lk]['level0'] = self.masc.get("Model.Link.Level", id_mas)
            else:
                self.clapi.add_info("Id_mas not found for numlink {}.".format(id_lk))
        del coords, lst_info

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
            self.results_fg_lk_mv[id_config]['TIME'].append(time)
            self.results_fg_lk_mv[id_config]['ZSTR'].append(newz)
        else:
            if (time - dt) not in self.results_fg_lk_mv[id_config]['TIME']:
                self.results_fg_lk_mv[id_config]['TIME'].append(time - dt)
                self.results_fg_lk_mv[id_config]['ZSTR'].append(zold)
            self.results_fg_lk_mv[id_config]['TIME'].append(time)
            self.results_fg_lk_mv[id_config]['ZSTR'].append(newz)


    def fg_actif(self):
        return self.init_var.fg_actif()
