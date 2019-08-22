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
        GraphProfilRes
        GraphHydro
"""

import os
from datetime import datetime, date

import matplotlib.dates as mdates
import matplotlib.image as mpimg
import matplotlib.lines as mlines
import numpy as np
from matplotlib import patches, colors
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
from matplotlib.widgets import RectangleSelector, SpanSelector, Cursor
from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *

from .Function import isfloat, interpole
from .Structure.ClassMethod import ClassMethod
from .Structure.StructureCreateDialog import ClassStructureCreateDialog
from .WaterQuality.ClassTableWQ import ClassTableWQ

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
            # self.mgis.add_info('couche {0}'.format(couche))

            flag_hydro = self.mgis.hydrogramme
            flag_profil = self.mgis.profil
            flag_profil_r = self.mgis.profil_result
            flag_casier_r = self.mgis.basin_result
            # self.mgis.add_info("flag_hydro: {0} \n flag_profil: {1} \n flag_profil_r:
            # {2} \n".format(flag_hydro,flag_profil,flag_profil_r))
            if couche == 'profiles' and flag_profil:
                self.mgis.coucheProfils = results[0].mLayer
                gid = results[0].mFeature["gid"]
                graph_p = GraphProfil(gid, self.mgis)
                graph_p.exec_()
            # else:
            #     if self.mgis.DEBUG:
            #         self.mgis.add_info("Visu_profil: Not layer")
            if couche == 'profiles' and flag_profil_r:
                self.mgis.coucheProfils = results[0].mLayer
                gid = results[0].mFeature["gid"]
                graph_res = GraphProfilRes(gid, self.mgis)
                # graph_res.exec_()
                graph_res.show()

            # #
            if flag_hydro and couche in ('profiles', 'outputs'):
                feature = results[0].mFeature
                selection = {'abs': [], 'nom': []}

                field_names = [field.name() for field
                               in results[0].mLayer.fields()]

                if 'code' in field_names:
                    selection['code'] = []
                if 'zero' in field_names:
                    selection['zero'] = []
                for f in results[0].mLayer.getFeatures():
                    if f['abscissa']:
                        selection['abs'].append(f['abscissa'])
                        selection['nom'].append(f['name'])
                        if 'code' in selection.keys():
                            selection['code'].append(f['code'])
                        if 'zero' in selection.keys():
                            selection['zero'].append(f['zero'])
                # self.mgis.add_info('graph {0}'.format(results[0].mFeature))
                graph_hyd = GraphHydro(feature, self.mgis, selection, feature['abscissa'], 't')
                # graph_hyd.exec_()
                graph_hyd.show()

            if flag_hydro and couche == 'branchs':
                feature = results[0].mFeature
                # chaine='Branche ' + str(feature['branche'])
                graph_hyd_pk = GraphHydro(feature, self.mgis, {}, '', 'pk')
                # graph_hyd.exec_()
                graph_hyd_pk.show()

            if flag_casier_r and couche in ('basins', 'links'):
                feature = results[0].mFeature
                selection_nontrie = {'num': [], 'nom': []}
                selection = {'num': [], 'nom': []}

                field_names = [field.name() for field
                               in results[0].mLayer.fields()]

                # Boucle sur les attributs de la couche casier ou liaison clickee
                for f in results[0].mLayer.getFeatures():
                    if f['name']:  # si un casier ou une liaison existe
                        selection_nontrie['nom'].append(f['name'])
                        if couche == 'links':
                            selection_nontrie['num'].append(f['linknum'])
                        else:
                            selection_nontrie['num'].append(f['basinnum'])

                # Tri sur les noms des objets
                aa = selection_nontrie['nom']
                for nom in sorted(aa):
                    index = aa.index(nom)
                    selection['nom'].append(selection_nontrie['nom'][index])
                    selection['num'].append(selection_nontrie['num'][index])

                # self.mgis.add_info('nom de la couche choisie' +str(couche))

                graph_basin_link = GraphBasin(feature, self.mgis, selection, feature['name'], couche)
                graph_basin_link.show()
        return


class GraphCommon(QDialog):
    def __init__(self, mgis=None):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.tbwq = ClassTableWQ(self.mgis, self.mdb)

        self.dossierPlugin = self.mgis.masplugPath
        self.dossierProjet = self.mgis.repProject
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)

    def init_ui_common_p(self, gid):
        """variables in common for profile graphics"""
        self.gid = gid
        self.coucheProfils = self.mgis.coucheProfils
        # try:
        self.liste = self.mdb.select("profiles", "", "abscissa")
        # except:
        #     self.mgis.add_info("Error Select profils")

        self.position = self.liste["gid"].index(self.gid)
        self.feature = {k: v[self.position] for k, v in self.liste.items()}
        self.nom = self.feature['name']

        self.courbes = []

    def gui_graph(self, ui):
        self.verticalLayout_99 = QVBoxLayout(ui.widget_figure)
        self.verticalLayout_99.setObjectName("verticalLayout_99")
        self.verticalLayout_99.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.verticalLayout_98 = QVBoxLayout(ui.widget_toolsbar)
        self.verticalLayout_98.setObjectName("verticalLayout_98")
        self.verticalLayout_98.addWidget(self.toolbar)


class GraphProfil(GraphCommon):
    """class Dialog graphProfil"""

    def __init__(self, gid, mgis=None):
        GraphCommon.__init__(self, mgis)

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphProfil.ui'), self)
        self.init_ui_common_p(gid)
        self.gui_graph(self.ui)
        self.init_ui()
        self.struct = ClassMethod(self.mgis)

        # action
        self.ui.actionBtTools_point_selection.triggered.connect(self.selector_toggled)
        self.ui.actionBtTools_zone_selection.triggered.connect(self.zone_selector_toggled)
        self.ui.actionBtTools_profil_translation.triggered.connect(self.deplace_toggled)

        self.ui.actionBt_add_point.triggered.connect(self.ajout_points)
        self.ui.actionBt_topo_load.triggered.connect(self.import_topo)
        self.ui.actionBt_topo_del.triggered.connect(self.del_topo)
        # self.ui.actionBt_img_load.triggered.connect(self.import_image)
        self.ui.actionBt_topo_save.triggered.connect(self.sauve_topo)

        self.ui.actionBt_reculTot.triggered.connect(lambda: self.avance(-10))
        self.ui.actionBt_recul.triggered.connect(lambda: self.avance(-1))
        self.ui.actionBt_av.triggered.connect(lambda: self.avance(1))
        self.ui.actionBt_avTot.triggered.connect(lambda: self.avance(10))
        self.ui.actionBt_profil_save.triggered.connect(self.sauve_profil)
        self.ui.actionBt_profil_filter.triggered.connect(self.filtre)
        self.ui.actionBt_profil_del.triggered.connect(self.efface_profil)
        self.ui.actionBt_minor_bed.triggered.connect(self.select_lit_mineur)
        self.ui.actionBt_r_stok.triggered.connect(lambda: self.select_stock("rightstock"))
        self.ui.actionBt_l_stok.triggered.connect(lambda: self.select_stock("leftstock"))
        self.ui.actionBt_ouvrage.triggered.connect(self.create_struct)

    def init_ui(self):

        # variables
        self.tab = {'x': [], 'z': []}
        self.selected = {}
        self.mnt = {'x': [], 'z': []}
        self.x0 = None
        self.flag = False
        self.image = None
        self.topoSelect = None
        self.bt_transla = self.ui.btTools_profil_translation
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
        self.tableau.selectionModel().selectionChanged.connect(self.select_changed)
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
        for i in range(5):
            temp, = self.axes.plot([], [], color='green', marker='+', mew=2,
                                   zorder=95, label='Topo', picker=5)
            self.courbeTopo.append(temp)

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
            self.ui.bt_add_point.setEnabled(True)
            self.bt_select_z.setChecked(False)
            self.bt_transla.setChecked(False)

        else:
            self.ui.bt_add_point.setDisabled(True)
            self.RS.set_active(False)

    def zone_selector_toggled(self, checked):
        """zone selection function"""
        if self.bt_select_z.isChecked():
            self.span.visible = True
            self.bt_select.setChecked(False)
            self.bt_transla.setChecked(False)
        else:
            self.span.visible = False

    def deplace_toggled(self, checked):
        """Translation function"""
        if self.bt_transla.isChecked():
            self.bt_select.setChecked(False)
            self.bt_select_z.setChecked(False)

    def create_struct(self):
        """ creation of hydraulic structure"""
        # TODO
        # self.struct.GUI()
        # choix pour la création de la config
        # return
        dlg = ClassStructureCreateDialog(self.mgis, self.gid)
        if dlg.exec_():
            pass
            # print("create_struct")
        # if self.feature["x"] and self.feature["z"]:
        #     self.struct.copy_profil(self.gid)
        #     print("create_struct")
        pass

    def avance(self, val):
        """next or back profiles """
        if self.image:
            self.image.set_visible(False)
        self.rectSelection.set_visible(False)
        self.selected = {}
        self.courbeSelection.set_data([], [])
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
        self.maj_graph()
        self.maj_limites()
        self.maj_legende()

    def extrait_mnt(self):
        self.mnt = {'x': [], 'z': []}

        condition = "idprofil={0}".format(self.gid)
        requete = self.mdb.select("mnt", condition)
        if "x" in requete.keys() and "z" in requete.keys():
            # self.mnt['x'] = list(map(float, requete["x"][0].split()))
            # self.mnt['z'] = list(map(float, requete["z"][0].split()))
            self.mnt['x'] = [float(var) for var in requete["x"][0].split()]
            self.mnt['z'] = [float(var) for var in requete["z"][0].split()]

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
            # self.tab['x'] = list(map(float, self.feature["x"].split()))
            # self.tab['z'] = list(map(float, self.feature["z"].split()))
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
            # self.mnt['x'] = list(map(float, self.feature["xmnt"].split()))
            # self.mnt['z'] = list(map(float, self.feature["zmnt"].split()))

    def extrait_topo(self):

        self.topo = {}

        condition = "profile='{0}'".format(self.nom)
        ordre = "name, order_"
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
            self.topo[nom]['x'] = self.mdb.projection(self.nom, self.topo[nom]['x'], self.topo[nom]['gid'])

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

        for k, v in self.tab.items():
            if isinstance(v, list):
                self.liste[k][self.position] = " ".join([str(var) for var in v])
            else:
                self.liste[k][self.position] = v

        self.feature = {k: v[self.position] for k, v in self.liste.items()}

        tab = {self.nom: self.tab}
        self.mdb.update("profiles", tab, var="name")

    def sauve_topo(self):
        """ Save les modification du à la translation de la topo"""
        for nom, t in self.topo.items():
            for x, z, gid, ordre in zip(t['x'], t['z'], t['gid'], t['ordre']):
                for f in self.coucheProfils.getFeatures():
                    if f["name"] == self.nom:
                        p = f.geometry().interpolate(x).asPoint()
                        geom = "ST_SetSRID(ST_MakePoint({0}, {1}),{2})".format(p.x(), p.y(), self.mdb.SRID)

                if gid:
                    sql = """UPDATE {0}.topo SET x={1}, geom={2}, order_={3}
                          WHERE gid={4}""".format(self.mdb.SCHEMA,
                                                  x,
                                                  geom,
                                                  ordre,
                                                  gid)
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
            condition = "name='{0}' AND profile='{1}'".format(name_topo, self.nom)
            self.mdb.delete("topo", condition)

        self.extrait_topo()
        self.maj_graph()
        self.maj_limites()
        self.maj_legende()

    def import_topo(self):
        if int(qVersion()[0]) < 5:  # qt4
            fichiers = QFileDialog.getOpenFileNames(None,
                                                    'File Selection',
                                                    self.dossierProjet,
                                                    "File (*.txt *.csv)")
        else:  # qt5
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
                    condition = "name='{}' AND profile='{}'".format(basename, profil)

                    self.mdb.delete("topo", condition)

                    tab = {'name': [], 'profile': [], 'order_': [], 'x': [], 'z': [],
                           'geom': []}
                    with open(fichier, "r") as fich:
                        entete = fich.readline()
                        if len(entete.split()) > 1:
                            sep = None
                        else:
                            sep = ";"

                        ordre = 0
                        for ligne in fich:
                            # x, z = list(map(float, ligne.split(sep)))
                            x, z = [float(var) for var in ligne.split(sep)]
                            ordre += 1

                            p = f.geometry().interpolate(x).asPoint()

                            # geom = "ST_MakePoint({0}, {1})".format(p.x(), p.y())

                            geom = "ST_SetSRID(ST_MakePoint({0}, {1}),{2})".format(p.x(), p.y(), self.mdb.SRID)

                            tab["name"].append("'" + basename + "'")
                            tab["profile"].append("'" + profil + "'")
                            tab["order_"].append(ordre)
                            tab["x"].append(x)
                            tab["z"].append(z)
                            tab["geom"].append(geom)

                    self.mdb.insert2("topo", tab)

    def import_image(self):
        if int(qVersion()[0]) < 5:  # qt4
            fichier = QFileDialog.getOpenFileName(None,
                                                  'Sélection des fichiers',
                                                  self.dossierProjet,
                                                  "Fichier (*.png *.jpg)")
        else:  # qt5
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
        deplace = self.bt_transla.isChecked()
        selector = self.bt_select.isChecked()
        zone_selector = self.bt_select_z.isChecked()
        bouton = event.mouseevent.button

        if deplace and legline in self.courbeTopo and bouton == 1:
            self.x0 = round(event.mouseevent.xdata, 2)
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
            courbe = self.lined[legline.get_label()]
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
                self.mgis.add_info("The table has {0} elements, please add ".format(n))

    def onrelease(self, event):
        if self.bt_transla.isChecked():
            self.x0 = None
        return

    def onclick(self, event):

        if self.flag and event.button == 3:
            if self.ordre == -9999:
                item, ok = QInputDialog.getItem(self,
                                                "Curve",
                                                "Choice of Curve",
                                                self.topo.keys(),
                                                0)

                if not ok:
                    return

                num, ok = QInputDialog.getInt(self,
                                              "Order",
                                              "Input the initial order",
                                              0)
                if not ok:
                    return

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
        if self.bt_transla.isChecked() and self.x0:
            f = self.courbeSelected.get_label()
            try:
                tab_x = self.topo[f]['x']
                # tab_x = list(map(lambda x: x + round(event.xdata, 2) - self.x0, tab_x))
                tempo = []
                # fct2 = lambda x: x + round(float(event.xdata), 2) - self.x0
                for var1 in tab_x:
                    tempo.append(self.fct2(var1, event.xdata, self.x0))
                tab_x = tempo

                self.topo[f]['x'] = tab_x
                self.courbeSelected.set_xdata(tab_x)

                self.x0 = round(float(event.xdata), 2)
            except:
                if self.mgis.DEBUG:
                    self.mgis.add_info("Warning:Out of graph")
            self.fig.canvas.draw()

    def maj_graph(self):
        """Updating  graphic"""
        self.ui.label_Title.setText(_translate("ProfilGraph", self.nom, None))
        ta = self.tab
        self.courbeProfil.set_data(ta['x'], ta['z'])

        self.remplir_tab([ta['x'], ta['z']])

        self.courbeMNT.set_data(self.mnt['x'], self.mnt['z'])

        self.courbes = [self.courbeProfil, self.courbeMNT]

        for c in self.courbeTopo:
            c.set_data([], [])

        for i, (fichier, v) in enumerate(self.topo.items()):
            if i >= len(self.courbeTopo):
                break

            self.courbeTopo[i].set_data(v['x'], v['z'])
            self.courbeTopo[i].set_label(fichier)
            self.courbes.append(self.courbeTopo[i])
        if ta['x'] is not None and ta['leftminbed'] is not None and ta['rightminbed'] is not None:
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
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(5)
            legline.set_linewidth(3)
            self.lined[legline.get_label()] = courbe
        self.canvas.draw()

    @staticmethod
    def fct1(x):
        """around"""
        return round(float(x), 2)

    def ajout_points(self):
        """ add points"""
        if self.selected:
            self.courbeSelection.set_visible(False)
            # self.selected['x'] = list(map(lambda x: round(x, 2), self.selected['x']))
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
                self.mgis.add_info("The table has {0} elements, please add ".format(n))

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
            previous = self.table_widget.selectionModel().selectedIndexes()[0]
            col = previous.column()
            columns = []
            rows = [self.table_widget.horizontalHeaderItem(col).text()]
            for index in self.table_widget.selectionModel().selectedIndexes():
                if col != index.column():
                    columns.append(rows)
                    col = index.column()
                    rows = [self.table_widget.horizontalHeaderItem(col).text()]
                rows.append(index.data())
                col = index.column()

            columns.append(rows)
            clipboard = ''
            nrows = len(columns[0])
            ncols = len(columns)
            for r in range(nrows):
                for c in range(ncols):
                    clipboard += columns[c][r]
                    if c != ncols - 1:
                        clipboard += '\t'

                clipboard += '\n'

            sys_clip = QApplication.clipboard()
            sys_clip.setText(clipboard)


class GraphProfilRes(GraphCommon):
    """class Dialog graphProfilRes"""

    def __init__(self, gid, mgis=None):
        GraphCommon.__init__(self, mgis)

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphProfilRes.ui'), self)
        self.init_ui_common_p(gid)
        self.gui_graph(self.ui)
        qres = self.init_ui()

        if qres:
            # Action
            self.ui.actionBt_reculTot.triggered.connect(lambda: self.avance(-10))
            self.ui.actionBt_recul.triggered.connect(lambda: self.avance(-1))
            self.ui.actionBt_av.triggered.connect(lambda: self.avance(1))
            self.ui.actionBt_avTot.triggered.connect(lambda: self.avance(10))

            #
            self.ui.actionBt_exportCSV.triggered.connect(self.export_csv)
            # self.ui.actionComboBox_State.triggered.connect(self.combo_run_changed)
            self.comboRun.currentIndexChanged['QString'].connect(self.combo_run_changed)
            # self.ui.comboBox_State.currentIndexChanged.connect(self.combo_run_changed)
            self.comboScen.currentIndexChanged['QString'].connect(self.combo_scen_changed)
            self.comboTime.currentIndexChanged['QString'].connect(self.combo_time_changed)

    def init_ui(self):

        try:
            self.tab = {}
            # condition = "NOT scenario LIKE '%init%'"
            # dico = self.mdb.select_distinct("date, run, scenario",
            #                                      "runs",
            #                                      condition)
            dico_run = self.mdb.select_distinct("date, run, scenario,t, comments", "runs")
            if not dico_run:
                self.mgis.add_info("No simulation to show")
                return False

            self.listeRuns = {}
            self.liste_comm = {}
            for run, scen, comm in zip(dico_run["run"], dico_run["scenario"],dico_run["comments"]):
                if run not in self.listeRuns.keys():
                    self.listeRuns[run] = []
                    self.liste_comm[run] = {}
                self.liste_comm[run][scen] = comm
                self.listeRuns[run].append(scen)

            self.run = list(self.listeRuns.keys())[-1]
            self.scenario = self.listeRuns[self.run][-1]

            # listing
            self.comboRun = self.ui.comboBox_State
            self.comboRun.clear()
            self.comboRun.addItems(self.listeRuns.keys())
            le = len(self.listeRuns.keys())
            self.comboRun.setCurrentIndex(le - 1)
            self.comboScen = self.ui.comboBox_Scenar
            self.comboScen.clear()

            self.comboScen.addItems(self.listeRuns[self.run])
            le = len(self.listeRuns[self.run])
            self.comboScen.setCurrentIndex(le - 1)

            # time list
            self.comboTime = self.ui.comboBox_Time
            self.posit = 'Hmax'
            self.listcombo_time()

            self.tableau = self.ui.tableWidget_RES
            self.tableau.addAction(CopySelectedCellsAction(self.tableau))

            # figure
            self.axes = self.fig.add_subplot(111)
            self.axes.grid(True)
            self.courbeProfil, = self.axes.plot([], [], zorder=100, label='Profile')
            # self.aireMouillee, = self.axes.plot([], [], zorder=90, label='aire')

            self.courbes = [self.courbeProfil]

            rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='pink',
                                     alpha=0.5, lw=1, zorder=80)
            self.litMineur = self.axes.add_patch(rect)

            rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                     alpha=0.3, lw=1, zorder=80)
            self.stockgauche = self.axes.add_patch(rect)

            rect = patches.Rectangle((0, -9999999), 0, 2 * 9999999, color='green',
                                     alpha=0.3, lw=1, zorder=80)
            self.stockdroit = self.axes.add_patch(rect)

            self.aire = []
            self.title = self.ui.label_Title

            self.label_hmax = self.ui.label_hmax

            self.titleFig = self.fig.suptitle("")

            self.maj_graph()
            self.maj_legende()
            self.maj_limites()

            self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
            self.fig.patch.set_facecolor((0.94, 0.94, 0.94))
            self.fig.canvas.mpl_connect('pick_event', self.onpick)
            # # self.fig.tight_layout()
            return True

        except:
            self.mgis.add_info("No simulation to show")
            return False

    def listcombo_time(self):
        """creation of the Time list"""
        self.comboTime.currentIndexChanged['QString'].disconnect()
        self.comboTime.clear()
        self.date = False
        self.type = 't'
        self.listeTime = {'t': [], 'date': []}
        condition = "run='{0}' AND scenario='{1}'".format(self.run,
                                                          self.scenario)
        temp = self.mdb.select_distinct("date", "resultats", condition, 'date')
        if temp["date"][0]:
            self.date = True
            if self.type == 't':
                self.type = 'date'
        else:
            if self.type == 'date':
                self.type = 't'

        self.listeTime['date'] = temp['date']
        temp = self.mdb.select_distinct("t", "resultats", condition, 't')
        self.listeTime['t'] = temp['t']
        self.comboTime.addItem('Hmax')
        for x in self.listeTime[self.type]:
            if isinstance(x, float):
                self.comboTime.addItem(str(x))
            else:
                self.comboTime.addItem('{0:%d/%m/%Y %H:%M:%S}'.format(x))
        self.posit = 'Hmax'
        self.comboTime.setCurrentIndex(0)
        self.comboTime.currentIndexChanged['QString'].connect(self.combo_time_changed)

    def export_csv(self):
        """Export Table to .CSV file"""

        default_name = self.nom.replace(' ', '_').replace(':', '-')
        if int(qVersion()[0]) < 5:  # qt4
            file_name_path = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
                                                         filter="CSV (*.csv *.)")
        else:  # qt5
            file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
                                                            filter="CSV (*.csv *.)")

        if file_name_path:
            file = open(file_name_path, 'w')
            file.write("# {0} \n".format(self.nom))
            file.write("# X ; Z \n")

            for i, x in enumerate(self.tab[self.nom]['x']):
                z = self.tab[self.nom]['z'][i]
                file.write("{0} ; {1} \n".format(x, z))
            file.close()

    def remplir_tab(self, liste):
        """ Fill items in the table"""
        self.tableau.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.tableau.setItem(i, j, QTableWidgetItem(str(v)))

    def colorie_tab(self, liste, dict_couleur):
        for i, type in enumerate(liste):
            for j in range(self.tableau.columnCount()):
                if type in dict_couleur.keys():
                    self.tableau.item(i, j).setBackground(dict_couleur[type])
                else:
                    self.tableau.item(i, j).setBackground(Qt.white)

    def selection_tab(self):
        mini_x = 99999999
        maxi_x = -99999999
        for index in self.tableau.selectionModel().selectedIndexes():
            if index.column() == 0:
                temp = float(index.data())
                mini_x = min(mini_x, temp)
                maxi_x = max(maxi_x, temp)
        return mini_x, maxi_x

    def maj_graph(self):
        for patch in self.aire:
            if patch in self.axes.patches:
                self.axes.patches.remove(patch)

        self.title.setText(self.nom)
        try :
            comm = self.liste_comm[self.run][self.scenario]
            if comm != '' and comm != None:
                self.ui.label_comments.show()
                self.ui.label2.show()
                self.ui.label_comments.setText(comm)
            else:
                self.ui.label_comments.hide()
                self.ui.label2.hide()
        except:
            self.ui.label_comments.hide()
            self.ui.label2.hide()
        # profile
        self.extrait_profil()

        ta = self.tab[self.nom]
        self.courbeProfil.set_data(ta['x'], ta['z'])

        self.remplir_tab([ta['x'], ta['z']])

        ta['leftminbed'] = self.feature["leftminbed"]
        ta['rightminbed'] = self.feature["rightminbed"]
        ta['leftstock'] = self.feature["leftstock"]
        ta['rightstock'] = self.feature["rightstock"]

        if ta['x'] and ta['leftminbed'] and ta['rightminbed']:
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

        # value H
        self.maj_val()

        if self.zH is not None:
            self.label_hmax.setText('{0}'.format(self.zmax))
            temp1 = np.array(ta['z'])

            if self.posit == 'Hmax':
                temp2 = np.array([self.zmax] * len(ta['z']))
            else:
                h = self.zH['zref'][0] + self.zH['y'][0]
                temp2 = np.array([h] * len(ta['z']))

            aire = self.axes.fill_between(ta['x'], temp1, temp2,
                                          where=temp2 >= temp1,
                                          interpolate=True)
            self.aire = []

            for p in aire.get_paths():
                if ta['leftminbed'] is not None:
                    gauch = ta['leftminbed']
                else:
                    gauch = min(p.vertices[:, 0])
                if ta['rightminbed'] is not None:
                    droit = ta['rightminbed']
                else:
                    droit = max(p.vertices[:, 0])
                for x, y in p.vertices:

                    if gauch <= x <= droit:
                        patch = patches.PathPatch(p,
                                                  facecolor='deepskyblue',
                                                  lw=0)
                        self.aire.append(patch)
                        self.axes.add_patch(patch)
                        break

            self.axes.collections.remove(aire)
            # Figure title
            if self.posit == 'Hmax':
                self.titleFig.set_text('Max of water level, {0} m '.format(round(self.zmax, 3)))
            elif isinstance(self.posit, float):
                self.titleFig.set_text('Water level, {0} m - {1} s'.format(h, self.posit))
            else:
                self.titleFig.set_text('Water level, {0} m - {1:%d/%m/%Y %H:%M}'.format(h, self.posit))

        self.canvas.draw()

    def maj_limites(self):
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

    def extrait_profil(self):
        if self.nom not in self.tab.keys():
            self.tab[self.nom] = {'x': [], 'z': []}
        else:
            return

        if self.feature['x'] and self.feature['z']:
            condition = "name='{0}'".format(self.nom)
            requete = self.mdb.select("profiles", condition)
            # self.tab[self.nom]['x'] = list(map(float, requete["x"][0].split()))
            # self.tab[self.nom]['z'] = list(map(float, requete["z"][0].split()))
            self.tab[self.nom]['x'] = [float(var) for var in requete["x"][0].split()]
            self.tab[self.nom]['z'] = [float(var) for var in requete["z"][0].split()]

    def onpick(self, event):
        legline = event.artist
        if legline in self.lined.keys():
            courbe = self.lined[legline]
            vis = not courbe.get_visible()
            courbe.set_visible(vis)
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)
            self.canvas.draw()

    def combo_run_changed(self, text):
        """function for change ComboBox and update the figure"""
        self.run = text
        # self.mgis.add_info("scenario")
        # self.mgis.add_info(self.scenario)

        if self.scenario not in self.listeRuns[self.run]:
            self.scenario = self.listeRuns[self.run][-1]
        self.comboScen.currentIndexChanged['QString'].disconnect()
        self.comboScen.clear()
        self.comboScen.addItems(self.listeRuns[self.run])
        self.comboScen.currentIndexChanged['QString'].connect(
            self.combo_scen_changed)

        self.listcombo_time()

        # self.maj_liste()
        # self.maj_tab()
        self.maj_graph()

    def combo_scen_changed(self, text):
        self.scenario = text
        self.listcombo_time()
        # self.maj_liste()
        # self.maj_tab()
        self.maj_graph()

    def combo_time_changed(self, text):
        # change the Figure in function of Time
        if text == 'Hmax':
            self.posit = text
        elif isfloat(text):
            self.posit = float(text)
        else:
            self.posit = datetime.strptime(text, '%d/%m/%Y %H:%M:%S')
        self.maj_graph()

    def maj_val(self):
        # get value for graphic
        abscisse = self.feature['abscissa']

        condition = "run='{0}' AND scenario='{1}' AND pk={2}".format(self.run,
                                                                     self.scenario,
                                                                     abscisse)
        self.zmax = self.mdb.select_max("z", "resultats", condition)

        if self.posit == 'Hmax':
            self.zH = self.zmax
        elif isinstance(self.posit, datetime):
            condition += """ AND date='{:%Y-%m-%d %H:%M:%S}'""".format(
                self.posit)
            self.zH = self.mdb.select("resultats", condition, "t")
        else:
            condition += " AND t={0}".format(self.posit)
            self.zH = self.mdb.select("resultats", condition, "t")

    def avance(self, val):

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

        self.maj_graph()
        self.maj_limites()
        self.maj_legende()

    def maj_legende(self):
        liste_noms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, liste_noms, loc='upper right',
                                    fancybox=False, shadow=False)
        self.leg.get_frame().set_alpha(0.4)
        self.leg.set_zorder(110)
        self.leg.draggable(True)
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(5)
            legline.set_linewidth(3)
            self.lined[legline] = courbe

        self.canvas.draw()

    def select_changed(self):
        mini_x, maxi_x = self.tableau.selection()

        if mini_x != 99999999 and maxi_x != -99999999:
            self.rectSelection.set_x(mini_x)
            self.rectSelection.set_width(maxi_x - mini_x)
            self.rectSelection.set_visible(True)
            self.canvas.draw()


class GraphHydro(GraphCommon):
    def __init__(self, feature, mgis, select, position, type):
        # feature, selection, position, type, mainp
        GraphCommon.__init__(self, mgis)
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphHydro.ui'), self)

        self.feature = feature
        self.position = position
        self.select = select
        self.type = type
        self.comboRun = self.ui.comboBox_State
        self.comboScen = self.ui.comboBox_Scenar
        self.comboTimePK = self.ui.comboBox_time
        self.comboVar1 = self.ui.comboBox_var1
        # insert graphic and toolsbars of graphic
        self.gui_graph(self.ui)

        self.init_ui()

        #         # Action
        self.ui.actionBt_reculTot.triggered.connect(lambda: self.avance(-10))
        self.ui.actionBt_recul.triggered.connect(lambda: self.avance(-1))
        self.ui.actionBt_av.triggered.connect(lambda: self.avance(1))
        self.ui.actionBt_avTot.triggered.connect(lambda: self.avance(10))
        #
        #
        self.ui.actionBt_exportCSV.triggered.connect(self.export_csv)
        self.comboRun.currentIndexChanged['QString'].connect(self.combo_run_changed)
        self.comboScen.currentIndexChanged['QString'].connect(self.combo_scen_changed)
        self.comboVar1.currentIndexChanged['QString'].connect(self.combo_var1_changed)
        self.comboTimePK.currentIndexChanged['QString'].connect(self.combo_time_pk_change)

    #         # self.ui.actionComboBox_var2.triggered.connect()
    #         # self.ui.actionTableWidget_RES.triggered.connect()
    #
    def init_ui(self):

        if self.type == 't':
            self.titre = 'Section '
            self.branche = self.feature["branchnum"]
        else:
            self.titre = 'Branche {}'.format(self.feature["branch"])
            self.branche = self.feature["branch"]

        self.liste = {'selection': self.select, 't': {}, 'date': {}, 'pk': {}}

        # self.fichierObs = os.path.join(self.mgis.dossierProjet, 'donnees',
        # 'observations.csv')
        self.temps = 'max'
        self.variables = self.mgis.variables

        # 'Cote'#''None'
        self.var1 = 'Z'
        self.coteVar = ['ZREF', 'Z', 'ZMAX', 'ZMIN']
        self.debVar = ['Q', 'QMIN', 'QMAJ', 'QMAX']

        self.obs = {}

        self.flag = False

        # list run
        # condition = "NOT scenario LIKE '%init%'"
        # dico = self.mdb.select_distinct("date, run, scenario",
        #                                           "runs",
        #                                           condition)
        dico_run = self.mdb.select_distinct("date, run, scenario, pk, comments",
                                            "runs")

        if not dico_run:
            self.mgis.add_info("No simulation to show")
            return False

        self.listeRuns = {}
        self.liste_comm = {}
        for run, scen, pk,comm in zip(dico_run["run"], dico_run["scenario"], dico_run['pk'],dico_run["comments"]):

            if self.type == 't':
                try:
                    pk_tmp = [round(elem, 2) for elem in pk]
                    idx = pk_tmp.index(self.position)
                    if run not in self.listeRuns.keys():
                        self.listeRuns[run] = []
                        self.liste_comm[run] = {}
                    self.listeRuns[run].append(str(scen))
                    self.liste_comm[run][scen] = comm
                except ValueError:
                    pass
            else:
                if run not in self.listeRuns.keys():
                    self.listeRuns[run] = []
                    self.liste_comm[run] = {}
                self.listeRuns[run].append(str(scen))
                self.liste_comm[run][scen] = comm


        if self.listeRuns == {}:
            self.mgis.add_info('No results for this profile. \n')
        self.run = sorted(self.listeRuns.keys())[-1]

        self.scenario = self.listeRuns[self.run][-1]

        self.comboRun.clear()
        self.comboRun.addItems(sorted(self.listeRuns.keys()))
        le = len(self.listeRuns.keys())
        self.comboRun.setCurrentIndex(le - 1)

        self.comboScen.clear()
        # self.mgis.add_info('{}'.format(self.listeRuns[self.run]))
        self.comboScen.addItems(self.listeRuns[self.run])
        le = len(self.listeRuns[self.run])
        self.comboScen.setCurrentIndex(le - 1)

        temp = self.mdb.select_distinct("abscissa", "weirs", "active")
        if temp:
            seuils = temp["abscissa"]
        else:
            seuils = []

        self.comboTimePK.clear()
        columns_tmp = self.mdb.list_columns("resultats")[8:]
        self.columns = []
        for col in columns_tmp:
            if not col in ['bnum', 'lnum']:
                self.columns.append(col)

        # self.mgis.add_info(' ListG {}'.format(self.columns))

        self.colVal = []
        self.unite = ""
        self.columns_tra = []
        lind = []
        for i, col in enumerate(self.columns):
            try:
                if self.variables[col]['code'] == self.var1:
                    self.unite = self.variables[col]['unite']
                    self.var1Name = self.variables[col]['nom']
                    self.colVal.append(col)
            except:
                self.columns_tra.append(col)
                lind.append(i)

        typ_trac = self.tbwq.get_cur_wq_mod()
        name_tra = self.tbwq.dico_wq_mod[typ_trac]
        color_names = list(colors.cnames.keys())

        length_color = len(color_names)
        cpt = 0
        ncolor = {'aliceblue': 'blue'}
        for i, col in enumerate(self.columns_tra):
            if cpt < length_color:
                if color_names[cpt] in list(ncolor.keys()):
                    color = ncolor[color_names[cpt]]
                else:
                    color = color_names[cpt]
                cpt += 1
            else:
                color = color_names[0]
                cpt = 1

            self.variables[col.lower()] = {'nom': self.tbwq.dico_phy[name_tra]['tracer'][i]['text'],
                                           'code': self.tbwq.dico_phy[name_tra]['tracer'][i]['sigle'],
                                           'unite': 'unit',
                                           'couleur': color}

        liste_nom = [self.type]
        # default value
        liste_g = []
        for col in self.columns:
            liste_nom.append(self.variables[col]['nom'])
            codd = self.variables[col]['code']
            # var = self.variables[col]['nom'].split()[0]
            if codd in self.coteVar:
                var = 'Levels'
            elif codd in self.debVar:
                var = 'Flow rates'
            elif codd in self.columns_tra:
                var = 'Tracers'
            else:
                var = self.variables[col]['nom']
            if var not in liste_g:
                liste_g.append(var)

        # creation tableau
        self.tableau = self.ui.tableWidget_RES
        self.tableau.setColumnCount(len(liste_nom))
        self.tableau.setRowCount(0)
        self.tableau.setHorizontalHeaderLabels(liste_nom)
        self.tableau.addAction(CopySelectedCellsAction(self.tableau))

        # comboGrandeur

        self.comboVar1.clear()
        self.comboVar1.addItems(liste_g)
        # if self.var1:
        #     self.comboVar1.setCurrentIndex(liste_g.index(self.var1))

        # Figure
        self.axes = self.fig.add_subplot(111)
        if self.type == 'pk':
            self.axes.set_xlabel('Pk (m)')

        else:
            self.axes.set_xlabel('Time (s)')
            self.axes.grid(True)

        self.axes.set_ylabel("{0} ({1})".format(self.var1Name, self.unite))

        self.courbeHydro = {}

        for i, col in enumerate(self.columns):
            couleur = self.variables[col]['couleur']
            temp, = self.axes.plot([], [], zorder=100, color=couleur)
            self.courbeHydro[col] = temp

        self.courbeObs, = self.axes.plot([], [], color='grey',
                                         marker='o', markeredgewidth=0,
                                         zorder=90, label='Observation')

        self.courbeLaisses = self.axes.scatter([], [], label="Flood marks")
        self.etiquetteLaisses = []

        self.maj_liste()

        self.maj_tab()
        self.maj_laisses()
        self.maj_legende()
        self.maj_graph()
        self.maj_limites()

        self.fig.tight_layout()
        self.fig.patch.set_facecolor((0.94, 0.94, 0.94))
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        self.annotation = []
        # arrow = dict(arrowstyle="-",facecolor='black')
        box = dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7)
        txtcoord = 'offset points'
        for i in range(10):
            self.annotation.append(self.axes.annotate("",
                                                      xy=(0, 0),
                                                      ha='left',
                                                      xytext=(10, 0),
                                                      textcoords=txtcoord,
                                                      va='top',
                                                      bbox=box,
                                                      visible=False,
                                                      zorder=110))
        self.ligne = self.axes.axvline(color="black")

        for s in seuils:
            self.axes.axvline(s, color="lightgrey", zorder=10, visible=True)
            # self.annotation = self.axes.annotate("", xy=(0, 0), ha='left',
            # xytext=(20,-20), textcoords='offset points', va='top',
            # bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.3),
            # visible=False, zorder=110)

        self.rect = self.axes.add_patch(patches.Rectangle((0, 0), 0, 0,
                                                          zorder=101,
                                                          color='white',
                                                          alpha=0.8))

        self.clic = self.fig.canvas.mpl_connect('button_press_event',
                                                self.onclick)
        self.declic = self.fig.canvas.mpl_connect('button_release_event',
                                                  self.offclick)
        self.motion = self.fig.canvas.mpl_connect('motion_notify_event',
                                                  self.onpress)
        # self.motion = self.fig.canvas.mpl_connect('motion_notify_event',
        # self.affiche_cadre)
        #
        return True

    def affiche_cadre(self, event):
        flag = True
        for c in self.toolbar.findChildren(QToolButton):
            if c.isChecked():
                flag = False
                break

        if not flag or not event.xdata or not event.ydata:
            for a in self.annotation:
                a.set_visible(False)
            self.ligne.set_visible(False)
            self.canvas.draw()
            return

        liste = []
        unite = []
        couleur = []

        if self.type == 'date':
            temp = round((event.xdata - 719163) * 24) * 3600
            decal = datetime.utcfromtimestamp(temp)
            absc = min(self.tab[self.type], key=lambda x: abs(x - decal))
        else:
            absc = min(self.tab[self.type], key=lambda x: abs(x - event.xdata))
        # liste.append("Abscisse: "+ str(absc))
        liste.append(absc)
        unite.append("")
        couleur.append('black')

        for col in self.colVal:
            if self.tab[col] and self.courbeHydro[col].get_visible():
                index = self.tab[self.type].index(absc)
                val = self.tab[col][index]
                nom = self.variables[col]['nom']
                # unite = self.variables[col]['unite']
                # liste.append("{0}: {1} {2}".format(nom, val, unite))
                liste.append(val)
                unite.append(self.variables[col]['unite'])
                couleur.append(self.variables[col]['couleur'])
                # couleurs.append(self.courbeHydro[col].get_color())

        if self.obs and absc in self.obs['date']:
            index = self.obs['date'].index(absc)

            if self.var1 in self.coteVar:
                liste.append(self.obs['valeur'][index])
                unite.append("m")
                couleur.append("grey")
            elif self.var1 in self.debVar:
                liste.append(self.obs['valeur'][index])
                unite.append(r"$m^3/s$")
                couleur.append("grey")

                # self.annotation.set_text("\n".join(liste))
        # self.annotation.set_visible(True)
        # self.annotation.xy = (event.xdata, event.ydata)

        for i, a in enumerate(self.annotation):
            if i < len(liste):
                a.set_text("{0} {1}".format(liste[i], unite[i]))
                a.set_color(couleur[i])
                if i == 0:
                    ymin, ymax = self.axes.get_ylim()
                    a.xytext = (10, 20)
                    a.xy = (absc, ymin)
                else:
                    a.xy = (absc, liste[i])
                a.set_visible(True)
            else:
                a.set_visible(False)

        self.ligne.set_xdata(absc)
        self.ligne.set_visible(True)
        self.canvas.draw()

    def export_csv(self):
        """Export Table to .CSV file"""
        # recupe tab export CSV
        default_name = self.nom.replace(' ', '_').replace(':', '-')
        if int(qVersion()[0]) < 5:  # qt4
            file_name_path = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
                                                         filter="CSV (*.csv *.)")
        else:  # qt5
            file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
                                                            filter="CSV (*.csv *.)")

        if file_name_path:
            file = open(file_name_path, 'w')
            ligne = '# {0} - {1} \n'.format(self.titre, self.nom)
            file.write(ligne + " \n")
            ligne = "# {0} ; ".format(self.type)
            for col in self.columns:
                ligne += "{0} ; ".format(self.variables[col]['nom'])
            file.write(ligne + " \n")

            nbl = len(self.listeTab[0])
            nbc = len(self.listeTab)
            tab1 = np.eye(nbl, nbc).astype(str)
            for j, val in enumerate(self.listeTab):
                for i, v in enumerate(val):
                    if isinstance(v, datetime):
                        v = v.strftime("%Y-%m-%d %H:%M:%S")
                    tab1[i, j] = str(v)
            for j in range(nbl):
                ligne = ""
                for i, val in enumerate(tab1[j, :]):
                    ligne += "{0} ; ".format(val)
                file.write(ligne + " \n")

            file.close()

    def onclick(self, event):
        self.flag = True
        if event.button == 1:
            self.affiche_cadre(event)
            self.fig.canvas.draw()

    def offclick(self, event):
        # self.annotation.set_visible(False)
        for a in self.annotation:
            a.set_visible(False)
        self.ligne.set_visible(False)
        self.flag = False
        self.canvas.draw()

    def onpress(self, event):

        if event.button == 1 and self.flag:
            self.affiche_cadre(event)

    def onpick(self, event):
        legline = event.artist
        if legline in self.lined.keys():
            courbe = self.lined[legline]
            vis = not courbe.get_visible()
            courbe.set_visible(vis)
            if vis:
                legline.set_alpha(1.0)
                if courbe.get_label() == "Flood marks":
                    for e in self.etiquetteLaisses:
                        e.set_visible(True)
            else:
                legline.set_alpha(0.2)
                if courbe.get_label() == "Flood marks":
                    for e in self.etiquetteLaisses:
                        e.set_visible(False)

            self.canvas.draw()

    def maj_liste(self):
        self.date = False
        condition = "run='{0}' AND scenario='{1}'".format(self.run,
                                                          self.scenario)
        temp = self.mdb.select_distinct("date", "resultats", condition, 'date')

        if temp["date"][0]:
            self.date = True
            if self.type == 't':
                self.type = 'date'
        else:
            if self.type == 'date':
                self.type = 't'

        self.liste['date']['abs'] = temp["date"]

        temp = self.mdb.select_distinct("t", "resultats", condition, 't')
        self.liste['t']['abs'] = temp["t"]

        temp = self.mdb.select_distinct('pk', "resultats", condition, 'pk')
        # TODO delete round in future
        self.liste['pk']['abs'] = []
        for elem in temp['pk']:
            if elem is not None:
                self.liste['pk']['abs'].append(round(elem, 2))
        # self.liste['pk']['abs'] = [round(elem, 2) for elem in temp['pk']]
        ss = self.liste['selection']

        if self.type == 'pk':
            self.inv = 't'
            if self.date:
                self.inv = 'date'

            self.position = self.liste[self.inv]['abs'][-1]

            ss['abs'] = []
            for i, x in enumerate(self.liste[self.inv]['abs']):
                if i % 12 == 0 or i == len(self.liste[self.inv]['abs']) - 1:
                    ss['abs'].append(x)

            self.exclutColonnes = ['rdc', 'rdg', 'zmin', 'q2d', 'q2g', 'qmax']

            self.positionLegende = 'upper right'

        else:
            self.inv = 'pk'

            for x in list(ss['abs']):
                if x not in self.liste[self.inv]['abs']:
                    i = ss['abs'].index(x)
                    ss['abs'].pop(i)
                    ss['nom'].pop(i)

            aa = ss['abs']
            ss['nom'] = [ss['nom'][aa.index(a)] for a in sorted(aa)]
            if 'code' in ss.keys():
                ss['code'] = [ss['code'][aa.index(a)] for a in sorted(aa)]
            if 'zero' in ss.keys():
                ss['zero'] = [ss['zero'][aa.index(a)] for a in sorted(aa)]
            aa.sort()

            # self.exclutColonnes = ['rdc', 'rdg', 'zref', 'zmin', 'zmax', 'q2d',
            #                        'q2g', 'qmax']
            self.exclutColonnes = ['rdc', 'rdg', 'zref', 'zmin', 'zmax', 'q2d',
                                   'q2g', 'qmax']
            self.positionLegende = 'upper left'

        if 'nom' in ss.keys() and self.position in ss['abs']:
            pos = ss['abs'].index(self.position)
            self.nom = ss['nom'][pos] + ' - ' + str(self.position)
        else:
            self.nom = str(self.position)
        #
        self.comboTimePK.currentIndexChanged['QString'].disconnect()
        self.comboTimePK.clear()

        for x in self.liste[self.inv]['abs']:
            if isinstance(self.position, float):
                self.comboTimePK.addItem(str(x))
            else:
                self.comboTimePK.addItem('{0:%d/%m/%Y %H:%M}'.format(x))
        try:
            index = self.liste[self.inv]['abs'].index(self.position)
        except ValueError as e:
            self.mgis.add_info('No results for this profile. \n Error : {}'.format(str(e)))

        self.comboTimePK.setCurrentIndex(index)
        self.comboTimePK.currentIndexChanged['QString'].connect(self.combo_time_pk_change)

    def maj_tab(self):
        condition = """run='{0}' AND scenario='{1}' """.format(self.run,
                                                               self.scenario)

        if self.type == "pk":
            condition += """AND branche={}""".format(self.branche)

        if isinstance(self.position, datetime):
            condition += """AND date='{:%Y-%m-%d %H:%M:%S}'""".format(
                self.position)
        else:
            condition += """AND {0}={1}""".format(self.inv, self.position)

        # self.mgis.add_info(condition)
        self.tab = self.mdb.select("resultats", condition, self.type )

        self.listeTab = [self.tab[self.type]]
        for c in self.columns:
            if self.tab[c] != [None] * len(self.tab[c]):
                self.listeTab.append(self.tab[c])
                self.courbeHydro[c].set_data(self.tab[self.type], self.tab[c])
            else:
                self.tab[c] = []
        # gui
        self.remplir_tab(self.listeTab)

    def remplir_tab(self, liste):
        """ Fill items in the table """
        self.tableau.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.tableau.setItem(i, j, QTableWidgetItem(str(v)))

    def maj_graph(self):
        """
        Update graph function
        """
        try :
            comm = self.liste_comm[self.run][self.scenario]
            if comm != '' and comm != None:
                self.ui.label_comments.show()
                self.ui.label2.show()
                self.ui.label_comments.setText(comm)
            else:
                self.ui.label_comments.hide()
                self.ui.label2.hide()
        except:
            self.ui.label_comments.hide()
            self.ui.label2.hide()

        if self.type == 't':
            fin = 'm (Pk)'
        else:
            fin = ''

        self.axes.set_title(r'{0} - {1} {2}'.format(self.titre, self.nom, fin))

        self.axes.set_ylabel(r"{0} ({1})".format(self.var1Name, self.unite))
        # self.axes.set_ylabel(r""+self.var1+" "+self.unite)
        # self.axes.set_ylabel(r"" + self.var1Name + "  "  + self.unite)
        if self.var1 in self.coteVar:
            self.courbeLaisses.set_visible(True)
            for e in self.etiquetteLaisses:
                e.set_visible(True)
        else:
            self.courbeLaisses.set_visible(False)
            for e in self.etiquetteLaisses:
                e.set_visible(False)

        try:
            ss = self.liste['selection']
            i = ss['abs'].index(self.position)
            code = ss['code'][i]
            zero = ss['zero'][i]
            mini = min(self.liste['date']['abs'])
            maxi = max(self.liste['date']['abs'])

            if self.var1 in self.coteVar:
                gg = 'H'
            elif self.var1 in self.debVar:
                gg = 'Q'

            condition = """code = '{0}'
                        AND date>'{1}'
                        AND date<'{2}'
                        AND type='{3}'
                        AND valeur > -99.9""".format(code, mini, maxi, gg)

            self.obs = self.mdb.select("observations", condition, "date")

            if self.obs["valeur"]:
                if self.var1 in self.coteVar:
                    # self.obs['valeur'] = list(map(lambda x: x + zero,
                    #                          self.obs['valeur']))
                    tempo = []
                    for var1 in self.obs['valeur']:
                        tempo.append(var1 + zero)
                    self.obs['valeur'] = tempo

                self.courbeObs.set_data(self.obs['date'], self.obs['valeur'])
                self.courbeObs.set_visible(True)
            else:
                self.courbeObs.set_visible(False)
                self.obs = {}

        except:
            # if self.mgis.DEBUG:
            #     self.mgis.add_info("No observation")
            self.courbeObs.set_visible(False)
            self.obs = {}

        self.canvas.draw()

    def add_courb(self, var):
        """add courbe for visualization"""
        for col in self.columns:
            vv = self.variables[col]
            if self.tab[col] and vv['code'] == var:
                self.colVal.append(col)
                self.courbeHydro[col].set_visible(True)
                self.courbeHydro[col].set_label(vv['nom'])
                self.courbeHydro[col].set_color(vv['couleur'])
            else:
                self.courbeHydro[col].set_visible(False)

        self.courbes = [self.courbeHydro[col] for col in self.colVal]

    def maj_legende(self):
        self.colVal = []
        if self.var1 in self.coteVar:
            for var in self.coteVar:
                self.add_courb(var)
        elif self.var1 in self.debVar:
            for var in self.debVar:
                self.add_courb(var)
        else:
            self.add_courb(self.var1)

        if self.obs:
            self.courbes.append(self.courbeObs)
        handles = [c for c in self.courbes]
        if self.var1 in self.coteVar:
            handles.append(mlines.Line2D([], [], color='darkcyan', marker='+',
                                         linewidth=0,
                                         markersize=10, label='Flood marks'))
            self.courbes.append(self.courbeLaisses)
        else:
            self.courbeLaisses.set_visible(False)
            for e in self.etiquetteLaisses:
                e.set_visible(False)
        liste_noms = [c.get_label() for c in self.courbes]

        self.leg = self.axes.legend(handles, liste_noms,
                                    loc=self.positionLegende,
                                    fancybox=False,
                                    shadow=False,
                                    fontsize="small")
        self.leg.get_frame().set_alpha(0.4)

        self.lined = dict()
        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            # size selection zone
            legline.set_picker(5)
            legline.set_linewidth(3)
            legline.set_alpha(1.0)
            legline.set_visible(True)
            self.lined[legline] = courbe
            courbe.set_visible(True)

            for col in self.variables.keys():
                nom = self.variables[col]['nom']
                if nom == courbe.get_label() and col in self.exclutColonnes:
                    legline.set_alpha(0.2)
                    legline.set_visible(True)
                    courbe.set_visible(False)
        # rend deplacable la legende mais fonctionne mal avec le choix des ligne dans la légende
        self.leg.draggable(True)

    def maj_limites(self):
        mini_x = min(self.tab[self.type])
        maxi_x = max(self.tab[self.type])
        mini_y = None
        maxi_y = None
        self.axes.set_xlim(mini_x, maxi_x)

        if isinstance(mini_x, datetime):
            date = mdates.DateFormatter('%d/%m/%Y')
        else:
            date = FormatStrFormatter('%d')
        self.axes.xaxis.set_major_formatter(date)

        marge = 0.05

        col_visibles = []
        for col in self.colVal:
            if self.courbeHydro[col].get_visible():
                col_visibles.append(col)

        temp = [min(self.tab[c]) for c in col_visibles if self.tab[c]]

        if temp:
            mini_y = min(temp)

        temp = [max(self.tab[c]) for c in col_visibles if self.tab[c]]

        if temp:
            maxi_y = max(temp)

        if mini_y is not None and maxi_y is not None:
            if self.obs and self.obs['valeur']:
                mini_y = min(min(self.obs['valeur']), mini_y)
                maxi_y = max(max(self.obs['valeur']), maxi_y)

            diff = maxi_y - mini_y
            self.axes.set_ylim(mini_y - diff * marge, maxi_y + diff * marge)

        self.canvas.draw()

    def maj_laisses(self):
        self.courbeLaisses.set_visible(False)
        self.courbeLaisses = self.axes.scatter([], [], label="Flood marks")
        for e in self.etiquetteLaisses:
            self.axes.texts.remove(e)
        self.etiquetteLaisses = []

        condition = "event = '{}'".format(self.scenario)
        self.laisses = self.mdb.select("flood_marks", condition, "abscissa")

        self.laisses['pk'] = self.laisses['abscissa']
        lai = self.laisses
        if self.type not in lai.keys():
            return
        xx = [v for v in lai[self.type] if v]
        if not xx:
            return

        zz = [v for i, v in enumerate(lai['z']) if lai[self.type][i]]
        if isinstance(xx[0], date):
            return
        if self.tab["zmax"]:
            couleurs = []
            taille = []
            for x, z in zip(xx, zz):
                val = interpole(x, self.tab["pk"], self.tab["zmax"])
                if val:
                    diff = z - val
                    if diff < 0:
                        couleurs.append("purple")
                    else:
                        couleurs.append("green")

                    if abs(diff) > 0.2:
                        taille.append(3)
                    elif abs(diff) > 0.1:
                        taille.append(2)
                    else:
                        taille.append(1)

                else:
                    couleurs.append("black")
                    taille.append(1)
        else:
            couleurs = ["black"] * len(xx)
            taille = [1] * len(xx)

        self.courbeLaisses = self.axes.scatter(xx, zz,
                                               color=couleurs,
                                               marker='+',
                                               label="Flood marks",
                                               s=80,
                                               linewidth=taille)

        self.courbeLaisses.set_visible(True)
        # self.courbeLaisses.set_color(couleurs)
        for x, z, c in zip(xx, zz, couleurs):
            temp = self.axes.annotate(str(z), xy=(x, z), xytext=(3, 3),
                                      ha='left', va='bottom',
                                      fontsize='x-small',
                                      color=c,
                                      textcoords='offset points')

            self.etiquetteLaisses.append(temp)

            # except :
            # return

    def combo_time_pk_change(self, text):
        if isinstance(self.position, float):
            self.position = float(text)
        else:
            self.position = datetime.strptime(text, '%d/%m/%Y %H:%M')
        self.maj_tab()
        self.maj_graph()
        if self.type != "pk":
            self.maj_limites()
            #

    def combo_run_changed(self, text):
        self.run = text
        if self.scenario not in self.listeRuns[self.run]:
            self.scenario = self.listeRuns[self.run][-1]
        self.comboScen.currentIndexChanged['QString'].disconnect()
        self.comboScen.clear()
        self.comboScen.addItems(self.listeRuns[self.run])
        self.comboScen.setCurrentIndex(self.listeRuns[self.run].index(
            self.scenario))
        self.comboScen.currentIndexChanged['QString'].connect(
            self.combo_scen_changed)

        self.maj_liste()
        self.maj_tab()
        self.maj_laisses()
        self.maj_graph()
        if self.type != "pk":
            self.maj_limites()
            #

    def combo_scen_changed(self, text):
        self.scenario = text
        self.maj_liste()
        self.maj_tab()
        self.maj_laisses()
        self.maj_graph()
        if self.type != "pk":
            self.maj_limites()
            #

    def combo_var1_changed(self, text):

        if text == 'Levels':
            self.unite = 'm'
            self.var1Name = 'Z'
            self.var1 = 'Z'
        elif text == 'Flow rates':
            self.unite = r'$m^3/s$'
            self.var1Name = 'Q'
            self.var1 = 'Q'
        else:
            for col in self.columns:
                if self.variables[col]['nom'] == text:
                    self.var1 = self.variables[col]['code']
                    self.unite = self.variables[col]['unite']
                    self.var1Name = text
                    break
        self.maj_legende()
        self.maj_graph()
        self.maj_limites()

    def avance(self, val):
        # TODO
        if abs(val) == 10:
            var = 'selection'
            val = int(val / 10)
        else:
            var = self.inv

        ss = self.liste['selection']
        if self.position not in self.liste[var]['abs']:
            pos = self.position
            i = self.liste[self.inv]['abs'].index(pos)
            n = self.liste[self.inv]['abs']

            while 0 < i < len(n) and pos not in ss['abs']:
                i -= val
                pos = self.liste[self.inv]['abs'][i]

            if i == len(self.liste[self.inv]['abs']):
                i = -1
            self.position = self.liste[self.inv]['abs'][i]

        pos = self.liste[var]['abs'].index(self.position)
        pos += val
        if len(self.liste[var]['abs']) > pos >= 0:
            self.position = self.liste[var]['abs'][pos]
            if 'nom' in ss.keys() and self.position in ss['abs']:
                i = ss['abs'].index(self.position)
                self.nom = ss['nom'][i] + ' - ' + str(self.position)
            else:
                self.nom = str(self.position)
            index = self.liste[self.inv]['abs'].index(self.position)
            self.comboTimePK.setCurrentIndex(index)
            self.maj_limites()


"""---------------------------------------------------------------------------------
        Classe de gestion du graphique pour les casiers et les liaisons 
------------------------------------------------------------------------------------"""


# ___________________________________________________________________________________________________________________________________________________________________________________________
class GraphBasin(GraphCommon):
    def __init__(self, feature, mgis, select, position, type):
        # feature, selection, position, type, main
        GraphCommon.__init__(self, mgis)
        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphBasin.ui'), self)

        self.feature = feature
        self.position = position
        self.select = select
        self.type = type
        self.combo_run = self.ui.comboBox_State
        self.combo_scen = self.ui.comboBox_Scenar
        self.combo_time_pk = self.ui.comboBox_time
        self.combo_var1 = self.ui.comboBox_var1
        # insert graphic and toolsbars of graphic
        self.gui_graph(self.ui)

        self.init_ui()

        # Action
        self.ui.actionBt_reculTot.triggered.connect(lambda: self.avance(-10))
        self.ui.actionBt_recul.triggered.connect(lambda: self.avance(-1))
        self.ui.actionBt_av.triggered.connect(lambda: self.avance(1))
        self.ui.actionBt_avTot.triggered.connect(lambda: self.avance(10))
        #
        #
        self.ui.actionBt_exportCSV.triggered.connect(self.export_csv)
        self.combo_run.currentIndexChanged['QString'].connect(self.combo_run_changed)
        self.combo_scen.currentIndexChanged['QString'].connect(self.combo_scen_changed)
        self.combo_var1.currentIndexChanged['QString'].connect(self.combo_var1_changed)
        self.combo_time_pk.currentIndexChanged['QString'].connect(self.combo_time_p_k_change)

    #
    def init_ui(self):

        if self.type == 'basins':
            self.titre = 'Basin '
            self.basin = self.feature["basinnum"]
        else:
            self.titre = 'Link '
            self.link = self.feature["linknum"]

        self.liste = {'selection': self.select, 't': {}, 'date': {}}

        self.temps = 'max'
        self.variables = self.mgis.variables

        self.flag = False

        dico_run = self.mdb.select_distinct("date, run, scenario",
                                            "runs")

        if not dico_run:
            self.mgis.add_info("No simulation to show")
            return False
        self.liste_runs = {}
        for run, scen in zip(dico_run["run"], dico_run["scenario"]):
            if not run in self.liste_runs.keys():
                self.liste_runs[run] = []
            # Exclusion des scenarios en régime permanent pour lesquels il n'y a pas de calcul casier
            if scen[len(scen) - 5:] != '_init':
                self.liste_runs[run].append(scen)

        self.run = sorted(self.liste_runs.keys())[-1]

        self.scenario = self.liste_runs[self.run][-1]

        self.combo_run.clear()
        self.combo_run.addItems(sorted(self.liste_runs.keys()))
        le = len(self.liste_runs.keys())
        self.combo_run.setCurrentIndex(le - 1)

        self.combo_scen.clear()
        self.combo_scen.addItems(self.liste_runs[self.run])
        le = len(self.liste_runs[self.run])
        self.combo_scen.setCurrentIndex(le - 1)

        self.combo_time_pk.clear()

        if self.type == 'basins':
            self.columns = ['zcas', 'surcas', 'volcas']
        else:
            self.columns = ['qech', 'vech']

        self.colVal = []
        self.unite = ""

        # Initialisation sur la 1ere colonne
        self.var1 = self.variables[self.columns[0]]['code']
        self.unite = self.variables[self.columns[0]]['unite']
        self.var1_name = self.variables[self.columns[0]]['nom']
        self.colVal.append(self.columns[0])
        liste_nom = ['t']
        # default value
        liste_g = []
        for col in self.columns:
            liste_nom.append(self.variables[col]['nom'])
            codd = self.variables[col]['code']
            var = self.variables[col]['nom']
            if not var in liste_g:
                liste_g.append(var)

        # creation tableau
        self.tableau = self.ui.tableWidget_RES
        self.tableau.setColumnCount(len(liste_nom))
        self.tableau.setRowCount(0)
        self.tableau.setHorizontalHeaderLabels(liste_nom)
        self.tableau.addAction(CopySelectedCellsAction(self.tableau))

        self.combo_var1.clear()
        self.combo_var1.addItems(liste_g)

        # Figure
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel('Time (s)')
        self.axes.grid(True)
        self.axes.set_ylabel("{0} ({1})".format(self.var1_name, self.unite))

        self.courbe_hydro = {}

        for i, col in enumerate(self.columns):
            couleur = self.variables[col]['couleur']
            temp, = self.axes.plot([], [], zorder=100, color=couleur)
            self.courbe_hydro[col] = temp

        self.maj_liste()
        self.maj_tab()
        self.maj_legende()
        self.maj_graph()
        self.maj_limites()

        self.fig.tight_layout()
        self.fig.patch.set_facecolor((0.94, 0.94, 0.94))
        self.fig.canvas.mpl_connect('pick_event', self.onpick)

        self.annotation = []
        box = dict(boxstyle='round,pad=0.5', fc='white', alpha=0.7)
        txtcoord = 'offset points'
        for i in range(10):
            self.annotation.append(self.axes.annotate("",
                                                      xy=(0, 0),
                                                      ha='left',
                                                      xytext=(10, 0),
                                                      textcoords=txtcoord,
                                                      va='top',
                                                      bbox=box,
                                                      visible=False,
                                                      zorder=110))
        self.ligne = self.axes.axvline(color="black")

        self.rect = self.axes.add_patch(patches.Rectangle((0, 0), 0, 0,
                                                          zorder=101,
                                                          color='white',
                                                          alpha=0.8))

        self.clic = self.fig.canvas.mpl_connect('button_press_event',
                                                self.onclick)
        self.declic = self.fig.canvas.mpl_connect('button_release_event',
                                                  self.offclick)
        self.motion = self.fig.canvas.mpl_connect('motion_notify_event',
                                                  self.onpress)
        return True

    def affiche_cadre(self, event):
        flag = True
        for c in self.toolbar.findChildren(QToolButton):
            if c.isChecked():
                flag = False
                break

        if not flag or not event.xdata or not event.ydata:
            for a in self.annotation:
                a.set_visible(False)
            self.ligne.set_visible(False)
            self.canvas.draw()
            return

        liste = []
        unite = []
        couleur = []

        if self.type == 'date':
            temp = round((event.xdata - 719163) * 24) * 3600
            decal = datetime.utcfromtimestamp(temp)
            absc = min(self.tab[self.type], key=lambda x: abs(x - decal))
        else:
            absc = min(self.tab[self.type], key=lambda x: abs(x - event.xdata))

        liste.append(absc)
        unite.append("")
        couleur.append('black')

        for col in self.colVal:
            if self.tab[col] and self.courbe_hydro[col].get_visible():
                index = self.tab[self.type].index(absc)
                val = self.tab[col][index]
                nom = self.variables[col]['nom']
                liste.append(val)
                unite.append(self.variables[col]['unite'])
                couleur.append(self.variables[col]['couleur'])

        for i, a in enumerate(self.annotation):
            if i < len(liste):
                a.set_text("{0} {1}".format(liste[i], unite[i]))
                a.set_color(couleur[i])
                if i == 0:
                    ymin, ymax = self.axes.get_ylim()
                    a.xytext = (10, 20)
                    a.xy = (absc, ymin)
                else:
                    a.xy = (absc, liste[i])
                a.set_visible(True)
            else:
                a.set_visible(False)

        self.ligne.set_xdata(absc)
        self.ligne.set_visible(True)
        self.canvas.draw()

    def export_csv(self):
        """Export Table to .CSV file"""
        # recupe tab export CSV
        default_name = self.nom.replace(' ', '_').replace(':', '-')
        if int(qVersion()[0]) < 5:  # qt4
            file_name_path = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
                                                         filter="CSV (*.csv *.)")
        else:  # qt5
            file_name_path, _ = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(default_name),
                                                            filter="CSV (*.csv *.)")

        if file_name_path:
            file = open(file_name_path, 'w')
            ligne = '# {0} - {1} \n'.format(self.titre, self.nom)
            file.write(ligne + " \n")
            ligne = "# {0} ; ".format('date')
            for col in self.columns:
                ligne += "{0} ; ".format(self.variables[col]['nom'])
            file.write(ligne + " \n")

            nbl = len(self.liste_tab[0])  # nombre de pas de temps

            # Boucle sur les pas de temps
            for j in range(nbl):
                ligne = ""
                # Boucle sur les colonnes de variables BZ, BArea, BVol pour casier et LQ,LVEL pour liaisons
                for i, val in enumerate(self.liste_tab):
                    if isinstance(val[j], datetime):
                        valj = val[j].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        valj = val[j]
                    ligne += "{0} ; ".format(str(valj))
                file.write(ligne + " \n")

            file.close()

    def onclick(self, event):
        self.flag = True
        if event.button == 1:
            self.affiche_cadre(event)
            self.fig.canvas.draw()

    def offclick(self, event):
        for a in self.annotation:
            a.set_visible(False)
        self.ligne.set_visible(False)
        self.flag = False
        self.canvas.draw()

    def onpress(self, event):

        if event.button == 1 and self.flag:
            self.affiche_cadre(event)

    def onpick(self, event):
        legline = event.artist
        if legline in self.lined.keys():
            courbe = self.lined[legline]
            vis = not courbe.get_visible()
            courbe.set_visible(vis)
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)

            self.canvas.draw()

    def maj_liste(self):
        self.date = False
        condition = "run='{0}' AND scenario='{1}'".format(self.run,
                                                          self.scenario)
        if self.type == 'basins':
            temp = self.mdb.select_distinct("date", "resultats_basin", condition, 'date')
        else:
            temp = self.mdb.select_distinct("date", "resultats_links", condition, 'date')

        self.liste['date']['abs'] = temp["date"]
        self.position_legende = 'upper left'
        self.nom = str(self.position)

        self.combo_time_pk.currentIndexChanged['QString'].disconnect()
        self.combo_time_pk.clear()

        for x in self.liste['selection']['nom']:
            self.combo_time_pk.addItem(str(x))

        try:
            index = self.liste['selection']['nom'].index(self.position)
        except ValueError as e:
            self.mgis.add_info('No results for this profile. \n Error : {}'.format(str(e)))

        self.combo_time_pk.setCurrentIndex(index)
        self.combo_time_pk.currentIndexChanged['QString'].connect(self.combo_time_p_k_change)

    def maj_tab(self):
        condition = """run='{0}' AND scenario='{1}' """.format(self.run,
                                                               self.scenario)

        index = self.liste['selection']['nom'].index(self.position)
        numero = self.liste['selection']['num'][index]
        # Cette operation car Mascaret renvoie les numeros de casiers, il ignore les noms
        if self.type == 'basins':
            condition += """AND {0}={1}""".format('bnum', numero)
        else:
            condition += """AND {0}={1}""".format('lnum', numero)

        # self.mgis.add_info(condition)
        if self.type == 'basins':
            self.tab = self.mdb.select("resultats_basin", condition, "t")

        else:
            self.tab = self.mdb.select("resultats_links", condition, "t")

        # Alimentation de la colonne des dates dans le tableau
        self.liste_tab = [self.tab['date']]
        for c in self.columns:
            if self.tab[c] != [None] * len(self.tab[c]):
                self.liste_tab.append(self.tab[c])
                # Valeurs en milliers pour barea et bvol passees dans les courbes
                #  pour ameliorer la visibilite des graphes
                if c == 'surcas' or c == 'volcas':
                    self.courbe_hydro[c].set_data(self.tab['date'], [valeur / 1000 for valeur in self.tab[c]])
                else:
                    self.courbe_hydro[c].set_data(self.tab['date'], self.tab[c])
            else:
                self.tab[c] = []
        # gui
        self.remplir_tab(self.liste_tab)

    def remplir_tab(self, liste):
        """ Fill items in the table """
        self.tableau.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.tableau.setItem(i, j, QTableWidgetItem(str(v)))

    def maj_graph(self):

        self.axes.set_title(r'{0} - {1}'.format(self.titre, self.nom))
        self.axes.set_ylabel(r"{0} ({1})".format(self.var1_name, self.unite))

        mini = min(self.liste['date']['abs'])
        maxi = max(self.liste['date']['abs'])

        self.canvas.draw()

    def add_courb(self, var):
        """add courbe for visualization"""
        for col in self.columns:
            vv = self.variables[col]
            if self.tab[col] and vv['code'] == var:
                self.colVal.append(col)
                self.courbe_hydro[col].set_visible(True)
                self.courbe_hydro[col].set_label(vv['nom'])
                self.courbe_hydro[col].set_color(vv['couleur'])
            else:
                self.courbe_hydro[col].set_visible(False)

        self.courbes = [self.courbe_hydro[col] for col in self.colVal]

    def maj_legende(self):
        self.colVal = []
        self.add_courb(self.var1)

        handles = [c for c in self.courbes]

        liste_noms = [c.get_label() for c in self.courbes]

        self.leg = self.axes.legend(handles, liste_noms,
                                    loc=self.position_legende,
                                    fancybox=False,
                                    shadow=False,
                                    fontsize="small")
        self.leg.get_frame().set_alpha(0.4)

        self.lined = dict()
        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(5)
            legline.set_linewidth(3)
            legline.set_alpha(1.0)
            legline.set_visible(True)
            self.lined[legline] = courbe
            courbe.set_visible(True)

        # rend deplacable la legende mais fonctionne mal avec le choix des ligne dans la légende
        self.leg.draggable(True)

    def maj_limites(self):
        if self.tab['date']:
            mini_x = min(self.tab['date'])
            maxi_x = max(self.tab['date'])
        else:
            mini_x = None
            maxi_x = None
        mini_y = None
        maxi_y = None
        self.axes.set_xlim(mini_x, maxi_x)

        if isinstance(mini_x, datetime):
            date = mdates.DateFormatter('%d/%m/%Y')
        else:
            date = FormatStrFormatter('%d')
        self.axes.xaxis.set_major_formatter(date)

        marge = 0.05

        col_visibles = []
        for col in self.colVal:
            if self.courbe_hydro[col].get_visible():
                col_visibles.append(col)

        # Recherche de la valeur mini sur les valeurs de la courbe et non du tableau, [1] pour les valeurs en ordonnees
        temp = [min(self.courbe_hydro[c].get_data()[1]) for c in col_visibles if self.courbe_hydro[c].get_data()]
        if temp:
            mini_y = min(temp)

        # Recherche de la valeur maxi sur les valeurs de la courbe et non du tableau, [1] pour les valeurs en ordonnees
        temp = [max(self.courbe_hydro[c].get_data()[1]) for c in col_visibles if self.courbe_hydro[c].get_data()]
        if temp:
            maxi_y = max(temp)

        # Cas special: si la surface du casier est constante, pour eviter une anomalie d'echelle
        if mini_y == maxi_y:
            mini_y = 0

        if mini_y is not None and maxi_y is not None:
            diff = maxi_y - mini_y
            self.axes.set_ylim(mini_y - diff * marge, maxi_y + diff * marge)

        self.canvas.draw()

    def combo_time_p_k_change(self, text):
        self.position = text
        self.nom = self.position
        self.maj_tab()
        self.maj_graph()
        self.maj_limites()

    def combo_run_changed(self, text):
        self.run = text
        if not self.scenario in self.liste_runs[self.run]:
            self.scenario = self.liste_runs[self.run][-1]
        self.combo_scen.currentIndexChanged['QString'].disconnect()
        self.combo_scen.clear()
        self.combo_scen.addItems(self.liste_runs[self.run])
        self.combo_scen.setCurrentIndex(self.liste_runs[self.run].index(
            self.scenario))
        self.combo_scen.currentIndexChanged['QString'].connect(
            self.combo_scen_changed)

        self.maj_liste()
        self.maj_tab()
        self.maj_graph()
        self.maj_limites()

    def combo_scen_changed(self, text):
        self.scenario = text
        self.maj_liste()
        self.maj_tab()
        self.maj_graph()
        self.maj_limites()

    def combo_var1_changed(self, text):
        for col in self.columns:
            if self.variables[col]['nom'] == text:
                self.var1 = self.variables[col]['code']
                self.unite = self.variables[col]['unite']
                self.var1_name = text
                break
        self.maj_legende()
        self.maj_graph()
        self.maj_limites()

    def avance(self, val):
        # TODO
        if abs(val) == 10:
            # var = 'selection'
            val = int(val / 10)
        # else:
        #    var = self.inv

        ss = self.liste['selection']

        pos = self.liste['selection']['nom'].index(self.position)
        pos += val
        if pos < len(self.liste['selection']['nom']) and pos >= 0:
            self.position = self.liste['selection']['nom'][pos]
            self.nom = self.position
            index = self.liste['selection']['nom'].index(self.position)
            self.combo_time_pk.setCurrentIndex(index)
            self.maj_limites()
