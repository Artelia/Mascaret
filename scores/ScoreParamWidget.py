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

from .ClassScores import ClassScores


class ScoreParamWidget(QWidget):
    def __init__(self, windmain):
        QWidget.__init__(self)
        self.windmain = windmain
        self.mdb = self.windmain.mgis.mdb
        self.ui = loadUi(
            os.path.join(self.windmain.mgis.masplugPath, 'ui/scores/ui_parametre.ui'),self)

        self.cl_score = ClassScores()
        self.lst_runs = self.windmain.lst_runs
        self.init_gui()

        self.bt_calcul_scores.clicked.connect(self.cpt_score)


    def init_gui(self):
        """
        initialize GUI
        :return:
        """
        pass
        # data = self.mdb.select('runs',
        #                        where="",
        #                        list_var=['init_date'])
        # if any( data['init_date']):
        #     # au moins 1 valeur



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
        if  self.ch_ns_err.isChecked():
            pass
        if  self.ch_vol_err.isChecked():
            pass
        if  self.ch_quantil_err.isChecked():
            # self.dsp_dist_quantil
            pass
        if  self.ch_persistence.isChecked():
            # self.start_time_persistence
            # self.last_time_persistence
            pass
        if  self.ch_pointe_err.isChecked():
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
        self.get_obs()

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

    def get_obs(self):
        """
        get observation data
        :return:
        """
        data = self.mdb.select('outputs',
                                        where="active ",
                                        order="abscissa",
                                        list_var=['code', 'zero',
                                                  'abscissa', 'name'])


        print(data)