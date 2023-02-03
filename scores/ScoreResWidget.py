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

from qgis.PyQt.QtWidgets import *


class ScoreResWidget(QWidget):
    def __init__(self, windmain):
        QWidget.__init__(self)
        self.windmain = windmain
        self.all = windmain.all
        self.mdb = self.windmain.mgis.mdb
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath,
                         'ui/scores/ui_results_score.ui'), self)
        self.dict_name = {}
        self.res = {}
        #
        self.data_write = {
            'mean_err': 'Mean error',
            'mean_abs_err': 'Mean absolute error',
            'mean_r_err': 'Mean relative error',
            'biais': 'Mean relative error in % (biais)',
            'mean_rabs_err': 'Mean relative absolute error',
            'precision': 'Mean relative absolute error in % (precision)',
            'std': 'Standard deviation',
            'eqm': 'Mean square error',
            'ns_err': 'Nash - Sutcliffe criterion',
            'vol_err': "Error on volumes",
            'pts_err': "Errors on the peaks",
            'pts_time_err': "Time shift on the peaks",
            'per_err': 'Persistence'
        }

        self.bt_export_csv.clicked.connect(self.export_csv)
        self.bt_export_csv.setEnabled(False)

    def fill_tab(self):
        """ fill table"""
        self.clear_tab()
        err_typ_lst = [err for err in self.res.keys() if err != 'quantil']
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
                                if err in tab_fill.keys():
                                    tab_fill[err][name_col] = tmp
                                else:
                                    tab_fill[err] = {name_col: tmp}

        if len(tab_fill.keys()) > 0:

            err_lst = [v for v in tab_fill.keys()]
            nb_line = len(err_lst)
            columns = list(set(lst_col))
            nb_col = len(columns)
            self.table_res.setRowCount(nb_line)
            self.table_res.setColumnCount(nb_col)
            self.table_res.setVerticalHeaderLabels(
                [self.data_write[v] for v in err_lst])
            self.table_res.setHorizontalHeaderLabels(columns)
            for row, dist in enumerate(err_lst):
                for tmp in tab_fill[dist].keys():
                    val = tab_fill[dist][tmp]
                    if val is None:
                        val = ''
                    if isinstance(val, str):
                        item = QTableWidgetItem(
                            '{}'.format(val))
                    elif dist == 'vol_err':
                        item = QTableWidgetItem(
                            '{:e}'.format(val))
                    else:
                        item = QTableWidgetItem('{:.3f}'.format(val))
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    item.setFlags(Qt.ItemIsEnabled)
                    col = columns.index(tmp)
                    self.table_res.setItem(row, col, item)

            self.bt_export_csv.setEnabled(True)

    def clear_tab(self):
        """clear table"""
        self.table_res.clear()
        self.bt_export_csv.setEnabled(False)

    def export_csv(self):
        """Export Table to .CSV file"""
        title = self.table_res.horizontalHeaderItem(0).text().split('\n')
        txt = 'Scores_{}'.format(title[0])
        #default_name = txt.replace(' ', '_').replace(':', '-')
        default_name = os.path.join(self.windmain.mgis.repProject, txt.replace(' ', '_').replace(':', '-'))
        file_name_path, _ = QFileDialog.getSaveFileName(self,
                                                        "saveFile",
                                                        "{0}.csv".format(
                                                            default_name),
                                                        filter="CSV (*.csv *.)")
        if file_name_path:
            self.windmain.mgis.up_rep_project(file_name_path)
            cur_tw = self.table_res
            range_r = range(0, cur_tw.rowCount())
            range_c = range(0, cur_tw.columnCount())
            clipboard = self.tw_to_txt(cur_tw, range_r, range_c, ';')
            file = open(file_name_path, 'w')
            file.write(clipboard)
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
        clipboard = '{}'.format(sep)
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
