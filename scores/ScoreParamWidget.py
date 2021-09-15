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
    def __init__(self, windmain, all=True):
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
        self.date_init = None
        self.lst_times = None
        self.all = all
        if not self.all :
            if self.cur_pknum == None:
                print('no find pknum')
        self.cur_pknum =  None
        self.data = {}
        # {id : { h : [],time : [], q :[]}}
        self.res = {}
        self.type_res = {
            'simple' : False,
            'nash_crit':  False,
            'quantil' : False,
        }

        self.widget_d = {}
        self.init_gui()

        self.bt_calcul_scores.clicked.connect(self.bt_calcul_fct)


    def init_gui(self):
        """
        initialize GUI
        :return:
        """
        # default value
        self.dsp_dist_quantil.setValue(25)
        print(self.lst_runs)
        self.lk_wgt_row = {'ref_time' : 0,
                                 'per_start_t': 1,
                                 'per_last_t': 2,
                                 'pt_start_t': 3,
                                 'pt_last_t': 4,
                                 'pt_alpha_Q': 5,
                                 'pt_alpha_H': 6, }

        for id_run in self.lst_runs:
            self.widget_d[id_run] = { 'ref_time' : QDateTimeEdit(self),
                                 'per_start_t': QDateTimeEdit(self),
                                 'per_last_t': QDateTimeEdit(self),
                                 'pt_start_t': QDateTimeEdit(self),
                                 'pt_last_t': QDateTimeEdit(self),
                                 'pt_alpha_Q': QDoubleSpinBox(self),
                                 'pt_alpha_H': QDoubleSpinBox(self),  }

            # add style widget
            for ctrl_ in ['per_start_t', 'pt_start_t', 'per_last_t',
                          'pt_last_t', 'ref_time']:
                self.widget_d[id_run][ctrl_].setCalendarPopup(True)
                self.widget_d[id_run][ctrl_].setDisplayFormat(
                    'yyyy. MM.dd hh:mm:ss')

                self.widget_d[id_run][ctrl_].setDateTimeRange(
                    QDateTime(1800, 1, 1, 00, 00, 00),
                    QDateTime(9999, 1, 1, 00, 00, 00))

            for ctrl_ in ['pt_alpha_Q', 'pt_alpha_H']:
                self.widget_d[id_run][ctrl_].setMinimum(0)
                self.widget_d[id_run][ctrl_].setSingleStep(0.1)
                self.widget_d[id_run][ctrl_].setDecimals(2)
                self.widget_d[id_run][ctrl_].setMaximum(999)

            # add initialisation widget
            self.date_init, self.lst_times = self.get_times(id_run)
            final_date = self.date_init + timedelta(seconds=self.lst_times[-1])
            tmps = datetime.today()
            self.today = QDateTime(tmps.year, tmps.month, tmps.day, 0, 0, 0)
            if isinstance(self.date_init, datetime):
                init_date_crt = datetime2QDateTime(self.date_init)
            else:
                init_date_crt = self.today
                self.widget_d[id_run]['ref_time'].setStyleSheet('color: red')
            self.widget_d[id_run]['ref_time'].setDateTime(init_date_crt)

            if isinstance(final_date, datetime):
                last_date_crt = datetime2QDateTime(final_date)
            else:
                last_date_crt = QDateTime(tmps.year, tmps.month, tmps.day, 1, 0,
                                          0)
            for ctrl_ in ['per_start_t','pt_start_t']:
                self.widget_d[id_run][ctrl_].setDateTime(init_date_crt)
            for ctrl_ in ['per_last_t', 'pt_last_t']:
                self.widget_d[id_run][ctrl_].setDateTime(last_date_crt)

            for ctrl_ in ['pt_alpha_Q', 'pt_alpha_H']:
                self.widget_d[id_run][ctrl_].setValue(1)
            # control
            self.widget_d[id_run]['ref_time'].dateChanged.connect(self.ch_date)

            for ctrl_ in ['per_start_t', 'per_last_t']:
                self.widget_d[id_run][ctrl_].dateChanged.connect(
                    self.ch_date_lim_per)
            for ctrl_ in ['pt_start_t', 'pt_last_t']:
                self.widget_d[id_run][ctrl_].dateChanged.connect(
                    self.ch_date_lim_pt)


            # fill table






    def get_times(self, id_run):
        """
        Get reference date if exist
        and time list of model
        :param id_run: run index
        :return:
        """
        dico = self.mdb.select("runs",
                               where="id_run={0}".format(id_run))
        init_time = dico["init_date"][0]
        info = self.mdb.select('runs_graph',
                               where="id_runs={} "
                                     "AND type_res='opt'"
                                     "AND var='time'".format(id_run),
                               list_var=['val'])
        lst_times = info['val'][0]
        return init_time , lst_times

    def clean_type_res(self):
        """
        clean type_res
        :return:
        """
        self.type_res = {
            'simple' : False,
            'nash_crit':  False,
            'quantil' : False,
        }

    def bt_calcul_fct(self):
        """
        action when click on button
        :return:
        """

        self.clean_type_res()
        self.cpt_score()

        tabscores = self.windmain.tabscores
        id_dist = tabscores.indexOf(self.windmain.wgt_dist)
        id_res = tabscores.indexOf(self.windmain.wgt_res)
        cond_enable = {'quantil': False, 'res': False}
        for key, cond in self.type_res.items():
            if key in ['quantil'] and cond:
                cond_enable['quantil'] =  True
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

        return h_obs,h_pred, q_obs,q_pred


    def cpt_score(self):
        """
        run the scores compute
        :return:
        """
        self.get_alldata()



        #TODO demander pour les deltat si variable?
        # TODO demandé si je fait un croisment ou interpolation linear du modèle ?


        for id_run in self.lst_runs:

            h_obs, h_pred, q_obs, q_pred = self.create_obs_pre(id_run, pknum = None)

            if self.ch_simple_err.isChecked():
                if self.data[id_run]['hcompt']:
                    self.res[id_run]['H']['simple'] = \
                        self.cpt_simple_err(h_obs, h_pred)
                    self.type_res['simple'] =  True
                if self.data[id_run]['qcompt']:
                    self.res[id_run]['Q']['simple'] =\
                        self.cpt_simple_err( q_obs, q_pred)
                    self.type_res['simple'] = True

            if self.ch_ns_err.isChecked():
                if self.data[id_run]['hcompt']:
                    self.res[id_run]['H']['nash_crit'] = \
                        self.cpt_ns_err( h_obs, h_pred)
                    self.type_res['nash_crit'] = True
                if self.data[id_run]['qcompt']:
                    self.res[id_run]['Q']['nash_crit'] =\
                        self.cpt_ns_err( q_obs, q_pred)
                    self.type_res['nash_crit'] = True

            if self.ch_vol_err.isChecked():
                pass

            if self.ch_quantil_err.isChecked():
                if self.data[id_run]['hcompt']:
                    self.res[id_run]['H']['quantil'] = \
                        self.cpt_quantil_err( h_obs,
                                               h_pred,
                                               self.dsp_dist_quantil.value() )
                    self.type_res['quantil'] = True
                if self.data[id_run]['qcompt']:
                    self.res[id_run]['Q']['quantil'] = \
                        self.cpt_quantil_err( q_obs,
                                               q_pred,
                                               self.dsp_dist_quantil.value())
                    self.type_res['quantil'] = True
            if self.ch_persistence.isChecked():
                # self.start_time_persistence
                # self.last_time_persistence
                pass
            if self.ch_pointe_err.isChecked():
                # self.start_time_point
                # self.last_time_point
                # self.alpha_Hcc
                # self.alpha_Q
                pass
        print(self.res[id_run]['H'])

    def cpt_simple_err(self, y_obs, y_pred):
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
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return:
        """

        dict_res ={
        'mean_err':self.cl_score.mean_err(y_obs, y_pred),
        'mean_abs_err': self.cl_score.mean_abs_err(y_obs, y_pred),
        'mean_r_err':self.cl_score.mean_r_err(y_obs, y_pred),
        'biais' : self.cl_score.biais(y_obs, y_pred),
        'mean_rabs_err': self.cl_score.mean_rabs_err(y_obs, y_pred),
        'precision': self.cl_score.precision(y_obs, y_pred),
        'std': self.cl_score.std(y_obs, y_pred),
        'eqm':  self.cl_score.eqm(y_obs, y_pred)
        }
        return dict_res


    def cpt_ns_err(self,y_obs, y_pred):
        """
        compute Nash-Sutcliffe criterion
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return:
        """
        # self.cl_score.nash_crit(y_obs, y_pred)
        dict_res = {
            'ns_err': self.cl_score.nash_crit(y_obs, y_pred)
        }
        return dict_res

    def cpt_vol_err(self):
        """
        compute Error on volumes
         :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return:
        """
        # self.cl_score.vol_err(q_obs, q_pred, deltat)
        pass

    def cpt_quantil_err(self, y_obs, y_pred, dist_step):
        """
        compute  quantiles:
            error quantiles : dist_err
            absolute error quantiles :  dist_abs_err
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :param dist_step: distribution step
        :return:
        """
        dict_res = {'dist_err' :self.cl_score.dist_err(y_obs, y_pred,  dist_step),
                    'dist_abs_err': self.cl_score.dist_err(y_obs, y_pred, dist_step)}
        return dict_res

    def cpt_persistence(self):
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
                #cote d'eau
                z = np.array(tmp['Z'])
            # interpolation en fonction des temps des Observation
            obs_time = np.array(
                [datum_to_float(vv, self.data[id_run][code]['h_obs_date'][0])
                 for vv in self.data[id_run][code]['h_obs_date']])
            print(self.interpol_date(obs_time,self.model[id_run]['times'],z))
            self.data[id_run][code]['h_mod'] = self.interpol_date(obs_time,
                                                                  self.model[
                                                                      id_run][
                                                                      'times'],
                                                                  z)
            self.data[id_run][code]['h_time'] = obs_time
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
                    np.ones(len(tmp_dict['valeur']))*self.obs[code]['zero']
                self.data[id_run][code] = {
                    'h_obs': z,
                    'h_obs_date': tmp_dict['date']}

            if gg == 'Q' and len(tmp_dict['valeur']) > 0:
                self.data[id_run][code] = {
                    'q_obs': np.array(tmp_dict['valeur']),
                    'q_obs_date': tmp_dict['date']}
        if  'h_obs_date' not in self.data[id_run][code].keys():
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
        for id_run, init_time in zip(self.lst_runs, self.init_dates):
            self.info_model( id_run, init_time)
            if not self.info_obs(id_run, init_time):
                self.model.pop(id_run)
                continue
            self.data[id_run] = {}
            self.res[id_run] = {'H': {}, 'Q': {}}

    def info_model(self, id_run, init_time ):
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
                    enumerate(info_var['var']) if info_var['id'][i] in data_rg['var']}
        self.model[id_run] = {
            'init_time': init_time,
            'final_time': final_time,
            'times': data_rg['time'],
            'var': var_dict,
            'pknum': data_rg['pknum'],
        }

    def info_obs(self,id_run, init_time):
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
            return  False
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

        for id_run in self.lst_runs:
            dict_model = self.model[id_run]
            self.data[id_run]['hcompt'] = False
            self.data[id_run]['qcompt'] = False
            if len(dict_model['lst_obs']) == 0:
                print('No find observation')
                return
            print('key',self.model[id_run].keys())
            if  'Z' in dict_model['var'] or \
                    ('ZREF' in dict_model['var'] and 'Y' in dict_model['var']\
                                 ):
                self.data[id_run]['hcompt'] = True
            if 'Q' in dict_model['var'] or \
                    ('QMIN' in dict_model['var'] and \
                                 'QMAJ' in dict_model['var']):
                self.data[id_run]['qcompt'] = True
            if not self.all:
                pass
                # TODO filtre PKNUM for observation en réduisant
                # dict_model['lst_obs'] avec le pk en cours
            for code in dict_model['lst_obs']:
                self.get_obs(id_run, code)
                self.get_model(id_run, code)


    def ch_date_ref(self, newdate):
        """ change color and change  parameter limite"""
        self.ref_time.setStyleSheet('color: Black')
        self.date_init = newdate.toPyDateTime()







        # # TODO a reprendre il peut avoir plusieur Run affiché
        #

        #
        # if isinstance(final_date, datetime):
        #
        #     last_date_crt = datetime2QDateTime(final_date)
        # else:
        #     last_date_crt = QDateTime(tmps.year, tmps.month, tmps.day, 1, 0, 0)
        #
        # self.start_time_persistence.setDateTime(init_date_crt)
        # self.last_time_persistence.setDateTime(last_date_crt)
        # self.start_time_point.setDateTime(init_date_crt)
        # self.last_time_point.setDateTime(last_date_crt)



        #         final_date = self.date_init + timedelta(seconds=self.lst_times[-1])
        #         if not self.all:
        #             if  self.date_init != old_init:
        #                 self.start_time_persistence.setDateTime(newdate)
        #                 self.start_time_point.setDateTime(newdate)
        #                 self.last_time_persistence.setDateTime(datetime2QDateTime(final_date))
        #                 self.last_time_point.setDateTime(datetime2QDateTime(final_date))
        #

        #
    def ch_date_lim_per(self, newdate):
        """ check limit"""
        date_comp = newdate.toPyDateTime()
        final_date = self.date_init + timedelta(seconds=self.lst_times[-1])
        if date_comp< self.date_init:
            self.start_time_persistence.setDateTime(
                datetime2QDateTime(self.date_init))
            txt = 'Tips start time is incorrect'
            QMessageBox.warning(None, 'warning', txt)
        if date_comp> final_date:
            self.last_time_persistence.setDateTime(
                datetime2QDateTime(final_date))
            txt = 'Tips start last is incorrect'
            QMessageBox.warning(None, 'warning', txt)

        #
        #
    def ch_date_lim_pt(self, newdate):
        """ check limit"""
        date_comp = newdate.toPyDateTime()
        final_date = self.date_init + timedelta(
            seconds=self.lst_times[-1])
        if date_comp < self.date_init:
            self.start_time_point.setDateTime(
                datetime2QDateTime(self.date_init))
            txt = 'Tips start time is incorrect'
            QMessageBox.warning(None, 'warning', txt)
        if date_comp > final_date:
            self.last_time_point.setDateTime(
                datetime2QDateTime(final_date))
            txt = 'Tips last time is incorrect'
            QMessageBox.warning(None, 'warning', txt)




        # if not self.all:
        #     id_run = self.lst_runs[0]
        #     self.date_init, self.lst_times = self.get_times(id_run)
        #     final_date = self.date_init + timedelta(seconds=self.lst_times[-1])
        #     tmps = datetime.today()
        #     self.today = QDateTime(tmps.year, tmps.month, tmps.day, 0, 0, 0)
        #     if isinstance(self.date_init, datetime):
        #         init_date_crt = datetime2QDateTime(self.date_init)
        #     else:
        #         init_date_crt = self.today
        #         self.ref_time.setStyleSheet('color: red')
        #     self.ref_time.setDateTime(init_date_crt)