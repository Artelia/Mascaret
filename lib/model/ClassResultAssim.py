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



class ClassResultAssim:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, num_zones):
        self.dictRes = {'time:': [],
                        "Z": {n for n in range(num_zones)},
                        "Q": {n for n in range(num_zones)},
                        }
        self.num_zones = num_zones

    def store_result(self, valZ, valQ, time, num_zone=None):
        """
        creation run line in runs table
        :param valZ: run name
        :param valQ: Discharge values
        :param time: Current time
        :param num_zone: number of zone to store. By default valZ and valQ contain values for all zones
        :return:
        """
        if num_zone:
            self.dictRes['Z'][num_zone].append(valZ[num_zone])
            self.dictRes['Q'][num_zone].append(valQ[num_zone])
            self.dictRes['time'].append(time)
        else:
            for i in range(self.num_zones):
                self.dictRes['Z'][i].append(valZ[i])
                self.dictRes['Q'][i].append(valQ[i])
                self.dictRes['time'].append(time)

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

