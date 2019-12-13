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
from .masc import Mascaret
from ..Structure.ClassMethod import ClassMethod
# from masc import Mascaret
import numpy as np
class ClassAPI_Mascaret:
    """ Class contain  model files creation and run model mascaret"""

    def __init__(self, main):
    # def __init__(self):
        self.clmas = main
        self.mgis = self.clmas.mgis
        self.mdb = self.mgis.mdb
        self.dossierFileMasc = self.clmas.dossierFileMasc
        self.DEBUG = self.mgis.DEBUG
        self.baseName =self.clmas.baseName
        self.tracer = False
        self.basin = False
        self.filelig = None

        # self.dossierFileMasc = r'/home/daoum/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Mascaret/api'
        # self.DEBUG = True
        # self.baseName = 'mascaret'

        self.npoin = 0
        self.zini = 0
        self.qini = 0

        # floodgat

        self.clmeth = ClassMethod(self.mgis)


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
            self.mgis.add_info('{} not found'.format(casfile))
            # print(casfile, ' not found')
            return None

        files_name.append(
            os.path.join(self.dossierFileMasc, casfile))
        law_files = []
        law_tr_files = []

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
                filepath = os.path.join(self.dossierFileMasc, file)
                files_name.append(filepath)
            elif '.phy' in file and initfile == self.check_init(file):
                self.tracer = True
                files_type.append('tracer_parphy')
                filepath = os.path.join(self.dossierFileMasc, file)
                files_name.append(filepath)
            elif '.conc' in file and initfile == self.check_init(file):
                self.tracer = True
                files_type.append('tracer_conc')
                filepath = os.path.join(self.dossierFileMasc, file)
                files_name.append(filepath)
            elif '_tra.loi' in file and initfile == self.check_init(file):
                self.tracer = True
                law_tr_files.append(file)
            elif '.loi' in file and initfile == self.check_init(file):
                 law_files.append(file)
            elif '.casier' in file and initfile == self.check_init(file):
                self.basin = True
                files_type.append('casier')
                files_name.append(
                    os.path.join(self.dossierFileMasc, file))
        # WARNING, the law order must be the same than xcas file
        if law_files:
            for file in sorted(law_files):
                files_type.append('loi')
                files_name.append(
                    os.path.join(self.dossierFileMasc, file))
        else:
            self.mgis.add_info("The laws are not found.")

        if self.tracer and law_tr_files :
            for file in sorted(law_tr_files):
                files_type.append('tracer_loi')
                filepath = os.path.join(self.dossierFileMasc, file)
                files_name.append(filepath)


        # listing
        files_type.append('listing')
        files_name.append(os.path.join(self.dossierFileMasc, self.baseName + '.lis'))
        if initfile :
            post = '_init'
        else:
            post = ''
        # Resultat
        files_type.append('res')
        files_name.append(os.path.join(self.dossierFileMasc, self.baseName +post+ '.opt'))

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
        # print(txt)
        self.mgis.add_info(txt)

    def compute(self):
        """compute"""
        t0 = self.tini
        dtp = self.dt
        t1 = t0 + dtp
        if self.stpcrit == 1:
            while t0 < self.tfin:
                if t1 > self.tfin and self.conum:
                    t1=self.tfin
                    dtp = t1 - t0
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
            dtp_tmp = self.masc.get('State.DT')
            if dtp_tmp != 0 :
                dtp = dtp_tmp
        t0 = t1
        t1 += dtp
        return t0, t1, dtp
    def finalize(self):
        del self.masc
        #self.clmeth.sav_meth(self.id_struct, self.current_meth, self.wgt_met)
        # del self.clmeth

    def main(self,filename,tracer=False, basin=False):

        self.masc = Mascaret(log_level='INFO')
        self.masc.create_mascaret(iprint=1)

        self.tracer=tracer
        self.basin=basin
        self.initial(filename)
        self.init_floogate()
        self.temporal_law(200.0)
        self.compute()
        self.finalize()



    def init_floogate(self):
        self.param_fg, link_name_id = self.clmeth.get_param_fg()
        # attention init.loi ou pas
        # connaitrea la relation config et non law
        nb_loi_sing = self.masc.get_var_size("Model.Weir.Name")[0]
        print("nb loi", nb_loi_sing)

        for id in range(nb_loi_sing):
            numgraph = self.masc.get("Model.Weir.GraphNum", i=id) - 1
            name = self.masc.get("Model.Graph.Name", i=numgraph)
            if name.replace('_init','') in list(link_name_id.keys()) :
                id_config = link_name_id[name]
                self.param_fg[id_config]['NUMGRAPH'] = numgraph
        print(self.param_fg)

    def temporal_law(self,time):
        """ modification of law """

        for id_config in self.param_fg.keys():
            print('rentre', id_config)
            list_final=self.clmeth.update_law(id_config,self.param_fg[id_config], time)
            tab_final = self.clmeth.sort_law(list_final)
            list_q = np.unique(tab_final[:, 0])
            nbq = len(list_q)
            list_zav = np.unique(tab_final[:, 1])
            nbzav = len(list_zav)
            list_zam=list(tab_final[:, 2])
            num=self.param_fg[id_config]['NUMGRAPH']

            dim1, dim2_q, dim3 = self.masc.get_var_size("Model.Graph.Discharge", num)
            self.masc.set_var_size("Model.Graph.Discharge", dim1, nbq, dim3, index=num + 1)
            self.masc.set_var_size("Model.Graph.DownLevel", dim1, nbzav, dim3, index=num + 1)
            self.masc.set_var_size("Model.Graph.UpLevel", dim1, nbq, nbzav, index=num + 1)

            for ii,qq in enumerate(list_q):
                self.masc.set("Model.Graph.Discharge",qq, i=num, j=ii, k=0)
                for jj, zav in enumerate(list_zav):
                    self.masc.set("Model.Graph.DownLevel",zav, i=num, j=jj, k=0)
                    self.masc.set("Model.Graph.UpLevel", 99 , i=num, j=ii, k=jj)
                    # list_zam[ii * nbzav + jj]
                    

    def test_tab(self,nbj,nbk, num):
        for ii in range(nbj):
            for jj in range(nbk):
                    zam = self.masc.get("Model.Graph.UpLevel", i=num, j=ii, k=jj)
                    print(ii, jj, zam)

        #
        # print(name, type)
        # if type == 6:
        #     list_var = ['Discharge', 'DownLevel', 'UpLevel']
        #     # recuperation de la taille
        #     dim1, dim2_q, dim3 = self.masc.get_var_size("Model.Graph.Discharge", 0)
        #     print(dim1, dim2_q, dim3)
        #     # # # dim1 nb de loi , Vecteur 1D (dim2: nb val qui sont différente pour q, dim3 n'existe pas)
        #     # dim1, dim2_zav, dim3 = self.masc.get_var_size("Model.Graph.DownLevel", numgraph)
        #     # print(dim1, dim2_zav, dim3)
        #     # # #dim1 nb de loi, Vecteur 1D (dim2: nb val qui sont différente pour Zav, dim3 n'existe pas)
        #     # print("jjjj",dim2_q, dim2_zav)
        #     dim1, dim_q, dim_zav = self.masc.get_var_size("Model.Graph.UpLevel", numgraph)
        #     print(dim1, dim_q, dim_zav)
        #     # dim1 nb de loi , Vecteur 2D ( dim_q :nb val de q, dim_zav: nb val de Zav)
        #     q = self.masc.get("Model.Graph.Discharge", i=0, j=49, k=0)
        #     print(q)
        #     dict = self.dico_law()
        #     print(dict)
        #     self.masc.set_var_size("Model.Graph.Discharge", 3, 51, 0, index=1)
        #     self.masc.set_var_size("Model.Graph.UpLevel", 3, 51, 41, index=1)
        #     # self.masc.get_var_size("Model.Graph.DownLevel",)
        #
        #     dim1, dim_q, dim_zav = self.masc.get_var_size("Model.Graph.UpLevel", numgraph)
        #     dict = self.dico_law()
        #     print(dict)
        #
        #     q2 = self.masc.get("Model.Graph.Discharge", i=0, j=50, k=0)
        #     print(q2)
        #     self.masc.set("Model.Graph.Discharge", 9999.0, i=0, j=50, k=0)
        #     q2 = self.masc.get("Model.Graph.Discharge", i=0, j=50, k=0)
        #
        #     for a in range(41):
        #         self.masc.set("Model.Graph.UpLevel", 0.00099, i=0, j=50, k=a)
        #         zav = self.masc.get("Model.Graph.DownLevel", i=0, j=a, k=0)
        #         zam = self.masc.get("Model.Graph.UpLevel", i=0, j=50, k=a)
        #         print(q2, zav, zam, a)

            # self.update_law_mas()


    # def update_law_mas(self,):
    #     get_law()
    #     new_size()
    #     fill_law()
    #     pass
    #
    # method genral
        # 1er etape (peut être fait avant):
            # recuperer info (OK,get_param_fg)
            # modifier la géométrie (A test, in classLaw , modif_poly_time)
            # calcul de la nouvelle loi A test


        # 2ieme step:
            # modification size law
            # modification des values
                # si suppression case attention décalage tableau il faut mieux tout re-ecrire

        # 3ieme etape fin du calcul remettre la valeur de la loi initial
        #     self.clmeth.sav_meth(self.id_struct, self.current_meth, self.wgt_met)


if __name__ == '__main__':
    api = ClassAPI_Mascaret()
    api.main('mascaret_init.xcas')
    # wl0 = [api.masc.get('State.Z', i) for i in range(api.npoin)]
    print('fin')
    # state seulement état final
    # wl = [api.masc.get('State.Z', i) for i in range(api.npoin)]
    # zf = [api.masc.get('Model.Zbot', i) for i in range(api.npoin)]
    # x = [api.masc.get('Model.X', i) for i in range(api.npoin)]


    del api
