# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : mars,2026
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
import json
import os

from qgis.PyQt.QtWidgets import QWidget


def apply_tooltips_from_json(widget, json_filename):
    """
    Apply tooltips defined in a JSON file to a Qt widget and its children.
    Expected JSON structure:
        {
            "objectName_1": "Tooltip text for widget 1",
            "objectName_2": "Tooltip text for widget 2",
            ...
        }
    :param widget : QtWidgets.QWidget
        The root widget (dialog, main widget, etc.) on which to apply tooltips.
        All its descendants are searched using findChild().
    :param json_filename : str
        Name of the JSON file containing the tooltips
        (e.g. "assim_law_widget.json").
    """
    tooltips_dir = os.path.dirname(os.path.abspath(__file__))
    tooltips_path = os.path.join(tooltips_dir, json_filename)

    try:
        with open(tooltips_path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[WARN] Tooltips file not found : {tooltips_path}")
        return
    except json.JSONDecodeError as exc:
        print(f"[WARN] Error JSON in {tooltips_path}: {exc}")
        return
    # Display element
    # for child in widget.findChildren(QWidget):
    #     print(f"  {child.__class__.__name__}: {child.objectName()!r}")
    # Application des tooltips
    for object_name, tooltip in data.items():
        child = widget.findChild(QWidget, object_name)

        if child is not None:
            child.setToolTip(tooltip)
        else:
            if widget.mgis.DEBUG:
                print(
                    f"[WARN] '{object_name}' Widget not found for tooltip "
                    f"in {widget.__class__.__name__}"
                )
