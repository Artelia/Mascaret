# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
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
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *

from .ui.custom_control import ClassWarningBox

if int(qVersion()[0]) < 5:  # qt4

    from qgis.PyQt.QtGui import *
else:  # qt4
    from qgis.PyQt.QtWidgets import *


class ClassUpdatePk(QDialog):
    """
    Class allow to update pk of the selected tables
    """

    def __init__(self, mgis, iface):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_update_pk.ui'), self)
        self.box = ClassWarningBox()
        self.tree = None
        self.lst_tables_p = ['links', 'profiles']
        self.lst_tables_pt = ['flood_marks', 'weirs', 'hydraulic_head',
                              'lateral_inflows',
                              'lateral_weirs', 'tracer_lateral_inflows',
                              'outputs']
        self.lst_tables_b = ['branchs']
        self.liste_tables = self.lst_tables_b + self.lst_tables_p + self.lst_tables_pt
        # self.liste_tables =  self.lst_tables_p + self.lst_tables_pt
        self.parent = {}
        self.init_gui()

    def init_gui(self):
        """
              initialisation GUI
          """
        if len(self.liste_tables) > 0:
            self.tree = self.ui.treeWidget

            for table in self.liste_tables:
                self.parent[table] = QTreeWidgetItem(self.tree)
                self.parent[table].setText(0, table)
                self.parent[table].setFlags(self.parent[table].flags() |
                                            Qt.ItemIsTristate |
                                            Qt.ItemIsUserCheckable)
                self.parent[table].setCheckState(0, Qt.Checked)
        else:
            self.ui.b_delete.setDisabled(True)
        self.ui.b_delete.clicked.connect(self.lancement)
        self.ui.b_cancel.clicked.connect(self.annule)

    def lancement(self):
        """ Delete selection function"""
        selection = []
        for table in self.liste_tables:
            if self.parent[table].checkState(0) > 0:
                selection.append("{}".format(table))
        self.close()

        if not self.mdb.check_fct(["update_abscisse_profil", "abscisse_profil",
                                   "update_abscisse_point", "abscisse_point",
                                   "update_abscisse_branch",
                                   "abscisse_branch"]):
            self.mdb.add_fct_for_update_pk()

        n = len(selection)

        sql = ''
        for i, table in enumerate(selection):
            if table in self.lst_tables_pt:
                sql += "SELECT public.update_abscisse_point('{0}.{1}','{0}.{2}')" \
                       ";\n".format(self.mdb.SCHEMA, table, 'branchs')
            elif table in self.lst_tables_p:
                sql += "SELECT public.update_abscisse_profil('{0}.{1}','{0}.{2}')" \
                       ";\n".format(self.mdb.SCHEMA, table, 'branchs')
            elif table in self.lst_tables_b:
                sql += "SELECT public.update_abscisse_branch('{0}.{1}')" \
                       ";\n".format(self.mdb.SCHEMA, table)
        self.mdb.run_query(sql)
        if self.mgis.DEBUG:
            self.mgis.add_info("Update pk Done")

    def annule(self):
        """"Cancel """
        self.close()
