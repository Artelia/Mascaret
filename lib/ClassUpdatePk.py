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
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *

from ..ui.custom_control import ClassWarningBox,_qt_is_checked

QT_VERSION = [int(v) for v in qVersion().split('.')][0]

class ClassUpdatePk(QDialog):
    """
    Class allow to update pk of the selected tables
    """

    def __init__(self, mgis, iface):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_update_pk.ui"), self)
        self.box = ClassWarningBox()
        self.tree = None
        self.lst_tables_p = ["links", "profiles"]
        self.lst_tables_pt = [
            "flood_marks",
            "weirs",
            "hydraulic_head",
            "lateral_inflows",
            "lateral_weirs",
            "tracer_lateral_inflows",
            "outputs"
        ]
        self.other = ["struct_config"]
        self.liste_tables = self.lst_tables_p + self.lst_tables_pt + self.other
        # self.liste_tables =  self.lst_tables_p + self.lst_tables_pt
        self.parent = {}
        self.init_gui()

    def init_gui(self):
        """
        initialisation GUI
        """
        if QT_VERSION > 5:
            qt_tris = Qt.ItemFlag.ItemIsAutoTristate
            qt_item_check = Qt.ItemFlag.ItemIsUserCheckable
            qt_ucheck = Qt.CheckState.Unchecked

        else:
            qt_tris = Qt.ItemIsAutoTristate
            qt_item_check = Qt.ItemIsUserCheckable
            qt_ucheck = Qt.Unchecked

        if len(self.liste_tables) > 0:
            self.tree = self.ui.treeWidget

            for table in self.liste_tables:
                self.parent[table] = QTreeWidgetItem(self.tree)
                self.parent[table].setText(0, table)
                self.parent[table].setFlags(self.parent[table].flags() | qt_tris | qt_item_check)
                self.parent[table].setCheckState(0,  qt_ucheck)
        else:
            self.ui.b_delete.setDisabled(True)
        self.ui.b_delete.clicked.connect(self.lancement)
        self.ui.b_cancel.clicked.connect(self.annule)

    def lancement(self):
        """Delete selection function"""
        selection = []
        for table in self.liste_tables:
            if _qt_is_checked(self.parent[table],check_level="any"):
                selection.append("{}".format(table))
        self.close()

        if not self.mdb.check_fct(
                ["update_abscisse_profil", "abscisse_profil", "update_abscisse_point", "abscisse_point"]
        ):
            self.mdb.add_fct_for_update_pk()

        n = len(selection)

        sql = ""
        for i, table in enumerate(selection):
            if table in self.lst_tables_pt:
                sql += "SELECT {0}.update_abscisse_point('{0}','{0}.{1}','{0}.{2}')" ";\n".format(
                    self.mdb.SCHEMA, table, "branchs"
                )
            elif table in self.lst_tables_p:
                sql += "SELECT {0}.update_abscisse_profil('{0}','{0}.{1}','{0}.{2}')" ";\n".format(
                    self.mdb.SCHEMA, table, "branchs"
                )
            elif table is "struct_config":
                feature = self.mdb.select(table, list_var=["id", "id_prof_ori"])
                if feature:
                    if len(feature['id']):
                        for idx, gid in enumerate(feature['id']):
                            where = "gid = '{0}' ".format(feature["id_prof_ori"][idx])
                            feat = self.mdb.select(
                                "profiles", where=where, list_var=["abscissa", "branchnum"]
                            )
                            if feat:
                                if len(feat["abscissa"]) > 0:
                                    sql += "UPDATE {0}.{1} SET abscissa={2}, branchnum={3} WHERE id={4};\n".format(
                                        self.mdb.SCHEMA,
                                        table,
                                        feat['abscissa'][0],
                                        feat['branchnum'][0],
                                        gid)
        self.mdb.run_query(sql)
        self.mgis.add_info("Update pk Done")

    def annule(self):
        """ "Cancel"""
        self.close()
