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
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

"""
from xml.etree.ElementTree import SubElement

from lib.model.utils_model_file import fmt, check_none
from lib.Function import del_symbol
from lib.Function import str2bool


def add_wq_xcas(mdb, fichier_cas, noyau, dict_libres, mess=None):
    """
    Modify xcas for Water Quality (WQ) parameters.
    :param fichier_cas (ElementTree): XML tree
    :param noyau (str): Kernel name
    :param dict_libres (dict): Dictionary of free extremities
    :return: (bool) True if successful, False otherwise
    """
    # requête pour récupérer les paramètres

    cas = fichier_cas.find("parametresCas")
    sql = (
        "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} "
        "WHERE gui_type = 'tracers' ORDER BY id;"
    )

    rows = mdb.run_query(sql.format(noyau, mdb.SCHEMA, "parametres"), fetch=True)

    for param, valeur, b1, b2 in rows:
        if param == "fichMeteoTracer":
            sql = "SELECT {0} FROM {1}.{2} WHERE parametre = 'fichmeteo' ;"
            wow = mdb.run_query(
                sql.format(noyau, mdb.SCHEMA, "parametres"), fetch=True
            )
            if str2bool(wow[0][0]) is False:
                continue

        if b1:
            try:
                cas.find(b1).text
            except Exception:
                balise1 = SubElement(cas, b1)
            if b2:
                try:
                    balise1.find(b2).text
                except Exception:
                    balise2 = SubElement(balise1, b2)

                par = SubElement(balise2, param)

                par.text = valeur.lower()
            else:
                par = SubElement(balise1, param)
                par.text = valeur.lower()

    # use dictLibres to have only extremities and not junction

    cas = cas.find("parametresTraceur")
    lateral = mdb.select("tracer_lateral_inflows", order="abscissa")

    list_loi = list(dict_libres["law_wq"])
    dico_s = {}
    dico_ex = {}

    for i, nom in enumerate(list_loi):
        dico_ex[i] = {"name": nom, "type": dict_libres["typeCond_tr"][i]}

    for i, cond in enumerate(lateral["active"]):
        if cond:
            dico_s[i] = {
                "name": lateral["name"][i],
                "name_law": lateral["law_wq"][i],
                "typs": lateral["typesources"][i],
                "numb": lateral["branchnum"][i],
                "abs": lateral["abscissa"][i],
                "leng": lateral["length"][i],
            }
            list_loi.append(lateral["law_wq"][i])
    if not len(list_loi) > 0:
        txt = "Please enter water quality laws"
        if mess:
            mess.add_mess("WQLoi", "critic", txt)
        return False
    list_loi = list(set(list_loi))
    list_loi = sorted(list_loi)

    # sources
    tracer_source = SubElement(cas, "parametresSourcesTraceur")
    nb = len(list(dico_s.keys()))
    SubElement(tracer_source, "nbSources").text = str(nb)
    struct = SubElement(tracer_source, "noms")
    typ = []
    numb = []
    abs = []
    leng = []
    numl = []
    if nb > 0:
        for num in sorted(list(dico_s.keys())):
            SubElement(struct, "string").text = dico_s[num]["name"]
            typ.append(dico_s[num]["typs"])
            numb.append(dico_s[num]["numb"])
            abs.append(dico_s[num]["abs"])
            leng.append(dico_s[num]["leng"])
            numl.append(list_loi.index(dico_s[num]["name_law"]) + 1)
    else:
        typ = ["-0"]
        numb = ["-0"]
        abs = ["-0"]
        leng = ["-0"]
        numl = ["-0"]
    SubElement(tracer_source, "typeSources").text = fmt(typ)
    SubElement(tracer_source, "numBranche").text = fmt(numb)
    if check_none(abs) and mess:
        txt = "Geometric object for tracer lateral inflows " "is not found"
        mess.add_mess("WQGeoLatInflow", "warning", txt)
    SubElement(tracer_source, "abscisses").text = fmt(abs)
    if check_none(leng) and mess:
        txt = "Warning : Lenght for tracer lateral inflows is not found"
        mess.add_mess("WQLenghtLatInflow", "warning", txt)
    SubElement(tracer_source, "longueurs").text = fmt(leng)
    SubElement(tracer_source, "numLoi").text = fmt(numl)

    # Lois traceur
    tracer_law = SubElement(cas, "parametresLoisTraceur")
    nb = len(list_loi)
    SubElement(tracer_law, "nbLoisTracer").text = str(nb)
    lois = SubElement(tracer_law, "loisTracer")
    if nb > 0:
        for name in list_loi:
            try:
                struct = SubElement(lois, "structureSParametresLoiTraceur")
                SubElement(struct, "nom").text = name
                SubElement(struct, "modeEntree").text = "1"
                SubElement(struct, "fichier").text = "{}_tra.loi".format(
                    del_symbol(name.lower())
                )
                SubElement(struct, "uniteTps").text = "-0"
                SubElement(struct, "nbPoints").text = "-0"
            except Exception as err:
                if mess:
                    mess.add_mess("WQLoi2", "critic", f"Check  water quality laws (extremities,inflows)\n{err}")
                return False

    # modif extremite info
    typ = [0, 0]
    numl = [0, 0]
    list_k = list(dico_ex.keys())
    if len(list_k):
        for i, num in enumerate(sorted(list_k)):
            typ[i] = dico_ex[num]["type"]
            numl[i] = list_loi.index(dico_ex[num]["name"]) + 1
    else:
        typ = ["-0"]
        numl = ["-0"]
    general = fichier_cas.find("parametresCas")
    cas = general.find("parametresTraceur")
    initiales = cas.find("parametresConditionsLimitesTraceur")
    initiales.find("typeCondLimTracer").text = fmt(typ)
    initiales.find("numLoiCondLimTracer").text = fmt(numl)

    return True
