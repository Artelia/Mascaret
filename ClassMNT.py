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

# from shapely.wkb import loads
import numpy as np
from qgis.PyQt.QtCore import *
from qgis.core import *
from qgis.gui import *


class ClassMNT(QObject):
    """Example worker for calculating the total area of all features in a layer"""

    def __init__(self, main, profil, raster, facteur):
        QObject.__init__(self)
        self.mgis = main
        self.profil = profil
        self.raster_provider = raster.dataProvider()
        self.res = raster.rasterUnitsPerPixelX()
        self.facteur = facteur
        self.mnt = {}

    def run(self):

        # try:

        features = self.profil.selectedFeatures()
        self.profil.startEditing()

        for feature in features:
            geomcoupe = feature.geometry()
            longueur = geomcoupe.length()
            if longueur < self.res:
                self.mgis.add_info(
                    "Problem {0} between lenght profile : {1} and Raster accurancy : {2}."
                    .format(feature["name"], longueur, self.res))
                self.mgis.add_info(
                    "This problem could come from the projection units.")

            else:
                nom = feature["name"]
                gid = feature["gid"]
                feature["xmnt"] = ""
                feature["zmnt"] = ""

                # self.res taille du la résolution du raster

                for dist in np.arange(0.0, round(longueur, 3),
                                      round(self.res, 3)):

                    point = geomcoupe.interpolate(dist)
                    ident = self.raster_provider.identify(point.asPoint(),
                                                          QgsRaster.IdentifyFormatValue).results()

                    if ident[1]:
                        feature["xmnt"] += " " + str(dist)
                        feature["zmnt"] += " " + str(ident[1] / self.facteur)
                self.profil.updateFeature(feature)

                if len(feature["zmnt"]) > 0:
                    self.mgis.add_info(
                        "Extraction of {0} : Ok".format(feature['name']))
                else:
                    self.mgis.add_info(
                        "Extraction of {} : Echec".format(feature['name']))
                    self.mgis.add_info(
                        "This problem could come from the different projection"
                        " between the raster and the profile")

        try:  # qgis2
            self.profil.saveEdits()
        except:  # qgis 3
            self.profil.commitChanges()
