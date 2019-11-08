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

import sys
import os




class ClassAPI_Mascaret:
    """ Class contain  model files creation and run model mascaret"""

    def __init__(self, main):
        self.clmas = main
        self.mgis = self.clmas.mgis
        self.mdb = self.mgis.mdb
        self.dossierFileMasc = self.clmas.dossierFileMasc
        self.DEBUG = self.mgis.DEBUG
        self.tracer = False
        self.basin = False
        # self.dossierFileMasc = r'/home/daoum/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Mascaret/api'
        # self.baseName = 'mascaret'
        # self.filelig = None
        # self.DEBUG = True

        self.npoin = 0
        self.zini = 0
        self.qini = 0

    def initial(self, casfile):
        """
        Initialisation mascaret model with
        :return:
        """
        study_files = self.init_file(casfile)
        print(len(study_files[0]), len(study_files[1]))
        if study_files is None:
            return 1
        self.masc.import_model(study_files[0], study_files[1])

        self.init_hydro()

        self.init_crit_stop()
        print(self.tini)

    def init_file(self, casfile):
        """
        Get file for compute
        :param casfile: xcas file
        :return: list of type and of file
        """
        initfile = False
        if '_init.' in casfile:
            initfile = True
        files_name = []
        files_type = ['xcas']
        if not os.path.isfile(casfile):
            # self.mgis.add_info('{} not found'.format(casfile))
            print(casfile, ' not found')
            return None

        files_name.append(
            os.path.join(self.dossierFileMasc, casfile))


        for file in os.listdir(self.dossierFileMasc):
            if '.geo' in file:
                files_type.append('geo')
                files_name.append(
                    os.path.join(self.dossierFileMasc, file))
            elif '.lig' in file and initfile == self.check_init(file):
                files_type.append('lig')
                self.filelig = os.path.join(self.dossierFileMasc, file)
                files_name.append(self.filelig)
            elif '.met' in file and initfile == self.check_init(file):
                self.tracer = True
                files_type.append('tracer_meteo')
                self.filelig = os.path.join(self.dossierFileMasc, file)
                files_name.append(self.filelig)
            elif '.phy' in file and initfile == self.check_init(file):
                self.tracer = True
                files_type.append('tracer_parphy')
                self.filelig = os.path.join(self.dossierFileMasc, file)
                files_name.append(self.filelig)
            elif '.conc' in file and initfile == self.check_init(file):
                self.tracer = True
                files_type.append('tracer_conc')
                self.filelig = os.path.join(self.dossierFileMasc, file)
                files_name.append(self.filelig)
            elif '_tra.loi' in file and initfile == self.check_init(file):
                self.tracer = True
                files_type.append('tracer_loi')
                self.filelig = os.path.join(self.dossierFileMasc, file)
                files_name.append(self.filelig)
            elif '.loi' in file and initfile == self.check_init(file):
                files_type.append('loi')
                files_name.append(
                    os.path.join(self.dossierFileMasc, file))
            elif '.casier' in file and initfile == self.check_init(file):
                self.basin = True
                files_type.append('casier')
                files_name.append(
                    os.path.join(self.dossierFileMasc, file))


        # listing
        files_type.append('listing')
        files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.lis'))
        # Resultat
        files_type.append('res')
        files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.opt'))

        if self.tracer:
            # listing
            files_type.append('tracer_listing')
            files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.tra_lis'))
            # Resultat
            files_type.append('tracer_res')
            files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.tra_opt'))

        if self.basin:
            # listing
            files_type.append('listing_casier')
            files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.cas_lis'))
            # Resultat
            files_type.append('res_casier')
            files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.cas_opt'))
            # listing
            files_type.append('listing_liaison')
            files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.liai_lis'))
            # Resultat
            files_type.append('res_liaison')
            files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.liai_opt'))

        return [files_name, files_type]

    def check_init(self, file):
        if '_init.' in file:
            return True
        return False

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
        if self.tracer :
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

        if self.DEBUG:
            self.mess_crit_stop()

    def mess_crit_stop(self):
        """Print the crieria information"""
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
                              api.masc.get('Model.X', self.sect_co - 1)))
        else:
            txt += "Criteria {} doesn't exists. \n".format(self.stpcrit)
        txt += '**************************************\n'
        print(txt)
        # self.mgis.add_info(txt)

    def compute(self):
        """compute"""
        t0 = self.tini
        dtp = self.dt
        t1 = t0 + dtp
        if self.stpcrit == 1:
            while t0 < self.tfin:
                t0, t1, dtp = self.one_iter(t0, t1, dtp)

        elif self.stpcrit == 2:
            for cmpt in range(self.tmaxiter):
                t0, t1, dtp = self.one_iter(t0, t1, dtp)
        elif self.stpcrit == 3:
            z_arret = api.masc.get('State.Z', self.sect_co - 1)
            while not z_arret > self.zmax_co:
                t0, t1, dtp = self.one_iter(t0, t1, dtp)
                z_arret = api.masc.get('State.Z', self.sect_co - 1)
        self.tfin = self.masc.get('State.PreviousTime')

    def one_iter(self, t0, t1, dtp):
        self.masc.compute(t0, t1, dtp)
        if self.conum:
            dtp = self.masc.get('State.DTRezo')
        t0 = t1
        t1 += dtp
        return t0, t1, dtp

    def main(self,filename,tracer, basin):
        if (not os.path.exists(os.path.join(os.environ.get('HOMETEL', ''),
                                            'builds',
                                            os.environ.get('USETELCFG', ''),
                                            'wrap_api', 'lib', 'api.pyf'))):
            print("  -> telapy not available doing nothing")
            # sys.exit(0)
        #TODO trouver comment gerer ca

        from telapy.api.masc import Mascaret

        self.masc = Mascaret(log_level='INFO')
        self.masc.create_mascaret(iprint=1)

        self.tracer=tracer
        self.basin=basin
        self.initial(filename)
        self.compute()
        del self.masc



if __name__ == '__main__':
    api = ClassAPI_Mascaret()
    api.main('mascaret.xcas')
    # wl0 = [api.masc.get('State.Z', i) for i in range(api.npoin)]
    print('fin')
    # state seulement état final
    # wl = [api.masc.get('State.Z', i) for i in range(api.npoin)]
    # zf = [api.masc.get('Model.Zbot', i) for i in range(api.npoin)]
    # x = [api.masc.get('Model.X', i) for i in range(api.npoin)]
    #
    # plt.plot(x, wl, 'r')
    # plt.plot(x, wl0, 'g')
    # plt.plot(x, zf, 'y')
    # plt.show()

    del api
