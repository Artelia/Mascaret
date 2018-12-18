# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
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
comment:

"""

import csv
import datetime
import os, sys
import re
import shutil
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as ETparse

from qgis.PyQt.QtCore import qVersion

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .table_WQ import table_WQ
from ..function import str2bool

class class_mascWQ():
    def __init__(self, main, file ):
        """

        :param main: main program
        :param mod: tracer mod
        :param file: repertory Mascaret
        """
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.schema=self.mdb.SCHEMA
        self.iface = self.mgis.iface

        self.tbwq = table_WQ(self.mgis, self.mdb)
        self.dico_phy = self.tbwq.dico_phy
        self.dossierFileMasc=file

        sql = "SELECT {} FROM {}.parametres WHERE parametre = 'modeleQualiteEau'".format('steady',self.schema)
        result = self.mdb.run_query(sql ,fetch=True)

        self.cur_wq_mod =self.tbwq.dico_wq_mod[int(result[0][0])]
        self.cur_wq_mod_int = int(result[0][0])

    def create_filephy(self):
        """creation .phy file """

        where="type = '{}'".format(self.cur_wq_mod)
        order="id"
        result = self.mdb.select('tracer_physic',where,order)
        entetfr=u": NOMBRE DE PARAMETRES PHYSIQUES"
        entet = u": NUMBER OF PHYSICAL PARAMETERS"
        # with open(os.path.join(self.dossierFileMasc, self.cur_wq_mod.lower() + '.phy'), 'w') as fich:
        with open(os.path.join(self.dossierFileMasc, 'mascaret.phy'), 'w') as fich:
            fich.write('{} {}\n'.format(len(self.dico_phy[ self.cur_wq_mod]['physic']),entet))
            for i,phy in enumerate(self.dico_phy[ self.cur_wq_mod]['physic']):
                idx=result['sigle'].index(phy['sigle'])
                fich.write('{} : {}\n'.format(result['value'][idx],result['text'][idx]))

    def law_tracer(self):
        """creation of law file for tracer"""
        extrem = self.mdb.select('extremities')
        lateral = self.mdb.select('tracer_lateral_inflows')
        dict_loi_tr={}
        list_loi=[]

        for i,cond in enumerate(extrem['active']):
            if cond :
                list_loi.append(extrem['law_wq'][i])
                dict_loi_tr[extrem['law_wq'][i]] ={"source":False, 'type':extrem['tracer_boundary_condition_type'][i]}


        for i, cond in enumerate(lateral['active']):
            if cond:
                list_loi.append(lateral['law_wq'][i])
                dict_loi_tr[extrem['law_wq'][i]] = {"source": True,
                                                    'type': lateral['typesources'][i]}

        if list_loi!=[]:
            where="type = '{}'".format(self.cur_wq_mod)
            order="id"
            list_trac = self.mdb.select('tracer_name',where,order)
            for name in list_loi:

                order = "id"
                where = "type = '{}' AND name = '{}'".format(self.cur_wq_mod_int , name)
                loi_trac = self.mdb.select('tracer_config', where, order)
                if loi_trac['id']==[]:
                    self.mgis.addInfo(u"The <<{}>> law doesn't exist. Please check  laws. ".format(name))
                else:
                    order='ORDER BY "time",id_trac'
                    where = "WHERE id_config= '{}' ".format(loi_trac['id'][0])
                    sql="""SELECT DISTINCT id_trac,time,value FROM {0}.{1} {2} {3}"""
                    loi_val,col =self.mdb.run_query(sql.format(self.mdb.SCHEMA, 'laws_wq', where, order),
                                                    fetch=True,namvar=True)
                    #write law
                    fich = open(os.path.join(self.dossierFileMasc, name.lower() + '.loi'), 'w')
                    header='# {}\n'.format(name)
                    header+='# Times (s) '
                    for sigle in list_trac['sigle']:
                        header += 'C_{} '.format(sigle)

                    header+='\n'
                    header+='         S\n'
                    fich.write(header)
                    t_pre=loi_val[0][1]
                    ligne = '{} '.format(t_pre)
                    for id, temps, val in loi_val:
                        if t_pre!=temps:
                            fich.write(ligne+'\n')
                            t_pre = temps
                            ligne = '{} {} '.format(t_pre, val)
                        else:
                            ligne+='{} '.format(val)
                    fich.write(ligne)
                    fich.close()
        return dict_loi_tr


    def init_conc_tracer(self):

        order = "id"
        where = "type = '{}' AND active=true".format(self.cur_wq_mod_int)
        init_trac = self.mdb.select('init_conc_config', where, order)
        if init_trac['id'] == []:
            self.mgis.addInfo("Warning: Please select the initial conditions for tracers")
            return
        order = 'ORDER BY bief,abscissa,id_trac'
        where = "WHERE id_config= '{}' ".format(init_trac['id'][0])
        sql = """SELECT DISTINCT id_trac,bief,abscissa,value FROM {0}.{1} {2} {3}"""

        init_val, col = self.mdb.run_query(sql.format(self.mdb.SCHEMA, 'init_conc_wq', where, order),
                                          fetch=True, namvar=True)
        if init_val==[] or init_val ==None:
            self.mgis.addInfo("Warning: Please fill the initial conditions for tracers")
            return
        # fich = open(os.path.join(self.dossierFileMasc, self.cur_wq_mod.lower() + '.conc'), 'w')
        fich = open(os.path.join(self.dossierFileMasc, 'mascaret.conc'), 'w')

        fich.write('[variables]\n')
        for i,var in enumerate(self.dico_phy[self.cur_wq_mod]['tracer']):
            fich.write('"{}";"C{}";"";11\n'.format(var['text'],i))

        fich.write('[resultats]')
        id_pre=init_val[0][1]
        abs_pre =init_val[0][2]
        ligne = ''
        first=True
        for i, val in enumerate(init_val):
            if val[3]==None:
                val[3]=0
            if id_pre != val[1] or abs_pre!=val[2] or first:
                first = False
                fich.write(ligne + '\n')
                id_pre = val[1]
                ligne = '        0.0;"  {}";"   {}";  {};  {};'.format(val[1], i+1, val[2],val[3])
            else:
                ligne += '  {};'.format(val[3])
        fich.write(ligne)
        fich.close()
