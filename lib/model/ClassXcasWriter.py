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
import os
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as et_parse

from lib.Function import del_symbol
from lib.Function import str2bool
from lib.model.Fct_model_file import (
    fmt,
    check_none,
    indent,
    backup_file)
from lib.model.xcas_writer.xcas_basin import add_basin_xcas
from lib.model.xcas_writer.xcas_seuil_link_mob import modif_seuil, modif_link
from lib.model.xcas_writer.xcas_wq import add_wq_xcas


class ClassXcasWriter:

    XCAS_FILE = "mascaret.xcas"

    def __init__(self, mdb, folder, cond_api, mess=None):
        """
        :param mdb: Database object providing select method.
        :param folder: Path to the output folder.
        :param mess: Optional message handler object.
        """

        self.mdb = mdb
        self.folder = folder
        self.mess = mess
        self.cond_api = cond_api
        self.dico_basinnum = {}
        self.dico_linknum = {}
        self.elem_xcas = None
        self.dico_loi = None
        self.dico_loi_struct = None

    def creer_xcas(self, noyau, filename=None, up_param=None):
        """
        Create the xcas file for the model.
        :param noyau (str): Kernel name
        :param filename: Name of the geometry file.
        :param up_param (dict): Optional parameters modifier
        :return: (dict, dict) dict_lois, dico_loi_struct
        """
        if not filename:
            filename = self.XCAS_FILE
        dict_lois = {}
        # try:
        fichier_sortie = os.path.join(self.folder, filename)
        backup_file(fichier_sortie, ".xcas")
        extr_toloi = {0: 6, 1: 1, 2: 2, 3: 4, 4: 5, 5: 4, 8: 3, 6: 6, 7: 7}
        abaque_toloi = {1: 6, 2: 4, 5: 2, 6: 5, 7: 5, 8: 7}

        # création du fichier xml
        fichier_cas = Element("fichier_cas")

        cas = SubElement(fichier_cas, "parametresCas")

        sql = "SELECT {0} FROM {1}.{2} WHERE parametre='presenceTraceurs';"
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        if rows is not None:
            tracer = str2bool(rows[0][0])
        else:
            tracer = False
        # requête pour récupérer les paramètres
        sql = (
            "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} "
            "WHERE gui_type = 'parameters' ORDER BY id;"
        )
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, b1, b2 in rows:
            # print("valeur : {0},  param : {1}  ,  b1 : {2} , b2:#\
            #  {3}".format(valeur, param, b1, b2))
            if up_param:
                if param in up_param.keys():
                    valeur = str(up_param[param])
            if b1:
                try:
                    cas.find(b1).text
                except Exception:
                    balise1 = SubElement(cas, b1)
                # if not cas.find(b1):
                #     balise1 = SubElement(cas, b1)

                if b2:
                    try:
                        balise1.find(b2).text
                    except Exception:
                        balise2 = SubElement(balise1, b2)
                    # if not balise1.find(b2):
                    #     balise2 = SubElement(balise1, b2)
                    par = SubElement(balise2, param)

                    par.text = valeur.lower()
                else:
                    par = SubElement(balise1, param)
                    par.text = valeur.lower()
        # requete sur les couches
        apports = self.mdb.select("lateral_inflows", "active", "abscissa")
        var = "branch, startb, endb"
        branches = self.mdb.select_distinct(var, "branchs", "active")
        deversoirs = self.mdb.select("lateral_weirs", "active", "abscissa")
        noeuds = self.mdb.select("extremities", "type=10  and active")
        libres = self.mdb.select("extremities", "type!=10 and active")
        pertescharg = self.mdb.select("hydraulic_head", "active", "abscissa")
        profils = self.mdb.select("profiles", "active", "abscissa")
        prof_seuil = self.mdb.select("profiles", "NOT active", "abscissa")
        seuils = self.mdb.select("weirs", "active", "abscissa")
        sorties = self.mdb.select("outputs", "active", "abscissa")
        zones = self.mdb.zone_ks()
        planim = self.mdb.planim_select()
        maillage = self.mdb.maillage_select()
        dico_str = self.mdb.select("struct_config", "active", "abscissa")
        seuils, loi_struct = modif_seuil(self.mdb, seuils, dico_str)
        casiers = self.mdb.select("basins", "active ORDER BY basinnum ")
        liaisons = self.mdb.select("links", "active ORDER BY linknum ")
        if any(liaisons['active_mob']) and self.cond_api:
            liaisons = modif_link(self.mdb, liaisons)

        # Extrémités
        numero = branches["branch"]
        branches["abscdebut"] = []
        branches["abscfin"] = []

        liste = list(zip(profils["abscissa"], profils["branchnum"]))
        for i, num in enumerate(numero):
            temp = [a for a, n in liste if n == num]
            if temp:
                branches["abscdebut"].append(min(temp))
                branches["abscfin"].append(max(temp))
            else:
                if self.mess:
                    self.mess.add_mess("CheckProf", "warning", "Checked if the profiles are activated.")

        dict_noeuds = {}
        dict_libres = {
            "nom": [],
            "num": [],
            "extrem": [],
            "typeCond": [],
            "typeCond_tr": [],
            "law_wq": [],
        }
        # 'law_wq','active','tracer_boundary_condition_type',num
        for n, d, f in zip(numero, branches["startb"], branches["endb"]):
            if noeuds and d in noeuds["name"]:
                if d not in dict_noeuds.keys():
                    dict_noeuds[d] = []
                dict_noeuds[d].append(n * 2 - 1)

            if noeuds and f in noeuds["name"]:
                if f not in dict_noeuds.keys():
                    dict_noeuds[f] = []
                dict_noeuds[f].append(n * 2)
            if libres and d in libres["name"]:
                i = libres["name"].index(d)
                type = libres["type"][i]
                formule = libres["method"][i]
                dict_libres["nom"].append(libres["name"][i])
                dict_libres["typeCond"].append(type)
                dict_libres["num"].append(len(dict_libres["nom"]))
                dict_libres["extrem"].append(n * 2 - 1)
                dict_libres["typeCond_tr"].append(libres["tracer_boundary_condition_type"][i])
                dict_libres["law_wq"].append(libres["law_wq"][i])

                dict_lois[d] = {
                    "type": extr_toloi[type],
                    "formule": formule,
                    "valeurperm": libres["firstvalue"][i],
                    "couche": "extremites",
                }

            if libres and f in libres["name"]:
                i = libres["name"].index(f)
                type = libres["type"][i]
                formule = libres["method"][i]
                dict_libres["nom"].append(libres["name"][i])
                dict_libres["typeCond"].append(type)
                dict_libres["num"].append(len(dict_libres["nom"]))
                dict_libres["extrem"].append(n * 2)
                dict_libres["typeCond_tr"].append(libres["tracer_boundary_condition_type"][i])
                dict_libres["law_wq"].append(libres["law_wq"][i])
                dict_lois[f] = {
                    "type": extr_toloi[type],
                    "formule": formule,
                    "valeurperm": libres["firstvalue"][i],
                    "couche": "extremites",
                }
        # Zones
        nb_pas = 0

        liste_stock = {"numProfil": [], "limGauchLitMaj": [], "limDroitLitMaj": []}

        tab = zip(
            profils["abscissa"],
            profils["x"],
            profils["z"],
            profils["leftstock"],
            profils["rightstock"],
            profils["branchnum"],
            profils["planim"],
        )

        for j, (abs, x, z, sg, sd, n, planim_val) in enumerate(tab):
            try:
                xx = [float(var) for var in x.split()]
                zz = [float(var) for var in z.split()]
                diff = max(zz) - min(zz)
            except Exception:
                if self.mess:
                    self.mess.add_mess("CheckProf1", "critic",
                                       "Check the {} profile if it's ok ".format(profils["name"][j]))
                return dict_lois

            try:
                nb_pas = max(int(diff / float(planim_val)) + 1, nb_pas)
            except Exception:
                if self.mess:
                    self.mess.add_mess(
                        "CheckPlani_{}".format(str(j)), "warning", "Check planim abs:{}".format(abs)
                    )

            if sg or sd:
                if sg:
                    lim_gauch_lit_maj = sg
                else:
                    lim_gauch_lit_maj = min(xx)

                if sd:
                    lim_droit_lit_maj = sd
                else:
                    lim_droit_lit_maj = max(xx)

                liste_stock["numProfil"].append(j + 1)
                liste_stock["limGauchLitMaj"].append(lim_gauch_lit_maj)
                liste_stock["limDroitLitMaj"].append(lim_droit_lit_maj)

        for i, type in enumerate(seuils["type"]):
            if type not in (3, 4):
                dict_lois[seuils["name"][i]] = {"type": abaque_toloi[type], "couche": "seuils"}

        for i, nom in enumerate(apports["name"]):
            if nom not in dict_lois.keys():
                dict_lois[nom] = {
                    "type": 1,
                    "formule": apports["method"][i],
                    "valeurperm": apports["firstvalue"][i],
                    "couche": "apports",
                }

        for i, nom in enumerate(deversoirs["name"]):
            if nom not in dict_lois.keys() and deversoirs["type"][i] == 2:
                dict_lois[nom] = {"type": 4, "couche": "deversoirs"}

        # Géométrie du réseau
        reseau = cas.find("parametresGeometrieReseau")
        # liste des Branches
        liste_branch = SubElement(reseau, "listeBranches")
        SubElement(liste_branch, "nb").text = str(len(numero))
        SubElement(liste_branch, "numeros").text = fmt(numero)
        SubElement(liste_branch, "abscDebut").text = fmt(branches["abscdebut"])
        SubElement(liste_branch, "abscFin").text = fmt(branches["abscfin"])
        extrem_debut = [i * 2 - 1 for i in numero]
        SubElement(liste_branch, "numExtremDebut").text = fmt(extrem_debut)
        extrem_fin = [i * 2 for i in numero]
        SubElement(liste_branch, "numExtremFin").text = fmt(extrem_fin)

        # liste des Noeuds
        liste_noeuds = SubElement(reseau, "listeNoeuds")

        SubElement(liste_noeuds, "nb").text = str(len(dict_noeuds.keys()))
        e_tnoeuds = SubElement(liste_noeuds, "noeuds")
        for k in sorted(dict_noeuds.keys()):
            noeud = SubElement(e_tnoeuds, "noeud")
            temp = dict_noeuds[k] + [0] * (5 - len(dict_noeuds[k]))
            SubElement(noeud, "num").text = fmt(temp)

        # liste des extrémités libres
        extr_libres = SubElement(reseau, "extrLibres")
        liste = dict_libres["nom"]
        SubElement(extr_libres, "nb").text = str(len(liste))
        SubElement(extr_libres, "num").text = fmt(dict_libres["num"])
        SubElement(extr_libres, "numExtrem").text = fmt(dict_libres["extrem"])

        noms = SubElement(extr_libres, "noms")
        for nom in liste:
            SubElement(noms, "string").text = nom

        SubElement(extr_libres, "typeCond").text = fmt(dict_libres["typeCond"])
        # temp=[]
        # for nom in liste:
        #     if nom in libres["name"] and (dictLois[nom]['type'] == 6 \
        #                   or dictLois[nom]['type'] == 7):
        #             temp.append(1)
        #     else:
        #             temp.append(sorted(dictLois.keys()).index(nom) + 1)

        temp = [sorted(dict_lois.keys()).index(nom) + 1 for nom in liste]
        SubElement(extr_libres, "numLoi").text = fmt(temp)

        # Confluents
        confluents = SubElement(cas, "parametresConfluents")
        SubElement(confluents, "nbConfluents").text = str(len(dict_noeuds.keys()))
        confluent = SubElement(confluents, "confluents")
        for k in sorted(dict_noeuds.keys()):
            struct = SubElement(confluent, "structureParametresConfluent")
            len_n = len(dict_noeuds[k])
            SubElement(struct, "nbAffluent").text = str(len_n)
            SubElement(struct, "nom").text = k
            i = noeuds["name"].index(k)
            a_en = ["abscissa", "ordinates", "angles"]
            for kk, a in enumerate(["abscisses", "ordonnees", "angles"]):
                if noeuds[a_en[kk]][i] is None or len_n != 3:
                    SubElement(struct, a).text = " 0.0" * len_n
                else:
                    SubElement(struct, a).text = noeuds[a_en[kk]][i]

        # Planimétrage et maillage
        planimaill = SubElement(cas, "parametresPlanimetrageMaillage")
        SubElement(planimaill, "methodeMaillage").text = "5"

        planim_e = SubElement(planimaill, "planim")
        SubElement(planim_e, "nbPas").text = str(nb_pas)
        SubElement(planim_e, "nbZones").text = str(len(planim["pas"]))
        SubElement(planim_e, "valeursPas").text = fmt(planim["pas"])
        SubElement(planim_e, "num1erProf").text = fmt(planim["min"])
        SubElement(planim_e, "numDerProf").text = fmt(planim["max"])

        maillage_e = SubElement(planimaill, "maillage")
        SubElement(maillage_e, "modeSaisie").text = "2"
        SubElement(maillage_e, "sauvMaillage").text = "false"
        maillage_c = SubElement(maillage_e, "maillageClavier")
        SubElement(maillage_c, "nbSections").text = "0"
        SubElement(maillage_c, "nbPlages").text = str(len(maillage["pas"]))
        SubElement(maillage_c, "num1erProfPlage").text = fmt(maillage["min"])
        SubElement(maillage_c, "numDerProfPlage").text = fmt(maillage["max"])
        SubElement(maillage_c, "pasEspacePlage").text = fmt(maillage["pas"])
        SubElement(maillage_c, "nbZones").text = "0"

        # Singularites
        singularite = SubElement(cas, "parametresSingularite")

        # Seuils
        SubElement(singularite, "nbSeuils").text = str(len(seuils["name"]))

        if len(seuils["name"]) > 0:
            e_tseuils = SubElement(singularite, "seuils")

        liste = [
            "type",
            "numBranche",
            "abscisse",
            "coteCrete",
            "coteCreteMoy",
            "coteRupture",
            "coeffDebit",
            "largVanne",
            "epaisseur",
        ]
        liste_en = [
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

        for i, nom in enumerate(seuils["name"]):
            struct = SubElement(e_tseuils, "structureParametresSeuil")
            SubElement(struct, "nom").text = nom
            for kk, len_n in enumerate(liste):
                if seuils[liste_en[kk].lower()][i] is None:
                    SubElement(struct, len_n).text = "-0"
                else:
                    SubElement(struct, len_n).text = str(seuils[liste_en[kk].lower()][i])

            if seuils["type"][i] not in (3, 4):
                SubElement(struct, "numLoi").text = str(sorted(dict_lois.keys()).index(nom) + 1)
            else:
                SubElement(struct, "numLoi").text = "-0"

            if seuils["type"][i] != 3:
                SubElement(struct, "nbPtLoiSeuil").text = "-0"
            else:
                try:
                    i = prof_seuil["name"].index(nom)
                    long = len(prof_seuil["x"][i].split())
                    SubElement(struct, "nbPtLoiSeuil").text = str(long)
                    # SubElement(struct, "abscTravCrete").text = prof_seuil['x'][i]
                    # SubElement(struct, "cotesCrete").text = prof_seuil['z'][i]
                    # traitment profil because of too many significant number
                    new_profx = " ".join(
                        [str(round(float(vvv), 3)) for vvv in prof_seuil["x"][i].split()]
                    )
                    SubElement(struct, "abscTravCrete").text = new_profx
                    new_profz = " ".join(
                        [str(round(float(vvv), 3)) for vvv in prof_seuil["z"][i].split()]
                    )
                    SubElement(struct, "cotesCrete").text = new_profz

                except Exception:
                    if self.mess:
                        self.mess.add_mess("CheckProfCret", "warning", f"Profil de crete introuvable pour {nom}")
                    return

            SubElement(struct, "gradient").text = "-0"

        # Pertes de charges
        if len(pertescharg["name"]) > 0:
            pertes = SubElement(singularite, "pertesCharges")
            SubElement(pertes, "nbPerteCharge").text = str(len(pertescharg["name"]))
            SubElement(pertes, "numBranche").text = fmt(pertescharg["branchnum"])
            SubElement(pertes, "abscisses").text = fmt(pertescharg["abscissa"])
            SubElement(pertes, "coefficients").text = fmt(pertescharg["coeff"])

        # Casiers et liaisons
        if len(casiers["name"]) > 0:
            self.dico_basinnum, self.dico_linknum = (
                add_basin_xcas(fichier_cas, casiers, liaisons, mess=self.mess))
        # Apports et déversoirs
        apport_dever = SubElement(cas, "parametresApportDeversoirs")
        # Apports
        e_tapports = SubElement(apport_dever, "debitsApports")
        SubElement(e_tapports, "nbQApport").text = str(len(apports["name"]))
        noms = SubElement(e_tapports, "noms")
        for nom in apports["name"]:
            SubElement(noms, "string").text = nom

        SubElement(e_tapports, "numBranche").text = fmt(apports["branchnum"])
        if check_none(apports["abscissa"]) and self.mess:
            self.mess.add_mess(
                "LatInflowAbs", "warning", "Geometric object for lateral inflows is not found"
            )
        SubElement(e_tapports, "abscisses").text = fmt(apports["abscissa"])
        if check_none(apports["length"]) and self.mess:
            self.mess.add_mess("LatInflowLen", "warning", "Lenght for lateral inflows is not found")
        SubElement(e_tapports, "longueurs").text = fmt(apports["length"])
        temp = [sorted(dict_lois.keys()).index(nom) + 1 for nom in apports["name"]]
        SubElement(e_tapports, "numLoi").text = fmt(temp)

        # Déversoirs
        devers_late = SubElement(apport_dever, "devers_late")
        SubElement(devers_late, "nbDeversoirs").text = str(len(deversoirs["name"]))
        noms = SubElement(devers_late, "noms")
        for nom in deversoirs["name"]:
            SubElement(noms, "string").text = nom

        SubElement(devers_late, "type").text = fmt(deversoirs["type"])

        l_en = ["branchnum", "abscissa", "length", "z_crest", "flowratecoef"]
        for kk, len_n in enumerate(
                ["numBranche", "abscisse", "longueur", "coteCrete", "coeffDebit"]
        ):
            SubElement(devers_late, len_n).text = fmt(deversoirs[l_en[kk].lower()])

        temp = []
        for nom in deversoirs["name"]:
            if nom in dict_lois.keys():
                temp.append(sorted(dict_lois.keys()).index(nom) + 1)
            else:
                temp.append(0)
        SubElement(devers_late, "numLoi").text = fmt(temp)

        # Calage
        calage = SubElement(cas, "parametresCalage")

        # frottement
        frottement = SubElement(calage, "frottement")
        SubElement(frottement, "loi").text = "1"
        SubElement(frottement, "nbZone").text = str(len(zones["zoneabsstart"]))
        SubElement(frottement, "numBranche").text = fmt(zones["branch"])
        l_en = ["zoneabsstart", "zoneabsend", "minbedcoef", "majbedcoef"]
        for kk, len_n in enumerate(["absDebZone", "absFinZone", "coefLitMin", "coefLitMaj"]):
            SubElement(frottement, len_n).text = fmt(zones[l_en[kk].lower()])

        # stockage
        zone_stockage = SubElement(calage, "zoneStockage")
        SubElement(zone_stockage, "loi").text = "1"
        n = len(liste_stock["numProfil"])
        SubElement(zone_stockage, "nbProfils").text = str(n)
        for len_n in ["numProfil", "limGauchLitMaj", "limDroitLitMaj"]:
            SubElement(zone_stockage, len_n).text = fmt(liste_stock[len_n])

        # Lois hydrauliques
        hydrauliques = SubElement(cas, "parametresLoisHydrauliques")

        for nom in dict_lois.keys():
            if nom in libres["name"] and (
                    dict_lois[nom]["type"] == 6 or dict_lois[nom]["type"] == 7
            ):
                # les types sont ceux de
                if dict_lois[nom]["type"] == 6:
                    dict_lois[nom]["type"] = 1
                    if self.mess:
                        self.mess.add_mess(
                            "LawChang_" + nom, "debug", "The  {} law changes type 6 => 1".format(nom)
                        )
                elif dict_lois[nom]["type"] == 7:
                    dict_lois[nom]["type"] = 2
                    if self.mess:
                        self.mess.add_mess(
                            "LawChang_" + nom, "debug", "The  {} law changes type 7 => 2".format(nom)
                        )

        nb = len(dict_lois.keys())
        SubElement(hydrauliques, "nb").text = str(nb)
        lois = SubElement(hydrauliques, "lois")

        for nom in sorted(dict_lois.keys()):
            struct = SubElement(lois, "structureParametresLoi")
            SubElement(struct, "nom").text = nom
            SubElement(struct, "type").text = str(dict_lois[nom]["type"])
            donnees = SubElement(struct, "donnees")
            SubElement(donnees, "modeEntree").text = "1"
            # WARNING The law must be sorted because of the order of
            # law must be the same than order File.law for API
            # SubElement(donnees, "fichier").text = '{}.loi'.format(
            #    del_symbol(self.geom_obj_toname(nom, dict_lois[nom]['type'])))
            SubElement(donnees, "fichier").text = "{}.loi".format(del_symbol(nom))
            SubElement(donnees, "uniteTps").text = "-0"
            SubElement(donnees, "nbPoints").text = "-0"
            SubElement(donnees, "nbDebitsDifferents").text = "-0"

        # impression résultats
        init = cas.find("parametresImpressionResultats")
        stockage = init.find("stockage")
        SubElement(stockage, "nbSite").text = str(len(sorties["name"]))
        SubElement(stockage, "branche").text = fmt(sorties["branchnum"])
        SubElement(stockage, "abscisse").text = fmt(sorties["abscissa"])
        # ******** XCAS tracer ********
        if tracer:
            add_wq_xcas(self.mdb, fichier_cas, noyau, dict_libres, self.mess)

        indent(fichier_cas)
        arbre = ElementTree(fichier_cas)
        arbre.write(fichier_sortie)
        if self.mess:
            self.mess.add_mess("CreatXcas", "info", "Save the Xcas file is done")
        self.elem_xcas = fichier_cas
        # except Exception as e:
        #     err = 'save Xcas file\n'
        #     err +='error: {}'.format(e)
        #     if self.mess:
        #       self.mess.add_mess("CreatXcas", 'critical,err)

        # add struct before harmonization
        dict_lois_tmp = dict_lois.copy()
        dico_loi_struct = {}
        for name in dict_lois_tmp.keys():
            if name in loi_struct["laws"]:
                dico_loi_struct[name] = dict_lois[name]
                idx = loi_struct["laws"].index(name)
                dico_loi_struct[name]["id_config"] = loi_struct["id_config"][idx]
                del dict_lois[name]

        return dict_lois, dico_loi_struct

    def create_init_xcas(self, fich_xcas):
        """

        :param fichier_cas:
        :param fich_xcas:
        :return:
        """
        fichier_cas = self.elem_xcas
        # ****** XCAS initialisation **********
        temps_max = 3600
        np_pas_temps_init = 2
        dt_init = temps_max / np_pas_temps_init
        param_cas = fichier_cas.find("parametresCas")
        parametres_generaux = param_cas.find("parametresGeneraux")
        parametres_generaux.find("fichMotsCles").text = fich_xcas
        parametres_generaux.find("code").text = "1"
        parametres_generaux.find("presenceCasiers").text = "false"
        parametres_temporels = param_cas.find("parametresTemporels")
        parametres_temporels.find("pasTemps").text = "{}".format(dt_init)
        parametres_temporels.find("critereArret").text = "2"
        parametres_temporels.find("nbPasTemps").text = "{}".format(np_pas_temps_init)
        parametres_temporels.find("tempsMax").text = "{}".format(temps_max)
        parametres_temporels.find("pasTempsVar").text = "false"
        geom_reseau = param_cas.find("parametresGeometrieReseau")
        type_cond = geom_reseau.find("extrLibres").find("typeCond")
        type_cond.text = type_cond.text.replace("4", "2")
        # type_cond.text = type_cond.text.replace('4', '2').replace('6',
        #                                                           '1').replace(
        #     '7', '2')
        type_cond.text = type_cond.text.replace("6", "1").replace("7", "2")
        lois_hydrauliques = param_cas.find("parametresLoisHydrauliques")
        lois = lois_hydrauliques.find("lois")
        for child in lois:
            # # tarage loi
            if child.find("type").text == "5":
                child.find("type").text = "2"
            donnee = child.find("donnees").find("fichier")
            temp = donnee.text.split(".")

            donnee.text = "{}_init.loi".format(del_symbol(temp[0]))

        initiales = param_cas.find("parametresConditionsInitiales")
        initiales.find("repriseEtude").find("repriseCalcul").text = "false"
        initiales.find("ligneEau").find("LigEauInit").text = "false"
        resultats = param_cas.find("parametresImpressionResultats")
        fich_opt = "mascaret_init.opt"
        resultats.find("resultats").find("fichResultat").text = fich_opt
        resultats.find("impression").find("impressionCalcul").text = "true"
        resultats.find("pasStockage").find("premPasTpsStock").text = "1"
        resultats.find("pasStockage").find("pasStock").text = "1"
        resultats.find("pasStockage").find("pasImpression").text = "1"
        resultats.find("stockage").find("option").text = "1"
        # tracers
        parametres_tracer = param_cas.find("parametresTraceur")
        parametres_tracer.find("presenceTraceurs").text = "false"

        indent(fichier_cas)
        arbre = ElementTree(fichier_cas)
        arbre.write(os.path.join(self.folder, fich_xcas))
        if self.mess:
            self.mess.add_mess("CreatXcasInit", "info", "Save the init. Xcas file  is done")

    def modif_xcas(self, parametres, xcasfile, fich_sortie=None):
        """
        Modify an existing xcas file with new parameters.
        :param parametres (dict): Parameters to update
        :param xcasfile (str): xcas filename
        :param fich_sortie (str): Optional output filename
        :return: None
        """
        fich_entree = os.path.join(self.folder, xcasfile)
        arbre = et_parse(fich_entree)
        racine = arbre.getroot()

        for param, val in parametres.items():
            parent = racine[0].find(val["balise1"])

            if "balise2" in val.keys() and val["balise2"]:
                child = parent.find(val["balise2"])
                child.find(param).text = val["valeur"]

            else:
                parent.find(param).text = val["valeur"]

        indent(racine)
        if fich_sortie:
            arbre.write(fich_sortie)
        else:
            arbre.write(fich_entree)
