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

import copy
import csv
import datetime
import gc
import json
import os
import re
import shutil
import subprocess
import sys
import json
import gc
import numpy as np
import copy

from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as et_parse

from qgis.PyQt.QtCore import qVersion
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .Function import TypeErrorModel
from .Function import del_symbol
from .Function import str2bool, del_accent, copy_dir_to_dir
from .Graphic.ClassResProfil import ClassResProfil
from .HydroLawsDialog import dico_typ_law
from .Structure.ClassMascStruct import ClassMascStruct
from .Structure.ClassPostPreFG import ClassPostPreFG
from .WaterQuality.ClassMascWQ import ClassMascWQ
from .api.ClassAPIMascaret import ClassAPIMascaret
from .ui.custom_control import ClassWarningBox

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *


class ClassMascaret:
    """ Class contain  model files creation and run model mascaret"""

    def __init__(self, main, rep_run=None):
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.iface = self.mgis.iface
        if not rep_run:
            self.dossierFileMasc = os.path.join(self.mgis.masplugPath,
                                                "mascaret")
        else:
            self.dossierFileMasc = rep_run

        if not os.path.isdir(self.dossierFileMasc):
            os.mkdir(self.dossierFileMasc)
        self.dossierFileMascOri = os.path.join(self.mgis.masplugPath,
                                               "mascaret_ori")
        self.dossierFile_bin = os.path.join(self.mgis.masplugPath, "bin")
        self.baseName = "mascaret"
        self.nomfichGEO = self.baseName + ".geo"
        self.box = ClassWarningBox()
        # state list
        self.listeState = ['Steady', 'Unsteady', 'Transcritical unsteady']
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]
        self.dico_basinnum = {}
        self.dico_linknum = {}
        self.wq = ClassMascWQ(self.mgis, self.dossierFileMasc)
        self.clmeth = ClassMascStruct(self.mgis)
        self.cond_api = self.mgis.cond_api
        self.save_res_struct = None

        self.err_model ={}
        self.err_model['timeLaw']=TypeErrorModel('timeLaw', ' ERROR : Law Time', stop= True)
        self.err_model['lInflowPos'] = TypeErrorModel('lInflowPos', 'WARNING : the inflow position')

    def creer_geo(self):
        """creation of gemoetry file"""
        try:
            nomfich = os.path.join(self.dossierFileMasc, self.baseName + '.geo')

            if os.path.isfile(nomfich):
                sauv = nomfich.replace(".geo", "_old.geo")
                shutil.move(nomfich, sauv)
            requete = self.mdb.select("profiles", "active", "abscissa")

            with open(nomfich, 'w') as fich:
                for i, nom in enumerate(requete["name"]):
                    branche = requete["branchnum"][i]
                    abs = requete["abscissa"][i]
                    temp_x = requete["x"][i]
                    temp_z = requete["z"][i]
                    lit_min_g = requete["leftminbed"][i]
                    lit_min_d = requete["rightminbed"][i]
                    if lit_min_d is not None and lit_min_g is None:
                        lit_min_g = 0.0

                    if branche and abs and temp_x and temp_z and lit_min_g \
                            and lit_min_d:
                        # tabX = list(map(lambda x: round(float(x), 2),
                        # temp_x.split()))
                        # tab_z = list(map(lambda x: round(float(x), 2),
                        # temp_z.split()))
                        tab_z = []
                        tab_x = []
                        # fct1 = lambda x: round(float(x), 2)
                        for var1, var2 in zip(temp_x.split(), temp_z.split()):
                            tab_x.append(self.around(var1))
                            tab_z.append(self.around(var2))

                        fich.write('PROFIL Bief_{0} {1} {2}\n'.format(branche,
                                                                      nom, abs))
                        for x, z in zip(tab_x, tab_z):
                            if lit_min_g <= x <= lit_min_d:
                                type = "B"
                            else:
                                type = "T"

                            fich.write(
                                '{0:.2f} {1:.2f} {2}\n'.format(x, z, type))
            self.mgis.add_info("Creation the geometry is done")
        except Exception as e:
            err = "Error: save the geometry .\n"
            err += str(e)
            self.mgis.add_info(err)
            raise Exception(err)

    def creer_geo_ref(self):
        # """creation of gemoetry file"""
        try:
            branche, nom = None, None
            nomfich = os.path.join(self.dossierFileMasc, self.baseName + '.geo')

            if os.path.isfile(nomfich):
                sauv = nomfich.replace(".geo", "_old.geo")
                shutil.move(nomfich, sauv)
            requete = self.mdb.select("profiles", "active", "abscissa")

            # To get projection and Line coordinated.
            vlayer = self.mdb.make_vlayer(self.mdb.register['profiles'])
            vlayer_dp = vlayer.dataProvider()
            vlayer_crs = vlayer_dp.crs()
            vlayer_crs_str = vlayer_crs.authid()

            # Write the File
            with open(nomfich, 'w') as fich:

                fich.write('#  DATE : {0:%d/%m/%Y %H:%M:%S}\n'
                           '#  PROJ. : {1}\n'.format(datetime.date.today(),
                                                     vlayer_crs_str))

                iter = vlayer.getFeatures()
                feature_list = [v for v in iter]
                name_feature = [v['name'] for v in feature_list]
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

                        if branche is not None and abs is not None \
                                and temp_x is not None \
                                and temp_z is not None \
                                and lit_min_g is not None \
                                and lit_min_d is not None:
                            tab_z = []
                            tab_x = []
                            # fct1 = lambda x: round(float(x), 2)
                            for var1, var2 in zip(temp_x.split(),
                                                  temp_z.split()):
                                tab_x.append(self.around(var1))
                                tab_z.append(self.around(var2))
                            points = geom.asMultiPolyline()[0]
                            (cood1X, cood1Y) = points[0]
                            (cood2X, cood2Y) = points[1]
                            cood_axe_x = cood1X + (cood2X - cood1X) / 2.
                            cood_axe_y = cood1Y + (cood2Y - cood1Y) / 2.

                            fich.write(
                                'PROFIL Bief_{0} {1} {2} {3} {4} {5} {6} '
                                'AXE {7} {8}\n'.format(
                                    branche, nom,
                                    abs,
                                    cood1X, cood1Y,
                                    cood2X, cood2Y,
                                    cood_axe_x,
                                    cood_axe_y))
                            dif = tab_x[-1] - geom.length()
                            if dif > 0:
                                dif += 1
                                # garde line centree
                                geom = geom.extendLine(dif / 2., dif / 2.)
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
                                    '{0:.2f} {1:.2f} {2} {3} '
                                    '{4}\n'.format(x, z,
                                                   type,
                                                   dpoint[
                                                       0],
                                                   dpoint[
                                                       1]))

            self.mgis.add_info("Creation the geometry is done")
        except Exception as e:
            err = "Error: save the geometry {}-{}".format(branche, nom)
            err += str(e)
            self.mgis.add_info(err)
            raise Exception(err)
            # Fonction de creation du fichier .casier avec la loi surface-volume

    def creer_geo_casier(self):
        try:
            nomfich = os.path.join(self.dossierFileMasc,
                                   self.baseName + '.casier')

            if os.path.isfile(nomfich):
                sauv = nomfich.replace(".casier", "_old.casier")
                shutil.move(nomfich, sauv)

            casiers = self.mdb.select("basins", "active ORDER BY basinnum")

            with open(nomfich, 'w') as fich:
                for i, nom in enumerate(casiers["name"]):
                    fich.write('CASIER {0}\n'.format(nom))
                    cotes = casiers["level"][i]
                    surfaces = casiers["area"][i]
                    volumes = casiers["volume"][i]
                    for j, cote in enumerate(cotes.split()):
                        fich.write(
                            '{0:.2f} {1:.2f} {2:.2f}\n'.format(
                                float(cotes.split()[j]),
                                float(surfaces.split()[j]),
                                float(volumes.split()[j])))

            self.mgis.add_info("Creation of the basin file is done")
        except Exception as e:
            err = "Error: save the basin file"
            err += str(e)
            self.mgis.add_info(err)
            raise Exception(err)

            # Fonction de remplacement des None de la liste par la valeur
            # remplaceNone
            # cad -1 ou -1.0 pour le moteur Mascaret

    def fmt_sans_none(self, liste, remplace_none):
        liste = [remplace_none if var is None else var for var in liste]
        return " ".join([str(var) for var in liste])

        # Fonction de transformation de la liste de numeros basin/link sous
        # Qgis en une chaine de numeros pour le moteur Mascaret

    def fmt_num_basin(self, liste, dico_num, remplace_none):
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
                    txterr = 'Error, the basin {} does not exist'.format(num_qgis)
                    self.mgis.add_info(txterr)
                    raise KeyError(txterr)

        return " ".join([str(var) for var in liste_num_masca])

        # Fonction de calcul du planimetrage entre 2 niveaux de la loi surface
        # volume du casier

    def fmt_plani_casier(self, liste):
        liste_plani = []
        for chaine_z in liste:
            try:
                liste_z = chaine_z.split()
                # Calcul des parties entieres et decimale de la planimetrie
                plani_entier = int((float(liste_z[1]) - float(liste_z[0])) // 1)
                liste_plani.append(str(plani_entier))
                plani_decimale = int(
                    (float(liste_z[1]) - float(liste_z[0])) % 1)
                if plani_decimale > 0:
                    self.mgis.add_info(
                        "Simulation Error: the basin planimetry has "
                        "to be an integer value")
            except:
                self.mgis.add_info(
                    "Simulation Error: the basin planimetry is not correct")
        return " ".join([str(var) for var in liste_plani])

    def indent(self, elem, level=0):
        """indentation auto"""
        i = '\n' + level * '  '
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + '  '
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)

            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        elif level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

    # def geom_obj_toname(self, nom, type_):
    #     """ get name law"""
    #     condition = "geom_obj='{0}' AND " \
    #                 "id_law_type={1} AND active".format(nom, type_)
    #
    #     inf_law = self.mdb.select_one('law_config', condition)
    #     if inf_law:
    #         if 'name' in inf_law.keys():
    #             return inf_law['name']
    #
    #     return nom

    def creer_xcas(self, noyau):
        """To create xcas file"""
        dict_lois = {}
        # try:
        fichier_sortie = os.path.join(self.dossierFileMasc,
                                      self.baseName + ".xcas")
        extr_toloi = {0: 6, 1: 1, 2: 2, 3: 4, 4: 5, 5: 4, 8: 3, 6: 6, 7: 7}
        abaque_toloi = {1: 6, 2: 4, 5: 2, 6: 5, 7: 5, 8: 7}

        # création du fichier xml
        fichier_cas = Element("fichier_cas")

        cas = SubElement(fichier_cas, "parametresCas")

        sql = "SELECT {0} FROM {1}.{2} WHERE parametre='presenceTraceurs';"
        rows = self.mdb.run_query(
            sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        if rows is not None:
            tracer = str2bool(rows[0][0])
        else:
            tracer = False
        # requête pour récupérer les paramètres
        sql = "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} " \
              "WHERE gui_type = 'parameters' ORDER BY id;"
        rows = self.mdb.run_query(
            sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, b1, b2 in rows:
            # self.mgis.add_info("valeur : {0},  param : {1}  ,  b1 : {2} , b2:#\
            #  {3}".format(valeur, param, b1, b2))
            if b1:
                try:
                    cas.find(b1).text
                except:
                    balise1 = SubElement(cas, b1)
                # if not cas.find(b1):
                #     balise1 = SubElement(cas, b1)

                if b2:
                    try:
                        balise1.find(b2).text
                    except:
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
        noeuds = self.mdb.select("extremities", "type=10", "active")
        libres = self.mdb.select("extremities", "type!=10 ", "active")
        pertescharg = self.mdb.select("hydraulic_head", "active", "abscissa")
        profils = self.mdb.select("profiles", "active", "abscissa")
        prof_seuil = self.mdb.select("profiles", "NOT active", "abscissa")
        seuils = self.mdb.select("weirs", "active", "abscissa")
        sorties = self.mdb.select("outputs", "active", "abscissa")
        zones = self.mdb.zone_ks()
        planim = self.mdb.planim_select()
        maillage = self.mdb.maillage_select()
        dico_str = self.mdb.select('struct_config', "active", "abscissa")
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
                self.mgis.add_info('Checked if the profiles are activated.')

        dict_noeuds = {}
        dict_libres = {"nom": [], "num": [], "extrem": [], "typeCond": [],
                       "typeCond_tr": [], "law_wq": []}
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
                dict_libres["typeCond_tr"].append(
                    libres["tracer_boundary_condition_type"][i])
                dict_libres["law_wq"].append(libres["law_wq"][i])

                dict_lois[d] = {'type': extr_toloi[type],
                                'formule': formule,
                                'valeurperm': libres["firstvalue"][i],
                                'couche': 'extremites'}

            if libres and f in libres["name"]:
                i = libres["name"].index(f)
                type = libres["type"][i]
                formule = libres["method"][i]
                dict_libres["nom"].append(libres["name"][i])
                dict_libres["typeCond"].append(type)
                dict_libres["num"].append(len(dict_libres["nom"]))
                dict_libres["extrem"].append(n * 2)
                dict_libres["typeCond_tr"].append(
                    libres["tracer_boundary_condition_type"][i])
                dict_libres["law_wq"].append(libres["law_wq"][i])
                dict_lois[f] = {'type': extr_toloi[type],
                                'formule': formule,
                                'valeurperm': libres["firstvalue"][i],
                                'couche': 'extremites'}
        # Zones
        nb_pas = 0

        liste_stock = {"numProfil": [],
                       'limGauchLitMaj': [],
                       'limDroitLitMaj': []}

        tab = zip(profils["abscissa"],
                  profils["x"],
                  profils["z"],
                  profils["leftstock"],
                  profils["rightstock"],
                  profils["branchnum"],
                  profils["planim"])

        for j, (abs, x, z, sg, sd, n, planim_val) in enumerate(tab):

            try:
                xx = [float(var) for var in x.split()]
                zz = [float(var) for var in z.split()]
                diff = max(zz) - min(zz)
            except:
                self.mgis.add_info("Check the {} profile if it's ok ".format(
                    profils["name"][j]))
                raise Exception("Check the {} profile if it's ok ".format(
                    profils["name"][j]))
                return dict_lois

            try:
                nb_pas = max(int(diff / float(planim_val)) + 1, nb_pas)
            except:
                self.mgis.add_info("Check planim ")

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
                dict_lois[seuils["name"][i]] = {'type': abaque_toloi[type],
                                                'couche': 'seuils'}

        for i, nom in enumerate(apports["name"]):
            if nom not in dict_lois.keys():
                dict_lois[nom] = {'type': 1,
                                  'formule': apports['method'][i],
                                  'valeurperm': apports["firstvalue"][i],
                                  'couche': 'apports'}

        for i, nom in enumerate(deversoirs["name"]):
            if nom not in dict_lois.keys() and deversoirs["type"][i] == 2:
                dict_lois[nom] = {'type': 4, 'couche': 'deversoirs'}

        # Géométrie du réseau
        reseau = cas.find("parametresGeometrieReseau")
        # liste des Branches
        liste_branch = SubElement(reseau, "listeBranches")
        SubElement(liste_branch, "nb").text = str(len(numero))
        SubElement(liste_branch, "numeros").text = self.fmt(numero)
        SubElement(liste_branch, "abscDebut").text = self.fmt(
            branches["abscdebut"])
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
        SubElement(extr_libres, "numExtrem").text = self.fmt(
            dict_libres["extrem"])

        noms = SubElement(extr_libres, "noms")
        for nom in liste:
            SubElement(noms, "string").text = nom

        SubElement(extr_libres, "typeCond").text = self.fmt(
            dict_libres["typeCond"])
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
        SubElement(confluents, "nbConfluents").text = str(
            len(dict_noeuds.keys()))
        confluent = SubElement(confluents, "confluents")
        for k in sorted(dict_noeuds.keys()):
            struct = SubElement(confluent, "structureParametresConfluent")
            l = len(dict_noeuds[k])
            SubElement(struct, "nbAffluent").text = str(l)
            SubElement(struct, "nom").text = k
            i = noeuds["name"].index(k)
            a_en = ["abscissa", "ordinates", "angles"]
            for kk, a in enumerate(["abscisses", "ordonnees", "angles"]):
                if noeuds[a_en[kk]][i] is None or l != 3:

                    SubElement(struct, a).text = " 0.0" * l
                else:
                    SubElement(struct, a).text = noeuds[a_en[kk]][i]

        # Planimétrage et maillage
        planimaill = SubElement(cas, "parametresPlanimetrageMaillage")
        SubElement(planimaill, "methodeMaillage").text = '5'

        planim_e = SubElement(planimaill, "planim")
        SubElement(planim_e, 'nbPas').text = str(nb_pas)
        SubElement(planim_e, 'nbZones').text = str(len(planim["pas"]))
        SubElement(planim_e, 'valeursPas').text = self.fmt(planim['pas'])
        SubElement(planim_e, 'num1erProf').text = self.fmt(planim['min'])
        SubElement(planim_e, 'numDerProf').text = self.fmt(planim['max'])

        maillage_e = SubElement(planimaill, "maillage")
        SubElement(maillage_e, 'modeSaisie').text = '2'
        SubElement(maillage_e, 'sauvMaillage').text = 'false'
        maillage_c = SubElement(maillage_e, 'maillageClavier')
        SubElement(maillage_c, 'nbSections').text = '0'
        SubElement(maillage_c, 'nbPlages').text = str(len(maillage["pas"]))
        SubElement(maillage_c, 'num1erProfPlage').text = self.fmt(maillage['min'])
        SubElement(maillage_c, 'numDerProfPlage').text = self.fmt(maillage['max'])
        SubElement(maillage_c, 'pasEspacePlage').text = self.fmt(maillage['pas'])
        SubElement(maillage_c, 'nbZones').text = '0'

        # Singularites
        singularite = SubElement(cas, "parametresSingularite")

        # Seuils
        SubElement(singularite, "nbSeuils").text = str(len(seuils["name"]))

        if len(seuils["name"]) > 0:
            e_tseuils = SubElement(singularite, "seuils")

        liste = ["type", "numBranche", "abscisse", "coteCrete", "coteCreteMoy",
                 "coteRupture", "coeffDebit", "largVanne", "epaisseur"]
        liste_en = ["type", "branchnum", "abscissa", "z_crest",
                    "z_average_crest",
                    "z_break", "flowratecoeff", "wide_floodgate", "thickness"]

        for i, nom in enumerate(seuils["name"]):
            struct = SubElement(e_tseuils, "structureParametresSeuil")
            SubElement(struct, "nom").text = nom
            for kk, l in enumerate(liste):
                if seuils[liste_en[kk].lower()][i] is None:
                    SubElement(struct, l).text = '-0'
                else:
                    SubElement(struct, l).text = str(
                        seuils[liste_en[kk].lower()][i])

            if seuils["type"][i] not in (3, 4):
                SubElement(struct, "numLoi").text = str(
                    sorted(dict_lois.keys()).index(nom) + 1)
            else:
                SubElement(struct, "numLoi").text = '-0'

            if seuils["type"][i] != 3:
                SubElement(struct, "nbPtLoiSeuil").text = '-0'
            else:
                try:
                    i = prof_seuil["name"].index(nom)
                    long = len(prof_seuil['x'][i].split())
                    SubElement(struct, "nbPtLoiSeuil").text = str(long)
                    # SubElement(struct, "abscTravCrete").text = prof_seuil['x'][i]
                    # SubElement(struct, "cotesCrete").text = prof_seuil['z'][i]
                    # traitment profil because of too many significant number
                    new_profx = ' '.join([str(round(float(vvv), 3))
                                          for vvv in
                                          prof_seuil['x'][i].split()])

                    SubElement(struct, "abscTravCrete").text = new_profx
                    new_profz = ' '.join([str(round(float(vvv), 3))
                                          for vvv in
                                          prof_seuil['z'][i].split()])
                    SubElement(struct, "cotesCrete").text = new_profz


                except:
                    msg = 'Profil de crete introuvable pour {}'
                    QMessageBox.warning(None, 'Message', msg.format(nom))
                    return

            SubElement(struct, "gradient").text = "-0"

        # Pertes de charges
        if len(pertescharg["name"]) > 0:
            pertes = SubElement(singularite, "pertesCharges")
            SubElement(pertes, "nbPerteCharge").text = str(
                len(pertescharg["name"]))
            SubElement(pertes, "numBranche").text = self.fmt(
                pertescharg["branchnum"])
            SubElement(pertes, "abscisses").text = self.fmt(
                pertescharg["abscissa"])
            SubElement(pertes, "coefficients").text = self.fmt(
                pertescharg["coeff"])

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

        SubElement(e_tapports, "numBranche").text = self.fmt(
            apports["branchnum"])
        if self.check_none(apports["abscissa"]):
            self.mgis.add_info(
                'Warning : Geometric object for lateral inflows is not found')
        SubElement(e_tapports, "abscisses").text = self.fmt(apports["abscissa"])
        if self.check_none(apports["length"]):
            self.mgis.add_info(
                'Warning : Lenght for lateral inflows is not found')
        SubElement(e_tapports, "longueurs").text = self.fmt(apports["length"])
        temp = [sorted(dict_lois.keys()).index(nom) + 1 for nom in
                apports["name"]]
        SubElement(e_tapports, "numLoi").text = self.fmt(temp)

        # Déversoirs
        devers_late = SubElement(apport_dever, "devers_late")
        SubElement(devers_late, "nbDeversoirs").text = str(
            len(deversoirs["name"]))
        noms = SubElement(devers_late, "noms")
        for nom in deversoirs["name"]:
            SubElement(noms, "string").text = nom

        SubElement(devers_late, "type").text = self.fmt(deversoirs["type"])

        l_en = ["branchnum", "abscissa", "length", "z_crest", "flowratecoef"]
        for kk, l in enumerate(
                ["numBranche", "abscisse", "longueur", "coteCrete",
                 "coeffDebit"]):
            SubElement(devers_late, l).text = self.fmt(
                deversoirs[l_en[kk].lower()])

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
        SubElement(frottement, "loi").text = '1'
        SubElement(frottement, "nbZone").text = str(len(zones["zoneabsstart"]))
        SubElement(frottement, "numBranche").text = self.fmt(zones["branch"])
        l_en = ['zoneabsstart', 'zoneabsend', 'minbedcoef', 'majbedcoef']
        for kk, l in enumerate(
                ["absDebZone", "absFinZone", "coefLitMin", "coefLitMaj"]):
            SubElement(frottement, l).text = self.fmt(zones[l_en[kk].lower()])

        # stockage
        zone_stockage = SubElement(calage, "zoneStockage")
        SubElement(zone_stockage, "loi").text = '1'
        n = len(liste_stock["numProfil"])
        SubElement(zone_stockage, "nbProfils").text = str(n)
        for l in ["numProfil", "limGauchLitMaj", "limDroitLitMaj"]:
            SubElement(zone_stockage, l).text = self.fmt(liste_stock[l])

        # Lois hydrauliques
        hydrauliques = SubElement(cas, "parametresLoisHydrauliques")

        for nom in dict_lois.keys():
            if nom in libres["name"] and (
                    dict_lois[nom]['type'] == 6 or \
                    dict_lois[nom]['type'] == 7):
                # les types sont ceux de
                if dict_lois[nom]['type'] == 6:
                    # TODO and noyau!='transcritical'
                    dict_lois[nom]['type'] = 1
                    self.mgis.add_info(
                        'The  {} law changes type 6 => 1'.format(nom), dbg=True)
                elif dict_lois[nom]['type'] == 7:
                    dict_lois[nom]['type'] = 2

                    self.mgis.add_info(
                        'The  {} law changes type 7 => 2'.format(nom), dbg=True)

        nb = len(dict_lois.keys())
        SubElement(hydrauliques, "nb").text = str(nb)
        lois = SubElement(hydrauliques, "lois")

        for nom in sorted(dict_lois.keys()):
            struct = SubElement(lois, "structureParametresLoi")
            SubElement(struct, "nom").text = nom
            SubElement(struct, "type").text = str(dict_lois[nom]['type'])
            donnees = SubElement(struct, "donnees")
            SubElement(donnees, "modeEntree").text = '1'
            # WARNING The law must be sorted because of the order of law must be the same than order File.law for API
            # SubElement(donnees, "fichier").text = '{}.loi'.format(
            #    del_symbol(self.geom_obj_toname(nom, dict_lois[nom]['type'])))
            SubElement(donnees, "fichier").text = '{}.loi'.format(del_symbol(nom))
            SubElement(donnees, "uniteTps").text = '-0'
            SubElement(donnees, "nbPoints").text = '-0'
            SubElement(donnees, "nbDebitsDifferents").text = '-0'

        # impression résultats
        init = cas.find("parametresImpressionResultats")
        stockage = init.find("stockage")
        SubElement(stockage, 'nbSite').text = str(len(sorties["name"]))
        SubElement(stockage, 'branche').text = self.fmt(sorties["branchnum"])
        SubElement(stockage, 'abscisse').text = self.fmt(sorties["abscissa"])
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
        self.mgis.add_info("Save the Xcas file is done")
        # ****** XCAS initialisation **********
        temps_max = 3600
        np_pas_temps_init = 2
        dt_init = temps_max / np_pas_temps_init

        param_cas = fichier_cas.find('parametresCas')
        parametres_generaux = param_cas.find('parametresGeneraux')
        fich_xcas = '{}_init.xcas'.format(self.baseName)
        parametres_generaux.find('fichMotsCles').text = fich_xcas
        parametres_generaux.find('code').text = '1'
        parametres_generaux.find('presenceCasiers').text = 'false'
        parametres_temporels = param_cas.find('parametresTemporels')
        parametres_temporels.find('pasTemps').text = '{}'.format(dt_init)
        parametres_temporels.find('critereArret').text = '2'
        parametres_temporels.find('nbPasTemps').text = '{}'.format(
            np_pas_temps_init)
        parametres_temporels.find('tempsMax').text = '{}'.format(temps_max)
        parametres_temporels.find('pasTempsVar').text = 'false'
        geom_reseau = param_cas.find('parametresGeometrieReseau')
        type_cond = geom_reseau.find('extrLibres').find('typeCond')
        type_cond.text = type_cond.text.replace('4', '2')
        # type_cond.text = type_cond.text.replace('4', '2').replace('6',
        #                                                           '1').replace(
        #     '7', '2')
        type_cond.text = type_cond.text.replace('6', '1').replace('7', '2')
        lois_hydrauliques = param_cas.find('parametresLoisHydrauliques')
        lois = lois_hydrauliques.find('lois')
        for child in lois:
            # # tarage loi
            if child.find('type').text == '5':
                child.find('type').text = '2'
            donnee = child.find('donnees').find('fichier')
            temp = donnee.text.split('.')

            donnee.text = '{}_init.loi'.format(
                del_symbol(temp[0]))

        initiales = param_cas.find('parametresConditionsInitiales')
        initiales.find('repriseEtude').find('repriseCalcul').text = 'false'
        initiales.find('ligneEau').find('LigEauInit').text = 'false'
        resultats = param_cas.find('parametresImpressionResultats')
        fich_opt = '{}_init.opt'.format(self.baseName)
        resultats.find('resultats').find('fichResultat').text = fich_opt
        resultats.find('impression').find('impressionCalcul').text = 'true'
        resultats.find('pasStockage').find('premPasTpsStock').text = '1'
        resultats.find('pasStockage').find('pasStock').text = '1'
        resultats.find('pasStockage').find('pasImpression').text = '1'
        resultats.find('stockage').find('option').text = '1'
        # tracers
        if tracer:
            parametres_tracer = param_cas.find('parametresTraceur')
            parametres_tracer.find('presenceTraceurs').text = 'false'

        self.indent(fichier_cas)
        arbre = ElementTree(fichier_cas)
        arbre.write(os.path.join(self.dossierFileMasc, fich_xcas))

        self.mgis.add_info("Save the init. Xcas file  is done")
        # except Exception as e:
        #     self.mgis.add_info("Error: save Xcas file")
        #     self.mgis.add_info('error: {}'.format(e))

        # add struct before harminization
        dict_lois_tmp = dict_lois.copy()
        dico_loi_struct = {}
        for name in dict_lois_tmp.keys():
            if name in loi_struct['laws']:
                dico_loi_struct[name] = dict_lois[name]
                idx = loi_struct['laws'].index(name)
                dico_loi_struct[name]['id_config'] = loi_struct['id_config'][
                    idx]
                del dict_lois[name]

        return dict_lois, dico_loi_struct

    def check_basin(self, liaisons, casiers,dico_basinnum):
        """
        Check if links is correctly defined
        """
        check_typ_link = {1 :['level','width','weirdischargecoef'],
                         2 : ['level','width','length','roughness'],
                         3 : ['level','length','crosssection','headlosscoef'],
                         4 : ['level','width','crosssection','weirdischargecoef',
                               'pipedischargecoef','culverttype',],}
        for idl, num in enumerate(liaisons["linknum"]):
            nat = liaisons["nature"][idl]
            tupl = liaisons["type"][idl]
            abs = liaisons["abscissa"][idl]
            stb = liaisons["basinstart"][idl]
            level = liaisons["level"][idl]
            ste = liaisons["basinend"][idl]
            #check "Basin-Reach" have an abscissa
            if nat == 1 and (abs is None or abs == -1):
                self.mgis.add_info('*** Error: The "Basin-Reach" type link {} '
                                   'does not have an abscissa on the reach'.format(num))
            # check coherent between variable and typ
            for key in check_typ_link[tupl]:
                val = liaisons[key][idl]
                if val is None:
                    self.mgis.add_info('*** Error: Link {} is not type coherent.'
                                       ''.format(num))
                    break

            #check level for the start basin
            if stb in dico_basinnum.keys():
                numc = casiers["basinnum"][dico_basinnum[stb]-1]
                init_level = casiers["initlevel"][dico_basinnum[stb]-1]
                if  level < init_level:
                    self.mgis.add_info('*** Warning: Please note that the elevation of '
                                       'the upstream basin {} is higher than the elevation of the link {}. \n'
                                       'This can generate an artificial flow.'.format(numc, num))
            else:
                self.mgis.add_info('*** Error: The link {} '
                                   'does not have "Basin number start"'.format(num))
            # check if "basinend" is existed  before  check level
            if ste is None or ste == -1 :
                continue
            # check level for the end basin
            if ste in dico_basinnum.keys():
                # -1 because of Python begin by 0
                numc = casiers["basinnum"][dico_basinnum[ste]-1]
                init_level = casiers["initlevel"][dico_basinnum[ste]-1]
                if level < init_level:
                    self.mgis.add_info('*** Warning: Please note that the elevation of '
                                       'the downtream basin {} is higher than the elevation of the link {}. \n'
                                       'This can generate an artificial flow.'.format(numc, num))
            else:
                self.mgis.add_info('*** Error: The link {} '
                                   'does not have "Basin number End"'.format(num))



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
        self.check_basin(liaisons, casiers,dico_basinnum_creat)
        # Creation des lignes a ajouter dans Xcas
        cas = fichier_cas.find('parametresCas')
        casier = SubElement(cas, "parametresCasier")
        SubElement(casier, "nbCasiers").text = str(len(casiers["name"]))
        SubElement(casier, "optionPlanimetrage").text = self.fmt_plani_casier(
            casiers["level"])
        SubElement(casier, "optionCalcul").text = "1"  # Todo
        SubElement(casier,
                   "fichierGeomCasiers").text = "mascaret.casier"  # Todo
        SubElement(casier, "cotesInitiale").text = self.fmt_sans_none(
            casiers["initlevel"], '-1.0')
        # Liaisons (champs non listes = active et linknum)
        et_liaisons = SubElement(casier, "liaisons")
        SubElement(et_liaisons, "nbLiaisons").text = str(len(liaisons["name"]))
        SubElement(et_liaisons, "types").text = self.fmt_sans_none(
            liaisons["type"], '-1.0')
        SubElement(et_liaisons, "nature").text = self.fmt_sans_none(
            liaisons["nature"], '-1.0')
        SubElement(et_liaisons, "cote").text = self.fmt_sans_none(
            liaisons["level"], '-1.0')
        SubElement(et_liaisons, "largeur").text = self.fmt_sans_none(
            liaisons["width"], '-1.0')
        SubElement(et_liaisons, "longueur").text = self.fmt_sans_none(
            liaisons["length"], '-1.0')
        SubElement(et_liaisons, "rugosite").text = self.fmt_sans_none(
            liaisons["roughness"], '-1.0')
        SubElement(et_liaisons, "section").text = self.fmt_sans_none(
            liaisons["crosssection"], '-1.0')
        SubElement(et_liaisons, "coefPerteCharge").text = self.fmt_sans_none(
            liaisons["headlosscoef"], '-1.0')
        SubElement(et_liaisons, "coefDebitSeuil").text = self.fmt_sans_none(
            liaisons["weirdischargecoef"], '-1.0')
        SubElement(et_liaisons, "coefActivation").text = self.fmt_sans_none(
            liaisons["activationcoef"], '-1.0')
        SubElement(et_liaisons, "coefDebitOrifice").text = self.fmt_sans_none(
            liaisons["pipedischargecoef"],
            '-1.0')
        SubElement(et_liaisons, "typeOrifice").text = self.fmt_sans_none(
            liaisons["culverttype"], '-1')
        SubElement(et_liaisons, "numCasierOrigine").text = self.fmt_num_basin(
            liaisons["basinstart"],
            dico_basinnum_creat, '-1')
        SubElement(et_liaisons, "numCasierFin").text = self.fmt_num_basin(
            liaisons["basinend"], dico_basinnum_creat,
            '-1')
        SubElement(et_liaisons, "numBiefAssocie").text = self.fmt_sans_none(
            liaisons["branchnum"], '-1')
        SubElement(et_liaisons, "abscBief").text = self.fmt_sans_none(
            liaisons["abscissa"], '-1.0')

    def add_wq_xcas(self, fichier_cas, noyau, dict_libres):
        """Modification of xcas for Water Quality"""
        # requête pour récupérer les paramètres
        cas = fichier_cas.find('parametresCas')
        sql = "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} " \
              "WHERE gui_type = 'tracers' ORDER BY id;"

        rows = self.mdb.run_query(
            sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, b1, b2 in rows:
            if param == "fichMeteoTracer":
                sql = "SELECT {0} FROM {1}.{2} WHERE parametre = 'fichmeteo' ;"
                wow = self.mdb.run_query(
                    sql.format(noyau, self.mdb.SCHEMA, "parametres"),
                    fetch=True)
                if str2bool(wow[0][0]) is False:
                    continue

            if b1:
                try:
                    cas.find(b1).text
                except:
                    balise1 = SubElement(cas, b1)
                if b2:
                    try:
                        balise1.find(b2).text
                    except:
                        balise2 = SubElement(balise1, b2)

                    par = SubElement(balise2, param)

                    par.text = valeur.lower()
                else:
                    par = SubElement(balise1, param)
                    par.text = valeur.lower()

        # use dictLibres to have only extremities and not junction

        cas = cas.find('parametresTraceur')
        lateral = self.mdb.select('tracer_lateral_inflows', order='abscissa')

        list_loi = list(dict_libres["law_wq"])
        dico_s = {}
        dico_ex = {}

        for i, nom in enumerate(list_loi):
            dico_ex[i] = {'name': nom, 'type': dict_libres["typeCond_tr"][i]}

        for i, cond in enumerate(lateral['active']):
            if cond:
                dico_s[i] = {'name': lateral['name'][i],
                             'name_law': lateral['law_wq'][i],
                             'typs': lateral['typesources'][i],
                             'numb': lateral['branchnum'][i],
                             'abs': lateral['abscissa'][i],
                             'leng': lateral['length'][i]
                             }
                list_loi.append(lateral['law_wq'][i])
        if not len(list_loi) > 0:
            self.mgis.add_info("Please enter water quality laws")
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
                typ.append(dico_s[num]['typs'])
                numb.append(dico_s[num]['numb'])
                abs.append(dico_s[num]['abs'])
                leng.append(dico_s[num]['leng'])
                numl.append(list_loi.index(dico_s[num]['name_law']) + 1)
        else:
            typ = ['-0']
            numb = ['-0']
            abs = ['-0']
            leng = ['-0']
            numl = ['-0']
        SubElement(tracer_source, "typeSources").text = self.fmt(typ)
        SubElement(tracer_source, "numBranche").text = self.fmt(numb)
        if self.check_none(abs):
            self.mgis.add_info(
                'Warning : Geometric object for tracer lateral inflows '
                'is not found')
        SubElement(tracer_source, "abscisses").text = self.fmt(abs)
        if self.check_none(leng):
            self.mgis.add_info(
                'Warning : Lenght for tracer lateral inflows is not found')
        SubElement(tracer_source, "longueurs").text = self.fmt(leng)
        SubElement(tracer_source, "numLoi").text = self.fmt(numl)

        # Lois traceur
        tracer_law = SubElement(cas, "parametresLoisTraceur")
        nb = len(list_loi)
        SubElement(tracer_law, "nbLoisTracer").text = str(nb)
        lois = SubElement(tracer_law, "loisTracer")
        if nb > 0:
            for name in list_loi:
                struct = SubElement(lois, "structureSParametresLoiTraceur")
                SubElement(struct, "nom").text = name
                SubElement(struct, "modeEntree").text = '1'
                SubElement(struct, "fichier").text = '{}_tra.loi'.format(
                    del_symbol(name.lower()))
                SubElement(struct, "uniteTps").text = '-0'
                SubElement(struct, "nbPoints").text = '-0'

        # modif extremite info
        typ = [0, 0]
        numl = [0, 0]
        list_k = list(dico_ex.keys())
        if len(list_k):
            for i, num in enumerate(sorted(list_k)):
                typ[i] = dico_ex[num]['type']
                numl[i] = list_loi.index(dico_ex[num]['name']) + 1
        else:
            typ = ['-0']
            numl = ['-0']
        general = fichier_cas.find('parametresCas')
        cas = general.find('parametresTraceur')
        initiales = cas.find('parametresConditionsLimitesTraceur')
        initiales.find("typeCondLimTracer").text = self.fmt(typ)
        initiales.find("numLoiCondLimTracer").text = self.fmt(numl)

        return True

    def modif_seuil(self, seuil, dico_str):

        liste = ["type", "branchnum", "abscissa", "z_crest", "z_average_crest",
                 "z_break", "flowratecoeff", "wide_floodgate", "thickness"]
        loi_struct = {'laws': [], 'id_config': []}
        if len(seuil["name"]) == 0:
            seuils = {'name': [], }
            for ls in liste:
                seuils[ls] = []

        for i, name in enumerate(dico_str['name']):
            seuil['name'].append(del_accent(name))
            loi_struct['laws'].append(del_accent(name))
            loi_struct['id_config'].append(dico_str['id'][i])
            for ls in liste:
                if ls == "type":
                    seuil[ls].append(self.typ_struct(dico_str['method'][i]))
                elif ls == 'abscissa':
                    seuil[ls].append(dico_str['abscissa'][i])
                elif ls == "branchnum":
                    seuil[ls].append(dico_str['branchnum'][i])
                elif ls == 'z_break':
                    seuil[ls].append(99999)
                elif ls == 'z_crest':
                    where = "id_config ='{}'".format(dico_str['id'][i])
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
        fich_entree = os.path.join(self.dossierFileMasc, xcasfile)
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

    def creer_loi(self, nom, tab, type_, init=False):
        # nom = self.geom_obj_toname(nom, type_)
        if init:
            nom = nom + '_init'
        with open(os.path.join(self.dossierFileMasc, del_symbol(nom) + '.loi'),
                  'w') as fich:
            fich.write('# ' + nom + '\n')
            if type_ == 1:
                fich.write('# Temps (S) Debit\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {flowrate:.6f}\n'

                #     self.mgis.add_info("\n", dbg=True)
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t
                #                       Flow Rate :{2}"
                #                       .format(nom, tab["temps"], tab["debit"]), dbg=True)

            elif type_ == 2:
                fich.write('# Temps (S) Cote\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z:.6f}\n'

                #     self.mgis.add_info("\n", dbg=True)
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t
                #                       Water Level :{2}"
                #                       .format(nom, tab["temps"],tab["cote"]), dbg=True)
            elif type_ == 3:
                fich.write('# Temps (S) Cote Debit\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z:.6f} {flowrate:.6f}\n'
                #     self.mgis.add_info("\n", dbg=True)
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t
                #                   Water Level :{2}\n \t Flow Rate {3}"
                #                       .format(nom, tab["temps"],
                # tab["cote"],tab["debit"]), dbg=True)
            elif type_ == 4:
                fich.write('# Debit Cote\n')
                chaine = ' {flowrate:.3f} {z:.6f}\n'
                #     self.mgis.add_info("\n", dbg=True)
                #     self.mgis.add_info("{0} :\n \t Flow Rate {2}\n
                #                       \t Water Level :{1}"
                #                       .format(nom, tab["cote"],tab["debit"]), dbg=True)
            elif type_ == 5:
                fich.write('# Cote Debit\n')
                chaine = ' {z:.6f} {flowrate:.6f}\n'
                #     self.mgis.add_info("\n", dbg=True)
                #     self.mgis.add_info("{0} :\n \t Water Level :{1}\n
                #                       \t Flow Rate {2}"
                #                       .format(nom, tab["cote"],tab["debit"]), dbg=True)
            elif type_ == 6:
                fich.write('# Debit Cote_Aval Cote_Amont\n')
                chaine = ' {flowrate:.6f} {z_downstream:.6f} {z_upstream:.6f}\n'
                #     self.mgis.add_info("\n", dbg=True)
                #     self.mgis.add_info("{0} :\n \t Upstream Water Level{1}\n
                #                          \t  Downstream Water Level :{2}"
                #                       .format(nom, tab["cote_amont"],
                #                       tab["cote_aval"]), dbg=True)
            elif type_ == 7:
                fich.write('# Temps (s) Cote inférieur Cote supérieur\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z_lower:.6f} {z_up:.6f}\n'
                #     self.mgis.add_info("\n", dbg=True)
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t
                #                        Upstream Water Level{2}\n \t  "
                #                       "Downstream Water Level :{3}"
                #                       .format(nom,tab["temps"],
                #                       tab["cote_amont"], tab["cote_aval"]), dbg=True)
            n = len(list(tab.values())[0])
            for i in range(n):
                dico = {k: v[i] for k, v in tab.items()}
                fich.write(chaine.format(**dico))

    def obs_to_loi(self, dict_lois, date_debut, date_fin, par):
        """
        Creation law with observation data
        :param dict_lois: dict of law
        :param date_debut: start date
        :param date_fin: last date
        :param par : dict of parameters
        :return:
        """
        # pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        pattern = re.compile('(\\w+)\\[t([+-][0-9]+)?\\]')
        somme = 0
        debit_prec = 0
        obs = {}
        # duree = int((date_fin - date_debut).total_seconds() / 3600)

        # liste_date = [date_debut + datetime.timedelta(hours=x)
        # for x in range(duree)]
        for nom, loi in dict_lois.items():

            if loi['type'] == 1:
                type = 'Q'
            elif loi['type'] == 2:
                type = 'H'
            else:
                continue

            valeur_init = None

            liste_stations = pattern.findall(loi['formule'])


            liste_date = None
            for cd_hydro, delta in liste_stations:
                if not delta:
                    delta = '0'
                dt = datetime.timedelta(hours=int(delta))
                condition = """code ='{0}'
                            AND type = '{1}'
                            AND date >= '{2:%Y-%m-%d %H:%M}' 
                            AND date <= '{3:%Y-%m-%d %H:%M}'
                            """.format(cd_hydro,
                                       type,
                                       date_debut + dt,
                                       date_fin + dt)

                obs[cd_hydro] = self.mdb.select('observations',
                                                condition,
                                                'code, date')

                if not liste_date:
                    # liste_date = map(lambda x: x - dt, obs[cd_hydro]['date'])
                    liste_date = [x - dt for x in obs[cd_hydro]['date']]

            fichier_loi = os.path.join(self.dossierFileMasc,
                                       del_symbol(nom) + '.loi')

            with open(fichier_loi, 'w') as fich_sortie:
                fich_sortie.write('# {0}\n'.format(nom))
                if type == "Q":
                    fich_sortie.write('# Temps (H) Debit\n')
                else:
                    fich_sortie.write('# Temps (H) Hauteur\n')
                fich_sortie.write(' H \n')

                for t in liste_date:
                    calc = loi['formule']
                    for cd_hydro, delta in liste_stations:
                        if not delta:
                            delta = '0'
                        t2 = t + datetime.timedelta(hours=int(delta))
                        if t2 in obs[cd_hydro]['date']:
                            i = obs[cd_hydro]['date'].index(t2)
                            val = obs[cd_hydro]['valeur'][i]
                        else:
                            val = None
                        calc = pattern.sub(str(val), calc, 1)

                    try:
                        resultat = eval(calc)
                    except:
                        resultat = None

                    if resultat is not None:
                        if valeur_init is None:
                            valeur_init = resultat
                            somme += resultat
                        tps = (t - date_debut).total_seconds() / 3600
                        chaine = '  {0:4.3f}   {1:3.6f}\n'
                        fich_sortie.write(chaine.format(tps, resultat))
            # check law after write
            initime = round((liste_date[0] - date_debut).total_seconds() / 3600, 3) * 3600
            lasttime = round((liste_date[-1] - date_debut).total_seconds() / 3600, 3) * 3600
            self.check_timelaw(par, nom, initime, lasttime)

            if valeur_init is not None:
                if type == "Q":
                    tab = {'time': [0, 3600],
                           'flowrate': [valeur_init, valeur_init]}
                    self.creer_loi(nom, tab, 1, init=True)
                else:
                    tab = {'time': [0, 3600], 'z': [valeur_init, valeur_init]}
                    self.creer_loi(nom, tab, 2, init=True)
            else:
                par["initialisationAuto"] = False
                self.mgis.add_info(
                    "No initialisation because of no SteadyValue")
        valeur_init = None
        for nom, loi in dict_lois.items():
            if not loi['type'] in (1, 2):
                # create other law
                tab = self.get_laws(nom, loi['type'],
                                    obs=True, date_deb=date_debut,
                                    date_fin=date_fin)
                if tab:
                    self.creer_loi(nom, tab, loi['type'])
                    if 'time' in tab.keys():
                        initime = round(tab['time'][0], 3)
                        lasttime = round(tab['time'][-1], 3)
                        self.check_timelaw(par, nom, initime, lasttime)
                else:
                    self.mgis.add_info(
                        'The law for {} is not create.'.format(nom))
                # create init law
                if loi['type'] in [4]:  # , 5]: # car 5 mascaret plante à l'init
                    self.creer_loi(nom, tab, loi['type'], init=True)
                elif loi['type'] in [5] and loi['couche'] == 'extremites':
                    for c, d in zip(tab["z"], tab["flowrate"]):
                        if debit_prec > 0 and d > somme:
                            valeur_init = (c - cote_prec) \
                                          / (d - debit_prec) \
                                          * (somme - debit_prec) \
                                          + cote_prec
                            break
                        else:
                            cote_prec, debit_prec = c, d
                    if valeur_init is not None:
                        tab = {'time': [0, 3600],
                               'z': [valeur_init, valeur_init]}
                        self.creer_loi(nom, tab, 2, init=True)
                else:
                    par["initialisationAuto"] = False
                    self.mgis.add_info("No initialisation, due to "
                                       "{}".format(nom))

    def fct_comment(self):
        liste_col = self.mdb.list_columns('runs')
        if 'comments' in liste_col:
            comments, ok = QInputDialog.getText(QWidget(), 'Comments',
                                                'if you want to input '
                                                'a comment :')
            if not isinstance(comments, str):
                comments = str(comments)
            if not ok:
                self.mgis.add_info("No comments.", dbg=True)
                comments = ''
        else:
            comments = ''
        return comments.replace("'", "''").replace('"', ' ')

    def mascaret_init(self, noyau, run, only_init):
        """
        Initial file creation in model
        :param noyau:(str) Mascaret kernel
        :param run:(str) run name
        :param only_init:(bool)  option to write the  model files but it doesn't
                work with 'evenement'
        :return:
        """
        comments = ''
        sql = "SELECT parametre, {0} FROM {1}.{2};"
        rows = self.mdb.run_query(
            sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        par = {}

        for param, valeur in rows:
            try:
                par[param] = eval(valeur.title())
            except:
                par[param] = valeur
        if not par['repriseCalcul']:
            self.clean_rep()
            self.creer_geo_ref()
            self.mgis.add_info("Geometric file is created.", dbg=True)
            self.mgis.add_info("noyau {}".format(noyau), dbg=True)
        else:
            self.clean_res()

        # Creation du fichier de la geometrie des casiers uniquement
        #   en non-permanent et si presence des casiers
        if par["presenceCasiers"] and noyau == "unsteady":
            self.creer_geo_casier()
        if only_init:
            if par["evenement"] and noyau != "steady":
                dict_scen_tmp = self.mdb.select('events', 'run', 'starttime')
                if len(dict_scen_tmp['name']) == 0:
                    self.mgis.add_info("**** Warning: scenario not found  ***")
                scen2, ok = QInputDialog.getItem(None,
                                                 'Select Events',
                                                 'Select Events',
                                                 dict_scen_tmp['name'], 0,
                                                 False)
                if ok:
                    id = dict_scen_tmp["name"].index(scen2)
                    dict_scen = {'name': [dict_scen_tmp["name"][id]],
                                 'starttime': [dict_scen_tmp['starttime'][id]],
                                 "endtime": [dict_scen_tmp["endtime"][id]],
                                 'run': [dict_scen_tmp['run'][id]]}

            else:
                dict_scen = {'name': ["test_api"]}

        else:
            if par["evenement"] and noyau != "steady":

                dict_scen_tmp = self.mdb.select('events', 'run', 'starttime')
                listexclu = []
                if len(dict_scen_tmp['name']) == 0:
                    self.mgis.add_info("**** Warning: scenario not found  ***")
                for i, scen in enumerate(dict_scen_tmp['name']):
                    # self.mgis.add_info("scen**************** {}".format(scen))
                    scen = scen.strip()
                    if not self.check_scenar(scen, run):
                        self.mgis.add_info(
                            "Canceled Simulation because of {0} "
                            "already exists.".format(scen))
                        listexclu.append(i)
                if listexclu:
                    dict_scen = {}
                    for key in dict_scen_tmp:
                        value = dict_scen_tmp[key]
                        value = [elt for idx, elt in enumerate(value) if
                                 not (idx in listexclu)]
                        dict_scen[key] = value
                else:
                    dict_scen = dict_scen_tmp
                comments = self.fct_comment()
            else:
                scen, ok = QInputDialog.getText(QWidget(), 'Scenario name',
                                                'Please input a scenario name :')
                scen = scen.replace("'", " ").replace('"', ' ').strip()
                if not ok or not self.check_scenar(scen, run):
                    self.mgis.add_info(
                        "Canceled Simulation because of {0} "
                        "already exists.".format(scen), dbg=True)
                    return None, None, None, None
                comments = self.fct_comment()
                dict_scen = {'name': [scen]}

        # progressMessageBar = self.iface.messageBar().createMessage(
        #     "Run ...")
        # self.iface.messageBar().pushWidget(progressMessageBar,
        # self.iface.messageBar().INFO)

        dict_lois, dico_loi_struct = self.creer_xcas(noyau)
        self.mgis.add_info("Xcas file is created.", dbg=True)
        if par['presenceTraceurs']:
            self.wq.create_filephy()
            self.wq.law_tracer()
            self.wq.init_conc_tracer()

        if dico_loi_struct.keys():
            for name in dico_loi_struct.keys():
                list_final = self.clmeth.get_list_law(
                    dico_loi_struct[name]['id_config'])

                self.clmeth.create_law(self.dossierFileMasc, name,
                                       dico_loi_struct[name]['type'],
                                       list_final)
                self.clmeth.create_law(self.dossierFileMasc, name + '_init',
                                       dico_loi_struct[name]['type'],
                                       list_final)


        self.mgis.add_info("Tracer files are created.", dbg=True)

        if par["LigEauInit"] and not par[
            "initialisationAuto"] and noyau != "steady":
            dict_scen = self.select_init_run_case(dict_scen)

        return par, dict_scen, dict_lois, comments

    def init_scen_steady(self, par, dict_lois):
        """
         Initial  files creation  for steady scenario
        :param par: (dict) parameters
        :param dict_lois:  (dict) laws
        :return:
        """

        if par['presenceTraceurs']:
            if self.wq.dico_phy[self.wq.cur_wq_mod]['meteo']:
                self.wq.create_filemet()

        for nom, l in dict_lois.items():
            if "valeurperm" not in l.keys():
                continue
            if l["valeurperm"] is None:
                # dictLois.items() extremities liste

                tab = self.get_laws(nom, l["type"])
                if tab:
                    self.creer_loi(nom, tab, l["type"])
                else:
                    self.mgis.add_info(
                        'The law for {} is not create.'.format(nom))
            else:
                try:
                    liste_ = ['pasTemps', 'critereArret', 'nbPasTemps',
                              'tempsMax', 'tempsInit']
                    temp_dic = {}
                    for info in liste_:
                        condition = "parametre ='{}'".format(info)
                        dtemp = self.mdb.select_distinct('steady', 'parametres',
                                                         condition)
                        temp_dic[info] = dtemp['steady'][0]
                except Exception as e:
                    self.mgis.add_info('erreur crit')
                    self.mgis.add_info(str(e))
                    return
                # self.mgis.add_info('{}'.format(condition))
                if temp_dic['critereArret'] == 1:
                    tfinal = temp_dic['tempsMax']
                elif temp_dic['critereArret'] == 2:
                    tfinal = temp_dic['tempsInit'] + temp_dic['pasTemps'] * \
                             temp_dic['nbPasTemps']
                elif temp_dic['critereArret'] == 3:
                    tfinal = 365 * 24 * 3600

                condition = "geom_obj='{0}' AND id_law_type={1} AND active".format(
                    nom, l['type'])
                if l['type'] == 1:
                    tab = {"time": [0, tfinal],
                           'flowrate': [l["valeurperm"]] * 2}
                # no possible to use rating curve (5) with steady.
                #   It's replaced in xcas
                elif l['type'] == 2 or l['type'] == 5:
                    l['type'] = 2
                    tab = {"time": [0, tfinal], 'z': [l["valeurperm"]] * 2}
                else:
                    tab = self.get_laws(nom, l["type"])

                if tab:
                    self.creer_loi(nom, tab, l["type"])
                else:
                    self.mgis.add_info(
                        'The law for {} is not create.'.format(nom))

    def init_scen_even(self, par, dict_lois, i, dict_scen):
        """
        Initial  files creation  for evenment scenario
        :param par:  (dict) parameters
        :param dict_lois: (dict) laws
        :param i: (int) um scenario
        :param dict_scen: (dict)dictionnay of scenarii
        :return:
        """
        # transcritical unsteady evenement
        date_debut = dict_scen['starttime'][i]
        date_fin = dict_scen['endtime'][i]
        duree = int((date_fin - date_debut).total_seconds()) - 3600

        tab = {"tempsMax": {'valeur': str(duree),
                            'balise1': 'parametresTemporels'},
               "titreCalcul": {'valeur': dict_scen['name'][i],
                               'balise1': 'parametresImpressionResultats'}
               }
        self.modif_xcas(tab, self.baseName + '.xcas')
        par['tempsMax'] = duree
        self.mgis.add_info("Xcas file is created.")
        if par['presenceTraceurs']:
            if self.wq.dico_phy[self.wq.cur_wq_mod]['meteo']:
                self.wq.create_filemet(typ_time='date', datefirst=date_debut,
                                       dateend=date_fin)

        self.obs_to_loi(dict_lois, date_debut, date_fin, par)

        return date_debut

    def init_scen_trans_unsteady(self, par, dict_lois):
        """
        Initial  files creation  for unsteady scenario
        :param par: dict contains the parameters
        :param dict_lois: dict contains the law
        :return:
        """

        if par['presenceTraceurs']:
            if self.wq.dico_phy[self.wq.cur_wq_mod]['meteo']:
                self.wq.create_filemet()

        for nom, l in dict_lois.items():
            # dictLois.items() extremities liste

            tab = self.get_laws(nom, l["type"])
            if tab:
                self.creer_loi(nom, tab, l["type"])
                if 'time' in tab.keys():
                    initime = round(tab['time'][0], 3)
                    lasttime = round(tab['time'][-1], 3)
                    self.check_timelaw(par, nom, initime, lasttime)
            else:
                self.mgis.add_info(
                    'The law for {} is not create.'.format(nom))

            self.mgis.add_info("Laws file is created.", dbg=True)

            if "valeurperm" not in l.keys():
                continue

            # nom = nom + "_init"
            if l["valeurperm"] is not None:
                if l['type'] == 1:
                    tab = {"time": [0, 3600], 'flowrate': [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 1, init=True)
                elif l['type'] == 2:
                    tab = {"time": [0, 3600], 'z': [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 2, init=True)
                elif l['type'] in [4, 5]:
                    self.creer_loi(nom, tab, l['type'], init=True)
                else:

                    par["initialisationAuto"] = False
                    self.mgis.add_info("No initialisation")
            else:
                if l['type'] in [4, 5]:
                    self.creer_loi(nom, tab, l['type'], init=True)
                else:
                    par["initialisationAuto"] = False
                    self.mgis.add_info(
                        "No initialisation because of no valeurperm "
                        "for {} condition".format(nom))

        return

    def select_init_run_case(self, dict_scen):
        """
        Select initial run case
        :return:
        """
        dico_run = self.mdb.select_distinct("run",
                                            "runs")

        if dico_run != {} and dico_run is not None:
            liste_run = ['{}'.format(v) for v in dico_run['run']]
        else:
            liste_run = []
        liste_run.append('".lig" File')
        dict_scen["id_run_init"] = []
        for i, scen in enumerate(dict_scen['name']):

            case, ok = QInputDialog.getItem(None,
                                            'Initial run case for {}'.format(scen),
                                            'Runs',
                                            liste_run, 0, False)
            if ok:
                if case == '".lig" File':
                    self.copy_lig()
                else:
                    condition = "run LIKE '{0}'".format(case)
                    dico_scen = self.mdb.select_distinct("scenario",
                                                         "runs", condition)
                    liste_scen = ['{}'.format(v) for v in dico_scen["scenario"]]

                    scen2, ok = QInputDialog.getItem(None,
                                                     'Initial Scenario for {}'.format(scen),
                                                     'Initial Scenario',
                                                     liste_scen, 0, False)

                    if ok:

                        id_run = self.mdb.run_query("SELECT id FROM {0}.runs "
                                                    "WHERE run = '{1}' "
                                                    "AND scenario = '{2}'".format(
                            self.mdb.SCHEMA, case, scen2), fetch=True)
                        dict_scen["id_run_init"].append(id_run[0][0])
                        # self.opt_to_lig( id_run[0][0], self.baseName)

                    else:
                        dict_scen["id_run_init"].append(None)
                        self.mgis.add_info("Cancel run : {}".format(scen), dbg=True)
            else:
                dict_scen["id_run_init"].append(None)
                self.mgis.add_info("Cancel run: {}".format(scen), dbg=True)

        return dict_scen

    # return
    def mascaret(self, noyau, run, only_init=False):
        """
        creation file and to run mascaret
        :param noyau: kernel
        :param run: name run
        :param only_init: if only intialisation is true
        :return:
        """
        par, dict_scen, dict_lois, comments = self.mascaret_init(noyau, run,
                                                                 only_init)
        if not par or not dict_scen or not dict_lois:
            return

        if only_init:
            id = 0

            if noyau == "steady":
                self.init_scen_steady(par, dict_lois)
            elif par["evenement"]:
                date_debut = self.init_scen_even(par, dict_lois, id, dict_scen)
            else:
                # transcritical unsteady hors evenement
                self.init_scen_trans_unsteady(par, dict_lois)
            if self.check_mobil_gate() and noyau == "unsteady":
                self.create_mobil_gate_file()
            self.fct_only_init(noyau, dict_scen)
            return

        #
        if self.mgis.task_use:
            self.mgis.task_mas = QgsTask.fromFunction('Run Mascaret',
                                                      self.task_mascaret,
                                                      on_finished=self.completed,
                                                      tup=(
                                                          par, dict_scen, dict_lois,
                                                          comments, noyau, run))
            self.mgis.task_mas.taskCompleted.connect(self.del_task_mas)
            self.mgis.task_mas.taskTerminated.connect(self.del_task_mas)
            QgsApplication.taskManager().addTask(self.mgis.task_mas)
        else:
            self.task_mascaret(None, tup=(par, dict_scen, dict_lois, comments, noyau, run))

    def del_task_mas(self):
        """
        Clean tastk_mas variable
        :return:
        """
        del self.mgis.task_mas
        gc.collect()
        self.mgis.task_mas = None

    def completed(self, exception):
        """this is called when run is finished. Exception is not None if run
        raises an exception. Result is the return value of run."""
        message_category = 'My tasks from a function'
        if exception is None:
            QgsMessageLog.logMessage(
                'task completed',
                message_category, Qgis.Info)
        else:
            QgsMessageLog.logMessage("Exception: {}".format(exception),
                                     message_category, Qgis.Critical)
            raise exception

    def task_mascaret(self, task, tup=None):

        if tup:
            par, dict_scen, dict_lois, comments, noyau, run = tup
        else:
            self.mgis.add_info('no transmitted variable for task_mascaret')
            return

        for i, scen in enumerate(dict_scen['name']):
            self.clean_res()
            self.mgis.add_info(" *** The current scenario is {} ***".format(scen))
            # initialise file
            date_debut = None
            if noyau == "steady":
                self.init_scen_steady(par, dict_lois)

            elif par["evenement"]:
                date_debut = self.init_scen_even(par, dict_lois, i, dict_scen)
            else:
                # transcritical unsteady hors evenement
                self.init_scen_trans_unsteady(par, dict_lois)
            if self.check_mobil_gate() and noyau == "unsteady":
                self.create_mobil_gate_file()

            # check error and warning:
            self.check_apport()
            arret = False
            for typerr in self.err_model:
                if self.err_model[typerr].status:
                    self.mgis.add_info(self.err_model[typerr].get_alltxt())
                    if self.err_model[typerr].stop:
                        arret = True
            if arret:
                return False

            # RUN Model
            if par["initialisationAuto"] and noyau != "steady":
                # add if name of init. exist previously
                sceninit = scen + '_init'
                if self.check_scenar(sceninit, run):

                    self.mgis.add_info(
                        "========== Run initialization =========")
                    self.mgis.add_info(
                        "Run = {} ;  Scenario = {} ; Kernel= {}".format(run,
                                                                        sceninit,
                                                                        noyau))

                    id_run = self.insert_id_run(run, sceninit)
                    self.lance_mascaret(self.baseName + '_init.xcas', id_run)

                    self.lit_opt_new(id_run, None,
                                     self.baseName + '_init', comments)
                    self.mgis.add_info("Auto-initialization Run is done", dbg=True)

                else:
                    self.mgis.add_info("No Run initialization.\n"
                                       " The initial boundaries come "
                                       "from {} scenario.".format(sceninit))
                    return

                self.opt_to_lig(id_run, self.baseName)
                tab = {"LigEauInit": {'valeur': 'true',
                                      'balise1': 'parametresConditionsInitiales',
                                      'balise2': 'ligneEau'}
                       }
                self.modif_xcas(tab, self.baseName + '.xcas')

            elif par["LigEauInit"] and noyau != "steady":
                #    self.select_init_run_case()
                id_run_init = None
                if 'id_run_init' in dict_scen.keys():
                    id_run_init = dict_scen['id_run_init'][i]
                if id_run_init is None:
                    self.mgis.add_info("Cancel run because No initial boundaries")
                    continue
                self.opt_to_lig(id_run_init, self.baseName)

            self.mgis.add_info("========== Run case  =========")
            self.mgis.add_info(
                "Run = {} ;  Scenario = {} ; Kernel= {}".format(run, scen,
                                                                noyau))
            cond_casier = False
            if par["presenceCasiers"] and noyau == "unsteady":
                cond_casier = True

            id_run = self.insert_id_run(run, scen)
            finish = self.lance_mascaret(self.baseName + '.xcas', id_run,
                                         par['presenceTraceurs'], cond_casier)
            if not finish:
                self.mgis.add_info("Simulation error")
                return

            self.lit_opt_new(id_run, date_debut, self.baseName, comments,
                             par['presenceTraceurs'], cond_casier)

            if self.check_mobil_gate():
                self.read_mobil_gate_res(id_run)

            # if task :
            #     if task.isCanceled():
            #         return
        # #
        self.iface.messageBar().clearWidgets()
        self.mgis.add_info("Simulation finished")
        return

    def import_results(self, run, scen, comments, path, date_debut=None):
        """
        import mascaret resultats
        :param run: (str) run name
        :param scen: (str) scenario name
        :param comments:(str) comments
        :param path: (str) path represitory
        :param date_debut: start time
        :return:
        """

        lia_cond = False
        cas_cond = False
        cond_tra = False

        for file in os.listdir(path):
            if file.split('.')[-1] == "liai_opt":
                lia_cond = True
            elif file.split('.')[-1] == "cas_opt":
                cas_cond = True
            elif file.split('.')[-1] == "tra_opt":
                cond_tra = True

        cond_casier = False
        if lia_cond and cas_cond:
            cond_casier = True

        id_run = self.insert_id_run(run, scen)
        self.lit_opt_new(id_run, date_debut, self.baseName, comments, cond_tra,
                         cond_casier)

        if os.path.isfile(os.path.join(path, 'Fichier_Crete.csv')):
            self.read_mobil_gate_res(id_run)

        if os.path.isfile(os.path.join(path, 'res_struct.res')):
            with open(os.path.join(path, 'res_struct.res'), 'r') as filein:
                dico = json.load(filein)
            self.stock_res_api(dico, id_run)

    def fct_only_init(self, noyau, dict_scen):
        """
        clean and model file creation
        :param noyau: (str) kernel
        :return:
        """
        # delete "initialisationAuto" file
        for file in os.listdir(self.dossierFileMasc):
            if '_init.loi' in file or '_init.xcas' in file:
                path = os.path.join(self.dossierFileMasc, file)
                if os.path.isfile(path):
                    os.remove(path)
        # select initial case
        if noyau != "steady":
            dict_scen = self.select_init_run_case(dict_scen)
            if dict_scen["id_run_init"][0] != None:
                self.opt_to_lig(dict_scen["id_run_init"][0], self.baseName)
        cl = ClassPostPreFG(self.mgis)

        # path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        # 'mascaret'))
        path = self.dossierFileMasc
        path = os.path.join(path, 'cli_fg.obj')
        cl.create_cli_fg(path)
        del cl

    def lance_mascaret(self, fichier_cas, id_run, tracer=False, casier=False):
        """
        Run mascaret
        :param fichier_cas:
        :param id_run:
        :param tracer:
        :param casier:
        :return:
        """
        os.chdir(self.dossierFileMasc)
        with open('FichierCas.txt', 'w') as fichier:
            fichier.write("'" + fichier_cas + "'\n")
        if not self.cond_api:
            test = sys.platform
            if 'linux' in test or test == 'cygwin':
                soft = "./mascaret_linux"
            elif test == 'win32':
                soft = "mascaret.exe"
            else:
                self.mgis.add_info(
                    "{0} platform  doesn't allow to run simulation.".format(
                        test))
                return False

            # Linux(2.x and 3.x) ='linux2' or 'linux'
            # Windows = 'win32'
            # Windows / Cygwin = 'cygwin'

            p = subprocess.Popen(soft, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE
                                 , stdin=subprocess.PIPE)
            p.wait()
            txt = "{0}".format(p.communicate()[0].decode("utf-8"))
            txt1 = "{0}".format(p.communicate()[1].decode("utf-8"))
            self.mgis.add_info(txt)
            self.mgis.add_info(txt1)

            return True
        else:
            pwd = os.getcwd()
            os.chdir(self.dossierFileMasc)
            clapi = ClassAPIMascaret(self)
            clapi.main(fichier_cas, tracer, casier)
            self.save_res_struct = (copy.deepcopy(clapi.results_api), id_run)
            del clapi

            os.chdir(pwd)
            return True

    def stock_res_api(self, dico, id_run):
        """ Stock api results """
        if len(dico) > 0:
            for key in dico.keys():
                if key == 'STRUCT_FG':
                    self.res_fg(dico[key], id_run)

    def res_fg(self, dico_res, id_run):
        """stock flood gate results"""

        # colonnes = ['id_runs', 'time', 'pknum', 'var', 'val']
        colonnes = ['idruntpk', 'var', 'val']
        values = []
        var_info = {'var': 'ZSTR',
                    'type_res': 'struct',
                    'name': 'valve movement',
                    'type_var': 'float'}
        id_var = self.mdb.check_id_var(var_info)

        dico_pk = {}
        dico_time = {}
        d_res = {}
        for id_config in dico_res.keys():
            rows = self.mdb.select('struct_config',
                                   where='id={}'.format(id_config),
                                   list_var=['abscissa'])
            pknum = rows['abscissa'][0]
            dico_pk[id_config] = pknum
            dico_time[id_config] = dico_res[id_config]['TIME']
            d_res[(pknum, id_var)] = {'t': dico_res[id_config]['TIME'],
                                      'v': dico_res[id_config]['ZSTR']}
        for (pk, var), v in d_res.items():
            values.append([id_run, pk, var,
                           "{" + ','.join(str(i) for i in v['t']) + "}",
                           "{" + ','.join(str(i) for i in v['v']) + "}"])
        if len(values) > 0:
            self.mdb.run_query(
                "INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(self.mdb.SCHEMA) +
                "VALUES (%s, %s, %s, %s, %s)", many=True, list_many=values)

        if len(dico_res.keys()) > 0:
            list_insert = [[id_run, 'struct', 'pknum', json.dumps(dico_pk)],
                           [id_run, 'struct', 'time', json.dumps(dico_time)],
                           [id_run, 'struct', 'var', json.dumps([id_var])]]
            col_tab = ['id_runs', 'type_res', 'var', 'val']
            self.mdb.insert_res('runs_graph', list_insert, col_tab)



    def opt_to_lig(self, id_run, base_namefiles):
        """Creation of .lig file """
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

        nb_bief = len(set(result['branche']))
        section = sorted(set(result['section']))

        imax = len(section)
        i1i2 = []
        for b in sorted(i1.keys()):
            i1i2.append(str(i1[b]))
            i1i2.append(str(i2[b]))

        with open(os.path.join(self.dossierFileMasc, base_namefiles + '.lig'),
                  'w') as fich:
            date = datetime.datetime.utcnow()
            fich.write(
                'RESULTATS CALCUL,DATE :  {0:%d/%m/%y %H:%M}\n'.format(date))
            fich.write('FICHIER RESULTAT MASCARET{0}\n'.format(' ' * 47))
            fich.write('{0} \n'.format('-' * 71))
            fich.write(' IMAX  = {0:4} NBBIEF= {1:3}\n'.format(str(imax),
                                                               str(nb_bief))
                       )

            chaine = [""]
            for k in range(0, len(i1i2), 10):
                chaine.append('I1,I2 =')
                for i in range(k, k + 10):
                    if i < len(i1i2):
                        chaine.append('{0:4}'.format(i1i2[i]))
                chaine.append("\n")
            fich.write(" ".join(chaine))

            for k in ['X', 'Z', 'Q']:
                fich.write(' ' + k + '\n')
                long = 0
                for x in result[k]:
                    fich.write('{:13.2f}'.format(x))
                    long += 1
                    if long == 5:
                        fich.write('\n')
                        long = 0

                if long != 0:
                    fich.write('\n')

            fich.write(' FIN\n')

    def copy_lig(self):
        """ Load .lig file in run model"""
        if int(qVersion()[0]) < 5:  # qt4
            fichiers = QFileDialog.getOpenFileNames(None,
                                                    'File Selection',
                                                    # self.dossierFileMasc,
                                                    self.mgis.repProject,
                                                    "File (*.lig)")

        else:  # qt5
            fichiers, _ = QFileDialog.getOpenFileNames(None,
                                                       'File Selection',
                                                       self.mgis.repProject,
                                                       # self.dossierFileMasc,
                                                       "File (*.lig)")

        try:
            fichiers = fichiers[0]
            self.mgis.up_rep_project(fichiers)
        except IndexError:
            self.mgis.add_info("Cancel  init file")
            return

        try:
            shutil.copy(fichiers, os.path.join(self.dossierFileMasc,
                                               self.baseName + '.lig'))
        except Exception as e:
            self.mgis.add_info("Error copying file")
            self.mgis.add_info("{}".format(e))

    def clean_rep(self):
        """ Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        for i in range(0, len(files)):
            os.remove(os.path.join(self.dossierFileMasc, files[i]))
        copy_dir_to_dir(self.dossierFileMascOri, self.dossierFileMasc)
        if not self.check_exe():
            self.mgis.download_bin()

        copy_dir_to_dir(self.dossierFile_bin, self.dossierFileMasc)

    def check_exe(self):
        """
        Check if exe file exists
        :return:
        """
        if not os.path.isdir(self.dossierFile_bin):
            return False
        test = sys.platform
        if 'linux' in test or test == 'cygwin':
            soft = "mascaret_linux"
        elif test == 'win32':
            soft = "mascaret.exe"
        if not os.path.isfile(os.path.join(self.dossierFile_bin, soft)):
            return False

        return True

    def clean_res(self):
        """ Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        listsup = [".opt", ".lig", '.cas_opt', '.liai_opt', '.tra_opt']
        for i in range(0, len(files)):
            ext = os.path.splitext(files[i])[1]
            # self.mgis.add_info('delet file rr{}rr {}'.format(ext,(ext in listsup)))
            if ext in listsup:
                os.remove(os.path.join(self.dossierFileMasc, files[i]))
                self.mgis.add_info('delete file {}'.format(files[i]), dbg=True)

    def del_folder_mas(self):
        """ Delete the copy folder"""
        try:
            shutil.rmtree(self.dossierFileMasc)
        except Exception as e:
            self.mgis.add_info(
                'Failed to delete {}. Reason: {}'.format(self.dossierFileMasc, e), dbg=True)

    def copy_run_file(self, rep):
        """copy run file in "rep" path"""
        try:
            files = os.listdir(self.dossierFileMasc)
            for i in range(0, len(files)):
                shutil.copy2(os.path.join(self.dossierFileMasc, files[i]),
                             os.path.join(rep, files[i]))
            return True
        except:
            return False

    def copy_file_model(self, rep, case=None):
        # self.mgis.add_info('{}'.format(rep))
        if case == 'xcas':
            file = os.path.join(self.dossierFileMasc, self.baseName + ".xcas")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info('{} not found'.format(file))
        elif case == 'geo':
            file = os.path.join(self.dossierFileMasc, self.baseName + ".geo")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info('{} not found'.format(file))
        elif case == 'georef':
            file = os.path.join(self.dossierFileMasc, self.baseName + ".georef")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info('{} not found'.format(file))
        elif case == 'casier':
            file = os.path.join(self.dossierFileMasc, self.baseName + ".casier")
            if os.path.isfile(file):
                shutil.copy2(file, rep)
            else:
                self.mgis.add_info('{} not found'.format(file))
        else:
            self.mgis.add_info('No file to export')

    def check_scenar(self, nom_scen, run):
        """if true :not exist nomScen and results """
        # kernel=self.listeState[self.Klist.index(kernel)]
        condition = "run LIKE '{0}'".format(run)
        allscen = self.mdb.select_distinct("scenario", "runs", condition)
        if allscen:
            if nom_scen in allscen['scenario'] or nom_scen + "_init" in allscen[
                'scenario']:
                info = True
            else:
                info = False

            if info:
                ok = self.box.yes_no_q(
                    'Do you want to remove the {} results for a '
                    'new simulation? '.format(nom_scen))

                if ok:
                    lst_tab = self.mdb.list_tables()
                    # delete case initalization
                    condition = "(scenario LIKE '{0}' OR  scenario " \
                                "LIKE '{0}_init')" \
                                " AND run LIKE '{1}' ".format(nom_scen,
                                                              run)

                    id_run = self.mdb.run_query("SELECT id FROM {0}.runs "
                                                "WHERE run = '{1}' "
                                                "AND (scenario LIKE '{2}' "
                                                "OR  scenario "
                                                "LIKE '{2}_init') ".format(
                        self.mdb.SCHEMA, run, nom_scen), fetch=True)
                    self.mdb.delete('runs', condition)
                    # new results
                    if len(id_run) > 0:
                        id_run = id_run[0][0]
                        condition = "id_runs = {}".format(id_run)
                        var = self.mdb.run_query(
                            "SELECT DISTINCT var FROM {0}.results "
                            "WHERE {1} ".format(self.mdb.SCHEMA, condition),
                            fetch=True)
                        list_var = [str(v[0]) for v in var]
                        if len(list_var) > 0:
                            self.mdb.run_query("DELETE  FROM {}.results_var "
                                               "where id in ({}) and "
                                               "type_res = '"
                                               "tracer_TRANSPORT_PUR'".format(
                                self.mdb.SCHEMA, ','.join(list_var)))
                        if 'results_old' in lst_tab:
                            self.mdb.delete('results_old', condition)

                        self.mdb.delete('results_sect', condition)
                        self.mdb.delete('runs_graph', condition)
                        self.mdb.delete('runs_plani', condition)

                        self.mdb.delete('results_by_pk', condition)
                        if 'results_val' in lst_tab:
                            condition_val = "idruntpk IN " \
                                            "(SELECT DISTINCT id_runs FROM {0}.results_idx " \
                                            "where id_runs={1})".format(self.mdb.SCHEMA, id_run)
                            self.mdb.delete('results_val', condition_val)
                        if 'results_idx' in lst_tab:
                            self.mdb.delete('results_idx', condition)


                    self.mgis.add_info(
                        "Deletion of {0} scenario for {1} is done".format(
                            nom_scen, run), dbg=True)
                    return True
                else:
                    return False

            else:
                return True
        else:
            return True

    def read_opt(self, nom_fich, date_debut, scen, run, init_col=None):
        """ Read opt file"""
        if init_col is None:
            init_col = []
        t = set([])
        pk = set([])
        if not init_col:
            col = ['t', 'branche', 'section', 'pk']
        else:
            col = init_col

        with open(nom_fich, 'r') as source:
            var = source.readline()
            if var[:2] == '/*':
                # comment
                var = source.readline()

            ligne = source.readline()

            while '[resultats]' not in ligne:
                temp = ligne.replace('"', '').replace('NaN', "'NULL'").split(
                    ';')
                col.append(temp[1].lower())
                ligne = source.readline()

            data = csv.DictReader(source, delimiter=';', fieldnames=col)
            if date_debut:
                col.append("date")
            col.append("run")
            col.append("scenario")

            value = []
            for ligne in data:
                if date_debut:

                    d = date_debut + datetime.timedelta(
                        seconds=float(ligne["t"]))
                    ligne["date"] = d
                    t.add("{:%Y-%m-%d %H:%M}".format(d))
                else:
                    t.add(ligne["t"])
                ligne["run"] = run
                ligne["scenario"] = scen

                if 'pk' in ligne.keys():
                    tempo = str(round(float(ligne["pk"]), 2))
                    pk.add(tempo)
                if "section" in ligne.keys():
                    ligne["section"] = ligne["section"].replace('"', '')
                if "branche" in ligne.keys():
                    ligne["branche"] = ligne["branche"].replace('"', '')

                ligne_list = []
                delcond_qtot = False

                for k in col:
                    if k == 'qtot':
                        delcond_qtot = True
                    elif k == 'pk':
                        tempo = str(round(float(ligne[k]), 2))
                        ligne_list.append(tempo)
                    elif k == 'bnum':
                        # extrait le numero mascaret de casier
                        numero_masca = re.findall('\\d+', ligne[k])[0]

                        # convertit le numero masca en qgis
                        # (different si un casier inactif)
                        numero_qgis = str(self.dico_basinnum[int(numero_masca)])
                        ligne_list.append(numero_qgis)
                    elif k == 'lnum':
                        # extrait le numero mascaret de liaison
                        numero_masca = re.findall('\\d+', ligne[k])[0]
                        # convertit le numero masca en qgis
                        # (different si une liaison inactive)
                        numero_qgis = str(self.dico_linknum[int(numero_masca)])
                        ligne_list.append(numero_qgis)
                    else:
                        ligne_list.append(ligne[k])

                value.append(ligne_list)
        # delete 'qtot' because of the same that 'q'
        if delcond_qtot:
            col.remove("qtot")

        return t, pk, col, value

    def create_mobil_gate_file(self):
        """
        create the mobile dam file (Fichier_Barrage_Mobile.txt)
        """

        info = self.mdb.select('weirs', where="active_mob = true",
                               list_var=['method_mob', 'gid', 'name'], order='gid')
        if info:
            try:
                nomfich = os.path.join(self.dossierFileMasc,
                                       'Fichier_Barrage_Mobile.txt')

                if os.path.isfile(nomfich):
                    os.remove(nomfich)
                fich = open(nomfich, 'w')

                for i, idw in enumerate(info['gid']):
                    if info['method_mob'][i] == '1':
                        rows = self.mdb.select('weirs_mob_val',
                                               where="id_weirs= {} AND (name_var='TIME' OR name_var='ZVAR')".format(
                                                   idw),
                                               order='name_var, id_order')
                        if len(rows['id_weirs']) > 0:
                            nbt = max(rows['id_order']) + 1
                            if nbt < 501:
                                fich.write(
                                    "{} {}\n".format(info['name'][i].replace(' ', '_'), nbt))
                                fich.write("methode 1\n")
                                fich.write("T(s)\n")
                                for j in range(nbt):
                                    fich.write('{} '.format(rows['value'][j]))
                                fich.write('\n')
                                fich.write("Zcrete(ngf)\n")
                                for j in range(nbt):
                                    fich.write(
                                        '{} '.format(rows['value'][j + nbt]))
                                fich.write("\n")
                            else:
                                self.mgis.add_info(
                                    "Warning: Value number is superior to 500 "
                                    "for {} weirs.\n"
                                    "The weir is ignored.".format(
                                        info['name'][i]))
                        else:
                            self.mgis.add_info(
                                "Warning: there aren't value in {} weirs".format(
                                    info['name'][i]))

                    elif info['method_mob'][i] == '2':

                        rows = self.mdb.select('weirs_mob_val',
                                               where="id_weirs= {} AND name_var!='TIME' AND name_var!='ZVAR'".format(
                                                   idw))
                        if len(rows['id_weirs']) > 0:
                            fich.write("{} {}\n".format(info['name'][i].replace(' ', '_'), idw))
                            fich.write("methode 2\n")
                            fich.write("Zregulation Zbas Zhaut (m ngf)\n")
                            fich.write("{} {} {}\n".format(
                                rows['value'][rows['name_var'].index('ZREG')],
                                rows['value'][rows['name_var'].index('ZBAS')],
                                rows['value'][rows['name_var'].index('ZHAUT')]))
                            fich.write("Vabaissement Vrehaussement m/s\n")
                            fich.write("{} {}\n".format(
                                rows['value'][rows['name_var'].index('VDESC')],
                                rows['value'][rows['name_var'].index('VMONT')]))
                    else:
                        self.mgis.add_info(
                            "Warning: there aren't value in {} weirs".format(
                                info['name'][i]))

                fich.close()

                self.mgis.add_info("Creation the dam is done")

            except Exception as e:
                err = "Error: save the dam file"
                err += str(e)
                self.mgis.add_info(err)
                raise Exception(err)

    def check_mobil_gate(self):
        """
        check if weirs active
        :return:
        """
        info = self.mdb.select('weirs', where="active_mob = true",
                               list_var=['method_mob', 'gid', 'name'])
        if info:
            if len(info['gid']) > 0:
                return True

        return False


    def read_mobil_gate_res(self, id_run):
        """
        read result mobil_gate
        :param id_run: run if
        :return:
        """
        nomfich = os.path.join(self.dossierFileMasc, 'Fichier_Crete.csv')
        if os.path.isfile(nomfich):
            try:

                # Read file
                dico_res = {}
                fich = open(nomfich, 'r')

                for ligne in fich:
                    liste = ligne.split()
                    if len(liste) > 1:
                        nom = liste[2].strip()
                        if not (nom in dico_res.keys()):
                            dico_res[nom] = {'TIME': [], 'ZSTR': []}
                        dico_res[nom]['TIME'].append(float(liste[0].strip()))
                        dico_res[nom]['ZSTR'].append(float(liste[1].strip()))
                fich.close()

                var_info = {'var': 'ZSTR',
                            'type_res': 'weirs',
                            'name': 'valve movement',
                            'type_var': 'float'}
                id_var = self.mdb.check_id_var(var_info)
                values = []
                d_res = {}
                dico_pk = {}
                dico_time= {}
                for name in dico_res.keys():
                    where = "name = '{}'".format(name)
                    info = self.mdb.select('weirs', where=where,
                                           list_var=['gid', 'abscissa'], order='gid')
                    if len(info['gid']) < 1:
                        where = "name LIKE '{}%'".format(name)
                        info = self.mdb.select('weirs', where=where,
                                               list_var=['gid', 'abscissa'], order='gid')
                    pknum = info['abscissa'][0]
                    d_res[(pknum,id_var)] = {'t' : dico_res[name]['TIME'] ,
                                             'v' : dico_res[name]['ZSTR'] }
                    dico_pk[name] = info['abscissa'][0]
                    dico_time[name] = dico_res[name]['TIME']

                for (pk, var), v in d_res.items():
                    values.append([id_run, pk, var,
                                       "{" + ','.join(str(i) for i in v['t']) + "}",
                                       "{" + ','.join(str(i) for i in v['v']) + "}"])
                if len(values) > 0:
                    self.mdb.run_query(
                        "INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(self.mdb.SCHEMA) +
                        "VALUES (%s, %s, %s, %s, %s)", many=True, list_many=values)

                if len(dico_res.keys()) > 0:
                    list_insert = [[id_run, 'weirs', 'pknum', json.dumps(dico_pk)],
                                   [id_run, 'weirs', 'time', json.dumps(dico_time)],
                                   [id_run, 'weirs', 'var', json.dumps([id_var])]]
                    col_tab = ['id_runs', 'type_res', 'var', 'val']
                    self.mdb.insert_res('runs_graph', list_insert, col_tab)
            except Exception as e:
                txt = "Erreur load of mobil_gate results.\n"
                self.mgis.add_info(txt)
                self.mgis.add_info(e)

    def insert_id_run(self, run, scen):
        """
        creation run line in runs table
        :param run: run name
        :param scen: scenario name
        :return:
        """
        maintenant = datetime.datetime.utcnow()
        tab = {run: {"scenario": scen,
                     "date": "{:%Y-%m-%d %H:%M}".format(maintenant)}
               }
        listimport = ["run", "scenario", "date"]

        self.mdb.insert("runs",
                        tab,
                        listimport)
        info = self.mdb.select('runs',
                               where="run='{}' AND scenario='{}'".format(run,
                                                                         scen),
                               list_var=['id'])

        id_run = info['id'][0]
        return id_run

    def new_read_opt(self, nom_fich, type_res, init_col=None):
        """
        Read opt file
        :param nom_fich: file name
        :param type_res: results type
        :param init_col: first column
        :return: dictionary of values
        """
        if init_col is None:
            init_col = []
        col = []
        var_del = []
        with open(nom_fich, 'r') as source:
            var = source.readline()
            if var[:2] == '/*':
                # comment
                var = source.readline()
            ligne = source.readline()
            if type_res.split('_')[0] == 'tracer':
                dico_tra = self.mdb.select('tracer_name',
                                           where="type ='{}'".format(
                                               self.wq.cur_wq_mod),
                                           order='id',
                                           list_var=['sigle', 'text'])
                cpt_tra = 0
                while '[resultats]' not in ligne:
                    temp = ligne.replace('"', '').replace('NaN',
                                                          "'NULL'").split(';')
                    if temp[1].strip().upper()[0] == 'C':
                        if self.wq.cur_wq_mod != 'TRANSPORT_PUR':
                            var_info = {'var': dico_tra['sigle'][cpt_tra],
                                        'type_res': type_res}
                        else:
                            var_info = {'var': dico_tra['sigle'][cpt_tra],
                                        'type_res': type_res,
                                        'name': dico_tra['text'][cpt_tra],
                                        'type_var': 'float'}
                        cpt_tra += 1
                    else:
                        var_info = {'var': temp[1].upper(),
                                    'type_res': type_res}
                    id_var = self.mdb.check_id_var(var_info)
                    # delete 'qtot' because of the same that 'q'
                    if temp[1].upper() == 'QTOT':
                        var_del.append(id_var)
                    if id_var:
                        col.append(id_var)
                    else:
                        col.append(temp[1])
                    ligne = source.readline()
            else:
                while '[resultats]' not in ligne:
                    temp = ligne.replace('"', '').replace('NaN',
                                                          "'NULL'").split(';')
                    var_info = {'var': temp[1].upper(),
                                'type_res': type_res}
                    id_var = self.mdb.check_id_var(var_info)
                    # delete 'qtot' because of the same that 'q'
                    if temp[1].upper() == 'QTOT':
                        var_del.append(id_var)

                    if id_var:
                        col.append(id_var)
                    else:
                        col.append(temp[1])
                    ligne = source.readline()

            if not init_col:
                col_tmp = ['TIME', 'BRANCH', 'SECTION', 'PK'] + col
            else:
                col_tmp = init_col + col

            dico_val = {}
            for key in col_tmp:
                dico_val[key] = []
            data = csv.DictReader(source, delimiter=';', fieldnames=col_tmp)
            int_val = ['BRANCHE', 'SECTION']

            for ligne in data:
                for key in dico_val.keys():
                    val = ligne[key].strip()
                    if key == 'PK':
                        val = round(float(val), 2)
                    elif key in int_val:
                        val = int(val)
                    elif key == 'BNUM':
                        numero_masca = re.findall('\\d+', val)[0]
                        # convertit le numero masca en qgis
                        # (different si un casier inactif)
                        numero_qgis = str(self.dico_basinnum[int(numero_masca)])
                        val = float(numero_qgis)
                    elif key == 'LNUM':
                        numero_masca = re.findall('\\d+', val)[0]
                        # convertit le numero masca en qgis
                        # (different si un link inactif)
                        numero_qgis = str(self.dico_linknum[int(numero_masca)])
                        val = float(numero_qgis)
                    else:
                        val = float(val)

                    dico_val[key].append(val)
        for id in var_del:
            if id:
                del dico_val[id]
        return dico_val

    @staticmethod
    def around(x):
        """around x"""
        x = round(float(x), 2)
        return x

    @staticmethod
    def fmt(liste):
        # list(map(str, liste))
        return " ".join([str(var) for var in liste])

    # @staticmethod
    # def fmt(self, liste):
    #     txt = ''
    #     for var in liste:
    #         if str(var) == 'None':
    #             txt += '0'
    #         else:
    #             txt += str(var)
    #         txt += " "
    #     return txt

    @staticmethod
    def check_none(liste):
        """ Check if None is list"""
        for val in liste:
            if str(val) == 'None':
                return True
        return False

    def save_run_graph(self, val, id_run, typ_res, max=True):
        """save info for graph"""

        list_insert = []
        list_var = []
        for id in val.keys():
            if isinstance(id, int):
                list_var.append(id)
        list_var = list(set(list_var))
        # delete doublon list(set(my_list))
        list_insert.append(
            [id_run, typ_res, 'var', json.dumps(sorted(list_var))])
        list_insert.append([id_run, typ_res, 'time',
                            json.dumps(sorted(list(set(val['TIME']))))])

        if typ_res == 'opt':
            var_info = {'var': 'ZMAX',
                        'type_res': 'opt'}
            id_zmax = self.mdb.check_id_var(var_info)
            # if zmax exist
            if id_zmax in list_var:
                dico_zmax = {}
                tmax = val['TIME'][-1]
                for i in range(len(val['TIME']) - 1, -1, -1):
                    if val['TIME'][i] == tmax:
                        dico_zmax[val['PK'][i]] = val[id_zmax][i]
                    else:
                        break

                list_insert.append(
                    [id_run, typ_res, 'zmax', json.dumps(dico_zmax)])
                key_pknum = 'PK'
            else:
                var_info = {'var': 'Z',
                            'type_res': 'opt'}
                id_z = self.mdb.check_id_var(var_info)
                if id_z in list_var and max:
                    dico_zmax = {}
                    for pknum in list(set(val['PK'])):
                        sql = "SELECT MAX(val) FROM {0}.results " \
                              "WHERE var = {2} " \
                              "AND id_runs={1} AND pknum ={3};".format(
                            self.mdb.SCHEMA, id_run, id_z, pknum)
                        rows = self.mdb.run_query(sql, fetch=True)
                        try:
                            dico_zmax[pknum] = rows[0][0]
                        except Exception:
                            dico_zmax[pknum] = None

                    list_insert.append(
                        [id_run, typ_res, 'zmax', json.dumps(dico_zmax)])
                    key_pknum = 'PK'
            # add stockage plani
            if dico_zmax:
                cl_geo = ClassResProfil()
                dico_zmax = {str(key): item for key, item in dico_zmax.items()}
                cl_geo.plani_stock(dico_zmax, id_run, self.mdb)

                del cl_geo
        elif typ_res == 'basin':
            key_pknum = 'BNUM'
        elif typ_res == 'link':
            key_pknum = 'LNUM'
        elif 'tracer_' in typ_res:
            key_pknum = 'PK'
        list_insert.append([id_run, typ_res, 'pknum',
                            json.dumps(sorted(list(set(val[key_pknum]))))])

        col_tab = ['id_runs', 'type_res', 'var', 'val']
        if len(list_insert) > 0:
            self.mdb.insert_res('runs_graph', list_insert, col_tab)

    def lit_opt_new(self, id_run, date_debut, base_namefile, comments='',
                    tracer=False, casier=False):
        """
        Read opt files and save in results table
        :param id_run: run index
        :param date_debut: initial date
        :param base_namefile: file name without extension
        :param comments: comments
        :param tracer: if tracers are actived
        :param casier: if basins are actived
        :return:
        """
        nom_fich = os.path.join(self.dossierFileMasc, base_namefile + '.opt')
        # if self.mgis.DEBUG:
        self.mgis.add_info("Load data ....")
        if not os.path.isfile(nom_fich):
            self.mgis.add_info("Simulation Error: there aren't results")
            self.mdb.delete('runs', 'id={}'.format(id_run))
            return False

        # update do old results
        tab = {id_run: {}}
        if date_debut:
            tab[id_run]["init_date"] = "{:%Y-%m-%d %H:%M}".format(date_debut)
        if comments != '':
            tab[id_run]["comments"] = comments
        if tracer:
            tab[id_run]['wq'] = self.wq.cur_wq_mod
        if tab[id_run]:
            self.mdb.update("runs", tab, var='id')

        type_res = 'opt'
        init_col = ['TIME', 'BRANCH', 'SECTION', 'PK']
        val_opt = self.new_read_opt(nom_fich, type_res, init_col)
        key_val_opt = list(val_opt.keys())

        self.save_new_results(val_opt, id_run)

        self.save_run_graph(val_opt, id_run, type_res)
        del val_opt

        if casier:
            nom_fich_bas = os.path.join(self.dossierFileMasc,
                                        base_namefile + '.cas_opt')
            if not os.path.isfile(nom_fich_bas):
                self.mgis.add_info(
                    "Simulation Error: there aren't basin results")
            else:
                type_res = 'basin'
                init_col = ['TIME', 'BNUM']
                val = self.new_read_opt(nom_fich_bas, type_res, init_col)

                self.save_new_results(val, id_run)
                self.save_run_graph(val, id_run, type_res)

                del val

            nom_fich_link = os.path.join(self.dossierFileMasc,
                                         base_namefile + '.liai_opt')
            if not os.path.isfile(nom_fich_link):
                self.mgis.add_info(
                    "Simulation Error: there aren't link results")
            else:
                type_res = 'link'
                init_col = ['TIME', 'LNUM']
                val = self.new_read_opt(nom_fich_link, type_res, init_col)

                self.save_new_results(val, id_run)
                self.save_run_graph(val, id_run, type_res)
                del val
        if tracer:
            nom_fich_tra = os.path.join(self.dossierFileMasc,
                                        base_namefile + '.tra_opt')
            if not os.path.isfile(nom_fich_tra):
                self.mgis.add_info(
                    "Simulation Error: there aren't basin results")
            else:
                init_col = ['TIME', 'BRANCH', 'SECTION', 'PK']
                type_res = 'tracer_{}'.format(self.wq.cur_wq_mod)

                val = self.new_read_opt(nom_fich_tra, type_res, init_col)
                key_val_opt.remove('TIME')
                key_val_opt.remove('PK')
                val_key = list(val.keys())
                for key in val_key:
                    if key in key_val_opt:
                        del val[key]
                self.save_new_results(val, id_run)
                self.save_run_graph(val, id_run, type_res)
        if self.cond_api:
            self.stock_res_api(self.save_res_struct[0], self.save_res_struct[1])

    def save_new_results(self, val, id_run):
        """
        Save values in results table
        :param val: (dict) values
        :param id_run: run index
        :return: True
        """
        val_keys = val.keys()
        if 'PK' in val_keys:
            lpk = val['PK']
        elif 'BNUM' in val_keys:
            lpk = val['BNUM']
        elif 'LNUM' in val_keys:
            lpk = val['LNUM']

        d_res = {}
        d_sect = {}
        for var in val_keys:
            if isinstance(var, int):
                for tps, pk, value in zip(val['TIME'], lpk, val[var]):
                    if (pk, var) not in d_res.keys():
                        d_res[(pk, var)] = {'t': list(), 'v': list()}
                    d_res[(pk, var)]['t'].append(tps)
                    d_res[(pk, var)]['v'].append(value)

            elif var == 'BRANCH':
                init_pk = lpk[0]
                cond = False
                for pk, bra, sect in zip(lpk, val['BRANCH'], val['SECTION']):
                    if pk == init_pk and cond:
                        break
                    if  bra not in d_sect.keys() :
                        d_sect[bra] = {'sect' : [], 'pk': []}
                    d_sect[bra]['sect'].append(sect)
                    d_sect[bra]['pk'].append(pk)
                    cond = True

        values = list()
        for (pk, var), v in d_res.items():
            values.append([id_run, pk, var,
                           "{" + ','.join(str(i) for i in v['t']) + "}",
                           "{" + ','.join(str(i) for i in v['v']) + "}"])
        if len(values) > 0 :
            self.mdb.run_query("INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(self.mdb.SCHEMA) +
                               "VALUES (%s, %s, %s, %s, %s)", many=True, list_many=values)

        values = list()
        for bra, v in d_sect.items():
            values.append([id_run, bra,
                           "{" + ','.join(str(i) for i in v['sect']) + "}",
                           "{" + ','.join(str(i) for i in v['pk']) + "}"])
        if len(values) > 0 :
            self.mdb.run_query("INSERT INTO {}.results_sect(id_runs, branch, section, pk) ".format(self.mdb.SCHEMA) +
                               "VALUES (%s, %s, %s, %s)", many=True, list_many=values)

        return True

    def get_for_lig(self, id_run):
        """
         Get value to create the lig file
        :param id_run: run index
        :return: return value to create the lig file
        """
        result = {}
        try:
            var = self.mdb.select("results_var", "type_res = 'opt'", 'id',
                                  ['id', 'var'])
            idz = var['id'][var['var'].index("Z")]
            idq = var['id'][var['var'].index("Q")]
            t_max = self.mdb.select_max("time", "results",
                                        "var = {}  AND id_runs = {} ".format(
                                            idz, id_run) )
            if t_max is None:
                self.mgis.add_info(
                    "No previous results to create the .lig file.")
                return None
            value = self.mdb.select("results",
                                    "var = {} AND id_runs = {}  "
                                    "AND time = {}".format(
                                        idz, id_run, t_max),
                                    'pknum', ['val'])
            result['Z'] = value['val']
            value = self.mdb.select("results",
                                    "var = {} AND id_runs = {} "
                                    "AND time = {}".format(
                                        idq, id_run, t_max),
                                    'pknum', ['val'])
            result['Q'] = value['val']

            value = self.mdb.select("results_sect",
                                    "id_runs = {}".format(id_run), 'pk',
                                    ['pk', 'branch', 'section'])

            result['X'] = value['pk'][0]
            result["section"] = value['section'][0]
            nb_elem= len(result['X'])
            result["branche"] = value['branch'] * nb_elem


            del value
        except:
            self.mgis.add_info('No results for initialisation')
            return None

        return result

    def get_laws(self, name_obj, typ_law, obs=False, date_deb=None,
                 date_fin=None):
        """
        Get law
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
                                 """.format(name_obj, typ_law, date_deb,
                                            date_fin)
            else:
                condition = "geom_obj='{0}' AND id_law_type={1} AND active".format(
                    name_obj,
                    typ_law)
            # self.mgis.add_info('{}'.format(condition))

            config = self.mdb.select_one('law_config', condition, verbose=False)
            if config:
                values = self.mdb.select("law_values",
                                         where='id_law={}'.format(config['id']),
                                         order='id_var, id_order',
                                         list_var=['id_var',
                                                   'id_order',
                                                   'value'])
                lst_var = [tmp['code'] for tmp in dico_typ_law[typ_law]['var']]
                lst_idvar = [id for id, tmp in
                             enumerate(dico_typ_law[typ_law]['var'])]

                tab = {key: [] for key in lst_var}
                conv_idvar = {id: lst_var[i] for i, id in enumerate(lst_idvar)}

                for value, id_var in zip(values['value'], values['id_var']):
                    tab[conv_idvar[id_var]].append(float(value))

                return tab
            else:
                err = "Error: Please check if law for {0} object " \
                      "is correct. \n".format(
                    name_obj)
                self.mgis.add_info(err)
                raise Exception(err)
                return None

        except Exception as e:
            err = "Error: Please check if law for {0} object " \
                  "is correct. \n".format(name_obj)
            err += str(e)
            self.mgis.add_info(err)
            raise Exception(err)
            return None

    def check_timelaw(self, par, name, initime, lasttime):
        cond = False
        if par['tempsInit'] < initime:
            self.err_model['timeLaw'].add_err(name,
                                             " Error law {} on the Initial Time".format(name))
            cond = True
        if par['critereArret'] == 1:
            # tmax
            if par['tempsMax'] > lasttime:
                self.err_model['timeLaw'].add_err(name,
                                                 " Error law {} on the Last Time".format(name))
                cond = True
        elif par['critereArret'] == 2:
            # nb iterration
            if par['nbPasTemps'] * par['pasTemps'] > lasttime:
                self.err_model['timeLaw'].add_err(name,
                                                 " Error law {} on the Last Time".format(name))
                cond = True

        return cond

    def check_apport(self):
        """checks if the inflow is before the first mesh."""
        #
        apports = self.mdb.select("lateral_inflows", "active", "abscissa")
        for i, numb in enumerate(apports['branchnum']):
            branches = self.mdb.select_one("visu_branchs",
                                           "branchnum={}".format(numb), 'abs_start',
                                           list_var=['abs_start', 'mesh'])

            comp = branches['abs_start'] + branches['mesh']
            if apports['abscissa'][i] < comp:
                self.err_model['lInflowPos'].add_err(apports['name'][i],
                                                    'Warning: {} is located before the first mesh.'
                                                    ' Ignore in the model'.format(apports['name'][i]))
