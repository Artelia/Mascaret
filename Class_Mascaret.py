# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : MascPlug
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
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
comment:
     creerGEO()
     fmt(liste)
     creerXCAS( noyau)
     indent(elem, level=0)
     modifXCAS(parametres, dossier, fichSortie=None)
     mascaret(noyau)
     lanceMascaret(fichierCAS)
     litOPT( run, scen, dateDebut, messageBar)
     OPTtoLIG(run, scen)
     copyLIG
     copyRunFile(rep)
     clean_rep
     clean_res
     copyFileModel(rep, case=None)
     checkScenar(nomScen,kernel)
"""


import csv
import datetime
import os,sys
import re
import shutil
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as ETparse

from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import subprocess
from ui.warningbox import Class_warningBox


class Class_Mascaret():


    def __init__(self,main):
        self.mgis=main
        self.mdb=self.mgis.mdb
        self.iface=self.mgis.iface
        self.dossierFileMasc= os.path.join(self.mgis.masplugPath, "mascaret")
        if not os.path.isdir(self.dossierFileMasc):
            os.mkdir(self.dossierFileMasc)
        self.dossierFileMascOri = os.path.join(self.mgis.masplugPath, "mascaret_ori")
        self.baseName = "mascaret"
        self.nomfichGEO=self.baseName+".geo"
        self.box= Class_warningBox(self.mgis)
        # state list
        self.listeState = ['Steady', 'Unsteady', 'Transcritical unsteady']
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]

    def creerGEO(self):
        """creation of gemoetry file"""
        try:
            nomfich = os.path.join(self.dossierFileMasc, self.baseName+'.geo')

            if os.path.isfile(nomfich):
                sauv = nomfich.replace(".geo", "_old.geo")
                shutil.move(nomfich, sauv)
            requete = self.mdb.select("profiles", "active", "abscissa")

            with open(nomfich, 'w') as fich:
                for i, nom in enumerate(requete["name"]):

                    branche = requete["branchnum"][i]
                    abs = requete["abscissa"][i]
                    tempX = requete["x"][i]
                    tempZ = requete["z"][i]
                    litMinG = requete["leftminbed"][i]
                    litMinD = requete["rightminbed"][i]

                    if branche and abs and tempX and tempZ and litMinG and litMinD:
                        tabX = map(lambda x: round(float(x), 2), tempX.split())
                        tabZ = map(lambda x: round(float(x), 2), tempZ.split())

                        fich.write('PROFIL Bief_{0} {1} {2}\n'.format(branche,
                                                                      nom, abs))

                        for x, z in zip(tabX, tabZ):
                            if x >= litMinG and x <= litMinD:
                                type = "B"
                            else:
                                type = "T"

                            fich.write('{0:.2f} {1:.2f} {2}\n'.format(x, z, type))
            self.mgis.addInfo("Creation the geometry is done")
        except Exception as e:
            self.mgis.addInfo("Error: save the geometry")
            self.mgis.addInfo(str(e))

    def fmt(self,liste):
        return (" ".join(map(str, liste)))

    def indent(self,elem, level=0):
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

    def creerXCAS(self, noyau):
        """To create xcas file"""
        dictLois = {}
        try:
            fichierSortie = os.path.join(self.dossierFileMasc, self.baseName+".xcas")
            extrToloi = {0: 6, 1: 1, 2: 2, 3: 4, 4: 5, 5: 4, 8: 3}
            abaqueToloi = {1: 3, 2: 4, 5: 2, 6: 5, 7: 5, 8: 7}
            # création du fichier xml
            fichierCas = Element("fichierCas")

            cas = SubElement(fichierCas, "parametresCas")

            # requête pour récupérer les paramètres
            sql = "SELECT parametre, {0}, balise1, balise2 FROM {1}.{2} ORDER BY id;"

            rows= self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)

            for param, valeur, b1, b2 in rows:
                # self.mgis.addInfo("valeur : {0},  param : {1}  ,  b1 : {2} , b2: {3}".format(valeur, param, b1, b2))
                if b1:
                    try:
                         cas.find(b1).text
                    except:
                        balise1 = SubElement(cas, b1)
                    # if not cas.find(b1):
                    #     balise1 = SubElement(cas, b1)

                    if b2:
                        try :
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
            branches = self.mdb.selectDistinct(var, "branchs", "active")
            zones = self.mdb.select("branchs", "active", "branch, zoneabsstart")
            deversoirs = self.mdb.select("lateral_weirs", "active", "abscissa")
            noeuds = self.mdb.select("extremities", "type=10", "active")
            libres = self.mdb.select("extremities", "type!=10", "active")
            pertescharg = self.mdb.select("hydraulic_head", "active", "abscissa")
            profils = self.mdb.select("profiles", "active", "abscissa")
            profSeuil = self.mdb.select("profiles", "NOT active", "abscissa")
            seuils = self.mdb.select("weirs", "active", "abscissa")
            sorties = self.mdb.select("outputs", "", "abscissa")
            # Extrémités
            numero = branches["branch"]
            branches["abscdebut"] = []
            branches["abscfin"] = []
            liste = zip(profils["abscissa"], profils["branchnum"])
            for i, num in enumerate(numero):
                temp = [a for a, n in liste if n == num]
                branches["abscdebut"].append(min(temp))
                branches["abscfin"].append(max(temp))
            dictNoeuds = {}
            dictLibres = {"nom": [], "num": [], "extrem": [], "typeCond": []}

            for n, d, f in zip(numero, branches["startb"], branches["endb"]):
                if noeuds and d in noeuds["name"]:
                    if not d in dictNoeuds.keys():
                        dictNoeuds[d] = []
                    dictNoeuds[d].append(n * 2 - 1)

                if noeuds and f in noeuds["name"]:
                    if not f in dictNoeuds.keys():
                        dictNoeuds[f] = []
                    dictNoeuds[f].append(n * 2)
                if libres and d in libres["name"]:
                    i = libres["name"].index(d)
                    type = libres["type"][i]
                    formule = libres["method"][i]
                    dictLibres["nom"].append(libres["name"][i])
                    dictLibres["typeCond"].append(type)
                    dictLibres["num"].append(len(dictLibres["nom"]))
                    dictLibres["extrem"].append(n * 2 - 1)

                    dictLois[d] = {'type': extrToloi[type],
                                   'formule': formule,
                                   'valeurperm': libres["firstvalue"][i]}

                if libres and f in libres["name"]:
                    i = libres["name"].index(f)
                    type = libres["type"][i]
                    formule = libres["method"][i]
                    dictLibres["nom"].append(libres["name"][i])
                    dictLibres["typeCond"].append(type)
                    dictLibres["num"].append(len(dictLibres["nom"]))
                    dictLibres["extrem"].append(n * 2)

                    dictLois[f] = {'type': extrToloi[type],
                                   'formule': formule,
                                   'valeurperm': libres["firstvalue"][i]}
            # Zones
            nbPas = 0
            i = 0
            zones['num1erProf'] = [1] * len(zones["zoneabsstart"])
            zones['numDerProfPlanim'] = [1] * len(zones["zoneabsstart"])
            zones['numDerProfMaill'] = [1] * len(zones["zoneabsstart"])
            listeStock = {"numProfil": [],
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
                    xx = map(float, x.split())
                    zz = map(float, z.split())
                    diff = max(zz) - min(zz)
                except:
                    self.mgis.addInfo("Check the {} proile if it's ok ".format(profils["name"][j]))
                    return (dictLois)

                if abs > zones['zoneabsend'][i]:
                    i = i + 1
                    zones['num1erProf'][i] = j + 1

                zones['numDerProfPlanim'][i] = j + 1
                
                nbPas = max(int(diff/ float(zones['planim'][i])) + 1, nbPas)


                index = numero.index(n)
                zones["zoneabsstart"][i] = max(zones["zoneabsstart"][i],
                                             branches["abscdebut"][index])
                zones["zoneabsend"][i] = min(zones["zoneabsend"][i],
                                             branches["abscfin"][index])
                if zones["zoneabsend"][i] == branches["abscfin"][index]:
                    zones['numDerProfMaill'][i] = zones['numDerProfPlanim'][i]
                else:
                    zones['numDerProfMaill'][i] = zones['numDerProfPlanim'][i] + 1

                if sg or sd:
                    if sg:
                        limGauchLitMaj = sg
                    else:
                        limGauchLitMaj = min(xx)

                    if sd:
                        limDroitLitMaj = sd
                    else:
                        limDroitLitMaj = max(xx)

                    listeStock["numProfil"].append(j + 1)
                    listeStock["limGauchLitMaj"].append(limGauchLitMaj)
                    listeStock["limDroitLitMaj"].append(limDroitLitMaj)

            for i, type in enumerate(seuils["type"]):
                if type not in (3, 4):
                    dictLois[seuils["name"]] = {'type': abaqueToloi[type]}

            for i, nom in enumerate(apports["name"]):
                if nom not in dictLois.keys():
                    dictLois[nom] = {'type': 1,
                                     'formule': apports['method'][i],
                                     'valeurperm': apports["firstvalue"][i]}

            for i, nom in enumerate(deversoirs["name"]):
                if nom not in dictLois.keys() and deversoirs["type"][i] == 2:
                    dictLois[nom] = {'type': 4}

            # Géométrie du réseau
            reseau = cas.find("parametresGeometrieReseau")

            # liste des Branches
            listeBranch = SubElement(reseau, "listeBranches")
            SubElement(listeBranch, "nb").text = str(len(numero))
            SubElement(listeBranch, "numeros").text = self.fmt(numero)
            SubElement(listeBranch, "abscDebut").text = self.fmt(branches["abscdebut"])
            SubElement(listeBranch, "abscFin").text = self.fmt(branches["abscfin"])
            extremDebut = [i * 2 - 1 for i in numero]
            SubElement(listeBranch, "numExtremDebut").text = self.fmt(extremDebut)
            extremFin = [i * 2 for i in numero]
            SubElement(listeBranch, "numExtremFin").text = self.fmt(extremFin)

            # liste des Noeuds
            listeNoeuds = SubElement(reseau, "listeNoeuds")

            SubElement(listeNoeuds, "nb").text = str(len(dictNoeuds.keys()))
            ETnoeuds = SubElement(listeNoeuds, "noeuds")
            for k in sorted(dictNoeuds.keys()):
                noeud = SubElement(ETnoeuds, "noeud")
                temp = dictNoeuds[k] + [0] * (5 - len(dictNoeuds[k]))
                SubElement(noeud, "num").text = self.fmt(temp)

            # liste des extrémités libres
            extrLibres = SubElement(reseau, "extrLibres")
            liste = dictLibres["nom"]
            SubElement(extrLibres, "nb").text = str(len(liste))
            SubElement(extrLibres, "num").text = self.fmt(dictLibres["num"])
            SubElement(extrLibres, "numExtrem").text = self.fmt(dictLibres["extrem"])

            noms = SubElement(extrLibres, "noms")
            for nom in liste:
                SubElement(noms, "string").text = nom

            SubElement(extrLibres, "typeCond").text = self.fmt(dictLibres["typeCond"])

            temp = [sorted(dictLois.keys()).index(nom) + 1 for nom in liste]
            SubElement(extrLibres, "numLoi").text = self.fmt(temp)

            # Confluents
            confluents = SubElement(cas, "parametresConfluents")
            SubElement(confluents, "nbConfluents").text = str(len(dictNoeuds.keys()))
            confluent = SubElement(confluents, "confluents")
            for k in sorted(dictNoeuds.keys()):
                struct = SubElement(confluent, "structureParametresConfluent")
                l = len(dictNoeuds[k])
                SubElement(struct, "nbAffluent").text = str(l)
                SubElement(struct, "nom").text = k
                i = noeuds["name"].index(k)
                a_en=["abscissa", "ordinates", "angles"]
                for kk, a in enumerate(["abscisses", "ordonnees", "angles"]):
                    if noeuds[a_en[kk]][i] is None or l != 3:
                        SubElement(struct, a).text = "0.0 0.0 0.0"
                    else:
                        SubElement(struct, a).text = noeuds[a_en[kk]][i]

            # Planimétrage et maillage
            planimaill = SubElement(cas, "parametresPlanimetrageMaillage")
            SubElement(planimaill, "methodeMaillage").text = '5'

            planim = SubElement(planimaill, "planim")
            SubElement(planim, 'nbPas').text = str(nbPas)
            SubElement(planim, 'nbZones').text = str(len(zones["zoneabsstart"]))
            SubElement(planim, 'valeursPas').text = self.fmt(zones['planim'])
            SubElement(planim, 'num1erProf').text = self.fmt(zones['num1erProf'])
            SubElement(planim, 'numDerProf').text = self.fmt(zones['numDerProfPlanim'])

            maillage = SubElement(planimaill, "maillage")
            SubElement(maillage, 'modeSaisie').text = '2'
            SubElement(maillage, 'sauvMaillage').text = 'false'
            maillageC = SubElement(maillage, 'maillageClavier')
            SubElement(maillageC, 'nbSections').text = '0'
            SubElement(maillageC, 'nbPlages').text = str(len(zones["zoneabsstart"]))
            SubElement(maillageC, 'num1erProfPlage').text = self.fmt(zones['num1erProf'])
            # temp = [n+1 for n in zones['numDerProf'][:-1]] + [zones['numDerProf'][-1]]
            temp = zones['numDerProfMaill']
            SubElement(maillageC, 'numDerProfPlage').text = self.fmt(temp)
            SubElement(maillageC, 'pasEspacePlage').text = self.fmt(zones['mesh'])
            SubElement(maillageC, 'nbZones').text = '0'

            ### Singularités
            singularite = SubElement(cas, "parametresSingularite")

            # Seuils
            SubElement(singularite, "nbSeuils").text = str(len(seuils["name"]))

            if len(seuils["name"]) > 0:
                ETseuils = SubElement(singularite, "seuils")

            liste = ["type", "numBranche", "abscisse", "coteCrete", "coteCreteMoy",
                     "coteRupture", "coeffDebit", "largVanne", "epaisseur"]
            liste_en = ["type", "branchnum", "abscissa", "z_crest", "z_average_crest",
                     "z_break", "flowratecoeff", "wide_floodgate", "thickness"]                     

            for i, nom in enumerate(seuils["name"]):
                struct = SubElement(ETseuils, "structureParametresSeuil")
                SubElement(struct, "nom").text = nom
                for kk,l in enumerate(liste):
                    if seuils[liste_en[kk].lower()][i] is None:
                        SubElement(struct, l).text = '-0'
                    else:
                        SubElement(struct, l).text = str(seuils[liste_en[kk].lower()][i])

                if seuils["type"][i] not in (3, 4):
                    SubElement(struct, "numLoi").text = str(sorted(dictLois.keys()))
                else:
                    SubElement(struct, "numLoi").text = '-0'

                if seuils["type"][i] != 3:
                    SubElement(struct, "nbPtLoiSeuil").text = '-0'
                else:
                    try:
                        i = profSeuil["nom"].index(nom)
                        long = len(profSeuil['x'][i].split())
                        SubElement(struct, "nbPtLoiSeuil").text = str(long)
                        SubElement(struct, "abscTravCrete").text = profSeuil['x'][i]
                        SubElement(struct, "cotesCrete").text = profSeuil['z'][i]

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

            ### Apports et déversoirs
            apportDever = SubElement(cas, "parametresApportDeversoirs")

            # Apports
            ETapports = SubElement(apportDever, "debitsApports")
            SubElement(ETapports, "nbQApport").text = str(len(apports["name"]))
            noms = SubElement(ETapports, "noms")
            for nom in apports["name"]:
                SubElement(noms, "string").text = nom

            SubElement(ETapports, "numBranche").text = self.fmt(apports["branchnum"])
            SubElement(ETapports, "abscisses").text = self.fmt(apports["abscissa"])
            SubElement(ETapports, "longueurs").text = self.fmt(apports["length"])
            temp = [sorted(dictLois.keys()).index(nom) + 1 for nom in apports["name"]]
            SubElement(ETapports, "numLoi").text = self.fmt(temp)

            # Déversoirs
            deversLate = SubElement(apportDever, "deversLate")
            SubElement(deversLate, "nbDeversoirs").text = str(len(deversoirs["name"]))
            noms = SubElement(deversLate, "noms")
            for nom in deversoirs["name"]:
                SubElement(noms, "string").text = nom

            SubElement(deversLate, "type").text = self.fmt(deversoirs["type"])

            l_en=["branchnum", "abscissa", "length", "z_crest", "flowratecoef"]
            for kk, l in enumerate(["numBranche", "abscisse", "longueur", "coteCrete", "coeffDebit"]):
                SubElement(deversLate, l).text = self.fmt(deversoirs[l_en[kk].lower()])

            temp = []
            for nom in deversoirs["name"]:
                if nom in dictLois.keys():
                    temp.append(sorted(dictLois.keys()).index(nom) + 1)
                else:
                    temp.append(0)
            SubElement(deversLate, "numLoi").text = self.fmt(temp)

            ### Calage
            calage = SubElement(cas, "parametresCalage")

            # frottement
            frottement = SubElement(calage, "frottement")
            SubElement(frottement, "loi").text = '1'
            SubElement(frottement, "nbZone").text = str(len(zones["zoneabsstart"]))
            SubElement(frottement, "numBranche").text = self.fmt(zones["branch"])
            l_en=['zoneabsstart','zoneabsend', 'minbedcoef', 'majbedcoef']
            for kk,l in enumerate(["absDebZone", "absFinZone", "coefLitMin", "coefLitMaj"]):
                SubElement(frottement, l).text = self.fmt(zones[l_en[kk].lower()])

            # stockage
            zoneStockage = SubElement(calage, "zoneStockage")
            SubElement(zoneStockage, "loi").text = '1'
            n = len(listeStock["numProfil"])
            SubElement(zoneStockage, "nbProfils").text = str(n)
            for l in ["numProfil", "limGauchLitMaj", "limDroitLitMaj"]:
                SubElement(zoneStockage, l).text = self.fmt(listeStock[l])

            ### Lois hydrauliques
            hydrauliques = SubElement(cas, "parametresLoisHydrauliques")
            SubElement(hydrauliques, "nb").text = str(len(dictLois.keys()))
            lois = SubElement(hydrauliques, "lois")


            for nom in sorted(dictLois.keys()):
                struct = SubElement(lois, "structureParametresLoi")
                SubElement(struct, "nom").text = nom
                SubElement(struct, "type").text = str(dictLois[nom]['type'])
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


            ##### XCAS modiication of type when steady case #####
            if noyau == 'steady':
                paramCas = fichierCas.find('parametresCas')
                parametresGeneraux = paramCas.find('parametresGeneraux')
                geomReseau = paramCas.find('parametresGeometrieReseau')
                typeCond = geomReseau.find('extrLibres').find('typeCond')
                typeCond.text = typeCond.text.replace('4', '2')
                loisHydrauliques = paramCas.find('parametresLoisHydrauliques')
                lois = loisHydrauliques.find('lois')
                for child in lois:
                    if child.find('type').text == '5':
                        child.find('type').text = '2'

            ############################################
            self.indent(fichierCas)
            arbre = ElementTree(fichierCas)
            arbre.write(fichierSortie)


            ##### XCAS initialisation #####

            paramCas = fichierCas.find('parametresCas')
            parametresGeneraux = paramCas.find('parametresGeneraux')
            fichXCAS = '{}_init.xcas'.format(self.baseName)
            parametresGeneraux.find('fichMotsCles').text = fichXCAS
            parametresGeneraux.find('code').text = '1'
            parametresTemporels = paramCas.find('parametresTemporels')
            parametresTemporels.find('pasTemps').text = '60'
            parametresTemporels.find('critereArret').text = '2'
            parametresTemporels.find('nbPasTemps').text = '2'
            geomReseau = paramCas.find('parametresGeometrieReseau')
            typeCond = geomReseau.find('extrLibres').find('typeCond')
            typeCond.text = typeCond.text.replace('4', '2')
            loisHydrauliques = paramCas.find('parametresLoisHydrauliques')
            lois = loisHydrauliques.find('lois')
            for child in lois:
                if child.find('type').text == '5':
                    child.find('type').text = '2'
                donnee = child.find('donnees').find('fichier')
                temp = donnee.text.split('.')
                donnee.text = '{}_init.loi'.format(temp[0])

            initiales = paramCas.find('parametresConditionsInitiales')
            initiales.find('repriseEtude').find('repriseCalcul').text = 'false'
            initiales.find('ligneEau').find('LigEauInit').text = 'false'
            resultats = paramCas.find('parametresImpressionResultats')
            fichOPT = '{}_init.opt'.format(self.baseName)
            resultats.find('resultats').find('fichResultat').text = fichOPT
            resultats.find('impression').find('impressionCalcul').text = 'true'
            resultats.find('pasStockage').find('premPasTpsStock').text = '1'
            resultats.find('pasStockage').find('pasStock').text = '1'
            resultats.find('pasStockage').find('pasImpression').text = '1'
            resultats.find('stockage').find('option').text = '1'

            self.indent(fichierCas)
            arbre = ElementTree(fichierCas)
            arbre.write(os.path.join(self.dossierFileMasc, fichXCAS))

            self.mgis.addInfo("Save the Xcas file is done")
        except Exception as e:
            self.mgis.addInfo("Error: save Xcas file")
            self.mgis.addInfo(str(e))

        return (dictLois)

    def modifXCAS(self,parametres,xcasfile,fichSortie=None):
        fichEntree = os.path.join(self.dossierFileMasc, xcasfile)
        arbre = ETparse(fichEntree)
        racine = arbre.getroot()

        for param, val in parametres.items():
            parent = racine[0].find(val["balise1"])

            if "balise2" in val.keys() and val["balise2"]:
                child = parent.find(val["balise2"])
                child.find(param).text = val["valeur"]

            else:
                parent.find(param).text = val["valeur"]

        self.indent(racine)
        if fichSortie:
            arbre.write(fichSortie)
        else:
            arbre.write(fichEntree)

    def creerLOI(self,nom, tab, type):
        with open(os.path.join(self.dossierFileMasc, nom + '.loi'), 'w') as fich:
            fich.write('# ' + nom + '\n')
            if type == 1:
                fich.write('# Temps (S) Debit\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {flowrate:.3f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.addInfo("\n")
                #     self.mgis.addInfo("{0} :\n \t Time : {1}\n \t Flow Rate :{2}"
                #                       .format(nom, tab["temps"], tab["debit"]))

            elif type == 2:
                fich.write('# Temps (S) Cote\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z:.3f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.addInfo("\n")
                #     self.mgis.addInfo("{0} :\n \t Time : {1}\n \t Water Level :{2}"
                #                       .format(nom, tab["temps"],tab["cote"]))
            elif type == 3:
                fich.write('# Temps (S) Cote Debit\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z:.3f} {flowrate:.3f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.addInfo("\n")
                #     self.mgis.addInfo("{0} :\n \t Time : {1}\n \t Water Level :{2}\n \t Flow Rate {3}"
                #                       .format(nom, tab["temps"],tab["cote"],tab["debit"]))
            elif type == 4:
                fich.write('# Debit Cote\n')
                chaine = ' {flowrate:.3f} {z:.3f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.addInfo("\n")
                #     self.mgis.addInfo("{0} :\n \t Flow Rate {2}\n \t Water Level :{1}"
                #                       .format(nom, tab["cote"],tab["debit"]))
            elif type == 5:
                fich.write('# Cote Debit\n')
                chaine = ' {z:.3f} {flowrate:.3f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.addInfo("\n")
                #     self.mgis.addInfo("{0} :\n \t Water Level :{1}\n \t Flow Rate {2}"
                #                       .format(nom, tab["cote"],tab["debit"]))
            elif type == 6:
                fich.write('# Debit Cote_Aval Cote_Amont\n')
                chaine = ' {flowrate:.3f} {z_downstream:.3f} {z_upstream:.3f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.addInfo("\n")
                #     self.mgis.addInfo("{0} :\n \t Upstream Water Level{1}\n \t  Downstream Water Level :{2}"
                #                       .format(nom, tab["cote_amont"], tab["cote_aval"]))
            elif type == 7:
                fich.write(u'# Temps (s) Cote inférieur Cote supérieur\n')
                fich.write(' S\n')
                chaine = ' {time:.3f} {z_lower:.3f} {z_up:.3f}\n'
                # if self.mgis.DEBUG:
                #     self.mgis.addInfo("\n")
                #     self.mgis.addInfo("{0} :\n \t Time : {1}\n \t Upstream Water Level{2}\n \t  "
                #                       "Downstream Water Level :{3}"
                #                       .format(nom,tab["temps"], tab["cote_amont"], tab["cote_aval"]))
            n = len(tab.values()[0])
            for i in range(n):
                dico = {k: v[i] for k, v in tab.items()}
                fich.write(chaine.format(**dico))

    def obsTOloi(self, dictLois, dateDebut, dateFin):
        pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        somme = 0
        debitPrec = 0
        obs = {}
        duree = int((dateFin - dateDebut).total_seconds() / 3600)

        liste_date = [dateDebut + datetime.timedelta(hours=x)
                      for x in range(duree)]

        for nom, loi in dictLois.items():
            if loi['type'] != 1:
                continue

            liste_stations = pattern.findall(loi['formule'])
            for cd_hydro, delta in liste_stations:
                condition = """code ='{0}'
                            AND type = 'Q'
                            AND date >= '{1:%Y-%m-%d %H:%M}' 
                            AND date <= '{2:%Y-%m-%d %H:%M}'
                            """.format(cd_hydro, dateDebut, dateFin)

                obs[cd_hydro] = self.mdb.select('observations',
                                                 condition,
                                                 'code, date')

            fichierLoi = os.path.join(self.dossierFileMasc, nom + '.loi')
            valeurInit = None

            with open(fichierLoi, 'w') as fich_sortie:
                fich_sortie.write('# {0}\n'.format(nom))
                fich_sortie.write('# Temps (H) Debit\n')
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

                    if resultat:
                        if not valeurInit:
                            valeurInit = resultat
                            somme += resultat
                        tps = (t - dateDebut).total_seconds() / 3600
                        chaine = '  {0:4.3f}   {1:3.3f}\n'
                        fich_sortie.write(chaine.format(tps, resultat))
            if valeurInit:
                tab = {'time': [0, 3600], 'flowrate': [valeurInit, valeurInit]}
                self.creerLOI(nom + '_init', tab, 1)

        for nom, loi in dictLois.items():
            if loi['type'] != 5:
                continue
            condition = """name ='{0}' 
                        AND type = {1}
                        AND starttime <= '{2:%Y-%m-%d %H:%M}' 
                        AND endtime >= '{3:%Y-%m-%d %H:%M}'
                        """.format(nom, loi['type'], dateDebut, dateFin)

            temp = self.mdb.selectOne('laws', condition)
            cote = map(float, temp['z'].split())
            debit = map(float, temp['flowrate'].split())

            self.creerLOI(nom, {'z': cote, 'flowrate': debit}, 5)

            for c, d in zip(cote, debit):
                if debitPrec > 0 and d > somme:
                    valeurInit = (c - cotePrec) \
                                 / (d - debitPrec) \
                                 * (somme - debitPrec) \
                                 + cotePrec
                    break
                else:
                    cotePrec, debitPrec = c, d
            if valeurInit:
                tab = {'time': [0, 3600], 'z': [valeurInit, valeurInit]}
                self.creerLOI(nom + '_init', tab, 2)

    def mascaret(self,noyau,run):
        """creation file and to run mascaret"""

        sql = "SELECT parametre, {0} FROM {1}.{2};"
        rows = self.mdb.run_query(sql.format(noyau, self.mdb.SCHEMA, "parametres"), fetch=True)
        par = {}

        for param, valeur in rows:
            try:
                par[param] = eval(valeur.title())
            except:
                par[param] = valeur
        if not par['repriseCalcul'] :
            self.clean_rep()
            self.creerGEO()
            if self.mgis.DEBUG:
                self.mgis.addInfo("Geometric file is created.")
                self.mgis.addInfo("noyau {}".format(noyau))
        else:
            self.clean_res()

        if par["evenement"] and noyau != "steady":
            dictScen_tmp = self.mdb.select('scenarios', 'run', 'starttime')
            listexclu=[]
            for i, scen in enumerate(dictScen_tmp['name']):
                # self.mgis.addInfo("scen******************* {}".format(scen))
                if not self.checkScenar(scen, noyau):
                    self.mgis.addInfo("Canceled Simulation because of {0} already exists.".format(scen))
                    listexclu.append(i)
            if listexclu:
                dictScen={}
                for key in dictScen_tmp:
                    value=dictScen_tmp[key]
                    value= [elt for idx, elt in enumerate(value) if not (idx in listexclu)]
                    dictScen[key]=value
            else:
                dictScen=dictScen_tmp

        else:
            scen, ok = QInputDialog.getText(QWidget(), u'Scenario name',
                                            u'Please input a scenario name :')
            if not ok or not self.checkScenar(scen, noyau):
                if self.mgis.DEBUG:
                    self.mgis.addInfo("Canceled Simulation because of {0} already exists.".format(scen))
                return
            dictScen = {'name': [scen]}


        # progressMessageBar = self.iface.messageBar().createMessage(
        #     "Run ...")
        # self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)

        dateDebut = None

        dictLois = self.creerXCAS(noyau)
        # self.mgis.addInfo('{}'.format(dictLois))
        if self.mgis.DEBUG:
            self.mgis.addInfo("Xcas file is created.")
        for i, scen in enumerate(dictScen['name']):
            if self.mgis.DEBUG:
                self.mgis.addInfo("The current scenario is {}".format(scen))
            if noyau == "steady":
                #steady
                for nom, l in dictLois.items():
                    if not "valeurperm" in l.keys():
                        continue
                    if l["valeurperm"] is None:
                        self.mgis.addInfo("Error : Add the 'valeurprerm' value in extremities.")
                    if l['type'] == 1:
                        tab = {"time": [0, 3600], 'flowrate': [l["valeurperm"]] * 2}
                    else:
                        #In steady case the other type don't exist
                        l['type'] = 2
                        tab = {"time": [0, 3600], 'z': [l["valeurperm"]] * 2}

                    self.creerLOI(nom, tab, l['type'])

            elif par["evenement"]:
                # transcritical unsteady evenement
                dateDebut = dictScen['starttime'][i]
                dateFin = dictScen['endtime'][i]
                duree = int((dateFin - dateDebut).total_seconds()) - 3600

                tab = {"tempsMax": {'valeur': str(duree),
                                    'balise1': 'parametresTemporels'},
                       "titreCalcul": {'valeur': scen,
                                       'balise1': 'parametresImpressionResultats'}
                       }
                self.modifXCAS(tab, self.baseName+'.xcas')

                self.obsTOloi(dictLois,dateDebut,dateFin)


            else:
                #transcritical unsteady hors evenement

                for nom, l in dictLois.items():
                    #dictLois.items() extremities liste
                    condition = "name ='{0}' AND type={1}".format(nom, l["type"])
                    # self.mgis.addInfo('{}'.format(condition))
                    try :
                        temp = self.mdb.selectOne('laws', condition)
                    except Exception as e:
                        self.mgis.addInfo("Error: Please check if law {0} is correct. ".format(nom))
                        self.mgis.addInfo(str(e))
                        return

                    # liste = ["cote", "debit", "temps", "cote_amont", "cote_aval",
                    #          "cote_inf", "cote_sup"]
                    liste = ["z", "flowrate", "time", "z_upstream", "z_downstream",
                             "z_lower", "z_up"]

                    tab = {k: map(float, v.split())
                       for k, v in temp.items() if v and k in liste}

                    self.creerLOI(nom, tab, l["type"])
                    if self.mgis.DEBUG:
                        self.mgis.addInfo("Laws file is created.")

                    if not "valeurperm" in l.keys():
                        continue

                    nom = nom + "_init"
                    #3600 To change TODO

                    if l['type'] == 1:
                        tab = {"time": [0, 3600], 'flowrate': [l["valeurperm"]] * 2}
                        self.creerLOI(nom, tab, 1)
                    elif l['type'] in [2, 4, 5]:
                        tab = {"time": [0, 3600], 'z': [l["valeurperm"]] * 2}
                        self.creerLOI(nom, tab, 2)
                    else:
                        par["initialisationAuto"]=False
                        self.mgis.addInfo("No initialisation")


            if par["initialisationAuto"] and noyau != "steady":
                # add if name of init. exist previously
                sceninit = scen + '_init'
                if self.checkScenar(sceninit , "steady"):
                    self.mgis.addInfo("Run initialization")
                    self.lanceMascaret(self.baseName + '_init.xcas')
                    self.litOPT("Steady", sceninit, None,
                                self.baseName + '_init')
                else:
                    self.mgis.addInfo("No Run initialization.\n"
                                      " The initial boundaries come from {} scenario.".format(sceninit))

                self.OPTtoLIG("Steady", sceninit,self.baseName)
                tab = {"LigEauInit": {'valeur': 'true',
                                    'balise1': 'parametresConditionsInitiales',
                                      'balise2': 'ligneEau'}
                       }
                self.modifXCAS(tab, self.baseName+'.xcas')



            elif par["LigEauInit"] and noyau != "steady":
                condition = "run LIKE 'Steady'"
                dico_run = self.mdb.selectDistinct("scenario",
                                                   "runs", condition)

                if not dico_run and self.mgis.DEBUG:
                    self.mgis.addInfo("There aren't scenarii for the Steady case.")
                    if self.mgis.DEBUG:
                        self.mgis.addInfo("Cancel run")
                    return

                liste2=list(dico_run["scenario"])
                liste2.append('".lig" File')

                scen2, ok = QInputDialog.getItem(None,
                                                'Initial Scenario',
                                                'Initial Scenario',
                                                liste2, 0, False)
                if ok:
                    if scen2=='".lig" File':
                        self.copyLIG()
                    else:
                        self.OPTtoLIG("Steady", scen2, self.baseName)
                else:
                    if self.mgis.DEBUG:
                        self.mgis.addInfo("Cancel run")
                    return



            if self.mgis.DEBUG:
                self.mgis.addInfo("Run case")

            finish=self.lanceMascaret(self.baseName + '.xcas')
            if not finish :
                self.mgis.addInfo("Simulation error")
                return

            self.litOPT( run, scen, dateDebut,self.baseName)
        self.iface.messageBar().clearWidgets()
        self.mgis.addInfo("Simulation finished")
        return

    def lanceMascaret(self,fichierCAS):
        """
        Run mascaret
        :param dossier:
        :return:
        """
        os.chdir(self.dossierFileMasc)

        with open('FichierCas.txt', 'w') as fichier:
            fichier.write("'" + fichierCAS + "'\n")
        test=sys.platform

        if test =='linux2' or test =='cygwin':
            soft = "./mascaret_linux"
        elif test =='win32' :
            soft = "mascaret.exe"
        else:
            self.mgis.addInfo("{0} platform  doesn't allow to run simulation.".format(test))
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
                             ,stdin=subprocess.PIPE)
        p.wait()
        self.mgis.addInfo("{0}".format(p.communicate()[0]))
        return True

    def litOPT(self, run, scen, dateDebut,baseNamefile):
        nomFich = os.path.join(self.dossierFileMasc, baseNamefile + '.opt')

        tempFichier = os.path.join(self.dossierFileMasc, baseNamefile + '_temp.opt')
        t = set([])
        pk = set([])


        if self.mgis.DEBUG:
            self.mgis.addInfo("Load data ....")
        if not os.path.isfile(nomFich) :
            self.mgis.addInfo("Simulation Error: there aren't results")
            return False


        with open(nomFich, 'r') as source:
            var = source.readline()
            col = ['t', 'branche', 'section', 'pk']

            ligne = source.readline()
            while '[resultats]' not in ligne:
                temp = ligne.replace('"', '').split(';')
                col.append(temp[1])
                ligne = source.readline()

            data = csv.DictReader(source, delimiter=';', fieldnames=col)
            if dateDebut:
                col.append("date")
            col.append("run")
            col.append("scenario")

            var=[]

            # with open(tempFichier, "wb") as fich:
            #     writer = csv.DictWriter(fich, fieldnames=col)
            # for ligne in data:
            #     if dateDebut:
            #         d = dateDebut + datetime.timedelta(
            #             seconds=float(ligne["t"]))
            #         ligne["date"] = d
            #         t.add("{:%Y-%m-%d %H:%M}".format(d))
            #     else:
            #         t.add(ligne["t"])
            #
            #     pk.add(ligne["pk"])
            #     ligne["run"] = run
            #     ligne["scenario"] = scen
            #
            #     ligne["section"] = ligne["section"].replace('"', '')
            #     ligne["branche"] = ligne["branche"].replace('"', '')

                # writer.writerow(ligne)
            var={}
            for ligne in data:
                self.mgis.addInfo("{}".format(ligne))
                # if dateDebut:
                #     d = dateDebut + datetime.timedelta(
                #         seconds=float(ligne["t"]))
                #     ligne["date"] = d
                #     t.add("{:%Y-%m-%d %H:%M}".format(d))
                # else:
                #     t.add(ligne["t"])
                #
                # pk.add(ligne["pk"])
                # ligne["run"] = run
                # ligne["scenario"] = scen
                #
                # ligne["section"] = ligne["section"].replace('"', '')
                # ligne["branche"] = ligne["branche"].replace('"', '')
                var.append(ligne)

            maintenant = datetime.datetime.utcnow()

            tab = {run: {"scenario": scen,
                         "date": "{:%Y-%m-%d %H:%M}".format(maintenant),
                         "t": list(t),
                         "pk": list(pk)}}

            self.mdb.insert("runs",
                             tab,
                             ["run", "date", "pk", "scenario", "t"],
                             ",")
            listeCol = self.mdb.listColumns("resultats")

            for c in col:
                if c.lower() not in listeCol:
                    self.mdb.addColumns("resultats", c.lower())
            #self.mdb.copy("resultats", col, tempFichier)

            self.mdb.insertRes("resultats", var,col)


        return True

    def OPTtoLIG(self,run, scen,baseNamefiles):
        """Creation of .lig file """
        condition = "run='{0}' AND scenario='{1}'".format(run, scen)
        tMax = self.mdb.selectMax("t", "resultats", condition)

        condition = condition + " AND t=" + str(tMax)

        result = self.mdb.select("resultats", condition)

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

        nbBief = len(set(result['branche']))
        section = sorted(set(result['section']))
        IMAX = len(section)
        i1i2 = []
        for b in sorted(i1.keys()):
            i1i2.append(str(i1[b]))
            i1i2.append(str(i2[b]))

        with open(os.path.join( self.dossierFileMasc, self.baseName + '.lig'), 'w') as fich:
            date = datetime.datetime.utcnow()
            fich.write(
                'RESULTATS CALCUL,DATE :  {0:%d/%m/%y %H:%M}\n'.format(date))
            fich.write('FICHIER RESULTAT MASCARET{0}\n'.format(' ' * 47))
            fich.write('{0} \n'.format('-' * 71))
            fich.write(' IMAX  =  {0} NBBIEF=    {1}\n'.format(str(IMAX),
                                                               str(nbBief))
                       )
            fich.write(' I1,I2 =    {0}\n'.format('  '.join(i1i2)))

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

    def deleteRun(self,case):
        """ Delete in tables the run case"""
        condition = "run LIKE '{0}'".format(case)
        dico_run = self.mdb.selectDistinct("scenario",
                                           "runs",condition)
        if not dico_run :
            self.mgis.addInfo("There aren't scenarii for the {0} case.".format(case))
            return


        # self.mgis.addInfo('{0}'.format( dico_run["scenario"]))
        scen, ok = QInputDialog.getItem(None,
                                        'Scenarii',
                                        'Scenarii',
                                dico_run["scenario"], 0, False)
        if ok :
            condition = "scenario LIKE '{0}' AND run LIKE '{1}'".format(scen,case)
            self.mdb.delete('runs',condition)
            self.mdb.delete('resultats', condition)
            self.mgis.addInfo("Deletion of {0} scenario for {1} is done".format(scen,case))

    def copyLIG(self):
        """ Load .lig file in run model"""
        fichiers = QFileDialog.getOpenFileNames(None,
                                                r'File Selection',
                                                self.dossierFileMasc,
                                                "File (*.lig)")
        shutil.copy(fichiers[0],os.path.join(self.dossierFileMasc, self.baseName + '.lig'))

    def clean_rep(self):
        """ Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        for i in range(0, len(files)):
            os.remove(os.path.join(self.dossierFileMasc,files[i]))
        files = os.listdir(self.dossierFileMascOri)
        for i in range(0, len(files)):
            shutil.copy2(os.path.join(self.dossierFileMascOri,files[i]), os.path.join(self.dossierFileMasc,files[i]))

    def clean_res(self):
        """ Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossierFileMasc)
        listsup = [".opt", ".lig"]
        for i in range(0, len(files)):
            ext=os.path.splitext(files[i])[1]
            # self.mgis.addInfo('delet file rr{}rr {}'.format(ext,(ext in listsup)))
            if ext in listsup:
                os.remove(os.path.join(self.dossierFileMasc,files[i]))
                if self.mgis.DEBUG:
                    self.mgis.addInfo('delet file {}'.format(files[i]))

    def copyRunFile(self,rep):
        """copy run file in "rep" path"""
        try:
            files = os.listdir(self.dossierFileMasc)
            for i in range(0, len(files)):
                shutil.copy2(os.path.join(self.dossierFileMasc, files[i]),
                                os.path.join(rep, files[i]))
            return True
        except :
            return False

    def copyFileModel(self, rep, case=None):
        if case=='xcas':
            shutil.copy2(os.path.join(self.dossierFileMasc,self.baseName+".xcas"),rep)

        elif case=='geo':
            shutil.copy2(os.path.join(self.dossierFileMasc, self.baseName+".geo"), rep)
        else:
            self.mgis.addInfo('No file to export')

    def checkScenar(self,nomScen,kernel):
        """if true :not exist nomScen and results """
        state=self.listeState[self.Klist.index(kernel)]
        condition = "run LIKE '{0}'".format(state)
        allscen = self.mdb.selectDistinct("scenario", "runs", condition)
        if allscen:
            if nomScen in allscen['scenario']:
                info=True
            else:
                info = False

            if info:
                    ok = self.box.yes_no_q('Do you want to remove the {} results for a new simulation? ?'.format(nomScen))
                    if ok:
                        # delete case initalization
                        condition = "scenario LIKE '{0}' AND run LIKE '{1}'".format(nomScen, state)
                        self.mdb.delete('runs', condition)
                        self.mdb.delete('resultats', condition)
                        if self.mgis.DEBUG:
                            self.mgis.addInfo("Deletion of {0} scenario for {1} is done".format(nomScen, state))
                        return True
                    else:
                        return False

            else:
                return True
        else:
            return True