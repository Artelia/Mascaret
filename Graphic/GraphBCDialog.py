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
        # self.tabWidget.addTab(self.wdgt_law,
        #                      'Laws')

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
        self.cur_event =  None
        self.cur_law = None


        self.graph_obj = GraphBC(self, self.lay_graph_home)
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
        if self.cur_event :
            condition = """geom_obj='{0}'
                            AND starttime <= '{1:%Y-%m-%d %H:%M}'
                            AND endtime >= '{2:%Y-%m-%d %H:%M}'
                            AND active""".format(self.param['name'],
                                       self.events[self.cur_event]['starttime'],
                                       self.events[self.cur_event]['endtime'])
        else:
            condition = """geom_obj='{0}' AND active""".format(self.param['name'])

        rows = self.mdb.select('law_config',condition, verbose=True)
        self.laws = {}
        if len(rows['id']):
            for i,id in enumerate(rows['id']) :
                self.cb_law.addItem(rows['name'][i], id)
            self.cur_law =  self.cb_law.currentData()
        else:
            self.cur_law = None

        self.update_data()


    def event_changed(self) :
        self.cur_event = self.cb_event.currentData()
        self.update_law_change()


    def law_changed(self) :
        pass

    def update_data(self):
        pass


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

        self.graph_obj = GraphBC(self, self.lay_graph_home)
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

        self.cur_vars = [type]
        lst_colors = ['black']
        self.cur_vars_lbl = [type]

        self.graph_obj.init_mdl(self.cur_vars, self.cur_vars_lbl,
                                lst_colors, [0], [1], 'm')

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

            self.graph_obj.init_graph_obs(data)
        else:
            self.graph_obj.main_axe.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clear()


