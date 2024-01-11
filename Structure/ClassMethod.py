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

import json

import numpy as np
from shapely.geometry import *

from .ClassTableStructure import ClassTableStructure
from .ClassPolygone import ClassPolygone
from ..ClassMessage import ClassMessage

class ClassMethod:
    def __init__(self, mgis):
        self.mgis = mgis
        self.mdb = mgis.mdb
        self.debug = mgis.DEBUG

        self.grav = 9.81
        self.tbst = ClassTableStructure()
        self.clpoly = ClassPolygone()
        self.mess = ClassMessage()
        self.num_mess = 0

    def sort_law(self, list_final):
        """
        sort the law
        :param list_final: law data
        :return:
        """
        info = np.array(list_final)
        # trie de la colonne 0 à 2
        info = info[info[:, 2].argsort()]  # First sort doesn't need to be stable.
        info = info[info[:, 1].argsort(kind="mergesort")]
        info = info[info[:, 0].argsort(kind="mergesort")]
        return info

    def create_poly_elem(self, id_config, config_type):
        """
        Creation of polygone for the differents elements and save in table
        :param id_config: index of hydraulic structuree
        :param config_type: type configuration PA :arch bridge
                                               PC: beam bridge,
                                               Bu: Buse,
                                               Da :scupper
        :return:
        """

        if self.checkprofil(id_config):
            profil = self.get_profil(id_config)
        else:
            msg = "Profile copy isn't found"
            self.add_info(msg)

            return
        zmin = min(profil["z"])
        poly_p = self.clpoly.poly_profil_del(profil, zmin)
        if poly_p.is_empty:
            msg = "Profile polygon is empty."
            if self.debug:
                self.add_info(msg)
            return
        if config_type == "PC":
            list_recup = ["EPAITAB", "ZTOPTAB", "FIRSTWD"]
            param_g = self.get_param_g(list_recup, id_config)
            param_g["ZPC"] = param_g["ZTOPTAB"] - param_g["EPAITAB"]
            recup_trav = ["LARGTRA"]
            recup_pil = ["FORMPIL", "LARGPIL", "LONGPIL"]
            recup_p1 = []
        elif config_type == "PA":
            list_recup = ["ZTOPTAB", "FIRSTWD"]
            param_g = self.get_param_g(list_recup, id_config)
            recup_trav = ["FORMARC", "LARGTRA", "ZMINARC", "ZMAXARC"]
            recup_pil = ["LARGPIL"]
            recup_p1 = ["FORMARC", "ZMINARC"]
        elif config_type == "DA":
            list_recup = ["ZTOPTAB", "FIRSTWD"]
            param_g = self.get_param_g(list_recup, id_config)
            recup_trav = ["LARGTRA", "COTERAD", "HAUTDAL"]
            recup_pil = ["LARGPIL"]
            recup_p1 = ["COTERAD", "HAUTDAL"]
        elif config_type == "BU":
            list_recup = ["ZTOPTAB"]
            param_g = self.get_param_g(list_recup, id_config)
            param_g["FIRSTWD"] = 0
            recup_trav = ["COTERAD", "ABSBUSE", "LARGTRA"]

        lid_elem = self.get_id_elem(id_config)
        first = True

        width = 0
        width_prec = 0
        width_trav = 0
        sav_zmaxelem = 0
        if not lid_elem["id_elem"]:
            msg = "Not element in table in create_poly_elem function"
            if self.debug:
                self.add_info(msg)
        for i, id_elem in enumerate(lid_elem["id_elem"]):
            # parametre element

            if lid_elem["type"][i] == 1:
                param_elem = self.get_param_elem(id_elem, recup_pil, id_config)
                param_elem["LARG"] = param_elem["LARGPIL"]
                if recup_p1:
                    param_p1 = self.get_param_elem(id_elem + 1, recup_p1, id_config)
            else:
                param_elem = self.get_param_elem(id_elem, recup_trav, id_config)
                param_elem["LARG"] = param_elem["LARGTRA"]
                width_trav += param_elem["LARG"]
            if first:
                width = param_g["FIRSTWD"]
                first = False
            else:
                width += width_prec
            width_prec = param_elem["LARG"]
            if lid_elem["type"][i] != 1:
                #  pont Cadre
                if config_type == "PC":
                    param_elem["ZMAXELEM"] = param_g["ZPC"]
                    sav_zmaxelem = param_elem["ZMAXELEM"]
                    poly_elem = self.clpoly.poly_pont_cadre(param_g, param_elem, width, zmin)
                # pont arc
                elif config_type == "PA":
                    param_elem["ZMAXELEM"] = param_elem["ZMINARC"]
                    sav_zmaxelem = param_elem["ZMAXELEM"]
                    poly_elem = self.clpoly.poly_arch(param_g, param_elem, width, zmin)
                # dalot
                elif config_type == "DA":
                    param_elem["ZMAXELEM"] = param_elem["COTERAD"] + param_elem["HAUTDAL"]
                    sav_zmaxelem = param_elem["ZMAXELEM"]
                    poly_elem = self.clpoly.poly_dalot(param_elem, width)
                # buse
                elif config_type == "BU":
                    poly_elem = self.clpoly.poly_buse(param_elem)

            else:
                if config_type == "PC":
                    param_elem["ZMAXELEM"] = sav_zmaxelem
                    param_elem["ZMAXELEM_P1"] = param_g["ZPC"]
                    poly_elem = self.clpoly.poly_pil(param_elem, width, zmin)
                elif config_type == "PA":
                    param_elem["ZMAXELEM"] = sav_zmaxelem
                    param_elem["ZMAXELEM_P1"] = param_p1["ZMINARC"]
                    poly_elem = self.clpoly.poly_pil(param_elem, width, zmin)
                elif config_type == "DA":
                    param_elem["ZMAXELEM"] = sav_zmaxelem
                    param_elem["ZMAXELEM_P1"] = param_p1["COTERAD"] + param_p1["HAUTDAL"]
                    poly_elem = self.clpoly.poly_pil(param_elem, width, zmin)

            # final
            if not poly_elem.is_empty:
                poly_final = poly_elem.difference(poly_p)
            else:
                poly_final = GeometryCollection()
                msg = "Element bridge polygon is empty."
                if self.debug:
                    self.add_info(msg)

            if not poly_final.is_empty:
                # # stock element
                if poly_final.geom_type == "MultiPolygon":
                    poly_final = "Null"

                self.clpoly.udpate_polygon_table(self.mdb, poly_final, id_config, id_elem)

        width += width_prec

    def add_info(self, txt):
        if self.mgis:
            self.mess('clMehtod{}'.format(self.num_mess), 'info', txt)
            # self.mgis.add_info(txt)
        else:
            print(txt)

    def get_id_elem(self, id_config):
        """
        get id and type of element
        :param id_config:
        :return:
        """
        where = "id_config = {0}".format(id_config)  # type=0 span, =1 bridge peir
        order = "id_elem"
        lid_elem = self.mdb.select(
            "struct_elem", where=where, order=order, list_var=["id_elem", "type"]
        )
        return lid_elem

    def get_param_elem(self, id_elem, list_recup, id_config):
        """
        Get element parameters
        :param id_elem: index of element
        :param list_recup: list of  value to get
        :param id_config: index of hydraulic structure
        :return: dico
        """
        param_elem = {}
        for info in list_recup:
            where = "id_config = {0} AND id_elem= {1} AND var = '{2}' ".format(
                id_config, id_elem, info
            )
            rows = self.mdb.select("struct_elem_param", where=where, list_var=["value"])

            if rows["value"]:
                param_elem[info] = rows["value"][0]
            else:
                if self.debug:
                    self.add_info("{} not specified in struct_elem_param table".format(info))

        return param_elem

    def get_struct(self):
        """
        Get struct dico
        :return dico
        """
        struct_dico = {}
        list_var = ["id", "name", "type", "active", "method"]
        if list_var is not None:
            lvar = ",".join([str(v) for v in list_var])
        else:
            lvar = "*"
        sql = "SELECT {1} FROM {0}.struct_config ORDER BY id;"
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA, lvar), fetch=True)
        if rows is None:
            if self.debug:
                self.add_info("struct_config is empty")
        for row in rows:
            struct_dico[row[0]] = {
                "name": row[1],
                "type": row[2],
                "active": row[3],
                "idmethod": row[4],
                "method": self.tbst.dico_meth_calc[row[4]],
            }
        #
        return struct_dico

    def fg_actif(self):
        where = "active AND id IN (SELECT id_config FROM {}.struct_fg  WHERE active) ".format(
            self.mdb.SCHEMA
        )
        rows = self.mdb.select("struct_config", where=where, list_var=["id"])
        if rows["id"]:
            return rows["id"]
        else:
            return None

    def get_param_fg(self):
        """get variable of the floodgate"""
        where = "active AND id_config in (SELECT id FROM {}.struct_config  WHERE active)".format(
            self.mdb.SCHEMA
        )
        dict_par = self.mdb.select(
            "struct_fg", where=where, list_var=["id_config", "type_fg", "var_reg", "xpos"]
        )
        param_fg = {}
        link_name_id = {}
        lid_config = dict_par["id_config"]
        for i, id_config in enumerate(lid_config):
            dict_tmp = {
                "DIRFG": dict_par["type_fg"][i],
                "LOCCONT": dict_par["xpos"][i],
                "VREG": dict_par["var_reg"][i],
            }

            list_recup = [
                "VELOFG",
                "ZMAXFG",
                "ZINCRFG",
                "DTREG",
                "VALREG",
                "TOLREG",
                "BIEFCONT",
                "XPCONT",
            ]

            for info in list_recup:
                where = "id_config = {0} AND name_var = '{1}' ".format(id_config, info)
                rows = self.mdb.select(
                    "struct_fg_val", where=where, order="id_order", list_var=["value"]
                )
                if rows["value"]:
                    dict_tmp[info] = rows["value"][0]
                else:
                    dict_tmp[info] = None

            where = "id = {}".format(id_config)
            rows = self.mdb.select("struct_config", where=where, list_var=["method", "name"])
            dict_tmp["NAME"] = rows["name"][0]
            dict_tmp["METH"] = rows["method"][0]
            link_name_id[rows["name"][0]] = id_config
            # init dict
            dict_tmp["STATEOLD"] = 0
            dict_tmp["ZRESI"] = 0
            param_fg[id_config] = dict_tmp

        return param_fg, link_name_id

    def select_poly(self, table, where="", order=""):
        """
        Select polygon
        example:
                where = "id_config = {0} AND id_elem = {1}".format(self.id_config, id_elem)
                toto=self.select_poly('struct_elem',where)
        :param table: table
        :param where:  "where" of sql script
        :param order: "order" of sql script

        :return:
        """
        if where:
            where = " WHERE " + where + " "
        if order:
            order = " ORDER BY " + order
        sql = "SELECT ST_AsGeoJSON(Polygon)  AS Polygon  FROM {0}.{1} {2} {3};"
        (results, namCol) = self.mdb.run_query(
            sql.format(self.mdb.SCHEMA, table, where, order), fetch=True, namvar=True
        )
        cols = [col[0] for col in namCol]
        dico = {}
        for col in cols:
            dico[col] = []
        for row in results:
            for i, val in enumerate(row):
                if val is not None:
                    try:
                        dico[cols[i]].append(shape(json.loads(val.strip())))
                    except AttributeError:
                        dico[cols[i]].append(shape(json.loads(val)))

        return dico

    def select_poly_elem(self, id_config, type_conf):
        """
        Get polygone list of hole
        :param id_config: index of hydraulic structure
        :param type_conf: 0: hole, 1:span
        :return:
        """
        where = " id_config={} and type={} ".format(id_config, type_conf)
        order = "id_elem"
        return self.select_poly("struct_elem", where, order)["polygon"]

    def get_profil(self, id_config):
        """
        Get profil coordonnee
        :param id_config: index of hydraulic structure
        """
        where = "id_config = {0}".format(id_config)
        order = "id_order"
        profil = self.mdb.select("profil_struct", where=where, order=order, list_var=["x,z"])
        return profil

    def checkprofil(self, id_config):
        """ "
        Check profil if it exists
        :param id_config: index of hydraulic structure
        """
        where = "id_config = {0}".format(id_config)
        profil = self.mdb.select("profil_struct", where=where, list_var=["id_order"])
        if profil["id_order"]:
            return True
        else:
            return False

    def get_abac(self, list_recup):
        """
        Get abacus
        :param list_recup: list of abacus
        :return: dico with abacus data
        #"""
        name_abac = []
        dico_abc = {}
        table = "struct_abac"
        if list_recup == "all":
            sql = "SELECT DISTINCT nam_method FROM {}.{};".format(self.mdb.SCHEMA, table)
            list_recup = self.mdb.run_query(sql, fetch=True, namvar=False)
            list_recup = [var[0] for var in list_recup]

        for metho in list_recup:
            where = "nam_method = '{0}' ".format(metho)
            list_nam = self.mdb.select_distinct("nam_abac", table, where)["nam_abac"]

            name_abac += list_nam
            for nam_abc in list_nam:
                sql = "SELECT DISTINCT var FROM {}.{} WHERE nam_method='{}' and nam_abac='{}';".format(
                    self.mdb.SCHEMA, table, metho, nam_abc
                )

                list_var = self.mdb.run_query(sql, fetch=True, namvar=False)
                dico_abc[nam_abc] = {}
                for var in list_var:
                    dico_abc[nam_abc][var[0]] = []
                    dico_abc[nam_abc]["order_{}".format(var[0])] = []

                sql = (
                    "SELECT  var,value,id_order FROM {}.{} WHERE nam_method='{}' "
                    "and nam_abac='{}' ORDER by id_order ;".format(
                        self.mdb.SCHEMA, table, metho, nam_abc
                    )
                )
                rows = self.mdb.run_query(sql, fetch=True, namvar=False)

                for row in rows:
                    dico_abc[nam_abc][row[0]].append(row[1])
                    dico_abc[nam_abc]["order_{}".format(row[0])].append(row[2])

        return dico_abc

    def get_param_g(self, list_recup, id_config):
        """
        Get general parameters
        :param list_recup: list of  value to get
        :param id_config: index of hydraulic structure
        :return: dico
        """

        param_g = {}
        if list_recup == "all":
            sql = "SELECT DISTINCT var FROM {}.{} " "WHERE id_config = {};".format(
                self.mdb.SCHEMA, "struct_param", id_config
            )
            list_recup = self.mdb.run_query(sql, fetch=True, namvar=False)
            list_recup = [var[0] for var in list_recup]

        if list_recup:
            for info in list_recup:
                where = "id_config = {0} AND var = '{1}' ".format(id_config, info)
                rows = self.mdb.select("struct_param", where=where, list_var=["value"])
                if rows["value"]:
                    param_g[info] = rows["value"][0]
                else:
                    if self.debug:
                        self.add_info("{} not specified in struct_param table".format(info))

            return param_g
        else:
            return None


# *********************************************************

if __name__ == "__main__":
    pass
