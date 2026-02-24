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
from pathlib import Path
from xml.etree.ElementTree import parse as et_parse

from .ClassAssimData import AssimData


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def indent(elem, level = 0):
    """Indent XML elements in-place for pretty printing.

    :param elem: XML element to indent.
    :param level: Current indentation depth.
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def fmt(liste):
    """Convert a list to a space-separated string.

    :param liste : List of values.
    :return: Space-separated string.
    """
    return " ".join(str(var) for var in liste)


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class ModelAssimBase:
    """Base class providing shared state, I/O and XML helpers for assimilation models.

    :attr:`data` is an :class:`~assim_data.AssimData` instance that centralises
    all access to the JSON configuration.
    """

    def __init__(self, mess=None):
        """Initialise the base model.

        :param mess: Optional messaging callable with signature
                     ``mess(key, level, text)``.
        """
        self.data = AssimData()
        self.mess = mess
        self.num_mess = 0

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def add_info(self, txt):
        """Log an informational message.

        :param txt: Message text.
        """
        if self.mess:
            self.mess(f"clAssim{self.num_mess}", "info", txt)
            self.num_mess += 1
        else:
            print(txt)

    # ------------------------------------------------------------------
    # JSON persistence  (thin wrappers – logic lives in AssimData)
    # ------------------------------------------------------------------

    def read_data_js(self, folder = ".", filein = "data_assim.json"):
        """Load assimilation data from a JSON file into :attr:`data`.

        :param folder: Directory containing the file.
        :param filein: Filename.
        """
        self.data.load(folder, filein)


    def export_data_json(
        self,
        folder = None,
        filename = None,
    ):
        """Persist :attr:`data` to disk.

        :param folder: Output directory (defaults to the folder used on load).
        :param filename: Output filename (defaults to the filename used on load).
        """
        self.data.save(folder, filename)

    # ------------------------------------------------------------------
    # File-system helpers
    # ------------------------------------------------------------------

    def clone_model(self, source_folder, target_folder):
        """Copy model initialisation files from *source_folder* to *target_folder*.

        Files with ``.opt`` or ``.lis`` extensions are skipped.

        :param source_folder: Path-like source directory.
        :param target_folder: Path-like target directory.
        :return: ``True`` on success, ``False`` otherwise.
        """
        ignore = {".opt", ".lis"}
        source = Path(source_folder)
        target = Path(target_folder)

        if not source.exists() or not source.is_dir():
            self.add_info(f"Invalid source folder: {source}")
            return False
        if not target.exists() or not target.is_dir():
            self.add_info(f"Invalid target folder: {target}")
            return False

        for file_path in source.iterdir():
            if not file_path.is_file() or file_path.suffix in ignore:
                continue
            try:
                shutil.copy2(file_path, target / file_path.name)
            except Exception as exc:
                self.add_info(f"Failed to copy '{file_path.name}': {exc}")

        return True

    # ------------------------------------------------------------------
    # XML helpers
    # ------------------------------------------------------------------

    def modif_xcas(self, parametres, xcasfile, folder):
        """Update friction parameters inside an xcas XML file.

        :param parametres: Mapping of parameter names to new values.
        :param xcasfile: xcas filename.
        :param folder: Directory containing *xcasfile*.
        """
        fich_entree = os.path.join(folder, xcasfile)
        arbre = et_parse(fich_entree)
        racine = arbre.getroot()

        parent = racine[0].find("parametresCalage")
        if parent is None:
            return

        child = parent.find("frottement")
        if child is None:
            return

        for param, val in parametres.items():
            element = child.find(param)
            if element is None:
                continue
            nouvelle_valeur = val.get("valeur", val) if isinstance(val, dict) else val
            if isinstance(nouvelle_valeur, (list, tuple)):
                element.text = " ".join(str(v) for v in nouvelle_valeur)
            else:
                element.text = str(nouvelle_valeur)

        indent(racine)
        arbre.write(fich_entree)

    def get_zone_frot(self, xcasfile, folder):
        """Extract friction-zone parameters from an xcas XML file.

        :param xcasfile: xcas filename.
        :param folder: Directory containing *xcasfile*.
        :return: Dictionary with friction-zone parameters.
        """
        fich_entree = os.path.join(folder, xcasfile)
        arbre = et_parse(fich_entree)
        racine = arbre.getroot()

        zone = {
            "loi": None,
            "nbZone": None,
            "numBranche": None,
            "absDebZone": None,
            "absFinZone": None,
            "coefLitMin": None,
            "coefLitMaj": None,
        }

        parent = racine[0].find("parametresCalage")
        if parent is None:
            return zone

        child = parent.find("frottement")
        if child is None:
            return zone

        for param in zone:
            element = child.find(param)
            if element is None or not element.text:
                continue
            text = element.text.strip()
            if param in ("coefLitMin", "coefLitMaj", "absDebZone", "absFinZone"):
                zone[param] = [float(v) for v in text.split()]
            elif param == "nbZone":
                zone[param] = int(text)
            else:
                zone[param] = text

        return zone

    # ------------------------------------------------------------------
    # Shared observation filter
    # ------------------------------------------------------------------

    def _filter_obs(self, data):
        """Deduplicate observation lists by identifier.

        :param data of observation dicts, each with ``id``, ``code``
                     and ``zero`` lists.
        :return: Deduplicated dict with ``id``, ``code`` and ``zero`` lists.
        """
        if not data:
            return {}

        unique_pairs = {}
        zero = {}
        for item in data:
            for i, id_val in enumerate(item["id"]):
                unique_pairs[id_val] = item["code"][i]
                zero[id_val] = item["zero"][i]

        return {
            "id": list(unique_pairs.keys()),
            "code": list(unique_pairs.values()),
            "zero": list(zero.values()),
        }

    # ------------------------------------------------------------------
    # Shared instance builder
    # ------------------------------------------------------------------

    def build_analyse_instance(
        self, drun, d_scen, order, type_assim,   xcas_file,
        xcas_file_init
    ):
        """Append analysis-run instance entries to *d_scen*.

        :param drun: Run configuration dict.
        :param d_scen: Scenario dict (modified in place).
        :param order: Current run-order counter.
        :param type_assim: Assimilation type label (e.g. ``'ctrlKS'``).
        :return: Updated ``(d_scen, order)`` tuple.
        """
        folder_run = os.path.join(d_scen["path_instance"], f"Analyse_{type_assim}")

        if drun["has_run_init"]:
            d_scen["instances"].append({
                "name": f"Analyse_{type_assim}_init",
                "name_xcas": xcas_file_init,
                "RUN_REP": os.path.join(folder_run, "run_init"),
                "has_casier": False,
                "has_tracer": False,
                "starttime": None,
                "order": order,
                "type_ctrl": type_assim,
            })
            order += 1

        d_scen["instances"].append({
            "name": f"Analyse_{type_assim}",
            "name_xcas": xcas_file,
            "RUN_REP": folder_run,
            "has_casier": drun["has_casier"],
            "has_tracer": drun["has_tracer"],
            "starttime": d_scen.get("starttime"),
            "order": order,
            "type_ctrl": type_assim,
        })
        order += 1

        return d_scen, order
