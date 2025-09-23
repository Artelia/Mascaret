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
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .MobilObjectMet1Widget import ClassMobilObjectMet1Widget
from .MobilObjectMet2Widget import ClassMobilObjectMet2Widget
from .MobilObjectMet3Widget import ClassMobilObjectMet3Widget

from ....ui.custom_control import _qt_is_checked

D_TYP_LINKS = {1: "Weir",
               2: "Channel",
               3: "Syphon",
               4: "Culvert"}


class ClassMobilObjectDialog(QDialog):
    def __init__(self, mgis, typ_obj):
        """
        Initialize the dialog for managing movable objects.
        :param mgis (object): Main GUI object
        :param typ_obj (str): Type of object ('weir' or 'link')
        """
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.typ_obj = typ_obj
        self.cur_obj = int()
        self.updating_info = False

        self.ui = loadUi(os.path.join(self.mgis.masplugPath,
                                      "ui/structures/ui_mobil_object.ui"),
                         self)

        if self.typ_obj == 'weir':
            self.setWindowTitle("Movable Weirs")
            self.lbl_table.setText("Active weirs (checked = movable)")
            self.obj_table = 'weirs'
            self.mob_table = 'weirs_mob_val'
            self.mob_table_id = 'id_weirs'
        elif self.typ_obj == 'link':
            self.setWindowTitle("Movable Links")
            self.lbl_table.setText("Active links (checked = movable)")
            self.obj_table = 'links'
            self.mob_table = 'links_mob_val'
            self.mob_table_id = 'id_links'

        self.wgt_m1 = ClassMobilObjectMet1Widget(self.mgis, self.typ_obj)
        self.ui.lay_met1.addWidget(self.wgt_m1)
        self.wgt_m1.widget_closed.connect(self.sub_widget_closed)

        self.wgt_m2 = ClassMobilObjectMet2Widget(self.mgis, self.typ_obj)
        self.ui.lay_met2.addWidget(self.wgt_m2)
        self.wgt_m2.widget_closed.connect(self.sub_widget_closed)

        self.wgt_m3 = ClassMobilObjectMet3Widget(self.mgis, self.typ_obj)
        self.ui.lay_met3.addWidget(self.wgt_m3)
        self.wgt_m3.widget_closed.connect(self.sub_widget_closed)

        self.ui.lst_obj.setSpacing(2)

        self.bg_method = QButtonGroup()
        self.bg_method.addButton(self.rb_met_0, 0)
        self.bg_method.addButton(self.rb_met_1, 1)
        self.bg_method.addButton(self.rb_met_2, 2)
        if self.typ_obj == 'link':
            self.bg_method.addButton(self.rb_met_3, 3)
        else:
            self.rb_met_3.hide()
        self.bg_method.buttonClicked.connect(self.cur_method_changed)

        self.ui.actionB_edit.triggered.connect(self.edit_object)

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface and fill the object list.
        :return: None
        """
        self.delete_useless_data()
        self.ui.main_sw.setCurrentIndex(0)
        self.fill_lst_objects()

    def sub_widget_closed(self):
        """
        Handle the closing of a sub-widget and return to the main view.
        :return: None
        """
        self.ui.main_sw.setCurrentIndex(0)

    def delete_useless_data(self):
        """
        Delete data in the mobility table that does not correspond to existing objects.
        :return: None
        """
        sql = "DELETE FROM {0}.{2} WHERE {3} NOT IN " \
              "(SELECT gid FROM {0}.{1})".format(self.mdb.SCHEMA,
                                                 self.obj_table,
                                                 self.mob_table,
                                                 self.mob_table_id)
        self.mdb.run_query(sql)

    def fill_lst_objects(self, def_id=None):
        """
        Fill the list of movable objects in the GUI.
        :param def_id (int): Optional, ID of the object to select by default
        :return: None
        """
        if QT_VERSION > 5:
            qt_check =Qt.CheckState.Checked
        else:
            qt_check = Qt.Checked
        mdl = QStandardItemModel()
        mdl.setColumnCount(1)

        self.ui.lst_obj.setModel(mdl)
        self.ui.lst_obj.setModelColumn(0)

        sql = "SELECT gid, name, type, active_mob FROM {0}.{1} WHERE active='t' " \
              "ORDER BY name".format(self.mdb.SCHEMA, self.obj_table)
        rows = self.mdb.run_query(sql, fetch=True)

        for r, row in enumerate(rows):
            obj_id, obj_name, obj_type, obj_act = row
            if self.typ_obj == 'link':
                obj_name = "{0} ({1})".format(obj_name, D_TYP_LINKS[obj_type])
            new_itm = QStandardItem(obj_name)
            new_itm.setData(obj_id, 32)
            new_itm.setEditable(False)
            new_itm.setCheckable(True)
            if obj_act:
                new_itm.setCheckState(qt_check)
            self.ui.lst_obj.model().setItem(r, new_itm)

        self.ui.lst_obj.model().itemChanged.connect(self.cur_object_status_changed)
        self.ui.lst_obj.selectionModel().selectionChanged.connect(self.cur_object_changed)

        self.cur_object_changed()
        if def_id:
            for r in range(self.ui.lst_obj.model().rowCount()):
                if self.ui.lst_obj.model().item(r, 0).data(0) == def_id:
                    self.ui.lst_obj.setCurrentIndex(self.ui.lst_obj.model().item(r, 0).index())
                    break

    def cur_object_changed(self):
        """
        Handle the event when the selected object changes.
        Updates the method selection and enables/disables controls accordingly.
        :return: None
        """
        self.updating_info = True
        self.ui.gbox_method.setEnabled(True)
        if self.ui.lst_obj.selectionModel().selectedIndexes():
            cur_idx = self.ui.lst_obj.selectionModel().selectedIndexes()[0]
            cur_itm = self.ui.lst_obj.model().itemFromIndex(cur_idx)
            self.cur_obj = cur_itm.data(32)

            rows = self.mdb.select(self.obj_table,
                                   where="gid = {0}".format(self.cur_obj),
                                   list_var=["method_mob"])

            cur_met = 0
            if rows:
                if rows["method_mob"][0] is not None and rows["method_mob"][0].strip() != 'None':
                    cur_met = int(rows["method_mob"][0])
                else:
                    cur_met = 0
            self.bg_method.button(cur_met).click()
        else:
            self.cur_obj = int()
            self.bg_method.button(0).click()
            self.ui.gbox_method.setEnabled(False)

        self.updating_info = False

    def cur_method_changed(self):
        """
        Handle the event when the selected mobility method changes.
        Updates the database and enables/disables the edit button.
        :return: None
        """
        cur_method = self.bg_method.checkedId()
        if cur_method == 0:
            self.bt_edit.setEnabled(False)
        else:
            self.bt_edit.setEnabled(True)

        if not self.updating_info:
            sql = "UPDATE {0}.{1} SET method_mob = '{2}' WHERE gid = {3}".format(self.mdb.SCHEMA,
                                                                                 self.obj_table,
                                                                                 cur_method,
                                                                                 self.cur_obj)
            self.mdb.run_query(sql)

    def cur_object_status_changed(self, itm):
        """
        Handle the event when the active/movable status of an object is changed.
        Updates the database accordingly.
        :param itm (QStandardItem): The item whose status changed
        :return: None
        """
        if _qt_is_checked(itm,check_level="full"):
            cur_val = 't'
        else:
            cur_val = 'f'

        sql = "UPDATE {0}.{1} SET active_mob = '{2}' WHERE gid = {3}".format(self.mdb.SCHEMA,
                                                                             self.obj_table,
                                                                             cur_val,
                                                                             itm.data(32))
        self.mdb.run_query(sql)

    def edit_object(self):
        """
        Open the appropriate widget for editing the selected object and method.
        :return: None
        """
        if self.cur_obj:
            cur_method = self.bg_method.checkedId()
            if cur_method == 1:
                self.ui.main_sw.setCurrentIndex(1)
                self.wgt_m1.load_object(self.cur_obj)
            if cur_method == 2:
                self.ui.main_sw.setCurrentIndex(2)
                self.wgt_m2.load_object(self.cur_obj)
            if cur_method == 3:
                self.ui.main_sw.setCurrentIndex(3)
                self.wgt_m3.load_object(self.cur_obj)
