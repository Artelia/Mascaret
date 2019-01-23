# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2017
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

class ClassTmp:
    def __init__(self, mgis):
        self.mgis = mgis
        self.mdb =  mgis.mdb
        self.id_config=0


    def get_param_g(self):
        """get general parameters"""
        list_recup=['eptab','cottab','firstw']
        param_g={}
        for info in list_recup:
            where="id_config = {0} AND var = '{1}' ".format(self.id_config ,info)
            rows=self.mdb.select('struct_param', where=where,list_var=['value'])
            if rows['value']:
                param_g[info]=rows['value'][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info('{} not specified in struct_param table'.format(info))
        # cas pont cadre
        param_g['cotpc']= param_g['cottab']- param_g['eptab']

        return param_g

    def get_param_elem(self,id_elem):
        """get general parameters"""
        list_recup = ['width']
        param_elem = {}
        for info in list_recup:
            where = "id_config = {0} AND id_elem= {1} AND var = '{2}' ".format(self.id_config, id_elem, info)
            rows = self.mdb.select('struct_elem_param', where=where, list_var=['value'])
            if rows['value']:
                param_elem[info] = rows['value'][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info('{} not specified in struct_elem_param table'.format(info))


        return param_elem

    def poly(self):
        # recuperation val général  pont cadre
        param_g=self.get_param_g()
        print(param_g)
        param_g['cotpc'] #point haut
        param_g['firstw']#point depart
        id_elem=0
        param_elem=self.get_param_elem(id_elem)
        print(param_elem)

        # where = "id_config = '{}'".format(self.cur_wq_mod)
        # order = "id"
        # result = self.mdb.select('tracer_physic', where, order)





    def copy_profil(self,gid,feature=None):
        """Profil copy"""

        colonnes=['id_config','id_prof_ori','order_','x','z']
        tab = {'x': [], 'z': []}
        if feature is None:
            where = "gid = '{0}' ".format(gid)
            feature=self.mdb.select('profiles',list_var=['x','z'])
            tab['x'] = [float(var) for var in feature["x"][0].split()]
            tab['z'] = [float(var) for var in feature["z"][0].split()]
        elif feature["x"] and feature["z"]:
            tab['x'] = [float(var) for var in feature["x"].split()]
            tab['z'] = [float(var) for var in feature["z"].split()]

        else:
            self.mgis.add_info("Check if the profile is saved.")
            return
        xz = list(zip(tab['x'], tab['z']))
        values=[]
        for order,(x,z) in enumerate(xz):
            values.append([self.id_config,gid,order,x,z])

        self.mdb.insert_res('profil_struct', values, colonnes)

