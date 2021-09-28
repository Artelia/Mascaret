# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : September,2021
copyright            : (C) 2021 by Artelia
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
import numpy as np

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


class ScoreDistWidget(QWidget):
    def __init__(self, windmain):
        QWidget.__init__(self)
        self.windmain = windmain
        self.mdb = self.windmain.mgis.mdb
        self.all = self.windmain.all
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath,
                         'ui/scores/ui_distib_score.ui'), self)
        self.dict_name = {}

        self.data_write = {
            'dist_err': 'Error',
            'dist_abs_err': 'Absolute Error'
        }
        self.taberr.setCurrentIndex(0)
        self.bt_export_csv.clicked.connect(self.export_csv)
        self.bt_export_csv.setEnabled(False)

    def fill_tab(self):
        """ fill table"""
        self.clear_tab()
        self.lst_runs = []

        self.dict_name = self.mdb.get_scen_name(self.res.keys())
        # table_dist_abs
        tab_fill = {}
        tab_fill_abs = {}
        lst_col = []
        lst_col_abs = []
        for id in self.res.keys():
            colh = []
            colh_abs = []
            colq = []
            colq_abs = []
            if 'H' in self.res[id].keys():
                if 'quantil' in self.res[id]['H'].keys():
                    tmp, colh = self.fill_dico(id, 'H', 'dist_err')
                    tmp_abs, colh_abs = self.fill_dico(id, 'H', 'dist_abs_err')
                    for kk in tmp.keys():
                        if kk in tab_fill.keys():
                            tab_fill[kk].update(tmp[kk])
                            tab_fill_abs[kk].update(tmp_abs[kk])
                        else:
                            tab_fill[kk] = tmp[kk]
                            tab_fill_abs[kk] = tmp_abs[kk]

            if 'Q' in self.res[id].keys():
                if 'quantil' in self.res[id]['Q'].keys():
                    tmp, colq = self.fill_dico(id, 'Q', 'dist_err')
                    tmp_abs, colq_abs = self.fill_dico(id, 'Q', 'dist_abs_err')
                    for kk in tmp.keys():
                        if kk in tab_fill.keys():
                            tab_fill[kk].update(tmp[kk])
                            tab_fill_abs[kk].update(tmp_abs[kk])
                        else:
                            tab_fill[kk] = tmp[kk]
                            tab_fill_abs[kk] = tmp_abs[kk]
                            # tab_fill.update(self.fill_dico(id, 'Q', 'dist_err'))
                            # tab_fill_abs.update(self.fill_dico(id, 'Q', 'dist_abs_err'))
            lst_col = lst_col + colh + colq
            lst_col_abs = lst_col_abs + colh_abs + colq_abs
        if len(tab_fill.keys()) > 0:
            dist_lst = [v for v in tab_fill.keys()]
            nb_line = len(dist_lst)
            # columns = [str(v) for v in tab_fill[dist_lst[0]].keys()]
            columns = list(set(lst_col))
            nb_col = len(columns)
            self.table_dist.setRowCount(nb_line)
            self.table_dist.setColumnCount(nb_col)
            self.table_dist.setVerticalHeaderLabels(
                [str(v) for v in dist_lst])
            self.table_dist.setHorizontalHeaderLabels(columns)

            self.table_dist_abs.setRowCount(nb_line)
            self.table_dist_abs.setColumnCount(nb_col)
            self.table_dist_abs.setVerticalHeaderLabels(
                [str(v) for v in dist_lst])
            self.table_dist_abs.setHorizontalHeaderLabels(columns)

            for row, dist in enumerate(dist_lst):
                for tmp in tab_fill[dist].keys():
                    item = QTableWidgetItem(
                        '{:.3f}'.format(tab_fill[dist][tmp]))
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    col = columns.index(tmp)
                    self.table_dist.setItem(row, col, item)
                for tmp in tab_fill_abs[dist].keys():
                    item = QTableWidgetItem(
                        '{:.3f}'.format(tab_fill[dist][tmp]))
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    col = columns.index(tmp)
                    self.table_dist_abs.setItem(row, col, item)

            self.bt_export_csv.setEnabled(True)

    def fill_dico(self, id, varhq, var):
        """
         change results shape to fill table
        :param id: run index
        :param varhq: variable (H or Q)
        :param var: erreur type 'dist_err' or 'dist_abs_err'
        :return:
        """
        tab_fill = {}
        res2 = self.res[id][varhq]['quantil']
        lst_col = []
        code = None
        oneobs = False
        if not self.all:
            keys = list(res2.keys())
            if len(keys) == 1:
                oneobs = True
                res2 = res2[keys[0]]
        if self.all or oneobs:

            name_row = '{} - {}\n' \
                       '{}'.format(self.dict_name[id]['run'],
                                   self.dict_name[id]['scenario'],
                                   varhq)
            dist_lst = res2['dist_err'][0]
            for id, dist in enumerate(dist_lst):
                tab_fill[dist] = {}
                tab_fill[dist][name_row] = res2[var][1][id]
                lst_col.append(name_row)
        else:
            for code in res2.keys():
                name_row = '{} - {}\n' \
                           '{} - {}'.format(self.dict_name[id]['run'],
                                            self.dict_name[id]['scenario'],
                                            varhq, code)
                dist_lst = res2[code]['dist_err'][0]
                for id, dist in enumerate(dist_lst):
                    tab_fill[dist] = {name_row: res2[code][var][1][id]}
                    lst_col.append(name_row)

        return tab_fill, lst_col

    def clear_tab(self):
        """clear table"""
        self.table_dist_abs.clear()
        self.table_dist.clear()
        self.bt_export_csv.setEnabled(False)

    def export_csv(self):
        """Export Table to .CSV file"""
        title = self.table_dist.horizontalHeaderItem(0).text().split('\n')
        txt = 'Quantiles_{}'.format(title[0])

        default_name = txt.replace(' ', '_').replace(':', '-')
        file_name_path, _ = QFileDialog.getSaveFileName(self,
                                                        "saveFile",
                                                        "{0}.csv".format(
                                                            default_name),
                                                        filter="CSV (*.csv *.)")
        if file_name_path:
            cur_tw = self.table_dist
            range_r = range(0, cur_tw.rowCount())
            range_c = range(0, cur_tw.columnCount())
            clipboard = self.tw_to_txt(cur_tw, range_r, range_c, ';')
            cur_tw_abs = self.table_dist_abs
            range_r = range(0, cur_tw_abs.rowCount())
            range_c = range(0, cur_tw_abs.columnCount())
            clipboard_abs = self.tw_to_txt(cur_tw, range_r, range_c, ';')
            file = open(file_name_path, 'w')
            file.write("Error quantiles\n\n")
            file.write(clipboard)
            file.write('\n\n')
            file.write("Absolute error quantiles\n\n")
            file.write(clipboard_abs)
            file.close()

    def tw_to_txt(self, tw, range_r, range_c, sep):
        """
        change table data to  text data
        :param tw: table object
        :param range_r: range of row
        :param range_c:range of column
        :param sep: separator
        :return:
        """
        clipboard = 'Distribution step' + sep
        for c in range_c:
            if c != range_c[-1]:
                clipboard = '{}{}{}'.format(clipboard,
                                            tw.horizontalHeaderItem(
                                                c).text().replace('\n', ' '),
                                            sep)
            else:
                clipboard = '{}{}\n'.format(clipboard,
                                            tw.horizontalHeaderItem(
                                                c).text().replace('\n', ' '))

        for r in range_r:
            clipboard = '{}{}{}'.format(clipboard,
                                        tw.verticalHeaderItem(r).text(),
                                        sep)
            for c in range_c:
                if tw.item(r, c):
                    val = tw.item(r, c).data(0)
                else:
                    val = ''
                if c != range_c[-1]:
                    clipboard = '{}{}{}'.format(clipboard,
                                                val,
                                                sep)
                else:
                    clipboard = '{}{}\n'.format(clipboard,
                                                val)

        return clipboard
