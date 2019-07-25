
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt


def read_loi(path):
    file= open(path)
    tab=[]
    for lng in file:
        lng=lng.split()
        if lng!=[] and lng[0]!='#':
            tab.append(lng)
    tab=np.array(tab,dtype=float)
    return tab
def inversion(M, colonne1,colonne2):
    for ligne in range(len(M)):
        M[ligne][colonne1], M[ligne][colonne2] = M[ligne][colonne2], M[ligne][colonne1]
    return M

def ptrait(tab):

    tab=inversion(tab, 0, 2)
    tab = inversion(tab, 0, 1)
    # print(tab)

    # trie de la colonne 0 à 2
    info=tab
    info = info[info[:, 2].argsort()]  # First sort doesn't need to be stable.
    info = info[info[:, 1].argsort(kind='mergesort')]
    info = info[info[:, 0].argsort(kind='mergesort')]

    return info
def courb(tab):
    fig = plt.figure()

    ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
    zav_sav=tab[0,0]
    i_old=0
    cmpt=0
    i_save=0
    listX=[2.018,4.019,4.269,5.269,5.019,6.769,9.768]
    #print(tab)
    for i, info in enumerate(tab):
        zav=info[0]
        if zav == zav_sav:
            i_save =i
        else:
            cmpt += 1
            # if zav_sav in listX:
            #     ax.plot(tab[i_old:i_save+1, 1],tab[i_old:i_save+1, 2], label=str(zav_sav),marker='+')
            #     ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., ncol=3)
            ax.plot(tab[i_old:i_save + 1, 1], tab[i_old:i_save + 1, 2], label=str(zav_sav), marker='+')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., ncol=3)
            zav_sav=zav
            i_old = i
    ax.plot(tab[i_old:i_save+1, 1],tab[i_old:i_save+1, 2], label=str(zav_sav))
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., ncol=3)

    cmpt += 1


    plt.title('deb =fct(am) pour un av')
    plt.show()
path='../mascaret/test.loi'
tab=read_loi(path)
tab=ptrait(tab)
#print(tab[np.where(tab[:, 0] == 3)])
courb(tab)
print(tab)


