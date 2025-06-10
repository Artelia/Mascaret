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

import datetime
import os
import re
import shutil
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as et_parse

from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ..ClassMessage import ClassMessage
from ..Function import del_symbol
from ..Function import str2bool, del_accent
from ..HydroLawsDialog import dico_typ_law


class ClassCreatFilesModels:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, mdb, dossier_file_masc):
        self.mdb = mdb
        self.dossier_file_masc = dossier_file_masc
        self.basename = "mascaret"
        self.mess = ClassMessage()
        self.geo_file = self.basename + ".geo"
        self.casier_file = self.basename + ".casier"
        self.dico_basinnum = {}
        self.dico_linknum = {}

    @staticmethod
    def around(x):
        """around x"""
        x = round(float(x), 2)
        return x

    @staticmethod
    def fmt(liste):
        # list(map(str, liste))
        return " ".join([str(var) for var in liste])

    @staticmethod
    def check_none(liste):
        """Check if None is list"""
        for val in liste:
            if str(val) == "None":
                return True
        return False

    # ************   GEO FILE   ********************************************************************
    def creer_geo(self):
        """creation of gemoetry file"""
        try:
            nomfich = os.path.join(self.dossier_file_masc, self.geo_file)

            if os.path.isfile(nomfich):
                sauv = nomfich.replace(".geo", "_old.geo")
                shutil.move(nomfich, sauv)
            requete = self.mdb.select("profiles", "active", "abscissa")

            with open(nomfich, "w") as fich:
                for i, nom in enumerate(requete["name"]):
                    branche = requete["branchnum"][i]
                    abs = requete["abscissa"][i]
                    temp_x = requete["x"][i]
                    temp_z = requete["z"][i]
                    lit_min_g = requete["leftminbed"][i]
                    lit_min_d = requete["rightminbed"][i]
                    if lit_min_d is not None and lit_min_g is None:
                        lit_min_g = 0.0

                    if branche and abs and temp_x and temp_z and lit_min_g and lit_min_d:
                        tab_z = []
                        tab_x = []
                        for var1, var2 in zip(temp_x.split(), temp_z.split()):
                            tab_x.append(self.around(var1))
                            tab_z.append(self.around(var2))

                        fich.write("PROFIL Bief_{0} {1} {2}\n".format(branche, nom, abs))
                        for x, z in zip(tab_x, tab_z):
                            if lit_min_g <= x <= lit_min_d:
                                type = "B"
                            else:
                                type = "T"

                            fich.write("{0:.2f} {1:.2f} {2}\n".format(x, z, type))

            self.mess.add_mess('creatGeo', 'info', "Creation the geometry is done")
        except Exception as e:
            err = "Error: save the geometry .\n"
            err += str(e)
            self.mess.add_mess('creatGeo', 'critic', err)

    def creer_geo_ref(self):
        """creation of gemoetry file"""
        try:
            branche, nom = None, None
            nomfich = os.path.join(self.dossier_file_masc, self.geo_file)

            if os.path.isfile(nomfich):
                sauv = nomfich.replace(".geo", "_old.geo")
                shutil.move(nomfich, sauv)
            requete = self.mdb.select("profiles", "active", "abscissa")

            # To get projection and Line coordinated.
            vlayer = self.mdb.make_vlayer(self.mdb.register["profiles"])
            vlayer_dp = vlayer.dataProvider()
            vlayer_crs = vlayer_dp.crs()
            vlayer_crs_str = vlayer_crs.authid()

            # Write the File
            with open(nomfich, "w") as fich:
                fich.write(
                    "#  DATE : {0:%d/%m/%Y %H:%M:%S}\n"
                    "#  PROJ. : {1}\n".format(datetime.date.today(), vlayer_crs_str)
                )

                iter = vlayer.getFeatures()
                feature_list = [v for v in iter]
                name_feature = [v["name"] for v in feature_list]
                for i, nom in enumerate(requete["name"]):
                    if nom in name_feature:
                        id = name_feature.index(nom)
                        # fetch geometry
                        geom = feature_list[id].geometry()
                        branche = requete["branchnum"][i]
                        abs = requete["abscissa"][i]
                        temp_x = requete["x"][i]
                        temp_z = requete["z"][i]
                        lit_min_g = requete["leftminbed"][i]
                        lit_min_d = requete["rightminbed"][i]
                        if lit_min_d is not None and lit_min_g is None:
                            lit_min_g = 0.0

                        if (
                                branche is not None
                                and abs is not None
                                and temp_x is not None
                                and temp_z is not None
                                and lit_min_g is not None
                                and lit_min_d is not None
                        ):
                            tab_z = []
                            tab_x = []
                            # fct1 = lambda x: round(float(x), 2)
                            for var1, var2 in zip(temp_x.split(), temp_z.split()):
                                tab_x.append(self.around(var1))
                                tab_z.append(self.around(var2))
                            points = geom.asMultiPolyline()[0]
                            (cood1X, cood1Y) = points[0]
                            (cood2X, cood2Y) = points[1]
                            cood_axe_x = cood1X + (cood2X - cood1X) / 2.0
                            cood_axe_y = cood1Y + (cood2Y - cood1Y) / 2.0

                            fich.write(
                                "PROFIL Bief_{0} {1} {2} {3} {4} {5} {6} "
                                "AXE {7} {8}\n".format(
                                    branche,
                                    nom,
                                    abs,
                                    cood1X,
                                    cood1Y,
                                    cood2X,
                                    cood2Y,
                                    cood_axe_x,
                                    cood_axe_y,
                                )
                            )
                            dif = tab_x[-1] - geom.length()
                            if dif > 0:
                                dif += 1
                                # garde line centree
                                geom = geom.extendLine(dif / 2.0, dif / 2.0)
                                feature_list[id].setGeometry(geom)
                                # change geometry
                                vlayer.startEditing()
                                vlayer.updateFeature(feature_list[id])
                                # Call commit to save the changes
                                vlayer.commitChanges()

                            for x, z in zip(tab_x, tab_z):
                                if lit_min_g <= x <= lit_min_d:
                                    type = "B"
                                else:
                                    type = "T"
                                # interpolate the distance on profile
                                dpoint = geom.interpolate(x).asPoint()
                                fich.write(
                                    "{0:.2f} {1:.2f} {2} {3} "
                                    "{4}\n".format(x, z, type, dpoint[0], dpoint[1])
                                )

            self.mess.add_mess('creatGeoRef', 'info', "Creation the geometry is done")
        except Exception as e:
            err = "Error: save the geometry {}-{}".format(branche, nom)
            err += str(e)
            self.mess.add_mess('creatGeoRef', 'critic', err)

    def creer_geo_casier(self):
        """
         Fonction de creation du fichier .casier avec la loi surface-volume
        """
        try:
            nomfich = os.path.join(self.dossier_file_masc, self.casier_file)

            if os.path.isfile(nomfich):
                sauv = nomfich.replace(".casier", "_old.casier")
                shutil.move(nomfich, sauv)

            casiers = self.mdb.select("basins", "active ORDER BY basinnum")
            lst_err = []
            with open(nomfich, "w") as fich:
                for i, nom in enumerate(casiers["name"]):
                    fich.write("CASIER {0}\n".format(nom))
                    cotes = casiers["level"][i]
                    surfaces = casiers["area"][i]
                    volumes = casiers["volume"][i]
                    if cotes is None or surfaces is None or volumes is None:
                        lst_err.append(i)
                        continue
                    for j, cote in enumerate(cotes.split()):
                        fich.write(
                            "{0:.2f} {1:.2f} {2:.2f}\n".format(
                                float(cotes.split()[j]),
                                float(surfaces.split()[j]),
                                float(volumes.split()[j]),
                            )
                        )
            if len(lst_err) > 0:
                raise Exception('ErrBasin', 'Basins law not specified. Id: '
                                            '{}'.format(lst_err))
            self.mess.add_mess('creatBasin', 'info', "Creation of the basin file is done")
        except Exception as e:
            err = "Error: save the basin file"
            err += str(e)
            self.mess.add_mess('creatBasin', 'critic', err)

    # ************   XCAS FILE   ********************************************************************
    def fmt_sans_none(self, liste, remplace_none):
        """
        Function to replace None in list with value
        Args:
            :param remplace_none : replacement value
            :param liste : list
        Returns:
            :return string list
            """
        liste = [remplace_none if var is None else var for var in liste]
        return " ".join([str(var) for var in liste])

    def fmt_num_basin(self, liste, dico_num, remplace_none):
        """
        Basin/link number list transformation function under
        Args:
            :param remplace_none : replacement value
            :param dico_num : dico which links the mascaret number to the Qgis number
            :param liste : list
        Returns:
            :return string list
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
                    self.mess.add_mess('CreatBasinNoNum', 'critic', txterr)
        return " ".join([str(var) for var in liste_num_masca])

    def fmt_plani_casier(self, liste):
        """
        Function for calculating the planning between 2 levels of the surface law
        Args:
            :param liste : list
        Returns:
            :return string list
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
                if plani_decimale > 0:
                    txt = "Simulation Error: the basin planimetry has " "to be an integer value"
                    self.mess.add_mess('CreatBasinPlani', 'critic', txt)
            except Exception:
                txt = "Simulation Error: the basin planimetry is not correct"
                self.mess.add_mess('CreatBasinPlani', 'critic', txt)
        return " ".join([str(var) for var in liste_plani])

    def indent(self, elem, level=0):
        """indentation auto
        Args:
            :param elem : items
            :param level : indentation level
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)

            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        elif level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    def creer_xcas(self, noyau, par_init=None):
        """To create xcas file
        Args:
        :param noyau: (str) kernel
        :param par_init (optionel) : (dict) initial parameters , default None
        Return :
            return : (dict) dict_lois, (dict)  dico_loi_struct
        """
        dict_lois = {}
        # try:
        fichier_sortie = os.path.join(self.dossier_file_masc, self.basename + ".xcas")
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
            if par_init:
                if param in par_init.keys():
                    valeur = str(par_init[param])
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
        seuils, loi_struct = self.modif_seuil(seuils, dico_str)
        casiers = self.mdb.select("basins", "active ORDER BY basinnum ")
        liaisons = self.mdb.select("links", "active ORDER BY linknum ")

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
                mess = "Check the {} profile if it's ok ".format(profils["name"][j])
                self.mess.add_mess("CheckProf1", "critic", mess)
                return dict_lois

            try:
                nb_pas = max(int(diff / float(planim_val)) + 1, nb_pas)
            except Exception:
                self.mess.add_mess("CheckPlani_{}".format(str(j)), "warning",
                                   "Check planim abs:{}".format(abs))

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
        SubElement(liste_branch, "numeros").text = self.fmt(numero)
        SubElement(liste_branch, "abscDebut").text = self.fmt(branches["abscdebut"])
        SubElement(liste_branch, "abscFin").text = self.fmt(branches["abscfin"])
        extrem_debut = [i * 2 - 1 for i in numero]
        SubElement(liste_branch, "numExtremDebut").text = self.fmt(extrem_debut)
        extrem_fin = [i * 2 for i in numero]
        SubElement(liste_branch, "numExtremFin").text = self.fmt(extrem_fin)

        # liste des Noeuds
        liste_noeuds = SubElement(reseau, "listeNoeuds")

        SubElement(liste_noeuds, "nb").text = str(len(dict_noeuds.keys()))
        e_tnoeuds = SubElement(liste_noeuds, "noeuds")
        for k in sorted(dict_noeuds.keys()):
            noeud = SubElement(e_tnoeuds, "noeud")
            temp = dict_noeuds[k] + [0] * (5 - len(dict_noeuds[k]))
            SubElement(noeud, "num").text = self.fmt(temp)

        # liste des extrémités libres
        extr_libres = SubElement(reseau, "extrLibres")
        liste = dict_libres["nom"]
        SubElement(extr_libres, "nb").text = str(len(liste))
        SubElement(extr_libres, "num").text = self.fmt(dict_libres["num"])
        SubElement(extr_libres, "numExtrem").text = self.fmt(dict_libres["extrem"])

        noms = SubElement(extr_libres, "noms")
        for nom in liste:
            SubElement(noms, "string").text = nom

        SubElement(extr_libres, "typeCond").text = self.fmt(dict_libres["typeCond"])
        # temp=[]
        # for nom in liste:
        #     if nom in libres["name"] and (dictLois[nom]['type'] == 6 or dictLois[nom]['type'] == 7):
        #             temp.append(1)
        #     else:
        #             temp.append(sorted(dictLois.keys()).index(nom) + 1)

        temp = [sorted(dict_lois.keys()).index(nom) + 1 for nom in liste]
        SubElement(extr_libres, "numLoi").text = self.fmt(temp)

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
        SubElement(planim_e, "valeursPas").text = self.fmt(planim["pas"])
        SubElement(planim_e, "num1erProf").text = self.fmt(planim["min"])
        SubElement(planim_e, "numDerProf").text = self.fmt(planim["max"])

        maillage_e = SubElement(planimaill, "maillage")
        SubElement(maillage_e, "modeSaisie").text = "2"
        SubElement(maillage_e, "sauvMaillage").text = "false"
        maillage_c = SubElement(maillage_e, "maillageClavier")
        SubElement(maillage_c, "nbSections").text = "0"
        SubElement(maillage_c, "nbPlages").text = str(len(maillage["pas"]))
        SubElement(maillage_c, "num1erProfPlage").text = self.fmt(maillage["min"])
        SubElement(maillage_c, "numDerProfPlage").text = self.fmt(maillage["max"])
        SubElement(maillage_c, "pasEspacePlage").text = self.fmt(maillage["pas"])
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
                    msg = "Profil de crete introuvable pour {}"
                    self.mess.add_mess("CheckProfCret", "warning", msg.format(nom))
                    return

            SubElement(struct, "gradient").text = "-0"

        # Pertes de charges
        if len(pertescharg["name"]) > 0:
            pertes = SubElement(singularite, "pertesCharges")
            SubElement(pertes, "nbPerteCharge").text = str(len(pertescharg["name"]))
            SubElement(pertes, "numBranche").text = self.fmt(pertescharg["branchnum"])
            SubElement(pertes, "abscisses").text = self.fmt(pertescharg["abscissa"])
            SubElement(pertes, "coefficients").text = self.fmt(pertescharg["coeff"])

        # Casiers et liaisons
        if len(casiers["name"]) > 0:
            self.add_basin_xcas(fichier_cas, casiers, liaisons)
        # Apports et déversoirs
        apport_dever = SubElement(cas, "parametresApportDeversoirs")

        # Apports
        e_tapports = SubElement(apport_dever, "debitsApports")
        SubElement(e_tapports, "nbQApport").text = str(len(apports["name"]))
        noms = SubElement(e_tapports, "noms")
        for nom in apports["name"]:
            SubElement(noms, "string").text = nom

        SubElement(e_tapports, "numBranche").text = self.fmt(apports["branchnum"])
        if self.check_none(apports["abscissa"]):
            self.mess.add_mess("LatInflowAbs", "warning",
                               "Geometric object for lateral inflows is not found")
        SubElement(e_tapports, "abscisses").text = self.fmt(apports["abscissa"])
        if self.check_none(apports["length"]):
            self.mess.add_mess("LatInflowLen", "warning",
                               "Lenght for lateral inflows is not found")
        SubElement(e_tapports, "longueurs").text = self.fmt(apports["length"])
        temp = [sorted(dict_lois.keys()).index(nom) + 1 for nom in apports["name"]]
        SubElement(e_tapports, "numLoi").text = self.fmt(temp)

        # Déversoirs
        devers_late = SubElement(apport_dever, "devers_late")
        SubElement(devers_late, "nbDeversoirs").text = str(len(deversoirs["name"]))
        noms = SubElement(devers_late, "noms")
        for nom in deversoirs["name"]:
            SubElement(noms, "string").text = nom

        SubElement(devers_late, "type").text = self.fmt(deversoirs["type"])

        l_en = ["branchnum", "abscissa", "length", "z_crest", "flowratecoef"]
        for kk, len_n in enumerate(["numBranche", "abscisse", "longueur", "coteCrete", "coeffDebit"]):
            SubElement(devers_late, len_n).text = self.fmt(deversoirs[l_en[kk].lower()])

        temp = []
        for nom in deversoirs["name"]:
            if nom in dict_lois.keys():
                temp.append(sorted(dict_lois.keys()).index(nom) + 1)
            else:
                temp.append(0)
        SubElement(devers_late, "numLoi").text = self.fmt(temp)

        # Calage
        calage = SubElement(cas, "parametresCalage")

        # frottement
        frottement = SubElement(calage, "frottement")
        SubElement(frottement, "loi").text = "1"
        SubElement(frottement, "nbZone").text = str(len(zones["zoneabsstart"]))
        SubElement(frottement, "numBranche").text = self.fmt(zones["branch"])
        l_en = ["zoneabsstart", "zoneabsend", "minbedcoef", "majbedcoef"]
        for kk, len_n in enumerate(["absDebZone", "absFinZone", "coefLitMin", "coefLitMaj"]):
            SubElement(frottement, len_n).text = self.fmt(zones[l_en[kk].lower()])

        # stockage
        zone_stockage = SubElement(calage, "zoneStockage")
        SubElement(zone_stockage, "loi").text = "1"
        n = len(liste_stock["numProfil"])
        SubElement(zone_stockage, "nbProfils").text = str(n)
        for len_n in ["numProfil", "limGauchLitMaj", "limDroitLitMaj"]:
            SubElement(zone_stockage, len_n).text = self.fmt(liste_stock[len_n])

        # Lois hydrauliques
        hydrauliques = SubElement(cas, "parametresLoisHydrauliques")

        for nom in dict_lois.keys():
            if nom in libres["name"] and (
                    dict_lois[nom]["type"] == 6 or dict_lois[nom]["type"] == 7
            ):
                # les types sont ceux de
                if dict_lois[nom]["type"] == 6:
                    # TODO and noyau!='transcritical'
                    dict_lois[nom]["type"] = 1
                    self.mess.add_mess("LawChang_" + nom, "debug",
                                       "The  {} law changes type 6 => 1".format(nom))
                elif dict_lois[nom]["type"] == 7:
                    dict_lois[nom]["type"] = 2
                    self.mess.add_mess("LawChang_" + nom, "debug",
                                       "The  {} law changes type 7 => 2".format(nom))

        nb = len(dict_lois.keys())
        SubElement(hydrauliques, "nb").text = str(nb)
        lois = SubElement(hydrauliques, "lois")

        for nom in sorted(dict_lois.keys()):
            struct = SubElement(lois, "structureParametresLoi")
            SubElement(struct, "nom").text = nom
            SubElement(struct, "type").text = str(dict_lois[nom]["type"])
            donnees = SubElement(struct, "donnees")
            SubElement(donnees, "modeEntree").text = "1"
            # WARNING The law must be sorted because of the order of law must be the same than order File.law for API
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
        SubElement(stockage, "branche").text = self.fmt(sorties["branchnum"])
        SubElement(stockage, "abscisse").text = self.fmt(sorties["abscissa"])
        # ******** XCAS tracer ********
        if tracer:
            self.add_wq_xcas(fichier_cas, noyau, dict_libres)

        # ******** XCAS modiication of type when steady case ********
        # only type rating curve 4 => liminigraph et 5 => liminigraph
        # if noyau == 'steady':
        #
        #     param_cas = fichier_cas.find('parametresCas')
        #     # parametres_generaux = param_cas.find('parametresGeneraux')
        #     geom_reseau = param_cas.find('parametresGeometrieReseau')
        #     type_cond = geom_reseau.find('extrLibres').find('typeCond')
        #     type_cond.text = type_cond.text.replace('4', '2')
        #     lois_hydrauliques = param_cas.find('parametresLoisHydrauliques')
        #     lois = lois_hydrauliques.find('lois')
        #     for child in lois:
        #         # no possible to use rating curve with steady
        #         if child.find('type').text == '5':
        #             child.find('type').text = '2'

        # **********************************
        self.indent(fichier_cas)
        arbre = ElementTree(fichier_cas)
        arbre.write(fichier_sortie)
        self.mess.add_mess("CreatXcas", "info",
                           "Save the Xcas file is done")
        # ****** XCAS initialisation **********
        temps_max = 3600
        np_pas_temps_init = 2
        dt_init = temps_max / np_pas_temps_init

        param_cas = fichier_cas.find("parametresCas")
        parametres_generaux = param_cas.find("parametresGeneraux")
        fich_xcas = "{}_init.xcas".format(self.basename)
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
        fich_opt = "{}_init.opt".format(self.basename)
        resultats.find("resultats").find("fichResultat").text = fich_opt
        resultats.find("impression").find("impressionCalcul").text = "true"
        resultats.find("pasStockage").find("premPasTpsStock").text = "1"
        resultats.find("pasStockage").find("pasStock").text = "1"
        resultats.find("pasStockage").find("pasImpression").text = "1"
        resultats.find("stockage").find("option").text = "1"
        # tracers
        if tracer:
            parametres_tracer = param_cas.find("parametresTraceur")
            parametres_tracer.find("presenceTraceurs").text = "false"

        self.indent(fichier_cas)
        arbre = ElementTree(fichier_cas)
        arbre.write(os.path.join(self.dossier_file_masc, fich_xcas))

        self.mess.add_mess("CreatXcasInit", "info",
                           "Save the init. Xcas file  is done")

        # except Exception as e:
        #     err = 'save Xcas file\n'
        #     err +='error: {}'.format(e)
        #     self.mess.add_mess("CreatXcas", 'critical,err)

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

    def check_basin(self, liaisons, casiers, dico_basinnum):
        """
        Check if links is correctly defined
        """
        for idc, num in enumerate(casiers["basinnum"]):
            if float(casiers["initlevel"][idc]) < min([float(val) for val in casiers["level"][idc].split()]):
                txte = ('*** Error: The "Reference level" for the basins {} '
                                   'which must be greater than or equal to '
                                   'the minimum level of the height volume law'.format(num))
                self.mess.add_mess("BasinErr_{}".format(num), "critic", txte)

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
            if nat == 1 and (abs is None or abs == -1):
                txte = ('*** Error: The "Basin-Reach" type link {} '
                        'does not have an abscissa on the reach'.format(num))
                self.mess.add_mess("LinkBR_{}".format(num), "critic", txte)
            # check coherent between variable and typ
            for key in check_typ_link[tupl]:
                val = liaisons[key][idl]
                if val is None:
                    txte = ('*** Error: Link {} is not type coherent.'.format(num))
                    self.mess.add_mess("LinkErr_{}".format(num), "critic", txte)
                    break

            # check level for the start basin
            if stb in dico_basinnum.keys():
                numc = casiers["basinnum"][dico_basinnum[stb] - 1]
                init_level = casiers["initlevel"][dico_basinnum[stb] - 1]
                if level < init_level:
                    txtw = (
                        "*** Warning: Please note that the elevation of "
                        "the upstream basin {} is higher than the elevation of the link {}. \n"
                        "This can generate an artificial flow.".format(numc, num)
                    )
                    self.mess.add_mess("Links_{}_{}".format(numc, num), "warning", txtw)
            else:
                txte = (
                    "*** Error: The link {} " 'does not have "Basin number start"'.format(num)
                )
                self.mess.add_mess("LinksB_{}".format(numc, num), "critic", txte)
            # check if "basinend" is existed  before  check level
            if ste is None or ste == -1:
                continue
            # check level for the end basin
            if ste in dico_basinnum.keys():
                # -1 because of Python begin by 0
                numc = casiers["basinnum"][dico_basinnum[ste] - 1]
                init_level = casiers["initlevel"][dico_basinnum[ste] - 1]
                if level < init_level:
                    txtw = (
                        "*** Warning: Please note that the elevation of "
                        "the downtream basin {} is higher than the elevation of the link {}. \n"
                        "This can generate an artificial flow.".format(numc, num)
                    )
                    self.mess.add_mess("Links1_{}_{}".format(numc, num), "warning", txtw)

            else:
                txte = (
                    "*** Error: The link {} " 'does not have "Basin number End"'.format(num)
                )
                self.mess.add_mess("LinksB1_{}".format(numc, num), "critic", txte)

    def add_basin_xcas(self, fichier_cas, casiers, liaisons):
        # Creation du dictionnaire de numero de casier entre mascaret (cle)
        # et qgis (valeur)
        self.dico_basinnum = {}
        dico_basinnum_creat = {}
        for id_mas, num_qgis in enumerate(casiers["basinnum"], 1):
            self.dico_basinnum[id_mas] = num_qgis
            dico_basinnum_creat[num_qgis] = id_mas
        # # Creation du dictionnaire de numero de liaison entre mascaret (cle)
        # # et qgis (valeur)
        self.dico_linknum = {}
        for id_mas, num_qgis in enumerate(liaisons["linknum"], 1):
            self.dico_linknum[id_mas] = num_qgis
        self.check_basin(liaisons, casiers, dico_basinnum_creat)
        # Creation des lignes a ajouter dans Xcas
        cas = fichier_cas.find("parametresCas")
        casier = SubElement(cas, "parametresCasier")
        SubElement(casier, "nbCasiers").text = str(len(casiers["name"]))
        SubElement(casier, "optionPlanimetrage").text = self.fmt_plani_casier(casiers["level"])
        SubElement(casier, "optionCalcul").text = "1"
        SubElement(casier, "fichierGeomCasiers").text = self.casier_file
        SubElement(casier, "cotesInitiale").text = self.fmt_sans_none(casiers["initlevel"], "-1.0")
        # Liaisons (champs non listes = active et linknum)
        et_liaisons = SubElement(casier, "liaisons")
        SubElement(et_liaisons, "nbLiaisons").text = str(len(liaisons["name"]))
        SubElement(et_liaisons, "types").text = self.fmt_sans_none(liaisons["type"], "-1.0")
        SubElement(et_liaisons, "nature").text = self.fmt_sans_none(liaisons["nature"], "-1.0")
        SubElement(et_liaisons, "cote").text = self.fmt_sans_none(liaisons["level"], "-1.0")
        SubElement(et_liaisons, "largeur").text = self.fmt_sans_none(liaisons["width"], "-1.0")
        SubElement(et_liaisons, "longueur").text = self.fmt_sans_none(liaisons["length"], "-1.0")
        SubElement(et_liaisons, "rugosite").text = self.fmt_sans_none(liaisons["roughness"], "-1.0")
        SubElement(et_liaisons, "section").text = self.fmt_sans_none(
            liaisons["crosssection"], "-1.0"
        )
        SubElement(et_liaisons, "coefPerteCharge").text = self.fmt_sans_none(
            liaisons["headlosscoef"], "-1.0"
        )
        SubElement(et_liaisons, "coefDebitSeuil").text = self.fmt_sans_none(
            liaisons["weirdischargecoef"], "-1.0"
        )
        SubElement(et_liaisons, "coefActivation").text = self.fmt_sans_none(
            liaisons["activationcoef"], "-1.0"
        )
        SubElement(et_liaisons, "coefDebitOrifice").text = self.fmt_sans_none(
            liaisons["pipedischargecoef"], "-1.0"
        )
        SubElement(et_liaisons, "typeOrifice").text = self.fmt_sans_none(
            liaisons["culverttype"], "-1"
        )
        SubElement(et_liaisons, "numCasierOrigine").text = self.fmt_num_basin(
            liaisons["basinstart"], dico_basinnum_creat, "-1"
        )
        SubElement(et_liaisons, "numCasierFin").text = self.fmt_num_basin(
            liaisons["basinend"], dico_basinnum_creat, "-1"
        )
        SubElement(et_liaisons, "numBiefAssocie").text = self.fmt_sans_none(
            liaisons["branchnum"], "-1"
        )
        SubElement(et_liaisons, "abscBief").text = self.fmt_sans_none(liaisons["abscissa"], "-1.0")

    def add_wq_xcas(self, fichier_cas, noyau, dict_libres):
        """Modification of xcas for Water Quality"""
        # requête pour récupérer les paramètres

        cas = fichier_cas.find("parametresCas")
        sql = (
            "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} "
            "WHERE gui_type = 'tracers' ORDER BY id;"
        )

        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, b1, b2 in rows:
            if param == "fichMeteoTracer":
                sql = "SELECT {0} FROM {1}.{2} WHERE parametre = 'fichmeteo' ;"
                wow = self.mdb.run_query(
                    sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True
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
        lateral = self.mdb.select("tracer_lateral_inflows", order="abscissa")

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
            txt = ("Please enter water quality laws")
            self.mess.add_mess("WQLoi", "critic", txt)
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
        SubElement(tracer_source, "typeSources").text = self.fmt(typ)
        SubElement(tracer_source, "numBranche").text = self.fmt(numb)
        if self.check_none(abs):
            txt = (
                "Geometric object for tracer lateral inflows " "is not found"
            )
            self.mess.add_mess("WQGeoLatInflow", "warning", txt)
        SubElement(tracer_source, "abscisses").text = self.fmt(abs)
        if self.check_none(leng):
            txt = ("Warning : Lenght for tracer lateral inflows is not found")
            self.mess.add_mess("WQLenghtLatInflow", "warning", txt)
        SubElement(tracer_source, "longueurs").text = self.fmt(leng)
        SubElement(tracer_source, "numLoi").text = self.fmt(numl)

        # Lois traceur
        tracer_law = SubElement(cas, "parametresLoisTraceur")
        nb = len(list_loi)
        SubElement(tracer_law, "nbLoisTracer").text = str(nb)
        lois = SubElement(tracer_law, "loisTracer")
        if nb > 0:
            for name in list_loi:
                try :
                    struct = SubElement(lois, "structureSParametresLoiTraceur")
                    SubElement(struct, "nom").text = name
                    SubElement(struct, "modeEntree").text = "1"
                    SubElement(struct, "fichier").text = "{}_tra.loi".format(del_symbol(name.lower()))
                    SubElement(struct, "uniteTps").text = "-0"
                    SubElement(struct, "nbPoints").text = "-0"
                except Exception as err:
                    txt = "Check  water quality laws (extremities,inflows)\n"
                    txt += str(err)
                    self.mess.add_mess("WQLoi2", "critic", txt)
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
        initiales.find("typeCondLimTracer").text = self.fmt(typ)
        initiales.find("numLoiCondLimTracer").text = self.fmt(numl)

        return True

    def modif_seuil(self, seuil, dico_str):
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
                    seuil[ls].append(self.typ_struct(dico_str["method"][i]))
                elif ls == "abscissa":
                    seuil[ls].append(dico_str["abscissa"][i])
                elif ls == "branchnum":
                    seuil[ls].append(dico_str["branchnum"][i])
                elif ls == "z_break":
                    seuil[ls].append(99999)
                elif ls == "z_crest":
                    where = "id_config ='{}'".format(dico_str["id"][i])
                    zmin = self.mdb.select_min("z", "profil_struct", where)
                    seuil[ls].append(zmin)
                else:
                    seuil[ls].append(None)

        return seuil, loi_struct

    def typ_struct(self, meth):
        """function to know the law type"""

        if meth == 0 or meth == 4 or meth == 1 or meth == 5 or meth == 3:
            return 1
        else:
            return None

    def modif_xcas(self, parametres, xcasfile, fich_sortie=None):
        fich_entree = os.path.join(self.dossier_file_masc, xcasfile)
        arbre = et_parse(fich_entree)
        racine = arbre.getroot()

        for param, val in parametres.items():
            parent = racine[0].find(val["balise1"])

            if "balise2" in val.keys() and val["balise2"]:
                child = parent.find(val["balise2"])
                child.find(param).text = val["valeur"]

            else:
                parent.find(param).text = val["valeur"]

        self.indent(racine)
        if fich_sortie:
            arbre.write(fich_sortie)
        else:
            arbre.write(fich_entree)

    # ************   LAW FILE   ********************************************************************

    def creer_loi(self, nom, tab, type_, init=False):
        # nom = self.geom_obj_toname(nom, type_)
        if init:
            nom = nom + "_init"
        with open(os.path.join(self.dossier_file_masc, del_symbol(nom) + ".loi"), "w") as fich:
            fich.write("# " + nom + "\n")
            if type_ == 1:
                fich.write("# Temps (S) Debit\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {flowrate:.6f}\n"
            elif type_ == 2:
                fich.write("# Temps (S) Cote\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {z:.6f}\n"
            elif type_ == 3:
                fich.write("# Temps (S) Cote Debit\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {z:.6f} {flowrate:.6f}\n"
            elif type_ == 4:
                fich.write("# Debit Cote\n")
                chaine = " {flowrate:.3f} {z:.6f}\n"
            elif type_ == 5:
                fich.write("# Cote Debit\n")
                chaine = " {z:.6f} {flowrate:.6f}\n"
            elif type_ == 6:
                fich.write("# Debit Cote_Aval Cote_Amont\n")
                chaine = " {flowrate:.6f} {z_downstream:.6f} {z_upstream:.6f}\n"
            elif type_ == 7:
                fich.write("# Temps (s) Cote inférieur Cote supérieur\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {z_lower:.6f} {z_up:.6f}\n"
                #   example:  print("{0} :\n \t Time : {1}\n \t
                #                        Upstream Water Level{2}\n \t  "
                #                       "Downstream Water Level :{3}"
                #                       .format(nom,tab["temps"],
                #                       tab["cote_amont"], tab["cote_aval"]))
            n = len(list(tab.values())[0])
            for i in range(n):
                dico = {k: v[i] for k, v in tab.items()}
                fich.write(chaine.format(**dico))

    def obs_to_loi(self, dict_lois, date_debut, date_fin, par):
        """
        Creation law with observation data
        Args:
            :param dict_lois: dict of law
            :param date_debut: start date
            :param date_fin: last date
            :param par : dict of parameters
        Return :
            :return:
        """
        # pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        pattern = re.compile("(\\w+)\\[t([+-][0-9]+)?\\]")
        somme = 0
        debit_prec = 0

        for nom, loi in dict_lois.items():
            if loi["type"] == 1:
                type_ = "Q"
            elif loi["type"] == 2:
                type_ = "H"
            else:
                continue
            if not loi.get("formule"):
                continue

            valeur_init = None
            liste_stations = pattern.findall(loi["formule"])
            # get observation each station
            obs_stations = {}
            for cd_hydro, delta in liste_stations:
                delta_h = int(delta) if delta else 0
                dt =  datetime.timedelta(hours=delta_h)
                sql_tab = (
                    "SELECT * FROM "
                    "(SELECT code,type, UNNEST(date)as date, "
                    "UNNEST(valeur)as valeur "
                    "FROM {0}.observations "
                    "WHERE code='{1}' and type='{2}') t "
                    "WHERE date >= '{3:%Y-%m-%d %H:%M}' "
                    "AND date <= '{4:%Y-%m-%d %H:%M}' "
                    "ORDER BY date ".format(
                        self.mdb.SCHEMA, cd_hydro, type_, date_debut + dt, date_fin + dt
                    )
                )
                obs_stations[cd_hydro] = self.mdb.query_todico(sql_tab)
                if not obs_stations[cd_hydro]["date"]:
                    self.mess.add_mess('NoInitSteady', 'critic',
                                       f"Error: Please check if law for {nom} object is correct.\n "
                                       f"No observations found for station {cd_hydro} "
                                       "on the dates: {0:%Y-%m-%d %H:%M} - {1:%Y-%m-%d %H:%M}"
                                       "".format(date_debut + dt, date_fin + dt))
                    continue
            # ref dates and station (first station)
            ref_station, ref_delta = liste_stations[0]
            ref_delta_h = int(ref_delta) if ref_delta else 0
            ref_dates = [d - datetime.timedelta(hours=ref_delta_h) for d in obs_stations[ref_station]["date"]]

            fichier_loi = os.path.join(self.dossier_file_masc, del_symbol(nom) + ".loi")
            with open(fichier_loi, "w") as fich_sortie:
                fich_sortie.write("# {0}\n".format(nom))
                if type_ == "Q":
                    fich_sortie.write("# Temps (H) Debit\n")
                else:
                    fich_sortie.write("# Temps (H) Hauteur\n")
                fich_sortie.write(" H \n")
                for t in ref_dates:
                    calc = loi["formule"]
                    for cd_hydro, delta in liste_stations:
                        delta_h = int(delta) if delta else 0
                        t2 = t + datetime.timedelta(hours=delta_h)
                        val = None
                        if t2 in obs_stations[cd_hydro]["date"]:
                            i = obs_stations[cd_hydro]["date"].index(t2)
                            val = obs_stations[cd_hydro]["valeur"][i]
                        calc = pattern.sub(str(val), calc, 1)
                    try:
                        resultat = eval(calc)
                    except Exception:
                        resultat = None

                    if resultat is not None:
                        if valeur_init is None:
                            valeur_init = resultat
                            somme += resultat
                        tps = (t - date_debut).total_seconds() / 3600
                        chaine = "  {0:4.3f}   {1:3.6f}\n"
                        fich_sortie.write(chaine.format(tps, resultat))

            # check law after write
            initime = round((ref_dates[0] - date_debut).total_seconds() / 3600, 3) * 3600
            lasttime = round((ref_dates[-1] - date_debut).total_seconds() / 3600, 3) * 3600
            self.check_timelaw(par, nom, initime, lasttime)

            if valeur_init is not None:
                if type_ == "Q":
                    tab = {"time": [0, 3600], "flowrate": [valeur_init, valeur_init]}
                    self.creer_loi(nom, tab, 1, init=True)
                else:
                    tab = {"time": [0, 3600], "z": [valeur_init, valeur_init]}
                    self.creer_loi(nom, tab, 2, init=True)
            else:
                par["initialisationAuto"] = False
                self.mess.add_mess('NoInitSteady', 'Warning',
                                   "No initialisation because of no SteadyValue")

        valeur_init = None

        for nom, loi in dict_lois.items():
            if not loi["type"] in (1, 2) or (loi["type"] in (1, 2) and not loi['formule']):
                # create other law
                tab = self.get_laws(
                    nom, loi["type"], obs=True, date_deb=date_debut, date_fin=date_fin
                )
                if tab:
                    self.creer_loi(nom, tab, loi["type"])
                    if "time" in tab.keys():
                        initime = round(tab["time"][0], 3)
                        lasttime = round(tab["time"][-1], 3)
                        self.check_timelaw(par, nom, initime, lasttime)
                else:
                    self.mess.add_mess('CreatLaw_{}'.format(nom), 'critic',
                                       "The law for {} is not create.".format(nom))
                    continue
                # create init law
                if loi["type"] in [1,2,4]:  # , 5]: # car 5 mascaret plante à l'init
                    self.creer_loi(nom, tab, loi["type"], init=True)
                elif loi["type"] in [5] and loi["couche"] == "extremites":
                    for c, d in zip(tab["z"], tab["flowrate"]):
                        if debit_prec > 0 and d > somme:
                            valeur_init = (c - cote_prec) / (d - debit_prec) * (
                                    somme - debit_prec
                            ) + cote_prec
                            break
                        else:
                            cote_prec, debit_prec = c, d
                    if valeur_init is not None:
                        tab = {"time": [0, 3600], "z": [valeur_init, valeur_init]}
                        self.creer_loi(nom, tab, 2, init=True)
                else:
                    par["initialisationAuto"] = False
                    self.mess.add_mess('NoInitSteady', 'Warning',
                                       "No initialisation because of no SteadyValue")
        return par

    def check_timelaw(self, par, name, initime, lasttime):
        cond = False
        if par["tempsInit"] < initime:
            self.mess.add_mess("tLaw_{}".format(name), "critic",
                               " Error law {} on the Initial Time".format(name))
            cond = True
        if par["critereArret"] == 1:
            # tmax
            if par["tempsMax"] > lasttime:
                self.mess.add_mess("tLaw_{}".format(name), "critic",
                                   " Error law {} on the Last Time".format(name))
                cond = True
        elif par["critereArret"] == 2:
            # nb iterration
            if par["nbPasTemps"] * par["pasTemps"] > lasttime:
                self.mess.add_mess("tLaw_{}".format(name), "critic",
                                   " Error law {} on the Last Time".format(name))
                cond = True

        return cond

    def get_laws(self, name_obj, typ_law, obs=False, date_deb=None, date_fin=None):
        """
        Get law
        Args:
            :param name_obj:
            :param typ_law:
            :param obs:
            :param date_deb:
            :param date_fin:
        :return:
        """

        try:
            if obs and date_deb is not None and date_fin is not None:
                condition = """geom_obj='{0}' 
                                 AND id_law_type = {1}
                                 AND starttime <= '{2:%Y-%m-%d %H:%M}' 
                                 AND endtime >= '{3:%Y-%m-%d %H:%M}'
                                 AND active
                                 """.format(
                    name_obj, typ_law, date_deb, date_fin
                )

            else:
                condition = "geom_obj='{0}' AND id_law_type={1} AND active".format(
                    name_obj, typ_law
                )

            config = self.mdb.select_one("law_config", condition, verbose=False)
            if config:
                values = self.mdb.select(
                    "law_values",
                    where="id_law={}".format(config["id"]),
                    order="id_var, id_order",
                    list_var=["id_var", "id_order", "value"],
                )
                lst_var = [tmp["code"] for tmp in dico_typ_law[typ_law]["var"]]
                lst_idvar = [id for id, tmp in enumerate(dico_typ_law[typ_law]["var"])]

                tab = {key: [] for key in lst_var}
                conv_idvar = {id: lst_var[i] for i, id in enumerate(lst_idvar)}

                for value, id_var in zip(values["value"], values["id_var"]):
                    tab[conv_idvar[id_var]].append(float(value))

                return tab
            else:
                err = "Error: Please check if law for {0} object " "is correct. \n".format(name_obj)
                self.mess.add_mess("obsLaw_{}".format(name_obj), "critic", err)
                return None

        except Exception as e:
            err = "Error: Please check if law for {0} object " "is correct. \n".format(name_obj)
            err += str(e)
            self.mess.add_mess("obsLaw_{}".format(name_obj), "critic", err)
            return None

    def classic_law(self,par, dict_lois):
        """
                files creation  for the classic law
               Args:
                   :param par: dict contains the parameters
                   :param dict_lois: dict contains the law
               Return :
                   :return: dict (par)
        """
        for nom, l in dict_lois.items():
            # dictLois.items() extremities liste

            tab = self.get_laws(nom, l["type"])
            if tab:
                self.creer_loi(nom, tab, l["type"])
                if "time" in tab.keys():
                    initime = round(tab["time"][0], 3)
                    lasttime = round(tab["time"][-1], 3)
                    self.check_timelaw(par, nom, initime, lasttime)
            else:
                self.mess.add_mess('CreatLaw_{}'.format(nom), 'critic',
                                   "The law for {} is not create.".format(nom))

            if "valeurperm" not in l.keys():
                continue

            # nom = nom + "_init"
            if l["valeurperm"] is not None:
                if l["type"] == 1:
                    tab = {"time": [0, 3600], "flowrate": [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 1, init=True)
                elif l["type"] == 2:
                    tab = {"time": [0, 3600], "z": [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 2, init=True)
                elif l["type"] in [4, 5]:
                    self.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    self.mess.add_mess('NoInitSteady', 'Warning',
                                       "No initialisation because of no SteadyValue")
        else:
                if l["type"] in [4, 5]:
                    self.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    txt = (
                            'No initialisation because of no steady value set for {} condition'.format(nom) +
                            'Set "steadyValue" in extremities layer for entity {}'.format(nom)
                    )
                    self.mess.add_mess(txt, 'NoInitUnsteady', 'warning')
        return par
    # ************   LIG FILE   ********************************************************************

    def opt_to_lig(self, id_run, base_namefiles):
        """Creation of .lig file"""
        result = self.get_for_lig(id_run)
        if not result:
            return None
        i1 = {}
        i2 = {}
        for section, branche in zip(result["section"], result["branche"]):
            if branche not in i1.keys():
                i1[branche] = 9999999
            if branche not in i2.keys():
                i2[branche] = -9999999
            i1[branche] = min(i1[branche], section)
            i2[branche] = max(i2[branche], section)

        nb_bief = len(set(result["branche"]))
        section = sorted(set(result["section"]))

        imax = len(section)
        i1i2 = []
        for b in sorted(i1.keys()):
            i1i2.append(str(i1[b]))
            i1i2.append(str(i2[b]))

        with open(os.path.join(self.dossier_file_masc, base_namefiles + ".lig"), "w") as fich:
            date = datetime.datetime.utcnow()
            fich.write("RESULTATS CALCUL,DATE :  {0:%d/%m/%y %H:%M}\n".format(date))
            fich.write("FICHIER RESULTAT MASCARET{0}\n".format(" " * 47))
            fich.write("{0} \n".format("-" * 71))
            fich.write(" IMAX  ={0:5d} NBBIEF={1:5d}\n".format(int(imax), int(nb_bief)))

            chaine = [""]
            for k in range(0, len(i1i2), 10):
                chaine.append("I1,I2 =")
                for i in range(k, k + 10):
                    if i < len(i1i2):
                        chaine.append("{0:4}".format(i1i2[i]))
                chaine.append("\n")
            fich.write(" ".join(chaine))

            for k in ["X", "Z", "Q"]:
                fich.write(" " + k + "\n")
                long = 0
                for x in result[k]:
                    fich.write("{:13.2f}".format(x))
                    long += 1
                    if long == 5:
                        fich.write("\n")
                        long = 0

                if long != 0:
                    fich.write("\n")

            fich.write(" FIN\n")

    def get_for_lig(self, id_run):
        """
         Get value to create the lig file
         Args:
            :param id_run: run index
         Return :
            :return: return value to create the lig file
        """
        result = {}
        try:
            var = self.mdb.select("results_var", "type_res = 'opt'", "id", ["id", "var"])
            idz = var["id"][var["var"].index("Z")]
            idq = var["id"][var["var"].index("Q")]
            t_max = self.mdb.select_max(
                "time", "results", "var = {}  AND id_runs = {} ".format(idz, id_run)
            )
            if t_max is None:
                txt = ("No previous results to create the .lig file.")
                self.mess.add_mess("LigFile", "critic", txt)
                return None
            value = self.mdb.select(
                "results",
                "var = {} AND id_runs = {}  " "AND time = {}".format(idz, id_run, t_max),
                "pknum",
                ["val"],
            )
            result["Z"] = value["val"]
            value = self.mdb.select(
                "results",
                "var = {} AND id_runs = {} " "AND time = {}".format(idq, id_run, t_max),
                "pknum",
                ["val"],
            )
            result["Q"] = value["val"]

            value = self.mdb.select(
                "results_sect", "id_runs = {}".format(id_run), "pk", ["pk", "branch", "section"]
            )
            result["X"] = []
            result["section"] = []
            result["branche"] = []
            for idx, pk in enumerate(value["pk"]):
                result["X"] += pk
                result["section"] += value["section"][idx]
                result["branche"] += value["branch"] * len(pk)
            del value
        except Exception:
            txt = ("No results for initialisation")
            self.mess.add_mess("LigFile", "critic", txt)
            return None

        return result

    # ************   Mobil Gate FILE   ********************************************************************

    def create_mobil_gate_file(self):
        """
        create the mobile dam file (Fichier_Barrage_Mobile.txt)
        """

        info = self.mdb.select(
            "weirs", where="active_mob = true", list_var=["method_mob", "gid", "name"], order="gid"
        )
        if info:
            try:
                nomfich = os.path.join(self.dossier_file_masc, "Fichier_Barrage_Mobile.txt")

                if os.path.isfile(nomfich):
                    os.remove(nomfich)
                fich = open(nomfich, "w")

                for i, idw in enumerate(info["gid"]):
                    if info["method_mob"][i] == "1":
                        rows = self.mdb.select(
                            "weirs_mob_val",
                            where="id_weirs= {} AND (name_var='TIME' OR name_var='ZVAR')".format(
                                idw
                            ),
                            order="name_var, id_order",
                        )
                        if len(rows["id_weirs"]) > 0:
                            nbt = max(rows["id_order"]) + 1
                            if nbt < 501:
                                fich.write("{} {}\n".format(info["name"][i].replace(" ", "_"), nbt))
                                fich.write("methode 1\n")
                                fich.write("T(s)\n")
                                for j in range(nbt):
                                    fich.write("{} ".format(rows["value"][j]))
                                fich.write("\n")
                                fich.write("Zcrete(ngf)\n")
                                for j in range(nbt):
                                    fich.write("{} ".format(rows["value"][j + nbt]))
                                fich.write("\n")
                            else:
                                txt = (
                                    "Value number is superior to 500 "
                                    "for {} weirs.\n"
                                    "The weir is ignored.".format(info["name"][i])
                                )
                                self.mess.add_mess("MobGate_{}".format(info["name"][i]), "warning", txt)
                        else:
                            txt = (
                                "There aren't value in {} weirs".format(info["name"][i])
                            )
                            self.mess.add_mess("MobGate_{}".format(info["name"][i]), "warning", txt)

                    elif info["method_mob"][i] == "2":
                        rows = self.mdb.select(
                            "weirs_mob_val",
                            where="id_weirs= {} AND name_var!='TIME' AND name_var!='ZVAR'".format(
                                idw
                            ),
                        )
                        if len(rows["id_weirs"]) > 0:
                            fich.write("{} {}\n".format(info["name"][i].replace(" ", "_"), idw))
                            fich.write("methode 2\n")
                            fich.write("Zregulation Zbas Zhaut (m ngf)\n")
                            fich.write(
                                "{} {} {}\n".format(
                                    rows["value"][rows["name_var"].index("ZREG")],
                                    rows["value"][rows["name_var"].index("ZBAS")],
                                    rows["value"][rows["name_var"].index("ZHAUT")],
                                )
                            )
                            fich.write("Vabaissement Vrehaussement m/s\n")
                            fich.write(
                                "{} {}\n".format(
                                    rows["value"][rows["name_var"].index("VDESC")],
                                    rows["value"][rows["name_var"].index("VMONT")],
                                )
                            )
                    else:
                        txt = (
                            "There aren't value in {} weirs".format(info["name"][i])
                        )
                        self.mess.add_mess("MobGate_{}".format(info["name"][i]), "warning", txt)

                fich.close()
                self.mess.add_mess("MobGate", "info", "Creation the dam is done")

            except Exception as e:
                err = "Error: save the dam file"
                err += str(e)
                self.mess.add_mess("MobGateFile", "critic", err)
