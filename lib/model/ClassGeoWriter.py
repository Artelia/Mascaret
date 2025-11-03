# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : October,2025
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
import datetime
import os

from .Fct_model_file import around, backup_file


class ClassGeoWriter:

    GEO_EXTENSION = '.geo'
    CASIER_EXTENSION = '.casier'

    def __init__(self, mdb, folder, geo_filename, mess=None):
        self.mdb = mdb
        self.mess = mess
        self.geo_filename = geo_filename
        self.folder = folder

    def set_geo_filename(self, filename):
        self.geo_filename = filename.replace('.geo','').replace('.casier','')
    def set_folder(self,folder):
        if os.path.isdir(folder):
            self.folder = folder

    def creer_geo(self):
        """
        Create the geometry file (.geo) for the model.
        :return: None
        """
        try:
            geo_path = os.path.join(self.folder, f'{self.geo_filename}{self.GEO_EXTENSION}')
            backup_file(geo_path, self.GEO_EXTENSION)

            requete = self.mdb.select("profiles", "active", "abscissa")

            with open(geo_path, "w") as fich:
                for i, nom in enumerate(requete["name"]):
                    branche = requete["branchnum"][i]
                    abs = requete["abscissa"][i]
                    temp_x = requete["x"][i]
                    temp_z = requete["z"][i]
                    lit_min_g = requete["leftminbed"][i]
                    lit_min_d = requete["rightminbed"][i]
                    if lit_min_d is not None and lit_min_g is None:
                        lit_min_g = 0.0

                    if branche and abs and temp_x and temp_z and lit_min_g and lit_min_d:
                        tab_z = []
                        tab_x = []
                        for var1, var2 in zip(temp_x.split(), temp_z.split()):
                            tab_x.append(around(var1))
                            tab_z.append(around(var2))

                        fich.write("PROFIL Bief_{0} {1} {2}\n".format(branche, nom, abs))
                        for x, z in zip(tab_x, tab_z):
                            if lit_min_g <= x <= lit_min_d:
                                type = "B"
                            else:
                                type = "T"

                            fich.write("{0:.2f} {1:.2f} {2}\n".format(x, z, type))
            if self.mess:
                self.mess.add_mess("creatGeo", "info", "Creation the geometry is done")
        except Exception as e:
            if self.mess:
                self.mess.add_mess("creatGeo", "critic", f"Error: save geometry.\n{e}")

    def creer_geo_ref(self):
        """
        Create the reference geometry file (.geo) with projection and coordinates.
        :return: None
        """
        try:
            geo_path = os.path.join(self.folder, f'{self.geo_filename}{self.GEO_EXTENSION}')
            backup_file(geo_path, self.GEO_EXTENSION)

            requete = self.mdb.select("profiles", "active", "abscissa")

            # To get projection and Line coordinated.
            vlayer = self.mdb.make_vlayer(self.mdb.register["profiles"])
            vlayer_dp = vlayer.dataProvider()
            vlayer_crs = vlayer_dp.crs()
            vlayer_crs_str = vlayer_crs.authid()

            # Write the File
            with open(geo_path, "w") as fich:
                fich.write(
                    "#  DATE : {0:%d/%m/%Y %H:%M:%S}\n"
                    "#  PROJ. : {1}\n".format(datetime.date.today(), vlayer_crs_str)
                )

                iter = vlayer.getFeatures()
                feature_list = [v for v in iter]
                name_feature = [v["name"] for v in feature_list]
                for i, nom in enumerate(requete["name"]):
                    if nom in name_feature:
                        id = name_feature.index(nom)
                        # fetch geometry
                        geom = feature_list[id].geometry()
                        branche = requete["branchnum"][i]
                        abs = requete["abscissa"][i]
                        temp_x = requete["x"][i]
                        temp_z = requete["z"][i]
                        lit_min_g = requete["leftminbed"][i]
                        lit_min_d = requete["rightminbed"][i]
                        if lit_min_d is not None and lit_min_g is None:
                            lit_min_g = 0.0

                        if (
                                branche is not None
                                and abs is not None
                                and temp_x is not None
                                and temp_z is not None
                                and lit_min_g is not None
                                and lit_min_d is not None
                        ):
                            tab_z = []
                            tab_x = []
                            # fct1 = lambda x: round(float(x), 2)
                            for var1, var2 in zip(temp_x.split(), temp_z.split()):
                                tab_x.append(around(var1))
                                tab_z.append(around(var2))
                            points = geom.asMultiPolyline()[0]
                            (cood1X, cood1Y) = points[0]
                            (cood2X, cood2Y) = points[1]
                            cood_axe_x = cood1X + (cood2X - cood1X) / 2.0
                            cood_axe_y = cood1Y + (cood2Y - cood1Y) / 2.0

                            fich.write(
                                "PROFIL Bief_{0} {1} {2} {3} {4} {5} {6} "
                                "AXE {7} {8}\n".format(
                                    branche,
                                    nom,
                                    abs,
                                    cood1X,
                                    cood1Y,
                                    cood2X,
                                    cood2Y,
                                    cood_axe_x,
                                    cood_axe_y,
                                )
                            )
                            dif = tab_x[-1] - geom.length()
                            if dif > 0:
                                dif += 1
                                # garde line centree
                                geom = geom.extendLine(dif / 2.0, dif / 2.0)
                                feature_list[id].setGeometry(geom)
                                # change geometry
                                vlayer.startEditing()
                                vlayer.updateFeature(feature_list[id])
                                # Call commit to save the changes
                                vlayer.commitChanges()

                            for x, z in zip(tab_x, tab_z):
                                if lit_min_g <= x <= lit_min_d:
                                    type = "B"
                                else:
                                    type = "T"
                                # interpolate the distance on profile
                                dpoint = geom.interpolate(x).asPoint()
                                fich.write(
                                    "{0:.2f} {1:.2f} {2} {3} "
                                    "{4}\n".format(x, z, type, dpoint[0], dpoint[1])
                                )

            if self.mess:
                self.mess.add_mess("creatGeoRef", "info", "Geometry creation done")
        except Exception as e:
            if self.mess:
                self.mess.add_mess("creatGeoRef", "critic", f"Error: save geometry.\n{e}")

    def creer_geo_casier(self):
        """
        Create the .casier file with the surface-volume law for basins.
        :return: None
        """
        try:
            geo_path = os.path.join(self.folder, f'{self.geo_filename}{self.CASIER_EXTENSION}')
            backup_file(geo_path, self.CASIER_EXTENSION)

            casiers = self.mdb.select("basins", "active ORDER BY basinnum")
            lst_err = []
            with open(geo_path, "w") as fich:
                for i, nom in enumerate(casiers["name"]):
                    fich.write("CASIER {0}\n".format(nom))
                    cotes = casiers["level"][i]
                    surfaces = casiers["area"][i]
                    volumes = casiers["volume"][i]
                    if cotes is None or surfaces is None or volumes is None:
                        lst_err.append(i)
                        continue
                    for j, cote in enumerate(cotes.split()):
                        fich.write(
                            "{0:.2f} {1:.2f} {2:.2f}\n".format(
                                float(cotes.split()[j]),
                                float(surfaces.split()[j]),
                                float(volumes.split()[j]),
                            )
                        )
            if len(lst_err) > 0:
                raise Exception("ErrBasin", "Basins law not specified. Id: " "{}".format(lst_err))
            if self.mess:
                self.mess.add_mess("creatBasin", "info", "Creation of the basin file is done")
        except Exception as e:
            if self.mess:
                self.mess.add_mess("creatBasin", "critic", f"Error: save the basin file.\n{e}")
