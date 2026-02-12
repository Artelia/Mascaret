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
import json
import shutil
from pathlib import Path
import traceback
from datetime import datetime
from lib.assim.ClassCreatModelAssim import CreatModelAssim
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as et_parse


def indent(elem, level=0):
    """
    Indent XML elements for pretty printing.
    :param elem (Element): XML element
    :param level (int): Indentation level
    :return: None
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def fmt(liste):
    """
    Convert a list to a space-separated string.
    :param liste (list): List of values
    :return: (str) Space-separated string
    """
    # list(map(str, liste))
    return " ".join([str(var) for var in liste])

class CreatAssimOnly:
    """Class Assimilation gestion base donneee"""
    DATA_ASSIM_FILE = "data_assim.json"
    def __init__(self, dict_param, mess=None):
        """Initialize the initializer.
        """
        self.data = {}
        self.mess=mess
        self.num_mess = 0
        self.cl_creat_assim = CreatModelAssim()
        self.path_model_ori = dict_param['path_model_ori']
        self.path_run= dict_param['path_run']
        self.read_data_js(dict_param['dico_assim'])
        self.XCAS_FILE = dict_param['xcas_file']

    def add_info(self, txt):
        if self.mess:
            self.mess('clAssim{}'.format(self.num_mess), 'info', txt)
            self.num_mess += 1
        else:
            print(txt)

    def clone_model(self, source_folder=None, target_folder=None):
        """Copy initialization files from source to target folder.
        :return: True if operation succeeded, False otherwise.
        :rtype: bool
        """
        ignore = ['.opt', '.lis']
        source = Path(source_folder)
        target = Path(target_folder)
        #
        # # Validate source folder
        if not source.exists() or not source.is_dir():
            self.add_info(f"Invalid source folder: {source}")
            return False
        #
        # # Validate target folder
        if not target.exists() or not target.is_dir():
            self.add_info(f"Invalid target folder: {target}")
            return False

        copied_count = 0
        for file_path in source.iterdir():
            if not file_path.is_file():
                continue

        #     # Check if file has a valid suffix
            if file_path.suffix in ignore:
                continue
            try:
                target_path = target / file_path.name
                shutil.copy2(file_path, target_path)  # copy2 preserves metadata
                copied_count += 1
            except Exception as e:
                self.add_info(
                    f"Failed to copy file '{file_path.name}': {str(e)}",
                )
        return True

    def read_data_js(self, filein=None):
        
        filein = filein or self.DATA_ASSIM_FILE
        

        with open(filein, "r") as file:
            self.data = json.load(file)

        # Convertir les starttime en datetime
        self.convert_starttime(self.data.get('instance', []))

        if self.data.get('generate_instance'):
            dscen = self.data['generate_instance'].get('dscen')
            if dscen:
                self.convert_starttime([dscen])

    def convert_starttime(self, instances):
        """Convertit les starttime ISO en objets datetime"""
        for instance in instances:
            if instance.get("starttime"):
                try:
                    instance["starttime"] = datetime.fromisoformat(instance["starttime"])
                except ValueError:
                    pass

    def get_zone_frot(self, xcasfile, folder):
        """
        Extract friction zone parameters from an xcas file.
        :param xcasfile (str): xcas filename
        :param folder (str): folder path
        :return: dict with friction zone parameters
        """
        fich_entree = os.path.join(folder, xcasfile)
        arbre = et_parse(fich_entree)
        racine = arbre.getroot()

        zone = {
            "loi": None,
            "nbZone": None,
            "numBranche": None,
            "absDebZone": None,
            "absFinZone": None,
            "coefLitMin": None,
            "coefLitMaj": None,
        }

        parent = racine[0].find("parametresCalage")
        if parent is None:
            return zone

        child = parent.find("frottement")
        if child is None:
            return zone

        for param in zone.keys():
            element = child.find(param)
            if element is not None and element.text:
                if param in ["coefLitMin", "coefLitMaj"]:
                    zone[param] = [float(val) for val in element.text.split()]
                else:
                    # Conversion appropriée selon le type attendu
                    text = element.text.strip()
                    if param == "nbZone":
                        zone[param] = int(text)
                    elif param in ["absDebZone", "absFinZone"]:
                        zone[param] = [float(val) for val in text.split()]
                    else:
                        zone[param] = text

        return zone

    def check_assim_ks(self):
        return bool(self.data.get('ctrlKS'))
    
    def get_list_cas_ks(self):
        """Génère la liste des cas de test pour l'assimilation KS."""
        if not self.check_assim_ks():
            return []

        d_ctrlks = self.data['ctrlKS']

        lst_cas = []
        for d_zone in d_ctrlks['lst_zone']:
            # Récupération des valeurs actuelles
            val_ksmaj = d_zone['zone_info']['ref_ks_maj']
            val_ksmin = d_zone['zone_info']['ref_ks_min']
            typ = d_zone['type']
            # Sélection de la perturbation selon le type
            pertub = (d_ctrlks['ksmin_perturb'][0] if typ == 'Ksmin'
                      else d_ctrlks['ksmaj_perturb'][0])
            pertub = abs(pertub)
            pertub = pertub if pertub > 0 else 1
            val = d_zone['val_min']
            temp_values = []
            while val < d_zone['val_max']:
                temp_values.append(round(val, 3))
                val += pertub
            temp_values.append(d_zone['val_max'])
            # Génération des cas selon le type
            for temp_val in temp_values:
                if typ == 'Ksmin' and temp_val != val_ksmin:
                    lst_cas.append({
                        'num_zone': d_zone['num_zone'],
                        'ksmin': temp_val,
                        'ksmaj': val_ksmaj,
                        'type': 'Ksmin'
                    })
                elif typ == 'Ksmaj' and temp_val != val_ksmaj:
                    lst_cas.append({
                        'num_zone': d_zone['num_zone'],
                        'ksmin': val_ksmin,
                        'ksmaj': temp_val,
                        'type': 'Ksmaj'
                    })
        return lst_cas

    def lst_instance_run_ctrlks(self, d_run, d_scen, order):
        folder = os.path.join(d_scen["path_instance"], 'run_ctrlKS')
        starttime = d_scen.get("starttime")
        lst_instance = []

        lst_case = self.get_list_cas_ks()
        for idx, case in enumerate(lst_case):
            name = f'ctrlKS_pertub{idx}'
            val = case['ksmin'] if case['type'] == 'Ksmin' else case['ksmaj']
            folder_run = os.path.join(folder,
                                      f"pertub{idx}_{case['type']}_{case['num_zone']}_{str(val).replace('.', 'p')}")
            lst_instance.append({'name': name,
                                 'name_xcas': self.XCAS_FILE,
                                 "RUN_REP": folder_run,
                                 "has_casier": d_run["has_casier"],
                                 "has_tracer": d_run["has_tracer"],
                                 "has_assim": d_run['has_assimilation'],
                                 "starttime": starttime,
                                 'type_ctrl': 'ctrlKS',
                                 "assim_info": {
                                     'num_pertub': idx,
                                     'type_case': case['type'],
                                     'num_zone': case['num_zone'],
                                     'ks_pertub': val, },
                                 "order": order, })
            order += 1

        d_scen["instances"] += lst_instance
        return d_scen

    def creat_assim_folder(self):
        
        folder_ref = os.path.join(self.path_run, 'run_ref')
        self.data["generate_instance"]["dscen"]["instances"] =[]
        instances = self.lst_instance_run_ctrlks(self.data["generate_instance"]["drun"],
                                     self.data["generate_instance"]["dscen"], 0)
        

        self.cl_creat_assim.clone_model(self.path_model_ori , folder_ref)
        for instance in instances:
            print(instance, 'pppppppppp')
            folder = instance["RUN_REP"]
            self.cl_creat_assim.clone_model(folder_ref, folder)
            if 'ctrlKS' == instance.get('type_ctrl', ''):
                zones = self.get_zone_frot(instance.get('name_xcas', 'mascaret.xcas'), folder)
                if instance.get("assim_info"):
                    assim_info = instance.get("assim_info")
                    numz = assim_info['num_zone']
                    if assim_info['type_case'] == "Ksmaj":
                        var = "coefLitMaj"
                    elif assim_info['type_case'] == "Ksmin":
                        var = "coefLitMin"
                    zones[var][numz] = assim_info['ks_pertub']
                parametres = {
                    "loi": "1",
                    "nbZone": str(zones["nbZone"]),
                    "numBranche": zones["numBranche"],
                    "absDebZone": fmt(zones["absDebZone"]),
                    "absFinZone": fmt(zones["absFinZone"]),
                    "coefLitMin": fmt(zones["coefLitMin"]),
                    "coefLitMaj": fmt(zones["coefLitMaj"]),

                }

                self.modif_xcas(parametres, instance.get('name_xcas', 'mascaret.xcas'), folder)

            if 'ctrlLaw' == instance.get('type_ctrl', ''):
                if instance.get("assim_info"):
                    assim_info = instance.get("assim_info")
                    name_law = f'{assim_info["name_law"]}.loi'

                    file_law = os.path.join(folder, name_law)
                    file_tmp = os.path.join(folder, f'{name_law}.tmp')
                    shutil.copy2(file_law, file_tmp)
                    filein = open(file_tmp, 'r')
                    with open(file_law, 'w') as fileout:
                        cpt = 1
                        for line in filein:
                            if line.startswith('#'):
                                fileout.write(line)
                                continue
                            if cpt == 1:
                                fileout.write(line)
                                cpt += 1
                            parts = line.split()
                            if len(parts) >= 2:
                                if assim_info['type_case'] == 'coefA':
                                    parts[1] = round(assim_info['coef_pertub'] * float(parts[1]), 6)
                                    fileout.write(' '.join([str(par) for par in parts]))
                                elif assim_info['type_case'] == 'coefB':
                                    parts[1] = round(assim_info['coef_pertub'] + float(parts[1]), 6)
                                    fileout.write(' '.join([str(par) for par in parts]))
                                fileout.write('\n')
                    filein.close()
                    os.remove(file_tmp)

    def modif_xcas(self, parametres, xcasfile, folder):
        """
        Modify an existing xcas file with new parameters.
        :param parametres (dict): Parameters to update
        :param xcasfile (str): xcas filename
        :param fich_sortie (str): Optional output filename
        :return: None
        """
        fich_entree = os.path.join(folder, xcasfile)
        arbre = et_parse(fich_entree)
        racine = arbre.getroot()
        parent = racine[0].find("parametresCalage")
        if parent is None:
            return

        child = parent.find("frottement")
        if child is None:
            return

        for param, val in parametres.items():
            element = child.find(param)
            if element is None:
                continue

            # Conversion de la valeur en string appropriée
            if isinstance(val, dict) and "valeur" in val:
                nouvelle_valeur = val["valeur"]
            else:
                nouvelle_valeur = val

            # Conversion en string selon le type
            if isinstance(nouvelle_valeur, (list, tuple)):
                element.text = " ".join(str(v) for v in nouvelle_valeur)
            else:
                element.text = str(nouvelle_valeur)

        indent(racine)
        arbre.write(fich_entree)



if __name__=="__main__":
    path_base = r"C:\Users\mehdi-pierre.daou\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\Mascaret\test"
    dict_param = {
    'xcas_file' : 'mascaret.xcas',
    'dico_assim' : os.path.join(path_base , 'data_assim.json'),
    'path_model_ori' :  os.path.join(path_base ,"model_ori"),
    'path_run' : path_base
    }
    cma = CreatAssimOnly(dict_param)
    cma.creat_assim_folder()
    print(cma.data)
