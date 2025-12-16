# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
copyright            : (C) 2017 by Artelia
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
import shutil
import sys
from pathlib import Path
import traceback

from ..ClassMessage import ClassMessage


from ...ui.custom_control import ClassWarningBox


class ClassAssimDB:
    """Class Assimilation gestion base donneee"""
    def __init__(self, mdb=None):
        """Initialize the initializer.
        """
        self.data = {}
        if mdb :
            self.update_data_db(mdb)

    def update_data_db(self, mdb):

        data_config = mdb.select("assil_config", where="active")
        if not data_config:
            self.data = {}
            return

        for idx, ctrl_type in enumerate(data_config['control_type']):
            if 'CtrlKs' in ctrl_type:
                id_type = data_config['id_type'][idx]
                data_ks = mdb.select("assil_ks", where=f"active and id_type={id_type}")
                if not data_ks:
                    continue
                if 'CtrlKs' not in self.data:
                    self.data['CtrlKs'] = { }
                d_perturb = {}
                for var, val  in zip(data_config['perturbation_var'][idx],data_config['perturbation_val'][idx]):
                    d_perturb[var] = val
                self.data['CtrlKs'].update({"obs_var": data_config['control_var'][idx],
                                       "seuil_rejet_misfit": data_config['seuil_rejet_misfit'][idx],
                                       "iterations_sigma": data_config['iterations_sigma'][idx],
                                       "ksmin_perturb": d_perturb['ksMin'],
                                       "ksmaj_perturb": d_perturb['ksMaj']
                })
                list_ks = []
                for idx, ks_type in   enumerate(data_ks['ks_type']):
                    dks = {"num_zone": data_ks['id_zone'][idx],
                           "type": ks_type,
                           "val_min" : data_ks['val_min'][idx],
                           "val_max": data_ks['val_max'][idx],
                           "lst_obs": data_ks['lst_obs'][idx],
                           }
                    list_ks.append(dks)

                self.data['CtrlKs'].update({'lst_zone' : list_ks})
            if 'CtrlLaw' in data_config['control_type']:
                id_type = data_config['id_type'][idx]
                data_law = mdb.select("assil_law", where=f"active and id_type={id_type}")
                if not data_law:
                    continue
                if 'CtrlLaw' not in self.data:
                    self.data['CtrlLaw'] = {}
                d_perturb = {}
                for var, val in zip(data_config['perturbation_var'][idx], data_config['perturbation_val'][idx]):
                    d_perturb[var] = val
                self.data['CtrlLaw'].update({"obs_var": data_config['control_var'][idx],
                                            "seuil_rejet_misfit": data_config['seuil_rejet_misfit'][idx],
                                            "iterations_sigma": data_config['iterations_sigma'][idx],
                                            "lcote_perturb": d_perturb['perturbationsCote'],
                                            "ldebit_perturb": d_perturb['perturbationsDebit'],
                                            "ldebit_lin_perturb": d_perturb['perturbationsDebitLineique']
                                            })
                list_law = []
                for idx, ks_type in enumerate(data_law ['ks_type']):
                    if not (data_law['active_a'][idx] and data_law['active_b'][idx]):
                        continue
                    dlaw= {"id_law": data_law['id_law'][idx],
                           "val_min": data_law['val_min'][idx],
                           "val_max": data_law['val_max'][idx],
                           "lst_obs": data_law['lst_obs'][idx],
                           }
                    if data_law['active_a'][idx]:
                        dlaw.update({
                            'type': 'coefA',
                            "std": data_law['std_a'][idx],
                        })
                        list_law.append(dlaw)
                    if data_law['active_b'][idx]:
                        dlaw.update({
                            'type': 'coefB',
                            "std": data_law['std_b'][idx],
                        })
                        list_law.append(dlaw)

                self.data['CtrlLaw'].update({'lst_loi': list_law})

    def check_assim(self):
        return  bool(self.data)
    def check_assim_ks(self):
        return  bool(self.data.get('CtrlKs'))
    def check_assim_ks(self):
        return  bool(self.data.get('CtrlLaw'))


    # def creat_instance_run_perturb(self):
    #     if not self.data:
    #         return
    #     if self.check_assim_ks:
    #         instance_ks = []
    #         self.data['CtrlKs']
    #         order = 2
    #         for
    #             instance_ks.append({'name': 'perturb',
    #                                  "RUN_REP": os.path.join(folder_run, 'run_init'),
    #                                  "has_casier": False,
    #                                  "has_tracer": False,
    #                                  "starttime": None,
    #                                  "order": order,
    #                                  }
    #             order +=2
    #
    #







