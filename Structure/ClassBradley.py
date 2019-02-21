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
import numpy as np
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from shapely.geometry import *


class ClassBradley:
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

    def init_method(self, id_config):
        if self.parent.checkprofil(id_config):
            profil = self.parent.get_profil(id_config)
        else:
            msg = "Profile copy isn't found"
            self.mgis.add_info(msg)
            print(msg)
            return

        list_recup = ['FIRSTWD', 'BIAIOUV', 'NBTRAVE', 'TOTALOUV',
                      'TOTALW', 'FORMCUL', 'ORIENTM',
                      'PENTTAL', 'ZTOPTAB', 'EPAITAB', 'BIAICUL',
                      # pile de pont
                      'LARGPIL', 'LONGPIL', 'FORMPIL', 'BIAIPIL',
                      # numeric
                      'MAXH', 'MINH', 'PASH', 'MINQ', 'MAXQ', 'PASQ']
        self.param_g = self.parent.get_param_g(list_recup, id_config)

        self.param_g['ZPC'] = self.param_g['ZTOPTAB'] - self.param_g['EPAITAB']
        self.param_g['BIAIOUV'] = self.param_g['BIAIOUV'] / 180. * m.pi  # rad
        self.param_g['NBPIL'] = self.param_g['NBTRAVE'] - 1
        self.poly_p = self.parent.poly_profil(profil)

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

    def init_bradley(self, method):
        """ initialisation for bradley method"""
        self.dico_name_abac = {
            'Bradley 78': {'abac': ['bradley', 'bradley78']},
            'Bradley 72': {'abac': ['bradley', 'bradley72']}
        }
        self.dico_abc = self.parent.get_abac(self.dico_name_abac[method]['abac'])

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

    def meth_brad(self, hn, q, list_poly_pil, coef_cor_biais, type_kb, list_ph, list_e):
        """
        Compute  h upstream with bradley method
        :param hn: h downstream
        :param q: flow rate
        :param list_poly_pil: span polygon list
        :param coef_cor_biais: angle correction coefficient
        :param type_kb: kb coefficient type
        :param list_ph: phi list in abacus
        :param list_e: e list in abacus
        :return  [flowrate, h downstream, h upstream]
        """
        area_pil = 0
        area_pil_proj = 0
        poly_wet = self.parent.coup_poly_h(self.poly_p, hn)
        if poly_wet.is_empty:
            return None

        area_wet = poly_wet.area
        # print('area_wet',area_wet)
        umoy = q / area_wet
        for poly_pil in list_poly_pil:
            poly_pil = self.parent.coup_poly_h(poly_pil, hn)
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
            # list_final.append([q, hn, hn])
            return [q, hn, hn]
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
        j = self.check_j(j, int(self.param_g['FORMPIL']), q, hn)
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
        hmon = hn + term1
        poly_wet = self.parent.coup_poly_h(self.poly_p, hmon)
        area_amont = poly_wet.area
        term2 = alpha1 * ((s1 / area_wet) ** 2 - (s1 / area_amont) ** 2) * va ** 2 / (
            2. * self.grav)
        # print("term2 Remout", term2)
        remout = term1 + term2

        # print("Remout Total", remout)
        return [q, hn, hn + remout]

    def bradley(self, id_config, method='Bradley 78'):
        """ Bradley method"""

        self.init_method(id_config)
        where = " id_config={} and type=1 ".format(id_config)
        order = "id_elem"
        list_poly_pil = self.parent.select_poly('struct_elem', where, order)['polygon']

        (minx, miny, maxx, maxy) = self.poly_p.bounds
        list_hn = [miny]
        list_hn += list(np.arange(miny + self.param_g['MINH'], self.param_g['ZPC'], self.param_g['PASH']))
        list_hn.append(self.param_g['ZPC'])

        list_q = list(np.arange(self.param_g['MINQ'], self.param_g['MAXQ'], self.param_g['PASQ']))
        list_q.append(self.param_g['MAXQ'])

        list_final = []

        (coef_cor_biais, type_kb, list_ph, list_e) = self.init_bradley(method)

        for hn in list_hn:
            for q in list_q:
                # print('hn,q',hn,q)
                value = self.meth_brad(hn, q, list_poly_pil, coef_cor_biais, type_kb, list_ph, list_e)
                if value is None:
                    continue
                else:
                    list_final.append(value)
        print(self.qh_j_no_hy)
        if list_final == []:
            sql = "SELECT name FROM {0}.{1} WHERE id={2}".format(self.mdb.SCHEMA, 'struct_config', id_config)

            name = self.mdb.run_query(sql, fetch=True)
            name = name[0][0]

            sql = "UPDATE {0}.{1} SET {2}  WHERE id={3};".format(self.mdb.SCHEMA, 'struct_config', 'active=False',
                                                                 id_config)
            self.mdb.run_query(sql)

            self.mgis.add_info(
                "No values for the law because the coefficients leave application domain of Bradley method.\n"
                "The <<{}>> hydraulic structur is deactivated".format(name))
        else:
            self.parent.save_law_st(method, id_config, list_final)

            # return list_final

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

    # *******************************************************
    # Seuil
    # *******************************************************
    #     def seuil(self, id_config, method=''):
    #         self.init_method()
    #         (minx, miny, maxx, maxy) = self.poly_p.bounds
    #         hmini_aval = self.param_g['ZPC']
    #         hmini_amont = self.param_g['ZTOPTAB']
    #         hmax = self.param_g['HMAX']
    #
    #         list_haval = list(np.arange(self.param_g['ZPC'], self.param_g['HMAX'], self.param_g['PASH']))
    #         list_hamont = list(np.arange(self.param_g['ZTOPTAB'], self.param_g['HMAX'], self.param_g['PASH']))
    #         list_hn.append(self.param_g['ZPC'])
    #
    #         list_final = []
    #         for hamont in list_hn:
    #             for haval in list_hn:
    #                 pass

    def meth_seuil(self, zam, zav,zcret,cf,larg):

        # cf = self.param_g['COEFDEB']
        # zcret = self.param_g['ZTOPTAB']
        # larg = self.param_g['TOTALW']

        ct = cf * m.sqrt(2 * self.grav)
        typ_s=0 # 0 :'thick', 1: thin

        h1 = max(zam - zcret, 0)
        h2 = max(zav - zcret, 0)
        if h1 ==0 and h2 ==0:
            q=0
            return q
        ham = max(h1, h2)
        hav = min(h1, h2)
        if (h1 >= h2):
            sens_ecoul = 1
        else:
            sens_ecoul = -1

        r = ham / hav
        q_denoy = ct*larg*m.power(ham,1.5)

        if typ_s == 0:
            if r<=0.8:
                k=1
            elif 0.8<r<=1:
                k=-25*m.power(r,2)+40*r-15
            else:
                k=0
        else:
            if ham == 0.:
                k=1
            else:
                k = m.power(m.power(1-r,1.5),0.385)

        q = sens_ecoul * k * q_denoy

        return q

    def meth_orif(self, zam, zav, zinf, zsup, larg, cf):

        # zinf = self.poly_p.bounds[1] #min profil
        # zup = self.param_g['ZPC']
        # cf= 1 #coef debit
        # larg =self.param_g["TOTALOUV"]

        ouv =  zsup - zinf
        h1 = zam - zinf
        h2 = zav - zinf
        hav = min(h1, h2)
        ham = max(h1, h2)

        ct = cf * m.sqrt(2 * self.grav)
        surf =  larg * ouv  # rempalce larg* ouv par surface mouillé ?

        if ham < 0:
            print('erreur loi orrifice ham <0')
            return None
        if (h1 >= h2):
            sens_ecoul = 1
        else:
            sens_ecoul = -1

        if hav < ouv and ham <1.5*ouv: # attnetion cas d'un pont   ham <1.5*ouv: tjrs vrai
            # equiv. seuil
            q = self.meth_seuil(zam, zav, zinf,cf,larg)
            # cas d'un pont zinf etant = mini profil
            # q = umoy *
        else:
            if hav > ouv:
                q = ct * surf *m.sqrt(ham-hav)
            else :
                q = ct * surf * m.sqrt(ham)
            q = sens_ecoul * q

        return q

