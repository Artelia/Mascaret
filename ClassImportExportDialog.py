import os
import json
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtGui import QIcon
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from qgis.PyQt.QtWidgets import *
from datetime import datetime
from .Function import read_version
from .db.Check_tab import CheckTab

class ClassDlgExport(QDialog):
    """
    Class allow to export schema
    """
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_export.ui'), self)

        self.listeRuns = []
        self.listeScen = {}
        self.init_gui()

    def init_gui(self):
        """
            initialisation GUI
        """
        liste_col = self.mdb.list_columns('runs')
        self.cond_com = ('comments' in liste_col)

        dico = self.mdb.select("runs", "", "date")

        if self.cond_com:
            for run, scen, date, comments in zip(dico["run"], dico["scenario"],
                                                 dico["date"],
                                                 dico["comments"]):
                if run not in self.listeRuns:
                    self.listeRuns.append(run)
                    self.listeScen[run] = []
                self.listeScen[run].append((scen, date, comments))
        else:
            for run, scen, date in zip(dico["run"], dico["scenario"],
                                       dico["date"]):
                if run not in self.listeRuns:
                    self.listeRuns.append(run)
                    self.listeScen[run] = []
                self.listeScen[run].append((scen, date))

        if len(self.listeRuns) > 0:
            self.parent = {}
            self.child = {}

            for run in self.listeRuns:
                self.parent[run] = QTreeWidgetItem(self.tw_runs)
                self.parent[run].setText(0, run)
                self.parent[run].setFlags(self.parent[run].flags() |
                                          Qt.ItemIsTristate |
                                          Qt.ItemIsUserCheckable)

                lbl = QLabel('')
                self.tw_runs.setItemWidget(self.parent[run], 2, lbl)

                self.child[run] = {}
                maxi = datetime(1900, 1, 1, 0, 0)
                if self.cond_com:
                    for scen, date, comments in self.listeScen[run]:
                        self.child[run][scen] = QTreeWidgetItem(
                            self.parent[run])
                        self.child[run][scen].setFlags(
                            self.child[run][scen].flags() |
                            Qt.ItemIsUserCheckable)
                        self.child[run][scen].setText(0, scen)

                        self.child[run][scen].setCheckState(0, Qt.Unchecked)

                        lbl = QLabel("{:%d/%m/%Y %H:%M}".format(date))
                        self.tw_runs.setItemWidget(self.child[run][scen], 1, lbl)

                        maxi = max(maxi, date)
                        lbl = QLabel(comments)
                        self.tw_runs.setItemWidget(self.child[run][scen], 2, lbl)
                else:
                    for scen, date in self.listeScen[run]:
                        self.child[run][scen] = QTreeWidgetItem(
                            self.parent[run])
                        self.child[run][scen].setFlags(
                            self.child[run][scen].flags() |
                            Qt.ItemIsUserCheckable)
                        self.child[run][scen].setText(0, scen)

                        self.child[run][scen].setCheckState(0, Qt.Unchecked)

                        lbl = QLabel("{:%d/%m/%Y %H:%M}".format(date))
                        self.tw_runs.setItemWidget(self.child[run][scen], 1, lbl)

                        maxi = max(maxi, date)

                lbl = QLabel("{:%d/%m/%Y %H:%M}".format(maxi))
                self.tw_runs.setItemWidget(self.parent[run], 1, lbl)

        self.b_export.clicked.connect(self.export)
        self.b_cancel.clicked.connect(self.annule)
        self.cb_all_exp_res.stateChanged.connect(self.state_changed)

    def state_changed(self):
        """

        :return:
        """
        if  self.cb_all_exp_res.isChecked():
            self.tw_runs.setEnabled(False)
        else:
            self.tw_runs.setEnabled(True)

    def export(self):
        """export results selected"""
        selection = {}
        if self.cb_all_exp_res.isChecked():
            for run in self.listeRuns:
                selection[run] = []
                for tple in self.listeScen[run]:
                    selection[run].append("'{}'".format(tple[0]))
        else:
            for run in self.listeRuns:
                if self.parent[run].checkState(0) > 0:
                    selection[run] = []
                    if self.cond_com:
                        for scen, date, comments in self.listeScen[run]:
                            if self.child[run][scen].checkState(0) > 1:
                                selection[run].append("'{}'".format(scen))
                    else:
                        for scen, date in self.listeScen[run]:
                            if self.child[run][scen].checkState(0) > 1:
                                selection[run].append("'{}'".format(scen))

        file = self.choix_file()
        if file !='':
            #self.mdb.export_model(selection,file)
            plug_ver = read_version(self.mgis.masplugPath)
            self.mgis.task_exp = QgsTask.fromFunction('Export Schema',
                                                      self.task_export,
                                                      on_finished=self.completed,
                                                      tup=(selection,file,plug_ver))
            self.mgis.task_exp.taskCompleted.connect(self.del_task_exp)
            self.mgis.task_exp.taskTerminated.connect(self.del_task_exp)
            QgsApplication.taskManager().addTask(self.mgis.task_exp)

            self.accept()
        else:
            return

    def del_task_exp(self):
        """
        Clean tastk_mas variable
        :return:
        """
        del self.mgis.task_exp
        self.mgis.task_exp = None

    def completed(self, exception):
        """this is called when run is finished. Exception is not None if run
        raises an exception. Result is the return value of run."""
        message_category = 'My tasks from a function'
        if exception is None:
            QgsMessageLog.logMessage(
                'task completed',
                message_category, Qgis.Info)
        else:
            QgsMessageLog.logMessage("Exception: {}".format(exception),
                                     message_category, Qgis.Critical)
            raise exception

    def task_export(self, task, tup=None):
        if tup:
            selection, file, plug_ver = tup
        else:
            print('no transmitted variable')
            return
        self.mdb.export_model(selection, file,plug_ver)
        return

    def annule(self):
        """"Cancel """
        self.close()

    def choix_file(self):
        """
        Database Export function
        :param self:
        :return:
        """
        # choix du fichier d'exportatoin

        file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                        os.path.join(QDir.homePath(),self.mdb.SCHEMA),
                                                        filter="JSON (*.json)")
        return file_name_path


class ClassDlgImport(QDialog):
    """
    Class allow to export schema
    """
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.iface = iface
        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/ui_import.ui'), self)

        self.jsfile =  None
        self.metadict = None
        self.checkdict = {
            'ver_plug': None,
            'updat_plug': False,
            'updat_db': False,
            'pgsql_version': None,
            'updat_pgsql': False,
            'schema_name': None,
            'exist_schema' : False,
            'err' : 0
        }
        self.bool_ver_plug = True
        self.bool_ver_postgres= True
        self.bool_name_schema = True

        self.init_gui()

    def init_gui(self):
        """
            initialisation GUI
        """
        chkt = CheckTab(self, self.mdb)
        self.list_ver = chkt.list_hist_version
        self.list_ver = [int(v.replace('.','')) for v in self.list_ver]
        self.checkdict['ver_plug'] = read_version(self.mgis.masplugPath)
        self.checkdict["pgsql_version"] = self.mdb.version_postgres()
        self.txt_file.textChanged[str].connect(self.change_file)
        self.btn_open_file.clicked.connect(self.get_file)
        self.btn_cancel.clicked.connect(self.annule)
        self.btn_valid.clicked.connect(self.import_db)

    def change_file(self):
        """
        check text
        :return:
        """
        txt = self.txt_file.text()
        if os.path.isfile(txt):
            self.read_meta(txt)
            self.fill_gui()


    def get_file(self):
        """
        Get file name
        :return:
        """
        file_name_path, _ = QFileDialog.getOpenFileName(None,
                                                         'File Selection',
                                                          QDir.homePath(),
                                                         filter="JSON (*.json);File (*)")
        if file_name_path != '' :
            self.txt_file.setText( file_name_path)

    def read_meta(self, filein) :
        """
        Read meta data file
        and fill the GUI
        :param filein:
        :return:
        """
        with open(filein,'r') as file:
            self.metadict = json.load(file)

    def fill_gui(self):
        """
        fill_gui
        :return:
        """
        self.txt_shem.setText(self.metadict["schema_name"])
        self.txt_vplug.setText(self.metadict["plugin_version"])
        self.txt_vpgsql.setText(self.metadict["pgsql_version"].replace('0','.'))

        self.check_ver_plug()
        self.check_name_schema()
        self.check_ver_postgres()

        self.txt_vplug.setStyleSheet('color: green')
        self.txt_vpgsql.setStyleSheet('color: green')
        self.txt_shem.setStyleSheet('color: green')

        if self.checkdict['updat_plug']:
            self.txt_vplug.setStyleSheet('color: red')
        elif self.checkdict['updat_db'] :
            self.txt_vplug.setStyleSheet('color: orange')
        if self.checkdict['updat_pgsql'] :
            self.txt_vpgsql.setStyleSheet('color: red')
        if self.checkdict['exist_schema']:
            self.txt_shem.setStyleSheet('color: orange')
        if self.checkdict['err'] > 0:
            txt = 'There is erreur in the metadata file (.json)\n'
            if self.checkdict['err'] == 1:
                txt += "The plugin version doesn't exist."
                self.txt_vplug.setStyleSheet('color: red')

            QMessageBox.critical(None, 'Erreur',
                                 txt)


    def check_ver_plug(self):
        """
        Fill  checkdict
        :return: True if import is possible if not False
        """
        vplug = int(self.metadict["plugin_version"].replace('.',''))
        self.checkdict['updat_plug'] = False
        self.checkdict['updat_db'] = False
        if vplug > max(self.list_ver):
            #update plug
            self.checkdict['updat_plug'] = True
            return  False
        elif vplug == max(self.list_ver):
            return True
        else:
            if vplug  in self.list_ver:
                # update data base
                self.checkdict['updat_db'] = True
                return True
            else:
                self.checkdict['err'] = 1
                return False

    def check_ver_postgres(self):
        vpsql  = int(self.metadict["plugin_version"].replace('.', ''))
        vdb = int(self.checkdict["pgsql_version"])
        if vdb >= vpsql:
            self.checkdict['updat_pgsql'] = False
        else:
            self.checkdict['updat_pgsql'] = True

    def check_name_schema(self):
        """ check if name exists yet"""
        lst_schema = self.mdb.list_schema()
        if self.metadict["schema_name"] in lst_schema :
            self.checkdict['exist_schema'] = True
        else:
            self.checkdict['exist_schema']= False

    def import_db(self):
        txt = self.txt_file.text()
        print('rrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
        if txt != '':
            self.jsfile = txt
        else :
            QMessageBox.warning(None, 'Warning',
                                "Please enter a filename?")
            return

        # Impossible to import
        bool_import = True
        if self.checkdict['err']>0 :
            bool_import = False
            # import impossible
            QMessageBox.warning(None, 'Erreur',
                                "Import isn't possible.")
            return
        elif self.checkdict['updat_pgsql']:
            # import impossible
            bool_import = False
            QMessageBox.warning(None, 'Erreur',
                                "Import isn't possible, because the Postgres version is superior.")
            return
        # change name
        if self.checkdict['exist_schema']:
            bool_import = False
            while not bool_import :
                rep = QMessageBox.question(self, 'MessageBox',
                                             "The {} schema already exists.\n "
                                             "Do you want overwrite the schema ?".format(
                                                 self.metadict["schema_name"])    ,
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                                           QMessageBox.Cancel)

                if rep == QMessageBox.Yes:
                    bool_import = True
                elif rep == QMessageBox.No:
                    newname, ok = QInputDialog.getText(self,
                                                       'new Model',
                                                       'Change the name of new model:')
                    if ok and newname != '':
                        self.metadict["schema_name"] = newname
                        self.check_name_schema()
                        if not self.checkdict['exist_schema'] :
                            bool_import = True
                    else:
                        bool_import = False
                else:
                    return


        if bool_import:
            self.metadict['jsfile'] = self.jsfile
            self.mdb.import_model(self.metadict)
            self.accept()

        return

    def annule(self):
        """"Cancel """
        self.close()



class ClassImportExportDialog :
    """ class of import and export of database """
    def __init__(self, parent):
        self.mgis = parent
        self.mdb =  self.mgis.mdb
        self.masplugPath = self.mgis.masplugPath
        self.box = self.mgis.box
        self.debug = self.mgis.DEBUG
        pass


    def export_model_old(self):
        """
        Database Export function
        :param self:
        :return:
        """
        # choix du fichier d'exportatoin

        file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile",
                                                        "{0}.psql".format(
                                                            os.path.join(
                                                                self.masplugPath,
                                                                self.mdb.dbname + "_" + self.mdb.SCHEMA)),
                                                        filter="PSQL (*.psql);;File (*)")

        if self.mdb.export_schema(file_name_path):
            self.mgis.add_info('Export is done.')
        else:
            self.mgis.add_info('Export failed.')


    def import_model_old(self):
        """
        Database Import function
        :param self:
        :return:
        """

        file_name_path, _ = QFileDialog.getOpenFileNames(None,
                                                         'File Selection',
                                                         self.masplugPath,
                                                         filter="PSQL (*.psql);File (*)")
        if self.mdb.check_extension():
            self.mgis.add_info(" Shema est {}".format(self.mdb.SCHEMA))
            self.mdb.add_ext_postgis()

        for file in file_name_path:
            if os.path.isfile(file):
                namesh = self.mdb.checkschema_import(file)
                if namesh is not None:
                    liste = self.mdb.list_schema()
                    if namesh in liste:
                        # demande change name
                        ok = self.box.yes_no_q("The {} schema already exists.\n "
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
                                if self.mdb.import_schema(file):
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

    def add_info(self,txt):
        """
        write info in GUI
        :return:
        """
        self.mgis.add_info(txt)

    def check_newname(self, name, liste):
        """
        Check the new name validation
            name : test name
            liste : exclud list
        """
        if name == '':
            if self.debug:
                self.add_info('Name is not correct.')
            return False
        elif name in liste:
            if self.debug:
                self.add_info('<<{}>> schema name already exists'.format(name))
            return False
        else:
            return True