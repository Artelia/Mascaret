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
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ClassTableStructure import ClassTableStructure, update_etat_struct

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence, \
        QIcon
    from qgis.PyQt.QtWidgets import *


class ClassStructureCreateDialog(QDialog):
    def __init__(self, mgis, id_profil):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure()
        self.type = ''
        self.name = ''
        self.comment = ''
        self.id_struct = -99

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_structure_create.ui'),
            self)
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)

        sql = "SELECT gid, name FROM {0}.profiles ORDER BY gid".format(
            self.mdb.SCHEMA)
        rows = self.mdb.run_query(sql, fetch=True)
        for row in rows:
            self.cb_profil.addItem(row[1], row[0])

        for id, struct in self.tbst.dico_struc_typ.items():
            self.cb_type.addItem(struct['name'], id)

        if id_profil:
            self.met = 'profil'
            self.id_profil = id_profil
            self.lbl_profil.hide()
            self.cb_profil.hide()
        else:
            self.met = 'struct'
            self.lbl_name.hide()
            self.txt_name.hide()
            self.lbl_comment.hide()
            self.txt_comment.hide()

        self.ui.adjustSize()

    def accept_page(self):
        # save Info
        self.type = self.cb_type.itemData(self.cb_type.currentIndex())
        self.name = self.txt_name.text()
        self.comment = self.txt_comment.text()

        if self.met == 'struct':
            self.id_profil = self.cb_profil.itemData(
                self.cb_profil.currentIndex())

        tab = {'x': [], 'z': []}
        where = "gid = '{0}' ".format(self.id_profil)
        feature = self.mdb.select('profiles', where=where,
                                  list_var=['x', 'z', 'abscissa', 'branchnum'])
        tab['x'] = [float(var) for var in feature["x"][0].split()]
        tab['z'] = [float(var) for var in feature["z"][0].split()]

        if len(tab['x']) == 0 or len(tab['z']) == 0:
            self.mgis.add_info("Check if the profile is saved.")
            return

        sql = "INSERT INTO {0}.struct_config (name, comment, type, id_prof_ori, active, abscissa, branchnum) " \
              "VALUES ('{1}', '{2}', '{3}', {4}, FALSE,{5} ,{6})".format(
            self.mdb.SCHEMA, self.name, self.comment, self.type, self.id_profil,
            feature['abscissa'][0], feature['branchnum'][0])
        self.mdb.run_query(sql)
        self.id_struct = self.mdb.select_max('id', 'struct_config')

        colonnes = ['id_config', 'id_order', 'x', 'z']
        xz = list(zip(tab['x'], tab['z']))
        values = []
        for order, (x, z) in enumerate(xz):
            values.append([self.id_struct, order, x, z])
        self.mdb.insert_res('profil_struct', values, colonnes)
        update_etat_struct(self.mdb)
        self.accept()

    def reject_page(self):
        # print('cancel')
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Structure")
        self.reject()
