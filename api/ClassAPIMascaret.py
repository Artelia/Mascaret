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

try:
    # Plugin
    from .masc import Mascaret
    from ..Structure.ClassFloodGate import ClassFloodGate
except:
    # autonome python
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from masc import Mascaret
    from Structure.ClassFloodGate import ClassFloodGate


def check_init(file):
    if '_init.' in file:
        return True
    return False


class ClassAPIMascaret:
    """ Class contain  model files creation and run model mascaret"""

    def __init__(self, main):
        # def __init__(self):

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

        self.results_api = {}

        self.masc = Mascaret(log_level='INFO')
        self.masc.create_mascaret(iprint=1)
        if isinstance(main, dict):
            self.clmas = None
            self.mgis = None
            self.dossierFileMasc = main["RUN_REP"]
            os.chdir(main["RUN_REP"])
            self.DEBUG = main["DEBUG"]
            self.baseName = main['BASE_NAME']
            self.clfg = ClassFloodGate(self)
            self.mobil_struct = self.clfg.fg_active()
        else:
            self.clmas = main
            self.mgis = self.clmas.mgis
            self.dossierFileMasc = self.clmas.dossierFileMasc
            self.DEBUG = self.mgis.DEBUG
            self.baseName = self.clmas.baseName
            # floodgat
            self.clfg = ClassFloodGate(self)
            self.mobil_struct = self.clfg.fg_active()

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
        return 0

    def init_file(self, casfile):
        """
        Get file for compute
        :param casfile: xcas file
        :return: list of type and of file
        """
        initfile = False
        if '_init.' in casfile:
            initfile = True
            self.mobil_struct = False
        files_name = []
        files_type = ['xcas']
        if not os.path.isfile(casfile):
            self.add_info('{} not found'.format(casfile))

            return None

        files_name.append(casfile)
        law_files = []
        law_tr_files = []

        for file in os.listdir('.'):
            if '.geo' in file:
                files_type.append('geo')
                files_name.append(file)
            elif '.lig' in file and initfile == check_init(file):
                files_type.append('lig')
                self.filelig = file
                files_name.append(self.filelig)
            elif '.met' in file and initfile == check_init(file):
                self.tracer = True
                files_type.append('tracer_meteo')
                filepath = file
                files_name.append(filepath)
            elif '.phy' in file and initfile == check_init(file):
                self.tracer = True
                files_type.append('tracer_parphy')
                filepath = file
                files_name.append(filepath)
            elif '.conc' in file and initfile == check_init(file):
                self.tracer = True
                files_type.append('tracer_conc')
                filepath = file
                files_name.append(filepath)
            elif '_tra.loi' in file and initfile == check_init(file):
                self.tracer = True
                law_tr_files.append(file)
            elif '.loi' in file and initfile == check_init(file):
                law_files.append(file)
            elif '.casier' in file and initfile == check_init(file):
                self.basin = True
                files_type.append('casier')
                files_name.append(file)
        # WARNING, the law order must be the same than xcas file
        if law_files:
            for file in sorted(law_files):
                files_type.append('loi')
                files_name.append(file)
        else:
            self.add_info("The laws are not found.")

        if self.tracer and law_tr_files:
            for file in sorted(law_tr_files):
                files_type.append('tracer_loi')
                filepath = file
                files_name.append(filepath)

        # listing
        files_type.append('listing')
        files_name.append(self.baseName + '.lis')
        if initfile:
            post = '_init'
        else:
            post = ''
        # Resultat
        files_type.append('res')
        files_name.append(self.baseName + post + '.opt')

        if self.tracer:
            # listing
            files_type.append('tracer_listing')
            files_name.append(self.baseName + '.tra_lis')
            # Resultat
            files_type.append('tracer_res')
            files_name.append(self.baseName + '.tra_opt')

        if self.basin:
            # listing
            files_type.append('listing_casier')
            files_name.append(self.baseName + '.cas_lis')
            # Resultat
            files_type.append('res_casier')
            files_name.append(self.baseName + '.cas_opt')
            # listing
            files_type.append('listing_liaison')
            files_name.append(self.baseName + '.liai_lis')
            # Resultat
            files_type.append('res_liaison')
            files_name.append(self.baseName + '.liai_opt')

        return [files_name, files_type]

    def init_hydro(self):
        """
        Initialize hydraulic
        :return:
        """
        self.npoin = self.masc.get_var_size('Model.X')[0]
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
        self.dt = self.masc.get('Model.DT')
        self.tini = self.masc.get('Model.InitTime')
        self.tfin = self.masc.get('Model.MaxCompTime')

        self.tmaxiter = self.masc.get('Model.MaxNbTimeStep')
        self.stpcrit = self.masc.get('Model.StopCriteria')
        self.conum = self.masc.get('Model.VarTimeStep')

        self.zmax_co = self.masc.get('Model.MaxControlZ')
        self.sect_co = self.masc.get('Model.ControlSection')

        #if self.DEBUG:
        self.mess_crit_stop()

    def mess_crit_stop(self):
        """Print the criteria information"""
        txt = '**************************************\n'

        if self.stpcrit == 1:
            txt += ('Stop Criteria : {} \n'
                    'Variable Time Step :{}\n'
                    'Initial Time : {} \n'
                    'Final Time :{} \n'
                    'Time Step : {} \n'.format(self.stpcrit,
                                               self.conum,
                                               self.tini,
                                               self.tfin,
                                               self.dt))
        elif self.stpcrit == 2:
            txt += ('Stop Criteria : {} \n'
                    'Variable Time Step :{}\n'
                    'Initial Time : {} \n'
                    'Max iteration :{} \n'
                    'Time Step : {} \n'.format(self.stpcrit,
                                               self.conum,
                                               self.tini,
                                               self.tmaxiter,
                                               self.dt))
        elif self.stpcrit == 3:
            txt += ('Stop Criteria : {} \n'
                    'Variable Time Step :{}\n'
                    'Initial Time : {} \n'
                    'Time Step : {} \n'
                    'Max level water of control : {} \n'
                    'Abscissa of control section : {} \n'
                    ''.format(self.stpcrit,
                              self.conum,
                              self.tini,
                              self.dt,
                              self.zmax_co,
                              self.masc.get('Model.X', self.sect_co - 1)))
        else:
            txt += "Criteria {} doesn't exists. \n".format(self.stpcrit)
        txt += '**************************************\n'
        self.add_info(txt)

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
            z_arret = self.masc.get('State.Z', self.sect_co - 1)
            while not z_arret > self.zmax_co:
                t0, t1, dtp = self.one_iter(t0, t1, dtp)
                z_arret = self.masc.get('State.Z', self.sect_co - 1)
        self.tfin = self.masc.get('State.PreviousTime')

    def one_iter(self, t0, t1, dtp):
        if self.mobil_struct:
            self.clfg.iter_fg(t0, dtp)

        self.masc.compute(t0, t1, dtp)
        if self.conum:
            dtp_tmp = self.masc.get('State.DT')
            if dtp_tmp != 0:
                dtp = dtp_tmp
        t0 = t1
        t1 += dtp
        return t0, t1, dtp

    def finalize(self):
        del self.masc
        if self.clfg is not None:
            self.clfg.finalize(self.tfin)
            self.results_api['STRUCT_FG'] = self.clfg.results_fg_mv
            if self.mgis is None:
                self.write_res_struct(self.results_api['STRUCT_FG'])

    def write_res_struct(self, res):
        import json
        with open(os.path.join(self.dossierFileMasc, "res_struct.res"),
                  'w') as filein:
            json.dump(res, filein)

    def main(self, filename, tracer=False, basin=False):
        self.tracer = tracer
        self.basin = basin
        self.initial(filename)
        if self.mobil_struct:
            self.clfg.init_floogate()
        self.compute()
        self.finalize()

    def add_info(self, txt):
        if self.mgis is not None:
            self.mgis.add_info(txt)
        else:
            print(txt)


if __name__ == '__main__':
    path = os.getcwd()
    dico = {
        "RUN_REP": path,
        "DEBUG": True,
        'BASE_NAME': 'mascaret'}

    api = ClassAPIMascaret(dico)
    api.main('mascaret.xcas')
    print('fin')
