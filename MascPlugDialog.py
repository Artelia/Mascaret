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
import posixpath

from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtGui import QIcon
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ClassMNT import ClassMNT
from .ClassMascaret import ClassMascaret
from .ClassParameterDialog import ClassParameterDialog
from .Graphic.GraphProfilDialog import IdentifyFeatureTool
from .Function import read_version
# # structures
from .Structure.StructureDialog import ClassStructureDialog
from .Structure.MobilSingDialog import ClassMobilSingDialog
from .WaterQuality.ClassMascWQ import ClassMascWQ
from .WaterQuality.ClassWaterQualityDialog import ClassWaterQualityDialog
from .WaterQuality.TracerLawsDialog import ClassTracerLawsDialog
from .ClassObservation import ClassEventObsDialog
from .db.ClassMasDatabase import ClassMasDatabase
from .db.Check_tab import CheckTab
from .ui.custom_control import ClassWarningBox
from .ClassDownload import ClassDownloadMasc
from .ClassImportExportDialog import ClassDlgExport, ClassDlgImport
from .ClassImport_res import ClassImportRes
from .scores.ClassScoresDialog import ClassScoresDialog
from .HydroLawsDialog import ClassHydroLawsDialog

from .Graphic.GraphBCDialog import GraphBCDialog

from qgis.PyQt.QtWidgets import *


class MascPlugDialog(QMainWindow):
    OPT_GENERAL, OPT_mdb, OPT_DTM = range(3)

    def __init__(self, iface, parent=None):
        QMainWindow.__init__(self, parent)
        if QApplication.overrideCursor():
            QApplication.restoreOverrideCursor()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.masplugPath = os.path.dirname(__file__)
        self.ui = loadUi(
            os.path.join(self.masplugPath, 'ui/MascPlug_dialog_base.ui'), self)
        # variables
        self.DEBUG = 1

        self.curConnName = None
        self.passwd = None
        self.mdb = None
        self.iface = iface

        self.map_tool = None

        self.crs = 0
        self.list_menu = []

        self.user = ''
        self.host = ''
        self.port = ''
        self.database = ''
        self.chkt = False
        self.opts = {}

        self.coucheProfils = None
        self.profil = None
        self.hydrogramme = None
        self.profil_result = None
        self.basin_result = None
        self.profil_z = None

        self.prev_tool = None

        self.dossierFileMasc = ''

        # self.pathPostgres = self.masplug_path
        # emplacement objet sql
        self.dossier_sql = os.path.join(os.path.join(self.masplugPath, "db"),
                                        "sql")
        # style des couches
        self.dossier_style = os.path.join(os.path.join(self.masplugPath, "db"),
                                          "style")
        self.dossier_struct = os.path.join(
            os.path.join(self.masplugPath, "Structure"), 'Abacus')
        self.repProject = None
        self.task_mas = None
        self.task_exp = None
        self.task_imp = None

        self.box = ClassWarningBox()
        # variables liste of results
        self.variables = {}
        with open(os.path.join(self.masplugPath, 'variables.dat'),
                  'r') as fichier:
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
        self.ui.actionRestore_Default_Options.triggered.connect(
            lambda: self.read_settings(defaults=True))

        self.ui.textEdit.append(
            '----------------------------------------------------------------------------')
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
        self.ui.crsWidget.setCrs(
            self.iface.mapCanvas().mapSettings().destinationCrs())
        self.update_default_crs()

        # # disable some actions until a connection to river database is established
        if not self.mdb:
            self.disable_actions_connection()

            # Menu action
        # visu Mascaret plugin
        self.ui.actionCross_section.triggered.connect(self.main_graph)
        self.ui.actionHydrogramme.triggered.connect(self.main_graph)
        self.ui.actionCross_section_results.triggered.connect(self.main_graph)
        self.ui.actionBasin.triggered.connect(self.main_graph)
        self.ui.actionGraphRes.triggered.connect(self.main_graph)

        # creatoin model
        self.ui.action_Extract_MNTfor_profile.triggered.connect(
            self.mnt_to_profil)
        self.ui.actionCreate_Geometry.triggered.connect(self.fct_create_geo)
        self.ui.actionCreate_xcas.triggered.connect(self.fct_create_xcas)
        self.ui.actionCreate_Basin.triggered.connect(self.fct_create_casier)
        self.ui.actionParameters.triggered.connect(self.fct_parametres)
        self.ui.actionRun.triggered.connect(self.fct_run)
        self.ui.actionDelete_Run.triggered.connect(self.del_run)
        self.ui.actionExport_Run.triggered.connect(self.export_run)
        self.ui.actionExport_Model.triggered.connect(self.export_model_dgl)
        self.ui.actionImport_Model.triggered.connect(self.import_model_dgl)

        self.ui.actionParameters_Water_Quality.triggered.connect(
            self.fct_parameters_wq)
        self.ui.actionTracer_Laws.triggered.connect(self.fct_tracer_laws)
        self.ui.actionObservations.triggered.connect(self.fct_event_obs)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionWebsite.triggered.connect(self.website)
        self.ui.actionWebsite.setEnabled(False)
        self.ui.actionWikisite.triggered.connect(self.wikisite)

        # Structures
        self.ui.actionStructures.triggered.connect(self.fct_structures)
        self.ui.actionExport_Model_Files.triggered.connect(self.fct_creat_run)
        self.ui.actionStructures_weirs.triggered.connect(self.fct_mv_dam)
        if self.cond_api:
            self.ui.actionStructures_weirs.setEnabled(False)
        else:
            self.ui.actionStructures_weirs.setEnabled(True)

        # WQ
        self.ui.actionexport_tracer_files.triggered.connect(
            self.fct_export_tracer_files)
        self.ui.action_update_bin.triggered.connect(self.download_bin)

        self.ui.actionUpdate_all_PK.triggered.connect(self.update_pk)
        self.ui.actionImport_Results.triggered.connect(self.import_resu_model)
        self.ui.actionImport_Results.setVisible(False)

        # scores
        self.ui.actionScores.triggered.connect(self.fct_scores)

        # Laws
        self.ui.actionHydro_Laws.triggered.connect(self.fct_hydro_laws)

        # TODO Finaliser
        self.ui.actionTest.triggered.connect(self.fct_test)
        self.ui.actionTest.setVisible(False)

        # TODO DELETE AFTER
        self.ui.actionImport_Old_Model.triggered.connect(
            self.import_old_model_dgl)
        self.ui.menuUpate_table.menuAction().setVisible(False)

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
                                self.ui.actionEfl]
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
                "Closing existing connection to {0}@{1} Mascaret database".format(
                    self.mdb.dbname, self.mdb.host))
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
        # first try to get the credentials from AuthManager, then from the basic settings
        authconf = settings.value('authcfg', None)
        if authconf:
            auth_manager = QgsApplication.authManager()
            conf = QgsAuthMethodConfig()
            auth_manager.loadAuthenticationConfig(authconf, conf, True)
            if conf.id():
                self.user = conf.config('username', '')
                self.passwd = conf.config('password', '')
        else:
            self.user = settings.value('username')
            self.passwd = settings.value('password')

        if not self.passwd:
            self.add_info("Warning: the password is NULL.")
        self.host = settings.value('host')
        self.port = settings.value('port')
        self.database = settings.value('database')
        settings.endGroup()
        # create a new connection to masPlug database
        self.mdb = ClassMasDatabase(self, self.database, self.host, self.port,
                                    self.user, self.passwd)
        self.chkt = CheckTab(self, self.mdb)
        self.mdb.SRID = int(self.crs.postgisSrid())
        msg = self.mdb.connect_pg()
        self.add_info('Created connection to mascaret database: {0}@{1}'.format(
            self.mdb.dbname, self.mdb.host))
        self.mdb.last_conn = conn_name
        if 'Error:' in msg or 'None:' in msg:
            self.disable_actions_connection()
        else:
            self.disable_actions_model()

    def db_create_model(self):
        """Model creation"""
        model_name, ok = QInputDialog.getText(self, 'New Model',
                                              'New Model name:')

        if ok:
            self.mdb.SCHEMA = model_name.lower()
            self.mdb.create_model(self.dossier_sql)
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
        except Exception:
            self.repProject = None

        if schema_info:
            (model, ok) = (schema_info, True)
        else:
            liste = self.mdb.liste_models()
            liste = [v for v in liste if not (v in self.mdb.ignor_schema)]
            model, ok = QInputDialog.getItem(None,
                                             'Model Choice',
                                             'Model',
                                             liste, 0, False)
        if ok:
            self.mdb.SCHEMA = model
            sql = """SELECT Find_SRID('{}', 'extremities','geom');"""
            res = self.mdb.run_query(sql.format(model), fetch=True)
            if res:
                self.mdb.SRID = int(res[0][0])
            try:
                self.chkt.update_adim()
            except Exception as e:
                self.add_info("********* Echec of update table ***********")
                self.add_info('Error : {}'.format(e))

            self.mdb.load_model()
            crs = QgsCoordinateReferenceSystem(
                "POSTGIS:{}".format(self.mdb.SRID))
            self.ui.crsWidget.setCrs(crs)

            self.mdb.last_schema = self.mdb.SCHEMA
            self.enable_all_actions()

        else:
            self.add_info('Droping Model cancelled.')

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
        except Exception:  # qgis 3
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
                self.add_info(
                    "Kernel {}".format(self.Klist[self.listeState.index(case)]))
            dlg = ClassParameterDialog(self,
                                       self.Klist[self.listeState.index(case)])
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
                self.add_info(
                    "Kernel {}".format(self.Klist[self.listeState.index(case)]))
            rep_run = os.path.join(self.masplugPath, "mascaret_copy")
            clam = ClassMascaret(self, rep_run=rep_run)

            clam.creer_xcas(self.Klist[self.listeState.index(case)])

            file_name_path, _ = QFileDialog.getSaveFileName(self,
                                                            "saveFile",
                                                            "{0}.xcas".format(
                                                                os.path.join(
                                                                    QDir.homePath(),
                                                                    clam.baseName)),
                                                            filter="XCAS (*.xcas)")
            if file_name_path:
                clam.copy_file_model(file_name_path, case='xcas')
            clam.del_folder_mas()

    def fct_create_geo(self):
        """ create Xcas"""
        rep_run = os.path.join(self.masplugPath, "mascaret_copy")
        clam = ClassMascaret(self, rep_run=rep_run)
        clam.creer_geo_ref()
        # clam.creer_geo()

        file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                        "{0}.geo".format(
                                                            os.path.join(
                                                                QDir.homePath(),
                                                                clam.baseName)),
                                                        filter="GEO (*.geo)")

        if file_name_path:
            clam.copy_file_model(file_name_path, case='geo')
        clam.del_folder_mas()

    def fct_create_casier(self):
        """ create file .Casier """
        # Mascaret.exe demande un .casier et pas basin d'ou le nom de la fonction
        # Pas de dialog box sur le noyau: les casiers sont uniquement en transitoire

        rep_run = os.path.join(self.masplugPath, "mascaret_copy")
        clam = ClassMascaret(self, rep_run=rep_run)
        # Appel de la fonction creerGEOCasier() definie dans Class_Mascaret.py
        clam.creer_geo_casier()

        file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                        "{0}.casier".format(
                                                            os.path.join(
                                                                QDir.homePath(),
                                                                clam.baseName)),
                                                        filter="CASIER (*.casier)")

        if file_name_path:
            clam.copy_file_model(file_name_path, case='casier')
        clam.del_folder_mas()

    def fct_run(self):
        """ Run Mascaret"""
        if self.task_mas:
            self.box.info("The simulation is not running,\n"
                          " because the previous simulation running yet")
            self.add_info('The simulation is not running\n')
            return
        case, ok = QInputDialog.getItem(None,
                                        'Study case',
                                        'Kernel',
                                        self.listeState, 0, False)
        if ok:
            if self.DEBUG:
                self.add_info(
                    "Kernel {}".format(self.Klist[self.listeState.index(case)]))
            run, ok = QInputDialog.getText(QWidget(), 'Run name',
                                           'Please input a run name :',
                                           text=case)
            run = run.replace("'", " ").replace('"', ' ').strip()
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

    def export_run(self, clam=None):
        if not clam:
            clam = ClassMascaret(self)
        folder_name_path = QFileDialog.getExistingDirectory(self,
                                                            "Choose a folder")
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
                    self.add_info(
                        "Options have no key ['{}']['{}']".format(group, name))

    def write_settings(self):
        """write Option"""
        for group, options in self.opts.items():
            for name, defaultValue in options.items():
                if group == 'mgis':
                    try:
                        self.opts['mgis'][name] = getattr(self, name)
                    except Exception:
                        self.add_info(
                            "Error: write_settings , group :{0}".format(group))
                        pass
                elif group == 'mdb':
                    try:
                        self.opts['mdb'][name] = getattr(self.mdb, name)
                    except Exception:
                        self.add_info(
                            "Error: write_settings , group :{0}".format(group))
                        pass
        # self.add_info('{0}'.format(self.opts))
        with open(os.path.join(self.masplugPath, 'settings.json'), 'w') as f:
            json.dump(self.opts, f)

            # *******************************
            #    Graphics
            # *******************************

    def do_something(self, layer, feature):
        print(feature.attributes())

    def export_model_dgl(self):
        if self.task_exp:
            self.box.info("The export is not running,\n"
                          " because the previous export running yet")
            self.add_info('The export is not running\n')
            return
        dlg = ClassDlgExport(self)
        if dlg.exec_():
            pass

        return

    def import_model_dgl(self):
        if self.task_imp:
            self.box.info("The export is not running,\n"
                          " because the previous import running yet")
            self.add_info('The import is not running\n')
            return
        dlg = ClassDlgImport(self)
        if dlg.exec_():
            pass
        return

    def import_old_model_dgl(self):
        """
        Import old format result
        :return:
        """
        if self.task_imp:
            self.box.info("The export is not running,\n"
                          " because the previous import running yet")
            self.add_info('The import is not running\n')

            return

        file_name_path, _ = QFileDialog.getOpenFileNames(None,
                                                         'File Selection',
                                                         self.masplugPath,
                                                         filter="PSQL (*.psql);;File (*)")
        if self.mdb.check_extension():
            self.add_info(" Shema est {}".format(self.mdb.SCHEMA))
            self.mdb.create_first_model()

        for file in file_name_path:
            if os.path.isfile(file):
                namesh = self.mdb.checkschema_import(file)
                if namesh is not None:
                    liste = self.mdb.list_schema()
                    if namesh in liste:
                        # demande change name
                        ok = self.box.yes_no_q("The {} shema already exists.\n "
                                               "Do you want change the schema name befor import?".format(
                            namesh))
                        if ok:
                            newname, ok = QInputDialog.getText(self,
                                                               'New Model',
                                                               'New Model name:')
                            if ok and self.check_newname(newname, liste):

                                sql = "ALTER SCHEMA {0} RENAME TO {0}_tmp".format(
                                    namesh)
                                self.mdb.run_query(sql)
                                sql = ''
                                if self.mdb.import_schema(file, old=True):
                                    self.add_info('Import is done.')
                                    sql = "ALTER SCHEMA {0} RENAME TO {1};\n".format(
                                        namesh, newname)
                                else:
                                    self.add_info('Import failed.')
                                #
                                sql += "ALTER SCHEMA {0}_tmp RENAME TO {0};".format(
                                    namesh)
                                self.mdb.run_query(sql)
                            else:
                                self.add_info('Import cancel.')
                                return
                        else:
                            self.add_info('Import cancel.')
                            return
                    else:
                        if self.mdb.import_schema(file, old=True):
                            self.add_info('Import is done.')
                        else:
                            self.add_info('Import failed.')
                else:
                    if self.mdb.import_schema(file, old=True):
                        self.add_info('Import is done.')
                    else:
                        self.add_info('Import failed.')
            else:
                self.add_info('File not found.')

        return

    def main_graph(self):
        """ GUI graphique"""

        canvas = self.iface.mapCanvas()
        self.coucheProfils = None
        self.profil = self.ui.actionCross_section.isChecked()
        self.hydrogramme = self.ui.actionHydrogramme.isChecked()
        self.profil_result = self.ui.actionCross_section_results.isChecked()
        self.basin_result = self.ui.actionBasin.isChecked()
        self.profil_z = self.ui.actionGraphRes.isChecked()

        # prevents use of other graphic button
        self.ui.actionHydrogramme.setEnabled(True)
        self.ui.actionCross_section.setEnabled(True)
        self.ui.actionCross_section_results.setEnabled(True)
        self.ui.actionBasin.setEnabled(True)
        self.ui.actionGraphRes.setEnabled(True)

        if self.profil:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section_results.setEnabled(False)
            self.ui.actionBasin.setEnabled(False)
            self.ui.actionGraphRes.setEnabled(False)
        elif self.hydrogramme:
            self.ui.actionCross_section_results.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)
            self.ui.actionBasin.setEnabled(False)
            self.ui.actionGraphRes.setEnabled(False)
        elif self.profil_result:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)
            self.ui.actionBasin.setEnabled(False)
            self.ui.actionGraphRes.setEnabled(False)
        elif self.basin_result:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)
            self.ui.actionCross_section_results.setEnabled(False)
            self.ui.actionGraphRes.setEnabled(False)
        elif self.profil_z:
            self.ui.actionHydrogramme.setEnabled(False)
            self.ui.actionCross_section.setEnabled(False)
            self.ui.actionCross_section_results.setEnabled(False)
            self.ui.actionBasin.setEnabled(False)

        self.prev_tool = canvas.mapTool()
        self.map_tool = IdentifyFeatureTool(self)
        try:  # qgis2
            QObject.connect(self.map_tool, SIGNAL('geomIdentified'),
                            self.do_something)
        except Exception:  # qgis3
            self.map_tool.changedRasterResults.connect(self.do_something)

        canvas.setMapTool(self.map_tool)

    def windinfo(self, txt, title='Informations'):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setWindowIcon(QIcon(
            os.path.join(os.path.join(self.masplugPath, 'icones'),
                         'icon_base.png')))
        msg.setText(txt)
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()

    def about(self):
        val = read_version(self.masplugPath)
        # TODO get "about" info of file
        txt = u"""
Plugin dedicated to the building and exploitation of Mascaret models.

Requires PostgreSQL and PostGIS.

Developed by Mehdi-Pierre DAOU, Christophe COULET, Aurelien PERRIN (Artelia),
With contribution of Philippe BAGOT (Cerema) for storage area,
Based on an initial version developped by Matthieu NICOLAS (SPC Maine Loire aval)
Some parts are based on the RiverGIS plugin developped by Radek Pasiok & Lukasz Debek 
(Many thanks for the work they've done on RiverGis).


Version : {}
           """.format(val)
        self.windinfo(txt, title='About')

    def website(self):
        pass
        # TODO

    def wikisite(self):
        import webbrowser
        webbrowser.open('https://github.com/Artelia/Mascaret/wiki')

    #  *******************************
    #    Water Quality
    # *******************************
    def fct_tracer_laws(self):
        dlg = ClassTracerLawsDialog(self)
        dlg.exec_()

    def fct_parameters_wq(self):
        dlg = ClassWaterQualityDialog(self)
        dlg.exec_()

    def fct_event_obs(self):
        dlg = ClassEventObsDialog(self)
        dlg.exec_()

    def fct_export_tracer_files(self):
        folder_name_path = QFileDialog.getExistingDirectory(self,
                                                            "Choose a folder")

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
        except Exception:
            self.add_info('Export failed.')

    # *******************************
    #    Structures
    # *******************************
    def fct_structures(self):
        dlg = ClassStructureDialog(self)
        dlg.setModal(False)
        dlg.exec_()

    def fct_mv_dam(self):
        """ Running GUI of movable dam"""

        dlg = ClassMobilSingDialog(self)
        dlg.exec_()

    def fct_creat_run(self):
        """
        model creation to run with api
        :return:
        """

        case, ok = QInputDialog.getItem(None,
                                        'Study case',
                                        'Kernel',
                                        self.listeState, 0, False)
        if ok:
            self.add_info(
                "Kernel {}".format(self.Klist[self.listeState.index(case)]))
            run = "test"
            rep_run = os.path.join(self.masplugPath, "mascaret_copy")
            clam = ClassMascaret(self, rep_run=rep_run)
            clam.mascaret(self.Klist[self.listeState.index(case)], run,
                          only_init=True)

            with open(os.path.join(clam.dossierFileMasc, 'FichierCas.txt'),
                      'w') as fichier:
                fichier.write("'mascaret.xcas'\n")
            self.export_run(clam)
            clam.del_folder_mas()

    def import_resu_model(self):
        """
        import resultats
        :return:
        """
        clam = ClassMascaret(self)
        dlg = ClassImportRes(clam)
        dlg.exec_()
        if dlg.complet:
            clam.import_results(dlg.run, dlg.scen, dlg.comments, dlg.path_model,
                                date_debut=dlg.date)
        del dlg
        del clam

    def fct_test(self):
        """ Test function"""
        # get_laws
        self.chkt.debug_update_vers_meta(version='4.0.10')
        #self.mdb.correction_seq()
        
        pass

    def update_pk(self):
        """
        update the abscissa
        :return:
        """
        from .ClassUpdatePk import ClassUpdatePk
        dlg = ClassUpdatePk(self, self.iface)
        dlg.exec_()

    def download_bin(self):
        """ download the Mascaret executable """
        # url git
        url_base = 'https://raw.githubusercontent.com/Artelia/Exe_Mascaret/'

        # branch_test
        branch = 'master'
        url_path = posixpath.join(url_base, branch)

        cl_load = ClassDownloadMasc(self.masplugPath, url_path, self)
        dico = {'bin': ['mascaret.exe',
                        'mascaret_linux']}

        cl_load.download_dir(dico)

    def fct_scores(self):
        dlg = ClassScoresDialog(self)
        dlg.exec_()
        # dlg.show()

    def fct_hydro_laws(self):
        dlg = ClassHydroLawsDialog(self)
        dlg.exec_()
