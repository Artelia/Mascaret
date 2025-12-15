import json
import os
import numpy as np

n_perturb = 2
n_zones = 2
base_folder = r'../../mascaret/titi/'
H = []

# Getting Zref and KS values
name_folder_ref = os.path.join(base_folder, 'run_ref')
with open(os.path.join(name_folder_ref, 'Z_Q_assim.json')) as f:
    dict_ref = json.load(f)
Zref = np.concatenate([dict_ref['Z'][str(i)] for i in range(1, n_zones + 1)])
# Getting Z perturb and building H
for i in range(1, n_perturb+1):
    print('Run perturbé', i)
    name_folder_pertub = os.path.join(base_folder, f'perturb_{i}')
    with open(os.path.join(name_folder_pertub, 'Z_Q_assim.json')) as f:
        dict_perturb = json.load(f)
    Zperturb = np.concatenate([dict_perturb['Z'][str(i)] for i in range(1, n_zones + 1)])

    deltas_param = [dict_perturb['KS_maj'][str(k)] - dict_ref['KS_maj'][str(k)] for k in range(1, n_zones + 1)] + \
                   [dict_perturb['KS_min'][str(k)] - dict_ref['KS_min'][str(k)] for k in range(1, n_zones + 1)]
    print(deltas_param)
    delta_p = deltas_param[np.argmax(np.abs(deltas_param))]
    print(delta_p)
    H.append(np.divide(np.subtract(Zperturb, Zref), delta_p))
H = np.array(H)
H = H.T
print(H)



