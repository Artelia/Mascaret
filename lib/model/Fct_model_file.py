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
import os
import shutil
import traceback
from ...ui.custom_control import ClassWarningBox

def around(x):
    """
    Round a value to two decimal places.
    :param x (float): Value to round
    :return: (float) Rounded value
    """
    x = round(float(x), 2)
    return x


def fmt(liste):
    """
    Convert a list to a space-separated string.
    :param liste (list): List of values
    :return: (str) Space-separated string
    """
    # list(map(str, liste))
    return " ".join([str(var) for var in liste])


def check_none(liste):
    """
    Check if any element in the list is None.
    :param liste (list): List to check
    :return: (bool) True if any element is None, False otherwise
    """
    for val in liste:
        if str(val) == "None":
            return True
    return False


def backup_file(file_path, ext):
    """
    Backup the file by renaming it with _old suffix.
    :param file_path: Path to the file.
    :param ext: Extension of the file (e.g. '.geo').
    """
    if os.path.isfile(file_path):
        backup = file_path.replace(ext, f"_old{ext}")
        shutil.move(file_path, backup)


def indent(elem, level=0):
    """
    Indent XML elements for pretty printing.
    :param elem (Element): XML element
    :param level (int): Indentation level
    :return: None
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def fmt_sans_none(liste, remplace_none):
    """
    Replace None values in a list with a given value and return as string.
    :param liste (list): List to process
    :param remplace_none (any): Value to replace None
    :return: (str) Space-separated string
    """
    liste = [remplace_none if var is None else var for var in liste]
    return " ".join([str(var) for var in liste])


def typ_struct(meth):
    """
    Get the law type for a given method.
    :param meth (int): Method code
    :return: (int or None) Law type
    """

    if meth == 0 or meth == 4 or meth == 1 or meth == 5 or meth == 3:
        return 1
    else:
        return None



