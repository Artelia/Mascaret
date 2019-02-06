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
        self.dico_meth_calc = {0: 'Bradley 72',
                               1: 'Borda',
                               2: 'Loi de seuil',
                               3: 'Loi d''orifice',
                               4: 'Bradley 78'}

        self.dico_meth_draw = {0: 'Method 1',
                               1: 'Method 2',
                               2: 'Method 3',
                               3: 'Method 4',
                               4: 'Method 5'}

        self.dico_struc_typ = {'PC': {'name': 'Pont cadre',
                                      'param': ['FIRSTWD', 'ZTOPTAB', 'EPAITAB', 'BIAIOUV', 'BIAICUL', 'BIAIPIL',
                                                'FORMCUL', 'ORIENTM', 'PENTTAL', 'FORMPIL', 'METTEST', 'LARGPIL',
                                                'LONGPIL', 'ALPHA1', 'ALPHA2', 'PASH', 'MINH', 'PASQ',
                                                'MINQ', 'MAXQ', 'NBTRAVE', 'METBR72', 'METBR78'],
                                      'meth_calc': [4],
                                      'meth_draw': [[0]]
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

        self.dico_struc_prm = {'FIRSTWD': {'name': 'Abscisse du pied de culée RG', 'unit': 'm'},
                               'ZTOPTAB': {'name': 'Cote du haut du tablier du pont', 'unit': 'm'},
                               'EPAITAB': {'name': 'Epaisseur du tablier', 'unit': 'm'},
                               'BIAIOUV': {'name': 'Biais de l''ouvrage', 'unit': '°'},
                               'BIAICUL': {'name': 'Biais des culées par rapport à l''axe du pont', 'unit': 'Y/N'},
                               'BIAIPIL': {'name': 'Biais de la pile par rapport à l''axe du pont', 'unit': 'Y/N'},
                               'FORMCUL': {'name': 'Forme des culées', 'unit': None},
                               'ORIENTM': {'name': 'Orientation des murs en aile', 'unit': '°'},
                               'PENTTAL': {'name': 'Pente de talus des culées', 'unit': None},
                               'FORMPIL': {'name': 'Forme des piles', 'unit': None},
                               'LARGPIL': {'name': 'Largeur des piles', 'unit': 'm'},
                               'LONGPIL': {'name': 'Longueur des piles', 'unit': 'm'},
                               'ALPHA1': {'name': 'Alpha 1', 'unit': '°'},
                               'ALPHA2': {'name': 'Alpha 2', 'unit': '°'},
                               'PASH': {'name': 'Pas H', 'unit': 'm'},
                               'MINH': {'name': 'Min H', 'unit': 'm'},
                               'PASQ': {'name': 'Pas Q', 'unit': ''},
                               'MINQ': {'name': 'Min Q', 'unit': ''},
                               'MAXQ': {'name': 'Max Q', 'unit': ''},
                               'NBTRAVE': {'name': 'Nombre de travées', 'unit': None},
                               'METBR72': {'name': 'Méthode de création pour Bradley 72', 'unit': None},
                               'METBR78': {'name': 'Méthode de création pour Bradley 78', 'unit': None}}

        self.dico_typ_elem = {0: 'Travée',
                              1: 'Pile',
                              2: 'Arche'}

        self.dico_elem_prm = {'LARGTRA': {'name': 'Largeur de la travée', 'unit': 'm'}
                              }

        self.dico_culee_pente_talus = {0: '1/1', 1: '1.5/1', 2: '2/1'}


