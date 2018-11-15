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
comment:
     fct:
        distance
        interpole
"""
import math


def data_to_float(txt):
    try:
        float(txt)
        return float(txt)
    except ValueError:
        return None

def isfloat(value):

    try:
        float(value)
        return True
    except ValueError:
        return False

def distance(a, b):
    return math.sqrt(math.pow(a.x() - b.x(), 2) + math.pow(a.y() - b.y(), 2))


def interpole(a, l1, l2):
    i, x = min(enumerate(l1), key=lambda x: abs(x[1] - a))

    if i < len(l1) - 1 and a >= x:
        return ((l2[i + 1] - l2[i]) / (l1[i + 1] - x) * (a - x) + l2[i])
    elif i > 0 and a <= x:
        return ((l2[i] - l2[i - 1]) / (x - l1[i - 1]) * (a - l1[i - 1]) + l2[i - 1])
    else:
        return (None)

def str2bool(s):
    """string to bool"""
    if "True" in s or "TRUE" in s:
        return True
    else:
        return False

def getCouche(nom,iface) :
    for couche in iface.legendInterface().layers():
        if couche.name() == nom :
            return(couche)

    return(None)


def calculAbscisses(listeCouches, riviere, iface, dossier):
    coucheRiv = getCouche(riviere, iface)
    # fusion des branches
    nomFich = os.path.join(dossier, "temp.shp")
    id = coucheRiv.fieldNameIndex("branche")
    QgsGeometryAnalyzer().dissolve(coucheRiv, nomFich,
                                   onlySelectedFeatures=False,
                                   uniqueIdField=id, p=None)

    coucheDissoute = QgsVectorLayer(nomFich, "temp", "ogr")

    longBranche = {}
    dico = {}
    for f in coucheDissoute.getFeatures():
        longBranche[f["branche"]] = f.geometry().length()
        dico[f["branche"]] = f

    longueurZone = {}
    for f in coucheRiv.getFeatures():
        if not f["branche"] in longueurZone.keys():
            longueurZone[f["branche"]] = []

        longueurZone[f["branche"]].append((f["numZone"], f.geometry().length()))

    for c in listeCouches:
        if c == riviere:
            continue

        couche =getCouche(c, iface)
        print(c)
        if couche.wkbType() == 5:
            coucheNoeud = QgsVectorLayer("Point", "temporary_points", "memory")

            coucheNoeud.dataProvider().addAttributes(
                [QgsField("nom", QVariant.String, 'string', 10, 0),
                 QgsField("numBranche", QVariant.Int, 'int', 2, 0),
                 QgsField("abscisse", QVariant.Double, 'double', 10, 1)])

            coucheNoeud.startEditing()
            for f in couche.getFeatures():
                for r in coucheDissoute.getFeatures():
                    if f.geometry().intersects(r.geometry()):
                        feat = QgsFeature(coucheNoeud.dataProvider().fields())
                        feat.setGeometry(f.geometry().intersection(
                            r.geometry()))
                        feat["nom"] = f["nom"]
                        feat["numBranche"] = r["branche"]
                        coucheNoeud.dataProvider().addFeatures([feat])
            coucheNoeud.commitChanges()

        else:
            coucheNoeud = couche

        coucheNoeud.startEditing()

        # parcours de la liste de coucheNoeuds
        for n in coucheNoeud.getFeatures():

            num = n["numBranche"]
            branche = dico[num]

            mini = 999999999
            i = 0
            # recuperation des coordonnees du point
            C = n.geometry().asPoint()

            # on cherche le segment le plus proche du point souhaité
            d, D, vB = branche.geometry().closestSegmentWithContext(C)
            vA = vB - 1

            # calcul de la distance depuis le début de la ligne
            somme = 0
            for i in range(1, vB):
                somme += distance(branche.geometry().vertexAt(i - 1),
                                  branche.geometry().vertexAt(i))

            somme += distance(branche.geometry().vertexAt(vA), D)

            # calcul de l'abcisse
            sommeB = sum([longBranche[i] for i in longBranche.keys() if i < num])
            if somme < longBranche[num]:
                n["abscisse"] = somme + sommeB
            else:
                n["abscisse"] = None
            coucheNoeud.updateFeature(n)

        coucheNoeud.commitChanges()

        if couche.wkbType() == 5:
            couche.startEditing()

            for f in coucheNoeud.getFeatures():
                for g in couche.getFeatures():
                    if f["nom"] == g["nom"]:
                        g["abscisse"] = f["abscisse"]
                        g["numBranche"] = f["numBranche"]
                        couche.updateFeature(g)

            couche.commitChanges()

    if riviere in listeCouches:
        abscDebut = {}
        abscFin = {}

        coucheProfil = getCouche("profils", iface)

        for p in coucheProfil.getFeatures():

            if p["abscisse"] and p["actif"]:
                num = p["numBranche"]

                if not num in abscDebut.keys(): abscDebut[num] = 99999999
                if not num in abscFin.keys(): abscFin[num] = -99999999

                abscDebut[num] = min(abscDebut[num], p["abscisse"])
                abscFin[num] = max(abscFin[num], p["abscisse"])

        coucheRiv.startEditing()

        for f in coucheRiv.getFeatures():
            num = f["branche"]
            f["abscDebut"] = abscDebut[num]
            f["abscFin"] = abscFin[num]
            sommeB = sum([longBranche[i] for i in longBranche.keys() if i < num])

            listDeb = [long for i, long in longueurZone[num] if i < f["numZone"]]
            f["absDebZone"] = max(sum(listDeb) + sommeB, abscDebut[num])

            listFin = [long for i, long in longueurZone[num] if i <= f["numZone"]]
            f["absFinZone"] = min(sum(listFin) + sommeB, abscFin[num])
            coucheRiv.updateFeature(f)

        coucheRiv.commitChanges()

        # del(coucheDissoute)
        # liste = glob.glob(nomFich[:-4]+".*")
        # for fich in liste :
        # os.remove(fich)


