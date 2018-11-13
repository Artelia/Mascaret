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
class table_WQ():
    def __init__(self, mgis, mdb):
        self.mgis = mgis
        self.mdb = mdb
        self.wq_module_default()
        self.tracer_physic_default()

    def wq_module_default(self):
        self.dico_wq_mod = {1: 'TRANSPORT_PUR',
                            2: 'O2',
                            3: 'BIOMASS',
                            4: 'EUTRO',
                            5: 'MICROPOLE',
                            6: 'THERMIC'
                            }

    def get_cur_wq_mod(self):
        sql = "SELECT steady FROM {0}.parametres WHERE id = 76".format(self.mdb.SCHEMA)
        rows = self.mdb.run_query(sql, fetch=True)
        return int(rows[0][0])

    def tracer_physic_default(self):
        self.dico_phy = {
            'O2': {
                'tracer': [{'sigle': 'O2', 'text': 'Dissolved oxygen'},
                           {'sigle': 'LOR', 'text': 'Organic load'},
                           {'sigle': 'NH4', 'text': 'Ammonia load'}
                           ],
                'physic': [
                    {'sigle': 'K1', 'text': 'KINETIC CONST. FOR ORGANIC LOAD DEPLETION  K1 (DAY-1)', 'value': 0.25},
                    {'sigle': 'K4', 'text': 'KINETIC CONST. FOR NITRIFICATION K4 (DAY-1)', 'value': 0.35},
                    {'sigle': 'BEN', 'text': 'BENTHIC OXYGEN DEMAND BEN (GO2/M2/DAY)', 'value': 0.1},
                    {'sigle': 'P', 'text': 'PHOTOSYNTHESIS P (MGO2/DAY/L)', 'value': 1.0},
                    {'sigle': 'R', 'text': 'PLANT RESPIRATION R (MGO2/DAY/L)', 'value': 0.06},
                    {'sigle': 'K2', 'text': 'OXYGEN REAERATION COEFF. K2 (DAY-1)', 'value': 0.9},
                    {'sigle': 'F_K2', 'text': 'FORMULA FOR THE COEFFICIENT K2', 'value': 0.},
                    {'sigle': 'Cs', 'text': 'OXYGEN SATURATION CONCENTRATION IN THE WATER CS (MG/L)', 'value': 9.0},
                    {'sigle': 'F_Cs', 'text': 'FORMULA FOR THE CONCENTRATION CS', 'value': 0.},
                    {'sigle': 'T', 'text': 'WATER TEMPERATURE T (°C)', 'value': 7.},
                    {'sigle': 'R_COEF', 'text': 'OXYGEN REAERATION COEFF. AT WEIRS R (.)', 'value': 0.},
                    {'sigle': 'F_R', 'text': 'FORMULA FOR THE REAERATION COEFF. r (.)', 'value': 1.},
                    {'sigle': 'N', 'text': 'NUMBER OF WEIRS N', 'value': 0.},
                    {'sigle': 'A_COEF', 'text': 'COEFF. A IN THE FORMULA FOR R AT WEIR N°1', 'value': 1.2},
                    {'sigle': 'B_COEF', 'text': 'COEFF. B IN THE FORMULA FOR R IN WEIR N°1', 'value': 0.7},
                    {'sigle': 'NUM_W', 'text': 'N° OF WEIR N°1', 'value': 1.}
                ]
            },
            'BIOMASS': {
                'tracer': [{'sigle': 'PHY', 'text': 'Phytoplankton biomass'},
                           {'sigle': 'PO4', 'text': 'Assimilable mineral phosphorus'},
                           {'sigle': 'POR', 'text': 'Non-assimilable mineral phosphorus'},
                           {'sigle': 'NO3', 'text': 'Assimilable mineral nitrogen'},
                           {'sigle': 'NOR', 'text': 'Non-assimilable mineral nitrogen'}
                           ],
                'physic': [
                    {'sigle': 'FPOR',
                     'text': 'SETTLING VELOCITY FOR ORGANIC PHOSPHORUS (M/S)',
                     'value': 0.},
                    {'sigle': 'FNOR',
                     'text': ' SETTLING VELOCITY FOR NON-ALGAL ORGANIC NITROGEN (M/S)',
                     'value': 0.},
                    {'sigle': 'Cmax',
                     'text': 'MAX ALGAL GROWTH RATE AT T=20°C',
                     'value': 2.},
                    {'sigle': 'PS',
                     'text': 'SECCHI DEPTH (M)',
                     'value': 0.0},
                    {'sigle': 'KE',
                     'text': 'EXTINCTION COEFF. FOR SOLAR RADIATION RAY WITHOUT PHYTOPLANKTON (M-1)',
                     'value': 3.},
                    {'sigle': 'KPE',
                     'text': 'TURBIDITY COEFF. DUE TO PLANTS (M2/MICROGCHLA)',
                     'value': 0.005},
                    {'sigle': 'IK',
                     'text': 'CALIBRATION PARAMETER FOR SMITH\'S FORMULA (M-1)',
                     'value': 120.},
                    {'sigle': 'KP',
                     'text': 'PHOSPHATE HALF-SATURATION CONSTANT (MG/L)',
                     'value': 0.005},
                    {'sigle': 'KN',
                     'text': 'NITROGEN HALF-SATURATION CONSTANT (MG/L)',
                     'value': 0.03},
                    {'sigle': 'ALPHA',
                     'text': 'WATER TOXICITY COEFF. 1 FOR ALGAE (ALPHA)',
                     'value': 1.},
                    {'sigle': 'ALPHA2',
                     'text': 'WATER TOXICITY COEFF. 2 FOR ALGAE (ALPHA2)',
                     'value': 0.},
                    {'sigle': 'RP',
                     'text': 'RESPIRATION RATE FOR ALGAL BIOMASS AT T=20 °C (DAY-1)',
                     'value': 0.05},
                    {'sigle': 'FP',
                     'text': 'PROPORTION OF PHOSPHORUS IN THE PHYTOPLANKTON CELLS (MGP/MICROGCHLA)',
                     'value': 0.0025},
                    {'sigle': 'DTP',
                     'text': 'PERCENTAGE OF PHOSPHORUS DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'value': 0.5},
                    {'sigle': 'K_PO',
                     'text': 'RATE OF TRANSFORMATION OF POR TO PO4 (DAY-1)',
                     'value': 0.03},
                    {'sigle': 'FN',
                     'text': 'PROPORTION OF NITROGEN IN THE PHYTOPLANKTON CELLS (MGN/MICROGCHLA)',
                     'value': 0.0035},
                    {'sigle': 'DTN',
                     'text': 'PERCENTAGE OF NITROGEN DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'value': 0.5},
                    {'sigle': 'K_NO',
                     'text': 'RATE OF TRASNFORMATION OF NOR TO NO3 (DAY-1)',
                     'value': 0.35},
                    {'sigle': 'M1',
                     'text': 'COEFF. 1 FOR ALGAE DEATH AT T=20 °C (DAY-1)',
                     'value': 0.1},
                    {'sigle': 'M2',
                     'text': 'COEFF. 2 FOR ALGAE DEATH AT T= 20 °C (DAY-1)',
                     'value': 0.003}
                ]
            },
            'EUTRO': {

                'tracer': [
                    {'sigle': 'PHY', 'text': 'Phytoplankton biomass'},
                    {'sigle': 'PO4',
                     'text': 'Assimilable mineral phosphorus'},
                    {'sigle': 'POR',
                     'text': 'Non-assimilable mineral phosphorus'},
                    {'sigle': 'NO3',
                     'text': 'Assimilable mineral nitrogen'},
                    {'sigle': 'NOR',
                     'text': 'Non-assimilable mineral nitrogen'},
                    {'sigle': 'O2', 'text': 'Dissolved oxygen'},
                    {'sigle': 'LOR', 'text': 'Organic load'},
                    {'sigle': 'NH4', 'text': 'Ammonia load'}
                ],
                'physic': [
                    {'sigle': 'FPOR',
                     'text': 'SETTLING VELOCITY FOR ORGANIC PHOSPHORUS (M/S)',
                     'value': 0.},
                    {'sigle': 'FNOR',
                     'text': ' SETTLING VELOCITY FOR NON-ALGAL ORGANIC NITROGEN (M/S)',
                     'value': 0.},
                    {'sigle': 'Cmax',
                     'text': 'MAX ALGAL GROWTH RATE AT T=20°C',
                     'value': 2.},
                    {'sigle': 'PS',
                     'text': 'SECCHI DEPTH (M)',
                     'value': 0.0},
                    {'sigle': 'KE',
                     'text': 'EXTINCTION COEFF. FOR SOLAR RADIATION RAY WITHOUT PHYTOPLANKTON (M-1)',
                     'value': 3.},
                    {'sigle': 'KPE',
                     'text': 'TURBIDITY COEFF. DUE TO PLANTS (M2/MICROGCHLA)',
                     'value': 0.005},
                    {'sigle': 'IK',
                     'text': 'CALIBRATION PARAMETER FOR SMITH\'S FORMULA (M-1)',
                     'value': 120.},
                    {'sigle': 'KP',
                     'text': 'PHOSPHATE HALF-SATURATION CONSTANT (MG/L)',
                     'value': 0.005},
                    {'sigle': 'KN',
                     'text': 'NITROGEN HALF-SATURATION CONSTANT (MG/L)',
                     'value': 0.03},
                    {'sigle': 'ALPHA',
                     'text': 'WATER TOXICITY COEFF. 1 FOR ALGAE (ALPHA)',
                     'value': 1.},
                    {'sigle': 'ALPHA2',
                     'text': 'WATER TOXICITY COEFF. 2 FOR ALGAE (ALPHA2)',
                     'value': 0.},
                    {'sigle': 'RP',
                     'text': 'RESPIRATION RATE FOR ALGAL BIOMASS AT T=20 °C (DAY-1)',
                     'value': 0.05},
                    {'sigle': 'FP',
                     'text': 'PROPORTION OF PHOSPHORUS IN THE PHYTOPLANKTON CELLS (MGP/MICROGCHLA)',
                     'value': 0.0025},
                    {'sigle': 'DTP',
                     'text': 'PERCENTAGE OF PHOSPHORUS DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'value': 0.5},
                    {'sigle': 'K_PO',
                     'text': 'RATE OF TRANSFORMATION OF POR TO PO4 (DAY-1)',
                     'value': 0.03},
                    {'sigle': 'FN',
                     'text': 'PROPORTION OF NITROGEN IN THE PHYTOPLANKTON CELLS (MGN/MICROGCHLA)',
                     'value': 0.0035},
                    {'sigle': 'DTN',
                     'text': 'PERCENTAGE OF NITROGEN DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'value': 0.5},
                    {'sigle': 'K_NO',
                     'text': 'RATE OF TRASNFORMATION OF NOR TO NO3 (DAY-1)',
                     'value': 0.35},
                    {'sigle': 'M1',
                     'text': 'COEFF. 1 FOR ALGAE DEATH AT T=20 °C (DAY-1)',
                     'value': 0.1},
                    {'sigle': 'M2',
                     'text': 'COEFF. 2 FOR ALGAE DEATH AT T= 20 °C (DAY-1)',
                     'value': 0.003},
                    {'sigle': 'K120',
                     'text': 'SETTLING VELOCIUTY FOR ORGANIC LOAD(M / S)',
                     'value': 0.0},
                    {'sigle': 'K1', 'text': 'KINETIC CONST. FOR ORGANIC LOAD DEPLETION  K1 (DAY-1)',
                     'value': 0.25},
                    {'sigle': 'K4', 'text': 'KINETIC CONST. FOR NITRIFICATION K4 (DAY-1)', 'value': 0.35},
                    {'sigle': 'F', 'text': 'OXYGEN PRODUCED BY PHOTOSYNTHESIS F(MGO2 / MICROGCHLA)',
                     'value': 0.15},
                    {'sigle': 'N',
                     'text': 'OXYGEN CONSUMED DURING NITRIFICATION N (MGO2/MGNH4)',
                     'value': 5.2},
                    {'sigle': 'BEN', 'text': 'BENTHIC OXYGEN DEMAND BEN (GO2/M2/DAY)', 'value': 0.1},
                    {'sigle': 'K2', 'text': 'OXYGEN REAERATION COEFF. K2 (DAY-1)', 'value': 0.9},
                    {'sigle': 'F_K2', 'text': 'FORMULA FOR THE COEFFICIENT K2', 'value': 0.},
                    {'sigle': 'Cs', 'text': 'OXYGEN SATURATION CONCENTRATION IN THE WATER CS (MG/L)',
                     'value': 9.0},
                    {'sigle': 'F_Cs', 'text': 'FORMULA FOR THE CONCENTRATION CS', 'value': 0.},
                    {'sigle': 'R_COEF', 'text': 'OXYGEN REAERATION COEFF. AT WEIRS R (.)', 'value': 0.},
                    {'sigle': 'F_R', 'text': 'FORMULA FOR THE REAERATION COEFF. r (.)', 'value': 1.},
                    {'sigle': 'N_W', 'text': 'NUMBER OF WEIRS N', 'value': 0.},
                    {'sigle': 'A_COEF', 'text': 'COEFF. A IN THE FORMULA FOR R AT WEIR N°1', 'value': 1.2},
                    {'sigle': 'B_COEF', 'text': 'COEFF. B IN THE FORMULA FOR R IN WEIR N°1', 'value': 0.7},
                    {'sigle': 'NUM_W', 'text': 'N° OF WEIR N°1', 'value': 1.}
                ]
            },
            'THERMIC': {'tracer': [
                {'sigle': 'TEAU', 'text': 'Water temperature'}],
                'physic': [
                    {'sigle': 'RHO',
                     'text': 'WATER DENSITY (KG/M3))',
                     'value': 1000.},
                    {'sigle': 'CPE',
                     'text': 'SPECIFIC HEAT OF WATER CPE (J/KG°C)',
                     'value': 4180.0},
                    {'sigle': 'CPA',
                     'text': 'SPECIFIC HEAT OF AIR UNDER CONSTANT PRESSURE (J/KG°C)',
                     'value': 1002.},
                    {'sigle': 'A_COEF_T',
                     'text': 'COEFF. A FOR THE AERATION FORMULA A+B*U',
                     'value': 0.002},
                    {'sigle': 'B_COEF_T',
                     'text': 'COEFF. B FOR THE AERATION FORMULA A+B*U',
                     'value': 0.002},
                    {'sigle': 'K_COEF',
                     'text': 'REPRESENTATIVE COEFF. FOR THE COULD COVER K',
                     'value': 0.2},
                    {'sigle': 'EMA',
                     'text': 'CALIBRATION COEFF FOR THE ATMOSPHERIC RADIATION EMA',
                     'value': 0.75},
                    {'sigle': 'EME',
                     'text': 'CALIBRATION COEFF FOR RADIATION AT WATER SURFACE EME',
                     'value': 0.97}
                ]

            },
            'MICROPOLE': {
                'tracer': [
                    {'sigle': 'MES',
                     'text': 'Suspended material'},
                    {'sigle': 'SED',
                     'text': 'Sediments'},
                    {'sigle': 'C_EAU',
                     'text': 'Concentration in water'},
                    {'sigle': 'C_MES',
                     'text': 'Concentration in suspended material'},
                    {'sigle': 'C_SED',
                     'text': 'Concentration in sediments'}
                ],
                'physic': [
                    {'sigle': 'E',
                     'text': 'EROSION RATE (KG/M2/S)',
                     'value': 0.},
                    {'sigle': 'TAU_SED',
                     'text': 'CRITICAL SHEAR STRESS FOR SEDIMENTATION (PA)',
                     'value': 5.},
                    {'sigle': 'TAU_SUSP',
                     'text': 'CRITICAL SHEAR STRESS FOR SUSPENSION (PA)',
                     'value': 1000.},
                    {'sigle': 'W',
                     'text': 'SETTLING VELOCITY OF SUSP.MATTER (M/S)',
                     'value': 0.},
                    {'sigle': 'L',
                     'text': 'EXPONENTIAL DISINTEGRATION CONSTANT (S-1)',
                     'value': 0.},
                    {'sigle': 'KD',
                     'text': 'DISTRIBUTION COEFFICIENT (M3/KG)',
                     'value': 1775.},
                    {'sigle': 'K1_DESO',
                     'text': 'DESORPTION KINETIC CONSTANT (S-1)',
                     'value': 0.}
                ]
            },
            'TRANSPORT_PUR': {
                'tracer': [
                    {'sigle': 'TRA1', 'text': 'Tracer 1'}],
                'physic': []
            }
        }


    def default_tab_phy(self):

        list_var_phy=[]
        list_var_name = []
        id = 1
        id1 = 1
        for key in self.dico_phy:
            for item in self.dico_phy[key]['physic']:
                if item:
                    list_var_phy.append([id,key,
                                    item['sigle'],
                                    item['value'],
                                    item['text']])
                    id += 1

            for item in self.dico_phy[key]['tracer']:
                list_var_name.append([id1,key,
                                item['sigle'],
                                item['text'],True,True])
                id1 += 1


        listeCol = self.mdb.listColumns('tracer_physic')
        var = ",".join(listeCol)
        valeurs = "("
        for k in listeCol:
            valeurs += '%s,'
        valeurs = valeurs[:-1] + ")"
        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                            'tracer_physic',
                                                            var,
                                                            valeurs)
        self.mdb.run_query(sql, many=True, listMany=list_var_phy)

        listeCol = self.mdb.listColumns('tracer_name')
        var = ",".join(listeCol)
        valeurs = "("
        for k in listeCol:
            valeurs += '%s,'
        valeurs = valeurs[:-1] + ")"
        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                            'tracer_name',
                                                            var,
                                                            valeurs)
        self.mdb.run_query(sql, many=True, listMany=list_var_name)







