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
        self.dico_meth_calc = {0: 'Bradley 78',
                               1: 'Borda',
                               2: 'Loi de seuil',
                               3: 'Loi d''orifice',
                               4: 'Methode test',
                               5: 'Bradley 72'}

        self.dico_meth_draw = {0: 'Method 1',
                               1: 'Method 2',
                               2: 'Method 3',
                               3: 'Method 4',
                               4: 'Method 5'}

        self.dico_struc_typ = {'PC': {'name': 'Pont cadre',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'FORMCUL',
                                                'ORIENTM', 'PENTTAL', 'METBRAD', 'METTEST', 'NBTRAVE',
                                                'TOTALW'],
                                      'meth_calc': [0, 4, 5],
                                      'meth_draw': [[0], [1, 2], [0]]
                                      },
                               'PA': {'name': 'Pont arche',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [1]
                                      },
                               'DA': {'name': 'Dalot',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [2, 3]
                                      },
                               'BU': {'name': 'Buse',
                                      'param': ['ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'FORMCUL'],
                                      'meth_calc': [1]
                                      }
                               }
        #
        self.dico_struc_prm = {'ZTOPTAB': {'name': 'Cote du haut du tablier du pont', 'unit': 'm'},
                               'EPAITAB': {'name': 'Epaisseur du tablier', 'unit': 'm'},
                               'BIAIOUV': {'name': 'Biais de l''ouvrage', 'unit': '°'},
                               'BIAICUL': {'name': 'Biais des culées par rapport à l''axe du pont', 'unit': '°'},
                               'FORMCUL': {'name': 'Forme des culées', 'unit': None},
                               'ORIENTM': {'name': 'Orientation des murs en aile', 'unit': '°'},
                               'PENTTAL': {'name': 'Pente de talus des culées', 'unit': None},
                               'METBRAD': {'name': 'Méthode de création si Bradley', 'unit': None},
                               'NBTRAVE': {'name': 'Nombre de travées', 'unit': None},
                               'METTEST': {'name': 'Méthode de création si Test', 'unit': None},
                               'TOTALW': {'name': 'largeur total sous pont', 'unit': None}
                               }
        # todo demander pour arch
        self.dico_typ_elem = {0: 'Travee',
                              1: 'Pile',
                              2: 'Arche'}
        # obliger de separe largeur pil et tra
        # bradley un seul Type de pile
        self.dico_elem_prm = {'LARG': {'name': 'Largeur de la travée ou pile', 'unit': 'm'},
                              'FORMPIL': {'name': 'Forme de la pile', 'unit': None},
                              # 'LARGPIL': {'name': 'Largeur de la pile', 'unit': 'm'},
                              'BIAIPIL': {'name': 'Biais de la pile par rapport à l''axe du pont', 'unit': '°'}}

        self.dico_culee_pente_talus = {0: '1/1', 1: '1.5/1', 2: '2/1'}


