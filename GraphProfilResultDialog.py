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
        self.list_var_lai = []
        self.zmax_save = None
        self.cur_data = dict()
        self.date = None
        self.obs = None
        self.list_typ_res = None
        self.info_graph = {}
        self.val_prof_ref = {}
        self.dict_run = dict()
        self.laisses = {}

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
                lambda: self.detail_changed(up_lim=True))

            self.bt_expCsv.clicked.connect(self.export_csv)
            self.tw_data.addAction(CopySelectedCellsAction(self.tw_data))

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
                                         'rightstock'])
        self.val_prof_ref = {}
        if prof:
            for i, pk in enumerate(prof['abscissa']):
                if pk:
                    try:
                        self.val_prof_ref[pk] = {}
                        self.val_prof_ref[pk]['x'] = [float(v) for v in
                                                      prof['x'][i].split()]
                        self.val_prof_ref[pk]['ZREF'] = [float(v) for v in
                                                         prof['z'][i].split()]
                        self.val_prof_ref[pk]['leftminbed'] = \
                            prof['leftminbed'][i]
                        self.val_prof_ref[pk]['rightminbed'] = \
                            prof['rightminbed'][i]
                        self.val_prof_ref[pk]['leftstock'] = prof['leftstock'][
                            i]
                        self.val_prof_ref[pk]['rightstock'] = \
                            prof['rightstock'][i]
                    except:
                        pass

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
        self.cb_scen.blockSignals(True)
        self.init_cb_scen()
        self.scen_changed()
        self.cb_scen.blockSignals(False)

    def scen_changed(self):
        """ change scen"""
        if self.cb_scen.currentIndex() != -1:
            self.cur_run = self.cb_scen.itemData(self.cb_scen.currentIndex())
            self.get_runs_graph()
            self.init_cb_graph()
            self.graph_changed_profil(False)
            self.init_cb_det(self.cur_pknum)
            self.detail_changed()

    def graph_changed_profil(self, update=True):
        """change graph of profile"""
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

    def update_data_profil(self):
        """
        update graph data for profile
        :return:
        """
        if not self.initialising:
            self.cur_data = dict(self.val_prof_ref[self.cur_pknum])

            if self.cur_run:
                if self.cur_t == 'Zmax':
                    val = self.zmax_save
                    where = "id_runs = {0} AND pknum = {1} " \
                            "AND var ={2} ".format(self.cur_run,
                                                   self.cur_pknum,
                                                   self.id_qmaj)
                    qmaj_max = self.mgis.mdb.select_max("val", 'results',
                                                        where=where)
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

                self.cur_data['Z'] = [val] * len(self.cur_data['x'])
                self.label_zmax.setText(str(self.zmax_save))
                self.cur_vars = ['ZREF', 'Z']

                self.cur_vars_lbl = self.find_var_lbl()
                self.fill_tab(self.x_var, nb_col=3)
                if self.cur_t == 'Zmax':
                    val_str = None
                    if self.zmax_save:
                        val_str = round(self.zmax_save, 3)
                    self.graph_obj.main_axe.title.set_text(
                        'Max of water level, {0} m '
                        ''.format(val_str))
                elif isinstance(self.cur_t, float):
                    try:
                        self.graph_obj.main_axe.title.set_text(
                            'Water level, {0} m - {1} s'
                            ''.format(self.cur_data['Z'][0],
                                      float(self.cb_det.currentText())))
                    except ValueError:
                        self.graph_obj.main_axe.title.set_text(
                            'Water level, {0} m - {1}'
                            ''.format(self.cur_data['Z'][0],
                                      self.cb_det.currentText()))
                self.graph_obj.main_axe.set_xlabel(r'Distance ($m$)')
                self.graph_obj.main_axe.set_ylabel(r'Level ($m$)')

                self.graph_obj.init_graph_profil(self.cur_data, self.x_var,
                                                 qmaj_max)

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