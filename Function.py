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

import dateutil


def data_to_float(txt):
    try:
        float(txt)
        return float(txt)
    except ValueError:
        return None


def data_to_date(txt):
    try:
        dateutil.parser.parse(txt, dayfirst=True)
        return dateutil.parser.parse(txt, dayfirst=True)
    except ValueError:
        return None


def data_to_int(txt):
    try:
        int(txt)
        return int(txt)
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
    """ Interpolation
        l1: list 1
        l2: list 2
        a interpol value"""
    i, x = min(enumerate(l1), key=lambda xx: abs(xx[1] - a))

    if i < len(l1) - 1 and a >= x:
        return (l2[i + 1] - l2[i]) / (l1[i + 1] - x) * (a - x) + l2[i]
    elif i > 0 and a <= x:
        return (l2[i] - l2[i - 1]) / (x - l1[i - 1]) * (a - l1[i - 1]) + l2[i - 1]
    else:
        return None


def str2bool(s):
    """string to bool"""
    if "True" in s or "TRUE" in s:
        return True
    else:
        return False


def get_couche(nom, iface):
    for couche in iface.legendInterface().layers():
        if couche.name() == nom:
            return couche

    return None


def calcul_abscisses(liste_couches, riviere, iface, dossier):
    couche_riv = get_couche(riviere, iface)
    # fusion des branches
    nom_fich = os.path.join(dossier, "temp.shp")
    id = couche_riv.fieldNameIndex("branche")
    QgsGeometryAnalyzer().dissolve(couche_riv, nom_fich,
                                   onlySelectedFeatures=False,
                                   uniqueIdField=id, p=None)

    couche_dissoute = QgsVectorLayer(nom_fich, "temp", "ogr")

    long_branche = {}
    dico = {}
    for f in couche_dissoute.getFeatures():
        long_branche[f["branche"]] = f.geometry().length()
        dico[f["branche"]] = f

    longueur_zone = {}
    for f in couche_riv.getFeatures():
        if not f["branche"] in longueur_zone.keys():
            longueur_zone[f["branche"]] = []

        longueur_zone[f["branche"]].append((f["numZone"], f.geometry().length()))

    for c in liste_couches:
        if c == riviere:
            continue

        couche = get_couche(c, iface)
        if couche.wkbType() == 5:
            couche_noeud = QgsVectorLayer("Point", "temporary_points", "memory")

            couche_noeud.dataProvider().addAttributes(
                [QgsField("nom", QVariant.String, 'string', 10, 0),
                 QgsField("numBranche", QVariant.Int, 'int', 2, 0),
                 QgsField("abscisse", QVariant.Double, 'double', 10, 1)])

            couche_noeud.startEditing()
            for f in couche.getFeatures():
                for r in couche_dissoute.getFeatures():
                    if f.geometry().intersects(r.geometry()):
                        feat = QgsFeature(couche_noeud.dataProvider().fields())
                        feat.setGeometry(f.geometry().intersection(
                            r.geometry()))
                        feat["nom"] = f["nom"]
                        feat["numBranche"] = r["branche"]
                        couche_noeud.dataProvider().addFeatures([feat])
            couche_noeud.commitChanges()

        else:
            couche_noeud = couche

        couche_noeud.startEditing()

        # parcours de la liste de coucheNoeuds
        for n in couche_noeud.getFeatures():

            num = n["numBranche"]
            branche = dico[num]

            mini = 999999999
            i = 0
            # recuperation des coordonnees du point
            coord = n.geometry().asPoint()

            # on cherche le segment le plus proche du point souhaité
            d, dist, v_b = branche.geometry().closestSegmentWithContext(coord)
            v_a = v_b - 1

            # calcul de la distance depuis le début de la ligne
            somme = 0
            for i in range(1, v_b):
                somme += distance(branche.geometry().vertexAt(i - 1),
                                  branche.geometry().vertexAt(i))

            somme += distance(branche.geometry().vertexAt(v_a), dist)

            # calcul de l'abcisse
            somme_b = sum([long_branche[i] for i in long_branche.keys() if i < num])
            if somme < long_branche[num]:
                n["abscisse"] = somme + somme_b
            else:
                n["abscisse"] = None
            couche_noeud.updateFeature(n)

        couche_noeud.commitChanges()

        if couche.wkbType() == 5:
            couche.startEditing()

            for f in couche_noeud.getFeatures():
                for g in couche.getFeatures():
                    if f["nom"] == g["nom"]:
                        g["abscisse"] = f["abscisse"]
                        g["numBranche"] = f["numBranche"]
                        couche.updateFeature(g)

            couche.commitChanges()

    if riviere in liste_couches:
        absc_debut = {}
        absc_fin = {}

        couche_profil = get_couche("profils", iface)

        for p in couche_profil.getFeatures():

            if p["abscisse"] and p["actif"]:
                num = p["numBranche"]

                if num not in absc_debut.keys():
                    absc_debut[num] = 99999999
                if num not in absc_fin.keys():
                    absc_fin[num] = -99999999

                absc_debut[num] = min(absc_debut[num], p["abscisse"])
                absc_fin[num] = max(absc_fin[num], p["abscisse"])

        couche_riv.startEditing()

        for f in couche_riv.getFeatures():
            num = f["branche"]
            f["absc_debut"] = absc_debut[num]
            f["absc_fin"] = absc_fin[num]
            somme_b = sum([long_branche[i] for i in long_branche.keys() if i < num])

            list_deb = [long for i, long in longueur_zone[num] if i < f["numZone"]]
            f["absDebZone"] = max(sum(list_deb) + somme_b, absc_debut[num])

            list_fin = [long for i, long in longueur_zone[num] if i <= f["numZone"]]
            f["absFinZone"] = min(sum(list_fin) + somme_b, absc_fin[num])
            couche_riv.updateFeature(f)

        couche_riv.commitChanges()
        # del(couche_dissoute)
        # liste = glob.glob(nom_fich[:-4]+".*")
        # for fich in liste :
        # os.remove(fich)
