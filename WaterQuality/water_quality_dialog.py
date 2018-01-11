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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.utils import *
from qgis.gui import *

from ui_water_quality import Ui_Parameter_water_q
from .. import function as fct

class Water_quality_dialog(QDialog):
    def __init__(self, mgis,kernel):
        QDialog.__init__(self)
        self.kernel=kernel
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.ui = Ui_Parameter_water_q()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.acceptDialog)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.actionB_add_line.triggered.connect(self.add_line)
        self.ui.actionB_delete_line.triggered.connect(self.delete_line)

        self.ui.actionB_delete_lineTabTracer.triggered.connect(self.delete_line)

        self.ui.actionB_add_lineTabTracer.triggered.connect(self.add_line)

        self.ui.actionB_phy_param.triggered.connect(self.physicFile)
        self.ui.actionB_meteo_param.triggered.connect(self.meteoFile)

        self.create_dico_para()
        self.initUI()

    def create_dico_para(self):
        self.par = {}
        # requete pour recuperer les parametres dans la base
        sql = "SELECT parametre, {0}, libelle, balise1, gui FROM {1}.{2};"

        rows = self.mdb.run_query(sql.format(self.kernel, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, libelle,  balise1, gui in rows:

            if balise1== 'parametresTraceur':
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

                # if param in self.exclusion[self.kernel]:
                #     obj.hide()
                #     if isinstance(obj, QSpinBox) or isinstance(obj, QDoubleSpinBox)\
                #             or isinstance(obj, QComboBox):
                #         getattr(self.ui, 'label_'+param).hide()

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
    def delete_line(self):
        #delete line
        self.mgis.addInfo('fct delete_line')
        pass


    def acceptDialog(self):
        """Modification of the parameters in sql table"""
        var=[]
        for param, info in self.par.items():
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
                else:
                    val = obj.value()


                sql = """   UPDATE {0}.parametres
                               SET {1}='{2}'
                               WHERE parametre='{3}'
                         """
                self.mdb.run_query(sql.format(self.mdb.SCHEMA, self.kernel, val, param))
        #
        liste = []
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
