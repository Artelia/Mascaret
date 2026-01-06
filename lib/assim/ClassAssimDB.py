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
import numpy as np
import json
import shutil
from pathlib import Path
import traceback
from datetime import datetime
from .ClassCreatModelAssim import CreatModelAssim
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


class ClassAssimDB:
    """Class Assimilation gestion base donneee"""
    XCAS_FILE = "mascaret.xcas"
    XCAS_FILE_INIT = "mascaret_init.xcas"
    DATA_ASSIM_FILE = "data_assim.json"

    def __init__(self, mdb):
        """Initialize the initializer.
        """
        self.data = {}
        self.mdb = mdb
        self.update_data_db()
        self.cl_creat_assim = CreatModelAssim()

    def update_data_db(self):
        """Met à jour les données de configuration depuis la base de données."""
        data_config = self.mdb.select("assim_config", where="active")
        if not data_config:
            self.data = {}
            return

        for idx, ctrl_type in enumerate(data_config['control_type']):
            if ctrl_type == 'ctrlKS':
                self._update_ctrl_ks(idx, data_config)
            elif ctrl_type == 'ctrlLaw':
                self._update_ctrl_law(idx, data_config)

    def _update_ctrl_ks(self, idx, data_config):
        """Gère la mise à jour des données ctrlKS."""
        id_type = data_config['id_type'][idx]
        data_ks = self.mdb.select(
            "assim_ks",
            where=f"active and (active_min or active_maj) and id_type={id_type}"
        )
        if not data_ks:
            return

        if 'ctrlKS' not in self.data:
            self.data['ctrlKS'] = {}

        d_perturb = dict(zip(
            data_config['perturbation_var'][idx],
            data_config['perturbation_val'][idx]))
        obs_var = data_config['control_var'][idx]
        self.data['ctrlKS'].update({
            "obs_var": obs_var,
            "seuil_rejet_misfit": data_config['seuil_rejet_misfit'][idx],
            "iterations_sigma": data_config['iterations_sigma'][idx],
            "ksmin_perturb": d_perturb['ksMin'],
            "ksmaj_perturb": d_perturb['ksMaj'],
            'lst_zone': self._build_ks_list(data_ks, obs_var)
        })

    def _build_ks_list(self, data_ks, obs_var):
        """Construit la liste des zones KS."""
        list_ks = []

        for idx in range(len(data_ks['id_zone'])):
            if data_ks['active_min'][idx]:
                list_ks.append(self._create_ks_entry(data_ks, idx, 'Ksmin', 'min', obs_var))
            if data_ks['active_maj'][idx]:
                list_ks.append(self._create_ks_entry(data_ks, idx, 'Ksmaj', 'maj', obs_var))

        return list_ks

    def _create_ks_entry(self, data_ks, idx, type_ks, val_type, obs_var):
        """Crée une entrée KS standardisée."""
        return {
            "num_zone": data_ks['id_zone'][idx],
            "type": type_ks,
            "val_min": data_ks[f'val_inf_{val_type}'][idx],
            "val_max": data_ks[f'val_sup_{val_type}'][idx],
            "std": data_ks[f'std_{val_type}'][idx],
            "lst_obs": data_ks['lst_obs_h'][idx] if obs_var == 'H' else data_ks['lst_obs_q'][idx],
            "abs_min": data_ks['abs_min'][idx],
            "abs_max": data_ks["abs_max"][idx],
            'branchnum': data_ks['branchnum'][idx],
        }

    def _update_ctrl_law(self, idx, data_config):
        """Gère la mise à jour des données CtrlLaw."""
        id_type = data_config['id_type'][idx]
        data_law = self.mdb.select(
            "assim_law",
            where=f"active and (active_a or active_b)"
        )
        if not data_law:
            return

        if 'CtrlLaw' not in self.data:
            self.data['CtrlLaw'] = {}

        d_perturb = dict(zip(
            data_config['perturbation_var'][idx],
            data_config['perturbation_val'][idx]))
        obs_var = data_config['control_var'][idx]
        self.data['CtrlLaw'].update({
            "obs_var": obs_var,
            "seuil_rejet_misfit": data_config['seuil_rejet_misfit'][idx],
            "iterations_sigma": data_config['iterations_sigma'][idx],
            "lcote_perturb": d_perturb['perturbationsCote'],
            "ldebit_perturb": d_perturb['perturbationsDebit'],
            "ldebit_lin_perturb": d_perturb['perturbationsDebitLineique'],
            'lst_loi': self._build_law_list(data_law, obs_var)
        })

    def _build_law_list(self, data_law, obs_var):
        """Construit la liste des lois."""
        list_law = []
        for idx in range(len(data_law['id_law'])):
            if data_law['active_a'][idx]:
                list_law.append(self._create_law_entry(data_law, idx, 'a', obs_var))
            if data_law['active_b'][idx]:
                list_law.append(self._create_law_entry(data_law, idx, 'b', obs_var))
        return list_law

    def _create_law_entry(self, data_law, idx, typ_coef, obs_var):
        """Crée une entrée KS standardisée."""
        return {
            "id_law": data_law['id_law'][idx],
            'source_law': data_law['source_law'][idx],
            'type': f'coef{typ_coef.upper()}',
            "std": data_law[f'std_{typ_coef}'][idx],
            "val_min": data_law['val_min'][idx],
            "val_max": data_law['val_max'][idx],
            "lst_obs": data_law['lst_obs_h'][idx] if obs_var == 'H' else data_law['lst_obs_q'][idx],
        }

    def check_assim(self):
        return bool(self.data)

    def check_assim_ks(self):
        return bool(self.data.get('ctrlKS'))

    def check_assim_law(self):
        return bool(self.data.get('CtrlLaw'))

    def get_list_cas_ks(self):
        """Génère la liste des cas de test pour l'assimilation KS."""
        if not self.check_assim_ks():
            return []

        dico_ks = self.mdb.zone_ks()
        d_ctrlks = self.data['ctrlKS']
        lst_cas = []

        for d_zone in d_ctrlks['lst_zone']:
            # Récupération des valeurs actuelles
            val_ksmaj = dico_ks["majbedcoef"][d_zone['num_zone']]
            val_ksmin = dico_ks["minbedcoef"][d_zone['num_zone']]
            typ = d_zone['type']

            # Sélection de la perturbation selon le type
            pertub = (d_ctrlks['ksmin_perturb'][0] if typ == 'Ksmin'
                      else d_ctrlks['ksmaj_perturb'][0])
            pertub = abs(pertub)
            # Calcul des points de test
            # n_points = (int(abs(d_zone['val_max'] - d_zone['val_min']) / pertub) + 1
            #             if pertub > 0 else 1)
            # temp_values = np.linspace(d_zone['val_min'], d_zone['val_max'], n_points)
            pertub =  pertub  if pertub > 0 else 1
            val = d_zone['val_min']
            temp_values = []
            while val < d_zone['val_max']:
                temp_values.append(round(val,3))
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

        # TODO: ajout d'un warning quand ksmaj n'est pas entre min et val
        return lst_cas

    def get_list_cas_law(self):
        """Génère la liste des cas de test pour l'assimilation LAW."""
        if not self.check_assim_law():
            return []

        d_ctrl_law = self.data['CtrlLaw']
        lst_cas = []
        for d_loi in d_ctrl_law['lst_loi']:
            if d_loi['source_law'] == 'extremities':
                sql = f"SELECT name, method, type FROM {self.mdb.SCHEMA}.extremities WHERE active and gid={d_loi['id_law']}"
            elif d_loi['source_law'] == 'lateral_inflows':
                sql = f"SELECT name, method FROM {self.mdb.SCHEMA}.lateral_inflows WHERE active and gid={d_loi['id_law']}"
            res = self.mdb.run_query(sql, fetch=True)
            if not res:
                # TODO message  pas de loi
                print("Hydraulic law not defined")
                continue
            methode = res[0][1]
            name_law = res[0][0]
            if methode == '' or methode == None:
                print("Hydraulic law method  not defined")
                continue

            if d_loi['source_law'] == 'extremities':
                if res[0][2] == 1:
                    type_law = 'perturbationsDebit'
                    pertub = d_ctrl_law['ldebit_perturb']
                elif res[0][2] == 2:
                    type_law = 'perturbationsCote'
                    pertub = d_ctrl_law['lcote_perturb']
            elif d_loi['source_law'] == 'lateral_inflows':
                type_law = 'perturbationsDebitLineique'
                pertub = d_ctrl_law['ldebit_lin_perturb']
            else:
                print("Hydraulic law type not defined")
                continue
            if d_loi['type'] == 'coefA':
                pertubf = abs(pertub[0])
            elif d_loi['type'] == 'coefB':
                pertubf = abs(pertub[1])

            #n_points = (int(abs(d_loi['val_max'] - d_loi['val_min']) / pertubf) + 1
            #            if pertubf > 0 else 1)
            pertubf = pertubf if pertubf > 0 else 1
            val = d_loi['val_min']
            temp_values = []
            while val < d_loi['val_max'] :
                temp_values.append(round(val,3))
                val += pertubf
            temp_values.append(d_loi['val_max'])
            # Génération des cas selon le type
            for temp_val in temp_values:
                if (temp_val == 1 and d_loi['type'] == 'coefA') or (temp_val == 0):
                    continue

                dnew = d_loi.copy()
                dnew.update({'methode': methode,
                             'name_law': name_law,
                             'type_law': type_law,
                             'pertub': pertubf,
                             'val_coef': temp_val
                             })
                lst_cas.append(dnew)

        return lst_cas

    def add_data_dgenerate_ks(self, d_run, d_scen):
        # TODO A traiter pour pom
        self.data['generate_instance'] = {
            'drun': {
                key: d_run[key]
                for key in ["has_casier", "has_tracer", "has_assimilation"]
            },
            'dscen': {
                "path_instance": d_scen["path_instance"],
                "starttime": d_scen.get("starttime")
            },
            "dico_ks": self.mdb.zone_ks()
        }

    def add_data_dgenerate_law(self, d_run, d_scen,):
        # TODO A traiter pour pom
        pass
        # self.data['generate_instance'] = {
        #     'drun': {
        #         key: d_run[key]
        #         for key in ["has_casier", "has_tracer", "has_assimilation"]
        #     },
        #     'dscen': {
        #         "path_instance": d_scen["path_instance"],
        #         "starttime": d_scen.get("starttime")
        #     },
        #     "dico_loi": self.mdb.zone_ks()
        # }
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
            if d_run['has_run_init']:
                lst_instance.append({'name': f'{name}_init',
                                     'name_xcas': self.XCAS_FILE_INIT,
                                     "RUN_REP": os.path.join(folder_run, 'run_init'),
                                     'type_ctrl': 'ctrlKS',
                                     "has_casier": False,
                                     "has_tracer": False,
                                     "starttime": None,
                                     "order": order,
                                     "assim_info": {
                                         'num_pertub': idx,
                                         'type_case': case['type'],
                                         'num_zone': case['num_zone'],
                                         'ks_pertub': val, },
                                     })
                order += 1
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

        self.add_data_dgenerate_ks(d_run, d_scen)
        return lst_instance

    def lst_instance_run_ctrl_law(self, d_run, d_scen, order):
        folder = os.path.join(d_scen["path_instance"], 'run_ctrlLaw')
        starttime = d_scen.get("starttime")
        lst_instance = []
        lst_case = self.get_list_cas_law()
        for idx, case in enumerate(lst_case):
            name = f'ctrlLaw_pertub{idx}'

            val = case['val_coef']
            folder_run = os.path.join(folder,
                                      f"pertub{idx}_{case['type']}_{case['name_law']}_{str(val).replace('.', 'p')}")
            if d_run['has_run_init']:
                lst_instance.append({'name': f'{name}_init',
                                     'name_xcas': self.XCAS_FILE_INIT,
                                     "RUN_REP": os.path.join(folder_run, 'run_init'),
                                     'type_ctrl': 'ctrlLaw',
                                     "has_casier": False,
                                     "has_tracer": False,
                                     "starttime": None,
                                     "order": order,
                                     "assim_info": {
                                         'num_pertub': idx,
                                         'type_case': case['type'],
                                         'name_law': case['name_law'],
                                         'id_law': case['id_law'],
                                         'source_law': case['source_law'],
                                         'coef_pertub': val, },
                                     })
                order += 1
            lst_instance.append({'name': name,
                                 'name_xcas': self.XCAS_FILE,
                                 "RUN_REP": folder_run,
                                 "has_casier": d_run["has_casier"],
                                 "has_tracer": d_run["has_tracer"],
                                 "has_assim": d_run['has_assimilation'],
                                 "starttime": starttime,
                                 'type_ctrl': 'ctrlLaw',
                                 "assim_info": {
                                     'num_pertub': idx,
                                     'type_case': case['type'],
                                     'name_law': case['name_law'],
                                     'id_law': case['id_law'],
                                     'source_law': case['source_law'],
                                     'coef_pertub': val, },
                                 "order": order, })
            order += 1
        #
        self.add_data_dgenerate_law(d_run,d_scen)
        return lst_instance

    def export_data_json(self, folder):
        if self.data.get('instance'):
            for instance in self.data['instance']:
                if instance.get("starttime"):
                    if isinstance(instance["starttime"], datetime):
                        instance["starttime"] = instance["starttime"].isoformat()

        if self.data.get('generate_instance'):
            instance = self.data['generate_instance']['dscen']
            if instance.get("starttime"):
                if isinstance(instance["starttime"], datetime):
                    instance["starttime"] = (
                        instance["starttime"].isoformat())

        with open(os.path.join(folder, self.DATA_ASSIM_FILE), "w") as f:
            json.dump(self.data, f, indent=4)

    def fill_assim_folder(self, ids, scen, obj_model):
        d_folder = obj_model.get_folder(scen)
        path_ref = Path(d_folder['ref'])
        path_init = Path(d_folder['init'])

        path_scen = path_ref.parent
        obj_model.assim.export_data_json(path_scen)
        for name, folder in d_folder.items():
            if name in ['ref', 'init']:
                continue

            instance = obj_model.get_instance(ids, name)
            if name.endswith('init'):
                self.cl_creat_assim.clone_model(path_init, folder)
            else:
                self.cl_creat_assim.clone_model(path_ref, folder)
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
                    name_law = f'{assim_info["name_law"]}_init.loi' if name.endswith('init') else f'{assim_info["name_law"]}.loi'

                    file_law = os.path.join(folder, name_law)
                    file_tmp = os.path.join(folder, f'{name_law}.tmp')
                    shutil.copy2(file_law , file_tmp)
                    filein = open(file_tmp, 'r')
                    with open(file_law,'w') as fileout:
                        cpt=1
                        for line in filein:
                            if line.startswith('#') :
                                fileout.write(line)
                                continue
                            if cpt==1:
                                fileout.write(line)
                                cpt += 1
                            parts = line.split()
                            if len(parts) >= 2:
                                if assim_info['type_case'] =='coefA':
                                    parts[1] = round(assim_info['coef_pertub'] *  float(parts[1]),6)
                                    fileout.write(' '.join([str(par) for par in parts]))
                                elif assim_info['type_case'] == 'coefB':
                                    parts[1] = round(assim_info['coef_pertub'] + float(parts[1]),6)
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
