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


from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
if int(qVersion()[0])<5:  #qt4
    from qgis.PyQt.QtGui import *
else: #qt5
    from qgis.PyQt.QtWidgets import *
import os

from qgis.core import *
from qgis.utils import *
from qgis.gui import *

from ..graphProfil_Dialog import CopySelectedCellsAction
from .. import function as fct
from .table_WQ import table_WQ
from .physical_param_dialog import physical_param_dialog
from .meteo_dialog import meteo_dialog
from .TracerInit_dialog import TracerInit_dialog

class Water_quality_dialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.kernel="steady"
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbwq=table_WQ(self.mgis,self.mdb)

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_water_quality.ui'), self)

        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.actionB_phy_param.triggered.connect(self.physicFile)
        self.ui.actionB_meteo_param.triggered.connect(self.meteoFile)

        self.ui.WaterQ.currentChanged.connect(self.onChangeTab)

        self.create_dico_para()
        self.initUI()
        # self.initUI_concent_init()


        self.modeleQualiteEau.currentIndexChanged['QString'].connect(self.modeleQualiteEauChanged)
        fct = lambda: self.delete_line(self.table_Tr,self.ui.nbTraceur)
        self.ui.actionB_delete_lineTabTracer.triggered.connect(fct)
        self.ui.actionB_add_lineTabTracer.triggered.connect(self.add_row_tr)


        self.optionConvectionChanged(self.ui.optionConvection.currentText())
        self.CalculDiffusionChanged( self.ui.optionCalculDiffusion.currentIndex())
        self.presenceTraceursChanged()

        self.ui.optionConvection.currentIndexChanged['QString'].connect(self.optionConvectionChanged)
        self.ui.ordreSchemaConvec.currentIndexChanged['QString'].connect(self.ordreSchemaConvecChanged)
        self.ui.optionCalculDiffusion.currentIndexChanged.connect(self.CalculDiffusionChanged)
        self.ui.presenceConcInit.stateChanged.connect(self.presenceTraceursChanged)

    # def initUI_concent_init(self):
    #     """initialisation of GUI of initial concentration"""
    #     self.initc=TracerInit_dialog(self)

    def presenceTraceursChanged(self):
        if self.ui.presenceConcInit.isChecked() ==True:
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

    def optionConvectionChanged(self, text):
            if  text == 'FV':
                self.ui.ordreSchemaConvec.setEnabled(True)
                self.ordreSchemaConvecChanged(self.ui.ordreSchemaConvec.currentText())

            else:
                self.ui.ordreSchemaConvec.setEnabled(False)
                if self.ui.ordreSchemaConvec.isEnabled:
                    self.ordreSchemaConvecChanged(None)

    def ordreSchemaConvecChanged(self,text ):
        if  text == '2':
            self.ui.LimitPente.setEnabled(True)
            self.ui.paramW.setEnabled(True)
            self.ui.label_LimitPente.setEnabled(True)
            self.ui.label_paramW.setEnabled(True)
        else:
            self.ui.LimitPente.setEnabled(False)
            self.ui.paramW.setEnabled(False)
            self.ui.label_LimitPente.setEnabled(False)
            self.ui.label_paramW.setEnabled(False)

    def CalculDiffusionChanged(self, text):
        if text == 0:
            self.ui.coeffDiffusion2.setEnabled(True)
        else:
            self.ui.coeffDiffusion2.setEnabled(False)

    def create_dico_para(self):
        self.par = {}
        # requete pour recuperer les parametres dans la base
        sql = "SELECT parametre, {0}, libelle, balise1, gui, gui_type FROM {1}.{2};"

        rows = self.mdb.run_query(sql.format("steady", self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, libelle,  balise1, gui, gui_type in rows:
            if gui_type== 'tracers':
                self.par[param] = {}
                try:
                    self.par[param]["val"] = eval(valeur.title())
                except:
                    self.par[param]["val"] = valeur

                self.par[param]["libelle"] = libelle
                self.par[param]["gui"] = fct.str2bool(gui)

    def initUI(self):
        self.modeleQualiteEauBox=self.ui.modeleQualiteEau
        self.presenceTraceursBox= self.ui.presenceTraceurs

        for param, info in self.par.items():
            if info['gui']:
                obj = getattr(self.ui, param)
                if isinstance(obj, QCheckBox):
                    obj.setChecked(info['val'])
                elif isinstance(obj, QDoubleSpinBox) or isinstance(obj, QSpinBox):
                    obj.setValue(info['val'])
                elif  isinstance(obj, QComboBox):
                    if param=='optionConvection':
                        val=info['val']-1
                    elif param=="modeleQualiteEau":
                        val = info['val']-1
                    elif param == 'optionCalculDiffusion':
                        val = info['val']-1
                    elif param=="LimitPente":
                        val = info['val']-1
                    elif param=='ordreSchemaConvec':
                        val = info['val'] - 1
                    obj.setCurrentIndex(val)
                else:
                    if self.mgis.DEBUG:
                        self.mgis.addInfo("param {}  obj {}  val {}".format(param, obj, info['val']))

        self.type=self.modeleQualiteEau.itemText(self.modeleQualiteEau.currentIndex())
        self.table_Tr = self.ui.tableWidget
        self.table_Tr.setColumnHidden(0, True)
        # self.table_Tr.addAction(CopySelectedCellsAction(self.table_Tr))
        self.initc = TracerInit_dialog(self)
        self.modeleQualiteEauChanged(self.type)

    def modeleQualiteEauChanged(self, text):
        self.type = text
        if self.type =='TRANSPORT_PUR':
            self.table_Tr.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.ui.b_add_lineTabTracer.show()
            self.ui.b_delete_lineTabTracer.show()
            self.b_phy_param.setEnabled(False)
        else:
            self.table_Tr.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ui.b_add_lineTabTracer.hide()
            self.ui.b_delete_lineTabTracer.hide()
            self.b_phy_param.setEnabled(True)
        self.initc.change_module(self.type)
        self.majTab()

    def majTab(self):
        condition = """type='{0}'""".format(self.type)
        # self.mgis.addInfo(condition)
        self.tab_tracer_name = self.mdb.select("tracer_name", condition)
        # print(self.tab_tracer_name)

        self.dicoTrac = []
        for t in range(len(self.tab_tracer_name["id"])):
            self.dicoTrac.append({"id": self.tab_tracer_name["id"][t],
                                  "sigle": self.tab_tracer_name["sigle"][t],
                                  "text": self.tab_tracer_name["text"][t],
                                  "convec": self.tab_tracer_name["convec"][t],
                                  "diffu": self.tab_tracer_name["diffu"][t]})

        self.columns = ['id', 'sigle', 'text']
        self.listeTab = []
        for c in self.columns:
            if self.tab_tracer_name[c] != [None] * len(self.tab_tracer_name[c]):
                self.listeTab.append(self.tab_tracer_name[c])

        # gui
        self.remplirTab_Tr(self.listeTab)
        self.ui.nbTraceur.setText('{}'.format( self.table_Tr.rowCount()))

    def remplirTab_Tr(self, liste):
        """ Fill items in the table """
        self.table_Tr.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.table_Tr.setItem(i, j, QTableWidgetItem(str(v)))

    def add_row_tr(self):
        self.table_Tr.setRowCount(self.table_Tr.rowCount() + 1)
        self.table_Tr.setItem(self.table_Tr.rowCount()-1, 0,QTableWidgetItem(''))
        self.table_Tr.setItem(self.table_Tr.rowCount()-1, 1, QTableWidgetItem('TRA{}'.format(self.table_Tr.rowCount())))
        self.table_Tr.setItem(self.table_Tr.rowCount()-1, 2, QTableWidgetItem('Tracer {}'.format(self.table_Tr.rowCount())))
        self.ui.nbTraceur.setText('{}'.format(self.table_Tr.rowCount()))
        self.dicoTrac.append({"id": '', "sigle": 'TRA{}'.format(self.table_Tr.rowCount()),
                              "text": 'Tracer{}'.format(self.table_Tr.rowCount()),
                              "convec": True, "diffu": True})


    def meteoFile(self):
        #ouvre et stock information fichier meteo
        # Temps ; Température de l’air ; Pression de vapeur saturante ; vitesse du vent ; nébulosité ; rayonnement solaire ; Pression atmosphérique

        self.mgis.addInfo('fct meteoFile')
        dlg = meteo_dialog(self.mgis)
        dlg.setWindowModality(2)
        dlg.exec_()

    def physicFile(self):
        # ouvre et stock tableau de physique
        dlg = physical_param_dialog(self.mgis, self.ui.modeleQualiteEau.currentText())
        dlg.setWindowModality(2)
        if dlg.exec_():
            mdl = dlg.ui.tab_param.model()
            for row in range(mdl.rowCount()):
                self.mdb.execute("UPDATE {0}.tracer_physic "
                                 "SET value = '{1}' "
                                 "WHERE id = {2}".format(self.mdb.SCHEMA, mdl.item(row, 3).data(0), mdl.item(row, 0).data(0)))

    def add_line(self):
        #add line au tableau
        self.mgis.addInfo('fct add_line')
        pass

    def delete_line(self,tableView,objnbTrac=None):
        #delete line
        self.mgis.addInfo('fct delete_line')
        if tableView.rowCount()>1:
            indices = tableView.selectedIndexes()
            for index in indices:
                    tableView.removeRow(index.row())
                    del self.dicoTrac[index.row()]
        if objnbTrac:
            objnbTrac.setText('{}'.format(tableView.rowCount()))

    def stockTable_Tr(self,table):
        if self.ui.WaterQ.currentIndex() == 2:
            self.onChangeTab(0)
        id_exist = None
        liste_id_cur = {}
        for row in range(table.rowCount()):
            if table.item(row, 0).text() != "":
                liste_id_cur[int(table.item(row, 0).text())] = row

        # delete transport_pur & laws_wq
        dico_trac = self.mdb.select('tracer_name', "type='TRANSPORT_PUR'")
        liste_id_bdd = sorted(dico_trac["id"])
        list_conv=[]
        list_dif=[]
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
                                 "WHERE id = {5}".format(self.mdb.SCHEMA, table.item(row, 1).text(), table.item(row, 2).text(),
                                                         self.dicoTrac[row]["convec"], self.dicoTrac[row]["diffu"], table.item(row, 0).text()))

        # add transport_pur & laws_wq
        idmax = self.mdb.selectMax("id", "tracer_name",'')
        for row in range(table.rowCount()):
            if table.item(row,0).text() == "":
                sql = """INSERT INTO {0}.tracer_name (id,type,sigle,text,convec,diffu ) VALUES
                                    ({1},'{2}','{3}','{4}',{5},{6})""".format(self.mdb.SCHEMA,idmax+1,
                                                                              self.type,
                                                                              table.item(row,1).text(),
                                                                              table.item(row, 2).text(),
                                                                              self.dicoTrac[row]["convec"],
                                                                              self.dicoTrac[row]["diffu"])
                self.mdb.run_query(sql)
                list_dif.append(self.dicoTrac[row]["diffu"])
                list_conv.append(self.dicoTrac[row]["convec"])

                if id_exist:
                    sql = """INSERT INTO {schem}.laws_wq (id_config, id_trac, time, value) 
                             SELECT id_config, {id_fin}, time, Null FROM {schem}.laws_wq WHERE id_trac = {id_src}""".format(schem=self.mdb.SCHEMA,
                                                                                                                            id_fin=idmax+1,
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
                          """.format(self.mdb.SCHEMA, txt_conv, 'convectionTraceurs')
        self.mdb.execute(sql)

        sql = """UPDATE {0}.parametres
                                SET (steady,unsteady,transcritical)=('{1}','{1}','{1}')
                                WHERE parametre='{2}'
                          """.format(self.mdb.SCHEMA, txt_dif, 'diffusionTraceurs')
        self.mdb.execute(sql)

    def update_conv_diff(self,table):
            if self.ui.WaterQ.currentIndex() == 2:
                self.onChangeTab(0)

            liste_id = {}
            for row in range(table.rowCount()):
                liste_id[int(table.item(row, 0).text())] = row

            list_conv=[]
            list_dif=[]
            for id in sorted(list(liste_id.keys())):
                row = liste_id[id]
                list_conv.append(self.dicoTrac[row]["convec"])
                list_dif.append(self.dicoTrac[row]["diffu"])
                self.mdb.execute("UPDATE {0}.tracer_name "
                                 "SET sigle = '{1}', text = '{2}', convec = {3}, diffu = {4} "
                                 "WHERE id = {5}".format(self.mdb.SCHEMA, table.item(row, 1).text(), table.item(row, 2).text(),
                                                         self.dicoTrac[row]["convec"], self.dicoTrac[row]["diffu"], table.item(row, 0).text()))

            txt_conv=''
            txt_dif = ''
            for conv,dif in zip(list_conv,list_dif):
                if conv:
                    txt_conv +='true '
                else:
                    txt_conv += 'false '
                if dif:
                    txt_dif += 'true '
                else:
                    txt_dif += 'false '

            sql = """   UPDATE {0}.parametres
                           SET (steady,unsteady,transcritical)=('{1}','{1}','{1}')
                           WHERE parametre='{2}'
                     """.format(self.mdb.SCHEMA,txt_conv,'convectionTraceurs')
            self.mdb.execute(sql)

            sql = """   UPDATE {0}.parametres
                           SET (steady,unsteady,transcritical)=('{1}','{1}','{1}')
                           WHERE parametre='{2}'
                     """.format(self.mdb.SCHEMA, txt_dif, 'diffusionTraceurs')
            self.mdb.execute(sql)

    def onChangeTab(self, idx):
        if idx != 0:
            self.table_conv_diff.setRowCount(0)
            for r in range(self.table_Tr.rowCount()):
                self.dicoTrac[r]["sigle"] = u"{}".format(self.table_Tr.item(r, 1).text())
                self.dicoTrac[r]["text"] = u"{}".format(self.table_Tr.item(r, 2).text())

                self.table_conv_diff.insertRow(r)
                self.table_conv_diff.setItem(r, 0, QTableWidgetItem(self.dicoTrac[r]["sigle"]))
                self.table_conv_diff.item(r, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table_conv_diff.setItem(r, 1, QTableWidgetItem(self.dicoTrac[r]["text"]))
                self.table_conv_diff.item(r, 1).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

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
                    cb = self.table_conv_diff.cellWidget(r, param[1]).layout().itemAt(0).widget()
                    self.dicoTrac[r][param[0]] = cb.isChecked()

    def acceptDialog(self):
        """Modification of the parameters in sql table"""
        for param, info in self.par.items():
            # print(info)
            if info['gui']:
                obj = getattr(self.ui, param)

                if isinstance(obj, QCheckBox) or isinstance(obj, QRadioButton):
                    val = obj.isChecked()
                elif isinstance(obj, QComboBox):
                    val = obj.currentIndex()
                    if param == 'optionConvection'or  param == "modeleQualiteEau" \
                            or param == 'optionCalculDiffusion' or param == "LimitPente"\
                            or param == 'ordreSchemaConvec':
                        val = val+1
                elif isinstance(obj, QLabel):
                    val=obj.text()
                    if param=='nbTraceur':
                        val = int(val)
                else:
                    val = obj.value()


                sql = """   UPDATE {0}.parametres
                               SET (steady,unsteady,transcritical)=('{1}','{1}','{1}') 
                               WHERE parametre='{2}'
                         """
                # print(sql.format(self.mdb.SCHEMA, val, param))
                self.mdb.run_query(sql.format(self.mdb.SCHEMA, val, param))

        # stock tracer
        if self.type == 'TRANSPORT_PUR':
            self.stockTable_Tr(self.table_Tr)
        else:
            self.update_conv_diff(self.table_Tr)


        #
        # liste = []
        # for var2 in self.variables:
        #     for param, obj in var:
        #         if var2==param:
        #             liste.append(str(obj.isChecked()).lower())
        #
        # sql = """   UPDATE {0}.parametres
        #                SET {1}='{2}'
        #                WHERE parametre='variablesStockees'
        #          """
        #
        # self.mdb.run_query(sql.format(self.mdb.SCHEMA, self.kernel, " ".join(liste)))



        self.close()
