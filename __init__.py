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
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MascPlug class from file MascPlug.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .MascPlug import MascPlug
    return MascPlug(iface)
