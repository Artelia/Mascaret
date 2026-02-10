import numpy as np
from ClassMatrix import ClassMatrix

base_folder = r'../../mascaret/event1_1/'


class classBLUE:
    def __init__(self):
        self.analyse = None
        self.innovation = None
        self.K = None
        self.matrixes = ClassMatrix(base_folder)
        self.matrixes.build_all_matrix()


    def compute_BLUE(self):
        self.build_gain_K()
        self.build_analysis()


    def build_gain_K(self):
        invB = np.linalg.inv(self.matrixes.B)
        print(invB)
        R = np.diag(self.matrixes.R)
        invR = np.linalg.inv(R)
        print(invR)
        # H^T x R^-1
        HTinvR = np.matmul(np.transpose(self.matrixes.H), invR)
        print(HTinvR)
        temp1 = invB + np.matmul(HTinvR, self.matrixes.H)
        self.K = np.matmul(temp1, np.transpose(self.matrixes.H))
        print('Calcul de gain effactué. K=', self.K)


    def build_analysis(self):
        self.innovation = np.matmul(self.K, self.matrixes.y0)
        self.analyse = self.matrixes.xb + self.innovation
        self.matrixes.build_B_matrix_analysed(self.K)
        print('Calcul de l\'état analysé effectué')
        print(self.analyse)

    def build_analysis_V2(self):
        self.innovation = np.matmul(self.K, self.matrixes.y0)



if __name__ == '__main__':
    CB = classBLUE()
    CB.build_gain_K()
    CB.build_analysis()

