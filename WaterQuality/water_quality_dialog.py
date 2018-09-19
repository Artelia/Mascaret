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
from table_WQ import  table_WQ
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

        self.ui.actionB_add_line.triggered.connect(self.add_line)
        self.ui.actionB_delete_line.triggered.connect(self.delete_line)



        self.ui.actionB_phy_param.triggered.connect(self.physicFile)
        self.ui.actionB_meteo_param.triggered.connect(self.meteoFile)

        self.create_dico_para()
        self.initUI()

        self.modeleQualiteEau.currentIndexChanged['QString'].connect(self.modeleQualiteEauChanged)
        fct = lambda: self.delete_line(self.table_Tr,self.ui.nbTraceur)
        self.ui.actionB_delete_lineTabTracer.triggered.connect(fct)
        self.ui.actionB_add_lineTabTracer.triggered.connect(self.add_row_tr)

    def create_dico_para(self):
        self.par = {}
        # requete pour recuperer les parametres dans la base
        sql = "SELECT parametre, {0}, libelle, balise1, gui, gui_type FROM {1}.{2};"

        rows = self.mdb.run_query(sql.format("steady", self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, libelle,  balise1, gui, gui_type in rows:
            print(param, gui_type)
            if gui_type== 'tracers':
                print("rentrer  {}".format(param))
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
        # self.table_Tr.addAction(CopySelectedCellsAction(self.table_Tr))
        if self.type =='TRANSPORT_PUR':
            self.table_Tr.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.ui.b_add_lineTabTracer.show()
            self.ui.b_delete_lineTabTracer.show()
        else:
            self.table_Tr.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ui.b_add_lineTabTracer.hide()
            self.ui.b_delete_lineTabTracer.hide()
        self.majTab()

    def modeleQualiteEauChanged(self, text):
        self.type = text
        if self.type =='TRANSPORT_PUR':
            self.table_Tr.setEditTriggers(QAbstractItemView.AllEditTriggers)
            self.ui.b_add_lineTabTracer.show()
            self.ui.b_delete_lineTabTracer.show()
        else:
            self.table_Tr.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ui.b_add_lineTabTracer.hide()
            self.ui.b_delete_lineTabTracer.hide()
        self.majTab()

    def majTab(self):
        condition = """type='{0}'""".format(self.type)
        # self.mgis.addInfo(condition)
        self.tab_tracer_name = self.mdb.select("tracer_name", condition)
        self.columns=['sigle','text']
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
        self.table_Tr.setItem(self.table_Tr.rowCount()-1, 0, QTableWidgetItem('TRA{}'.format(self.table_Tr.rowCount())))
        self.table_Tr.setItem(self.table_Tr.rowCount()-1, 1, QTableWidgetItem('Tracer {}'.format(self.table_Tr.rowCount())))
        self.ui.nbTraceur.setText('{}'.format(self.table_Tr.rowCount()))

    def meteoFile(self):
        #ouvre et stock information fichier meteo
        self.mgis.addInfo('fct meteoFile')
        pass

    def physicFile(self):
        # ouvre et stock tableau de physique
        self.mgis.addInfo('fct physicFile')
        pass
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
        if objnbTrac:
            objnbTrac.setText('{}'.format(tableView.rowCount()))


    def stockTable_Tr(self,table):
        liste_stock=[]

        # delete transport_pur

        # add transport_pur
        condition = "type='TRANSPORT_PUR'"
        self.mdb.delete('tracer_name', condition)
        idmax = self.mdb.selectMax("id", "tracer_name",'')
        for row in range(table.rowCount()):
            sql = """INSERT INTO {0}.tracer_name (id,type,sigle,text,convec,diffu ) VALUES
                                ({6},'{1}','{2}','{3}',{4},{5})""".format(self.mdb.SCHEMA,
                                                                    self.type,
                                                                    table.item(row,0).text(),
                                                                        table.item(row, 1).text(),
                                                                        'true','true',idmax+1)
            idmax += 1
            self.mdb.run_query(sql)


    def acceptDialog(self):
        """Modification of the parameters in sql table"""
        for param, info in self.par.items():
            print(info)
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
                print(sql.format(self.mdb.SCHEMA, val, param))
                self.mdb.run_query(sql.format(self.mdb.SCHEMA, val, param))

        # stock tracer
        if self.type == 'TRANSPORT_PUR':
            self.stockTable_Tr(self.table_Tr)


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
