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
import os

import numpy as np
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *


class ClassLaws:
    def __init__(self, parent):
        self.parent = parent
        self.mgis = self.parent.mgis
        self.mdb = self.parent.mdb
        self.tbst = self.parent.tbst
        self.grav = self.parent.grav
        self.dico_abc = {}
        self.dossier_file_masc = os.path.join(self.mgis.masplugPath, "mascaret")
        self.dico_name_abac = {}
        self.param_g = {}
        self.poly_p = None
        self.qh_j_no_hy = []
        # valeur pour éviter des débit null et blocker le model
        self.deb_min = 0.0001

    def init_method(self, id_config):
        """intialisation variables"""
        if self.parent.checkprofil(id_config):
            profil = self.parent.get_profil(id_config)
        else:
            msg = "Profile copy isn't found"
            self.mgis.add_info(msg)
            print(msg)
            return

        list_recup = ['FIRSTWD', 'NBTRAVE',
                      'ZTOPTAB', 'COEFDS', 'COEFDO',
                      # numeric
                      'MAXH', 'MINH', 'PASH']
        self.param_g = self.parent.get_param_g(list_recup, id_config)
        list_key = list(self.param_g.keys())
        if not 'COEFDO' in list_key:
            self.param_g['COEFDO'] = 1
        if not 'COEFDS' in list_key:
            self.param_g['COEFDS'] = 0.385

        self.param_g['NBPIL'] = self.param_g['NBTRAVE'] - 1
        self.poly_p = self.parent.poly_profil(profil)

        poly_tmp = self.parent.coup_poly_h(self.poly_p, self.param_g['ZTOPTAB'])
        (minx, miny, maxx, maxy) = poly_tmp.bounds
        self.param_g['TOTALW'] = maxx - minx

        # ***********************************
        (minx, miny, maxx, maxy) = self.poly_p.bounds
        self.minz = miny
        # self.list_zav = [miny]
        self.list_zav = list(
            np.arange(self.minz + self.param_g['MINH'], self.param_g['MAXH'] + self.minz, self.param_g['PASH']))
        self.list_zav.append(self.param_g['MAXH'] + self.minz)

        self.list_zam = np.array(self.list_zav)

        where = " id_config={} and type=0 ".format(id_config)
        order = "id_elem"
        self.list_poly_trav = self.parent.select_poly('struct_elem', where, order)['polygon']

        # TODO modifier ZPC car arch depend element meme pour dalot
        self.param_elem = {'ZMAXELEM': [], 'LARGELEM': [], 'SURFELEM': []}
        for poly in self.list_poly_trav:
            (minx, miny, maxx, maxy) = poly.bounds
            self.param_elem['ZMAXELEM'].append(maxy)
            self.param_elem['LARGELEM'].append(maxx - minx)
            self.param_elem['SURFELEM'].append(poly.area)

    def check_listinter(self, dico_abc, name_abc, varx, vary):
        if len(dico_abc[name_abc][varx]) == len(dico_abc[name_abc][vary]):
            return dico_abc[name_abc][varx], dico_abc[name_abc][vary]
        else:
            list_inter_x = []
            list_inter_y = []
            for idx, orderx in enumerate(dico_abc[name_abc]['order_{}'.format(varx)]):
                for jdx, ordery in enumerate(dico_abc[name_abc]['order_{}'.format(vary)]):
                    if orderx == ordery:
                        list_inter_x.append(dico_abc[name_abc][varx][idx])
                        list_inter_y.append(dico_abc[name_abc][vary][jdx])
            return list_inter_x, list_inter_y

            # *******************************************************
            # Bradley
            # *******************************************************

    def check_coefm(self, coefm, verb=False):
        cond = True
        msg = 'The following coeficients leave application domain :\n'
        if coefm < 0.45:
            msg += '\t - Kp coeficient\n'
            cond = False
        if coefm < 0.3:
            msg += '\t - Kb coeficient\n'
            cond = False
        if coefm < 0.2 or coefm > 1:
            msg += '\t - Ke coeficient\n'
            cond = False
        if coefm < 0.3 or coefm > 1:
            msg += '\t - Ks coeficient\n'
            cond = False
        if m.isnan(coefm):
            msg = '\t m coeficient is NAN\n'
            cond = False
        if not cond and verb:
            print(msg)
        return cond

    def check_j(self, j, form, q, h):
        if form == 1 and j > 0.057:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
        if form == 2 and j > 0.067:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
        if form == 3 and j > 0.095:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
        if form == 4 and j > 0.116:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
        if form == 5 and j > 0.14:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
        if form == 6 and j > 0.166:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
        if form == 7 and j > 0.18:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
        if form == 8 and j > 0.18:
            if [q, h] not in self.qh_j_no_hy:
                self.qh_j_no_hy.append([q, h])
            j = 0.18  # hyp for working
        return j

    def init_bradley(self, method, id_config):
        """ initialisation for bradley method"""
        list_recup = ['BIAIOUV',
                      'FORMCUL', 'ORIENTM',
                      'PENTTAL', 'EPAITAB', 'BIAICUL',
                      # pile de pont
                      'LARGPIL', 'LONGPIL', 'FORMPIL', 'BIAIPIL',
                      # numeric
                      'MAXQ', 'MINQ', 'PASQ']
        param_g_temp = self.parent.get_param_g(list_recup, id_config)
        self.param_g.update(param_g_temp)
        self.param_g['BIAIOUV'] = self.param_g['BIAIOUV'] / 180. * m.pi  # rad
        # only brad
        where = " id_config={} and type=1 ".format(id_config)
        order = "id_elem"
        self.list_poly_pil = self.parent.select_poly('struct_elem', where, order)['polygon']

        self.list_q = list(np.arange(self.param_g['MINQ'], self.param_g['MAXQ'], self.param_g['PASQ']))
        self.list_q.append(self.param_g['MAXQ'])

        self.dico_name_abac = {
            'Bradley 78': {'abac': ['bradley', 'bradley78']},
            'Bradley 72': {'abac': ['bradley', 'bradley72']}
        }
        self.dico_abc = self.parent.get_abac(self.dico_name_abac[method]['abac'])
        self.param_g['TOTALOUV'] = 0
        for poly in self.list_poly_trav:
            (minx, miny, maxx, maxy) = poly.bounds
            self.param_g['TOTALOUV'] += (maxx - minx)

        type_kb = self.def_type_kb(method)

        if self.param_g['BIAICUL'] == '0':
            abac_dks = "dKs_casA_abac"
        else:
            abac_dks = "dKs_casB_abac"

        list_ph = []
        for key in self.dico_abc[abac_dks].keys():
            if key != 'M' and key != 'phi>45' and 'order_' not in key:
                list_ph.append((key, float(key.split('=')[1])))
        list_ph = sorted(list_ph)

        list_e = []
        for key in self.dico_abc['dKe_abac'].keys():
            if key != 'M' and 'order_' not in key:
                list_e.append((key, float(key.split('=')[1])))
        list_e = sorted(list_e)

        coef_cor_biais = (self.param_g['LONGPIL'] * m.sin(self.param_g['BIAIOUV']) +
                          self.param_g['LARGPIL'] * m.cos(self.param_g['BIAIOUV'])) / self.param_g['LARGPIL']

        return coef_cor_biais, type_kb, list_ph, list_e

    def meth_brad(self, zav, q, coef_cor_biais, type_kb, list_ph, list_e):
        """
        Compute  h upstream with bradley method
        :param zav: zav cote downstream
        :param q: flow rate

        :param coef_cor_biais: angle correction coefficient
        :param type_kb: kb coefficient type
        :param list_ph: phi list in abacus
        :param list_e: e list in abacus
        :return  [flowrate, h downstream, h upstream]
        """
        area_pil = 0
        area_pil_proj = 0
        poly_wet = self.parent.coup_poly_h(self.poly_p, zav + self.minz)
        if poly_wet.is_empty:
            return None
        area_wet = poly_wet.area
        # print('area_wet',area_wet)
        umoy = q / area_wet
        for poly_pil in self.list_poly_pil:
            poly_pil = self.parent.coup_poly_h(poly_pil, zav + self.minz)
            if self.param_g['BIAIOUV'] != 0:
                area_pil_proj += poly_pil.area * coef_cor_biais
            area_pil += poly_pil.area
        if area_pil_proj == 0:
            area_pil_proj = area_pil
        ssoh = self.parent.coup_poly_v(poly_wet, [self.param_g['FIRSTWD'], self.param_g['TOTALW']],
                                       typ='LR').area
        q1 = ssoh * umoy
        q2 = self.parent.coup_poly_v(poly_wet, self.param_g['FIRSTWD'], typ='R').area * umoy
        q3 = self.parent.coup_poly_v(poly_wet, self.param_g['TOTALW'], typ='L').area * umoy
        qtot = q1 + q2 + q3
        alpha1 = 1
        alpha2 = 1
        if qtot != 0:
            coefm = q1 / qtot
        else:
            # hyp si debit null cote aval =cote amon
            # list_final.append([q, zav, zav])
            return [self.deb_min, zav, zav]
            # coefm = 0

        # print('q1,q2,q3',q1,q2,q3)
        # print('area q1, area q2,area q3', ssoh,
        # self.parent.coup_poly_v(poly_wet,self.param_g['FIRSTWD'],typ='R').area,
        #       self.parent.coup_poly_v(poly_wet,self.param_g['TOTALW'],typ='L' ).area)
        # print('coefm', coefm)
        if not self.check_coefm(coefm):
            return None

        s1 = ssoh - area_pil_proj
        # print('S1',s1)
        va = q / s1
        # print('Va', va)
        # *************** kb
        list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, "kb_abac", 'M', type_kb)
        kb = np.interp(coefm, list_inter_x, list_inter_y)

        # *************** Dkp
        # print(area_pil_proj,ssoh,area_pil)
        j = area_pil_proj / ssoh
        j = self.check_j(j, int(self.param_g['FORMPIL']), q, zav)
        # print('j',j)
        list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, 'DKp_abac', 'J',
                                                          str(int(self.param_g['FORMPIL'])))
        dkp = np.interp(j, list_inter_x, list_inter_y)

        # print('Dkp', dkp)
        list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, 's_abac', 'M',
                                                          str(int(self.param_g['FORMPIL'])))
        coefs = np.interp(coefm, list_inter_x, list_inter_y)
        # print('s', coefs)
        dkp = dkp * coefs
        # print('sDkp',dkp)
        if q3 < q2:
            e_calc = 1 - q3 / q2
        elif q2 < q3:
            e_calc = 1 - q2 / q3
        else:
            e_calc = 0

        list_m_interp = []
        list_e_interp = []
        for ee in list_e:
            list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, 'dKe_abac', 'M', ee[0])
            inter_tmp = np.interp(coefm, list_inter_x, list_inter_y)
            list_m_interp.append(inter_tmp)
            list_e_interp.append(ee[1])

        dke = np.interp(e_calc, list_e_interp, list_m_interp)
        # print('dke', dke)

        if self.param_g['BIAIPIL'] == 0:
            dks = 0
        else:
            if self.param_g['BIAIOUV'] > 45:
                list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, abac_dks, 'M', 'phi>45')
                dksx = np.interp(coefm, list_inter_x, list_inter_y)
            else:

                list_m_interp = []
                list_ph_interp = []
                for ph in list_ph:
                    list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, abac_dks, 'M', ph[0])
                    inter_tmp = np.interp(coefm, list_inter_x, list_inter_y)
                    list_m_interp.append(inter_tmp)
                    list_ph_interp.append(ph[1])
                dksx = np.interp(self.param_g['BIAIOUV'], list_ph_interp, list_m_interp)

            if dksx > 0:
                dks = dksx
            else:
                dks = 0
        # print("dks",dks)
        term1 = (kb + dkp + dke + dks) * va ** 2 / (2. * self.grav) * alpha2
        # print("term1 Remout",term1)
        hmon = zav + term1
        poly_wet = self.parent.coup_poly_h(self.poly_p, hmon + self.minz)
        area_amont = poly_wet.area
        term2 = alpha1 * ((s1 / area_wet) ** 2 - (s1 / area_amont) ** 2) * va ** 2 / (
            2. * self.grav)
        # print("term2 Remout", term2)
        remout = term1 + term2

        # print("Remout Total", remout)
        return [q, zav, zav + remout]

    def filtre_list(self, liste, valG, valD):
        """
        To filter list
        :param liste: list to filter
        :param valG: left value
        :param valD:  right value
        :return: (list)
        """
        idx = np.where(valG < liste)[0]
        sortie = liste[idx]
        idx = np.where(sortie < valD)[0]

        return list(sortie[idx])

    def bradley(self, id_config, method='Bradley 78', ui=None):
        """cas methode bradley"""
        # *************************************
        self.init_method(id_config)
        list_final = []

        (coef_cor_biais, type_kb, list_ph, list_e) = self.init_bradley(method, id_config)

        val = 90 / len(self.list_zav)

        zinf_vann = self.poly_p.bounds[1]  # z min du profil
        zcret = self.param_g['ZTOPTAB']
        # self.list_zav=[9.75,6.25]
        ztransi = min(self.param_elem['ZMAXELEM'])  # Z de transition

        for zav in self.list_zav:
            list_brad = []
            brad_lim = None
            for q in self.list_q:
                value = self.meth_brad(zav - self.minz, q, coef_cor_biais, type_kb, list_ph, list_e)
                # [q, zav, zav + remout]
                if value is None:
                    continue
                else:
                    if value[2] > ztransi:
                        brad_lim = value
                        break
                    list_brad.append(value)
            # traitement entre les deux loi
            list_ori = []
            if len(list_brad) > 0:
                # interpol ztrans
                list_ori.append(list_brad[-1])
                if brad_lim:
                    # interpolation
                    q_tmp = np.array([list_brad[-1][0], brad_lim[0]])
                    zam_tmp = np.array([list_brad[-1][2], brad_lim[2]])
                    q_new = np.interp(ztransi, zam_tmp, q_tmp)
                    list_ori = list_ori + [[q_new, zav, ztransi]]
                    # list_final += [[q_new ,zav ,ztransi]]
                    qmax = q_new
                    za = ztransi
                else:
                    qmax = max(np.array(list_brad)[:, 0])
                    za = list_brad[-1][2]
                    list_ori.append([qmax, zav, za])
            else:
                qmax = self.deb_min
                za = zav
                list_ori.append([qmax, zav, za])

            idx = np.where(self.list_zam > za)[0]
            if len(idx) > 0:
                # if self.list_zam[idx[0]-1] == zav:
                # if self.deb_min == qmax:
                # list_final.append([self.deb_min, zav, zav])
                for zam in self.list_zam[idx[0]:]:
                    if zav != zam:
                        q_seuil = 0
                        q_ori = 0
                        for i, zsup in enumerate(self.param_elem['ZMAXELEM']):
                            q_ori += self.meth_orif_cano(zam, zav, zinf_vann, zsup, zcret,
                                                         self.param_elem['LARGELEM'][i], self.param_g['COEFDS'],
                                                         self.param_g['COEFDO'], self.param_elem['SURFELEM'][i])

                        # print('zam q_ori',zam, q_ori)
                        if zam >= zcret:
                            q_seuil = self.meth_seuil(zam, zav, zcret, self.param_g['COEFDS'], self.param_g['TOTALW'])
                        # print('q_seuil',zam, q_seuil)
                        if q_ori == 0 and q_seuil == 0:
                            value = None
                        else:
                            value = [q_ori + q_seuil, zav, zam]
                        if value is None:
                            continue
                        else:
                            if value[0] > self.param_g['MAXQ']:
                                list_ori.append(value)
                                break
                            # if value[0] > qmax: # permet l'interpolation des valeurs h superieur même si le débit inferieur
                            # print('ori va',value)
                            # probléme peut venir de ça
                            list_ori.append(value)

            # interpol q fix
            if len(list_ori) > 1:
                idx = np.where(np.array(self.list_q) > list_ori[0][0])[0]
                if len(idx) > 0:
                    list_q_tmp = self.list_q[idx[0]:]
                else:
                    list_q_tmp = self.list_q
                # print(list_ori)
                q_tmp = np.array(list_ori)[:, 0]
                zam_tmp = np.array(list_ori)[:, 2]
                zam_f = np.interp(list_q_tmp, q_tmp, zam_tmp)
                interpol_list = [[a, b, c] for a, b, c in zip(list_q_tmp, [zav] * len(zam_f), zam_f)]
                list_ori = interpol_list
            else:
                list_ori = []
            list_final = list_final + list_brad + list_ori

            if ui is not None:
                ui.progress_bar(val)
        list_final = self.transition_charge(list_final, ztransi)
        list_final = self.complete_law(list_final)
        self.save_list_final(list_final, id_config, method)
        if ui is not None:
            ui.progress_bar(100)
        self.test_csv(list_final)

        return list_final

    def transition_charge(self, list_final, ztransi):
        """

        :param list_final: law interpol
        :param ztransi:
        :return:
        """
        # trie pour être sûr
        info = self.parent.sort_law(list_final)
        # ajout de Z pour  acroite le point d'infexion
        for id, deb in enumerate(self.list_q):
            # cherche nb de debi
            idxq = np.where(info[:, 0] == deb)[0]
            # cherche position transition
            idxz = np.where(info[idxq, 2] < ztransi)[0]
            if len(idxz) > 0:
                idxz = idxq[0] + idxz[-1]
                tab_tmp = info[idxz, :]
                tab_tmp1 = info[idxz + 1, :]
                print(tab_tmp, tab_tmp1, deb)

                zmoy = (tab_tmp[1] + tab_tmp1[1]) / 2
                ecartmoy = (tab_tmp1[2] + tab_tmp[2]) / 2 - zmoy
                ecart1 = tab_tmp[2] - tab_tmp[1]
                ecart2 = tab_tmp1[2] - tab_tmp1[1]

                if ecart2 < ecartmoy:
                    ecart2 = ecartmoy
                    # return list_final
                if ecart1 > ecartmoy:
                    ecart1 = ecartmoy
                    # return list_final

                z1 = (tab_tmp[1] + 2 * zmoy) / 3
                z2 = (tab_tmp1[1] + 2 * zmoy) / 3

                list_final.append([deb, z1, z1 + ecart1])
                list_final.append([deb, zmoy, (tab_tmp1[2] + tab_tmp[2]) / 2])
                list_final.append([deb, z2, z2 + ecart2])

        return list_final

    def complete_law(self, list_final):
        info = self.parent.sort_law(list_final)
        unique, counts = np.unique(info[:, 1], return_counts=True)
        nb_val = max(counts)
        list_val = []
        new_list = []
        for val, cpt in zip(unique, counts):
            if cpt != nb_val:
                list_val.append(val)

        for id, deb in enumerate(self.list_q):
            idxq = np.where(info[:, 0] == deb)[0]
            tab = info[idxq, :]
            modif = False
            add_val = []
            for val in list_val:
                if not (val in tab[:,1]):
                    modif = True

                    zam_f = np.interp(val, tab[:,1], tab[:,2])
                    if deb == 100:
                        print('rrrrrr',zam_f,deb,val)
                    add_val.append([deb, val, zam_f])
            if modif:
                new_list = new_list + list(tab) + add_val
            else:
                new_list += list(tab)

        return new_list

    def save_list_final(self, list_final, id_config, method):
        # **********************************************************************************************
        # save
        # *********************************************************************************************
        if list_final == []:
            sql = "SELECT name FROM {0}.{1} WHERE id={2}".format(self.mdb.SCHEMA, 'struct_config', id_config)

            name = self.mdb.run_query(sql, fetch=True)
            name = name[0][0]

            sql = "UPDATE {0}.{1} SET {2}  WHERE id={3};".format(self.mdb.SCHEMA, 'struct_config', 'active=False',
                                                                 id_config)
            self.mdb.run_query(sql)

            self.mgis.add_info(
                "No values for the law because the coefficients leave application domain of the method.\n"
                "The <<{}>> hydraulic structur is deactivated".format(name))
        else:
            self.parent.save_law_st(method, id_config, list_final)

    def def_type_kb(self, method):
        if method == 'Bradley 78':
            if self.param_g['TOTALOUV'] > 60 and self.param_g['FORMCUL'] == 1:
                type_kb = 'Others'
            else:
                type_kb = 'type1<60m'
                list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, "kb_abac", 'M', type_kb)
                self.dico_abc["kb_abac"]['M'] = list_inter_x
                self.dico_abc["kb_abac"][type_kb] = list_inter_y

        elif method == 'Bradley 72':
            if self.param_g['FORMCUL'] == 1:
                type_kb = 'type1'
            elif self.param_g['FORMCUL'] == 2:
                if self.param_g['ORIENTM'] == 30:
                    type_kb = 'type2_30deg'
                else:
                    type_kb = 'type2_45to60deg'
            elif self.param_g['FORMCUL'] == 3:
                if self.param_g['PENTTAL'] == 0:
                    type_kb = 'type3_1:1'
                elif self.param_g['PENTTAL'] == 1:
                    type_kb = 'type3_1.5:1'
                else:
                    type_kb = 'type3_2:1'
            else:
                # defaut 1
                type_kb = 'type1'
                # list_inter_x, list_inter_y = self.check_listinter(self.dico_abc, "kb_abac", 'M', type_kb)
        return type_kb

    def meth_seuil(self, zam, zav, zcret, cf, larg):
        """ methode seuil"""
        ct = cf * m.sqrt(2 * self.grav)
        typ_s = 0  # 0 :'thick', 1: thin

        h1 = max(zam - zcret, 0)
        h2 = max(zav - zcret, 0)
        if h1 == 0 and h2 == 0:
            return 0
        ham = max(h1, h2)
        hav = min(h1, h2)
        r = hav / ham
        if (h1 >= h2):
            sens_ecoul = 1
        else:
            sens_ecoul = -1
        q_denoy = ct * larg * m.pow(ham, 1.5)
        if typ_s == 0:
            if r <= 0.8:
                k = 1
            elif 0.8 < r <= 1:
                k = -25 * m.pow(r, 2) + 40 * r - 15
            else:
                k = 0
        else:
            if ham == 0.:
                k = 1
            else:
                k = m.pow(m.pow(1 - r, 1.5), 0.385)
        q = sens_ecoul * k * q_denoy

        return q

    def meth_orif_mas(self, zam, zav, zinf, zsup, larg, cf, cfo, surf):
        """ methode orifice"""
        ouv = zsup - zinf
        h1 = zam - zinf
        h2 = zav - zinf
        hav = min(h1, h2)
        ham = max(h1, h2)
        ct = cfo * m.sqrt(2 * self.grav)

        if ham < 0:
            print('erreur loi orifice ham <0')
            return None
        if (h1 >= h2):
            sens_ecoul = 1
        else:
            sens_ecoul = -1

        if hav < ouv and ham < ouv + 0.2:

            q = self.meth_seuil(zam, zav, zinf, cf, larg)
        else:
            if hav > ouv:
                q = ct * surf * m.sqrt(ham - hav)
            else:
                q = ct * surf * m.sqrt(ham)
            q = sens_ecoul * q

        return q

    def meth_orif_cano(self, zam, zav, zinf, zsup, zcret, larg, cf, cfo, surf):

        ouv = zsup - zinf
        h1 = zam - zinf
        h2 = zav - zinf
        hav = min(h1, h2)
        ham = max(h1, h2)
        epsd = 0.01
        epso = 0  # 0.05 * (zcret - zsup)
        rac_epsd = m.sqrt(0.01)
        ct = cfo * m.sqrt(2 * self.grav)
        if (h1 >= h2):
            sens_ecoul = 1
        else:
            sens_ecoul = -1
        if ham < 0:
            print('erreur loi orifice ham <0')
            return None

        if (surf < 0.):
            return 0
        qo = 0
        qs = 0
        if ham < ouv + epso:
            qs = self.meth_seuil(zam, zav, zinf, cf, larg)

        if ham > ouv:  # ! fonctionnement en orifice
            a2 = 0.65
            # a1 = ouv / ham
            # a2 = 0.65
            # # if 0.55<= a1 < 0.9 :
            #         a2 = 0.5 + 0.268 * a1
            # elif 0.9<= a1 :
            #         a2 = 0.745 + 2.55 * (a1 - 0.9)
            if (ham - hav) <= epsd:  # traitement linéarisé pour les petits déniveles
                qo = surf * a2 * (ham - hav) / rac_epsd

            else:  # ! traitement normal
                a3 = max(hav, 0.5 * ouv)
                qo = surf * a2 * m.sqrt(ham - a3)
        qo = ct * qo

        if ham < ouv:
            q = qs
        elif ham > ouv + epso:
            q = qo
        else:
            q = qs + (ham - ouv) * (qo - qs) / epso
        q = sens_ecoul * q

        return q

    def search_qmax(self, tmp):
        """
        search the most little max
        :param tmp: list of values
        :return:
        """
        list_qmax = []
        for zav in np.unique(tmp[:, 1]):
            idx = np.where(tmp[:, 1] == zav)[0]
            if len(idx) > 0:
                list_qmax.append(max(tmp[idx, 0]))
        if list_qmax:
            qmax = min(list_qmax)
        else:
            qmax = max(tmp[:, 0])

        return qmax

    def interpol_list_final_for_new_q(self, list_final, pasq=10):
        """
        Search the  new (q, zav) couple and interpole with new q
        :param list_final
        :return:
        """
        tmp = np.array(list_final)
        qmin = min(tmp[:, 0])

        qmax = max(tmp[:, 0])
        # int(qmin) pour avoir des valeurs rondes
        q_new = np.arange(int(qmin), qmax, pasq)
        q_new[0] = qmin
        list_final = []
        for zav in np.unique(tmp[:, 1]):
            idx = np.where(tmp[:, 1] == zav)[0]
            if len(idx) > 1:
                q_tmp = tmp[idx, 0]
                zam_tmp = tmp[idx, 2]
                zam_f = np.interp(q_new, q_tmp, zam_tmp)
                interpol_list = [[a, b, c] for a, b, c in zip(q_new, [zav] * len(zam_f), zam_f)]
                list_ori = interpol_list
            else:
                list_ori = []
            list_final = list_final + list_ori

        return list_final

    def borda_q(self, id_config, method='Borda', ui=None):
        """Borda methode for structure"""
        self.init_method(id_config)
        list_final = []
        qmax = self.deb_min  # self.param_g['MINQ']
        zcret = self.param_g['ZTOPTAB']
        # self.list_zav =[3,4,6,7,9]
        val = 90 / len(self.list_zav)
        area_tot = 0.
        for poly_trav in self.list_poly_trav:
            area_tot += poly_trav.area

        for zav in self.list_zav:

            pr_area_wet = self.area_wet_fct(self.poly_p, zav)
            area_wet = 0
            for poly_trav in self.list_poly_trav:
                area_wet += self.area_wet_fct(poly_trav, zav)
            if pr_area_wet == 0 or area_wet == 0:
                continue
            list_borda = []
            for q in self.list_q:
                if pr_area_wet != 0 and area_wet != 0:
                    zam = self.meth_borda_z(pr_area_wet, area_wet, q, zav)
                    # [q, zav, zam]

                    if zam > zcret:
                        borda_lim = [q, zav, zam]
                        break
                    list_borda.append([q, zav, zam])

                list_seuil = []
                if len(list_borda) > 0:
                    # interpol ztrans
                    list_seuil.append(list_borda[-1])
                    if borda_lim:
                        # interpolation
                        q_tmp = np.array([list_borda[-1][0], borda_lim[0]])
                        zam_tmp = np.array([list_borda[-1][2], borda_lim[2]])
                        q_new = np.interp(zcret, zam_tmp, q_tmp)
                        list_seuil = list_seuil + [[q_new, zav, zcret]]
                        qmax = q_new
                        za = zcret
                    else:
                        qmax = max(np.array(list_borda)[:, 0])
                        za = list_borda[-1][2]
                        list_seuil.append([qmax, zav, za])
                else:
                    qmax = self.deb_min
                    za = zav
                    list_seuil.append([qmax, zav, za])

                idx = np.where(self.list_zam > za)[0]
                if len(idx) > 0:
                    for zam in self.list_zam[idx[0]:]:
                        q_borda = self.meth_borda_q(pr_area_wet, area_tot, zam, zav)
                        q_seuil = self.meth_seuil(zam, zav, zcret, self.param_g['COEFDS'], self.param_g['TOTALW'])
                        print('q_seuil', q_seuil, zav, zam)

                        value = [q_seuil + q_borda, zav, zam]
                        if q_seuil is None:
                            continue
                        else:
                            if value[0] > qmax:
                                # print('ori va',value)
                                list_seuil.append(value)

                if len(list_seuil) > 1:
                    idx = np.where(np.array(self.list_q) > list_seuil[0][0])[0]
                    if len(idx) > 0:
                        list_q_tmp = self.list_q[idx[0]:]
                    else:
                        list_q_tmp = self.list_q
                    print(list_seuil)
                    q_tmp = np.array(list_seuil)[:, 0]
                    zam_tmp = np.array(list_seuil)[:, 2]
                    zam_f = np.interp(list_q_tmp, q_tmp, zam_tmp)
                    interpol_list = [[a, b, c] for a, b, c in zip(list_q_tmp, [zav] * len(zam_f), zam_f)]
                    list_seuil = interpol_list
                else:
                    list_seuil = []

                list_final = list_final + list_brad + list_ori
            if ui is not None:
                ui.progress_bar(val)

        list_final = self.interpol_list_final_for_new_q(list_final, pasq=10)
        # print(list_final)
        self.test_csv(list_final)

        self.save_list_final(list_final, id_config, method)
        if ui is not None:
            ui.progress_bar(100)
        return list_final

    def borda(self, id_config, method='Borda', ui=None):
        """Borda methode for structure"""
        self.init_method(id_config)
        list_final = []
        qmax = self.deb_min  # self.param_g['MINQ']
        zcret = self.param_g['ZTOPTAB']
        # self.list_zav =[3,4,6,7,9]
        val = 90 / len(self.list_zav)

        for zav in self.list_zav:

            pr_area_wet = self.area_wet_fct(self.poly_p, zav)
            area_wet = 0
            for poly_trav in self.list_poly_trav:
                area_wet += self.area_wet_fct(poly_trav, zav)
            if pr_area_wet == 0 or area_wet == 0:
                continue
            idx = np.where(self.list_zam > zav)[0]
            if len(idx) > 0:
                # debut debit mini
                if self.list_zam[idx[0] - 1] == zav:
                    # attention traitemen peut être différent
                    value = [self.deb_min, zav, self.list_zam[idx[0] - 1]]
                    list_final.append(value)

                for zam in self.list_zam[idx[0]:]:
                    q_seuil = 0
                    q_bor = self.meth_borda_q(pr_area_wet, area_wet, zam, zav)

                    print('q_bor', q_bor, zav, zam, area_wet)

                    if zam >= zcret:
                        q_seuil = self.meth_seuil(zam, zav, zcret, self.param_g['COEFDS'], self.param_g['TOTALW'])
                        print('q_seuil', q_seuil, zav, zam)
                    if q_bor is None:
                        value = None
                    else:
                        value = [q_bor + q_seuil, zav, zam]
                    if value is None:
                        continue
                    else:
                        if value[0] > qmax:
                            # print('ori va',value)
                            list_final.append(value)

            if ui is not None:
                ui.progress_bar(val)

        list_final = self.interpol_list_final_for_new_q(list_final, pasq=10)
        # print(list_final)
        self.test_csv(list_final)

        self.save_list_final(list_final, id_config, method)
        if ui is not None:
            ui.progress_bar(100)
        return list_final

    def test_csv(self, list_final):
        f = open(
            r'C:\Users\mehdi-pierre.daou\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\Mascaret\mascaret\toto.csv',
            'w')
        f.write('q ;zav ;zam \n')
        for val in list_final:
            f.write('{}; {} ;{} \n'.format(val[0], val[1], val[2]))
        f.close()

    def orifice(self, id_config, method='Loi d\'orifice', ui=None):
        """orifice methode for structure"""
        self.init_method(id_config)
        list_final = []
        qmax = self.deb_min  # self.param_g['MINQ']
        zcret = self.param_g['ZTOPTAB']
        surf = 0
        val = 90 / len(self.list_zav)
        self.param_g['TOTALOUV'] = 0
        for poly_trav in self.list_poly_trav:
            surf += poly_trav.area
            (minx, miny, maxx, maxy) = poly_trav.bounds
            self.param_g['TOTALOUV'] += (maxx - minx)
            self.param_g['ZPC'] = zcret - maxy

        zinf_vann = self.poly_p.bounds[1]  # z min du profil

        for zav in self.list_zav:
            qtest = 0
            pr_area_wet = self.area_wet_fct(self.poly_p, zav)
            area_wet = 0
            for poly_trav in self.list_poly_trav:
                area_wet += self.area_wet_fct(poly_trav, zav)
            if pr_area_wet == 0 or area_wet == 0:
                continue
            idx = np.where(self.list_zam > zav)[0]
            if len(idx) > 0:
                # debut debit mini
                if self.list_zam[idx[0] - 1] == zav:
                    # attention traitemen peut être différent
                    value = [self.deb_min, zav, self.list_zam[idx[0] - 1]]
                    list_final.append(value)

                for zam in self.list_zam[idx[0]:]:
                    q_seuil = 0
                    q_ori = 0
                    for i, zsup in enumerate(self.param_elem['ZMAXELEM']):
                        q_ori += self.meth_orif_cano(zam, zav, zinf_vann, zsup, zcret,
                                                     self.param_elem['LARGELEM'][i], self.param_g['COEFDS'],
                                                     self.param_g['COEFDO'], self.param_elem['SURFELEM'][i])
                    if zam >= zcret:
                        q_seuil = self.meth_seuil(zam, zav, zcret, self.param_g['COEFDS'], self.param_g['TOTALW'])
                        # print('q_seuil', q_seuil,zav,zam)
                    if q_ori is None:
                        value = None
                    else:
                        value = [q_ori + q_seuil, zav, zam]
                    if value is None:
                        continue
                    else:
                        if value[0] > qmax and value[0] > qtest:
                            # print('ori va',value)
                            list_final.append(value)
                            # impose debit toujours superieur
                            qtest = value[0]
            if ui is not None:
                ui.progress_bar(val)

        list_final = self.interpol_list_final_for_new_q(list_final, pasq=10)
        self.test_csv(list_final)

        self.save_list_final(list_final, id_config, method)
        if ui is not None:
            ui.progress_bar(100)
        return list_final

    def meth_borda_q(self, sav, sc, zam, zav):
        k = (sav / sc - 1) ** 2
        q = m.sqrt((zam - zav) * 2 * self.grav / k) * sav
        return q

    def meth_borda_z(self, sav, sc, q, zav):
        k = (sav / sc - 1) ** 2
        zam = (q / sav) ** 2 * k / (2 * self.grav) + zav
        return zam

    def area_wet_fct(self, poly, zav):
        poly_wet = self.parent.coup_poly_h(poly, zav)
        if poly_wet.is_empty:
            return 0
        return poly_wet.area
