import json
import os
import numpy as np


# n_perturb = 2
# zones = [2]
# base_folder = r'../../mascaret/event1_1/'


def get_perturb_folder(base_folder, iperturb):
    print('Finding perturbation folders in', base_folder)
    name_folder = None
    type_perturb = ''
    val_perturb = 0.0
    zone_perturb = None
    for folder in os.listdir(base_folder):
        if f'pertub{iperturb}' in folder:
            name_folder = folder
            type_perturb = folder.split('_')[1]
            val_perturb = float(folder.split('_')[-1].replace('p', '.'))
            zone_perturb = folder.split('_')[2]
    if name_folder is not None:
        return name_folder, type_perturb, val_perturb, zone_perturb
    else:
        raise FileNotFoundError(f'Directory for perturbation number {iperturb} not found')


class ClassMatrix:
    """"""

    # TODO Passer en argument d'entrée le dico ou json des paramètres d'assimilation !
    def __init__(self, base_folder, ctrl_type, json_assim=None):
        """"""
        # Vecteur d'ébauche
        self.misfit = []
        self.B_analysed = None
        self.Z_obs = []
        self.xb = []
        # Vecteur d'observations
        self.y0 = []
        self.param_ref = None
        self.H = None
        self.B = None
        self.R = None
        self.min_values = []
        self.max_values = []

        if not (os.path.exists(base_folder)):
            raise FileNotFoundError(f'Unfound working folder : {base_folder}')
        self.base_folder = base_folder
        self.zones = []
        self.nbzones = 0
        json_path = os.path.join(self.base_folder, 'data_assim.json')
        self.ctrlKs = False
        self.ctrlLaw = False
        with open(json_path) as f:
            self.dict_assim = json.load(f)

        # Récupération du type de controle
        if self.dict_assim.get("ctrlKS") is not None and ctrl_type == "ctrlKS":
            self.ctrlKs = True
        if self.dict_assim.get("ctrlLaw") is not None and ctrl_type == "ctrlLaw":
            self.ctrlLaw = True
        self.ctrl_type = ctrl_type

        # Récupération du nombre de zones et de la liste des zones
        if self.ctrlKs and self.ctrl_type == 'ctrlKS':
            self.zones = [dico.get("num_zone") for dico in self.dict_assim["ctrlKS"]["lst_zone"]]
            self.zones = np.unique(self.zones)
            self.nb_zones = len(self.zones)
            self.seuil_rejet_misfit = self.dict_assim[ctrl_type].get("seuil_rejet_misfit", 500)
        if self.ctrlLaw and self.ctrl_type == 'ctrlLaw':
            self.zones = [dico.get("name_law") for dico in self.dict_assim["ctrlLaw"]["lst_loi"]]
            self.zones = np.unique(self.zones)
            self.nb_zones = len(self.zones)
            self.seuil_rejet_misfit = self.dict_assim[ctrl_type].get("seuil_rejet_misfit", 500)

        # Récupération du nombre total de pas de temps d'observation
        name_folder_ref = os.path.join(self.base_folder, 'run_ref')
        with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
            dict_ref = json.load(f)
        self.nb_dt_obs = len(dict_ref['time'])

        # Récupération des zéros des observations
        self.zero_obs = {}
        if ctrl_type == 'ctrlKS' and self.ctrlKs:
            for d in self.dict_assim["ctrlKS"]["lst_zone"]:
                dico = d.get("lst_obs", {})
                if dico != {}:
                    for ic, c in enumerate(dico.get("code")):
                        if c not in self.zero_obs.keys():
                            self.zero_obs[c] = dico.get("zero")[ic]
            self.key_lst = 'lst_zone'
        if ctrl_type == 'ctrlLaw' and self.ctrlLaw:
            for d in self.dict_assim[ctrl_type]["lst_loi"]:
                dico = d.get("lst_obs", {})
                if dico != {}:
                    for ic, c in enumerate(dico.get("code")):
                        if c not in self.zero_obs.keys():
                            self.zero_obs[c] = dico.get("zero")[ic]
            self.key_lst = 'lst_loi'

        self.type_perturb = []
        # Récupération du nombre total de perturbations
        if self.ctrlKs or self.ctrlLaw:
            self.nbperturb = 0
            for d in self.dict_assim[self.ctrl_type][self.key_lst]:
                type_pert = d.get("type")
                if type_pert == "Ksmin" or type_pert == "coefA":
                    self.nbperturb += 1
                    self.type_perturb.append(1)
                if type_pert == "Ksmaj" or type_pert == "coefB":
                    self.nbperturb += 1
                    self.type_perturb.append(2)
            print('Total number of perturbations:', self.nbperturb)

    def build_all_matrix(self):
        self.build_B_matrix_ini()
        self.build_diago_R_matrix_ini()
        self.build_H_matrix()
        self.build_misfit()
        self.build_min_max_values()

    def build_B_matrix_ini(self):
        liste_sigma = []
        if self.ctrl_type == 'ctrlKS' and self.ctrlKs:
            for d in self.dict_assim.get("ctrlKS")["lst_zone"]:
                std_zone = d["std"]
                if d.get("std") is None:
                    raise KeyError("Key std not found in data_assim.json")
                if d.get("type") == "Ksmin":
                    liste_sigma += [2 * std_zone]
                if d.get("type") == "Ksmaj":
                    liste_sigma += [2 * std_zone]

        if self.ctrl_type == 'ctrlLaw' and self.ctrlLaw:
            for d in self.dict_assim.get("ctrlLaw")["lst_loi"]:
                std_zone = d["std"]
                if d.get("std") is None:
                    raise KeyError("Key std not found in data_assim.json")
                # TODO je suis pas sur que la différenciation soit toujours utile..
                if d.get("type") == "coefA":
                    liste_sigma += [2 * std_zone]
                if d.get("type") == "coefB":
                    liste_sigma += [2 * std_zone]
            # raise NotImplementedError('Control law matrices not implemented yet')

        if len(liste_sigma) != self.nbperturb:
            raise ValueError(f'Problem with initial B matrix creation. '
                             f'Size should be {self.nbperturb}, it is {len(liste_sigma)}')
        self.B = np.diag(liste_sigma, 0)
        print("Matrices des covariances d'erreur d'ébauche B", self.B)

    def build_B_matrix_analysed(self, K):
        self.B_analysed = self.B - np.matmul(np.matmul(K, self.H), self.B)


    def build_diago_R_matrix_ini(self):
        diag_R = []
        # TODO faire sur toutes les obs dispos !, une seule fois
        # num_stations = []
        num_obs = []
        if self.ctrl_type == 'ctrlKS' and self.ctrlKs:
            for dico in self.dict_assim.get("ctrlKS").get("lst_zone"):
                # if int(dico.get("num_zone")) not in num_stations:
                    # num_stations.append(int(dico.get("num_zone")))
                dict2 = dico.get("lst_obs")
                for icode, code in enumerate(dict2.get("code")):
                    if code not in num_obs:
                        if dict2.get("stderr") is None:
                            raise KeyError("Key std_obs not found in data_assim.json")
                        diag_R += [float(dict2["stderr"][icode]) ** 2 for i in
                                   range(self.nb_dt_obs)]
                        num_obs.append(code)

        elif self.ctrl_type == 'ctrlLaw' and self.ctrlLaw:
            for dico in self.dict_assim.get(self.ctrl_type).get("lst_loi"):
                dict2 = dico.get("lst_obs")
                for icode, code in enumerate(dict2.get("code")):
                    if code not in num_obs:
                        if dict2.get("stderr") is None:
                            raise KeyError("Key std_obs not found in data_assim.json")
                        diag_R += [float(dict2["stderr"][icode]) ** 2 for i in
                                   range(self.nb_dt_obs)]
                        num_obs.append(code)
        print("Diagonale des matrices des covariances d'erreur d'observation R", diag_R)
        self.R = np.array(diag_R)

    def build_min_max_values(self):
        """
        Builds minimal and maximal values vectors for assim parameters
        It is stored in the same order than in data_assim json file.
        """
        for dico in self.dict_assim.get(self.ctrl_type).get(self.key_lst):
            self.min_values.append(dico.get("val_min"))
            self.max_values.append(dico.get("val_max"))

    def build_misfit(self):
        name_folder_ref = os.path.join(self.base_folder, 'run_ref')
        with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
            dict_ref = json.load(f)

        Zref = {}
        for zone in self.zones:
            for station in dict_ref['Z'][str(zone)]:
                if station not in Zref.keys():
                    Zref[station] = []

        # Boucle sur les zones concernées
        for zone in self.zones:
            # Boucle sur les stations d'observation dans chaque zone
            for station in dict_ref['Z'][str(zone)]:
                Zref[station] += dict_ref['Z'][str(zone)][station]

        print('ZREF : ', Zref)
        # TODO choix de la variable a caler, par défaut c'est Z pour le moment
        obs_folder = os.path.join(self.base_folder, 'Observations')
        self.Z_obs = {}
        for station in Zref.keys():
            self.Z_obs[station] = {'time': [], 'Z': []}
            file_name = os.path.join(obs_folder, str(station) + '.loi')
            with open(file_name) as f:
                lines = f.readlines()[3:]
                # TODO handle time units !!!
                self.Z_obs[station]['time'] = [float(l.split()[0]) * 3600 for l in lines]
                self.Z_obs[station]['Z'] = [float(l.split()[1]) for l in lines]
        print('Z station', self.Z_obs)
        ista = 0
        for it, time in enumerate(dict_ref['time']):
            for station in Zref.keys():
                self.y0.append(self.Z_obs[station]['Z'][it])
                print(self.Z_obs[station]['Z'][it])
                delta_z = self.Z_obs[station]['Z'][it] - Zref[station][it]
                # Application du seuil de rejet misfit
                if abs(100 * np.divide(delta_z, Zref[station][it])) > self.seuil_rejet_misfit:
                    delta_z = 0.
                self.misfit.append(delta_z)
                ista += 1
        print('Y0', self.y0)

    def build_H_matrix(self):
        """

        """
        H = []
        # Getting Zref and KS values
        name_folder_ref = os.path.join(self.base_folder, 'run_ref')
        base_folder_perturb = os.path.join(self.base_folder, f'run_{self.ctrl_type}')
        with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
            dict_ref = json.load(f)

        Zref = []
        all_stations = []
        # Boucle sur les zones concernées
        for zone in self.zones:
            # Boucle sur les stations d'observation dans chaque zone
            for station in dict_ref['Z'][str(zone)]:
                if station not in all_stations:
                    Zref += dict_ref['Z'][str(zone)][station]
                    all_stations.append(station)
        Zref = np.array(Zref, dtype=float)
        print('Z reference', Zref)
        # Zref = np.concatenate([dict_ref['Z'][str(zone)] for zone in self.zones])
        # Getting initial values of KS
        if self.ctrlKs:
            data = self.dict_assim["ctrlKS"]
            KSminref = {str(zone["num_zone"]): zone["zone_info"]["ref_ks_min"]
                        for zone in data["lst_zone"] if zone["num_zone"] in self.zones}
            KSmajref = {str(zone["num_zone"]): zone["zone_info"]["ref_ks_maj"]
                        for zone in data["lst_zone"] if zone["num_zone"] in self.zones}
            self.param_ref = {'Ksmin': KSminref, 'Ksmaj': KSmajref}

        if self.ctrlLaw:
            data = self.dict_assim["ctrlLaw"]
            # Pour les lois on part d'un coeff ref a = 1, b=0
            coefAref = {str(zone["name_law"]): 1
                        for zone in data["lst_loi"] if zone["name_law"] in self.zones}
            coefBref = {str(zone["name_law"]): 0
                        for zone in data["lst_loi"] if zone["name_law"] in self.zones}
            self.param_ref = {'coefA': coefAref, 'coefB': coefBref}

        # Getting Z perturb and building H
        for i in range(self.nbperturb):
            print('Run perturbé', i)
            # Nom de dossier = './perturb
            # Fonctionne pour Law et KS normalement
            name_folder_pertub, type_perturb, val_perturb, zone_perturb = (
                get_perturb_folder(base_folder_perturb, i))

            print('Perturbation de type', type_perturb)
            name_folder_pertub = os.path.join(base_folder_perturb, name_folder_pertub)
            # name_folder_pertub = os.path.join(base_folder_perturb, f'perturb_{i}')
            with open(os.path.join(name_folder_pertub, 'Z_Q_assim.json')) as f:
                dict_perturb = json.load(f)

            Zperturb = []
            # Boucle sur les zones concernées
            all_stations = []
            for zone in self.zones:
                # Boucle sur les stations d'observation dans chaque zone
                for station in dict_perturb['Z'][str(zone)]:
                    if station not in all_stations:
                        Zperturb += dict_perturb['Z'][str(zone)][station]
                        all_stations.append(station)
            Zperturb = np.array(Zperturb, dtype=float)
            print('Zperturb iperturb = ', i + 1, Zperturb)
            # Deltas_param contient l'ensemble des différences entre les paramètres de REF et de
            # PERTURB Avec potentiellement des valeurs nulles pour les paramètres non modifiés Ici
            # pour KS, on a les différences sur KS_MIn et MAJ pour chaque zone.

            deltas_param = [val_perturb -
                            self.param_ref[type_perturb][str(zone_perturb)]]
            self.xb.append(self.param_ref[type_perturb][str(zone_perturb)])
            print('Deltas params', deltas_param)
            # On récupère la valeur du DeltaP effectif > 0 (les autres sont à 0)
            delta_p = deltas_param[np.argmax(np.abs(deltas_param))]
            print(delta_p)
            # H(:, ib) = (Z_perturb,ib - Z_ref) / (deltap_ib)
            H.append(np.divide(np.subtract(Zperturb, Zref), delta_p))
        H = np.array(H)
        # print(H)
        H = H.T
        print('Matrice H', H)
        print(H.shape)
        self.H = H

# if __name__ == '__main__':
#     M = ClassMatrix(base_folder)
#     M.build_H_matrix()
#     M.build_B_matrix_ini()
#     M.build_diago_R_matrix_ini()
#     M.build_misfit()
