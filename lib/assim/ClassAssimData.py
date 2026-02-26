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
        """Initialize the assimilation data accessor with empty store.

        :return: None.
        """
        self.raw = {}
        self._file_js = "data_assim.json"
        self._folder_js = "."

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    @property
    def filepath(self):
        """Full path to the current JSON file.

        :return: String path combining folder and filename.
        """
        return os.path.join(self._folder_js, self._file_js)

    def load(self, folder=".", filename="data_assim.json"):
        """Load and deserialize the JSON file into internal data store.

        ISO-formatted strings are automatically converted to
        :class:`~datetime.datetime` objects.

        :param folder: Directory containing the file.
        :param filename: JSON filename.
        :return: None. Populates *self.raw* from file.
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
        """Serialize internal data to a JSON file.

        :class:`~datetime.datetime` values are converted to ISO strings
        before writing.

        :param folder: Output directory (defaults to the folder used by :meth:`load`).
        :param filename: Output filename (defaults to the filename used by :meth:`load`).
        :return: None. Writes JSON file to disk.
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
        """Return value for a given key in the top-level data dict.

        :param var: Key name to retrieve.
        :param default: Default value if key is not found.
        :return: Value associated with key or default if not found.
        """
        return self.raw.get(var, default)

    @property
    def generate_instance(self):
        """The ``generate_instance`` top-level section.

        :return: Dict with run and scenario generation data.
        """
        return self.raw.get("generate_instance", {})

    @generate_instance.setter
    def generate_instance(self, value):
        """Set the ``generate_instance`` top-level section.

        :param value: Dict to store.
        :return: None.
        """
        self.raw["generate_instance"] = value

    @property
    def dscen(self):
        """The scenario sub-section of ``generate_instance``.

        :return: Scenario dict with instances list and metadata.
        """
        return self.generate_instance.get("dscen", {})

    @dscen.setter
    def dscen(self, value):
        """Set the scenario sub-section.

        :param value: Scenario dict to store.
        :return: None.
        """
        self.raw.setdefault("generate_instance", {})["dscen"] = value

    @property
    def drun(self):
        """The run configuration sub-section of ``generate_instance``.

        :return: Run configuration dict with run parameters.
        """
        return self.generate_instance.get("drun", {})

    # ------------------------------------------------------------------
    # Scenario convenience helpers
    # ------------------------------------------------------------------

    @property
    def instances(self):
        """List of run-instance dicts inside the scenario.

        :return: List of instance configuration dicts.
        """
        return self.dscen.get("instances", [])

    def initial_order(self):
        """Return the starting run-order index based on whether an init run exists.

        :return: ``2`` if the run has an initialisation phase, ``1`` otherwise.
        """
        return 2 if self.drun.get("has_run_init") else 1

    def get_folder(self):
        """Get mapping of instance name to RUN_REP folder for a scenario.

        :return: Dict mapping instance names to their RUN_REP path.
        """
        d_folder = {}
        for instance in self.instances:
            name = instance.get('name')
            if not name:
                continue
            d_folder[name] = instance.get("RUN_REP")
        return d_folder

    def get_instance(self, instance_name):
        """Get instance by name.

        :param instance_name: Instance name to find.
        :return: Instance dict or ``None`` if not found.
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

        :param data: Dict or list to process recursively.
        :return: None. Modifies *data* in place, converting ISO strings to datetime objects.
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

        :param data: Dict or list to process recursively.
        :return: None. Modifies *data* in place, converting datetime objects to ISO format.
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
        """Check if data store is non-empty.

        :return: ``True`` if data dict contains entries, ``False`` otherwise.
        """
        return bool(self.raw)

    def __repr__(self):
        """Return string representation of the AssimData instance.

        :return: String showing filepath and top-level section keys.
        """
        return f"AssimData(file={self.filepath!r}, sections={list(self.raw.keys())})"

    def __getitem__(self, key):
        """Get value from underlying data dict by key.

        :param key: Dict key to retrieve.
        :return: Value associated with key.
        :raises KeyError: If key not found in data dict.
        """
        return self.raw[key]

    def __setitem__(self, key, value):
        """Set value in underlying data dict by key.

        :param key: Dict key to set.
        :param value: Value to associate with key.
        :return: None.
        """
        self.raw[key] = value

    def __contains__(self, key):
        """Check if key exists in underlying data dict.

        :param key: Dict key to check.
        :return: ``True`` if key is present in data dict, ``False`` otherwise.
        """
        return key in self.raw
