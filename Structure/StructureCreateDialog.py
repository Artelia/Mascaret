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

from .ClassTableStructure import ClassTableStructure
from .ClassTmp import ClassTmp

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QIcon
    from qgis.PyQt.QtWidgets import *

class ClassStructureCreateDialog(QDialog):
    def __init__(self, mgis, id_profil):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbst = ClassTableStructure(self.mgis, self.mdb)
        self.struct = ClassTmp(self.mgis)

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_structure_create.ui'), self)
        self.b_ok.accepted.connect(self.accept_page)
        self.b_ok.rejected.connect(self.reject_page)

        sql = "SELECT gid, name FROM {0}.profiles ORDER BY gid".format(self.mdb.SCHEMA)
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
        if self.met == 'profil':
            self.type = self.cb_type.itemData(self.cb_type.currentIndex())
            self.name = self.txt_name.text()
            self.comment = self.txt_comment.text()
            sql = "INSERT INTO {0}.struct_config (name, comment, type, id_prof_ori, active) " \
                  "VALUES ('{1}', '{2}', '{3}', {4}, FALSE)".format(self.mdb.SCHEMA, self.name, self.comment,
                                                                    self.type, self.id_profil)
        elif self.met == 'struct':
            self.id_profil = self.cb_profil.itemData(self.cb_profil.currentIndex())
            self.type = self.cb_type.itemData(self.cb_type.currentIndex())
            sql = "INSERT INTO {0}.struct_config (type, id_prof_ori, active) " \
                  "VALUES ('{1}', {2}, FALSE)".format(self.mdb.SCHEMA, self.type, self.id_profil)

        self.mdb.run_query(sql)
        id_struct = self.mdb.select_max('id', 'struct_config')

        self.struct.copy_profil(self.id_profil, id_struct)
        self.accept()

    def reject_page(self):
        print('cancel')
        if self.mgis.DEBUG:
            self.mgis.add_info("Cancel of Structure")
        self.reject()
