# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : Mascaret
Description          : Mascaret parameters
Date                 : septembre 2017

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

from qgis.PyQt.QtWidgets import *


class ClassParamExportDialog(QDialog):
    def __init__(self, mgis, kernel):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb

        self.kernel = kernel
        self.lig_eau_init = False
        self.event = False

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_export_file.ui"), self)

        self.combo = {}
        self.libel_var = []
        self.variables = []
        self.exclusion = {}
        self.par = {}
        self.dict_accept = {}
        self.new_par = {}
        self.complet = False

        self.init_ui()

        self.rb_init.clicked.connect(self.chg_init)
        self.rb_init_lig.clicked.connect(self.chg_init)


        fct = self.selb(self.ui.box_velocity)
        self.ui.box_velocity.clicked.connect(fct)
        fct = self.selb(self.ui.box_stress)
        self.ui.box_stress.clicked.connect(fct)
        fct = self.selb(self.ui.box_hydro)
        self.ui.box_hydro.clicked.connect(fct)
        fct = self.selb(self.ui.box_time)
        self.ui.box_time.clicked.connect(fct)
        fct = self.selb(self.ui.box_coef)
        self.ui.box_coef.clicked.connect(fct)
        fct = self.selb(self.ui.box_WaterLevel)
        self.ui.box_WaterLevel.clicked.connect(fct)
        self.ui.bt_export.clicked.connect(self.accept_dialog)
        self.bt_edit_param.clicked.connect(self.enable_tabwgt)
        self.bt_lig.clicked.connect(self.path_search_lig)
        self.bt_rep.clicked.connect(self.path_search)
        self.cb_init_run.currentIndexChanged.connect(self.fill_cb_init_cas)


    def init_ui(self):
        """initialisation GUI"""
        self.combo = {
            "code": {1: "Steady", 2: "Unsteady", 3: "Transcritical"},
            "option": {1: "Sections de calcul", 2: "couche Points de sortie",
                       3:"couche profils + amont/aval singularite"},
            "critereArret": {
                1: "Temps maximum",
                2: "Nombre de pas de temps max",
                3: "Cote maximale de controle",
            },
        }

        self.libel_var = [
            "Bottom elevation",
            "Left bank water level",
            "Right bank water level",
            "Minor friction coefficient",
            "Major friction coefficient",
            "Water level",
            "Flow rate in minor river bed",
            "Flow rate in major river bed",
            "Wetted area of minor river bed",
            "Wetted area of major river bed",
            "Froude number",
            "Coefficient beta of Debord's formula",
            "Surface width of minor river bed",
            "Surface width of major river bed",
            "Surface width of storage area",
            "Wetted perimeter of minor river bed",
            "Wetted perimeter of major river bed",
            "Hydaulic radius of minor river bed",
            "Hydaulic radius of major river bed",
            "Velocity of minor river bed",
            "Velocity of major river bed",
            "Bottom shear stress",
            "Water depth",
            "Average water depth",
            "Flow rate in left major river bed",
            "Flow rate in right major river bed",
            "Wetted area of storage area",
            "Cumulative volume of the active river bed",
            "Cumulative volume of the storage area",
            "Hydraulic head",
            "Maximal water level",
            "Date of maximal water level",
            "Velocity for the maximal water level",
            "Minimal water level",
            "Date of minimal water level",
            "Minimum minor river bed velocity",
            "Maximum minor river bed velocity",
            "Maximum surface width",
            "Arrival time of the floodwave",
            "Maximum flow rate",
            "Date of maximum flow rate",
            "Maximum energy",
            "Total wetted area",
            "Basin water level",
            "Basin area",
            "Basin volume",
            "Link flow rate",
            "Link velocity",
        ]

        self.variables = [
            "ZREF",
            "RGC",
            "RDC",
            "KMIN",
            "KMAJ",
            "Z",
            "QMIN",
            "QMAJ",
            "S1",
            "S2",
            "FR",
            "BETA",
            "B1",
            "B2",
            "BS",
            "P1",
            "P2",
            "RH1",
            "RH2",
            "VMIN",
            "VMAJ",
            "TAUF",
            "Y",
            "HMOY",
            "Q2G",
            "Q2D",
            "SS",
            "VOL",
            "VOLS",
            "CHAR",
            "ZMAX",
            "TZMA",
            "VZMX",
            "ZMIN",
            "TZMI",
            "VINF",
            "VSUP",
            "BMAX",
            "TOND",
            "QMAX",
            "TQMA",
            "EMAX",
            "ATOT",
            "ZCAS",
            "SURCAS",
            "VOLCAS",
            "QECH",
            "VECH",
        ]
        self.exclusion = {
            "steady": [
                "pasTempsVar",
                "nbCourant",
            ],
            "unsteady": [
                "pasTempsVar",
                "nbCourant",
            ],
        }
        self.create_dico_para()
        self.init_gui()
        self.enable_tabwgt()

    def create_dico_para(self):
        self.par = {}
        # requete pour recuperer les parametres dans la base
        sql = "SELECT parametre, {0}, libelle, gui, gui_type FROM {1}.{2};"

        rows = self.mdb.run_query(
            sql.format(self.kernel, self.mdb.SCHEMA, "parametres"), fetch=True
        )
        for param, valeur, libelle, gui, gui_type in rows:
            if gui_type == "parameters":
                if param == "variablesStockees":
                    self.par[param] = {}
                    try:
                        self.par[param]["val"] = eval(valeur.title())
                    except:
                        self.par[param]["val"] = valeur

                    # valeurs = list(map(eval, valeur.title().split()))
                    valeurs = []
                    for var1 in valeur.title().split():
                        valeurs.append(eval(var1))

                    for var, val, lib in zip(self.variables, valeurs, self.libel_var):
                        self.par[var] = {
                            "val": val,
                            "libelle": lib,
                            "gui": True,
                            "gui_type": "parameters",
                        }
                        # self.par[var] = {"val": val, "libelle": lib}
                else:
                    self.par[param] = {}
                    try:
                        self.par[param]["val"] = eval(valeur.title())
                    except:
                        self.par[param]["val"] = valeur

                    self.par[param]["libelle"] = libelle
                    self.par[param]["gui"] = self.str2bool(gui)
                    self.par[param]["gui_type"] = gui_type
        # Clear the useless parameters
        old_par = self.par.copy()
        self.lig_eau_init = self.par["LigEauInit"]
        self.event  = self.par["evenement"]

        for param, info in old_par.items():
            try :
                obj = getattr(self.ui, param)
            except AttributeError :
                del self.par[param]
                continue


    def init_gui(self):
        for param, info in self.par.items():
            # self.mgis.add_info("param {}  info {}".format(param, info))
            obj = getattr(self.ui, param)
            if isinstance(obj, QCheckBox):
                obj.setChecked(info["val"])
            elif isinstance(obj, QDoubleSpinBox) or isinstance(obj, QSpinBox):
                obj.setValue(info["val"])
            elif isinstance(obj, QComboBox):
                if param == "option":
                    val = info["val"] - 1
                elif param == "critereArret":
                    val = info["val"] - 1
                elif param == "postProcesseur":
                    val = info["val"] - 1
                obj.setCurrentIndex(val)
            else:
                self.mgis.add_info(
                    "param {}  obj {}  val {}".format(param, obj, info["val"]), dbg=True
                )
            if param in self.exclusion[self.kernel]:
                obj.hide()
                if (
                    isinstance(obj, QSpinBox)
                    or isinstance(obj, QDoubleSpinBox)
                    or isinstance(obj, QComboBox)
                ):
                    getattr(self.ui, "label_" + param).hide()
        # other parameters

        # if lig_eau
        lst_lig = [self.cb_init_run, self.cb_init_scen, self.rb_init, self.rb_init_lig, self.label_init_cas]
        if not self.lig_eau_init:
            self.hide_lstobj(lst_lig)
        else:
            self.show_lstobj(lst_lig)
            self.fill_cb_init_run()
            self.fill_cb_init_cas()
            self.rb_init.setChecked(True)
            self.chg_init()

        lst_ev = [self.cb_event, self.label_event]
        if not self.event:
            self.hide_lstobj(lst_ev)
        else:
            self.fill_cb_event()
            self.show_lstobj(lst_ev)

    def fill_cb_init_run(self):
        """
        Fill cb_init_run comboBox
        """
        dico_run = self.mdb.select_distinct("run", "runs")
        if dico_run != {} and dico_run is not None:
            liste_run = ["{}".format(v) for v in dico_run["run"]]
        else:
            liste_run = []
        self.cb_init_run.addItems(liste_run)

    def fill_cb_init_cas(self):
        """
        Fill cb_init_cas comboBox
        """
        self.cb_init_scen.clear()
        init_run = self.cb_init_run.currentText()
        condition = "run LIKE '{0}'".format(init_run)
        dico_scen = self.mdb.select_distinct("scenario", "runs", condition)
        liste_scen = ["{}".format(v) for v in dico_scen["scenario"]]
        self.cb_init_scen.addItems(liste_scen)

    def fill_cb_event(self):
        """
        Fill event comboBox
        """
        dict_scen_tmp = self.mdb.select("events", "run", "starttime")
        if len(dict_scen_tmp["name"]) == 0:
            QMessageBox.warning(
                self, "WARNING", "**** Warning: scenario not found  ***"
            )
            self.close()
        list_event = dict_scen_tmp["name"]
        self.cb_event.addItems(list_event)

    def chg_init(self):
        """
        change radio button
        """
        lst_init = [self.label_init_cas, self.cb_init_run, self.cb_init_scen]
        lst_lig = [self.label_init_lig, self.bt_lig, self.lbl_lig]
        if  self.rb_init.isChecked():
            self.show_lstobj(lst_init)
            self.hide_lstobj(lst_lig)
        else:
            self.hide_lstobj(lst_init)
            self.show_lstobj(lst_lig)


    def enable_tabwgt(self):
        """ Disable and Enbale tabWidget"""
        self.tab_widget.setEnabled(self.bt_edit_param.isChecked())


    def path_search_lig(self):
        """search path windows"""
        path, _ = QFileDialog.getOpenFileNames(self, "Choose a File", self.mgis.repProject,  "File (*.lig)",)
        if path:
            self.lbl_lig.setText(path[0])
        else:
            self.lbl_lig.setText('')

    def path_search(self):
        """search path windows"""
        path = QFileDialog.getExistingDirectory(self, "Choose a folder", self.mgis.repProject)
        if path:
            self.txt_rep.setText(path)
        else:
            self.txt_rep.setText('')

    def hide_lstobj(self,lst_obj):
        """Hide the PyQt object list
        :param lst_obj: Pyqt object list
        """
        for obj in lst_obj:
            obj.hide()

    def show_lstobj(self,lst_obj):
        """SHow the PyQt object list
        :param lst_obj: Pyqt object list
        """
        for obj in lst_obj:
            obj.show()

    @staticmethod
    def str2bool(s):
        """string to bool"""
        if "True" in s or "TRUE" in s:
            return True
        else:
            return False

    def selb(self, obj):
        """function selectbox"""
        return lambda: self.selectbox(obj)

    def selectbox(self, box):
        """function allow to select  or not for checkBox"""
        for checkbox in box.findChildren(QCheckBox):
            checkbox.setChecked(box.isChecked())

    def get_new_par(self):
        self.new_par = {}
        var = []
        for param, info in self.par.items():
            if info["gui"]:
                obj = getattr(self.ui, param)
                if param in self.variables:
                    var.append((param, obj))
                    continue
                else:
                    if isinstance(obj, QCheckBox) or isinstance(obj, QRadioButton):
                        val = obj.isChecked()
                    elif isinstance(obj, QComboBox):
                        val = obj.currentIndex()
                        if (
                                param == "option"
                                or param == "critereArret"
                                or param == "postProcesseur"
                        ):
                            val = val + 1
                    else:
                        val = obj.value()
                    self.new_par[param] = val
                    #
        liste = []
        for var2 in self.variables:
            for param, obj in var:
                if var2 == param:
                    liste.append(str(obj.isChecked()).lower())
        self.new_par['variablesStockees'] = " ".join(liste)

    def accept_dialog(self):
        """Modification of the parameters in sql table"""

        # if par["LigEauInit"] and not par["initialisationAuto"] and noyau != "steady":
        #     dict_scen = self.select_init_run_case(dict_scen)
        self.dict_accept = {}
        self.get_new_par()

        self.dict_accept['lig_eau_init'] = self.lig_eau_init
        self.dict_accept['event'] = self.event

        if self.lig_eau_init :
            if self.rb_init.isChecked():
                case = self.cb_init_run.currentText()
                scen =  self.cb_init_scen.currentText()
                id_run = self.mdb.run_query(
                    "SELECT id FROM {0}.runs "
                    "WHERE run = '{1}' "
                    "AND scenario = '{2}'".format(self.mdb.SCHEMA, case, scen),
                    fetch=True,
                )
                self.dict_accept['lig'] =  False
                self.dict_accept["id_run_init"] = [id_run[0][0]]

            else :
                self.dict_accept['lig'] = True
                self.dict_accept['path_copy'] = self.lbl_lig.text()

        if self.event:
            dict_scen_tmp = self.mdb.select("events", "run", "starttime")
            scen_event = self.cb_event.currentText()
            id = dict_scen_tmp["name"].index(scen_event)
            self.dict_accept['dict_scen']  = {
                "name": [dict_scen_tmp["name"][id]],
                "starttime": [dict_scen_tmp["starttime"][id]],
                "endtime": [dict_scen_tmp["endtime"][id]],
                "run": [dict_scen_tmp["run"][id]],
            }
        else:
            self.dict_accept['dict_scen'] = {"name": ["model"]}
        if not os.path.isdir(self.txt_rep.text()):
            QMessageBox.warning(
                self, "WARNING", "The save folder does not exist."
            )
            return
        self.dict_accept['path_rep'] = self.txt_rep.text()
        self.dict_accept['par'] = self.new_par
        self.complet = True
        self.close()
