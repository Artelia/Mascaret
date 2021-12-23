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
import json
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .GraphResult import GraphResult
from ..Function import tw_to_txt, fill_zminbed
from datetime import timedelta
from .ClassResProfil import ClassResProfil, get_valeurs
from shapely.geometry import shape
from .WidgetProfResultDialog import WidgetProfResultDialog
from shapely.ops import cascaded_union
from shapely.geometry import GeometryCollection


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


class GraphProfilResultDialog(QWidget):
    def __init__(self, mgis, typ_graph, id=None):
        QWidget.__init__(self)
        self.initialising = True
        self.mgis = mgis
        self.mdb = self.mgis.mdb

        self.typ_graph = typ_graph
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/graphProfilResult.ui'),
            self)
        self.graph_obj = GraphResult(self, self.lay_graph)
        self.cur_run, self.cur_graph, self.cur_vars = None, None, None
        self.cur_vars_lbl, self.cur_branch, self.cur_pknum, self.cur_t = None, None, None, None
        self.cur_id_tab = 0
        self.list_var_lai = []
        self.zmax_save = None
        self.val_zmax_save = None
        self.date = None
        self.obs = None
        self.list_typ_res = None
        self.recadre = True
        self.info_graph = {}
        self.val_prof_ref = {}
        self.plani_graph = {}
        self.cmpl_info = {}
        self.cas_prt = {}
        self.dict_run = dict()
        self.laisses = {}
        self.ctrl_label = {'area': self.label_warea,
                           'perimeter': self.label_wpermi,
                           'width': self.label_wmirror,
                           }

        fill_zminbed(self.mdb)
        self.show_hide_com(False)
        if self.checkrun():
            self.typ_res = 'opt'
            self.x_var = 'x'
            self.sql_where = "results.pknum = {1}"

            self.cur_pknum = id
            sql = "SELECT id FROM {0}.results_var WHERE var = 'Z'".format(
                self.mdb.SCHEMA)
            rows = self.mdb.run_query(sql, fetch=True)
            self.id_z = rows[0][0]
            sql = "SELECT id FROM {0}.results_var WHERE var = 'QMAJ'".format(
                self.mdb.SCHEMA)
            rows = self.mdb.run_query(sql, fetch=True)
            self.id_qmaj = rows[0][0]
            self.cur_t = "Zmax"
            self.get_profil_data()

            self.cb_run.currentIndexChanged.connect(self.run_changed)
            self.cb_scen.currentIndexChanged.connect(self.scen_changed)
            self.cb_graph.currentIndexChanged.connect(
                lambda: self.graph_changed_profil(True))
            self.cb_det.currentIndexChanged.connect(
                lambda: self.detail_changed(up_lim=False))

            self.name_tab = {'prof': {'name': 'Graph Results',
                                      'lst_vars': ['ZREF', 'Z']},
                             }
            self.curent_data = {'prof': {},
                                }

            # TODO Export
            self.bt_expCsv.clicked.connect(self.export_csv)

            self.lst_runs = []
            self.init_dico_run()

            self.initialising = False

            self.update_data_profil()
            self.initialising = False

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

    def get_profil_data(self):
        """ Get data of a profile"""
        if self.cur_run is not None:
            txt = self.mdb.select_distinct("comments", "runs",
                                           where='id={}'.format(self.cur_run))
            if txt:
                txt = txt['comments'][0]
                if not isinstance(txt, str):
                    txt = str(txt)
                self.lbl_coment.setText(txt['comments'][0])
                self.show_hide_com(True)
            else:
                self.show_hide_com(False)
        else:
            self.show_hide_com(False)
        prof = self.mdb.select('profiles', order='abscissa',
                               list_var=['abscissa', 'x', 'z', 'leftminbed',
                                         'rightminbed', 'leftstock',
                                         'rightstock', 'zleftminbed',
                                         'zrightminbed', 'branchnum'])
        self.val_prof_ref = {}
        self.plani_graph = {}
        if prof:
            for id, pk in enumerate(prof['abscissa']):
                if pk:
                    try:
                        self.val_prof_ref[pk] = {}
                        self.val_prof_ref[pk]['x'] = [float(v) for v in
                                                      prof['x'][id].split()]
                        self.val_prof_ref[pk]['ZREF'] = [float(v) for v in
                                                         prof['z'][id].split()]
                        self.val_prof_ref[pk]['leftminbed'] = \
                            prof['leftminbed'][id]
                        self.val_prof_ref[pk]['rightminbed'] = \
                            prof['rightminbed'][id]
                        self.val_prof_ref[pk]['leftstock'] = prof['leftstock'][
                            id]
                        self.val_prof_ref[pk]['rightstock'] = \
                            prof['rightstock'][id]
                        self.val_prof_ref[pk]['zleftminbed'] = \
                            prof['zleftminbed'][id]
                        self.val_prof_ref[pk]['zrightminbed'] = \
                            prof['zrightminbed'][id]
                        self.val_prof_ref[pk]['branch'] = prof['branchnum'][id]


                    except:
                        pass

    def get_profil_plani(self):
        self.plani_graph = {}
        for pk, info in self.val_prof_ref.items():
            # print(info.keys(),pk)
            if info:
                x = info['x']
                z = info['ZREF']
                profil = list(zip(x, z))

                min_bed = [info['leftminbed'],
                           info['rightminbed']]
                if info['leftstock'] and \
                        info['rightstock']:
                    maj_bed = [info['leftstock'],
                               info['rightstock']]
                else:
                    maj_bed = [x[0],
                               x[-1]]

                cond_plani, dico_plani = self.check_run_plani(pk)
                # cond_plani  = False
                self.plani_graph[pk] = {}
                if cond_plani:
                    cl_geo = ClassResProfil()
                    self.cas_prt = cl_geo.cas_prt
                    cl_geo.init_cl(pk, profil,
                                   info['branch'],
                                   min_bed, maj_bed, self.cur_run,
                                   zmax=self.zmax_save,
                                   dico_plani=dico_plani,
                                   database=self.mdb)

                    cl_geo.get_results()
                    if cl_geo.dico_res:
                        for id, name in cl_geo.cas_prt.items():
                            if id in cl_geo.dico_res.keys():
                                self.plani_graph[pk][name] = dict(
                                    cl_geo.dico_res[id])

                    del cl_geo

    def get_run_plani(self, pk, get_bas=False):
        where = 'id_runs = {} AND pknum = {}'.format(self.cur_run, pk)
        elem_plani = self.mdb.select('runs_plani', order='id_type,id_order',
                                     where=where,
                                     list_var=['id_type', 'id_order',
                                               'ST_AsGeoJSON(line)'])

        if get_bas:
            where = "id_runs = {0} AND var = 'pt_bas' AND type_res = 'opt'".format(
                self.cur_run)

            elem = self.mdb.select('runs_graph', order='id',
                                   where=where,
                                   list_var=['val'])

            if len(elem['val']) > 0:
                self.info_graph['opt']['pt_bas'] = elem['val'][0]
            else:
                self.info_graph['opt']['pt_bas'] = {}

        return elem_plani

    def create_dico_plani(self, elem, pt_bas):

        dico_plani = {}
        for id, id_type in enumerate(elem['id_type']):
            if not id_type in dico_plani.keys():
                dico_plani[id_type] = {'pt_bas': pt_bas[str(id_type)],
                                       'line': []}
                # st_asgeojson eqv. line
            dico_plani[id_type]['line'].append(
                shape(json.loads(elem['st_asgeojson'][id])))

        return dico_plani

    def check_run_plani(self, pk):

        pt_bas = None
        elem = self.get_run_plani(pk)

        if 'pt_bas' in self.info_graph['opt'].keys():
            if str(pk) in self.info_graph['opt']['pt_bas'].keys():
                pt_bas = self.info_graph['opt']['pt_bas'][str(pk)]

        if len(elem['id_type']) > 0 and pt_bas:
            dico_plani = self.create_dico_plani(elem, pt_bas)
        else:

            if not 'pt_bas' in self.info_graph['opt'].keys():
                # if pt_bas not existe => update table
                cond = True
            else:
                if len(self.info_graph['opt']['pt_bas'].keys()) < 1:
                    # if  no itmes => update table
                    cond = True
                else:
                    # no need to update  table because of the items are not able to existe
                    cond = False

            if cond:
                # creation Complete table si information n'existat pour le run
                cl_geo = ClassResProfil()
                self.cas_prt = cl_geo.cas_prt
                cl_geo.plani_stock(self.info_graph[self.typ_res]['zmax'],
                                   self.cur_run, self.mdb)
                del cl_geo

                elem = self.get_run_plani(pk, get_bas=True)
                pt_bas = None

                if str(pk) in self.info_graph['opt']['pt_bas'].keys():
                    if str(pk) in self.info_graph['opt']['pt_bas'].keys():
                        pt_bas = self.info_graph['opt']['pt_bas'][str(pk)]

                if len(elem['id_type']) > 0 and pt_bas:
                    dico_plani = self.create_dico_plani(elem, pt_bas)
                else:
                    # Pas de valeur pour le pk
                    return False, None
            else:
                # Pas de valeur pour le pk en cours
                return False, None

        return True, dico_plani

    def get_runs_graph(self):
        sql = "SELECT type_res,var,val FROM {0}.runs_graph WHERE " \
              "id_runs = {1} ORDER BY id".format(self.mdb.SCHEMA,
                                                 self.cur_run)

        rows = self.mdb.run_query(sql, fetch=True)

        self.info_graph = {}
        for i, row in enumerate(rows):
            if row[0] in self.info_graph.keys():
                self.info_graph[row[0]][row[1]] = row[2]
            else:
                self.info_graph[row[0]] = {row[1]: row[2]}

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

        lst_graph = []
        info = self.mdb.select('profiles', list_var=['abscissa', "name"])
        for pknum in self.info_graph['opt']['pknum']:
            if pknum in info['abscissa']:
                txt = str(pknum) + ' : ' + info['name'][
                    info['abscissa'].index(pknum)]
                lst_graph.append({"name": txt, 'id': float(pknum)})
                # else:
                #     lst_graph.append({"name": str(pknum), 'id': float(pknum)})
        self.lst_graph = lst_graph
        for i, graph in enumerate(lst_graph):
            self.cb_graph.addItem(graph["name"], graph["id"])
        self.cb_graph.setCurrentIndex(
            self.cb_graph.findData(self.cur_pknum))
        self.cb_graph.blockSignals(False)

    def init_cb_det(self, id):
        self.cb_det.blockSignals(True)
        self.cb_det.clear()

        sql = "SELECT init_date FROM {0}.runs " \
              "WHERE id = {1} ".format(self.mgis.mdb.SCHEMA,
                                       self.cur_run)
        info = self.mdb.run_query(sql, fetch=True)
        if info:
            self.date = info[0][0]
        else:
            self.date = None
        if self.typ_graph == 'hydro_profil':
            self.cb_det.addItem("Zmax", "Zmax")

        for time_ in self.info_graph['opt']['time']:
            if self.date:
                aff = self.date + timedelta(seconds=time_)
                aff = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(aff,
                                                             aff.microsecond / 10000.0)
            else:
                aff = str(time_)
            self.cb_det.addItem(aff, time_)

        self.cb_det.setCurrentIndex(0)
        self.cur_t = self.cb_det.itemData(self.cb_det.currentIndex())

        if self.cb_det.count() == 0:
            self.graph_obj.main_axe.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clearContents()
        else:
            self.sld_det.setMaximum(self.cb_det.count() - 1)
        self.cb_det.blockSignals(False)

    def run_changed(self):
        """ change fct for cb_run"""
        self.graph_obj.update_limites = True
        self.cb_scen.blockSignals(True)
        self.init_cb_scen()
        self.scen_changed()
        self.cb_scen.blockSignals(False)

    def scen_changed(self):
        """ change scen"""
        self.graph_obj.update_limites = True
        if self.cb_scen.currentIndex() != -1:
            self.cur_run = self.cb_scen.itemData(self.cb_scen.currentIndex())
            self.get_runs_graph()
            self.get_profil_plani()
            self.init_cb_graph()
            self.graph_changed_profil(False)
            self.init_cb_det(self.cur_pknum)
            self.detail_changed()

    def graph_changed_profil(self, update=True):
        """change graph of profile"""
        self.graph_obj.update_limites = True
        if self.cb_graph.currentIndex() != -1:
            self.cur_pknum = self.cb_graph.itemData(
                self.cb_graph.currentIndex())
            self.cur_vars = ['ZREF']
            lst_colors = ['black']
            self.cur_vars_lbl = self.find_var_lbl()

            self.graph_obj.init_mdl(self.cur_vars, self.cur_vars_lbl,
                                    lst_colors, [0], [1], 'm')
            self.zmax_save = None
            if self.cur_run:
                if 'zmax' in self.info_graph[self.typ_res].keys():
                    self.zmax_save = self.info_graph[self.typ_res]['zmax'][
                        str(self.cur_pknum)]
                    new_poly = GeometryCollection()

                    qmaj_max = self.get_qmaj_max()

                    for i, key in enumerate(
                            self.plani_graph[self.cur_pknum].keys()):
                        if i == 0:
                            new_poly = self.plani_graph[self.cur_pknum][key][
                                'pr_poly']
                            if new_poly.is_valid and not new_poly.is_empty:
                                last_poly = new_poly
                        else:
                            # check if flow major_bed
                            if qmaj_max > 0.001:
                                new_poly = cascaded_union([last_poly,
                                                           self.plani_graph[
                                                               self.cur_pknum][
                                                               key][
                                                               'pr_poly']])
                                if new_poly.is_valid and not new_poly.is_empty:
                                    last_poly = new_poly
                    # save max
                    self.val_zmax_save = get_valeurs(self.zmax_save, new_poly)

            if update:
                self.update_data_profil()
        else:
            self.graph_obj.main_axe.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clear()

    def detail_changed(self, up_lim=True):
        """ change pk or data"""
        self.graph_obj.update_limites = up_lim
        if self.cb_det.currentIndex() != -1:
            self.cur_t = self.cb_det.itemData(self.cb_det.currentIndex())
            self.sld_det.setValue(self.cb_det.currentIndex())
            self.update_data_profil()
        else:
            self.graph_obj.main_axe.cla()
            self.graph_obj.canvas.draw()
            self.tw_data.clear()

    def get_qmaj_max(self):
        """
        get Flowrate for Zmax
        :return:
        """
        where = "id_runs = {0} AND pknum = {1} " \
                "AND var ={2} ".format(self.cur_run,
                                       self.cur_pknum,
                                       self.id_qmaj)
        qmaj_max = self.mgis.mdb.select_max("val", 'results',
                                            where=where)
        return qmaj_max

    def update_data_profil(self):
        """
        update graph data for profile
        :return:
        """

        if not self.initialising:
            self.curent_data['prof'] = dict(self.val_prof_ref[self.cur_pknum])

            if self.cur_run:
                if self.cur_t == 'Zmax':
                    val = self.zmax_save
                    qmaj_max = self.get_qmaj_max()
                else:
                    where = "id_runs = {0} AND pknum = {1} " \
                            "AND var ={2} AND time = {3}".format(self.cur_run,
                                                                 self.cur_pknum,
                                                                 self.id_z,
                                                                 self.cur_t)
                    val = self.mgis.mdb.select('results', where=where,
                                               list_var=["val"])
                    if val:
                        val = val['val'][0]

                    where = "id_runs = {0} AND pknum = {1} " \
                            "AND var ={2} AND time = {3}".format(self.cur_run,
                                                                 self.cur_pknum,
                                                                 self.id_qmaj,
                                                                 self.cur_t)
                    qmaj_max = self.mgis.mdb.select_max("val", 'results',
                                                        where=where)

                self.curent_data['prof']['Z'] = [val] * len(
                    self.curent_data['prof']['x'])

                self.label_zmax.setText(str(self.zmax_save))
                self.cur_vars = ['ZREF', 'Z']

                self.cur_vars_lbl = self.find_var_lbl()

                if self.cur_t == 'Zmax':
                    zlevel = self.zmax_save
                    val_str = None
                    if self.zmax_save:
                        val_str = round(self.zmax_save, 3)
                    self.graph_obj.main_axe.title.set_text(
                        'Max of water level, {0} m '
                        ''.format(val_str))

                elif isinstance(self.cur_t, float):
                    zlevel = self.curent_data['prof']['Z'][0]
                    try:
                        self.graph_obj.main_axe.title.set_text(
                            'Water level, {0} m - {1} s'
                            ''.format(self.curent_data['prof']['Z'][0],
                                      float(self.cb_det.currentText())))
                    except ValueError:
                        self.graph_obj.main_axe.title.set_text(
                            'Water level, {0} m - {1}'
                            ''.format(self.curent_data['prof']['Z'][0],
                                      self.cb_det.currentText()))
                self.graph_obj.main_axe.set_xlabel(r'Distance ($m$)')
                self.graph_obj.main_axe.set_ylabel(r'Level ($m$)')

                # *******************************

                plani = False
                if self.plani_graph:
                    self.clear_plani_to_current_data()
                    self.curent_data.update(
                        dict(self.plani_graph[self.cur_pknum]))
                    self.graph_obj.init_graph_plani(
                        self.plani_graph[self.cur_pknum])
                    for key, ctrl_ in self.ctrl_label.items():
                        val_d = self.val_zmax_save[key]
                        if val_d:
                            val_d = str(round(val_d, 2))
                        ctrl_.setText(val_d)
                    plani = True
                # ********************************************
                self.fill_tab(zlevel, qmaj_max)
                self.graph_obj.init_graph_profil(self.curent_data['prof'],
                                                 self.x_var,
                                                 qmaj_max,
                                                 plani=plani)

    def clear_plani_to_current_data(self):
        for num, key in self.cas_prt.items():
            if key in self.curent_data.keys():
                del self.curent_data[key]

    def get_var_info(self, var):
        """
        Get variables name and color
        :param var: variable sigle
        :return:
        """
        if var.lower() in self.mgis.variables.keys():
            return self.mgis.variables[var.lower()]['nom'], \
                   self.mgis.variables[var.lower()]['couleur']
        else:
            return "", "blue"

    def fill_tab(self, zlevel, qmaj_max):
        self.cur_id_tab = self.clas_data.currentIndex()
        self.clas_data.clear()
        for idx, wow in enumerate(self.curent_data.items()):
            name, param = wow
            if not param:
                continue

            if name == 'prof':
                tw = QTableWidget()
                tw.addAction(CopySelectedCellsAction(tw))
                x_var = 'x'
                self.clas_data.addTab(tw, self.name_tab[name]['name'])
                lst_vars = [x_var]
                lst_vars.extend(self.name_tab[name]['lst_vars'])
                lst_lbls = []
                for var in lst_vars:
                    if var == 'x':
                        lbl = 'Abscisa'
                    else:
                        lbl, _ = self.get_var_info(var)
                    lst_lbls.append(lbl)
            else:
                x_var = 'z'
                cl_res = WidgetProfResultDialog(self)
                tw = cl_res.tw
                tw.addAction(CopySelectedCellsAction(tw))
                self.clas_data.addTab(cl_res, name)
                # same behavior that the fill of graph
                dico_tmp = {}
                if qmaj_max > 0.001 or self.cas_prt[0] == name:
                    dico_tmp = get_valeurs(zlevel, param['pr_poly'])
                else:
                    dico_tmp = {'z': zlevel,
                                'area': None,
                                'perimeter': None,
                                'width': None}

                cl_res.change_label(dico_tmp)

                lst_vars = [x_var]
                lst_vars.extend(['width', 'area', 'debitance'])
                lst_lbls = []
                for var in lst_vars:
                    if var == 'z':
                        lbl = 'Altitude'
                    else:
                        lbl = var
                    lst_lbls.append(lbl)

            tw.setColumnCount(0)
            nbcol = len(lst_vars)
            tw.setColumnCount(nbcol)
            tw.setRowCount(0)
            tw.setRowCount(len(param[x_var]))
            for c, var in enumerate(lst_vars):
                tw.setHorizontalHeaderItem(c, QTableWidgetItem(lst_lbls[c]))
                for r, val in enumerate(param[var]):
                    itm = QTableWidgetItem()
                    itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    itm.setData(0, val)
                    tw.setItem(r, c, itm)

            tw.setVisible(False)
            tw.resizeColumnsToContents()
            tw.resizeRowsToContents()
            tw.setVisible(True)

        if not self.cur_id_tab < self.clas_data.count():
            self.cur_id_tab = 0
        self.clas_data.setCurrentIndex(self.cur_id_tab)

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
        idx = self.clas_data.currentIndex()
        name = self.clas_data.tabText(idx)
        txt = txt + ' ' + name

        default_name = txt.replace(' ', '_').replace(':', '-')

        file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                        "{0}.csv".format(
                                                            default_name),
                                                        filter="CSV (*.csv *.)")

        if file_name_path:
            wdget = self.clas_data.currentWidget()
            select = wdget.findChildren(QTableWidget)
            if select:
                # one table
                cur_tw = select[0]
            else:
                cur_tw = wdget
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
