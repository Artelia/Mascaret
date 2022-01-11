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

"""

import os
import re
import datetime
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .GraphBC import GraphBC
from .GraphHydro import GraphHydroLaw

from ..HydroLawsDialog import dico_typ_law

#
# dico_typ_law = {1: {'name': 'Hydrograph Q(t)',
#                     'var': [{'name': 'time', 'code': 'time'},
#                             {'name': 'flowrate', 'code': 'flowrate'}],
#                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
#                               'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
#                     'geom': {'extremities': [1], 'weirs': False,
#                              'lateral_inflows': True, 'lateral_weirs': False},
#                     'xIsTime': True},
#                 2: {'name': 'Limnigraph Z(t)',
#                     'var': [{'name': 'time', 'code': 'time'},
#                             {'name': 'level', 'code': 'z'}],
#                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
#                               'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
#                     'geom': {'extremities': [2], 'weirs': [5],
#                              'lateral_inflows': False, 'lateral_weirs': False},
#                     'xIsTime': True},
#                 3: {'name': 'Limnihydrograph Z,Q(t)',
#                     'var': [{'name': 'time', 'code': 'time'},
#                             {'name': 'level', 'code': 'z'},
#                             {'name': 'flowrate', 'code': 'flowrate'}],
#                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
#                               'y': {'var': [1, 2], 'tit': 'Various',
#                                     'unit': ''}},
#                     'geom': {'extremities': [8], 'weirs': False,
#                              'lateral_inflows': False, 'lateral_weirs': False},
#                     'xIsTime': True},
#                 4: {'name': 'Rating Curve Z = f(Q)',
#                     'var': [{'name': 'flowrate', 'code': 'flowrate'},
#                             {'name': 'level', 'code': 'z'}],
#                     'graph': {'x': {'var': 0, 'tit': 'Q', 'unit': 'm3/s'},
#                               'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
#                     'geom': {'extremities': [3, 5], 'weirs': [2],
#                              'lateral_inflows': False, 'lateral_weirs': [2]},
#                     'xIsTime': False},
#                 5: {'name': 'Rating Curve Q = f(Z)',
#                     'var': [{'name': 'level', 'code': 'z'},
#                             {'name': 'flowrate', 'code': 'flowrate'}],
#                     'graph': {'x': {'var': 0, 'tit': 'Z', 'unit': 'm'},
#                               'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
#                     'geom': {'extremities': [4], 'weirs': [6, 7],
#                              'lateral_inflows': False, 'lateral_weirs': False},
#                     'xIsTime': False},
#                 6: {'name': 'Weir Zam = f(Q, Zav)',
#                     'var': [
#                         {'name': 'flowrate', 'code': 'flowrate', 'leg': 'Q'},
#                         {'name': 'downstream level', 'code': 'z_downstream',
#                          'leg': 'Zdown'},
#                         {'name': 'upstream level', 'code': 'z_upstream'}],
#                     'graph': {'x': {'var': None, 'tit': None, 'unit': None},
#                               'y': {'var': [2], 'tit': 'Zup', 'unit': 'm'}},
#                     'geom': {'extremities': [0, 6], 'weirs': [1],
#                              'lateral_inflows': False, 'lateral_weirs': False},
#                     'xIsTime': False},
#                 7: {'name': 'Floodgate Zinf, Zsup = f(t)',
#                     'var': [{'name': 'time', 'code': 'time'},
#                             {'name': 'lower level', 'code': 'z_lower'},
#                             {'name': 'upper level', 'code': 'z_up'}],
#
#                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
#                               'y': {'var': [1, 2], 'tit': 'Z', 'unit': 'm'}},
#                     'geom': {'extremities': [7], 'weirs': [8],
#                              'lateral_inflows': False, 'lateral_weirs': False},
#                     'xIsTime': True}
#                 }



class GraphBCDialog(QWidget):
    def __init__(self, mgis, param):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.param = param
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_visu_law.ui'),self)
        self.init_gui()


    def init_gui(self):

        print(self.param)
        self.wdgt_law = GraphBCLaw(self.mgis, self.param)
        self.tabWidget.addTab(self.wdgt_law,
                             'Laws')

        self.wdgt_obs = GraphBCObs(self.mgis, self.param)
        self.tabWidget.addTab(self.wdgt_obs,
                               'Observations')
        # print(feature.fieldNameIndex('name'))


class GraphBCLaw(QWidget):
    def __init__(self, mgis, param):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.param = param
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_wdget_bc.ui'),self)
        self.initialising = True
        self.events = {}
        self.laws = {}
        self.cur_event =  None
        self.cur_law = None

        self.graph_obj = GraphHydroLaw(self.mgis, self.lay_graph_home)
        self.init_event_changed()

        self.cb_event.currentIndexChanged.connect(self.event_changed)
        self.cb_law.currentIndexChanged.connect(self.law_changed)

    def init_event_changed(self):
        """
        Initialize combobox on events
        :return:
        """
        list_event = self.mdb.select('events',where ='run',order='starttime')
        self.events = {}
        self.cb_event.clear()
        if len(list_event['name']) >0 :
            for id, name in enumerate(list_event['name']):
                self.cb_event.addItem(name, name)
                self.events[name] = {'starttime': list_event['starttime'][id],
                                  'endtime': list_event['endtime'][id],}
        self.cb_event.addItem('only law', None)
        self.cur_event =  self.cb_event.currentText()
        self.update_law_change()


    def update_law_change(self):
        """
        Initialize combobox on law
        :return:
        """
        self.cb_law.clear()
        if self.cur_event != None :
            condition = """geom_obj='{0}'
                            AND starttime <= '{1:%Y-%m-%d %H:%M}'
                            AND endtime >= '{2:%Y-%m-%d %H:%M}'
                            AND active""".format(self.param['name'],
                                       self.events[self.cur_event]['starttime'],
                                       self.events[self.cur_event]['endtime'])
        else:
            #condition = """geom_obj='{0}' AND active""".format(self.param['name'])
            condition = """geom_obj='{0}'""".format(
                self.param['name'])

        rows = self.mdb.select('law_config',condition, verbose=True)
        print()
        self.laws = {}
        if len(rows['id']):
            for i,id in enumerate(rows['id']) :
                self.cb_law.addItem(rows['name'][i], id)
                self.laws[id] = { 'starttime': rows['starttime'][i],
                                  'endtime': rows['endtime'][i],
                                  'type': rows['id_law_type'][i],
                                  'name' : rows['name'][i],
                                  'active': rows['active'][i]
                }
            self.cur_law =  self.cb_law.currentData()
            print(self.laws)
        else:
            self.cur_law = None

        self.update_data()


    def event_changed(self) :
        self.cur_event = self.cb_event.currentData()
        self.update_law_change()


    def law_changed(self) :
        self.cur_law = self.cb_law.currentData()
        self.update_data()

    def update_data(self):
        """
        display graph
        :return:
        """
        if self.cur_law != None and self.cur_law in self.laws.keys() :
            id_law = self.cur_law
            typ_law = self.laws[id_law]['type']
            param_law = dico_typ_law[typ_law]
            #graph_opt = self.cb_graph_opt.currentData()

            if typ_law != 6:
                date_ref = None
                if param_law['xIsTime']:
                    if self.cur_event != None :
                        date_ref = self.laws[id_law]['starttime']

                self.graph_obj.initCurv(typ_law, param_law, date_ref)
                self.graph_obj.initGraph(id_law, date_ref)
            else:
                self.graph_obj.initCurvWeirZam(param_law, id_law,
                                                graph_opt)
                self.graph_obj.initGraphWeirZam(id_law)
        else:
            self.graph_obj.initCurv()

        # # event
        # if self.cur_event :
        #     values = self.mdb.select("law_values",
        #                              where='id_law={}'.format(self.cur_law),
        #                              order='id_var, id_order',
        #                              list_var=['id_var',
        #                                        'id_order',
        #                                        'value'])
        #
        #     lst_var = [tmp['code'] for tmp in dico_typ_law[typ_law]['var']]
        #     lst_idvar = [id for id, tmp in
        #                  enumerate(dico_typ_law[typ_law]['var'])]
        #
        #     tab = {key: [] for key in lst_var}
        #     conv_idvar = {id: lst_var[i] for i, id in enumerate(lst_idvar)}
        #
        #     for value, id_var in zip(values['value'], values['id_var']):
        #         tab[conv_idvar[id_var]].append(float(value))


        # for nom, loi in dict_lois.items():
        #     if loi['type'] in (1, 2):
        #         continue
        #     tab = self.get_laws(nom, loi['type'],
        #                         obs=True, date_deb=date_debut,
        #                         date_fin=date_fin)

        # loi
        # for nom, l in dict_lois.items():
        #     if "valeurperm" not in l.keys():
        #         continue
        #     if l["valeurperm"] is None:
        #         # dictLois.items() extremities liste
        #
        #         tab = self.get_laws(nom, l["type"])
        #         if tab:
        #             self.creer_loi(nom, tab, l["type"])
        #         else:
        #             self.mgis.add_info(
        #                 'The law for {} is not create.'.format(nom))
        #
        #     else:
        #         try:
        #             liste_ = ['pasTemps', 'critereArret', 'nbPasTemps',
        #                       'tempsMax', 'tempsInit']
        #             temp_dic = {}
        #             for info in liste_:
        #                 condition = "parametre ='{}'".format(info)
        #                 dtemp = self.mdb.select_distinct('steady', 'parametres',
        #                                                  condition)
        #                 temp_dic[info] = dtemp['steady'][0]
        #         except Exception as e:
        #             self.mgis.add_info(str(e))
        #             return
        #         # self.mgis.add_info('{}'.format(condition))
        #         if temp_dic['critereArret'] == 1:
        #             tfinal = temp_dic['tempsMax']
        #         elif temp_dic['critereArret'] == 2:
        #             tfinal = temp_dic['tempsInit'] + temp_dic['pasTemps'] * \
        #                                              temp_dic['nbPasTemps']
        #         elif temp_dic['critereArret'] == 3:
        #             tfinal = 365 * 24 * 3600
        #
        #         condition = "geom_obj='{0}' AND id_law_type={1} AND active".format(
        #             nom, l['type'])
        #         if l['type'] == 1:
        #             tab = {"time": [0, tfinal],
        #                    'flowrate': [l["valeurperm"]] * 2}
        #         # no possible to use rating curve (5) with steady.
        #         #   It's replaced in xcas
        #         elif l['type'] == 2 or l['type'] == 5:
        #             l['type'] = 2
        #             tab = {"time": [0, tfinal], 'z': [l["valeurperm"]] * 2}
        #         else:
        #             tab = self.get_laws(nom, l["type"])
        #
        #         if tab:
        #             self.creer_loi(nom, tab, l["type"])
        #         else:
        #             self.mgis.add_info(
        #                 'The law for {} is not create.'.format(nom))

        # loi 2
        # for nom, l in dict_lois.items():
        #     # dictLois.items() extremities liste
        #
        #     tab = self.get_laws(nom, l["type"])
        #     if tab:
        #         self.creer_loi(nom, tab, l["type"])
        #     else:
        #         self.mgis.add_info(
        #             'The law for {} is not create.'.format(nom))
        #     if self.mgis.DEBUG:
        #         self.mgis.add_info("Laws file is created.")
        #
        #     if "valeurperm" not in l.keys():
        #         continue
        #
        #     # nom = nom + "_init"
        #     if l["valeurperm"] is not None:
        #         if l['type'] == 1:
        #             tab = {"time": [0, 3600], 'flowrate': [l["valeurperm"]] * 2}
        #             self.creer_loi(nom, tab, 1, init=True)
        #         elif l['type'] == 2:
        #             tab = {"time": [0, 3600], 'z': [l["valeurperm"]] * 2}
        #             self.creer_loi(nom, tab, 2, init=True)
        #         elif l['type'] in [4, 5]:
        #             self.creer_loi(nom, tab, l['type'], init=True)
        #         else:
        #
        #             par["initialisationAuto"] = False
        #             self.mgis.add_info("No initialisation")
        #     else:
        #         if l['type'] in [4, 5]:
        #             self.creer_loi(nom, tab, l['type'], init=True)
        #         else:
        #             par["initialisationAuto"] = False
        #             self.mgis.add_info(
        #                 "No initialisation because of no valeurperm "
        #                 "for {} condition".format(nom))


class GraphBCObs(QWidget):
    def __init__(self, mgis, param):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.param = param
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_wdget_bc.ui'),self)
        self.initialising = True
        self.events = {}
        self.cur_event = None
        self.cur_law = None
        self.cb_law.hide()

        self.dico_obs = {
            'H': {'name': 'Limnigraph Z(t)',
                     'var': [{'name': 'time', 'code': 'time'},
                             {'name': 'level', 'code': 'z'}],
                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                               'y': {'var': [1], 'tit': 'Z', 'unit': 'm'}},
                     'xIsTime': True},
            'Q': {'name': 'Hydrograph Q(t)',
                     'var': [{'name': 'time', 'code': 'time'},
                             {'name': 'flowrate', 'code': 'flowrate'}],
                     'graph': {'x': {'var': 0, 'tit': 'time', 'unit': 's'},
                               'y': {'var': [1], 'tit': 'Q', 'unit': 'm3/s'}},
                     'xIsTime': True}, }

        self.graph_obj = GraphHydroLaw(self.mgis, self.lay_graph_home)
        self.init_event_changed()

        self.cb_event.currentIndexChanged.connect(self.event_changed)
        #elf.cb_law.currentIndexChanged.connect(self.law_changed)


    def init_event_changed(self):
        """
        Initialize combobox on events
        :return:
        """
        list_event = self.mdb.select('events', where='run', order='starttime')
        self.events = {}
        self.cb_event.clear()
        if len(list_event['name']) > 0:
            for id, name in enumerate(list_event['name']):
                self.cb_event.addItem(name, name)
                self.events[name] = {'starttime': list_event['starttime'][id],
                                     'endtime': list_event['endtime'][id], }
        self.cur_event = self.cb_event.currentText()
        self.update_data()

    def event_changed(self):
        self.cur_event = self.cb_event.currentData()
        self.update_data()

    def update_data(self):

        # pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        pattern = re.compile('(\w+)\\[t([+-][0-9]+)?\\]')
        obs = {}
        liste_date = []

        if self.param['type'] == 1:
            type = 'Q'
        elif self.param['type'] == 2:
            type = 'H'
        else:
            type= None

        self.graph_obj.initCurv(typ_law=type,
                                param_law=self.dico_obs[type],
                                date_ref=True)

        if type :
            liste_stations = pattern.findall(self.param['method'])
            for cd_hydro, delta in liste_stations:
                if not delta:
                    delta = '0'

                dt = datetime.timedelta(hours=int(delta))

                condition = """code ='{0}'
                            AND type = '{1}'
                            AND date >= '{2:%Y-%m-%d %H:%M}'
                            AND date <= '{3:%Y-%m-%d %H:%M}'
                            """.format(cd_hydro,
                                       type,
                                       self.events[self.cur_event]['starttime'] + dt,
                                       self.events[self.cur_event]['endtime'] + dt)

                obs[cd_hydro] = self.mdb.select('observations',
                                                condition,
                                                'code, date',
                                                list_var=['id', 'valeur','date'])

                if not liste_date:
                    liste_date = [x - dt for x in obs[cd_hydro]['date']]
            resultat =  None
            data = {'date' : [],
                    'val' : []}
            for t in liste_date:
                calc = self.param['method']
                for cd_hydro, delta in liste_stations:
                    if not delta:
                        delta = '0'
                    t2 = t + datetime.timedelta(hours=int(delta))
                    if t2 in obs[cd_hydro]['date']:
                        i = obs[cd_hydro]['date'].index(t2)
                        val = obs[cd_hydro]['valeur'][i]
                    else:
                        val = None
                    calc = pattern.sub(str(val), calc, 1)

                try:
                    resultat = eval(calc)
                except:
                    resultat = None

                data['date'].append(t)
                data['val'].append(resultat)

            self.graph_obj.init_graph_obs(data,self.dico_obs[type])
        else:
            self.graph_obj.initCurv()
    # def display_graph_home(self):
    #     """
    #     display graph
    #     :return:
    #     """
    #     if self.tree_laws.selectedItems():
    #         itm = self.tree_laws.selectedItems()[0]
    #         id_law = itm.data(0, 32)
    #         typ_law = itm.parent().data(0, 32)
    #         param_law = dico_typ_law[typ_law]
    #         graph_opt = self.cb_graph_opt.currentData()
    #
    #         if typ_law != 6:
    #             date_ref = None
    #             if param_law['xIsTime']:
    #                 if graph_opt == 'date':
    #                     date_ref = itm.data(1, 32)
    #
    #             self.graph_home.initCurv(typ_law, param_law, date_ref)
    #             self.graph_home.initGraph(id_law, date_ref)
    #         else:
    #             self.graph_home.initCurvWeirZam(param_law, id_law,
    #                                             graph_opt)
    #             self.graph_home.initGraphWeirZam(id_law)
    #     else:
    #         self.graph_home.initCurv()


