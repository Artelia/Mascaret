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
from datetime import timedelta

import numpy as np
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *

from .Function import del_accent
from .ui.custom_control import ClassWarningBox


class ClassNameModel(QDialog):
    """
    Class allow to export date of the runs
    """

    def __init__(self, mgis, run, scen, station, code):
        QDialog.__init__(self)
        self.ui = loadUi(os.path.join(mgis.masplugPath, "ui/name_model.ui"), self)
        self.bt_valid_name.clicked.connect(self.valid)
        self.new_name = '{}-{}'.format(run, scen)
        self.le_model.setText(self.new_name)
        self.lbl_cas.setText('Run: {}, Scenario: {}, Station: {}, code: {}'.format(run, scen, station, code))

    def valid(self):
        self.new_name = del_accent(self.le_model.text().strip())
        self.close()


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
        # for observation link between obs var and result var
        where = "var IN ('Z','Q')"
        dvar = self.mdb.select("results_var", where=where, order="id", list_var=['id', 'name', 'var'])
        self.typ2id = {}
        for idx, var in enumerate(dvar['var']):
            if var == 'Z':
                self.typ2id['H'] = {'id': dvar['id'][idx], 'name': dvar['name'][idx], 'var': var}
            else:
                self.typ2id[var] = {'id': dvar['id'][idx], 'name': dvar['name'][idx], 'var': var}
        # ****

        self.model_prof, self.id_to_name_prof = self.profil_mod()
        self.model_out, self.id_to_name_out = self.outputs_mod()
        self.model_sta, self.id_to_name_sta = self.stations_mod()
        self.model_scen, self.id_to_run = self.run_scenar_mod()

        self.model_var = None
        self.model_obs = None
        # default
        self.mod_lst = "Profiles"
        self.mod_lst_var = "CSV"
        self.lst_station.setModel(self.model_prof)
        self.rb_otamin.hide()

        self.rb_stations.toggled.connect(self.toggled_chang_lst)
        self.rb_output.toggled.connect(self.toggled_chang_lst)
        self.rb_prof.toggled.connect(self.toggled_chang_lst)

        self.rb_csv.toggled.connect(self.toggled_chang_format)

        self.rb_otamin.toggled.connect(self.toggled_chang_format)

        self.bt_clear_scenar.clicked.connect(self.clear_scen)
        self.bt_allscenar.clicked.connect(self.all_scen)
        self.bt_clear.clicked.connect(lambda x: self.clear_check(self.mod_lst))
        self.bt_allselect.clicked.connect(lambda x: self.allselect(self.mod_lst))
        self.bt_allselect_var.clicked.connect(self.allselect_var)

        self.bt_clear_var.clicked.connect(self.clear_var)
        self.bt_export.clicked.connect(self.validation)
        self.bt_cancel.clicked.connect(self.close)
        self.bt_valid.clicked.connect(self.fct_chang_stack)
        self.bt_cancel2.clicked.connect(self.fct_chang_stack)

        self.treev_scenar.setModel(self.model_scen)
        self.treev_scenar.expandAll()
        self.model_scen.itemChanged.connect(self.scen_item_changed)
        self.ch_ignor.stateChanged.connect(self.ignore_init)

    def clear_var(self):
        """
        Clear variable
        :return : None
        """
        model = self.mod_lst_var
        if model is None:
            return
        elif model == "CSV":
            obj = self.model_var
        elif model == "OTAMIN":
            obj = self.model_obs

        for row in range(obj.rowCount()):
            check_item = obj.item(row)
            if check_item.checkState() == Qt.Checked:
                check_item.setCheckState(False)

    def allselect_var(self):
        """
        Check variable
        :return : None
        """
        model = self.mod_lst_var
        if model is None:
            return
        elif model == "CSV":
            obj = self.model_var
        elif model == "OTAMIN":
            obj = self.model_obs

        for row in range(obj.rowCount()):
            check_item = obj.item(row)
            if check_item.checkState() != Qt.Checked:
                check_item.setCheckState(2)

    def toggled_chang_format(self):
        """
        Change list var
        :return : None
        """
        sender = self.sender()  # Obtenir le bouton radio émetteur du signal
        if sender.isChecked():
            txt = sender.text()
            self.change_lst_var(txt)

    def add_obs(self, model_var, row_to_name_var):
        """
        Creation of a QStandardItemModel for variable
                :return : (QStandardItemMode) model list,
                          (dict) dict[row]={'id': index variable, 'name' : name, 'var':short name},
                          (bool) exit status
        """
        lst_abs = self.get_name_abs_mod(self.mod_lst)
        lst_name = self.get_name_abs_mod(self.mod_lst, 'name')
        # if self.mod_lst in ("Profiles"):
        #     sql = "SELECT DISTINCT type FROM {0}.observations WHERE code " \
        #           "IN (SELECT code FROM {0}.outputs WHERE active " \
        #           "AND code is not NULL " \
        #           "AND abscissa IN ({1}));".format(self.mdb.SCHEMA,
        #                                            ','.join([str(abs) for abs in lst_abs]))
        # else:
        sql = "SELECT DISTINCT type FROM {0}.observations WHERE code " \
              "IN (SELECT code FROM {0}.outputs WHERE active " \
              "AND code is not NULL AND name IN ({2}) " \
              "AND abscissa IN ({1}));".format(self.mdb.SCHEMA,
                                               ','.join([str(abs) for abs in lst_abs]),
                                               ','.join(["'{}'".format(txt) for txt in lst_name]))
        dtmp = self.mdb.query_todico(sql)
        if dtmp is None:
            return model_var, row_to_name_var
        lastrow = len(row_to_name_var.keys())
        for id, var in enumerate(dtmp['type']):
            name = self.typ2id[var]['name']
            row_to_name_var[id + lastrow] = {"id": self.typ2id[var]['id'], 'name': name,
                                             'var': self.typ2id[var]['var'], 'obs': True}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            nname = '{} - obs - {}'.format(var, name)
            check_item = QStandardItem(nname)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_var.appendRow(check_item)
        return model_var, row_to_name_var

    def obs_mod(self):
        """
                Creation of a QStandardItemModel for variable
                :return : (QStandardItemMode) model list,
                          (dict) dict[row]={'id': index variable, 'name' : name, 'var':short name},
                          (bool) exit status
                """
        list_row = self.get_mod(self.mod_lst)
        list_run = self.get_list_runs()
        model_obs = QStandardItemModel()
        row_to_name_obs = {}
        exit_status = False
        if len(list_run) == 0 or len(list_row) == 0:
            return model_obs, row_to_name_obs
        where = "var IN ('Z','Q') AND id in (SELECT DISTINCT var FROM {}.results " \
                "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in list_run]))
        dtmp = self.mdb.select("results_var", where=where, order="id", list_var=['id', 'name', 'var'])
        if dtmp is None:
            dtmp = {'name': []}
        for id, name in enumerate(dtmp['name']):
            var = dtmp['var'][id]
            row_to_name_obs[id] = {"id": dtmp['id'][id], 'name': dtmp['name'][id], 'var': var, 'obs': False}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            nname = '{} - {}'.format(var, name)
            check_item = QStandardItem(nname)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_obs.appendRow(check_item)

        model_obs, row_to_name_obs = self.add_obs(model_obs, row_to_name_obs)

        return model_obs, row_to_name_obs

    def var_mod(self):
        """
        Creation of a QStandardItemModel for variable
        :return : (QStandardItemMode) model list,
                  (dict) dict[row]={'id': index variable, 'name' : name, 'var':short name},
                  (bool) exit status
        """
        list_row = self.get_mod(self.mod_lst)
        list_run = self.get_list_runs()
        model_var = QStandardItemModel()
        row_to_name_var = {}
        exit_status = False
        if len(list_run) == 0 or len(list_row) == 0:
            return model_var, row_to_name_var, exit_status
        where = "id in (SELECT DISTINCT var FROM {}.results " \
                "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in list_run]))
        dtmp = self.mdb.select("results_var", where=where, order="id", list_var=['id', 'name', 'var'])
        for id, name in enumerate(dtmp['name']):
            var = dtmp['var'][id]
            row_to_name_var[id] = {"id": dtmp['id'][id], 'name': dtmp['name'][id], 'var': var, 'obs': False}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            nname = '{} - {}'.format(var, name)
            check_item = QStandardItem(nname)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_var.appendRow(check_item)

        model_var, row_to_name_var = self.add_obs(model_var, row_to_name_var)

        exit_status = True
        return model_var, row_to_name_var, exit_status

    def get_mod(self, model):
        """
        Get the rows list for a model
        :param model: (object) QStandardItemModel
        :return : (list)  the rows list for a model
        """
        if model is None:
            return
        elif model == "Profiles":
            obj = self.model_prof
        elif model == "Outputs":
            obj = self.model_out
        elif model == "Stations":
            obj = self.model_sta
        elif model == 'CSV':
            obj = self.model_var
        elif model == 'OTAMIN':
            obj = self.model_obs

        list_row_mod = []
        for row in range(obj.rowCount()):
            check_item = obj.item(row)
            if check_item.checkState() == Qt.Checked:
                list_row_mod.append(row)
        return list_row_mod

    def get_name_abs_mod(self, model, var="abscissa"):
        """
        Get the rows list for a model
        :param model: (object) QStandardItemModel
        :return : (list)  the rows list for a model
        """
        if model is None:
            return
        elif model == "Profiles":
            obj = self.id_to_name_prof
        elif model == "Outputs":
            obj = self.id_to_name_out
        elif model == "Stations":
            obj = self.id_to_name_sta
        list_row_mod = self.get_mod(model)
        list_abs_mod = []
        for row in list_row_mod:
            list_abs_mod.append(obj[row][var])
        return list_abs_mod

    def ignore_init(self):
        """
        ignore _init run
        :return : None
        """
        lst_row = self.get_treeview_rows()
        old_row = self.id_to_run.copy()
        self.model_scen, self.id_to_run = self.run_scenar_mod(ignore_init=self.ch_ignor.checkState())
        new_row = [key for key, value in self.id_to_run.items() if any(
            key_old in old_row and value["id"] == old_row[key_old]['id'] for key_old in lst_row)]
        self.add_scen(new_row)
        self.model_scen.itemChanged.connect(self.scen_item_changed)
        self.treev_scenar.setModel(self.model_scen)
        self.treev_scenar.expandAll()

    def toggled_chang_lst(self):
        """
        Change list
        :return : None
        """
        sender = self.sender()  # Obtenir le bouton radio émetteur du signal
        if sender.isChecked():
            txt = sender.text()
            self.change_lst(txt)

    def change_lst(self, txt):
        """
        Change list of profiles, stations, or outputs
        :param txt: (str) list name
        :return : None
        """
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
        :return : None
        """
        val = self.stack_wgt.currentIndex()
        if val == 0:
            if self.mod_lst == "Stations":
                self.rb_otamin.show()
            else:
                self.rb_otamin.hide()
            self.model_var, self.row_to_name_var, exit_status = self.var_mod()
            if not exit_status:
                self.box.info('No data found.')
                return
            self.model_obs, self.row_to_name_obs = self.obs_mod()
            self.mod_lst_var = "CSV"
            self.lstv_data.setModel(self.model_var)
            self.rb_csv.setChecked(True)
            self.stack_wgt.setCurrentIndex(1)
        else:
            self.stack_wgt.setCurrentIndex(0)

    def scen_item_changed(self, item):
        """
        Change status item
        :param item :(QStandardItem) items
        :return : None
        """
        if item.isCheckable():
            if item.hasChildren():
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
        :param lst: (list) (run, scenario) list
        :return : None
        """
        for row in range(self.model_scen.rowCount()):
            cmpt = 0
            run_item = self.model_scen.item(row)
            nb_child = run_item.rowCount()
            for child_row in range(nb_child):
                if (row, child_row) in lst:
                    cmpt += 1
                    scen_item = run_item.child(child_row)
                    if scen_item.checkState() == Qt.Unchecked:
                        scen_item.setCheckState(2)
            if run_item.checkState() == Qt.Unchecked and cmpt == nb_child:
                run_item.setCheckState(2)

    def clear_scen(self):
        """
        Clear the scenario which are selected
        :return : None
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
        :param model: (object) QStandardItemModel
        :return : None
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
        :param model: (object) QStandardItemModel
        :return : None
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
        """
        Creation of a QStandardItemModel for the runs
        :param ignore_init :(bool) ignore run that ends with '_init'
        :return : (QStandardItemMode) model list  ,
                  (dict) dict[row]={'id': index runs},
        """
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
            dtmp = self.mdb.select("runs", where="run='{}'".format(run), list_var=['id', 'scenario'])
            cmpt = 0
            for id, scen in enumerate(dtmp['scenario']):
                if scen[-5:] == '_init' and ignore_init:
                    continue
                self.d_run2id[(run, scen)] = dtmp['id'][id]
                run_item = QStandardItem(scen)
                run_item.setCheckable(True)
                run_item.setCheckState(False)
                item.appendRow(run_item)
                id_to_run[(row, cmpt)] = {'id': dtmp['id'][id]}
                cmpt += 1
            treeModel.appendRow(item)
        return treeModel, id_to_run

    def profil_mod(self, lst_runs=[]):
        """
        Creation of a QStandardItemModel for the profiles
        :param lst_runs :(list) run list
        :return : (QStandardItemMode) model list  ,
                  (dict) dict[row]={"abscissa": pk, "gid": index geometry, "name": name}
        """
        if len(lst_runs) > 0:
            where = "active AND abscissa IN " \
                    "(SELECT DISTINCT pknum FROM {}.results " \
                    "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in lst_runs]))
        else:
            where = "active"
        dtmp = self.mdb.select("profiles", where=where, order="abscissa", list_var=['gid', 'name', 'abscissa'])

        id_to_name_prof = {}
        model_prof = QStandardItemModel()
        for id, name in enumerate(dtmp['name']):
            pk = dtmp['abscissa'][id]
            id_to_name_prof[id] = {"abscissa": pk, 'gid': dtmp['gid'][id], 'name': dtmp['name'][id]}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            nname = '{} - {}'.format(name, pk)
            check_item = QStandardItem(nname)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_prof.appendRow(check_item)
        return model_prof, id_to_name_prof

    def outputs_mod(self, lst_runs=[]):
        """   Creation of a QStandardItemModel for the outputs
        :param lst_runs :(list) runs list
        :return : (QStandardItemMode) model list  ,
                  (dict) dict[row]={"abscissa": pk, "gid": index geometry, "name": name}"""
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
            pk = dtmp['abscissa'][id]
            id_to_name_out[id] = {"abscissa": pk, 'gid': dtmp['gid'][id], 'name': dtmp['name'][id]}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            nname = '{} - {}'.format(name, pk)
            check_item = QStandardItem(nname)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_out.appendRow(check_item)
        return model_out, id_to_name_out

    def stations_mod(self, lst_runs=[]):
        """   Creation of a QStandardItemModel for the stations
        :param lst_runs :(list) runs list
        :return : (QStandardItemMode) model list  ,
                  (dict) dict[row]={"abscissa": pk, "gid": index geometry, "name": name, 'code': 'code station'}"""

        if len(lst_runs) > 0:
            where = "active AND code is not NULL AND abscissa IN " \
                    "(SELECT DISTINCT pknum FROM {}.results " \
                    "WHERE id_runs in ({}))".format(self.mdb.SCHEMA, ','.join([str(val) for val in lst_runs]))
        else:
            where = "active AND code is not NULL"

        dtmp = self.mdb.select("outputs", where=where, order="abscissa",
                               list_var=['gid', 'name', 'abscissa', 'code', 'zero'])

        id_to_name_sta = {}
        model_sta = QStandardItemModel()
        for id, name in enumerate(dtmp['name']):
            pk = dtmp['abscissa'][id]
            id_to_name_sta[id] = {"abscissa": pk, 'name': dtmp['name'][id],
                                  'gid': dtmp['gid'][id], 'code': dtmp['code'][id], 'zero': dtmp['zero'][id]}
            # Utilisation de QStandardItem pour représenter les cases à cocher
            nname = '{} - {}'.format(name, pk)
            check_item = QStandardItem(nname)
            check_item.setCheckable(True)
            check_item.setCheckState(False)  # Vous pouvez également utiliser Qt.Checked pour cocher par défaut
            check_item.setSelectable(False)  # Pour rendre seulement la case à cocher cliquable
            # Ajout de l'élément de texte et de la case à cocher au modèle
            model_sta.appendRow(check_item)
        return model_sta, id_to_name_sta

    def get_treeview(self):
        """
        Get the checked runs in treeView
        return:(list) (run,scenario) list
        """
        lst_rs = []
        for row in range(self.model_scen.rowCount()):
            run_item = self.model_scen.item(row)
            for child_row in range(run_item.rowCount()):
                scen_item = run_item.child(child_row)
                if scen_item.checkState() == Qt.Checked:
                    lst_rs.append((str(run_item.text()), str(scen_item.text())))
        return lst_rs

    def get_treeview_rows(self):
        """
        Get the checked rows in treeView
        return:(list) rows list
        """
        lst_rs = []
        for row in range(self.model_scen.rowCount()):
            run_item = self.model_scen.item(row)
            for child_row in range(run_item.rowCount()):
                scen_item = run_item.child(child_row)
                if scen_item.checkState() == Qt.Checked:
                    lst_rs.append((row, child_row))
        return lst_rs

    def get_list_runs(self):
        """
        Get the id_run
        return:(list)  list of id_run (run index)
        """
        liste = self.get_treeview()
        id_list = []
        for val in liste:
            id_list.append(self.d_run2id[val])
        return id_list

    def add_check(self, model, lst_rows):
        """
        Clear the profiles which are selected
        :param   lst_rows : (list) List of the rows
        :param model: (object) QStandardItemModel
        :return: None
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
            if row in lst_rows:
                check_item = obj.item(row)
                if check_item.checkState() == Qt.Unchecked:
                    check_item.setCheckState(2)

    def check_pk_val(self):
        """
        Manage the list of pk objects
        :return : None
        """
        lst = self.get_list_runs()
        # save the old checkboxes
        lst_pr = self.get_mod("Profiles")
        old_prof = self.id_to_name_prof.copy()
        lst_out = self.get_mod("Outputs")
        old_out = self.id_to_name_out.copy()
        lst_sta = self.get_mod("Stations")
        old_sta = self.id_to_name_sta.copy()
        # create new list
        self.model_prof, self.id_to_name_prof = self.profil_mod(lst)
        self.model_out, self.id_to_name_out = self.outputs_mod(lst)
        self.model_sta, self.id_to_name_sta = self.stations_mod(lst)
        self.change_lst(self.mod_lst)
        # find the checkboxes
        new_prof = [key for key, value in self.id_to_name_prof.items() if any(
            key_old in old_prof and value["abscissa"] == old_prof[key_old]["abscissa"] for key_old in lst_pr)]
        new_sta = [key for key, value in self.id_to_name_sta.items() if any(
            key_old in old_sta and value["abscissa"] == old_sta[key_old]["abscissa"]
            and value["name"] == old_out[key_old]["name"] for key_old in lst_sta)]
        new_out = [key for key, value in self.id_to_name_out.items() if any(
            key_old in old_out and value["abscissa"] == old_out[key_old]["abscissa"]
            and value["name"] == old_out[key_old]["name"] for key_old in lst_out)]
        # checks the new the checkboxes
        self.add_check("Profiles", new_prof)
        self.add_check("Outputs", new_out)
        self.add_check("Stations", new_sta)

    def change_lst_var(self, txt):
        """
        Change list of profiles, stations, or outputs
        :param txt: (str) list name
        :return : None
        """
        if txt == "CSV Format":
            self.mod_lst_var = "CSV"
            self.lstv_data.setModel(self.model_var)
        elif txt == "OTAMIN Format":
            self.mod_lst_var = "OTAMIN"
            self.lstv_data.setModel(QStandardItemModel())

    def validation(self):
        """
        TODO : Creation of the file
        """
        folder_name_path = QFileDialog.getExistingDirectory(self, "Choose a folder")

        lst_run = self.get_list_runs()
        lst_var = self.get_mod(self.mod_lst_var)
        lst_pr = self.get_mod(self.mod_lst)

        if self.mod_lst == "Profiles":
            dico_mod = self.id_to_name_prof
        elif self.mod_lst == "Outputs":
            dico_mod = self.id_to_name_out
        elif self.mod_lst == "Stations":
            dico_mod = self.id_to_name_sta

        if self.mod_lst_var == "CSV":
            dico_var = self.row_to_name_var
        elif self.mod_lst_var == "OTAMIN":
            dico_var = self.row_to_name_obs

        if self.mod_lst == "Stations" and self.mod_lst_var == "OTAMIN":
            self.otamin(dico_mod, lst_pr, lst_run, dico_var, folder_name_path)
        else:
            self.csv_file(dico_mod, dico_var, lst_var, lst_pr, lst_run, folder_name_path)

        self.close()


    def otamin(self, dico_mod, lst_pr, lst_run, dico_var, folder_name_path):
        """
        Create otamin file
        """
        self.mgis.add_info('Create files :')
        for id_run in lst_run:
            drun = self.mdb.select("runs", where="id='{}'".format(id_run), list_var=['run', 'scenario', 'init_date'])
            scen = drun['scenario'][0]
            run = drun['run'][0]
            init_date = drun['init_date'][0]
            if init_date is None:
                continue

            for stat in lst_pr:
                dlg = ClassNameModel(self.mgis, run, scen, dico_mod[stat]['name'], dico_mod[stat]['code'])
                dlg.exec_()
                nmodel = dlg.new_name
                dvar = self.mdb.select('results_var', where="var in ('ZREF', 'Z', 'Q')", list_var=['id', 'var', 'name'])
                dtyp = {}

                for row, id in enumerate(dvar['id']):
                    if dvar['var'][row] == 'Z':
                        dtyp['H'] = {'id': id, 'name': dvar['name'][row]}
                    else:
                        dtyp[dvar['var'][row]] = {'id': id, 'name': dvar['name'][row]}
                lstvar = []

                for row in dico_var.keys():
                    if dico_var[row]['var'] == 'Z' and 'H' not in lstvar and dico_var[row]['obs']:
                        lstvar.append('H')
                    elif dico_var[row]['var'] == 'Q' and 'Q' not in lstvar and dico_var[row]['obs']:
                        lstvar.append('Q')
                for var in lstvar:
                    where = "id_runs={} AND var={} AND pknum={}".format(id_run, dtyp[var]['id'],
                                                                        dico_mod[stat]['abscissa'])
                    dmodel = self.mdb.select("results", where=where, list_var=['time', 'val'])
                    dmodel['date'] = [init_date + timedelta(seconds=time_) for time_ in dmodel['time']]
                    if dmodel is None:
                        # self.box.info('No data found for the model.\n'
                        #               'The model {} and type {} is ignored.'.format(nmodel, var))
                        continue

                    if len(dmodel['val']) == 0:
                        # self.box.info('No data found for the model.\n'
                        #               'The model {} and type {} is ignored.'.format(nmodel, var))
                        continue

                    sql_query = (
                        "SELECT date, valeur FROM (SELECT code,type, UNNEST(date) as date, "
                        "UNNEST(valeur) as valeur FROM {4}.observations "
                        "WHERE code = '{0}' AND type='{3}') t "
                        " WHERE date>='{1}' AND date<='{2}' AND valeur > -999.9 "
                        "ORDER BY date".format(
                            dico_mod[stat]['code'], dmodel['date'][0], dmodel['date'][-1], var, self.mdb.SCHEMA
                        )
                    )
                    obs_val = self.mdb.query_todico(sql_query)
                    if len(obs_val['date']) == 0:
                        # self.box.info('No data found for the observation.\n'
                        #               'The code  {} and type {} is ignored.'.format(dico_mod[stat]['code'], var))
                        continue

                    date_x = np.array([dt.timestamp() for dt in dmodel['date']])
                    date_interp = np.array([dt.timestamp() for dt in obs_val['date']])

                    interp_val = np.interp(date_interp, date_x, dmodel['val'])

                    name_file = '{}_{}_000{}.csv'.format(dico_mod[stat]['code'][:8], nmodel[:10], var)

                    with open(os.path.join(folder_name_path, name_file), 'w') as filein:
                        filein.write('Stations;{}\n'.format(dico_mod[stat]['code']))
                        filein.write("Grandeurs;{}\n".format(var))
                        filein.write("Modeles;{}\n".format(nmodel))
                        filein.write("# JJ-MM-AAAA HH:MM;OBS;PREV\n")
                        for date_w, val_obs, val_mod in zip(obs_val['date'], obs_val['valeur'], interp_val):
                            if var == 'H':
                                filein.write('{};{};{}\n'.format(date_w.strftime("%m-%d-%Y %H:%M"),
                                                                 val_obs + dico_mod[stat]['zero'], val_mod))
                            else:
                                filein.write('{};{};{}\n'.format(date_w.strftime("%m-%d-%Y %H:%M"),
                                                                 val_obs, val_mod))
                    self.mgis.add_info('{} : Model: {}-{}, Code: {}, '
                                       'Type: {}, Output: {}'.format(name_file, run,
                                                                    scen,
                                                                    dico_mod[stat]['code'],
                                                                    var, dico_mod[stat]['name']))


    def csv_file(self,dico_mod, dico_var, lst_var, lst_pr, lst_run, folder_name_path) :
        """ Creat csv file"""
        #Run; Scenario; Variable , date; Valeur
        self.mgis.add_info('Create files :')
        for idx in lst_pr:
            nam_pk = dico_mod[idx]['name']
            abs =  dico_mod[idx]['abscissa']
            name_file = '{}-{}.csv'.format(nam_pk, abs)

            with open(os.path.join(folder_name_path, name_file), 'w') as filein:
                for id_run in lst_run:
                    drun = self.mdb.select("runs", where="id='{}'".format(id_run),
                                           list_var=['run', 'scenario', 'init_date'])
                    scen = drun['scenario'][0]
                    run = drun['run'][0]
                    init_date = drun['init_date'][0]
                    date_var = False
                    if init_date  is not None:
                        date_var = True

                    lst_obs_var = [dico_var[idx]['var'] for idx in lst_var if dico_var[idx]['obs']]
                    if  date_var :
                        filein.write("# Run; Scenario; Variable; Date; Values \n")
                    else:
                        filein.write("# Run; Scenario; Variable; Time; Values \n")
                    for row in  lst_var:
                        if not dico_var[row]['obs']:
                            where = "id_runs={} AND var={} AND pknum={}".format(id_run,  dico_var[row]['id'],
                                                                                abs)
                            dmodel = self.mdb.select("results", where=where, list_var=['time', 'val'])
                            if len(dmodel['time']) ==0 :
                                continue
                            for idt, tps in enumerate(dmodel['time']):
                                if  date_var :
                                    date_w = init_date + timedelta(seconds=tps)
                                    filein.write(
                                        '{};{};{};{};{} \n'.format(run, scen, dico_var[row]['var'],
                                                                date_w.strftime("%m-%d-%Y %H:%M"), dmodel['val'][idt]))
                                else:
                                    filein.write('{};{};{};{};{} \n'.format(run, scen, dico_var[row]['var'],
                                                                           tps, dmodel['val'][idt]))

                    if  date_var :
                        where = "id_runs={} AND pknum={}".format(id_run, abs)
                        lst_time = self.mdb.select_distinct('time', "results", where=where, ordre='time')

                        lst_date = [init_date + timedelta(seconds=time_) for time_ in lst_time['time']]

                        for var in lst_obs_var:
                            if var == 'Z':
                                var = 'H'
                            sql_query = (
                                "SELECT date, valeur FROM (SELECT code,type, UNNEST(date) as date, "
                                "UNNEST(valeur) as valeur FROM {3}.observations "
                                "WHERE code = (SELECT DISTINCT code FROM {3}.outputs WHERE active AND name='{4}' AND abscissa={5}) AND type='{2}') t "
                                " WHERE date>='{0}' AND date<='{1}' AND valeur > -999.9 "
                                "ORDER BY date".format(
                                   lst_date[0],lst_date[-1] , var, self.mdb.SCHEMA, nam_pk, abs
                                )
                            )
                           # print(sql_query)
                            obs_val = self.mdb.query_todico(sql_query)
                            if len(obs_val['valeur']) == 0:
                                continue

                            for idt, tps in enumerate(obs_val['date']):
                                filein.write(
                                    '{};{};{};{};{} \n'.format(run, scen, '{}-{}'.format(var,'obs'),
                                                              tps.strftime("%m-%d-%Y %H:%M"), obs_val['valeur'][idt]))
