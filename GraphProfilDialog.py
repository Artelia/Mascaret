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
from .GraphCommon import DraggableLegend, GraphCommon
from .Structure.StructureCreateDialog import ClassStructureCreateDialog
from .GraphResultDialog import GraphResultDialog

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
                      "(SELECT id FROM {0}.results_var WHERE type_res ='{1}' )".format(self.mgis.mdb.SCHEMA, type_res)

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
                graph_p.exec_()
            # else:
            #     if self.mgis.DEBUG:
            #         self.mgis.add_info("Visu_profil: Not layer")
            if couche == 'profiles' and flag_profil_r:
                self.mgis.coucheProfils = results[0].mLayer
                prof_a = self.mgis.mdb.select_distinct("name", "profiles", "active")
                if results[0].mFeature['name'] in prof_a['name']:
                    graph_res = GraphResultDialog(self.mgis, "hydro_profil", results[0].mFeature["abscissa"])

                    graph_res.show()
                else:
                    self.mgis.add_info('no active profiles')
            # #
            if flag_hydro and couche in ('profiles', 'outputs'):
                feature = results[0].mFeature

                prof_a = self.mgis.mdb.select_distinct("name,abscissa", "profiles", "active")

                if feature['name'] in prof_a['name'] or feature['abscissa'] in prof_a['abscissa']:
                    graph_hyd = GraphResultDialog(self.mgis, "hydro", feature['abscissa'])
                    graph_hyd.show()
                else:
                    self.mgis.add_info('no active profiles')

            if flag_hydro and couche == 'branchs':
                feature = results[0].mFeature
                # chaine='Branche ' + str(feature['branche'])
                branches = self.mgis.mdb.select_distinct("branch", "branchs", "active")
                if feature['branch'] in branches['branch']:
                    graph_hyd_pk = GraphResultDialog(self.mgis, "hydro_pk", feature['branch'])
                    graph_hyd_pk.show()
                else:
                    self.mgis.add_info('no active branch')

            if flag_casier_r and couche in ('basins', 'links'):
                feature = results[0].mFeature

                if couche == 'links':
                    links = self.mgis.mdb.select_distinct("name", "links", "active")
                    if feature['name'] in links['name']:
                        graph_link = GraphResultDialog(self.mgis, "hydro_link", feature["linknum"])
                        graph_link.show()
                else:

                    basins = self.mgis.mdb.select_distinct("name", "basins", "active")
                    if feature['name'] in basins['name']:
                        graph_basin = GraphResultDialog(self.mgis, "hydro_basin", feature["basinnum"])
                        graph_basin.show()

        return


class GraphProfil(GraphCommon):
    """class Dialog graphProfil"""

    def __init__(self, gid, mgis=None):
        GraphCommon.__init__(self, mgis)

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphProfil.ui'), self)
        self.init_ui_prof(gid)
        self.gui_graph(self.ui.widget_figure)
        self.fig.autofmt_xdate()
        self.init_ui()

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
                        interp = f.geometry().interpolate(x)
                        if interp.isNull():
                            self.mgis.add_info("Warning : Check the profil lenght")
                        p = interp.asPoint()
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

                            if ligne[0] != '#':
                                ligne = ligne.replace('\n', '')
                                if len(ligne.split(sep)) < 1:
                                    break
                                x, z = (float(var) for var in ligne.split(sep))

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
