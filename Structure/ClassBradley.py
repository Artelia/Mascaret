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
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from shapely.geometry import *
# from ..Function  import interp
import numpy as np


class ClassBradley:

    def __init__(self, parent):
        self.parent=parent
        self.mgis=self.parent.mgis
        self.mdb = self.parent.mdb
        self.grav=9.81
        self.DEBUG=True
        self.epsi=0.0001
        self.nam_abc={}

    def poly_profil(self, profil):
        """ creation profile polygone """

        zmax = max(profil['z'])
        zmax = zmax +self.epsi
        x0_p= profil['x'][0]
        z0_p= profil['z'][0]
        liste_poly=[[x0_p,zmax],[x0_p,z0_p]]
        for x,z in list(zip(profil['x'],profil['z'])):
            liste_poly.append([x,z])

        liste_poly.append([profil['x'][-1], zmax])
        liste_poly.append([x0_p,zmax])
        poly_p = Polygon(liste_poly)
        return poly_p

    def coup_poly_h(self, poly, cote):
        msg=None
        (minx, miny, maxx, maxy) = poly.bounds
        delpoly=Polygon([[minx - 1, cote], [maxx + 1, cote],
                         [maxx + 1, maxy + 1], [minx - 1, maxy + 1],
                         [minx - 1, cote]])
        if not delpoly.is_empty:
            polyw=poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg="Error: Wet polygon creation"
        else:
            polyw =GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"


        if self.mgis.DEBUG and msg is not None:
            print(msg)
        return polyw

    def coup_poly_v(self, poly, xo, typ='L'):
        msg = None
        print(xo)
        if  type(xo)==list:
            typ='LR'
        (minx, miny, maxx, maxy) = poly.bounds
        if typ == 'L':
            delpoly = Polygon([[minx - 1, maxy + 1], [xo, maxy + 1],
                               [xo, miny - 1], [minx - 1, miny - 1],
                               [minx - 1, maxy + 1]])
        elif typ == 'R':
            delpoly = Polygon([[xo, maxy + 1], [maxx + 1, maxy + 1],
                               [maxx + 1, miny - 1], [xo, miny - 1],
                               [xo, maxy + 1]])
        elif typ == 'LR':
            delpoly = Polygon([[minx - 1, maxy + 1], [xo[0], maxy + 1],
                               [xo[0], miny - 1], [minx - 1, miny - 1],
                               [minx - 1, maxy + 1]])

            delpolyR =  Polygon([[xo[1], maxy + 1], [maxx + 1, maxy + 1],
                               [maxx + 1, miny - 1], [xo[1], miny - 1],
                               [xo[1], maxy + 1]])
        else:
            delpoly = GeometryCollection()
        if not delpoly.is_empty:
            polyw = poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"
        else:
            polyw = GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"

        if typ == 'LR' and not polyw.is_empty:
            polyw = polyw.difference(delpolyR)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"

        if self.mgis.DEBUG and msg is not None:
            print(msg)
        return polyw

    def calc_kb(self,coefm,):
        pass

    def check_coefm(self,coefm):
        cond = True
        msg ='The following coeficients leave application domain :\n'
        if coefm < 0.45:
            msg+= '\t - Kp coeficient\n'
            cond = False
        if coefm <0.3:
            msg += '\t - Kb coeficient\n'
            cond = False
        if coefm < 0.2 or coefm>1:
            msg += '\t - Ke coeficient\n'
            cond = False
        if coefm < 0.3 or coefm > 1:
            msg += '\t - Ks coeficient\n'
            cond = False
        if not cond:
            print(msg)
        return cond

    def get_abac(self,list_recup):
        """get abac"""
        name_abac=[]
        table='struct_abac'
        for metho in list_recup:
            where = "nam_method = '{0}' ".format(metho)
            list_nam=self.mdb.select_distinct("nam_abac", table, where)['nam_abac']
            name_abac+=list_nam
            for nam_abc in   list_nam:
                sql = "SELECT DISTINCT var FROM {}.{} WHERE nam_method='{}' and nam_abac='{}';".format(
                    self.mdb.SCHEMA, table, metho, nam_abc)

                list_var = self.mdb.run_query(sql, fetch=True, namvar=False)
                self.nam_abc[nam_abc]={}
                for var in list_var:
                    self.nam_abc[nam_abc][var[0]]=[]

                sql="SELECT  var,value FROM {}.{} WHERE nam_method='{}' and nam_abac='{}' ORDER by id_order ;".format(self.mdb.SCHEMA,table,metho,nam_abc)
                rows = self.mdb.run_query(sql, fetch=True, namvar=False)
                for row in rows:
                    self.nam_abc[nam_abc][row[0]].append(row[1])

        # return param_elem

    def bradley(self,        methode = 'Bradley 72'):
        pas_h = 0.1
        pas_Q = 10
        bornQ=[10,1000]

        # if  self.parent.checkprofil(self.parent.id_config):
        #     profil = self.parent.get_profil(self.parent.id_config)
        # else:
        #     msg = "Profile copy isn't found"
        #     self.mgis.add_info(msg)
        #     print(msg)
        #     return
        # self.parent.get_param_g(self, list_recup)
        self.dico_name_abac={'Bradley 78':
                            {'abac':['bradley','bradley78']},
                         'Bradley 72':
                             {'abac': ['bradley', 'bradley72']}
                             }
        self.get_abac(self.dico_name_abac[methode]['abac'])
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
        list_poly_pil=[Polygon([[44,6.5],[44,18.45],[45.50,18.45],[45.50,6.5],[44,6.5]]),
                       Polygon([[85.5, 6.5], [85.5, 18.45], [87, 18.45], [87, 6.5], [85.5, 6.5]]),
                       Polygon([[127, 14], [127, 18.45], [128.50, 18.45], [128.50, 14], [127, 14]])]

        self.param_pil={}
        self.param_g = {}
        self.param_g['BIAIOUV'] = 5
        self.param_g['NBTRAV'] = 4
        self.param_g['firstw'] =4
        self.param_g['TOTALOUV'] = 140.0 # ouverture traver
        self.param_g['TOTALW'] = 144.5
        self.param_g['ALPHA1'] = 1
        self.param_g['ALPHA2'] = 1
        self.param_g['FORMCUL']=1
        self.param_g['ORIENTM'] = 30 #30 45 60
        self.param_g['PENTTAL'] =0

        # bradley considere une forme de pile
        self.param_pil['LARG'] = 1.5
        self.param_pil['LONG'] = 11
        self.param_pil['FORMPIL']=5 # ATTENTION 1 seul Type de pil est permit dans la formulation et commence par 1



        list_hn=[8.85]
        list_q= [100]
    #*****************************************
        poly_p=self.poly_profil(profil)
        (minx, miny, maxx, maxy) = poly_p.bounds
        # list_hn = list(np.arange(miny, maxy, pas_h))
        # list_q = list(np.arange(bornQ[0],bornQ[1], pas_Q))

        self.param_g['BIAIOUV']= self.param_g['BIAIOUV']/180.*m.pi # rad
        self.param_g['NBPIL']=self.param_g['NBTRAV']-1
        list_final=[]
        # Test
        for hn in list_hn:
            for q in list_q:
                area_pil=0
                area_pil_proj = 0
                poly_wet = self.coup_poly_h(poly_p, hn)
                area_wet = poly_wet.area
                print('area_wet',area_wet)
                umoy=q/area_wet
                for  poly_pil in list_poly_pil:
                    poly_pil= self.coup_poly_h(poly_pil, hn)
                    if self.param_g['BIAIOUV'] != 0:
                        area_pil_proj += poly_pil.area * \
                                        (self.param_pil['LONG'] * m.sin(self.param_g['BIAIOUV']) +
                                         self.param_pil['LARG'] * m.cos(self.param_g['BIAIOUV'])) \
                                        / self.param_pil['LARG']
                    area_pil +=poly_pil.area
                if area_pil_proj==0:
                    area_pil_proj=area_pil

                ssoh=self.coup_poly_v(poly_wet,[self.param_g['firstw'],self.param_g['TOTALW']],typ='LR').area
                q1 =ssoh *umoy
                q2 = self.coup_poly_v(poly_wet,self.param_g['firstw'],typ='R').area*umoy
                q3 = self.coup_poly_v(poly_wet,self.param_g['TOTALW'],typ='L' ).area*umoy
                coefm=q1/(q1+q2+q3)
                print('q1,q2,q3',q1,q2,q3)
                print('area q1, area q2,area q3', ssoh, self.coup_poly_v(poly_wet,self.param_g['firstw'],typ='R').area, self.coup_poly_v(poly_wet,self.param_g['TOTALW'],typ='L' ).area)
                self.check_coefm(coefm)
                print('coefm',coefm)
                s1=ssoh-area_pil_proj
                print('S1',s1)
                va=q/s1
                print('Va', va)
                # *************** kb
                if methode=='Bradley 78':
                    if self.param_g['TOTALOUV']>60 and self.param_g['FORMCUL']==1:
                        list_inter=self.nam_abc["kb_abac"]['Others']
                    else:
                        list_inter = self.nam_abc["kb_abac"]['type1<60m']
                    kb = np.interp(coefm, self.nam_abc["kb_abac"]['M'],list_inter )
                    print('kb',kb)
                elif  methode=='Bradley 72':
                    print(self.nam_abc["kb_abac"])
                    if self.param_g['FORMCUL']==1:
                        list_inter = self.nam_abc["kb_abac"]['type1']
                    elif self.param_g['FORMCUL']==2:
                        if self.param_g['ORIENTM']==30:
                            list_inter = self.nam_abc["kb_abac"]['type2_30deg']
                        else:
                            list_inter = self.nam_abc["kb_abac"]['type2_45to60deg']
                    elif self.param_g['FORMCUL'] == 3:
                        if self.param_g['PENTTAL'] == 0:
                            list_inter = self.nam_abc["kb_abac"]['type3_1:1']
                        elif self.param_g['PENTTAL'] == 1:
                            list_inter = self.nam_abc["kb_abac"]['type3_1.5:1']
                        else:
                            list_inter = self.nam_abc["kb_abac"]['type3_2:1']
                    else:
                        # defaut 1
                        list_inter = self.nam_abc["kb_abac"]['type1']

                    kb = np.interp(coefm, self.nam_abc["kb_abac"]['M'], list_inter)
                else:
                    kb=0

                #*************** Dkp
                print(area_pil_proj,ssoh,area_pil)
                j=area_pil_proj/ssoh
                print('j',j)


                dkp = np.interp(j, self.nam_abc['DKp_abac']['J'],self.nam_abc['DKp_abac'][str(self.param_pil['FORMPIL'])])
                print('Dkp', dkp)
                coefs = np.interp(coefm, self.nam_abc['s_abac']['M'],self.nam_abc['s_abac'][str(self.param_pil['FORMPIL'])])
                print('s', coefs)
                dkp=dkp*coefs
                print('sDkp',dkp)

                if q3< q2:
                    e_calc = 1 - q3 / q2
                elif q2<q3:
                    e_calc = 1 - q2 / q3
                else:
                    e_calc = 0
                list_e=[]
                for key in self.nam_abc['dKe_abac'].keys():
                    if key !='M':
                        list_e.append((key,float(key.split('=')[1])))
                list_e=sorted(list_e)

                list_m_interp = []
                list_e_interp =[]
                for ee in list_e:
                    list_m_interp.append(np.interp(coefm, self.nam_abc['dKe_abac']['M'],self.nam_abc['dKe_abac'][ee[0]]))
                    list_e_interp.append(ee[1])

                dke=np.interp(e_calc,list_e_interp, list_m_interp)
                print('dke', dke)

                if self.param_g['BIAIOUV']=='0':
                    abac_dks = "dKs_casA_abac"
                else:
                     abac_dks = "dKs_casB_abac"
                if self.param_g['BIAIOUV'] == 0 :
                    dks=0
                else:
                    if self.param_g['BIAIOUV'] > 45:
                        dkx=np.interp(coefm, self.nam_abc[abac_dks]['M'], self.nam_abc[abac_dks]['phi>45'])
                    else:
                        list_ph = []
                        for key in self.nam_abc[abac_dks].keys():
                            if key != 'M' and key != 'phi>45':
                                list_ph.append((key, float(key.split('=')[1])))
                        list_ph = sorted(list_ph)

                        list_m_interp = []
                        list_ph_interp = []
                        for ph in list_ph:
                            list_m_interp.append(
                                np.interp(coefm, self.nam_abc[abac_dks]['M'], self.nam_abc[abac_dks][ph[0]]))
                            list_ph_interp.append(ph[1])
                        dksx = np.interp(self.param_g['BIAIOUV'],list_ph_interp, list_m_interp)

                    if dksx>0:
                        dks=dksx
                    else:
                        dks=0
                print("dks",dks)

                term1=(kb+dkp+dke+dks)*va**2/(2.*self.grav)*self.param_g['ALPHA2']
                print("term1 Remout",term1)
                hmon=hn+term1
                poly_wet = self.coup_poly_h(poly_p, hmon)
                area_amont= poly_wet.area
                term2 = self.param_g['ALPHA1']*((s1/area_wet)**2 - (s1/area_amont)**2 )*va**2 /(2.*self.grav)
                print("term2 Remout", term2)
                remout=term1+term2
                print("Remout Total", remout)
                list_final.append([hn,q,hn+remout])