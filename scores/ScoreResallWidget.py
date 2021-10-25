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


class ScoreResallWidget(QWidget):
    def __init__(self, windmain):
        QWidget.__init__(self)
        self.windmain = windmain
        self.all = windmain.all
        self.mdb = self.windmain.mgis.mdb
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath,
                         'ui/scores/ui_results_all_score.ui'), self)
        self.dict_name = {}
        self.res = {}
        self.lst_runs = []
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
        self.data_err = {
            'simple': 'Simple error',
            'nash_crit': 'Nash-Sutcliffe criterion',
            'volume': "Error on volumes",
            'tips_err': "Errors on the peaks",
            'persistence': "Persistence score"
        }


    def add_dict(self,err_typ,err,name_line,code, tmp):
        """

        :return:
        """

        if err_typ in self.tab_fill.keys():
            if err in self.tab_fill[err_typ].keys():
                if name_line in self.tab_fill[err_typ][err].keys():
                    self.tab_fill[err_typ][err][name_line][code] = tmp
                else:
                    self.tab_fill[err_typ][err][name_line] = {code: tmp}
            else:
                self.tab_fill[err_typ][err] = {name_line: {code: tmp}}
        else:
            self.tab_fill[err_typ] = {err :{name_line : {code: tmp}}}

    def fill_tab(self):
        self.clear_tab()
        self.get_data()
        self.add_gui()
        self.fill_table()

    def get_data(self):
        """ fill table"""
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
        self.tab_fill = {}
        # tab_fill[tab][sstab][line][col]= val
        for err_typ in err_typ_lst:
            for idrun, dict_id in self.res[err_typ].items():
                for code, dict_code in dict_id.items():
                    for varq, tmp_var in dict_code.items():
                        name_line = '{} - {}'.format(
                            self.dict_name[idrun]['run'],
                            self.dict_name[idrun]['scenario'])
                        name_col = '{} - {}'.format(code, varq)
                        for err, tmp in tmp_var.items():
                            self.add_dict(err_typ,err,name_line,name_col, tmp)
                            # tab_fill[err_typ][err][name_line] = {code : tmp}

    def add_gui(self):
        """GUI gestion"""
        self.parent = {}
        self.child = {}
        if len(self.tab_fill.keys()) > 0:
            for err_typ,tab_err_typ  in self.tab_fill.items():
                self.parent[err_typ] =  QTabWidget()
                self.child[err_typ] = {}
                self.tabWidget.addTab(self.parent[err_typ], self.data_err[err_typ])
                for err, tab_err in tab_err_typ.items():
                    self.child[err_typ][err] = QTableWidget()
                    self.parent[err_typ].addTab(self.child[err_typ][err],
                                                self.data_write[err])

    def fill_table(self):
        if len(self.tab_fill.keys()) > 0:
            for err_typ,tab_err_typ  in self.tab_fill.items():
                for err, tab_err in tab_err_typ.items():
                    # self.tab_fill[err_typ][err][name_line] = {code: tmp}
                    line_lst= [v for v in tab_err.keys()]
                    lst_col = []
                    for line in line_lst:
                        lst_col += list(tab_err[line].keys())
                    nb_line = len(line_lst)
                    columns = list(set(lst_col))
                    nb_col = len(columns)
                    self.child[err_typ][err].setRowCount(nb_line)
                    self.child[err_typ][err].setColumnCount(nb_col)
                    self.child[err_typ][err].setVerticalHeaderLabels(line_lst)
                    self.child[err_typ][err].setHorizontalHeaderLabels(columns)
                    for row, dist in enumerate(line_lst):
                        for tmp in tab_err[dist].keys():
                            val = tab_err[dist][tmp]
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
                            self.child[err_typ][err].setItem(row, col, item)
    #
    def clear_tab(self):
        """clear table"""
        self.tabWidget.clear()
        self.child = {}
        self.parent = {}

        # self.bt_export_csv.setEnabled(False)

    def export_csv(self):
        """Export Table to .CSV file"""
    #               erreur 1         erreur 2
    #  ligne run    observations    observations


        txt = 'Scores_results.csv
        # default_name = txt.replace(' ', '_').replace(':', '-')
        file_name_path, _ = QFileDialog.getSaveFileName(self,
                                                        "saveFile",
                                                        "{0}.csv".format(
                                                            default_name),
                                                        filter="CSV (*.csv *.)")
        if file_name_path:
            file = open(file_name_path, 'w')
            file.write(clipboard)
            file.close()


    def clipboard_fill(self,sep = ';'):
        # txt =  ''
        #
        # for err_typ, tab_err_typ in self.tab_fill.items():
        #     for err, tab_err in tab_err_typ.items():
        # liste tout les line possible
        # liste toute les clones et doublons
        #  completer les ligne et colonne du fichier
        #         for name_line, tab_line  in tab_err.items():
        #             line = '{} {}'.format(name_line, sep)
        #             for col, tmp in tab_line.items():
        #                 line+= '{} {}'.format(tmp, sep)
        #
        #         {}

                {name_line}{sep}{err1/obs1}{sep}{err1/obs2}{sep}{err2/obs1}{sep}{err2/obs2}
        # self.tab_fill[err_typ][err][name_line] = {code: tmp}



        #    cur_tw = self.table_res
        #     range_r = range(0, cur_tw.rowCount())
        #     range_c = range(0, cur_tw.columnCount())
        #     clipboard = self.tw_to_txt(cur_tw, range_r, range_c, ';')
        #     file = open(file_name_path, 'w')
        #     file.write(clipboard)
        #     file.close()
    #
    # def tw_to_txt(self, tw, range_r, range_c, sep):
    #     """
    #     change table data to  text data
    #     :param tw: table object
    #     :param range_r: range of row
    #     :param range_c:range of column
    #     :param sep: separator
    #     :return:
    #     """
    #     clipboard = '{}'.format(sep)
    #     for c in range_c:
    #         if c != range_c[-1]:
    #             clipboard = '{}{}{}'.format(clipboard,
    #                                         tw.horizontalHeaderItem(
    #                                             c).text().replace('\n', ' '),
    #                                         sep)
    #         else:
    #             clipboard = '{}{}\n'.format(clipboard,
    #                                         tw.horizontalHeaderItem(
    #                                             c).text().replace('\n', ' '))
    #
    #     for r in range_r:
    #         clipboard = '{}{}{}'.format(clipboard,
    #                                     tw.verticalHeaderItem(r).text(),
    #                                     sep)
    #
    #         for c in range_c:
    #             if tw.item(r, c):
    #                 val = tw.item(r, c).data(0)
    #             else:
    #                 val = ''
    #             if c != range_c[-1]:
    #                 clipboard = '{}{}{}'.format(clipboard,
    #                                             val,
    #                                             sep)
    #             else:
    #                 clipboard = '{}{}\n'.format(clipboard,
    #                                             val)
    #
    #     return clipboard
