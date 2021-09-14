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
        self.lst_runs =  None
        self.init_dates = None
        self.data = {}
        # {id : { h : [],time : [], q :[]}}
        self.init_gui()

        # self.bt_calcul_scores.clicked.connect(self.cpt_score)
        self.bt_calcul_scores.clicked.connect(self.get_test)

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
        self.get_test()

        # self.cl_score.mean_err( y_obs, y_pred)
        # self.cl_score.mean_abs_err( y_obs, y_pred)
        # self.cl_score.mean_r_err( y_obs, y_pred)
        # self.cl_score.biais( y_obs, y_pred)
        # self.cl_score.mean_rabs_err( y_obs, y_pred)
        # self.cl_score.precision( y_obs, y_pred)
        # self.cl_score.std(y_obs, y_pred)
        # self.cl_score.eqm( y_obs, y_pred)

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

    # def get_data(self):
    #     res = {}
    #     for id_run in self.lst_runs :
    #         res[id_run] = {'time' : [],
    #                         'obs' :[],
    #                        'model':[]}
    #         # get limit time
    #         # get observation
    #         # get model
    #
    #         obs = self.mdb


    def interpol_date(self, datearray, time_model, var_model):
        obs_time = datum_to_float(datearray)
        print(obs_time)
    def get_model(self,id_run):
        """
        get model data
        :return:
        """
        dict_model = self.model[id_run]
        lst_varh = []
        if 'Y' in dict_model['var'] :
            lst_varh.append('Y')
        elif ('ZREF' in dict_model['var'] and 'Z' in dict_model['var']) :
            lst_varh.append('ZREF')
            lst_varh.append('Z')

        lst_varq = []
        if 'Q' in dict_model['var'] :
            lst_varq.append('Q')
        elif ('QMIN' in dict_model['var'] and 'QMAJ' in dict_model['var']):
            lst_varq.append('QMIN')
            lst_varq.append('QMAJ')

        if len(dict_model['lst_obs']) == 0:
            print('No find observation')
            return
        if len(lst_varh) and len(lst_varq)  == 0:
            print('No find variable Q And H')
            return

        for code in dict_model['lst_obs']:
            if self.obs[code]['abscissa']:
                where = 'abscissa = {1}'.format(self.obs[code]['abscissa'])
            elif     self.obs[code]['name'] :
                where = "name='{0}'".format(self.obs[code]['name'])
            else:
                print('No find profile {0}={1} '.format(self.obs[code]['name'],
                                                        self.obs[code]['abscissa']))
                return
            info = self.mdb.select('profiles',
                                   where= where,
                                   list_var=['abscissa'])

            pknum = info['abscissa'][0]
            lst_var = lst_varh + lst_varq

            tmp = {}
            for var in lst_var:
                val = self.mdb.select('results',
                                where="id_runs={0} AND pknum= {1} " \
                                      "and var = {2}".format(id_run,
                                                                pknum,
                                                             dict_model['var'][var] ),
                                order = 'time',
                                list_var=['val'],
                                      verbose= True)
                tmp[var] = val['val']


            if len(lst_varh) > 0:
                if len(lst_varh) > 1:
                    zref = np.array(tmp['ZREF'])
                    z = np.array(tmp['Z'])
                    h = z - zref
                else :
                    h = np.array(tmp['Y'])
                # TODO interpol en fonction des Observations
                #print(h)
                self.interpol_date( self.data[id_run][code]['h_obs_date'],
                                    self.model[id_run]['times'],
                                    h)
                # self.data[id_run][code] = {
                #     'h_mod': h,
                #     'h_mod_time': self.model[id_run]['time']}

            if len(lst_varq) > 0:
                if len(lst_varq) > 1:
                    qmin = np.array(tmp['QMIN'])
                    qmaj = np.array(tmp['QMAJ'])
                    q = qmin + qmaj
                else:
                    q = np.array(tmp['Q'])
                # TODO interpol en fonction de Observation
                # self.data[id_run][code] = {
                #     'q_mod': q,
                #     'q_mod_time': self.model[id_run]['time']}



    def get_obs(self, id_run):
        """
        get observation data
        :return:
        """
        dict_model  = self.model[id_run]
        # variable
        lst_var = []
        if 'Y' in dict_model['var'] or  \
            ('ZREF' in dict_model['var'] and 'Z' in dict_model['var']):
            lst_var.append('H')
        if 'Q' in dict_model['var'] or \
                ('QMIN' in dict_model['var'] and 'QMAJ' in dict_model['var']):
            lst_var.append('Q')

        if len(dict_model['lst_obs']) == 0:
            return
        if len(lst_var) == 0:
            return


        for code in dict_model['lst_obs'] :
            for gg in lst_var:
                condition = """code = '{0}'
                                      AND date>'{1}'
                                      AND date<'{2}'
                                      AND type='{3}'
                                      AND valeur > -999.9""".format(
                    code, dict_model['init_time'],
                    dict_model['final_time'], gg)
                tmp_dict = self.mdb.select("observations", condition, "date",
                                           list_var=['date','valeur'] )
                if gg == 'H' and len(tmp_dict['valeur'])>0:
                  self.data[id_run][code] = {'h_obs' : np.array(tmp_dict['valeur']),
                                            'h_obs_date' : tmp_dict['date']}
                if gg == 'Q' and len(tmp_dict['valeur'])>0:
                    self.data[id_run][code] = {'q_obs' : np.array(tmp_dict['valeur']),
                                            'q_obs_date' : tmp_dict['date']}


    def get_test(self):
        self.obs = {}
        self.model = {}

        # pour chaque run
        for id_run, init_time in zip(self.lst_runs, self.init_dates):

            info = self.mdb.select('runs_graph', where="id_runs={} "
                                                       "AND type_res='opt'"
                                                       "AND var in "
                                                       "('var','time','pknum')".format(id_run),
                                   list_var=['var', 'val']
                                   )
            if len(info['var'])>0:
                data_rg = {var: info['val'][i] for i, var in
                           enumerate(info['var'])}

            final_time = init_time + datetime.timedelta(
                seconds=data_rg['time'][-1])

            info_var = self.mdb.select('results_var',
                                       where="type_res = 'opt' "
                                             "AND var IN('Y', 'ZREF', 'Z', "
                                             "'Q', 'QMIN', 'QMAJ')",
                                   list_var=['id','var'])
            print(info_var)
            var_dict = {var : info_var['id'][i] for i,var in enumerate(info_var['var'])}



            where = "active AND code IN (SELECT DISTINCT code FROM {0}.observations " \
                    " WHERE date>'{1}' AND date<'{2}') " \
                    "AND (name IN (SELECT DISTINCT name  FROM {0}.profiles) "\
	                "OR abscissa IN (SELECT DISTINCT abscissa " \
                    "FROM {0}.profiles))".format(self.mdb.SCHEMA,
                                                init_time,final_time)
            rows = self.mdb.select('outputs',
                                   where=where,
                                   order="abscissa",
                                   list_var=['code', 'abscissa', 'name'])

            if len(rows['code'])==0:
                self.mgis.add_info("The id_run={} doesn't obsevation.\n "
                                   "The score isn't computed.")
                continue
            for i, code in enumerate(rows['code']):
                if code not in self.obs.keys() :
                    self.obs[code] =  {'name': rows['name'][i],
                                       'abscissa': rows['abscissa'][i]}


            self.model[id_run] = {
                'init_time': init_time,
                'final_time': final_time,
                'times': data_rg['time'],
                'var': var_dict,
                'pknum': data_rg['pknum'],
                'lst_obs': rows['code']
            }
            self.data[id_run] = {}

        # get info model and get info Obs OK
        # print( self.model)
        # print(self.obs)
        # get value  for comparaison
        for id_run in self.lst_runs:
            self.get_obs(id_run)
            self.get_model(id_run)

            #print(self.data[id_run])







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
