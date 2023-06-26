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
import math
import os
import re
from shutil import copy2
import numpy as np
import dateutil


def del_2space(txt):
    return re.sub(' +', ' ', txt)


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
        return (l2[i] - l2[i - 1]) / (x - l1[i - 1]) * (a - l1[i - 1]) + l2[
            i - 1]
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

        longueur_zone[f["branche"]].append(
            (f["numZone"], f.geometry().length()))

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

            # mini = 999999999
            # i = 0
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
            somme_b = sum(
                [long_branche[i] for i in long_branche.keys() if i < num])
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
            somme_b = sum(
                [long_branche[i] for i in long_branche.keys() if i < num])

            list_deb = [long for i, long in longueur_zone[num] if
                        i < f["numZone"]]
            f["absDebZone"] = max(sum(list_deb) + somme_b, absc_debut[num])

            list_fin = [long for i, long in longueur_zone[num] if
                        i <= f["numZone"]]
            f["absFinZone"] = min(sum(list_fin) + somme_b, absc_fin[num])
            couche_riv.updateFeature(f)

        couche_riv.commitChanges()
        # del(couche_dissoute)
        # liste = glob.glob(nom_fich[:-4]+".*")
        # for fich in liste :
        # os.remove(fich)


def del_accent(ligne):
    """ supprime les accents du texte source """
    accents = {u'a': [u'à', u'ã', u'á', u'â'],
               u'e': [u'é', u'è', u'ê', u'ë'],
               u'i': [u'î', u'ï'],
               u'u': [u'ù', u'ü', u'û'],
               u'o': [u'ô', u'ö']}
    for (char, accented_chars) in accents.items():
        for accented_char in accented_chars:
            ligne = ligne.replace(accented_char, char)
    return ligne


def copy_dir_to_dir(src, target):
    """ Copi file in directory"""
    files = os.listdir(src)
    for i in range(0, len(files)):
        copy2(os.path.join(src, files[i]),
              os.path.join(target, files[i]))


def del_symbol(ligne):
    """ supprime les accents du texte source """
    accents = {u'_': [u'-', u'.']}
    for (char, accented_chars) in accents.items():
        for accented_char in accented_chars:
            ligne = ligne.replace(accented_char, char)
    return ligne


def replace_all(txt, dico):
    """
    Replace several items
    :param txt: text orginal
    :param dico: de remplacement des variable
    :return:
    """
    for i in dico:
        txt = txt.replace(i, dico[i])
    return txt


def read_version(masplug_path):
    """
    read version of plugin
    :return: (str) version
    """
    file = open(os.path.join(masplug_path, 'metadata.txt'), 'r')
    for ligne in file:
        if ligne.find("version=") > -1:
            ligne = ligne.split('=')
            val = ligne[1].strip()
            break
    file.close()
    return val


def tw_to_txt(tw, range_r, range_c, sep):
    clipboard = ''
    for c in range_c:
        if c != range_c[-1]:
            clipboard = '{}{}{}'.format(clipboard,
                                        tw.horizontalHeaderItem(c).text(), sep)
        else:
            clipboard = '{}{}\n'.format(clipboard,
                                        tw.horizontalHeaderItem(c).text())
    for r in range_r:
        for c in range_c:
            if c != range_c[-1]:
                clipboard = '{}{}{}'.format(clipboard, tw.item(r, c).data(0),
                                            sep)
            else:
                clipboard = '{}{}\n'.format(clipboard, tw.item(r, c).data(0))
    return clipboard


def datum_to_float(d, init):
    """
    :param d: array of datetime
    :param init:  initial datetime
    :return: time in second in function of initial datetime
    """
    return (d - init).total_seconds()


def fill_zminbed(mdb):
    """
    fill zleftminbed zrightminbed variables for profiles table
    :param mdb: classMasDatabase
    :return:
    """
    info = mdb.select('profiles',
                      where='X IS NOT NULL AND (zleftminbed IS NULL '
                            'OR zrightminbed IS NULL)',
                      list_var=['gid', 'x', 'z',
                                'leftminbed', 'zleftminbed',
                                'rightminbed', 'zrightminbed'])
    if not info:
        return
    if len(info['gid']) <= 1:
        return

    update_dico = {}
    for i, gid in enumerate(info['gid']):
        update_dico[gid] = {}
        x = [float(v) for v in info['x'][i].split()]
        z = [float(v) for v in info['z'][i].split()]
        if not info['rightminbed'][i]:
            info['rightminbed'][i] = x[-1]
            info['zrightminbed'][i] = z[-1]
            update_dico[gid]['rightminbed'] = x[-1]
            update_dico[gid]['zrightminbed'] = z[-1]

        if not info['leftminbed'][i]:
            info['leftminbed'][i] = x[0]
            info['zleftminbed'][i] = z[0]
            update_dico[gid]['leftminbed'] = x[0]
            update_dico[gid]['zleftminbed'] = z[0]

        if not info['zrightminbed'][i] or not info['zleftminbed'][i]:
            lstz_minor = []
            for xx, zz in zip(x, z):
                if info['leftminbed'][i] <= xx <= info['rightminbed'][i]:
                    lstz_minor.append(zz)
            update_dico[gid]['zrightminbed'] = lstz_minor[-1]
            update_dico[gid]['zleftminbed'] = lstz_minor[0]

    mdb.update("profiles", update_dico, var="gid")

def filter_pr_fct(pr_x, pr_z, seuil,fixe_x =[]):
    """
    Filters the points of a profile according to its slope
    :param pr_x: list of X point
    :param pr_z: list of Z point
    :param seuil: step
    :return:new  profile point X, Y and the error information
    """
    err = ''

    n = len(pr_z)
    nb = 5
    seuil2 = 0.
    x = [pr_x[0]]
    z = [pr_z[0]]
    derniere_pente = 1

    for i in range(1, n - 1):
        mini = max(0, i - nb)
        maxi = min(i + nb + 1, n)
        xx = pr_x[mini:maxi]
        zz = pr_z[mini:maxi]

        pente, ord = np.polyfit(xx, zz, 1)
        zz.sort()
        if len(zz) <= nb:
            err ="Warning: The filter works if there are a minimum of 5 points"
            return pr_x, pr_z, err
        mediane = zz[nb]

        if abs((pente - derniere_pente) / derniere_pente) > seuil:
            x.append(pr_x[i])
            # z.append(self.tab['z'][i])
            if abs(pr_z[i] - mediane) > seuil2:
                z.append(pr_z[i])
            else:
                z.append(mediane)
            derniere_pente = pente

    x.append(pr_x[-1])
    z.append(pr_z[-1])

    flag = True
    pr_x = [x[0]]
    pr_z = [z[0]]
    m = len(z)
    for i in range(1, m):
        if z[i - 1] != z[i]:
            if flag:
                pr_x.append(x[i - 1])
                pr_z.append(z[i - 1])

            pr_x.append(x[i])
            pr_z.append(z[i])
            flag = False
        elif i == m - 1:
            pr_x.append(x[i])
            pr_z.append(z[i])
        else:
            flag = True
    # force interpole sur les points de berge
    if len(fixe_x) > 0:
        new_points = list(zip(pr_x,pr_z))
        new_points = interp_point_fix(new_points,fixe_x)
        pr_x, pr_z = [], []
        for xx, zz in new_points:
            pr_x.append(xx)
            pr_z.append(zz)

    return pr_x, pr_z, err


def find_perpendicular_distance(p, p1, p2):
    """
    Compute the perpendicular distance between p point and the segment (p1,p2)
    :param p1 : tuple of point 1
    :param p2: tuple of point 2
    :param p: tuple of point P
    :return: distance
    """
    ## if start and end point are on the same x the distance is the difference in X.
    result = 0.0
    slope  = 0.0
    if abs(p1[0]-p2[0]):
        result=abs(p[0]-p1[0]);
    else:
        slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        intercept = p1[1] - (slope * p1[0])
        result = abs(slope * p[0] - p[1] + intercept) / math.sqrt(math.pow(slope, 2) + 1)
    return result


def proper_rdp(points, epsilon):
    """
    function of filter according to the perpendicular distance
     :param points: list of points
    :param epsilon: limit distance
    :return: filters points
    """
    firstPoint = points[0]
    lastPoint  = points[-1]
    if (len(points) < 3):
        return points
    index = -1
    dist  = 0.
    for i in range(1,len(points)-2):
        cDist = find_perpendicular_distance(points[i], firstPoint, lastPoint)
        if cDist > dist:
            dist = cDist
            index = i
    if (dist > epsilon):
        ##iterate
        l1 = points[0:index+1]
        l2 = points[index:]
        r1 = proper_rdp(l1, epsilon)
        r2 = proper_rdp(l2, epsilon)
        ## Concat r2 to r1 minus the end/startpoint that will be the same
        rs = r1[0:-1] + r2
        return rs
    else:
        return [firstPoint,lastPoint]

def filter_dist_perpendiculaire(pr_x, pr_z, seuil, fixe_x = [],dist_detection_vert = 0.2):
    """
    filters the points of a profile according to the perpendicular distance
    :param pr_x: list of X point
    :param pr_z: list of Z point
    :param seuil: limit distance
    :param dist_detection_vert :Gap of x for the detection of a vertical parish
    :return:new  profile point X, Y and the error information
    """
    err = ''
    points = list(zip(pr_x,pr_z))
    if len(points) <3 :
        err = "Warning: The filter works if there are a minimum of 3 points"
        return
    # traitement des paroi vertical a conserver  et fix conserver
    pointvert = []
    pointfixe = []
    pointhori = []
    savp = []
    for i, pts in enumerate(points[:-1]):
        if abs(points[i][0] - points[i + 1][0]) < dist_detection_vert:
            if points[i] not in pointvert:
                pointvert.append(points[i])
            pointvert.append(points[i + 1])
        if points[i][0] in fixe_x and points[i] not in pointfixe :
            pointfixe.append(points[i])
        if pts[1] == points[i + 1][1]:
            savp.append(pts)
            continue
        if len(savp) > 0 :
            pointhori.append((savp[0],pts))
            savp = []
    if len(savp) > 0:
        pointhori.append((savp[0],points[-1]))


    pointvert.sort(key=lambda x: x[0])
    pointfixe.sort(key=lambda x: x[0])
    # applique le filtre
    new_points = proper_rdp(points, seuil)
    # retire apres filtre les point correspondant vertical et horrizontal
    tmp_points = []
    cmpt = 0
    nbph = len(pointhori)
    if nbph > 0 :
        xh1 = pointhori[cmpt][0][0]
        xh2 = pointhori[cmpt][1][0]
    else:
        xh1 = 0
        xh2 = 0

    for idp, point in enumerate(new_points[:-1]):
        if point[0] in [x for x,y in pointfixe]:
            continue
        if len(pointvert) > 0:
            if point[0] in [x for x,y in pointvert]:
                continue
        if cmpt < nbph:
            if xh1 <= point[0]  <= xh2:
                continue
            if point[0]>xh2:
                cmpt +=1
                if cmpt < nbph:
                    xh1 = pointhori[cmpt][0][0]
                    xh2 = pointhori[cmpt][1][0]
        tmp_points.append(point)
    # last point
    tmp_points.append(new_points[-1])
    pointh = []
    for pts in pointhori :
        for ptn in pts:
                pointh.append(ptn)
    # adition des point
    new_points = tmp_points + pointvert + pointfixe +  pointh
    new_points.sort(key=lambda x: x[0])
    # traitement des berge qui n'ont pas de point
    tmp =  np.array(pointfixe)
    lst_interp = [ptx for ptx in fixe_x if ptx not in tmp[:,0]]
    if len(lst_interp) > 0:
        new_points = interp_point_fix(new_points, lst_interp)
    # supprimer double
    new_points = list(set(new_points))
    new_points.sort(key=lambda x: x[0])
    newx, newz = [], []
    for xx, zz in new_points:
        newx.append(round(xx,3))
        newz.append(round(zz,3))
    return newx, newz, err

def interp_point_fix(points,fixe_x):
    """
    Interpolation of fixpoints in filtered profiles
    :param points list of points
    :param fixe_x : X point list of fixpoints
     :return: new points
    """

    newfixe_x = []
    points_tmp = np.array(points)
    if len(fixe_x)>0 :
        newfixe_x = [val for val in fixe_x if val not in points_tmp[:,0] ]
        newfixe_x.sort()
    if len(newfixe_x) > 0 :
        fix_y = np.interp(newfixe_x, points_tmp[:,0], points_tmp[:,1])
        for ifix, xfix in enumerate(newfixe_x):
            compt = 0
            xx = points[compt][0]
            while xx<xfix :
                compt +=1
                xx = points[compt][0]
            points.insert(compt ,(xfix,fix_y[ifix]))

    return points

# ****************************************************************

class TypeErrorModel:
    """ Class contain  info error in Model"""

    def __init__(self, name=None, description=None, stop=None):
        """
        Args:
            :param description: str Type Name
            :param description:str description of error
            :param status: boolean status default of erro (True exist False: not exist)
        """
        self.name = ''
        if isinstance(name, str):
            self.name = name
        self.description = 'No description'
        if isinstance(description, str):
            self.description = description
        self.dicterr = {}
        self._status = None
        self.stop = stop

    @property
    def status(self):
        """
        Returns status value
        """
        self._status = self.get_status()

        return self._status

    def add_err(self, name_obj, txt, value=True):
        """
        add element error
        Args:
            :param name_obj : object name
            :param value : bool value of error
            :param txt : text of error
        """
        self.dicterr[name_obj] = {"value": value,
                                  "txt": txt
                                  }

    def del_err(self, name_obj):
        """
        delete in error dict
        Args:
            :param name_obj : object name
        """
        if name_obj in self.dicterr[name_obj].keys():
            del self.dicterr[name_obj]

    def get_val(self, name_obj):
        """
        delete in error dict
        Args:
            :param name_obj : object name
        Returns:
            :return value : value of error
        """
        return self.dicterr[name_obj]["value"]

    def get_txt(self, name_obj):
        """
        get txt in error dict
        Args:
            :param name_obj : object name
        Returns:
            :return  txt : text of error
        """
        return self.dicterr[name_obj]["txt"]

    def get_alltxt(self):
        """
        get all txt in error dict

        Returns:
            :return  txt : text of error
        """
        txtr = ''
        if len(self.dicterr.keys()) > 0:
            first = True
            for name_obj in self.dicterr.keys():
                if self.get_val(name_obj):
                    if first:
                        txtr += '*** {} ***\n'.format(self.description)
                        first = False
                    txtr += self.get_txt(name_obj)
                    txtr += '\n'
        return txtr

    def get_status(self):
        """
        get status
        """
        if len(self.dicterr.keys()) > 0:
            for name_obj in self.dicterr.keys():
                if self.get_val(name_obj):
                    return True
        else:
            return False

    def clear_err(self):
        self.dicterr = {}
