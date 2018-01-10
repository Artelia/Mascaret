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
        sql = "SELECT parametre, {0}, libelle, gui FROM {1}.{2};"

        rows = self.mdb.run_query(sql.format(self.kernel, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, libelle, gui in rows:

            # if param == 'variablesStockees':
            #     valeurs = map(eval, valeur.title().split())
            #     for var, val, lib in zip(self.variables, valeurs, self.libel_var):
            #         self.par[var] = {"val": val, "libelle": lib, "gui": True}
            #         # self.par[var] = {"val": val, "libelle": lib}
            # else:
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
            # self.mgis.addInfo("param {}  info {}".format(param, info))
            print param, info
            # if info['gui']:
            #     print param,info
                # obj = getattr(self.ui, param)
                # if isinstance(obj, QtGui.QCheckBox):
                #     obj.setChecked(info['val'])
                # elif isinstance(obj, QtGui.QDoubleSpinBox) or isinstance(obj, QtGui.QSpinBox):
                #     obj.setValue(info['val'])
                # elif obj==self.ui.evenement:
                #     self.ui.evenement.setChecked(info['val'])
                #     self.chEvent()
                # elif  isinstance(obj, QtGui.QComboBox):
                #     if param=='option':
                #         val=info['val']-1
                #     elif param=="compositionLits":
                #         val = info['val']
                #     elif param=="critereArret":
                #         val = info['val']-1
                #     elif param=='postProcesseur':
                #         val = info['val'] - 1
                #     obj.setCurrentIndex(val)
                # else:
                #     if self.mgis.DEBUG:
                #         self.mgis.addInfo("param {}  obj {}  val {}".format(param, obj, info['val']))
                #
                # if param in self.exclusion[self.kernel]:
                #     obj.hide()
                #     if isinstance(obj, QtGui.QSpinBox) or isinstance(obj, QtGui.QDoubleSpinBox)\
                #             or isinstance(obj, QtGui.QComboBox):
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
