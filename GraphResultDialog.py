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

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *


class GraphResultDialog(QWidget):
    def __init__(self, mgis, typ_graph, id=None):
        QWidget.__init__(self)
        self.initialising = True
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_graph = typ_graph
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphResult.ui'), self)
        self.graph_obj = GraphResult(self.lay_graph, self)
        self.cur_run, self.cur_graph, self.cur_vars, self.cur_vars_lbl, self.cur_branch, self.cur_pknum, self.cur_t = None, None, None, None, None, None, None
        self.cur_data = dict()

        if self.typ_graph == "struct":
            self.typ_res = "struct"
            self.lst_graph = [{"id": "struct_lev", "name": "Level", "unit": "m", "vars": ["ZSTR"],
                                                                                 "colors": ["#FF0000"]},
                              {"id": "test", "name": "Test", "unit": "m²", "vars": ["AAA", "BBB"],
                                                                           "colors": ["#AAFF00", "#FF00FF"]}]
            self.x_var = "time"
            self.sql_where = "results.pknum = {1}"
            self.cur_pknum = id

        self.cb_run.currentIndexChanged.connect(self.init_cb_scen)
        self.cb_scen.currentIndexChanged.connect(self.scen_changed)
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
        self.update_data()

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
        for graph in self.lst_graph:
            self.cb_graph.addItem(graph["name"], graph["id"])

    def init_cb_det(self, id):
        self.cb_det.clear()
        if self.typ_graph == "struct":
            sql = "SELECT DISTINCT profiles.abscissa, profiles.abscissa || ' : ' || profiles.name FROM {0}.results " \
                  "INNER JOIN {0}.profiles ON results.pknum = profiles.abscissa WHERE id_runs = {2} AND " \
                  "var IN (SELECT id FROM {0}.results_var WHERE type_res = '{1}')".format(self.mgis.mdb.SCHEMA,
                                                                                          self.typ_res, self.cur_run)
        rows = self.mdb.run_query(sql, fetch=True)
        self.sld_det.setMaximum(len(rows) - 1)
        for row in rows:
            self.cb_det.addItem(row[1], row[0])

        self.cb_det.setCurrentIndex(self.cb_det.findData(id))

    def scen_changed(self):
        if self.cb_scen.currentIndex() != -1:
            self.cur_run = self.cb_scen.itemData(self.cb_scen.currentIndex())
            self.update_data()

    def graph_changed(self):
        if self.cb_graph.currentIndex() != -1:
            self.cur_graph = self.cb_graph.itemData(self.cb_graph.currentIndex())
            for graph in self.lst_graph:
                if graph["id"] == self.cur_graph:
                    self.cur_vars = graph["vars"]
                    self.cur_vars_lbl = self.find_var_lbl()
                    self.graph_obj.init_mdl(graph["vars"], self.cur_vars_lbl, graph["colors"], graph["unit"])
                    break
            self.update_data()

    def detail_changed(self):
        if self.cb_det.currentIndex() != -1:
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

    def update_data(self):
        if not self.initialising:
            self.cur_data = dict()
            sqlv = "('{}')".format("', '".join(self.cur_vars))
            sqlw = self.sql_where.format(self.cur_branch, self.cur_pknum, self.cur_t)
            sql = "SELECT DISTINCT {1} FROM {0}.results WHERE id_runs = {2} AND {4} " \
                  "AND var IN (SELECT id FROM {0}.results_var WHERE var in {3}) " \
                  "ORDER BY {1}".format(self.mgis.mdb.SCHEMA, self.x_var, self.cur_run, sqlv, sqlw)
            rows = self.mdb.run_query(sql, fetch=True)
            self.cur_data[self.x_var] = [row[0] for row in rows]

            for var in self.cur_vars:
                sql = "SELECT {1}, val FROM {0}.results WHERE id_runs = {2} AND " \
                      "var IN (SELECT id FROM {0}.results_var WHERE results_var.var = '{3}') " \
                      "AND {4} ORDER BY {1}".format(self.mgis.mdb.SCHEMA, self.x_var, self.cur_run, var, sqlw)
                rows = self.mdb.run_query(sql, fetch=True)
                self.cur_data[var] = [row[1] for row in rows]

            self.fill_tab()
            self.graph_obj.init_graph(self.cur_data, self.x_var)

    def fill_tab(self):
        self.tw_data.setColumnCount(0)
        self.tw_data.setColumnCount(len(self.cur_data))
        self.tw_data.setRowCount(0)
        self.tw_data.setRowCount(len(self.cur_data[self.x_var]))
        lst_vars = [self.x_var]
        lst_vars.extend(self.cur_vars)
        lst_lbls = [self.x_var]
        lst_lbls.extend(self.cur_vars_lbl)
        for c, var in enumerate(lst_vars):
            self.tw_data.setHorizontalHeaderItem(c, QTableWidgetItem(lst_lbls[c]))
            for r, val in enumerate(self.cur_data[var]):
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


def tw_to_txt(tw, range_r, range_c, sep):
    clipboard = ''
    for c in range_c:
        if c != range_c[-1]:
            clipboard = '{}{}{}'.format(clipboard, tw.horizontalHeaderItem(c).text(), sep)
        else:
            clipboard = '{}{}\n'.format(clipboard, tw.horizontalHeaderItem(c).text())
    for r in range_r:
        for c in range_c:
            if c != range_c[-1]:
                clipboard = '{}{}{}'.format(clipboard, tw.item(r, c).data(0), sep)
            else:
                clipboard = '{}{}\n'.format(clipboard, tw.item(r, c).data(0))
    return clipboard


class GraphResult(GraphCommonNew):
    def __init__(self, lay=None, wgt=None):
        GraphCommonNew.__init__(self, lay, wgt)
        self.init_ui()

    def init_ui(self):
        self.axes = self.fig.add_subplot(111)
        self.init_ui_common_p()

    def init_mdl(self, lst_vars, lst_lbls, lst_colors, unit_y):
        self.axes.cla()
        self.list_var = []
        self.courbes = []
        self.annotation = []
        self.unit_y = unit_y

        self.annot_var = self.axes.annotate("", xy=(0, 0), ha='left', xytext=(10, 0), textcoords='offset points',
                                            va='top', bbox=dict(boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                            c='black', visible=False, zorder=200)
        self.annotation.append(self.annot_var)

        for v, var in enumerate(lst_vars):
            self.list_var.append({"id": v, "name": var, "clr": lst_colors[v]})
            self.courbe_var, = self.axes.plot([], [], c=lst_colors[v], zorder=100 - v, label=lst_lbls[v])
            self.courbes.append(self.courbe_var)
            self.annot_var = self.axes.annotate("", xy=(0, 0), ha='left', xytext=(10, 0), textcoords='offset points',
                                                va='top', bbox=dict(boxstyle='round, pad=0.5', fc='white', alpha=0.7),
                                                c=lst_colors[v], visible=False, zorder=199 - v)
            self.annotation.append(self.annot_var)

        self.axes.tick_params(axis='both', labelsize=7.)
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

