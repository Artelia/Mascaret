import numpy as np
import sys
try:
    from .ClassMatrix import ClassMatrix
except:
    print('Using non relative imports')
    from ClassMatrix import ClassMatrix
import os
import json

# base_folder = r'../../mascaret/event1_1/'


class classBLUE:
    def __init__(self, base_folder):
        self.R = None
        self.analyse = None
        self.innovation = None
        self.K = None
        print('Using Blue in ', base_folder)
        self.base_folder = base_folder
        self.matrixes = ClassMatrix(self.base_folder)
        self.matrixes.build_all_matrix()


    def compute_BLUE(self):
        self.build_gain_K()
        self.build_analysis()


    def build_gain_K(self):
        # invB = np.linalg.inv(self.matrixes.B)
        # print(invB)
        self.R = np.diag(self.matrixes.R)
        invR = np.linalg.inv(self.R)
        print(invR)
        # Calcul de BHt
        BHT = self.matrixes.B @ self.matrixes.H.transpose()
        # H^T x R^-1
        # Calcul de HBHt
        print('BHT', BHT)
        HBHT = self.matrixes.H @ self.matrixes.B @ self.matrixes.H.transpose()
        # Calcul de (HBHt + R)^-1
        print('HBHT', HBHT)
        HBHT_plus_R = np.linalg.inv(HBHT + self.R)
        # HTinvR = np.matmul(np.transpose(self.matrixes.H), invR)
        # print(HTinvR)
        # temp1 = invB + np.matmul(HTinvR, self.matrixes.H)
        # self.K = np.matmul(temp1, np.transpose(self.matrixes.H))
        self.K = BHT @ HBHT_plus_R
        print('Calcul de gain effactué. K=', self.K)


    def build_analysis(self):
        print('Ebauche xb', self.matrixes.xb)
        print('MISFIT', self.matrixes.misfit)

        self.innovation = np.matmul(self.K, self.matrixes.misfit)
        self.analyse = self.matrixes.xb + self.innovation
        self.analyse = self.matrixes.xb + self.K @ (self.matrixes.y0 - self.matrixes.H @ self.matrixes.xb)
        self.analyse = self.matrixes.xb + self.K @ self.matrixes.misfit
        self.matrixes.build_B_matrix_analysed(self.K)
        print('Calcul de l\'état analysé effectué')
        print(self.analyse)

    def clean_result_file(self):
        with open(os.path.join(self.base_folder, 'blue_results.txt'), 'w' ) as f:
            f.write('BLUE assimilation step results \n')
            f.write('--'*50 + '\n')


    def store_results(self, first):
        # First adding xa to data_assim.json
        json_assim = os.path.join(self.base_folder, 'data_assim.json')
        with open(json_assim) as f:
            data_assim = json.load(f)
        print(data_assim)
        d = data_assim.get('ctrlKS', {})
        print(d)
        for izone, lzones in enumerate(d.get("lst_zone", [])):
            if not lzones:
                pass
            else:
                if d["lst_zone"][izone].get("xa") is None or first:
                    d["lst_zone"][izone]["xa"] = [round(self.analyse[izone],2)]
                else:
                    d["lst_zone"][izone]["xa"].append(round(self.analyse[izone],2))
        data_assim['ctrlKS'] = d
        with open(json_assim, 'w') as f:
            json.dump(data_assim, f, indent=4)
        # Then storing in txt file every BLUE matrix for debug/verif
        with open(os.path.join(self.base_folder, 'blue_results.txt'), 'a' ) as f:
            f.write('Matrice B \n')
            current_mat = self.matrixes.B
            sep = '\t\t\t'
            for i in range(current_mat.shape[1]):
                # for j in range(self.matrixes.B.shape()[1]):
                lg = sep.join(np.array(current_mat[:, i], dtype='str'))
                f.write('|' + lg + '|\n')
            f.write('--'*50 + '\n')

            f.write('Matrice R \n')
            current_mat = self.R
            for i in range(current_mat.shape[1]):
                # for j in range(self.matrixes.B.shape()[1]):
                lg = sep.join(np.array(current_mat[:, i], dtype='str'))
                f.write('|' + lg + '|\n')
            f.write('--'*50 + '\n')

            f.write('Matrice H \n')
            current_mat = self.matrixes.H
            for i in range(current_mat.shape[1]):
                # for j in range(self.matrixes.B.shape()[1]):
                lg = sep.join(np.array(current_mat[:, i], dtype='str'))
                f.write('|' + lg + '|\n')
            f.write('--'*50 + '\n')

            f.write('Matrice K \n')
            current_mat = self.K
            for i in range(current_mat.shape[1]):
                # for j in range(self.matrixes.B.shape()[1]):
                lg = sep.join(np.array(current_mat[:, i], dtype='str'))
                f.write('|' + lg + '|\n')
            f.write('--'*50 + '\n')

            f.write('Etat analyse xa \n')
            current_mat = self.analyse
            # for i in range(current_mat.shape[0]):
                # for j in range(self.matrixes.B.shape()[1]):
            lg = sep.join(np.array(current_mat[:], dtype='str'))
            f.write('|' + lg + '|\n')


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        raise ValueError("No base folder file provided.")
    base_folder = sys.argv[1]
    # base_folder = r'../../mascaret/event1_1/'
    print('BASE_FOLDER', base_folder)
    CB = classBLUE(base_folder)
    CB.compute_BLUE()
    #TODO first doit être un bool de first step assim si on enchaine
    CB.store_results(first=True)
    # CB.build_gain_K()
    # CB.build_analysis()
    # CB.clean_result_file()
    # CB.store_results()

