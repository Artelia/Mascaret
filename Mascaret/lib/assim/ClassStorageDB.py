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

from .ClassAssimData import AssimData

class ClassStorageDB:
    """Handle storage of assimilation results in the database.

    Instances wrap a database manager and a scenario folder, providing
    convenience methods for inserting or querying the various tables used by
    the assimilation workflow.  The object also loads the associated JSON
    configuration using :class:`~assim_data.AssimData`.
    """

    def __init__(self, mdb, id_run, rep_scen, type_ctrl):
        """Initialize the assimilation database handler.

        :param mdb: Database manager instance implementing ``run_query`` and
                    exposing a ``SCHEMA`` attribute.
        :param rep_scen: Path to the scenario directory (used to load JSON data).
        :param id_run: Identifier of the current run within the database.
        :param type_ctrl: Control type string (``'ctrlKS'`` or ``'ctrlLaw'``).
        """
        self.mdb = mdb
        self.rep_scen =  rep_scen
        self.type_ctrl = type_ctrl
        self.id_run = id_run

        self.data = AssimData()
        self.data.load(folder=self.rep_scen)



    def storage_results(self):
        """Dispatch storage based on control type."""

        dispatch = {
            "ctrlKS": self.storage_ctrl_ks,
            "ctrlLaw": self.storage_ctrl_law,
        }
        handler = dispatch.get(self.type_ctrl)
        if handler:
            handler()


    def get_id_assim_ks(self, id_run, numz):
        """Retrieve control identifier for a ks zone.

        :param id_run: Identifier of the run.
        :param numz: Zone number associated with the ks control.
        :return: The ``id_ctrl`` value from the database, or ``None`` if not found.
        """
        sql = (
            f"SELECT id_ctrl FROM {self.mdb.SCHEMA}.assim_res_ks "
            f"WHERE id_runs = %s AND zone_num = %s"
        )
        return self.mdb.run_query(sql, (id_run, numz), fetch=True, arraysize=1)

    def get_info_law(self, id_law, source_law):
        """Get law name and type from database.

        :param id_law: Law identifier.
        :param source_law: Source type ('extremities' or 'lateral_inflows').
        :return: Tuple of ``(name, type)`` where *name* is the law name and *type* is
                 the law type code or -1 if not found.
        """
        if source_law == "extremities":
            sql = (
                f"SELECT name, type FROM {self.mdb.SCHEMA}.extremities "
                f"WHERE active AND gid = %s"
            )
        elif source_law == "lateral_inflows":
            sql = (
                f"SELECT name FROM {self.mdb.SCHEMA}.lateral_inflows "
                f"WHERE active AND gid = %s"
            )
        else:
            return None, -1

        info = self.mdb.run_query(sql, (id_law,), fetch=True)
        if not info:
            return None, -1

        type_loi = info[0][1] if len(info[0]) > 1 else -1
        return info[0][0], type_loi

    def get_id_assim_law(self, id_run, id_law, source_law):
        """Retrieve control identifier for a law-based assimilation.

        :param id_run: Identifier of the run.
        :param id_law: Identifier of the law entry.
        :param source_law: Source type string.
        :return: The ``id_ctrl`` value from the database, or ``None`` if not found.
        """
        sql = (
            f"SELECT id_ctrl FROM {self.mdb.SCHEMA}.assim_res_law "
            f"WHERE id_runs = %s AND source_law = %s AND id_law = %s"
        )
        return self.mdb.run_query(sql, (id_run, source_law, id_law), fetch=True, arraysize=1)

    def storage_ctrl_ks(self):
        """Store ks-control results from the loaded assimilation data."""
        ctrl_ks = self.data.get("ctrlKS")
        if not ctrl_ks:
            return

        for zone in ctrl_ks["lst_zone"]:
            numz = zone["num_zone"]
            info = zone["zone_info"]

            self._insert_or_ignore_assim_res_ks(
                self.id_run,
                numz,
                info["branchnum"],
                info["abs_min"],
                info["abs_max"],
                info["ref_ks_min"],
                info["ref_ks_maj"],
            )

            if not zone.get("xa"):
                continue

            if zone["type"] == "Ksmin" :
                var = 'ks_min'
            else:
                var = 'ks_maj'
            id_ctrl = self.get_id_assim_ks(self.id_run, numz)
            self._insert_assim_res(id_ctrl, self.id_run, "ctrlKS", var, zone["xa"][0])

    def storage_ctrl_law(self):
        """Store law-control results from the loaded assimilation data."""
        ctrl_law = self.data.get("ctrlLaw")
        if not ctrl_law:
            return

        for loi in ctrl_law["lst_loi"]:
            id_law = loi["id_law"]
            source_law = loi["source_law"]
            name_law, _ = self.get_info_law(id_law, source_law)

            self._insert_or_ignore_assim_res_law(
                self.id_run, id_law, source_law, loi["name_law"], name_law
            )

            if not loi.get("xa"):
                continue
            id_ctrl = self.get_id_assim_law(self.id_run, id_law, source_law)
            self._insert_assim_res(id_ctrl, self.id_run, "ctrlLaw", loi["type"], loi["xa"][0])

    def _insert_or_ignore_assim_res_law(self, id_runs, id_law, source_law, name_file_law, name_law):
        """Insert a row into the ``assim_res_law`` table if the
        combination (id_runs, id_law, source_law) does not already exist.

        :param id_runs: integer run identifier
        :param id_law: integer law identifier
        :param source_law: text indicating the law source (e.g. 'extremities')
        :param name_file_law: filename or identifier of the law file
        :param name_law: human-readable name of the law
        """
        query = f"""
            INSERT INTO {self.mdb.SCHEMA}.assim_res_law 
                (id_runs, id_law, source_law, name_file_law, name_law)
            SELECT %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM {self.mdb.SCHEMA}.assim_res_law
                WHERE id_runs = %s
                  AND id_law = %s
                  AND source_law = %s
            );
        """
        self.mdb.run_query(
            query,
            (id_runs, id_law, source_law, name_file_law, name_law,
             id_runs, id_law, source_law),
        )

    def _insert_or_ignore_assim_res_ks(
        self, id_runs, id_zone, branchnum, abs_min, abs_maj, ks_min, ks_maj
    ):
        """Insert a row into the ``assim_res_ks`` table for a ks-zone if
        the combination (id_runs, zone_num, branchnum) does not already exist.

        :param id_runs: integer run identifier
        :param id_zone: integer zone number
        :param branchnum: integer branch number
        :param abs_min: minimum abscissa value of the zone (double)
        :param abs_maj: maximum abscissa value of the zone (double)
        :param ks_min: reference ks minor bed (double)
        :param ks_maj: reference ks major bed (double)
        """
        query = f"""
            INSERT INTO {self.mdb.SCHEMA}.assim_res_ks
                (id_runs, zone_num, branchnum, abs_min, abs_max, ks_min, ks_maj)
            SELECT %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM {self.mdb.SCHEMA}.assim_res_ks
                WHERE id_runs = %s
                  AND zone_num = %s
                  AND branchnum = %s
            );
        """
        self.mdb.run_query(
            query,
            (id_runs, id_zone, branchnum, abs_min, abs_maj, ks_min, ks_maj,
             id_runs, id_zone, branchnum),
        )

    def _insert_assim_res(self, id_ctrl, id_runs, type_ctrl, var, val):
        """Insert a row into the ``assim_res`` table. 
        :param id_ctrl: integer control identifier (foreign key to control table)
        :param id_runs: integer run identifier
        :param type_ctrl: text controlling type (e.g. 'ctrlKS' or 'ctrlLaw')
        :param var: text name of the variable modified
        :param val:  value 
        """
        query = f"""
            INSERT INTO {self.mdb.SCHEMA}.assim_res 
                (id_runs, type_ctrl, id_ctrl, var, val)
            VALUES (%s, %s, %s, %s, %s);
        """
        self.mdb.run_query(query, (id_runs, type_ctrl, id_ctrl, var, val))
