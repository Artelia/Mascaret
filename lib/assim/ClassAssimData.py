# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret – AssimData
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

import json
import os
from datetime import datetime


class AssimData:
    """Typed accessor and persistence layer for the assimilation JSON data.

    The data dict is stored in :attr:`data` and all reads / writes go through
    named properties so callers never have to know the key names.

    Example::

        ad = AssimData()
        ad.load(".", "data_assim.json")
        d_scen = ad.dscen          # typed shortcut
        ad.dscen = d_scen          # write-back
        ad.save()
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self):
        """Initialise with an empty data store."""
        self.raw = {}
        self._file_js = "data_assim.json"
        self._folder_js = "."

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    @property
    def filepath(self):
        """Full path to the current JSON file."""
        return os.path.join(self._folder_js, self._file_js)

    def load(self, folder=".", filename="data_assim.json"):
        """Load and deserialise the JSON file into :attr:`data`.

        ISO-formatted strings are automatically converted to
        :class:`~datetime.datetime` objects.

        :param folder: Directory containing the file.
        :param filename: JSON filename.
        """
        self._folder_js = folder
        self._file_js = filename
        with open(self.filepath, "r") as fp:
            self.raw = json.load(fp)
        self._convert_str_to_datetime(self.raw)

    def save(
            self,
            folder=None,
            filename=None,
    ):
        """Serialise :attr:`data` to a JSON file.

        :class:`~datetime.datetime` values are converted back to ISO strings
        before writing.

        :param folder: Output directory (defaults to the folder used by
                       :meth:`load`).
        :param filename: Output filename (defaults to the filename used by
                         :meth:`load`).
        """
        out_folder = folder or self._folder_js
        out_file = filename or self._file_js
        snapshot = self.raw.copy()
        self._convert_datetime_to_str(snapshot)
        with open(os.path.join(out_folder, out_file), "w") as fp:
            json.dump(snapshot, fp, indent=4)

    # ------------------------------------------------------------------
    # Top-level section accessors
    # ------------------------------------------------------------------

    # @property
    # def data(self):
    #     """Return the internal data dict."""
    #     return self.raw

    def get(self, var, default=None):
        """Return value for a given key in the top-level data dict."""
        return self.raw.get(var, default)

    @property
    def generate_instance(self):
        """``generate_instance`` top-level section."""
        return self.raw.get("generate_instance", {})

    @generate_instance.setter
    def generate_instance(self, value):
        self.raw["generate_instance"] = value

    @property
    def dscen(self):
        """Scenario sub-section of ``generate_instance``."""
        return self.generate_instance.get("dscen", {})

    @dscen.setter
    def dscen(self, value):
        self.raw.setdefault("generate_instance", {})["dscen"] = value

    @property
    def drun(self):
        """Run configuration sub-section of ``generate_instance``."""
        return self.generate_instance.get("drun", {})

    # ------------------------------------------------------------------
    # Scenario convenience helpers
    # ------------------------------------------------------------------

    @property
    def instances(self):
        """List of run-instance dicts inside the scenario."""
        return self.dscen.get("instances", [])

    def initial_order(self):
        """Return the starting run-order index based on whether an init run exists.

        :return: ``2`` if the run has an initialisation phase, ``1`` otherwise.
        """
        return 2 if self.drun.get("has_run_init") else 1

    def get_folder(self):
        """Return mapping of instance name -> RUN_REP folder for a scenario.
        :return: Dict mapping instance names to their RUN_REP path.
        :rtype: dict
        """
        d_folder = {}
        for instance in self.instances:
            name = instance.get('name')
            if not name:
                continue
            d_folder[name] = instance.get("RUN_REP")
        return d_folder

    def get_instance(self, instance_name):
        """Get  instance by name .
        :param instance_name: Instance name to find.
        :type instance_name: str
        :return: Instance dict or None.
        :rtype: dict or None
        """
        for instance in self.instances:
            name = instance.get('name')
            if name == instance_name:
                return instance
        return None

    # ------------------------------------------------------------------
    # Internal datetime helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _convert_str_to_datetime(data):
        """Recursively convert ISO strings to :class:`datetime` objects in place.

        :param data or list to process.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    try:
                        data[key] = datetime.fromisoformat(value)
                    except ValueError:
                        pass
                else:
                    AssimData._convert_str_to_datetime(value)
        elif isinstance(data, list):
            for item in data:
                AssimData._convert_str_to_datetime(item)

    @staticmethod
    def _convert_datetime_to_str(data):
        """Recursively convert :class:`datetime` objects to ISO strings in place.

        :param data or list to process.
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, datetime):
                    data[key] = value.isoformat()
                else:
                    AssimData._convert_datetime_to_str(value)
        elif isinstance(data, list):
            for item in data:
                AssimData._convert_datetime_to_str(item)

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __bool__(self):
        return bool(self.raw)

    def __repr__(self):
        return f"AssimData(file={self.filepath!r}, sections={list(self.raw.keys())})"

    def __getitem__(self, key):
        return self.raw[key]

    def __setitem__(self, key, value):
        self.raw[key] = value

    def __contains__(self, key):
        return key in self.raw
