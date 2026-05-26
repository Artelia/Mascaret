# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : October,2025
copyright            : (C) 2017 by Artelia
email                :
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

"""
import pandas as pd

from ...Function import del_accent
from ..Fct_model_file import typ_struct


def modif_seuil(mdb, seuil, dico_str):
    """
    Modify weir (seuil) data with structure configuration.
    :param seuil (dict): Weir data
    :param dico_str (dict): Structure configuration
    :param mdb: Database object providing select method.
    :return: (dict, dict) seuil, loi_struct
    """
    liste = [
        "type",
        "branchnum",
        "abscissa",
        "z_crest",
        "z_average_crest",
        "z_break",
        "flowratecoeff",
        "wide_floodgate",
        "thickness",
    ]
    loi_struct = {"laws": [], "id_config": []}
    if len(seuil["name"]) == 0:
        seuils = {
            "name": [],
        }
        for ls in liste:
            seuils[ls] = []

    for i, name in enumerate(dico_str["name"]):
        seuil["name"].append(del_accent(name))
        loi_struct["laws"].append(del_accent(name))
        loi_struct["id_config"].append(dico_str["id"][i])
        for ls in liste:
            if ls == "type":
                seuil[ls].append(typ_struct(dico_str["method"][i]))
            elif ls == "abscissa":
                seuil[ls].append(dico_str["abscissa"][i])
            elif ls == "branchnum":
                seuil[ls].append(dico_str["branchnum"][i])
            elif ls == "z_break":
                if "zbreak" in dico_str:
                    seuil[ls].append(dico_str["zbreak"][i])
                else:
                    seuil[ls].append(99999)
            elif ls == "z_crest":
                where = "id_config ='{}'".format(dico_str["id"][i])
                zmin = mdb.select_min("z", "profil_struct", where)
                seuil[ls].append(zmin)
            else:
                seuil[ls].append(None)
    if any(seuil["active_mob"]):
        rows = mdb.run_query(
            "SELECT id_weirs, name_var, value FROM {schema}.weirs_mob_val "
            "WHERE id_weirs IN (SELECT gid FROM {schema}.weirs WHERE active_mob)",
            fetch=True,
            schema=True,
        )
        dico_mob = {"id_weirs": [], "name_var": [], "value": []}
        for id_weirs, name_var, value in rows:
            dico_mob["id_weirs"].append(id_weirs)
            dico_mob["name_var"].append(name_var)
            dico_mob["value"].append(value)
        for id_w in dico_mob["id_weirs"]:
            try:
                id_s = seuil["gid"].index(id_w)
                id_n = dico_mob["name_var"].index("ZINITREG")
                seuil["z_crest"][id_s] = dico_mob["value"][id_n]
            except ValueError:
                continue
    return seuil, loi_struct


def modif_link(mdb, liaisons):
    """
    Modification of dictionaries used to create in the Xcas file
    - Modify the initial levels of links when mobile links
    :param liaisons:
    :param mdb: Database object providing select method.
    :return:
    """
    rows = mdb.run_query(
        "SELECT id_links, name_var, value FROM {schema}.links_mob_val "
        "WHERE id_links IN (SELECT gid FROM {schema}.links WHERE active_mob)",
        fetch=True,
        schema=True,
    )
    if not rows:
        return liaisons
    dico_mob = {"id_links": [], "name_var": [], "value": []}
    for id_links, name_var, value in rows:
        dico_mob["id_links"].append(id_links)
        dico_mob["name_var"].append(name_var)
        dico_mob["value"].append(value)
    lst_gid = {"id_links": sorted(set(dico_mob["id_links"]))}
    df_mob = pd.DataFrame(dico_mob)
    for id_lk in lst_gid["id_links"]:
        try:
            id_s = liaisons["gid"].index(id_lk)
            valeur = df_mob[(df_mob["id_links"] == id_lk) & (df_mob["name_var"] == "ZINITREG")][
                "value"
            ].tolist()
            if valeur:
                valeur = valeur[0]
                lvl0 = liaisons["level"][id_s]
                liaisons["level"][id_s] = float(valeur)
                if liaisons["type"][id_s] == 4:
                    htop = liaisons["crosssection"][id_s] / liaisons["width"][id_s]
                    newsec = max(
                        liaisons["width"][id_s] * (htop - max(liaisons["level"][id_s] - lvl0, 0)),
                        1e-4,
                    )
                    liaisons["crosssection"][id_s] = newsec
        except ValueError:
            continue
    return liaisons
