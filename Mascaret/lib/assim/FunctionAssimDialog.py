# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2017
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
"""
from qgis.core import (
    QgsProject,
    QgsCoordinateTransform,
    QgsGeometry
)

def reproject_geom_to_project(geom, source_crs):
    """Reproject a geometry to the project CRS if needed.

    :param geom: QgsGeometry — geometry to reproject.
    :param source_crs: QgsCoordinateReferenceSystem or None — CRS of the geometry.
                       If None, geometry is returned as-is.
    :return: QgsGeometry reprojected into the project CRS.
    """

    if source_crs is None or not source_crs.isValid():
        return geom

    project_crs = QgsProject.instance().crs()
    if source_crs == project_crs:
        return geom

    transform = QgsCoordinateTransform(
        source_crs,
        project_crs,
        QgsProject.instance(),
    )

    geom_reprojected = QgsGeometry(geom)  # copie pour ne pas muter l'original
    geom_reprojected.transform(transform)
    return geom_reprojected