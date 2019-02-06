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
# from ..Function  import interp
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
        self.grav = 9.81
        self.DEBUG = True
        self.dico_abc = {}
        self.dossier_file_masc = os.path.join(self.mgis.masplugPath, "mascaret")

    def check_coefm(self, coefm):
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
        if not cond:
            print(msg)
        return cond

    def bradley(self, method='Bradley 78'):
        pas_h = 0.25
        hmin = 2
        pas__q = 10
        born_q = [10, 1000]

        # if  self.parent.checkprofil(self.parent.id_config):
        #     profil = self.parent.get_profil(self.parent.id_config)
        # else:
        #     msg = "Profile copy isn't found"
        #     self.mgis.add_info(msg)
        #     print(msg)
        #     return
        # self.parent.get_param_g(self, list_recup)
        self.dico_name_abac = {'Bradley 78':
                                   {'abac': ['bradley', 'bradley78']},
                               'Bradley 72':
                                   {'abac': ['bradley', 'bradley72']}
                               }
        self.dico_abc = self.parent.get_abac(self.dico_name_abac[method]['abac'])
        # for test ***************************


        profil = {'x': [0.00,
                        0.01,
                        100.00,
                        100.10,
                        150.00,
                        150.01,
                        ],
                  'z': [25,
                        6.5,
                        6.5,
                        14,
                        14,
                        25,
                        ]}
        list_poly_pil = [Polygon([[44, 6.5], [44, 18.45], [45.50, 18.45], [45.50, 6.5], [44, 6.5]]),
                         Polygon([[85.5, 6.5], [85.5, 18.45], [87, 18.45], [87, 6.5], [85.5, 6.5]]),
                         Polygon([[127, 14], [127, 18.45], [128.50, 18.45], [128.50, 14], [127, 14]])]

        self.param_pil = {}
        self.param_g = {}
        self.param_g['BIAIOUV'] = 5
        self.param_g['NBTRAV'] = 4
        self.param_g['firstw'] = 4
        self.param_g['TOTALOUV'] = 140.0  # ouverture traver
        self.param_g['TOTALW'] = 144.5
        self.param_g['ALPHA1'] = 1
        self.param_g['ALPHA2'] = 1
        self.param_g['FORMCUL'] = 1
        self.param_g['ORIENTM'] = 30  # 30 45 60
        self.param_g['PENTTAL'] = 0
        self.param_g['ZTOPTAB'] = 19.55
        self.param_g['EPAITAB'] = 1.1
        self.param_g['ZPC'] = self.param_g['ZTOPTAB'] - self.param_g['EPAITAB']

        # bradley considere une forme de pile
        self.param_pil['LARG'] = 1.5
        self.param_pil['LONG'] = 11
        self.param_pil['FORMPIL'] = 5  # ATTENTION 1 seul Type de pil est permit dans la formulation et commence par 1

        list_hn = [8.85]
        list_q = [100]
        # *****************************************
        poly_p = self.parent.poly_profil(profil)
        (minx, miny, maxx, maxy) = poly_p.bounds
        list_hn = list(np.arange(miny + hmin, self.param_g['ZPC'], pas_h))
        list_q = list(np.arange(born_q[0], born_q[1], pas__q))

        self.param_g['BIAIOUV'] = self.param_g['BIAIOUV'] / 180. * m.pi  # rad
        self.param_g['NBPIL'] = self.param_g['NBTRAV'] - 1
        list_final = []
        # Test

        for hn in list_hn:
            for q in list_q:
                area_pil = 0
                area_pil_proj = 0
                poly_wet = self.parent.coup_poly_h(poly_p, hn)
                area_wet = poly_wet.area
                # print('area_wet',area_wet)
                umoy = q / area_wet
                for poly_pil in list_poly_pil:
                    poly_pil = self.parent.coup_poly_h(poly_pil, hn)
                    if self.param_g['BIAIOUV'] != 0:
                        area_pil_proj += poly_pil.area * \
                                         (self.param_pil['LONG'] * m.sin(self.param_g['BIAIOUV']) +
                                          self.param_pil['LARG'] * m.cos(self.param_g['BIAIOUV'])) \
                                         / self.param_pil['LARG']
                    area_pil += poly_pil.area
                if area_pil_proj == 0:
                    area_pil_proj = area_pil

                ssoh = self.parent.coup_poly_v(poly_wet, [self.param_g['firstw'], self.param_g['TOTALW']],
                                               typ='LR').area
                q1 = ssoh * umoy
                q2 = self.parent.coup_poly_v(poly_wet, self.param_g['firstw'], typ='R').area * umoy
                q3 = self.parent.coup_poly_v(poly_wet, self.param_g['TOTALW'], typ='L').area * umoy
                coefm = q1 / (q1 + q2 + q3)
                # print('q1,q2,q3',q1,q2,q3)
                # print('area q1, area q2,area q3', ssoh, self.parent.coup_poly_v(poly_wet,self.param_g['firstw'],typ='R').area,
                #       self.parent.coup_poly_v(poly_wet,self.param_g['TOTALW'],typ='L' ).area)
                self.check_coefm(coefm)
                # print('coefm',coefm)
                s1 = ssoh - area_pil_proj
                # print('S1',s1)
                va = q / s1
                # print('Va', va)
                # *************** kb
                if method == 'Bradley 78':
                    if self.param_g['TOTALOUV'] > 60 and self.param_g['FORMCUL'] == 1:
                        list_inter = self.dico_abc["kb_abac"]['Others']
                    else:
                        list_inter = self.dico_abc["kb_abac"]['type1<60m']
                    kb = np.interp(coefm, self.dico_abc["kb_abac"]['M'], list_inter)
                    # print('kb',kb)
                elif method == 'Bradley 72':
                    if self.param_g['FORMCUL'] == 1:
                        list_inter = self.dico_abc["kb_abac"]['type1']
                    elif self.param_g['FORMCUL'] == 2:
                        if self.param_g['ORIENTM'] == 30:
                            list_inter = self.dico_abc["kb_abac"]['type2_30deg']
                        else:
                            list_inter = self.dico_abc["kb_abac"]['type2_45to60deg']
                    elif self.param_g['FORMCUL'] == 3:
                        if self.param_g['PENTTAL'] == 0:
                            list_inter = self.dico_abc["kb_abac"]['type3_1:1']
                        elif self.param_g['PENTTAL'] == 1:
                            list_inter = self.dico_abc["kb_abac"]['type3_1.5:1']
                        else:
                            list_inter = self.dico_abc["kb_abac"]['type3_2:1']
                    else:
                        # defaut 1
                        list_inter = self.dico_abc["kb_abac"]['type1']

                    kb = np.interp(coefm, self.dico_abc["kb_abac"]['M'], list_inter)
                else:
                    kb = 0

                # *************** Dkp
                # print(area_pil_proj,ssoh,area_pil)
                j = area_pil_proj / ssoh
                # print('j',j)

                dkp = np.interp(j, self.dico_abc['DKp_abac']['J'],
                                self.dico_abc['DKp_abac'][str(self.param_pil['FORMPIL'])])
                # print('Dkp', dkp)
                coefs = np.interp(coefm, self.dico_abc['s_abac']['M'],
                                  self.dico_abc['s_abac'][str(self.param_pil['FORMPIL'])])
                # print('s', coefs)
                dkp = dkp * coefs
                # print('sDkp',dkp)

                if q3 < q2:
                    e_calc = 1 - q3 / q2
                elif q2 < q3:
                    e_calc = 1 - q2 / q3
                else:
                    e_calc = 0
                list_e = []
                for key in self.dico_abc['dKe_abac'].keys():
                    if key != 'M':
                        list_e.append((key, float(key.split('=')[1])))
                list_e = sorted(list_e)

                list_m_interp = []
                list_e_interp = []
                for ee in list_e:
                    list_m_interp.append(
                        np.interp(coefm, self.dico_abc['dKe_abac']['M'], self.dico_abc['dKe_abac'][ee[0]]))
                    list_e_interp.append(ee[1])

                dke = np.interp(e_calc, list_e_interp, list_m_interp)
                # print('dke', dke)

                if self.param_g['BIAIOUV'] == '0':
                    abac_dks = "dKs_casA_abac"
                else:
                    abac_dks = "dKs_casB_abac"
                if self.param_g['BIAIOUV'] == 0:
                    dks = 0
                else:
                    if self.param_g['BIAIOUV'] > 45:
                        dksx = np.interp(coefm, self.dico_abc[abac_dks]['M'], self.dico_abc[abac_dks]['phi>45'])
                    else:
                        list_ph = []
                        for key in self.dico_abc[abac_dks].keys():
                            if key != 'M' and key != 'phi>45':
                                list_ph.append((key, float(key.split('=')[1])))
                        list_ph = sorted(list_ph)

                        list_m_interp = []
                        list_ph_interp = []
                        for ph in list_ph:
                            list_m_interp.append(
                                np.interp(coefm, self.dico_abc[abac_dks]['M'], self.dico_abc[abac_dks][ph[0]]))
                            list_ph_interp.append(ph[1])
                        dksx = np.interp(self.param_g['BIAIOUV'], list_ph_interp, list_m_interp)

                    if dksx > 0:
                        dks = dksx
                    else:
                        dks = 0
                # print("dks",dks)

                term1 = (kb + dkp + dke + dks) * va ** 2 / (2. * self.grav) * self.param_g['ALPHA2']
                # print("term1 Remout",term1)
                hmon = hn + term1
                poly_wet = self.parent.coup_poly_h(poly_p, hmon)
                area_amont = poly_wet.area
                term2 = self.param_g['ALPHA1'] * ((s1 / area_wet) ** 2 - (s1 / area_amont) ** 2) * va ** 2 / (
                2. * self.grav)
                # print("term2 Remout", term2)
                remout = term1 + term2
                # print("Remout Total", remout)
                list_final.append([q, hn, hn + remout])

        return list_final

    def law_brad(self, list_final, nom):
        """creeation of law"""

        with open(os.path.join(self.dossier_file_masc, nom + '.loi'), 'w') as fich:
            fich.write('# ' + nom + '\n')
            fich.write('# Debit Cote_Aval Cote_Amont\n')
            chaine = ' {flowrate:.3f} {z_downstream:.3f} {z_upstream:.3f}\n'
            for val in list_final:
                dico = {'flowrate': val[0], 'z_downstream': val[1], 'z_upstream': val[2]}
                fich.write(chaine.format(**dico))

    # def write_law(self):
    #     ouvrage = self.mdb.select("weirs", "active")

    def modif_xcas_str(self, fichier_cas):
        prof_seuil = self.mdb.select("profiles", "NOT active", "abscissa")
        seuils = self.mdb.select("weirs", "active", "abscissa")
        ouvrages = self.mdb.select('struct_config', "active", "abscissa")
        print(ouvrages)
        print(seuils)
        print(prof_seuil)
        # singularite = fichier_cas.find("parametresSingularite")
        # # Seuils
        # SubElement(singularite, "nbSeuils").text = str(len(seuils["name"]))
        #
        # if len(seuils["name"]) > 0:
        #     e_tseuils = SubElement(singularite, "seuils")
        #
        # liste = ["type", "numBranche", "abscisse", "coteCrete", "coteCreteMoy",
        #          "coteRupture", "coeffDebit", "largVanne", "epaisseur"]
        # liste_en = ["type", "branchnum", "abscissa", "z_crest", "z_average_crest",
        #             "z_break", "flowratecoeff", "wide_floodgate", "thickness"]
        #
        # for i, nom in enumerate(seuils["name"]):
        #     struct = SubElement(e_tseuils, "structureParametresSeuil")
        #     SubElement(struct, "nom").text = nom
        #     for kk, l in enumerate(liste):
        #         if seuils[liste_en[kk].lower()][i] is None:
        #             SubElement(struct, l).text = '-0'
        #         else:
        #             SubElement(struct, l).text = str(seuils[liste_en[kk].lower()][i])
        #
        #     if seuils["type"][i] not in (3, 4):
        #         SubElement(struct, "numLoi").text = str(sorted(dict_lois.keys()))
        #     else:
        #         SubElement(struct, "numLoi").text = '-0'
        #     if seuils["type"][i] != 3:
        #         SubElement(struct, "nbPtLoiSeuil").text = '-0'
        #     else:
        #         try:
        #             i = prof_seuil["name"].index(nom)
        #             long = len(prof_seuil['x'][i].split())
        #             SubElement(struct, "nbPtLoiSeuil").text = str(long)
        #             SubElement(struct, "abscTravCrete").text = prof_seuil['x'][i]
        #             SubElement(struct, "cotesCrete").text = prof_seuil['z'][i]
        #
        #         except:
        #             msg = 'Profil de crete introuvable pour {}'
        #             QMessageBox.warning(None, 'Message', msg.format(nom))
        #             return
        #
        #     SubElement(struct, "gradient").text = "-0"

    def main(self):
        struct_dico = self.parent.get_struct()
        for id_config in struct_dico:
            dico_st = struct_dico[id_config]
            if dico_st["active"]:
                if dico_st['idmethod'] == 0 or dico_st['idmethod'] == 1:
                    listf = self.bradley(method=dico_st['method'])
                    self.parent.save_law_st(dico_st, id_config, listf)
                    self.write_law()
                elif dico_st['idmethod'] == 2:
                    pass
