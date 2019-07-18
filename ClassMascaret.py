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

import csv
import datetime
import os
import re
import shutil
import subprocess
import sys
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as et_parse

from qgis.PyQt.QtCore import qVersion
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .Function import str2bool, del_accent
from .Structure.ClassMethod import ClassMethod
from .WaterQuality.ClassMascWQ import ClassMascWQ
from .ui.custom_control import ClassWarningBox

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *


class ClassMascaret:
    """ Class contain  model files creation and run model mascaret"""

    def __init__(self, main):
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.iface = self.mgis.iface
        self.dossierFileMasc = os.path.join(self.mgis.masplugPath, "mascaret")
        if not os.path.isdir(self.dossierFileMasc):
            os.mkdir(self.dossierFileMasc)
        self.dossierFileMascOri = os.path.join(self.mgis.masplugPath, "mascaret_ori")
        self.baseName = "mascaret"
        self.nomfichGEO = self.baseName + ".geo"
        self.box = ClassWarningBox(self.mgis)
        # state list
        self.listeState = ['Steady', 'Unsteady', 'Transcritical unsteady']
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]
        self.wq = ClassMascWQ(self.mgis, self.dossierFileMasc)
        self.clmeth = ClassMethod(self.mgis)


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

                    if branche and abs and temp_x and temp_z and lit_min_g and lit_min_d:
                        # tabX = list(map(lambda x: round(float(x), 2), temp_x.split()))
                        # tab_z = list(map(lambda x: round(float(x), 2), temp_z.split()))
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

                            fich.write('{0:.2f} {1:.2f} {2}\n'.format(x, z, type))
            self.mgis.add_info("Creation the geometry is done")
        except Exception as e:
            self.mgis.add_info("Error: save the geometry")
            self.mgis.add_info(str(e))

    def creer_geo_ref(self):
        # """creation of gemoetry file"""
        try:
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
                           '#  PROJ. : {1}\n'.format(datetime.date.today(), vlayer_crs_str))

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
                        if branche is not None and abs is not None and temp_x is not None \
                                and temp_z is not None and lit_min_g is not None and lit_min_d is not None:
                            tab_z = []
                            tab_x = []
                            # fct1 = lambda x: round(float(x), 2)
                            for var1, var2 in zip(temp_x.split(), temp_z.split()):
                                tab_x.append(self.around(var1))
                                tab_z.append(self.around(var2))
                            # tab_x = list(map(lambda x: round(float(x), 2), temp_x.split()))
                            # tab_z = list(map(lambda x: round(float(x), 2), tempZ.split()))

                            points = geom.asMultiPolyline()[0]
                            (cood1X, cood1Y) = points[0]
                            (cood2X, cood2Y) = points[1]
                            cood_axe_x = cood1X + (cood2X - cood1X) / 2.
                            cood_axe_y = cood1Y + (cood2Y - cood1Y) / 2.

                            fich.write('PROFIL Bief_{0} {1} {2} {3} {4} {5} {6} AXE {7} {8}\n'.format(branche, nom, abs,
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
                                fich.write('{0:.2f} {1:.2f} {2} {3} {4}\n'.format(x, z, type, dpoint[0], dpoint[1]))

            self.mgis.add_info("Creation the geometry is done")
        except Exception as e:
            self.mgis.add_info("Error: save the geometry")
            self.mgis.add_info(str(e))
            # Fonction de creation du fichier .casier avec la loi surface-volume

    def creer_geo_casier(self):
        try:
            nomfich = os.path.join(self.dossierFileMasc, self.baseName + '.casier')

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
                            '{0:.2f} {1:.2f} {2:.2f}\n'.format(float(cotes.split()[j]), float(surfaces.split()[j]),
                                                               float(volumes.split()[j])))

            self.mgis.add_info("Creation of the basin file is done")
        except Exception as e:
            self.mgis.add_info("Error: save the basin file")
            self.mgis.add_info(str(e))
            # Fonction de remplacement des None de la liste par la valeur remplaceNone
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
                # Ajout d'une valeur nulle codee ici par remplaceNone, cad -1 ou -1.0, pour le moteur mascaret
                liste_num_masca.append(remplace_none)
            else:
                # Inversion du dictionnaire: on cherche le numero mascaret pour le numero de casier sous Qgis
                liste_num_masca.append(list(dico_num.keys())[list(dico_num.values()).index(num_qgis)])
        return " ".join([str(var) for var in liste_num_masca])

        # Fonction de calcul du planimetrage entre 2 niveaux de la loi surface volume du casier

    def fmt_plani_casier(self, liste):
        liste_plani = []
        for chaine_z in liste:
            try:
                liste_z = chaine_z.split()
                # Calcul des parties entieres et decimale de la planimetrie
                plani_entier = int((float(liste_z[1]) - float(liste_z[0])) // 1)
                liste_plani.append(str(plani_entier))
                plani_decimale = int((float(liste_z[1]) - float(liste_z[0])) % 1)
                if plani_decimale > 0:
                    self.mgis.add_info("Simulation Error: the basin planimetry has to be an integer value")
            except:
                self.mgis.add_info("Simulation Error: the basin planimetry is not correct")
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

    def planim_select(self):
        sql = """SELECT MIN(t1.planim) AS pas, MIN(t2.nombre),MAX(t2.nombre) 
                 FROM (SELECT branch, planim, ST_UNION(geom) AS geom
                       FROM  (SELECT branch, 
                                     planim, 
                                     geom,
                                     row_number() 
                                        OVER (PARTITION BY branch, planim 
                                              ORDER BY zonenum)
                                        - zonenum AS grp
                              FROM   {0}.branchs
                              WHERE active) x
                       GROUP  BY branch, planim, grp) AS t1,
                      (SELECT ROW_NUMBER() OVER(ORDER BY abscissa) AS nombre, geom 
                       FROM {0}.profiles 
                       WHERE active ) AS t2 
                 WHERE ST_INTERSECTS(t1.geom,t2.geom) 
                 GROUP BY t1.geom
                 ORDER BY min;"""

        (results, namCol) = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True, namvar=True)

        dico = {}
        colonnes = [col[0] for col in namCol]
        for col in colonnes:
            dico[col] = []

        for row in results:
            for i, val in enumerate(row):

                try:
                    dico[colonnes[i]].append(val.strip())
                except:
                    dico[colonnes[i]].append(val)

        return dico

    def maillage_select(self):
        sql = """SELECT MIN(t1.mesh) AS pas, 
                                    MIN(t2.nombre),
                                    MAX(t2.nombre)+MIN(diff)+1 AS max
                             FROM (SELECT branch, mesh, 
                                          ST_UNION(geom) AS geom, 
                                          MIN(diff) AS diff 
                                   FROM  (SELECT branch, 
                                                 mesh, 
                                                 geom,
                                                 row_number() 
                                                    OVER (PARTITION BY branch,  mesh 
                                                          ORDER BY zonenum)
                                                    - zonenum AS grp,
                                                 branch-lead(branch,1,branch+1) 
                                                    OVER (ORDER BY zonenum) AS diff
                                          FROM   {0}.branchs
                                          WHERE active) x
                                   GROUP  BY branch, mesh, grp) AS t1,
                                  (SELECT ROW_NUMBER() OVER(ORDER BY abscissa) AS nombre, geom 
                                   FROM {0}.profiles 
                                   WHERE active ) AS t2 
                             WHERE ST_INTERSECTS(t1.geom,t2.geom) 
                             GROUP BY t1.geom
                             ORDER BY min;"""

        (results, namCol) = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True, namvar=True)

        dico = {}
        colonnes = [col[0] for col in namCol]
        for col in colonnes:
            dico[col] = []

        for row in results:
            for i, val in enumerate(row):

                try:
                    dico[colonnes[i]].append(val.strip())
                except:
                    dico[colonnes[i]].append(val)

        return dico

    def creer_xcas(self, noyau):
        """To create xcas file"""
        dict_lois = {}
        # try:
        fichier_sortie = os.path.join(self.dossierFileMasc, self.baseName + ".xcas")
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
        sql = "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} WHERE gui_type = 'parameters' ORDER BY id;"
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, b1, b2 in rows:
            # self.mgis.add_info("valeur : {0},  param : {1}  ,  b1 : {2} , b2: {3}".format(valeur, param, b1, b2))
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
        zones = self.mdb.select("branchs", "active", "branch, zoneabsstart")
        deversoirs = self.mdb.select("lateral_weirs", "active", "abscissa")
        noeuds = self.mdb.select("extremities", "type=10", "active")
        libres = self.mdb.select("extremities", "type!=10 ", "active")
        pertescharg = self.mdb.select("hydraulic_head", "active", "abscissa")
        profils = self.mdb.select("profiles", "active", "abscissa")
        prof_seuil = self.mdb.select("profiles", "NOT active", "abscissa")
        seuils = self.mdb.select("weirs", "active", "abscissa")
        sorties = self.mdb.select("outputs", "", "abscissa")
        planim = self.planim_select()
        maillage = self.maillage_select()
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
        dict_libres = {"nom": [], "num": [], "extrem": [], "typeCond": [], "typeCond_tr": [], "law_wq": []}
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
                # TODO add 'formule': formule, 'valeurperm': libres["firstvalue"

                dict_lois[d] = {'type': extr_toloi[type],
                                'formule': formule,
                                'valeurperm': libres["firstvalue"][i]}

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
                # TODO add 'formule': formule, 'valeurperm': libres["firstvalue"
                dict_lois[f] = {'type': extr_toloi[type],
                                'formule': formule,
                                'valeurperm': libres["firstvalue"][i]}
        # Zones
        nb_pas = 0
        i = 0
        #  zones['num1erProf'] = [1] * len(zones["zoneabsstart"])
        #  zones['numDerProfPlanim'] = [1] * len(zones["zoneabsstart"])
        #  zones['numDerProfMaill'] = [1] * len(zones["zoneabsstart"])
        liste_stock = {"numProfil": [],
                       'limGauchLitMaj': [],
                       'limDroitLitMaj': []}

        tab = zip(profils["abscissa"],
                  profils["x"],
                  profils["z"],
                  profils["leftstock"],
                  profils["rightstock"],
                  profils["branchnum"])

        for j, (abs, x, z, sg, sd, n) in enumerate(tab):

            try:
                xx = [float(var) for var in x.split()]
                zz = [float(var) for var in z.split()]
                diff = max(zz) - min(zz)
            except:
                self.mgis.add_info("Check the {} profile if it's ok ".format(profils["name"][j]))
                return dict_lois

            if abs > zones['zoneabsend'][i]:
                i = i + 1

            try:
                nb_pas = max(int(diff / float(zones['planim'][i])) + 1, nb_pas)
            except:
                self.mgis.add_info("Check planim ")

            index = numero.index(n)
            zones["zoneabsstart"][i] = max(zones["zoneabsstart"][i],
                                           branches["abscdebut"][index])
            zones["zoneabsend"][i] = min(zones["zoneabsend"][i],
                                         branches["abscfin"][index])

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
                dict_lois[seuils["name"][i]] = {'type': abaque_toloi[type]}

        for i, nom in enumerate(apports["name"]):
            if nom not in dict_lois.keys():
                dict_lois[nom] = {'type': 1,
                                  'formule': apports['method'][i],
                                  'valeurperm': apports["firstvalue"][i]}

        for i, nom in enumerate(deversoirs["name"]):
            if nom not in dict_lois.keys() and deversoirs["type"][i] == 2:
                dict_lois[nom] = {'type': 4}

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
        liste_en = ["type", "branchnum", "abscissa", "z_crest", "z_average_crest",
                    "z_break", "flowratecoeff", "wide_floodgate", "thickness"]

        for i, nom in enumerate(seuils["name"]):
            struct = SubElement(e_tseuils, "structureParametresSeuil")
            SubElement(struct, "nom").text = nom
            for kk, l in enumerate(liste):
                if seuils[liste_en[kk].lower()][i] is None:
                    SubElement(struct, l).text = '-0'
                else:
                    SubElement(struct, l).text = str(seuils[liste_en[kk].lower()][i])

            if seuils["type"][i] not in (3, 4):
                SubElement(struct, "numLoi").text = str(sorted(dict_lois.keys()).index(nom) + 1)
            else:
                SubElement(struct, "numLoi").text = '-0'

            if seuils["type"][i] != 3:
                SubElement(struct, "nbPtLoiSeuil").text = '-0'
            else:
                try:
                    i = prof_seuil["name"].index(nom)
                    long = len(prof_seuil['x'][i].split())
                    SubElement(struct, "nbPtLoiSeuil").text = str(long)
                    SubElement(struct, "abscTravCrete").text = prof_seuil['x'][i]
                    SubElement(struct, "cotesCrete").text = prof_seuil['z'][i]

                except:
                    msg = 'Profil de crete introuvable pour {}'
                    QMessageBox.warning(None, 'Message', msg.format(nom))
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
            self.mgis.add_info('Warning : Geometric object for lateral inflows is not found')
        SubElement(e_tapports, "abscisses").text = self.fmt(apports["abscissa"])
        if self.check_none(apports["length"]):
            self.mgis.add_info('Warning : Lenght for lateral inflows is not found')
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
        for kk, l in enumerate(["numBranche", "abscisse", "longueur", "coteCrete", "coeffDebit"]):
            SubElement(devers_late, l).text = self.fmt(deversoirs[l_en[kk].lower()])

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
        for kk, l in enumerate(["absDebZone", "absFinZone", "coefLitMin", "coefLitMaj"]):
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
            if nom in libres["name"] and (dict_lois[nom]['type'] == 6 or dict_lois[nom]['type'] == 7):
                # les types sont ceux de
                # print( dictLois[nom]['type'], nom)
                if dict_lois[nom]['type'] == 6:  # TODO and noyau!='transcritical'
                    dict_lois[nom]['type'] = 1
                    if self.mgis.DEBUG:
                        self.mgis.add_info('The  {} law changes type 6 => 1'.format(nom))
                elif dict_lois[nom]['type'] == 7:
                    dict_lois[nom]['type'] = 2
                    if self.mgis.DEBUG:
                        self.mgis.add_info('The  {} law changes type 7 => 2'.format(nom))

        nb = len(dict_lois.keys())
        SubElement(hydrauliques, "nb").text = str(nb)
        lois = SubElement(hydrauliques, "lois")

        for nom in sorted(dict_lois.keys()):
            struct = SubElement(lois, "structureParametresLoi")
            SubElement(struct, "nom").text = nom
            SubElement(struct, "type").text = str(dict_lois[nom]['type'])
            donnees = SubElement(struct, "donnees")
            SubElement(donnees, "modeEntree").text = '1'
            SubElement(donnees, "fichier").text = '{}.loi'.format(nom)
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
        if noyau == 'steady':

            param_cas = fichier_cas.find('parametresCas')
            parametres_generaux = param_cas.find('parametresGeneraux')
            geom_reseau = param_cas.find('parametresGeometrieReseau')
            type_cond = geom_reseau.find('extrLibres').find('typeCond')
            type_cond.text = type_cond.text.replace('4', '2')
            lois_hydrauliques = param_cas.find('parametresLoisHydrauliques')
            lois = lois_hydrauliques.find('lois')
            for child in lois:
                if child.find('type').text == '5':
                    child.find('type').text = '2'

        # **********************************
        self.indent(fichier_cas)
        arbre = ElementTree(fichier_cas)
        arbre.write(fichier_sortie)

        # ****** XCAS initialisation **********
        dt_init = 60
        np_pas_temps_init = int(3600 / 60.)

        param_cas = fichier_cas.find('parametresCas')
        parametres_generaux = param_cas.find('parametresGeneraux')
        fich_xcas = '{}_init.xcas'.format(self.baseName)
        parametres_generaux.find('fichMotsCles').text = fich_xcas
        parametres_generaux.find('code').text = '1'
        parametres_generaux.find('presenceCasiers').text = 'false'
        parametres_temporels = param_cas.find('parametresTemporels')
        parametres_temporels.find('pasTemps').text = '{}'.format(dt_init)
        parametres_temporels.find('critereArret').text = '2'
        parametres_temporels.find('nbPasTemps').text = '{}'.format(np_pas_temps_init)
        parametres_temporels.find('pasTempsVar').text = 'false'
        geom_reseau = param_cas.find('parametresGeometrieReseau')
        type_cond = geom_reseau.find('extrLibres').find('typeCond')
        type_cond.text = type_cond.text.replace('4', '2').replace('6', '1').replace('7', '2')
        lois_hydrauliques = param_cas.find('parametresLoisHydrauliques')
        lois = lois_hydrauliques.find('lois')
        for child in lois:
            if child.find('type').text == '5':
                child.find('type').text = '2'
            donnee = child.find('donnees').find('fichier')
            temp = donnee.text.split('.')
            donnee.text = '{}_init.loi'.format(temp[0])

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

        self.mgis.add_info("Save the Xcas file is done")
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
                dico_loi_struct[name]['id_config'] = loi_struct['id_config'][idx]
                del dict_lois[name]
        # print(dico_loi_struct)
        return dict_lois, dico_loi_struct

    def add_basin_xcas(self, fichier_cas, casiers, liaisons):
        # Creation du dictionnaire de numero de casier entre mascaret (cle) et qgis (valeur)
        self.dico_basinnum = {}
        for i, num_qgis in enumerate(casiers["basinnum"], 1):
            self.dico_basinnum[i] = num_qgis
        # Creation du dictionnaire de numero de liaison entre mascaret (cle) et qgis (valeur)
        self.dico_linknum = {}
        for i, num_qgis in enumerate(liaisons["linknum"], 1):
            self.dico_linknum[i] = num_qgis
        # Creation des lignes a ajouter dans Xcas
        cas = fichier_cas.find('parametresCas')
        casier = SubElement(cas, "parametresCasier")
        SubElement(casier, "nbCasiers").text = str(len(casiers["name"]))
        SubElement(casier, "optionPlanimetrage").text = self.fmt_plani_casier(casiers["level"])
        SubElement(casier, "optionCalcul").text = "1"  # Todo
        SubElement(casier, "fichierGeomCasiers").text = "mascaret.casier"  # Todo
        SubElement(casier, "cotesInitiale").text = self.fmt_sans_none(casiers["initlevel"], '-1.0')
        # Liaisons (champs non listes = active et linknum)
        et_liaisons = SubElement(casier, "liaisons")
        SubElement(et_liaisons, "nbLiaisons").text = str(len(liaisons["name"]))
        SubElement(et_liaisons, "types").text = self.fmt_sans_none(liaisons["type"], '-1.0')
        SubElement(et_liaisons, "nature").text = self.fmt_sans_none(liaisons["nature"], '-1.0')
        SubElement(et_liaisons, "cote").text = self.fmt_sans_none(liaisons["level"], '-1.0')
        SubElement(et_liaisons, "largeur").text = self.fmt_sans_none(liaisons["width"], '-1.0')
        SubElement(et_liaisons, "longueur").text = self.fmt_sans_none(liaisons["length"], '-1.0')
        SubElement(et_liaisons, "rugosite").text = self.fmt_sans_none(liaisons["roughness"], '-1.0')
        SubElement(et_liaisons, "section").text = self.fmt_sans_none(liaisons["crosssection"], '-1.0')
        SubElement(et_liaisons, "coefPerteCharge").text = self.fmt_sans_none(liaisons["headlosscoef"], '-1.0')
        SubElement(et_liaisons, "coefDebitSeuil").text = self.fmt_sans_none(liaisons["weirdischargecoef"], '-1.0')
        SubElement(et_liaisons, "coefActivation").text = self.fmt_sans_none(liaisons["activationcoef"], '-1.0')
        SubElement(et_liaisons, "coefDebitOrifice").text = self.fmt_sans_none(liaisons["pipedischargecoef"],
                                                                             '-1.0')
        SubElement(et_liaisons, "typeOrifice").text = self.fmt_sans_none(liaisons["culverttype"], '-1')
        SubElement(et_liaisons, "numCasierOrigine").text = self.fmt_num_basin(liaisons["basinstart"],
                                                                              self.dico_basinnum, '-1')
        SubElement(et_liaisons, "numCasierFin").text = self.fmt_num_basin(liaisons["basinend"], self.dico_linknum,
                                                                         '-1')
        SubElement(et_liaisons, "numBiefAssocie").text = self.fmt_sans_none(liaisons["branchnum"], '-1')
        SubElement(et_liaisons, "abscBief").text = self.fmt_sans_none(liaisons["abscissa"], '-1.0')

    def add_wq_xcas(self, fichier_cas, noyau, dict_libres):
        """Modification of xcas for Water Quality"""
        # requête pour récupérer les paramètres
        cas = fichier_cas.find('parametresCas')
        sql = "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} WHERE gui_type = 'tracers' ORDER BY id;"

        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, b1, b2 in rows:
            if param == "fichMeteoTracer":
                sql = "SELECT {0} FROM {1}.{2} WHERE parametre = 'fichmeteo' ;"
                wow = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
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
        # # TODO add 'formule': formule, 'valeurperm': libres["firstvalue"
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
            self.mgis.add_info('Warning : Geometric object for tracer lateral inflows is not found')
        SubElement(tracer_source, "abscisses").text = self.fmt(abs)
        if self.check_none(leng):
            self.mgis.add_info('Warning : Lenght for tracer lateral inflows is not found')
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
                SubElement(struct, "fichier").text = '{}.loi'.format(name)
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
        loi_struct = {}
        loi_struct['laws'] = []
        loi_struct['id_config'] = []
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

        if meth == 0 or meth == 4 or meth == 1 or meth == 5  or meth == 3:
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

    def creer_loi(self, nom, tab, type):
        with open(os.path.join(self.dossierFileMasc, nom + '.loi'), 'w') as fich:
            fich.write('# ' + nom + '\n')
            if type == 1:
                fich.write('# Temps (S) Debit\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {flowrate:.6f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.add_info("\n")
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t Flow Rate :{2}"
                #                       .format(nom, tab["temps"], tab["debit"]))

            elif type == 2:
                fich.write('# Temps (S) Cote\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z:.6f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.add_info("\n")
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t Water Level :{2}"
                #                       .format(nom, tab["temps"],tab["cote"]))
            elif type == 3:
                fich.write('# Temps (S) Cote Debit\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z:.6f} {flowrate:.6f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.add_info("\n")
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t Water Level :{2}\n \t Flow Rate {3}"
                #                       .format(nom, tab["temps"],tab["cote"],tab["debit"]))
            elif type == 4:
                fich.write('# Debit Cote\n')
                chaine = ' {flowrate:.3f} {z:.6f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.add_info("\n")
                #     self.mgis.add_info("{0} :\n \t Flow Rate {2}\n \t Water Level :{1}"
                #                       .format(nom, tab["cote"],tab["debit"]))
            elif type == 5:
                fich.write('# Cote Debit\n')
                chaine = ' {z:.6f} {flowrate:.6f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.add_info("\n")
                #     self.mgis.add_info("{0} :\n \t Water Level :{1}\n \t Flow Rate {2}"
                #                       .format(nom, tab["cote"],tab["debit"]))
            elif type == 6:
                fich.write('# Debit Cote_Aval Cote_Amont\n')
                chaine = ' {flowrate:.6f} {z_downstream:.6f} {z_upstream:.6f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.add_info("\n")
                #     self.mgis.add_info("{0} :\n \t Upstream Water Level{1}\n \t  Downstream Water Level :{2}"
                #                       .format(nom, tab["cote_amont"], tab["cote_aval"]))
            elif type == 7:
                fich.write('# Temps (s) Cote inférieur Cote supérieur\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z_lower:.6f} {z_up:.6f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.add_info("\n")
                #     self.mgis.add_info("{0} :\n \t Time : {1}\n \t Upstream Water Level{2}\n \t  "
                #                       "Downstream Water Level :{3}"
                #                       .format(nom,tab["temps"], tab["cote_amont"], tab["cote_aval"]))
            n = len(list(tab.values())[0])

            for i in range(n):
                dico = {k: v[i] for k, v in tab.items()}
                fich.write(chaine.format(**dico))

    def obs_to_loi(self, dict_lois, date_debut, date_fin):
        """
        Creation law with observation data
        :param dict_lois:
        :param date_debut:
        :param date_fin:
        :return:
        """
        pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        somme = 0
        debit_prec = 0
        obs = {}
        duree = int((date_fin - date_debut).total_seconds() / 3600)

        # liste_date = [date_debut + datetime.timedelta(hours=x)
        # for x in range(duree)]

        for nom, loi in dict_lois.items():
            if loi['type'] == 1:
                type = 'Q'
            elif loi['type'] == 2:
                type = 'H'
            else:
                continue

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
                    #liste_date = map(lambda x: x - dt, obs[cd_hydro]['date'])
                    liste_date = [x - dt for x in obs[cd_hydro]['date']]

            fichier_loi = os.path.join(self.dossierFileMasc, nom + '.loi')
            valeur_init = None

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

            if valeur_init is not None:
                if type == "Q":
                    tab = {'time': [0, 3600], 'flowrate': [valeur_init, valeur_init]}
                    self.creer_loi(nom + '_init', tab, 1)
                else:
                    tab = {'time': [0, 3600], 'z': [valeur_init, valeur_init]}
                    self.creer_loi(nom + '_init', tab, 2)

        for nom, loi in dict_lois.items():
            if loi['type'] != 5:
                continue
            condition = """name ='{0}' 
                        AND type = {1}
                        AND starttime <= '{2:%Y-%m-%d %H:%M}' 
                        AND endtime >= '{3:%Y-%m-%d %H:%M}'
                        """.format(nom, loi['type'], date_debut, date_fin)

            temp = self.mdb.select_one('laws', condition)
            # cote = list(map(float, temp['z'].split()))
            # debit = list(map(float, temp['flowrate'].split()))
            cote = [float(var) for var in temp['z'].split()]
            debit = [float(var) for var in temp['flowrate'].split()]

            self.creer_loi(nom, {'z': cote, 'flowrate': debit}, 5)

            for c, d in zip(cote, debit):
                if debit_prec > 0 and d > somme:
                    valeur_init = (c - cote_prec) \
                                  / (d - debit_prec) \
                                  * (somme - debit_prec) \
                                  + cote_prec
                    break
                else:
                    cote_prec, debit_prec = c, d
            if valeur_init is not None:
                tab = {'time': [0, 3600], 'z': [valeur_init, valeur_init]}
                self.creer_loi(nom + '_init', tab, 2)

    def  fct_comment(self):
        liste_col = self.mdb.list_columns('runs')
        if 'comments' in liste_col:
            comments, ok = QInputDialog.getText(QWidget(), 'Comments',
                                                'if you want to input a comment :')
            if not ok:
                if self.mgis.DEBUG:
                    self.mgis.add_info("No comments.")
                    comments = ''
        else:
            comments = ''
        return comments.replace("'","''")

    def mascaret(self, noyau, run):
        """creation file and to run mascaret"""
        comments = ''
        sql = "SELECT parametre, {0} FROM {1}.{2};"
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        par = {}

        for param, valeur in rows:
            try:
                par[param] = eval(valeur.title())
            except:
                par[param] = valeur
        if not par['repriseCalcul']:
            self.clean_rep()
            self.creer_geo_ref()
            if self.mgis.DEBUG:
                self.mgis.add_info("Geometric file is created.")
                self.mgis.add_info("noyau {}".format(noyau))
        else:
            self.clean_res()

        # Creation du fichier de la geometrie des casiers uniquement en non-permanent et si presence des casiers
        if par["presenceCasiers"] and noyau == "unsteady":
            self.creer_geo_casier()

        if par["evenement"] and noyau != "steady":

            dict_scen_tmp = self.mdb.select('events', 'run', 'starttime')
            listexclu = []
            if len(dict_scen_tmp['name']) == 0:
                self.mgis.add_info("Warning: scenario not found")
            for i, scen in enumerate(dict_scen_tmp['name']):
                # self.mgis.add_info("scen******************* {}".format(scen))
                if not self.check_scenar(scen, run):
                    self.mgis.add_info("Canceled Simulation because of {0} already exists.".format(scen))
                    listexclu.append(i)
            if listexclu:
                dict_scen = {}
                for key in dict_scen_tmp:
                    value = dict_scen_tmp[key]
                    value = [elt for idx, elt in enumerate(value) if not (idx in listexclu)]
                    dict_scen[key] = value
            else:
                dict_scen = dict_scen_tmp
        else:
            scen, ok = QInputDialog.getText(QWidget(), 'Scenario name',
                                            'Please input a scenario name :')
            if not ok or not self.check_scenar(scen, run):
                if self.mgis.DEBUG:
                    self.mgis.add_info("Canceled Simulation because of {0} already exists.".format(scen))
                return
            comments=self.fct_comment()

            dict_scen = {'name': [scen]}

        # progressMessageBar = self.iface.messageBar().createMessage(
        #     "Run ...")
        # self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)

        date_debut = None

        dict_lois, dico_loi_struct = self.creer_xcas(noyau)
        if self.mgis.DEBUG:
            self.mgis.add_info("Xcas file is created.")
        if par['presenceTraceurs']:
            self.wq.create_filephy()
            self.wq.law_tracer()
            self.wq.init_conc_tracer()

        if dico_loi_struct.keys():
            for name in dico_loi_struct.keys():
                list_final = self.clmeth.get_list_law(dico_loi_struct[name]['id_config'])

                self.clmeth.create_law(self.dossierFileMasc, name, dico_loi_struct[name]['type'], list_final)
                self.clmeth.create_law(self.dossierFileMasc, name + '_init', dico_loi_struct[name]['type'],
                                       list_final)

        if self.mgis.DEBUG:
            self.mgis.add_info("Tracer files are created.")

        for i, scen in enumerate(dict_scen['name']):
            if self.mgis.DEBUG:
                self.mgis.add_info("The current scenario is {}".format(scen))
            if noyau == "steady":
                if par['presenceTraceurs']:
                    if self.wq.dico_phy[self.wq.cur_wq_mod]['meteo']:
                        self.wq.create_filemet()
                # steady
                for nom, l in dict_lois.items():
                    if "valeurperm" not in l.keys():
                        continue
                    if l["valeurperm"] is None:
                        self.mgis.add_info("Error : Add the 'valeurprerm' value in extremities.")

                    try:
                        liste_ = ['pasTemps', 'critereArret', 'nbPasTemps', 'tempsMax', 'tempsInit']
                        temp_dic = {}
                        for info in liste_:
                            condition = "parametre ='{}'".format(info)
                            dtemp = self.mdb.select_distinct('steady', 'parametres', condition)
                            temp_dic[info] = dtemp['steady'][0]
                    except Exception as e:
                        self.mgis.add_info(str(e))
                        return
                    if temp_dic['critereArret'] == 1:
                        tfinal = temp_dic['tempsMax']
                    elif temp_dic['critereArret'] == 2:
                        tfinal = temp_dic['tempsInit'] + temp_dic['pasTemps'] * temp_dic['nbPasTemps']
                    elif temp_dic['critereArret'] == 3:
                        tfinal = 365 * 24 * 3600
                    if l['type'] == 1:
                        tab = {"time": [0, tfinal], 'flowrate': [l["valeurperm"]] * 2}
                    else:
                        # In steady case the other type don't exist
                        l['type'] = 2
                        tab = {"time": [0, tfinal], 'z': [l["valeurperm"]] * 2}

                    self.creer_loi(nom, tab, l['type'])

            elif par["evenement"]:
                # transcritical unsteady evenement
                if par['presenceTraceurs']:
                    if self.wq.dico_phy[self.wq.cur_wq_mod]['meteo']:
                        self.wq.create_filemet()
                date_debut = dict_scen['starttime'][i]
                date_fin = dict_scen['endtime'][i]
                duree = int((date_fin - date_debut).total_seconds()) - 3600

                tab = {"tempsMax": {'valeur': str(duree),
                                    'balise1': 'parametresTemporels'},
                       "titreCalcul": {'valeur': scen,
                                       'balise1': 'parametresImpressionResultats'}
                       }
                self.modif_xcas(tab, self.baseName + '.xcas')
                self.mgis.add_info("Xcas file is created.")
                if par['presenceTraceurs']:
                    if self.wq.dico_phy[self.wq.cur_wq_mod]['meteo']:
                        self.wq.create_filemet(typ_time='date', datefirst=date_debut, dateend=date_fin)

                self.obs_to_loi(dict_lois, date_debut, date_fin)

            else:
                # TODO ATTENTION CREATION LOI STRUCTUR HYdraulic
                # transcritical unsteady hors evenement
                if par['presenceTraceurs']:
                    if self.wq.dico_phy[self.wq.cur_wq_mod]['meteo']:
                        self.wq.create_filemet()

                for nom, l in dict_lois.items():
                    # dictLois.items() extremities liste
                    condition = "name ='{0}' AND type={1}".format(nom, l["type"])
                    # self.mgis.add_info('{}'.format(condition))
                    try:
                        temp = self.mdb.select_one('laws', condition)
                    except Exception as e:
                        self.mgis.add_info("Error: Please check if law {0} is correct. ".format(nom))
                        self.mgis.add_info(str(e))
                        return

                    liste = ["z", "flowrate", "time", "z_upstream", "z_downstream",
                             "z_lower", "z_up"]
                    tab = {}
                    for k, v in temp.items():
                        if v and k in liste:
                            tab[k] = [float(var) for var in v.split()]

                    self.creer_loi(nom, tab, l["type"])
                    if self.mgis.DEBUG:
                        self.mgis.add_info("Laws file is created.")

                    if "valeurperm" not in l.keys():
                        continue

                    nom = nom + "_init"
                    # 3600 To change TODO
                    if l["valeurperm"] is not None:
                        if l['type'] == 1:
                            tab = {"time": [0, 3600], 'flowrate': [l["valeurperm"]] * 2}
                            self.creer_loi(nom, tab, 1)
                        elif l['type'] in [2, 4, 5]:
                            tab = {"time": [0, 3600], 'z': [l["valeurperm"]] * 2}
                            self.creer_loi(nom, tab, 2)
                        else:
                            par["initialisationAuto"] = False
                            self.mgis.add_info("No initialisation")
                    else:
                        par["initialisationAuto"] = False
                        self.mgis.add_info("No initialisation because of no valeurperm for {} condition".format(nom))

            if par["initialisationAuto"] and noyau is not "steady":
                # add if name of init. exist previously
                sceninit = scen + '_init'
                if self.check_scenar(sceninit, run):
                    self.mgis.add_info("========== Run initialization =========")
                    self.mgis.add_info("Run = {} ;  Scenario = {} ; Kernel= {}".format(run, sceninit, noyau))
                    self.lance_mascaret(self.baseName + '_init.xcas')
                    self.lit_opt(run, sceninit, None,
                                 self.baseName + '_init', comments, par['presenceTraceurs'])
                else:
                    self.mgis.add_info("No Run initialization.\n"
                                       " The initial boundaries come from {} scenario.".format(sceninit))

                self.opt_to_lig(run, sceninit, self.baseName)
                tab = {"LigEauInit": {'valeur': 'true',
                                      'balise1': 'parametresConditionsInitiales',
                                      'balise2': 'ligneEau'}
                       }
                self.modif_xcas(tab, self.baseName + '.xcas')

            elif par["LigEauInit"] and noyau != "steady":
                # condition = "run LIKE 'Steady'"
                # dico_run = self.mdb.select_distinct("scenario",
                #                                    "runs", condition)
                # dico_run = self.mdb.select("runs")
                #
                # if not dico_run and self.mgis.DEBUG:
                #     self.mgis.add_info("There aren't scenarii for the Steady case.")
                #     if self.mgis.DEBUG:
                #         self.mgis.add_info("Cancel run")
                #     return

                # liste2=list(dico_run["scenario"])

                dico_run = self.mdb.select_distinct("run",
                                                    "runs")
                if dico_run != {}:
                    liste_run = ['{}'.format(v) for v in dico_run['run']]
                else:
                    liste_run = []
                liste_run.append('".lig" File')
                case, ok = QInputDialog.getItem(None,
                                                'Initial run case ',
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
                                                         'Initial Scenario',
                                                         'Initial Scenario',
                                                         liste_scen, 0, False)

                        if ok:
                            self.opt_to_lig(case, scen2, self.baseName)
                        else:
                            if self.mgis.DEBUG:
                                self.mgis.add_info("Cancel run")
                            return

                else:
                    if self.mgis.DEBUG:
                        self.mgis.add_info("Cancel run")
                    return

            self.mgis.add_info("========== Run case  =========")
            self.mgis.add_info("Run = {} ;  Scenario = {} ; Kernel= {}".format(run, scen, noyau))

            finish = self.lance_mascaret(self.baseName + '.xcas')
            if not finish:
                self.mgis.add_info("Simulation error")
                return

            # Lecture de l'OPT des casiers et liaisons puis ecriture dans la table resultats
            cond_casier = False
            if par["presenceCasiers"] and noyau == "unsteady":
                cond_casier = True
                # self.lit_casiers_opt(run, scen, date_debut, self.baseName, "basin")
                # self.lit_casiers_opt(run, scen, date_debut, self.baseName, "link")
            self.lit_opt(run, scen, date_debut, self.baseName, comments, par['presenceTraceurs'], cond_casier)

        self.iface.messageBar().clearWidgets()
        self.mgis.add_info("Simulation finished")
        return

    def lance_mascaret(self, fichier_cas):
        """
        Run mascaret
        """
        os.chdir(self.dossierFileMasc)

        with open('FichierCas.txt', 'w') as fichier:
            fichier.write("'" + fichier_cas + "'\n")
        test = sys.platform

        if test == 'linux2' or test == 'cygwin':
            soft = "./mascaret_linux"
        elif test == 'win32':
            soft = "mascaret.exe"
        else:
            self.mgis.add_info("{0} platform  doesn't allow to run simulation.".format(test))
            return False

        # Linux(2.x and 3.x) ='linux2'
        # Windows = 'win32'
        # Windows / Cygwin = 'cygwin'
        # MacOSX = 'darwin'
        # OS / 2 = 'os2'
        # OS / 2  EMX ='os2emx'
        # RiscOS ='riscos'
        # AtheOS= 'atheos
        p = subprocess.Popen(soft, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                             , stdin=subprocess.PIPE)
        p.wait()
        self.mgis.add_info("{0}".format(p.communicate()[0].decode("utf-8")))
        return True

    def lit_opt(self, run, scen, date_debut, base_namefile, comments='', tracer=False, casier=False):
        nom_fich = os.path.join(self.dossierFileMasc, base_namefile + '.opt')
        # tempFichier = os.path.join(self.dossierFileMasc, baseNamefile + '_temp.opt')
        if self.mgis.DEBUG:
            self.mgis.add_info("Load data ....")
        if not os.path.isfile(nom_fich):
            self.mgis.add_info("Simulation Error: there aren't results")
            return False

        t, pk, col, value = self.read_opt(nom_fich, date_debut, scen, run)
        if tracer:
            nom_fich_tra = os.path.join(self.dossierFileMasc, base_namefile + '.tra_opt')

            if not os.path.isfile(nom_fich_tra):
                self.mgis.add_info("Simulation Error: there aren't results")
                return False
            t_tra, pk_tra, col_tra, value_tra = self.read_opt(nom_fich_tra, date_debut, scen, run)
            lind = []
            for i, c in enumerate(col_tra):
                if c not in col:
                    col.append(c)
                    lind.append(i)
            # add value_tra in value list
            for j, lignval in enumerate(value):
                for i in lind:
                    lignval.append(value_tra[j][i])

        maintenant = datetime.datetime.utcnow()

        tab = {run: {"scenario": scen,
                     "date": "{:%Y-%m-%d %H:%M}".format(maintenant),
                     "t": list(t),
                     "pk": list(pk)}}

        listimport = ["run", "date", "pk", "scenario", "t"]
        if comments != '':
            tab[run]["comments"] = comments
            listimport.insert(1, "comments")
        if tracer:
            tab[run]['wq'] = self.wq.cur_wq_mod
            listimport.append("wq")

        self.mdb.insert("runs",
                        tab,
                        listimport,
                        ",")
        liste_col = self.mdb.list_columns("resultats")
        for c in col:
            if c.lower() not in liste_col:
                self.mdb.add_columns("resultats", c.lower())

        self.mdb.insert_res("resultats", value, col)

        if casier:
            nom_fich_bas = os.path.join(self.dossierFileMasc, base_namefile + '.cas_opt')
            nom_fich_link = os.path.join(self.dossierFileMasc, base_namefile + '.liai_opt')

            t_bas, pk_bas, col_bas, value_bas = self.read_opt(nom_fich_bas, date_debut, scen, run,
                                                              init_col=['t', 'bnum'])
            t_link, pk_link, col_link, value_link = self.read_opt(nom_fich_link, date_debut, scen, run,
                                                                  init_col=['t', 'lnum'])

            self.mdb.insert_res("resultats_basin", value_bas, col_bas)
            self.mdb.insert_res("resultats_links", value_link, col_link)

        return True

    def opt_to_lig(self, run, scen, base_namefiles):
        """Creation of .lig file """
        condition = "run='{0}' AND scenario='{1}'".format(run, scen)
        t_max = self.mdb.select_max("t", "resultats", condition)

        condition = condition + " AND t=" + str(t_max)

        #result = self.mdb.select("resultats", condition, 'id')
        result = self.mdb.select("resultats", condition, 'pk')
        if not result:
            self.mgis.add('No results for initialisation')
            return

        result["X"] = result.pop("pk")
        result["Z"] = result.pop("z")
        result["Q"] = result.pop("q")

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

        with open(os.path.join(self.dossierFileMasc, base_namefiles + '.lig'), 'w') as fich:
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
                                                    self.dossierFileMasc,
                                                    "File (*.lig)")

        else:  # qt5
            fichiers, _ = QFileDialog.getOpenFileNames(None,
                                                       'File Selection',
                                                       self.dossierFileMasc,
                                                       "File (*.lig)")
        fichiers = fichiers[0]
        shutil.copy(fichiers, os.path.join(self.dossierFileMasc, self.baseName + '.lig'))

    def clean_rep(self):
        """ Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        for i in range(0, len(files)):
            os.remove(os.path.join(self.dossierFileMasc, files[i]))
        files = os.listdir(self.dossierFileMascOri)
        for i in range(0, len(files)):
            shutil.copy2(os.path.join(self.dossierFileMascOri, files[i]),
                         os.path.join(self.dossierFileMasc, files[i]))

    def clean_res(self):
        """ Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        listsup = [".opt", ".lig"]
        for i in range(0, len(files)):
            ext = os.path.splitext(files[i])[1]
            # self.mgis.add_info('delet file rr{}rr {}'.format(ext,(ext in listsup)))
            if ext in listsup:
                os.remove(os.path.join(self.dossierFileMasc, files[i]))
                if self.mgis.DEBUG:
                    self.mgis.add_info('delete file {}'.format(files[i]))

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
            if nom_scen in allscen['scenario'] or nom_scen + "_init" in allscen['scenario']:
                info = True
            else:
                info = False

            if info:
                ok = self.box.yes_no_q('Do you want to remove the {} results for a new simulation? ?'.format(nom_scen))

                if ok:
                    # delete case initalization
                    # TODO condition = "scenario LIKE '{0}' OR AND scenario LIKE '{0}_init' run LIKE '{1}'
                    # AND kernel LIKE '{2}'".format(nomScen, run,kernel)
                    condition = "(scenario LIKE '{0}' OR  scenario " \
                                "LIKE '{0}_init') AND run LIKE '{1}' ".format(nom_scen,
                                                                              run)
                    self.mdb.delete('runs', condition)
                    self.mdb.delete('resultats', condition)
                    if self.mgis.DEBUG:
                        self.mgis.add_info("Deletion of {0} scenario for {1} is done".format(nom_scen, run))
                    return True
                else:
                    return False

            else:
                return True
        else:
            return True

    def read_opt(self, nom_fich, date_debut, scen, run, init_col=[]):
        """ Read opt file"""
        t = set([])
        pk = set([])
        if init_col == []:
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
                temp = ligne.replace('"', '').replace('NaN', "'NULL'").split(';')
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
                        numero_masca = re.findall('\d+', ligne[k])[0]

                        # convertit le numero masca en qgis (different si un casier inactif)
                        numero_qgis = str(self.dico_basinnum[int(numero_masca)])
                        ligne_list.append(numero_qgis)
                    elif k == 'lnum':
                        # extrait le numero mascaret de liaison
                        numero_masca = re.findall('\d+', ligne[k])[0]
                        # convertit le numero masca en qgis (different si une liaison inactive)
                        numero_qgis = str(self.dico_linknum[int(numero_masca)])
                        ligne_list.append(numero_qgis)
                    else:
                        ligne_list.append(ligne[k])

                value.append(ligne_list)
        # delete 'qtot' because of the same that 'q'
        if delcond_qtot:
            col.remove("qtot")

        return t, pk, col, value

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
