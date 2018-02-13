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

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *

import json
from qgis.core import *
from qgis.utils import *
from qgis.gui import *

from .WaterQuality.TracerLaws_dialog import TracerLaws_dialog
from .WaterQuality.water_quality_dialog import Water_quality_dialog

from .graphProfil_Dialog import IdentifyFeatureTool
from .db.mas_database import MasDatabase
from .MNT_class import Worker
from .Class_Mascaret import Class_Mascaret
from .parameter_dialog import parameter_dialog

import math
import os

class MascPlugDialog(QMainWindow):

    OPT_GENERAL, OPT_mdb, OPT_DTM = range(3)

    def __init__(self, iface, parent=None):
        QMainWindow.__init__(self, parent)
        if QApplication.overrideCursor():
            QApplication.restoreOverrideCursor()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.masplugPath = os.path.dirname(__file__)
        self.ui = loadUi(os.path.join(self.masplugPath,'ui/MascPlug_dialog_base.ui'), self)
        #variables
        self.DEBUG = 1
        self.curConnName= None
        self.passwd = None
        self.mdb = None
        self.iface = iface

        # self.pathPostgres = self.masplugPath
        # emplacement objet sql
        self.dossierSQL = os.path.join(os.path.join(self.masplugPath,"db"), "sql")
        #style des couches
        self.dossierStyle = os.path.join(os.path.join(self.masplugPath,"db"), "style")
        self.repProject = None
        #variables liste of results
        self.variables = {}
        with open(os.path.join(self.masplugPath, 'variables.dat'), 'r') as fichier:
            for ligne in fichier:
                val = ligne.strip().replace('"', '').split(';')
                self.variables[val[1].lower()] = {'nom': val[0],
                                                  'code': val[1],
                                                  'unite': val[2],
                                                  'couleur': val[4]}

        # state list
        self.listeState = ['Steady', 'Unsteady', 'Transcritical unsteady']
        #kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]

        self.actions2Disable = []
        self.menus = self.ui.menubar.findChildren(QMenu)
        self.toolbars = self.findChildren(QToolBar)
        # self.mapRegistry = QgsProject.instance()

        #setting
        self.readSettings()
        # self.postgres_path=self.opts['mgis']['postgres_path']
        self.addInfo(self.postgres_path)
        self.updateDefaultCrs()



        # DB
        self.ui.actionRefresh_Database.triggered.connect(self.connChanged)
        self.ui.actionCreate_New_Model.triggered.connect(self.dbCreateModel)
        self.ui.actionDeleteModel.triggered.connect(self.dbDeleteModel)
        # #mascaret
        self.ui.actionLoad_Model.triggered.connect(self.dbLoad)

        # combos
        self.ui.crsWidget.crsChanged.connect(self.updateDefaultCrs)
        self.ui.connsCbo.activated.connect(self.connChanged)

        # Settings
        self.ui.actionOptions.triggered.connect(self.options)
        self.ui.actionRestore_Default_Options.triggered.connect(lambda: self.readSettings(defaults=True))

        self.ui.textEdit.append('----------------------------------------------------------------------------')
        #initialise

        # restore the window state
        # s = QSettings()
        # self.restoreGeometry(s.value("/Mascaret/mainWindow/geometry", QByteArray(), type=QByteArray))
        # self.restoreState(s.value("/Mascaret/mainWindow/windowState", QByteArray(), type=QByteArray))


        # # check if we should connect to previuosly used RDB
        if self.open_last_conn:
            self.connChanged(conn_name=self.opts['mdb']['last_conn'])
            self.addInfo('shema {}'.format(self.opts['mdb']['last_schema']))
            if self.open_last_schema :
                self.dbLoad(schemaInfo=self.opts['mdb']['last_schema'])
        else:
            self.connChanged()

        # restore settings
        self.readSettings()

        # set QGIS projection CRS as a default for MasPlug
        self.ui.crsWidget.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        self.updateDefaultCrs()

        # # disable some actions until a connection to river database is established
        if not self.mdb:
            self.disableActionsConnection()

    # Menu action
        # visu Mascaret plugin
        self.ui.actionCross_section.triggered.connect(self.mainGraph)
        self.ui.actionHydrogramme.triggered.connect(self.mainGraph)
        self.ui.actionCross_section_results.triggered.connect(self.mainGraph)

        # creatoin model
        self.ui.action_Extract_MNTfor_profile.triggered.connect(self.MntToProfil)
        self.ui.actionCreate_Geometry.triggered.connect(self.fct_createGeo)
        self.ui.actionCreate_xcas.triggered.connect(self.fct_createXcas)
        self.ui.actionParameters.triggered.connect(self.fct_parametres)
        self.ui.actionRun.triggered.connect(self.fct_run)
        self.ui.actionDelete_Run.triggered.connect(self.del_run)
        self.ui.actionExport_Run.triggered.connect(self.export_run)
        self.ui.actionExport_Model.triggered.connect(self.exportModel)
        self.ui.actionImport_Model.triggered.connect(self.importModel)
        # TODO
        self.ui.actionParameters_Water_Quality.triggered.connect(self.fct_parametersWQ)
        self.ui.actionTracer_Laws.triggered.connect(self.fct_tracer_laws)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionWebsite.triggered.connect(self.website)
        self.ui.actionWebsite.setEnabled(False)
        self.ui.actionAbout.setEnabled(False)




    def addInfo(self, text):
        self.ui.textEdit.append(text)

    def updateDefaultCrs(self):
        self.crs = self.ui.crsWidget.crs()
        if self.mdb:
            self.mdb.SRID = int(self.crs.postgisSrid())
        self.addInfo('\nCurrent projection is {0}'.format(self.crs.authid()))

    def disableAll(self):
        menusAlwaysOn = ['Help','Setting']
        for m in self.menus:
            if not m.title() in menusAlwaysOn:
                for a in m.findChildren(QAction):
                    a.setDisabled(True)
        for t in self.toolbars:
            for b in t.findChildren(QToolButton):
                b.setDisabled(True)

    def disableActionsConnection(self):
        """ cache les items avant la connection"""
        self. disableAll()
        self.list_menu=['Refresh Connections List']
        for t in self.ui.dbToolBar.findChildren(QToolButton):
            if t.text() in self.list_menu:
                t.setEnabled(True)
        self.actions2Disable = [self.ui.actionCreate_New_Model,
                                self.ui.actionLoad_Model,
                                self.ui.actionDeleteModel,
                                self.ui.actionExport_Model]
        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in self.actions2Disable:
            a.setDisabled(True)

    def disableActionsModel(self):

        self.disableAll()
        #bouton afficher
        self.list_menu = ['Refresh Connections List',
                          "Load Model",
                          "Create New Model",
                          "Delete Model",
                          "Import Model"]
        for t in self.ui.dbToolBar.findChildren(QToolButton):
            if t.text() in self.list_menu:
                t.setEnabled(True)

        #menu a cacher
        if  self.actions2Disable:
            for a in self.actions2Disable:
                a.setEnabled(True)
        else:
            pass

        self.actions2Disable=[self.ui.actionExport_Model]
        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in self.actions2Disable:
            a.setDisabled(True)

    def enableAllActions(self):
        for m in self.menus:
            for a in m.findChildren(QAction):
                a.setEnabled(True)
        for t in self.toolbars:
            for b in t.findChildren(QToolButton):
                b.setEnabled(True)
        for a in self.actions2Disable:
            a.setEnabled(True)

    def disableActions(self, list_actionBlock):
        """ cache les items de la liste d'action"""

        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in list_actionBlock:
            a.setDisabled(True)

    def enableActions(self, list_actionBlock):
        """ montre les items de la liste d'action"""
        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in list_actionBlock:
            a.setEnabled(True)

    def toggleDebugMode(self):
        if self.ui.actionDebugMode.isChecked():
            self.DEBUG = 1
        else:
            self.DEBUG = 0

    def closeEvent(self, e):
        # save the window state
        settings = QSettings()
        settings.setValue("/MasPlug/mainWindow/windowState", self.saveState())
        settings.setValue("/MasPlug/mainWindow/geometry", self.saveGeometry())
        settings.setValue("/MasPlug/mainWindow/flags", self.windowFlags())
        self.writeSettings()
        QMainWindow.closeEvent(self, e)

    def connChanged(self, conn_name='toto'):
        # close any existing connection to a MascPlug database
        if self.mdb:
            self.addInfo("Closing existing connection to {0}@{1} Mascaret database".format(self.mdb.dbname, self.mdb.host))
            self.mdb.disconnect_pg()
            self.mdb = None
        else:
            pass
        settings= QSettings()
        settings.beginGroup('/PostgreSQL/connections')
        connsNames = settings.childGroups()
        if conn_name in connsNames:
            self.curConnName = conn_name
        else:
            self.curConnName = self.ui.connsCbo.currentText()
        self.addInfo('{}'.format(self.curConnName))
        self.ui.connsCbo.clear()
        self.ui.connsCbo.addItem('')
        for conn in connsNames:
            self.ui.connsCbo.addItem(conn)
        try:
            i = connsNames.index(self.curConnName) + 1
        except ValueError:
            i = 0
        self.ui.connsCbo.setCurrentIndex(i)
        connName = self.ui.connsCbo.currentText()
        settings.endGroup()

        settings.beginGroup('/PostgreSQL/connections/{0}'.format(connName))
        self.host = settings.value('host')
        self.port = settings.value('port')
        self.database = settings.value('database')
        self.user = settings.value('username')
        self.passwd = settings.value('password')
        settings.endGroup()
        # create a new connection to masPlug database
        self.mdb = MasDatabase(self, self.database, self.host, self.port, self.user, self.passwd)
        self.mdb.SRID = int(self.crs.postgisSrid())
        msg=self.mdb.connect_pg()
        self.addInfo('Created connection to mascaret database: {0}@{1}'.format(self.mdb.dbname, self.mdb.host))
        self.mdb.last_conn = connName
        if 'Error:' in msg:
            self.disableActionsConnection()
        else:
            self.disableActionsModel()

    def dbCreateModel(self):
        """Model creation"""
        modelName, ok = QInputDialog.getText(self, 'New Model', 'New Model name:')

        if ok:
            self.mdb.SCHEMA=modelName
            self.mdb.create_model(self.dossierSQL)
            self.mdb.last_schema = self.mdb.SCHEMA
            self.enableAllActions()
        else:

            self.addInfo('Creating new model cancelled.')

    def dbDeleteModel(self):
        """ Model delete"""

        liste = self.mdb.listeModels()
        model, ok = QInputDialog.getItem(None,
                                          'Project choice',
                                          'Project',
                                          liste,0, False)
        if ok:
            self.mdb.drop_model(model, cascade=True)

        else:
            self.addInfo('Droping Model cancelled.')

    def dbLoad(self,schemaInfo=None):
        """ load model"""
        try:
            self.repProject = os.path.dirname(
                QgsProject.instance().fileName())
        except:
            self.repProject = None

        if schemaInfo:
            (model,ok)=(schemaInfo,True)
        else:
            liste = self.mdb.listeModels()
            model, ok = QInputDialog.getItem(None,
                                              'Model Choice',
                                              'Model',
                                              liste,0, False)
        if ok:
            self.mdb.SCHEMA = model
            self.mdb.loadModel()
            self.mdb.last_schema = self.mdb.SCHEMA
            self.enableAllActions()

        else:
            self.addInfo('Droping Model cancelled.')


###**************************************
## Menus Functions
###**************************************

    def MntToProfil(self):
        """
        Extraction of the profiles from Raster
        :return:
        """
        raster=None
        if isinstance(self.iface.activeLayer(), QgsRasterLayer):
            raster = self.iface.activeLayer()

        if not raster:
            QMessageBox.warning(None, 'Message',
                                'Please, selection the DTM raster')
            return

        for couche in QgsProject.instance().mapLayers().values():
            if couche.name()=="profiles":
                profil=couche

        if len(profil.selectedFeatures())==0:
                QMessageBox.warning(None, 'Message',
                                    'Please, selection the profiles')
                return

        liste = ["m", "dm", "cm", "mm"]

        valeur, ok = QInputDialog.getItem(None, "Selection of the DTM unit",
                                          'Unit', liste,0, False)

        if not ok:
            return

        facteur = math.pow(10, liste.index(valeur))

        if self.DEBUG:
            self.addInfo("Raster and Profile Selection, and Unit are Ok")
        # create a new worker instance
        worker = Worker(self,profil, raster, facteur)
        worker.run()
        if self.DEBUG:
            self.addInfo("Extraction is done")

    def fct_parametres(self):
        """
            Open parametters menu
            :return:
        """

        case, ok = QInputDialog.getItem(None,
                                          'Study case',
                                          'Kernel',
                                        self.listeState,0, False)
        #kernel list
        if ok:
            if self.DEBUG:
                self.addInfo("Kernel {}".format(self.Klist[self.listeState.index(case)]))
            dlg = parameter_dialog(self,self.Klist[self.listeState.index(case)])
            dlg.exec_()

    def fct_createXcas(self):
        """ create Xcas"""

        case, ok = QInputDialog.getItem(self,
                                        'Study case',
                                        'Kernel',
                                        self.listeState, 0, False)

        # kernel list
        if ok:
            if self.DEBUG:
                self.addInfo("Kernel {}".format(self.Klist[self.listeState.index(case)]))
            clam = Class_Mascaret(self)
            clam.creerXCAS(self.Klist[self.listeState.index(case)])
            fileNamePath = QFileDialog.getSaveFileName(self, "saveFile",
                                                       "{0}.xcas".format(os.path.join(self.masplugPath,clam.baseName)),
                                                        filter="XCAS (*.xcas)")
            fileNamePath=fileNamePath[0]
            if fileNamePath:
                clam.copyFileModel(fileNamePath, case='xcas')

    def fct_createGeo(self):
        """ create Xcas"""
        clam = Class_Mascaret(self)
        clam.creerGEORef()
        fileNamePath = QFileDialog.getSaveFileName(self, "saveFile",
                                                   "{0}.geo".format(os.path.join(self.masplugPath,clam.baseName)),
                                                   filter="GEO (*.geo)")
        fileNamePath = fileNamePath[0]
        if fileNamePath:
            clam.copyFileModel(fileNamePath, case='geo')

    def fct_run(self):
        """ Run Mascaret"""
        case, ok = QInputDialog.getItem(None,
                                        'Study case',
                                        'Kernel',
                                        self.listeState, 0, False)
        if ok:
            if self.DEBUG:
                self.addInfo("Kernel {}".format(self.Klist[self.listeState.index(case)]))
            clam = Class_Mascaret(self)
            clam.mascaret(self.Klist[self.listeState.index(case)],case)

    def del_run(self):
        """ Delete run of curent model"""

        case, ok = QInputDialog.getItem(None,
                                        'Study case',
                                        'Kernel',
                                          self.listeState, 0, False)
        if ok:
            clam = Class_Mascaret(self)
            clam.deleteRun(case)




### *******************************
#    SETTINGS
##*******************************

    def export_run(self):
        clam = Class_Mascaret(self)
        folderNamePath = QFileDialog.getExistingDirectory(self, "Choose a folder")
        if clam.copyRunFile(folderNamePath):
            self.addInfo('Export is done.')
        else:
            self.addInfo('Export failed.')

    def options(self, widget):
        """ GUI option"""
        from .settings_dialog import Settings
        dlg = Settings(self)
        dlg.exec_()

    def readSettings(self, defaults=False):
        """read Option"""
        sFile = os.path.join(self.masplugPath, 'settings.json')
        if not os.path.isfile(sFile) or defaults:
            sFile = os.path.join(self.masplugPath, 'default_settings.json')
        with open(sFile, 'r') as f:
            self.opts = json.load(f)
        for group, options in self.opts.items():
            for name, defaultValue in options.items():
                if group == 'mgis' and name in self.opts['mgis'].keys():
                    setattr(self, name, self.opts['mgis'][name])
                elif group == 'mdb' and name in self.opts['mdb'].keys():
                    setattr(self, name, self.opts['mdb'][name])
                else:
                    self.addInfo("Options have no key ['{}']['{}']".format(group, name))

    def writeSettings(self):
        """write Option"""
        for group, options in self.opts.items():
            for name, defaultValue in options.items():
                if group == 'mgis':
                    try:
                        self.opts['mgis'][name] = getattr(self, name)
                    except:
                        self.addInfo("Error: writeSettings , group :{0}".format(group))
                        pass
                elif group == 'mdb':
                    try:
                        self.opts['mdb'][name] = getattr(self.mdb, name)
                    except:
                        self.addInfo("Error: writeSettings , group :{0}".format(group))
                        pass
        # self.addInfo('{0}'.format(self.opts))
        with open(os.path.join(self.masplugPath, 'settings.json'), 'w') as f:
            json.dump(self.opts, f)

### *******************************
#    Graphics
##*******************************

    def do_something(self, layer, feature):
        print (feature.attributes())

    def exportModel(self):
        #choix du fichier d'exportatoin
        fileNamePath = QFileDialog.getSaveFileName(self, "saveFile",
                                                   "{0}.psql".format(
                                                    os.path.join(self.masplugPath, self.mdb.dbname+"_"+self.mdb.SCHEMA)),
                                                   filter="PSQL (*.psql);;File (*)")
        fileNamePath = fileNamePath[0]
        self.addInfo('{}'.format(fileNamePath))
        if self.mdb.exportSchema(fileNamePath) :
            self.addInfo('Export is done.')
        else:
            self.addInfo('Export failed.')

    def importModel(self):
        fileNamePath =QFileDialog.getOpenFileNames(None,
                                                'File Selection',
                                                   self.masplugPath,
                                                filter="PSQL (*.psql);;File (*)")
        # choix du fichier d'exportatoin

        fileNamePath=fileNamePath[0]
        if self.mdb.importSchema(fileNamePath):
            self.addInfo('Import is done.')
        else:
            self.addInfo('Import failed.')

    def mainGraph(self):
        """ GUI graphique"""

        canvas = self.iface.mapCanvas()
        self.coucheProfils=None
        self.profil=self.ui.actionCross_section.isChecked()
        self.hydrogramme=self.ui.actionHydrogramme.isChecked()
        self.profilResult=self.ui.actionCross_section_results.isChecked()

        # prevents use of other graphic button
        self.ui.actionHydrogramme.setEnabled(True)
        self.ui.actionCross_section.setEnabled(True)
        self.ui.actionCross_section_results.setEnabled(True)

        if self.profil:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section_results.setEnabled(False)
        elif self.hydrogramme :
            self.ui.actionCross_section_results.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)
        elif self.profilResult:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)

        self.prev_tool = canvas.mapTool()
        self.map_tool = IdentifyFeatureTool(self)
        # QObject.connect(self.map_tool, SIGNAL('geomIdentified'),
        #                 self.do_something)
        self.map_tool.changedRasterResults.connect(self.do_something)

        canvas.setMapTool(self.map_tool)

    def windinfo(self, txt, title='Informations'):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(txt)
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def about(self):
        pass

    def website(self):
        pass
        #TODO

    ### *******************************
    #    Water Quality
    ##*******************************
    def fct_tracer_laws(self):
        dlg = TracerLaws_dialog(self)
        dlg.exec_()

    def fct_parametersWQ(self):

        case, ok = QInputDialog.getItem(None,
                                          'Study case',
                                          'Kernel',
                                        self.listeState,0, False)
        #kernel list
        if ok:
            if self.DEBUG:
                self.addInfo("Kernel {}".format(self.Klist[self.listeState.index(case)]))
            dlg = Water_quality_dialog(self,self.Klist[self.listeState.index(case)])
            dlg.exec_()
