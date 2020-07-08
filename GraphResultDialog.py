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
from .GraphCommon import GraphCommonNew
from .Function import tw_to_txt, interpole
from datetime import date, timedelta
from matplotlib import patches
import numpy as np
import re
import numpy as np
import matplotlib.lines as mlines

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *
import time


class GraphResultDialog(QWidget):
    def __init__(self, mgis, typ_graph, id=None):
        QWidget.__init__(self)
        self.initialising = True
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_graph = typ_graph
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphResult.ui'), self)
        self.graph_obj = GraphResult(self.lay_graph, self)
        self.cur_run, self.cur_graph, self.cur_vars = None, None, None
        self.cur_vars_lbl, self.cur_branch, self.cur_pknum, self.cur_t = None, None, None, None
        self.list_var_lai =[]
        self.zmax_save = None
        self.cur_data = dict()
        self.date = None
        self.list_typ_res = None
        self.show_hide_com(False)
        if self.checkrun():

            if self.typ_graph == "struct" or self.typ_graph == "weirs":
                if self.typ_graph == "weirs":
                    self.typ_res = "weirs"
                else:
                    self.typ_res = "struct"
                self.lst_graph = [{"id": "gate_move", "name": "Gate movement", "unit": "m",
                                   "vars": ["ZSTR"], "colors": ["blue"]}]
                self.x_var = "time"
                self.sql_where = "results.pknum = {1}"
                self.cur_pknum = id

            elif self.typ_graph == "hydro" or self.typ_graph == "hydro_pk":
                self.list_typ_res = ["opt",
                                     "tracer_MICROPOLE",
                                     "tracer_EUTRO",
                                     "tracer_O2",
                                     "tracer_BIOMASS",
                                     "tracer_TRANSPORT_PUR"]
                if self.typ_graph == "hydro_pk":
                    self.x_var = "pknum"
                    self.sql_where = "results.time = {1}"
                    # id= branch
                    self.cur_branch = id
                    self.cur_t = -1
                else:
                    self.x_var = "time"
                    self.sql_where = "results.pknum = {1}"
                    self.cur_pknum = id

            #
            elif self.typ_graph == "hydro_profil":
                self.list_typ_res = ['opt']
                self.x_var = 'x'
                self.sql_where = "results.pknum = {1}"

                self.cur_pknum = id
                sql = "SELECT id FROM {0}.results_var WHERE var = 'Z'".format(self.mdb.SCHEMA)
                rows = self.mdb.run_query(sql, fetch=True)
                self.id_z = rows[0][0]
                self.cur_t = "Zmax"
                self.get_profil_data()




            elif self.typ_graph == "hydro_basin" or self.typ_graph == "hydro_link":
                self.x_var = "time"
                self.cur_pknum = id
                self.sql_where =  "results.pknum = {1}"
                if self.typ_graph == 'hydro_link':
                    self.typ_res = 'link'
                else:
                    self.typ_res = 'basin'

            self.cb_run.currentIndexChanged.connect(self.init_cb_scen)
            self.cb_scen.currentIndexChanged.connect(self.scen_changed)
            if self.typ_graph == 'hydro_profil':
                self.cb_graph.currentIndexChanged.connect(self.graph_changed_profil)
            else:
                self.label_lbzmax.hide()
                self.label_zmax.hide()
                self.cb_graph.currentIndexChanged.connect(self.graph_changed)
            self.cb_det.currentIndexChanged.connect(self.detail_changed)

            # self.bt_reculTot.clicked.connect(lambda: self.avance_detail("start"))
            # self.bt_recul.clicked.connect(lambda: self.avance_detail("prev"))
            # self.bt_av.clicked.connect(lambda: self.avance_detail("next"))
            # self.bt_avTot.clicked.connect(lambda: self.avance_detail("end"))
            self.bt_expCsv.clicked.connect(self.export_csv)

            self.tw_data.addAction(CopySelectedCellsAction(self.tw_data))

            self.init_dico_run()
            self.init_cb_graph()
            self.init_cb_det(self.cur_pknum)

            self.initialising = False
            if self.typ_graph == 'hydro_profil':

                self.update_data_profil()

            else:
                self.update_data()

    def show_hide_com(self, vis=True):

        if vis:
            self.lbl_coment.show()
            self.label_coment.show()
        else:
            self.lbl_coment.hide()
            self.label_coment.hide()

    def checkrun(self):
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs "
                                  "ORDER BY run, scenario".format(self.mdb.SCHEMA), fetch=True)
        if rows:
            return True
        else:
            self.mgis.add_info("No data.")
            return False

    def get_profil_data(self):

        txt = self.mdb.select_distinct("comments", "runs", where='id={}'.format(self.cur_run))
        if txt:
            self.lbl_coment.setText(txt['comments'][0])
            self.show_hide_com(True)
        else:
            self.show_hide_com(False)

        prof = self.mdb.select('profiles', order='abscissa',
                               list_var=['abscissa', 'x', 'z', 'leftminbed', 'rightminbed', 'leftstock',
                                         'rightstock'])

        self.val_prof_ref = {}
        if prof:
            for i, pk in enumerate(prof['abscissa']):
                if pk:
                    self.val_prof_ref[pk] = {}
                    self.val_prof_ref[pk]['x'] = [float(v) for v in prof['x'][i].split()]
                    self.val_prof_ref[pk]['ZREF'] = [float(v) for v in prof['z'][i].split()]
                    self.val_prof_ref[pk]['leftminbed'] = prof['leftminbed'][i]
                    self.val_prof_ref[pk]['rightminbed'] = prof['rightminbed'][i]
                    self.val_prof_ref[pk]['leftstock'] = prof['leftstock'][i]
                    self.val_prof_ref[pk]['rightstock'] = prof['rightstock'][i]

    def list_sql(self, liste):
        """
        list to srting for sql script
        :param liste:
        :return:
        """
        txt = '('
        for t_res in liste:
            txt += "'{}',".format(t_res)
        txt = txt[:-1] + ')'
        return txt

    def get_lst_graph_opt(self, id_run=None):
        """
        Get graphic list
        :param typ_res: typ_res liste
        :return:
        """

        liste = [{"id": "Z", "name": "Levels", "unit": "$m$",
                  "vars": ['ZREF', 'Z', 'ZMIN', 'ZMAX'], "colors": ["black", "blue", "green", "red"]},
                 {"id": "Q", "name": "Flow rate", "unit": "$m^3/s$",
                  "vars": ['Q', 'QMIN', 'QMAJ', 'QMAX'], "colors": ["blue", "green", "cyan", "red"]}
                 ]
        exclu = {'Q': False, 'QMIN': False, 'QMAJ': False, 'QMAX': False,
                 'ZREF': False, 'Z': False, 'ZMIN': False, 'ZMAX': False}

        if id_run:
            # pb 15 s a optimiser
            sql = "SELECT * FROM {0}.results_var WHERE type_res in {1} " \
                  "AND id in (SELECT var FROM {0}.results WHERE " \
                  "id_runs={2} group by var)".format(self.mdb.SCHEMA,
                                        self.list_sql(self.list_typ_res),
                                        id_run)

        else:
            sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res in {1}".format(self.mdb.SCHEMA,
                                                                                        self.list_sql(
                                                                                            self.list_typ_res))
        rows = self.mdb.run_query(sql, fetch=True)

        for rws in rows:
            if not rws[2] in exclu.keys():
                liste.append({"id": rws[2], "name": rws[3], "unit": "",
                              "vars": [rws[2]], "colors": ["blue"]})
            else:
                exclu[rws[2]] = True

        iterlist =[]
        iterlist.append(zip(list(liste[0]['vars']), list(liste[0]['colors'])))
        iterlist.append(zip(list(liste[1]['vars']), list(liste[1]['colors'])))

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
         :param list_var : liste of dict containing graphs informations
         :return the update list
        """

        for dico_var in liste_var:
            for i, var in enumerate(dico_var["vars"]):
                if var.lower() in self.mgis.variables.keys():
                    dico_var["colors"][i] = self.mgis.variables[var.lower()]['couleur']
                    if not var in ['Q', 'QMIN', 'QMAJ', 'QMAX', 'ZREF', 'Z', 'ZMIN', 'ZMAX']:
                        if self.mgis.variables[var.lower()]['unite'].strip() =='':
                            dico_var['unit'] = ''
                        else:
                            dico_var['unit'] = r'$'+self.mgis.variables[var.lower()]['unite'].strip()+r'$'
        return liste_var

    def get_lst_graph_bl(self, typ_res, id_run=None):
        """
        Get graphic list basin and link
        :param id_run:
        :return:
        """
        #
        # if id_run:
        #     sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res = '{1}' " \
        #           "AND id in (SELECT DISTINCT var FROM {0}.results WHERE " \
        #           "id_runs={2})".format(self.mdb.SCHEMA,
        #                                 typ_res,
        #                                 id_run)
        # else:
        sql = "SELECT DISTINCT * FROM {0}.results_var WHERE type_res = '{1}'".format(self.mdb.SCHEMA,
                                                                                         typ_res)
        rows = self.mdb.run_query(sql, fetch=True)

        liste = []

        for rws in rows:
            liste.append({"id": rws[2], "name": rws[3], "unit": "",
                          "vars": [rws[2]], "colors": ["blue"]})
        liste = self.change_lengend_var(liste)
        return liste

    def init_dico_run(self):
        self.dict_run = dict()
        rows = self.mdb.run_query("SELECT id, run, scenario FROM {0}.runs "
                                  "ORDER BY run, scenario".format(self.mdb.SCHEMA), fetch=True)
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

        self.cb_graph.clear()
        lst_graph = None
        if self.cur_run:
            # add comment
            txt = self.mdb.select_distinct("comments", "runs", where='id={}'.format(self.cur_run))
            if txt:
                self.lbl_coment.setText(txt['comments'][0])
                self.show_hide_com(True)
            else:
                self.show_hide_com(False)
        if self.typ_graph == "struct" or self.typ_graph == "weirs":
            lst_graph = self.lst_graph
        elif self.typ_graph == "hydro" or self.typ_graph == "hydro_pk":
            lst_graph = self.get_lst_graph_opt(self.cur_run)
        elif self.typ_graph == "hydro_basin" or self.typ_graph == "hydro_link":
            lst_graph = self.get_lst_graph_bl(self.typ_res, self.cur_run)
        elif self.typ_graph == 'hydro_profil':
            lst_graph = []
            sql = "SELECT DISTINCT pknum FROM {0}.results WHERE id_runs={1} " \
                  "AND var IN (SELECT id FROM {0}.results_var " \
                  "WHERE var ='Z') ORDER BY pknum".format(self.mgis.mdb.SCHEMA,
                                                          self.cur_run)

            rows = self.mdb.run_query(sql, fetch=True)
            info = self.mdb.select('profiles', list_var=['abscissa', "name"])

            for row in rows:
                if row[0] in info['abscissa']:
                    txt = str(row[0]) + ' : ' + info['name'][info['abscissa'].index(row[0])]
                    lst_graph.append({"name": txt, 'id': float(row[0])})
            self.lst_graph = lst_graph
            id = -1
            for i, graph in enumerate(lst_graph):
                self.cb_graph.addItem(graph["name"], graph["id"])
            # self.cb_graph.setCurrentIndex(id)
            #self.cb_graph.setCurrentIndex(self.cb_graph.findData(float(self.cur_pknum)))
            return
        self.lst_graph = lst_graph
        for graph in self.lst_graph:
            self.cb_graph.addItem(graph["name"], graph["id"])

    def init_cb_det(self, id):
        self.cb_det.clear()
        if self.typ_graph == "struct" or self.typ_graph == "weirs":
            sql = "SELECT DISTINCT profiles.abscissa, profiles.abscissa || ' : ' || profiles.name FROM {0}.results " \
                  "INNER JOIN {0}.profiles ON results.pknum = profiles.abscissa WHERE id_runs = {2} AND " \
                  "var IN (SELECT id FROM {0}.results_var WHERE type_res = '{1}')".format(self.mgis.mdb.SCHEMA,
                                                                                          self.typ_res, self.cur_run)
            rows = self.mdb.run_query(sql, fetch=True)
            self.sld_det.setMaximum(len(rows) - 1)
            for row in rows:
                self.cb_det.addItem(row[1], row[0])
            self.cb_det.setCurrentIndex(self.cb_det.findData(id))
        elif self.typ_graph == "hydro":

            sql = "SELECT DISTINCT pknum FROM {0}.results WHERE id_runs={1} " \
                  "AND var IN (SELECT id FROM {0}.results_var " \
                  "WHERE type_res IN {2}) ORDER BY pknum".format(self.mgis.mdb.SCHEMA,
                                                                 self.cur_run,
                                                                 self.list_sql(self.list_typ_res))

            rows = self.mdb.run_query(sql, fetch=True)
            info = self.mdb.select('profiles', list_var=['abscissa', "name"])
            self.sld_det.setMaximum(len(rows) - 1)
            for row in rows:
                if row[0] in info['abscissa']:
                    txt = str(row[0]) + ' : ' + info['name'][info['abscissa'].index(row[0])]
                else:
                    txt = str(row[0])
                self.cb_det.addItem(txt, row[0])
            self.cb_det.setCurrentIndex(self.cb_det.findData(id))

        elif self.typ_graph == "hydro_pk":
            sql = "SELECT DISTINCT time FROM {0}.results WHERE id_runs={1} " \
                  "AND var IN (SELECT id FROM {0}.results_var " \
                  "WHERE type_res IN {2}) ORDER BY time".format(self.mgis.mdb.SCHEMA,
                                                                self.cur_run,
                                                                self.list_sql(self.list_typ_res))

            rows = self.mdb.run_query(sql, fetch=True)

            self.sld_det.setMaximum(len(rows) - 1)
            sql = "SELECT init_date FROM {0}.runs WHERE id = {1} ".format(self.mgis.mdb.SCHEMA,
                                                                          self.cur_run)
            info = self.mdb.run_query(sql, fetch=True)
            if info:
                self.date = info[0][0]
            else:
                self.date = None
            if self.typ_graph == 'hydro_profil':
                self.cb_det.addItem("Zmax", "Zmax")
            for row in rows:
                if self.date:
                    aff = self.date + timedelta(seconds=row[0])
                    aff = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(aff, aff.microsecond / 10000.0)
                else:
                    aff = str(row[0])
                self.cb_det.addItem(aff, row[0])
            self.cb_det.setCurrentIndex(self.cb_det.count() - 1)

        elif self.typ_graph == 'hydro_profil':
            sql = "SELECT DISTINCT time FROM {0}.results WHERE id_runs={1} " \
                  "AND var ={2} ORDER BY time".format(self.mgis.mdb.SCHEMA,
                                                      self.cur_run, self.id_z)
            rows = self.mdb.run_query(sql, fetch=True)
            self.sld_det.setMaximum(len(rows) - 1)
            sql = "SELECT init_date FROM {0}.runs WHERE id = {1} ".format(self.mgis.mdb.SCHEMA,
                                                                          self.cur_run)
            info = self.mdb.run_query(sql, fetch=True)
            if info:
                self.date = info[0][0]
            else:
                self.date = None
            if self.typ_graph == 'hydro_profil':
                self.cb_det.addItem("Zmax", "Zmax")
            for row in rows:
                if self.date:
                    aff = self.date + timedelta(seconds=row[0])
                    aff = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(aff, aff.microsecond / 10000.0)
                else:
                    aff = str(row[0])
                self.cb_det.addItem(aff, row[0])

            self.cb_det.setCurrentIndex(0)


        elif self.typ_graph == "hydro_link" or self.typ_graph == "hydro_basin":
            if self.typ_res == 'link':
                table = "links"
                num = "linknum"
            else:
                table = "basins"
                num = "basinnum"

            sql = "SELECT DISTINCT name,{4},gid FROM  {0}.{3} WHERE {4} IN " \
                  "(SELECT DISTINCT pknum FROM {0}.results WHERE id_runs={1} " \
                  "AND var IN (SELECT id FROM {0}.results_var " \
                  "WHERE type_res = '{2}') ORDER BY pknum)".format(self.mgis.mdb.SCHEMA,
                                                                   self.cur_run,
                                                                   self.typ_res,
                                                                   table,
                                                                   num)

            rows = self.mdb.run_query(sql, fetch=True)
            for row in rows:
                self.cb_det.addItem(row[0], row[1])
            self.cb_det.setCurrentIndex(self.cb_det.findData(id))
            self.sld_det.setMaximum(len(rows) - 1)

    def scen_changed(self):
        if self.cb_scen.currentIndex() != -1:
            self.cur_run = self.cb_scen.itemData(self.cb_scen.currentIndex())
            self.init_cb_graph()
            self.init_cb_det(self.cur_pknum)
            if self.typ_graph == 'hydro_profil':
                # self.init_cb_det(self.cur_pknum)
                pass
            elif self.typ_graph == "hydro" or self.typ_graph == "hydro_pk":
                # self.init_cb_det(self.cur_pknum)
                self.get_laisses()
            else:
                pass
                # self.init_cb_det(self.cur_pknum)
                # self.update_data()

    def graph_changed(self):
        if self.cb_graph.currentIndex() != -1:
            self.cur_graph = self.cb_graph.itemData(self.cb_graph.currentIndex())

            for graph in self.lst_graph:
                if graph["id"] == self.cur_graph:
                    self.cur_vars = graph["vars"]
                    self.cur_vars_lbl = self.find_var_lbl()
                    self.graph_obj.init_mdl(graph["vars"], self.cur_vars_lbl, graph["colors"], graph["unit"],graph['name'] )
                    break
            self.graph_obj.clean_laisse()
            self.update_data()

    def graph_changed_profil(self):

        if self.cb_graph.currentIndex() != -1:
            self.cur_pknum = self.cb_graph.itemData(self.cb_graph.currentIndex())
            self.cur_vars = ['ZREF']
            lst_colors = ['black']
            self.cur_vars_lbl = self.find_var_lbl()

            self.graph_obj.init_mdl(self.cur_vars, self.cur_vars_lbl, lst_colors, 'm')
            if self.cur_run:
                condition = "id_runs = {0} AND pknum = {1} " \
                            "AND var ={2}".format(self.cur_run, self.cur_pknum, self.id_z)
                self.zmax_save = self.mdb.select_max("val", 'results', condition)
            else:
                self.zmax_save = None

    def detail_changed(self):
        if self.cb_det.currentIndex() != -1:
            if self.typ_graph == 'hydro_profil':
                self.cur_t = self.cb_det.itemData(self.cb_det.currentIndex())
                self.update_data_profil()
            else:
                self.cur_pknum = self.cb_det.itemData(self.cb_det.currentIndex())
                self.update_data()

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

    def update_data_profil(self):
        if not self.initialising:
            self.cur_data = dict(self.val_prof_ref[self.cur_pknum])

            if self.cur_run:
                print(self.cur_t)
                if self.cur_t == 'Zmax':
                    val = self.zmax_save
                else:
                    where = "id_runs = {0} AND pknum = {1} " \
                            "AND var ={2} AND time = {3}".format(self.cur_run, self.cur_pknum,
                                                                 self.id_z, self.cur_t)
                    val = self.mgis.mdb.select('results', where=where, list_var=["val"])

                    if val:
                        val = val['val'][0]

                self.cur_data['Z'] = [val] * len(self.cur_data['x'])
                self.label_zmax.setText(str(self.zmax_save))
                self.cur_vars = ['ZREF', 'Z']

                self.cur_vars_lbl = self.find_var_lbl()
                self.fill_tab(self.x_var, nb_col=3)
                if self.cur_t == 'Zmax':
                    val_str = None
                    if self.zmax_save:
                        val_str = round(self.zmax_save, 3)
                    self.graph_obj.axes.title.set_text('Max of water level, {0} m '
                                                       ''.format(val_str))
                elif isinstance(self.cur_t, float):
                    try:
                        self.graph_obj.axes.title.set_text('Water level, {0} m - {1} s'
                                                           ''.format(self.cur_data['Z'][0],
                                                                     float(self.cb_det.currentText())))
                    except ValueError:
                        self.graph_obj.axes.title.set_text('Water level, {0} m - {1}'
                                                           ''.format(self.cur_data['Z'][0],
                                                                     self.cb_det.currentText()))
                self.graph_obj.axes.set_xlabel(r'Distance ($m$)')
                self.graph_obj.axes.set_ylabel(r'Level ($m$)')
                self.graph_obj.init_graph_profil(self.cur_data, self.x_var)

    def update_data(self):

        if not self.initialising:
            self.cur_data = dict()

            t0 = time.time()
            sqlv = "('{}')".format("', '".join(self.cur_vars))
            sqlw = self.sql_where.format(self.cur_branch, self.cur_pknum, self.cur_t)
            if self.typ_graph == 'hydro_pk':
                sql_hyd_pk = "AND pknum IN (SELECT pk FROM {0}.results_sect WHERE " \
                             "id_runs = {1} AND branch = {2})".format(self.mgis.mdb.SCHEMA,
                                                                      self.cur_run,
                                                                      self.cur_branch)
            else:
                sql_hyd_pk = ''

            sql = "SELECT DISTINCT {1} FROM {0}.results WHERE id_runs = {2} AND {4} " \
                  "AND var IN (SELECT id FROM {0}.results_var WHERE var in {3}) {5} " \
                  "ORDER BY {1}".format(self.mgis.mdb.SCHEMA, self.x_var, self.cur_run,
                                        sqlv, sqlw, sql_hyd_pk)

            rows = self.mdb.run_query(sql, fetch=True)


            sql = "SELECT init_date FROM {0}.runs WHERE id = {1} ".format(self.mgis.mdb.SCHEMA,
                                                                          self.cur_run)
            info = self.mdb.run_query(sql, fetch=True)
            print('get_value_first', time.time() - t0)
            if info:
                self.date = info[0][0]
                if self.date :
                    self.cur_data["date"] = [self.date + timedelta(seconds=row[0]) for row in rows]
            else:
                self.date = None

            self.cur_data[self.x_var] = [row[0] for row in rows]
            t0 = time.time()
            for var in self.cur_vars:
                sql = "SELECT {1}, val FROM {0}.results WHERE id_runs = {2} AND " \
                      "var IN (SELECT id FROM {0}.results_var WHERE results_var.var = '{3}') " \
                      "AND {4} {5} " \
                      "ORDER BY {1}".format(self.mgis.mdb.SCHEMA, self.x_var, self.cur_run,
                                            var, sqlw, sql_hyd_pk)
                rows = self.mdb.run_query(sql, fetch=True)
                self.cur_data[var] = [row[1] for row in rows]
            print('get_value', time.time()-t0)
            x_var_ = self.x_var
            if self.x_var == 'time':
                if self.date:
                    x_var_ = 'date'
                    self.graph_obj.axes.set_xlabel(r'Time')
                else:
                    self.graph_obj.axes.set_xlabel(r'Time ($s$)')
                    self.graph_obj.axes.title.set_text(r'Branch {0} - {1} m'
                                                           ''.format(self.cur_branch,
                                                                     self.cb_det.currentText()))
            else:
                try:
                    self.graph_obj.axes.title.set_text(r'Branch {0} - {1} $s$'
                                                       ''.format(self.cur_branch,
                                                                 float(self.cb_det.currentText())))
                except ValueError:
                    self.graph_obj.axes.title.set_text(r'Branch {0} - {1} $s$'
                                                       ''.format(self.cur_branch,
                                                                 self.cb_det.currentText()))


                self.graph_obj.axes.set_xlabel(r'Pk ($m$)')

            #
            self.fill_tab(x_var_)

            self.graph_obj.init_graph(self.cur_data, x_var_)

            if self.typ_graph == "hydro" or self.typ_graph == "hydro_pk":
                if 'Z' in self.cur_vars:
                    self.update_laisse(x_var_)
               # self.update_obs()

    def get_laisses(self):
        t0 = time.time()
        info = self.mdb.select('runs', where="id={}".format(self.cur_run), list_var=['scenario'])
        condition = "event = '{}'".format(info["scenario"][0])
        self.laisses = self.mdb.select("flood_marks", condition, "abscissa")
        if self.laisses:
            self.laisses['pknum'] = self.laisses['abscissa']
        print('time laisse',t0-time.time())


    def update_laisse(self,var_x):
        """
        To graph the flood mark

        :param var_x:
        :return:
        """
        t0=time.time()
        courbe_lais = {}
        lai = self.laisses
        if lai:
            if var_x not in lai.keys():
                return

            courbe_lais["x"] = [v for v in lai[var_x] if v]
            if not courbe_lais["x"]:
                return

            courbe_lais["z"] = [v for i, v in enumerate(lai['z']) if lai[var_x][i]]
            if 'ZMAX' in self.cur_data.keys():
                courbe_lais["couleurs"] = []
                courbe_lais["taille"] = []
                for x, z in zip(courbe_lais["x"], courbe_lais["z"]):
                    val = interpole(x, self.cur_data["pknum"], self.cur_data['ZMAX'])
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

        print('time update laisse', time.time()-t0)

    def update_obs(self):

        if "date" in self.cur_data.keys():

            print("update obs")
            if "Z" in self.cur_data.keys():
                gg = 'H'
            elif "Q" in self.cur_data.keys():
                gg = 'Q'
            else:
                return
            mini = min(self.cur_data["date"])
            maxi = max(self.cur_data["date"])

            sql = "SELECT code FROM {0}.outputs " \
                  "WHERE active AND abscissa = {1};".format(self.mdb.SCHEMA, self.cur_pknum)
            print(sql)
            rows = self.mdb.run_query(sql, fetch=True)
            print(rows)
            if rows:
                code = rows[0]
            else:
                return
            obs = {}
            for code in rows:
                code = code[0]
                condition = """code = '{0}'
                                               AND date>'{1}'
                                               AND date<'{2}'
                                               AND type='{3}'
                                               AND valeur > -999.9""".format(code, mini, maxi, gg)

                obs[code] = self.mdb.select("observations", condition, "date")
            print(obs)
            if not obs:
                return
            if 'zero' in col:
                zero = self.mgis.mdb.select_distinct("zero", "profiles",
                                                     where="active AND abscissa = {};".format(self.cur_pknum))
                if zero:
                    obs['valeur'] = [var1 + zero['zero'] for var1 in obs['valeur']]
            print(obs)
            self.graph_obj.init_obs(obs)

        else:
            return

            #

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
            self.tw_data.setHorizontalHeaderItem(c, QTableWidgetItem(lst_lbls[c]))
            for r, val in enumerate(self.cur_data[var]):
                if var == "date":
                    val = '{:%d/%m/%Y %H:%M:%S}.{:02.0f}'.format(val, val.microsecond / 10000.0)
                itm = QTableWidgetItem()
                itm.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                itm.setData(0, val)
                self.tw_data.setItem(r, c, itm)
        self.tw_data.setVisible(False)
        # self.tw_data.resizeColumnsToContents()
        self.tw_data.resizeRowsToContents()
        self.tw_data.setVisible(True)

    def find_var_lbl(self):
        tmp = []
        for var in self.cur_vars:
            rows = self.mdb.run_query("SELECT name FROM {0}.results_var "
                                      "WHERE var = '{1}'".format(self.mgis.mdb.SCHEMA, var), fetch=True)
            tmp.append(rows[0][0])
        return tmp

    def export_csv(self):
        """Export Table to .CSV file"""
        # recupe tab export CSV
        txt = self.cb_graph.currentText()
        default_name = txt.replace(' ', '_').replace(':', '-')
        if int(qVersion()[0]) < 5:  # qt4
            file_name_path = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
                                                         filter="CSV (*.csv *.)")
        else:  # qt5
            file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
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
            lst_r = [idx.row() for idx in self.cur_tw.selectionModel().selectedIndexes()]
            lst_c = [idx.column() for idx in self.cur_tw.selectionModel().selectedIndexes()]
            range_r = range(min(lst_r), max(lst_r) + 1)
            range_c = range(min(lst_c), max(lst_c) + 1)
            clipboard = tw_to_txt(self.cur_tw, range_r, range_c, '\t')
            sys_clip = QApplication.clipboard()
            sys_clip.setText(clipboard)


class GraphResult(GraphCommonNew):
    def __init__(self, lay=None, wgt=None):
        GraphCommonNew.__init__(self, lay, wgt)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.init_ui_common_p()

    def init_mdl(self, lst_vars, lst_lbls, lst_colors, unit_y, name= None):
        self.axes.cla()
        self.list_var = []
        self.courbes = []
        self.annotation = []
        self.unit_y = unit_y

        self.annot_var = self.axes.annotate("", xy=(0, 0), ha='left', xytext=(10, 0), textcoords='offset points',
                                            va='top', bbox=dict(boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                            color='black', visible=False, zorder=200)
        self.annotation.append(self.annot_var)
        self.courbeLaisses = []
        self.etiquetteLaisses = []
        for v, var in enumerate(lst_vars):
            self.list_var.append({"id": v, "name": var, "clr": lst_colors[v]})
            courbe_var, = self.axes.plot([], [], color=lst_colors[v], zorder=100 - v, label=lst_lbls[v])
            self.courbes.append(courbe_var)
            annot_var = self.axes.annotate("", xy=(0, 0), ha='left', xytext=(10, 0), textcoords='offset points',
                                                va='top', bbox=dict(boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                                color=lst_colors[v], visible=False, zorder=199 - v)
            self.annotation.append(annot_var)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='pink',
                                 alpha=0.5, lw=1, zorder=80)
        self.litMineur = self.axes.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                 alpha=0.3, lw=1, zorder=80)
        self.stockgauche = self.axes.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                 alpha=0.3, lw=1, zorder=80)
        self.stockdroit = self.axes.add_patch(rect)

        self.aire = []

        self.axes.tick_params(axis='both', labelsize=7.)

        txt_ylabel = r''
        if name :
            txt_ylabel+=r'{} '.format(name)
            if self.unit_y!='':
                txt_ylabel +=r'({}) '.format(self.unit_y)
        self.axes.set_ylabel(txt_ylabel)

        self.axes.grid(True)
        self.v_line = self.axes.axvline(color="black")
        self.init_legende()

    def init_graph(self, data, x_var, all_vis=True):
        self.set_data(data, x_var)
        leglines = self.leg.get_lines()
        for v, var in enumerate(self.list_var):
            self.courbes[v].set_data(data[x_var], data[var["name"]])
            if all_vis:
                self.courbes[v].set_visible(True)
                leglines[v].set_alpha(1.0)
        self.maj_limites()

    def init_graph_profil(self, data, x_var):

        self.set_data(data, x_var)

        if len(self.courbes) > 0:
            self.courbes[0].set_data(data["x"], data['ZREF'])
            self.courbes[0].set_visible(True)
        else:
            return

        for patch in self.aire:
            if patch in self.axes.patches:
                self.axes.patches.remove(patch)

        if data['x'] and data['leftminbed'] and data['rightminbed']:
            self.litMineur.set_x(data['leftminbed'])
            self.litMineur.set_width(data['rightminbed'] - data['leftminbed'])
            self.litMineur.set_visible(True)
        else:
            self.litMineur.set_visible(False)

        if data['x'] and data["leftstock"]:
            mini = min(data['x'])
            self.stockgauche.set_x(mini)
            self.stockgauche.set_width(data['leftstock'] - mini)
            self.stockgauche.set_visible(True)
        else:
            self.stockgauche.set_visible(False)

        if data['x'] and data["rightstock"]:
            self.stockdroit.set_x(data['rightstock'])
            self.stockdroit.set_width(max(data['x']) - data['rightstock'])
            self.stockdroit.set_visible(True)
        else:
            self.stockdroit.set_visible(False)
        temp1 = np.array(data['ZREF'])
        temp2 = np.array(data['Z'])

        aire = self.axes.fill_between(data['x'], temp1, temp2,
                                      where=temp2 >= temp1,
                                      interpolate=True)
        self.aire = []

        for p in aire.get_paths():
            if data['leftminbed'] is not None:
                gauch = data['leftminbed']
            else:
                gauch = min(p.vertices[:, 0])
            if data['rightminbed'] is not None:
                droit = data['rightminbed']
            else:
                droit = max(p.vertices[:, 0])
            for x, y in p.vertices:

                if gauch <= x <= droit:
                    patch = patches.PathPatch(p,
                                              facecolor='deepskyblue',
                                              lw=0)
                    self.aire.append(patch)
                    self.axes.add_patch(patch)

                    break

        self.axes.collections.remove(aire)

        self.maj_limites()

    def clean_laisse(self):
        """flood mark"""
        # self.courbeLaisses = self.axes.scatter([], [], label="Flood marks",
        # #                                        marker='+', color='darkcyan')
        if self.courbes:
            tmp= []
            for i,cb in enumerate(self.courbes):
                if not  cb in self.courbeLaisses:
                    tmp.append(cb)
            self.courbes =list(tmp)

        self.courbeLaisses = []
        for e in self.etiquetteLaisses:
            self.axes.texts.remove(e)
        self.etiquetteLaisses = []

    def init_graph_laisse(self, laisses):
        """ add flood mark in graph"""

        self.clean_laisse()

        self.courbeLaisses.append(self.axes.scatter(laisses['x'], laisses['z'],
                                               color=laisses["couleurs"],
                                               marker='+',
                                               label="Flood marks",
                                               s=80,
                                               linewidth=laisses['taille']))

        self.courbeLaisses[0].set_visible(True)
        for x, z, c in zip(laisses['x'], laisses['z'], laisses["couleurs"]):
            temp = self.axes.annotate(str(z), xy=(x, z), xytext=(3, 3),
                                      ha='left', va='bottom',
                                      fontsize='x-small',
                                      color=c,
                                      textcoords='offset points', clip_on=True)

            self.etiquetteLaisses.append(temp)

        handles = [c for c in self.courbes]
        handles.append(mlines.Line2D([], [], color='darkcyan', marker='+',
                                     linewidth=0,
                                     markersize=10, label='Flood marks'))


        self.courbes += self.courbeLaisses

        self.init_legende(handles=handles)
        self.maj_limites()


    def init_obs(self, obs):
        self.maj_obs(obs)
