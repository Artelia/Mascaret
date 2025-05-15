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
    if "_init." in file:
        return True
    return False


class ClassAPIMascaret:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main, dbg=False):
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
            self.dossierFileMasc = main["RUN_REP"]
            os.chdir(main["RUN_REP"])
            self.baseName = main["BASE_NAME"]
        else:
            self.clmas = main
            self.mgis = self.clmas.mgis
            self.dossierFileMasc = self.clmas.dossierFileMasc
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
        Initialisation mascaret model with
        :return:
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
        intialize the management break
        :return:
        """

        param = get_no_keep_break()
        if param :
            size_sing = self.masc.get_var_size("Model.Weir.Name")[0]
            dtest={ tuple(val[0]): val[1] for val in param.values()}

            for i in range(size_sing):
                name = self.masc.get("Model.Weir.Name", i)
                node = self.masc.get("Model.Weir.Node", i)
                abs = self.masc.get("Model.Weir.RelAbscissa",i)
                branchnum  = self.masc.get("Model.Weir.ReachNum",i)
                blevel = self.masc.get("Model.Weir.BrkLevel", i)
                if (name,branchnum,abs) in dtest:
                    self.lst_node[i]= {'node':node - 1, 'BrkLevel': blevel}  # cause fortran commence 1



    def init_file(self, casfile):
        """
        Get file for compute
        :param casfile: xcas file
        :return: list of type and of file
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
        Initialize hydraulic
        :return:
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
        Initializes the variables  for the different stop criteriae
        :return:
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
        """Print the criteria information"""
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

    def check_not_to_keep_break(self):
        """
        Check if the break is kept
        :return:
        """
        # size_sing = self.masc.get_var_size("Model.Weir.Name")[0]
        # for i in range(size_sing):
        #     print(self.masc.get("Model.Weir.RelAbscissa",i))
        #     print(self.masc.get("State.Z", self.masc.get("Model.Weir.Node", i)-1 ))
        #     print(self.masc.get("Model.Weir.State",  i))
        #     print(self.masc.get("Model.Weir.BrkLevel", i))
        # print('******************************')
        if len(self.lst_node)>0:
            for ind, item in self.lst_node.items():
                stat = self.masc.get("Model.Weir.State",  ind)
                if stat and self.masc.get("State.Z",  item['node']) < item['BrkLevel']:
                    self.masc.set("Model.Weir.State", False, ind)



    def compute(self):
        """compute"""
        t0 = self.tini
        dtp = self.dt
        t1 = t0 + dtp
        if self.stpcrit == 1:
            while t0 < self.tfin:
                if t1 > self.tfin and self.conum:
                    t1 = self.tfin
                    dtp = t1 - t0
                t0, t1, dtp = self.one_iter(t0, t1, dtp)

        elif self.stpcrit == 2:
            for cmpt in range(self.tmaxiter):
                t0, t1, dtp = self.one_iter(t0, t1, dtp)
        elif self.stpcrit == 3:
            z_arret = self.masc.get("State.Z", self.sect_co - 1)
            while not z_arret > self.zmax_co:
                t0, t1, dtp = self.one_iter(t0, t1, dtp)
                z_arret = self.masc.get("State.Z", self.sect_co - 1)
        self.tfin = self.masc.get("State.PreviousTime")

    def one_iter(self, t0, t1, dtp):
        if self.mobil_struct:
            self.clfg.iter_fg(t0, dtp)
        if self.mobil_link:
            self.clfg_lk.iter_fg(t0, dtp)
        #print(f'**** time  {t0} ****')
        self.check_not_to_keep_break()
        if self.mobil_w:
            self.clfg_w.iter_fg(t0, dtp)

        self.masc.compute(t0, t1, dtp)
        if self.conum:
            dtp_tmp = self.masc.get("State.DT")
            if dtp_tmp != 0:
                dtp = dtp_tmp
        t0 = t1
        t1 += dtp
        return t0, t1, dtp

    def finalize(self):
        """
        Finalize the computing :
        - store results
        - close masc object
        - Display the end information
        :return:
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
        self.mess.export_obj(self.dossierFileMasc)

    def write_res_struct(self, res, filen="res_struct.res"):
        """
        Write a json file about the hydraulic structure results
        :param res: results to write f
        :return:
        """
        with open(os.path.join(self.dossierFileMasc, filen), "w") as filein:
            json.dump(res, filein)


    def main(self, filename, tracer=False, basin=False):
        """
         Main programme which run model
        :param filename: Xcas file
        :param tracer: if there is the tracers
        :param basin: if there is the basins
        :return:
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
        Display text
        :param txt: Text to display
        :return:
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
