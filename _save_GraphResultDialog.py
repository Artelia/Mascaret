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
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .GraphResult import GraphResult
from .Function import tw_to_txt, interpole
from .scores.ClassScoresResDialog import ClassScoresResDialog
from datetime import date, timedelta, datetime

if int(qVersion()[0]) < 5:
    from qgis.PyQt.QtGui import *
else:
    from qgis.PyQt.QtWidgets import *


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


class CurveSelectionWidget(QWidget):
    def __init__(self, mgis, typ_graph):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_graph = typ_graph

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_curve_selector.ui'), self)

        # self.cb_run.currentIndexChanged.connect(self.run_changed)
        # self.cb_scen.currentIndexChanged.connect(self.scen_changed)
        # self.cb_graph.currentIndexChanged.connect(self.graph_changed)





class GraphResultDialog(QWidget):
    def __init__(self, mgis, typ_graph, id=None):
        QWidget.__init__(self)
        self.initialising = True
        self.mgis = mgis
        self.mdb = self.mgis.mdb

        self.typ_graph = typ_graph
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphResult_new.ui'), self)
        self.curve_selector = CurveSelectionWidget(self.mgis, typ_graph)
        self.lay_sel_curve.addWidget(self.curve_selector)
        self.graph_obj = GraphResult(self, self.lay_graph, self.lay_graph_tbar)
        self.cur_run, self.cur_graph, self.cur_vars = None, None, None
        self.cur_vars_lbl, self.cur_branch, self.cur_pknum, self.cur_t = None, None, None, None
        self.list_var_lai = []
        self.zmax_save = None
        self.cur_data = dict()
        self.old_lst_run_score = []
        self.date = None
        self.obs = None
        self.list_typ_res = None
        self.info_graph = {}
        self.val_prof_ref = {}
        self.dict_run = dict()
        self.laisses = {}

        print('Typ graph :', self.typ_graph)

        self.show_hide_com(False)
        if self.checkrun():
            if self.typ_graph == "struct" or self.typ_graph == "weirs":
                if self.typ_graph == "weirs":
                    self.typ_res = "weirs"
                else:
                    self.typ_res = "struct"
                self.lst_graph = [
                    {"id": "gate_move", "name": "Gate movement", "unit": "m",
                     "vars": ["ZSTR"], "colors": ["blue"],
                     'type_res': self.typ_res}]
                self.x_var = "time"
                self.sql_where = "results.pknum = {1}"
                self.cur_pknum = id

            elif self.typ_graph == "hydro" or self.typ_graph == "hydro_pk":
                self.list_typ_res = ["opt",
                                     "tracer_MICROPOLE",
                                     "tracer_EUTRO",
                                     "tracer_O2",
                                     "tracer_BIOMASS",
                                     "tracer_THERMIC",
                                     "tracer_TRANSPORT_PUR"]
                self.typ_res = 'opt'
                if self.typ_graph == "hydro_pk":
                    self.x_var = "pknum"
                    self.sql_where = "results.time = {1}"
                    self.cur_branch = id
                    self.cur_t = -1
                else:
                    self.x_var = "time"
                    self.sql_where = "results.pknum = {1}"
                    self.cur_pknum = id

            elif self.typ_graph == "hydro_basin" or self.typ_graph == "hydro_link":
                self.x_var = "time"
                self.cur_pknum = id

                self.sql_where = "results.pknum = {1}"
                if self.typ_graph == 'hydro_link':
                    self.typ_res = 'link'
                else:
                    self.typ_res = 'basin'

            self.cb_run.currentIndexChanged.connect(self.run_changed)
            self.cb_scen.currentIndexChanged.connect(self.scen_changed)
            self.cb_graph.currentIndexChanged.connect(self.graph_changed)
            if self.typ_graph == 'hydro_pk':
                self.cb_det.currentIndexChanged.connect(lambda: self.detail_changed(up_lim=False))
            else:
                self.cb_det.currentIndexChanged.connect(lambda: self.detail_changed(up_lim=True))

            self.bt_expCsv.clicked.connect(self.export_csv)
            self.tw_data.addAction(CopySelectedCellsAction(self.tw_data))
            self.cc_scores.stateChanged.connect(self.ch_score)

            self.lst_runs = []
            self.stw_res.setCurrentIndex(0)
            self.cl_scores = ClassScoresResDialog(self)
            self.disenable_score()
            self.init_dico_run()

            self.initialising = False
            self.update_data()
            self.initialising = False

    def ch_score(self):
        """ change tab for score"""
        if self.cc_scores.isChecked():
            self.stw_res.setCurrentIndex(1)
        else:
            self.stw_res.setCurrentIndex(0)

    def show_hide_com(self, vis=True):
        if vis:
            self.lbl_coment.show()
            self.label_coment.show()
        else:
            self.lbl_coment.hide()
            self.label_coment.hide()

    def checkrun(self):
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs "
                                  "WHERE id in (SELECT DISTINCT id_runs FROM {0}.runs_graph) "
                                  "ORDER BY run, scenario ".format(
            self.mdb.SCHEMA), fetch=True)

        if rows:
            return True
        else:
            self.mgis.add_info("No data.")
            return False

    def get_lst_graph_opt(self, id_run=None):
        """
        Get graphic list
        :param id_run: id of model
        :return:
        """

        liste = [{"id": "Z", "name": "Levels", "unit": "$m$",
                  "vars": ['ZREF', 'Z', 'ZMIN', 'ZMAX', 'CHAR'],
                  "colors": ["black", "blue", "green", "red", "cyan"],
                  'type_res': 'opt'},
                 {"id": "Q", "name": "Flow rate", "unit": "$m^3/s$",
                  "vars": ['Q', 'QMIN', 'QMAJ', 'QMAX'],
                  "colors": ["blue", "green", "cyan", "red"], 'type_res': 'opt'}
                 ]
        exclu = {'Q': False, 'QMIN': False, 'QMAJ': False, 'QMAX': False,
                 'ZREF': False, 'Z': False, 'ZMIN': False, 'ZMAX': False,
                 'CHAR': False}

        if id_run:

            list_tot = []

            for typ_res in self.list_typ_res:
                if typ_res in self.info_graph.keys():
                    list_tot += self.info_graph[typ_res]['var']

            sql = "SELECT  * FROM {0}.results_var WHERE " \
                  " id in {1}".format(self.mdb.SCHEMA, list_sql(list_tot))

        else:
            sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res in {1}".format(
                self.mdb.SCHEMA,
                list_sql(
                    self.list_typ_res))

        rows = self.mdb.run_query(sql, fetch=True)
        if not rows:
            self.mgis.add_info('No data')
        for rws in rows:
            if not rws[2] in exclu.keys():
                liste.append({"id": rws[2], "name": rws[3], "unit": "",
                              "vars": [rws[2]], "colors": ["blue"],
                              'type_res': rws[1]})
            else:
                exclu[rws[2]] = True

        iterlist = [zip(list(liste[0]['vars']), list(liste[0]['colors'])),
                    zip(list(liste[1]['vars']), list(liste[1]['colors']))]

        for i, itlist in enumerate(iterlist):
            liste[i]['vars'] = []
            liste[i]['colors'] = []
            for val, clr in itlist:
                if exclu[val]:
                    liste[i]['vars'].append(val)
                    liste[i]['colors'].append(clr)

        liste = self.change_lengend_var(liste)

        return liste

    def change_lengend_var(self, liste_var):
        """Change unit and color with variables.dat file
         :param liste_var : liste of dict containing graphs informations
         :return the update list
        """

        for dico_var in liste_var:
            for i, var in enumerate(dico_var["vars"]):
                if var.lower() in self.mgis.variables.keys():
                    dico_var["colors"][i] = self.mgis.variables[var.lower()][
                        'couleur']
                    if var not in ['Q', 'QMIN', 'QMAJ', 'QMAX', 'ZREF', 'Z',
                                   'ZMIN', 'ZMAX', 'CHAR']:
                        if self.mgis.variables[var.lower()][
                            'unite'].strip() == '':
                            dico_var['unit'] = ''
                        else:
                            dico_var['unit'] = \
                                r'$' + self.mgis.variables[var.lower()][
                                    'unite'].strip() + r'$'
        return liste_var

    def get_runs_graph(self):
        sql = "SELECT type_res, var, val FROM {0}.runs_graph WHERE " \
              "id_runs = {1} ORDER BY id".format(self.mdb.SCHEMA,
                                                 self.cur_run)

        rows = self.mdb.run_query(sql, fetch=True)

        self.info_graph = {}
        for i, row in enumerate(rows):
            if row[0] in self.info_graph.keys():
                self.info_graph[row[0]][row[1]] = row[2]
            else:
                self.info_graph[row[0]] = {row[1]: row[2]}
        print (self.info_graph)

    def get_lst_graph_bl(self, typ_res, id_run=None):
        """
        Get graphic list basin and link
        :param typ_res: result typ
        :param id_run: id of model
        :return:
        """
        liste = []
        if typ_res in self.info_graph.keys():
            if id_run:
                sql = "SELECT  * FROM {0}.results_var WHERE " \
                      "id in {1}".format(self.mdb.SCHEMA,
                                         list_sql(
                                             self.info_graph[typ_res]['var']))

            else:
                sql = "SELECT DISTINCT * FROM {0}.results_var " \
                      "WHERE type_res = '{1}'".format(self.mdb.SCHEMA,
                                                      typ_res)

            rows = self.mdb.run_query(sql, fetch=True)

            for rws in rows:
                liste.append({"id": rws[2], "name": rws[3], "unit": "",
                              "vars": [rws[2]], "colors": ["blue"],
                              'type_res': typ_res})
            liste = self.change_lengend_var(liste)
        return liste

    def init_dico_run(self):
        self.dict_run = dict()
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs "
                                  "WHERE id in (SELECT DISTINCT id_runs FROM {0}.runs_graph) "
                                  "ORDER BY date DESC, run ASC, scenario ASC;".format(
            self.mdb.SCHEMA), fetch=True)
        for row in rows:
            if row[1] not in self.dict_run.keys():
                self.dict_run[row[1]] = dict()
            self.dict_run[row[1]][row[2]] = row[0]
        self.init_cb_run()

    def init_cb_run(self):
        self.cb_run.clear()
        for run in self.dict_run.keys():
            self.cb_run.addItem(run, run)

    def init_cb_scen(self):
        run = self.cb_run.currentText()
        self.cb_scen.clear()
        for nm_scen, id_scen in self.dict_run[run].items():
            self.cb_scen.addItem(nm_scen, id_scen)

    def init_cb_graph(self):
        self.cb_graph.blockSignals(True)
        self.cb_graph.clear()
        lst_graph = None
        if self.cur_run:
            # add comment
            txt = self.mdb.select_distinct("comments", "runs",
                                           where='id={}'.format(self.cur_run))
            if txt:
                txt = txt['comments'][0]
                if not isinstance(txt, str):
                    txt = str(txt)
                self.lbl_coment.setText(txt)
                self.show_hide_com(True)
            else:
                self.show_hide_com(False)
        if self.typ_graph == "struct" or self.typ_graph == "weirs":
            lst_graph = self.lst_graph
        elif self.typ_graph == "hydro" or self.typ_graph == "hydro_pk":
            lst_graph = self.get_lst_graph_opt(self.cur_run)
        elif self.typ_graph == "hydro_basin" or self.typ_graph == "hydro_link":
            lst_graph = self.get_lst_graph_bl(self.typ_res, self.cur_run)

        self.lst_graph = lst_graph
        for graph in self.lst_graph:
            self.cb_graph.addItem(graph["name"], graph["id"])

        if self.cb_graph.count() == 0:
            self.graph_obj.axes.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clearContents()
        self.cb_graph.blockSignals(False)

    def init_cb_det(self, id):
        self.cb_det.blockSignals(True)
        self.cb_det.clear()
        if self.typ_graph == "struct" or self.typ_graph == "weirs":
            lstpk = []
            if self.typ_res in self.info_graph.keys():
                for id_config in self.info_graph[self.typ_res]['pknum'].keys():
                    lstpk.append(
                        self.info_graph[self.typ_res]['pknum'][id_config])
                info = self.mdb.select('profiles',
                                       where='abscissa IN {0}'.format(
                                           list_sql(lstpk, 'float'))
                                       , list_var=['abscissa', "name"])
                for pknum in lstpk:
                    if pknum in info['abscissa']:
                        txt = str(pknum) + ' : ' + info['name'][
                            info['abscissa'].index(pknum)]
                    else:
                        txt = str(pknum)
                    self.cb_det.addItem(txt, pknum)
            else:
                pass

            self.cb_det.setCurrentIndex(self.cb_det.findData(id))
        elif self.typ_graph == "hydro":
            info = self.mdb.select('profiles', list_var=['abscissa', "name"])

            for pknum in self.info_graph['opt']['pknum']:
                if pknum in info['abscissa']:
                    txt = str(pknum) + ' : ' + info['name'][
                        info['abscissa'].index(pknum)]
                else:
                    txt = str(pknum)
                self.cb_det.addItem(txt, pknum)

            self.cb_det.setCurrentIndex(self.cb_det.findData(id))

        elif self.typ_graph == "hydro_pk":

            sql = "SELECT init_date FROM {0}.runs " \
                  "WHERE id = {1} ".format(self.mgis.mdb.SCHEMA,
                                           self.cur_run)
            info = self.mdb.run_query(sql, fetch=True)
            if info:
                self.date = info[0][0]
            else:
                self.date = None

            for time_ in self.info_graph[self.typ_res]['time']:
                if self.date:
                    aff = self.date + timedelta(seconds=time_)
                    aff = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(aff,
                                                                 aff.microsecond / 10000.0)
                else:
                    aff = str(time_)
                self.cb_det.addItem(aff, time_)
            self.cb_det.setCurrentIndex(self.cb_det.count() - 1)
            self.cur_t = self.cb_det.itemData(self.cb_det.currentIndex())

        elif self.typ_graph == "hydro_link" or self.typ_graph == "hydro_basin":
            if self.typ_res == 'link':
                table = "links"
                num = "linknum"
            else:
                table = "basins"
                num = "basinnum"

            if self.typ_res in self.info_graph.keys():
                sql = "SELECT DISTINCT name,{3},gid FROM  {0}.{2} WHERE {3} " \
                      "IN {1} ".format(self.mgis.mdb.SCHEMA,
                                       list_sql(self.info_graph[self.typ_res][
                                                    'pknum'],
                                                'float'),
                                       table,
                                       num)

                rows = self.mdb.run_query(sql, fetch=True)
                for row in rows:
                    self.cb_det.addItem(row[0], row[1])

            self.cb_det.setCurrentIndex(self.cb_det.findData(id))
            self.sld_det.setValue(self.cb_det.findData(id))
        if self.cb_det.count() == 0:
            self.graph_obj.axes.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clearContents()
        else:
            self.sld_det.setMaximum(self.cb_det.count() - 1)
        self.cb_det.blockSignals(False)

    def run_changed(self):
        """ change fct for cb_run"""
        self.cb_scen.blockSignals(True)
        self.init_cb_scen()
        self.scen_changed()
        self.cb_scen.blockSignals(False)

    def scen_changed(self):
        """ change scen"""
        if self.cb_scen.currentIndex() != -1:
            self.cur_run = self.cb_scen.itemData(self.cb_scen.currentIndex())
            self.get_runs_graph()
            self.clean_score()
            self.init_cb_graph()
            self.graph_changed(False)
            self.init_cb_det(self.cur_pknum)
            self.detail_changed()

    def graph_changed(self, update=True):
        """ change graph"""
        self.graph_obj.update_limites = True
        if self.cb_graph.currentIndex() != -1:
            self.cur_graph = self.cb_graph.itemData(
                self.cb_graph.currentIndex())
            for graph in self.lst_graph:
                if graph["id"] == self.cur_graph:
                    self.typ_res = graph['type_res']
                    self.cur_vars = graph["vars"]
                    self.cur_vars_lbl = self.find_var_lbl()
                    self.graph_obj.init_mdl(graph["vars"], self.cur_vars_lbl,
                                            graph["colors"], graph["unit"],
                                            graph['name'])
                    break

            if update:
                self.update_data()
        else:
            self.graph_obj.axes.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clearContents()

    def detail_changed(self, up_lim=True):
        """ change pk or data"""
        self.graph_obj.update_limites = up_lim
        if self.cb_det.currentIndex() != -1:
            self.cur_pknum = self.cb_det.itemData(
                self.cb_det.currentIndex())
            self.sld_det.setValue(self.cb_det.currentIndex())
            self.update_data()
        else:
            self.graph_obj.axes.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clear()

    # def avance_detail(self, meth):
    #     idx = self.cb_det.currentIndex()
    #     if meth == "start":
    #         self.cb_det.setCurrentIndex(0)
    #     elif meth == "prev":
    #         if idx != 0:
    #             self.cb_det.setCurrentIndex(idx - 1)
    #     elif meth == "next":
    #         if idx != (self.cb_det.count() - 1):
    #             self.cb_det.setCurrentIndex(idx + 1)
    #     elif meth == "end":
    #          self.cb_det.setCurrentIndex(self.cb_det.count() - 1)


    def update_data(self):
        """
        update data graph
        :return:
        """
        if not self.initialising:
            self.cur_data = dict()
            if self.cur_vars is None:
                self.graph_obj.axes.cla()
                self.graph_obj.canvas.draw()
                self.tw_data.clear()
                self.mgis.add_info('No Data')
                return

            sqlv = "('{}')".format("', '".join(self.cur_vars))
            sqlw = self.sql_where.format(self.cur_branch, self.cur_pknum,
                                         self.cur_t)
            if self.typ_graph == 'hydro_pk':
                sql_hyd_pk = "AND pknum IN (SELECT pk FROM {0}.results_sect WHERE " \
                             "id_runs = {1} AND branch = {2})".format(
                    self.mgis.mdb.SCHEMA, self.cur_run, self.cur_branch)
            else:
                sql_hyd_pk = ''

            sql = "SELECT DISTINCT {1} FROM {0}.results WHERE id_runs = {2} AND {4} " \
                  "AND var IN (SELECT id FROM {0}.results_var WHERE var in {3}) {5} " \
                  "ORDER BY {1}".format(self.mgis.mdb.SCHEMA, self.x_var,
                                        self.cur_run,
                                        sqlv, sqlw, sql_hyd_pk)

            if self.x_var == 'time':
                if self.typ_graph in ['struct', 'weirs']:
                    x_val = None
                    if self.typ_res in self.info_graph.keys():
                        for id_config in self.info_graph[self.typ_res][
                            'pknum'].keys():
                            if self.info_graph[self.typ_res]['pknum'][
                                id_config] == self.cur_pknum:
                                x_val = self.info_graph[self.typ_res]['time'][
                                    id_config]
                    if not x_val:
                        x_val = self.info_graph['opt']['time']
                else:
                    x_val = self.info_graph[self.typ_res]['time']
                sql = "SELECT init_date FROM {0}.runs " \
                      "WHERE id = {1} ".format(self.mgis.mdb.SCHEMA,
                                               self.cur_run)
                info = self.mdb.run_query(sql, fetch=True)
                if info:
                    self.date = info[0][0]
                    if self.date:
                        self.cur_data["date"] = [
                            self.date + timedelta(seconds=row)
                            for row in x_val]
                else:
                    self.date = None

            elif self.x_var == 'pk':
                if self.typ_graph == 'hydro_pk':
                    sql = "SELECT pk FROM {0}.results_sect WHERE " \
                          "id_runs = {1} AND branch = {2} ORDER BY pk" \
                          ";".format(self.mgis.mdb.SCHEMA, self.cur_run,
                                     self.cur_branch)
                    rows = self.mdb.run_query(sql, fetch=True)
                    x_val = [row[0] for row in rows]
                else:
                    x_val = self.info_graph[self.typ_res]['pknum']

            else:
                rows = self.mdb.run_query(sql, fetch=True)

                x_val = [row[0] for row in rows]

            self.cur_data[self.x_var] = x_val

            for var in self.cur_vars:
                sql = "SELECT {1}, val FROM {0}.results WHERE id_runs = {2} AND " \
                      "var  IN (SELECT id FROM {0}.results_var WHERE results_var.var = '{3}') " \
                      "AND {4} {5} " \
                      "ORDER BY {1}".format(self.mgis.mdb.SCHEMA,
                                            self.x_var, self.cur_run,
                                            var, sqlw, sql_hyd_pk)

                rows = self.mdb.run_query(sql, fetch=True)
                self.cur_data[var] = [row[1] for row in rows]
            x_var_ = self.x_var
            if self.x_var == 'time':
                if self.date:
                    x_var_ = 'date'
                    self.graph_obj.unit_x = 'date'
                    self.graph_obj.axes.set_xlabel(r'Time')
                else:
                    self.graph_obj.axes.set_xlabel(r'Time ($s$)')

            else:
                self.graph_obj.axes.set_xlabel(r'Pk ($m$)')

            self.update_title()
            self.fill_tab(x_var_)
            self.graph_obj.clear_laisse()
            self.graph_obj.clear_obs()
            if self.typ_graph == "hydro":
                self.get_obs()
                self.update_obs()
            lais_g = False
            if self.typ_graph == "hydro" or self.typ_graph == "hydro_pk":
                if 'Z' in self.cur_vars:
                    self.get_laisses()
                    lais_g = self.update_laisse(x_var_)

            self.graph_obj.init_graph(self.cur_data, x_var_, lais=lais_g)

    def get_laisses(self):
        """
        get flood marks data
        :return:
        """

        info = self.mdb.select('runs', where="id={} ".format(self.cur_run),
                               list_var=['scenario'])
        condition = "event = '{}' AND active AND z is not null ".format(
            info["scenario"][0])
        if self.typ_graph == "hydro":
            condition += "AND abscissa = {} ".format(self.cur_pknum)

        self.laisses = self.mdb.select("flood_marks", condition, "abscissa")
        if self.laisses:
            self.laisses['pknum'] = self.laisses['abscissa']

    def get_obs(self):
        """
        get observation data
        :return:
        """
        sql = "SELECT name FROM {0}.profiles " \
              "WHERE abscissa={1} ".format(self.mdb.SCHEMA, self.cur_pknum)
        rows = self.mdb.run_query(sql, fetch=True)

        if rows:
            val = rows[0][0]
            self.obs = self.mgis.mdb.select('outputs',
                                            where="active AND (abscissa = {0} OR name = '{1}')"
                                                  "".format(self.cur_pknum,
                                                            val),
                                            order="abscissa",
                                            list_var=['code', 'zero',
                                                      'abscissa', 'name'])
            if self.obs:
                if len(self.obs['code']) == 0:
                    self.obs = None
        else:
            self.obs = None

    def update_title(self):
        """ update graph title"""
        if self.typ_graph == "struct" or self.typ_graph == "weirs" \
                or self.typ_graph == "hydro":
            try:
                self.graph_obj.axes.title.set_text(r'Profile - {0} m'
                                                   ''.format(
                    float(self.cb_det.currentText())))
            except ValueError:
                list_txt = self.cb_det.currentText().split(':')
                if len(list_txt) > 1:
                    self.graph_obj.axes.title.set_text(r'Profile {1} - {0} m '
                                                       ''.format(list_txt[0],
                                                                 list_txt[1]))
        elif self.typ_graph == "hydro_pk":
            try:
                self.graph_obj.axes.title.set_text(r'Branch {0} - {1} $s$'
                                                   ''.format(self.cur_branch,
                                                             float(
                                                                 self.cb_det.currentText())))
            except ValueError:
                self.graph_obj.axes.title.set_text(r'Branch {0} - {1}'
                                                   ''.format(self.cur_branch,
                                                             self.cb_det.currentText()))

        elif self.typ_graph == "hydro_basin":
            self.graph_obj.axes.title.set_text(r'Basin - {0}'
                                               ''.format(
                self.cb_det.currentText()))

        elif self.typ_graph == "hydro_link":
            self.graph_obj.axes.title.set_text(r'Link - {0}'
                                               ''.format(
                self.cb_det.currentText()))

    def update_laisse(self, var_x):
        """
        To graph the flood mark

        :param var_x:
        :return:
        """
        courbe_lais = {}
        lai = self.laisses
        if lai:
            if var_x not in lai.keys():
                self.graph_obj.clear_laisse()
                return False

            courbe_lais["x"] = [v for v in lai[var_x] if v]
            if not courbe_lais["x"]:
                self.graph_obj.clear_laisse()
                return False

            courbe_lais["z"] = [v for i, v in enumerate(lai['z']) if
                                lai[var_x][i]]
            if 'ZMAX' in self.cur_data.keys():
                courbe_lais["couleurs"] = []
                courbe_lais["taille"] = []
                if "pknum" in self.cur_data.keys():
                    key_val = "pknum"
                elif "date" in self.cur_data.keys():
                    key_val = "date"
                for x, z in zip(courbe_lais["x"], courbe_lais["z"]):
                    if key_val == "date":
                        x_cur_data = [datetime.timestamp(t) for t in
                                      self.cur_data[key_val]]
                        x_inter = datetime.timestamp(
                            datetime(*x.timetuple()[:-4]))
                    else:
                        x_cur_data = self.cur_data[key_val]
                        x_inter = x
                    val = interpole(x_inter, x_cur_data, self.cur_data['ZMAX'])

                    if val:
                        diff = z - val
                        if diff < 0:
                            courbe_lais["couleurs"].append("purple")
                        else:
                            courbe_lais["couleurs"].append("green")

                        if abs(diff) > 0.2:
                            courbe_lais["taille"].append(3)
                        elif abs(diff) > 0.1:
                            courbe_lais["taille"].append(2)
                        else:
                            courbe_lais["taille"].append(1)

                    else:
                        courbe_lais["couleurs"].append("black")
                        courbe_lais["taille"].append(1)
            else:
                courbe_lais["couleurs"] = ["black"] * len(courbe_lais["x"])
                courbe_lais["taille"] = [1] * len(courbe_lais["x"])

            self.graph_obj.init_graph_laisse(courbe_lais)
            return True
        return False

    def update_obs(self):
        """ """
        # observation seulement si event
        if self.obs and "date" in self.cur_data.keys():

            if "Z" in self.cur_data.keys():
                gg = 'H'
            elif "Q" in self.cur_data.keys():
                gg = 'Q'
            else:
                self.graph_obj.clear_obs()
                self.disenable_score()
                return
            mini = min(self.cur_data["date"])
            maxi = max(self.cur_data["date"])
            for code in self.obs['code']:
                condition = """code = '{0}'
                           AND date>'{1}'
                           AND date<'{2}'
                           AND type='{3}'
                           AND valeur > -999.9""".format(code, mini,
                                                         maxi, gg)

                obs_graph = self.mdb.select("observations", condition, "date")
                # print( obs_graph)
                if len(obs_graph['valeur']) != 0:
                    break

            if len(obs_graph['valeur']) == 0:
                self.graph_obj.clear_obs()
                self.disenable_score()
                return

            if "Z" in self.cur_data.keys():
                tempo = []
                for var1 in obs_graph['valeur']:
                    tempo.append(var1 + self.obs['zero'][0])
                obs_graph['valeur'] = tempo

            self.graph_obj.init_graph_obs(obs_graph)
            self.lst_runs = [self.cur_run]
            self.cc_scores.setEnabled(True)
            self.cl_scores.wgt_param.cur_pknum = self.cur_pknum
            self.cl_scores.wgt_param.lst_runs = self.lst_runs
            if self.old_lst_run_score != self.lst_runs:
                self.cl_scores.wgt_param.init_gui()
                self.old_lst_run_score = self.lst_runs
            else:
                self.old_lst_run_score = self.lst_runs

        elif self.obs and not ("date" in self.cur_data.keys()):
            self.graph_obj.clear_obs()
            self.lst_runs = [self.cur_run]
            self.cc_scores.setEnabled(True)
            self.cl_scores.wgt_param.cur_pknum = self.cur_pknum
            self.cl_scores.wgt_param.lst_runs = self.lst_runs
            if self.old_lst_run_score != self.lst_runs:
                self.cl_scores.wgt_param.init_gui()
                self.old_lst_run_score = self.lst_runs
            else:
                self.old_lst_run_score = self.lst_runs
        else:
            self.graph_obj.clear_obs()
            self.disenable_score()

    def fill_tab(self, x_var, nb_col=None):
        self.tw_data.setColumnCount(0)
        if nb_col:
            nbcol = nb_col
        elif 'date' in self.cur_data.keys():
            nbcol = len(self.cur_data) - 1
        else:
            nbcol = len(self.cur_data)

        self.tw_data.setColumnCount(nbcol)
        self.tw_data.setRowCount(0)
        self.tw_data.setRowCount(len(self.cur_data[x_var]))
        lst_vars = [x_var]
        lst_vars.extend(self.cur_vars)
        lst_lbls = [x_var]
        lst_lbls.extend(self.cur_vars_lbl)
        for c, var in enumerate(lst_vars):
            self.tw_data.setHorizontalHeaderItem(c,
                                                 QTableWidgetItem(lst_lbls[c]))
            for r, val in enumerate(self.cur_data[var]):
                if var == "date":
                    val = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(val,
                                                                 val.microsecond / 10000.0)
                itm = QTableWidgetItem()
                itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                itm.setData(0, val)
                self.tw_data.setItem(r, c, itm)

        self.tw_data.setVisible(False)
        self.tw_data.resizeColumnsToContents()
        self.tw_data.resizeRowsToContents()
        self.tw_data.setVisible(True)

    def clean_score(self):
        """
        clean scores
        """
        self.cl_scores.clear_scores()
        self.cc_scores.setChecked(False)

    def disenable_score(self):
        """ disenable scores """
        self.clean_score()
        self.cc_scores.setEnabled(False)

    def find_var_lbl(self):
        tmp = []
        for var in self.cur_vars:
            rows = self.mdb.run_query("SELECT name FROM {0}.results_var "
                                      "WHERE var = '{1}'".format(
                self.mgis.mdb.SCHEMA, var),
                fetch=True)
            tmp.append(rows[0][0])
        return tmp

    def export_csv(self):
        """Export Table to .CSV file"""

        txt = self.cb_graph.currentText()
        default_name = txt.replace(' ', '_').replace(':', '-')
        if int(qVersion()[0]) < 5:
            file_name_path = QFileDialog.getSaveFileName(self, "saveFile",
                                                         "{0}.csv".format(
                                                             default_name),
                                                         filter="CSV (*.csv *.)")
        else:
            file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                            "{0}.csv".format(
                                                                default_name),
                                                            filter="CSV (*.csv *.)")

        if file_name_path:
            cur_tw = self.tw_data
            range_r = range(0, cur_tw.rowCount())
            range_c = range(0, cur_tw.columnCount())
            clipboard = tw_to_txt(cur_tw, range_r, range_c, ';')
            file = open(file_name_path, 'w')
            file.write(clipboard)
            file.close()


class CopySelectedCellsAction(QAction):
    def __init__(self, cur_tw):
        if not isinstance(cur_tw, QTableWidget):
            chaine = """CopySelectedCellsAction must be initialised with
                     a QTableWidget. A {0} was given."""
            raise ValueError(chaine.format(type(cur_tw)))

        super(CopySelectedCellsAction, self).__init__('Copy', cur_tw)
        self.setShortcut('Ctrl+C')
        self.triggered.connect(self.copy_cells_to_clipboard)
        self.cur_tw = cur_tw

    def copy_cells_to_clipboard(self):
        if len(self.cur_tw.selectionModel().selectedIndexes()) > 0:
            lst_r = [idx.row() for idx in
                     self.cur_tw.selectionModel().selectedIndexes()]
            lst_c = [idx.column() for idx in
                     self.cur_tw.selectionModel().selectedIndexes()]
            range_r = range(min(lst_r), max(lst_r) + 1)
            range_c = range(min(lst_c), max(lst_c) + 1)
            clipboard = tw_to_txt(self.cur_tw, range_r, range_c, '\t')
            sys_clip = QApplication.clipboard()
            sys_clip.setText(clipboard)



