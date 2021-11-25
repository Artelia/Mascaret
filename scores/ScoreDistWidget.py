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
        self.res = {}
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
        if not ('quantil' in self.res.keys()):
            return
        err_typ_lst = ['quantil']
        id_lst = []

        for err in err_typ_lst:
            for idrun in self.res[err].keys():
                id_lst.append(idrun)
        id_lst = list(set(id_lst))

        if len(id_lst) > 0:
            self.dict_name = self.mdb.get_scen_name(id_lst)
        else:
            self.dict_name = {}

        lst_col = []
        tab_fill = {}
        tab_fill_abs = {}
        for err_typ in err_typ_lst:
            for idrun, dict_id in self.res[err_typ].items():
                for pk, dict_pk in dict_id.items():
                    for code, dict_code in dict_pk.items():
                        for varq, tmp_var in dict_code.items():
                            name_col = '{} - {}\n' \
                                       '{}\n' \
                                       '{} - {}'.format(
                                self.dict_name[idrun]['run'],
                                self.dict_name[idrun]['scenario'],
                                pk,
                                code,
                                varq)
                            lst_col.append(name_col)
                            for err, tmp in tmp_var.items():
                                dist_lst = tmp[0]
                                for id, dist in enumerate(dist_lst):
                                    if err == 'dist_err':
                                        if dist in tab_fill.keys():
                                            tab_fill[dist][name_col] = tmp[1][
                                                id]
                                        else:
                                            tab_fill[dist] = {
                                                name_col: tmp[1][id]}
                                    elif err == 'dist_abs_err':
                                        if dist in tab_fill_abs.keys():
                                            tab_fill_abs[dist][name_col] = \
                                            tmp[1][id]
                                        else:
                                            tab_fill_abs[dist] = {
                                                name_col: tmp[1][id]}

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
                    item.setFlags(Qt.ItemIsEnabled)
                    col = columns.index(tmp)
                    self.table_dist.setItem(row, col, item)
                for tmp in tab_fill_abs[dist].keys():
                    item = QTableWidgetItem(
                        '{:.3f}'.format(tab_fill_abs[dist][tmp]))
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    item.setFlags(Qt.ItemIsEnabled)
                    col = columns.index(tmp)
                    self.table_dist_abs.setItem(row, col, item)

            self.bt_export_csv.setEnabled(True)

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
