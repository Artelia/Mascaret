import numpy as np
import sys
try:
    from .ClassMatrix import ClassMatrix
except:
    print('Using non relative imports')
    from ClassMatrix import ClassMatrix
import os
import json


def write_matrix_auto(f, matrix, decimals=5):
    """Writes matrix to file
    :param f: file object (already opened by python),
    :param matrix: matrix to write (1 or 2 dimensions)
    :param decimals: number of decimal places to use
    """
    if len(matrix.shape) == 2:
        # Formater toutes les valeurs en chaînes
        str_matrix = [[f"{val:.{decimals}f}" for val in row] for row in matrix]

        # Largeur max par colonne
        col_widths = [
            max(len(str_matrix[r][c]) for r in range(len(str_matrix)))
            for c in range(len(str_matrix[0]))
        ]

        for row in str_matrix:
            line = "  ".join(val.rjust(col_widths[c]) for c, val in enumerate(row))
            f.write(line + "\n")
    elif len(matrix.shape) == 1:
        # Formater toutes les valeurs en chaînes
        str_matrix = [f"{val:.{decimals}f}" for val in matrix]
        print(str_matrix)

        # Largeur max par colonne
        col_width = [len(val) for val in str_matrix]

        line = "  ".join(val.rjust(col_width[c]) for c, val in enumerate(str_matrix))
        print(line)
        f.write(line + "\n")


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

        self.innovation =self.K @ self.matrixes.misfit
        self.analyse = self.matrixes.xb + self.innovation

        # Clipping xa based on min and max values
        for ia, xa in enumerate(self.analyse):
            if xa < self.matrixes.min_values[ia]:
                self.analyse[ia] = self.matrixes.min_values[ia]
            if xa > self.matrixes.max_values[ia]:
                self.analyse[ia] = self.matrixes.max_values[ia]
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
            write_matrix_auto(f, current_mat)

            f.write('Matrice R \n')
            current_mat = self.R
            write_matrix_auto(f, current_mat)

            f.write('Matrice H \n')
            current_mat = self.matrixes.H
            write_matrix_auto(f, current_mat)

            f.write('Matrice K \n')
            current_mat = self.K
            write_matrix_auto(f, current_mat)

            f.write('Etat analyse xa \n')
            current_mat = self.analyse
            write_matrix_auto(f, current_mat)


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

