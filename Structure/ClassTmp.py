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
import math as m
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


from shapely.geometry import *
import shapely.affinity
from shapely import wkb
class ClassTmp(QDialog):

    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb =  mgis.mdb
        self.id_config=2 #cadre
        self.config_type='cadre'
        # self.id_config=3 #arc cercl
        # self.config_type='arch'
        #check test
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/test_graph.ui'), self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.gui_graph(self.ui)
        self.create_poly_elem()

    def gui_graph(self, ui):
        self.verticalLayout1 = QVBoxLayout(ui.widget_figure)
        self.verticalLayout1.setObjectName("verticalLayout1")
        self.verticalLayout1.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.verticalLayout2 = QVBoxLayout(ui.widget_toolsbar)
        self.verticalLayout2.setObjectName("verticalLayout2")
        self.verticalLayout2.addWidget(self.toolbar)

    def get_param_g(self,list_recup):
        """get general parameters"""
        param_g={}
        for info in list_recup:
            where="id_config = {0} AND var = '{1}' ".format(self.id_config ,info)
            rows=self.mdb.select('struct_param', where=where,list_var=['value'])
            if rows['value']:
                param_g[info]=rows['value'][0]
            else:
                if self.mgis.DEBUG:
                    self.mgis.add_info('{} not specified in struct_param table'.format(info))

        return param_g

    def get_param_elem(self,id_elem,list_recup):
        """get element parameters"""
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

    def checkprofil(self):
        where = "id_config = {0}".format(self.id_config)
        profil = self.mdb.select('profil_struct', where=where,list_var=['id_prof_ori'])
        if profil['id_prof_ori']:
            return True
        else:
            return False

    def poly_pont_cadre(self, param_g, param_elem, zmin=-99999,x0=None):
        if x0 is None:
            x0 = param_g['firstw']#point depart
        x1 = x0 + param_elem['width']
        z = param_g['cotpc']#point haut
        zmin_t = zmin- 10
        if zmin < z:
            poly_t = Polygon([[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
        else:
            poly_t = GeometryCollection()

            print('Inconsistent Z for the span')
        return poly_t

    def poly_arch(self, param_g, param_elem, zmin=-99999,type='circle',x0=None):
        if x0 is None:
            x0 = param_g['firstw']#point depart
        x1 = x0 + param_elem['width']
        x_c= param_elem['width']/2.+x0
        z = param_elem['cotarc']
        print(type)
        if type=='ellipse':
            zmax = param_elem['cotmax']
            #hyp. zmax-z=b/2
            b=2*(zmax-z)
            z_c=zmax-b
            frac=m.pow(x0-x_c,2)/(1-m.pow(z-z_c,2)/m.pow(b,2))
            a=m.sqrt(frac)
        elif type=='circle':
            b=param_elem['width']/2.
            a=b
            z_c = z
        else:
            poly_t = GeometryCollection()
            msg = 'Unkwnown arch : {}'.format(type)
            if self.mgis.DEBUG:
                self.mgis.add_info(msg)
            print(msg)
            return poly_t

        zmin_t = zmin- 10
        if zmin < z:
            # Let create a circle of radius 1 around center point:
            circ = Point([x_c,z_c]).buffer(1)
            # Let create the ellipse along x and y:
            ell = shapely.affinity.scale(circ, int(a), int(b))
            # # If one need to rotate it clockwise along an upward pointing x axis:
            # poly_t = shapely.affinity.rotate(ell, 90 - ellipse[2])
            # # According to the man, a positive value means a anti-clockwise angle,
            # # and a negative one a clockwise angle.
            poly = Polygon([[x_c-a-1,  z-b*2], [x_c-a-1, z], [x_c+a+1, z], [x_c+a+1,  z-b*2], [x_c-a-1, z-b*2]])
            ell = ell.difference(poly) # demi circle
            poly = Polygon([[x0, zmin_t], [x0, z], [x1, z], [x1, zmin_t], [x0, zmin_t]])
            poly_t=ell.union(poly)
        else:
            poly_t = GeometryCollection()
            msg='Inconsistent Z for the span'
            if self.mgis.DEBUG:
                self.mgis.add_info(msg)
            print(msg)
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

    def create_poly_elem(self):
        # TODO reactualiser variable
        # get profil
        if self.checkprofil():
            profil = self.get_profil()
        else:
            msg="Profile copy isn't found"
            self.mgis.add_info(msg)
            print(msg)
            return
        zmin=min(profil['z'])
        poly_p=self.poly_profil(profil,zmin)
        if poly_p.is_empty:
            msg = 'Profile polygon is empty.'
            if self.mgis.DEBUG:
                self.mgis.add_info(msg)
            print(msg)
            return

        if self.config_type == 'cadre':
            # parametre general
            list_recup = ['eptab', 'cottab', 'firstw']
            param_g = self.get_param_g(list_recup)
            param_g['cotpc'] = param_g['cottab'] - param_g['eptab']
            list_recup_elem = ['width']
        if self.config_type == 'arch':
            # parametre general
            list_recup = ['cottab', 'firstw']
            param_g = self.get_param_g(list_recup)
            list_recup_elem = ['width', 'cotmax', 'cotarc']


        where = "id_config = {0}".format(self.id_config) # type=0 span, =1 bridge peir
        order = "id_elem"
        lid_elem= self.mdb.select('struct_elem', where=where,order=order, list_var=['id_elem',"type"])
        first=True
        width=0
        width_prec = 0
        for i,id_elem in enumerate(lid_elem["id_elem"]):
            # TODO à checker si tou est bon
            # parametre element
            param_elem = self.get_param_elem(id_elem, list_recup_elem)
            if first:
                width = param_g['firstw']
                first =False
            else:
                width += width_prec

            width_prec= param_elem["width"]

            if lid_elem["type"][id_elem] != 1:
                # # pont Cadre
                if self.config_type=='cadre':
                    #polygon
                    poly_elem=self.poly_pont_cadre(param_g, param_elem, zmin, x0=width)
                    # if not poly_elem.is_empty:
                    #     self.draw_test(poly_elem,decal_ax=10)
                # pont arc
                if self.config_type == 'arch':
                    #polygon
                    poly_elem = self.poly_arch(param_g, param_elem, zmin,type='ellipse', x0=width)

                #final
                if not poly_elem.is_empty :
                    poly_final = poly_elem.difference(poly_p)
                else:
                    msg = 'Element bridge polygon is empty.'
                    if self.mgis.DEBUG:
                        self.mgis.add_info(msg)
                    print(msg)

                if not poly_final.is_empty:

                    self.draw_test(poly_final, decal_ax=10,xmin=profil['x'][0],xmax=profil['x'][-1])
                    # # stock element
                    where="WHERE id_config = {0}  AND id_elem = {1} ".format(self.id_config,id_elem)
                    sql = """UPDATE {0}.struct_elem SET polygon ='{1}'  {2}""".format(self.mdb.SCHEMA,
                                                                                    poly_final,
                                                                                    where)
                    self.mdb.run_query(sql)

        # return poly_final

    def select_poly(self, table,where='', var='polygon'):
        """ select polygon
        example:
                where = "id_config = {0} AND id_elem = {1}".format(self.id_config, id_elem)
                toto=self.select_poly('struct_elem',where)
                print(toto)
        """

        poly_l = self.mdb.select(table, where=where, list_var=[var])
        list_poly=[]
        for poly in poly_l[var]:
            list_poly.append(wkb.loads(poly.decode('hex')))
        poly_l[var]= list_poly
        return  poly_l

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

    def draw_test(self,poly, title=None,decal_ax=1,xmin=None,xmax=None):

        ax = self.figure.add_subplot(111)
        # ax.grid(True)
        new_poly = [ coord for coord in poly.exterior.coords]

        (minx, miny, maxx, maxy) = poly.bounds
        if xmin is not None:
            minx=xmin
        if xmax is not None:
            maxx=xmax

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