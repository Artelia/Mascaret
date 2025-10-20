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
import shutil
import sys
from pathlib import Path
import traceback

from qgis.PyQt.QtWidgets import (
    QInputDialog,
    QWidget
)

from .ClassGeoWriter import ClassGeoWriter
from .ClassXcasWriter import ClassXcasWriter
from .ClassBCWriter import ClassBCWriter
from ..ClassMessage import ClassMessage

from ..Structure.ClassLinkFGParam import ClassLinkFGParam
from ..Structure.ClassMobilWeirsParam import ClassMobilWeirsParam
from ..Structure.ClassPostPreFG import ClassPostPreFG
from ..WaterQuality.ClassMascWQ import ClassMascWQ
from ..Structure.ClassMascStruct import ClassMascStruct

from ...ui.custom_control import ClassWarningBox



class ClassInitializeModel:
    """Class contain  model files creation and run model mascaret"""
    CREST_FILE = "Fichier_Crete.csv"
    STRUCT_RES_FILE = "res_struct.res"
    LINK_MOBILE_FILE = "links_cli_fg.obj"
    WEIRS_MOBILE_FILE ="weirs_cli_fg.obj"
    LIG_FILE = "mascaret.lig"
    XCAS_FILE = "mascaret.xcas"
    XCAS_INIT_FILE = "mascaret_init.xcas"

    def __init__(self, main, obj_model):
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.obj_model = obj_model
        self.dgeneral = self.obj_model.get_dgeneral()
        self.drun = self.obj_model.get_drun()
        self.par = self.obj_model.get_param_model(self.drun["kernel"])
        self.dbg = self.dgeneral['dbg']

        self.mess = ClassMessage()
        self.box = ClassWarningBox()

        folder = self.dgeneral["path_runs"]
        self.cl_geo = ClassGeoWriter(self.mdb, folder, 'mascaret', self.mess)
        self.cl_xcas = ClassXcasWriter(self.mdb, folder, self.dgeneral["api"], self.mess)
        self.cl_bc = ClassBCWriter(self.mdb, '', self.mess)
        self.clmeth = ClassMascStruct(self.mdb)
        self.wq = ClassMascWQ(self.mgis, '')

    def main(self):
        self.generate_models_folders()
        lscenar = self.obj_model.get_list_name_scenario()
        lst_idx_del = []
        for ids, scen in enumerate(lscenar):
            stat = self.mascaret_init(scen)
            if not stat:
                lst_idx_del.append(ids)
                self.box.critic(f"Similation {scen} aborted.")
                # TODO arrêt si 1 plante ?
        self.obj_model.del_lscenar(lst_idx_del)


    def generate_models_folders(self):

        tmpl_path = Path( self.dgeneral["template_path"])
        lst_copy = [tmpl_path / file for file in tmpl_path.iterdir() if file.is_file()]
        if not self.dgeneral["api"] :
            b_path = Path( self.dgeneral["binary_path"])
            if not self.check_exe():
                self.mgis.download_bin()
            lst_copy += [b_path / file for file in b_path.iterdir() if file.is_file()]
        lscenario = self.obj_model.get_lscenar()

        # Clear repertoire
        err = self.clear_folder( self.dgeneral['path_runs'], ask_confirm=self.dgeneral["has_new_run_path"])
        if err:
            self.mgis.add_info(f"ERROR : {err}", box=True, btype='CRITICAL')
            return

        for instance in lscenario:
            for key in ('path_instance', 'path_instance_init'):
                path_ = Path(instance.get(key)) if instance.get(key) else None
                if path_:
                    Path(path_).mkdir(parents=True, exist_ok=True)
                    for src in lst_copy:
                        target = path_ / src.name
                        shutil.copyfile(src, target)

    def copy_initialization_files(self, source_folder, target_folder):
        """
        Copy initialization files from source to target folder.

        Args:
            source_folder: Source directory path
            target_folder: Destination directory path

        Returns:
            bool: True if operation succeeded, False otherwise
        """
        init_file_suffixes = {'.geo', '.casier', '.loi', '.xcas'}
        init_pattern = {'.loi': '_init.loi', '.xcas': '_init.xcas'}

        source = Path(source_folder)
        target = Path(target_folder)

        # Validate source folder
        if not source.exists() or not source.is_dir():
            self.mgis.add_info(f"Invalid source folder: {source}", dbg=True)
            return False

        # Validate target folder
        if not target.exists() or not target.is_dir():
            self.mgis.add_info(f"Invalid target folder: {target}", dbg=True)
            return False

        copied_count = 0

        for file_path in source.iterdir():
            if not file_path.is_file():
                continue

            # Check if file has a valid suffix
            if file_path.suffix not in init_file_suffixes:
                continue

            # Check if file matches required pattern for specific suffixes
            required_pattern = init_pattern.get(file_path.suffix)
            if required_pattern and required_pattern not in file_path.name:
                continue

            try:
                target_path = target / file_path.name
                shutil.copy2(file_path, target_path)  # copy2 preserves metadata
                copied_count += 1
            except Exception as e:
                self.mgis.add_info(
                    f"Failed to copy file '{file_path.name}': {str(e)}",
                    dbg=True
                )
        self.mgis.add_info(f"Successfully copied {copied_count} initialization file(s)", dbg=True)
        return True

    def copy_lig(self, fichiers, folder):
        """Load .lig file in run model when exporting
        Args:
          :param fichiers: (str) path of the file to copy
        """
        try:
            shutil.copyfile(fichiers, os.path.join(folder, self.LIG_FILE))
            return False
        except Exception as e:
            self.mgis.add_info(
                f"Failed to copy file '{fichiers}': {str(e)}",
                dbg=True
            )
            return True

    def exit_cpte(self,exit_status, txt=''):
        if exit_status :
            txt_f = "Compute is cancel.\n" + txt
            self.mgis.add_info(txt_f)
        return  exit_status

    def mascaret_init(self, scen):
        """
        Initialize and prepare Mascaret model files for a scenario.

        Args:
            scen: Scenario identifier

        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        # Get scenario configuration
        self.mgis.add_info(f'*** Creation of the modeles Files for scenario {scen} ***')
        d_scen = self.obj_model.get_scenario(scen)
        model_folder = d_scen["path_instance"]
        init_folder = d_scen["path_instance_init"]
        kernel = self.drun['kernel']

        # Configure geometry, xcas, and boundary conditions handlers
        self.configure_handlers(model_folder)

        # Step 1: Create geometry files
        if not self.create_geometry_files():
            return False

        # Step 2: Create mobile structures files (links and weirs)
        if not self.create_mobile_structures(model_folder):
            return False

        # Step 3: Handle tracer configuration
        if not self.tracer_configuration(model_folder, kernel):
            return False

        # Step 4: Handle initial conditions
        if not self.initial_conditions(d_scen, model_folder):
            return False

        # Step 5: Create XCAS file and structural laws
        dict_lois, dico_loi_struct = self.cl_xcas.creer_xcas(kernel, filename=self.XCAS_FILE)
        if self.check_and_log_errors():
            return False
        # Step 5bis: FichierCas.txt
        fichier_run = os.path.join(model_folder, "FichierCas.txt")
        with open(fichier_run, "w") as fichier:
            fichier.write(f"'{self.XCAS_FILE}'\n")

        # Step 6: Create law files
        if not self.create_law_files(dico_loi_struct, model_folder, init_folder):
            return False

        # Step 7: Initialize scenario based on kernel type
        if not self.initialize_scen_by_kernel(kernel, dict_lois, d_scen):
            return False

        self.mgis.add_info("Laws file is created.")

        # TODO delete if barage only api
        # Step 8: Handle mobile gates (unsteady mode only)
        if not self.mobile_gates(kernel):
            return False

        # Step 9: Create additional files and perform checks
        self.cl_bc.creat_file_no_keep_break()
        self.cl_bc.check_apport()
        self.write_mess(self.cl_bc.mess)


        # Step 10: Finalize initialization files
        if self.drun['has_run_init']:
            self.cl_xcas.create_init_xcas(self.XCAS_INIT_FILE)
            # Step 5bis: FichierCas.txt
            fichier_run = os.path.join(init_folder, "FichierCas.txt")
            with open(fichier_run, "w") as fichier:
                fichier.write(f"'{self.XCAS_INIT_FILE}'\n")
            self.copy_initialization_files(model_folder, init_folder)
            self.purge_init_file_in_model(model_folder)

        return True

    def configure_handlers(self, folder):
        """Configure geometry, xcas, and boundary condition handlers."""
        self.cl_geo.set_folder(folder)
        self.cl_xcas.set_folder(folder)
        self.cl_bc.set_folder(folder)

    def create_geometry_files(self):
        """Create geometry reference and casier files if needed."""
        self.cl_geo.creer_geo_ref()

        if self.drun["has_casier"]:
            self.cl_geo.creer_geo_casier()

        if self.check_and_log_errors():
            return False

        return True

    def create_mobile_structures(self, folder):
        """Create mobile links and weirs configuration files."""
        # Create mobile links file
        if self.drun["has_link_fg"]:
            if not self.create_structure_file(
                    ClassLinkFGParam,
                    folder,
                    self.LINK_MOBILE_FILE
            ):
                return False

        # Create mobile weirs file
        if self.drun["has_weir_fg"]:
            if not self.create_structure_file(
                    ClassMobilWeirsParam,
                    folder,
                    self.WEIRS_MOBILE_FILE
            ):
                return False

        return True

    def create_structure_file(self, structure_class, folder, filename):
        """
        Generic method to create structure configuration files.

        Args:
            structure_class: Class to instantiate for structure creation
            folder: Target folder path
            filename: Output filename

        Returns:
            bool: True if creation succeeded
        """
        structure = structure_class()
        path = os.path.join(folder, filename)
        structure.create_cli_fg(self.mgis, path)

        has_errors = structure.mess.get_critic_status()
        self.write_mess(structure.mess)
        del structure

        return not self.exit_cpte(has_errors)

    def tracer_configuration(self, folder, kernel):
        """Handle tracer files creation if tracers are enabled."""
        if not self.drun["has_tracer"]:
            return True

        self.wq.create_filephy(folder)
        self.wq.law_tracer(folder)
        self.wq.init_conc_tracer(folder)

        # Create meteorological file for non-steady kernels
        if self.wq.dico_phy[self.wq.cur_wq_mod]["meteo"] and kernel != 'steady':
            has_errors, message = self.wq.create_filemet(folder)
            if self.exit_cpte(has_errors, message):
                return False

        return True

    def initial_conditions(self, scen, folder):
        """Handle initial conditions from scenario or LIG file."""
        if self.drun["has_run_init"] or not self.drun["ligInit"]:
            return True

        # Case 1: Use initial scenario
        if scen.get("scenar_init"):
            return self.initial_scen(scen)

        # Case 2: Use LIG file
        elif scen.get("lig_file"):
            if self.exit_cpte(self.copy_lig(scen["lig_file"], folder)):
                return False

        # Case 3: No initial conditions provided
        else:
            self.exit_cpte(False, 'No initial file provided')
            return False

        return True

    def initial_scen(self, scen):
        """Retrieve and use initial scenario for conditions."""
        init_scen = scen["scenar_init"]
        run_ids = self.mdb.get_id_run({init_scen[0]: [init_scen[1]]})

        if not run_ids:
            self.exit_cpte(False, 'Initial scenario does not exist')
            return False

        self.cl_bc.opt_to_lig(run_ids[0], lig_filename=self.LIG_FILE)
        return True

    def create_law_files(self, dico_loi_struct, model_folder, init_folder):
        """Create law files for structural elements."""
        if not dico_loi_struct:
            return True

        for name, config in dico_loi_struct.items():
            law_list = self.clmeth.get_list_law(config["id_config"])

            # Create law for model folder
            self.clmeth.create_law(
                model_folder,
                name,
                config["type"],
                law_list
            )

            # Create law for init folder if needed
            if self.drun['has_run_init']:
                self.clmeth.create_law(
                    init_folder,
                    f"{name}_init",
                    config["type"],
                    law_list
                )

        return True

    def initialize_scen_by_kernel(self, kernel, dict_lois, scen):
        """Initialize scenario based on kernel type (steady/event/unsteady)."""
        if kernel == "steady":
            has_errors = self.init_scen_steady(dict_lois)
        elif self.drun["event"]:
            has_errors = self.init_scen_even(dict_lois, scen)
        else:
            # Transcritical unsteady mode (non-event)
            self.par = self.cl_bc.classic_law(self.par, dict_lois)
            has_errors = self.mess.get_critic_status()

        # Update initialization flag if needed
        if self.par["initialisationAuto"] != self.drun['has_run_init']:
            self.drun['has_init'] = self.par["initialisationAuto"]

        return not self.exit_cpte(has_errors)

    def mobile_gates(self, kernel):
        """Create mobile gate files for unsteady kernel in non-API mode."""
        if not (self.check_mobil_gate() and
                kernel == "unsteady" and
                not self.dgeneral["api"]):
            return True

        self.cl_bc.create_mobil_gate_file()

        has_errors = self.cl_bc.mess.get_critic_status()
        self.write_mess(self.cl_bc.mess)

        return not self.exit_cpte(has_errors)

    def check_and_log_errors(self):
        """Check for critical errors and log messages."""
        has_errors = self.mess.get_critic_status()
        self.write_mess(self.mess)
        return self.exit_cpte(has_errors)


    def init_scen_steady(self, dict_lois):
        """
         Initial  files creation  for steady scenario
         Args:
            :param dict_lois:  (dict) laws
        Return :
            :return: boolean True if critical error
        """
        for nom, l in dict_lois.items():
            if "valeurperm" not in l.keys():
                continue
            if l["valeurperm"] is None:
                # dictLois.items() extremities liste
                tab = self.cl_bc.get_laws(nom, l["type"])
                if tab:
                    self.cl_bc.creer_loi(nom, tab, l["type"])
                else:
                    txt = "The law for {} is not create.".format(nom)
                    self.mgis.add_info(txt)
                    return True
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
                    if self.dbg:
                        error_info = traceback.format_exc()
                        err = err + "\n" + error_info
                    self.mgis.add_info(err)
                    return True
                if temp_dic["critereArret"] == 1:
                    tfinal = temp_dic["tempsMax"]
                elif temp_dic["critereArret"] == 2:
                    tfinal = temp_dic["tempsInit"] + temp_dic["pasTemps"] * temp_dic["nbPasTemps"]
                elif temp_dic["critereArret"] == 3:
                    tfinal = 365 * 24 * 3600
                else:
                    tfinal = 0

                if l["type"] == 1:
                    tab = {"time": [0, tfinal], "flowrate": [l["valeurperm"]] * 2}
                # no possible to use rating curve (5) with steady.
                #   It's replaced in xcas
                elif l["type"] == 2 or l["type"] == 5:
                    l["type"] = 2
                    tab = {"time": [0, tfinal], "z": [l["valeurperm"]] * 2}
                else:
                    tab = self.cl_bc.get_laws(nom, l["type"])

                if tab:
                    self.cl_bc.creer_loi(nom, tab, l["type"])
                else:
                    txt = "The law for {} is not create.".format(nom)
                    self.mgis.add_info(txt)
                    return True
        return False

    def check_exe(self):
        """
        Check if exe file exists
        :return:
        """
        if not os.path.isdir(self.bin_dir):
            return False
        test = sys.platform
        soft = None
        if "linux" in test or test == "cygwin":
            soft = "mascaret_linux"
        elif test == "win32":
            soft = "mascaret.exe"

        if not os.path.isfile(os.path.join(self.bin_dir, soft)):
            return False

        return True

    def purge_res_file_in_model(self, folder):
        """Clean the run folder and copy the essential files to run mascaret"""
        folder = Path(folder)
        listsup = [".opt", ".cas_opt", ".liai_opt",".tra_opt" ]
        fil_sup = [self.CREST_FILE, self.STRUCT_RES_FILE]
        if not folder.exists() or not folder.is_dir():
            self.mgis.add_info(f"Folder no valide {folder}", dbg=True)
            return
        for file in folder.iterdir():

            if not file.is_file():
                continue

            if (file.suffix in listsup or file in fil_sup):
                try:
                    file.unlink()
                except Exception as e:
                    self.mgis.add_info(f"delete file {file} \n {str(e)}", dbg=True)

    def purge_init_file_in_model(self, folder):
        """Clean the run folder and copy the essential files to run mascaret"""
        folder = Path(folder)
        partern_init_file = '_init.'

        if not folder.exists() or not folder.is_dir():
            self.mgis.add_info(f"Folder no valide {folder}", dbg=True)
            return
        for file in folder.iterdir():
            if not file.is_file():
                continue
            if partern_init_file not in file.name:
                continue
            try:
                file.unlink()
            except Exception as e:
                self.mgis.add_info(f"delete file {file} \n {str(e)}", dbg=True)

    def write_mess(self, obj):
        """
        Write message in plugin GUI
        Args:
            :param obj: object of classMessage to write the text
        """
        txt = obj.message()
        self.mgis.add_info(txt)
        obj.clear_derror()

    def init_scen_even(self,dict_lois,  dict_scen):
        """
        Initial  files creation  for evenment scenario
        Args:
            :param dict_lois: (dict) laws
            :param dict_scen: (dict)dictionnay of scenarii
        Return :
            :return: date begin (date_debut) and parameters (par)
        """
        # transcritical unsteady evenement
        date_debut = dict_scen["starttime"]
        date_fin = dict_scen["endtime"]
        duree = int((date_fin - date_debut).total_seconds())  # - 3600

        tab = {
            "tempsMax": {"valeur": str(duree), "balise1": "parametresTemporels"},
            "titreCalcul": {
                "valeur": dict_scen["name"],
                "balise1": "parametresImpressionResultats",
            },
        }
        self.cl_xcas.modif_xcas(tab,self.XCAS_FILE)
        self.par["tempsMax"] = duree
        if  self.drun["has_tracer"]:
            if self.wq.dico_phy[self.wq.cur_wq_mod]["meteo"]:
                exit_status, txt = self.wq.create_filemet(
                    typ_time="date", datefirst=date_debut, dateend=date_fin
                )
                if exit_status:
                    self.mgis.add_info(txt)
                    return True

        self.par = self.cl_bc.obs_to_loi(dict_lois, date_debut, date_fin, self.par)
        exit_status = self.mess.get_critic_status()
        self.write_mess(self.mess)
        return exit_status

    def clear_folder(self, folder_path, ask_confirm=False):
        """
        Deletes all files and subdirectories inside the specified folder.

        Args:
            folder_path (str): Absolute or relative path to the folder to be cleaned.
        """
        if not os.path.isdir(folder_path):
            return f"Folder not found : {folder_path}"
        if ask_confirm:
            box = ClassWarningBox()
            exist_folder = self.box.yes_no_q(f'Would you delete folder ?\n {folder_path}',
                                            'Delete Folder Confirmation')
            if not exist_folder :
                return f"Folder Deletion Aborted"

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except PermissionError as pe:
            return f"Permission denied while deleting: {item_path}"
        except Exception as e:
            return f"Error while deleting: {item_path}\n{str(e)}"
        return ''

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


