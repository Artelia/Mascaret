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

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtCore import *

if int(qVersion()[0])<5:   #qt4

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
else: #qt4
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


from . import function as fct

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
# **************************************************
try:
    _encoding = QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

import matplotlib.dates as mdates
from matplotlib.widgets import RectangleSelector, SpanSelector, Cursor
from matplotlib.ticker import FormatStrFormatter
# MOD!
# import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.image as mpimg
# MOD!
import matplotlib.colors as colors
import matplotlib.lines as mlines

from matplotlib import gridspec, patches

from datetime import datetime

import numpy as np

import sys, os



class IdentifyFeatureTool(QgsMapToolIdentify):
    def __init__(self, main):
        self.mgis = main
        self.canvas = self.mgis.iface.mapCanvas()
        self.graphP = False
        self.gid = None
        QgsMapToolIdentify.__init__(self, self.canvas)

    def canvasReleaseEvent(self, mouseEvent):

        results = self.identify(mouseEvent.x(), mouseEvent.y(),
                                self.TopDownStopAtFirst, self.VectorLayer)

        if len(results) > 0:
            couche = results[0].mLayer.name()
            # self.mgis.addInfo('couche {0}'.format(couche))

            flagHydro = self.mgis.hydrogramme
            flagProfil = self.mgis.profil
            flagProfilR = self.mgis.profilResult
            # self.mgis.addInfo("flagHydro: {0} \n flagProfil: {1} \n flagProfilR: {2} \n".format(flagHydro,flagProfil,flagProfilR))
            if couche == 'profiles' and flagProfil:
                self.mgis.coucheProfils = results[0].mLayer
                gid = results[0].mFeature["gid"]
                graphP = GraphProfil(gid, self.mgis)
                graphP.exec_()
            # else:
            #     if self.mgis.DEBUG:
            #         self.mgis.addInfo("Visu_profil: Not layer")
            if couche == 'profiles' and flagProfilR:
                self.mgis.coucheProfils = results[0].mLayer
                gid = results[0].mFeature["gid"]
                graphRes = GraphProfilRes(gid, self.mgis)
                graphRes.exec_()

            # #
            if flagHydro and couche in ('profiles', 'outputs'):
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
                # self.mgis.addInfo('graph {0}'.format(couche))
                graphHyd = GraphHydro(feature, self.mgis, selection, feature['abscissa'], 't')
                graphHyd.exec_()

            if flagHydro and couche == 'branchs':
                feature = results[0].mFeature
                # chaine='Branche ' + str(feature['branche'])
                graphHyd = GraphHydro(feature, self.mgis, {}, '', 'pk')
                graphHyd.exec_()
        return


class GraphCommon(QDialog):
    def __init__(self, mgis=None):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.dossierPlugin = self.mgis.masplugPath
        self.dossierProjet = self.mgis.repProject
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)


    def initUI_common_P(self, gid):
        """variables in common for profile graphics"""
        self.gid = gid
        self.coucheProfils = self.mgis.coucheProfils
        # try:
        self.liste = self.mdb.select("profiles", "", "abscissa")
        # except:
        #     self.mgis.addInfo("Error Select profils")

        self.position = self.liste["gid"].index(self.gid)
        self.feature = {k: v[self.position] for k, v in self.liste.items()}
        self.nom = self.feature['name']

        self.courbes = []

    def GUI_graph(self,ui):

        self.verticalLayout_99 = QVBoxLayout(ui.widget_figure)
        self.verticalLayout_99.setObjectName(_fromUtf8("verticalLayout_99"))
        self.verticalLayout_99.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.verticalLayout_98 = QVBoxLayout(ui.widget_toolsbar)
        self.verticalLayout_98.setObjectName(_fromUtf8("verticalLayout_98"))
        self.verticalLayout_98.addWidget(self.toolbar)


class GraphProfil(GraphCommon):
    """class Dialog graphProfil"""

    def __init__(self, gid, mgis=None):
        GraphCommon.__init__(self, mgis)

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, 'ui/graphProfil.ui'), self)
        self.initUI_common_P(gid)
        self.GUI_graph(self.ui)
        self.initUI()

        # self.plot()
        # action


        self.ui.actionBtTools_point_selection.triggered.connect(self.selectorToggled)
        self.ui.actionBtTools_zone_selection.triggered.connect(self.zoneSelectorToggled)
        self.ui.actionBtTools_profil_translation.triggered.connect(self.deplaceToggled)

        self.ui.actionBt_add_point.triggered.connect(self.ajoutPoints)
        self.ui.actionBt_topo_load.triggered.connect(self.importTopo)
        self.ui.actionBt_topo_del.triggered.connect(self.delTopo)
        # self.ui.actionBt_img_load.triggered.connect(self.importImage)
        self.ui.actionBt_topo_save.triggered.connect(self.sauveTopo)

        self.ui.actionBt_reculTot.triggered.connect(lambda: self.avance(-10))
        self.ui.actionBt_recul.triggered.connect(lambda: self.avance(-1))
        self.ui.actionBt_av.triggered.connect(lambda: self.avance(1))
        self.ui.actionBt_avTot.triggered.connect(lambda: self.avance(10))
        self.ui.actionBt_profil_save.triggered.connect(self.sauveProfil)
        self.ui.actionBt_profil_filter.triggered.connect(self.filtre)
        self.ui.actionBt_profil_del.triggered.connect(self.effaceProfil)
        self.ui.actionBt_minor_bed.triggered.connect(self.selectLitMineur)
        self.ui.actionBt_r_stok.triggered.connect(lambda: self.selectStock("rightstock"))
        self.ui.actionBt_l_stok.triggered.connect(lambda: self.selectStock("leftstock"))

    def initUI(self):

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
        self.tableau.selectionModel().selectionChanged.connect(self.selectChanged)
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
        self.span = SpanSelector(self.axes, self.onselectZone, 'horizontal',
                                 rectprops=dict(alpha=0, facecolor='yellow'),
                                 onmove_callback=self.onselectZone,
                                 useblit=False)

        self.span.visible = False

        self.curseur = Cursor(self.axes, useblit=True, color="red")
        self.curseur.visible = False

        # figure suite
        # self.extraitMNT()
        # self.fichierDecalage()
        self.extraitProfil()
        self.extraitTopo()
        self.majGraph()
        self.majLegende()
        self.majLimites()
        self.fig.tight_layout()
        self.fig.patch.set_facecolor((0.94, 0.94, 0.94))
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('button_release_event', self.onrelease)
        self.fig.canvas.mpl_connect('motion_notify_event', self.onpress)
        # zoom_fun = zoom mollette
        # self.fig.canvas.mpl_connect('scroll_event', self.zoom_fun)


    def selectorToggled(self):
        """Point selection function"""
        if self.bt_select.isChecked():
            self.RS.set_active(True)
            self.ui.bt_add_point.setEnabled(True)
            self.bt_select_z.setChecked(False)
            self.bt_transla.setChecked(False)

        else:
            self.ui.bt_add_point.setDisabled(True)
            self.RS.set_active(False)

    def zoneSelectorToggled(self, checked):
        """zone selection function"""
        if self.bt_select_z.isChecked():
            self.span.visible = True
            self.bt_select.setChecked(False)
            self.bt_transla.setChecked(False)
        else:
            self.span.visible = False

    def deplaceToggled(self, checked):
        """Translation function"""
        if self.bt_transla.isChecked():
            self.bt_select.setChecked(False)
            self.bt_select_z.setChecked(False)

    def avance(self, val):
        """next or back profiles """
        if self.image:
            self.image.set_visible(False)
        self.rectSelection.set_visible(False)
        self.selected = {}
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

        self.extraitProfil()
        self.extraitTopo()
        self.majGraph()
        self.majLimites()
        self.majLegende()

    def extraitMNT(self):
        self.mnt = {'x': [], 'z': []}

        condition = "idprofil={0}".format(self.gid)
        requete = self.mdb.select("mnt", condition)
        if "x" in requete.keys() and "z" in requete.keys():
            # self.mnt['x'] = list(map(float, requete["x"][0].split()))
            # self.mnt['z'] = list(map(float, requete["z"][0].split()))
            self.mnt['x']=[float(var) for var in requete["x"][0].split()]
            self.mnt['z']=[float(var) for var in requete["z"][0].split()]

    def extraitProfil(self):

        self.tab = {'x': [], 'z': []}
        # liste = ["litmingauc", "litmindroi", "stockgauch", 'stockdroit']
        liste = ["leftminbed", "rightminbed", "leftstock", 'rightstock']
        for l in liste:
            self.tab[l] = None
        self.mnt = {'x': [], 'z': []}

        if self.feature["x"] and self.feature["z"]:
            # self.tab['x'] = list(map(float, self.feature["x"].split()))
            # self.tab['z'] = list(map(float, self.feature["z"].split()))
            self.tab['x']=[float(var) for var in self.feature["x"].split()]
            self.tab['z']=[float(var) for var in self.feature["z"].split()]

            mini = min(self.tab['x'])
            maxi = max(self.tab['x'])
            for l in liste:
                val = self.feature[l]
                if val and val > mini and val < maxi:
                    self.tab[l] = val

        if self.feature["xmnt"] and self.feature["zmnt"]:
            self.mnt['x']=[float(var) for var in self.feature["xmnt"].split()]
            self.mnt['z']=[float(var) for var in self.feature["zmnt"].split()]
            # self.mnt['x'] = list(map(float, self.feature["xmnt"].split()))
            # self.mnt['z'] = list(map(float, self.feature["zmnt"].split()))

    def extraitTopo(self):

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
            if not nom in self.topo.keys():
                self.topo[nom] = {'x': [], 'z': [], 'ordre': [], 'gid': []}

            if not x:
                x = round(self.mdb.projection(gid, nom), 2)
            if not ordre:
                ordre = i + 1000
            self.topo[nom]['x'].append(x)
            self.topo[nom]['z'].append(round(z, 2))
            self.topo[nom]['gid'].append(gid)
            self.topo[nom]['ordre'].append(ordre)

            # self.mgis.addInfo('self.topo.keys()  {}'.format(self.topo.keys()))

    def remplirTab(self, liste):
        """ Fill items in the table"""
        # self.tableau.rempit(Liste)
        self.tableau.itemChanged.disconnect()
        self.tableau.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.tableau.setItem(i, j, QTableWidgetItem(str(v)))
        self.tableau.itemChanged.connect(self.modifie)

    def colorieTab(self, liste, dictCouleur):
        self.tableau.itemChanged.disconnect()
        for i, type in enumerate(liste):
            for j in range(self.tableau.columnCount()):
                if type in dictCouleur.keys():
                    self.tableau.item(i, j).setBackground(dictCouleur[type])
                else:
                    self.tableau.item(i, j).setBackground(Qt.white)
        self.tableau.itemChanged.connect(self.modifie)

    def selectionTab(self):
        miniX = 99999999
        maxiX = -99999999
        for index in self.tableau.selectionModel().selectedIndexes():
            if index.column() == 0:
                temp = float(index.data())
                miniX = min(miniX, temp)
                maxiX = max(maxiX, temp)
        return ((miniX, maxiX))

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

    def sauveProfil(self):

        for k, v in self.tab.items():
            if isinstance(v, list):
                self.liste[k][self.position] = " ".join([str(var) for var in v])
            else:
                self.liste[k][self.position] = v

        self.feature = {k: v[self.position] for k, v in self.liste.items()}

        tab = {self.nom: self.tab}
        self.mdb.update("profiles", tab, var="name")

    def sauveTopo(self):
        """ Save les modification du à la translation de la topo"""
        for nom, t in self.topo.items():
            for x, z, gid, ordre in zip(t['x'], t['z'], t['gid'], t['ordre']):
                for f in self.coucheProfils.getFeatures():
                    if f["name"] == self.nom:
                        P = f.geometry().interpolate(x).asPoint()
                        geom = "ST_SetSRID(ST_MakePoint({0}, {1}),{2})".format(P.x(), P.y(), self.mdb.SRID)
                # print(x, ordre)
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

        self.extraitTopo()

    def effaceProfil(self):

        self.tab = {"x": [], "z": [], "leftminbed": None,
                    "rightminbed": None, "leftstock": None,
                    "rightstock": None}

        self.mdb.update("profiles", {self.nom: self.tab}, var='name')

        self.majGraph()

    def delTopo(self):
        """delete topo"""
        liste = self.topo.keys()
        nameTopo, ok = QInputDialog.getItem(None,
                                            'Topo Choice',
                                            'Topo',
                                            liste)
        if ok:
            condition = "name='{0}' AND profile='{1}'".format(nameTopo, self.nom)
            self.mdb.delete("topo", condition)

        self.extraitTopo()
        self.majGraph()
        self.majLimites()
        self.majLegende()

    def importTopo(self):
        if int(qVersion()[0]) < 5: #qt4
            fichiers = QFileDialog.getOpenFileNames(None,
                                                    'File Selection',
                                                    self.dossierProjet,
                                                    "File (*.txt *.csv)")
        else: #qt5
            fichiers,_ = QFileDialog.getOpenFileNames(None,
                                                    'File Selection',
                                                    self.dossierProjet,
                                                    "File (*.txt *.csv)")

        if fichiers:

            self.chargerBathy(fichiers, self.coucheProfils,
                              self.nom)

            self.extraitTopo()
            self.majGraph()
            self.majLimites()
            self.majLegende()
        else:
            self.mgis.addInfo('File "{}" cannot open.'.format(fichiers))

    def chargerBathy(self, liste, coucheProfil, profil=None):
        """charge la bathymetrie"""
        for fichier in liste:
            basename = os.path.basename(fichier)
            if not profil:
                profil = basename.split(".")[0]
            for f in coucheProfil.getFeatures():
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
                            x, z =[float(var) for var in ligne.split(sep)]
                            ordre += 1

                            P = f.geometry().interpolate(x).asPoint()

                            # geom = "ST_MakePoint({0}, {1})".format(P.x(), P.y())

                            geom = "ST_SetSRID(ST_MakePoint({0}, {1}),{2})".format(P.x(), P.y(), self.mdb.SRID)

                            tab["name"].append("'" + basename + "'")
                            tab["profile"].append("'" + profil + "'")
                            tab["order_"].append(ordre)
                            tab["x"].append(x)
                            tab["z"].append(z)
                            tab["geom"].append(geom)

                    self.mdb.insert2("topo", tab)

    def importImage(self):
        if int(qVersion()[0]) < 5:  # qt4
            fichier = QFileDialog.getOpenFileName(None,
                                                  'Sélection des fichiers',
                                                  self.dossierProjet,
                                                  "Fichier (*.png *.jpg)")
        else: #qt5
            fichier,_ = QFileDialog.getOpenFileName(None,
                                                  'Sélection des fichiers',
                                                  self.dossierProjet,
                                                  "Fichier (*.png *.jpg)")


        try:
            fich = open(fichier + "w", "r")
        except OSError:
            self.mgis.addInfo('File "{}" cannot open.'.format(fichier + "w"))
        else:
            x0 = float(fich.readline())
            z0 = float(fich.readline())
            l = float(fich.readline())
            h = float(fich.readline())
            fich.close()
        try:
            img = mpimg.imread(fichier)
        except:
            self.mgis.addInfo('File "{}" cannot open.'.format(fichier))
        else:
            self.image = self.axes.imshow(img,
                                          extent=[x0, x0 + l, z0 - h, z0],
                                          zorder=1,
                                          aspect='auto')
            # self.axes.imshow(fichier)
            self.canvas.draw()

    def closeEvent(self, event):
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
        zoneSelector = self.bt_select_z.isChecked()
        bouton = event.mouseevent.button

        if deplace and legline in self.courbeTopo and bouton == 1:
            self.x0 = round(event.mouseevent.xdata, 2)
            self.courbeSelected = legline

        elif self.flag and bouton == 1 and legline in self.courbeTopo:
            N = len(event.ind)
            if not N:
                return True
            # the click locations
            lbl = legline.get_label()
            x = round(event.mouseevent.xdata, 2)
            z = round(event.mouseevent.ydata, 2)
            xs = np.array(self.topo[lbl]['x'])
            zs = np.array(self.topo[lbl]['z'])
            # print(event.ind,x, z)

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

            self.majGraph()
        elif not zoneSelector and bouton == 1:
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
        miniX = min(eclick.xdata, erelease.xdata)
        maxiX = max(eclick.xdata, erelease.xdata)
        miniY = min(eclick.ydata, erelease.ydata)
        maxiY = max(eclick.ydata, erelease.ydata)
        self.selected = {'x': [], 'z': [], 'label': []}
        for courbe in self.courbes:
            if courbe.get_visible():
                xdata = courbe.get_xdata()
                ydata = courbe.get_ydata()
                label = courbe.get_label()
                for x, y in zip(xdata, ydata):
                    if x > miniX and x < maxiX and y > miniY and y < maxiY:
                        self.selected['x'].append(x)
                        self.selected['z'].append(y)
                        self.selected['label'].append(label)

        self.courbeSelection.set_data(self.selected['x'], self.selected['z'])
        self.courbeSelection.set_visible(True)

        self.fig.canvas.draw()

    def onselectZone(self, xmin, xmax):
        """selectionne zone"""
        n = len(self.tab['x'])
        if n > 0:

            mini = min(self.tab['x'], key=lambda x: abs(x - xmin))
            iMin = self.tab['x'].index(mini)

            maxi = min(self.tab['x'], key=lambda x: abs(x - xmax))
            iMax = self.tab['x'].index(maxi)
            range = QTableWidgetSelectionRange(iMin, 0, iMax, 1)
            self.tableau.clearSelection()
            self.tableau.setRangeSelected(range, True)
            self.tableau.scrollToItem(self.tableau.item(iMin, 0))

            self.rectSelection.set_x(mini)
            self.rectSelection.set_width(maxi - mini)
            self.rectSelection.set_visible(True)
            self.canvas.draw()
        else:
            if self.mgis.DEBUG:
                self.mgis.addInfo("The table has {0} elements, please add ".format(n))

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
                if not self.topoSelect in self.topo.keys():
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
            # print(event.xdata, event.ydata)
            self.majGraph()

    def onpress(self, event):
        if self.bt_transla.isChecked() and self.x0:
            f = self.courbeSelected.get_label()
            try:
                tabX = self.topo[f]['x']
                # tabX = list(map(lambda x: x + round(event.xdata, 2) - self.x0, tabX))
                tempo = []
                fct1 = lambda x: x + round(float(event.xdata), 2) - self.x0
                for var1 in tabX:
                    tempo.append(fct1(var1))
                tabX=tempo

                self.topo[f]['x'] = tabX
                self.courbeSelected.set_xdata(tabX)

                self.x0 = round(float(event.xdata), 2)
            except:
                if self.mgis.DEBUG:
                    self.mgis.addInfo("Warning:Out of graph")
            self.fig.canvas.draw()

    def majGraph(self):
        self.ui.label_Title.setText(_translate("ProfilGraph", self.nom, None))

        T = self.tab
        self.courbeProfil.set_data(T['x'], T['z'])

        self.remplirTab([T['x'], T['z']])

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

        if T['x'] and T['leftminbed'] and T['rightminbed']:
            self.litMineur.set_x(T['leftminbed'])
            self.litMineur.set_width(T['rightminbed'] - T['leftminbed'])
            self.litMineur.set_visible(True)
        else:
            self.litMineur.set_visible(False)

        if T['x'] and T["leftstock"]:
            mini = min(T['x'])
            self.stockgauche.set_x(mini)
            self.stockgauche.set_width(T['leftstock'] - mini)
            self.stockgauche.set_visible(True)
        else:
            self.stockgauche.set_visible(False)

        if T['x'] and T["rightstock"]:
            self.stockdroit.set_x(T['rightstock'])
            self.stockdroit.set_width(max(T['x']) - T['rightstock'])
            self.stockdroit.set_visible(True)
        else:
            self.stockdroit.set_visible(False)

        self.canvas.draw()

    def majLimites(self):
        miniX = 99999999
        maxiX = -99999999
        miniZ = 99999999
        maxiZ = -99999999

        for courbe in self.courbes:
            x, z = courbe.get_data()
            if courbe.get_visible() and x:
                miniX = min(miniX, min(x))
                maxiX = max(maxiX, max(x))
                miniZ = min(miniZ, min(z) - 1)
                maxiZ = max(maxiZ, max(z) + 1)

        if miniX < 99999999:
            self.axes.set_xlim(miniX, maxiX)
            self.axes.set_ylim(miniZ, maxiZ)
            self.canvas.draw()

    def majLegende(self):
        listeNoms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, listeNoms, loc='upper right',
                                    fancybox=False, shadow=False)
        self.leg.get_frame().set_alpha(0.4)
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(10)
            legline.set_linewidth(3)
            self.lined[legline.get_label()] = courbe
        self.canvas.draw()

    def ajoutPoints(self):
        if self.selected:
            self.courbeSelection.set_visible(False)
            # self.selected['x'] = list(map(lambda x: round(x, 2), self.selected['x']))
            tempo = []
            fct1 = lambda x: round(float(x), 2)
            for var1 in self.selected['x']:
                tempo.append(fct1(var1))
            self.selected['x']=tempo

            miniX = min(self.selected['x'])
            maxiX = max(self.selected['x'])

            T = self.tab

            iMin = 0
            iMax = len(T['x'])
            for i, x in enumerate(T['x']):
                if x < miniX:
                    iMin = max(i, iMin)

                if x > maxiX:
                    iMax = min(i, iMax)

            # print(T['x'][:iMin],self.selected['x'],T['x'][iMax:])
            T['x'] = T['x'][:iMin] + self.selected['x'] + T['x'][iMax:]
            T['z'] = T['z'][:iMin] + self.selected['z'] + T['z'][iMax:]
            # print(T['x'], T['z'])
            self.selected = {}

            self.majGraph()

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
            self.majGraph()

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
        X = [self.tab['x'][0]]
        Z = [self.tab['z'][0]]
        dernierePente = 1

        for i in range(1, n - 1):
            mini = max(0, i - nb)
            maxi = min(i + nb + 1, n)
            xx = self.tab['x'][mini:maxi]
            zz = self.tab['z'][mini:maxi]

            pente, ord = np.polyfit(xx, zz, 1)
            zz.sort()
            mediane = zz[nb]
            # print(abs((pente - dernierePente)/dernierePente))
            if abs((pente - dernierePente) / dernierePente) > seuil:

                X.append(self.tab['x'][i])
                # Z.append(self.tab['z'][i])
                if abs(self.tab['z'][i] - mediane) > seuil2:
                    Z.append(self.tab['z'][i])
                else:
                    Z.append(mediane)

                dernierePente = pente

        X.append(self.tab['x'][-1])
        Z.append(self.tab['z'][-1])

        flag = True
        self.tab['x'] = [X[0]]
        self.tab['z'] = [Z[0]]
        m = len(Z)
        for i in range(1, m):
            if Z[i - 1] != Z[i]:
                if flag:
                    self.tab['x'].append(X[i - 1])
                    self.tab['z'].append(Z[i - 1])

                self.tab['x'].append(X[i])
                self.tab['z'].append(Z[i])
                flag = False
            elif i == m - 1:
                self.tab['x'].append(X[i])
                self.tab['z'].append(Z[i])
            else:
                flag = True

        self.majGraph()

    def selectLitMineur(self):
        self.rectSelection.set_visible(False)
        xmin = round(self.rectSelection.get_x(), 2)
        xmax = round(self.rectSelection.get_width() + xmin, 2)

        self.tab["leftminbed"] = xmin
        self.tab["rightminbed"] = xmax

        # self.liste[self.position] = (self.feature["abscisse"], self.feature)
        self.majGraph()

    def selectStock(self, side):
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
            self.majGraph()
        else:
            if self.mgis.DEBUG:
                self.mgis.addInfo("The table has {0} elements, please add ".format(n))

    def selectChanged(self):
        # miniX, maxiX = self.tableau.selection()
        miniX, maxiX = self.selectionTab()

        if miniX != 99999999 and maxiX != -99999999:
            self.rectSelection.set_x(miniX)
            self.rectSelection.set_width(maxiX - miniX)
            self.rectSelection.set_visible(True)
            self.canvas.draw()

            # def zoom_fun(self, event):
            #     # get the current x and y limits
            #     try:
            #         base_scale = 1.5
            #         cur_xlim = self.axes.get_xlim()
            #         cur_ylim = self.axes.get_ylim()
            #         cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
            #         cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
            #         xdata = event.xdata  # get event x location
            #         ydata = event.ydata  # get event y location
            #         # print(event.button)
            #         if event.button == 'up':
            #             # deal with zoom in
            #             scale_factor = 1 / base_scale
            #         elif event.button == 'down':
            #             # deal with zoom out
            #             scale_factor = base_scale
            #         else:
            #             # deal with something that should never happen
            #             scale_factor = 1
            #             # print event.button
            #         # set new limits
            #         self.axes.set_xlim([xdata - cur_xrange * scale_factor,
            #                             xdata + cur_xrange * scale_factor])
            #         self.axes.set_ylim([ydata - cur_yrange * scale_factor,
            #                             ydata + cur_yrange * scale_factor])
            #         self.fig.canvas.draw()  # force re-draw
            #     except:
            #         pass

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
            for r in xrange(nrows):
                for c in xrange(ncols):
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
        self.initUI_common_P(gid)
        self.GUI_graph(self.ui)
        qres = self.initUI()

        if qres:
            # Action
            self.ui.actionBt_reculTot.triggered.connect(lambda: self.avance(-10))
            self.ui.actionBt_recul.triggered.connect(lambda: self.avance(-1))
            self.ui.actionBt_av.triggered.connect(lambda: self.avance(1))
            self.ui.actionBt_avTot.triggered.connect(lambda: self.avance(10))

            #
            self.ui.actionBt_exportCSV.triggered.connect(self.exportCSV)
            # self.ui.actionComboBox_State.triggered.connect(self.comboRunChanged)
            self.comboRun.currentIndexChanged['QString'].connect(self.comboRunChanged)
            # self.ui.comboBox_State.currentIndexChanged.connect(self.comboRunChanged)
            self.comboScen.currentIndexChanged['QString'].connect(self.comboScenChanged)
            self.comboTime.currentIndexChanged['QString'].connect(self.comboTimeChanged)

    def initUI(self):

        try:
            self.tab = {}
            # condition = "NOT scenario LIKE '%init%'"
            # dico = self.mdb.selectDistinct("date, run, scenario",
            #                                      "runs",
            #                                      condition)
            dico_run = self.mdb.selectDistinct("date, run, scenario,t",
                                               "runs")

            if not dico_run:
                self.mgis.addInfo("No simulation to show")
                return False



            self.listeRuns = {}
            for run, scen in zip(dico_run["run"], dico_run["scenario"]):
                if not run in self.listeRuns.keys():
                    self.listeRuns[run] = []
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

            #time list
            self.comboTime = self.ui.comboBox_Time
            self.posit='Hmax'
            self.listcomboTime()

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

            self.majGraph()
            self.majLegende()
            self.majLimites()

            self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
            self.fig.patch.set_facecolor((0.94, 0.94, 0.94))
            self.fig.canvas.mpl_connect('pick_event', self.onpick)
            # # self.fig.tight_layout()
            return True


        except:
            self.mgis.addInfo("No simulation to show")
            return False

    def listcomboTime(self):
        """creation of the Time list"""
        self.comboTime.currentIndexChanged['QString'].disconnect()
        self.comboTime.clear()
        self.date = False
        self.type = 't'
        self.listeTime={'t':[],'date':[]}
        condition = "run='{0}' AND scenario='{1}'".format(self.run,
                                                          self.scenario)
        temp = self.mdb.selectDistinct("date", "resultats", condition)
        if temp["date"][0]:
            self.date = True
            if self.type == 't':
                self.type = 'date'
        else:
            if self.type == 'date':
                self.type = 't'

        self.listeTime['date'] = temp['date']
        temp = self.mdb.selectDistinct("t", "resultats", condition)
        self.listeTime['t']= temp['t']
        self.comboTime.addItem('Hmax')
        for x in self.listeTime[self.type]:
            if isinstance(x, float):
                self.comboTime.addItem(str(x))
            else:
                self.comboTime.addItem('{0:%d/%m/%Y %H:%M:%S}'.format(x))
        self.posit = 'Hmax'
        self.comboTime.setCurrentIndex(0)
        self.comboTime.currentIndexChanged['QString'].connect(self.comboTimeChanged)


    def exportCSV(self):
        """Export Table to .CSV file"""
        # recupe tab export CSV

        if int(qVersion()[0]) < 5: #qt4
            fileNamePath = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(self.nom),
                                                       filter="CSV (*.csv *.)")
        else: # qt5
            fileNamePath,_ = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(self.nom),
                                                   filter="CSV (*.csv *.)")

        if fileNamePath:
            file = open(fileNamePath, 'w')
            file.write("# {0} \n".format(self.nom))
            file.write("# X ; Z \n")

            for i, x in enumerate(self.tab[self.nom]['x']):
                z = self.tab[self.nom]['z'][i]
                file.write("{0} ; {1} \n".format(x, z))
            file.close()


    def remplirTab(self, liste):
        """ Fill items in the table"""
        self.tableau.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.tableau.setItem(i, j, QTableWidgetItem(str(v)))


    def colorieTab(self, liste, dictCouleur):
        for i, type in enumerate(liste):
            for j in range(self.tableau.columnCount()):
                if type in dictCouleur.keys():
                    self.tableau.item(i, j).setBackground(dictCouleur[type])
                else:
                    self.tableau.item(i, j).setBackground(Qt.white)


    def selectionTab(self):
        miniX = 99999999
        maxiX = -99999999
        for index in self.tableau.selectionModel().selectedIndexes():
            if index.column() == 0:
                temp = float(index.data())
                miniX = min(miniX, temp)
                maxiX = max(maxiX, temp)
        return ((miniX, maxiX))


    def majGraph(self):
        for patch in self.aire:
            if patch in self.axes.patches:
                self.axes.patches.remove(patch)

        self.title.setText(self.nom)

        # profile
        self.extraitProfil()

        T = self.tab[self.nom]
        self.courbeProfil.set_data(T['x'], T['z'])

        self.remplirTab([T['x'], T['z']])

        T['leftminbed'] = self.feature["leftminbed"]
        T['rightminbed'] = self.feature["rightminbed"]
        T['leftstock'] = self.feature["leftstock"]
        T['rightstock'] = self.feature["rightstock"]

        if T['x'] and T['leftminbed'] and T['rightminbed']:
            self.litMineur.set_x(T['leftminbed'])
            self.litMineur.set_width(T['rightminbed'] - T['leftminbed'])
            self.litMineur.set_visible(True)
        else:
            self.litMineur.set_visible(False)

        if T['x'] and T["leftstock"]:
            mini = min(T['x'])
            self.stockgauche.set_x(mini)
            self.stockgauche.set_width(T['leftstock'] - mini)
            self.stockgauche.set_visible(True)
        else:
            self.stockgauche.set_visible(False)

        if T['x'] and T["rightstock"]:
            self.stockdroit.set_x(T['rightstock'])
            self.stockdroit.set_width(max(T['x']) - T['rightstock'])
            self.stockdroit.set_visible(True)
        else:
            self.stockdroit.set_visible(False)

        #value H
        self.majVal()

        if self.zH:
            self.label_hmax.setText('{0}'.format(self.zmax))
            temp1 = np.array(T['z'])

            if self.posit=='Hmax':
                temp2 = np.array([self.zmax] * len(T['z']))
            else:
                h=self.zH['zref'][0] + self.zH['y'][0]
                temp2 = np.array([h] * len(T['z']))


            aire = self.axes.fill_between(T['x'], temp1, temp2,
                                          where=temp2 >= temp1,
                                          interpolate=True)
            self.aire = []
            for p in aire.get_paths():
                for x, y in p.vertices:
                    if x >= T['leftminbed'] and x <= T['rightminbed']:
                        patch = patches.PathPatch(p,
                                                  facecolor='deepskyblue',
                                                  lw=0)
                        self.aire.append(patch)
                        self.axes.add_patch(patch)
                        break

            self.axes.collections.remove(aire)
            # Figure title
            if self.posit=='Hmax':
                self.titleFig.set_text('Max of water level, {0} m '.format(self.zmax))
            elif isinstance(self.posit, float):
                self.titleFig.set_text('Water level, {0} m - {1} s'.format(h,self.posit))
            else:
                self.titleFig.set_text('Water level, {0} m - {1:%d/%m/%Y %H:%M}'.format(h,self.posit))

        self.canvas.draw()


    def majLimites(self):
        miniX = 99999999
        maxiX = -99999999
        miniZ = 99999999
        maxiZ = -99999999

        for courbe in self.courbes:
            x, z = courbe.get_data()
            if courbe.get_visible() and x:
                miniX = min(miniX, min(x))
                maxiX = max(maxiX, max(x))
                miniZ = min(miniZ, min(z) - 1)
                maxiZ = max(maxiZ, max(z) + 1)

        if miniX < 99999999:
            self.axes.set_xlim(miniX, maxiX)
            self.axes.set_ylim(miniZ, maxiZ)
            self.canvas.draw()


    def extraitProfil(self):
        if self.nom not in self.tab.keys():
            self.tab[self.nom] = {'x': [], 'z': []}
        else:
            return

        if self.feature['x'] and self.feature['z']:
            condition = "name='{0}'".format(self.nom)
            requete = self.mdb.select("profiles", condition)
            # self.tab[self.nom]['x'] = list(map(float, requete["x"][0].split()))
            # self.tab[self.nom]['z'] = list(map(float, requete["z"][0].split()))
            self.tab[self.nom]['x']=[float(var) for var in requete["x"][0].split()]
            self.tab[self.nom]['z']=[float(var) for var in requete["z"][0].split()]



    def onpick(self, event):
        legline = event.artist

        courbe = self.lined[legline]
        vis = not courbe.get_visible()
        courbe.set_visible(vis)
        if vis:
            legline.set_alpha(1.0)
        else:
            legline.set_alpha(0.2)
        self.canvas.draw()


    def comboRunChanged(self, text):
        """function for change ComboBox and update the figure"""
        self.run = text
        # self.mgis.addInfo("scenario")
        # self.mgis.addInfo(self.scenario)

        if not self.scenario in self.listeRuns[self.run]:
            self.scenario = self.listeRuns[self.run][-1]
        self.comboScen.currentIndexChanged['QString'].disconnect()
        self.comboScen.clear()
        self.comboScen.addItems(self.listeRuns[self.run])
        self.comboScen.currentIndexChanged['QString'].connect(
            self.comboScenChanged)

        self.listcomboTime()

        # self.majListe()
        # self.majTab()
        self.majGraph()


    def comboScenChanged(self, text):
        self.scenario = text
        self.listcomboTime()
        # self.majListe()
        # self.majTab()
        self.majGraph()

    def comboTimeChanged(self, text):
        #change the Figure in function of Time
        if text=='Hmax':
            self.posit =text
        elif fct.isfloat(text):
            self.posit = float(text)
        else:
            self.posit = datetime.strptime(text, '%d/%m/%Y %H:%M:%S')
        self.majGraph()


    def majVal(self):
        # get value for graphic
        abscisse = self.feature['abscissa']

        condition = "run='{0}' AND scenario='{1}' AND pk={2}".format(self.run,
                                                                     self.scenario,
                                                                     abscisse)
        self.zmax = self.mdb.selectMax("z", "resultats", condition)

        if self.posit=='Hmax':
            self.zH= self.zmax
        elif isinstance(self.posit, datetime):
            condition += """AND date='{:%Y-%m-%d %H:%M:%S}'""".format(
                self.posit)
            self.zH = self.mdb.select("resultats", condition, "t")
        else:
            condition += "AND t={0}".format(self.posit)
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

        self.majGraph()
        self.majLimites()
        self.majLegende()


    def majLegende(self):
        listeNoms = [c.get_label() for c in self.courbes]
        self.leg = self.axes.legend(self.courbes, listeNoms, loc='upper right',
                                    fancybox=False, shadow=False)
        self.leg.get_frame().set_alpha(0.4)
        self.leg.set_zorder(110)
        self.lined = dict()

        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(10)
            legline.set_linewidth(3)
            self.lined[legline] = courbe

        self.canvas.draw()


    def selectChanged(self):
        miniX, maxiX = self.tableau.selection()

        if miniX != 99999999 and maxiX != -99999999:
            self.rectSelection.set_x(miniX)
            self.rectSelection.set_width(maxiX - miniX)
            self.rectSelection.set_visible(True)
            self.canvas.draw()


class GraphHydro(GraphCommon):
    def __init__(self, feature, mgis, select, position, type):
        # feature, selection, position, type, main
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
        self.GUI_graph(self.ui)

        self.initUI()

        #         # Action
        self.ui.actionBt_reculTot.triggered.connect(lambda: self.avance(-10))
        self.ui.actionBt_recul.triggered.connect(lambda: self.avance(-1))
        self.ui.actionBt_av.triggered.connect(lambda: self.avance(1))
        self.ui.actionBt_avTot.triggered.connect(lambda: self.avance(10))
        #
        #
        self.ui.actionBt_exportCSV.triggered.connect(self.exportCSV)
        self.comboRun.currentIndexChanged['QString'].connect(self.comboRunChanged)
        self.comboScen.currentIndexChanged['QString'].connect(self.comboScenChanged)
        self.comboVar1.currentIndexChanged['QString'].connect(self.comboVar1Changed)
        self.comboTimePK.currentIndexChanged['QString'].connect(self.comboTimePKChange)

    #         # self.ui.actionComboBox_var2.triggered.connect()
    #         # self.ui.actionTableWidget_RES.triggered.connect()
    #
    def initUI(self):

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
        # dico = self.mdb.selectDistinct("date, run, scenario",
        #                                           "runs",
        #                                           condition)
        dico_run = self.mdb.selectDistinct("date, run, scenario",
                                           "runs")

        if not dico_run:
            self.mgis.addInfo("No simulation to show")
            return False
        self.listeRuns = {}
        for run, scen in zip(dico_run["run"], dico_run["scenario"]):
            if not run in self.listeRuns.keys():
                self.listeRuns[run] = []
            self.listeRuns[run].append(scen)

        self.run = sorted(self.listeRuns.keys())[-1]

        self.scenario = self.listeRuns[self.run][-1]

        self.comboRun.clear()
        self.comboRun.addItems(sorted(self.listeRuns.keys()))
        le = len(self.listeRuns.keys())
        self.comboRun.setCurrentIndex(le - 1)

        self.comboScen.clear()
        # self.mgis.addInfo('{}'.format(self.listeRuns[self.run]))
        self.comboScen.addItems(self.listeRuns[self.run])
        le = len(self.listeRuns[self.run])
        self.comboScen.setCurrentIndex(le - 1)

        temp = self.mdb.selectDistinct("abscissa", "weirs", "active")
        if temp:
            seuils = temp["abscissa"]
        else:
            seuils = []

        self.comboTimePK.clear()

        # selection = self.liste['selection']
        # info observation
        # if 'code' in selection.keys() and os.path.isfile(self.fichierObs):
        # with open(self.fichierObs, 'r') as fichier:
        # ligne = fichier.readline().strip()
        # codes = ligne.split(';')[1:]

        # ligne = fichier.readline().strip()
        # ligne = ligne.replace('H', 'Cote').replace('Q', 'Debit')
        # types = ligne.split(';')[1:]

        # ligne = fichier.readline().strip()
        # nomStat = ligne.split(';')[1:]

        # self.obs['date'] = []
        # for code, type in zip(codes, types):
        # if code not in self.obs.keys():
        # self.obs[code] = {}
        # self.obs[code][type] = []

        # for ligne in fichier:
        # temp = ligne.strip().split(';')
        # valeurs = list(map(float, temp[1:]))
        # self.obs['date'].append(fct.fmtDate(temp[0]))

        # for i, val in enumerate(valeurs):
        # if types[i] == 'Cote' and 'zero' in selection.keys():
        # index=selection['code'].index(codes[i])
        # val += selection['zero'][index]
        # self.obs[codes[i]][types[i]].append(val)


        self.columns = self.mdb.listColumns("resultats")[8:]
        # self.mgis.addInfo(' ListG {}'.format(self.columns))
        self.colVal = []
        self.unite = ""
        for col in self.columns:
            if self.variables[col]['code'] == self.var1:
                self.unite = self.variables[col]['unite']
                self.var1Name = self.variables[col]['nom']
                self.colVal.append(col)
        listeNom = [self.type]
        # default value
        listeG = []
        for col in self.columns:
            listeNom.append(self.variables[col]['nom'])
            codd = self.variables[col]['code']
            # var = self.variables[col]['nom'].split()[0]
            if codd in self.coteVar:
                var = 'Levels'
            elif codd in self.debVar:
                var = 'Flow rates'
            else:
                var = self.variables[col]['nom']
            if not var in listeG:
                listeG.append(var)

        # creation tableau
        self.tableau = self.ui.tableWidget_RES
        self.tableau.setColumnCount(len(listeNom))
        self.tableau.setRowCount(0)
        self.tableau.setHorizontalHeaderLabels(listeNom)
        self.tableau.addAction(CopySelectedCellsAction(self.tableau))

        # comboGrandeur

        self.comboVar1.clear()
        self.comboVar1.addItems(listeG)
        # if self.var1:
        #     self.comboVar1.setCurrentIndex(listeG.index(self.var1))

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

        self.majListe()

        self.majTab()
        self.majLaisses()
        self.majLegende()
        self.majGraph()
        self.majLimites()

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
        # print("cool")

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

    def exportCSV(self):
        """Export Table to .CSV file"""
        # recupe tab export CSV
        if int(qVersion()[0]) < 5: #qt4
            fileNamePath,_ = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(self.nom),
                                                       filter="CSV (*.csv *.)")
        else: #qt5
            fileNamePath = QFileDialog.getSaveFileName(self, "saveFile", "{0}.csv".format(self.nom),
                                                   filter="CSV (*.csv *.)")
        if fileNamePath:
            file = open(fileNamePath, 'w')
            ligne = '# {0} - {1} \n'.format(self.titre, self.nom)
            file.write(ligne + " \n")
            ligne = "# {0} ; ".format(self.type)
            for col in self.columns:
                ligne += "{0} ; ".format(self.variables[col]['nom'])
            file.write(ligne + " \n")

            nbl = len(self.listeTab[0])
            nbc = len(self.listeTab)
            tab1 = np.eye(nbl, nbc)
            for j, val in enumerate(self.listeTab):
                for i, v in enumerate(val):
                    tab1[i, j] = v

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

    #         self.canvas.draw()

    def onpress(self, event):
        if event.button == 1 and self.flag:
            self.affiche_cadre(event)
            #

    def onpick(self, event):
        legline = event.artist
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

    def majListe(self):
        self.date = False
        condition = "run='{0}' AND scenario='{1}'".format(self.run,
                                                          self.scenario)
        temp = self.mdb.selectDistinct("date", "resultats", condition)

        if temp["date"][0]:
            self.date = True
            if self.type == 't':
                self.type = 'date'
        else:
            if self.type == 'date':
                self.type = 't'

        self.liste['date']['abs'] = temp["date"]

        temp = self.mdb.selectDistinct("t", "resultats", condition)
        self.liste['t']['abs'] = temp["t"]

        temp = self.mdb.selectDistinct('pk', "resultats", condition)
        self.liste['pk']['abs'] = temp['pk']
        S = self.liste['selection']

        if self.type == 'pk':
            self.inv = 't'
            if self.date:
                self.inv = 'date'

            self.position = self.liste[self.inv]['abs'][-1]

            S['abs'] = []
            for i, x in enumerate(self.liste[self.inv]['abs']):
                if i % 12 == 0 or i == len(self.liste[self.inv]['abs']) - 1:
                    S['abs'].append(x)

            self.exclutColonnes = ['rdc', 'rdg', 'zmin', 'q2d', 'q2g', 'qmax']

            self.positionLegende = 'upper right'

        else:
            self.inv = 'pk'

            for x in list(S['abs']):
                if x not in self.liste[self.inv]['abs']:
                    i = S['abs'].index(x)
                    S['abs'].pop(i)
                    S['nom'].pop(i)

            A = S['abs']
            S['nom'] = [S['nom'][A.index(a)] for a in sorted(A)]
            if 'code' in S.keys():
                S['code'] = [S['code'][A.index(a)] for a in sorted(A)]
            if 'zero' in S.keys():
                S['zero'] = [S['zero'][A.index(a)] for a in sorted(A)]
            A.sort()

            # self.exclutColonnes = ['rdc', 'rdg', 'zref', 'zmin', 'zmax', 'q2d',
            #                        'q2g', 'qmax']
            self.exclutColonnes = ['rdc', 'rdg', 'zmin', 'zmax', 'q2d',
                                   'q2g', 'qmax']
            self.positionLegende = 'upper left'

        if 'nom' in S.keys() and self.position in S['abs']:
            pos = S['abs'].index(self.position)
            self.nom = S['nom'][pos] + ' - ' + str(self.position)
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
        except ValueError as e :
            self.mgis.addInfo('No results for this profile. \n Error : {}'.format(e))



        self.comboTimePK.setCurrentIndex(index)
        self.comboTimePK.currentIndexChanged['QString'].connect(self.comboTimePKChange)


    def majTab(self):
        condition = """run='{0}' AND scenario='{1}' """.format(self.run,
                                                               self.scenario)

        if self.type == "pk":
            condition += """AND branche={}""".format(self.branche)

        if isinstance(self.position, datetime):
            condition += """AND date='{:%Y-%m-%d %H:%M:%S}'""".format(
                self.position)
        else:
            condition += """AND {0}={1}""".format(self.inv, self.position)

        # self.mgis.addInfo(condition)
        self.tab = self.mdb.select("resultats", condition, "t")

        self.listeTab = [self.tab[self.type]]
        for c in self.columns:
            if self.tab[c] != [None] * len(self.tab[c]):
                self.listeTab.append(self.tab[c])
                self.courbeHydro[c].set_data(self.tab[self.type], self.tab[c])
            else:
                self.tab[c] = []
        # gui
        self.remplirTab(self.listeTab)

    def remplirTab(self, liste):
        """ Fill items in the table """
        self.tableau.setRowCount(len(liste[0]))
        for j, val in enumerate(liste):
            for i, v in enumerate(val):
                self.tableau.setItem(i, j, QTableWidgetItem(str(v)))

    def majGraph(self):
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
            S = self.liste['selection']
            i = S['abs'].index(self.position)
            code = S['code'][i]
            zero = S['zero'][i]
            mini = min(self.liste['date']['abs'])
            maxi = max(self.liste['date']['abs'])

            if self.var1 in self.coteVar:
                G = 'H'
            elif self.var1 in self.debVar:
                G = 'Q'

            condition = """code = '{0}'
                        AND date>'{1}'
                        AND date<'{2}'
                        AND type='{3}'
                        AND valeur > -99.9""".format(code, mini, maxi, G)

            self.obs = self.mdb.select("observations", condition, "date")

            if self.obs["valeur"]:
                if self.var1 in self.coteVar:
                    # self.obs['valeur'] = list(map(lambda x: x + zero,
                    #                          self.obs['valeur']))
                    tempo = []
                    for var1 in  self.obs['valeur']:
                        tempo.append(var1+ zero)
                    self.obs['valeur'] = tempo

                self.courbeObs.set_data(self.obs['date'], self.obs['valeur'])
                self.courbeObs.set_visible(True)
            else:
                raise

        except:
            # if self.mgis.DEBUG:
            #     self.mgis.addInfo("No observation")
            self.courbeObs.set_visible(False)
            self.obs = {}

        self.canvas.draw()

    def addCourb(self, var):
        """add courbe for visualization"""
        for col in self.columns:
            V = self.variables[col]
            if self.tab[col] and V['code'] == var:
                self.colVal.append(col)
                self.courbeHydro[col].set_visible(True)
                self.courbeHydro[col].set_label(V['nom'])
                self.courbeHydro[col].set_color(V['couleur'])
            else:
                self.courbeHydro[col].set_visible(False)

        self.courbes = [self.courbeHydro[col] for col in self.colVal]

    def majLegende(self):
        self.colVal = []
        if self.var1 in self.coteVar:
            for var in self.coteVar:
                self.addCourb(var)
        elif self.var1 in self.debVar:
            for var in self.debVar:
                self.addCourb(var)
        else:
            self.addCourb(self.var1)

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
        listeNoms = [c.get_label() for c in self.courbes]

        self.leg = self.axes.legend(handles, listeNoms,
                                    loc=self.positionLegende,
                                    fancybox=False,
                                    shadow=False,
                                    fontsize="small")
        self.leg.get_frame().set_alpha(0.4)

        # print(self.leg.get_patches())
        self.lined = dict()
        for legline, courbe in zip(self.leg.get_lines(), self.courbes):
            legline.set_picker(10)
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


                    # self.canvas.draw()

    def majLimites(self):
        miniX = min(self.tab[self.type])
        maxiX = max(self.tab[self.type])
        miniY = None
        maxiY = None
        self.axes.set_xlim(miniX, maxiX)

        if isinstance(miniX, datetime):
            date = mdates.DateFormatter('%d/%m/%Y')
        else:
            date = FormatStrFormatter('%d')
        self.axes.xaxis.set_major_formatter(date)

        marge = 0.05

        colVisibles = []
        for col in self.colVal:
            if self.courbeHydro[col].get_visible():
                colVisibles.append(col)

        temp = [min(self.tab[c]) for c in colVisibles if self.tab[c]]

        if temp:
            miniY = min(temp)

        temp = [max(self.tab[c]) for c in colVisibles if self.tab[c]]

        if temp:
            maxiY = max(temp)

        if miniY is not None and maxiY is not None:
            if self.obs and self.obs['valeur']:
                miniY = min(min(self.obs['valeur']), miniY)
                maxiY = max(max(self.obs['valeur']), maxiY)

            diff = maxiY - miniY
            self.axes.set_ylim(miniY - diff * marge, maxiY + diff * marge)

        self.canvas.draw()

    def majLaisses(self):
        self.courbeLaisses.set_visible(False)
        self.courbeLaisses = self.axes.scatter([], [], label="Flood marks")
        for e in self.etiquetteLaisses:
            self.axes.texts.remove(e)
        self.etiquetteLaisses = []

        condition = "event = '{}'".format(self.scenario)
        self.laisses = self.mdb.select("flood_marks", condition, "abscissa")

        self.laisses['pk'] = self.laisses['abscissa']
        L = self.laisses
        if not self.type in L.keys():
            return
        X = [v for v in L[self.type] if v]
        if not X:
            return

        Z = [v for i, v in enumerate(L['z']) if L[self.type][i]]

        if self.tab["zmax"]:
            couleurs = []
            taille = []
            for x, z in zip(X, Z):
                val = fct.interpole(x, self.tab["pk"], self.tab["zmax"])
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
            couleurs = ["black"] * len(X)
            taille = [1] * len(X)

        self.courbeLaisses = self.axes.scatter(X, Z,
                                               color=couleurs,
                                               marker='+',
                                               label="Flood marks",
                                               s=80,
                                               linewidth=taille)

        self.courbeLaisses.set_visible(True)
        # self.courbeLaisses.set_color(couleurs)
        for x, z, c in zip(X, Z, couleurs):
            temp = self.axes.annotate(str(z), xy=(x, z), xytext=(3, 3),
                                      ha='left', va='bottom',
                                      fontsize='x-small',
                                      color=c,
                                      textcoords='offset points')

            self.etiquetteLaisses.append(temp)

            # except :
            # return

    def comboTimePKChange(self, text):
        if isinstance(self.position, float):
            self.position = float(text)
        else:
            self.position = datetime.strptime(text, '%d/%m/%Y %H:%M')
        self.majTab()
        self.majGraph()
        if self.type != "pk":
            self.majLimites()
            #

    def comboRunChanged(self, text):
        self.run = text
        if not self.scenario in self.listeRuns[self.run]:
            self.scenario = self.listeRuns[self.run][-1]
        self.comboScen.currentIndexChanged['QString'].disconnect()
        self.comboScen.clear()
        self.comboScen.addItems(self.listeRuns[self.run])
        self.comboScen.setCurrentIndex(self.listeRuns[self.run].index(
            self.scenario))
        self.comboScen.currentIndexChanged['QString'].connect(
            self.comboScenChanged)

        self.majListe()
        self.majTab()
        self.majLaisses()
        self.majGraph()
        if self.type != "pk":
            self.majLimites()
            #

    def comboScenChanged(self, text):
        self.scenario = text
        self.majListe()
        self.majTab()
        self.majLaisses()
        self.majGraph()
        if self.type != "pk":
            self.majLimites()
            #

    def comboVar1Changed(self, text):

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
        self.majLegende()
        self.majGraph()
        self.majLimites()

    def avance(self, val):
        # TODO
        if abs(val) == 10:
            var = 'selection'
            val = val / 10
        else:
            var = self.inv

        S = self.liste['selection']
        if self.position not in self.liste[var]['abs']:
            pos = self.position
            i = self.liste[self.inv]['abs'].index(pos)
            n = self.liste[self.inv]['abs']

            while i > 0 and i < len(n) and pos not in S['abs']:
                i -= val
                pos = self.liste[self.inv]['abs'][i]

            if i == len(self.liste[self.inv]['abs']):
                i = -1
            self.position = self.liste[self.inv]['abs'][i]

        pos = self.liste[var]['abs'].index(self.position)
        pos += val
        if pos < len(self.liste[var]['abs']) and pos >= 0:
            self.position = self.liste[var]['abs'][pos]
            if 'nom' in S.keys() and self.position in S['abs']:
                i = S['abs'].index(self.position)
                self.nom = S['nom'][i] + ' - ' + str(self.position)
            else:
                self.nom = str(self.position)
            index = self.liste[self.inv]['abs'].index(self.position)
            self.comboTimePK.setCurrentIndex(index)
            self.majLimites()
