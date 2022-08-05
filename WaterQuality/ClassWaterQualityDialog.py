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

from .ClassTableWQ import ClassTableWQ
from .ClassTracerInitDialog import ClassTracerInitDialog
from .MeteoDialog import ClassMeteoDialog
from .PhysicalParamDialog import ClassPhysicalParamDialog
from ..Function import str2bool
from ..ui.custom_control import ScientificDoubleSpinBox

if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *


class ClassWaterQualityDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.kernel = "steady"
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbwq = ClassTableWQ(self.mgis, self.mdb)

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_water_quality.ui'), self)

        self.par = {}
        self.modeleQualiteEauBox = None
        self.presenceTraceursBox = None
        self.type = ''
        self.table_Tr = None
        self.initc = None
        self.dicoTrac = []

        self.ui.buttonBox.accepted.connect(self.accept_dialog)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.actionB_phy_param.triggered.connect(self.physic_file)
        self.ui.actionB_meteo_param.triggered.connect(self.meteo_file)

        self.ui.WaterQ.currentChanged.connect(self.on_change_tab)

        self.create_dico_para()
        self.init_ui()

        self.modeleQualiteEau.currentIndexChanged['QString'].connect(
            self.modele_qualite_eau_changed)
        fct = lambda: self.delete_line(self.table_Tr, self.ui.nbTraceur)
        self.ui.actionB_delete_lineTabTracer.triggered.connect(fct)
        self.ui.actionB_add_lineTabTracer.triggered.connect(self.add_row_tr)

        self.option_convection_changed(self.ui.optionConvection.currentText())
        self.calcul_diffusion_changed(
            self.ui.optionCalculDiffusion.currentIndex())
        self.presence_traceurs_changed()

        self.ui.optionConvection.currentIndexChanged['QString'].connect(
            self.option_convection_changed)
        self.ui.ordreSchemaConvec.currentIndexChanged['QString'].connect(
            self.ordre_schema_convec_changed)
        self.ui.optionCalculDiffusion.currentIndexChanged.connect(
            self.calcul_diffusion_changed)
        self.ui.presenceConcInit.stateChanged.connect(
            self.presence_traceurs_changed)

    def presence_traceurs_changed(self):
        """ Enabled/Disenabled in function tracer presence parameter"""
        if self.ui.presenceConcInit.isChecked():
            self.ui.b_edit.setEnabled(True)
            self.ui.b_new.setEnabled(True)
            self.ui.b_delete.setEnabled(True)
            self.ui.b_add_line.setEnabled(True)
            self.ui.b_delete_line.setEnabled(True)
            self.ui.b_import.setEnabled(True)
        else:
            self.ui.b_edit.setEnabled(False)
            self.ui.b_new.setEnabled(False)
            self.ui.b_delete.setEnabled(False)
            self.ui.b_import.setEnabled(False)
            self.ui.b_add_line.setEnabled(False)
            self.ui.b_delete_line.setEnabled(False)

    def option_convection_changed(self, text):
        """function when convection option is changed"""
        if text == 'FV':
            self.ui.ordreSchemaConvec.setEnabled(True)
            self.ordre_schema_convec_changed(
                self.ui.ordreSchemaConvec.currentText())

        else:
            self.ui.ordreSchemaConvec.setEnabled(False)
            if self.ui.ordreSchemaConvec.isEnabled:
                self.ordre_schema_convec_changed(None)

    def ordre_schema_convec_changed(self, text):
        """change convection schema order"""
        if text == '2':
            self.ui.LimitPente.setEnabled(True)
            self.ui.paramW.setEnabled(True)
            self.ui.label_LimitPente.setEnabled(True)
            self.ui.label_paramW.setEnabled(True)
        else:
            self.ui.LimitPente.setEnabled(False)
            self.ui.paramW.setEnabled(False)
            self.ui.label_LimitPente.setEnabled(False)
            self.ui.label_paramW.setEnabled(False)

    def calcul_diffusion_changed(self, text):
        """ change state for diffusion"""
        if text == 0:
            self.ui.coeffDiffusion2.setEnabled(True)
        else:
            self.ui.coeffDiffusion2.setEnabled(False)

    def create_dico_para(self):
        """ creation of parameters dico"""
        self.par = {}
        # requete pour recuperer les parametres dans la base
        sql = "SELECT parametre, {0}, libelle, balise1, gui, gui_type FROM {1}.{2};"

        rows = self.mdb.run_query(
            sql.format("steady", self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, libelle, balise1, gui, gui_type in rows:
            if gui_type == 'tracers':
                self.par[param] = {}
                try:
                    self.par[param]["val"] = eval(valeur.title())
                except:
                    self.par[param]["val"] = valeur

                self.par[param]["libelle"] = libelle
                self.par[param]["gui"] = str2bool(gui)

    def init_ui(self):
        """initialisation GUI"""
        self.modeleQualiteEauBox = self.ui.modeleQualiteEau
        self.presenceTraceursBox = self.ui.presenceTraceurs

        for param, info in self.par.items():
            if info['gui']:
                obj = getattr(self.ui, param)
                if isinstance(obj, QCheckBox):
                    obj.setChecked(info['val'])
                elif isinstance(obj, QDoubleSpinBox) or isinstance(obj,
                                                                   QSpinBox):
                    if param == 'coeffDiffusion2':
                        self.ui.coeffDiffusion2 = ScientificDoubleSpinBox(
                            self.ui.tab_3)
                        self.ui.coeffDiffusion2.setValue(info['val'])
                        self.ui.gridLayout_5.addWidget(self.coeffDiffusion2, 4,
                                                       2, 1, 1)
                        self.coeffDiffusion2.setSingleStep(0.1)
                    elif param == 'paramW':
                        self.ui.paramW = ScientificDoubleSpinBox(self.ui.tab_3)
                        self.ui.paramW.setValue(info['val'])
                        self.ui.gridLayout_5.addWidget(self.paramW, 2, 3, 1, 1)
                        self.paramW.setSingleStep(0.1)
                    else:
                        obj.setValue(info['val'])
                elif isinstance(obj, QComboBox):
                    if param == 'optionConvection':
                        val = info['val'] - 2
                    elif param == "modeleQualiteEau":
                        val = info['val'] - 1
                    elif param == 'optionCalculDiffusion':
                        val = info['val'] - 1
                    elif param == "LimitPente":
                        if info['val']:
                            val = 0
                        else:
                            val = 1
                    elif param == 'ordreSchemaConvec':
                        val = info['val'] - 1
                    obj.setCurrentIndex(val)
                else:
                    if self.mgis.DEBUG:
                        pass
                        # self.mgis.add_info("param {}  obj {}  val {}".format(param, obj, info['val']))

        self.type = self.modeleQualiteEau.itemText(
            self.modeleQualiteEau.currentIndex())
        self.table_Tr = self.ui.tableWidget
        self.table_Tr.setColumnHidden(0, True)
        # self.table_Tr.addAction(CopySelectedCellsAction(self.table_Tr))
        self.initc = ClassTracerInitDialog(self)
        self.modele_qualite_eau_changed(self.type)

    def modele_qualite_eau_changed(self, text):
        """ function to change water quality model"""
        self.type = text
        self.b_meteo_param.setEnabled(False)
        if self.type == 'TRANSPORT_PUR':
            self.table_Tr.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.ui.b_add_lineTabTracer.show()
            self.ui.b_delete_lineTabTracer.show()
            self.b_phy_param.setEnabled(False)

        else:
            self.table_Tr.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ui.b_add_lineTabTracer.hide()
            self.ui.b_delete_lineTabTracer.hide()
            self.b_phy_param.setEnabled(True)
        if self.tbwq.dico_phy[self.type]['meteo']:
            self.b_meteo_param.setEnabled(True)
        self.initc.change_module(self.type)
        self.maj_tab()

    def maj_tab(self):
        """updating table"""
        condition = """type='{0}'""".format(self.type)
        # self.mgis.add_info(condition)
        tab_tracer_name = self.mdb.select("tracer_name", condition)

        self.dicoTrac = []
        for t in range(len(tab_tracer_name["id"])):
            self.dicoTrac.append({"id": tab_tracer_name["id"][t],
                                  "sigle": tab_tracer_name["sigle"][t],
                                  "text": tab_tracer_name["text"][t],
                                  "convec": tab_tracer_name["convec"][t],
                                  "diffu": tab_tracer_name["diffu"][t]})

        columns = ['id', 'sigle', 'text']
        liste_tab = []
        for c in columns:
            if tab_tracer_name[c] != [None] * len(tab_tracer_name[c]):
                liste_tab.append(tab_tracer_name[c])

        # gui
        self.remplir_tab__tr(liste_tab)
        self.ui.nbTraceur.setText('{}'.format(self.table_Tr.rowCount()))

    def remplir_tab__tr(self, liste):
        """ Fill items in the table """
        self.table_Tr.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.table_Tr.setItem(i, j, QTableWidgetItem(str(v)))

    def add_row_tr(self):
        """ add row"""
        self.table_Tr.setRowCount(self.table_Tr.rowCount() + 1)
        self.table_Tr.setItem(self.table_Tr.rowCount() - 1, 0,
                              QTableWidgetItem(''))
        self.table_Tr.setItem(self.table_Tr.rowCount() - 1, 1,
                              QTableWidgetItem(
                                  'TRA{}'.format(self.table_Tr.rowCount())))
        self.table_Tr.setItem(self.table_Tr.rowCount() - 1, 2,
                              QTableWidgetItem(
                                  'Tracer {}'.format(self.table_Tr.rowCount())))
        self.ui.nbTraceur.setText('{}'.format(self.table_Tr.rowCount()))
        self.dicoTrac.append(
            {"id": '', "sigle": 'TRA{}'.format(self.table_Tr.rowCount()),
             "text": 'Tracer{}'.format(self.table_Tr.rowCount()),
             "convec": True, "diffu": True})

    def meteo_file(self):
        """ Display meteo window"""
        # ouvre et stock information fichier meteo
        # Temps ; Température de l’air ; Pression de vapeur saturante ;
        # vitesse du vent ; nébulosité ; rayonnement solaire ; Pression atmosphérique

        # self.mgis.add_info('fct meteo_file')
        dlg = ClassMeteoDialog(self.mgis)
        dlg.setWindowModality(2)
        dlg.exec_()

    def physic_file(self):
        """ Display physical window"""
        # ouvre et stock tableau de physique
        dlg = ClassPhysicalParamDialog(self.mgis,
                                       self.ui.modeleQualiteEau.currentText())
        dlg.setWindowModality(2)
        if dlg.exec_():
            mdl = dlg.ui.tab_param.model()
            for row in range(mdl.rowCount()):
                self.mdb.execute("UPDATE {0}.tracer_physic "
                                 "SET value = '{1}' "
                                 "WHERE id = {2}".format(self.mdb.SCHEMA,
                                                         mdl.item(row, 3).data(
                                                             0),
                                                         mdl.item(row, 0).data(
                                                             0)))

    def delete_line(self, table_view, objnb_trac=None):
        """ delete line"""
        # delete line
        # self.mgis.add_info('fct delete_line')
        if table_view.rowCount() > 1:
            indices = table_view.selectedIndexes()
            row_to_del = []
            for index in indices:
                if index.row() not in row_to_del:
                    row_to_del.append(index.row())
            row_to_del = sorted(row_to_del, reverse=True)
            for row in row_to_del:
                table_view.removeRow(row)
                del self.dicoTrac[row]
        if objnb_trac:
            objnb_trac.setText('{}'.format(table_view.rowCount()))

    def stock_table_tr(self, table):
        """
        Insert table data in database
        """
        if self.ui.WaterQ.currentIndex() == 2:
            self.on_change_tab(0)
        id_exist = None
        liste_id_cur = {}
        for row in range(table.rowCount()):
            if table.item(row, 0).text() != "":
                liste_id_cur[int(table.item(row, 0).text())] = row

        # delete transport_pur & laws_wq
        dico_trac = self.mdb.select('tracer_name', "type='TRANSPORT_PUR'")
        liste_id_bdd = sorted(dico_trac["id"])
        list_conv = []
        list_dif = []
        for id in liste_id_bdd:
            if id not in liste_id_cur.keys():
                self.mdb.delete('tracer_name', "id = {}".format(id))
                self.mdb.delete('laws_wq', "id_trac = {}".format(id))
            else:
                if not id_exist:
                    id_exist = id
                row = liste_id_cur[id]
                list_dif.append(self.dicoTrac[row]["diffu"])
                list_conv.append(self.dicoTrac[row]["convec"])

                self.mdb.execute("UPDATE {0}.tracer_name "
                                 "SET sigle = '{1}', text = '{2}', convec = {3}, diffu = {4} "
                                 "WHERE id = {5}".format(self.mdb.SCHEMA,
                                                         table.item(row,
                                                                    1).text(),
                                                         table.item(row,
                                                                    2).text(),
                                                         self.dicoTrac[row][
                                                             "convec"],
                                                         self.dicoTrac[row][
                                                             "diffu"],
                                                         table.item(row,
                                                                    0).text()))

        # add transport_pur & laws_wq
        idmax = self.mdb.select_max("id", "tracer_name", '')
        for row in range(table.rowCount()):
            if table.item(row, 0).text() == "":
                sql = """INSERT INTO {0}.tracer_name (id,type,sigle,text,convec,diffu ) VALUES
                                    ({1},'{2}','{3}','{4}',{5},{6})""".format(
                    self.mdb.SCHEMA, idmax + 1,
                    self.type,
                    table.item(row, 1).text(),
                    table.item(row, 2).text(),
                    self.dicoTrac[row]["convec"],
                    self.dicoTrac[row]["diffu"])
                self.mdb.run_query(sql)
                list_dif.append(self.dicoTrac[row]["diffu"])
                list_conv.append(self.dicoTrac[row]["convec"])

                if id_exist:
                    sql = """INSERT INTO {schem}.laws_wq (id_config, id_trac, time, value) 
                             SELECT id_config, {id_fin}, time, Null FROM {schem}.laws_wq 
                             WHERE id_trac = {id_src}""".format(
                        schem=self.mdb.SCHEMA,
                        id_fin=idmax + 1,
                        id_src=id_exist)
                    self.mdb.run_query(sql)

                idmax += 1

        # # update parameter table
        txt_conv = ''
        txt_dif = ''

        for conv, dif in zip(list_conv, list_dif):
            if conv:
                txt_conv += 'true '
            else:
                txt_conv += 'false '
            if dif:
                txt_dif += 'true '
            else:
                txt_dif += 'false '

        sql = """UPDATE {0}.parametres
                                SET (steady,unsteady,transcritical)=('{1}','{1}','{1}')
                                WHERE parametre='{2}'
                          """.format(self.mdb.SCHEMA, txt_conv,
                                     'convectionTraceurs')
        self.mdb.execute(sql)

        sql = """UPDATE {0}.parametres
                                SET (steady,unsteady,transcritical)=('{1}','{1}','{1}')
                                WHERE parametre='{2}'
                          """.format(self.mdb.SCHEMA, txt_dif,
                                     'diffusionTraceurs')
        self.mdb.execute(sql)

    def update_conv_diff(self, table):
        """ updating convection and diffusion parameters in database"""
        if self.ui.WaterQ.currentIndex() == 2:
            self.on_change_tab(0)

        liste_id = {}
        for row in range(table.rowCount()):
            liste_id[int(table.item(row, 0).text())] = row

        list_conv = []
        list_dif = []
        for id in sorted(list(liste_id.keys())):
            row = liste_id[id]
            list_conv.append(self.dicoTrac[row]["convec"])
            list_dif.append(self.dicoTrac[row]["diffu"])
            self.mdb.execute("UPDATE {0}.tracer_name "
                             "SET sigle = '{1}', text = '{2}', convec = {3}, diffu = {4} "
                             "WHERE id = {5}".format(self.mdb.SCHEMA,
                                                     table.item(row, 1).text(),
                                                     table.item(row, 2).text(),
                                                     self.dicoTrac[row][
                                                         "convec"],
                                                     self.dicoTrac[row][
                                                         "diffu"],
                                                     table.item(row, 0).text()))

        txt_conv = ''
        txt_dif = ''
        for conv, dif in zip(list_conv, list_dif):
            if conv:
                txt_conv += 'true '
            else:
                txt_conv += 'false '
            if dif:
                txt_dif += 'true '
            else:
                txt_dif += 'false '
        sql = """   UPDATE {0}.parametres
                           SET (steady,unsteady,transcritical)=('{1}','{1}','{1}')
                           WHERE parametre='{2}'
                     """.format(self.mdb.SCHEMA, txt_conv, 'convectionTraceurs')
        self.mdb.execute(sql)

        sql = """   UPDATE {0}.parametres
                           SET (steady,unsteady,transcritical)=('{1}','{1}','{1}')
                           WHERE parametre='{2}'
                     """.format(self.mdb.SCHEMA, txt_dif, 'diffusionTraceurs')
        self.mdb.execute(sql)

    def on_change_tab(self, idx):
        """function when table state change """
        if idx != 0:
            self.table_conv_diff.setRowCount(0)
            for r in range(self.table_Tr.rowCount()):
                self.dicoTrac[r]["sigle"] = u"{}".format(
                    self.table_Tr.item(r, 1).text())
                self.dicoTrac[r]["text"] = u"{}".format(
                    self.table_Tr.item(r, 2).text())

                self.table_conv_diff.insertRow(r)
                self.table_conv_diff.setItem(r, 0, QTableWidgetItem(
                    self.dicoTrac[r]["sigle"]))
                self.table_conv_diff.item(r, 0).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table_conv_diff.setItem(r, 1, QTableWidgetItem(
                    self.dicoTrac[r]["text"]))
                self.table_conv_diff.item(r, 1).setFlags(
                    Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                for param in [["convec", 2], ["diffu", 3]]:
                    cb = QCheckBox()
                    if self.dicoTrac[r][param[0]]:
                        cb.setCheckState(2)
                    else:
                        cb.setCheckState(0)
                    wdg = QWidget()
                    lay = QHBoxLayout(wdg)
                    lay.setSpacing(0)
                    lay.setContentsMargins(0, 0, 0, 0)
                    lay.addWidget(cb)
                    lay.setAlignment(Qt.AlignCenter)
                    wdg.setLayout(lay)
                    self.table_conv_diff.setCellWidget(r, param[1], wdg)

        elif idx != 2:
            for r in range(self.table_conv_diff.rowCount()):
                for param in [["convec", 2], ["diffu", 3]]:
                    cb = self.table_conv_diff.cellWidget(r, param[
                        1]).layout().itemAt(0).widget()
                    self.dicoTrac[r][param[0]] = cb.isChecked()

    def accept_dialog(self):
        """Modification of the parameters in sql table"""
        for param, info in self.par.items():
            if info['gui']:
                obj = getattr(self.ui, param)

                if isinstance(obj, QCheckBox) or isinstance(obj, QRadioButton):
                    val = obj.isChecked()
                elif isinstance(obj, QComboBox):
                    val = obj.currentIndex()
                    if param == 'optionConvection' or param == "modeleQualiteEau" \
                            or param == 'optionCalculDiffusion' or param == "LimitPente" \
                            or param == 'ordreSchemaConvec':
                        if param == "LimitPente":
                            if val == 0 and self.ui.LimitPente.isEnabled():
                                val = 'True'
                            else:
                                val = 'False'
                        elif param == 'optionConvection':
                            val = val + 2

                        else:
                            val = val + 1
                elif isinstance(obj, QLabel):
                    val = obj.text()
                    if param == 'nbTraceur':
                        val = int(val)
                else:
                    if param == "paramW":
                        if not self.ui.paramW.isEnabled():
                            val = 0
                        else:
                            val = obj.value()
                    else:
                        val = obj.value()

                sql = """   UPDATE {0}.parametres
                               SET (steady,unsteady,transcritical)=('{1}','{1}','{1}') 
                               WHERE parametre='{2}'
                         """
                self.mdb.run_query(sql.format(self.mdb.SCHEMA, val, param))

        # stock tracer
        if self.type == 'TRANSPORT_PUR':
            self.stock_table_tr(self.table_Tr)
        else:
            self.update_conv_diff(self.table_Tr)
        # meteo
        if self.tbwq.dico_phy[self.type]['meteo']:
            order = "id"
            where = "active=true"
            meteo_trac = self.mdb.select('meteo_config', where, order)
            if not meteo_trac['id']:
                val = 'FALSE'
            else:
                val = 'TRUE'
            sql = """   UPDATE {0}.parametres
                              SET (steady,unsteady,transcritical)=('{1}','{1}','{1}') 
                              WHERE parametre='{2}'
                        """
            self.mdb.run_query(sql.format(self.mdb.SCHEMA, val, "fichmeteo"))

        self.close()
