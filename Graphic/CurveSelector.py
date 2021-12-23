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
from qgis.PyQt.QtCore import qVersion, pyqtSignal
from qgis.PyQt.uic import *

if int(qVersion()[0]) < 5:
    from qgis.PyQt.QtGui import *
else:
    from qgis.PyQt.QtWidgets import *

from datetime import date, timedelta, datetime


def list_sql(liste, typ='str'):
    """
    list to srting for sql script
    :param liste: element list
    :param typ : element type
    :return:
    """
    txt = '('
    for t_res in liste:
        if typ is 'str':
            txt += "'{}',".format(t_res)
        elif typ == 'int' or typ == 'float':
            txt += "{},".format(t_res)
    txt = txt[:-1] + ')'
    return txt


class CurveSelectorWidget(QWidget):
    cur_scen_edited = pyqtSignal()
    graph_parameters_edited = pyqtSignal(int, dict)

    def __init__(self, mgis, mode, row, typ_graph, typ_res, x_var, dict_run,
                 cur_pknum, cur_branch):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.row = row
        self.typ_graph = typ_graph
        self.typ_res = typ_res
        self.x_var = x_var
        self.dict_run = dict_run

        self.init_date_displayed = False
        self.init_date_needed = False

        self.lst_graph = list()
        self.info_graph = dict()
        self.param_graph = dict()

        self.cur_pknum, self.cur_branch, self.cur_t = cur_pknum, cur_branch, None
        self.cur_run, self.cur_scen, self.cur_graph = None, None, None

        self.ui = loadUi(os.path.join(self.mgis.masplugPath,
                                      'ui/ui_curve_selector_{}.ui'.format(
                                          mode)), self)

        self.cb_run.currentIndexChanged.connect(self.run_changed)
        self.cb_scen.currentIndexChanged.connect(self.scen_changed)
        self.cb_graph.currentIndexChanged.connect(self.graph_changed)
        if self.typ_graph == 'hydro_pk':
            self.cb_det.currentIndexChanged.connect(
                lambda: self.detail_changed(up_lim=False))
        else:
            self.cb_det.currentIndexChanged.connect(
                lambda: self.detail_changed(up_lim=True))

    def init_run(self, param_init=None, param_date=None):
        """ initialize GUI"""
        ini_run, ini_scen, ini_graph, ini_det = None, None, None, None
        if param_init:
            self.cb_axe.blockSignals(True)
            self.cb_axe.setCurrentIndex(self.cb_axe.findData(param_init["axe"]))
            self.cb_axe.blockSignals(False)
            ini_run = param_init["run"]
            ini_scen = param_init["scen"]
            ini_graph = param_init["graph"]["id"]
            if self.typ_graph == "hydro_pk":
                ini_det = param_init["t"]
            else:
                ini_det = param_init["pknum"]

            if param_date:
                if not param_date["display"]:
                    self.hide_init_date(False)
                else:
                    self.show_init_date(param_date["need"], param_date["init"],
                                        False)

        self.cb_run.blockSignals(True)
        self.init_cb_run(ini_run)
        self.cb_run.blockSignals(False)
        self.run_changed(None, ini_scen, ini_graph, ini_det)

    def init_cb_run(self, ini_run=None):
        """
         initialize cb_run object
        :param ini_run: run name to default
        :return:
        """
        self.cb_run.clear()
        for run in self.dict_run.keys():
            self.cb_run.addItem(run, run)
        if ini_run:
            self.cb_run.setCurrentIndex(self.cb_run.findData(ini_run))

    def run_changed(self, v, ini_scen=None, ini_graph=None, ini_det=None):
        """
         action when change run
        :param v:
        :param ini_scen: scenario name to default
        :param ini_graph: graphic name to default
        :param ini_det: cb_det name to default
        :return:
        """
        self.cur_run = self.cb_run.currentData()
        self.cb_scen.blockSignals(True)
        self.init_cb_scen(ini_scen)
        self.cb_scen.blockSignals(False)
        self.scen_changed(None, ini_graph, ini_det)

    def init_cb_scen(self, ini_scen=None):
        """
        initialize cb_scen object
        :param ini_scen:  scenario name to default
        :return:
        """
        run = self.cb_run.currentText()
        self.cb_scen.clear()
        for nm_scen, id_scen in self.dict_run[run].items():
            self.cb_scen.addItem(nm_scen, id_scen)
        if ini_scen:
            self.cb_scen.setCurrentIndex(self.cb_scen.findData(ini_scen))

    def scen_changed(self, v, ini_graph=None, ini_det=None):
        """
         action when change scenario
        :param v:
        :param ini_graph: graphic name to default
        :param ini_det: cb_det name to default
        :return:
        """
        if self.cb_scen.currentIndex() != -1:
            self.cur_scen_edited.emit()
            self.cur_scen = self.cb_scen.currentData()
            self.update_graph_infos()

            self.cb_graph.blockSignals(True)
            self.init_cb_graph(ini_graph)
            self.cb_graph.blockSignals(False)
            self.graph_changed(v=None, update=False)

            self.cb_det.blockSignals(True)
            self.init_cb_det(ini_det)
            self.cb_det.blockSignals(False)
            self.detail_changed()

    def init_cb_graph(self, ini_graph=None):
        """
        initialize cb_graph
        :param ini_graph:
        :return:
        """
        self.cb_graph.clear()
        self.lst_graph.clear()
        if self.cur_scen:
            if self.typ_graph in ["struct", "weirs"]:
                self.lst_graph = [{"type_res": self.typ_res, "id": 'gate_move',
                                   "name": 'Gate movement', "unit": 'm',
                                   "vars": ["ZSTR"]}]
            elif self.typ_graph in ["hydro", "hydro_pk"]:
                self.get_lst_graph_opt()
            elif self.typ_graph in ["hydro_basin", "hydro_link"]:
                self.get_lst_graph_bl()

            for graph in self.lst_graph:
                self.cb_graph.addItem(graph["name"], graph["id"])

            if ini_graph:
                self.cb_graph.setCurrentIndex(self.cb_graph.findData(ini_graph))

    def graph_changed(self, v=None, update=True):
        """
         action when change graphic
        :param v:
        :param update:
        :return:
        """
        if self.cb_graph.currentIndex() != -1:
            self.cur_graph = self.cb_graph.currentData()
        if update:
            self.update_param_graph()
            self.graph_parameters_edited.emit(self.row, self.param_graph)

    def init_cb_det(self, ini_det=None):
        """
        initialize  cb_det object
        :param ini_det:
        :return:
        """
        self.cb_det.clear()
        if self.typ_graph in ["struct", "weirs"]:
            lstpk = []
            if self.typ_res in self.info_graph.keys():
                for id_config in self.info_graph[self.typ_res]['pknum'].keys():
                    lstpk.append(
                        self.info_graph[self.typ_res]['pknum'][id_config])
                info = self.mdb.select('profiles',
                                       where='abscissa IN {0}'.format(
                                           list_sql(lstpk, 'float')),
                                       list_var=['abscissa', "name"])
                for pknum in lstpk:
                    if pknum in info['abscissa']:
                        txt = str(pknum) + ' : ' + info['name'][
                            info['abscissa'].index(pknum)]
                    else:
                        txt = str(pknum)
                    self.cb_det.addItem(txt, pknum)
            else:
                pass

        elif self.typ_graph == "hydro":
            info = self.mdb.select('profiles', list_var=['abscissa', "name"])
            for pknum in self.info_graph['opt']['pknum']:
                if pknum in info['abscissa']:
                    txt = str(pknum) + ' : ' + info['name'][
                        info['abscissa'].index(pknum)]
                else:
                    txt = str(pknum)
                self.cb_det.addItem(txt, pknum)

        elif self.typ_graph == "hydro_pk":
            self.init_date = None

            sql = "SELECT init_date FROM {0}.runs WHERE id = {1} ".format(
                self.mgis.mdb.SCHEMA, self.cur_scen)
            info = self.mdb.run_query(sql, fetch=True)
            if info:
                self.init_date = info[0][0]

            for time_ in self.info_graph[self.typ_res]['time']:
                if self.init_date:
                    aff = self.init_date + timedelta(seconds=time_)
                    aff = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(aff,
                                                                 aff.microsecond / 10000.0)
                else:
                    aff = str(time_)
                self.cb_det.addItem(aff, time_)

        elif self.typ_graph in ["hydro_basin", "hydro_link"]:
            table, num = "{}s".format(self.typ_res), "{}num".format(
                self.typ_res)
            if self.typ_res in self.info_graph.keys():
                sql = "SELECT DISTINCT name, {3}, gid FROM  {0}.{2} " \
                      "WHERE {3} IN {1} ".format(self.mgis.mdb.SCHEMA,
                                                 list_sql(self.info_graph[
                                                              self.typ_res][
                                                              'pknum'],
                                                          'float'), table, num)
                rows = self.mdb.run_query(sql, fetch=True)
                for row in rows:
                    self.cb_det.addItem(row[0], row[1])

        if ini_det:
            self.cb_det.setCurrentIndex(self.cb_det.findData(ini_det))
        else:
            if self.typ_graph == "hydro_pk":
                self.cb_det.setCurrentIndex(self.cb_det.count() - 1)
            else:
                self.cb_det.setCurrentIndex(
                    self.cb_det.findData(self.cur_pknum))

    def detail_changed(self, up_lim=True):
        """
        action when change cb_det
        :param up_lim:
        :return:
        """
        # self.graph_obj.update_limites = up_lim TODO
        if self.cb_det.currentIndex() != -1:
            if self.typ_graph == "hydro_pk":
                self.cur_t = self.cb_det.itemData(self.cb_det.currentIndex())
            else:
                self.cur_pknum = self.cb_det.itemData(
                    self.cb_det.currentIndex())
        self.update_param_graph()
        self.graph_parameters_edited.emit(self.row, self.param_graph)

    def update_param_graph(self):
        """
        update graphic parameter
        :return:
        """
        self.param_graph.clear()
        self.param_graph["run"] = self.cur_run
        self.param_graph["scen"] = self.cur_scen
        self.param_graph["init_date"] = None
        self.param_graph["info_graph"] = self.info_graph
        self.param_graph["branch"] = self.cur_branch
        self.param_graph["pknum"] = self.cur_pknum
        self.param_graph["t"] = self.cur_t
        if (self.cb_graph.currentIndex() != -1) and (
                    self.cb_det.currentIndex() != -1):
            for graph in self.lst_graph:
                if graph["id"] == self.cur_graph:
                    self.param_graph["graph"] = graph
                    break

    def update_graph_infos(self):
        """
        update info graphic
        :return:
        """
        sql = "SELECT type_res, var, val FROM {0}.runs_graph WHERE " \
              "id_runs = {1} ORDER BY id".format(self.mdb.SCHEMA, self.cur_scen)
        rows = self.mdb.run_query(sql, fetch=True)
        self.info_graph.clear()
        for i, row in enumerate(rows):
            if row[0] in self.info_graph.keys():
                self.info_graph[row[0]][row[1]] = row[2]
            else:
                self.info_graph[row[0]] = {row[1]: row[2]}

    def get_lst_graph_opt(self):
        """
        get variable of graphic
        :return:
        """
        list_typ_res = ["opt", "tracer_MICROPOLE", "tracer_EUTRO", "tracer_O2",
                        "tracer_BIOMASS", "tracer_THERMIC",
                        "tracer_TRANSPORT_PUR"]

        self.lst_graph = [
            {"type_res": 'opt', "id": 'Z', "name": 'Levels', "unit": '$m$',
             "vars": ['ZREF', 'Z', 'ZMIN', 'ZMAX', 'CHAR']},
            {"type_res": 'opt', "id": 'Q', "name": 'Flow rate',
             "unit": '$m^3/s$',
             "vars": ['Q', 'QMIN', 'QMAJ', 'QMAX']}]

        common_var_exists = {'Q': False, 'QMIN': False, 'QMAJ': False,
                             'QMAX': False,
                             'ZREF': False, 'Z': False, 'ZMIN': False,
                             'ZMAX': False, 'CHAR': False}

        if self.cur_scen:
            list_vars = []
            for typ_res in list_typ_res:
                if typ_res in self.info_graph.keys():
                    list_vars.extend(self.info_graph[typ_res]['var'])
            sql = "SELECT * FROM {0}.results_var WHERE id in {1}".format(
                self.mdb.SCHEMA, list_sql(list_vars))
        # else:
        #     sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res in {1}".format(self.mdb.SCHEMA, list_sql(self.list_typ_res))

        rows = self.mdb.run_query(sql, fetch=True)
        if not rows:
            self.mgis.add_info('No data')
        else:
            for rws in rows:
                if not rws[2] in common_var_exists.keys():
                    self.lst_graph.append(
                        {"type_res": rws[1], "id": rws[2], "name": rws[3],
                         "unit": '', "vars": [rws[2]]})
                else:
                    common_var_exists[rws[2]] = True

        for graph in self.lst_graph[:2]:
            graph["vars"] = [v for v in graph["vars"] if common_var_exists[v]]

        self.correct_units()

    def get_lst_graph_bl(self):
        """
        Get graphic list basin and link
        :return:
        """
        if self.typ_res in self.info_graph.keys():
            if self.cur_scen:
                sql = "SELECT * FROM {0}.results_var " \
                      "WHERE id in {1}".format(self.mdb.SCHEMA, list_sql(
                    self.info_graph[self.typ_res]['var']))
            else:
                sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res = '{1}'".format(
                    self.mdb.SCHEMA, self.typ_res)
            rows = self.mdb.run_query(sql, fetch=True)

            for rws in rows:
                self.lst_graph.append(
                    {"type_res": self.typ_res, "id": rws[2], "name": rws[3],
                     "unit": '', "vars": [rws[2]]})

            self.correct_units()

    def correct_units(self):
        """
        unit correction
        :return:
        """
        for graph in self.lst_graph:
            if graph["id"] not in ['Z', 'Q']:
                var = graph["vars"][0].lower()
                if var in self.mgis.variables.keys():
                    if self.mgis.variables[var]['unite']:
                        graph["unit"] = r"${}$".format(
                            self.mgis.variables[var]['unite'])


class SlideCurveSelectorWidget(CurveSelectorWidget):
    """
    slider management
    """

    def __init__(self, mgis=None, row=None, typ_graph=None, typ_res=None,
                 x_var=None, dict_run=None, cur_pknum=None, cur_branch=None):
        CurveSelectorWidget.__init__(self, mgis, "slide", row, typ_graph,
                                     typ_res, x_var, dict_run, cur_pknum,
                                     cur_branch)

    def scen_changed(self, v, ini_graph=None, ini_det=None):
        CurveSelectorWidget.scen_changed(self, v, ini_graph, ini_det)
        self.display_comment()

    def display_comment(self):
        txt = self.mdb.select_distinct("comments", "runs",
                                       where='id={}'.format(self.cur_scen))
        if txt:
            txt = txt['comments'][0]
            if not isinstance(txt, str):
                txt = str(txt)
            self.lbl_com.setText(txt)
            self.lbl_com.show()
            self.label_com.show()
        else:
            self.lbl_com.hide()
            self.label_com.hide()

    def init_cb_det(self, id):
        CurveSelectorWidget.init_cb_det(self, id)
        if self.cb_det.currentIndex() != -1:
            self.sld_det.setMaximum(self.cb_det.count() - 1)

    def detail_changed(self, up_lim=True):
        if self.cb_det.currentIndex() != -1:
            self.sld_det.setValue(self.cb_det.currentIndex())
        CurveSelectorWidget.detail_changed(self, up_lim)

    def update_param_graph(self):
        CurveSelectorWidget.update_param_graph(self)
        self.param_graph["axe"] = 1


class CompareCurveSelectorWidget(CurveSelectorWidget):
    def __init__(self, mgis=None, row=None, typ_graph=None, typ_res=None,
                 x_var=None, dict_run=None, cur_pknum=None, cur_branch=None):
        CurveSelectorWidget.__init__(self, mgis, "compare", row, typ_graph,
                                     typ_res, x_var, dict_run, cur_pknum,
                                     cur_branch)

        self.cb_axe.clear()
        for a in [1, 2]:
            self.cb_axe.addItem("Axe {}".format(a), a)

        self.lbl_date_init.hide()
        self.ctrl_date_init.hide()
        if x_var == "time":
            self.lbl_det.setText("Pk")
        elif x_var == "pknum":
            self.lbl_det.setText("Date")

        self.cb_axe.currentIndexChanged.connect(self.axe_changed)
        self.ctrl_date_init.dateTimeChanged.connect(self.date_changed)

    def date_changed(self):
        self.update_param_graph()
        self.graph_parameters_edited.emit(self.row, self.param_graph)

    def axe_changed(self):
        self.update_param_graph()
        self.graph_parameters_edited.emit(self.row, self.param_graph)

    def update_param_graph(self):
        CurveSelectorWidget.update_param_graph(self)
        self.param_graph["axe"] = self.cb_axe.currentData()
        if self.init_date_needed:
            self.param_graph[
                "init_date"] = self.ctrl_date_init.dateTime().toPyDateTime()

    def show_init_date(self, needed=False, value=None, update=True):
        self.lbl_date_init.show()
        self.ctrl_date_init.show()
        self.ctrl_date_init.setEnabled(needed)
        if not self.init_date_needed:
            if value:
                self.ctrl_date_init.blockSignals(True)
                self.ctrl_date_init.setDateTime(value)
                self.ctrl_date_init.blockSignals(False)
        self.init_date_needed = needed
        self.init_date_displayed = True
        if update: self.update_param_graph()

    def hide_init_date(self, update=True):
        self.lbl_date_init.hide()
        self.ctrl_date_init.hide()
        self.ctrl_date_init.setEnabled(False)
        self.init_date_needed = False
        self.init_date_displayed = False
        if update: self.update_param_graph()
