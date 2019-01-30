import math as m
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from shapely.geometry import *


class ClassBradley:

    def __init__(self, parent):
        self.parent=parent
        self.mgis=self.parent.mgis
        self.mdb = self.parent.mdb
        self.grav=9.81
        self.DEBUG=True
        self.epsi=0.0001

    def poly_profil(self, profil):
        """ creation profile polygone """

        zmax = max(profil['z'])
        zmax = zmax +self.epsi
        x0_p= profil['x'][0]
        z0_p= profil['z'][0]
        liste_poly=[[x0_p,zmax],[x0_p,z0_p]]
        for x,z in list(zip(profil['x'],profil['z'])):
            liste_poly.append([x,z])

        liste_poly.append([profil['x'][-1], zmax])
        liste_poly.append([x0_p,zmax])
        poly_p = Polygon(liste_poly)
        return poly_p

    def coup_poly_h(self, poly, cote):
        msg=None
        (minx, miny, maxx, maxy) = poly.bounds
        delpoly=Polygon([[minx - 1, cote], [maxx + 1, cote],
                         [maxx + 1, maxy + 1], [minx - 1, maxy + 1],
                         [minx - 1, cote]])
        if not delpoly.is_empty:
            polyw=poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg="Error: Wet polygon creation"
        else:
            polyw =GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"


        if self.mgis.DEBUG and msg is not None:
            print(msg)
        return polyw

    def coup_poly_v(self, poly, xo,typ='G'):
        msg = None
        (minx, miny, maxx, maxy) = poly.bounds
        if typ=='G':
            delpoly = Polygon([[minx - 1, maxy+1], [xo, maxy+1],
                               [xo, maxy + 1], [minx - 1, maxy + 1],
                               [minx - 1, maxy+1]])
        elif typ == 'D':
            delpoly = Polygon([[xo, maxy+1], [maxx+1, maxy+1],
                               [maxx+1, maxy + 1], [xo, maxy + 1],
                               [xo, maxy+1]])
        elif typ == 'GD':
            delpoly = Polygon([[minx - 1, maxy + 1], [xo[0], maxy + 1],
                               [xo[0], maxy + 1], [minx - 1, maxy + 1],
                               [minx - 1, maxy + 1]])

            delpolyD = Polygon([[xo[1], maxy+1], [maxx+1, maxy+1],
                               [maxx+1, maxy + 1], [xo[1], maxy + 1],
                               [xo[1], maxy+1]])

        if not delpoly.is_empty:
            polyw = poly.difference(delpoly)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"
        else:
            polyw = GeometryCollection()
            msg = "Error: delpoly creation in calc_polyw()"

        if typ == 'GD' not polyw.is_empty:
            polyw = polyw.difference(delpolyD)
            if not polyw.is_valid:
                polyw = GeometryCollection()
                msg = "Error: Wet polygon creation"

        if self.mgis.DEBUG and msg is not None:
            print(msg)
        return polyw

    def main(self):
        pas_h = 0.1
        pas_Q = 10
        bornQ=[10,1000]

        # if  self.parent.checkprofil(self.parent.id_config):
        #     profil = self.parent.get_profil(self.parent.id_config)
        # else:
        #     msg = "Profile copy isn't found"
        #     self.mgis.add_info(msg)
        #     print(msg)
        #     return
        # self.parent.get_param_g(self, list_recup)

        # for test ***************************
        profil = {'x': [0.00,
                        0.01,
                        100.00,
                        100.10,
                        150.00,
                        150.01,
                        ],
                  'z': [25,
                        6.5,
                        6.5,
                        14,
                        14,
                        25,
                        ]}
        list_poly_pil=[Polygon([[44,6.5],[44,18.45],[44.20,18.45],[44.20,6.5],[44,6.5]])]

        self.param_pil={}
        self.param_g = {}
        self.param_pil['LARG'] = 0.2
        self.param_pil['LONG'] = 11
        self.param_g['BIAIOUV'] = 5

        self.param_g['NBTRAV'] = 4
        self.param_g['firstw'] =4
        self.param_g['TOTALW'] = 140.60
        list_hn=[8.85]
        list_q= [100]
    #*****************************************
        poly_p=self.poly_profil(profil)
        (minx, miny, maxx, maxy) = poly_p.bounds
        # list_hn = list(np.arange(miny, maxy, pas_h))
        # list_q = list(np.arange(bornQ[0],bornQ[1], pas_Q))

        self.param_g['BIAIOUV']= self.param_g['BIAIOUV']/180.*m.pi # rad
        self.param_g['NBPIL']=self.param_g['NBTRAV']-1

        # Test
        for hn in list_hn:
            for q in list_q:
                area_pil=0
                for  poly_pil in list_poly_pil:
                    poly_pil= self.coup_poly_h(poly_pil, hn)
                    area_pil +=poly_pil.area
                print(area_pil)
                if self.param_g['BIAIOUV'] != 0:
                    area_pil_proj = area_pil*\
                                    (self.param_pil['LONG'] * m.sin(self.param_g['BIAIOUV']) +
                                     self.param_pil['LARG'] * m.cos(self.param_g['BIAIOUV'])) \
                                    / self.param_pil['LARG']
                    print(" area_pil_proj", area_pil_proj)

                q2=self.coup_poly_v(poly_p,)
                q1 = self.coup_poly_v(poly_p, )
                q3= self.coup_poly_v(poly_p, )