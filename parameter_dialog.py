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
from PyQt4 import QtCore, QtGui
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

from qgis.core import *
from qgis.gui import *

from ui.ui_parameter import Ui_Parameters
from Class_observation import Class_observation

class parameter_dialog(QtGui.QDialog):
    def __init__(self,mgis, kernel):
        QtGui.QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb

        self.kernel=kernel

        self.ui = Ui_Parameters()
        self.ui.setupUi(self)

        self.initUI()
        # nonfunctional

        self.ui.repriseCalcul.setEnabled(False)

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

        self.libel_var=[_translate("param_diag", "Bottom elevation", None),
                          _translate("param_diag", "Left bank water level", None),
                          _translate("param_diag", "Right bank water level", None),
                          _translate("param_diag", "Minor friction coefficient", None),
                          _translate("param_diag", "Major friction coefficient", None),
                          _translate("param_diag", "Water level", None),
                          _translate("param_diag", "Flow rate in minor river bed", None),
                          _translate("param_diag", "Flow rate in major river bed", None),
                          _translate("param_diag", "Wetted area of minor river bed", None),
                          _translate("param_diag", "Wetted area of major river bed", None),
                          _translate("param_diag", "Froude number", None),
                          _translate("param_diag", "Coefficient beta of Debord's formula", None),
                          _translate("param_diag", "Surface width of minor river bed", None),
                          _translate("param_diag", "Surface width of major river bed", None),
                          _translate("param_diag", "Surface width of storage area", None),
                          _translate("param_diag", "Wetted perimeter of minor river bed", None),
                          _translate("param_diag", "Wetted perimeter of major river bed", None),
                          _translate("param_diag", "Hydaulic radius of minor river bed", None),
                          _translate("param_diag", "Hydaulic radius of major river bed", None),
                          _translate("param_diag", "Velocity of minor river bed", None),
                          _translate("param_diag", "Velocity of major river bed", None),
                          _translate("param_diag", "Bottom shear stress", None),
                          _translate("param_diag", "Water depth", None),
                          _translate("param_diag", "Average water depth", None),
                          _translate("param_diag", "Flow rate in left major river bed", None),
                          _translate("param_diag", "Flow rate in right major river bed", None),
                          _translate("param_diag", "Wetted area of storage area", None),
                          _translate("param_diag", "Cumulative volume of the active river bed", None),
                          _translate("param_diag", "Cumulative volume of the storage area", None),
                          _translate("param_diag", "Hydraulic head", None),
                          _translate("param_diag", "Maximal water level", None),
                          _translate("param_diag", "Date of maximal water level", None),
                          _translate("param_diag", "Velocity for the maximal water level", None),
                          _translate("param_diag", "Minimal water level", None),
                          _translate("param_diag", "Date of minimal water level", None),
                          _translate("param_diag", "Minimum minor river bed velocity", None),
                          _translate("param_diag", "Maximum minor river bed velocity", None),
                          _translate("param_diag", "Maximum surface width", None),
                          _translate("param_diag", "Arrival time of the floodwave", None),
                          _translate("param_diag", "Maximum flow rate", None),
                          _translate("param_diag", "Date of maximum flow rate", None),
                          _translate("param_diag", "Maximum energy", None)
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
                                            'compositionLits']

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
                valeurs = map(eval, valeur.title().split())
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
                if isinstance(obj, QtGui.QCheckBox):
                    obj.setChecked(info['val'])
                elif isinstance(obj, QtGui.QDoubleSpinBox) or isinstance(obj, QtGui.QSpinBox):
                    obj.setValue(info['val'])
                elif obj==self.ui.evenement:
                    self.ui.evenement.setChecked(info['val'])
                    self.chEvent()
                elif  isinstance(obj, QtGui.QComboBox):
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
                    if isinstance(obj, QtGui.QSpinBox) or isinstance(obj, QtGui.QDoubleSpinBox)\
                            or isinstance(obj, QtGui.QComboBox):
                        getattr(self.ui, 'label_'+param).hide()

    def importObserv(self):
        """load observation"""
        fileNamePath = QtGui.QFileDialog.getOpenFileNames(None,
                                                    r'File Selection',
                                                    self.mgis.masplugPath,
                                                    filter="CSV (*.csv);;File (*)")
        if self.obs.evtTOobs(fileNamePath):
            self.mgis.addInfo(_translate("param_diag",'Import is done.',None))
        else:
            self.mgis.addInfo(_translate("param_diag",'Import failed.',None))

    def delObserv(self):
        """delete observation """
        dico_code = self.mdb.selectDistinct("code",
                                           "Observations")
        ok=False
        if dico_code:
            # self.mgis.addInfo("{}".format(dico_code))
            event, ok = QtGui.QInputDialog.getItem(None,
                                              'Event choice',
                                              'Event',
                                             dico_code['code'],0, False)


        if ok :
            where="code = '{0}'".format(event)
            self.mdb.delete("observations",where)
            if self.mgis.DEBUG:
                self.mgis.addInfo(_translate("param_diag",'{} is deleted.'.format(event),None))
        else:
            txt = _translate("param_diag", "There aren't deleted observations .", None)
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

        for checkbox in box.findChildren(QtGui.QCheckBox):
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
                    if isinstance(obj, QtGui.QCheckBox) or isinstance(obj, QtGui.QRadioButton):
                        val = obj.isChecked()
                    elif isinstance(obj, QtGui.QComboBox):
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



