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

import json
import os
import numpy as np


def get_coords_assim(json_file, masc_xcoords, folder=None):
    """
    creation run line in runs table
    :param json_file: fichier json avec les IDs de zones
    :param masc_xcoords: cordonnées du modèle mascaret
    :return:
    """
    # self.dict_stations contient en clé un ID de zone à caler, et en valeurs un dico avec
    # - les coordonnées X des observations associées
    dict_tempo = {1: {'X': [281.41]}, 2: {'X': [281.41]}}
    with open(json_file, 'w') as f:
        json.dump(dict_tempo, f)

    if os.path.exists(json_file):
        with open(json_file) as f:
            dict_stations = json.load(f)
        dict_obs = {}
        keys = np.array([k for k in dict_stations], dtype=int)
        for key in keys:
            for x in dict_stations[str(key)]['X']:
                coord_obs = np.argmin(np.abs(np.subtract(masc_xcoords, x)))
                if coord_obs in dict_obs:
                    dict_obs[coord_obs] = [key]
                else:
                    dict_obs[coord_obs].append(key)
        if folder:
            with open(folder + 'dico_obs.json', 'w') as f:
                json.dump(dict_obs, f)
        return dict_obs, len(keys)
    else:
        return False


class ClassResultAssim:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self):

        self.dictRes = None
        self.num_zones = 0
        self.dict_stations = {}
        self.is_assim = False
        self.dict_obs = {}

    def get_coords_assim(self, json_file, masc_xcoords, folder=None):
        """
        creation run line in runs table
        :param json_file: fichier json avec les IDs de zones
        :param masc_xcoords: cordonnées du modèle mascaret
        :return:
        """
        # self.dict_stations contient en clé un ID de zone à caler, et en valeurs un dico avec
        # - les coordonnées X des observations associées
        # Pour le cas test pour le moment dico en dur avec zone 2 seulement
        dict_tempo = {2: {'X': [83.58]}}
        with open(json_file, 'w') as f:
            json.dump(dict_tempo, f)

        if os.path.exists(json_file):
            with open(json_file) as f:
                self.dict_stations = json.load(f)

            keys = np.array([k for k in self.dict_stations], dtype=int)
            for key in keys:
                for x in self.dict_stations[str(key)]['X']:
                    # print(masc_xcoords)
                    index_obs = int(np.argmin(np.abs(np.subtract(masc_xcoords, x))))
                    if index_obs not in self.dict_obs:
                        self.dict_obs[index_obs] = {'id_zone': [int(key)],
                                                    'x_obs': x}
                    else:
                        self.dict_obs[index_obs]['id_zone'].append(int(key))

            if folder:
                with open(os.path.join(folder, 'dico_obs.json'), 'w') as f:
                    json.dump(self.dict_obs, f)
            # return self.dict_obs
            self.is_assim = True
            self.num_zones = len(keys)
            self.build_res_dict()

    def build_res_dict(self):
        self.dictRes = {'time': [],
                        'Z': {n: [] for n in range(1, self.num_zones + 1)},
                        'Q': {n: [] for n in range(1, self.num_zones + 1)},
                        'Ksmaj': {n: -99 for n in range(1, self.num_zones + 1)},
                        'Ksmin': {n: -99 for n in range(1, self.num_zones + 1)}
                        }

    def store_KS_values(self, KSmin, KSmaj):
        """
        creation run line in runs table
        :param KSmin: KS values in minor bed
        :param KSmaj: KS_values in major bed
        :return:
        """
        for idx, i in enumerate(self.dict_obs):
            for zone in self.dict_obs[i]["id_zone"]:
                self.dictRes['Ksmin'][zone] = KSmin[idx]
                self.dictRes['Ksmaj'][zone] = KSmaj[idx]

    def store_result(self, valZ, valQ, time, num_zone=None):
        """
        creation run line in runs table
        :param valZ: Z values (order of dict_zone keys)
        :param valQ: Discharge values (order of dict_zone keys)
        :param time: Current time
        :param num_zone: number of zone to store. By default valZ and valQ contain values for all zones
        :return:
        """
        if num_zone:
            self.dictRes['Z'][num_zone].append(valZ[num_zone])
            self.dictRes['Q'][num_zone].append(valQ[num_zone])
            self.dictRes['time'].append(time)
        else:
            first = True
            for idx, i in enumerate(self.dict_obs):
                if first:
                    self.dictRes['time'].append(time)
                    first = False
                for zone in self.dict_obs[i]["id_zone"]:
                    self.dictRes['Z'][zone].append(valZ[idx])
                    self.dictRes['Q'][zone].append(valQ[idx])

    def write_results(self, folder, name):
        """
        creation run line in runs table
        :param folder: run name
        :param name: scenario name
        :return:
        """
        if os.path.exists(folder):
            with open(os.path.join(folder, name), 'w') as f:
                json.dump(self.dictRes, f)
        else:
            raise FileNotFoundError(f'Dossier {folder} inexistant')
