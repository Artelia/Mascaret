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

from .FunctionScores import *
from ..Function import datum_to_float
from ..ui.custom_control import datetime2QDateTime
from ..ui.custom_control import ScientificDoubleSpinBox


class ScoreParamWidget(QWidget):
    """
    Class for Parameter GUI and compute score
    """

    def __init__(self, windmain, all=True, ):
        """
        Class constructor
        :param windmain: main windows (parent)
        :param all: True if the all profile process else only one profile
        """
        QWidget.__init__(self)
        self.windmain = windmain
        self.mdb = self.windmain.mgis.mdb
        self.mgis = self.windmain.mgis
        self.exe = False
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath,
                         'ui/scores/ui_parametre.ui'), self)

        self.lst_runs = []
        self.lst_runs_old = []
        self.init_dates = None
        self.all = all
        self.dict_pk = {}
        self.txt_err_get = ''

        self.obs = {}
        self.model = {}
        self.data = {}
        self.no_obs = []
        self.cmpt_var = {}

        # {id : { h : [],time : [], q :[]}}
        self.res = {}
        self.type_res = {
            'simple': False,
            'nash_crit': False,
            'volume': False,
            'quantil': False,
            'tips_err': False,
            'persistence': False
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
        self.val_lim = ScientificDoubleSpinBox()
        self.lay_lim.addWidget(self.val_lim)

        self.init_gui()

        self.bt_calcul_scores.clicked.connect(self.bt_calcul_fct)
        self.bt_default.clicked.connect(self.bt_default_fct)

    def ch_lst_run(self, list_run):
        """ change list_run"""

        self.lst_runs_old = self.lst_runs
        self.lst_runs = list_run

    def ch_dict_pk(self, pks):
        self.dict_pk = pks

    def clean_control(self):
        """
        clean control
        :return:
        """

        self.ch_limit.disconnect()
        self.ch_simple_err.disconnect()
        self.ch_quantil_err.disconnect()

        try:
            self.ch_persistence.disconnect()
            self.ch_pointe_err.disconnect()

            for id_run in self.lst_runs_old:
                self.widget_d[id_run]['ref_time'].disconnect()
                for ctrl_ in ['per_start_t', 'pt_start_t']:
                    self.widget_d[id_run][ctrl_].disconnect()
                for ctrl_ in ['per_last_t', 'pt_last_t']:
                    self.widget_d[id_run][ctrl_].disconnect()
        except TypeError:
            pass

    def clean_widget_d(self):
        """
        clean dict widget
        :return:
        """
        del self.widget_d
        self.widget_d = {}

    def control_no_change(self):
        # default value
        self.dsp_dist_quantil.setValue(25)
        self.val_lim.setValue(1e-6)
        self.dsp_dist_quantil.setEnabled(False)
        self.ch_limit.setEnabled(False)
        self.ch_limit.setChecked(False)
        self.val_lim.setEnabled(False)
        self.ch_limit.stateChanged.connect(self.fct_chang_valim)
        self.ch_simple_err.stateChanged.connect(self.fct_chang_ch_lim)
        self.ch_quantil_err.stateChanged.connect(self.fct_chang_quantil)

    def init_gui(self):
        """
        initialize GUI
        :return:
        """

        if self.exe:
            self.clean_control()
            self.clean_widget_d()
        else:
            self.exe = True
        self.control_no_change()
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

                current_row_count = self.tw_param.rowCount()  # necessary even when there are no rows in the table
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
                self.fct_chang_persistence()
                self.fct_chang_point()
                self.ch_persistence.stateChanged.connect(
                    self.fct_chang_persistence)
                self.ch_pointe_err.stateChanged.connect(self.fct_chang_point)

    def fct_chang_persistence(self):
        """
        Change Enable/DisEnable for rows table
        :return:
        """
        lst_tmp = ['per_start_t', 'per_last_t', 'per_step_t']
        if self.ch_persistence.isChecked():
            for id_run in self.widget_d.keys():
                for ctrl_ in lst_tmp:
                    self.widget_d[id_run][ctrl_].setEnabled(True)

        else:
            for id_run in self.widget_d.keys():
                for ctrl_ in lst_tmp:
                    self.widget_d[id_run][ctrl_].setEnabled(False)

    def fct_chang_point(self):
        """
        Change Enable/DisEnable for rows table
        :return:
        """
        lst_tmp = ['pt_start_t', 'pt_last_t', 'pt_alpha_Q', 'pt_alpha_H']

        if self.ch_pointe_err.isChecked():
            for id_run in self.widget_d.keys():
                for ctrl_ in lst_tmp:
                    self.widget_d[id_run][ctrl_].setEnabled(True)

        else:
            for id_run in self.widget_d.keys():
                for ctrl_ in lst_tmp:
                    self.widget_d[id_run][ctrl_].setEnabled(False)

    def fct_chang_valim(self):
        """
        Change Enable/DisEnable for self.val_lim
        :return:
        """
        if self.ch_limit.isChecked():
            self.val_lim.setEnabled(True)
        else:
            self.val_lim.setEnabled(False)

    def fct_chang_ch_lim(self):
        """
        Change Enable/DisEnable for self.ch_limit
        :return:
        """
        if self.ch_simple_err.isChecked():
            self.ch_limit.setEnabled(True)
        else:
            self.ch_limit.setEnabled(False)
            self.ch_limit.setChecked(False)

    def fct_chang_quantil(self):
        """
        Change Enable/DisEnable for self.dsp_dist_quantil
        :return:
        """
        if self.ch_quantil_err.isChecked():
            self.dsp_dist_quantil.setEnabled(True)
        else:
            self.dsp_dist_quantil.setEnabled(False)

    def bt_default_fct(self):
        """
        Read the data base to update the default parameters
        :return:
        """
        self.init_gui()
        self.fct_chang_quantil()
        self.fct_chang_ch_lim()
        self.fct_chang_valim()
        self.fct_chang_point()
        self.fct_chang_persistence()

        pass

    def get_times(self, id_run, only_init=False):
        """
        Get reference date if exist
        and time list of model
        :param id_run: run index
        :param only_init: only initialize
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

        if len(info['val']) > 0:
            lst_times = info['val'][0]
        else:
            lst_times = list()
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
            'tips_err': False,
            'persistence': False
        }

    def bt_calcul_fct(self):
        """
        action when click on button
        :return:
        """
        ch_err = [self.ch_simple_err.isChecked(),
                  self.ch_ns_err.isChecked(),
                  self.ch_vol_err.isChecked(),
                  self.ch_quantil_err.isChecked(),
                  self.ch_persistence.isChecked(),
                  self.ch_pointe_err.isChecked()]
        if any(ch_err):

            self.get_parameter()
            self.clean_type_res()
            self.res = {}
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

    def cpt_score(self):
        """
        run the scores compute
        intepolation model linear with observation time
        :return:
        """
        self.txt_err_get = ''
        add_txt = ''
        other_txt = ''
        self.get_data()

        if len(self.model.keys()) > 0:

            dict_name = self.mdb.get_scen_name(self.model.keys())

            for id_run in self.no_obs:
                name_run = '{} - {}'.format(dict_name[id_run]['run'],
                                            dict_name[id_run]['scenario'])
                add_txt += '- No observation for the Run : {}\n'.format(
                    name_run)

            for id_run in self.model.keys():
                name_run = '{} - {}'.format(dict_name[id_run]['run'],
                                            dict_name[id_run]['scenario'])
                if self.ch_simple_err.isChecked():
                    if not self.cpt_simple_err(id_run):
                        add_txt += '- Simple scores (Run : {})\n'.format(
                            name_run)

                if self.ch_ns_err.isChecked():
                    if not self.cpt_ns_err(id_run):
                        add_txt += '- Nash - Sutcliffe criterion ' \
                                   '(Run : {})\n'.format(name_run)
                    else:
                        for pk, tmp1 in self.res['nash_crit'][id_run].items():
                            for code, tmp in tmp1.items():
                                if 'Q' in tmp.keys():
                                    if tmp['Q']['ns_err'] is None:
                                        other_txt += '- Nash - Sutcliffe criterion' \
                                                     ' (Run : {}, variable: Q, obs : {}):\n ' \
                                                     '    The Sum in denominator is null.' \
                                                     '\n'.format(name_run, code)
                                if 'H' in tmp.keys():
                                    if tmp['H']['ns_err'] is None:
                                        other_txt += '- Nash - Sutcliffe criterion' \
                                                     ' (Run : {}, variable: H, obs : {}):\n ' \
                                                     '    The Sum in denominator is null.' \
                                                     '\n'.format(name_run, code)

                if self.ch_vol_err.isChecked():
                    if not self.cpt_vol_err(id_run):
                        add_txt += '- Volume error (Run : {})\n'.format(
                            name_run)

                if self.ch_quantil_err.isChecked():
                    if not self.cpt_quantil_err(id_run):
                        add_txt += '- Quantil error (Run : {})\n'.format(
                            name_run)

                if self.ch_persistence.isChecked():
                    # check pas de temps régulier

                    init_mod = self.model[id_run]['init_time']
                    lst_mod = self.model[id_run]['final_time']
                    last = self.param[id_run]['per_last_t']
                    fst = self.param[id_run]['per_start_t']

                    if (init_mod < last <= lst_mod) and (
                                    lst_mod > fst >= init_mod):
                        test, lst_test = self.cpt_persistence(id_run)
                        if not test:
                            add_txt += '- Persistance error (Run : {})\n'.format(
                                name_run)
                        else:
                            if len(lst_test) > 0:
                                add_txt += '- Persistance error (Run : {}), Time step' \
                                           ' no constant : \n'.format(name_run)
                                for code in lst_test:
                                    '    - {} observation)\n'.format(code)

                    if 'persistence' in self.res.keys():
                        for pk, tmp1 in self.res['persistence'][id_run].items():
                            for code, tmp in tmp1.items():
                                if 'Q' in tmp.keys():
                                    if tmp['Q']['per_err'] is None:
                                        other_txt += '- Persistance error (Run : {}, variable: Q , obs : {}):\n ' \
                                                     '    The Sum in denominator is null. \n'.format(
                                            name_run, code)
                                if 'H' in tmp.keys():
                                    if tmp['H']['per_err'] is None:
                                        other_txt += '- Persistance error (Run : {}, variable: H, obs : {}): \n' \
                                                     '    The Sum in denominator is null. \n'.format(
                                            name_run, code)
                    else:
                        add_txt += '- Persistance error, No data in time rang' \
                                   ' (Run : {})\n'.format(name_run)

                if self.ch_pointe_err.isChecked():
                    init_mod = self.model[id_run]['init_time']
                    lst_mod = self.model[id_run]['final_time']
                    last = self.param[id_run]['per_last_t']
                    fst = self.param[id_run]['per_start_t']
                    if (init_mod < last <= lst_mod) and (
                                    lst_mod > fst >= init_mod):
                        if not self.cpt_pointe_err(id_run):
                            add_txt += '- Tips error (Run : {})\n'.format(
                                name_run)
                    else:
                        add_txt += '- Tips error, No data in time rang' \
                                   ' (Run : {})\n'.format(name_run)

        txt = ''
        if self.txt_err_get != '':
            txt += self.txt_err_get
            txt += '-----------\n'
        if add_txt != '':
            txt += 'No data, to compute : \n {}'.format(add_txt)
            txt += '-----------\n'
        if other_txt != '':
            txt += 'Other errors: \n {}'.format(other_txt)
            txt += '-----------\n'
        if txt != '':
            QMessageBox.warning(None, 'Warning',
                                txt)

    def creat_dict_simple(self, y_obs, y_pred, seuil=None):
        """

        :param y_obs: observation data
        :param y_pred: model data
        :param seuil : threshold value
        :return: dict contain the simple error
        """
        dict_res = {
            'mean_err': mean_err(y_obs, y_pred),
            'mean_abs_err': mean_abs_err(y_obs, y_pred),
            'mean_r_err': mean_r_err(y_obs, y_pred, seuil),
            'biais': biais(y_obs, y_pred, seuil),
            'mean_rabs_err': mean_rabs_err(y_obs, y_pred, seuil),
            'precision': precision(y_obs, y_pred, seuil),
            'std': std(y_obs, y_pred),
            'eqm': eqm(y_obs, y_pred)
        }
        return dict_res

    def add_res_dict(self, err, id_run, pk, code):
        """
        add element dict
        :param err : error type
        :param id_run : run index
        :param pk : abscissa
        :param code : observation code
        :return:
        """
        if err in self.res.keys():
            if id_run in self.res[err].keys():
                if pk in self.res[err][id_run].keys():
                    if code in self.res[err][id_run][pk].keys():
                        return
                    else:
                        self.res[err][id_run][pk][code] = {}
                else:
                    self.res[err][id_run][pk] = {code: {}}
            else:
                self.res[err][id_run] = {pk: {code: {}}}
        else:
            self.res[err] = {id_run: {pk: {code: {}}}}
        return

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
        seuil = None
        if self.ch_limit.isChecked():
            seuil = self.val_lim.value()
        for pk in self.data[id_run].keys():
            for code in self.data[id_run][pk].keys():
                if self.cmpt_var[id_run][pk][code]['H']:
                    self.add_res_dict('simple', id_run, pk, code)
                    self.res['simple'][id_run][pk][code][
                        'H'] = self.creat_dict_simple(
                        self.data[id_run][pk][code]['h_obs'],
                        self.data[id_run][pk][code]['h_mod'], seuil)
                    self.type_res['simple'] = True
                    out = True
                if self.cmpt_var[id_run][pk][code]['Q']:
                    self.add_res_dict('simple', id_run, pk, code)
                    self.res['simple'][id_run][pk][code][
                        'Q'] = self.creat_dict_simple(
                        self.data[id_run][pk][code]['q_obs'],
                        self.data[id_run][pk][code]['q_mod'], seuil)
                    self.type_res['simple'] = True
                    out = True

        return out

    def cpt_ns_err(self, id_run):
        """
        compute Nash-Sutcliffe criterion
        :param id_run:  run index
        :return: out : True if the compute is Ok
        """
        out = False
        for pk in self.data[id_run].keys():

            for code in self.data[id_run][pk].keys():
                if self.cmpt_var[id_run][pk][code]['H']:
                    self.add_res_dict('nash_crit', id_run, pk, code)
                    self.res['nash_crit'][id_run][pk][code]['H'] = \
                        {
                            'ns_err': nash_crit(
                                self.data[id_run][pk][code]['h_obs'],
                                self.data[id_run][pk][code]['h_mod'])
                        }
                    self.type_res['nash_crit'] = True
                    out = True
                if self.cmpt_var[id_run][pk][code]['Q']:
                    self.add_res_dict('nash_crit', id_run, pk, code)
                    self.res['nash_crit'][id_run][pk][code]['Q'] = {
                        'ns_err': nash_crit(
                            self.data[id_run][pk][code]['q_obs'],
                            self.data[id_run][pk][code]['q_mod'])
                    }
                    self.type_res['nash_crit'] = True
                    out = True
        return out

    def cpt_vol_err(self, id_run):
        """
        compute Error on volumes
        :param id_run:  run index
        :return:out : True if the compute is Ok
        """
        out = False

        for pk in self.data[id_run].keys():
            if self.cmpt_var[id_run][pk]['Q']:
                for code in self.data[id_run][pk].keys():
                    if self.cmpt_var[id_run][pk][code]['Q']:
                        q_obs = self.data[id_run][pk][code]['q_obs']
                        q_pred = self.data[id_run][pk][code]['q_mod']
                        # the same because model is sample on the observations
                        lst_time_pred = self.data[id_run][pk][code][
                            'q_obs_time']
                        lst_time_obs = self.data[id_run][pk][code]['q_obs_time']
                        self.add_res_dict('volume', id_run, pk, code)
                        self.res['volume'][id_run][pk][code]['Q'] = {
                            'vol_err': vol_err(q_obs, q_pred,
                                                             lst_time_pred,
                                                             lst_time_obs)}
                        self.type_res['volume'] = True
                        out = True

        return out

    def cpt_quantil_err(self, id_run):
        """
        compute  quantiles:
            error quantiles : dist_err
            absolute error quantiles :  dist_abs_err
        :param id_run:  run index
        :return: out : True if the compute is Ok
        """
        out = False
        dist_step = self.dsp_dist_quantil.value()

        for pk in self.data[id_run].keys():
            for code in self.data[id_run][pk].keys():
                if self.cmpt_var[id_run][pk][code]['H']:
                    y_obs = self.data[id_run][pk][code]['h_obs']
                    y_pred = self.data[id_run][pk][code]['h_mod']
                    self.add_res_dict('quantil', id_run, pk, code)
                    self.res['quantil'][id_run][pk][code]['H'] = \
                        {'dist_err': dist_err(y_obs, y_pred,
                                                            dist_step),
                         'dist_abs_err': dist_abs_err(y_obs,
                                                                    y_pred,
                                                                    dist_step)}
                    self.type_res['quantil'] = True
                    out = True
                if self.cmpt_var[id_run][pk][code]['Q']:
                    y_obs = self.data[id_run][pk][code]['q_obs']
                    y_pred = self.data[id_run][pk][code]['q_mod']
                    self.add_res_dict('quantil', id_run, pk, code)
                    self.res['quantil'][id_run][pk][code]['Q'] = \
                        {'dist_err': dist_err(y_obs, y_pred,
                                                            dist_step),
                         'dist_abs_err': dist_abs_err(y_obs,
                                                                    y_pred,
                                                                    dist_step)}
                    self.type_res['quantil'] = True
                    out = True

        return out

    def check_cst_deltat(self, obs_times, pred_times):
        """
        check if detla time is constant
        :param obs_times: observation time
        :param pred_times: model time
        :return:
        """
        dt_obs = generate_deltat(obs_times)
        dt_pred = generate_deltat(pred_times)
        cobs = np.all(dt_obs == dt_obs[0])
        cpred = np.all(dt_pred == dt_pred[0])
        if cobs and cpred:
            return True
        else:
            return False

    def cpt_persistence(self, id_run):
        """
        compute persistence
        Warning the model is interpoled on observation time
        :param id_run : run index
        :return: out : True if persistance is calculated
        """

        out = False
        lst_no_cst = []
        frst_date = self.param[id_run]['per_start_t']
        last_date = self.param[id_run]['per_last_t']
        deltat = self.param[id_run]['per_step_t']

        ref_time = self.param[id_run]['ref_time']

        frst_time = datum_to_float(frst_date, ref_time)
        last_time = datum_to_float(last_date, ref_time)

        for pk in self.data[id_run].keys():
            for code in self.data[id_run][pk].keys():

                if self.cmpt_var[id_run][pk][code]['H']:

                    new_obs, new_obs_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code]['h_obs'],
                                         self.data[id_run][pk][code][
                                             'h_obs_time'])
                    new_pred, new_pred_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code]['h_mod'],
                                         self.data[id_run][pk][code][
                                             'h_obs_time'])
                    #
                    if len(new_obs) == 0:
                        # txterr += "Persistance error : No data in time range : "\
                        #       "{}".format(code)
                        continue

                    if not self.check_cst_deltat(new_obs_times, new_pred_times):
                        lst_no_cst.append(code)
                        continue
                    self.add_res_dict('persistence', id_run, pk, code)
                    self.res['persistence'][id_run][pk][code]['H'] = \
                        {
                            'per_err':
                                persistence(new_obs, new_pred,
                                                          new_obs_times,
                                                          deltat),
                        }
                    self.type_res['persistence'] = True
                    out = True

                if self.cmpt_var[id_run][pk][code]['Q']:
                    new_obs, new_obs_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code]['q_obs'],
                                         self.data[id_run][pk][code][
                                             'q_obs_time'])
                    new_pred, new_pred_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code]['q_mod'],
                                         self.data[id_run][pk][code][
                                             'q_obs_time'])
                    #
                    if len(new_obs) == 0:
                        continue
                    if not self.check_cst_deltat(new_obs_times, new_pred_times):
                        lst_no_cst.append(code)
                        continue
                    self.add_res_dict('persistence', id_run, pk, code)
                    self.res['persistence'][id_run][pk][code]['Q'] = \
                        {
                            'per_err':
                                persistence(new_obs, new_pred,
                                                          new_obs_times,
                                                          deltat),
                        }
                    self.type_res['persistence'] = True
                    out = True

        return out, lst_no_cst

    def filter_time(self, first, last, data, times):
        """
        filter time
        :param first: first date
        :param last: last date
        :param data : data to filter
        :param times: times to filter
        :return: return new data, new times
        """
        new_data = []
        new_times = []
        for i, tmp in enumerate(times):
            if first <= tmp <= last:
                new_data.append(data[i])
                new_times.append(tmp)
        return np.array(new_data), np.array(new_times)

    def cpt_pointe_err(self, id_run):
        """
        compute Errors on the tips (L’erreur sur les pointes sur H et Q)
            Errors on the tips
            Time shift on the tip
        :param id_run : run index
        :return:
        """
        out = False
        frst_date = self.param[id_run]['pt_start_t']
        last_date = self.param[id_run]['pt_last_t']
        alphaq = self.param[id_run]['pt_alpha_Q']
        alphah = self.param[id_run]['pt_alpha_H']
        ref_time = self.param[id_run]['ref_time']

        frst_time = datum_to_float(frst_date, ref_time)
        last_time = datum_to_float(last_date, ref_time)

        for pk in self.data[id_run].keys():
            for code in self.data[id_run][pk].keys():

                if self.cmpt_var[id_run][pk][code]['H']:

                    new_obs, new_obs_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code]['h_obs'],
                                         self.data[id_run][pk][code][
                                             'h_obs_time'])
                    new_pred, new_pred_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code][
                                             'h_mod_ori'],
                                         self.data[id_run][pk][code][
                                             'h_mod_ori_time'])
                    #
                    if len(new_obs) == 0:
                        continue
                    self.add_res_dict('tips_err', id_run, pk, code)
                    self.res['tips_err'][id_run][pk][code]['H'] = \
                        {
                            'pts_err':
                                err_point(new_obs, new_pred),
                            'pts_time_err':
                                err_temps_point(new_obs, new_pred,
                                                              new_obs_times,
                                                              new_pred_times,
                                                              alphah)
                        }
                    self.type_res['tips_err'] = True
                    out = True

                if self.cmpt_var[id_run][pk][code]['Q']:
                    new_obs, new_obs_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code]['q_obs'],
                                         self.data[id_run][pk][code][
                                             'q_obs_time'])
                    new_pred, new_pred_times = \
                        self.filter_time(frst_time, last_time,
                                         self.data[id_run][pk][code][
                                             'q_mod_ori'],
                                         self.data[id_run][pk][code][
                                             'q_mod_ori_time'])
                    #
                    if len(new_obs) == 0:
                        continue
                    self.add_res_dict('tips_err', id_run, pk, code)
                    self.res['tips_err'][id_run][pk][code]['Q'] = {
                        'pts_err':
                            err_point(new_obs, new_pred),
                        'pts_time_err':
                            err_temps_point(new_obs, new_pred,
                                                          new_obs_times,
                                                          new_pred_times,
                                                          alphaq)
                    }
                    self.type_res['tips_err'] = True
                    out = True
        return out

    def interpol_date(self, obs_time, time_model, var_model):
        """
        Interpolation values
        :param obs_time: array    observation time
        :param time_model: list(float)   model time
        :param var_model: array  model variable
        :return:
        """
        fct = interpolate.interp1d(time_model, var_model, kind='linear')
        model_var = fct(obs_time)
        return model_var

    def get_pk(self, code):
        nb = len(self.obs[code]['abscissa'])
        lst_pk = []
        for i in range(nb):
            if self.obs[code]['abscissa'][i]:
                where = 'abscissa = {0}'.format(self.obs[code]['abscissa'][i])
            elif self.obs[code]['name'][i]:
                where = "name='{0}'".format(self.obs[code]['name'][i])
            else:
                txt = 'No find profile {0}={1} '.format(
                    self.obs[code]['name'][i],
                    self.obs[code]['abscissa'][i])
                self.txt_err_get += txt
                # return None
            info = self.mdb.select('profiles',
                                   where=where,
                                   list_var=['abscissa'])

            lst_pk.append(info['abscissa'][0])

        if lst_pk:
            return lst_pk
        else:
            return None

    def pk2obs(self, id_run, pk):
        """
        get observation from pk
        :param id_run: run index
        :param pk : abscissa
        :return:
        """
        where = 'abscissa = {0}'.format(pk)
        info = self.mdb.select('profiles',
                               where=where,
                               list_var=['gid', 'name', 'abscissa'])

        name = None
        abs = None
        if len(info['abscissa']) > 0:
            name = info['name'][0]
            abs = info['abscissa'][0]
        else:
            abs = pk

        lst_code = []
        for code, dict in self.obs.items():
            if name:
                if name in dict['name']:
                    lst_code.append(code)
            elif abs:
                if abs in dict['abscissa']:
                    lst_code.append(code)

        return lst_code

    def get_model(self, id_run, pk, code):
        """
        get model data
        :param id_run : run index
        :param pk : abscissa
        :param code : observation code
        :return:
        """

        dict_model = self.model[id_run]
        lst_varh = []
        lst_varq = []

        if 'Z' in dict_model['var']:
            lst_varh.append('Z')
        elif 'ZREF' in dict_model['var'] and 'Y' in dict_model['var']:
            lst_varh.append('ZREF')
            lst_varh.append('Y')

        if 'Q' in dict_model['var']:
            lst_varq.append('Q')
        elif 'QMIN' in dict_model['var'] and 'QMAJ' in dict_model['var']:
            lst_varq.append('QMIN')
            lst_varq.append('QMAJ')

        lst_var = lst_varq + lst_varh
        tmp = {}
        for var in lst_var:
            val = self.mdb.select('results',
                                  where="id_runs={0} AND pknum= {1} " \
                                        "and var = {2}".format(id_run,
                                                               pk,
                                                               dict_model[
                                                                   'var'][var]),
                                  order='time',
                                  list_var=['val'],
                                  verbose=False)
            tmp[var] = val['val']

        if len(lst_varh) > 0:
            if len(lst_varh) > 1:
                zref = np.array(tmp['ZREF'])
                h = np.array(tmp['Y'])
                z = h + zref
            else:
                # cote d'eau
                z = np.array(tmp['Z'])

            self.data[id_run][pk][code]['h_mod_ori'] = z
            self.data[id_run][pk][code]['h_mod_ori_time'] = self.model[id_run][
                'times']

        if len(lst_varq) > 0:
            if len(lst_varq) > 1:
                qmin = np.array(tmp['QMIN'])
                qmaj = np.array(tmp['QMAJ'])
                q = qmin + qmaj
            else:
                q = np.array(tmp['Q'])
            self.data[id_run][pk][code]['q_mod_ori'] = q
            self.data[id_run][pk][code]['q_mod_ori_time'] = self.model[id_run][
                'times']

    def resample_model_h(self, id_run, pk, code):
        """
        Resample model time for H
        :param id_run : run index
        :param pk : abscissa
        :param code : observation code
        :return:
        """
        # interpolation en fonction des temps des Observation
        # ******* Z  **********
        z = self.data[id_run][pk][code]['h_mod_ori']
        obs_time = self.data[id_run][pk][code]['h_obs_time']
        self.data[id_run][pk][code]['h_mod'] = self.interpol_date(obs_time,
                                                                  self.model[
                                                                      id_run][
                                                                      'times'],
                                                                  z)

    def resample_model_q(self, id_run, pk, code):
        """
        Resample model time for Q
        :param id_run : run index
        :param pk : abscissa
        :param code : observation code
        :return:
        """
        # ******* Q  **********

        q = self.data[id_run][pk][code]['q_mod_ori']
        obs_time = self.data[id_run][pk][code]['q_obs_time']
        self.data[id_run][pk][code]['q_mod'] = self.interpol_date(obs_time,
                                                                  self.model[
                                                                      id_run][
                                                                      'times'],
                                                                  q)

    def get_obs(self, id_run, pk, code):
        """
        get observation data
        :param id_run : run index
        :param pk : abscissa
        :param code : observation code
        :return:
        """
        lst_var = ['H', 'Q']
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
                                       list_var=['date', 'valeur'],
                                       verbose=False)

            if self.obs[code]['zero'] is None:
                self.obs[code]['zero'] = 0
            if gg == 'H' and len(tmp_dict['valeur']) > 0:
                z = np.array(tmp_dict['valeur']) + \
                    np.ones(len(tmp_dict['valeur'])) * self.obs[code]['zero']
                obs_time = np.array(
                    [datum_to_float(vv,
                                    tmp_dict['date'][0])
                     for vv in tmp_dict['date']])
                dic_tmp = {
                    'h_obs': z,
                    'h_obs_date': tmp_dict['date'],
                    'h_obs_time': obs_time}
                if code in self.data[id_run][pk].keys():
                    self.data[id_run][pk][code].update(dic_tmp)
                else:
                    self.data[id_run][pk][code] = dic_tmp
            if gg == 'Q' and len(tmp_dict['valeur']) > 0:
                obs_time = np.array(
                    [datum_to_float(vv,
                                    tmp_dict['date'][0])
                     for vv in tmp_dict['date']])

                dic_tmp = {
                    'q_obs': np.array(tmp_dict['valeur']),
                    'q_obs_date': tmp_dict['date'],
                    'q_obs_time': obs_time}
                if code in self.data[id_run][pk].keys():
                    self.data[id_run][pk][code].update(dic_tmp)
                else:
                    self.data[id_run][pk][code] = dic_tmp

    def dict_pretr(self):
        """
        Create  :
        self.data[id_run]
        self.obs
        self.model
        And get information observation
        :return:
        """

        self.model = {}
        self.data = {}
        for id_run in self.lst_runs:
            init_time = self.param[id_run]['ref_time']
            self.info_model(id_run, init_time)
            if not self.info_obs(id_run, init_time):
                self.model.pop(id_run)
                continue
            self.data[id_run] = {}

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
        else:
            dict_name = self.mdb.get_scen_name([id_run])
            txt = "No data model for {} - {}\n " \
                  "".format(dict_name[id_run]['run'],
                            dict_name[id_run]['scenario'])
            self.txt_err_get += txt
            return

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
        self.obs = {}

        where = "active AND code IN (SELECT DISTINCT code FROM {0}.observations " \
                " WHERE date>='{1}' AND date<='{2}') " \
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
            dict_name = self.mdb.get_scen_name([id_run])
            txt = "No find observation for {} - {}\n " \
                  "".format(dict_name[id_run]['run'],
                            dict_name[id_run]['scenario'])
            # self.mgis.add_info(txt)
            self.txt_err_get += txt
            return False
        for i, code in enumerate(rows['code']):
            if code not in self.obs.keys():
                self.obs[code] = {'name': [],
                                  'abscissa': [],
                                  'zero': []}
        self.model[id_run]['lst_obs'] = list(self.obs.keys())
        for i, code in enumerate(rows['code']):
            self.obs[code]['name'].append(rows['name'][i])
            self.obs[code]['abscissa'].append(rows['abscissa'][i])
            self.obs[code]['zero'].append(rows['zero'][i])
            pknums = self.get_pk(code)
            self.obs[code]['lst_pk'] = pknums

        return True

    def get_data(self):
        """
        get all data (model and observation)
        :return:
        """
        # if not all len(lst_run) == 1

        if not (len(self.lst_runs) > 0):
            self.txt_err_get += 'No model selected \n'

        self.dict_pretr()

        self.no_obs = []
        self.cmpt_var = {}
        txt_nocpt = ''
        txt_nodata = ''

        if len(self.model.keys()) > 0:
            dict_name = self.mdb.get_scen_name(list(self.model.keys()))
        else:
            dict_name = {}
        for id_run in self.model.keys():
            dict_model = self.model[id_run]
            if self.all:
                lst_obs = dict_model['lst_obs']
                for code in lst_obs:
                    for pk in self.obs[code]['lst_pk']:
                        if pk in self.data[id_run].keys():
                            self.data[id_run][pk][code] = {}
                        else:
                            self.data[id_run][pk] = {code: {}}

            else:
                lst_obs = []
                if id_run in self.dict_pk.keys():
                    for pk in self.dict_pk[id_run]:
                        lobs = self.pk2obs(id_run, pk)
                        lst_obs.extend(lobs)
                        for code in lobs:
                            if pk in self.data[id_run].keys():
                                self.data[id_run][pk][code] = {}
                            else:
                                self.data[id_run][pk] = {code: {}}
            if len(lst_obs) == 0:
                txt_nodata += "- {} - {}\n " \
                              "".format(dict_name[id_run]['run'],
                                        dict_name[id_run]['scenario'])

                self.no_obs.append(id_run)
                continue

            for pk in self.data[id_run].keys():
                for code in self.data[id_run][pk].keys():
                    # self.data[id_run][pk][code] = {}

                    self.get_obs(id_run, pk, code)
                    self.get_model(id_run, pk, code)

                self.check_comput_hq(id_run, pk)

            if not self.cmpt_var[id_run][pk]['H'] and \
                    not self.cmpt_var[id_run][pk]['Q']:
                txt = "- {} - {}\n " \
                      "".format(dict_name[id_run]['run'],
                                dict_name[id_run]['scenario'])
                self.txt_err_get += txt

        if txt_nodata != '':
            self.txt_err_get += 'No data to :\n'
            self.txt_err_get += txt_nodata
            self.txt_err_get += '-----------\n'
        if txt_nocpt != '':
            self.txt_err_get += 'No compute scores to :\n'
            self.txt_err_get += txt_nocpt
            self.txt_err_get += '-----------\n'

    def check_comput_hq(self, id_run, pk):
        """
        Check if Q et z in model can be use
        :param id_run: run index
        :param lst_obs: observation index list
        :param pk : abscissa
        :return:
        """
        if not (id_run in self.cmpt_var.keys()):
            self.cmpt_var[id_run] = {}
        if not (pk in self.cmpt_var[id_run].keys()):
            self.cmpt_var[id_run][pk] = {}
        for code in self.data[id_run][pk].keys():
            if not (code in self.cmpt_var[id_run][pk].keys()):
                self.cmpt_var[id_run][pk][code] = {}

            if 'h_obs' in self.data[id_run][pk][code].keys() and \
                            'h_mod_ori' in self.data[id_run][pk][code].keys():

                self.cmpt_var[id_run][pk][code]['H'] = True
                self.resample_model_h(id_run, pk, code)
            else:
                if 'H' in self.cmpt_var[id_run][pk][code].keys():
                    if not self.cmpt_var[id_run][pk][code]['H']:
                        self.cmpt_var[id_run][pk][code]['H'] = False
                else:
                    self.cmpt_var[id_run][pk][code]['H'] = False

            if 'q_obs' in self.data[id_run][pk][code].keys() and \
                            'q_mod_ori' in self.data[id_run][pk][code].keys():
                self.cmpt_var[id_run][pk][code]['Q'] = True
                self.resample_model_q(id_run, pk, code)
            else:
                if 'Q' in self.cmpt_var[id_run][pk][code].keys():
                    if not self.cmpt_var[id_run][pk][code]['Q']:
                        self.cmpt_var[id_run][pk][code]['Q'] = False
                else:
                    self.cmpt_var[id_run][pk][code]['Q'] = False

        self.cmpt_var[id_run][pk]['H'] = False
        self.cmpt_var[id_run][pk]['Q'] = False
        for k in self.cmpt_var[id_run][pk].values():
            if isinstance(k, dict):
                if k['H']:
                    self.cmpt_var[id_run][pk]['H'] = True
                if k['Q']:
                    self.cmpt_var[id_run][pk]['Q'] = True

    def ch_date_ref(self):
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
        """
        Check if date value is right with model time
        :return:
        """
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
        self.ch_limit.setChecked(False)


def ctrl_get_value(ctrl):
    val = None
    if ctrl.metaObject().className() == 'QDateTimeEdit':
        # val = ctrl.dateTime().toString('yyyy-MM-dd HH:mm:ss')
        val = ctrl.dateTime().toPyDateTime()
    elif ctrl.metaObject().className() in ('QSpinBox', 'QDoubleSpinBox'):
        val = ctrl.value()
    return val
