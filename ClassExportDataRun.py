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

from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from .ui.custom_control import ClassWarningBox
from qgis.PyQt.QtWidgets import *


class ClassExportDataRun(QDialog):
    """
    Class allow to export date of the runs
    """

    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/export_data_run.ui"), self)
        self.box = ClassWarningBox()
        self.model_prof = None

        self.init_gui()

    def init_gui(self):
        """
        initialisation GUI
        """

        self.d_run2id = {}

        self.model_prof, self.id_to_name_prof = self.profil_mod()
        self.model_out, self.id_to_name_out = self.outputs_mod()
        self.model_sta, self.id_to_name_sta = self.stations_mod()
        self.model_scen, self.id_to_run = self.run_scenar_mod()

        self.model_var = None
        # default
        self.mod_lst = "Profiles"
        self.lst_station.setModel(self.model_prof)
        self.rb_otamin.hide()


        self.rb_stations.toggled.connect(self.toggled_chang_lst)
        self.rb_output.toggled.connect(self.toggled_chang_lst)
        self.rb_prof.toggled.connect(self.toggled_chang_lst)

        self.rb_csv.toggled.connect(self.toggled_chang_format)
        self.rb_otamin.toggled.connect(self.toggled_chang_format)

        self.bt_clear_scenar.clicked.connect(self.clear_scen)
        self.bt_allscenar.clicked.connect(self.all_scen)
        self.bt_clear.clicked.connect(lambda x : self.clear_check(self.mod_lst))
        self.bt_allselect.clicked.connect(lambda x : self.allselect(self.mod_lst))
        self.bt_export.clicked.connect(self.fct_chang_stack)
        self.bt_cancel.clicked.connect(self.close)
        self.bt_valid.clicked.connect(self.validation)
        self.bt_cancel2.clicked.connect(self.fct_chang_stack)

        self.treev_scenar.setModel(self.model_scen)
        self.treev_scenar.expandAll()
        self.model_scen.itemChanged.connect(self.scen_item_changed)
        self.ch_ignor.stateChanged.connect(self.ignore_init)

    def toggled_chang_format(self):
        """
        """
        # TODO
        # change list_var en fonction du format
        pass

    def var_mod(self):
        list_row = self.get_mod(self.mod_lst)
        list_run = self.get_list_runs()
        model_var = QStandardItemModel()
        row_to_name_out = {}
        exit_status = False
        if len(list_run) == 0 or len(list_row)== 0:
            return  model_var, row_to_name_out, exit_status
        where = "id in (SELECT DISTINCT var FROM {}.results " \
                "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in list_run]))
        dtmp = self.mdb.select("results_var", where=where, order="id", list_var=['id', 'name', 'var'],verbose =True)
        for id, name in enumerate(dtmp['name']):
            var = dtmp['var'][id]
            row_to_name_out[id] = {"id": dtmp['id'][id], 'name': dtmp['name'][id], 'var': var}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            nname = '{} - {}'.format(var, name)
            check_item = QStandardItem(nname)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_var.appendRow(check_item)
        exit_status = True
        return model_var, row_to_name_out, exit_status

    def get_mod(self, model):
        if model is None:
            return
        elif model == "Profiles":
            obj = self.model_prof
        elif model == "Outputs":
            obj = self.model_out
        elif model == "Stations":
            obj = self.model_sta
        list_row_mod = []
        for row in range(obj.rowCount()):
            check_item = obj.item(row)
            if check_item.checkState() == Qt.Checked:
                list_row_mod.append(row)
        return  list_row_mod

    def ignore_init(self):
        """
        ignore _init run
        """
        lst_row = self.get_treeview_rows()
        old_row  = self.id_to_run.copy()
        self.model_scen, self.id_to_run= self.run_scenar_mod(ignore_init=self.ch_ignor.checkState() )
        new_row = [key for key, value in self.id_to_run.items() if any(
            key_old in old_row and value["id"] == old_row[key_old]['id'] for key_old in lst_row)]
        self.add_scen(new_row)
        self.model_scen.itemChanged.connect(self.scen_item_changed)
        self.treev_scenar.setModel(self.model_scen)
        self.treev_scenar.expandAll()

    def toggled_chang_lst(self):
        """
        Change list
        """
        sender = self.sender()  # Obtenir le bouton radio émetteur du signal
        if sender.isChecked():
            txt = sender.text()
            self.change_lst(txt)

    def change_lst(self, txt):
        if txt == "Outputs":
            self.mod_lst = "Outputs"
            self.lst_station.setModel(self.model_out)
        elif txt == "Profiles":
            self.mod_lst = "Profiles"
            self.lst_station.setModel(self.model_prof)
        elif txt == "Stations":
            self.mod_lst = "Stations"
            self.lst_station.setModel(self.model_sta)

    def fct_chang_stack(self):
        """
        Go to the next page
        """
        val = self.stack_wgt.currentIndex()
        if val == 0:
            if self.mod_lst == "Stations":
                self.rb_otamin.show()
            else :
                self.rb_otamin.hide()
            self.model_var, self.row_to_name_out, exit_status = self.var_mod()
            if not exit_status:
                self.box.info('No data found.')
                return
            self.lstv_data.setModel(self.model_var)
            self.stack_wgt.setCurrentIndex(1)
        else:
            self.stack_wgt.setCurrentIndex(0)

    def scen_item_changed(self, item):
        """
        Change status item
        """
        if item.isCheckable():
            if item.hasChildren() :
                state = item.checkState()
                for row in range(item.rowCount()):
                    scen_item = item.child(row)
                    scen_item.setCheckState(state)
        self.check_pk_val()

    def all_scen(self):
        """
        Clear the scenario which are selected
        """
        for row in range(self.model_scen.rowCount()):
            run_item = self.model_scen.item(row)
            if run_item.checkState() == Qt.Unchecked:
                run_item.setCheckState(Qt.Checked)
            for child_row in range(run_item.rowCount()):
                scen_item = run_item.child(child_row)
                if scen_item.checkState() == Qt.Unchecked:
                    scen_item.setCheckState(Qt.Checked)

    def add_scen(self, lst):
        """
        Clear the scenario which are selected
        """
        for row in range(self.model_scen.rowCount()):
            cmpt = 0
            run_item = self.model_scen.item(row)
            nb_child = run_item.rowCount()
            for child_row in range(nb_child ):
                print((row, child_row) in lst)
                print(row, child_row, lst)
                if (row, child_row) in lst:
                    cmpt += 1
                    scen_item = run_item.child(child_row)
                    if scen_item.checkState() == Qt.Unchecked:
                        scen_item.setCheckState(2)
            if run_item.checkState() == Qt.Unchecked and cmpt == nb_child :
                run_item.setCheckState(2)

    def clear_scen(self):
        """
        Clear the scenario which are selected
        """
        for row in range(self.model_scen.rowCount()):
            run_item = self.model_scen.item(row)
            if run_item.checkState() == Qt.Checked:
                run_item.setCheckState(False)
            for child_row in range(run_item.rowCount()):
                scen_item = run_item.child(child_row)
                if scen_item.checkState() == Qt.Checked:
                    scen_item.setCheckState(False)

    def clear_check(self, model):
        """
        Clear the profiles which are selected
        """
        if model is None:
            return
        elif model == "Profiles":
            obj = self.model_prof
        elif model == "Outputs":
            obj = self.model_out
        elif model == "Stations":
            obj = self.model_sta

        for row in range(obj.rowCount()):
            check_item = obj.item(row)
            if check_item.checkState() == Qt.Checked:
                check_item.setCheckState(False)

    def allselect(self, model):
        """
        Check all profiles
        """
        if model is None:
            return
        elif model == "Profiles":
            obj = self.model_prof
        elif model == "Outputs":
            obj = self.model_out
        elif model == "Stations":
            obj = self.model_sta

        for row in range(obj.rowCount()):
            check_item = obj.item(row)
            if check_item.checkState() != Qt.Checked:
                check_item.setCheckState(2)

    def run_scenar_mod(self, ignore_init=False):
        self.d_run2id = {}
        treeModel = QStandardItemModel()
        dtmp = self.mdb.select_distinct('run', "runs")
        if dtmp is None:
            return treeModel
        lst_runs = dtmp['run']
        id_to_run = {}
        for row, run in enumerate(lst_runs):

            item = QStandardItem(run)
            item.setCheckable(True)
            item.setCheckState(False)
            dtmp = self.mdb.select("runs", where="run='{}'".format(run), list_var=['id','scenario'], verbose=True)
            cmpt = 0
            for id, scen in enumerate(dtmp['scenario']):
                if scen[-5:]=='_init' and ignore_init:
                    continue
                self.d_run2id[(run, scen)]= dtmp['id'][id]
                run_item = QStandardItem(scen)
                run_item.setCheckable(True)
                run_item.setCheckState(False)
                item.appendRow(run_item)
                id_to_run[(row,cmpt )] = {'id': dtmp['id'][id]}
                cmpt += 1
            treeModel.appendRow(item)
        return treeModel, id_to_run

    def profil_mod(self,lst_runs=[]):
        if len(lst_runs) >0:
            where = "active AND abscissa IN " \
                    "(SELECT DISTINCT pknum FROM {}.results " \
                    "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in lst_runs]))
        else:
            where = "active"
        dtmp = self.mdb.select("profiles", where=where, order="abscissa", list_var=['gid', 'name', 'abscissa'])

        id_to_name_prof = {}
        model_prof = QStandardItemModel()
        for id, name in enumerate(dtmp['name']):
            id_to_name_prof[id] = {"abscissa" : dtmp['abscissa'][id], 'gid':dtmp['gid'][id], 'name':dtmp['name'][id]}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            check_item = QStandardItem(name)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_prof.appendRow(check_item)
        return model_prof, id_to_name_prof

    def outputs_mod(self, lst_runs=[]):
        if len(lst_runs) > 0:
            where = "active AND abscissa IN " \
                    "(SELECT DISTINCT pknum FROM {}.results " \
                    "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in lst_runs]))
        else:
            where = "active"
        dtmp = self.mdb.select("outputs", where=where, order="abscissa", list_var=['gid', 'name', 'abscissa'])

        id_to_name_out = {}
        model_out = QStandardItemModel()
        for id, name in enumerate(dtmp['name']):
            id_to_name_out[id] = {"abscissa" : dtmp['abscissa'][id], 'gid':dtmp['gid'][id], 'name':dtmp['name'][id]}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            check_item = QStandardItem(name)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_out.appendRow(check_item)
        return model_out, id_to_name_out

    def stations_mod(self, lst_runs=[]):

        if len(lst_runs) > 0:
            where = "active AND code is not NULL AND abscissa IN " \
                    "(SELECT DISTINCT pknum FROM {}.results " \
                    "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in lst_runs]))
        else:
            where = "active AND code is not NULL"

        dtmp = self.mdb.select("outputs", where=where, order="abscissa", list_var=['gid', 'name', 'abscissa', 'code'])

        id_to_name_sta = {}
        model_sta = QStandardItemModel()
        for id, name in enumerate(dtmp['name']):
            id_to_name_sta[id] = {"abscissa" : dtmp['abscissa'][id], 'gid':dtmp['gid'][id], 'code':dtmp['code'][id]}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            check_item = QStandardItem(name)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_sta.appendRow(check_item)
        return  model_sta, id_to_name_sta

    def get_treeview(self):
        lst_rs = []
        for row in range(self.model_scen.rowCount()):
            run_item = self.model_scen.item(row)
            for child_row in range(run_item.rowCount()):
                scen_item = run_item.child(child_row)
                if scen_item.checkState() == Qt.Checked:
                    lst_rs.append((str(run_item.text()), str(scen_item.text())))
        return lst_rs

    def get_treeview_rows(self):
        lst_rs = []
        for row in range(self.model_scen.rowCount()):
            run_item = self.model_scen.item(row)
            for child_row in range(run_item.rowCount()):
                scen_item = run_item.child(child_row)
                if scen_item.checkState() == Qt.Checked:
                    lst_rs.append((row, child_row))
        return lst_rs

    def get_list_runs(self):
        liste = self.get_treeview()
        id_list = []
        for val in liste :
            id_list.append(self.d_run2id[val])
        return id_list

    def add_check(self, model, lst_rows):
        """
        Clear the profiles which are selected
        """
        if model is None:
            return
        elif model == "Profiles":
            obj = self.model_prof
        elif model == "Outputs":
            obj = self.model_out
        elif model == "Stations":
            obj = self.model_sta

        for row in range(obj.rowCount()):
            if row in lst_rows :
                check_item = obj.item(row)
                if check_item.checkState() == Qt.Unchecked:
                    check_item.setCheckState(2)

    def check_pk_val(self):
        lst = self.get_list_runs()

        lst_pr = self.get_mod("Profiles")
        old_prof = self.id_to_name_prof.copy()
        lst_out = self.get_mod("Outputs")
        old_out= self.id_to_name_out .copy()
        lst_sta =self.get_mod("Stations")
        old_sta = self.id_to_name_sta.copy()

        self.model_prof, self.id_to_name_prof = self.profil_mod(lst)
        self.model_out, self.id_to_name_out = self.outputs_mod(lst)
        self.model_sta, self.id_to_name_sta = self.stations_mod(lst)
        self.change_lst(self.mod_lst)


        new_prof = [key for key, value in self.id_to_name_prof.items() if any(
            key_old in old_prof and value["abscissa"] == old_prof[key_old]["abscissa"] for key_old in lst_pr)]
        new_sta = [key for key, value in self.id_to_name_sta.items() if any(
            key_old in old_sta and value["abscissa"] == old_sta[key_old]["abscissa"] for key_old in lst_sta)]
        new_out = [key for key, value in self.id_to_name_out.items() if any(
            key_old in old_out and value["abscissa"] == old_out[key_old]["abscissa"] for key_old in lst_out)]

        self.add_check("Profiles", new_prof)
        self.add_check("Outputs", new_out)
        self.add_check("Stations", new_sta)






    def validation(self):
        """
        TODO : Creation of the file
        """

        self.check_pk_val()
        pass



