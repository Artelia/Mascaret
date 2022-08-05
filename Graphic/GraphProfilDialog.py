# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
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

Comment:
    class :
        IdentifyFeatureTool
        GraphCommon
        GraphProfil
        CopySelectedCellsAction
"""

import os
import matplotlib.image as mpimg
import numpy as np
from matplotlib import patches
from matplotlib.widgets import RectangleSelector, SpanSelector, Cursor
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *

from .GraphCommon import GraphCommon, DraggableLegend
from ..Structure.StructureCreateDialog import ClassStructureCreateDialog
from ..Structure.ClassPolygone import ClassPolygone
from .GraphProfilResultDialog import GraphProfilResultDialog
from .GraphResultDialog import GraphResultDialog
from .ClassProfInterpDialog import ClassProfInterpDialog
from ..Function import tw_to_txt
from .GraphBCDialog import GraphBCDialog

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

# **************************************************
try:
    _encoding = QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


class IdentifyFeatureTool(QgsMapToolIdentify):
    def __init__(self, main):
        self.mgis = main
        self.canvas = self.mgis.iface.mapCanvas()
        self.graphP = False
        self.gid = None
        QgsMapToolIdentify.__init__(self, self.canvas)

    def canvasReleaseEvent(self, mouse_event):

        results = self.identify(mouse_event.x(), mouse_event.y(),
                                self.TopDownStopAtFirst, self.VectorLayer)

        if len(results) > 0:
            couche = results[0].mLayer.name()

            flag_hydro = self.mgis.hydrogramme
            flag_profil = self.mgis.profil
            flag_profil_r = self.mgis.profil_result
            flag_casier_r = self.mgis.basin_result
            flag_profil_z = self.mgis.profil_z

            if (couche == 'profiles' or couche == 'weirs') and flag_profil_z:
                if couche == 'profiles':
                    type_res = 'struct'
                elif couche == 'weirs':
                    type_res = 'weirs'

                self.mgis.coucheProfils = results[0].mLayer
                gid = results[0].mFeature["abscissa"]
                sql = "SELECT DISTINCT pknum FROM {0}.results WHERE var IN " \
                      "(SELECT id FROM {0}.results_var WHERE type_res ='{1}' )".format(
                    self.mgis.mdb.SCHEMA, type_res)

                rows = self.mgis.mdb.run_query(sql, fetch=True)
                graph_res = GraphResultDialog(self.mgis, type_res, gid)
                graph_res.show()
                # else:
                #     #pass
                #     print ("Erreur")
                #     #a = QMessageBox.Warning(self, 'Error', 'Aucun résultat pour ce profil')

            if couche == 'profiles' and flag_profil:
                self.mgis.coucheProfils = results[0].mLayer
                gid = results[0].mFeature["gid"]
                graph_p = GraphProfil(gid, self.mgis)
                graph_p.show()
            # else:
            #     if self.mgis.DEBUG:
            #         self.mgis.add_info("Visu_profil: Not layer")
            if couche == 'profiles' and flag_profil_r:
                self.mgis.coucheProfils = results[0].mLayer
                prof_a = self.mgis.mdb.select_distinct("name", "profiles",
                                                       "active")
                if results[0].mFeature['name'] in prof_a['name']:
                    graph_res = GraphProfilResultDialog(self.mgis,
                                                        "hydro_profil",
                                                        results[0].mFeature[
                                                            "abscissa"])

                    graph_res.show()
                else:
                    self.mgis.add_info('no active profiles')
            # #
            if flag_hydro and couche in ('profiles', 'outputs'):
                feature = results[0].mFeature

                prof_a = self.mgis.mdb.select_distinct("name,abscissa",
                                                       "profiles", "active")
                if feature['name'] in prof_a['name'] or feature['abscissa'] in \
                        prof_a['abscissa']:
                    graph_hyd = GraphResultDialog(self.mgis, "hydro",
                                                  feature['abscissa'])
                    graph_hyd.show()
                else:
                    self.mgis.add_info('no active profiles')

            if flag_hydro and couche == 'branchs':
                feature = results[0].mFeature
                # chaine='Branche ' + str(feature['branche'])
                branches = self.mgis.mdb.select_distinct("branch", "branchs",
                                                         "active")
                if feature['branch'] in branches['branch']:
                    graph_hyd_pk = GraphResultDialog(self.mgis, "hydro_pk",
                                                     feature['branch'])
                    graph_hyd_pk.show()
                else:
                    self.mgis.add_info('no active branch')

            if flag_hydro and couche in ('weirs', 'extremities',
                                         'lateral_inflows', 'lateral_weirs'):
                feature = results[0].mFeature
                param = {'name': None,
                         'couche': couche,
                         'method': None,
                         'type': None,
                         'active': None,
                         'firstvalue': None}
                cond = True
                if 'extremities' == couche:
                    for var in ['name', 'method', 'active', 'firstvalue',
                                'type']:
                        id = feature.fieldNameIndex(var)
                        param[var] = feature.attributes()[id]

                    if param['type'] in [10]:
                        cond = False

                elif 'weirs' == couche:
                    weirs_tolaw = {1: 6, 2: 4, 5: 2, 6: 5, 7: 5, 8: 7}
                    id = feature.fieldNameIndex('type')
                    type = feature.attributes()[id]
                    if type not in (3, 4):
                        param['type'] = weirs_tolaw[type]
                        for var in ['name', 'method', 'active']:
                            id = feature.fieldNameIndex(var)
                            param[var] = feature.attributes()[id]
                    else:
                        cond = False
                elif 'lateral_inflows' == couche:
                    for var in ['name', 'method', 'firstvalue', 'active']:
                        id = feature.fieldNameIndex(var)
                        param[var] = feature.attributes()[id]
                    param['type'] = 1
                elif 'lateral_weirs' == couche:
                    id = feature.fieldNameIndex('type')
                    if feature.attributes()[id] == 2:
                        for var in ['name', 'active']:
                            id = feature.fieldNameIndex(var)
                            param[var] = feature.attributes()[id]
                        param['type'] = 4
                    else:
                        cond = False

                if cond and param['name']:
                    graph_law = GraphBCDialog(self.mgis, param)
                    # graph_law.show()
                    graph_law.exec_()
            if flag_casier_r and couche in ('basins', 'links'):
                feature = results[0].mFeature

                if couche == 'links':
                    links = self.mgis.mdb.select_distinct("name", "links",
                                                          "active")
                    if links is not None:
                        if feature['name'] in links['name']:
                            graph_link = GraphResultDialog(self.mgis,
                                                           "hydro_link",
                                                           feature["linknum"])
                            graph_link.show()
                else:

                    basins = self.mgis.mdb.select_distinct("name", "basins",
                                                           "active")
                    if basins is not None:
                        if feature['name'] in basins['name']:
                            graph_basin = GraphResultDialog(self.mgis,
                                                            "hydro_basin",
                                                            feature["basinnum"])
                            graph_basin.show()

        return


class GraphProfil(GraphCommon):
    """class Dialog graphProfil"""

    def __init__(self, gid, mgis=None):
        GraphCommon.__init__(self, mgis)

        self.ui = loadUi(
            os.path.join(self.mgis.masplugPath, 'ui/graphProfil.ui'), self)
        self.init_ui_prof(gid)
        self.gui_graph(self.ui.widget_figure)
        self.fig.autofmt_xdate()
        self.init_ui()

        # action
        self.bt_translah.clicked.connect(self.deplace_h_toggled)
        self.bt_translav.clicked.connect(self.deplace_v_toggled)
        self.bt_reverse_prof.clicked.connect(self.reverse_prof)
        self.bt_select.clicked.connect(self.selector_toggled)
        self.bt_select_z.clicked.connect(self.zone_selector_toggled)

        self.ui.bt_add_point.clicked.connect(self.ajout_points)
        self.ui.bt_topo_load.clicked.connect(self.import_topo)
        self.ui.bt_topo_del.clicked.connect(self.del_topo)
        # self.ui.bt_img_load.clicked.connect(self.import_image)
        self.ui.bt_topo_save.clicked.connect(self.sauve_topo)
        self.ui.bt_amont_aval.clicked.connect(self.topo_amont_aval)
        self.ui.bt_del_amont_aval.clicked.connect(self.del_amont_aval)
        self.ui.bt_check_prof.clicked.connect(self.check_prof_diag)

        self.ui.bt_reculTot.clicked.connect(lambda: self.avance(-10))
        self.ui.bt_recul.clicked.connect(lambda: self.avance(-1))
        self.ui.bt_av.clicked.connect(lambda: self.avance(1))
        self.ui.bt_avTot.clicked.connect(lambda: self.avance(10))
        self.ui.bt_profil_save.clicked.connect(self.sauve_profil)
        self.ui.bt_profil_filter.clicked.connect(self.filtre)
        self.ui.bt_profil_del.clicked.connect(self.efface_profil)
        self.ui.bt_minor_bed.clicked.connect(self.select_lit_mineur)
        self.ui.bt_r_stok.clicked.connect(
            lambda: self.select_stock("rightstock"))
        self.ui.bt_l_stok.clicked.connect(
            lambda: self.select_stock("leftstock"))
        self.ui.bt_ouvrage.clicked.connect(self.create_struct)
        self.ui.bt_interp.clicked.connect(self.bt_interpol_profile)

        self.ui.bt_add_line.clicked.connect(self.add_line)
        self.ui.bt_del_line.clicked.connect(self.del_line)

        self.ui.tab_aff.hide()

    def init_ui(self):

        # variables
        self.tab = {'x': [], 'z': []}
        self.selected = {}
        self.mnt = {'x': [], 'z': []}
        self.x0 = None
        self.y0 = None
        self.flag = False
        self.down_vis = False
        self.up_vis = False
        self.image = None
        self.topoSelect = None
        self.order_topo = 0
        self.bt_translah = self.ui.BtTools_profil_translationH
        self.bt_translav = self.ui.BtTools_profil_translationV
        self.bt_select = self.ui.btTools_point_selection
        self.bt_select_z = self.ui.btTools_zone_selection
        self.ui.bt_add_point.setDisabled(True)
        # self.ui.bt_topo_save.hide()
        # self.ui.bt_topo_save.setDisabled(True)
        # ***********************************************
        #  bouton retiré par rapport au plugin originale
        # (non fonctionnel )
        # ***********************************************
        self.ui.bt_img_load.hide()
        self.ui.bt_img_load.setDisabled(True)
        # **********************************************
        # tableau
        self.tableau = self.ui.tableWidget
        self.tableau.itemChanged.connect(self.modifie)
        self.tableau.selectionModel().selectionChanged.connect(
            self.select_changed)
        self.tableau.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.tableau.addAction(CopySelectedCellsAction(self.tableau))

        # figure

        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        # courbe
        self.courbeProfil, = self.axes.plot([], [], zorder=100, label='Profile')

        self.courbeMNT, = self.axes.plot([], [], color='grey', marker='o',
                                         markeredgewidth=0, zorder=90,
                                         label='MNT')
        self.courbeTopo = []
        for i in range(12):
            temp, = self.axes.plot([], [], color='green', marker='+', mew=2,
                                   zorder=95, label='Topo', picker=5)
            self.courbeTopo.append(temp)

        self.courbedown,  = self.axes.plot([], [], color="purple", marker='+', mew=2,
                               zorder=95, label='downstream', picker=5)
        self.courbeup, = self.axes.plot([], [], color="brown", marker='+', mew=2,
                                          zorder=95, label='upstream', picker=5)

        self.etiquetteTopo = []
        self.courbes = [self.courbeProfil, self.courbeMNT]

        # Selelection Zones
        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='pink',
                                 alpha=0.5, lw=1, zorder=80)
        self.litMineur = self.axes.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                 alpha=0.3, lw=1, zorder=80)
        self.stockgauche = self.axes.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                 alpha=0.3, lw=1, zorder=80)
        self.stockdroit = self.axes.add_patch(rect)

        rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='yellow',
                                 alpha=0.5, lw=1, zorder=80)
        self.rectSelection = self.axes.add_patch(rect)
        self.rectSelection.set_visible(False)

        self.courbeSelection, = self.axes.plot([], [], marker='o', linewidth=0,
                                               color='yellow', zorder=110)

        self.RS = RectangleSelector(self.axes, self.onselect, drawtype='box')
        self.RS.set_active(False)
        self.span = SpanSelector(self.axes, self.onselect_zone, 'horizontal',
                                 rectprops=dict(alpha=0, facecolor='yellow'),
                                 onmove_callback=self.onselect_zone,
                                 useblit=False)

        self.span.visible = False

        self.curseur = Cursor(self.axes, useblit=True, color="red")
        self.curseur.visible = False

        # figure suite
        # self.extrait_mnt()
        # self.fichierDecalage()
        self.extrait_profil()
        self.extrait_topo()
        self.maj_graph()
        self.maj_legende()
        self.maj_limites()
        self.fig.tight_layout()
        self.fig.patch.set_facecolor((0.94, 0.94, 0.94))
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onpress)
        # zoom_fun = zoom mollette
        self.fig.canvas.mpl_connect('scroll_event', self.zoom_fun)

    def selector_toggled(self):
        """Point selection function"""
        if self.bt_select.isChecked():
            self.RS.set_active(True)
            self.RS.update()
            self.span.visible = False
            self.rectSelection.set_visible(False)
            self.ui.bt_add_point.setEnabled(True)
            self.bt_select_z.setChecked(False)
            self.bt_translah.setChecked(False)
            self.bt_translav.setChecked(False)

        else:
            self.ui.bt_add_point.setDisabled(True)
            self.RS.set_active(False)
            self.RS.update()
            self.courbeSelection.set_visible(False)



    def zone_selector_toggled(self):
        """zone selection function"""
        if self.bt_select_z.isChecked():
            self.span.visible = True
            self.span.active = True
            self.bt_select.setChecked(False)
            self.RS.set_active(False)
            self.RS.update()
            self.courbeSelection.set_visible(False)
            self.bt_translah.setChecked(False)
            self.bt_translav.setChecked(False)
        else:
            self.span.active = False
            self.rectSelection.set_visible(False)


    def deplace_h_toggled(self):
        """Translation function"""
        if self.bt_translah.isChecked():
            self.bt_select.setChecked(False)
            self.bt_select_z.setChecked(False)
            self.bt_translav.setChecked(False)

    def deplace_v_toggled(self):
        """Translation function"""
        if self.bt_translav.isChecked():
            self.bt_select.setChecked(False)
            self.bt_select_z.setChecked(False)
            self.bt_translah.setChecked(False)

    def create_struct(self):
        """ creation of hydraulic structure"""
        dlg = ClassStructureCreateDialog(self.mgis, self.gid)
        if dlg.exec_():
            pass

    def avance(self, val):
        """next or back profiles """
        if self.image:
            self.image.set_visible(False)
        self.rectSelection.set_visible(False)
        self.selected = {}
        self.courbeSelection.set_data([], [])
        self.down_vis = False
        self.up_vis = False
        pos = self.position
        pos += val

        if pos >= len(self.liste["gid"]):
            pos = len(self.liste["gid"]) - 1
        elif pos < 0:
            pos = 0
        else:
            pass
        self.position = pos
        self.feature = {k: v[pos] for k, v in self.liste.items()}
        self.nom = self.feature['name']
        self.gid = self.feature['gid']

        self.extrait_profil()
        self.extrait_topo()
        self.maj_tab_check()
        self.maj_graph(allvis=True)
        self.maj_limites()
        self.maj_legende()

    def extrait_mnt(self):
        self.mnt = {'x': [], 'z': []}

        condition = "idprofil={0}".format(self.gid)
        requete = self.mdb.select("mnt", condition)
        if "x" in requete.keys() and "z" in requete.keys():
            self.mnt['x'] = [self.fct1(var, arrondi=3) for var in requete["x"][0].split()]
            self.mnt['z'] = [self.fct1(var, arrondi=3) for var in requete["z"][0].split()]

    def extrait_profil(self):

        self.tab = {'x': [], 'z': []}
        # liste = ["litmingauc", "litmindroi", "stockgauch", 'stockdroit']
        liste = ["leftminbed", "rightminbed", "leftstock", 'rightstock']
        for l in liste:
            if self.feature[l] is not None:
                self.tab[l] = self.feature[l]
            else:
                self.tab[l] = None
        self.mnt = {'x': [], 'z': []}

        if self.feature["x"] and self.feature["z"]:
            self.tab['x'] = [float(var) for var in self.feature["x"].split()]
            self.tab['z'] = [float(var) for var in self.feature["z"].split()]

            mini = min(self.tab['x'])
            maxi = max(self.tab['x'])
            for l in liste:
                val = self.feature[l]
                if val and mini < val < maxi:
                    self.tab[l] = val

        if self.feature["xmnt"] and self.feature["zmnt"]:
            self.mnt['x'] = [float(var) for var in self.feature["xmnt"].split()]
            self.mnt['z'] = [float(var) for var in self.feature["zmnt"].split()]

    def extrait_topo(self):

        self.topo = {}

        condition = "profile='{0}'".format(self.nom)
        ordre = "name, order_,x,gid"
        requete = self.mdb.select("topo", condition, ordre)
        if not requete:
            return
        table = zip(requete['gid'],
                    requete['name'],
                    requete['x'],
                    requete['z'],
                    requete['order_'])

        for i, (gid, nom, x, z, ordre) in enumerate(table):
            nom = nom.strip()
            if nom not in self.topo.keys():
                self.topo[nom] = {'x': [], 'z': [], 'ordre': [], 'gid': []}
            if not ordre:
                ordre = i + 1000
            self.topo[nom]['x'].append(x)
            self.topo[nom]['z'].append(round(z, 2))
            self.topo[nom]['gid'].append(gid)
            self.topo[nom]['ordre'].append(ordre)
        for nom in self.topo.keys():
            self.topo[nom]['x'] = self.mdb.projection(self.nom,
                                                      self.topo[nom]['x'],
                                                      self.topo[nom]['gid'])

    def remplir_tab(self, liste):
        """ Fill items in the table"""
        # self.tableau.rempit(Liste)
        self.tableau.itemChanged.disconnect()
        self.tableau.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.tableau.setItem(i, j, QTableWidgetItem(str(v)))
        self.tableau.itemChanged.connect(self.modifie)

    def colorie_tab(self, liste, dict_couleur):
        self.tableau.itemChanged.disconnect()
        for i, type in enumerate(liste):
            for j in range(self.tableau.columnCount()):
                if type in dict_couleur.keys():
                    self.tableau.item(i, j).setBackground(dict_couleur[type])
                else:
                    self.tableau.item(i, j).setBackground(Qt.white)
        self.tableau.itemChanged.connect(self.modifie)

    def selection_tab(self):
        mini_x = 99999999
        maxi_x = -99999999
        for index in self.tableau.selectionModel().selectedIndexes():
            if index.column() == 0:
                temp = float(index.data())
                mini_x = min(mini_x, temp)
                maxi_x = max(maxi_x, temp)
        return mini_x, maxi_x

    def modifie(self, item):
        i = item.row()
        j = item.column()
        if j == 0:
            self.tab['x'][i] = float(item.text())
        else:
            self.tab['z'][i] = float(item.text())

        self.courbeProfil.set_xdata(self.tab['x'])
        self.courbeProfil.set_ydata(self.tab['z'])
        self.canvas.draw()

    def sauve_profil(self):
        if not self.tab['x']:
            self.mgis.add_info('No data to save profile')
            return
        self.tab['zrightminbed'] = None
        self.tab['zleftminbed'] = None

        for k, v in self.tab.items():

            if isinstance(v, list):
                self.liste[k][self.position] = " ".join([str(var) for var in v])
            else:
                if k == 'rightminbed' and not v:
                    v = max(self.tab['x'])
                    self.tab['rightminbed'] = v
                    self.tab['zrightminbed'] = self.tab['z'][-1]

                if k == 'leftminbed' and not v:
                    v = min(self.tab['x'])
                    self.tab['leftminbed'] = v
                    self.tab['zleftminbed'] = self.tab['z'][0]

                self.liste[k][self.position] = v

        if not self.tab['zrightminbed'] or not self.tab['zleftminbed']:
            lstz_minor = []
            for x, z in zip(self.tab['x'], self.tab['z']):
                if self.tab['leftminbed'] <= x \
                        and x <= self.tab['rightminbed']:
                    lstz_minor.append(z)

            if not self.tab['zrightminbed']:
                self.tab['zrightminbed'] = lstz_minor[-1]
                self.liste['zrightminbed'][self.position] = lstz_minor[-1]

            if not self.tab['zleftminbed']:
                self.tab['zleftminbed'] = lstz_minor[0]
                self.liste['zleftminbed'][self.position] = lstz_minor[0]

        self.feature = {k: v[self.position] for k, v in self.liste.items()}
        tab = {self.nom: self.tab}
        self.mdb.update("profiles", tab, var="name")

    def sauve_topo(self):
        """ Save les modification du à la translation de la topo"""
        for nom, t in self.topo.items():
            for x, z, gid, ordre in zip(t['x'], t['z'], t['gid'], t['ordre']):
                for f in self.coucheProfils.getFeatures():
                    if f["name"] == self.nom:
                        if x < 0:
                            geom = 'NULL'
                        else:
                            interp = f.geometry().interpolate(x)
                            if interp.isNull():
                                geom = 'NULL'
                            else:
                                # if interp.isNull():
                                #     self.mgis.add_info(
                                #         "Warning : Check the profil lenght")

                                p = f.geometry().interpolate(x).asPoint()
                                geom = "ST_SetSRID(ST_MakePoint({0}, {1}),{2})".format(
                                    p.x(), p.y(), self.mdb.SRID)

                if gid:
                    sql = """UPDATE {0}.topo SET x={1}, geom={2}, order_={3}
                          WHERE gid={4}""".format(self.mdb.SCHEMA,
                                                  x,
                                                  geom,
                                                  ordre,
                                                  gid)
                    self.mdb.run_query(sql)
                else:
                    sql = """INSERT INTO {0}.topo
                          (name, profile, order_, x, z, geom)
                          VALUES
                          ('{1}','{2}',{3},{4},{5},{6})""".format(
                        self.mdb.SCHEMA,
                        nom,
                        self.nom,
                        ordre,
                        x,
                        z,
                        geom)

                    self.mdb.run_query(sql)

        self.extrait_topo()

    def efface_profil(self):

        self.tab = {"x": [], "z": [], "leftminbed": None,
                    "rightminbed": None, "leftstock": None,
                    "rightstock": None}

        self.mdb.update("profiles", {self.nom: self.tab}, var='name')

        self.maj_graph()

    def del_topo(self):
        """delete topo"""
        liste = self.topo.keys()
        name_topo, ok = QInputDialog.getItem(None,
                                             'Topo Choice',
                                             'Topo',
                                             liste)
        if ok:
            condition = "name='{0}' AND profile='{1}'".format(name_topo,
                                                              self.nom)
            self.mdb.delete("topo", condition)

        self.extrait_topo()
        self.maj_graph()
        self.maj_limites()
        self.maj_legende()

    def import_topo(self):

        fichiers, _ = QFileDialog.getOpenFileNames(None,
                                                   'File Selection',
                                                   self.dossierProjet,
                                                   "File (*.txt *.csv)")

        if fichiers:

            self.charger_bathy(fichiers, self.coucheProfils,
                               self.nom)

            self.extrait_topo()
            self.maj_graph()
            self.maj_limites()
            self.maj_legende()
        else:
            self.mgis.add_info('File "{}" cannot open.'.format(fichiers))

    def charger_bathy(self, liste, couche_profil, profil=None):
        """charge la bathymetrie"""
        for fichier in liste:
            basename = os.path.basename(fichier)
            if not profil:
                profil = basename.split(".")[0]
            for f in couche_profil.getFeatures():
                if f["name"] == profil:
                    condition = "name='{}' AND profile='{}'".format(basename,
                                                                    profil)

                    self.mdb.delete("topo", condition)

                    tab = {'name': [], 'profile': [], 'order_': [], 'x': [],
                           'z': [],
                           'geom': []}
                    with open(fichier, "r") as fich:
                        entete = fich.readline()
                        if len(entete.split()) > 1:
                            sep = None
                        else:
                            sep = ";"

                        ordre = 0
                        for ligne in fich:

                            if ligne[0] != '#':
                                ligne = ligne.replace('\n', '')
                                if len(ligne.split(sep)) < 1:
                                    break
                                x, z = (float(var) for var in ligne.split(sep))

                                ordre += 1
                                if x < 0:
                                    geom = 'NULL'
                                else:

                                    p = f.geometry().interpolate(x).asPoint()

                                    # geom = "ST_MakePoint({0}, {1})".format(p.x(), p.y())

                                    geom = "ST_SetSRID(ST_MakePoint({0}, {1}),{2})".format(
                                        p.x(), p.y(), self.mdb.SRID)

                                tab["name"].append("'" + basename + "'")
                                tab["profile"].append("'" + profil + "'")
                                tab["order_"].append(ordre)
                                tab["x"].append(x)
                                tab["z"].append(z)
                                tab["geom"].append(geom)

                    self.mdb.insert2("topo", tab)

    def import_image(self):
        fichier, _ = QFileDialog.getOpenFileName(None,
                                                 'Sélection des fichiers',
                                                 self.dossierProjet,
                                                 "Fichier (*.png *.jpg)")

        try:
            fich = open(fichier + "w", "r")
        except OSError:
            self.mgis.add_info('File "{}" cannot open.'.format(fichier + "w"))
        else:
            x0 = float(fich.readline())
            z0 = float(fich.readline())
            l = float(fich.readline())
            h = float(fich.readline())
            fich.close()
        try:
            img = mpimg.imread(fichier)
        except:
            self.mgis.add_info('File "{}" cannot open.'.format(fichier))
        else:
            self.image = self.axes.imshow(img,
                                          extent=[x0, x0 + l, z0 - h, z0],
                                          zorder=1,
                                          aspect='auto')
            # self.axes.imshow(fichier)
            self.canvas.draw()

    def close_event(self, event):
        # reply = QMessageBox.question(self, 'Message',
        # 'Voulez-vous enregistrer les modifications ?',
        # QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # if reply == QMessageBox.Yes:

        # self.mdb.update("profiles", self.tab,var='name')

        # conn = self.mdb.connect()
        # cur = conn.cursor()
        # for nom in self.topo.keys() :
        # for fichier, t in self.topo[nom].items() :
        # for ordre, x in enumerate(t['x']) :
        # for f in self.coucheProfils.getFeatures() :
        # if f["nom"] == nom :
        # P = f.geometry().interpolate(x).asPoint()
        # geom = "ST_MakePoint({0}, {1})".format(P.x(), P.y())

        # sql = """UPDATE {0}.topo SET x={1}, geom={2}
        # WHERE nom='{3}'
        # AND profil='{4}'
        # AND ordre={5}""".format(self.mdb.schema,
        # x,
        # geom,
        # fichier,
        # nom,
        # ordre+1)
        # cur.execute(sql)
        # conn.commit()
        # conn.close()
        # event.accept()
        # else:
        # event.accept()
        pass

    def onpick(self, event):
        legline = event.artist
        deplaceh = self.bt_translah.isChecked()
        deplacev = self.bt_translav.isChecked()
        selector = self.bt_select.isChecked()
        zone_selector = self.bt_select_z.isChecked()
        bouton = event.mouseevent.button

        if (deplaceh and legline in self.courbeTopo and bouton == 1) or \
                (deplaceh and legline in [self.courbedown, self.courbeup] and bouton == 1):
            self.x0 = round(event.mouseevent.xdata, 2)
            self.courbeSelected = legline
        elif (deplacev and legline in self.courbeTopo and bouton == 1) or \
                (deplacev and legline in [self.courbedown, self.courbeup] and bouton == 1):
            self.y0 = round(event.mouseevent.ydata, 2)
            self.courbeSelected = legline
        elif self.flag and bouton == 1 and legline in self.courbeTopo:
            n = len(event.ind)
            if not n:
                return True
            # the click locations
            lbl = legline.get_label()
            x = round(event.mouseevent.xdata, 2)
            z = round(event.mouseevent.ydata, 2)
            xs = np.array(self.topo[lbl]['x'])
            zs = np.array(self.topo[lbl]['z'])

            distances = np.hypot(x - xs[event.ind], z - zs[event.ind])
            indmin = distances.argmin()
            dataind = event.ind[indmin]
            if self.ordre == -9999:
                ordre = self.topo[lbl]['ordre'][dataind]
                num, ok = QInputDialog.getInt(self,
                                              "Ordre",
                                              "Entrez l'ordre initial",
                                              ordre)
                if ok:
                    self.ordre = num
                else:
                    self.ordre = ordre

                self.topoSelect = lbl

            elif lbl == self.topoSelect:
                self.ordre += 1
            else:
                return

            self.topo[lbl]['ordre'][dataind] = self.ordre
            self.topo[lbl]['ordre'].sort()
            i = self.topo[lbl]['ordre'].index(self.ordre)

            for k in ['x', 'z', 'gid']:
                self.topo[lbl][k].insert(i, self.topo[lbl][k].pop(dataind))

            self.selected = {'x': [xs[dataind]], 'z': [zs[dataind]]}
            self.courbeSelection.set_data(self.selected['x'],
                                          self.selected['z'])
            self.courbeSelection.set_visible(True)

            self.maj_graph()

        elif not zone_selector and bouton == 1:
            if legline in self.lined.keys():
                courbe = self.lined[legline]
                # efface en cliquand sur la legende
                vis = not courbe.get_visible()
                courbe.set_visible(vis)
                if vis:
                    legline.set_alpha(1.0)
                else:
                    legline.set_alpha(0.2)
                self.canvas.draw()

    def onselect(self, eclick, erelease):
        mini_x = min(eclick.xdata, erelease.xdata)
        maxi_x = max(eclick.xdata, erelease.xdata)
        mini_y = min(eclick.ydata, erelease.ydata)
        maxi_y = max(eclick.ydata, erelease.ydata)
        self.selected = {'x': [], 'z': [], 'label': []}
        for courbe in self.courbes:
            if courbe.get_visible():
                xdata = courbe.get_xdata()
                ydata = courbe.get_ydata()
                label = courbe.get_label()
                for x, y in zip(xdata, ydata):
                    if mini_x < x < maxi_x and mini_y < y < maxi_y:
                        self.selected['x'].append(x)
                        self.selected['z'].append(y)
                        self.selected['label'].append(label)

        self.courbeSelection.set_data(self.selected['x'], self.selected['z'])
        self.courbeSelection.set_visible(True)

        self.fig.canvas.draw()

    def onselect_zone(self, xmin, xmax):
        """selectionne zone"""
        n = len(self.tab['x'])
        if n > 0:

            mini = min(self.tab['x'], key=lambda x: abs(x - xmin))
            i_min = self.tab['x'].index(mini)

            maxi = min(self.tab['x'], key=lambda x: abs(x - xmax))
            i_max = self.tab['x'].index(maxi)
            range = QTableWidgetSelectionRange(i_min, 0, i_max, 1)
            self.tableau.clearSelection()
            self.tableau.setRangeSelected(range, True)
            self.tableau.scrollToItem(self.tableau.item(i_min, 0))

            self.rectSelection.set_x(mini)
            self.rectSelection.set_width(maxi - mini)
            self.rectSelection.set_visible(True)
            self.canvas.draw()
        else:
            if self.mgis.DEBUG:
                self.mgis.add_info(
                    "The table has {0} elements, please add ".format(n))

    def onrelease(self, event):
        if self.bt_translah.isChecked():
            self.x0 = None
        elif self.bt_translav.isChecked():
            self.y0 = None

        return

    def onclick(self, event):

        if self.flag and event.button == 3:
            if self.ordre == -9999:
                if self.topoSelect in self.topo.keys():
                    idx_topo = list(self.topo.keys()).index(self.topoSelect)
                else:
                    idx_topo = 0
                item, ok = QInputDialog.getItem(self,
                                                "Curve",
                                                "Choice of Curve",
                                                self.topo.keys(),
                                                idx_topo)

                if not ok:
                    return

                num, ok = QInputDialog.getInt(self,
                                              "Order",
                                              "Input the initial order",
                                              self.order_topo)
                if not ok:
                    return
                self.order_topo = num + 1
                self.ordre = num

                self.topoSelect = item
                self.ordre = num
                if self.topoSelect not in self.topo.keys():
                    self.topo[self.topoSelect] = {'x': [],
                                                  'z': [],
                                                  'ordre': [],
                                                  'gid': []}

                self.topo[self.topoSelect]['ordre'].append(self.ordre)
                self.topo[self.topoSelect]['ordre'].sort()
                i = self.topo[self.topoSelect]['ordre'].index(self.ordre)
                self.ordre = -9999

            else:
                self.ordre += 1

                self.topo[self.topoSelect]['ordre'].append(self.ordre)
                self.topo[self.topoSelect]['ordre'].sort()
                i = self.topo[self.topoSelect]['ordre'].index(self.ordre)

            self.topo[self.topoSelect]['x'].insert(i, round(event.xdata, 2))
            self.topo[self.topoSelect]['z'].insert(i, round(event.ydata, 2))
            self.topo[self.topoSelect]['gid'].insert(i, None)
            self.maj_graph()

    @staticmethod
    def fct2(x, xdata, x0):
        """ function"""
        return x + round(float(xdata), 2) - x0

    def onpress(self, event):
        """ event """
        if self.bt_translah.isChecked() and self.x0:
            f = self.courbeSelected.get_label()
            try:
                #tab_x = self.topo[f]['x']
                tab_x = self.courbeSelected.get_xdata()
                tempo = []
                # fct2 = lambda x: x + round(float(event.xdata), 2) - self.x0
                for var1 in tab_x:
                    tempo.append(self.fct2(var1, event.xdata, self.x0))
                tab_x = tempo
                if self.courbeSelected in self.courbeTopo :
                    self.topo[f]['x'] = tab_x
                self.courbeSelected.set_xdata(tab_x)
                self.x0 = round(float(event.xdata), 2)
            except:
                if self.mgis.DEBUG:
                    self.mgis.add_info("Warning:Out of graph")

        elif self.bt_translav.isChecked() and self.y0:
            f = self.courbeSelected.get_label()
            try:
                #tab_z = self.topo[f]['z']
                tab_z = self.courbeSelected.get_ydata()
                tempo = []
                for var1 in tab_z:
                    tempo.append(self.fct2(var1, event.ydata, self.y0))
                tab_z = tempo
                if self.courbeSelected in self.courbeTopo:
                    self.topo[f]['z'] = tab_z
                self.courbeSelected.set_ydata(tab_z)

                self.y0 = round(float(event.ydata), 2)
            except:
                if self.mgis.DEBUG:
                    self.mgis.add_info("Warning:Out of graph")
        self.fig.canvas.draw()

    def maj_graph(self, allvis=False):
        """Updating  graphic"""
        self.ui.label_Title.setText(_translate("ProfilGraph", self.nom, None))
        ta = self.tab
        self.courbeProfil.set_data(ta['x'], ta['z'])

        self.remplir_tab([ta['x'], ta['z']])

        self.courbeMNT.set_data(self.mnt['x'], self.mnt['z'])
        self.courbes = [self.courbeProfil, self.courbeMNT]

        if self.up_vis:
            self.courbes.append(self.courbeup)
        else:
            self.courbeup.set_data([], [])
        if self.down_vis:
            self.courbes.append(self.courbedown)
        else:
            self.courbedown.set_data([], [])

        for c in self.courbeTopo:
            c.set_data([], [])

        for i, (fichier, v) in enumerate(self.topo.items()):
            if i >= len(self.courbeTopo):
                break

            self.courbeTopo[i].set_data(v['x'], v['z'])
            self.courbeTopo[i].set_label(fichier)
            if fichier == 'downstream':
                self.courbeTopo[i].set_color("purple")
            elif fichier == 'upstream':
                self.courbeTopo[i].set_color("brown")
            elif fichier == 'interpolation':
                self.courbeTopo[i].set_color("orange")
            else:
                self.courbeTopo[i].set_color("green")
            self.courbes.append(self.courbeTopo[i])

        if allvis:
            for cb in self.courbes:
                cb.set_visible(True)
        if ta['x'] is not None and ta['leftminbed'] is not None and ta[
            'rightminbed'] is not None:
            self.litMineur.set_x(ta['leftminbed'])
            self.litMineur.set_width(ta['rightminbed'] - ta['leftminbed'])
            self.litMineur.set_visible(True)
        else:
            self.litMineur.set_visible(False)

        if ta['x'] and ta["leftstock"]:
            mini = min(ta['x'])
            self.stockgauche.set_x(mini)
            self.stockgauche.set_width(ta['leftstock'] - mini)
            self.stockgauche.set_visible(True)
        else:
            self.stockgauche.set_visible(False)

        if ta['x'] and ta["rightstock"]:
            self.stockdroit.set_x(ta['rightstock'])
            self.stockdroit.set_width(max(ta['x']) - ta['rightstock'])
            self.stockdroit.set_visible(True)
        else:
            self.stockdroit.set_visible(False)

        self.canvas.draw()

    def maj_limites(self):
        """Updating  limit"""
        mini_x = 99999999
        maxi_x = -99999999
        mini_z = 99999999
        maxi_z = -99999999

        for courbe in self.courbes:
            x, z = courbe.get_data()
            if courbe.get_visible() and x:
                mini_x = min(mini_x, min(x))
                maxi_x = max(maxi_x, max(x))
                mini_z = min(mini_z, min(z) - 1)
                maxi_z = max(maxi_z, max(z) + 1)

        if mini_x < 99999999:
            self.axes.set_xlim(mini_x, maxi_x)
            self.axes.set_ylim(mini_z, maxi_z)
            self.canvas.draw()

    def maj_legende(self):

        liste_noms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, liste_noms, loc='upper right',
                                    fancybox=False, shadow=False)
        self.leg.get_frame().set_alpha(0.4)
        self.leg.set_zorder(110)
        # self.leg.draggable(True)
        DraggableLegend(self.leg)
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(5)
            legline.set_linewidth(3)
            self.lined[legline] = courbe
        self.canvas.draw()

    @staticmethod
    def fct1(x, arrondi = 2):
        """around"""
        return round(float(x),  arrondi)

    def del_line(self):
        """
        delete line
        :return:
        """
        if self.tableau.selectedIndexes():
            rows = [idx.row() for idx in self.tableau.selectedIndexes() if
                    idx.row() > 0]
            rows = list(set(rows))
            rows.sort(reverse=True)

            ta = self.tab
            newta = {'x': [], 'z': []}
            for i, x in enumerate(ta["x"]):
                if i not in rows:
                    newta['x'].append(x)
                    newta['z'].append(ta["z"][i])

            ta['x'] = newta['x']
            ta['z'] = newta['z']

            self.maj_graph()

    def add_line(self):

        """
        add line
        :return:
        """
        if self.tableau.selectedIndexes():
            rows = [idx.row() for idx in self.tableau.selectedIndexes() if
                    idx.row() > 0]
            rows = list(set(rows))
            rows.sort(reverse=True)

            ta = self.tab
            newta = {'x': [], 'z': []}
            lenta = len(ta["x"])
            for i, x in enumerate(ta["x"]):
                newta['x'].append(x)
                newta['z'].append(ta["z"][i])
                if i in rows:
                    if i == lenta - 1:
                        newta['x'].append(x + 1)
                        newta['z'].append(ta["z"][i])
                    else:
                        newta['x'].append(self.fct1((ta["x"][i] + ta["x"][i + 1]) / 2.))
                        newta['z'].append(self.fct1((ta["z"][i] + ta["z"][i + 1]) / 2.))
            ta['x'] = newta['x']
            ta['z'] = newta['z']

            self.maj_graph()

    def ajout_points(self):
        """ add points"""
        if self.selected:
            self.courbeSelection.set_visible(False)

            tempo = []
            for var1 in self.selected['x']:
                tempo.append(self.fct1(var1))
            self.selected['x'] = tempo

            mini_x = min(self.selected['x'])
            maxi_x = max(self.selected['x'])

            ta = self.tab

            i_min = 0
            i_max = len(ta['x'])
            for i, x in enumerate(ta['x']):
                if x < mini_x:
                    i_min = max(i, i_min)

                if x > maxi_x:
                    i_max = min(i, i_max)

            ta['x'] = ta['x'][:i_min] + self.selected['x'] + ta['x'][i_max:]
            ta['z'] = ta['z'][:i_min] + self.selected['z'] + ta['z'][i_max:]
            self.selected = {}
            self.maj_graph()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Delete and self.selected:
            index = []

            liste = [self.tab[k] for k in ('x', 'z')]
            for i, (x, z) in enumerate(zip(*liste)):
                flag = True
                for x1, z1 in zip(self.selected['x'], self.selected['z']):
                    if x1 == x and z1 == z:
                        flag = False
                        break

                if flag:
                    index.append(i)

            self.tab['x'] = [liste[0][i] for i in index]
            self.tab['z'] = [liste[1][i] for i in index]
            self.selected = {}
            self.maj_graph()

        if event.key() == Qt.Key_O:
            self.flag = True
            self.ordre = -9999
            self.curseur.visible = True
            self.fig.canvas.draw()

        if event.key() == Qt.Key_S:
            self.flag = False
            self.courbeSelection.set_data([], [])
            self.courbeSelection.set_visible(False)
            self.curseur.visible = False
            self.fig.canvas.draw()

        if event.key() == Qt.Key_Escape:
            self.rectSelection.set_visible(False)
            self.courbeSelection.set_data([], [])
            self.courbeSelection.set_visible(False)
            self.fig.canvas.draw()

    def filtre(self):

        seuil, ok = QInputDialog.getDouble(self,
                                           "Filtrage",
                                           "Entrez le seuil",
                                           0.5)
        if not ok:
            return

        n = len(self.tab['z'])
        nb = 5
        seuil2 = 0.
        x = [self.tab['x'][0]]
        z = [self.tab['z'][0]]
        derniere_pente = 1

        for i in range(1, n - 1):
            mini = max(0, i - nb)
            maxi = min(i + nb + 1, n)
            xx = self.tab['x'][mini:maxi]
            zz = self.tab['z'][mini:maxi]

            pente, ord = np.polyfit(xx, zz, 1)
            zz.sort()
            if len(zz) <= nb :
                self.mgis.add_info("Warning: The filter works if there are a minimum of 5 points ")
                return
            mediane = zz[nb]

            if abs((pente - derniere_pente) / derniere_pente) > seuil:

                x.append(self.tab['x'][i])
                # z.append(self.tab['z'][i])
                if abs(self.tab['z'][i] - mediane) > seuil2:
                    z.append(self.tab['z'][i])
                else:
                    z.append(mediane)

                derniere_pente = pente

        x.append(self.tab['x'][-1])
        z.append(self.tab['z'][-1])

        flag = True
        self.tab['x'] = [x[0]]
        self.tab['z'] = [z[0]]
        m = len(z)
        for i in range(1, m):
            if z[i - 1] != z[i]:
                if flag:
                    self.tab['x'].append(x[i - 1])
                    self.tab['z'].append(z[i - 1])

                self.tab['x'].append(x[i])
                self.tab['z'].append(z[i])
                flag = False
            elif i == m - 1:
                self.tab['x'].append(x[i])
                self.tab['z'].append(z[i])
            else:
                flag = True

        self.maj_graph()

    def select_lit_mineur(self):
        self.rectSelection.set_visible(False)
        xmin = round(self.rectSelection.get_x(), 2)
        xmax = round(self.rectSelection.get_width() + xmin, 2)

        self.tab["leftminbed"] = xmin
        self.tab["rightminbed"] = xmax
        # self.liste[self.position] = (self.feature["abscisse"], self.feature)
        self.maj_graph()

    def select_stock(self, side):
        n = len(self.tab['x'])
        if n > 0:
            self.rectSelection.set_visible(False)
            xmin = round(self.rectSelection.get_x(), 2)
            xmax = round(self.rectSelection.get_width() + xmin, 2)

            if xmax < min(self.tab['x']):
                xmax = None

            if xmin > max(self.tab['x']):
                xmin = None

            if side == "leftstock":
                self.tab[side] = xmax
            else:
                self.tab[side] = xmin

            # self.liste[self.position] = (self.feature["abscisse"], self.feature)
            self.maj_graph()
        else:
            if self.mgis.DEBUG:
                self.mgis.add_info(
                    "The table has {0} elements, please add ".format(n))

    def select_changed(self):
        # mini_x, maxi_x = self.tableau.selection()
        mini_x, maxi_x = self.selection_tab()

        if mini_x != 99999999 and maxi_x != -99999999:
            self.rectSelection.set_x(mini_x)
            self.rectSelection.set_width(maxi_x - mini_x)
            self.rectSelection.set_visible(True)
            self.canvas.draw()

    def zoom_fun(self, event):
        # get the current x and y limits
        try:
            base_scale = 1.5
            cur_xlim = self.axes.get_xlim()
            cur_ylim = self.axes.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
            cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            # print(event.button)
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                # print event.button
            # set new limits
            self.axes.set_xlim([xdata - cur_xrange * scale_factor,
                                xdata + cur_xrange * scale_factor])
            self.axes.set_ylim([ydata - cur_yrange * scale_factor,
                                ydata + cur_yrange * scale_factor])
            self.fig.canvas.draw()  # force re-draw
        except:
            pass

    def reverse_prof(self):
        """
        Revers profil
        :return:
        """
        self.tab['z'].reverse()
        oldx = self.tab['x'].copy()

        lmin = self.tab['leftminbed']
        rmin = self.tab['rightminbed']
        lmaj = self.tab['leftstock']
        rmaj = self.tab['rightstock']
        xo = oldx[0]
        if lmin and rmin:
            self.tab['leftminbed'] = oldx[-1] - (lmin - xo)
            self.tab['rightminbed'] = oldx[-1] - (rmin - xo)
        if lmaj and rmaj:
            self.tab['leftstock'] = oldx[-1] - (lmaj - xo)
            self.tab['rightstock'] = oldx[-1] - (rmaj - xo)

        dist_x = []
        for i, x in enumerate(oldx):
            if i != 0:
                dist_x.append(round(x - xo, 6))
                xo = x
        dist_x.reverse()
        xf = oldx[0]
        new_x = [xf]
        for dist in dist_x:
            xf = round(xf + dist, 6)
            new_x.append(xf)
        self.tab['x'] = new_x

        self.maj_graph()

    def add_topo(self, xval, zval, basename):

        tab = {'name': [], 'profile': [], 'order_': [], 'x': [],
               'z': [],
               'geom': []}
        ordre = 0
        for f in self.coucheProfils.getFeatures():
            if f["name"] == self.nom:
                for x, z in zip(xval, zval):

                    ordre += 1
                    if x < 0:
                        geom = 'NULL'
                    else:

                        geo_tmp = f.geometry().interpolate(x)
                        if not geo_tmp.isNull:
                            p = geo_tmp.asPoint()
                            # geom = "ST_MakePoint({0}, {1})".format(p.x(), p.y())
                            geom = "ST_SetSRID(ST_MakePoint({0}, {1}),{2})".format(
                                p.x(), p.y(), self.mdb.SRID)
                        else:
                            geom = 'NULL'

                    tab["name"].append("'" + basename + "'")
                    tab["profile"].append("'" + self.nom + "'")
                    tab["order_"].append(ordre)
                    tab["x"].append(x)
                    tab["z"].append(z)
                    tab["geom"].append(geom)

        self.mdb.insert2("topo", tab)
    def del_amont_aval(self):
        """
        delet curve the down/upstream courbe
        :return:
        """
        self.up_vis = False
        self.down_vis = False
        self.maj_graph()
        self.maj_limites()
        self.maj_legende()
    def del_amont_aval_old(self):
        """
        delet in top tab the down/upstream courbe
        :return:
        """
        reply = QMessageBox.question(self, 'Message',
                                     'Do you want to delete the upstream / downstream topo profiles?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            condition = "name='{0}' AND profile='{1}'".format('upstream',
                                                              self.nom)
            self.mdb.delete("topo", condition)

            condition = "name='{0}' AND profile='{1}'".format('downstream',
                                                              self.nom)
            self.mdb.delete("topo", condition)

            self.extrait_topo()
            self.maj_graph()
            self.maj_limites()
            self.maj_legende()

    def topo_amont_aval(self):
        """
        add curve tab the down/upstream courbe
        :return:
        """
        id = self.liste['name'].index(self.nom)
        idam = id - 1
        idav = id + 1
        maj = False
        self.down_vis = False
        self.up_vis = False

        if 0 <= idam:
            if self.liste['branchnum'][id] == self.liste['branchnum'][idam]:
                if self.liste['x'][idam]:
                    xamont = [float(val) for val in
                              self.liste['x'][idam].split()]
                    zamont = [float(val) for val in
                              self.liste['z'][idam].split()]
                    self.courbeup.set_data(xamont, zamont)
                    self.up_vis = True
                    maj = True
        if idav < len(self.liste['branchnum']):
            if self.liste['branchnum'][id] == self.liste['branchnum'][idav]:
                if self.liste['x'][idav]:
                    xaval = [float(val) for val in
                             self.liste['x'][idav].split()]
                    zaval = [float(val) for val in
                             self.liste['z'][idav].split()]
                    self.courbedown.set_data(xaval , zaval)
                    self.down_vis = True
                    maj = True

        if maj:
            self.maj_graph()
            self.maj_limites()
            self.maj_legende()

    def topo_amont_aval_old(self):
        """
        add in top tab the down/upstream courbe
        :return:
        """

        id = self.liste['name'].index(self.nom)
        idam = id - 1
        idav = id + 1
        maj = False

        if 0 < idam:
            if self.liste['branchnum'][id] == self.liste['branchnum'][idam]:
                if self.liste['x'][idam]:
                    xamont = [float(val) for val in
                              self.liste['x'][idam].split()]
                    zamont = [float(val) for val in
                              self.liste['z'][idam].split()]
                    self.add_topo(xamont, zamont, 'upstream')
                    maj = True
        if idav < len(self.liste['branchnum']):
            if self.liste['branchnum'][id] == self.liste['branchnum'][idav]:
                if self.liste['x'][idav]:
                    xaval = [float(val) for val in
                             self.liste['x'][idav].split()]
                    zaval = [float(val) for val in
                             self.liste['z'][idav].split()]
                    self.add_topo(xaval, zaval, 'downstream')
                    maj = True
        if maj:
            self.extrait_topo()
            self.maj_graph()
            self.maj_limites()
            self.maj_legende()

    def val_prof(self, id):
        """
        Compute value:
            section minor bed
            overflow point
            bottom point
        :param id : index of profil
        :return:
        """
        clpoly = ClassPolygone()

        pr_m, rmin, lmin = self.get_minor_pr(id)

        lz = pr_m[0][1]
        rz = pr_m[-1][1]
        h_pbord = min(lz, rz)

        bool = np.all(pr_m == pr_m[0, :], axis=0)
        if bool[1]:
            # print('flat profil')
            return pr_m[0, 1], None, rz, lz, rmin, lmin
        poly = clpoly.poly2_profile(pr_m)
        if poly.is_empty:
            # print('Profil is empty')
            return np.min(pr_m[:, 1]), None, rz, lz, rmin, lmin
        poly = clpoly.coup_poly_h(poly, h_pbord, typ='U')

        if poly.is_empty:
            # print('Profil is empty')
            return np.min(pr_m[:, 1]), None, rz, lz
        _, minz, _, _ = poly.bounds
        return minz, poly.area, rz, lz, rmin, lmin

    def val_inter_prof(self, id):
        """
        Compute value interpolation topo:
            section minor bed
            overflow point
            bottom point
        :param id : index of profil if  -1 get topo interpolation
        :return:
        """
        clpoly = ClassPolygone()
        if id == -1:
            nom = 'interpolation'
            prof = np.zeros(shape=(len(self.topo[nom]['x']), 2))

            for i, order in enumerate(self.topo[nom]['ordre']):
                prof[order - 1, 0] = self.topo[nom]['x'][i]
                prof[order - 1, 1] = self.topo[nom]['z'][i]
        else:
            x_pr = [float(val) for val in self.liste['x'][id].split()]
            z_pr = [float(val) for val in self.liste['z'][id].split()]
            lin_s = []
            for x, z in zip(x_pr, z_pr):
                lin_s.append((x, z))
            prof = np.array(lin_s)

        bool = np.all(prof == prof[0, :], axis=0)
        if bool[1]:
            # print('flat profil')
            return prof[0, 1], None
        poly = clpoly.poly2_profile(prof)
        if poly.is_empty:
            # print('Profil is empty')
            return np.min(prof[:, 1]), None
        _, minz, _, _ = poly.bounds
        return minz, poly.area

    def check_prof(self):

        id = self.liste['name'].index(self.nom)
        self.ch_prof = {}
        # cas = -1 amont, cas=1 aval
        dcas = {-1: 'upstream', 0: 'current', 1: 'downstream'}
        nofind = {'point_bas': None,
                  'sect_plein_bord': None,
                  'cote_d': None,
                  'cote_g': None,
                  'x_d': None,
                  'x_g': None, }
        for cas in [-1, 0, 1]:
            if 0 <= id + cas < len(self.liste['x']):
                if self.liste['x'][id + cas]:
                    # print(self.liste['name'][id + cas])
                    minz, area, rz, lz, rmin, lmin = self.val_prof(
                        id + cas)
                    self.ch_prof[dcas[cas]] = {'point_bas': minz,
                                               'sect_plein_bord': area,
                                               'cote_d': rz,
                                               'cote_g': lz,
                                               'x_d': rmin,
                                               'x_g': lmin}
                else:
                    self.ch_prof[dcas[cas]] = nofind
            else:
                self.ch_prof[dcas[cas]] = nofind

    def check_prof_interp(self):
        # TODO interpolation is all profile

        id = self.liste['name'].index(self.nom)
        self.ch_prof_inter = {}
        # cas = -1 amont, cas=1 aval
        dcas = {-1: 'upstream', 0: 'interpolation', 1: 'downstream'}
        nofind = {'point_bas': None,
                  'sect_plein_bord': None}
        for cas in [-1, 0, 1]:
            if cas == 0:
                if 'interpolation' in self.topo.keys():
                    minz, area = self.val_inter_prof(-1)
                    self.ch_prof_inter[dcas[cas]] = {'point_bas': minz,
                                                     'sect_plein_bord': area,
                                                     }
                else:
                    self.ch_prof_inter[dcas[cas]] = nofind
            elif 0 <= id + cas < len(self.liste['x']):
                if self.liste['x'][id + cas]:
                    # print(self.liste['name'][id + cas])

                    minz, area = self.val_inter_prof(id + cas)
                    self.ch_prof_inter[dcas[cas]] = {'point_bas': minz,
                                                     'sect_plein_bord': area,
                                                     }
                else:
                    self.ch_prof_inter[dcas[cas]] = nofind
            else:
                self.ch_prof_inter[dcas[cas]] = nofind

    def check_prof_diag(self):

        self.ui.tab_aff.show()

        self.ui.table_check.show()
        self.check_prof()
        self.fill_table_check()

        self.ui.table_check_interp.show()
        self.check_prof_interp()
        self.fill_table_check_interp()

    def fill_table_check_interp(self):
        """
        Fill table for 'check profile'
        :return:
        """
        # cols = list(self.ch_prof.keys())
        # lines = list(self.ch_prof['current'].keys())
        # exclude_line = ['x_d','x_g']
        # for var in exclude_line :
        #     lines.remove(var)

        cols = ['interpolation', 'upstream', 'downstream']  # , 'interpolation']
        key_str = {'point_bas': 'bottom point',
                   'sect_plein_bord': "Section", }
        lines = list(key_str.keys())
        self.ui.table_check_interp.clear()
        self.ui.table_check_interp.setRowCount(len(lines))
        self.ui.table_check_interp.setColumnCount(len(cols))
        self.ui.table_check_interp.setVerticalHeaderLabels(
            list(key_str.values()))
        self.ui.table_check_interp.setHorizontalHeaderLabels(cols)
        for idc, col in enumerate(cols):
            for idl, line in enumerate(lines):
                val = self.ch_prof_inter[col][line]
                if val is None:
                    val = 'None'
                if isinstance(val, str):
                    item = QTableWidgetItem(
                        '{}'.format(val))
                else:
                    item = QTableWidgetItem('{:.3f}'.format(val))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsEnabled)
                self.ui.table_check_interp.setItem(idl, idc, item)

    def fill_table_check(self):
        """
        Fill table for 'check profile'
        :return:
        """
        # cols = list(self.ch_prof.keys())
        # lines = list(self.ch_prof['current'].keys())
        # exclude_line = ['x_d','x_g']
        # for var in exclude_line :
        #     lines.remove(var)

        cols = ['current', 'upstream', 'downstream']  # , 'interpolation']
        key_str = {'point_bas': 'bottom point',
                   'sect_plein_bord': "Section of minor bed",
                   'cote_d': "Height of the right bank",
                   'cote_g': "Height of the left bank", }
        lines = list(key_str.keys())
        self.ui.table_check.clear()
        self.ui.table_check.setRowCount(len(lines))
        self.ui.table_check.setColumnCount(len(cols))
        self.ui.table_check.setVerticalHeaderLabels(list(key_str.values()))
        self.ui.table_check.setHorizontalHeaderLabels(cols)
        for idc, col in enumerate(cols):
            for idl, line in enumerate(lines):
                val = self.ch_prof[col][line]
                if val is None:
                    val = 'None'
                if isinstance(val, str):
                    item = QTableWidgetItem(
                        '{}'.format(val))
                else:
                    item = QTableWidgetItem('{:.3f}'.format(val))
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsEnabled)
                self.ui.table_check.setItem(idl, idc, item)

    # •	La section de plein bord du lit mineur (profil en cours, aval et amont, soit 3 valeurs)
    # •	Le point bas du lit mineur (profil en cours, aval et amont, soit 3 valeurs)
    # •	Des cotes de débordement de la rive droite et gauche (profil en cours, aval et amont, soit 6 valeurs)
    #
    def maj_tab_check(self):
        self.ch_prof = {}
        self.ui.tab_aff.hide()
        self.ui.table_check.clear()

    def bt_interpol_profile(self):
        """
        Interpolate profile
        :return:
        """
        err = {}
        msgerr, id, idam, idav = self.find_pr_inter()
        if msgerr != '':
            err['iderr'] = msgerr
        self.gui_interpol(id, idam, idav, err)

    def gui_interpol(self, id, idam, idav, err):

        if id:
            plani = self.get_plani(self.liste['abscissa'][id],
                                   self.liste['branchnum'][id])
        else:
            plani = None
        nplan = 100
        if plani is None or idam is None or idav is None:
            err['plani'] = 'Planim not found'
            err['nplan'] = 'No compute discretization'
        else:
            nplan = self.get_nplan(idam, idav, plani)
            if nplan == 0:
                err['nplan'] = 'No compute discretization'

        dict_interp = {}
        if isinstance(idam, int) and isinstance(idav, int):
            dict_interp['up'] = self.get_pr(idam)
            dict_interp['down'] = self.get_pr(idav)

        dlg = ClassProfInterpDialog(self.mgis)
        dlg.init_gui(nplan, plani, dict_interp,
                     self.liste['abscissa'][id], err)
        if dlg.exec_():
            pass

        if dlg.interpol_prof:
            new_prof = np.array(dlg.interpol_prof['prof'])

            condition = "name='{0}' AND profile='{1}'".format('interpolation',
                                                              self.nom)
            self.mdb.delete("topo", condition)
            self.add_topo(new_prof[:, 0], new_prof[:, 1], 'interpolation')
            self.extrait_topo()
            # temporaire zone
            if dlg.interpol_prof['minor'][1]:
                self.tab['rightminbed'] = dlg.interpol_prof['minor'][1]
            if dlg.interpol_prof['minor'][0]:
                self.tab['leftminbed'] = dlg.interpol_prof['minor'][0]
            if dlg.interpol_prof['major'][1]:
                self.tab['rightstock'] = dlg.interpol_prof['major'][1]
            if dlg.interpol_prof['major'][0]:
                self.tab['leftstock'] = dlg.interpol_prof['major'][0]

            self.maj_graph()
            self.maj_legende()
            self.maj_limites()

    def get_plani(self, pk, branch):
        """
        Get planimetry value
        :param pk: abscissa of the profile
        :param branch: branch number
        :return: plani
        """
        plani = None

        rows = self.mdb.select('branchs',
                               where="branch='{}'".format(branch),
                               order="zoneabsstart",
                               list_var=['zonenum', 'zoneabsstart',
                                         'zoneabsend', 'planim', 'active'])

        if rows:

            for i, zone in enumerate(rows['zonenum']):
                if rows['zoneabsstart'][i] <= pk <= rows['zoneabsend'][i]:
                    plani = rows['planim'][i]
                    if rows['active'][i]:
                        break

        # print('plani', plani)
        return plani

    def get_nplan(self, idam, idav, plani):
        """
        get nplan:
            The higher number of planes between the minor bed of the upstream
            profile and that of the downstream profile
        :param idam: upstream profile index
        :param idav: downstream profile  index
        :param plani: planimetry value
        :return:
        """
        nplan_lst = []
        nplan = 0
        for id in [idam, idav]:
            pr_m, rmin, lmin = self.get_minor_pr(id)
            lz = pr_m[0][1]
            rz = pr_m[-1][1]
            bottom = np.min(pr_m)
            nplan_l = (lz - bottom) / plani
            nplan_r = (rz - bottom) / plani
            nplan_lst.append(max(nplan_l, nplan_r))
        nplan = max(nplan, max(nplan_lst))
        return nplan

    def get_pr(self, id):
        """
        get profil id
        :param id:
        :return:
        """

        x_pr = [float(val) for val in self.liste['x'][id].split()]
        z_pr = [float(val) for val in self.liste['z'][id].split()]
        lmin = self.liste['leftminbed'][id]
        rmin = self.liste['rightminbed'][id]
        lmaj = self.liste['leftstock'][id]
        rmaj = self.liste['rightstock'][id]

        lin_s = []
        for x, z in zip(x_pr, z_pr):
            lin_s.append((x, z))

        if not lmin:
            # no valeur for minor bed
            lmin = x_pr[0]
        if not rmin:
            # no valeur for minor bed
            rmin = x_pr[-1]

        if not lmaj:
            # no valeur for major bed
            lmaj = x_pr[0]
        if not rmaj:
            # no valeur for major bed
            rmaj = x_pr[-1]

        dico = {
            'name': self.liste['name'][id],
            'id': self.liste['gid'][id],
            'branch': self.liste['branchnum'][id],
            'prof': lin_s,
            'pk': self.liste['abscissa'][id],
            'minor': [lmin, rmin],
            'major': [lmaj, rmaj],
        }
        return dico

    def get_minor_pr(self, id):
        """
        Get minor bed
        :param id : index profil
        :return:
        """
        x_pr = [float(val) for val in self.liste['x'][id].split()]
        z_pr = [float(val) for val in self.liste['z'][id].split()]
        lmin = self.liste['leftminbed'][id]
        rmin = self.liste['rightminbed'][id]

        lin_s = []
        for x, z in zip(x_pr, z_pr):
            lin_s.append((x, z))
        #
        if not lmin:
            # no valeur for minor bed
            lmin = x_pr[0]
        if not rmin:
            # no valeur for minor bed
            rmin = x_pr[-1]
        pr_m, _, _, _, _ = decoup_pr(lin_s, [lmin, rmin], [lmin, rmin])
        pr_m = np.array(pr_m)
        return pr_m, rmin, lmin

    def find_pr_inter(self):
        msgerr = ''
        idam = None
        idav = None

        id = self.liste['name'].index(self.nom)
        idmax = len(self.liste["name"]) - 1
        if id == 0:
            msgerr += 'No finds upstream profile'
            return msgerr, id, idam, idav
        elif id == idmax:
            msgerr += 'No finds downstream profile'
            return msgerr, id, idam, idav

        # upstream
        idf = id
        while idf != 0:
            idf -= 1
            if self.liste['x'][idf] is not None:
                idam = idf
                break
        # downstream
        idf = id
        while idf != idmax :
            idf += 1
            if self.liste['x'][idf] is not None:
                idav = idf
                break
        # check val
        if idam is None:
            msgerr += 'No finds upstream profile'
        elif idav is None:
            msgerr += 'No finds downstream profile'
        return msgerr, id, idam, idav


def decoup_pr(pr, lminor_x, lmaj_x):
    pr_g = []
    pr_d = []
    pr_m = []
    pr_st_g = []
    pr_st_d = []
    for point in pr:
        if point[0] < lminor_x[0]:
            if point[0] < lmaj_x[0]:
                pr_st_g.append(point)
            else:
                pr_g.append(point)
        elif point[0] > lminor_x[1]:
            if point[0] > lmaj_x[1]:
                pr_st_d.append(point)
            else:
                pr_d.append(point)
        else:
            pr_m.append(point)
    if not pr_m:
        print('Pas de profil lit mineur')
        return [], [], [], [], []
    if not pr_g:
        pr_g = [pr_m[0], pr_m[0]]
    else:
        pr_g = pr_g + [pr_m[0], pr_m[0]]
    if not pr_d:
        pr_d = [pr_m[-1], pr_m[-1]]
    else:
        pr_d = [pr_m[-1], pr_m[-1]] + pr_d
    if not pr_st_g:
        pr_st_g = [pr_g[0], pr_g[0]]
    else:
        pr_st_g = pr_st_g + [pr_g[0], pr_g[0]]
    if not pr_st_d:
        pr_st_d = [pr_d[-1], pr_d[-1]]
    else:
        pr_st_d = [pr_d[-1], pr_d[-1]] + pr_st_d

    return pr_m, pr_g, pr_d, pr_st_g, pr_st_d


class CopySelectedCellsAction(QAction):
    def __init__(self, table_widget):
        if not isinstance(table_widget, QTableWidget):
            chaine = """CopySelectedCellsAction must be initialised with
                     a QTableWidget. A {0} was given."""
            raise ValueError(chaine.format(type(table_widget)))

        super(CopySelectedCellsAction, self).__init__('Copy', table_widget)
        self.setShortcut('Ctrl+C')
        self.triggered.connect(self.copy_cells_to_clipboard)
        self.table_widget = table_widget

    def copy_cells_to_clipboard(self):
        if len(self.table_widget.selectionModel().selectedIndexes()) > 0:
            lst_r = [idx.row() for idx in
                     self.table_widget.selectionModel().selectedIndexes()]
            lst_c = [idx.column() for idx in
                     self.table_widget.selectionModel().selectedIndexes()]
            range_r = range(min(lst_r), max(lst_r) + 1)
            range_c = range(min(lst_c), max(lst_c) + 1)
            clipboard = tw_to_txt(self.table_widget, range_r, range_c, '\t')

            sys_clip = QApplication.clipboard()
            sys_clip.setText(clipboard)
