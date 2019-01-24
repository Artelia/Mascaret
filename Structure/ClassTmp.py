# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2017
copyright            : (C) 2017 by Artelia
email                :
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
from matplotlib.patches import Polygon as mpoly
from matplotlib.figure import Figure

from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *

if int(qVersion()[0]) < 5:  # qt4

    from qgis.PyQt.QtGui import *

    try:
        from matplotlib.backends.backend_qt4agg \
            import FigureCanvasQTAgg as FigureCanvas
    except:
        from matplotlib.backends.backend_qt4agg \
            import FigureCanvasQT as FigureCanvas
    # ***************************
    try:
        from matplotlib.backends.backend_qt4agg \
            import NavigationToolbar2QTAgg as NavigationToolbar
    except:
        from matplotlib.backends.backend_qt4agg \
            import NavigationToolbar2QT as NavigationToolbar
else:  # qt4
    from qgis.PyQt.QtWidgets import *

    try:
        from matplotlib.backends.backend_qt5agg \
            import FigureCanvasQTAgg as FigureCanvas
    except:
        from matplotlib.backends.backend_qt5agg \
            import FigureCanvasQT as FigureCanvas
    # ***************************
    try:
        from matplotlib.backends.backend_qt5agg \
            import NavigationToolbar2QTAgg as NavigationToolbar
    except:
        from matplotlib.backends.backend_qt5agg \
            import NavigationToolbar2QT as NavigationToolbar





from shapely.geometry import Polygon,LineString,GeometryCollection


class ClassTmp(QDialog):

    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb =  mgis.mdb
        self.id_config=0
        #check test
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/test_graph.ui'), self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.gui_graph(self.ui)
        self.poly()

    def gui_graph(self, ui):
        self.verticalLayout1 = QVBoxLayout(ui.widget_figure)
        self.verticalLayout1.setObjectName("verticalLayout1")
        self.verticalLayout1.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.verticalLayout2 = QVBoxLayout(ui.widget_toolsbar)
        self.verticalLayout2.setObjectName("verticalLayout2")
        self.verticalLayout2.addWidget(self.toolbar)

    def get_param_g(self):
        """get general parameters"""
        list_recup=['eptab','cottab','firstw']
        param_g={}
        for info in list_recup:
            where="id_config = {0} AND var = '{1}' ".format(self.id_config ,info)
            rows=self.mdb.select('struct_param', where=where,list_var=['value'])
            if rows['value']:
                param_g[info]=rows['value'][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info('{} not specified in struct_param table'.format(info))
        # cas pont cadre
        param_g['cotpc']= param_g['cottab']- param_g['eptab']

        return param_g

    def get_param_elem(self,id_elem):
        """get element parameters"""
        list_recup = ['width']
        param_elem = {}
        for info in list_recup:
            where = "id_config = {0} AND id_elem= {1} AND var = '{2}' ".format(self.id_config, id_elem, info)
            rows = self.mdb.select('struct_elem_param', where=where, list_var=['value'])
            if rows['value']:
                param_elem[info] = rows['value'][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info('{} not specified in struct_elem_param table'.format(info))


        return param_elem

    def get_profil(self):
        """profil coordonnee"""
        where = "id_config = {0}".format(self.id_config)
        order = "order_"
        profil = self.mdb.select('profil_struct', where=where, order=order, list_var=['x,z'])
        return profil

    def poly_pont_cadre(self, param_g, param_elem, zmin=-99999,x0=None):
        if x0 is None:
            x0=param_g['firstw']#point depart
        x1=x0+param_elem['width']
        z=param_g['cotpc']#point haut
        zmin_t = zmin- 10
        if zmin < z:
            poly_t = Polygon([[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
        else:
            poly_t = GeometryCollection()
            print('Pb z de la traver')
        return poly_t

    def poly_profil(self, profil, zmin=-99999):

        zmin_p = zmin - 20
        x0_p= profil['x'][0]-1# -1 est pour évité le cas du 0
        z0_p= profil['z'][0]
        liste_poly=[[x0_p,zmin_p],[x0_p,z0_p]]
        for x,z in list(zip(profil['x'],profil['z'])):
            liste_poly.append([x,z])

        liste_poly.append([profil['x'][-1], zmin_p])
        liste_poly.append([x0_p,zmin_p])
        poly_p = Polygon(liste_poly)
        return poly_p

    def poly(self):
        # recuperation val général  pont cadre
        param_g=self.get_param_g()
        print(param_g)
        id_elem=0
        param_elem=self.get_param_elem(id_elem)
        print(param_elem)
        profil = self.get_profil()
        zmin=min(profil['z'])
        print(zmin)

        poly_p=self.poly_profil(profil,zmin)

        poly_cadre=self.poly_pont_cadre(param_g, param_elem, zmin, x0=param_g['firstw'])
        #

        # print(poly_cadre.exterior.xy)
        # if not poly_p.is_empty:
        #     self.draw_test(poly_p, decal_ax=10)
        #
        # if not poly_cadre.is_empty:
        #     self.draw_test(poly_cadre,decal_ax=10)

        poly_final=poly_cadre.difference(poly_p)
        if not poly_final.is_empty:
            self.draw_test(poly_final, decal_ax=10)



    def copy_profil(self,gid,feature=None):
        """Profil copy"""

        colonnes=['id_config','id_prof_ori','order_','x','z']
        tab = {'x': [], 'z': []}
        if feature is None:
            where = "gid = '{0}' ".format(gid)
            feature=self.mdb.select('profiles',list_var=['x','z'])
            tab['x'] = [float(var) for var in feature["x"][0].split()]
            tab['z'] = [float(var) for var in feature["z"][0].split()]
        elif feature["x"] and feature["z"]:
            tab['x'] = [float(var) for var in feature["x"].split()]
            tab['z'] = [float(var) for var in feature["z"].split()]

        else:
            self.mgis.add_info("Check if the profile is saved.")
            return
        xz = list(zip(tab['x'], tab['z']))
        values=[]
        for order,(x,z) in enumerate(xz):
            values.append([self.id_config,gid,order,x,z])

        self.mdb.insert_res('profil_struct', values, colonnes)




    def draw_test(self,poly, title=None,decal_ax=1):

        ax = self.figure.add_subplot(111)
        # ax.grid(True)
        new_poly = [ coord for coord in poly.exterior.coords]

        (minx, miny, maxx, maxy) = poly.bounds
        poly_d = mpoly(new_poly, facecolor='blue', edgecolor='red',alpha=0.5)
        ax.add_patch(poly_d)

        ax.set_xlim((minx-decal_ax, maxx+decal_ax))
        ax.set_ylim((miny-decal_ax, maxy+decal_ax))
        if title is not None:
            ax.set_title(title)

        self.canvas.draw()


if __name__ == '__main__':
    # a = Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
    # draw_test(a,'toto')
    pass