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
from datetime import timedelta, datetime

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .CurveSelector import SlideCurveSelectorWidget, \
    CompareCurveSelectorWidget
from .GraphResult import GraphResult
from ..Function import tw_to_txt, interpole, fill_zminbed
from ..scores.ClassScoresResDialog import ClassScoresResDialog


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


class GraphResultDialog(QWidget):
    def __init__(self, mgis, typ_graph, id=None):
        QWidget.__init__(self)
        self.initialising = True
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_graph = typ_graph

        self.mode = "slider"
        self.lst_comp_wgt = list()
        self.lst_slid_graph, self.lst_comp_graph = list(), list()

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/graphResult.ui'), self)
        self.graph_obj = GraphResult(self, self.lay_graph, self.lay_graph_tbar)
        self.id_branch, self.id_pknum = None, None

        self.lst_runs = list()
        self.lst_graph = list()
        self.lst_obs = dict()
        self.lst_debord = dict()
        self.cur_data = dict()

        self.old_lst_run_score = list()
        self.laisses = dict()

        self.btn_add_graph.clicked.connect(self.add_wgt_compare)
        self.btn_del_graph.clicked.connect(self.del_wgt_compare)

        if self.checkrun():
            self.btn_add_graph.setEnabled(True)

            if self.typ_graph in ["struct", "weirs"]:
                self.typ_res = self.typ_graph
                self.x_var = "time"
            elif self.typ_graph in ["hydro", "hydro_pk"]:
                self.typ_res = "opt"
                if self.typ_graph == "hydro_pk":
                    self.x_var = "pknum"
                else:
                    self.x_var = "time"
            elif self.typ_graph in ["hydro_basin", "hydro_link"]:
                self.typ_res = self.typ_graph.replace("hydro_", "")
                self.x_var = "time"

            if self.x_var == "pknum":
                self.sql_where = "results.time = {2}"
                self.id_branch = id
            elif self.x_var == "time":
                self.sql_where = "results.pknum = {1}"
                self.id_pknum = id

            self.tw_mode.currentChanged.connect(self.graph_mode_changed)
            self.bt_expCsv.clicked.connect(self.export_csv)
            self.cc_scores.stateChanged.connect(self.ch_score)

            self.stw_res.setCurrentIndex(0)
            self.cl_scores = ClassScoresResDialog(self)
            self.disable_score()

            self.dict_run = self.init_dico_run()

            self.curve_selector = SlideCurveSelectorWidget(self.mgis, 0,
                                                           self.typ_graph,
                                                           self.typ_res,
                                                           self.x_var,
                                                           self.dict_run,
                                                           self.id_pknum,
                                                           self.id_branch)
            self.curve_selector.cur_scen_edited.connect(self.clean_score)
            self.curve_selector.graph_parameters_edited.connect(
                self.slider_graph_edited)
            self.curve_selector.init_run()
            self.lay_sel_curve.addWidget(self.curve_selector)

            self.add_wgt_compare()

            self.initialising = False
            self.update_graph()

    def add_wgt_compare(self):
        """
        compare mode widget
        :return:
        """
        param_init, param_date = dict(), dict()
        idx = len(self.lst_comp_wgt)
        if idx:
            param_init = self.lst_comp_wgt[-1].param_graph
            param_date = {"display": self.lst_comp_wgt[-1].init_date_displayed,
                          "need": self.lst_comp_wgt[-1].init_date_needed,
                          "init": self.lst_comp_wgt[
                              -1].ctrl_date_init.dateTime()}

        if 'graph' not in param_init.keys() and idx > 0:
            QMessageBox.warning(None, 'Error',
                                'Last chart is empty.')
            return
        itm = QListWidgetItem()
        itm.setSizeHint(QSize(0, 22))
        self.lw_graph.addItem(itm)


        wgt = CompareCurveSelectorWidget(self.mgis, idx, self.typ_graph,
                                         self.typ_res, self.x_var,
                                         self.dict_run, self.id_pknum,
                                         self.id_branch)
        self.lst_comp_wgt.append(wgt)
        self.lw_graph.setItemWidget(itm, wgt)
        self.lst_comp_graph.append(None)

        wgt.graph_parameters_edited.connect(self.compar_graph_edited)
        wgt.init_run(param_init, param_date)

        if idx == 3:
            self.btn_add_graph.setEnabled(False)
        else:
            self.btn_add_graph.setEnabled(True)

        if idx == 0:
            self.btn_del_graph.setEnabled(False)
        else:
            self.btn_del_graph.setEnabled(True)

    def del_wgt_compare(self):
        """
        del graphic in compare mode
        :return:
        """
        idx = self.lw_graph.currentRow()
        if idx != -1:
            self.lw_graph.takeItem(idx)
            del self.lst_comp_wgt[idx]
            del self.lst_comp_graph[idx]
            for wgt in self.lst_comp_wgt[idx:]:
                wgt.row -= 1

            if self.x_var == "time":
                self.compar_graph_verif_date()
            self.update_graph()
        else:
            QMessageBox.warning(None, 'warning',
                                'No chart selected.')

        if len(self.lst_comp_graph) == 4:
            self.btn_add_graph.setEnabled(False)
        else:
            self.btn_add_graph.setEnabled(True)

        if len(self.lst_comp_graph) == 1:
            self.btn_del_graph.setEnabled(False)
        else:
            self.btn_del_graph.setEnabled(True)

    def graph_mode_changed(self, idx):
        """
        change mode graphic
        :param idx: index
        :return:
        """
        if idx == 0:
            self.mode = "slider"
        elif idx == 1:
            self.mode = "compar"
        self.update_graph()

    def slider_graph_edited(self, idx, param):
        """
        slider management
        :param idx: index
        :param param: dict of paramater
        :return:
        """
        self.lst_slid_graph = [param]
        if not self.initialising:
            self.update_graph()

    def compar_graph_edited(self, idx, param):
        """ edit of  compare mode """
        self.lst_comp_graph[idx] = param

        if not self.initialising:
            if self.x_var == "time":
                self.compar_graph_verif_date()
            self.update_graph()

    def compar_graph_verif_date(self):
        """
        check date of  compare mode
        :return:
        """
        date_multi_format = False
        graph_with_date, graph_with_no_date = list(), list()
        date_ref = None
        for g, graph in enumerate(self.lst_comp_graph):
            if graph:
                rows = self.mdb.run_query(
                    "SELECT init_date FROM {0}.runs WHERE id = {1}".format(
                        self.mdb.SCHEMA, graph["scen"]), fetch=True)
                if rows[0][0]:
                    graph_with_date.append((g, rows[0][0]))
                    if not date_ref: date_ref = rows[0][0]
                else:
                    graph_with_no_date.append(g)

        if graph_with_date and graph_with_no_date:
            date_multi_format = True

        if date_multi_format:
            for (g, d) in graph_with_date:
                self.lst_comp_wgt[g].show_init_date(False, d)
            for g in graph_with_no_date:
                self.lst_comp_wgt[g].show_init_date(True, date_ref)
        else:
            for wgt in self.lst_comp_wgt:
                wgt.hide_init_date()

        for w, wgt in enumerate(self.lst_comp_wgt):
            self.lst_comp_graph[w]["init_date"] = wgt.param_graph["init_date"]

    def update_graph(self):
        """
        update graphic
        :return:
        """
        self.lst_graph.clear()
        if self.mode == "slider":
            lst_graph = self.lst_slid_graph
        else:
            lst_graph = self.lst_comp_graph
        self.lst_graph = [graph for graph in lst_graph if
                          "graph" in graph.keys()]

        lst_unit, lst_name = {1: list(), 2: list()}, {1: list(), 2: list()}
        lst_var, lst_lbl, lst_col, lst_lin, lst_axe = list(), list(), list(), list(), list()

        n_graph = len(self.lst_graph)
        for g, graph in enumerate(self.lst_graph):
            lst_unit[graph["axe"]].append(graph["graph"]["unit"])
            lst_name[graph["axe"]].append(graph["graph"]["name"])
            for var in graph["graph"]["vars"]:
                lbl, col = self.get_var_info(var)
                lst_var.append(var)
                lst_col.append(col)
                lst_lin.append(g)
                lst_axe.append(graph["axe"])
                if n_graph > 1:
                    lst_lbl.append("[{}] {}".format(g + 1, lbl))
                else:
                    lst_lbl.append(lbl)

        title_y, unit_y = [None, None], [None, None]
        for ax in [1, 2]:
            if lst_name[ax]:
                dist_title = list(set(lst_name[ax]))
                title_y[ax - 1] = dist_title[0] if len(
                    dist_title) == 1 else "Various"
            if lst_unit[ax]:
                dist_unit = list(set(lst_unit[ax]))
                unit_y[ax - 1] = dist_unit[0] if len(dist_unit) == 1 else ""

        self.graph_obj.update_limites = True
        self.graph_obj.init_mdl(lst_var, lst_lbl, lst_col, lst_lin, lst_axe,
                                unit_y, title_y)
        self.graph_obj.maj_limites()

        self.update_data(lst_var)

    def get_var_info(self, var):
        """
        get information variable dict
        :param var: name var
        :return:
        """
        if var.lower() in self.mgis.variables.keys():
            return self.mgis.variables[var.lower()]['nom'], \
                   self.mgis.variables[var.lower()]['couleur']
        else:
            return "", "blue"

    def ch_score(self):
        """ change tab for score"""
        if self.cc_scores.isChecked():
            self.stw_res.setCurrentIndex(1)
        else:
            self.stw_res.setCurrentIndex(0)

    def checkrun(self):
        """
        check if there is run
        :return:
        """
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs "
                                  "WHERE id in (SELECT DISTINCT id_runs FROM {0}.runs_graph) "
                                  "ORDER BY run, scenario ".format(
            self.mdb.SCHEMA), fetch=True)

        if rows:
            return True
        else:
            self.mgis.add_info("No data.")
            return False

    def init_dico_run(self):
        """
        initialize dico_run
        :return: dico_run
        """
        dict_run = dict()
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs "
                                  "WHERE id in (SELECT DISTINCT id_runs FROM {0}.runs_graph) "
                                  "ORDER BY date DESC, run ASC, scenario ASC;".format(
            self.mdb.SCHEMA), fetch=True)
        for row in rows:
            if row[1] not in dict_run.keys():
                dict_run[row[1]] = dict()
            dict_run[row[1]][row[2]] = row[0]

        return dict_run

    def clear_results(self):
        """ clear graphic"""
        self.cur_data.clear()
        self.graph_obj.fig.clf()
        self.graph_obj.canvas.draw()
        self.clas_data.clear()

    def update_data(self, lst_var):
        """
        update data graph
        :return:
        """
        if not self.initialising:
            self.cur_data = list()
            if lst_var is None:
                self.clear_results()
                self.mgis.add_info('No Data')
                return

            for param in self.lst_graph:
                tmp_data = dict()
                tmp_data["name"] = param["graph"]["name"]
                tmp_data["is_obs"] = False
                tmp_data["x_var"] = self.x_var
                tmp_data["y_var"] = param["graph"]["vars"]
                tmp_data["y_unit"] = param["graph"]["unit"]

                sql_hyd_pk = ''
                if self.typ_graph == 'hydro_pk':
                    sql_hyd_pk = "AND pknum IN (SELECT pk FROM {0}.results_sect " \
                                 "WHERE id_runs = {1} AND branch = {2})".format(
                        self.mgis.mdb.SCHEMA, param["scen"], param["branch"])
                sqlw = self.sql_where.format(param["branch"], param["pknum"],
                                             param["t"])

                if self.x_var == 'time':
                    if self.typ_graph in ['struct', 'weirs']:
                        x_val = None
                        if self.typ_res in param["info_graph"].keys():
                            for id_config in param["info_graph"][self.typ_res][
                                'pknum'].keys():
                                if param["info_graph"][self.typ_res]['pknum'][
                                    id_config] == param["pknum"]:
                                    x_val = \
                                        param["info_graph"][self.typ_res][
                                            'time'][
                                            id_config]
                        if not x_val:
                            x_val = param["info_graph"]['opt']['time']
                        if "init_date" in param.keys():
                            date = param["init_date"]
                        else:
                            date = None
                    else:
                        x_val = param["info_graph"][self.typ_res]['time']

                        date = param["init_date"]
                    sql = "SELECT init_date FROM {0}.runs WHERE id = {1} ".format(
                        self.mgis.mdb.SCHEMA, param["scen"])
                    info = self.mdb.run_query(sql, fetch=True)
                    if info:
                        if info[0][0]:
                            date = info[0][0]

                    if date:
                        tmp_data["x_var"] = "date"
                        tmp_data["date"] = [date + timedelta(seconds=row) for
                                            row in x_val]

                elif self.x_var == 'pknum':
                    if self.typ_graph == 'hydro_pk':
                        sql = "SELECT pk FROM {0}.results_sect WHERE id_runs = {1} AND branch = {2} " \
                              "ORDER BY pk".format(self.mgis.mdb.SCHEMA,
                                                   param["scen"],
                                                   param["branch"])
                        rows = self.mdb.run_query(sql, fetch=True)
                        x_val = [row[0] for row in rows]
                    else:
                        x_val = param["info_graph"][self.typ_res]['pknum']

                else:
                    sqlv = "('{}')".format("', '".join(param["vars"]))
                    sql = "SELECT DISTINCT {1} FROM {0}.results WHERE id_runs = {2} AND {4} AND var IN " \
                          "(SELECT id FROM {0}.results_var WHERE var in {3}) {5} " \
                          "ORDER BY {1}".format(self.mgis.mdb.SCHEMA,
                                                self.x_var, param["scen"], sqlv,
                                                sqlw, sql_hyd_pk)
                    rows = self.mdb.run_query(sql, fetch=True)
                    x_val = [row[0] for row in rows]

                tmp_data[self.x_var] = x_val

                for var in param["graph"]["vars"]:
                    sql = "SELECT {1}, val FROM {0}.results WHERE id_runs = {2} AND " \
                          "var IN (SELECT id FROM {0}.results_var WHERE results_var.var = '{3}') AND {4} {5} " \
                          "ORDER BY {1}".format(self.mgis.mdb.SCHEMA,
                                                self.x_var, param["scen"], var,
                                                sqlw, sql_hyd_pk)
                    rows = self.mdb.run_query(sql, fetch=True)
                    tmp_data[var] = [row[1] for row in rows]

                self.cur_data.append(tmp_data)

            lst_x_var = list(set([d["x_var"] for d in self.cur_data]))
            if len(lst_x_var) == 1:
                x_var_ = lst_x_var[0]
                if x_var_ == 'time':
                    self.graph_obj.unit_x = 'time'
                    self.graph_obj.ax[1]["axe"].set_xlabel(r'Time ($s$)')
                elif x_var_ == 'date':
                    self.graph_obj.unit_x = 'date'
                    self.graph_obj.ax[1]["axe"].set_xlabel(r'Time')
                elif x_var_ == 'pknum':
                    self.graph_obj.unit_x = 'pk'
                    self.graph_obj.ax[1]["axe"].set_xlabel(r'Pk ($m$)')
            else:
                self.clear_results()
                return

            if self.typ_graph == "hydro":
                self.update_obs(x_var_)
                if self.lst_obs:
                    self.graph_obj.insert_obs_curves(self.lst_obs)

            if self.typ_graph == "hydro_pk":
                self.update_debord(x_var_)
                if self.lst_debord:
                    self.graph_obj.insert_debord_curves(self.lst_debord)
            self.update_title()
            self.fill_tab()

            self.graph_obj.clear_laisse()
            lais_g = False
            if self.mode == "slider":
                if self.typ_graph in ["hydro", "hydro_pk"]:
                    if 'Z' in self.lst_graph[0]["graph"]["vars"]:
                        self.get_laisses(self.lst_graph[0])
                        lais_g = self.update_laisse(x_var_, self.cur_data[0])

            self.graph_obj.init_graph(self.cur_data, x_var_, lais=lais_g)

    def update_title(self):
        """ update graph title"""
        if self.mode == "slider":
            lst_title = [self.curve_selector.cb_det.currentText()]
        elif self.mode == "compar":
            lst_title = list(
                set([wgt.cb_det.currentText() for wgt in self.lst_comp_wgt]))
        lst_branch = list(set([graph["branch"] for graph in self.lst_graph]))

        if len(lst_title) == 1:
            txt_title = lst_title[0]
            if self.typ_graph in ["struct", "weirs", "hydro"]:
                try:
                    self.graph_obj.main_axe.title.set_text(
                        r'Profile - {0} m'.format(float(txt_title)))
                except ValueError:
                    list_txt = txt_title.split(':')
                    if len(list_txt) > 1:
                        self.graph_obj.main_axe.title.set_text(
                            r'Profile {1} - {0} m '.format(list_txt[0],
                                                           list_txt[1]))
            elif self.typ_graph == "hydro_pk":
                if len(lst_branch) == 1:
                    try:
                        self.graph_obj.main_axe.title.set_text(
                            r'Branch {0} - {1} $s$'.format(lst_branch[0],
                                                           float(txt_title)))
                    except ValueError:
                        self.graph_obj.main_axe.title.set_text(
                            r'Branch {0} - {1}'.format(lst_branch[0],
                                                       txt_title))
            elif self.typ_graph == "hydro_basin":
                self.graph_obj.main_axe.title.set_text(
                    r'Basin - {0}'.format(txt_title))
            elif self.typ_graph == "hydro_link":
                self.graph_obj.main_axe.title.set_text(
                    r'Link - {0}'.format(txt_title))
        else:
            self.graph_obj.main_axe.title.set_text(r"")

    def update_debord(self, x_var_):
        """
         update debord variable
        :param x_var_: name of axis variable
        :return:
        """
        for g, param in enumerate(self.lst_graph):
            vars = param["graph"]["vars"]
            var = None
            axe = None
            if "Z" in vars:
                var = 'H'
                axe = param["axe"]
                break
        self.lst_debord.clear()
        if x_var_ == 'pknum' and var:
            fill_zminbed(self.mdb)
            id_branch = self.lst_graph[0]["branch"]
            dict_data = self.mdb.select('profiles',
                                        where='zleftminbed IS NOT NULL '
                                              'AND zrightminbed IS NOT NULL AND active AND '
                                              'branchnum = {}'.format(
                                            id_branch),
                                        order='abscissa',
                                        list_var=['gid', 'name', 'abscissa',
                                                  'zleftminbed',
                                                  'zrightminbed'])

            curve = {}
            if dict_data:
                curve['x'] = []
                curve['y'] = {'left': [], 'right': []}

                for idx, gid in enumerate(dict_data['gid']):
                    curve['x'].append(dict_data['abscissa'][idx])
                    curve['y']['left'].append(dict_data['zleftminbed'][idx])
                    curve['y']['right'].append(dict_data['zrightminbed'][idx])

                for cote in ['left', 'right']:
                    tmp_data = dict()
                    tmp_data["x_var"] = 'pknum'
                    tmp_data["y_var"] = [var]
                    tmp_data["y_unit"] = "$m$"
                    tmp_data["is_obs"] = True
                    tmp_data["name"] = "overflow level - {0} ".format(cote)
                    tmp_data["pknum"] = curve['x']
                    tmp_data[var] = curve['y'][cote]
                    self.lst_debord[(cote, var)] = {"axe": axe,
                                                    "name": cote}
                    self.cur_data.append(tmp_data)

    def update_obs(self, x_var_):
        """
        update observation variable
        :param x_var_: name of axis variable
        :return:
        """
        dict_pk_obs = dict()
        for g, param in enumerate(self.lst_graph):
            pk, vars = param["pknum"], param["graph"]["vars"]
            var = None
            if "Z" in vars:
                var = 'H'
            elif "Q" in vars:
                var = 'Q'

            if var:
                if x_var_ == 'date':
                    date_min = min(self.cur_data[g]["date"])
                    date_max = max(self.cur_data[g]["date"])
                    if (pk, var) not in dict_pk_obs.keys():
                        dict_pk_obs[(pk, var)] = {"min": date_min,
                                                  "max": date_max}
                    else:
                        if date_min < dict_pk_obs[(pk, var)]["min"]:
                            dict_pk_obs[(pk, var)]["min"] = date_min
                        if date_max > dict_pk_obs[(pk, var)]["max"]:
                            dict_pk_obs[(pk, var)]["max"] = date_max
                else:
                    dict_pk_obs[(pk, var)] = {"min": None, "max": None}

        dict_obs = dict()
        for g, param in enumerate(self.lst_graph):
            pk, vars = param["pknum"], param["graph"]["vars"]
            var = None
            if "Z" in vars:
                var = 'H'
            elif "Q" in vars:
                var = 'Q'

            if var:
                sql = "SELECT name FROM {0}.profiles WHERE abscissa={1} ".format(
                    self.mdb.SCHEMA, pk)
                rows = self.mdb.run_query(sql, fetch=True)
                if rows:
                    val = rows[0][0]
                    d_obs = self.mgis.mdb.select('outputs',
                                                 where="active AND (abscissa = {0} OR name = '{1}')".format(
                                                     pk, val),
                                                 order="abscissa",
                                                 list_var=['code', 'zero',
                                                           'abscissa', 'name'])
                    for o, obs in enumerate(d_obs['code']):
                        if obs and len(obs) != 0:
                            if (obs, var) not in dict_obs.keys():
                                dict_obs[(obs, var)] = {
                                    "name": d_obs['name'][o],
                                    "abs": d_obs['abscissa'][o],
                                    "zero": d_obs['zero'][o], "pk": pk,
                                    "axe": param["axe"],
                                    "date_min": dict_pk_obs[(pk, var)]["min"],
                                    "date_max": dict_pk_obs[(pk, var)]["max"]}

        if not dict_obs:
            self.disable_score()
        else:
            self.score(dict_obs)

        self.lst_obs.clear()
        if x_var_ == 'date':
            for (id_obs, var), param_obs in dict_obs.items():
                condition = """code = '{0}' AND date>='{1}' AND date<='{2}' AND type='{3}' 
                AND valeur > -999.9""".format(id_obs, param_obs["date_min"],
                                              param_obs["date_max"], var)
                obs_graph = self.mdb.select("observations", condition, "date")

                if len(obs_graph["valeur"]) != 0:
                    self.lst_obs[(obs, var)] = param_obs
                    tmp_data = dict()
                    tmp_data["name"] = "Obs {0} - {1}".format(obs, var)
                    tmp_data["is_obs"] = True
                    tmp_data["x_var"] = "date"
                    tmp_data["y_var"] = [var]
                    tmp_data["y_unit"] = "$m$"
                    tmp_data["date"] = obs_graph['date']
                    if var == "H":
                        tmp_data[var] = [v + param_obs["zero"] for v in
                                         obs_graph['valeur']]
                    else:
                        tmp_data[var] = obs_graph['valeur']
                    self.cur_data.append(tmp_data)

    def score(self, dict_obs):
        """
        score management
        :param dict_obs: dict() observation info
        :return:
        """
        self.cc_scores.setEnabled(True)
        # self.lst_runs = list(set([g["scen"] for g in self.lst_graph]))
        # pks = {id: [] for id in self.lst_runs}
        obs_pk = list(set([g['pk'] for k, g in dict_obs.items()]))
        pks = {}
        lst_runs = []
        for param in self.lst_graph:
            if param["pknum"] in obs_pk:
                if param["scen"] in pks.keys():
                    pks[param["scen"]].append(param["pknum"])
                    lst_runs.append(param["scen"])
                else:
                    pks[param["scen"]] = [param["pknum"]]
                    lst_runs.append(param["scen"])

        if pks != self.cl_scores.wgt_param.dict_pk and pks:
            self.cl_scores.wgt_param.ch_lst_run(lst_runs)
            self.cl_scores.wgt_param.ch_dict_pk(pks)
            self.cl_scores.wgt_param.init_gui()

    def fill_tab(self):
        """
        fill table in GUI
        :return:
        """
        self.clas_data.clear()
        for idx, param in enumerate(self.cur_data):
            tw = QTableWidget()
            tw.addAction(CopySelectedCellsAction(tw))

            if len(self.lst_graph) == 1:
                self.clas_data.addTab(tw, param["name"])
            else:
                if param["is_obs"]:
                    self.clas_data.addTab(tw, param["name"])
                else:
                    self.clas_data.addTab(tw, "[{}] {}".format(idx + 1,
                                                               param["name"]))

            tw.setColumnCount(0)
            nbcol = len(param["y_var"]) + 1
            tw.setColumnCount(nbcol)
            tw.setRowCount(0)
            tw.setRowCount(len(param[param["x_var"]]))

            lst_vars = [param["x_var"]]
            lst_vars.extend(param["y_var"])
            lst_lbls = [param["x_var"].title()]
            for var in param["y_var"]:
                if var in ["H", "Q"]:
                    lbl = var
                else:
                    lbl, _ = self.get_var_info(var)
                lst_lbls.append(lbl)

            for c, var in enumerate(lst_vars):
                tw.setHorizontalHeaderItem(c, QTableWidgetItem(lst_lbls[c]))
                for r, val in enumerate(param[var]):
                    if var == "date":
                        val = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(val,
                                                                     val.microsecond / 10000.0)
                    itm = QTableWidgetItem()
                    itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    itm.setData(0, val)
                    tw.setItem(r, c, itm)

            tw.setVisible(False)
            tw.resizeColumnsToContents()
            tw.resizeRowsToContents()
            tw.setVisible(True)
            self.clas_data.setCurrentIndex(idx)
        self.clas_data.setCurrentIndex(0)

    def get_laisses(self, param):
        """
        get flood marks data
        :return:
        """
        info = self.mdb.select('runs', where="id={} ".format(param["scen"]),
                               list_var=['scenario'])
        condition = "event = '{}' AND active AND z is not null ".format(
            info["scenario"][0])
        if self.typ_graph == "hydro":
            condition += "AND abscissa = {} ".format(param["pknum"])

        self.laisses = self.mdb.select("flood_marks", condition, "abscissa")
        if self.laisses:
            self.laisses['pknum'] = self.laisses['abscissa']

    def update_laisse(self, var_x, cur_data):
        """
        To graph the flood mark
        :param var_x:  name of axis variable
        :param cur_data: dict() curent data
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
            if 'ZMAX' in cur_data.keys():
                courbe_lais["couleurs"] = []
                courbe_lais["taille"] = []
                if "pknum" in cur_data.keys():
                    key_val = "pknum"
                elif "date" in cur_data.keys():
                    key_val = "date"
                for x, z in zip(courbe_lais["x"], courbe_lais["z"]):
                    if key_val == "date":
                        x_cur_data = [datetime.timestamp(t) for t in
                                      cur_data[key_val]]
                        x_inter = datetime.timestamp(
                            datetime(*x.timetuple()[:-4]))
                    else:
                        x_cur_data = cur_data[key_val]
                        x_inter = x
                    val = interpole(x_inter, x_cur_data, cur_data['ZMAX'])

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

    def clean_score(self):
        """
        clean scores
        """
        self.cl_scores.clear_scores()
        self.cc_scores.setChecked(False)

    def disable_score(self):
        """ disable scores """
        self.clean_score()
        self.cc_scores.setEnabled(False)

    def export_csv(self):
        """Export Table to .CSV file"""

        # txt = self.cb_graph.currentText()
        txt = "text"
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
            cur_tw = self.clas_data.currentWidget()
            range_r = range(0, cur_tw.rowCount())
            range_c = range(0, cur_tw.columnCount())
            clipboard = tw_to_txt(cur_tw, range_r, range_c, ';')
            file = open(file_name_path, 'w')
            file.write(clipboard)
            file.close()

            # =======================================================================

    def copier(self, tw):
        """copier la zone sélectionnée dans le clipboard
        """
        # emplacement sélectionné pour copier dans le clipboard
        selected = tw.selectedRanges()

        # construction du texte à copier, ligne par ligne et colonne par colonne
        texte = ""
        for i in range(selected[0].topRow(), selected[0].bottomRow() + 1):
            for j in range(selected[0].leftColumn(),
                           selected[0].rightColumn() + 1):
                try:
                    texte += tw.item(i, j).text() + "\t"
                except AttributeError:
                    # quand une case n'a jamais été initialisée
                    texte += "\t"
            texte = texte[:-1] + "\n"  # le [:-1] élimine le '\t' en trop

        # enregistrement dans le clipboard
        QtGui.QApplication.clipboard().setText(texte)


class CopySelectedCellsAction(QAction):
    def __init__(self, table_widget):
        if not isinstance(table_widget, QTableWidget):
            chaine = """CopySelectedCellsAction must be initialised with
                     a QTableWidget. A {0} was given."""
            raise ValueError(chaine.format(type(table_widget)))

        super(CopySelectedCellsAction, self).__init__('Copy', table_widget)
        self.setShortcut('Ctrl+C')
        self.triggered.connect(self.copy_cells_to_clipboard)
        self.table_widget = table_widget

    def copy_cells_to_clipboard(self):
        if len(self.table_widget.selectionModel().selectedIndexes()) > 0:
            lst_r = [idx.row() for idx in
                     self.table_widget.selectionModel().selectedIndexes()]
            lst_c = [idx.column() for idx in
                     self.table_widget.selectionModel().selectedIndexes()]
            range_r = range(min(lst_r), max(lst_r) + 1)
            range_c = range(min(lst_c), max(lst_c) + 1)
            clipboard = tw_to_txt(self.table_widget, range_r, range_c, '\t')

            sys_clip = QApplication.clipboard()
            sys_clip.setText(clipboard)
