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
    no_graph_selected = pyqtSignal()
    cur_graph_edited = pyqtSignal(dict)

    def __init__(self, mgis,  mode, typ_graph, typ_res, dict_run, cur_pknum, cur_branch):
        QWidget.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_graph = typ_graph
        self.typ_res = typ_res
        self.dict_run = dict_run

        self.cur_pknum = cur_pknum
        self.cur_branch = cur_branch
        self.cur_t = None

        self.lst_graph = list()
        self.info_graph = dict()

        self.cur_run, self.cur_graph, self.cur_vars = None, None, None
        self.cur_vars_lbl = None

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_curve_selector_{}.ui'.format(mode)), self)

        self.cb_run.currentIndexChanged.connect(self.run_changed)
        self.cb_scen.currentIndexChanged.connect(self.scen_changed)
        self.cb_graph.currentIndexChanged.connect(self.graph_changed)
        if self.typ_graph == 'hydro_pk':
           self.cb_det.currentIndexChanged.connect(lambda: self.detail_changed(up_lim=False))
        else:
           self.cb_det.currentIndexChanged.connect(lambda: self.detail_changed(up_lim=True))


    def init_run(self):
        self.init_cb_run()


    def init_cb_run(self):
        self.cb_run.clear()
        for run in self.dict_run.keys():
            self.cb_run.addItem(run, run)


    def run_changed(self):
        self.cb_scen.blockSignals(True)
        self.init_cb_scen()
        self.scen_changed()
        self.cb_scen.blockSignals(False)


    def init_cb_scen(self):
        run = self.cb_run.currentText()
        self.cb_scen.clear()
        for nm_scen, id_scen in self.dict_run[run].items():
            self.cb_scen.addItem(nm_scen, id_scen)


    def scen_changed(self):
        if self.cb_scen.currentIndex() != -1:
            self.cur_scen_edited.emit()
            self.cur_run = self.cb_scen.itemData(self.cb_scen.currentIndex())
            self.get_run_graph_infos()
            self.init_cb_graph()
            self.graph_changed(None, False)
            self.init_cb_det(self.cur_pknum)
            self.detail_changed()


    def init_cb_graph(self):
        self.cb_graph.blockSignals(True)
        self.cb_graph.clear()
        self.lst_graph.clear()

        if self.cur_run:
            if self.typ_graph in ["struct", "weirs"]:
                self.lst_graph = [{"id": "gate_move", "name": "Gate movement", "unit": "m",
                                   "vars": ["ZSTR"], "colors": ["blue"],
                                   'type_res': self.typ_res}]
            elif self.typ_graph in ["hydro", "hydro_pk"]:
                self.lst_graph = self.get_lst_graph_opt()
            elif self.typ_graph in ["hydro_basin", "hydro_link"]:
                self.lst_graph = self.get_lst_graph_bl()

            for graph in self.lst_graph:
                self.cb_graph.addItem(graph["name"], graph["id"])

        # if self.cb_graph.count() == 0:
        #     self.no_graph_selected.emit()

        self.cb_graph.blockSignals(False)


    def graph_changed(self, v=None, update=True):
        #self.graph_obj.update_limites = True TODO
        if self.cb_graph.currentIndex() != -1:
            self.cur_graph = self.cb_graph.itemData(self.cb_graph.currentIndex())
            for graph in self.lst_graph:
                if graph["id"] == self.cur_graph:
                    # self.typ_res = graph['type_res'] TODO Utile ??????
                    self.cur_vars = graph["vars"]
                    self.cur_vars_lbl = self.find_var_lbl()
                    #self.graph_obj.init_mdl(graph["vars"], self.cur_vars_lbl, graph["colors"], graph["unit"], graph['name']) TODO
                    break

            if update:
                self.recup_param_graph()


    def init_cb_det(self, id):
        self.cb_det.blockSignals(True)
        self.cb_det.clear()

        if self.typ_graph in ["struct", "weirs"]:
            lstpk = []
            if self.typ_res in self.info_graph.keys():
                for id_config in self.info_graph[self.typ_res]['pknum'].keys():
                    lstpk.append(self.info_graph[self.typ_res]['pknum'][id_config])
                info = self.mdb.select('profiles', where='abscissa IN {0}'.format(list_sql(lstpk, 'float')),
                                       list_var=['abscissa', "name"])
                for pknum in lstpk:
                    if pknum in info['abscissa']:
                        txt = str(pknum) + ' : ' + info['name'][info['abscissa'].index(pknum)]
                    else:
                        txt = str(pknum)
                    self.cb_det.addItem(txt, pknum)
            else:
                pass

        elif self.typ_graph == "hydro":
            info = self.mdb.select('profiles', list_var=['abscissa', "name"])
            for pknum in self.info_graph['opt']['pknum']:
                if pknum in info['abscissa']:
                    txt = str(pknum) + ' : ' + info['name'][info['abscissa'].index(pknum)]
                else:
                    txt = str(pknum)
                self.cb_det.addItem(txt, pknum)

        elif self.typ_graph == "hydro_pk":
            sql = "SELECT init_date FROM {0}.runs WHERE id = {1} ".format(self.mgis.mdb.SCHEMA, self.cur_run)
            info = self.mdb.run_query(sql, fetch=True)
            if info:
                self.date = info[0][0]
            else:
                self.date = None

            for time_ in self.info_graph[self.typ_res]['time']:
                if self.date:
                    aff = self.date + timedelta(seconds=time_)
                    aff = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(aff, aff.microsecond / 10000.0)
                else:
                    aff = str(time_)
                self.cb_det.addItem(aff, time_)

        elif self.typ_graph in ["hydro_basin", "hydro_link"]:
            table, num = "{}s".format(self.typ_res), "{}num".format(self.typ_res)
            if self.typ_res in self.info_graph.keys():
                sql = "SELECT DISTINCT name, {3}, gid FROM  {0}.{2} " \
                      "WHERE {3} IN {1} ".format(self.mgis.mdb.SCHEMA,
                                       list_sql(self.info_graph[self.typ_res]['pknum'], 'float'), table, num)
                rows = self.mdb.run_query(sql, fetch=True)
                for row in rows:
                    self.cb_det.addItem(row[0], row[1])

        if self.typ_graph == "hydro_pk":
            self.cb_det.setCurrentIndex(self.cb_det.count() - 1)
        else:
            self.cb_det.setCurrentIndex(self.cb_det.findData(id))

        self.cb_det.blockSignals(False)


    def detail_changed(self, up_lim=True):
        # self.graph_obj.update_limites = up_lim TODO
        if self.cb_det.currentIndex() != -1:
            if self.typ_graph == "hydro_pk":
                self.cur_t = self.cb_det.itemData(self.cb_det.currentIndex())
            else:
                self.cur_pknum = self.cb_det.itemData(self.cb_det.currentIndex())
            self.recup_param_graph()


    def recup_param_graph(self):
        if (self.cb_graph.currentIndex() == -1) or (self.cb_det.currentIndex() == -1):
            self.no_graph_selected.emit()
        else:
            param = dict()
            param["cur_run"] = self.cur_run
            param["cur_pknum"] = self.cur_pknum
            param["cur_branch"] = self.cur_branch
            param["cur_t"] = self.cur_t
            param["cur_vars"] = self.cur_vars
            param["info_graph"] = self.info_graph
            self.cur_graph_edited.emit(param)















    def get_run_graph_infos(self):
        sql = "SELECT type_res, var, val FROM {0}.runs_graph WHERE " \
              "id_runs = {1} ORDER BY id".format(self.mdb.SCHEMA, self.cur_run)
        rows = self.mdb.run_query(sql, fetch=True)
        self.info_graph.clear()
        for i, row in enumerate(rows):
            if row[0] in self.info_graph.keys():
                self.info_graph[row[0]][row[1]] = row[2]
            else:
                self.info_graph[row[0]] = {row[1]: row[2]}


    def get_lst_graph_opt(self):
        list_typ_res = ["opt", "tracer_MICROPOLE", "tracer_EUTRO", "tracer_O2",
                        "tracer_BIOMASS", "tracer_THERMIC", "tracer_TRANSPORT_PUR"]

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

        if self.cur_run:
            list_tot = []
            for typ_res in list_typ_res:
                if typ_res in self.info_graph.keys():
                    list_tot += self.info_graph[typ_res]['var']
            sql = "SELECT  * FROM {0}.results_var WHERE " \
                  " id in {1}".format(self.mdb.SCHEMA, list_sql(list_tot))
        else:
            sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res in {1}".format(
                self.mdb.SCHEMA,
                list_sql(self.list_typ_res))

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

        liste = self.change_legend_var(liste)
        return liste


    def get_lst_graph_bl(self):
        """
        Get graphic list basin and link
        :param typ_res: result typ
        :param id_run: id of model
        :return:
        """
        liste = []
        if self.typ_res in self.info_graph.keys():
            if self.cur_run:
                sql = "SELECT * FROM {0}.results_var " \
                      "WHERE id in {1}".format(self.mdb.SCHEMA, list_sql(self.info_graph[self.typ_res]['var']))
            else:
                sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res = '{1}'".format(self.mdb.SCHEMA, self.typ_res)
            rows = self.mdb.run_query(sql, fetch=True)

            for rws in rows:
                liste.append({"id": rws[2], "name": rws[3], "unit": "",
                              "vars": [rws[2]], "colors": ["blue"],
                              'type_res': self.typ_res})
            liste = self.change_legend_var(liste)
        return liste


    def change_legend_var(self, liste_var):
        """Change unit and color with variables.dat file
         :param liste_var : liste of dict containing graphs informations
         :return the update list
        """
        for dico_var in liste_var:
            for i, var in enumerate(dico_var["vars"]):
                if var.lower() in self.mgis.variables.keys():
                    dico_var["colors"][i] = self.mgis.variables[var.lower()]['couleur']
                    if var not in ['Q', 'QMIN', 'QMAJ', 'QMAX', 'ZREF', 'Z', 'ZMIN', 'ZMAX', 'CHAR']:
                        if self.mgis.variables[var.lower()]['unite'].strip() == '':
                            dico_var['unit'] = ''
                        else:
                            dico_var['unit'] = r'$' + self.mgis.variables[var.lower()]['unite'].strip() + r'$'
        return liste_var


    def find_var_lbl(self):
        tmp = []
        for var in self.cur_vars:
            rows = self.mdb.run_query("SELECT name FROM {0}.results_var "
                                      "WHERE var = '{1}'".format(self.mgis.mdb.SCHEMA, var), fetch=True)
            tmp.append(rows[0][0])
        return tmp





class SlideCurveSelectorWidget(CurveSelectorWidget):
    def __init__(self, mgis=None, typ_graph=None, typ_res=None, dict_run=None, cur_pknum=None, cur_branch=None):
        CurveSelectorWidget.__init__(self, mgis, "slide", typ_graph, typ_res, dict_run, cur_pknum, cur_branch)

    def scen_changed(self):
        CurveSelectorWidget.scen_changed(self)
        self.display_comment()

    def display_comment(self):
        txt = self.mdb.select_distinct("comments", "runs", where='id={}'.format(self.cur_run))
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

