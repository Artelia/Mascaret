
from PyQt5.QtCore import pyqtSignal
from qgis.core import QgsTask

from ClassMessage import ClassMessage

from ClassGetResults import ClassGetResults
from ClassCreatFilesModels import ClassCreatFilesModels
import time

MESSAGE_CATEGORY ='TaskMascPost'

class TaskMascPost(QgsTask):
    message = pyqtSignal(str)

    def __init__(self, comput_task, mdb, dict_scen,
                 basename,  comments):
        super().__init__()
        self.comput_task = comput_task
        self.mdb = mdb
        self.basename = basename
        self.comments = comments
        self.dossier_file_masc = None
        self.dict_scen = dict_scen

        self.mess = ClassMessage()


        # Task info
        self.exc_start_time = time.time()
        self.description = 'Computing model'

    def write_mess(self, obj):
        txt = obj.message()
        obj.clear_derror()
        return txt

    def get_precedent_task(self):
        self.comput_task.waitForFinished()

        self.date_debut = self.comput_task.date_debut
        self.par = self.comput_task.par
        self.noyau = self.comput_task.noyau
        self.scen = self.comput_task.scen
        self.cpt_init = self.comput_task.cpt_init
        self.id_run = self.comput_task.id_run
        self.cond_api = self.comput_task.cond_api
        self.save_res_struct = self.comput_task.save_res_struct

        self.cls_res = ClassGetResults(self.mdb)
        self.clfile = ClassCreatFilesModels(self.mdb, self.dossier_file_masc)


    def run_post(self):

        self.get_precedent_task()
        # RUN Model
        if self.cpt_init:
            self.cls_res.lit_opt_new(self.id_run, None, self.basename + "_init", self.comments,
                                     cond_api=self.cond_api, save_res_struct = self.save_res_struct)
            self.clfile.opt_to_lig(self.id_run, self.basename)
            tab = {
                "LigEauInit": {
                    "valeur": "true",
                    "balise1": "parametresConditionsInitiales",
                    "balise2": "ligneEau",
                }
            }
            self.clfile.modif_xcas(tab, self.basename + ".xcas")
        else:
            cond_casier = False
            if self.par["presenceCasiers"] and  self.noyau == "unsteady":
                cond_casier = True
            self.cls_res.lit_opt_new(
                self.id_run, self.date_debut, self.basename, self.comments,
                self.par["presenceTraceurs"], cond_casier,
                self.cond_api, self.save_res_struct)

            if self.check_mobil_gate():
                self.cls_res.read_mobil_gate_res(self.id_run)

    def check_mobil_gate(self):
        """
        check if weirs active
        :return:
        """
        info = self.mdb.select(
            "weirs", where="active_mob = true", list_var=["method_mob", "gid", "name"]
        )
        if info:
            if len(info["gid"]) > 0:
                return True

        return False

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
