import threading
import os
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from qgis.core import QgsTask
import copy
import csv
import datetime
import gc
import json
import os
import re
import shutil
import subprocess
import sys
import json
import gc
import numpy as np
import copy

from .Function import TypeErrorModel
from .Function import del_symbol
from .Function import str2bool, del_accent, copy_dir_to_dir
from .Graphic.ClassResProfil import ClassResProfil
from .HydroLawsDialog import dico_typ_law
from .Structure.ClassMascStruct import ClassMascStruct
from .Structure.ClassPostPreFG import ClassPostPreFG
from .WaterQuality.ClassMascWQ import ClassMascWQ
from .api.ClassAPIMascaret import ClassAPIMascaret
from .ui.custom_control import ClassWarningBox
from ClassMessage import ClassMessage

from ClassCreatFilesModels import ClassCreatFilesModels
import time

MESSAGE_CATEGORY ='TaskMascComput'

class TaskMascComput(QgsTask):
    message = pyqtSignal(str)
    error_sim = pyqtSignal(str)

    def __init__(self,cl_mas, init_task, mdb,cond_api, cpt_init = False):
        super().__init__()
        self.cl_mas = cl_mas
        self.init_task = init_task
        self.mdb = mdb
        self.cpt_init = cpt_init
        self.id_run = None
        self.cond_api =  cond_api
        self.save_res_struct = None
        # precedent task
        self.par = None
        self.noyau = None
        self.scen = None
        self.dossier_file_masc = None
        self.base_name  = None

        # Task info
        self.exc_start_time = time.time()
        self.description = 'Computing model'

    def write_mess(self, obj):
        txt = obj.message()
        obj.clear_derror()
        return txt

    def get_precedent_task(self):
        self.init_task.waitForFinished()
        self.par = self.init_task.par
        self.noyau = self.init_task.noyau
        self.scen = self.init_task.scen
        self.dossier_file_masc = self.init_task.dossier_file_masc
        self.base_name = self.init_task.base_name


    def run_mascaret(self):
        if self.cpt_init :
            sceninit = self.scen + "_init"
            self.id_run = self.insert_id_run(self.run, sceninit)
            self.lance_mascaret(self.base_name + "_init.xcas", self.id_run)

        else:
            cond_casier = False
            if self.par["presenceCasiers"] and self.noyau == "unsteady":
                cond_casier = True

            self.id_run = self.insert_id_run(self.run, self.scen)
            finish = self.lance_mascaret(
                self.base_name + ".xcas", self.id_run, self.par["presenceTraceurs"], cond_casier
            )
            if not finish:
                self.mgis.add_info()
                self.mess.add_mess("ErrSim", 'Warning', "Simulation error")
                self.error_sim.emit(self.write_mess(self.mess))
                self.taskTerminated.emit()
                return

    def lance_mascaret(self, fichier_cas, id_run, tracer=False, casier=False):
        """
        Run mascaret
        :param fichier_cas:
        :param id_run:
        :param tracer:
        :param casier:
        :return:
        """
        os.chdir(self.dossier_file_masc)
        with open("FichierCas.txt", "w") as fichier:
            fichier.write("'" + fichier_cas + "'\n")
        if not self.cond_api:
            test = sys.platform
            if "linux" in test or test == "cygwin":
                soft = "./mascaret_linux"
            elif test == "win32":
                soft = "mascaret.exe"
            else:
                txt =("{0} platform  doesn't allow to run simulation.".format(test))
                self.mess.add_mess('ErrPlatform', 'critic',  txt)
                return False

            # Linux(2.x and 3.x) ='linux2' or 'linux'
            # Windows = 'win32'
            # Windows / Cygwin = 'cygwin'

            p = subprocess.Popen(
                soft,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            p.wait()
            txt = "{0}".format(p.communicate()[0].decode("utf-8"))
            txt1 = "{0}".format(p.communicate()[1].decode("utf-8"))
            self.mess.add_mess('InfoRun', 'info', txt)
            self.mess.add_mess('InfoRun1', 'info', txt1)
            return True
        else:
            pwd = os.getcwd()
            os.chdir(self.dossier_file_masc)
            clapi = ClassAPIMascaret(self.cl_mas)
            clapi.main(fichier_cas, tracer, casier)
            self.save_res_struct = (copy.deepcopy(clapi.results_api), id_run)
            del clapi

            os.chdir(pwd)
            return True




    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        """
        exc_fin_time = time.time()
        total = exc_fin_time - self.exc_start_time
        if result:
            txt_mess = 'Task "{name}" completed\nTotal time: {total} s'.format(name=self.description, total=total)
            QgsMessageLog.logMessage(txt_mess,MESSAGE_CATEGORY, Qgis.Success)
        else:
            txt_mess = 'Task "{name}" echec\nTotal time: {total} s'.format(name=self.description, total=total)
            QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Critical)

    def cancel(self):
        exc_fin_time = time.time()
        total = exc_fin_time - self.exc_start_time
        txt_mess = 'Task "{name}" was canceled \nTask time: {total} s'.format(name=self.description, total=total)
        QgsMessageLog.logMessage(txt_mess, MESSAGE_CATEGORY, Qgis.Warning)
        super().cancel()
