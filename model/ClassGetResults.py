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

"""

import datetime
import json
import os
import re
import pandas as pd

from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ..ClassMessage import ClassMessage
from ..Graphic.ClassResProfil import ClassResProfil


class ClassGetResults:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, mdb, dossier_file_masc, dbg):
        self.dbg = dbg
        self.mdb = mdb
        self.dossier_file_masc = dossier_file_masc
        self.basename = "mascaret"
        self.mess = ClassMessage()
        self.num_casier()

    def num_casier(self):
        """
        Compute dico contains the link between  xcas numero and model numero
        """
        casiers = self.mdb.select("basins", "active ORDER BY basinnum ")
        liaisons = self.mdb.select("links", "active ORDER BY linknum ")
        self.dico_basinnum = {}
        self.dico_linknum = {}
        if casiers:
            if len(casiers["basinnum"]) > 0:
                for id_mas, num_qgis in enumerate(casiers["basinnum"], 1):
                    self.dico_basinnum[id_mas] = num_qgis
            # # Creation du dictionnaire de numero de liaison entre mascaret (cle)
            # # et qgis (valeur)
            if len(liaisons["linknum"]) > 0:
                for id_mas, num_qgis in enumerate(liaisons["linknum"], 1):
                    self.dico_linknum[id_mas] = num_qgis

    def insert_id_run(self, run, scen):
        """
        creation run line in runs table
        :param run: run name
        :param scen: scenario name
        :return:
        """
        maintenant = datetime.datetime.utcnow()
        tab = {run: {"scenario": scen, "date": "{:%Y-%m-%d %H:%M}".format(maintenant)}}
        listimport = ["run", "scenario", "date"]

        self.mdb.insert("runs", tab, listimport)
        info = self.mdb.select(
            "runs", where="run='{}' AND scenario='{}'".format(run, scen), list_var=["id"]
        )

        id_run = info["id"][0]
        return id_run

    def import_results(self, run, scen, comments, path, date_debut=None):
        """
        import mascaret resultats
        :param run: (str) run name
        :param scen: (str) scenario name
        :param comments:(str) comments
        :param path: (str) path represitory
        :param date_debut: start time
        :return:
        """

        lia_cond = False
        cas_cond = False
        cond_tra = False

        for file in os.listdir(path):
            if file.split(".")[-1] == "liai_opt":
                lia_cond = True
            elif file.split(".")[-1] == "cas_opt":
                cas_cond = True
            elif file.split(".")[-1] == "tra_opt":
                cond_tra = True

        cond_casier = False
        if lia_cond and cas_cond:
            cond_casier = True

        id_run = self.insert_id_run(run, scen)
        self.lit_opt_new(id_run, date_debut, self.basename, comments=comments, tracer=cond_tra, casier=cond_casier)

        if os.path.isfile(os.path.join(path, "Fichier_Crete.csv")):
            self.read_mobil_gate_res(id_run)

        if os.path.isfile(os.path.join(path, "res_struct.res")):
            with open(os.path.join(path, "res_struct.res"), "r") as filein:
                dico = json.load(filein)
            self.stock_res_api(dico, id_run)

    def read_mobil_gate_res(self, id_run):
        """
        read result mobil_gate
        :param id_run: run if
        :return:
        """
        nomfich = os.path.join(self.dossier_file_masc, "Fichier_Crete.csv")
        if os.path.isfile(nomfich):
            try:
                # Read file
                dico_res = {}
                fich = open(nomfich, "r")

                for ligne in fich:
                    liste = ligne.split()
                    if len(liste) > 1:
                        nom = liste[2].strip()
                        if not (nom in dico_res.keys()):
                            dico_res[nom] = {"TIME": [], "ZSTR": []}
                        dico_res[nom]["TIME"].append(float(liste[0].strip()))
                        dico_res[nom]["ZSTR"].append(float(liste[1].strip()))
                fich.close()

                var_info = {
                    "var": "ZSTR",
                    "type_res": "weirs",
                    "name": "valve movement",
                    "type_var": "float",
                }
                id_var = self.mdb.check_id_var(var_info)
                values = []
                d_res = {}
                dico_pk = {}
                dico_time = {}
                for name in dico_res.keys():
                    where = "name = '{}'".format(name)
                    info = self.mdb.select(
                        "weirs", where=where, list_var=["gid", "abscissa"], order="gid"
                    )
                    if len(info["gid"]) < 1:
                        where = "name LIKE '{}%'".format(name)
                        info = self.mdb.select(
                            "weirs", where=where, list_var=["gid", "abscissa"], order="gid"
                        )
                    pknum = info["gid"][0]
                    d_res[(pknum, id_var)] = {
                        "t": dico_res[name]["TIME"],
                        "v": dico_res[name]["ZSTR"],
                    }
                    dico_pk[name] = pknum
                    dico_time[name] = dico_res[name]["TIME"]

                for (pk, var), v in d_res.items():
                    values.append(
                        [
                            id_run,
                            pk,
                            var,
                            "{" + ",".join(str(i) for i in v["t"]) + "}",
                            "{" + ",".join(str(i) for i in v["v"]) + "}",
                        ]
                    )
                if len(values) > 0:
                    self.mdb.run_query(
                        "INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(
                            self.mdb.SCHEMA
                        )
                        + "VALUES (%s, %s, %s, %s, %s)",
                        many=True,
                        list_many=values,
                    )

                if len(dico_res.keys()) > 0:
                    list_insert = [
                        [id_run, "weirs", "pknum", json.dumps(dico_pk)],
                        [id_run, "weirs", "time", json.dumps(dico_time)],
                        [id_run, "weirs", "var", json.dumps([id_var])],
                    ]
                    col_tab = ["id_runs", "type_res", "var", "val"]
                    self.mdb.insert_res("runs_graph", list_insert, col_tab)
            except Exception as e:
                txt = "Erreur load of mobil_gate results.\n"
                txt += e

                self.mess.add_mess('RMobGate', 'warning', txt)

    def new_read_opt(self, nom_fich, type_res, init_col=None):
        """
        Read opt file
        :param nom_fich: file name
        :param type_res: results type
        :param init_col: first column
        :return: dictionary of values
        """
        if init_col is None:
            init_col = []
        col = []
        var_del = []
        with open(nom_fich, "r") as source:
            var = source.readline()
            if var[:2] == "/*":
                # comment
                var = source.readline()
            ligne = source.readline()
            if type_res.split("_")[0] == "tracer":
                dico_tra = self.mdb.select(
                    "tracer_name",
                    where="type ='{}'".format(self.wq.cur_wq_mod),
                    order="id",
                    list_var=["sigle", "text"],
                )
                cpt_tra = 0
                while "[resultats]" not in ligne:
                    temp = ligne.replace('"', "").replace("NaN", "'NULL'").split(";")
                    if temp[1].strip().upper()[0] == "C":
                        if self.wq.cur_wq_mod != "TRANSPORT_PUR":
                            var_info = {"var": dico_tra["sigle"][cpt_tra], "type_res": type_res}
                        else:
                            var_info = {
                                "var": dico_tra["sigle"][cpt_tra],
                                "type_res": type_res,
                                "name": dico_tra["text"][cpt_tra],
                                "type_var": "float",
                            }
                        cpt_tra += 1
                    else:
                        var_info = {"var": temp[1].upper(), "type_res": type_res}
                    id_var = self.mdb.check_id_var(var_info)
                    # delete 'qtot' because of the same that 'q'
                    if temp[1].upper() == "QTOT":
                        var_del.append(id_var)
                    if id_var:
                        col.append(id_var)
                    else:
                        col.append(temp[1])
                    ligne = source.readline()
            else:
                while "[resultats]" not in ligne:
                    temp = ligne.replace('"', "").replace("NaN", "'NULL'").split(";")
                    var_info = {"var": temp[1].upper(), "type_res": type_res}
                    id_var = self.mdb.check_id_var(var_info)
                    # delete 'qtot' because of the same that 'q'
                    if temp[1].upper() == "QTOT":
                        var_del.append(id_var)

                    if id_var:
                        col.append(id_var)
                    else:
                        col.append(temp[1])
                    ligne = source.readline()

            if not init_col:
                col_tmp = ["TIME", "BRANCH", "SECTION", "PK"] + col
            else:
                col_tmp = init_col + col

            dico_val = {}
            for key in col_tmp:
                dico_val[key] = []

            data = pd.read_csv(source, delimiter=';', names=col_tmp)
            data = data.drop_duplicates()
            data = data.to_dict(orient='records')
            int_val = ["BRANCHE", "SECTION"]

            for ligne in data:
                for key in dico_val.keys():
                    # val = ligne[key].strip()
                    val = ligne[key]
                    if key == "PK":
                        val = round(float(val), 2)
                    elif key in int_val:
                        val = int(val)
                    elif key == "BNUM":
                        numero_masca = re.findall("\\d+", val)[0]
                        # convertit le numero masca en qgis
                        # (different si un casier inactif)
                        numero_qgis = str(self.dico_basinnum[int(numero_masca)])
                        val = float(numero_qgis)
                    elif key == "LNUM":
                        numero_masca = re.findall("\\d+", val)[0]
                        # convertit le numero masca en qgis
                        # (different si un link inactif)
                        numero_qgis = str(self.dico_linknum[int(numero_masca)])
                        val = float(numero_qgis)
                    else:
                        val = float(val)

                    dico_val[key].append(val)
        for id in var_del:
            if id:
                del dico_val[id]
        return dico_val

    def save_run_graph(self, val, id_run, typ_res, max=True):
        """save info for graph"""

        list_insert = []
        list_var = []
        for id in val.keys():
            if isinstance(id, int):
                list_var.append(id)
        list_var = list(set(list_var))
        # delete doublon list(set(my_list))
        list_insert.append([id_run, typ_res, "var", json.dumps(sorted(list_var))])
        list_insert.append([id_run, typ_res, "time", json.dumps(sorted(list(set(val["TIME"]))))])

        if typ_res == "opt":
            var_info = {"var": "ZMAX", "type_res": "opt"}
            id_zmax = self.mdb.check_id_var(var_info)
            # if zmax exist
            if id_zmax in list_var:
                dico_zmax = {}
                tmax = val["TIME"][-1]
                for i in range(len(val["TIME"]) - 1, -1, -1):
                    if val["TIME"][i] == tmax:
                        dico_zmax[val["PK"][i]] = val[id_zmax][i]
                    else:
                        break

                list_insert.append([id_run, typ_res, "zmax", json.dumps(dico_zmax)])
                key_pknum = "PK"
            else:
                var_info = {"var": "Z", "type_res": "opt"}
                id_z = self.mdb.check_id_var(var_info)
                if id_z in list_var and max:
                    dico_zmax = {}
                    for pknum in list(set(val["PK"])):
                        sql = (
                            "SELECT MAX(val) FROM {0}.results "
                            "WHERE var = {2} "
                            "AND id_runs={1} AND pknum ={3};".format(
                                self.mdb.SCHEMA, id_run, id_z, pknum
                            )
                        )
                        rows = self.mdb.run_query(sql, fetch=True)
                        try:
                            dico_zmax[pknum] = rows[0][0]
                        except Exception:
                            dico_zmax[pknum] = None

                    list_insert.append([id_run, typ_res, "zmax", json.dumps(dico_zmax)])
                    key_pknum = "PK"
            # add stockage plani
            if dico_zmax:
                cl_geo = ClassResProfil()
                dico_zmax = {str(key): item for key, item in dico_zmax.items()}
                txterr = cl_geo.plani_stock(dico_zmax, id_run, self.mdb)
                if txterr:
                    self.mess.add_mess('ClGeoPlani', 'debug', txterr)
                del cl_geo
        elif typ_res == "basin":
            key_pknum = "BNUM"
        elif typ_res == "link":
            key_pknum = "LNUM"
        elif "tracer_" in typ_res:
            key_pknum = "PK"
        list_insert.append(
            [id_run, typ_res, "pknum", json.dumps(sorted(list(set(val[key_pknum]))))]
        )

        col_tab = ["id_runs", "type_res", "var", "val"]
        if len(list_insert) > 0:
            self.mdb.insert_res("runs_graph", list_insert, col_tab)

    def lit_opt_new(
            self, id_run, date_debut, base_namefile, comments="", tracer=False, casier=False,
            cond_api=False, save_res_struct=[]
    ):
        """
        Read opt files and save in results table
        :param id_run: run index
        :param date_debut: initial date
        :param base_namefile: file name without extension
        :param comments: comments
        :param tracer: if tracers are actived
        :param casier: if basins are actived
        :return:
        """
        nom_fich = os.path.join(self.dossier_file_masc, base_namefile + ".opt")
        self.mess.add_mess('LoadOpt1', 'info', "Load data ....")
        if not os.path.isfile(nom_fich):
            txt = "Simulation Error: there aren't results"
            self.mess.add_mess('LoadOptFile', 'critic', txt)
            self.mdb.delete("runs", "id={}".format(id_run))
            return False
        # update do old results
        tab = {id_run: {}}
        if date_debut:
            tab[id_run]["init_date"] = "{:%Y-%m-%d %H:%M}".format(date_debut)
        if comments != "":
            tab[id_run]["comments"] = comments
        if tracer:
            tab[id_run]["wq"] = self.wq.cur_wq_mod
        if tab[id_run]:
            self.mdb.update("runs", tab, var="id")

        type_res = "opt"
        init_col = ["TIME", "BRANCH", "SECTION", "PK"]
        val_opt = self.new_read_opt(nom_fich, type_res, init_col)
        self.save_new_results(val_opt, id_run)
        self.save_run_graph(val_opt, id_run, type_res)
        del val_opt

        if casier:
            nom_fich_bas = os.path.join(self.dossier_file_masc, base_namefile + ".cas_opt")
            if not os.path.isfile(nom_fich_bas):
                txt = "Simulation Error: there aren't basin results"
                self.mess.add_mess('LoadOptCas', 'warning', txt)
            else:

                type_res = "basin"
                init_col = ["TIME", "BNUM"]

                val = self.new_read_opt(nom_fich_bas, type_res, init_col)
                self.save_new_results(val, id_run)
                self.save_run_graph(val, id_run, type_res)

                del val

            nom_fich_link = os.path.join(self.dossier_file_masc, base_namefile + ".liai_opt")
            if not os.path.isfile(nom_fich_link):
                txt = "Simulation Error: there aren't link results"
                self.mess.add_mess('LoadOptLink', 'warning', txt)
            else:
                type_res = "link"
                init_col = ["TIME", "LNUM"]
                val = self.new_read_opt(nom_fich_link, type_res, init_col)

                self.save_new_results(val, id_run)
                self.save_run_graph(val, id_run, type_res)
                del val
        if tracer:
            nom_fich_tra = os.path.join(self.dossier_file_masc, base_namefile + ".tra_opt")
            if not os.path.isfile(nom_fich_tra):
                txt = "Simulation Error: there aren't basin results"
                self.mess.add_mess('LoadOptWQ', 'warning', txt)
            else:
                init_col = ["TIME", "BRANCH", "SECTION", "PK"]
                type_res = "tracer_{}".format(self.wq.cur_wq_mod)

                val = self.new_read_opt(nom_fich_tra, type_res, init_col)
                self.save_new_results(val, id_run)
                self.save_run_graph(val, id_run, type_res)
                del val

        if cond_api and len(save_res_struct) >= 2:
            self.stock_res_api(save_res_struct[0], save_res_struct[1])

    def save_new_results(self, val, id_run):
        """
        Save values in results table
        :param val: (dict) values
        :param id_run: run index
        :return: True
        """
        val_keys = val.keys()
        if "PK" in val_keys:
            lpk = val["PK"]
        elif "BNUM" in val_keys:
            lpk = val["BNUM"]
        elif "LNUM" in val_keys:
            lpk = val["LNUM"]

        d_res = {}
        d_sect = {}
        for var in val_keys:
            if isinstance(var, int):
                for tps, pk, value in zip(val["TIME"], lpk, val[var]):
                    if (pk, var) not in d_res.keys():
                        d_res[(pk, var)] = {"t": list(), "v": list()}
                    d_res[(pk, var)]["t"].append(tps)
                    d_res[(pk, var)]["v"].append(value)

            elif var == "BRANCH":
                init_pk = lpk[0]
                cond = False
                for pk, bra, sect in zip(lpk, val["BRANCH"], val["SECTION"]):
                    if pk == init_pk and cond:
                        break
                    if bra not in d_sect.keys():
                        d_sect[bra] = {"sect": [], "pk": []}
                    d_sect[bra]["sect"].append(sect)
                    d_sect[bra]["pk"].append(pk)
                    cond = True

        values = list()
        for (pk, var), v in d_res.items():
            values.append(
                [
                    id_run,
                    pk,
                    var,
                    "{" + ",".join(str(i) for i in v["t"]) + "}",
                    "{" + ",".join(str(i) for i in v["v"]) + "}",
                ]
            )
        if len(values) > 0:
            self.mdb.run_query(
                "INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(
                    self.mdb.SCHEMA
                )
                + "VALUES (%s, %s, %s, %s, %s)",
                many=True,
                list_many=values,
            )

        values = list()
        for bra, v in d_sect.items():
            values.append(
                [
                    id_run,
                    bra,
                    "{" + ",".join(str(i) for i in v["sect"]) + "}",
                    "{" + ",".join(str(i) for i in v["pk"]) + "}",
                ]
            )
        rows = self.mdb.select_one("results_sect", where="id_runs={}".format(id_run), list_var=["id_runs"])
        if len(values) > 0 and rows is None:
            self.mdb.run_query(
                "INSERT INTO {}.results_sect(id_runs, branch, section, pk) ".format(self.mdb.SCHEMA)
                + "VALUES (%s, %s, %s, %s)",
                many=True,
                list_many=values,
            )

        return True

    def stock_res_api(self, dico, id_run):
        """Stock api results"""
        if len(dico) > 0:
            for key in dico.keys():
                if key == "STRUCT_FG":
                    self.res_fg(dico[key], id_run)
                if key == 'LINK_FG':
                    self.res_link_fg(dico[key], id_run)
                if key == 'WEIRS':
                    self.res_weirs_fg(dico[key], id_run)

    def res_weirs_fg(self, dico_res, id_run):
        """stock flood gate results"""

        values = []
        var_info = {'var': "ZSTR",
                    'type_res': 'weirs',
                    'name': 'Gate movement',
                    'type_var': 'float'}
        id_var_zlink = self.mdb.check_id_var(var_info)

        var_info = {'var': 'REGVAR',
                    'type_res': 'weirs',
                    'name': 'Variable of regulation',
                    'type_var': 'float'}
        id_var_reg = self.mdb.check_id_var(var_info)

        d_res = {}
        dico_pk = {}
        dico_time = {}

        for id_link in dico_res.keys():
            dico_pk[id_link] = id_link
            dico_time[id_link] =  dico_res[id_link]['TIME']
            d_res[(id_link, id_var_zlink)] = {'t': dico_res[id_link]['TIME'],
                                            'v': dico_res[id_link]["ZSTR"]}

            d_res[(id_link, id_var_reg)] = {'t': dico_res[id_link]['TIME'],
                                            'v': dico_res[id_link]['REGVAR']}
        for (pk, var), v in d_res.items():
            values.append([id_run, pk, var,
                           "{" + ','.join(str(i_t) for i_t in v['t']) + "}",
                           "{" + ','.join(str(i_v) for i_v in v['v']) + "}"])
        if len(values) > 0:
            self.mdb.run_query(
                "INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(self.mdb.SCHEMA) +
                "VALUES (%s, %s, %s, %s, %s)", many=True, list_many=values)

        if len(dico_res.keys()) > 0:
            list_insert = [[id_run, 'weirs', 'pknum', json.dumps(dico_pk)],
                           [id_run, 'weirs', 'time', json.dumps(dico_time)],
                           [id_run, 'weirs', 'var', json.dumps([id_var_zlink, id_var_reg])]]
            col_tab = ['id_runs', 'type_res', 'var', 'val']
            self.mdb.insert_res('runs_graph', list_insert, col_tab)


    def res_link_fg(self, dico_res, id_run):
        """stock flood gate results"""
        values = []
        var_info = {'var': 'ZLINK',
                    'type_res': 'link_fg',
                    'name': 'Gate movement',
                    'type_var': 'float'}
        id_var_zlink = self.mdb.check_id_var(var_info)

        var_info = {'var': 'CSECLINK',
                    'type_res': 'link_fg',
                    'name': 'Opening section of Gate for culvert',
                    'type_var': 'float'}
        id_var_csec = self.mdb.check_id_var(var_info)

        var_info = {'var': 'WIDTHLINK',
                    'type_res': 'link_fg',
                    'name': 'Width link',
                    'type_var': 'float'}
        id_var_width = self.mdb.check_id_var(var_info)

        var_info = {'var': 'REGVAR',
                    'type_res': 'link_fg',
                    'name': 'Variable of regulation',
                    'type_var': 'float'}
        id_var_reg = self.mdb.check_id_var(var_info)

        d_res = {}
        dico_pk = {}
        dico_time = {}

        for id_link in dico_res.keys():
            dico_pk[id_link] = id_link
            dico_time[id_link] =  dico_res[id_link]['TIME']
            d_res[(id_link, id_var_zlink)] = {'t': dico_res[id_link]['TIME'],
                                            'v': dico_res[id_link]['ZLINK']}
            d_res[(id_link, id_var_csec)] = {'t': dico_res[id_link]['TIME'],
                                              'v': dico_res[id_link]['CSECLINK']}
            d_res[(id_link, id_var_width)] = {'t': dico_res[id_link]['TIME'],
                                             'v': dico_res[id_link]['WIDTHLINK']}

            d_res[(id_link, id_var_reg)] = {'t': dico_res[id_link]['TIME'],
                                            'v': dico_res[id_link]['REGVAR']}
        for (pk, var), v in d_res.items():
            values.append([id_run, pk, var,
                           "{" + ','.join(str(i_t) for i_t in v['t']) + "}",
                           "{" + ','.join(str(i_v) for i_v in v['v']) + "}"])
        if len(values) > 0:
            self.mdb.run_query(
                "INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(self.mdb.SCHEMA) +
                "VALUES (%s, %s, %s, %s, %s)", many=True, list_many=values)

        if len(dico_res.keys()) > 0:
            list_insert = [[id_run, 'link_fg', 'pknum', json.dumps(dico_pk)],
                           [id_run, 'link_fg', 'time', json.dumps(dico_time)],
                           [id_run, 'link_fg', 'var', json.dumps([id_var_zlink, id_var_csec, id_var_width, id_var_reg])]]
            col_tab = ['id_runs', 'type_res', 'var', 'val']
            self.mdb.insert_res('runs_graph', list_insert, col_tab)


    def res_fg(self, dico_res, id_run):
        """stock flood gate results"""

        # colonnes = ['id_runs', 'time', 'pknum', 'var', 'val']
        colonnes = ["idruntpk", "var", "val"]
        values = []
        var_info = {
            "var": "ZSTR",
            "type_res": "struct",
            "name": "valve movement",
            "type_var": "float",
        }
        id_var = self.mdb.check_id_var(var_info)
        dico_pk = {}
        dico_time = {}
        d_res = {}
        for id_config in dico_res.keys():
            rows = self.mdb.select(
                "struct_config", where="id={}".format(id_config), list_var=["abscissa"]
            )
            pknum = rows["abscissa"][0]
            dico_pk[id_config] = pknum
            dico_time[id_config] = dico_res[id_config]["TIME"]
            d_res[(pknum, id_var)] = {
                "t": dico_res[id_config]["TIME"],
                "v": dico_res[id_config]["ZSTR"],
            }

        for (pk, var), v in d_res.items():
            values.append(
                [
                    id_run,
                    pk,
                    var,
                    "{" + ",".join(str(i_t) for i_t in v["t"]) + "}",
                    "{" + ",".join(str(i_v) for i_v in v["v"]) + "}",
                ]
            )

        if len(values) > 0:
            self.mdb.run_query(
                "INSERT INTO {}.results_by_pk (id_runs, pknum, var, time, val) ".format(
                    self.mdb.SCHEMA
                )
                + "VALUES (%s, %s, %s, %s, %s)",
                many=True,
                list_many=values,
            )

        if len(dico_res.keys()) > 0:
            list_insert = [
                [id_run, "struct", "pknum", json.dumps(dico_pk)],
                [id_run, "struct", "time", json.dumps(dico_time)],
                [id_run, "struct", "var", json.dumps([id_var])],
            ]
            col_tab = ["id_runs", "type_res", "var", "val"]
            self.mdb.insert_res("runs_graph", list_insert, col_tab)
