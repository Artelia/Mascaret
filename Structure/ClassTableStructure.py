# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2017
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

class ClassTableStructure:
    def __init__(self, mgis, mdb):
        self.mgis = mgis
        self.mdb = mdb
        self.structure_default()

    def structure_default(self):
        self.dico_struc_typ = {1: {'name': 'Pont cadre',
                                   'param': [1, 2, 3, 4, 5],
                                   'method': {1: {'name': 'Bradley',
                                                  'input': []
                                                  }
                                              }
                                   },
                               2: {'name': 'Pont : arche'},
                               3: {'name': 'Dalot'},
                               4: {'name': 'Buse'}
                               }

        self.dico_struc_prm = {1: {'name': 'Cote du haut du tablier du pont', 'unit': 'm'},
                               2: {'name': 'Epaisseur du tablier', 'unit': 'm'},
                               3: {'name': 'Biais de l''ouvrage', 'unit': '°'},
                               4: {'name': 'Biais des culées par rapport à l''axe du pont', 'unit': '°'},
                               5: {'name': 'Forme des culées', 'unit': None}}

        self.dico_mod_wq = {'TRANSPORT_PUR': 1,
                            'O2': 2,
                            'BIOMASS': 3,
                            'EUTRO': 4,
                            'MICROPOLE': 5,
                            'THERMIC': 6
                            }

        self.dico_meteo = [{"id": 1, "name": 'Air temperatures'},
                           {"id": 2, "name": 'Saturation vapor pressure'},
                           {"id": 3, "name": 'Wind velocities'},
                           {"id": 4, "name": 'Nebulosity'},
                           {"id": 5, "name": 'Solar radiation'},
                           {"id": 6, "name": 'Atmospheric pressure'}]