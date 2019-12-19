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
# from .masc import Mascaret
from mascv2 import Mascaret

class ClassAPI_Mascaret:
    """ Class contain  model files creation and run model mascaret"""

    # def __init__(self, main):
    def __init__(self):
        # self.clmas = main
        # self.mgis = self.clmas.mgis
        # self.mdb = self.mgis.mdb
        # self.dossierFileMasc = self.clmas.dossierFileMasc
        # self.DEBUG = self.mgis.DEBUG
        # self.baseName =self.clmas.baseName
        self.tracer = False
        self.basin = False
        self.filelig = None

        self.dossierFileMasc = r'/home/daoum/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Mascaret/mascaret'
        self.DEBUG = True
        self.baseName = 'mascaret'

        self.npoin = 0
        self.zini = 0
        self.qini = 0
        self.mobil_struct = True
    def initial(self, casfile):
        """
        Initialisation mascaret model with
        :return:
        """
        study_files = self.init_file(casfile)
        # print(len(study_files[0]), len(study_files[1]))
        if study_files is None:
            return 1
        print(study_files[0])
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
            print("The laws are not found.")

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
        print(self.dt,self.tini, self.tfin)
        self.tmaxiter = self.masc.get('Model.MaxNbTimeStep')
        self.stpcrit = self.masc.get('Model.StopCriteria')
        print(self.tmaxiter, self.stpcrit)
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
                print(t0)
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

        if self.mobil_struct:
            self.update_law_struct(t1)

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


    def main(self, filename, tracer=False, basin=False):

        self.masc = Mascaret(log_level='INFO')
        self.masc.create_mascaret(iprint=1)

        self.tracer = tracer
        self.basin = basin
        self.initial(filename)
        self.compute()
        self.finalize()

    def update_law_struct(self, time):
        """ Update structure law """
        # 2 cas
        #   o mouvement en fonction du Time : velocity
        #   o mouvement en fonction de la cote dans le domaine
        ##******************************
        # fonctionnement vanne
        #    o si cote atteint vanne en mouvement avec une vitesse d'incrementation
        #    o modification polygone
        ##******************************

        # for id_config in self.param_fg.keys():

            # TODO check modification
            # compute new law
            # list_final=self.clmeth.update_law(id_config,self.param_fg[id_config], time)
            # tab_final = self.clmeth.sort_law(list_final)
            # list_q = np.unique(tab_final[:, 0])
            # list_zav = np.unique(tab_final[:, 1])
            # list_zam=list(tab_final[:, 2]))
        list_q = []
        list_zav = []
        list_zam = []
        # modification in mascaret model
        id_config=0
        if time == 200:
            self.update_law_mas(id_config, list_q, list_zav, list_zam)

    def update_law_mas(self, id_config, list_q, list_zav, list_zam):
        """
         update information model with api
        :param id_config: index of structure
        :param list_q: list of flow rate
        :param list_zav: list of upstream Z
        :param list_zam: list of downstream Z
        :return
        """
        # nbq = len(list_q)
        # nbzav = len(list_zav)
        # num = self.param_fg[id_config]['NUMGRAPH']
        num = 0
        nbq=51
        nbzav=42
       # list_zam = [10] * (nbq*nbzav)
        list_zam = []
        self.write('deb.csv',nbq-1,nbzav-1)
        list_q=[]
        list_zav=[]
        cond = True
        for ii in range(nbq-1):
            list_q.append(self.masc.get("Model.Weir.PtQ", i=0, j=ii, k=0))

            for jj in range(nbzav-1):
                if cond:
                    list_zav.append(self.masc.get("Model.Weir.PtZds", i=0, j=jj, k=0))

                list_zam.append(self.masc.get("Model.Weir.PtZus", i=0, j=ii, k=jj))
            cond = False
            list_zam.append(list_zam[-1] + 1)
        list_q.append(list_q[-1]+10)
        list_zav.append(list_zav[-1]+1)
        for kk in range(nbzav+1):
            list_zam.append(20)

        dim1, dim2_q, dim3 = self.masc.get_var_size("Model.Weir.PtQ", num)
        # q = self.masc.get("Model.Weir.PtQ", i=0, j=49, k=0)
        print(dim1, dim2_q, dim3)
        self.masc.set_var_size('Model.Weir.PtQ', dim1, nbq, dim3, index=num + 1)
        # self.masc.set("Model.Weir.PtQ", q+10, i=0, j=50, k=0)

        dim11, dim22_q, dim33 = self.masc.get_var_size("Model.Weir.PtQ", num)
        print(dim11, dim22_q, dim33)
        self.masc.set_var_size("Model.Weir.PtZds", dim1, nbzav, dim3, index=num + 1)
        dim11, dim22_q, dim33 = self.masc.get_var_size("Model.Weir.PtZds", num)
        print(dim11, dim22_q, dim33)
        self.masc.set_var_size("Model.Weir.PtZus", dim1, nbq, nbzav, index=num + 1)
        dim11, dim22_q, dim33 = self.masc.get_var_size("Model.Weir.PtZus", num)
        print(dim11, dim22_q, dim33)
        cond = True
        for ii in range(nbq):
            self.masc.set("Model.Weir.PtQ", list_q[ii], i=num, j=ii, k=0)
            for jj in range(nbzav):
                if cond:
                    self.masc.set("Model.Weir.PtZds", list_zav[jj], i=num, j=jj, k=0)
                self.masc.set("Model.Weir.PtZus", list_zam[ii * nbzav + jj], i=num, j=ii, k=jj)
            cond = False
        self.write('fin.csv', nbq, nbzav)

    def write(self, name,nbq, nbzav):
        file= open(name,'w')
        file.write('q;zav;zam\n')
        for ii in range(nbq ):
            q = self.masc.get("Model.Weir.PtQ", i=0, j=ii, k=0)
            for jj in range(nbzav):
                zav = self.masc.get("Model.Weir.PtZds", i=0, j=jj, k=0)
                zam = self.masc.get("Model.Weir.PtZus", i=0, j=ii, k=jj)
                file.write('{};{};{}\n'.format(q,zav,zam))
        file.close()
        #
        # for ii, qq in enumerate(list_q):
        #     self.masc.set("Model.Weir.PtQ", qq, i=num, j=ii, k=0)
        #     for jj, zav in enumerate(list_zav):
        #         self.masc.set("Model.Weir.PtZds", zav, i=num, j=jj, k=0)
        #         self.masc.set("Model.Weir.PtZus", list_zam[ii * nbzav + jj], i=num, j=ii, k=jj)

    #

    def test_graph(self):
        nb_loi_sing = self.masc.get_var_size("Model.Weir.Name")
        print("nb loi",nb_loi_sing)
        numgraph =self.masc.get("Model.Weir.GraphNum", i=0)-1
        print(numgraph)
        name = self.masc.get("Model.Graph.Name", i=numgraph)
        type = self.masc.get("Model.Graph.Type", i=numgraph)
        print(name,type)
        if type==6:
            list_var=['Discharge','DownLevel','UpLevel']
            # recuperation de la taille
            dim1, dim2_q, dim3 = self.masc.get_var_size("Model.Graph.Discharge", 0)
            print(dim1, dim2_q, dim3 )
            # # # dim1 nb de loi , Vecteur 1D (dim2: nb val qui sont différente pour q, dim3 n'existe pas)
            # dim1, dim2_zav, dim3 = self.masc.get_var_size("Model.Graph.DownLevel", numgraph)
            # print(dim1, dim2_zav, dim3)
            # # #dim1 nb de loi, Vecteur 1D (dim2: nb val qui sont différente pour Zav, dim3 n'existe pas)
            # print("jjjj",dim2_q, dim2_zav)
            dim1, dim_q, dim_zav = self.masc.get_var_size("Model.Graph.UpLevel", numgraph)
            print(dim1, dim_q, dim_zav)
            # dim1 nb de loi , Vecteur 2D ( dim_q :nb val de q, dim_zav: nb val de Zav)
            q = self.masc.get("Model.Graph.Discharge", i=0, j=49,k=0)
            print(q)
            dict = self.dico_law()
            print(dict)
            self.masc.set_var_size("Model.Graph.Discharge", 3, 51, 0,index=1)
            self.masc.set_var_size("Model.Graph.UpLevel", 3, 51 ,41, index=1)
            # self.masc.get_var_size("Model.Graph.DownLevel",)

            dim1, dim_q, dim_zav = self.masc.get_var_size("Model.Graph.UpLevel", numgraph)
            dict=self.dico_law()
            print(dict)

            q2 = self.masc.get("Model.Graph.Discharge", i=0, j=50, k=0)
            print(q2)
            self.masc.set("Model.Graph.Discharge", 9999.0, i=0, j=50, k=0)
            q2 = self.masc.get("Model.Graph.Discharge", i=0, j=50, k=0)


            for a in range(41):
                self.masc.set("Model.Graph.UpLevel", 0.00099, i=0, j=50,k=a)
                zav = self.masc.get("Model.Graph.DownLevel", i=0, j=a, k=0)
                zam = self.masc.get("Model.Graph.UpLevel", i=0, j=50, k=a)
                print(q2,zav,zam,a)
    def dico_law(self):
        dic_loi = {}
        nb_loi_sing = self.masc.get_var_size("Model.Weir.Name")[0]
        # recupere le nombre singularite weir dont les structure
        for i in range(nb_loi_sing):
            numgraph = self.masc.get("Model.Weir.GraphNum", i=i) - 1
            var_graph = "Model.Graph."
            type = self.masc.get(var_graph + "Type", i=numgraph)
            name = self.masc.get(var_graph + "Name", i=numgraph)
            dic_loi[name] = {'id': i, 'type': type}
            if type == 6:
                list_var = ['Discharge', 'DownLevel', 'UpLevel']
                dim1, dim_q, dim_zav = self.masc.get_var_size(var_graph + "UpLevel", numgraph)
                dic_loi[name] = {'id': i, 'type': type, 'vars': list_var,
                                 'dim': [[dim_q], [dim_zav], [dim_q, dim_zav]]}
        return  dic_loi
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

