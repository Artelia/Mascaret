import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtGui import QIcon
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from qgis.PyQt.QtWidgets import *
from datetime import datetime


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



        self.ui.b_export.clicked.connect(self.export)
        self.ui.b_cancel.clicked.connect(self.annule)

    def export(self):
        """export results selected"""
        selection = {}
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
                                                         filter="PSQL (*.psql);;File (*)")
        if self.mdb.check_extension():
            self.mgis.add_info(" Shema est {}".format(self.mdb.SCHEMA))
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