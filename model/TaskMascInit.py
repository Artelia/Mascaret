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
import os
from qgis.core import QgsTask, QgsMessageLog, Qgis
from PyQt5.QtCore import QObject, pyqtSignal

from  ..ClassMessage import ClassMessage
import time

from .ClassCreatFilesModels import ClassCreatFilesModels
from ..Structure.ClassMascStruct import ClassMascStruct

MESSAGE_CATEGORY ='TaskMascaret'

class TaskMascInit():
    """Task of the Creating model initial files"""

    def __init__(self, glb_param, init_param):
        super().__init__()


        self.mdb =  glb_param['mdb']
        self.dossier_file_masc = glb_param['dossier_file_masc']
        self.wq = init_param['waterq']
        self.basename = glb_param['basename']
        self.noyau = glb_param['noyau']
        self.dict_scen = glb_param['dict_scen']
        self.dict_lois = init_param['dict_lois']
        self.dico_loi_struct = init_param['dico_loi_struct']
        self.scen = None
        self.idx = None
        self.par = None

        self.clfile = ClassCreatFilesModels(self.mdb, self.dossier_file_masc)
        self.clmeth = ClassMascStruct(self.mdb)
        self.mess = ClassMessage()
        self.date_debut = None

        # Task info
        self.exc_start_time = time.time()
        self.description = 'Creating model initial files'


    def update_inputs(self, up_dict):
        """
        Updating class parameters
        :param  up_dict: (dict) new parameters
        :param cpt_init : (boolean) if inialisation phase or not
        """
        self.idx = up_dict['idx']
        self.scen = up_dict['scen']
        self.par = up_dict['par']

    def maj_param(self, up_dict):
        """"
        Updating the information transfer dictionary
        :param  up_dict: (dict) transfer dictionary
        :return: (dict)
        """
        up_dict['par'] = self.par
        up_dict['date_debut'] = self.date_debut
        return  up_dict


    def exit_status_(self,obj):
        """check if critical message
        :return boolean"""
        exit_status = obj.get_critic_status()
        return exit_status

    def clean_res(self):
        """Clean the run folder and copy the essential files to run mascaret"""
        files = os.listdir(self.dossier_file_masc)
        listsup = [".opt", ".lig", ".cas_opt", ".liai_opt", ".tra_opt"]
        for i in range(0, len(files)):
            ext = os.path.splitext(files[i])[1]
            if ext in listsup:
                os.remove(os.path.join(self.dossier_file_masc, files[i]))
                txt = "delete file {}".format(files[i])
                self.log_mess(txt, 'CleanRes', 'debug')

    def log_mess(self, txt, flag, typ='info'):
        """Manage message
            :param txt : (str) text
            :param flag : (str) error flag
            :param typ :(str) message typ
        """
        self.mess.add_mess(flag, typ, txt)
        if typ ==  'warning':
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Warning)
        elif typ == 'critic':
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Critical)
        else:
            QgsMessageLog.logMessage(txt, MESSAGE_CATEGORY, Qgis.Info)

    def add_log_mess(self, obj):
        """
        Add log message to classMessage object
        :param obj : (object) ClassMessage
        """
        fill_d  = self.mess.mess_fill_other_obj(obj)
        if fill_d:
            for key, item in fill_d.items() :
                if  item['type'] == 'warning':
                    QgsMessageLog.logMessage(item['message'], MESSAGE_CATEGORY, Qgis.Warning)
                elif  item['type'] == 'critic':
                    QgsMessageLog.logMessage(item['message'], MESSAGE_CATEGORY, Qgis.Critical)
                else:
                    QgsMessageLog.logMessage(item['message'], MESSAGE_CATEGORY, Qgis.Info)

    def run(self):
        """
        Run task
        :return boolean
        """
        try :
            self.log_mess('TaskMascInit Begin', 'info1')
            self.clean_res()
            if self.dico_loi_struct.keys():
                for name in self.dico_loi_struct.keys():
                    list_final = self.clmeth.get_list_law(self.dico_loi_struct[name]["id_config"])

                    self.clmeth.create_law(
                        self.dossier_file_masc, name, self.dico_loi_struct[name]["type"], list_final
                    )
                    self.clmeth.create_law(
                        self.dossier_file_masc, name + "_init", self.dico_loi_struct[name]["type"], list_final
                    )

            # initialise Law file
            self.date_debut = None
            if self.noyau == "steady":
                exit_status = self.init_scen_steady(self.par, self.dict_lois)
            elif self.par["evenement"]:
                self.date_debut, self.par = self.init_scen_even(self.par, self.dict_lois, self.idx, self.dict_scen)
                exit_status = self.clfile.mess.get_critic_status()
            else:
                # transcritical unsteady hors evenement
                self.par = self.init_scen_trans_unsteady(self.par, self.dict_lois)
                exit_status = self.clfile.mess.get_critic_status()

            self.add_log_mess(self.clfile.mess)
            if exit_status:
                return False
            txt = "Laws file is created."
            self.log_mess(txt, "Laws")
            if self.exit_status_(self.mess):
                return False
            if self.check_mobil_gate() and self.noyau == "unsteady":
                self.clfile.create_mobil_gate_file()
                self.add_log_mess(self.clfile.mess)
                if self.exit_status_(self.clfile.mess):
                    return False

            # check error and warning:
            self.check_apport()
            if self.exit_status_(self.mess):
                return False

            if self.par["LigEauInit"] and not self.par["initialisationAuto"] and self.noyau != "steady":
                id_run_init = None
                if "id_run_init" in self.dict_scen.keys():
                    id_run_init = self.dict_scen["id_run_init"][self.idx]
                if id_run_init is None:
                    txt = "Cancel run because No initial boundaries"
                    self.log_mess(txt, "ErrInit", 'critic')
                    return False
                self.clfile.opt_to_lig(id_run_init, self.basename)
                self.add_log_mess(self.clfile.mess)
                if self.exit_status_(self.clfile.mess):
                    return False
            self.log_mess('TaskMascInit End', 'info2')
            return True
        except Exception as e:
            self.log_mess(str(e),'errInit','critic')
            return False

    def init_scen_steady(self, dict_lois):
        """
         Initial  files creation  for steady scenario
        :param par: (dict) parameters
        :param dict_lois:  (dict) laws
        :return: boolean
        """
        exit_status = False
        for nom, l in dict_lois.items():
            if "valeurperm" not in l.keys():
                continue
            if l["valeurperm"] is None:
                # dictLois.items() extremities liste
                tab = self.clfile.get_laws(nom, l["type"])
                if tab:
                    self.clfile.creer_loi(nom, tab, l["type"])
                else:
                    txt =  "The law for {} is not create.".format(nom)
                    self.log_mess(txt, "law_{}".format(nom),'critic' )
                    exit_status = True
                    return exit_status
            else:
                try:
                    liste_ = ["pasTemps", "critereArret", "nbPasTemps", "tempsMax", "tempsInit"]
                    temp_dic = {}
                    for info in liste_:
                        condition = "parametre ='{}'".format(info)
                        dtemp = self.mdb.select_distinct("steady", "parametres", condition)
                        temp_dic[info] = dtemp["steady"][0]
                except Exception as e:
                    err = "erreur crit, {}".format(str(e))
                    self.log_mess(err, "law_{}".format(nom), 'critic')
                    exit_status = True
                    return exit_status
                if temp_dic["critereArret"] == 1:
                    tfinal = temp_dic["tempsMax"]
                elif temp_dic["critereArret"] == 2:
                    tfinal = temp_dic["tempsInit"] + temp_dic["pasTemps"] * temp_dic["nbPasTemps"]
                elif temp_dic["critereArret"] == 3:
                    tfinal = 365 * 24 * 3600

                if l["type"] == 1:
                    tab = {"time": [0, tfinal], "flowrate": [l["valeurperm"]] * 2}
                # no possible to use rating curve (5) with steady.
                #   It's replaced in xcas
                elif l["type"] == 2 or l["type"] == 5:
                    l["type"] = 2
                    tab = {"time": [0, tfinal], "z": [l["valeurperm"]] * 2}
                else:
                    tab = self.clfile.get_laws(nom, l["type"])

                if tab:
                    self.clfile.creer_loi(nom, tab, l["type"])
                else:
                    txt = "The law for {} is not create.".format(nom)
                    self.log_mess(txt, "law_{}".format(nom), 'critic')
                    exit_status = True
                    return exit_status
        return exit_status

    def init_scen_even(self, par, dict_lois, idx, dict_scen):
        """
        Initial  files creation  for evenment scenario
        :param par:  (dict) parameters
        :param dict_lois: (dict) laws
        :param idx: (int) index scenario
        :param dict_scen: (dict)dictionnay of scenarii
        :return: date begin (date_debut) and parameters (par)
        """
        # transcritical unsteady evenement
        date_debut = dict_scen["starttime"][idx]
        date_fin = dict_scen["endtime"][idx]
        duree = int((date_fin - date_debut).total_seconds()) - 3600

        tab = {
            "tempsMax": {"valeur": str(duree), "balise1": "parametresTemporels"},
            "titreCalcul": {
                "valeur": dict_scen["name"][idx],
                "balise1": "parametresImpressionResultats",
            },
        }
        self.clfile.modif_xcas(tab, self.basename + ".xcas")
        par["tempsMax"] = duree
        if par["presenceTraceurs"]:
            if self.wq.dico_phy[self.wq.cur_wq_mod]["meteo"]:
                exit_status, txt = self.wq.create_filemet(typ_time="date", datefirst=date_debut, dateend=date_fin)
                if exit_status:
                    self.log_mess(txt, "WQMeteo", 'critic')

        par = self.clfile.obs_to_loi(dict_lois, date_debut, date_fin, par)

        return date_debut, par

    def init_scen_trans_unsteady(self, par, dict_lois):
        """
        Initial  files creation  for unsteady scenario
        :param par: dict contains the parameters
        :param dict_lois: dict contains the law
        :return: dict (par)
        """
        exit_satus = False
        if par["presenceTraceurs"]:
            if self.wq.dico_phy[self.wq.cur_wq_mod]["meteo"]:
                exit_status, txt = self.wq.create_filemet()
                if exit_status:
                    self.log_mess(txt, "WQMeteo", 'critic')
                    return

        for nom, l in dict_lois.items():
            # dictLois.items() extremities liste

            tab = self.clfile.get_laws(nom, l["type"])
            if tab:
                self.clfile.creer_loi(nom, tab, l["type"])
                if "time" in tab.keys():
                    initime = round(tab["time"][0], 3)
                    lasttime = round(tab["time"][-1], 3)
                    self.clfile.check_timelaw(par, nom, initime, lasttime)
            else:
                txt = "The law for {} is not create.".format(nom)
                self.log_mess(txt, 'CreatLaw_{}'.format(nom), 'warning')

            if "valeurperm" not in l.keys():
                continue

            # nom = nom + "_init"
            if l["valeurperm"] is not None:
                if l["type"] == 1:
                    tab = {"time": [0, 3600], "flowrate": [l["valeurperm"]] * 2}
                    self.clfile.creer_loi(nom, tab, 1, init=True)
                elif l["type"] == 2:
                    tab = {"time": [0, 3600], "z": [l["valeurperm"]] * 2}
                    self.clfile.creer_loi(nom, tab, 2, init=True)
                elif l["type"] in [4, 5]:
                    self.clfile.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    txt = "No initialisation because of no SteadyValue"
                    self.log_mess(txt, 'NoInitUnsteady', 'warning')
            else:
                if l["type"] in [4, 5]:
                    self.clfile.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    txt = (
                        "No initialisation because of no valeurperm " "for {} condition".format(nom)
                    )
                    self.log_mess(txt, 'NoInitUnsteady', 'warning')

        return par

    def check_apport(self):
        """checks if the inflow is before the first mesh."""
        #
        apports = self.mdb.select("lateral_inflows", "active", "abscissa")
        for i, numb in enumerate(apports["branchnum"]):
            branches = self.mdb.select_one(
                "visu_branchs",
                "branchnum={}".format(numb),
                "abs_start",
                list_var=["abs_start", "mesh"],
            )
            comp = branches["abs_start"] + branches["mesh"]
            if apports["abscissa"][i] < comp:
                err = ("{} is located before the first mesh. Ignore in the model".format(apports["name"][i]))
                self.log_mess(err, "lInflowPos_{}".format(apports["name"][i]), 'warning')


    def check_mobil_gate(self):
        """
        check if weirs active
        :return: boolean
        """
        info = self.mdb.select(
            "weirs", where="active_mob = true", list_var=["method_mob", "gid", "name"]
        )
        if info:
            if len(info["gid"]) > 0:
                return True

        return False
