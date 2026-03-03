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
from pathlib import Path
from .ClassAssimData import AssimData

class ClassExtractAssim:
    """Class contain  model files creation and run model mascaret"""
    ASSIM_FILE = "data_assim.json"
    def __init__(self, run_path):


        self.dictRes = None
        self.num_zones = 0
        self.dict_stations = {}
        self.dict_obs = {}
        self.zones = []
        self.run_path = run_path
        self.assim_path = self.find_data_assim_path()
        self.assim_dict = AssimData()

    def find_data_assim_path(self):
        """
        Walk upward in the directory tree starting from `start_path`
            to locate the directory containing `data_assim.json`.
        """
        current = Path(self.run_path).resolve()

        if current.is_file():
            current = current.parent

        for directory in [current, *current.parents]:
            data_assim = directory / self.ASSIM_FILE
            if data_assim.is_file():
                return directory

        return '.'

    def init_assim(self, masc):
        size_x = masc.get_var_size("Model.X")[0]
        xcoords = np.array([masc.get("Model.X", i) for i in range(size_x)])
        self.get_coords_assim(xcoords)
        return self.num_zones, self.dict_obs

    def extract_zq(self, masc, t0):
        # Periodic assimilation: store Z and Q at observation nodes

            # Saving results for assimilation
            # TODO if assim ?
            try:
                obs_keys = self.dict_obs  # node indices for observation points
                val_z = [masc.get("State.Z", i) for i in obs_keys]
                val_q = [masc.get("State.Q", i) for i in obs_keys]
                self.store_result(val_z, val_q, t0)
            except Exception as exc:
                raise ValueError(exc) from exc


    def get_coords_assim(self, masc_xcoords):
        """
        creation run line in runs table
        :param masc_xcoords: cordonnées du modèle mascaret
        :return:
        """
        # self.dict_stations contient en clé un ID de zone à caler, et en valeurs un dico avec
        # - les coordonnées X des observations associées
        # Pour le cas test pour le moment dico en dur avec zone 2 seulement
        # dict_tempo = {3: {'X': [83.58]}}
        # with open(json_file, 'w') as f:
        #     json.dump(dict_tempo, f)
        self.assim_dict.load(self.assim_path,filename=self.ASSIM_FILE)
        if self.assim_dict.get("ctrlKS") is not None:
            for dico in self.assim_dict["ctrlKS"]["lst_zone"]:
                self.dict_stations[str(dico["num_zone"])] = {'X': dico["lst_obs"]["abscissa"],
                                                             'code': dico["lst_obs"]["code"]}
                if str(dico["num_zone"]) not in self.zones:
                    self.zones.append(str(dico["num_zone"]))
        # self.dict_stations = json.load(f)
        keys = np.array([k for k in self.dict_stations], dtype=int)

        for key in keys:
            for ix, x in enumerate(self.dict_stations[str(key)]['X']):
                # print(masc_xcoords)
                index_obs = int(np.argmin(np.abs(np.subtract(masc_xcoords, x)))) + 1
                code_obs = self.dict_stations[str(key)]['code'][ix]
                obs_folder = os.path.join(self.assim_path, 'Observations')
                file_obs = os.path.join(obs_folder, str(code_obs) + '.loi')
                with open(file_obs) as f:
                    lines = f.readlines()[3:]
                    # TODO handle time units !!!
                    dt_obs = (float(lines[1].split()[0]) - float(lines[0].split()[0])) * 3600
                    pass
                if index_obs not in self.dict_obs:
                    self.dict_obs[index_obs] = {'id_zone': [int(key)],
                                                'x_obs': x,
                                                'code': code_obs,
                                                'dt_obs': dt_obs}
                else:
                    self.dict_obs[index_obs]['id_zone'].append(int(key))

        with open(os.path.join(self.run_path, 'dico_obs.json'), 'w') as f:
            json.dump(self.dict_obs, f)
        self.build_res_dict()
        self.num_zones = len(keys)
        # return self.dict_obs

    def build_res_dict(self):
        self.dictRes = {'time': [],
                        'Z': {n: {k: [] for k in self.dict_stations[n]["code"]} for n in self.zones},
                        'Q': {n: {k: [] for k in self.dict_stations[n]["code"]} for n in self.zones},
                        'Ksmaj': {n: -99 for n in self.zones},
                        'Ksmin': {n: -99 for n in self.zones}
                        }

    def store_KS_values(self, KSmin, KSmaj):
        """
        creation run line in runs table
        :param KSmin: KS values in minor bed
        :param KSmaj: KS_values in major bed
        :return:
        """
        for i in self.dict_obs:
            print(i)
            print(KSmin[i], KSmaj[i])
            for zone in self.zones:
                self.dictRes['Ksmin'][zone] = KSmin[i]
                self.dictRes['Ksmaj'][zone] = KSmaj[i]

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
            # self.dictRes['time'].append(time)
            first = True
            for idx, i in enumerate(self.dict_obs):
                key_station = self.dict_obs[i]['code']
                if first:
                    self.dictRes['time'].append(time)
                    first = False
                for zone in self.dict_obs[i]["id_zone"]:
                    self.dictRes['Z'][str(zone)][key_station].append(valZ[idx])
                    self.dictRes['Q'][str(zone)][key_station].append(valQ[idx])

    def write_results(self, folder, name):
        """
        creation run line in runs table
        :param folder: run name
        :param name: scenario name
        :return:
        """
        if os.path.exists(self.run_path):
            with open(os.path.join(folder, name), 'w') as f:
                json.dump(self.dictRes, f)
        else:
            raise FileNotFoundError(f'Dossier {folder} inexistant')
