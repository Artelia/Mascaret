from ..assim import CreatModelAssim
import os
import numpy as np
import json
class Run_Assim :
    DATA_ASSIM_FILE = "data_assim.json"
    def __init__(self, mess= None, file_json=None):
        """Initialize the initializer.
        """
        self.data = {}
        self.mess=mess
        self.num_mess = 0
        self.read_data_js(file_json)

    def main(self):
        pass
        # d_scen = self.data['generate_instance']['dscen'][0]
        # d_run =  self.data['generate_instance']['drun']
        # order = 2
        # lst_instance = self.lst_instance_run_ctrlks(order)
        # TODO : create_folder
            # TODO : Copy file
            # TODO : Modification file
        # gestion des run_models
        # Utilisation task mascaret


    def read_data_js(self, filein=None):
        filein = filein or self.DATA_ASSIM_FILE
        if not os.path.isfile(filein):
            return
        with open(filein, "r") as file:
            self.data = json.load(file)

if __name__=="__main__":
    path_mode = r"C:\Users\mehdi-pierre.daou\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\Mascaret\mascaret\event1_1"
    ppa = Preparation_Assim()
    print(ppa.data)
    pass
        # # Convertir les starttime en datetime
        # self.convert_starttime(self.data.get('instance', []))
        #
        # if self.data.get('generate_instance'):
        #     dscen = self.data['generate_instance'].get('dscen')
        #     if dscen:
        #         self.convert_starttime(dscen)
    #
    # def get_list_cas(self):
    #     """Génère la liste des cas de test pour l'assimilation KS."""
    #     if not self.check_assim_ks():
    #         return []
    #
    #     dico_ks = self.data['generate_instance']['dico_ks']
    #     d_ctrlks = self.data['ctrlKS']
    #     lst_cas = []
    #
    #     for d_zone in d_ctrlks['lst_zone']:
    #         # Récupération des valeurs actuelles
    #         val_ksmaj = dico_ks["majbedcoef"][d_zone['num_zone']]
    #         val_ksmin = dico_ks["minbedcoef"][d_zone['num_zone']]
    #         typ = d_zone['type']
    #
    #         # Sélection de la perturbation selon le type
    #         pertub = (d_ctrlks['ksmin_perturb'][0] if typ == 'Ksmin'
    #                   else d_ctrlks['ksmaj_perturb'][0])
    #
    #         # Calcul des points de test
    #         n_points = (int(abs(d_zone['val_max'] - d_zone['val_min']) / pertub) + 1
    #                     if pertub > 0 else 1)
    #         temp_values = np.linspace(d_zone['val_min'], d_zone['val_max'], n_points)
    #
    #         # Génération des cas selon le type
    #         for temp_val in temp_values:
    #             if typ == 'Ksmin' and temp_val != val_ksmin:
    #                 lst_cas.append({
    #                     'num_zone': d_zone['num_zone'],
    #                     'ksmin': temp_val,
    #                     'ksmaj': val_ksmaj,
    #                     'type': 'Ksmin'
    #                 })
    #             elif typ == 'Ksmaj' and temp_val != val_ksmaj:
    #                 lst_cas.append({
    #                     'num_zone': d_zone['num_zone'],
    #                     'ksmin': val_ksmin,
    #                     'ksmaj': temp_val,
    #                     'type': 'Ksmaj'
    #                 })
    #
    #     # TODO: ajout d'un warning quand ksmaj n'est pas entre min et val
    #     return lst_cas
    #
    # def lst_instance_run_ctrlks(self, d_run, d_scen, order):
    #     folder = os.path.join(d_scen["path_instance"], 'run_ctrlKS')
    #     starttime = d_scen.get("starttime")
    #     lst_instance = []
    #
    #     lst_case = self.get_list_cas()
    #     for idx, case in enumerate(lst_case):
    #         name = f'ctrlKS_pertub{idx}'
    #         val = case['ksmin'] if case['type'] == 'Ksmin' else case['ksmaj']
    #         folder_run = os.path.join(folder,
    #                                   f"pertub{idx}_{case['type']}_{case['num_zone']}_{str(val).replace('.', 'p')}")
    #         if d_run['has_run_init']:
    #             lst_instance.append({'name': f'{name}_init',
    #                                  "RUN_REP": os.path.join(folder_run, 'run_init'),
    #                                  "has_casier": False,
    #                                  "has_tracer": False,
    #                                  "starttime": None,
    #                                  "order": order,
    #                                  })
    #             order += 1
    #         lst_instance.append({'name': name,
    #                              'name_xcas': self.XCAS_FILE,
    #                              "RUN_REP": folder_run,
    #                              "has_casier": d_run["has_casier"],
    #                              "has_tracer": d_run["has_tracer"],
    #                              "has_assim": d_run['has_assimilation'],
    #                              "starttime": starttime,
    #                              "assim_info": {
    #                                  'num_pertub': idx,
    #                                  'type_ctrl': 'ctrlKS',
    #                                  'type_case': case['type'],
    #                                  'num_zone': case['num_zone'],
    #                                  'ks_pertub': val, },
    #                              "order": order, })
    #         order += 1
    #
    #     return lst_instance

