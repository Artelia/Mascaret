import numpy as np
import os
from ClassMatrix import ClassMatrix

base_folder = r'../../mascaret/assim1/'


class classBLUE:
    def __init__(self):
        self.K = None
        self.matrixes = ClassMatrix(base_folder)
        self.matrixes.build_all_matrix()

    def build_gain_K(self):
        invB = np.linalg.inv(self.matrixes.B)
        print(invB)
        invR = 1./self.matrixes.R
        print(invR)
        HTinvR = np.matmul(np.transpose(self.matrixes.H), invR)
        print(HTinvR)
        temp1 = invB + np.matmul(HTinvR, self.matrixes.H)
        self.K = np.matmul(temp1, np.transpose(self.matrixes.H))
        print('Calcul de gain effactué. K=', self.K)


if __name__ == '__main__':
    CB = classBLUE()
    CB.build_gain_K()

