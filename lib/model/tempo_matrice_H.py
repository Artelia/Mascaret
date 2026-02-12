import json
import os
import numpy as np

n_perturb = 4
zones = [2]
base_folder = r'../../mascaret/assim1/'


def get_perturb_folder(base_folder, iperturb):
    print('Finding perturbation folders in', base_folder)
    name_folder = None
    for folder in os.listdir(base_folder):
        print(folder)
        if f'pertub{iperturb}' in folder:
            name_folder = folder
            type_perturb = folder.split('_')[1]
            val_perturb = float(folder.split('_')[-1].replace('p', '.'))
    if name_folder is not None:
        return name_folder, type_perturb, val_perturb
    else:
        raise FileNotFoundError(f'Directory for perturbation number {iperturb} not found')


def build_B_matrix_ini(base_folder):
    json_path = os.path.join(base_folder, 'data_assim.json')
    with open(json_path) as f:
        dict_assim = json.load(f)
    liste_sigma = []
    for dict in dict_assim.get("ctrlKS").get("lst_zone"):
        print(dict)
        if dict.get("std") is None:
            raise KeyError("Key std not found in data_assim.json")
        liste_sigma.append(float(dict.get("std")))
    B = np.diag(liste_sigma, 0)
    print("Matrices des covariances d'erreur d'ébauche B", B)


def build_diago_R_matrix_ini(base_folder, nb_dt_obs):
    json_path = os.path.join(base_folder, 'data_assim.json')
    with open(json_path) as f:
        dict_assim = json.load(f)
    diag_R = []
    for dict in dict_assim.get("ctrlKS").get("lst_zone"):
        print(dict)
        if dict.get("std_obs") is None:
            raise KeyError("Key std_obs not found in data_assim.json")
        for sigma in dict.get("std_obs"):
            diag_R += [float(sigma) for i in range(nb_dt_obs)]
    print("Diagonales des matrices des covariances d'erreur d'observation R", diag_R)


def build_H_matrix(base_folder, zones, n_perturb):
    H = []
    # Getting Zref and KS values
    name_folder_ref = os.path.join(base_folder, 'run_ref')
    base_folder_perturb = os.path.join(base_folder, 'run_ctrlKS')
    with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
        dict_ref = json.load(f)
    Zref = np.concatenate([dict_ref['Z'][str(zone)] for zone in zones])

    # Getting Z perturb and building H
    for i in range(n_perturb):
        print('Run perturbé', i)
        # Nom de dossier = './perturb
        name_folder_pertub, type_perturb, val_perturb = get_perturb_folder(base_folder_perturb, i)
        print('Perturbation de type', type_perturb)
        name_folder_pertub = os.path.join(base_folder_perturb, name_folder_pertub)
        # name_folder_pertub = os.path.join(base_folder_perturb, f'perturb_{i}')
        with open(os.path.join(name_folder_pertub, 'Z_Q_assim.json')) as f:
            dict_perturb = json.load(f)
        Zperturb = np.concatenate([dict_perturb['Z'][str(zone)] for zone in zones])
        # Deltas_param contient l'ensemble des différences entre les paramètres de REF et de
        # PERTURB Avec potentiellement des valeurs nulles pour les paramètres non modifiés Ici
        # pour KS, on a les différences sur KS_MIn et MAJ pour chaque zone. Pour l'instant on
        # laisse toutes les zones, mais à terme on devrait pouvoir identifer la zone avec le nom
        # de dossier et calculer directement delta_p #TODO
        deltas_param = [dict_perturb[type_perturb][str(k)] - dict_ref[type_perturb][str(k)] for k in
                        zones]
        print('Deltas params', deltas_param)
        # On récupère la valeur du DeltaP effectif > 0 (les autres sont à 0)
        delta_p = deltas_param[np.argmax(np.abs(deltas_param))]
        print(delta_p)
        # H(:, ib) = (Z_perturb,ib - Z_ref) / (deltap_ib)
        H.append(np.divide(np.subtract(Zperturb, Zref), delta_p))
    H = np.array(H)
    print(H)
    H = H.T
    print(H)


if __name__ == '__main__':
    build_H_matrix(base_folder, zones, n_perturb)
    build_B_matrix_ini(base_folder)
    build_diago_R_matrix_ini(base_folder, 4)