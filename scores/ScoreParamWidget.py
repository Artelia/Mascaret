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
from datetime import datetime, timedelta
import numpy as np
from scipy import interpolate

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ClassScores import ClassScores
from ..Function import datum_to_float
from ..ui.custom_control import datetime2QDateTime


class ScoreParamWidget(QWidget):
    def __init__(self, windmain, all=True, ):
        QWidget.__init__(self)
        self.windmain = windmain
        self.mdb = self.windmain.mgis.mdb
        self.mgis = self.windmain.mgis
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath,
                         'ui/scores/ui_parametre.ui'), self)

        self.cl_score = ClassScores()
        self.lst_runs = []
        self.init_dates = None
        self.all = all
        self.cur_pknum = None

        self.data = {}
        # {id : { h : [],time : [], q :[]}}
        self.res = {}
        self.type_res = {
            'simple': False,
            'nash_crit': False,
            'volume': False,
            'quantil': False,
        }
        self.lk_wgt_row = {'ref_time': 0,
                           'per_step_t': 1,
                           'per_start_t': 2,
                           'per_last_t': 3,
                           'pt_start_t': 4,
                           'pt_last_t': 5,
                           'pt_alpha_Q': 6,
                           'pt_alpha_H': 7, }
        self.param = {}
        self.widget_d = {}

        self.init_gui()

        self.bt_calcul_scores.clicked.connect(self.bt_calcul_fct)
        self.bt_default.clicked.connect(self.bt_default_fct)

    def init_gui(self):
        """
        initialize GUI
        :return:
        """

        # default value
        self.dsp_dist_quantil.setValue(25)

        if len(self.lst_runs) > 0:
            dict_name = self.mdb.get_scen_name(self.lst_runs)

            self.tw_param.setColumnCount(len(self.lst_runs))
            for col, id_run in enumerate(self.lst_runs):
                self.widget_d[id_run] = {
                    'ref_time': QDateTimeEdit(self),
                    'per_step_t': QDoubleSpinBox(self),
                    'per_start_t': QDateTimeEdit(self),
                    'per_last_t': QDateTimeEdit(self),
                    'pt_start_t': QDateTimeEdit(self),
                    'pt_last_t': QDateTimeEdit(self),
                    'pt_alpha_Q': QDoubleSpinBox(self),
                    'pt_alpha_H': QDoubleSpinBox(self), }

                # ************ add style widget ************
                for ctrl_ in ['per_start_t', 'pt_start_t', 'per_last_t',
                              'pt_last_t', 'ref_time']:
                    self.widget_d[id_run][ctrl_].setCalendarPopup(True)
                    self.widget_d[id_run][ctrl_].setDisplayFormat(
                        'yyyy. MM.dd hh:mm:ss')

                    self.widget_d[id_run][ctrl_].setDateTimeRange(
                        QDateTime(1800, 1, 1, 00, 00, 00),
                        QDateTime(9999, 1, 1, 00, 00, 00))

                for ctrl_ in ['pt_alpha_Q', 'pt_alpha_H', 'per_step_t']:
                    self.widget_d[id_run][ctrl_].setMinimum(0)
                    self.widget_d[id_run][ctrl_].setSingleStep(0.1)
                    self.widget_d[id_run][ctrl_].setDecimals(2)
                    self.widget_d[id_run][ctrl_].setMaximum(9999999)

                # ************ add initialisation widget ************
                date_init, lst_times = self.get_times(id_run)
                tmps = datetime.today()
                if len(lst_times) > 1:
                    deltat = lst_times[1] - lst_times[0]
                else:
                    deltat = 1
                if isinstance(date_init, datetime):
                    final_date = date_init + timedelta(seconds=lst_times[-1])
                else:

                    # self.today = QDateTime(tmps.year, tmps.month, tmps.day, 0, 0, 0)
                    date_init = datetime(tmps.year,
                                         tmps.month,
                                         tmps.day,
                                         0, 0, 0)
                    final_date = datetime(tmps.year,
                                          tmps.month,
                                          tmps.day,
                                          1, 0, 0)
                    self.widget_d[id_run]['ref_time'].setStyleSheet(
                        'color: red')

                init_date_crt = datetime2QDateTime(date_init)
                last_date_crt = datetime2QDateTime(final_date)
                self.widget_d[id_run]['ref_time'].setDateTime(init_date_crt)

                for ctrl_ in ['per_start_t', 'pt_start_t']:
                    self.widget_d[id_run][ctrl_].setDateTime(init_date_crt)
                for ctrl_ in ['per_last_t', 'pt_last_t']:
                    self.widget_d[id_run][ctrl_].setDateTime(last_date_crt)

                for ctrl_ in ['pt_alpha_Q', 'pt_alpha_H']:
                    self.widget_d[id_run][ctrl_].setValue(1)
                print(deltat)
                self.widget_d[id_run]['per_step_t'].setValue(deltat)
                # ******** add control ************
                self.widget_d[id_run]['ref_time'].dateTimeChanged.connect(
                    self.ch_date_ref)

                for ctrl_ in ['per_start_t', 'pt_start_t']:
                    self.widget_d[id_run][ctrl_].dateTimeChanged.connect(
                        self.ch_date_limit)
                for ctrl_ in ['per_last_t', 'pt_last_t']:
                    self.widget_d[id_run][ctrl_].dateTimeChanged.connect(
                        self.ch_date_limit)
                # ************ fill table ************
                name_col = '{} - {}'.format(dict_name[id_run]['run'],
                                            dict_name[id_run]['scenario'])
                self.tw_param.setHorizontalHeaderItem(col, QTableWidgetItem(
                    name_col))

                currentRowCount = self.tw_param.rowCount()  # necessary even when there are no rows in the table
                for ctrl_, row in self.lk_wgt_row.items():
                    self.tw_param.setCellWidget(row, col,
                                                self.widget_d[id_run][ctrl_])

                self.param[id_run] = {'lst_times': lst_times,
                                      'ref_time': date_init,
                                      'per_step_t': deltat,
                                      'per_start_t': date_init,
                                      'per_last_t': final_date,
                                      'pt_start_t': date_init,
                                      'pt_last_t': final_date,
                                      'pt_alpha_Q': 1,
                                      'pt_alpha_H': 1
                                      }

    def bt_default_fct(self):
        """
        Relit la based donnee pour mettre à jours la table
        :return:
        """
        self.init_gui()
        pass

    def get_times(self, id_run, only_init=False):
        """
        Get reference date if exist
        and time list of model
        :param id_run: run index
        :return:
        """
        dico = self.mdb.select("runs",
                               where="id={0}".format(id_run))
        init_time = dico["init_date"][0]
        if only_init:
            return init_time

        info = self.mdb.select('runs_graph',
                               where="id_runs={} "
                                     "AND type_res='opt'"
                                     "AND var='time'".format(id_run),
                               list_var=['val'])
        lst_times = info['val'][0]
        return init_time, lst_times

    def clean_type_res(self):
        """
        clean type_res
        :return:
        """
        self.type_res = {
            'simple': False,
            'nash_crit': False,
            'volume': False,
            'quantil': False,
        }

    def bt_calcul_fct(self):
        """
        action when click on button
        :return:
        """

        self.get_parameter()
        self.clean_type_res()
        self.cpt_score()

        tabscores = self.windmain.tabscores
        id_dist = tabscores.indexOf(self.windmain.wgt_dist)
        id_res = tabscores.indexOf(self.windmain.wgt_res)
        cond_enable = {'quantil': False, 'res': False}
        for key, cond in self.type_res.items():
            if key in ['quantil'] and cond:
                cond_enable['quantil'] = True
            elif cond:
                cond_enable['res'] = True

        tabscores.setTabEnabled(id_dist, cond_enable['quantil'])
        tabscores.setTabEnabled(id_res, cond_enable['res'])

    def create_obs_pre(self, id_run, pknum):
        """
        create Model data and Observation data with that compute the scores
        :param id_run: run index
        :return:
        """
        h_obs = np.array([])
        h_pred = np.array([])
        q_obs = np.array([])
        q_pred = np.array([])

        if self.all:
            # TODO first elem 0 à check

            for code in self.data[id_run].keys():
                if code == 'hcompt' or code == 'qcompt':
                    continue
                if self.data[id_run]['hcompt']:
                    h_obs = np.concatenate(
                        (h_obs, self.data[id_run][code]['h_obs']), axis=0)
                    h_pred = np.concatenate(
                        (h_pred, self.data[id_run][code]['h_mod']), axis=0)
                if self.data[id_run]['qcompt']:
                    q_obs = np.concatenate(
                        (q_obs, self.data[id_run][code]['q_obs']), axis=0)
                    q_pred = np.concatenate(
                        (q_pred, self.data[id_run][code]['q_mod']), axis=0)
        else:
            for code in self.data[id_run].keys():
                if code == 'hcompt' or code == 'qcompt':
                    continue
                if self.data[id_run]['hcompt']:
                    h_obs = np.concatenate(
                        (h_obs, self.data[id_run][code]['h_obs']), axis=0)
                    h_pred = np.concatenate(
                        (h_pred, self.data[id_run][code]['h_mod']), axis=0)
                if self.data[id_run]['qcompt']:
                    q_obs = np.concatenate(
                        (q_obs, self.data[id_run][code]['q_obs']), axis=0)
                    q_pred = np.concatenate(
                        (q_pred, self.data[id_run][code]['q_mod']), axis=0)

        return h_obs, h_pred, q_obs, q_pred

    def cpt_score(self):
        """
        run the scores compute
        :return:
        """
        self.get_alldata()

        # TODO demander pour les deltat si variable? => persistance non variable
        # TODO demandé si je fait un croisment ou interpolation linear du modèle ?
        dict_name = self.mdb.get_scen_name(self.model.keys())
        add_txt = ''
        for id_run in self.no_obs:
            name_run = '{} - {}'.format(dict_name[id_run]['run'],
                                        dict_name[id_run]['scenario'])
            add_txt += '- No observation for the Run : {}\n'.format(name_run)

        for id_run in self.model.keys():
            name_run = '{} - {}'.format(dict_name[id_run]['run'],
                                        dict_name[id_run]['scenario'])
            if self.ch_simple_err.isChecked():
                if not self.cpt_simple_err(id_run):
                    add_txt += '- Simple scores (Run : {})\n'.format(name_run)

            if self.ch_ns_err.isChecked():
                if not self.cpt_ns_err(id_run):
                    add_txt += '- Nash - Sutcliffe criterion ' \
                               '(Run : {})\n'.format(name_run)

            if self.ch_vol_err.isChecked():
                if not self.cpt_vol_err(id_run):
                    add_txt += '- Volume error (Run : {})\n'.format(name_run)

            if self.ch_quantil_err.isChecked():
                if not self.cpt_quantil_err(id_run):
                    add_txt += '- Quantil error (Run : {})\n'.format(name_run)

            if self.ch_persistence.isChecked():
                # check pas de temps régulier

                # message de non calcul
                # self.start_time_persistence
                # self.last_time_persistence
                pass
            if self.ch_pointe_err.isChecked():
                # self.start_time_point
                # self.last_time_point
                # self.alpha_Hcc
                # self.alpha_Q
                pass
        if add_txt != '':
            txt = 'No data, to compute : \n {}'.format(add_txt)
            QMessageBox.warning(None, 'Warning',
                                txt)

    def cpt_simple_err_old(self, id_run):
        """
        compute simple scores :

        mean_err :mean_err
        mean absolute error :mean_abs_err
        mean relative error : mean_r_err
        mean relative error in % : biais
        mean relative absolute error : mean_rabs_err
        mean relative absolute error in % : precision
        standard deviation : std
        mean square error :eqm
        :param id_run:  run index
        :return:
        """
        out = False
        h_obs, h_pred, q_obs, q_pred = self.create_obs_pre(id_run,
                                                           pknum=None)
        if self.data[id_run]['hcompt']:
            y_obs = h_obs
            y_pred = h_pred
            self.res[id_run]['H']['simple'] = \
                {
                    'mean_err': self.cl_score.mean_err(y_obs, y_pred),
                    'mean_abs_err': self.cl_score.mean_abs_err(y_obs, y_pred),
                    'mean_r_err': self.cl_score.mean_r_err(y_obs, y_pred),
                    'biais': self.cl_score.biais(y_obs, y_pred),
                    'mean_rabs_err': self.cl_score.mean_rabs_err(y_obs, y_pred),
                    'precision': self.cl_score.precision(y_obs, y_pred),
                    'std': self.cl_score.std(y_obs, y_pred),
                    'eqm': self.cl_score.eqm(y_obs, y_pred)
                }
            self.type_res['simple'] = True
            out = True
        if self.data[id_run]['qcompt']:
            y_obs = q_obs
            y_pred = q_pred
            self.res[id_run]['Q']['simple'] = \
                {
                    'mean_err': self.cl_score.mean_err(y_obs, y_pred),
                    'mean_abs_err': self.cl_score.mean_abs_err(y_obs, y_pred),
                    'mean_r_err': self.cl_score.mean_r_err(y_obs, y_pred),
                    'biais': self.cl_score.biais(y_obs, y_pred),
                    'mean_rabs_err': self.cl_score.mean_rabs_err(y_obs, y_pred),
                    'precision': self.cl_score.precision(y_obs, y_pred),
                    'std': self.cl_score.std(y_obs, y_pred),
                    'eqm': self.cl_score.eqm(y_obs, y_pred)
                }
            self.type_res['simple'] = True
            out = True
        return out

    def creat_dict_simple(self, y_obs, y_pred):
        """

        :param y_obs: observation data
        :param y_pred: model data
        :return:
        """
        dict_res = {
            'mean_err': self.cl_score.mean_err(y_obs, y_pred),
            'mean_abs_err': self.cl_score.mean_abs_err(y_obs, y_pred),
            'mean_r_err': self.cl_score.mean_r_err(y_obs, y_pred),
            'biais': self.cl_score.biais(y_obs, y_pred),
            'mean_rabs_err': self.cl_score.mean_rabs_err(y_obs, y_pred),
            'precision': self.cl_score.precision(y_obs, y_pred),
            'std': self.cl_score.std(y_obs, y_pred),
            'eqm': self.cl_score.eqm(y_obs, y_pred)
        }
        return dict_res

    def cpt_simple_err(self, id_run):
        """
        compute simple scores :

        mean_err :mean_err
        mean absolute error :mean_abs_err
        mean relative error : mean_r_err
        mean relative error in % : biais
        mean relative absolute error : mean_rabs_err
        mean relative absolute error in % : precision
        standard deviation : std
        mean square error :eqm
        :param id_run:  run index
        :return:
        """
        out = False

        if self.data[id_run]['hcompt']:
            h_obs = np.array([])
            h_pred = np.array([])
            # TODO first elem 0 à check
            dict_tmp = {}
            for code in self.data[id_run].keys():
                if code == 'hcompt' or code == 'qcompt':
                    continue
                if  self.all:
                    h_obs = np.concatenate(
                        (h_obs, self.data[id_run][code]['h_obs']), axis=0)
                    h_pred = np.concatenate(
                        (h_pred, self.data[id_run][code]['h_mod']), axis=0)
                else:
                    dict_tmp[code] = self.creat_dict_simple(
                        self.data[id_run][code]['h_obs'],
                        self.data[id_run][code]['h_mod'])
            if self.all:
                self.res[id_run]['H']['simple'] = self.creat_dict_simple(h_obs,
                                                                         h_pred)
            else:
                self.res[id_run]['H']['simple'] =  dict_tmp
            self.type_res['simple'] = True
            out = True

        if self.data[id_run]['qcompt']:
            q_obs = np.array([])
            q_pred = np.array([])
            dict_tmp = {}
            for code in self.data[id_run].keys():
                if code == 'hcompt' or code == 'qcompt':
                    continue
                if self.all:
                    q_obs = np.concatenate(
                        (q_obs, self.data[id_run][code]['q_obs']), axis=0)
                    q_pred = np.concatenate(
                        (q_pred, self.data[id_run][code]['q_mod']), axis=0)
                else:
                    dict_tmp[code] = self.creat_dict_simple(
                        self.data[id_run][code]['q_obs'],
                        self.data[id_run][code]['q_mod'])
            if self.all:
                self.res[id_run]['Q']['simple'] = self.creat_dict_simple(q_obs,
                                                                         q_pred)
            else:
                self.res[id_run]['Q']['simple'] = dict_tmp
            self.type_res['simple'] = True
            out = True
        return out

    def cpt_ns_err(self,id_run):
        """
        compute Nash-Sutcliffe criterion
        :param id_run:  run index
        :return:
        """
        out = False

        if self.data[id_run]['hcompt']:
            h_obs = np.array([])
            h_pred = np.array([])
            # TODO first elem 0 à check
            dict_tmp = {}
            for code in self.data[id_run].keys():
                if code == 'hcompt' or code == 'qcompt':
                    continue
                if self.all:
                    h_obs = np.concatenate(
                        (h_obs, self.data[id_run][code]['h_obs']), axis=0)
                    h_pred = np.concatenate(
                        (h_pred, self.data[id_run][code]['h_mod']), axis=0)
                else:
                    dict_tmp[code] = \
                        {
                            'ns_err': self.cl_score.nash_crit(
                                self.data[id_run][code]['h_obs'],
                                self.data[id_run][code]['h_mod'])
                        }
            if self.all:
                self.res[id_run]['H']['nash_crit'] = \
                    {
                        'ns_err': self.cl_score.nash_crit(h_obs, h_pred)
                    }
            else:
                self.res[id_run]['H']['nash_crit'] = dict_tmp
            self.type_res['nash_crit'] = True
            out = True

        if self.data[id_run]['qcompt']:
            q_obs = np.array([])
            q_pred = np.array([])
            dict_tmp = {}
            for code in self.data[id_run].keys():
                if code == 'hcompt' or code == 'qcompt':
                    continue
                if self.all:
                    q_obs = np.concatenate(
                        (q_obs, self.data[id_run][code]['q_obs']), axis=0)
                    q_pred = np.concatenate(
                        (q_pred, self.data[id_run][code]['q_mod']), axis=0)
                else:
                    dict_tmp[code] = self.cl_score.nash_crit(
                        self.data[id_run][code]['q_obs'],
                        self.data[id_run][code]['q_mod'])
            if self.all:
                self.res[id_run]['Q']['nash_crit'] =  {
                        'ns_err': self.cl_score.nash_crit(h_obs, h_pred)
                    }
            else:
                self.res[id_run]['Q']['nash_crit'] =   dict_tmp[code]

            self.type_res['nash_crit'] = True
            out = True
        return out

    def cpt_ns_err_old(self, id_run):
        """
        compute Nash-Sutcliffe criterion
        :param id_run:  run index
        :return:
        """
        # self.cl_score.nash_crit(y_obs, y_pred)
        out = False
        h_obs, h_pred, q_obs, q_pred = self.create_obs_pre(id_run,
                                                           pknum=None)
        if self.data[id_run]['hcompt']:
            self.res[id_run]['H']['nash_crit'] = \
                {
                    'ns_err': self.cl_score.nash_crit(h_obs, h_pred)
                }
            self.type_res['nash_crit'] = True
            out = True
        if self.data[id_run]['qcompt']:
            self.res[id_run]['Q']['nash_crit'] = \
                {
                    'ns_err': self.cl_score.nash_crit(q_obs, q_pred)
                }
            self.type_res['nash_crit'] = True
            out = True
        return out

    def cpt_vol_err(self, id_run):
        """
        compute Error on volumes
        :param id_run:  run index
        :return:
        """
        out = False
        err = 0
        dict_tmp = {}
        if self.data[id_run]['qcompt']:
            for code in self.data[id_run].keys():
                if code == 'hcompt' or code == 'qcompt':
                    continue
                q_obs = self.data[id_run][code]['q_obs']
                q_pred = self.data[id_run][code]['q_mod']
                # the same because model is sample on the observations
                lst_time_pred = self.data[id_run][code]['q_time']
                lst_time_obs = self.data[id_run][code]['q_time']
                if self.all:
                    err += self.cl_score.vol_err(q_obs, q_pred,
                                                 lst_time_pred, lst_time_obs)
                else:
                    dict_tmp[code] = {
                        'vol_err': self.cl_score.vol_err(q_obs, q_pred,
                                                         lst_time_pred,
                                                         lst_time_obs)}

            if self.all:
                self.res[id_run]['Q']['volume'] = {'vol_err': err}
            else:
                self.res[id_run]['Q']['volume'] = dict_tmp
            self.type_res['volume'] = True
            out = True
        return out

    def cpt_quantil_err_olde(self, id_run):
        """
        compute  quantiles:
            error quantiles : dist_err
            absolute error quantiles :  dist_abs_err
        :param id_run:  run index
        :return:
        """
        out = False
        h_obs, h_pred, q_obs, q_pred = self.create_obs_pre(id_run,
                                                           pknum=None)
        dist_step = self.dsp_dist_quantil.value()
        if self.data[id_run]['hcompt']:
            self.res[id_run]['H']['quantil'] = \
                {'dist_err': self.cl_score.dist_err(h_obs, h_pred, dist_step),
                 'dist_abs_err': self.cl_score.dist_err(h_obs, h_pred,
                                                        dist_step)}
            self.type_res['quantil'] = True
            out = True
        if self.data[id_run]['qcompt']:
            self.res[id_run]['Q']['quantil'] = {
                'dist_err': self.cl_score.dist_err(q_obs, q_pred, dist_step),
                'dist_abs_err': self.cl_score.dist_err(q_obs, q_pred,
                                                       dist_step)}

            self.type_res['quantil'] = True
            out = True
        return out

    def cpt_quantil_err(self, id_run):
        """
        compute  quantiles:
            error quantiles : dist_err
            absolute error quantiles :  dist_abs_err
        :param id_run:  run index
        :return:
        """
        out = False
        dist_step = self.dsp_dist_quantil.value()

        h_obs = np.array([])
        h_pred = np.array([])
        q_obs = np.array([])
        q_pred = np.array([])
        dict_tmp_h = {}
        dict_tmp_q = {}
        for code in self.data[id_run].keys():
            if code == 'hcompt' or code == 'qcompt':
                continue
            if self.data[id_run]['hcompt']:
                if self.all:
                    h_obs = np.concatenate(
                        (h_obs, self.data[id_run][code]['h_obs']), axis=0)
                    h_pred = np.concatenate(
                        (h_pred, self.data[id_run][code]['h_mod']), axis=0)
                else:
                    y_obs = self.data[id_run][code]['h_obs']
                    y_pred = self.data[id_run][code]['h_mod']
                    dict_tmp_h[code] = \
                        {'dist_err': self.cl_score.dist_err(y_obs, y_pred,
                                                            dist_step),
                         'dist_abs_err': self.cl_score.dist_err(y_obs, y_pred,
                                                                dist_step)}
            if self.data[id_run]['qcompt']:
                if self.all:
                    q_obs = np.concatenate(
                        (q_obs, self.data[id_run][code]['q_obs']), axis=0)
                    q_pred = np.concatenate(
                        (q_pred, self.data[id_run][code]['q_mod']), axis=0)
                else:
                        y_obs = self.data[id_run][code]['q_obs']
                        y_pred = self.data[id_run][code]['q_mod']
                        dict_tmp_q[code] = \
                            {'dist_err': self.cl_score.dist_err(y_obs, y_pred,
                                                                dist_step),
                             'dist_abs_err': self.cl_score.dist_err(y_obs,
                                                                    y_pred,
                                                                    dist_step)}

        if self.data[id_run]['hcompt']:
            if self.all:
                self.res[id_run]['H']['quantil'] = \
                    {'dist_err': self.cl_score.dist_err(h_obs, h_pred,
                                                        dist_step),
                     'dist_abs_err': self.cl_score.dist_err(h_obs, h_pred,
                                                            dist_step)}
            else:
                self.res[id_run]['Q']['quantil'] = dict_tmp_q
            self.type_res['quantil'] = True
            out = True
        if self.data[id_run]['qcompt']:
            if self.all:
                self.res[id_run]['Q']['quantil'] = \
                    {'dist_err': self.cl_score.dist_err(q_obs, q_pred,
                                                        dist_step),
                     'dist_abs_err': self.cl_score.dist_err(q_obs, q_pred,
                                                            dist_step)}
            else:
                self.res[id_run]['H']['quantil'] = dict_tmp_h
            self.type_res['quantil'] = True
            out = True

        return out

    def cpt_persistence(self, id_run):
        """
        compute persistence
        :return:
        """

        pass

    def cpt_pointe_err(self):
        """
        compute (L’erreur sur les pointes sur H et Q)
        :return:
        """
        pass

    def interpol_date(self, obs_time, time_model, var_model):
        """
        :param obs_time: array    observation time
        :param time_model: list(float)   model time
        :param var_model: array  model variable
        :return:
        """
        fct = interpolate.interp1d(time_model, var_model, kind='linear')
        model_var = fct(obs_time)
        return model_var

    def get_pknum(self, code):
        if self.obs[code]['abscissa']:
            where = 'abscissa = {1}'.format(self.obs[code]['abscissa'])
        elif self.obs[code]['name']:
            where = "name='{0}'".format(self.obs[code]['name'])
        else:
            print('No find profile {0}={1} '.format(self.obs[code]['name'],
                                                    self.obs[code]['abscissa']))
            return
        info = self.mdb.select('profiles',
                               where=where,
                               list_var=['abscissa'])

        pknum = info['abscissa'][0]
        return pknum

    def pknum2obs(self, id_run, pknum):
        where = 'abscissa = {0}'.format(pknum)
        info = self.mdb.select('profiles',
                               where=where,
                               list_var=['gid', 'name', 'abscissa'])
        name = None
        abs = None
        if len(info['abscissa']) > 0:
            name = info['name'][0]
            abs = info['abscissa'][0]

        else:

            where = ' id_runs={0} AND pk = {1}'.format(id_run, pknum)
            info = self.mdb.select_distinct('abscissa', 'results',
                                            where=where,
                                            ordre='abscissa')
            if len(info['abscissa']) > 0:
                abs = info['abscissa'][0]
        for code, dict in self.obs.items():
            if name:
                if dict['name'] == name:
                    return code
            if abs:
                if abs == dict['abscissa']:
                    return code

        return None

    def get_model(self, id_run, code):
        """
        get model data
        :return:
        """

        dict_model = self.model[id_run]
        lst_varh = []
        lst_varq = []
        if self.data[id_run]['hcompt']:
            if 'Z' in dict_model['var']:
                lst_varh.append('Z')
            elif 'ZREF' in dict_model['var'] and 'Y' in dict_model['var']:
                lst_varh.append('ZREF')
                lst_varh.append('Y')
            else:
                self.data[id_run]['hcompt'] = False

        if self.data[id_run]['qcompt']:
            if 'Q' in dict_model['var']:
                lst_varq.append('Q')
            elif 'QMIN' in dict_model['var'] and 'QMAJ' in dict_model['var']:
                lst_varq.append('QMIN')
                lst_varq.append('QMAJ')
            else:
                self.data[id_run]['qcompt'] = False

        pknum = self.get_pknum(code)
        lst_var = lst_varq + lst_varh
        tmp = {}
        for var in lst_var:
            val = self.mdb.select('results',
                                  where="id_runs={0} AND pknum= {1} " \
                                        "and var = {2}".format(id_run,
                                                               pknum,
                                                               dict_model[
                                                                   'var'][var]),
                                  order='time',
                                  list_var=['val'],
                                  verbose=True)
            tmp[var] = val['val']

        if len(lst_varh) > 0:
            if len(lst_varh) > 1:
                zref = np.array(tmp['ZREF'])
                h = np.array(tmp['Y'])
                z = h + zref
            else:
                # cote d'eau
                z = np.array(tmp['Z'])
            # interpolation en fonction des temps des Observation
            obs_time = np.array(
                [datum_to_float(vv, self.data[id_run][code]['h_obs_date'][0])
                 for vv in self.data[id_run][code]['h_obs_date']])
            self.data[id_run][code]['h_mod'] = self.interpol_date(obs_time,
                                                                  self.model[
                                                                      id_run][
                                                                      'times'],
                                                                  z)
            self.data[id_run][code]['h_time'] = obs_time

            self.data[id_run][code]['q_mod_ori'] = z
            self.data[id_run][code]['q_mod_ori_time'] = self.model[id_run][
                'times']
        else:
            self.data[id_run]['hcompt'] = False

        if len(lst_varq) > 0:
            if len(lst_varq) > 1:
                qmin = np.array(tmp['QMIN'])
                qmaj = np.array(tmp['QMAJ'])
                q = qmin + qmaj
            else:
                q = np.array(tmp['Q'])
            # interpolation en fonction des temps des Observation
            obs_time = np.array(
                [datum_to_float(vv, self.data[id_run][code]['q_obs_date'][0])
                 for vv in self.data[id_run][code]['q_obs_date']])

            self.data[id_run][code]['q_mod'] = self.interpol_date(obs_time,
                                                                  self.model[
                                                                      id_run][
                                                                      'times'],
                                                                  q)
            self.data[id_run][code]['q_mod_ori'] = q
            self.data[id_run][code]['q_mod_ori_time'] = self.model[id_run][
                'times']
            self.data[id_run][code]['q_time'] = obs_time
        else:
            self.data[id_run]['qcompt'] = False

    def get_obs(self, id_run, code):
        """
        get observation data
        :return:
        """
        lst_var = []  # TODO
        if self.data[id_run]['hcompt']:
            lst_var.append('H')
        if self.data[id_run]['qcompt']:
            lst_var.append('Q')
        dict_model = self.model[id_run]
        for gg in lst_var:
            condition = """code = '{0}'
                                  AND date>='{1}'
                                  AND date<='{2}'
                                  AND type='{3}'
                                  AND valeur > -999.9""".format(
                code, dict_model['init_time'],
                dict_model['final_time'], gg)
            tmp_dict = self.mdb.select("observations", condition, "date",
                                       list_var=['date', 'valeur'])
            if gg == 'H' and len(tmp_dict['valeur']) > 0:
                z = np.array(tmp_dict['valeur']) + \
                    np.ones(len(tmp_dict['valeur'])) * self.obs[code]['zero']
                self.data[id_run][code] = {
                    'h_obs': z,
                    'h_obs_date': tmp_dict['date']}

            if gg == 'Q' and len(tmp_dict['valeur']) > 0:
                self.data[id_run][code] = {
                    'q_obs': np.array(tmp_dict['valeur']),
                    'q_obs_date': tmp_dict['date']}
        if 'h_obs_date' not in self.data[id_run][code].keys():
            self.data[id_run]['hcompt'] = False
        if 'q_obs_date' not in self.data[id_run][code].keys():
            self.data[id_run]['qcompt'] = False

    def dict_pretr(self):
        """
        Create  :
        self.data[id_run]
        self.obs
        self.model
        And get information observation
        :return:
        """
        self.obs = {}
        self.model = {}
        self.data = {}
        for id_run in self.lst_runs:
            init_time = self.param[id_run]['ref_time']
            self.info_model(id_run, init_time)
            if not self.info_obs(id_run, init_time):
                self.model.pop(id_run)
                continue
            self.data[id_run] = {}
            self.res[id_run] = {'H': {}, 'Q': {}}

    def info_model(self, id_run, init_time):
        """
        Get information of model :
            'init_time'
            'final_time'
            'times'
            'var'
            'pknum'
        :param id_run: run index
        :param init_time: initial time
        :return:
        """
        info = self.mdb.select('runs_graph',
                               where="id_runs={} "
                                     "AND type_res='opt'"
                                     "AND var in "
                                     "('var','time','pknum')".format(
                                   id_run),
                               list_var=['var', 'val']
                               )
        if len(info['var']) > 0:
            data_rg = {var: info['val'][i] for i, var in
                       enumerate(info['var'])}

        final_time = init_time + timedelta(
            seconds=data_rg['time'][-1])

        info_var = self.mdb.select('results_var',
                                   where="type_res = 'opt' "
                                         "AND var IN('Y', 'ZREF', 'Z', "
                                         "'Q', 'QMIN', 'QMAJ')",
                                   list_var=['id', 'var'])
        var_dict = {var: info_var['id'][i] for i, var in
                    enumerate(info_var['var']) if
                    info_var['id'][i] in data_rg['var']}
        self.model[id_run] = {
            'init_time': init_time,
            'final_time': final_time,
            'times': data_rg['time'],
            'var': var_dict,
            'pknum': data_rg['pknum'],
        }

    def info_obs(self, id_run, init_time):
        """
         Get information of obs:
         self.obs :
            'name'
            'abscissa'
            'zero'

        self.model
            'lst_obs'
        :param id_run: run index
        :param init_time: initial time
        :return:
        """

        where = "active AND code IN (SELECT DISTINCT code FROM {0}.observations " \
                " WHERE date>'{1}' AND date<'{2}') " \
                "AND (name IN (SELECT DISTINCT name  FROM {0}.profiles) " \
                "OR abscissa IN (SELECT DISTINCT abscissa " \
                "FROM {0}.profiles))".format(self.mdb.SCHEMA,
                                             init_time,
                                             self.model[id_run]['final_time'])
        rows = self.mdb.select('outputs',
                               where=where,
                               order="abscissa",
                               list_var=['code', 'abscissa', 'name', 'zero'])

        if len(rows['code']) == 0:
            self.mgis.add_info("The id_run={} doesn't obsevation.\n "
                               "The score isn't computed.")
            return False
        for i, code in enumerate(rows['code']):
            if code not in self.obs.keys():
                self.obs[code] = {'name': rows['name'][i],
                                  'abscissa': rows['abscissa'][i],
                                  'zero': rows['zero'][i]}

        self.model[id_run]['lst_obs'] = rows['code']
        return True

    def get_alldata(self):
        # if not all len(lst_run) == 1
        self.dict_pretr()
        self.no_obs = []
        for id_run in self.model.keys():
            self.data[id_run]['hcompt'] = False
            self.data[id_run]['qcompt'] = False
            dict_model = self.model[id_run]
            if self.all:
                lst_obs = dict_model['lst_obs']
            else:
                # TODO filtre PKNUM for observation en réduisant
                # dict_model['lst_obs'] avec le pk en cours
                code = self.pknum2obs(id_run, self.cur_pknum)
                if code:
                    lst_obs = [code]
                else:
                    lst_obs = []

            if len(lst_obs) == 0:
                print('No find observation')
                self.no_obs.append(id_run)
                continue

            if 'Z' in dict_model['var'] or \
                    ('ZREF' in dict_model['var'] and 'Y' in dict_model['var'] \
                     ):
                self.data[id_run]['hcompt'] = True
            if 'Q' in dict_model['var'] or \
                    ('QMIN' in dict_model['var'] and \
                                 'QMAJ' in dict_model['var']):
                self.data[id_run]['qcompt'] = True

            for code in lst_obs:
                self.get_obs(id_run, code)
                self.get_model(id_run, code)

    def ch_date_ref(self, newDate):
        """ change color and change  parameter limite"""
        ctrl = self.sender()  # get widget which invok signal
        ctrl.setStyleSheet('color: Black')
        self.check_lim()

    def ch_date_limit(self, newDate):
        """ check limit"""
        date_comp = newDate.toPyDateTime()
        ctrl = self.sender()
        self.check_lim()

    def get_parameter(self):
        """ get parameter runs"""
        for col, id_run in enumerate(self.lst_runs):
            for ctrl_ in self.widget_d[id_run].keys():
                self.param[id_run][ctrl_] = \
                    ctrl_get_value(self.widget_d[id_run][ctrl_])

    def check_lim(self):
        rows_start = ['per_start_t', 'pt_start_t']
        rows_last = ['per_last_t', 'pt_last_t']
        rows = rows_start + rows_last
        for col, id_run in enumerate(self.lst_runs):
            for row in rows:
                self.widget_d[id_run][row].blockSignals(True)

        for col, id_run in enumerate(self.lst_runs):
            ref_time = self.widget_d[id_run][
                'ref_time'].dateTime().toPyDateTime()
            old_ref = self.param[id_run]['ref_time']

            final_date = ref_time + \
                         timedelta(seconds=self.param[id_run]['lst_times'][-1])
            final_date_crt = datetime2QDateTime(final_date)
            init_date_crt = datetime2QDateTime(ref_time)
            for row in rows:
                new_date = self.widget_d[id_run][row].dateTime().toPyDateTime()
                if ref_time != old_ref:
                    self.param[id_run]['ref_time'] = ref_time
                    if row in rows_start:
                        self.widget_d[id_run][row].setDateTime(init_date_crt)
                    elif row in rows_last:
                        self.widget_d[id_run][row].setDateTime(final_date_crt)
                else:
                    if new_date < ref_time:
                        self.widget_d[id_run][row].setDateTime(init_date_crt)
                    elif new_date > final_date:
                        self.widget_d[id_run][row].setDateTime(final_date_crt)

        for col, id_run in enumerate(self.lst_runs):
            for row in rows:
                self.widget_d[id_run][row].blockSignals(False)

    def clean_param(self):
        """clean paramater """
        self.clean_type_res()
        self.obs = {}
        self.model = {}
        self.data = {}

        self.ch_simple_err.setChecked(False)
        self.ch_ns_err.setChecked(False)
        self.ch_vol_err.setChecked(False)
        self.ch_quantil_err.setChecked(False)
        self.ch_persistence.setChecked(False)
        self.ch_pointe_err.setChecked(False)


def ctrl_get_value(ctrl):
    val = None
    if ctrl.metaObject().className() == 'QDateTimeEdit':
        # val = ctrl.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        val = ctrl.dateTime().toPyDateTime()
    elif ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
        val = ctrl.value()
    return val
