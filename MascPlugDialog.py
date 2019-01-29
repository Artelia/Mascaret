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
import json
import math
import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ClassMNT import ClassMNT
from .ClassMascaret import ClassMascaret
from .ClassParameterDialog import ClassParameterDialog
from .GraphProfilDialog import IdentifyFeatureTool
from .WaterQuality.ClassMascWQ import ClassMascWQ
from .WaterQuality.ClassWaterQualityDialog import ClassWaterQualityDialog
from .WaterQuality.TracerLawsDialog import ClassTracerLawsDialog
from .db.ClassMasDatabase import ClassMasDatabase
from .ui.custom_control import ClassWarningBox
from .Structure.ClassTmp import ClassTmp


if int(qVersion()[0]) < 5:  # qt4
    from qgis.PyQt.QtGui import *
else:  # qt5
    from qgis.PyQt.QtWidgets import *


class MascPlugDialog(QMainWindow):
    OPT_GENERAL, OPT_mdb, OPT_DTM = range(3)

    def __init__(self, iface, parent=None):
        QMainWindow.__init__(self, parent)
        if QApplication.overrideCursor():
            QApplication.restoreOverrideCursor()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.masplugPath = os.path.dirname(__file__)
        self.ui = loadUi(os.path.join(self.masplugPath, 'ui/MascPlug_dialog_base.ui'), self)
        # variables
        self.DEBUG = 1
        self.curConnName = None
        self.passwd = None
        self.mdb = None
        self.iface = iface

        self.map_tool = None

        # self.pathPostgres = self.masplugPath
        # emplacement objet sql
        self.dossierSQL = os.path.join(os.path.join(self.masplugPath, "db"), "sql")
        # style des couches
        self.dossierStyle = os.path.join(os.path.join(self.masplugPath, "db"), "style")
        self.repProject = None

        self.box = ClassWarningBox(self)
        # variables liste of results
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
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]

        self.actions2Disable = []
        self.menus = self.ui.menubar.findChildren(QMenu)
        self.toolbars = self.findChildren(QToolBar)

        # setting
        self.read_settings()
        # self.postgres_path=self.opts['mgis']['postgres_path']
        self.add_info(self.postgres_path)
        self.update_default_crs()

        # DB
        self.ui.actionRefresh_Database.triggered.connect(self.conn_changed)
        self.ui.actionCreate_New_Model.triggered.connect(self.db_create_model)
        self.ui.actionDeleteModel.triggered.connect(self.db_delete_model)
        # #mascaret
        self.ui.actionLoad_Model.triggered.connect(self.db_load)

        # combos
        self.ui.crsWidget.crsChanged.connect(self.update_default_crs)
        self.ui.connsCbo.activated.connect(self.conn_changed)

        # Settings
        self.ui.actionOptions.triggered.connect(self.options)
        self.ui.actionRestore_Default_Options.triggered.connect(lambda: self.read_settings(defaults=True))

        self.ui.textEdit.append('----------------------------------------------------------------------------')
        # initialise

        # restore the window state
        # s = QSettings()
        # self.restoreGeometry(s.value("/Mascaret/mainWindow/geometry", QByteArray(), type=QByteArray))
        # self.restoreState(s.value("/Mascaret/mainWindow/windowState", QByteArray(), type=QByteArray))

        # # check if we should connect to previuosly used RDB
        if self.open_last_conn:
            self.conn_changed(conn_name=self.opts['mdb']['last_conn'])
            self.add_info('shema {}'.format(self.opts['mdb']['last_schema']))
            if self.open_last_schema:
                self.db_load(schema_info=self.opts['mdb']['last_schema'])
        else:
            self.conn_changed()

        # restore settings
        self.read_settings()

        # set QGIS projection CRS as a default for MasPlug
        self.ui.crsWidget.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        self.update_default_crs()

        # # disable some actions until a connection to river database is established
        if not self.mdb:
            self.disable_actions_connection()

            # Menu action
        # visu Mascaret plugin
        self.ui.actionCross_section.triggered.connect(self.main_graph)
        self.ui.actionHydrogramme.triggered.connect(self.main_graph)
        self.ui.actionCross_section_results.triggered.connect(self.main_graph)

        # creatoin model
        self.ui.action_Extract_MNTfor_profile.triggered.connect(self.mnt_to_profil)
        self.ui.actionCreate_Geometry.triggered.connect(self.fct_create_geo)
        self.ui.actionCreate_xcas.triggered.connect(self.fct_create_xcas)
        self.ui.actionParameters.triggered.connect(self.fct_parametres)
        self.ui.actionRun.triggered.connect(self.fct_run)
        self.ui.actionDelete_Run.triggered.connect(self.del_run)
        self.ui.actionExport_Run.triggered.connect(self.export_run)
        self.ui.actionExport_Model.triggered.connect(self.export_model)
        self.ui.actionImport_Model.triggered.connect(self.import_model)

        self.ui.actionParameters_Water_Quality.triggered.connect(self.fct_parameters_wq)
        self.ui.actionTracer_Laws.triggered.connect(self.fct_tracer_laws)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionWebsite.triggered.connect(self.website)
        self.ui.actionWebsite.setEnabled(False)
        # test
        self.ui.actionexport_tracer_files.triggered.connect(self.fct_export_tracer_files)
        self.ui.actionAdd_WQ_tables.triggered.connect(self.fct_add_wq_tables)
        self.ui.actionAdd_Structure_tables.triggered.connect(self.fct_add_struct_tables)
        #TODO a supp
        # self.ui.actionStructures.triggered.connect()
        self.ui.actionTest_struct.triggered.connect(self.fct_test)

    def add_info(self, text):
        self.ui.textEdit.append(text)

    def update_default_crs(self):
        self.crs = self.ui.crsWidget.crs()
        if self.mdb:
            self.mdb.SRID = int(self.crs.postgisSrid())
        self.add_info('\nCurrent projection is {0}'.format(self.crs.authid()))

    def disable_all(self):
        menus_always_on = ['Help', 'Setting']
        for m in self.menus:
            if not m.title() in menus_always_on:
                for a in m.findChildren(QAction):
                    a.setDisabled(True)
        for t in self.toolbars:
            for b in t.findChildren(QToolButton):
                b.setDisabled(True)

    def disable_actions_connection(self):
        """ cache les items avant la connection"""
        self.disable_all()
        self.list_menu = ['Refresh Connections List']
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

    def disable_actions_model(self):

        self.disable_all()
        # bouton afficher
        self.list_menu = ['Refresh Connections List',
                          "Load Model",
                          "Create New Model",
                          "Delete Model",
                          "Import Model"]
        for t in self.ui.dbToolBar.findChildren(QToolButton):
            if t.text() in self.list_menu:
                t.setEnabled(True)

        # menu a cacher
        if self.actions2Disable:
            for a in self.actions2Disable:
                a.setEnabled(True)
        else:
            pass

        self.actions2Disable = [self.ui.actionExport_Model]
        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in self.actions2Disable:
            a.setDisabled(True)

    def enable_all_actions(self):
        for m in self.menus:
            for a in m.findChildren(QAction):
                a.setEnabled(True)
        for t in self.toolbars:
            for b in t.findChildren(QToolButton):
                b.setEnabled(True)
        for a in self.actions2Disable:
            a.setEnabled(True)

    def disable_actions(self, list_action_block):
        """ cache les items de la liste d'action"""

        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in list_action_block:
            a.setDisabled(True)

    def enable_actions(self, list_action_block):
        """ montre les items de la liste d'action"""
        self.ui.menuDB.findChildren(QAction)[0].setEnabled(True)
        for a in list_action_block:
            a.setEnabled(True)

    def toggle_debug_mode(self):
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
        self.write_settings()
        QMainWindow.closeEvent(self, e)

    def conn_changed(self, conn_name='toto'):
        """change the data base"""
        # close any existing connection to a MascPlug database
        if self.mdb:
            self.add_info(
                "Closing existing connection to {0}@{1} Mascaret database".format(self.mdb.dbname, self.mdb.host))
            self.mdb.disconnect_pg()
            self.mdb = None
        else:
            pass
        settings = QSettings()
        settings.beginGroup('/PostgreSQL/connections')
        conns_names = settings.childGroups()
        if conn_name in conns_names:
            self.curConnName = conn_name
        else:
            self.curConnName = self.ui.connsCbo.currentText()
        self.add_info('{}'.format(self.curConnName))
        self.ui.connsCbo.clear()
        self.ui.connsCbo.addItem('')
        for conn in conns_names:
            self.ui.connsCbo.addItem(conn)
        try:
            i = conns_names.index(self.curConnName) + 1
        except ValueError:
            i = 0
        self.ui.connsCbo.setCurrentIndex(i)
        conn_name = self.ui.connsCbo.currentText()
        settings.endGroup()

        settings.beginGroup('/PostgreSQL/connections/{0}'.format(conn_name))
        self.host = settings.value('host')
        self.port = settings.value('port')
        self.database = settings.value('database')
        self.user = settings.value('username')
        self.passwd = settings.value('password')
        settings.endGroup()
        # create a new connection to masPlug database
        self.mdb = ClassMasDatabase(self, self.database, self.host, self.port, self.user, self.passwd)
        self.mdb.SRID = int(self.crs.postgisSrid())
        msg = self.mdb.connect_pg()
        self.add_info('Created connection to mascaret database: {0}@{1}'.format(self.mdb.dbname, self.mdb.host))
        self.mdb.last_conn = conn_name
        if 'Error:' in msg or 'None:' in msg:
            self.disable_actions_connection()
        else:
            self.disable_actions_model()

    def db_create_model(self):
        """Model creation"""
        model_name, ok = QInputDialog.getText(self, 'New Model', 'New Model name:')

        if ok:
            self.mdb.SCHEMA = model_name.lower()
            self.mdb.create_model(self.dossierSQL)
            self.mdb.last_schema = self.mdb.SCHEMA
            self.enable_all_actions()
        else:

            self.add_info('Creating new model cancelled.')

    def db_delete_model(self):
        """ Model delete"""
        from .ClassDeletshDialog import ClassDeletshDialog
        dlg = ClassDeletshDialog(self, self.iface)
        dlg.exec_()

    def db_load(self, schema_info=None):
        """ load model"""
        try:
            self.repProject = os.path.dirname(
                QgsProject.instance().fileName())
        except:
            self.repProject = None

        if schema_info:
            (model, ok) = (schema_info, True)
        else:
            liste = self.mdb.liste_models()
            model, ok = QInputDialog.getItem(None,
                                             'Model Choice',
                                             'Model',
                                             liste, 0, False)
        if ok:
            self.mdb.SCHEMA = model
            self.mdb.load_model()
            self.mdb.last_schema = self.mdb.SCHEMA
            self.enable_all_actions()

        else:
            self.add_info('Droping Model cancelled.')

            # **************************************
            #  Menus Functions
            # **************************************

    def mnt_to_profil(self):
        """
        Extraction of the profiles from Raster
        :return:
        """
        raster = None
        if isinstance(self.iface.activeLayer(), QgsRasterLayer):
            raster = self.iface.activeLayer()

        if not raster:
            QMessageBox.warning(None, 'Message',
                                'Please, selection the DTM raster')
            return
        try:  # qgis2
            tempo = QgsMapLayerRegistry.instance().mapLayers().values()

        except:  # qgis 3
            tempo = QgsProject.instance().mapLayers().values()
        for couche in tempo:
            if couche.name() == "profiles":
                profil = couche

        if len(profil.selectedFeatures()) == 0:
            QMessageBox.warning(None, 'Message',
                                'Please, selection the profiles')
            return

        liste = ["m", "dm", "cm", "mm"]

        valeur, ok = QInputDialog.getItem(None, "Selection of the DTM unit",
                                          'Unit', liste, 0, False)

        if not ok:
            return

        facteur = math.pow(10, liste.index(valeur))

        if self.DEBUG:
            self.add_info("Raster and Profile Selection, and Unit are Ok")
        # create a new worker instance
        worker = ClassMNT(self, profil, raster, facteur)
        worker.run()
        if self.DEBUG:
            self.add_info("Extraction is done")

    def fct_parametres(self):
        """
            Open parametters menu
            :return:
        """

        case, ok = QInputDialog.getItem(None,
                                        'Study case',
                                        'Kernel',
                                        self.listeState, 0, False)
        # kernel list
        if ok:
            if self.DEBUG:
                self.add_info("Kernel {}".format(self.Klist[self.listeState.index(case)]))
            dlg = ClassParameterDialog(self, self.Klist[self.listeState.index(case)])
            dlg.exec_()

    def fct_create_xcas(self):
        """ create Xcas"""

        case, ok = QInputDialog.getItem(self,
                                        'Study case',
                                        'Kernel',
                                        self.listeState, 0, False)

        # kernel list
        if ok:
            if self.DEBUG:
                self.add_info("Kernel {}".format(self.Klist[self.listeState.index(case)]))
            clam = ClassMascaret(self)
            clam.creer_xcas(self.Klist[self.listeState.index(case)])
            if int(qVersion()[0]) < 5:  # qt4
                file_name_path = QFileDialog.getSaveFileName(self, "saveFile",
                                                             "{0}.xcas".format(
                                                                 os.path.join(self.masplugPath, clam.baseName)),
                                                             filter="XCAS (*.xcas)")
            else:  # qt5
                file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                                "{0}.xcas".format(
                                                                    os.path.join(self.masplugPath, clam.baseName)),
                                                                filter="XCAS (*.xcas)")
            if file_name_path:
                clam.copy_file_model(file_name_path, case='xcas')

    def fct_create_geo(self):
        """ create Xcas"""
        clam = ClassMascaret(self)
        clam.creer_geo_ref()
        # clam.creer_geo()
        if int(qVersion()[0]) < 5:  # qt4
            file_name_path = QFileDialog.getSaveFileName(self, "saveFile",
                                                         "{0}.geo".format(
                                                             os.path.join(self.masplugPath, clam.baseName)),
                                                         filter="GEO (*.geo)")
        else:  # qt5
            file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                            "{0}.geo".format(
                                                                os.path.join(self.masplugPath, clam.baseName)),
                                                            filter="GEO (*.geo)")

        if file_name_path:
            clam.copy_file_model(file_name_path, case='geo')

    def fct_run(self):
        """ Run Mascaret"""
        case, ok = QInputDialog.getItem(None,
                                        'Study case',
                                        'Kernel',
                                        self.listeState, 0, False)
        if ok:
            if self.DEBUG:
                self.add_info("Kernel {}".format(self.Klist[self.listeState.index(case)]))
            run, ok = QInputDialog.getText(QWidget(), 'Run name',
                                           'Please input a run name :', text=case)
            if ok:
                clam = ClassMascaret(self)
                clam.mascaret(self.Klist[self.listeState.index(case)], run)

    def del_run(self):
        """ Delete run of curent model"""
        from .ClassDeletrunDialog import ClassDeletrunDialog
        dlg = ClassDeletrunDialog(self, self.iface)
        dlg.exec_()

    #  *******************************
    #    SETTINGS
    # *******************************

    def export_run(self):
        clam = ClassMascaret(self)
        folder_name_path = QFileDialog.getExistingDirectory(self, "Choose a folder")
        if clam.copy_run_file(folder_name_path):
            self.add_info('Export is done.')
        else:
            self.add_info('Export failed.')

    def options(self, widget):
        """ GUI option"""
        from .ClassSettingsDialog import ClassSettingsDialog
        dlg = ClassSettingsDialog(self)
        dlg.exec_()

    def read_settings(self, defaults=False):
        """read Option"""
        s_file = os.path.join(self.masplugPath, 'settings.json')
        if not os.path.isfile(s_file) or defaults:
            s_file = os.path.join(self.masplugPath, 'default_settings.json')
        with open(s_file, 'r') as f:
            self.opts = json.load(f)
        for group, options in self.opts.items():
            for name, defaultValue in options.items():
                if group == 'mgis' and name in self.opts['mgis'].keys():
                    setattr(self, name, self.opts['mgis'][name])
                elif group == 'mdb' and name in self.opts['mdb'].keys():
                    setattr(self, name, self.opts['mdb'][name])
                else:
                    self.add_info("Options have no key ['{}']['{}']".format(group, name))

    def write_settings(self):
        """write Option"""
        for group, options in self.opts.items():
            for name, defaultValue in options.items():
                if group == 'mgis':
                    try:
                        self.opts['mgis'][name] = getattr(self, name)
                    except:
                        self.add_info("Error: write_settings , group :{0}".format(group))
                        pass
                elif group == 'mdb':
                    try:
                        self.opts['mdb'][name] = getattr(self.mdb, name)
                    except:
                        self.add_info("Error: write_settings , group :{0}".format(group))
                        pass
        # self.add_info('{0}'.format(self.opts))
        with open(os.path.join(self.masplugPath, 'settings.json'), 'w') as f:
            json.dump(self.opts, f)

            # *******************************
            #    Graphics
            # *******************************

    def do_something(self, layer, feature):
        print(feature.attributes())

    def export_model(self):
        # choix du fichier d'exportatoin
        if int(qVersion()[0]) < 5:  # qt4
            file_name_path = QFileDialog.getSaveFileName(self, "saveFile",
                                                         "{0}.psql".format(
                                                             os.path.join(self.masplugPath,
                                                                          self.mdb.dbname + "_" + self.mdb.SCHEMA)),
                                                         filter="PSQL (*.psql);;File (*)")
        else:  # qt5
            file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                            "{0}.psql".format(
                                                                os.path.join(self.masplugPath,
                                                                             self.mdb.dbname + "_" + self.mdb.SCHEMA)),
                                                            filter="PSQL (*.psql);;File (*)")

        if self.mdb.export_schema(file_name_path):
            self.add_info('Export is done.')
        else:
            self.add_info('Export failed.')

    def import_model(self):
        if int(qVersion()[0]) < 5:  # qt4
            file_name_path = QFileDialog.getOpenFileNames(None,
                                                          'File Selection',
                                                          self.masplugPath,
                                                          filter="PSQL (*.psql);;File (*)")
        else:  # qt5
            file_name_path, _ = QFileDialog.getOpenFileNames(None,
                                                             'File Selection',
                                                             self.masplugPath,
                                                             filter="PSQL (*.psql);;File (*)")
        if self.mdb.check_extension():
            self.add_info(" Shema est {}".format(self.SCHEMA))
            self.mdb.create__first_model()

        for file in file_name_path:
            if os.path.isfile(file):
                namesh = self.mdb.checkschema_import(file)
                if namesh is not None:
                    liste = self.mdb.list_schema()
                    if namesh in liste:
                        # demande change name
                        ok = self.box.yes_no_q("The {} shema already exists.\n "
                                               "Do you want change the schema name befor import?".format(namesh))
                        if ok:
                            newname, ok = QInputDialog.getText(self, 'New Model', 'New Model name:')
                            if ok and self.check_newname(newname, liste):

                                sql = "ALTER SCHEMA {0} RENAME TO {0}_tmp".format(namesh)
                                self.mdb.run_query(sql)
                                sql = ''
                                if self.mdb.import_schema(file):
                                    self.add_info('Import is done.')
                                    sql = "ALTER SCHEMA {0} RENAME TO {1};\n".format(namesh, newname)
                                else:
                                    self.add_info('Import failed.')
                                #
                                sql += "ALTER SCHEMA {0}_tmp RENAME TO {0};".format(namesh)
                                self.mdb.run_query(sql)
                            else:
                                self.add_info('Import cancel.')
                                return
                        else:
                            self.add_info('Import cancel.')
                            return
                    else:
                        if self.mdb.import_schema(file):
                            self.add_info('Import is done.')
                        else:
                            self.add_info('Import failed.')
                else:
                    if self.mdb.import_schema(file):
                        self.add_info('Import is done.')
                    else:
                        self.add_info('Import failed.')
            else:
                self.add_info('File not found.')
        return

    def check_newname(self, name, liste):
        """Check the new name validation
            name : test name
            liste : exclud list"""
        if name == '':
            if self.DEBUG:
                self.add_info('Name is not correct.')
            return False
        elif name in liste:
            if self.DEBUG:
                self.add_info('<<{}>> schema name already exists'.format(name))
            return False
        else:
            return True

    def main_graph(self):
        """ GUI graphique"""

        canvas = self.iface.mapCanvas()
        self.coucheProfils = None
        self.profil = self.ui.actionCross_section.isChecked()
        self.hydrogramme = self.ui.actionHydrogramme.isChecked()
        self.profilResult = self.ui.actionCross_section_results.isChecked()

        # prevents use of other graphic button
        self.ui.actionHydrogramme.setEnabled(True)
        self.ui.actionCross_section.setEnabled(True)
        self.ui.actionCross_section_results.setEnabled(True)

        if self.profil:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section_results.setEnabled(False)

        elif self.hydrogramme:
            self.ui.actionCross_section_results.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)
        elif self.profilResult:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)

        self.prev_tool = canvas.mapTool()
        self.map_tool = IdentifyFeatureTool(self)
        try:  # qgis2
            QObject.connect(self.map_tool, SIGNAL('geomIdentified'),
                            self.do_something)
        except:  # qgis3
            self.map_tool.changedRasterResults.connect(self.do_something)

        canvas.setMapTool(self.map_tool)

    def windinfo(self, txt, title='Informations'):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setWindowIcon(QIcon(os.path.join(os.path.join(self.masplugPath, 'icones'), 'icon_base.png')))
        msg.setText(txt)
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def about(self):
        file = open(os.path.join(self.masplugPath, 'metadata.txt'), 'r')
        for ligne in file:
            if ligne.find("version=") > -1:
                ligne = ligne.split('=')
                val = ligne[1]
                break
        # TODO get "about" info of file
        txt = u"""
Plugin dedicated to the building and exploitation of Mascaret models.

Requires PostgreSQL and PostGIS.

Developed by Mehdi-Pierre DAOU, Christophe COULET, Aurélien PERRIN (Artelia),
Based on an initial version developped by Matthieu NICOLAS (SPC Maine Loire aval)
Some parts are based on the RiverGIS plugin developped by Radek Pasiok & Lukasz Debek 
(Many thanks for the work they've done on RiverGis).


Version : {}
           """.format(val)
        self.windinfo(txt, title='About')

    def website(self):
        pass
        # TODO

    #  *******************************
    #    Water Quality
    # *******************************
    def fct_tracer_laws(self):
        dlg = ClassTracerLawsDialog(self)
        dlg.exec_()

    def fct_parameters_wq(self):

        dlg = ClassWaterQualityDialog(self)
        dlg.exec_()

    def fct_export_tracer_files(self):
        folder_name_path = QFileDialog.getExistingDirectory(self, "Choose a folder")

        self.dossierFileMasc = os.path.join(self.masplugPath, "mascaret")
        cl = ClassMascWQ(self, self.dossierFileMasc)
        try:
        # # if cl.dico_phy[cl.cur_wq_mod]['meteo']:
        #     #simul date
        #     # dat1=datetime.datetime(2019, 1, 13, 13, 35, 12)
        #     # dat2=datetime.datetime(2019, 1, 10, 13, 35, 12)
        #     # cl.create_filemet(dossier=folder_name_path,typ_time='date',datefirst=dat2, dateend=dat1)
        #     cl.create_filemet(dossier=folder_name_path)
            cl.init_conc_tracer(dossier=folder_name_path)
            cl.create_filephy(dossier=folder_name_path)
            cl.law_tracer(dossier=folder_name_path)

            self.add_info('Export is done.')
        except:
            self.add_info('Export failed.')

    def fct_add_wq_tables(self):

        ok = self.box.yes_no_q('Do you want add tracer tables ? \n '
                               'WARNING: if the tables exist then it will be emptied.')
        if ok:
            self.mdb.add_table_wq(self.dossierSQL)

    def fct_add_struct_tables(self):

        ok = self.box.yes_no_q('Do you want add hydraulic structure tables ? \n '
                               'WARNING: if the tables exist then it will be emptied.')
        if ok:
            self.mdb.add_table_struct(self.dossierSQL)


    def fct_test(self):

        # cl=ClassTmp(self)
        # # cl.copy_profil(28)
        # cl.show()

        # cl.create_poly_elem()
        dossier=r"C:\Users\mehdi-pierre.daou\.qgis2\python\plugins\Mascaret\Structure\Abacus"
        self.mdb.insert_abacus_table(dossier)

