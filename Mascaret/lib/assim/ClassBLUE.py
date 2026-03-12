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

    def __init__(self, base_folder, ctrl_type):
        self.analyse = None
        self.innovation = None
        self.K = None
        self.ctrl_type = ctrl_type
        print('Using Blue in ', base_folder)
        self.base_folder = base_folder
        self.json_assim = os.path.join(self.base_folder, 'data_assim.json')
        with open(self.json_assim) as f:
            self.data_assim = json.load(f)
        self.iterations_sigma = self.data_assim.get(ctrl_type, {}).get("iterations_sigma", 0)
        self.matrixes = ClassMatrix(self.base_folder, self.ctrl_type)
        self.matrixes.build_all_matrix()
        self.current_B = self.matrixes.B
        self.current_R = np.diag(self.matrixes.R)
        self.so = 1
        self.old_so = 0
        self.residual = None
        # Une valeur de sb par type de perturbation (Ksmin et Ksmaj par ex)
        self.sb = [1] * np.max(self.matrixes.type_perturb)
        self.old_sb = [0] * np.max(self.matrixes.type_perturb)
        self.delta_so = 1.
        self.delta_sb = [1] * np.max(self.matrixes.type_perturb)
        self.raison_arret = ""

    def compute_BLUE(self):
        """ Computes different BLUE steps to get analysed state """
        for i in range(self.iterations_sigma):
            self.build_gain_K()
            self.build_analysis()
            self.calc_so_sb()

            # Arrêt si un des sb est < 0
            if np.any(np.array(self.sb) < 0):
                self.raison_arret = "Arrêt sur critère sb < 0"
                self.store_results(first=(i == 0), assim_step=i)
                break
            # Arrêt si delta_sb et delta_so sont < 1e-3
            elif (self.delta_so < 1e-3) and (np.all(np.array(self.delta_sb) < 1e-3)):
                self.raison_arret = ("'Arret sur critere de convergence de sb et so. Variation "
                                     "inférieure à 1e-3 entre deux pas d'assimilation")
                self.store_results(first=(i == 0), assim_step=i)
                break

            self.store_results(first=(i == 0), assim_step=i)
            # Updating B and R values
            # B = sb * B_initialz
            # Avec sb qui dépend du type de perturbation, appliqué aux colonnes correspondantes
            for j in range(self.current_B.shape[1]):
                isigma = self.matrixes.type_perturb[j] - 1
                self.current_B[:, j] = self.sb[isigma] * self.current_B[:, j]
            # R = so * R_initial
            self.current_R = self.so * np.diag(self.matrixes.R)
            print(self.current_R)

        self.raison_arret = "Nombre iterations sigma atteint"

    def build_gain_K(self):
        """ Computes gain matrix K : K =BH^t (HBH^t + R)^-1 """
        # Calcul de BHt
        BHT = self.current_B @ self.matrixes.H.transpose()
        # Calcul de HBHt
        HBHT = self.matrixes.H @ self.current_B @ self.matrixes.H.transpose()
        # Calcul de (HBHt + R)^-1
        HBHT_plus_R = np.linalg.inv(HBHT + self.current_R)
        self.K = BHT @ HBHT_plus_R
        print('Calcul de gain effactué. K=', self.K)

    def calc_so_sb(self):
        trace_HBHT = []
        self.old_sb = np.copy(self.sb)
        self.old_so = np.copy(self.so)

        for itype in range(np.max(self.matrixes.type_perturb)):
            B_tempo = np.copy(self.current_B)
            # Boucle sur les colonnes de B
            for j in range(B_tempo.shape[1]):
                if self.matrixes.type_perturb[j] != itype + 1:
                    B_tempo[:, j] = np.zeros(B_tempo.shape[0])
            print(B_tempo)
            HBHT = self.matrixes.H @ B_tempo @ self.matrixes.H.transpose()
            trace_HBHT.append(np.trace(HBHT))
        print('Trace HBHT', trace_HBHT)
        for itype in range(np.max(self.matrixes.type_perturb)):
            self.sb[itype] = np.divide(np.dot(self.matrixes.misfit, self.matrixes.H @ self.analyse),
                                       trace_HBHT[itype])
        self.residual = np.array(self.matrixes.misfit) - self.matrixes.H @ self.analyse
        # Ajout de la nouvelle valeur de so
        self.so = np.divide(np.dot(self.matrixes.misfit, self.residual), np.trace(self.current_R))
        self.delta_so = abs(self.so - self.old_so)
        self.delta_sb = np.abs(np.subtract(self.sb, self.old_sb))

    def build_analysis(self):
        """ Computes analysed state xa : x_a = x_b + K*misfit """

        print('Ebauche xb', self.matrixes.xb)
        print('MISFIT', self.matrixes.misfit)

        self.innovation = self.K @ self.matrixes.misfit
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

        with open(os.path.join(self.base_folder, 'blue_results.txt'), 'w') as f:
            f.write('BLUE assimilation step results \n')
            f.write('--' * 50 + '\n')

    def _update_xa(self, first):
        """Update xa values in data_assim dict."""
        # TODO éviter variable 1 lettre
        d = self.data_assim.get(self.ctrl_type, {})
        lst_var = "lst_zone" if self.ctrl_type == 'ctrlKS' else "lst_loi"
        for izone, lzone in enumerate(d.get(lst_var, [])):
            if not lzone:
                continue
            xa_val = round(self.analyse[izone], 2)
            if d[lst_var][izone].get("xa") is None or first:
                d[lst_var][izone]["xa"] = [xa_val]
            else:
                d[lst_var][izone]["xa"].append(xa_val)
        with open(self.json_assim, 'w') as f:
            json.dump(self.data_assim, f, indent=4)

    def _write_matrix(self, f, label, mat):
        """Write a labeled matrix to file."""
        f.write(f'{label}\n')
        write_matrix_auto(f, mat)

    def _write_matrix_safe(self, f, label, mat):
        """Write a labeled matrix to file, ignoring errors."""
        try:
            self._write_matrix(f, label, np.array(mat))
        except Exception as e:
            print(e)

    def store_results(self, first, assim_step):
        """ Store results in file
         :param first: True if first assimilation step
         """
        # First adding xa to data_assim.json
        # json_assim = os.path.join(self.base_folder, 'data_assim.json')
        # with open(json_assim) as f:
        #     data_assim = json.load(f)

        self._update_xa(first)

        # Then storing in txt file every BLUE matrix for debug/verif
        with open(os.path.join(self.base_folder, 'blue_results.txt'), 'a') as f:
            if first:
                if first:
                    f.write(f'Assimilation - {self.ctrl_type}\n')
                    self._write_matrix(f, 'Matrice H', self.matrixes.H)
                    f.write(25 * '*-' + '\n')

            f.write(f'Assimilation step number {assim_step + 1}\n')
            for label, mat in [
                ('Matrice B', self.current_B),
                ('Matrice R', self.current_R),
                ('Matrice K', self.K),
                ('Etat analyse xa', self.analyse),
            ]:
                self._write_matrix(f, label, mat)

            f.write('Sigma o\n')
            f.write(str(self.so) + '\n')

            for label, mat in [
                ('Sigma b par type', self.sb),
                ('Residual', self.residual),
                ('Misfit', self.matrixes.misfit),
                ('Observations Y0', self.matrixes.y0),
                ('Type perturbations', self.matrixes.type_perturb),
            ]:
                self._write_matrix_safe(f, label, mat)

            f.write(25 * '*-' + '\n')
            f.write(self.raison_arret)


if __name__ == '__main__':
    if len(sys.argv) <= 2:
        raise ValueError(
            "No base folder file provided and no assimilation type . Usage: ClassBLUE.py <path> "
            "<ctrl_type>")
    base_folder = sys.argv[1]
    ctrl_type = sys.argv[2]
    # base_folder = r'../../mascaret/event1_1/'
    print('BASE_FOLDER', base_folder)
    CB = classBLUE(base_folder, ctrl_type)
    CB.compute_BLUE()
    # TODO first doit être un bool de first step assim si on enchaine
    # CB.store_results(first=True)
