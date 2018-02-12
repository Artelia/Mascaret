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


from PyQt5.QtWidgets import *
from PyQt5.uic import *
import os


from qgis.core import *
from qgis.gui import *


from .Class_observation import Class_observation

class parameter_dialog(QDialog):
    def __init__(self,mgis, kernel):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb

        self.kernel=kernel

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/ui_parameter.ui'), self)

        self.initUI()

        self.ui.actionB_delete_law.triggered.connect(self.delObserv)
        self.ui.actionB_load_law.triggered.connect(self.importObserv)
        self.ui.actionEvenement.triggered.connect(self.chEvent)
        self.ui.actionRadioButton_law.triggered.connect(self.chEvent)
        self.ui.buttonBox_valid.accepted.connect(self.acceptDialog)
        self.ui.buttonBox_valid.rejected.connect(self.reject)
        fct = lambda: self.selectbox(self.ui.box_velocity)
        self.ui.actionbox_velocity.triggered.connect(fct)
        fct = lambda: self.selectbox(self.ui.box_stress)
        self.ui.actionbox_stress.triggered.connect(fct)
        fct = lambda: self.selectbox(self.ui.box_hydro)
        self.ui.actionbox_hydro.triggered.connect(fct)
        fct = lambda: self.selectbox(self.ui.box_time)
        self.ui.actionbox_time.triggered.connect(fct)
        fct = lambda: self.selectbox(self.ui.box_coef)
        self.ui.actionbox_coef.triggered.connect(fct)
        fct = lambda: self.selectbox(self.ui.box_WaterLevel)
        self.ui.actionbox_WaterLevel.triggered.connect(fct)

    def initUI(self):
        self.obs=Class_observation(self.mgis)
        self.combo =    {'code': {1: 'Steady',
                                  2: 'Unsteady',
                                  3: 'Transcritical'},
                         'compositionLits': {0: 'Aucun',
                                             1: 'Debord',
                                             2: 'fond/berge'},
                         'option': {1: 'Sections de calcul',
                                    2: 'couche Points de sortie'},
                         'postProcesseur': {1: 'Rubens',
                                            2: 'Opthyca'},
                         'critereArret': {1: 'Temps maximum',
                                          2: 'Nombre de pas de temps max',
                                          3: 'Cote maximale de controle'},
                         }

        self.libel_var=["Bottom elevation",
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
                          "Maximum energy"
                          ]


        self.variables=['ZREF',
                        'RGC',
                        'RDC',
                        'KMIN',
                        'KMAJ',
                        'Z',
                        'QMIN',
                        'QMAJ',
                        'S1',
                        'S2',
                        'FR',
                        'BETA',
                        'B1',
                        'B2',
                        'BS',
                        'P1',
                        'P2',
                        'RH1',
                        'RH2',
                        'VMIN',
                        'VMAJ',
                        'TAUF',
                        'Y',
                        'HMOY',
                        'Q2G',
                        'Q2D',
                        'SS',
                        'VOL',
                        'VOLS',
                        'CHAR',
                        'ZMAX',
                        'TZMA',
                        'VZMX',
                        'ZMIN',
                        'TZMI',
                        'VINF',
                        'VSUP',
                        'BMAX',
                        'TOND',
                        'QMAX',
                        'TQMA',
                        'EMAX'
                        ]
        #Q

        self.exclusion = {'steady': ['presenceCasiers',
                                     'elevCoteArrivFront',
                                     'calcOndeSubmersion',
                                     'froudeLimCondLim',
                                     'traitImplicitFrot',
                                     'implicitNoyauTrans',
                                     'optimisNoyauTrans',
                                     'perteChargeAutoElargissement',
                                     'termesNonHydrostatiques',
                                     'attenuationConvection',
                                     'pasTempsVar',
                                     'nbCourant',
                                     'repriseCalcul',
                                     'LigEauInit',
                                     'modeEntree',
                                     'fichLigEau',
                                     'formatFichLig',
                                     'initialisationAuto'],
                          'unsteady': ['elevCoteArrivFront',
                                       'calcOndeSubmersion',
                                       'froudeLimCondLim',
                                       'traitImplicitFrot',
                                       'implicitNoyauTrans',
                                       'optimisNoyauTrans',
                                       'perteChargeAutoElargissement',
                                       'termesNonHydrostatiques',
                                       'pasTempsVar',
                                       'nbCourant',
                                       'repriseCalcul'],
                          'transcritical': ['presenceCasiers',
                                            'attenuationConvection',
                                            'compositionLits',
                                            'repriseCalcul']

                          }
        self.create_dico_para()
        self.init_GUI()

    def create_dico_para(self):
        self.par = {}
        # requete pour recuperer les parametres dans la base
        sql = "SELECT parametre, {0}, libelle, gui FROM {1}.{2};"

        rows = self.mdb.run_query(sql.format(self.kernel, self.mdb.SCHEMA, "parametres"), fetch=True)

        for param, valeur, libelle, gui in rows:

            if param == 'variablesStockees':
                valeurs = list(map(eval, valeur.title().split()))
                for var, val, lib in zip(self.variables, valeurs,self.libel_var):
                    self.par[var] = {"val": val, "libelle": lib,"gui": True}
                    # self.par[var] = {"val": val, "libelle": lib}
            else:
                self.par[param] = {}
                try:
                    self.par[param]["val"] = eval(valeur.title())
                except:
                    self.par[param]["val"] = valeur

                self.par[param]["libelle"] = libelle
                self.par[param]["gui"] = self.str2bool(gui)

    def init_GUI(self):
        # pass
        for param, info in self.par.items():
            # self.mgis.addInfo("param {}  info {}".format(param, info))
            if info['gui']:
                obj = getattr(self.ui, param)
                if isinstance(obj, QCheckBox):
                    obj.setChecked(info['val'])
                elif isinstance(obj, QDoubleSpinBox) or isinstance(obj, QSpinBox):
                    obj.setValue(info['val'])
                elif obj==self.ui.evenement:
                    self.ui.evenement.setChecked(info['val'])
                    self.chEvent()
                elif  isinstance(obj, QComboBox):
                    if param=='option':
                        val=info['val']-1
                    elif param=="compositionLits":
                        val = info['val']
                    elif param=="critereArret":
                        val = info['val']-1
                    elif param=='postProcesseur':
                        val = info['val'] - 1
                    obj.setCurrentIndex(val)
                else:
                    if self.mgis.DEBUG:
                        self.mgis.addInfo("param {}  obj {}  val {}".format(param, obj, info['val']))

                if param in self.exclusion[self.kernel]:
                    obj.hide()
                    if isinstance(obj, QSpinBox) or isinstance(obj, QDoubleSpinBox)\
                            or isinstance(obj, QComboBox):
                        getattr(self.ui, 'label_'+param).hide()

    def importObserv(self):
        """load observation"""
        fileNamePath = QFileDialog.getOpenFileNames(None,
                                                    'File Selection',
                                                    self.mgis.masplugPath,
                                                    filter="CSV (*.csv);;File (*)")
        fileNamePath=fileNamePath[0]
        if self.obs.evtTOobs(fileNamePath):
            self.mgis.addInfo('Import is done.')
        else:
            self.mgis.addInfo('Import failed.')

    def delObserv(self):
        """delete observation """
        dico_code = self.mdb.selectDistinct("code",
                                           "Observations")
        ok=False
        if dico_code:
            # self.mgis.addInfo("{}".format(dico_code))
            event, ok = QInputDialog.getItem(None,
                                              'Event choice',
                                              'Event',
                                             dico_code['code'],0, False)


        if ok :
            where="code = '{0}'".format(event)
            self.mdb.delete("observations",where)
            if self.mgis.DEBUG:
                self.mgis.addInfo('{} is deleted.'.format(event))
        else:
            txt = "There aren't deleted observations ."
            self.mgis.windinfo(txt)
            self.mgis.addInfo( txt)

    def chEvent(self):
        "event change between law and evenment"
        event=self.ui.evenement.isChecked()

        if event:
            self.ui.label.setEnabled(True)
            self.ui.b_delete_law.setEnabled(True)
            self.ui.b_load_law.setEnabled(True)
        else:
            self.ui.label.setDisabled(True)
            self.ui.b_delete_law.setDisabled(True)
            self.ui.b_load_law.setDisabled(True)

        self.par['evenement']["val"] =event

    def str2bool(self,s):
        """string to bool"""
        if s=="True" or s=="TRUE":
            return True
        else:
            return False

    def selectbox(self,box):
        """ function allow to select  or not for checkBox"""

        for checkbox in box.findChildren(QCheckBox):
            checkbox.setChecked(box.isChecked())
            # checkbox.setEnabled(True)

    def acceptDialog(self):
        """Modification of the parameters in sql table"""
        var=[]
        for param, info in self.par.items():
            if info['gui']:
                obj = getattr(self.ui, param)
                if param in self.variables:
                    var.append((param, obj))
                    continue
                else:
                    if isinstance(obj, QCheckBox) or isinstance(obj, QRadioButton):
                        val = obj.isChecked()
                    elif isinstance(obj, QComboBox):
                        val = obj.currentIndex()
                        if param == 'option' or param == "critereArret" or param == 'postProcesseur':
                            val = val+1
                        elif param == "compositionLits":
                            val = val
                    else:
                        val = obj.value()


                    sql = """   UPDATE {0}.parametres
                                   SET {1}='{2}'
                                   WHERE parametre='{3}'
                             """
                    self.mdb.run_query(sql.format(self.mdb.SCHEMA, self.kernel, val, param))
    #
        liste = []
        for var2 in self.variables:
            for param, obj in var:
                if var2==param:
                    liste.append(str(obj.isChecked()).lower())

        sql = """   UPDATE {0}.parametres
                       SET {1}='{2}'
                       WHERE parametre='variablesStockees'
                 """

        self.mdb.run_query(sql.format(self.mdb.SCHEMA, self.kernel, " ".join(liste)))

        self.close()



