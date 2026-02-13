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
        print(folder)
        if f'pertub{iperturb}' in folder:
            name_folder = folder
            type_perturb = folder.split('_')[1]
            val_perturb = float(folder.split('_')[-1].replace('p', '.'))
            zone_perturb = int(folder.split('_')[2])
    if name_folder is not None:
        return name_folder, type_perturb, val_perturb, zone_perturb
    else:
        raise FileNotFoundError(f'Directory for perturbation number {iperturb} not found')


class ClassMatrix:
    """"""
    # TODO Passer en argument d'entrée le dico ou json des paramètres d'assimilation !
    def __init__(self, base_folder, json_assim=None):
        """"""
        # Vecteur d'ébauche
        self.misfit = []
        self.B_analysed = None
        self.Z_obs = []
        self.xb = []
        # Vecteur d'observations
        self.y0= []
        self.KSref = None
        self.H = None
        self.B = None
        self.R = None
        if not(os.path.exists(base_folder)):
            raise FileNotFoundError(f'Unfound working folder : {base_folder}')
        self.base_folder = base_folder
        self.zones = []
        self.nbzones = 0
        json_path = os.path.join(self.base_folder, 'data_assim.json')
        print(self.base_folder, json_path)
        self.ctrlKs = False
        self.ctrlLaw = False
        with open(json_path) as f:
            self.dict_assim = json.load(f)

        # Récupération du type de controle
        if self.dict_assim.get("ctrlKS") is not None:
            self.ctrlKs = True
        if self.dict_assim.get("ctrlLaw") is not None:
            self.ctrlLaw = True

        # Récupération du nombre de zones et de la liste des zones
        if self.ctrlKs:
            self.zones = [dico.get("num_zone") for dico in self.dict_assim["ctrlKS"]["lst_zone"]]
            self.zones = np.unique(self.zones)
            self.nb_zones = len(self.zones)
        if self.ctrlLaw:
            self.zones = [dico.get("num_zone") for dico in self.dict_assim["ctrlLaw"]["lst_zone"]]
            self.zones = np.unique(self.zones)
            self.nb_zones = len(self.zones)

        # Récupération du nombre total de pas de temps d'observation
        name_folder_ref = os.path.join(self.base_folder, 'run_ref')
        with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
            dict_ref = json.load(f)
        self.nb_dt_obs = len(dict_ref['time'])

        # Récupération des zéros des observations
        self.zero_obs = {}
        if self.ctrlKs:
            for d in self.dict_assim["ctrlKS"]["lst_zone"]:
                dico = d.get("lst_obs", {})
                if dico != {}:
                    for ic, c in enumerate(dico.get("code")):
                        if c not in self.zero_obs.keys():
                            self.zero_obs[c] = dico.get("zero")[ic]

        # Récupération du nombre total de perturbations
        if self.ctrlKs:
            self.nbperturb = 0
            self.minperturb = self.dict_assim["ctrlKS"]["ksmin_perturb"][0]
            self.majperturb = self.dict_assim["ctrlKS"]["ksmaj_perturb"][0]
            for d in self.dict_assim["ctrlKS"]["lst_zone"]:
                if d.get("type") == "Ksmin":
                    self.nbperturb += 1
                    # self.nbperturb += int(np.ceil((d["val_max"] - d["val_min"])/self.minperturb)) + 1
                if d.get("type") == "Ksmaj":
                    self.nbperturb += 1
                    # self.nbperturb += int(np.ceil((d["val_max"] - d["val_min"])/self.majperturb)) + 1
            # self.nbperturb = 1
            print('Total number of perturbations:', self.nbperturb)


    def build_all_matrix(self):
        self.build_B_matrix_ini()
        self.build_diago_R_matrix_ini()
        self.build_H_matrix()
        self.build_misfit()


    def build_B_matrix_ini(self):
        liste_sigma = []
        if self.ctrlKs:
            for d in self.dict_assim.get("ctrlKS")["lst_zone"]:
                std_zone = d["std"]
                if d.get("std") is None:
                    raise KeyError("Key std not found in data_assim.json")
                if d.get("type") == "Ksmin":
                    liste_sigma += [2 * std_zone]
                    # liste_sigma += int(np.ceil((d["val_max"] - d["val_min"])/self.minperturb) + 1) * [std_zone]
                if d.get("type") == "Ksmaj":
                    liste_sigma += [2 * std_zone]
                    # liste_sigma += int(np.ceil((d["val_max"] - d["val_min"])/self.majperturb) + 1) * [std_zone]

        if self.ctrlLaw:
            raise NotImplementedError('Control law matrices not implemented yet')

        if len(liste_sigma) != self.nbperturb:
            raise ValueError(f'Problem with initial B matrix creation. '
                             f'Size should be {self.nbperturb}, it is {len(liste_sigma)}')
        self.B = np.diag(liste_sigma, 0)
        print("Matrices des covariances d'erreur d'ébauche B", self.B)


    def build_B_matrix_analysed(self, K):
        self.B_analysed = self.B - np.matmul(np.matmul(K, self.H), self.B)


    def build_diago_R_matrix_ini(self):
        diag_R = []
        #TODO faire sur toutes les obs dispos !, une seule fois
        num_stations = []
        for dico in self.dict_assim.get("ctrlKS").get("lst_zone"):
            print(dico)
            if int(dico.get("num_zone")) not in num_stations:
                num_stations.append(int(dico.get("num_zone")))
                dict2 = dico.get("lst_obs")
                if dict2.get("stderr") is None:
                    raise KeyError("Key std_obs not found in data_assim.json")
                for sigma in dict2.get("stderr"):
                    diag_R += [float(sigma) ** 2 for i in range(self.nb_dt_obs)]
        print("Diagonale des matrices des covariances d'erreur d'observation R", diag_R)
        self.R = np.array(diag_R)


    def build_misfit(self):
        name_folder_ref = os.path.join(self.base_folder, 'run_ref')
        with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
            dict_ref = json.load(f)

        Zref = {}
        for zone in self.zones:
            for station in dict_ref['Z'][str(zone)]:
                if station not in Zref.keys():
                    Zref[station] = []
        print(Zref)

        # Boucle sur les zones concernées
        for zone in self.zones:
            # Boucle sur les stations d'observation dans chaque zone
            for station in dict_ref['Z'][str(zone)]:
                Zref[station] += dict_ref['Z'][str(zone)][station]
        # Zref = np.array(Zref, dtype=float)
        print('ZREF : ', Zref)
        nb_time = len(dict_ref['time'])
        obs_folder = os.path.join(self.base_folder, 'Observations')
        self.Z_obs = {}
        for zone in self.zones:
            for station in dict_ref['Z'][str(zone)]:
                self.Z_obs[station] = {'time': [], 'Z': []}
                file_name = os.path.join(obs_folder, str(station) + '.loi')
                with open(file_name) as f:
                    lines = f.readlines()[3:]
                    # TODO handle time units !!!
                    self.Z_obs[station]['time'] = [float(l.split()[0]) * 3600 for l in lines]
                    self.Z_obs[station]['Z'] = [float(l.split()[1]) for l in lines]
        print('Z station', self.Z_obs)
        ista = 0
        for zone in self.zones:
            for it, time in enumerate(dict_ref['time']):
                for station in dict_ref['Z'][str(zone)]:
                    idx_zref = ista * nb_time + it
                    self.y0.append(self.Z_obs[station]['Z'][it])
                    # print(idx_zref, Zref[idx_zref])
                    print(self.Z_obs[station]['Z'][it])
                    self.misfit.append(self.Z_obs[station]['Z'][it] - Zref[station][it])
                    ista += 1
            print('Y0', self.y0)

    def build_H_matrix(self):
        """

        """
        H = []
        # Getting Zref and KS values
        name_folder_ref = os.path.join(self.base_folder, 'run_ref')
        base_folder_perturb = os.path.join(self.base_folder, 'run_ctrlKS')
        with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
            dict_ref = json.load(f)

        Zref = []
        # Boucle sur les zones concernées
        for zone in self.zones:
            # Boucle sur les stations d'observation dans chaque zone
            for station in dict_ref['Z'][str(zone)]:
                Zref += dict_ref['Z'][str(zone)][station]
        Zref = np.array(Zref, dtype=float)
        print('Z reference', Zref)
        # Zref = np.concatenate([dict_ref['Z'][str(zone)] for zone in self.zones])
        # Getting initial values of KS
        if self.ctrlKs:
            dico = self.dict_assim["generate_instance"]["dico_ks"]
            print(dico)
            KSminref = {str(zone): dico["minbedcoef"][zone] for zone in self.zones}
            KSmajref = {str(zone): dico["majbedcoef"][zone] for zone in self.zones}
            self.KSref = {'Ksmin': KSminref, 'Ksmaj': KSmajref}

        if self.ctrlLaw:
            raise NotImplementedError('CtrlLaw not yet implemented')
        # Getting Z perturb and building H
        for i in range(self.nbperturb):
            print('Run perturbé', i)
            # Nom de dossier = './perturb
            name_folder_pertub, type_perturb, val_perturb, zone_perturb = (
                get_perturb_folder(base_folder_perturb, i))

            print('Perturbation de type', type_perturb)
            name_folder_pertub = os.path.join(base_folder_perturb, name_folder_pertub)
            print(name_folder_pertub)
            # name_folder_pertub = os.path.join(base_folder_perturb, f'perturb_{i}')
            with open(os.path.join(name_folder_pertub, 'Z_Q_assim.json')) as f:
                dict_perturb = json.load(f)

            Zperturb= []
            # Boucle sur les zones concernées
            for zone in self.zones:
                # Boucle sur les stations d'observation dans chaque zone
                for station in dict_perturb['Z'][str(zone)]:
                    Zperturb += dict_perturb['Z'][str(zone)][station]
            Zperturb = np.array(Zperturb, dtype=float)
            print('Zperturb iperturb = ', i+1 ,Zperturb)
            # Deltas_param contient l'ensemble des différences entre les paramètres de REF et de
            # PERTURB Avec potentiellement des valeurs nulles pour les paramètres non modifiés Ici
            # pour KS, on a les différences sur KS_MIn et MAJ pour chaque zone.

            deltas_param = [val_perturb -
                            self.KSref[type_perturb][str(zone_perturb)] ]
            self.xb.append(self.KSref[type_perturb][str(zone_perturb)])
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
