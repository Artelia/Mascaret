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
import datetime
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


class ScoreParamWidget(QWidget):
    def __init__(self, windmain):
        QWidget.__init__(self)
        self.windmain = windmain
        self.mdb = self.windmain.mgis.mdb
        self.mgis = self.windmain.mgis
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath,
                         'ui/scores/ui_parametre.ui'), self)

        self.cl_score = ClassScores()
        self.lst_runs = None
        self.init_dates = None
        self.all = True
        self.data = {}
        # {id : { h : [],time : [], q :[]}}
        self.res = {}

        self.init_gui()

        self.bt_calcul_scores.clicked.connect(self.cpt_score)
        #self.bt_calcul_scores.clicked.connect(self.get_test)

    def init_gui(self):
        """
        initialize GUI
        :return:
        """
        pass

    # self.ctrl_ref_date.hide()
    # self.lbl_ref_date.hide()

    # self.ctrl_ref_date # date de référence quand il n'y a pas event pour le modèle
    # if event :
    # self.ctrl_ref_date.hide()
    # self.lbl_ref_date.hide()

    def cpt_score(self):
        """
        run the scores compute
        :return:
        """

        if self.ch_simple_err.isChecked():
            self.cpt_simple_err()
            pass
        if self.ch_ns_err.isChecked():
            pass
        if self.ch_vol_err.isChecked():
            pass
        if self.ch_quantil_err.isChecked():
            # self.dsp_dist_quantil
            pass
        if self.ch_persistence.isChecked():
            # self.start_time_persistence
            # self.last_time_persistence
            pass
        if self.ch_pointe_err.isChecked():
            # self.start_time_point
            # self.last_time_point
            # self.alpha_H
            # self.alpha_Q
            pass

    def cpt_simple_err(self):
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
        :return:
        """
        if self.all :
            self.get_alldata()
        else:
            print('get local ')
            pass
        for id_run in self.lst_runs:

            if self.all:
                h_obs = np.array([])
                h_pred = np.array([])
                q_obs = np.array([])
                q_pred = np.array([])
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

            if self.data[id_run]['hcompt'] :
                print(h_obs, h_pred)
                self.res[id_run]['H']['simple'] = {
                'mean_err':self.cl_score.mean_err(h_obs, h_pred),
                'mean_abs_err': self.cl_score.mean_abs_err( h_obs, h_pred),
                'mean_r_err':self.cl_score.mean_r_err( h_obs, h_pred),
                'biais' : self.cl_score.biais( h_obs, h_pred),
                'mean_rabs_err': self.cl_score.mean_rabs_err( h_obs, h_pred),
                'precision': self.cl_score.precision( h_obs, h_pred),
                'std': self.cl_score.std(h_obs, h_pred),
                'eqm':  self.cl_score.eqm( h_obs, h_pred)
                }

            if self.data[id_run]['qcompt'] :
                self.res[id_run]['Q']['simple'] = {
                'mean_err':self.cl_score.mean_err(q_obs, q_pred),
                'mean_abs_err': self.cl_score.mean_abs_err( q_obs, q_pred),
                'mean_r_err':self.cl_score.mean_r_err( q_obs, q_pred),
                'biais' : self.cl_score.biais( q_obs, q_pred),
                'mean_rabs_err': self.cl_score.mean_rabs_err( q_obs, q_pred),
                'precision': self.cl_score.precision( q_obs, q_pred),
                'std': self.cl_score.std(q_obs, q_pred),
                'eqm':  self.cl_score.eqm( q_obs, q_pred)
                }
        print( self.res[id_run]['H']['simple'])
        pass

    def cpt_ns_err(self):
        """
        compute Nash-Sutcliffe criterion
        :return:
        """
        # self.cl_score.nash_crit(y_obs, y_pred)
        pass

    def cpt_vol_err(self):
        """
        compute Error on volumes
        :return:
        """
        # self.cl_score.vol_err(q_obs, q_pred, deltat)
        pass

    def cpt_quantil_err(self):
        """
        compute  quantiles:
            error quantiles : dist_err
            absolute error quantiles :  dist_abs_err
        :return:
        """
        # self.cl_score.dist_err(y_obs, y_pred, dist_step = None)
        # self.cl_score.dist_abs_err(y_obs, y_pred, dist_step = None)
        pass

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

    def create_dict_pretraitment(self):
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

            final_time = init_time + datetime.timedelta(
                seconds=data_rg['time'][-1])

            info_var = self.mdb.select('results_var',
                                       where="type_res = 'opt' "
                                             "AND var IN('Y', 'ZREF', 'Z', "
                                             "'Q', 'QMIN', 'QMAJ')",
                                       list_var=['id', 'var'])
            print(info_var)
            var_dict = {var: info_var['id'][i] for i, var in
                        enumerate(info_var['var'])}

            where = "active AND code IN (SELECT DISTINCT code FROM {0}.observations " \
                    " WHERE date>'{1}' AND date<'{2}') " \
                    "AND (name IN (SELECT DISTINCT name  FROM {0}.profiles) " \
                    "OR abscissa IN (SELECT DISTINCT abscissa " \
                    "FROM {0}.profiles))".format(self.mdb.SCHEMA,
                                                 init_time, final_time)
            rows = self.mdb.select('outputs',
                                   where=where,
                                   order="abscissa",
                                   list_var=['code', 'abscissa', 'name','zero'])

            if len(rows['code']) == 0:
                self.mgis.add_info("The id_run={} doesn't obsevation.\n "
                                   "The score isn't computed.")
                continue
            for i, code in enumerate(rows['code']):
                if code not in self.obs.keys():
                    self.obs[code] = {'name': rows['name'][i],
                                      'abscissa': rows['abscissa'][i],
                                      'zero' : rows['zero'][i]}

            self.model[id_run] = {
                'init_time': init_time,
                'final_time': final_time,
                'times': data_rg['time'],
                'var': var_dict,
                'pknum': data_rg['pknum'],
                'lst_obs': rows['code']
            }
            self.data[id_run] = {}
            self.res[id_run] = {'H' : {} , 'Q' : {}}

    def get_alldata(self):
        self.create_dict_pretraitment()
        for id_run in self.lst_runs:
            dict_model = self.model[id_run]
            self.data[id_run]['hcompt'] = False
            self.data[id_run]['qcompt'] = False
            if len(dict_model['lst_obs']) == 0:
                print('No find observation')
                return

            if  'Z' in dict_model['var'] or \
                    ('ZREF' in dict_model['var'] and 'Y' in dict_model['var']\
                                 ):
                self.data[id_run]['hcompt'] = True
            if 'Q' in dict_model['var'] or \
                    ('QMIN' in dict_model['var'] and \
                                 'QMAJ' in dict_model['var']):
                self.data[id_run]['qcompt'] = True

            for code in dict_model['lst_obs']:
                self.get_obs(id_run, code)
                self.get_model(id_run, code)

            #print(self.data)







        # récupéré date initial et les liste de  RUns - OK
        # Pour 1 run :
        # connaitre pour le run la date final et initial du modèle :
        # récupérer les data d'observation sur les dates correspondante => abcisse, date, valeur, Q or Z
        # recouper les dates entre observation et modèle
        # check si Z et Q existe si ignore
        # en fonction de la date et de l'abscisse récupéer les valeurs du modèle.
        # interpolation temporel du modèle pour 1 abscisse


        # {run : {time : [...], Z_data : [...], Q_data: [...],
        #                 Z_obs[...], Q_obs[...]}
        # calcul des scores
