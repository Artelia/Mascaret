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
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

"""

import datetime
import os
import re
import numpy as np

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ..Function import filter_xy_by_time_ensur
from .GraphHydro import GraphHydroLaw
from ..HydroLawsDialog import dico_typ_law

QT_VERSION = [int(v) for v in qVersion().split('.')][0]


class GraphBCDialog(QDialog):
    def __init__(self, mgis, param):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.param = param
        self.if_ana = False
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_visu_law.ui"), self)
        self.init_gui()

    def init_gui(self):
        """
        initialize GUI
        :return:
        """

        self.wdgt_obs = GraphBCObs(self.mgis, self.param)
        id_obs = self.tabWidget.addTab(self.wdgt_obs, "Observations")

        self.wdgt_law = GraphBCLaw(self.mgis, self.param)
        id_law = self.tabWidget.addTab(self.wdgt_law, "Laws")

        d_res = self.select_ana_param()
        self.wdgt_assim = GraphBCAssim(self.mgis, self.param, d_res)
        id_assim = self.tabWidget.addTab(self.wdgt_assim, "Assimilation")
        self.tabWidget.setTabEnabled(id_assim, False)

        condition = """geom_obj='{0}' and active""".format(self.param["name"])
        rows = self.mdb.select("law_config", condition)

        if len(rows["id"]) == 0:
            self.tabWidget.setTabEnabled(id_law, False)
            self.tabWidget.setTabEnabled(id_assim, False)
            self.tabWidget.setTabOrder(self.wdgt_obs, self.wdgt_law)

        if str(self.param["method"]) in ("NULL", ""):
            self.tabWidget.setTabEnabled(id_obs, False)
            self.tabWidget.setTabEnabled(id_assim, False)
            self.tabWidget.setTabOrder(self.wdgt_law, self.wdgt_obs)

        if d_res.get('id_run'):
            self.tabWidget.setTabEnabled(id_assim, True)

    def select_ana_param(self):
        sql = f"""
        SELECT
            r.id AS id_run,
            r.run,
            r.scenario,
            a.id_ctrl,
            ar.var,
            ar.val
        FROM
            {self.mdb.SCHEMA}.runs r
        JOIN
            {self.mdb.SCHEMA}.assim_res_law a
                ON r.id = a.id_runs
        LEFT JOIN
            {self.mdb.SCHEMA}.assim_res ar
                ON ar.id_runs = r.id
               AND ar.id_ctrl = a.id_ctrl
        WHERE
            RIGHT(r.scenario, LENGTH('_ana_ctrl_law')) = '_ana_ctrl_law'
            AND a.name_law = '{self.param['name']}'
            AND a.source_law = '{self.param['couche']}'
        ORDER BY
            r.id,
            a.id_ctrl,
            ar.var;
        """
        (results, nam_col) = self.mdb.run_query(
            sql, fetch=True, namvar=True
        )
        if not results:
            return {}
        cols = [col[0] for col in nam_col]
        d_res = {col: [] for col in cols}
        for row in results:
            for idc, col in enumerate(cols):
                d_res[col].append(row[idc])

        return d_res


class GraphBCLaw(QWidget):
    def __init__(self, mgis, param):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.param = param
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_wdget_bc.ui"), self)
        self.initialising = True
        self.events = {}
        self.laws = {}
        self.cur_event = None
        self.cur_law = None

        self.bg_abs = QButtonGroup()
        self.bg_abs.addButton(self.rb_abs_q, 0)
        self.bg_abs.addButton(self.rb_abs_z, 1)
        self.rb_abs_q.click()
        self.fram_absweirs.hide()
        self.cb_run.hide()
        self.graph_obj = GraphHydroLaw(self.mgis, self.lay_graph_home)

        self.bg_abs.buttonClicked.connect(self.chg_abs_weir_zam)

        self.init_event_changed()

        self.cb_event.currentIndexChanged.connect(self.event_changed)
        self.cb_law.currentIndexChanged.connect(self.law_changed)

    def init_event_changed(self):
        """
        Initialize combobox on events
        :return:
        """
        self.cur_event = None
        list_event = self.mdb.select("events", where="run", order="starttime")
        self.events = {}
        self.cb_event.clear()
        if len(list_event["name"]) > 0:
            for id, name in enumerate(list_event["name"]):
                condition = """geom_obj='{0}'
                                            AND starttime <= '{1:%Y-%m-%d %H:%M}'
                                            AND endtime >= '{2:%Y-%m-%d %H:%M}'
                                            AND active""".format(
                    self.param["name"], list_event["starttime"][id], list_event["endtime"][id]
                )
                rows = self.mdb.select("law_config", condition)
                if len(rows["id"]) > 0:
                    self.cb_event.addItem(name, name)
                    self.events[name] = {
                        "starttime": list_event["starttime"][id],
                        "endtime": list_event["endtime"][id],
                    }
        self.cb_event.addItem("only law", None)
        self.cur_event = self.cb_event.currentData()

        self.update_law_change()

    def update_law_change(self):
        """
        Initialize combobox on law
        :return:
        """
        self.cb_law.clear()
        if self.cur_event is not None:
            condition = """geom_obj='{0}'
                            AND starttime <= '{1:%Y-%m-%d %H:%M}'
                            AND endtime >= '{2:%Y-%m-%d %H:%M}'
                            AND active""".format(
                self.param["name"],
                self.events[self.cur_event]["starttime"],
                self.events[self.cur_event]["endtime"],
            )
        else:
            # condition = """geom_obj='{0}' AND active""".format(self.param['name'])
            condition = """geom_obj='{0}' AND active""".format(self.param["name"])

        rows = self.mdb.select("law_config", condition)
        self.laws = {}
        if len(rows["id"]) > 0:
            for i, id in enumerate(rows["id"]):
                self.cb_law.addItem(rows["name"][i], id)
                self.laws[id] = {
                    "starttime": rows["starttime"][i],
                    "endtime": rows["endtime"][i],
                    "type": rows["id_law_type"][i],
                    "name": rows["name"][i],
                    "active": rows["active"][i],
                }
            self.cur_law = self.cb_law.currentData()

        else:
            self.cur_law = None

        self.update_data()

    def event_changed(self):
        """
        change event combobox
        :return:
        """
        self.cur_event = self.cb_event.currentData()
        self.update_law_change()

    def law_changed(self):
        """
        change law in combobox
        :return:
        """
        self.cur_law = self.cb_law.currentData()
        self.update_data()

    def update_data(self):
        """
        display graph
        :return:
        """
        if self.cur_law is not None and self.cur_law in self.laws.keys():
            id_law = self.cur_law
            typ_law = self.laws[id_law]["type"]
            param_law = dico_typ_law[typ_law]
            if typ_law != 6:
                date_ref = None
                if param_law["xIsTime"]:
                    if self.cur_event is not None:
                        date_ref = self.laws[id_law]["starttime"]

                self.graph_obj.init_curv(typ_law, param_law, date_ref)
                self.graph_obj.init_graph(id_law, date_ref)
                self.fram_absweirs.hide()
            else:
                self.fram_absweirs.show()
                self.graph_obj.init_curv_weir_zam(param_law, id_law, var_x=self.bg_abs.checkedId())
                self.graph_obj.init_graph_weir_zam(id_law)
        else:
            self.graph_obj.init_curv()

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
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_wdget_bc.ui"), self)
        self.initialising = True
        self.events = {}
        self.cur_event = None
        self.cur_law = None
        self.display_obs = False
        self.cb_law.hide()
        self.cb_run.hide()
        self.fram_absweirs.hide()

        self.dico_obs = {
            "H": {
                "name": "Limnigraph Z(t)",
                "var": [{"name": "time", "code": "time"}, {"name": "level", "code": "z"}],
                "graph": {
                    "x": {"var": 0, "tit": "time", "unit": "s"},
                    "y": {"var": [1], "tit": "Z", "unit": "m"},
                },
                "xIsTime": True,
            },
            "Q": {
                "name": "Hydrograph Q(t)",
                "var": [{"name": "time", "code": "time"}, {"name": "flowrate", "code": "flowrate"}],
                "graph": {
                    "x": {"var": 0, "tit": "time", "unit": "s"},
                    "y": {"var": [1], "tit": "Q", "unit": "m3/s"},
                },
                "xIsTime": True,
            },
        }

        self.graph_obj = GraphHydroLaw(self.mgis, self.lay_graph_home)
        if str(self.param["method"]) not in ("NULL", ""):
            self.init_event_changed()
            self.cb_event.currentIndexChanged.connect(self.event_changed)

    def init_event_changed(self):
        """
        Initialize combobox on events
        :return:
        """
        self.cur_event = None
        list_event = self.mdb.select("events", where="run", order="starttime")
        self.events = {}
        self.cb_event.clear()

        if len(list_event["name"]) > 0:
            for id, name in enumerate(list_event["name"]):
                self.cb_event.addItem(name, name)
                self.events[name] = {
                    "starttime": list_event["starttime"][id],
                    "endtime": list_event["endtime"][id],
                }
            self.cur_event = self.cb_event.currentData()
        else:
            self.cb_event.addItem("No events", None)
            self.cur_event = None
            self.cb_event.setEnabled(False)

        self.update_data()

    def event_changed(self):
        """
        change event combobox
        :return:
        """
        self.cur_event = self.cb_event.currentData()
        self.update_data()

    def update_data(self):
        """
        update data
        :return:
        """

        # pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        # pattern = re.compile(r"(\w+)\\[t([+-][0-9]+)?\\]")
        pattern = re.compile(r"(\w+)\[t([+-]?\d+)?\]")
        obs = {}
        liste_date = []

        if self.param["type"] == 1:
            type = "Q"
        elif self.param["type"] == 2:
            type = "H"
        else:
            type = None

        self.graph_obj.init_curv(typ_law=type, param_law=self.dico_obs[type], date_ref=True)

        if type and self.param["method"]:
            liste_stations = pattern.findall(self.param["method"])

            for cd_hydro, delta in liste_stations:
                if not delta:
                    delta = "0"

                dt = datetime.timedelta(hours=int(delta))
                if self.cur_event:
                    sql_query = (
                        "SELECT date, valeur FROM (SELECT code,type, UNNEST(date) as date, "
                        "UNNEST(valeur) as valeur FROM {4}.observations "
                        "WHERE code = '{0}' AND type='{3}') t "
                        " WHERE date>='{1}' AND date<='{2}' AND valeur > -999.9 "
                        "ORDER BY date".format(
                            cd_hydro, self.events[self.cur_event]["starttime"] + dt,
                                      self.events[self.cur_event]["endtime"] + dt,
                            type, self.mdb.SCHEMA
                        )
                    )

                else:
                    sql_query = """SELECT  id, UNNEST(date) as date, 
                                UNNEST(valeur) as valeur  FROM  {2}.observations 
                                WHERE code ='{0}'AND type = '{1}'
                                ORDER BY code, date;""".format(
                        cd_hydro, type, self.mdb.SCHEMA
                    )
                obs[cd_hydro] = self.mdb.query_todico(sql_query, verbose=False)

                if not liste_date:
                    liste_date = [x - dt for x in obs[cd_hydro]["date"]]
            resultat = None
            data = {"date": [], "val": []}
            for t in liste_date:
                calc = self.param["method"]
                for cd_hydro, delta in liste_stations:
                    if not delta:
                        delta = "0"
                    t2 = t + datetime.timedelta(hours=int(delta))
                    if t2 in obs[cd_hydro]["date"]:
                        i = obs[cd_hydro]["date"].index(t2)
                        val = obs[cd_hydro]["valeur"][i]
                    else:
                        val = None
                    calc = pattern.sub(str(val), calc, 1)

                try:
                    resultat = eval(calc)
                except:
                    resultat = None

                data["date"].append(t)
                data["val"].append(resultat)
            self.graph_obj.init_graph_obs(data, self.dico_obs[type])
        else:
            self.graph_obj.init_curv()


#
class GraphBCAssim(QWidget):
    def __init__(self, mgis, param, assim_info):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.param = param
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_wdget_bc.ui"), self)
        if not assim_info:
            return
        self.assim_info = assim_info

        self.initialising = True
        self.events = {}
        self.cur_event = None
        self.cur_law = None
        self.display_obs = False
        self.cb_law.hide()
        self.fram_absweirs.hide()
        #
        self.dico_obs = {
            "H": {
                "name": "Limnigraph Z(t)",
                "var": [{"name": "time", "code": "time"}, {"name": "level", "code": "z"}],
                "graph": {
                    "x": {"var": 0, "tit": "time", "unit": "s"},
                    "y": {"var": [1], "tit": "Z", "unit": "m"},
                },
                "xIsTime": True,
            },
            "Q": {
                "name": "Hydrograph Q(t)",
                "var": [{"name": "time", "code": "time"}, {"name": "flowrate", "code": "flowrate"}],
                "graph": {
                    "x": {"var": 0, "tit": "time", "unit": "s"},
                    "y": {"var": [1], "tit": "Q", "unit": "m3/s"},
                },
                "xIsTime": True,
            },
        }
        self.graph_obj = GraphHydroLaw(self.mgis, self.lay_graph_home)

        condition = """geom_obj='{0}' and active""".format(self.param["name"])
        rows = self.mdb.select("law_config", condition)
        self.if_law = bool(str(self.param["method"]) in ("NULL", "") and len(rows["id"]) != 0)

        self.init_run_changed()
        self.init_event_changed()
        self.cb_run.currentIndexChanged.connect(self.run_changed)
        self.cb_event.currentIndexChanged.connect(self.event_changed)

    #
    def init_run_changed(self):
        self.cur_run = None

        self.cb_run.clear()
        list_run = list(set(self.assim_info.get('run', [])))
        if list_run:
            for name in list_run:
                self.cb_run.addItem(name, name)
        else:
            self.cb_run.addItem("No run", None)
        self.cur_run = self.cb_run.currentData()

    def find_coef(self,name_ctrl):
        if self.cur_run is None:
            return 1, 0
        resultats = {
            self.assim_info['var'][i] : self.assim_info['val'][i]
            for i in range(len(self.assim_info['run']))
            if self.assim_info['run'][i] == self.cur_run and self.assim_info['scenario'][i] == name_ctrl
        }
        val_min = resultats.get('coefA_val_min', None)
        val_max = resultats.get('coefA_val_max', None)
        if not val_max:
            val_max = resultats.get('coefB_val_max', None)
        if not val_min:
            val_min = resultats.get('coefB_val_min', None)

        return resultats.get('coefA', 1), resultats.get('coefB', 0), val_min, val_max

    def init_event_changed(self):
        """
        Initialize combobox on events
        :return:
        """
        self.cur_event = None
        self.events = {}
        self.cb_event.blockSignals(True)
        self.cb_event.clear()
        runs = self.assim_info.get('run', [])

        scenarios = [
            self.assim_info["scenario"][i]
            for i, run in enumerate(runs)
            if run == self.cur_run
        ]
        list_scen_str = [f"'{scen.replace('_ana_ctrl_law', '')}'" for scen in list(set(scenarios))]
        list_event = self.mdb.select("events", where=f"name IN ({','.join(list_scen_str)})", order="starttime",
                                     verbose=False)

        if len(list_event["name"]) > 0:
            for id, name in enumerate(list_event["name"]):
                name_ctrl = name + '_ana_ctrl_law'
                self.cb_event.addItem(name_ctrl, name_ctrl)
                id_law= None
                start_time_law= None
                if self.if_law:
                    condition = """geom_obj='{0}'
                                                        AND starttime <= '{1:%Y-%m-%d %H:%M}'
                                                        AND endtime >= '{2:%Y-%m-%d %H:%M}'
                                                        AND active""".format(
                        self.param["name"], list_event["starttime"][id], list_event["endtime"][id]
                    )
                    rows = self.mdb.select("law_config", condition)
                    id_law = rows.get('id', [])
                    if len(id_law) > 0:
                        id_law = id_law[0]
                        start_time_law = rows.get('starttime', [None])[0]

                coefa, coefb, valmin, valmax = self.find_coef(name_ctrl)
                self.events[name_ctrl] = {
                    "starttime": list_event["starttime"][id],
                    "endtime": list_event["endtime"][id],
                    "coefA": coefa,
                    "coefB": coefb,
                    "valmin": valmin,
                    "valmax": valmax,
                    "id_law": id_law,
                    "start_time_law": start_time_law
                }
            self.cur_event = self.cb_event.currentData()

        else:
            self.cb_event.addItem("No events", None)
            self.cur_event = None
            self.cb_event.setEnabled(False)
        self.cb_event.blockSignals(False)
        if self.if_law:
            self.update_data_law()
        else:
            self.update_data_obs()

    def run_changed(self):
        """
        change event combobox
        :return:
        """
        self.cur_run = self.cb_run.currentData()
        self.init_event_changed()

    def event_changed(self):
        """
        change event combobox
        :return:
        """
        self.cur_event = self.cb_event.currentData()
        if self.if_law:
            self.update_data_law()
        else:
            self.update_data_obs()

    #
    def update_data_obs(self):
        """
        update data
        :return:
        """

        # pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        # pattern = re.compile(r"(\w+)\\[t([+-][0-9]+)?\\]")
        pattern = re.compile(r"(\w+)\[t([+-]?\d+)?\]")
        obs = {}
        liste_date = []

        if self.param["type"] == 1:
            type = "Q"
        elif self.param["type"] == 2:
            type = "H"
        else:
            type = None

        self.graph_obj.init_curv_assim(typ_law=type, param_law=self.dico_obs[type], date_ref=True)

        if type and self.param["method"]:
            liste_stations = pattern.findall(self.param["method"])

            for cd_hydro, delta in liste_stations:
                if not delta:
                    delta = "0"

                dt = datetime.timedelta(hours=int(delta))
                if self.cur_event:
                    sql_query = (
                        "SELECT date, valeur FROM (SELECT code,type, UNNEST(date) as date, "
                        "UNNEST(valeur) as valeur FROM {4}.observations "
                        "WHERE code = '{0}' AND type='{3}') t "
                        " WHERE date>='{1}' AND date<='{2}' AND valeur > -999.9 "
                        "ORDER BY date".format(
                            cd_hydro, self.events[self.cur_event]["starttime"] + dt,
                                      self.events[self.cur_event]["endtime"] + dt,
                            type, self.mdb.SCHEMA
                        )
                    )

                else:
                    sql_query = """SELECT  id, UNNEST(date) as date,
                                UNNEST(valeur) as valeur  FROM  {2}.observations
                                WHERE code ='{0}'AND type = '{1}'
                                ORDER BY code, date;""".format(
                        cd_hydro, type, self.mdb.SCHEMA
                    )
                obs[cd_hydro] = self.mdb.query_todico(sql_query, verbose=False)

                if not liste_date:
                    liste_date = [x - dt for x in obs[cd_hydro]["date"]]
            resultat = None
            data = {"date": [], "val": [], "val_ctrl": []}
            for t in liste_date:
                calc = self.param["method"]
                for cd_hydro, delta in liste_stations:
                    if not delta:
                        delta = "0"
                    t2 = t + datetime.timedelta(hours=int(delta))
                    if t2 in obs[cd_hydro]["date"]:
                        i = obs[cd_hydro]["date"].index(t2)
                        val = obs[cd_hydro]["valeur"][i]
                    else:
                        val = None
                    calc = pattern.sub(str(val), calc, 1)
                valmin = self.events[self.cur_event]["valmin"]
                valmax = self.events[self.cur_event]["valmax"]
                try:
                    resultat = eval(calc)
                    resultat_ctrl = self.events[self.cur_event]["coefA"] * resultat + self.events[self.cur_event][
                        "coefB"]
                    if valmin and valmax:
                        if resultat_ctrl < valmin:
                            resultat_ctrl = valmin
                        elif resultat_ctrl > valmax:
                            resultat_ctrl = valmax

                except Exception as err:
                    print(err)
                    resultat = None
                    resultat_ctrl = None

                data["date"].append(t)
                data["val_ctrl"].append(resultat_ctrl)
                data["val"].append(resultat)
                # data["val_ctrl_law"].append(resultat_ctrl)

            self.graph_obj.init_graph_obs_assim(data, self.dico_obs[type])
        else:
            self.graph_obj.init_curv_assim()

    def update_data_law(self):
        """
        update data
        :return:
        """
        obs = {}
        liste_date = []

        if self.param["type"] == 1:
            type = "Q"
        elif self.param["type"] == 2:
            type = "H"
        else:
            type = None

        self.graph_obj.init_curv_assim(typ_law=type, param_law=self.dico_obs[type], date_ref=True)
        if not type:
            self.graph_obj.init_curv_assim()
            return

        # id_law
        id_law = self.events[self.cur_event]['id_law']
        if not id_law:
            return
        idx_var = self.dico_obs[type]['graph']["x"]["var"]
        sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} and id_var = {2} ORDER BY id_order".format(
            self.mdb.SCHEMA, id_law, idx_var
        )
        rows = self.mdb.run_query(sql, fetch=True)
        lst_x = [self.events[self.cur_event]["start_time_law"] +
                 datetime.timedelta(seconds=r[0]) for r in rows]
        idy_var = self.dico_obs[type]['graph']["y"]["var"][0]
        sql = "SELECT value FROM {0}.law_values WHERE id_law = {1} and id_var = {2} ORDER BY id_order".format(
            self.mdb.SCHEMA, id_law, idy_var
        )
        rows = self.mdb.run_query(sql, fetch=True)
        lst_y = [r[0] for r in rows]

        start = self.events[self.cur_event]["starttime"]
        end = self.events[self.cur_event]["endtime"]
        x_filt, y_filt = filter_xy_by_time_ensur(lst_x, lst_y, start, end)
        data = {"date": x_filt, "val": y_filt,
                "val_ctrl": self.events[self.cur_event]["coefA"] * np.array(y_filt) \
                            + self.events[self.cur_event]["coefB"]}
        self.graph_obj.init_graph_obs_assim(data, self.dico_obs[type])


