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
                        self.tw_runs.setItemWidget(self.child[run][scen], 1,
                                                   lbl)

                        maxi = max(maxi, date)
                        lbl = QLabel(comments)
                        self.tw_runs.setItemWidget(self.child[run][scen], 2,
                                                   lbl)
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
                        self.tw_runs.setItemWidget(self.child[run][scen], 1,
                                                   lbl)

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
        if self.cb_all_exp_res.isChecked():
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
        if file != '':
            # self.mdb.export_model(selection,file)
            plug_ver = read_version(self.mgis.masplugPath)
            self.mgis.task_exp = QgsTask.fromFunction('Export Schema',
                                                      self.task_export,
                                                      on_finished=self.completed,
                                                      tup=(selection, file,
                                                           plug_ver))
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
        self.mdb.ignor_schema = list()
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
        self.mdb.export_model(selection, file, plug_ver)
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
                                                        os.path.join(
                                                            QDir.homePath(),
                                                            self.mdb.SCHEMA),
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

        self.jsfile = None
        self.metadict = None
        self.checkdict = {
            'ver_plug': None,
            'updat_plug': False,
            'updat_db': False,
            'pgsql_version': None,
            'updat_pgsql': False,
            'schema_name': None,
            'exist_schema': False,
            'err': 0
        }
        self.bool_ver_plug = True
        self.bool_ver_postgres = True
        self.bool_name_schema = True

        self.init_gui()

    def init_gui(self):
        """
            initialisation GUI
        """
        chkt = CheckTab(self, self.mdb)
        self.list_ver = chkt.list_hist_version
        # self.list_ver = [int(v.replace('.','')) for v in self.list_ver]
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
        self.metadict = None
        if os.path.isfile(txt):
            self.read_meta(txt)
            self.fill_gui()
        else:
            self.clean_gui()

    def get_file(self):
        """
        Get file name
        :return:
        """
        file_name_path, _ = QFileDialog.getOpenFileName(None,
                                                        'File Selection',
                                                        QDir.homePath(),
                                                        filter="JSON (*.json);File (*)")
        if file_name_path != '':
            self.txt_file.setText(file_name_path)

    def read_meta(self, filein):
        """
        Read meta data file
        and fill the GUI
        :param filein:
        :return:
        """
        with open(filein, 'r') as file:
            self.metadict = json.load(file)

    def clean_gui(self):
        """
             clean gui
             :return:
             """
        self.txt_shem.setText('')
        self.txt_vplug.setText('')
        self.txt_vpgsql.setText('')

    def fill_gui(self):
        """
        fill_gui
        :return:
        """
        self.txt_shem.setText(self.metadict["schema_name"])
        self.txt_vplug.setText(self.metadict["plugin_version"])
        self.txt_vpgsql.setText('.'.join(
            [str(v) for v in
             self.conv_ver_psql(self.metadict["pgsql_version"])])
        )

        if self.check_metadata():
            self.check_ver_plug()
            self.check_name_schema()
            self.check_ver_postgres()

        self.txt_vplug.setStyleSheet('color: green')
        self.txt_vpgsql.setStyleSheet('color: green')
        self.txt_shem.setStyleSheet('color: green')

        if self.checkdict['updat_plug']:
            self.txt_vplug.setStyleSheet('color: red')
        elif self.checkdict['updat_db']:
            self.txt_vplug.setStyleSheet('color: orange')
        if self.checkdict['updat_pgsql']:
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

    def check_metadata(self):
        """
        check metadata file
        :return:
        """
        if self.metadict is None:
            self.checkdict['err'] = 2
            return False
        else:
            self.checkdict['err'] = 0
            return True

    def check_ver_plug(self):
        """
        Fill  checkdict
        :return: True if import is possible if not False
        """
        self.checkdict['updat_db'] = False
        self.checkdict['updat_plug'] = False
        vplug = [int(v) for v in self.metadict["plugin_version"].split('.')]
        maxv = self.list_ver[-1]
        maxv = [int(v) for v in maxv.split('.')]
        if maxv == vplug:
            return True
        elif self.compa_ver(vplug, maxv):
            self.checkdict['updat_plug'] = True
            return False
        # check in list
        for val in self.list_ver:
            elem = [int(v) for v in val.split('.')]
            if elem == vplug:
                self.checkdict['updat_db'] = True
                return True
        self.checkdict['err'] = 1
        return False

    def check_ver_postgres(self):
        """
        check version of postgres
        :return:
        """
        self.checkdict['updat_pgsql'] = False
        vpsql = self.conv_ver_psql(self.metadict["pgsql_version"])
        vdb = self.conv_ver_psql(self.checkdict["pgsql_version"])
        if not self.compa_ver(vdb, vpsql):
            self.checkdict['updat_pgsql'] = True

    def conv_ver_psql(sefl, ver):
        """
        Convert psql version in list
        :param ver: format of the psql version
        :return: the version in list
        """
        strlst = []
        wow = []
        for i, val in enumerate(ver):
            wow.append(val)
            if val == '0':
                if i < len(ver) - 1:
                    if ver[i + 1] != '0':
                        strlst.append(wow[:-1])
                        wow = []
        strlst.append(wow)
        lst_v = []
        for val in strlst:
            wow = int(''.join(val))
            lst_v.append(wow)
        return lst_v

    def compa_ver(self, vdb, vmeta):
        """
        Comparaison of version
        :param vdb: version of database
        :param vmeta:  version of importation
        :return: True if  vdb >= vmeta
        """
        cond = False
        if vdb[0] > vmeta[0]:
            cond = True
        else:

            if vdb[1] > vmeta[1] and vdb[0] == vmeta[0]:
                cond = True
            else:
                if vdb[2] >= vmeta[2] \
                        and vdb[0] == vmeta[0] \
                        and vdb[1] == vmeta[1]:
                    cond = True
        return cond

    def check_name_schema(self):
        """ check if name exists yet"""
        self.checkdict['exist_schema'] = False
        lst_schema = self.mdb.list_schema()
        if self.metadict["schema_name"] in lst_schema:
            self.checkdict['exist_schema'] = True

    def import_db(self):
        """
        import of database
        :return:
        """
        txt = self.txt_file.text()
        if txt != '' and os.path.isfile(txt):
            self.jsfile = txt
        else:
            QMessageBox.warning(None, 'Warning',
                                "Please enter a valid filename?")
            return

        dir = os.path.dirname(self.jsfile)
        file_name = os.path.splitext(os.path.basename(self.jsfile))[0]
        psqlfile = os.path.join(dir, file_name + '.psql')
        if not os.path.isfile(psqlfile):
            QMessageBox.critical(None, 'Error',
                                 "Not found {}".format(psqlfile))
            return

            # Impossible to import
        bool_import = True
        if self.checkdict['err'] > 0:
            bool_import = False
            # import impossible
            txt = ''
            if self.checkdict['err'] == 2:
                txt = "Metafile isn't right."
            QMessageBox.critical(None, 'Erreur',
                                 "Import isn't possible.\n {}".format(txt))
            return
        elif self.checkdict['updat_plug']:
            bool_import = False
            QMessageBox.critical(None, 'Erreur',
                                 "Import isn't possible, because the Plugin version is superior.")
            return
        elif self.checkdict['updat_pgsql']:
            # import impossible
            bool_import = False
            QMessageBox.critical(None, 'Erreur',
                                 "Import isn't possible, because the Postgres version is superior.")
            return

        # change name
        if self.checkdict['exist_schema']:
            bool_import = False
            while not bool_import:
                rep = QMessageBox.question(self, 'MessageBox',
                                           "The {} schema already exists.\n "
                                           "Do you want overwrite the schema ?".format(
                                               self.metadict["schema_name"]),
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
                        if not self.checkdict['exist_schema']:
                            bool_import = True
                    else:
                        bool_import = False
                else:
                    return

        if bool_import:
            self.metadict['jsfile'] = self.jsfile
            self.metadict['psqlfile'] = psqlfile
            self.mgis.task_imp = QgsTask.fromFunction('Import Schema',
                                                      self.task_import,
                                                      on_finished=self.completed,
                                                      tup=None)
            self.mgis.task_imp.taskCompleted.connect(self.del_task_imp)
            self.mgis.task_imp.taskTerminated.connect(self.del_task_imp)
            QgsApplication.taskManager().addTask(self.mgis.task_imp)
            self.accept()

        return

    def del_task_imp(self):
        """
        Clean tastk_mas variable
        :return:
        """
        del self.mgis.task_imp
        self.mgis.task_imp = None

    def completed(self, exception):
        """this is called when run is finished. Exception is not None if run
        raises an exception. Result is the return value of run."""
        message_category = 'My tasks from a function'
        self.mdb.ignor_schema = list()
        if exception is None:
            QgsMessageLog.logMessage(
                'task completed',
                message_category, Qgis.Info)
        else:
            QgsMessageLog.logMessage("Exception: {}".format(exception),
                                     message_category, Qgis.Critical)
            raise exception

    def task_import(self, task, tup=None):

        self.mdb.import_model(self.metadict)
        return

    def annule(self):
        """"Cancel """
        self.close()
