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
        for id in self.res.keys():
            if 'H' in self.res[id].keys():
                if 'quantil' in self.res[id]['H'].keys():
                    tab_fill.update(self.fill_dico(id, 'H', 'dist_err'))
                    tab_fill_abs.update(self.fill_dico(id, 'H', 'dist_abs_err'))
            if 'Q' in self.res[id].keys():
                if 'quantil' in self.res[id]['Q'].keys():
                    tab_fill.update(self.fill_dico(id, 'Q', 'dist_err'))
                    tab_fill_abs.update(self.fill_dico(id, 'Q', 'dist_abs_err'))

        if len(tab_fill.keys()) > 0:
            dist_lst = [v for v in tab_fill.keys()]
            nb_line = len(dist_lst)
            columns = [str(v) for v in tab_fill[dist_lst[0]].keys()]
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
                for col, tmp in enumerate(tab_fill[dist].keys()):
                    item = QTableWidgetItem(
                        '{:.3f}'.format(tab_fill[dist][tmp]))
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table_dist.setItem(row, col, item)
                for col, tmp in enumerate(tab_fill_abs[dist].keys()):
                    item = QTableWidgetItem(
                        '{:.3f}'.format(tab_fill[dist][tmp]))
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
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

        code = None
        oneobs =  False
        if not self.all :
            keys = list(res2.keys())
            if len(keys)==1:
                oneobs= True
                res2 =  res2[keys[0]]
        if self.all  or oneobs:

            name_row = '{} - {}\n' \
                       '{}'.format(self.dict_name[id]['run'],
                                   self.dict_name[id]['scenario'],
                                   varhq)
            dist_lst = res2['dist_err'][0]
            for id, dist in enumerate(dist_lst):
                tab_fill[dist] = {}
                tab_fill[dist][name_row] = res2[var][1][id]
        else:
            for code in res2.keys():
                name_row = '{} - {}\n' \
                                   '{} - {}'.format(self.dict_name[id]['run'],
                                                    self.dict_name[id]['scenario'],
                                                    varhq, code)
                dist_lst = res2[code]['dist_err'][0]
                for id, dist in enumerate(dist_lst):
                    tab_fill[dist] = { name_row : res2[code][var][1][id]}

        return tab_fill

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
                if c != range_c[-1]:
                    clipboard = '{}{}{}'.format(clipboard,
                                                tw.item(r, c).data(0),
                                                sep)
                else:
                    clipboard = '{}{}\n'.format(clipboard,
                                                tw.item(r, c).data(0))

        return clipboard
