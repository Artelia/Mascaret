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


def err_temps_point(y_obs, y_pred, tps_obs, tps_pred, alpha):
    """
    Time shift on the tip

    The calculation of a time lag on the flood maximum will highlight
    the performance of the model on this particular point,
    which is frequently the subject of a communication of quantified
    forecasts. The average of the time shifts on the peak,
    calculated for all the events, can also give an order of
    magnitude of the range of uncertainty on the maxima.
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param tps_obs:(array)observation times
    :param tps_pred:(array) model times
    :param alpha: coefficient
    :return: error
    """
    mxpred = np.max(y_pred * alpha)
    mxobs = np.max(y_obs * alpha)
    idpred = np.where(y_pred == mxpred)[0]
    idobs = np.where(y_obs == mxobs)[0]

    if idpred.size == 0 or idpred.size == 0:
        deltatmax = "No found peaks"
    else:
        deltatmax = tps_pred[idpred[0]] - tps_obs[idobs[0]]
    return deltatmax


def err_point(y_obs, y_pred):
    """
    Errors on the tips
    The calculation of an error on the flood maximum will highlight
    the performance of the model on this particular point, which is
    frequently the subject of a communication of quantified forecasts.
    The average of the errors on the peak, calculated for all the events,
    can also give an order of magnitude of the range of uncertainty
    on the maxima.
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :return: error
    """

    return np.max(y_pred) - np.max(y_obs)


def check_dt_cst(tps):
    """
    check if deltat constant
    :param tps: time data
    :return: true if deltat constant and deltat
    """
    difref = tps[1] - tps[0]
    cond = True
    nbre = len(tps)
    for i in range(nbre):
        if i + 1 < nbre:
            dif = tps[i + 1] - tps[i]
            if not difref == dif:
                cond = False
                break
    return cond, difref


def calc_dist(dist_step=None):
    """
    distribution list
    :param dist_step: distribution step
    :return: (list)distribution
    """
    if not dist_step:
        dist_step = 10
    wow = 0
    dist = []
    while wow < 100 - dist_step:
        wow += dist_step
        dist.append(wow / 100.0)
    return dist


def generate_deltat(lst_time):
    """
    generate deltat array
    :param lst_time: time list
    :return:
    """
    ltime = lst_time[0]
    deltat = []
    for time in lst_time[1:]:
        deltat.append(time - ltime)
        ltime = time
    return np.array(deltat)


def nash_crit(y_obs, y_pred):
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

    :param y_obs: (array)observation data
    :param y_pred: (array) model datal
    :return:(array) Nash-Sutcliffe criterion
    """
    soma = np.sum((y_obs - y_pred) ** 2)
    somb = np.sum((y_obs - np.mean(y_obs)) ** 2)
    if somb == 0:
        nash = None
    else:
        nash = 1 - (soma / somb)
    return nash


def mean_rabs_err(y_obs, y_pred, seuil=None):
    """
    mean relative absolute error
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param seuil : threshold value
    :return: (array) mean relative absolute error
    """
    if seuil:
        tmp = np.ma.masked_array(y_obs, mask=((y_obs <= seuil) & (y_obs >= -seuil)))
        yn_obs = tmp.data
        yn_pred = y_pred[~tmp.mask]
    else:
        yn_obs = y_obs
        yn_pred = y_pred
    res = np.mean(np.abs((yn_pred - yn_obs) / yn_obs))
    return res


def mean_r_err(y_obs, y_pred, seuil=None):
    """
    mean relative error
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param seuil : threshold value
    :return: (array)  mean relative error
    """

    if seuil:
        tmp = np.ma.masked_array(y_obs, mask=((y_obs <= seuil) & (y_obs >= -seuil)))
        yn_obs = tmp.data
        yn_pred = y_pred[~tmp.mask]
    else:
        yn_obs = y_obs
        yn_pred = y_pred

    res = np.mean((yn_pred - yn_obs) / yn_obs)
    return res


def mean_abs_err(y_obs, y_pred):
    """
    mean absolute error
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :return: (array) mean absolute error
    """
    return np.mean(np.abs(y_pred - y_obs))


def mean_err(y_obs, y_pred):
    """
    mean error
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :return:(array) mean error
    """
    return np.mean((y_pred - y_obs))


def ecart_abs(y_obs, y_pred):
    """
          absolute error
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
          :return:(array) mean error
    """
    return np.abs(y_pred - y_obs)


def ecart(y_obs, y_pred):
    """
          error
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
          :return:(array) mean error
    """
    return y_pred - y_obs


def eqm(y_obs, y_pred):
    """
    mean square error
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :return: (array)mean square error
    """
    return np.sqrt(np.mean((y_obs - y_pred) ** 2))


def persistence(y_obs, y_pred, tps_obs, deltat, sumc=False):
    """
    Persistance
    The persistence score is calculated for a given forecast period.
    It amounts to comparing the model studied with the “naive model”,
    which would systematically propose as a forecast at t + Δt
    the value observed at t. Its result varies from - ¥ to +1 and we can
    interpret it this way:
     - Persistence = 1: perfect correspondence between observations
     and forecasts at t + Δt
     - 0 <Persistence <1: the closer the criterion is to 1, the better
     the performance of the model is for the chosen forecast period.
     - Persistence = 0: on average, the model studied is as efficient as
     the naive model, therefore probably not viable
     - Persistence <0: on average, the model studied is less efficient
     than the naive model, therefore probably not viable
    Applying the persistence criterion for very (too) short forecast times
    is irrelevant, the naive model then becoming very difficult to beat
    (and the persistence score being generally poor).
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param deltat : time step
    :param tps_obs:(array)observation times
    :param  sumc : (bool)  if true return sum else reture error
    :return: error
    """
    cond, deltatref = check_dt_cst(tps_obs)
    if cond:
        nb_decal = int(deltat / deltatref)
        sum_n = 0
        sum_d = 0
        nb_obs = len(y_obs)
        i = 0
        while i + nb_decal < nb_obs:
            sum_n += (y_pred[i + nb_decal] - y_obs[i + nb_decal]) ** 2
            sum_d += (y_obs[i] - y_obs[i + nb_decal]) ** 2
            i += 1
        if sumc:
            if sum_d == 0:
                res = None
            else:
                res = 1 - (sum_n / sum_d)
            return res, sum_n, sum_d
        else:
            if sum_d == 0:
                res = None
            else:
                res = 1 - (sum_n / sum_d)
            return res
    else:
        if sumc:
            return None, 0, 0
        else:
            return None


def dist_abs_err(y_obs, y_pred, dist_step=None):
    """
    absolute error quantiles
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param dist_step: distribution step
    :return:
    """
    err = ecart_abs(y_obs, y_pred)
    dist = calc_dist(dist_step)
    return dist, np.quantile(err, dist)


def dist_err(y_obs, y_pred, dist_step=None):
    """
    error quantiles
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param dist_step: distribution step
    :return: error
    """
    err = ecart(y_obs, y_pred)
    dist = calc_dist(dist_step)
    return dist, np.quantile(err, dist)


def vol_err(q_obs, q_pred, lst_time_pred, lst_time_obs):
    """
    Error on volumes
    :param q_obs: array)observation
    :param q_pred: (array) flowrate model
    :param lst_time_pred: model times
    :param lst_time_obs : observation times
    :return:(array) Error on volumes
    """
    q_p = q_pred[1:]
    deltp = generate_deltat(lst_time_pred)
    q_o = q_obs[1:]
    delto = generate_deltat(lst_time_obs)
    return np.sum(q_p * deltp) - np.sum(q_o * delto)


def std(y_obs, y_pred):
    """
    standard deviation
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :return:(array) standard deviation
    """
    esp = mean_err(y_obs, y_pred)
    res = np.sqrt(np.mean((y_pred - y_obs - esp) ** 2))
    return res


def precision(y_obs, y_pred, seuil=None):
    """
    mean relative absolute error in %
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param seuil : threshold value
    :return: (array) mean relative absolute error in %
    """
    return mean_rabs_err(y_obs, y_pred, seuil) * 100


def biais(y_obs, y_pred, seuil=None):
    """
    mean relative error in %
    :param y_obs: (array)observation data
    :param y_pred: (array) model data
    :param seuil : threshold value
    :return:(array)
    """
    return mean_r_err(y_obs, y_pred, seuil) * 100


if __name__ == "__main__":
    pass
