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


class ClassTableWQ:
    def __init__(self, mgis, mdb):
        self.mgis = mgis
        self.mdb = mdb
        self.dico_wq_mod = {}
        self.dico_mod_wq = {}
        self.dico_meteo = {}
        self.dico_phy = {}

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

    def get_cur_wq_mod(self):
        # modeleQualiteEau
        sql = "SELECT steady FROM {0}.parametres WHERE parametre = 'modeleQualiteEau'".format(
            self.mdb.SCHEMA)
        rows = self.mdb.run_query(sql, fetch=True)
        return int(rows[0][0])

    def tracer_physic_default(self):
        self.dico_phy = {
            'O2': {
                'tracer': [{'sigle': 'O2', 'text': 'Dissolved oxygen',
                            'textfr': u"Oxygène dissous"},
                           {'sigle': 'LOR', 'text': 'Organic load',
                            'textfr': u"Charge organique"},
                           {'sigle': 'NH4', 'text': 'Ammonia load',
                            'textfr': u"Charge ammoniacale"}
                           ],
                'physic': [
                    {'sigle': 'K1',
                     'text': 'KINETIC CONST. FOR ORGANIC LOAD DEPLETION  K1 (DAY-1)',
                     'textfr': u"CONST. DE CINET. DE DEGRADATION DE LA CHARGE ORGANIQUE K1 (J-1)",
                     'value': 0.25},
                    {'sigle': 'K4',
                     'text': 'KINETIC CONST. FOR NITRIFICATION K4 (DAY-1)',
                     'textfr': u"CONST. DE CINET. DE NITRIFICATION K4 (J-1)",
                     'value': 0.35},
                    {'sigle': 'BEN',
                     'text': 'BENTHIC OXYGEN DEMAND BEN (GO2/M2/DAY)',
                     'textfr': u"DEMANDE BENTHIQUE BEN (GO2/M2/J)",
                     'value': 0.1},
                    {'sigle': 'P', 'text': 'PHOTOSYNTHESIS P (MGO2/DAY/L)',
                     'textfr': u"PHOTOSYNTHESE P (MGO2/J/L)",
                     'value': 1.0},
                    {'sigle': 'R', 'text': 'PLANT RESPIRATION R (MGO2/DAY/L)',
                     'textfr': u"RESPIRATION VEGETALE R (MGO2/J/L)",
                     'value': 0.06},
                    {'sigle': 'K2',
                     'text': 'OXYGEN REAERATION COEFF. K2 (DAY-1)',
                     'textfr': u"COEFFICIENT DE REAERATION K2 (J-1)",
                     'value': 0.9},
                    {'sigle': 'F_K2', 'text': 'FORMULA FOR THE COEFFICIENT K2',
                     'textfr': u"FORMULE DE CALCUL DE K2",
                     'value': 0.},
                    {'sigle': 'Cs',
                     'text': 'OXYGEN SATURATION CONCENTRATION IN THE WATER CS (MG/L)',
                     'textfr': u"CONCENTRATION DE SATURATION EN OXYGENE DE L'EAU CS (MG/L)",
                     'value': 9.0},
                    {'sigle': 'F_Cs',
                     'text': 'FORMULA FOR THE CONCENTRATION CS',
                     'textfr': u"FORMULE DE CALCUL DE CS",
                     'value': 0.},
                    {'sigle': 'T', 'text': 'WATER TEMPERATURE T ( C)',
                     'textfr': u"TEMPERATURE DE L'EAU T ( C)",
                     'value': 7.},
                    {'sigle': 'R_COEF',
                     'text': 'OXYGEN REAERATION COEFF. AT WEIRS R (.)',
                     'textfr': u"COEFFICIENT DE REAERATION AUX SEUILS R (.)",
                     'value': 0.},
                    {'sigle': 'F_R',
                     'text': 'FORMULA FOR THE REAERATION COEFF. r (.)',
                     'textfr': u"FORMULE DE CALCUL DE R",
                     'value': 1.},
                    {'sigle': 'N', 'text': 'NUMBER OF WEIRS N',
                     'textfr': u"NOMBRE DE SEUILS N",
                     'value': 0.},
                    {'sigle': 'A_COEF',
                     'text': 'COEFF. A IN THE FORMULA FOR R AT WEIR N 1',
                     'textfr': u"COEFFICIENT A DES FORMULES DE CALCUL DE R POUR LE SEUIL N 1",
                     'value': 1.2},
                    {'sigle': 'B_COEF',
                     'text': 'COEFF. B IN THE FORMULA FOR R IN WEIR N 1',
                     'textfr': u"COEFFICIENT B DES FORMULES DE CALCUL DE R POUR LE SEUIL N 1",
                     'value': 0.7},
                    {'sigle': 'NUM_W', 'text': 'N  OF WEIR N 1',
                     'textfr': u"N  DU SEUIL N 1",
                     'value': 1.}
                ],
                'meteo': False
            },
            'BIOMASS': {
                'tracer': [{'sigle': 'PHY', 'text': 'Phytoplankton biomass',
                            'textfr': u"Biomasse phytoplanctonique"},
                           {'sigle': 'PO4',
                            'text': 'Assimilable mineral phosphorus',
                            'textfr': u"Phosphore minéral assimilable"},
                           {'sigle': 'POR',
                            'text': 'Non-assimilable mineral phosphorus',
                            'textfr': u"Phosphore minéral non assimilable"},
                           {'sigle': 'NO3',
                            'text': 'Assimilable mineral nitrogen',
                            'textfr': u"Azote minéral assimilable"},
                           {'sigle': 'NOR',
                            'text': 'Non-assimilable mineral nitrogen',
                            'textfr': u"Azote minéral non assimilable"}
                           ],
                'physic': [
                    {'sigle': 'FPOR',
                     'text': 'SETTLING VELOCITY FOR ORGANIC PHOSPHORUS (M/S)',
                     'textfr': u"VITESSE DE SEDIMENTATION DU PHOSPHORE ORGANIQUE (M/S)",
                     'value': 0.},
                    {'sigle': 'FNOR',
                     'text': ' SETTLING VELOCITY FOR NON-ALGAL ORGANIC NITROGEN (M/S)',
                     'textfr': u"VITESSE DE SEDIMENTATION DE L'AZOTE ORGANIQUE NON ALGALE (M/S)",
                     'value': 0.},
                    {'sigle': 'Cmax',
                     'text': 'MAX ALGAL GROWTH RATE AT T=20 C',
                     'textfr': u"TAUX DE CROISSANCE ALGALE MAXIMUM A 20 C",
                     'value': 2.},
                    {'sigle': 'PS',
                     'text': 'SECCHI DEPTH (M)',
                     'textfr': u"PROFONDEUR DE SECCHI (M)",
                     'value': 0.0},
                    {'sigle': 'KE',
                     'text': 'EXTINCTION COEFF. FOR SOLAR RADIATION RAY WITHOUT PHYTOPLANKTON (M-1)',
                     'textfr': u"COEFFICIENT D'EXTINCTION DU RAY SANS PHYTO (M-1)",
                     'value': 3.},
                    {'sigle': 'KPE',
                     'text': 'TURBIDITY COEFF. DUE TO PLANTS (M2/MICROGCHLA)',
                     'textfr': u"COEFFICIENT DE TURBIDITE VEGETALE (M2/MICROGCHLA)",
                     'value': 0.005},
                    {'sigle': 'IK',
                     'text': 'CALIBRATION PARAMETER FOR SMITH\'S FORMULA (M-1)',
                     'textfr': u"PARAMETRE DE CALAGE DE LA FORMULE DE SMITH (M-1)",
                     'value': 120.},
                    {'sigle': 'KP',
                     'text': 'PHOSPHATE HALF-SATURATION CONSTANT (MG/L)',
                     'textfr': u"CONSTANTE DE DEMI-SATURATION EN PHOSPHATE (MG/L)",
                     'value': 0.005},
                    {'sigle': 'KN',
                     'text': 'NITROGEN HALF-SATURATION CONSTANT (MG/L)',
                     'textfr': u"CONSTANTE DE DEMI-SATURATION EN AZOTE (MG/L)",
                     'value': 0.03},
                    {'sigle': 'ALPHA',
                     'text': 'WATER TOXICITY COEFF. 1 FOR ALGAE (ALPHA)',
                     'textfr': u"COEFFICIENT 1 DE TOXICITE DE L'EAU POUR LES ALGUES (ALPHA)",
                     'value': 1.},
                    {'sigle': 'ALPHA2',
                     'text': 'WATER TOXICITY COEFF. 2 FOR ALGAE (ALPHA2)',
                     'textfr': u"COEFFICIENT 2 DE TOXICITE DE L'EAU POUR LES ALGUES (ALPHA2)",
                     'value': 0.},
                    {'sigle': 'RP',
                     'text': 'RESPIRATION RATE FOR ALGAL BIOMASS AT T=20  C (DAY-1)',
                     'textfr': u"TAUX DE RESPIRATION DE LA BIOMASSE ALGALE A 20 C (J-1)",
                     'value': 0.05},
                    {'sigle': 'FP',
                     'text': 'PROPORTION OF PHOSPHORUS IN THE PHYTOPLANKTON CELLS (MGP/MICROGCHLA)',
                     'textfr': u"PROP DE PHOSPHORE DANS LES CELLULES DU PHYTO (MGP/MICROGCHLA)",
                     'value': 0.0025},
                    {'sigle': 'DTP',
                     'text': 'PERCENTAGE OF PHOSPHORUS DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'textfr': u"POURCENT. DE PHOSPHORE DIRECT. ASSIMILABLE DANS LE PHYTO MORT (%)",
                     'value': 0.5},
                    {'sigle': 'K_PO',
                     'text': 'RATE OF TRANSFORMATION OF POR TO PO4 (DAY-1)',
                     'textfr': u"TAUX DE TRANSFORMATION DU POR EN PO4 (J-1)",
                     'value': 0.03},
                    {'sigle': 'FN',
                     'text': 'PROPORTION OF NITROGEN IN THE PHYTOPLANKTON CELLS (MGN/MICROGCHLA)',
                     'textfr': u"PROP D'AZOTE DANS LES CELLULES DU PHYTO (MGN/MICROGCHLA)",
                     'value': 0.0035},
                    {'sigle': 'DTN',
                     'text': 'PERCENTAGE OF NITROGEN DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'textfr': u"POURCENT. D'AZOTE DIRECT. ASSIMILABLE DANS LE PHYTO MORT (%)",
                     'value': 0.5},
                    {'sigle': 'K_NO',
                     'text': 'RATE OF TRASNFORMATION OF NOR TO NO3 (DAY-1)',
                     'textfr': u"TAUX DE TRANSFORMATION DU NOR EN NO3 (J-1)",
                     'value': 0.35},
                    {'sigle': 'M1',
                     'text': 'COEFF. 1 FOR ALGAE DEATH AT T=20  C (DAY-1)',
                     'textfr': u"COEFFICIENT 1 DE MORTALITE ALGALE A 20 C (J-1)",
                     'value': 0.1},
                    {'sigle': 'M2',
                     'text': 'COEFF. 2 FOR ALGAE DEATH AT T= 20  C (DAY-1)',
                     'textfr': u"COEFFICIENT 2 DE MORTALITE ALGALE A 20 C (J-1/MG)",
                     'value': 0.003}
                ],
                'meteo': True,
            },
            'EUTRO': {

                'tracer': [
                    {'sigle': 'PHY', 'text': 'Phytoplankton biomass',
                     'textfr': u"Biomasse phytoplanctonique"},
                    {'sigle': 'PO4',
                     'text': 'Assimilable mineral phosphorus',
                     'textfr': u"Phosphore minéral assimilable"},
                    {'sigle': 'POR',
                     'text': 'Non-assimilable mineral phosphorus',
                     'textfr': u"Phosphore minéral non assimilable"},
                    {'sigle': 'NO3',
                     'text': 'Assimilable mineral nitrogen',
                     'textfr': u"Azote minéral assimilable"},
                    {'sigle': 'NOR',
                     'text': 'Non-assimilable mineral nitrogen',
                     'textfr': u"Azote minéral non assimilable"},
                    {'sigle': 'NH4', 'text': 'Ammonia load',
                     'textfr': u"Charge ammoniacale"},
                    {'sigle': 'LOR', 'text': 'Organic load',
                     'textfr': u"Charge organique"},
                    {'sigle': 'O2', 'text': 'Dissolved oxygen',
                     'textfr': u"Oxygène dissous"}
                ],
                'physic': [
                    {'sigle': 'FPOR',
                     'text': u'SETTLING VELOCITY FOR ORGANIC PHOSPHORUS (M/S)',
                     'textfr': u"VITESSE DE SEDIMENTATION DU PHOSPHORE ORGANIQUE (M/S)",
                     'value': 0.},
                    {'sigle': 'FNOR',
                     'text': u'SETTLING VELOCITY FOR NON-ALGAL ORGANIC NITROGEN (M/S)',
                     'textfr': u"VITESSE DE SEDIMENTATION DE L'AZOTE ORGANIQUE NON ALGALE (M/S)",
                     'value': 0.},
                    {'sigle': 'Cmax',
                     'text': u'MAX ALGAL GROWTH RATE AT T=20 C',
                     'textfr': u"TAUX DE CROISSANCE ALGALE MAXIMUM A 20 C",
                     'value': 2.},
                    {'sigle': 'PS',
                     'text': u'SECCHI DEPTH (M)',
                     'textfr': u"PROFONDEUR DE SECCHI (M)",
                     'value': 0.0},
                    {'sigle': 'KE',
                     'text': u'EXTINCTION COEFF. FOR SOLAR RADIATION RAY WITHOUT PHYTOPLANKTON (M-1)',
                     'textfr': u"COEFFICIENT D'EXTINCTION DU RAY SANS PHYTO (M-1)",
                     'value': 3.},
                    {'sigle': 'KPE',
                     'text': u'TURBIDITY COEFF. DUE TO PLANTS (M2/MICROGCHLA)',
                     'textfr': u"COEFFICIENT DE TURBIDITE VEGETALE (M2/MICROGCHLA)",
                     'value': 0.005},
                    {'sigle': 'IK',
                     'text': u'CALIBRATION PARAMETER FOR SMITH\'S FORMULA (M-1)',
                     'textfr': u"PARAMETRE DE CALAGE DE LA FORMULE DE SMITH (M-1)",
                     'value': 120.},
                    {'sigle': 'KP',
                     'text': u'PHOSPHATE HALF-SATURATION CONSTANT (MG/L)',
                     'textfr': u"CONSTANTE DE DEMI-SATURATION EN PHOSPHATE (MG/L)",
                     'value': 0.005},
                    {'sigle': 'KN',
                     'text': u'NITROGEN HALF-SATURATION CONSTANT (MG/L)',
                     'textfr': u"CONSTANTE DE DEMI-SATURATION EN AZOTE (MG/L)",
                     'value': 0.03},
                    {'sigle': 'ALPHA',
                     'text': u'WATER TOXICITY COEFF. 1 FOR ALGAE (ALPHA)',
                     'textfr': u"COEFFICIENT 1 DE TOXICITE DE L'EAU POUR LES ALGUES (ALPHA)",
                     'value': 1.},
                    {'sigle': 'ALPHA2',
                     'text': u'WATER TOXICITY COEFF. 2 FOR ALGAE (ALPHA2)',
                     'textfr': u"COEFFICIENT 2 DE TOXICITE DE L'EAU POUR LES ALGUES (ALPHA2)",
                     'value': 0.},
                    {'sigle': 'RP',
                     'text': u'RESPIRATION RATE FOR ALGAL BIOMASS AT T=20  C (DAY-1)',
                     'textfr': u"TAUX DE RESPIRATION DE LA BIOMASSE ALGALE A 20 C (J-1)",
                     'value': 0.05},
                    {'sigle': 'FP',
                     'text': u'PROPORTION OF PHOSPHORUS IN THE PHYTOPLANKTON CELLS (MGP/MICROGCHLA)',
                     'textfr': u"PROP DE PHOSPHORE DANS LES CELLULES DU PHYTO (MGP/MICROGCHLA)",
                     'value': 0.0025},
                    {'sigle': 'DTP',
                     'text': u'PERCENTAGE OF PHOSPHORUS DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'textfr': u"POURCENT. DE PHOSPHORE DIRECT. ASSIMILABLE DANS LE PHYTO MORT (%)",
                     'value': 0.5},
                    {'sigle': 'K_PO',
                     'text': u'RATE OF TRANSFORMATION OF POR TO PO4 (DAY-1)',
                     'textfr': u"TAUX DE TRANSFORMATION DU POR EN PO4 (J-1)",
                     'value': 0.03},
                    {'sigle': 'FN',
                     'text': u'PROPORTION OF NITROGEN IN THE PHYTOPLANKTON CELLS (MGN/MICROGCHLA)',
                     'textfr': u"PROP D'AZOTE DANS LES CELLULES DU PHYTO (MGN/MICROGCHLA)",
                     'value': 0.0035},
                    {'sigle': 'DTN',
                     'text': u'PERCENTAGE OF NITROGEN DIRECTLY ASSIMILATED BY DEAD PHYTOPLANKTON (%)',
                     'textfr': u"POURCENT. D'AZOTE DIRECT. ASSIMILABLE DANS LE PHYTO MORT (%)",
                     'value': 0.5},
                    {'sigle': 'K_NO',
                     'text': u'RATE OF TRASNFORMATION OF NOR TO NO3 (DAY-1)',
                     'textfr': u"TAUX DE TRANSFORMATION DU NOR EN NO3 (J-1)",
                     'value': 0.35},
                    {'sigle': 'M1',
                     'text': u'COEFF. 1 FOR ALGAE DEATH AT T=20  C (DAY-1)',
                     'textfr': u"COEFFICIENT 1 DE MORTALITE ALGALE A 20 C (J-1)",
                     'value': 0.1},
                    {'sigle': 'M2',
                     'text': u'COEFF. 2 FOR ALGAE DEATH AT T= 20  C (DAY-1)',
                     'textfr': u"COEFFICIENT 2 DE MORTALITE ALGALE A 20 C (J-1/MG)",
                     'value': 0.003},
                    {'sigle': 'K120',
                     'text': u'SETTLING VELOCIUTY FOR ORGANIC LOAD(M / S)',
                     'textfr': u"VITESSE DE SEDIMENTATION DE LA CHARGE ORGANIQUE (M/S)",
                     'value': 0.0},
                    {'sigle': 'K1',
                     'text': u'KINETIC CONST. FOR ORGANIC LOAD DEPLETION  K1 (DAY-1)',
                     'textfr': u"CONST. DE CINET. DE DEGRADATION DE LA CHARGE ORGANIQUE K120 (J-1)",
                     'value': 0.25},
                    {'sigle': 'K4',
                     'text': 'KINETIC CONST. FOR NITRIFICATION K4 (DAY-1)',
                     'textfr': u"CONST. DE CINET. DE NITRIFICATION K520 (J-1)",
                     'value': 0.35},
                    {'sigle': 'F',
                     'text': u'OXYGEN PRODUCED BY PHOTOSYNTHESIS F(MGO2 / MICROGCHLA)',
                     'textfr': u"QTTE D'OXYGENE PRODUITE PAR PHOTOSYNTHESE F (MGO2/MICROGCHLA)",
                     'value': 0.15},
                    {'sigle': 'N',
                     'text': u'OXYGEN CONSUMED DURING NITRIFICATION N (MGO2/MGNH4)',
                     'textfr': u"QTTE D'OXYGENE CONSOMMEE PAR NITRIFICATION N (MGO2/MGNH4)",
                     'value': 5.2},
                    {'sigle': 'BEN',
                     'text': u'BENTHIC OXYGEN DEMAND BEN (GO2/M2/DAY)',
                     'textfr': u"DEMANDE BENTHIQUE BEN (GO2/M2/J)",
                     'value': 0.1},
                    {'sigle': 'K2',
                     'text': u'OXYGEN REAERATION COEFF. K2 (DAY-1)',
                     'textfr': u"COEFFICIENT DE REAERATION K2 (J-1)",
                     'value': 0.9},
                    {'sigle': 'F_K2', 'text': u'FORMULA FOR THE COEFFICIENT K2',
                     'textfr': u"FORMULE DE CALCUL DE K2",
                     'value': 0.},
                    {'sigle': 'Cs',
                     'text': u'OXYGEN SATURATION CONCENTRATION IN THE WATER CS (MG/L)',
                     'textfr': u"CONCENTRATION DE SATURATION EN OXYGENE DE L'EAU CS (MG/L)",
                     'value': 9.0},
                    {'sigle': 'F_Cs',
                     'text': u'FORMULA FOR THE CONCENTRATION CS',
                     'textfr': u"FORMULE DE CALCUL DE CS",
                     'value': 0.},
                    {'sigle': 'R_COEF',
                     'text': u'OXYGEN REAERATION COEFF. AT WEIRS R (.)',
                     'textfr': u"COEFFICIENT DE REAERATION AUX SEUILS R (.)",
                     'value': 0.},
                    {'sigle': 'F_R',
                     'text': u'FORMULA FOR THE REAERATION COEFF. r (.)',
                     'textfr': u"FORMULE DE CALCUL DE R",
                     'value': 1.},
                    {'sigle': 'N_W', 'text': u'NUMBER OF WEIRS N',
                     'textfr': u"NOMBRE DE SEUILS N",
                     'value': 0.},
                    {'sigle': 'A_COEF',
                     'text': u'COEFF. A IN THE FORMULA FOR R AT WEIR N 1',
                     'textfr': u"COEFFICIENT A DES FORMULES DE CALCUL DE R POUR LE SEUIL N 1",
                     'value': 1.2},
                    {'sigle': 'B_COEF',
                     'text': u'COEFF. B IN THE FORMULA FOR R IN WEIR N 1',
                     'textfr': u"COEFFICIENT B DES FORMULES DE CALCUL DE R POUR LE SEUIL N 1",
                     'value': 0.7},
                    {'sigle': 'NUM_W',
                     'text': u'N  OF WEIR N 1',
                     'textfr': u"N  DU SEUIL N 1",
                     'value': 1.}
                ],
                'meteo': True
            },
            'THERMIC': {'tracer': [
                {'sigle': 'TEAU', 'text': u'Water temperature',
                 'textfr': u"Température de l'eau"}],
                'physic': [
                    {'sigle': 'RHO',
                     'text': u'WATER DENSITY (KG/M3)',
                     'textfr': u"MASSE VOLUMIQUE DE L'EAU RHO (KG/M3)",
                     'value': 1000.},
                    {'sigle': 'CPE',
                     'text': u'SPECIFIC HEAT OF WATER CPE (J/KG C)',
                     'textfr': u"CHALEUR SPECIFIQUE DE L'EAU CPE (J/KG C)",
                     'value': 4180.0},
                    {'sigle': 'CPA',
                     'text': u'SPECIFIC HEAT OF AIR UNDER CONSTANT PRESSURE (J/KG C)',
                     'textfr': u"CHALEUR SPECIFIQUE DE L'AIR A PRESSION CONSTANTE CPA (J/KG C)",
                     'value': 1002.},
                    {'sigle': 'A_COEF_T',
                     'text': u'COEFF. A FOR THE AERATION FORMULA A+B*U',
                     'textfr': u"COEFFICIENT A DE LA FORMULE D'AERATION A+B*U",
                     'value': 0.002},
                    {'sigle': 'B_COEF_T',
                     'text': u'COEFF. B FOR THE AERATION FORMULA A+B*U',
                     'textfr': u"COEFFICIENT B DE LA FORMULE D'AERATION A+B*U",
                     'value': 0.002},
                    {'sigle': 'K_COEF',
                     'text': u'REPRESENTATIVE COEFF. FOR THE COULD COVER K',
                     'textfr': u"COEFFICIENT REPRESENTATIF DE LA COUVERTURE NUAGEUSE K",
                     'value': 0.2},
                    {'sigle': 'EMA',
                     'text': u'CALIBRATION COEFF FOR THE ATMOSPHERIC RADIATION EMA',
                     'textfr': u"COEFFICIENT DE CALAGE DU RAYONNEMENT ATMOSPHERIQUE EMA",
                     'value': 0.75},
                    {'sigle': 'EME',
                     'text': u'CALIBRATION COEFF FOR RADIATION AT WATER SURFACE EME',
                     'textfr': u"COEFFICIENT DE CALAGE DU RAYONNEMENT DU PLAN D'EAU EME",
                     'value': 0.97}
                ],
                'meteo': True

            },
            'MICROPOLE': {
                'tracer': [
                    {'sigle': 'MES',
                     'text': u'Suspended material',
                     'textfr': u"Matière en suspension"},
                    {'sigle': 'SED',
                     'text': u'Sediments',
                     'textfr': u"Sédiments"},
                    {'sigle': 'C_EAU',
                     'text': u'Concentration in water',
                     'textfr': u"Concentration dans l'eau"},
                    {'sigle': 'C_MES',
                     'text': u'Concentration in suspended material',
                     'textfr': u"Concentration dans les MES"},
                    {'sigle': 'C_SED',
                     'text': u'Concentration in sediments',
                     'textfr': u"Concentration dans les sédiments"}
                ],
                'physic': [
                    {'sigle': 'E',
                     'text': u'EROSION RATE (KG/M2/S)',
                     'textfr': u"TAUX D'EROSION (KG/M2/S)",
                     'value': 0.},
                    {'sigle': 'TAU_SED',
                     'text': u'CRITICAL SHEAR STRESS FOR SEDIMENTATION (PA)',
                     'textfr': u"CONTRAINTE CRITIQUE DE SEDIMENTATION (PA)",
                     'value': 5.},
                    {'sigle': 'TAU_SUSP',
                     'text': u'CRITICAL SHEAR STRESS FOR SUSPENSION (PA)',
                     'textfr': u"CONTRAINTE CRITIQUE DE REMISE EN SUSPENSION (PA)",
                     'value': 1000.},
                    {'sigle': 'W',
                     'text': u'SETTLING VELOCITY OF SUSP.MATTER (M/S)',
                     'textfr': u"VITESSE DE CHUTE DES M.E.S. (M/S)",
                     'value': 0.},
                    {'sigle': 'L',
                     'text': u'EXPONENTIAL DISINTEGRATION CONSTANT (S-1)',
                     'textfr': u"CONSTANTE DE DESINTEGRATION EXPONENTIELLE (S-1)",
                     'value': 0.},
                    {'sigle': 'KD',
                     'text': u'DISTRIBUTION COEFFICIENT (M3/KG)',
                     'textfr': u"COEFFICIENT DE DISTRIBUTION (M3/KG)",
                     'value': 1775.},
                    {'sigle': 'K1_DESO',
                     'text': u'DESORPTION KINETIC CONSTANT (S-1)',
                     'textfr': u"CONSTANTE CINETIQUE DE DESORPTION (S-1)",
                     'value': 0.}
                ],
                'meteo': False
            },
            'TRANSPORT_PUR': {
                'tracer': [
                    {'sigle': 'TRA1', 'text': u'Tracer 1',
                     'textfr': u"Traceur 1"
                     }],
                'physic': [],
                'meteo': False
            }
        }

    def default_tab_phy(self):

        list_var_phy = []
        list_var_name = []
        id = 1
        id1 = 1
        for key in self.dico_phy:
            for item in self.dico_phy[key]['physic']:
                if item:
                    list_var_phy.append([id, key,
                                         item['sigle'],
                                         item['value'],
                                         item['text'],
                                         item['textfr']
                                         ])
                    id += 1

            for item in self.dico_phy[key]['tracer']:
                list_var_name.append([id1, key,
                                      item['sigle'],
                                      item['text'], item['textfr'], True, True])
                id1 += 1

        liste_col = self.mdb.list_columns('tracer_physic')
        var = ",".join(liste_col)
        valeurs = "("
        for k in liste_col:
            valeurs += '%s,'
        valeurs = valeurs[:-1] + ")"
        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                            'tracer_physic',
                                                            var,
                                                            valeurs)
        self.mdb.run_query(sql, many=True, list_many=list_var_phy)

        liste_col = self.mdb.list_columns('tracer_name')
        var = ",".join(liste_col)
        valeurs = "("
        for k in liste_col:
            valeurs += '%s,'
        valeurs = valeurs[:-1] + ")"
        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.mdb.SCHEMA,
                                                            'tracer_name',
                                                            var,
                                                            valeurs)
        self.mdb.run_query(sql, many=True, list_many=list_var_name)
