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
import numpy as np

class ClassScores():
    """
    Class allow to computre scores
    """

    def __init__(self):
        pass

    def eqm(self, y_obs, y_pred):
        """
        mean square error
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return: (array)mean square error
        """
        return np.sqrt(np.mean((y_obs - y_pred) ** 2))

    def ecart(self, y_obs, y_pred):
        """
              error
              :param y_obs: (array)observation
              :param y_pred: (array) data model
              :return:(array) mean error
        """
        return  y_pred - y_obs

    def ecart_abs(self, y_obs, y_pred):
        """
              absolute error
              :param y_obs: (array)observation
              :param y_pred: (array) data model
              :return:(array) mean error
              """
        return np.abs(y_pred - y_obs)

    def mean_err(self, y_obs, y_pred):
        """
        mean error
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return:(array) mean error
        """
        return np.mean((y_pred - y_obs))

    def mean_abs_err(self, y_obs, y_pred):
        """
        mean absolute error
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return: (array) mean absolute error
        """
        return np.mean(np.abs(y_pred - y_obs))

    def mean_r_err(self, y_obs, y_pred):
        """
        mean relative error
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return: (array)  mean relative error
        """
        #TODO
        # Il est à noter que cette formule peut aboutir à des valeurs abérrantes
        #  lorsque les données d'observation sont proches de 0
        # (ce qui se produit, principalement pour du calcul en hauteur,
        # lorsque le zéro de l'échelle est au dessus des plus bas
        # niveaux observables – c'est le cas pour certains marégraphes).
        # Pour remédier à cela, il est possible d'utiliser
        # le paramètre SEUIL_MINIMAL, qui permet d'ignorer
        # les valeurs proches de 0.

        res = np.mean((y_pred - y_obs) / y_obs)
        return res

    def biais(self, y_obs, y_pred):
        """
        mean relative error in %
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return:(array)
        """
        return self.mean_r_err(y_obs, y_pred) * 100

    def mean_rabs_err(self, y_obs, y_pred):
        """
        mean relative absolute error
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return: (array) mean relative absolute error
        """
        #TODO SEUIL_MINIMAL for value near 0
        res = np.mean(np.abs((y_pred - y_obs) / y_obs))
        return res

    def precision(self, y_obs, y_pred):
        """
        mean relative absolute error in %
        :param y_obs: (array)observation
        :param y_pred:  (array) data model
        :return: (array) mean relative absolute error in %
        """
        return self.mean_rabs_err(y_obs, y_pred) * 100

    def std(self, y_obs, y_pred):
        """
        standard deviation
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return:(array) standard deviation
        """
        esp = self.mean_err( y_obs, y_pred)
        res =  np.sqrt(np.mean((y_obs - y_pred -  esp ) ** 2))
        return res

    def nash_crit(self, y_obs, y_pred):
        """
        Nash-Sutcliffe criterion
        We can interpret the results as follows:
            - Nash = 1 : perfect match between observations and forecasts
            - 0 < Nash < 1 : the closer the criterion is to 1, the better the accuracy of the model
            - Nash = 0 : the model is as good as the "climatology"
            (taking the average of the observations as a forecast
            at each time step would have on average the same relevance as the model)
            - Nash < 0 : the model is less good than "climatology"
        It should be noted that the Nash-Sutcliffe criterion is generally
        considered not very relevant for the maritime or estuarine domain
        given the strong and repetitive variations that one meets
        there due to the influence of the tides. This criterion also lends
        itself well to calculations by class, with rephasing or in the ascent phase.

        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :return:(array) Nash-Sutcliffe criterion
        """
        soma = np.sum((y_obs - y_pred) ** 2)
        somb = np.sum((y_obs - np.mean(y_obs)) ** 2)
        nash = 1 - (soma / somb)
        return  nash

    def vol_err(self, q_obs, q_pred, deltat):
        """
        Error on volumes
        :param q_obs: array)observation
        :param q_pred: (array) flowrate model
        :param deltat : time step
        :return:(array) Error on volumes
        """
        return  np.sum(q_pred * deltat) - np.sum(q_obs*deltat)

    def calc_dist(self,dist_step = None):
        """
        distribution list
        :param dist_step: distribution step
        :return: (list)distribution
        """
        if  not dist_step :
            dist_step = 10
        wow = 0
        dist = []
        while wow < 100 - dist_step:
            wow += dist_step
            dist.append(wow / 100.)
        return dist

    def dist_err(self, y_obs, y_pred, dist_step = None):
        """
        error quantiles
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :param dist_step: distribution step
        :return:
        """
        err = self.ecart(y_obs, y_pred)
        dist = self.calc_dist(dist_step)
        return dist, np.quantile(err, dist)

    def dist_abs_err(self, y_obs, y_pred, dist_step = None):
        """
        absolute error quantiles
        :param y_obs: (array)observation
        :param y_pred: (array) data model
        :param dist_step: distribution step
        :return:
        """
        err = self.ecart_abs(y_obs, y_pred)
        dist = self.calc_dist(dist_step)
        return dist, np.quantile(err, dist)

if __name__ == '__main__':
  pass

