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
import os
import collections
import numpy as np


class ClassMascStruct:
    def __init__(self, mgis):
        self.mgis = mgis
        self.mdb = mgis.mdb
        self.debug = mgis.DEBUG

    def get_list_law(self, id_config):
        """
        Get list law
        :param id_config: index of hydraulic structure
        :return: law list
        """
        liste_f = []

        where = "WHERE id_config={}".format(id_config)
        order = "ORDER BY id_var, id_order "
        sql = "SELECT {4} FROM {0}.{1} {2} {3};"
        tabval = self.mdb.run_query(
            sql.format(self.mdb.SCHEMA, "struct_laws", where, order,
                       'id_var , value'),
            fetch=True)
        if not tabval:
            return liste_f
        tabval = np.array(tabval)
        wow = tabval[:, 0]
        nbval = collections.Counter(wow)
        nb = int(nbval[0])

        for i in range(nb):
            list_tmp = []
            for j in nbval.keys():
                list_tmp.append(tabval[int(j) * nb + i, 1])
            liste_f.append(list_tmp)
        return liste_f

    def create_law(self, dossier, nom, typel, list_final):
        """
        Creation of law for Mascaret
        :param dossier: repertory
        :param nom: law name
        :param typel: type law
        :param list_final: data law
        :return:
        """

        if not list_final:
            return
        with open(os.path.join(dossier, nom + '.loi'), 'w') as fich:
            fich.write('# ' + nom + '\n')
            if typel == 6:
                fich.write('# Debit Cote_Aval Cote_Amont\n')
                chaine = ' {flowrate:.3f} {z_downstream:.3f} {z_upstream:.3f}\n'
                list_final = list(self.sort_law(list_final))

                for val in list_final:
                    dico = {'flowrate': val[0], 'z_downstream': val[1],
                            'z_upstream': val[2]}
                    fich.write(chaine.format(**dico))

    def sort_law(self, list_final):
        """
        sort the law
        :param list_final: law data
        :return:
        """
        info = np.array(list_final)
        # trie de la colonne 0 à 2
        info = info[
            info[:, 2].argsort()]  # First sort doesn't need to be stable.
        info = info[info[:, 1].argsort(kind='mergesort')]
        info = info[info[:, 0].argsort(kind='mergesort')]
        return info
