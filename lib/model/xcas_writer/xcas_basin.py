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
from xml.etree.ElementTree import SubElement

from lib.model.utils_model_file import fmt_sans_none


def fmt_plani_casier(liste, mess=None):
    """
    Calculate the planimetry between two levels of the surface law.
    :param liste (list): List of level strings
    :param mess: Optional message handler object.
    :return: (str) Space-separated string
    """

    # volume du casier
    liste_plani = []
    for chaine_z in liste:
        try:
            liste_z = chaine_z.split()
            # Calcul des parties entieres et decimale de la planimetrie
            plani_entier = int((float(liste_z[1]) - float(liste_z[0])) // 1)
            liste_plani.append(str(plani_entier))
            plani_decimale = int((float(liste_z[1]) - float(liste_z[0])) % 1)
            if plani_decimale > 0 and mess:
                txt = "Simulation Error: the basin planimetry has " "to be an integer value"
                mess.add_mess("CreatBasinPlani", "critic", txt)
        except Exception:
            txt = "Simulation Error: the basin planimetry is not correct"
            if mess:
                mess.add_mess("CreatBasinPlani", "critic", txt)
    return " ".join([str(var) for var in liste_plani])


def fmt_num_basin(liste, dico_num, remplace_none, mess=None):
    """
    Transform a list of basin/link numbers using a mapping dictionary.
    :param liste (list): List of QGIS numbers
    :param dico_num (dict): Mapping from QGIS to Mascaret numbers
    :param remplace_none (any): Value to replace None
    :param mess: Optional message handler object.
    :return: (str) Space-separated string
    """
    # Qgis en une chaine de numeros pour le moteur Mascaret
    liste_num_masca = []
    for num_qgis in liste:
        if num_qgis is None:
            # Ajout d'une valeur nulle codee ici par remplaceNone, cad -1
            # ou -1.0, pour le moteur mascaret
            liste_num_masca.append(remplace_none)
        else:
            # Inversion du dictionnaire: on cherche le numero mascaret
            # pour le numero de casier sous Qgis
            try:
                liste_num_masca.append(dico_num[num_qgis])
            except KeyError:
                txterr = "Error, the basin {} does not exist".format(num_qgis)
                if mess:
                    mess.add_mess("CreatBasinNoNum", "critic", txterr)
    return " ".join([str(var) for var in liste_num_masca])


def check_basin(liaisons, casiers, dico_basinnum, mess=None):
    """
    Check if links and basins are correctly defined.
    :param liaisons (dict): Link data
    :param casiers (dict): Basin data
    :param dico_basinnum (dict): Mapping of basin numbers
    :return: None
    """
    for idc, num in enumerate(casiers["basinnum"]):
        if float(casiers["initlevel"][idc]) < min(
                [float(val) for val in casiers["level"][idc].split()]
        ) and mess:
            txte = (
                '*** Error: The "Reference level" for the basins {} '
                "which must be greater than or equal to "
                "the minimum level of the height volume law".format(num)
            )
            mess.add_mess("BasinErr_{}".format(num), "critic", txte)

    check_typ_link = {
        1: ["level", "width", "weirdischargecoef"],
        2: ["level", "width", "length", "roughness"],
        3: ["level", "length", "crosssection", "headlosscoef"],
        4: [
            "level",
            "width",
            "crosssection",
            "weirdischargecoef",
            "pipedischargecoef",
            "culverttype",
        ],
    }
    for idl, num in enumerate(liaisons["linknum"]):
        nat = liaisons["nature"][idl]
        tupl = liaisons["type"][idl]
        abs = liaisons["abscissa"][idl]
        stb = liaisons["basinstart"][idl]
        level = liaisons["level"][idl]
        ste = liaisons["basinend"][idl]
        # check "Basin-Reach" have an abscissa
        if nat == 1 and (abs is None or abs == -1) and mess:
            txte = (
                '*** Error: The "Basin-Reach" type link {} '
                "does not have an abscissa on the reach".format(num)
            )
            mess.add_mess("LinkBR_{}".format(num), "critic", txte)
        # check coherent between variable and typ
        for key in check_typ_link[tupl]:
            val = liaisons[key][idl]
            if val is None:
                txte = "*** Error: Link {} is not type coherent.".format(num)
                if mess:
                    mess.add_mess("LinkErr_{}".format(num), "critic", txte)
                break

        # check level for the start basin
        if stb in dico_basinnum.keys():
            numc = casiers["basinnum"][dico_basinnum[stb] - 1]
            init_level = casiers["initlevel"][dico_basinnum[stb] - 1]
            if level < init_level and mess:
                txtw = (
                    "*** Warning: Please note that the elevation of "
                    "the upstream basin {} is higher than the elevation of the link {}. \n"
                    "This can generate an artificial flow.".format(numc, num)
                )
                mess.add_mess("Links_{}_{}".format(numc, num), "warning", txtw)
        else:
            txte = "*** Error: The link {} " 'does not have "Basin number start"'.format(num)
            if mess:
                mess.add_mess("LinksB_{}".format(num), "critic", txte)
        # check if "basinend" is existed  before  check level
        if ste is None or ste == -1:
            continue
        # check level for the end basin
        if ste in dico_basinnum.keys():
            # -1 because of Python begin by 0
            numc = casiers["basinnum"][dico_basinnum[ste] - 1]
            init_level = casiers["initlevel"][dico_basinnum[ste] - 1]
            if level < init_level and mess:
                txtw = (
                    "*** Warning: Please note that the elevation of "
                    "the downtream basin {} is higher than the elevation of the link {}. \n"
                    "This can generate an artificial flow.".format(numc, num)
                )
                mess.add_mess("Links1_{}_{}".format(numc, num), "warning", txtw)

        else:
            txte = "*** Error: The link {} " 'does not have "Basin number End"'.format(num)
            if mess:
                mess.add_mess("LinksB1_{}".format(num), "critic", txte)


def add_basin_xcas(fichier_cas, casiers, liaisons, name_geo_casier='mascaret.casier', mess=None):
    """
    Add basin and link information to the xcas XML structure.
    :param fichier_cas (ElementTree): XML tree
    :param casiers (dict): Basin data
    :param liaisons (dict): Link data
    :return: None
    """
    # Creation du dictionnaire de numero de casier entre mascaret (cle)
    # et qgis (valeur)
    dico_basinnum = {}
    dico_basinnum_creat = {}
    for id_mas, num_qgis in enumerate(casiers["basinnum"], 1):
        dico_basinnum[id_mas] = num_qgis
        dico_basinnum_creat[num_qgis] = id_mas
    # # Creation du dictionnaire de numero de liaison entre mascaret (cle)
    # # et qgis (valeur)
    dico_linknum = {}
    for id_mas, num_qgis in enumerate(liaisons["linknum"], 1):
        dico_linknum[id_mas] = num_qgis
    check_basin(liaisons, casiers, dico_basinnum_creat)
    # Creation des lignes a ajouter dans Xcas
    cas = fichier_cas.find("parametresCas")
    casier = SubElement(cas, "parametresCasier")
    SubElement(casier, "nbCasiers").text = str(len(casiers["name"]))
    SubElement(casier, "optionPlanimetrage").text = fmt_plani_casier(casiers["level"], mess)
    SubElement(casier, "optionCalcul").text = "1"
    SubElement(casier, "fichierGeomCasiers").text = name_geo_casier
    SubElement(casier, "cotesInitiale").text = fmt_sans_none(casiers["initlevel"], "-1.0")
    # Liaisons (champs non listes = active et linknum)
    et_liaisons = SubElement(casier, "liaisons")
    SubElement(et_liaisons, "nbLiaisons").text = str(len(liaisons["name"]))
    SubElement(et_liaisons, "types").text = fmt_sans_none(liaisons["type"], "-1.0")
    SubElement(et_liaisons, "nature").text = fmt_sans_none(liaisons["nature"], "-1.0")
    SubElement(et_liaisons, "cote").text = fmt_sans_none(liaisons["level"], "-1.0")
    SubElement(et_liaisons, "largeur").text = fmt_sans_none(liaisons["width"], "-1.0")
    SubElement(et_liaisons, "longueur").text = fmt_sans_none(liaisons["length"], "-1.0")
    SubElement(et_liaisons, "rugosite").text = fmt_sans_none(liaisons["roughness"], "-1.0")
    SubElement(et_liaisons, "section").text = fmt_sans_none(
        liaisons["crosssection"], "-1.0"
    )
    SubElement(et_liaisons, "coefPerteCharge").text = fmt_sans_none(
        liaisons["headlosscoef"], "-1.0"
    )
    SubElement(et_liaisons, "coefDebitSeuil").text = fmt_sans_none(
        liaisons["weirdischargecoef"], "-1.0"
    )
    SubElement(et_liaisons, "coefActivation").text = fmt_sans_none(
        liaisons["activationcoef"], "-1.0"
    )
    SubElement(et_liaisons, "coefDebitOrifice").text = fmt_sans_none(
        liaisons["pipedischargecoef"], "-1.0"
    )
    SubElement(et_liaisons, "typeOrifice").text = fmt_sans_none(
        liaisons["culverttype"], "-1"
    )
    SubElement(et_liaisons, "numCasierOrigine").text = fmt_num_basin(
        liaisons["basinstart"], dico_basinnum_creat, "-1", mess
    )
    SubElement(et_liaisons, "numCasierFin").text = fmt_num_basin(
        liaisons["basinend"], dico_basinnum_creat, "-1", mess
    )
    SubElement(et_liaisons, "numBiefAssocie").text = fmt_sans_none(
        liaisons["branchnum"], "-1"
    )
    SubElement(et_liaisons, "abscBief").text = fmt_sans_none(liaisons["abscissa"], "-1.0")

    return dico_basinnum, dico_linknum
