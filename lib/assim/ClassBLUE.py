import numpy as np
import sys
try:
    from .ClassMatrix import ClassMatrix
except:
    print('Using non relative imports')
    from ClassMatrix import ClassMatrix
import os
import json

def write_matrix_2dims(file, matrix):
    """Writes matrix to file
    :param file: file object (already opened by python),
    :param matrix: matrix to write (1 or 2 dimensions)"""
    sep = '\t\t\t'
    if len(matrix.shape) == 2:
        for i in range(matrix.shape[1]):
            lg = sep.join(np.array(matrix[:, i], dtype='str'))
            file.write('|' + lg + '|\n')
        file.write('--' * 50 + '\n')
    elif len(matrix.shape) == 1:
        lg = sep.join(np.array(matrix[:], dtype='str'))
        file.write('|' + lg + '|\n')
        file.write('--' * 50 + '\n')

class classBLUE:
    """Class that computes the analysed state of parameters using BLUE method"""

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
        """ Computes different BLUE steps to get analysed state """
        self.build_gain_K()
        self.build_analysis()


    def build_gain_K(self):
        """ Computes gain matrix K : K =BH^t (HBH^t + R)^-1 """

        self.R = np.diag(self.matrixes.R)
        # Calcul de BHt
        BHT = self.matrixes.B @ self.matrixes.H.transpose()
        # Calcul de HBHt
        HBHT = self.matrixes.H @ self.matrixes.B @ self.matrixes.H.transpose()
        # Calcul de (HBHt + R)^-1
        HBHT_plus_R = np.linalg.inv(HBHT + self.R)
        self.K = BHT @ HBHT_plus_R
        print('Calcul de gain effactué. K=', self.K)


    def build_analysis(self):
        """ Computes analysed state xa : x_a = x_b + K*misfit """

        print('Ebauche xb', self.matrixes.xb)
        print('MISFIT', self.matrixes.misfit)

        self.innovation = np.matmul(self.K, self.matrixes.misfit)
        self.analyse = self.matrixes.xb + self.innovation
        self.analyse = self.matrixes.xb + self.K @ (self.matrixes.y0 -
                                                    self.matrixes.H @ self.matrixes.xb)
        self.analyse = self.matrixes.xb + self.K @ self.matrixes.misfit
        self.matrixes.build_B_matrix_analysed(self.K)
        print('Calcul de l\'état analysé effectué')
        print(self.analyse)

    def clean_result_file(self):
        """ Overwrites matrix file """

        with open(os.path.join(self.base_folder, 'blue_results.txt'), 'w' ) as f:
            f.write('BLUE assimilation step results \n')
            f.write('--'*50 + '\n')


    def store_results(self, first):
        """ Store results in file
         :param first: True if first assimilation step
         """
        # First adding xa to data_assim.json
        json_assim = os.path.join(self.base_folder, 'data_assim.json')
        with open(json_assim) as f:
            data_assim = json.load(f)
        d = data_assim.get('ctrlKS', {})
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
            write_matrix_2dims(f, current_mat)

            f.write('Matrice R \n')
            current_mat = self.R
            write_matrix_2dims(f, current_mat)

            f.write('Matrice H \n')
            current_mat = self.matrixes.H
            write_matrix_2dims(f, current_mat)

            f.write('Matrice K \n')
            current_mat = self.K
            write_matrix_2dims(f, current_mat)

            f.write('Etat analyse xa \n')
            current_mat = self.analyse
            write_matrix_2dims(f, current_mat)


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

