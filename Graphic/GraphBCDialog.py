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


class GraphBCDialog(QDialog):
    def __init__(self, mgis, param):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.param = param
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_visu_law.ui'),self)
        self.init_gui()


    def init_gui(self):

        self.wdgt_law = GraphBCLaw(self.mgis, self.param)
        id_law = self.tabWidget.addTab(self.wdgt_law, 'Laws')
        condition = """geom_obj='{0}' and active""".format(self.param['name'])
        rows = self.mdb.select('law_config', condition)

        self.wdgt_obs = GraphBCObs(self.mgis, self.param)
        id_obs = self.tabWidget.addTab(self.wdgt_obs, 'Observations')

        if len(rows['id']) == 0:
            self.tabWidget.setTabEnabled(id_law, False)
            self.tabWidget.setTabOrder(self.wdgt_obs, self.wdgt_law)

        if str(self.param['method']) in ('NULL', '') :
            self.tabWidget.setTabEnabled(id_obs, False)
            self.tabWidget.setTabOrder(self.wdgt_law, self.wdgt_obs)

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
        self.bg_abs = QButtonGroup()
        self.bg_abs.addButton(self.rb_abs_q, 0)
        self.bg_abs.addButton(self.rb_abs_z, 1)
        self.rb_abs_q.click()
        self.fram_absweirs.hide()

        self.graph_obj = GraphHydroLaw(self.mgis, self.lay_graph_home)

        self.bg_abs.buttonClicked[int].connect(self.chg_abs_weir_zam)

        self.init_event_changed()

        self.cb_event.currentIndexChanged.connect(self.event_changed)
        self.cb_law.currentIndexChanged.connect(self.law_changed)



    def init_event_changed(self):
        """
        Initialize combobox on events
        :return:
        """
        self.cur_event = None
        list_event = self.mdb.select('events',where ='run',order='starttime')
        self.events = {}
        self.cb_event.clear()
        if len(list_event['name']) >0 :
            for id, name in enumerate(list_event['name']):
                condition = """geom_obj='{0}'
                                            AND starttime <= '{1:%Y-%m-%d %H:%M}'
                                            AND endtime >= '{2:%Y-%m-%d %H:%M}'
                                            AND active""".format(
                    self.param['name'],
                    list_event['starttime'][id],
                    list_event['endtime'][id])
                rows = self.mdb.select('law_config', condition)
                if len(rows['id']) > 0:
                    self.cb_event.addItem(name, name)
                    self.events[name] = {'starttime': list_event['starttime'][id],
                                      'endtime': list_event['endtime'][id],}
        self.cb_event.addItem('only law', None)
        self.cur_event =  self.cb_event.currentData()

        self.update_law_change()



    def update_law_change(self):
        """
        Initialize combobox on law
        :return:
        """
        self.cb_law.clear()
        if self.cur_event != None  :
            condition = """geom_obj='{0}'
                            AND starttime <= '{1:%Y-%m-%d %H:%M}'
                            AND endtime >= '{2:%Y-%m-%d %H:%M}'
                            AND active""".format(self.param['name'],
                                       self.events[self.cur_event]['starttime'],
                                       self.events[self.cur_event]['endtime'])
        else:
            #condition = """geom_obj='{0}' AND active""".format(self.param['name'])
            condition = """geom_obj='{0}' AND active""".format(
                self.param['name'])

        rows = self.mdb.select('law_config',condition)
        self.laws = {}
        if len(rows['id'])>0:
            for i,id in enumerate(rows['id']) :
                self.cb_law.addItem(rows['name'][i], id)
                self.laws[id] = { 'starttime': rows['starttime'][i],
                                  'endtime': rows['endtime'][i],
                                  'type': rows['id_law_type'][i],
                                  'name' : rows['name'][i],
                                  'active': rows['active'][i]
                }
            self.cur_law =  self.cb_law.currentData()


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
            if typ_law != 6:
                date_ref = None
                if param_law['xIsTime']:
                    if self.cur_event != None :
                        date_ref = self.laws[id_law]['starttime']

                self.graph_obj.initCurv(typ_law, param_law, date_ref)
                self.graph_obj.initGraph(id_law, date_ref)
                self.fram_absweirs.hide()
            else:
                self.fram_absweirs.show()
                self.graph_obj.initCurvWeirZam(param_law, id_law,
                                               var_x=self.bg_abs.checkedId())
                self.graph_obj.initGraphWeirZam(id_law)
        else:
            self.graph_obj.initCurv()

    def chg_abs_weir_zam(self, v):
        """
        Change absissa for the graph
        :param v:
        :return:
        """
        self.update_data()


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
        self.display_obs = False
        self.cb_law.hide()
        self.fram_absweirs.hide()

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
        if str(self.param['method']) not in ('NULL', '') :
            self.init_event_changed()
            self.cb_event.currentIndexChanged.connect(self.event_changed)


    def init_event_changed(self):
        """
        Initialize combobox on events
        :return:
        """
        self.cur_event =  None
        list_event = self.mdb.select('events', where='run', order='starttime')
        self.events = {}
        self.cb_event.clear()

        if len(list_event['name']) > 0:
            for id, name in enumerate(list_event['name']):
                self.cb_event.addItem(name, name)
                self.events[name] = {'starttime': list_event['starttime'][id],
                                     'endtime': list_event['endtime'][id], }
            self.cur_event = self.cb_event.currentData()
        else:
            self.cb_event.addItem("No events", None)
            self.cur_event = None
            self.cb_event.setEnabled(False)

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
                if self.cur_event:
                    condition = """code ='{0}'
                                AND type = '{1}'
                                AND date >= '{2:%Y-%m-%d %H:%M}'
                                AND date <= '{3:%Y-%m-%d %H:%M}'
                                """.format(cd_hydro,
                                           type,
                                           self.events[self.cur_event]['starttime'] + dt,
                                           self.events[self.cur_event]['endtime'] + dt)
                else:
                    condition = """code ='{0}'
                                  AND type = '{1}'""".format(cd_hydro,type)

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

