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

