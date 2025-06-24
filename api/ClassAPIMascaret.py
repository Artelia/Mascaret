# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : Octobre,2019
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
import os
import sys
import json

try:
    # Plugin
    from .masc import Mascaret
    from ..Structure.ClassTableStructure import get_no_keep_break
    from ..Structure.ClassFloodGate import ClassFloodGate
    from ..Structure.ClassFloodGateLk import ClassFloodGateLk
    from ..Structure.ClassMobilWeirs import ClassMobilWeirs
    from ..ClassMessage import ClassMessage
except  ModuleNotFoundError or ImportError:
    # autonome python
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from masc import Mascaret
    from Structure.ClassTableStructure import get_no_keep_break
    from Structure.ClassFloodGate import ClassFloodGate
    from Structure.ClassFloodGateLk import ClassFloodGateLk
    from Structure.ClassMobilWeirs import ClassMobilWeirs


def check_init(file):
    """
    Check if the file is an initialization file.
    :param file (str): File name
    :return: (bool) True if file is an init file, False otherwise
    """
    if "_init." in file:
        return True
    return False


class ClassAPIMascaret:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main, dbg=False):
        """
        Initialize the API Mascaret class.
        :param main (object or dict): Main object or configuration dictionary
        :param dbg (bool): Debug mode
        :return: None
        """
        # def __init__(self):
        self.DEBUG = dbg

        self.npoin = 0
        self.zini = 0
        self.qini = 0

        self.dt = 0
        self.tini = 0
        self.tfin = 0

        self.tmaxiter = 0
        self.stpcrit = 0
        self.conum = 0

        self.zmax_co = 0
        self.sect_co = 0

        self.tracer = False
        self.basin = False
        self.filelig = None
        self.info = ''

        self.lst_node = {}

        self.results_api = {}

        self.masc = Mascaret(log_level="INFO")
        self.masc.create_mascaret(iprint=1)
        if isinstance(main, dict):
            self.clmas = None
            self.mgis = None
            self.dossier_file_masc = main["RUN_REP"]
            os.chdir(main["RUN_REP"])
            self.baseName = main["BASE_NAME"]
        else:
            self.clmas = main
            self.mgis = self.clmas.mgis
            self.dossier_file_masc = self.clmas.dossier_file_masc
            self.baseName = self.clmas.baseName

        self.mess = ClassMessage()
        self.num_mess = 0
        # floodgat
        self.clfg = ClassFloodGate(self)
        self.mobil_struct = self.clfg.fg_active()
        # links floodgate
        self.clfg_lk = ClassFloodGateLk(self)
        self.mobil_link = self.clfg_lk.actif_mobil_lk
        # weirs mobile
        self.clfg_w = ClassMobilWeirs(self)
        self.mobil_w = self.clfg_w.actif_mobil_weir
        # Break permanent
        # Model.Weir.BrkLevel
        # Model.Weir.State

    def initial(self, casfile):
        """
        Initialize the Mascaret model with the given case file.
        :param casfile (str): Path to the xcas file
        :return: (int) 0 if successful, 1 otherwise
        """
        study_files = self.init_file(casfile)
        # print(len(study_files[0]), len(study_files[1]))
        if study_files is None:
            return 1
        # print(study_files[0])
        self.masc.import_model(study_files[0], study_files[1])

        self.init_hydro()

        self.init_crit_stop()

        self.init_break_and_regul()

        return 0

    def init_break_and_regul(self):
        """
        Initialize the management of breaks for weirs.
        :return: None
        """

        param = get_no_keep_break()
        if param:
            size_sing = self.masc.get_var_size("Model.Weir.Name")[0]
            dtest = {tuple(val[0]): val[1] for val in param.values()}

            for i in range(size_sing):
                name = self.masc.get("Model.Weir.Name", i)
                node = self.masc.get("Model.Weir.Node", i)
                abs = self.masc.get("Model.Weir.RelAbscissa", i)
                branchnum = self.masc.get("Model.Weir.ReachNum", i)
                blevel = self.masc.get("Model.Weir.BrkLevel", i)
                if (name, branchnum, abs) in dtest:
                    self.lst_node[i] = {'node': node - 1, 'BrkLevel': blevel}  # cause fortran commence 1

    def init_file(self, casfile):
        """
        Get files for computation.
        :param casfile (str): xcas file
        :return: (list) List of file names and types, or None if not found
        """
        initfile = False
        if "_init." in casfile:
            initfile = True
            self.mobil_struct = False
            self.mobil_link = False
            self.mobil_w = False
        files_name = []
        files_type = ["xcas"]
        if not os.path.isfile(casfile):
            self.add_info("{} not found".format(casfile))

            return None

        files_name.append(casfile)
        law_files = []
        law_tr_files = []

        for file in os.listdir("."):
            if ".geo" in file:
                files_type.append("geo")
                files_name.append(file)
            elif ".lig" in file and initfile == check_init(file):
                files_type.append("lig")
                self.filelig = file
                files_name.append(self.filelig)
            elif ".met" in file and initfile == check_init(file):
                self.tracer = True
                files_type.append("tracer_meteo")
                filepath = file
                files_name.append(filepath)
            elif ".phy" in file and initfile == check_init(file):
                self.tracer = True
                files_type.append("tracer_parphy")
                filepath = file
                files_name.append(filepath)
            elif ".conc" in file and initfile == check_init(file):
                self.tracer = True
                files_type.append("tracer_conc")
                filepath = file
                files_name.append(filepath)
            elif "_tra.loi" in file and initfile == check_init(file):
                self.tracer = True
                law_tr_files.append(file)
            elif ".loi" in file and initfile == check_init(file):
                law_files.append(file)
            elif ".casier" in file and initfile == check_init(file):
                self.basin = True
                files_type.append("casier")
                files_name.append(file)
        # WARNING, the law order must be the same than xcas file
        if law_files:
            if initfile:
                law_tmp = [file.replace("_init.loi", "") for file in law_files]
                for file in sorted(law_tmp):
                    files_type.append("loi")
                    files_name.append(file + "_init.loi")
            else:
                for file in sorted(law_files):
                    files_type.append("loi")
                    files_name.append(file)

        else:
            self.add_info("The laws are not found.")

        if self.tracer and law_tr_files:
            for file in sorted(law_tr_files):
                files_type.append("tracer_loi")
                filepath = file
                files_name.append(filepath)

        # listing
        files_type.append("listing")
        files_name.append(self.baseName + ".lis")
        if initfile:
            post = "_init"
        else:
            post = ""
        # Resultat
        files_type.append("res")
        files_name.append(self.baseName + post + ".opt")

        if self.tracer:
            # listing
            files_type.append("tracer_listing")
            files_name.append(self.baseName + ".tra_lis")
            # Resultat
            files_type.append("tracer_res")
            files_name.append(self.baseName + ".tra_opt")

        if self.basin:
            # listing
            files_type.append("listing_casier")
            files_name.append(self.baseName + ".cas_lis")
            # Resultat
            files_type.append("res_casier")
            files_name.append(self.baseName + ".cas_opt")
            # listing
            files_type.append("listing_liaison")
            files_name.append(self.baseName + ".liai_lis")
            # Resultat
            files_type.append("res_liaison")
            files_name.append(self.baseName + ".liai_opt")

        return [files_name, files_type]

    def init_hydro(self):
        """
        Initialize hydraulic state for Mascaret.
        :return: None
        """
        self.npoin = self.masc.get_var_size("Model.X")[0]
        if self.filelig is None:
            qinit = [self.qini] * self.npoin
            zinit = [self.zini] * self.npoin
            self.masc.init_hydro(zinit, qinit)
        else:
            self.masc.init_hydro_from_file(self.filelig)
        if self.tracer:
            self.masc.init_tracer_state()

    def init_crit_stop(self):
        """
        Initialize variables for the different stop criteria.
        :return: None
        """
        self.dt = self.masc.get("Model.DT")
        self.tini = self.masc.get("Model.InitTime")
        self.tfin = self.masc.get("Model.MaxCompTime")

        self.tmaxiter = self.masc.get("Model.MaxNbTimeStep")
        self.stpcrit = self.masc.get("Model.StopCriteria")
        self.conum = self.masc.get("Model.VarTimeStep")

        self.zmax_co = self.masc.get("Model.MaxControlZ")
        self.sect_co = self.masc.get("Model.ControlSection")

        self.mess_crit_stop()

    def mess_crit_stop(self):
        """
        Print the criteria information.
        :return: None
        """
        txt = "**************************************\n"
        if self.stpcrit == 1:
            txt += (
                "Stop Criteria : {} \n"
                "Variable Time Step :{}\n"
                "Initial Time : {} \n"
                "Final Time :{} \n"
                "Time Step : {} \n".format(self.stpcrit, self.conum, self.tini, self.tfin, self.dt)
            )
        elif self.stpcrit == 2:
            txt += (
                "Stop Criteria : {} \n"
                "Variable Time Step :{}\n"
                "Initial Time : {} \n"
                "Max iteration :{} \n"
                "Time Step : {} \n".format(
                    self.stpcrit, self.conum, self.tini, self.tmaxiter, self.dt
                )
            )
        elif self.stpcrit == 3:
            txt += (
                "Stop Criteria : {} \n"
                "Variable Time Step :{}\n"
                "Initial Time : {} \n"
                "Time Step : {} \n"
                "Max level water of control : {} \n"
                "Abscissa of control section : {} \n"
                "".format(
                    self.stpcrit,
                    self.conum,
                    self.tini,
                    self.dt,
                    self.zmax_co,
                    self.masc.get("Model.X", self.sect_co - 1),
                )
            )
        else:
            txt += "Criteria {} doesn't exists. \n".format(self.stpcrit)
        txt += "**************************************\n"
        self.add_info(txt)

    def check_not_to_keep_break(self, masc):
        """
        Check if the break is kept for each weir.
        :param masc (Mascaret): Mascaret model object
        :return: None
        """
        # Optimisation: regrouper les accès à masc.get pour limiter les appels coûteux
        lst_node = self.lst_node
        if len(lst_node) > 0:
            items = list(lst_node.items())  # évite multiples itérations
            weir_states = [masc.get("Model.Weir.State", ind) for ind, _ in items]
            state_z = [masc.get("State.Z", item['node']) for _, item in items]
            brk_levels = [item['BrkLevel'] for _, item in items]
            for idx, (ind, item) in enumerate(items):
                if weir_states[idx] and state_z[idx] < brk_levels[idx]:
                    self.masc.set("Model.Weir.State", False, ind)
                    # TODO intergrer dans les graph

    def compute(self):
        """
        Run the Mascaret computation loop according to stop criteria.
        :return: None
        """
        t0 = self.tini
        dtp = self.dt
        t1 = t0 + dtp
        tfin = self.tfin
        conum = self.conum
        clfg = self.clfg
        clfg_lk = self.clfg_lk
        clfg_w = self.clfg_w
        masc = self.masc
        mobil_struct = self.mobil_struct
        mobil_link = self.mobil_link
        mobil_w = self.mobil_w
        sect_co = self.sect_co

        if self.stpcrit == 1:
            while t0 < tfin and not any([clfg_lk.arret_comput, clfg_w.arret_comput]):
                if t1 > tfin and conum:
                    t1 = tfin
                    dtp = t1 - t0
                t0, t1, dtp = self.one_iter(t0, t1, dtp,
                                            masc, conum, clfg, clfg_lk, clfg_w,
                                            mobil_struct, mobil_link, mobil_w)

        elif self.stpcrit == 2:
            for cmpt in range(self.tmaxiter):
                t0, t1, dtp = self.one_iter(t0, t1, dtp,
                                            masc, conum, clfg, clfg_lk, clfg_w,
                                            mobil_struct, mobil_link, mobil_w)
                if any([clfg_lk.arret_comput, clfg_w.arret_comput]):
                    break
        elif self.stpcrit == 3:
            z_arret = self.masc.get("State.Z", sect_co - 1)
            while not z_arret > self.zmax_co:
                t0, t1, dtp = self.one_iter(t0, t1, dtp,
                                            masc, conum, clfg, clfg_lk, clfg_w,
                                            mobil_struct, mobil_link, mobil_w)
                z_arret = self.masc.get("State.Z", sect_co - 1)
                if any([clfg_lk.arret_comput, clfg_w.arret_comput]):
                    break

        self.tfin = self.masc.get("State.PreviousTime")

    def one_iter(self, t0, t1, dtp,
                 masc, conum, clfg, clfg_lk, clfg_w,
                 mobil_struct, mobil_link, mobil_w):
        """
        Perform one iteration of the Mascaret computation.
        :param t0 (float): Current time
        :param t1 (float): Next time
        :param dtp (float): Time step
        :param masc (Mascaret): Mascaret model object
        :param conum (bool): Variable time step flag
        :param clfg (ClassFloodGate): FloodGate structure handler
        :param clfg_lk (ClassFloodGateLk): FloodGate link handler
        :param clfg_w (ClassMobilWeirs): Mobile weirs handler
        :param mobil_struct (bool): Structure mobility flag
        :param mobil_link (bool): Link mobility flag
        :param mobil_w (bool): Weir mobility flag
        :return: (tuple) Updated t0, t1, dtp
        """
        # Optimisation: stocker les méthodes dans des variables locales

        if mobil_struct:
            clfg.iter_fg(t0, dtp)
        if mobil_link:
            clfg_lk.iter_fg(t0, dtp)
        self.check_not_to_keep_break(masc)
        if mobil_w:
            clfg_w.iter_fg(t0, dtp)
            # Suppression du print inutile pour accélérer la boucle
            # print('1iter', time.perf_counter() - a)

        masc.compute(t0, t1, dtp)
        if conum:
            dtp_tmp = masc.get("State.DT")
            if dtp_tmp != 0:
                dtp = dtp_tmp
        t0 = t1
        t1 += dtp
        return t0, t1, dtp

    def finalize(self):
        """
        Finalize the computation:
        - Store results
        - Close Mascaret object
        - Display end information
        :return: None
        """
        info = self.masc.log_stream.getvalue()
        self.add_info(info)
        self.masc.delete_mascaret()
        del self.masc
        if self.clfg is not None:
            self.clfg.finalize(self.tfin)
            self.results_api["STRUCT_FG"] = self.clfg.results_fg_mv
            if self.mgis is None:
                self.write_res_struct(self.results_api["STRUCT_FG"], "res_struct.res")
        if self.mobil_link:
            self.clfg_lk.finalize(self.tfin)
            self.results_api["LINK_FG"] = self.clfg_lk.results_fg_lk_mv
            if self.mgis is None:
                self.write_res_struct(self.results_api["LINK_FG"], "res_link_fg.res")
        if self.mobil_w:
            self.clfg_w.finalize(self.tfin)
            self.results_api["WEIRS"] = self.clfg_w.results_fg_weirs_mv
            if self.mgis is None:
                self.write_res_struct(self.results_api["WEIRS"], "res_weirs_fg.res")
        self.mess.export_obj(self.dossier_file_masc)

    def write_res_struct(self, res, filen="res_struct.res"):
        """
        Write a JSON file about the hydraulic structure results.
        :param res (dict): Results to write
        :param filen (str): File name, default "res_struct.res"
        :return: None
        """
        with open(os.path.join(self.dossier_file_masc, filen), "w") as filein:
            json.dump(res, filein)

    def main(self, filename, tracer=False, basin=False):
        """
        Main program which runs the model.
        :param filename (str): Xcas file
        :param tracer (bool): If there are tracers
        :param basin (bool): If there are basins
        :return: None
        """
        self.tracer = tracer
        self.basin = basin
        self.initial(filename)
        if self.mobil_struct:
            self.clfg.init_floogate()
        if basin and self.mobil_link:
            self.clfg_lk.init_fg_links()
        else:
            self.mobil_link = False
        if self.mobil_w:
            self.clfg_w.init_fg_weirs()
        if self.clfg_lk.arret_comput or self.clfg_w.arret_comput:
            self.finalize()

        self.compute()
        self.finalize()

    def add_info(self, txt):
        """
        Display text information.
        :param txt (str): Text to display
        :return: None
        """
        self.mess.add_mess('api_{}'.format(self.num_mess), 'info', txt)
        self.num_mess += 1
        # print(txt)


if __name__ == "__main__":
    path = os.getcwd()
    dico = {"RUN_REP": path, "DEBUG": True, "BASE_NAME": "mascaret"}

    api = ClassAPIMascaret(dico)
    api.main("mascaret.xcas")
    print("fin")
