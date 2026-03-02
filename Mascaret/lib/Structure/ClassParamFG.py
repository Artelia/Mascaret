# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : December,2025
copyright            : (C) 2025 by Artelia
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
import os

from shapely import wkt
from shapely.geometry import shape

try :
    from ..ClassMessage import ClassMessage
    from ..Function import str2bool, data_to_float, data_to_int
except:
    from ClassMessage import ClassMessage
    from Function import str2bool, data_to_float, data_to_int

class ClassParamFG(object):
    """
    Class to manage floodgate link parameters for Mascaret.
    Handles import/export, validation, and database interaction.
    """
    def __init__(self):
        """
        Constructor for ClassLinkFGParam.
        Initializes parameter dictionaries and default values.
        :return: None
        """
        self.param_fg = {}
        self.link_name_id = {}
        self.list_poly_trav = {}
        self.list_poly_pil = {}
        self.profil = {}
        self.param_g = {}
        self.abac = {}
        self.list_actif = []
        self.mess = ClassMessage()



    def get_param(self, parent=None, file_name="cli_fg.obj"):
        """
        Retrieve parameters for mobile structur.

        If `parent` is provided, fetch parameters from the database.
        Otherwise, import parameters from a file.

        :param parent (object): Parent class (optional).
        :param file (str): Name of the file to import parameters from (default: "cli_fg.obj").
        :return: (bool) True if parameters are valid, False otherwise
        """
        if not parent:
            path = os.path.abspath(os.getcwd())
            path = os.path.join(path, file_name)
            complet = self.import_cl(path)
        else:
            complet = self.fill_param_to_db(parent.mdb)

        if complet:
            txt = "Import configuration Mobile Hydraulic Structure"
            self.mess.add_mess('import_fg', 'info', txt)
        else:
            txt = "Error when the Mobile Hydraulic Structure import"
            self.mess.add_mess('import_fg', 'warning', txt)

    def import_cl(self, name="cli_fg.obj"):
        if os.path.isfile(name):
            # with open(name, 'rb') as file:
            # obj = pickle.load(file)
            with open(name, "r") as file:
                obj = json.load(file)
            for key, val in obj.items():
                if key == "list_poly_trav" or key == "list_poly_pil":
                    for key2, itm in val.items():
                        val[key2] = [wkt.loads(poly) for poly in itm]

                setattr(self, key, val)

            #raise Exception(self.list_poly_trav ,obj["list_poly_trav"])
            return True
        return  False

    def fill_param_to_db(self, db):
        """
        Populate the `param_fg` dictionary with parameters from the database.

        Fetches general link information from the  table and
        mobility-specific values from the  table.

        :param db (object): Database object.
        :return:(bool) True if parameters are successfully fetched, otherwise False.

        """
        self.list_actif = self.fg_actif(db)
        self.abac = self.get_db_abac(db)
        where = f"active AND id_config in (SELECT id FROM {db.SCHEMA}.struct_config  WHERE active)"
        dict_par = db.select(
            "struct_fg", where=where, list_var=["id_config", "type_fg", "var_reg", "xpos"]
        )

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
                where = f"id_config = {id_config} AND name_var = '{info}' "
                rows = db.select(
                    "struct_fg_val", where=where, order="id_order", list_var=["value"]
                )
                if rows["value"]:
                    dict_tmp[info] = rows["value"][0]
                else:
                    dict_tmp[info] = None

            where = "id = {}".format(id_config)
            rows = db.select("struct_config", where=where, list_var=["method", "name"])
            dict_tmp["NAME"] = rows["name"][0]
            dict_tmp["METH"] = rows["method"][0]
            self.link_name_id[rows["name"][0]] = id_config
            # init dict
            dict_tmp["STATEOLD"] = 0
            dict_tmp["ZRESI"] = 0
            self.param_fg[id_config] = dict_tmp
            self.profil[id_config] = self.get_db_profil(db, id_config)
            self.param_g[id_config] =self.get_db_param_g(db, id_config)
            #0: hole, 1:span
            self.list_poly_trav[id_config] = self.select_db_poly_elem(db, id_config,0)
            self.list_poly_pil[id_config] = self.select_db_poly_elem(db, id_config,1)
        return  True

    def get_db_profil(self, db, id_config):
        """
        Get profil coordonnee
        :param id_config: index of hydraulic structure
        """
        where = "id_config = {0}".format(id_config)
        order = "id_order"
        profil = db.select("profil_struct", where=where, order=order, list_var=["x,z"])
        return profil

    def export_cl(self, obj, name="object.js"):
        """

        :param obj: object to dump
        :param name: name file
        :return:
        """
        with open(name, "w") as file:
            json.dump(obj, file)

    def create_cli_fg(self, parent=None, name=None):
        """
        Creation of ClassInfomParamFG (python object save compte data)
        :param name: name file for export
        :return:
        """
        if not parent:
            txt = "Error database no access"
            self.mess.add_mess('export_fg', 'critic', txt)
            return False

        complet = self.fill_param_to_db(parent.mdb)
        if not complet:
            txt = "Get data"
            self.mess.add_mess('export_fg', 'critic', txt)
            return False

        tmp_list_poly_trav = {}
        tmp_list_poly_pil = {}
        if self.link_name_id:
            for id_config in self.list_poly_trav.keys():
                tmp_list_poly_trav[id_config] = [
                    poly.wkt for poly in self.list_poly_trav[id_config]
                ]
                tmp_list_poly_pil[id_config] = [
                    poly.wkt for poly in  self.list_poly_pil[id_config]
                ]
        dico = {
            "list_actif": self.fg_actif(),
            "param_fg": self.param_fg,
            "link_name_id": self.link_name_id,
            "list_poly_trav": tmp_list_poly_trav,
            "list_poly_pil": tmp_list_poly_pil,
            "profil": self.profil,
            "param_g": self.param_g,
            "abac": self.abac
        }
        self.export_cl(dico, name)


    def get_profil(self, id_config):
        """
        Get profil coordonnee
        :param id_config: index of hydraulic structure
        """
        return self.profil[id_config]

    def get_param_fg(self):
        """get variable of the floodgate"""
        return self.param_fg, self.link_name_id

    def fg_actif(self, db=None):
        """list of  active flood gate"""
        if db :
            where = f"active AND id IN (SELECT id_config FROM {db.SCHEMA}.struct_fg  WHERE active) "
            rows = db.select("struct_config", where=where, list_var=["id"])
            if rows["id"]:
                return rows["id"]
            return []
        else:
            return self.list_actif

    def get_param_g(self, list_recup, id_config):
        """
        Get general parameters
        :param list_recup: list of  value to get
        :param id_config: index of hydraulic structure
        :return: dico
        """
        dico = self.param_g[id_config]
        new_dico = {}
        for info in list_recup:
            if info in dico.keys():
                new_dico[info] = dico[info]
        return new_dico

    def get_db_param_g(self, db, id_config , list_recup='all'):
        """
        Get general parameters
        :param list_recup: list of  value to get
        :param id_config: index of hydraulic structure
        :return: dico
        """

        param_g = {}
        if list_recup == "all":
            sql = f"SELECT DISTINCT var FROM {db.SCHEMA}.struct_param WHERE id_config = {id_config};"
            list_recup = db.run_query(sql, fetch=True, namvar=False)
            list_recup = [var[0] for var in list_recup]

        if list_recup:
            for info in list_recup:
                where = f"id_config = {id_config} AND var = '{info}' "
                rows = db.select("struct_param", where=where, list_var=["value"])
                if rows["value"]:
                    param_g[info] = rows["value"][0]
                else:
                    txt = f"{info} not specified in struct_param table"
                    self.mess.add_mess('get_param_g', 'warning', txt)

        return param_g

    def get_abac(self, liste):
        """
        Get abacus
        :param liste: list of abacus
        :return: dico with abacus data
        """
        dico = {}
        for key in liste:
            dico[key] = self.abac[key]
        return dico

    def get_db_abac(self,db, list_recup='all'):
        """
        Get abacus
        :param list_recup: list of abacus
        :return: dico with abacus data
        #"""
        name_abac = []
        dico_abc = {}
        table = "struct_abac"
        if list_recup == "all":
            sql = f"SELECT DISTINCT nam_method FROM {db.SCHEMA}.{table};"
            list_recup = db.run_query(sql, fetch=True, namvar=False)
            list_recup = [var[0] for var in list_recup]

        for metho in list_recup:
            where = f"nam_method = '{metho}' "
            list_nam = db.select_distinct("nam_abac", table, where)["nam_abac"]

            name_abac += list_nam
            for nam_abc in list_nam:
                sql = f"SELECT DISTINCT var FROM {db.SCHEMA}.{table} WHERE nam_method='{metho}' and nam_abac='{nam_abc}';"
                list_var = db.run_query(sql, fetch=True, namvar=False)
                dico_abc[nam_abc] = {}
                for var in list_var:
                    dico_abc[nam_abc][var[0]] = []
                    dico_abc[nam_abc]["order_{}".format(var[0])] = []

                sql = (
                    f"SELECT  var,value,id_order FROM {db.SCHEMA}.{table} WHERE nam_method='{metho}' "
                    f"and nam_abac='{nam_abc}' ORDER by id_order ;"
                )
                rows = db.run_query(sql, fetch=True, namvar=False)

                for row in rows:
                    dico_abc[nam_abc][row[0]].append(row[1])
                    dico_abc[nam_abc][f"order_{row[0]}"].append(row[2])

        return dico_abc

    def select_db_poly(self, db, table, where="", order=""):
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
        (results, nam_col) = db.run_query(
            sql.format(db.SCHEMA, table, where, order), fetch=True, namvar=True
        )
        cols = [col[0] for col in nam_col]
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

    def select_db_poly_elem(self,db, id_config, type_conf):
        """
        Get polygone list of hole
        :param id_config: index of hydraulic structure
        :param type_conf: 0: hole, 1:span
        :return:
        """
        where = " id_config={} and type={} ".format(id_config, type_conf)
        order = "id_elem"
        return self.select_db_poly(db,"struct_elem", where, order)["polygon"]

    def select_poly_elem(self, id_config, type_conf):
        if type_conf == 0:
            return self.list_poly_trav[id_config]
        elif type_conf == 1:
            return self.list_poly_pil[id_config]
        else:
            return {}