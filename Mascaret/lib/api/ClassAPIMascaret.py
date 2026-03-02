# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : Octobre, 2019
copyright            : (C) 2019 by Artelia
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
import sys

import numpy as np

try:
    # Plugin mode: relative imports when used inside QGIS
    from .masc import Mascaret
    from ..Structure.ClassTableStructure import get_no_keep_break
    from ..Structure.ClassFloodGate import ClassFloodGate
    from ..Structure.ClassFloodGateLk import ClassFloodGateLk
    from ..Structure.ClassMobilWeirs import ClassMobilWeirs
    from ..ClassMessage import ClassMessage
    from lib.assim.ClassExtractAssim import ClassExtractAssim
except Exception:
    # Standalone mode: absolute imports when run directly
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api.masc import Mascaret
    from Structure.ClassTableStructure import get_no_keep_break
    from Structure.ClassFloodGate import ClassFloodGate
    from Structure.ClassFloodGateLk import ClassFloodGateLk
    from Structure.ClassMobilWeirs import ClassMobilWeirs
    from ClassMessage import ClassMessage
    from assim.ClassExtractAssim import ClassExtractAssim

# Mapping from file extension to Mascaret file type, used in init_file
_EXT_TYPE_MAP = {
    ".met": "tracer_meteo",
    ".phy": "tracer_parphy",
    ".conc": "tracer_conc",
    ".casier": "casier",
}

# Extensions that activate the tracer flag
_TRACER_EXTENSIONS = {".met", ".phy", ".conc"}


def check_init(file):
    """Return True if the file is an initialisation file (contains '_init.' in its name)."""
    return "_init." in file


class ClassAPIMascaret:
    """Creates Mascaret model files and runs the Mascaret hydraulic model."""

    def __init__(self, main, dbg=False, generate_lig=False):
        """
        Initialise the Mascaret API.

        :param main: Main object or configuration dictionary.
        :param dbg: Enable debug mode.
        :param generate_lig: Generate a .lig restart file after computation.
        """
        self.DEBUG = dbg
        self.generate_lig = generate_lig

        # Initial hydraulic state
        self.npoin = 0
        self.zini = 0.0
        self.qini = 0.0

        # Time parameters
        self.dt = 0.0
        self.tini = 0.0
        self.tfin = 0.0

        # Stop criteria parameters
        self.tmaxiter = 0
        self.stpcrit = 0
        self.conum = 0
        self.zmax_co = 0.0
        self.sect_co = 0

        # Flags and file references
        self.tracer = False
        self.basin = False
        self.assim = False
        self.filelig = None
        self.info = ""

        self.lst_node = {}
        self.results_api = {}

        self.mess = ClassMessage()
        self.masc = Mascaret(log_level="INFO")
        self.masc.create_mascaret(iprint=1)

        # Configure paths depending on whether main is a dict or a plugin object
        if isinstance(main, dict):
            self.clmas = None
            self.mgis = None
            self.dossier_file_masc = main["RUN_REP"]
            os.chdir(main["RUN_REP"])
            self.base_name = main["BASE_NAME"]
        else:
            self.clmas = main
            self.mgis = self.clmas.mgis
            self.dossier_file_masc = self.clmas.dossier_file_masc
            self.base_name = self.clmas.baseName

        self.num_mess = 0

        # Data assimilation attributes
        self.num_zones_assim = 0
        self.dico_assim = None
        self.res_assim = None
        self.pdt_assim = 360  # assimilation time step in seconds

        # Mobile hydraulic structures
        self.clfg = ClassFloodGate(self)
        self.mobil_struct = self.clfg.actif_mobil_fg

        self.clfg_lk = ClassFloodGateLk(self)
        self.mobil_link = self.clfg_lk.actif_mobil_lk

        self.clfg_w = ClassMobilWeirs(self)
        self.mobil_w = self.clfg_w.actif_mobil_weir

        self.res_assim = ClassExtractAssim(self.dossier_file_masc)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def initial(self, casfile):
        """
        Initialise the Mascaret model using the given case file.

        :param casfile: Path to the .xcas file.
        :return: 0 on success, 1 on failure.
        """
        study_files = self.init_file(casfile)
        if study_files is None:
            return 1

        self.masc.import_model(study_files[0], study_files[1])
        self.init_hydro()
        self.init_crit_stop()
        self.init_struct()
        self.init_assim()

        return 0

    def init_assim(self):
        if self.assim:
            self.num_zones_assim = self.res_assim.init_assim(self.masc)

    def init_struct(self):

        self.init_break_and_regul()

        if self.mobil_struct:
            self.clfg.init_floogate()

        if self.basin and self.mobil_link:
            self.clfg_lk.init_fg_links()
        else:
            # No basin or link initialisation failed: disable link mobility
            self.mobil_link = False

        if self.mobil_w:
            self.clfg_w.init_fg_weirs()

    def init_break_and_regul(self):
        """
        Initialise breach management for weirs.

        Builds a lookup dict of weirs that must not be kept broken,
        indexed by their position in the Mascaret weir array.
        """
        param = get_no_keep_break()
        if not param:
            return

        size_sing = self.masc.get_var_size("Model.Weir.Name")[0]

        # Build an O(1) lookup: key = (name, branchnum, rel_abscissa)
        dtest = {tuple(val[0]): val[1] for val in param.values()}

        # Cache the get method to avoid repeated attribute resolution in the loop
        masc_get = self.masc.get

        for i in range(size_sing):
            name = masc_get("Model.Weir.Name", i)
            node = masc_get("Model.Weir.Node", i)
            rel_abs = masc_get("Model.Weir.RelAbscissa", i)  # renamed: 'abs' shadows the builtin
            branchnum = masc_get("Model.Weir.ReachNum", i)
            blevel = masc_get("Model.Weir.BrkLevel", i)
            if (name, branchnum, rel_abs) in dtest:
                # node - 1: Fortran arrays are 1-based, Python is 0-based
                self.lst_node[i] = {"node": node - 1, "BrkLevel": blevel}

    def init_file(self, casfile):
        """
        Collect all files required for computation.

        Scans the current working directory and categorises files by extension.
        Law files are sorted to match the order expected by the xcas file.

        :param casfile: Path to the .xcas file.
        :return: [list of file names, list of file types], or None if casfile not found.
        """
        initfile = check_init(casfile)
        if initfile:
            # Disable all mobile structures for initialisation runs
            self.mobil_struct = False
            self.mobil_link = False
            self.mobil_w = False

        if not os.path.isfile(casfile):
            self.add_info(f"{casfile} not found")
            return None

        files_name = [casfile]
        files_type = ["xcas"]
        law_files = []
        law_tr_files = []

        for file in os.listdir("."):
            matched = False

            # Match file against the extension-to-type mapping table
            for ext, ftype in _EXT_TYPE_MAP.items():
                if file.endswith(ext) and initfile == check_init(file):
                    if ext in _TRACER_EXTENSIONS:
                        self.tracer = True
                    elif ext == ".casier":
                        self.basin = True
                    files_type.append(ftype)
                    files_name.append(file)
                    matched = True
                    break
            if not matched:
                if file.endswith('.geo'):
                    files_type.append('geo')
                    files_name.append(file)
                # Handle extensions not covered by the mapping table
                elif ".lig" in file and initfile == check_init(file):
                    files_type.append("lig")
                    self.filelig = file
                    files_name.append(file)
                elif "_tra.loi" in file and initfile == check_init(file):
                    self.tracer = True
                    law_tr_files.append(file)
                elif ".loi" in file and initfile == check_init(file):
                    law_files.append(file)

        # WARNING: law file order must match the xcas file declaration order
        if law_files:
            if initfile:
                # Strip the '_init' suffix for sorting, then restore it
                law_tmp = sorted(f.replace("_init.loi", "") for f in law_files)
                for base in law_tmp:
                    files_type.append("loi")
                    files_name.append(base + "_init.loi")
            else:
                for file in sorted(law_files):
                    files_type.append("loi")
                    files_name.append(file)
        else:
            self.add_info("The laws are not found.")

        if self.tracer and law_tr_files:
            for file in sorted(law_tr_files):
                files_type.append("tracer_loi")
                files_name.append(file)

        # Listing and result output files
        files_type.append("listing")
        files_name.append(self.base_name + ".lis")

        post = "_init" if initfile else ""
        files_type.append("res")
        files_name.append(self.base_name + post + ".opt")

        if self.tracer:
            files_type.extend(["tracer_listing", "tracer_res"])
            files_name.extend([self.base_name + ".tra_lis", self.base_name + ".tra_opt"])

        if self.basin:
            files_type.extend(["listing_casier", "res_casier", "listing_liaison", "res_liaison"])
            files_name.extend([
                self.base_name + ".cas_lis",
                self.base_name + ".cas_opt",
                self.base_name + ".liai_lis",
                self.base_name + ".liai_opt",
            ])

        return [files_name, files_type]

    def init_hydro(self):
        """
        Initialise the hydraulic state of the Mascaret model.

        Uses np.full for array creation (faster than Python list multiplication).
        If a .lig restart file is available, the state is loaded from it instead.
        """
        self.npoin = self.masc.get_var_size("Model.X")[0]
        if self.filelig is None:
            # np.full is faster than [val] * n for large arrays
            zinit = np.full(self.npoin, self.zini)
            qinit = np.full(self.npoin, self.qini)
            self.masc.init_hydro(zinit, qinit)
        else:
            self.masc.init_hydro_from_file(self.filelig)

        if self.tracer:
            self.masc.init_tracer_state()

    def init_crit_stop(self):
        """
        Read and store all stop-criteria variables from the Mascaret model.

        Caches self.masc.get to reduce attribute lookups across multiple calls.
        """
        masc_get = self.masc.get  # local reference to avoid repeated attribute resolution
        self.dt = masc_get("Model.DT")
        self.tini = masc_get("Model.InitTime")
        self.tfin = masc_get("Model.MaxCompTime")

        self.tmaxiter = masc_get("Model.MaxNbTimeStep")
        self.stpcrit = masc_get("Model.StopCriteria")
        self.conum = masc_get("Model.VarTimeStep")

        self.zmax_co = masc_get("Model.MaxControlZ")
        self.sect_co = masc_get("Model.ControlSection")

        self.mess_crit_stop()

    def mess_crit_stop(self):
        """
        Log the active stop criterion and its associated parameters.

        Builds the message string from a shared base and criterion-specific details.
        """
        sep = "**************************************\n"

        # Common fields shared by all criteria
        base = (
            f"Variable Time Step : {self.conum}\n"
            f"Initial Time : {self.tini}\n"
            f"Time Step : {self.dt}\n"
        )

        if self.stpcrit == 1:
            details = f"Stop Criteria : {self.stpcrit}\n" + base + f"Final Time : {self.tfin}\n"
        elif self.stpcrit == 2:
            details = (
                    f"Stop Criteria : {self.stpcrit}\n" + base + f"Max iteration : {self.tmaxiter}\n"
            )
        elif self.stpcrit == 3:
            ctrl_x = self.masc.get("Model.X", self.sect_co - 1)
            details = (
                    f"Stop Criteria : {self.stpcrit}\n"
                    + base
                    + f"Max level water of control : {self.zmax_co}\n"
                      f"Abscissa of control section : {ctrl_x}\n"
            )
        else:
            details = f"Criteria {self.stpcrit} doesn't exist.\n"

        self.add_info(sep + details + sep)

    # ------------------------------------------------------------------
    # Computation loop
    # ------------------------------------------------------------------

    def check_not_to_keep_break(self, masc):
        """
        Reset weir breach state when the water level falls below the breach weirs.

        Short-circuits: State.Z is only fetched when Weir.State is True,
        avoiding unnecessary API calls.

        :param masc: Mascaret model object.
        """
        if not self.lst_node:
            return

        # Cache get/set methods to avoid repeated attribute resolution in the loop
        masc_get = self.masc.get
        masc_set = self.masc.set

        for ind, item in self.lst_node.items():
            if masc_get("Model.Weir.State", ind) and masc_get("State.Z", item["node"]) < item["BrkLevel"]:
                masc_set("Model.Weir.State", False, ind)

    def _should_stop(self):
        return (
                self.clfg_lk.arret_comput
                or self.clfg_w.arret_comput
                or bool(self.masc.error)
        )

    def compute(self):
        """
        Run the Mascaret computation loop according to the active stop criterion.

        Stop criteria:
            1 - Run until final time (tfin).
            2 - Run for a fixed number of iterations (tmaxiter).
            3 - Run until water level at control section exceeds zmax_co.

        Local variable caching is used to avoid repeated attribute lookups
        inside the hot loop.
        """
        t0 = self.tini
        dtp = self.dt
        t1 = t0 + dtp
        tfin = self.tfin
        conum = self.conum

        # Cache frequently accessed attributes as locals for performance
        masc = self.masc
        clfg = self.clfg
        clfg_lk = self.clfg_lk
        clfg_w = self.clfg_w
        mobil_struct = self.mobil_struct
        mobil_link = self.mobil_link
        mobil_w = self.mobil_w
        sect_co = self.sect_co

        def should_stop():
            """Return True if any stop condition has been triggered."""
            return any([clfg_lk.arret_comput, clfg_w.arret_comput, bool(masc.error)])

        if self.stpcrit == 1:
            # Time-based criterion: run until tfin
            while t0 < tfin:
                if t1 > tfin and conum:
                    # Clamp last time step to avoid overshooting tfin
                    t1 = tfin
                    dtp = t1 - t0
                t0, t1, dtp = self.one_iter(
                    t0, t1, dtp, masc, conum,
                    clfg, clfg_lk, clfg_w,
                    mobil_struct, mobil_link, mobil_w,
                )
                if self.should_stop():
                    break

        elif self.stpcrit == 2:
            # Iteration-based criterion: run for tmaxiter steps
            for _ in range(self.tmaxiter):
                t0, t1, dtp = self.one_iter(
                    t0, t1, dtp, masc, conum,
                    clfg, clfg_lk, clfg_w,
                    mobil_struct, mobil_link, mobil_w,
                )
                if should_stop():
                    break

        elif self.stpcrit == 3:
            # Level-based criterion: run until water level exceeds zmax_co
            while masc.get("State.Z", sect_co - 1) <= self.zmax_co:
                t0, t1, dtp = self.one_iter(
                    t0, t1, dtp, masc, conum,
                    clfg, clfg_lk, clfg_w,
                    mobil_struct, mobil_link, mobil_w,
                )
                if self.should_stop():
                    break

        # Store the actual simulation end time
        self.tfin = masc.get("State.PreviousTime")

    def one_iter(self, t0, t1, dtp, masc, conum, clfg, clfg_lk, clfg_w,
                 mobil_struct, mobil_link, mobil_w):
        """
        Perform one iteration of the Mascaret computation.

        Calls mobile structure handlers, runs the hydraulic solver, handles
        periodic assimilation, and updates the time step if variable stepping is active.

        :param t0: Current simulation time.
        :param t1: Target time for this step.
        :param dtp: Current time step duration.
        :param masc: Mascaret model object.
        :param conum: True if variable time step is active.
        :param clfg: FloodGate structure handler.
        :param clfg_lk: FloodGate link handler.
        :param clfg_w: Mobile weirs handler.
        :param mobil_struct: True if flood gate structures are active.
        :param mobil_link: True if flood gate links are active.
        :param mobil_w: True if mobile weirs are active.
        :return: Updated tuple (t0, t1, dtp).
        """
        # Update mobile structures before advancing the hydraulic solver
        if mobil_struct:
            clfg.iter_fg(t0, dtp)
        if mobil_link:
            clfg_lk.iter_fg(t0, dtp)
        self.check_not_to_keep_break(masc)
        if mobil_w:
            clfg_w.iter_fg(t0, dtp)

        # Advance the hydraulic solver by one step
        masc.compute(t0, t1, dtp)

        if self.assim and t0 % self.pdt_assim == 0:
            txt = f'{self.num_zones_assim} - {self.masc.nb_nodes}'
            self.add_info(txt)
            self.res_assim.extract_zq(self.masc, t0)

        # Update time step from model if variable stepping is active
        if conum:
            dtp_tmp = masc.get("State.DT")
            if dtp_tmp != 0:
                dtp = dtp_tmp

        t0 = t1
        t1 += dtp
        return t0, t1, dtp

    # ------------------------------------------------------------------
    # Finalisation
    # ------------------------------------------------------------------

    def finalize(self):
        """
        Finalise the computation.

        - Flushes the Mascaret log.
        - Writes assimilation results if active.
        - Closes and deletes the Mascaret object.
        - Finalises each active mobile structure handler and saves results.
        """
        # Flush and store the Mascaret internal log
        self.add_info(self.masc.log_stream.getvalue())
        # TODO if self.assim
        if self.assim:
            # Storing additionally KS values for later use in BLUE
            # valKSmin = [self.masc.get('Model.FricCoefMainCh', i) for i in self.res_assim.dict_obs]
            # valKSmaj = [self.masc.get('Model.FricCoefFP', i) for i in self.res_assim.dict_obs]
            # valKSmin = {i: self.masc.get('Model.FricCoefMainCh', i) for i in self.res_assim.dict_obs}
            # valKSmaj = {i: self.masc.get('Model.FricCoefFP', i) for i in self.res_assim.dict_obs}
            #
            # self.res_assim.store_KS_values(valKSmin, valKSmaj)
            self.res_assim.write_results(self.dossier_file_masc, 'Z_Q_assim.json')

        self.masc.delete_mascaret()
        del self.masc

        # Descriptor table: (active_flag, handler, result_key,  result_attr, output_filename)
        struct_map = [
            (self.mobil_struct, self.clfg, "STRUCT_FG", "results_fg_mv", "res_structs.res"),
            (self.mobil_link, self.clfg_lk, "LINK_FG", "results_fg_lk_mv", "res_links.res"),
            (self.mobil_w, self.clfg_w, "WEIRS", "results_fg_weirs_mv", "res_weirs.res"),
        ]
        for active, handler, key, attr, filename in struct_map:
            if active:
                handler.finalize(self.tfin)
                self.results_api[key] = getattr(handler, attr)
                # Only write to disk in standalone mode (no QGIS layer available)
                if self.mgis is None:
                    self.write_res_struct(self.results_api[key], filename)

        self.mess.export_obj(self.dossier_file_masc)

    def write_res_struct(self, res, filen="res_struct.res"):
        """
        Write hydraulic structure results to a JSON file.

        :param res: Dictionary of results to serialise.
        :param filen: Output file name (default: "res_struct.res").
        """
        filepath = os.path.join(self.dossier_file_masc, filen)
        with open(filepath, "w") as f:
            json.dump(res, f)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def fct_main(self, filename, tracer=False, basin=False, assim=False):
        """
        Top-level method that runs the full Mascaret workflow.

        Initialises the model, activates mobile structures, runs the computation,
        optionally generates a restart file, and finalises.

        :param filename: Path to the .xcas file.
        :param tracer: True if tracers are present in the model.
        :param basin: True if storage basins (casiers) are present.
        """
        self.tracer = tracer
        self.basin = basin
        self.assim = assim
        self.initial(filename)

        # # Early exit if a structure reported a blocking error during initialisation
        if self.clfg_lk.arret_comput or self.clfg_w.arret_comput:
            self.finalize()
            return

        self.compute()

        if self.generate_lig:
            self.masc.save_lig_restart(out_file="mascaret.lig", k_s=None)

        self.finalize()

    def add_info(self, txt):
        """
        Record an informational message via the message handler.

        Each message is assigned a unique incremental key of the form 'api_N'.

        :param txt: Text message to record.
        """
        self.mess.add_mess(f"api_{self.num_mess}", "info", txt)
        self.num_mess += 1


# ----------------------------------------------------------------------
# Script entry point
# ----------------------------------------------------------------------

if __name__ == "__main__":
    try:
        if len(sys.argv) <= 1:
            raise ValueError("No JSON file provided. Usage: script.py <config.json>")

        jsonf = sys.argv[1]
        with open(jsonf) as json_data:
            dico = json.load(json_data)

        # Determine whether to generate a .lig restart file from the xcas name
        gen_lig = dico.get("name", "").endswith("init")

        # TODO: replace this hard-coded path with a configuration key (e.g. dico["error_log"])
        error_log = dico.get(
            "error_log",
            os.path.join(os.path.dirname(jsonf), "ERROR.txt"),
        )
        with open(error_log, "a") as f:
            f.write(f"Gen lig {gen_lig}\n")

        api = ClassAPIMascaret(dico, generate_lig=gen_lig)
        api.fct_main(
            dico.get("name_xcas"),
            dico.get("has_tracer", False),
            dico.get("has_casier", False),
            dico.get("has_assim", False),
        )
        print("Work is done.")

    except Exception as err:
        import traceback

        error_info = f"{err}\n{traceback.format_exc()}"
        print("Error :", error_info)
