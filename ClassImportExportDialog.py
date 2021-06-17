import os
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtGui import QIcon
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from qgis.PyQt.QtWidgets import *


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