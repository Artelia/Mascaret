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
import re

import json

from lib.Function import del_symbol
from lib.HydroLawsDialog import dico_typ_law
import datetime
import os

from lib.model.utils_model_file import backup_file

class ClassBCWriter:


    def __init__(self, mdb, folder, mess=None):
        self.mdb = mdb
        self.mess = mess
        self.folder = folder

    # ************   LAW FILE   ********************************************************************
    def creer_loi(self, nom, tab, type_, init=False):
        """
        Create a law file (.loi) with the given name and data.
        :param nom (str): Law name
        :param tab (dict): Law data
        :param type_ (int): Law type
        :param init (bool): If True, the computation is an initialization (default: False)
        :return: None
        """
        if init:
            nom = nom + "_init"
        with open(os.path.join(self.folder, del_symbol(nom) + ".loi"), "w") as fich:
            fich.write("# " + nom + "\n")
            if type_ == 1:
                fich.write("# Temps (S) Debit\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {flowrate:.6f}\n"
            elif type_ == 2:
                fich.write("# Temps (S) Cote\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {z:.6f}\n"
            elif type_ == 3:
                fich.write("# Temps (S) Cote Debit\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {z:.6f} {flowrate:.6f}\n"
            elif type_ == 4:
                fich.write("# Debit Cote\n")
                chaine = " {flowrate:.3f} {z:.6f}\n"
            elif type_ == 5:
                fich.write("# Cote Debit\n")
                chaine = " {z:.6f} {flowrate:.6f}\n"
            elif type_ == 6:
                fich.write("# Debit Cote_Aval Cote_Amont\n")
                chaine = " {flowrate:.6f} {z_downstream:.6f} {z_upstream:.6f}\n"
            elif type_ == 7:
                fich.write("# Temps (s) Cote inférieur Cote supérieur\n")
                fich.write(" S\n")
                chaine = " {time:.3f} {z_lower:.6f} {z_up:.6f}\n"
                #   example:  print("{0} :\n \t Time : {1}\n \t
                #                        Upstream Water Level{2}\n \t  "
                #                       "Downstream Water Level :{3}"
                #                       .format(nom,tab["temps"],
                #                       tab["cote_amont"], tab["cote_aval"]))
            n = len(list(tab.values())[0])
            for i in range(n):
                dico = {k: v[i] for k, v in tab.items()}
                fich.write(chaine.format(**dico))
    
    
    def obs_to_loi(self,  dict_lois, date_debut, date_fin, par):
        """
        Create a law file from observation data.
        :param dict_lois (dict): Dictionary of law definitions
        :param date_debut (datetime): Start date for observation
        :param date_fin (datetime): End date for observation
        :param par (dict): Parameters dictionary
        :return: par (dict): Updated parameters dictionary
        """
        # pattern = re.compile('([A-Z][0-9]{7})\\[t([+-][0-9]+)?\\]')
        pattern = re.compile(r"(\\w+)\\[t([+-][0-9]+)?\\]")
        somme = 0
        debit_prec = 0
        for nom, loi in dict_lois.items():
            if loi["type"] == 1:
                type_ = "Q"
            elif loi["type"] == 2:
                type_ = "H"
            else:
                continue
            if not loi.get("formule"):
                continue
            valeur_init = None
            liste_stations = pattern.findall(loi["formule"])
            # get observation each station
            obs_stations = {}
            err_critic = False
            for cd_hydro, delta in liste_stations:
                delta_h = int(delta) if delta else 0
                dt = datetime.timedelta(hours=delta_h)
    
                sql_tab = ("SELECT o.code, o.type, d.date, d.valeur "
                           "FROM {0}.observations o, "
                           "LATERAL UNNEST(o.date, o.valeur) AS d(date, valeur) "
                           "WHERE o.code = '{1}' AND o.type = '{2}' "
                           "AND d.date >= '{3:%Y-%m-%d %H:%M}' "
                           " AND d.date <= COALESCE(( "
                           " SELECT MIN(d2.date) "
                           " FROM {0}.observations o2, "
                           "LATERAL UNNEST(o2.date) AS d2(date) "
                           "WHERE o2.code = '{1}' AND o2.type = '{2}' "
                           " AND d2.date >= '{4:%Y-%m-%d %H:%M}' "
                           " ), '{4:%Y-%m-%d %H:%M}') "
                           "ORDER BY d.date;".format(
                    self.mdb.SCHEMA, cd_hydro, type_, date_debut + dt, date_fin + dt
                ))
    
                obs_stations[cd_hydro] = self.mdb.query_todico(sql_tab)
                if not obs_stations[cd_hydro]["date"]:
                    if self.mess:
                        self.mess.add_mess('NoInitSteady', 'critic',
                                      f"Error: Please check if law for {nom} object is correct.\n "
                                      f"No observations found for station {cd_hydro} "
                                      "on the dates: {0:%Y-%m-%d %H:%M} - {1:%Y-%m-%d %H:%M}"
                                      "".format(date_debut + dt, date_fin + dt))
                    err_critic = True
                    continue
            if err_critic:
                return
                # ref dates and station (first station)
            ref_station, ref_delta = liste_stations[0]
            ref_delta_h = int(ref_delta) if ref_delta else 0
            ref_dates = [d - datetime.timedelta(hours=ref_delta_h) for d in obs_stations[ref_station]["date"]]
    
            fichier_loi = os.path.join(self.folder, del_symbol(nom) + ".loi")
    
            with open(fichier_loi, "w") as fich_sortie:
                fich_sortie.write("# {0}\n".format(nom))
                if type_ == "Q":
                    fich_sortie.write("# Temps (H) Debit\n")
                else:
                    fich_sortie.write("# Temps (H) Hauteur\n")
                fich_sortie.write(" H \n")
                for t in ref_dates:
                    calc = loi["formule"]
                    for cd_hydro, delta in liste_stations:
                        delta_h = int(delta) if delta else 0
                        t2 = t + datetime.timedelta(hours=delta_h)
                        val = None
                        if t2 in obs_stations[cd_hydro]["date"]:
                            i = obs_stations[cd_hydro]["date"].index(t2)
                            val = obs_stations[cd_hydro]["valeur"][i]
                        calc = pattern.sub(str(val), calc, 1)
                    try:
                        resultat = eval(calc)
                    except Exception:
                        resultat = None
    
                    if resultat is not None:
                        if valeur_init is None:
                            valeur_init = resultat
                            somme += resultat
                        tps = (t - date_debut).total_seconds() / 3600
                        chaine = "  {0:4.3f}   {1:3.6f}\n"
                        fich_sortie.write(chaine.format(tps, resultat))
    
            # check law after write
            initime = round((ref_dates[0] - date_debut).total_seconds() / 3600, 3) * 3600
            lasttime = round((ref_dates[-1] - date_debut).total_seconds() / 3600, 3) * 3600
    
            self.check_timelaw(par, nom, initime, lasttime)
    
            if valeur_init is not None:
                if type_ == "Q":
                    tab = {"time": [0, 3600], "flowrate": [valeur_init, valeur_init]}
                    self.creer_loi(nom, tab, 1, init=True)
                else:
                    tab = {"time": [0, 3600], "z": [valeur_init, valeur_init]}
                    self.creer_loi(nom, tab, 2, init=True)
            else:
                par["initialisationAuto"] = False
                if self.mess:
                    self.mess.add_mess(
                        "NoInitSteady", "Warning", "No initialisation because of no SteadyValue"
                    )
        valeur_init = None
    
        for nom, loi in dict_lois.items():
            if not loi["type"] in (1, 2) or (loi["type"] in (1, 2) and not loi["formule"]):
                # create other law
                tab = self.get_laws(
                    nom, loi["type"], obs=True, date_deb=date_debut, date_fin=date_fin
                )
                if tab:
                    self.creer_loi(nom, tab, loi["type"])
                    if "time" in tab.keys():
                        initime = round(tab["time"][0], 3)
                        lasttime = round(tab["time"][-1], 3)
                        self.check_timelaw(par, nom, initime, lasttime)
                else:
                    if self.mess:
                        self.mess.add_mess(
                            "CreatLaw_{}".format(nom),
                            "critic",
                            "The law for {} is not create.".format(nom),
                        )
                    continue
                # create init law
                if loi["type"] in [1, 2, 4]:  # , 5]: # car 5 mascaret plante à l'init
                    self.creer_loi(nom, tab, loi["type"], init=True)
                elif loi["type"] in [5] and loi["couche"] == "extremites":
                    for c, d in zip(tab["z"], tab["flowrate"]):
                        if debit_prec > 0 and d > somme:
                            valeur_init = (c - cote_prec) / (d - debit_prec) * (
                                    somme - debit_prec
                            ) + cote_prec
                            break
                        cote_prec, debit_prec = c, d
                    if valeur_init is not None:
                        tab = {"time": [0, 3600], "z": [valeur_init, valeur_init]}
                        self.creer_loi(nom, tab, 2, init=True)
                else:
                    par["initialisationAuto"] = False
                    if self.mess:
                        self.mess.add_mess(
                            "NoInitSteady", "Warning", "No initialisation because of no SteadyValue"
                        )
        return par
    
    
    def check_timelaw(self,par, name, initime, lasttime):
        """_
        Check the time law for initialization and last time.
        :param par (dict): Parameters dictionary
        :param name (str): Name of the law
        :param initime (float): Initial time in seconds
        :param lasttime (float): Last time in seconds
        :return: (bool) True if there is an error, False otherwise
        """
        cond = False
        if par["tempsInit"] < initime:
            cond = True
            if self.mess:
                self.mess.add_mess(
                    "tLaw_{}".format(name), "critic", " Error law {} on the Initial Time".format(name)
                )
    
        if par["critereArret"] == 1:
            # tmax
            if par["tempsMax"] > lasttime:
                cond = True
                if self.mess:
                    self.mess.add_mess(
                        "tLaw_{}".format(name), "critic", " Error law {} on the Last Time".format(name)
                    )
    
        elif par["critereArret"] == 2:
            # nb iterration
            if par["nbPasTemps"] * par["pasTemps"] > lasttime:
                cond = True
                if self.mess:
                    self.mess.add_mess(
                        "tLaw_{}".format(name), "critic", " Error law {} on the Last Time".format(name)
                    )
    
        return cond
    
    
    def get_laws(self, name_obj, typ_law, obs=False, date_deb=None, date_fin=None):
        """
        Get the law for a given object and type.
        If obs is True, it will filter by date_deb and date_fin.
        :param name_obj (object): Name of the object
        :param typ_law (str): Type of the law
        :param obs (bool): If True, filter by date
        :param date_deb (datetime): Start date for filtering
        :param date_fin (datetime): End date for filtering
        :return: (dict) Law data or None if not found
        """
    
        try:
            if obs and date_deb is not None and date_fin is not None:
                condition = """geom_obj='{0}' 
                                 AND id_law_type = {1}
                                 AND starttime <= '{2:%Y-%m-%d %H:%M}' 
                                 AND endtime >= '{3:%Y-%m-%d %H:%M}'
                                 AND active
                                 """.format(
                    name_obj, typ_law, date_deb, date_fin
                )
    
            else:
                condition = "geom_obj='{0}' AND id_law_type={1} AND active".format(
                    name_obj, typ_law
                )
    
            config = self.mdb.select_one("law_config", condition)
            if config:
                values = self.mdb.select(
                    "law_values",
                    where="id_law={}".format(config["id"]),
                    order="id_var, id_order",
                    list_var=["id_var", "id_order", "value"],
                )
                lst_var = [tmp["code"] for tmp in dico_typ_law[typ_law]["var"]]
                lst_idvar = [id for id, tmp in enumerate(dico_typ_law[typ_law]["var"])]
    
                tab = {key: [] for key in lst_var}
                conv_idvar = {id: lst_var[i] for i, id in enumerate(lst_idvar)}
    
                for value, id_var in zip(values["value"], values["id_var"]):
                    tab[conv_idvar[id_var]].append(float(value))
    
                return tab
            else:
                err = "Error: Please check if law for {0} object " "is correct. \n".format(name_obj)
                if self.mess:
                    self.mess.add_mess("obsLaw_{}".format(name_obj), "critic", err)
                return None
    
        except Exception as e:
            err = "Error: Please check if law for {0} object " "is correct. \n".format(name_obj)
            err += str(e)
            if self.mess:
                self.mess.add_mess("obsLaw_{}".format(name_obj), "critic", err)
            return None
    
    
    def classic_law(self, par, dict_lois):
        """
        Create the law for the classic case
        :param par: dict contains the parameters
        :param dict_lois: dict contains the law
        :return: dict (par)
        """
        for nom, l in dict_lois.items():
            # dictLois.items() extremities liste
    
            tab = self.get_laws(nom, l["type"])
            if tab:
                self.creer_loi(nom, tab, l["type"])
                if "time" in tab.keys():
                    initime = round(tab["time"][0], 3)
                    lasttime = round(tab["time"][-1], 3)
                    self.check_timelaw(par, nom, initime, lasttime)
            else:
                if self.mess:
                    self.mess.add_mess(
                        "CreatLaw_{}".format(nom), "critic", "The law for {} is not create.".format(nom)
                    )
    
            if "valeurperm" not in l.keys():
                continue
    
            # nom = nom + "_init"
            if l["valeurperm"]:
                if l["type"] == 1:
                    tab = {"time": [0, 3600], "flowrate": [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 1, init=True)
                elif l["type"] == 2:
                    tab = {"time": [0, 3600], "z": [l["valeurperm"]] * 2}
                    self.creer_loi(nom, tab, 2, init=True)
                elif l["type"] in [4, 5]:
                    self.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    if self.mess:
                        self.mess.add_mess(
                            "NoInitSteady", "Warning", "No initialisation because of no SteadyValue"
                        )
            else:
                if l["type"] in [4, 5]:
                    self.creer_loi(nom, tab, l["type"], init=True)
                else:
                    par["initialisationAuto"] = False
                    txt = "No initialisation because of no steady value set for {} condition".format(
                        nom
                    ) + 'Set "steadyValue" in extremities layer for entity {}'.format(nom)
                    if self.mess:
                        self.mess.add_mess(txt, "NoInitUnsteady", "warning")
        return par
    
    
    # ************   LIG FILE   ********************************************************************
    
    def opt_to_lig(self, id_run,  lig_filename='mascaret.lig'):
        """
        Creation of .lig file
        :param id_run (int): run index
        :param base_namefiles (str): base name for the lig file
        :return: None"""
    
        lig_path = os.path.join(self.folder, lig_filename)
        backup_file(lig_path, ".lig")
    
        result = self.get_for_lig(self.mdb,id_run)
        if not result:
            return None
        i1 = {}
        i2 = {}
        for section, branche in zip(result["section"], result["branche"]):
            if branche not in i1.keys():
                i1[branche] = 9999999
            if branche not in i2.keys():
                i2[branche] = -9999999
            i1[branche] = min(i1[branche], section)
            i2[branche] = max(i2[branche], section)
    
        nb_bief = len(set(result["branche"]))
        section = sorted(set(result["section"]))
    
        imax = len(section)
        i1i2 = []
        for b in sorted(i1.keys()):
            i1i2.append(str(i1[b]))
            i1i2.append(str(i2[b]))
    
        with open(lig_path, "w") as fich:
            date = datetime.datetime.now()
            fich.write("RESULTATS CALCUL,DATE :  {0:%d/%m/%y %H:%M}\n".format(date))
            fich.write("FICHIER RESULTAT MASCARET{0}\n".format(" " * 47))
            fich.write("{0} \n".format("-" * 71))
            fich.write(" IMAX  ={0:5d} NBBIEF={1:5d}\n".format(int(imax), int(nb_bief)))
    
            chaine = [""]
            for k in range(0, len(i1i2), 10):
                chaine.append("I1,I2 =")
                for i in range(k, k + 10):
                    if i < len(i1i2):
                        chaine.append("{0:4}".format(i1i2[i]))
                chaine.append("\n")
            fich.write(" ".join(chaine))
    
            for k in ["X", "Z", "Q"]:
                fich.write(" " + k + "\n")
                long = 0
                for x in result[k]:
                    fich.write("{:13.2f}".format(x))
                    long += 1
                    if long == 5:
                        fich.write("\n")
                        long = 0
    
                if long != 0:
                    fich.write("\n")
    
            fich.write(" FIN\n")
    
    
    def get_for_lig(self, id_run):
        """
        Get value to create the lig file
           :param id_run (int): run index
           :return: (dict) return value to create the lig file
        """
        result = {}
        try:
            var = self.mdb.select("results_var", "type_res = 'opt'", "id", ["id", "var"])
            idz = var["id"][var["var"].index("Z")]
            idq = var["id"][var["var"].index("Q")]
            t_max = self.mdb.select_max(
                "time", "results", "var = {}  AND id_runs = {} ".format(idz, id_run)
            )
            if t_max is None:
                txt = "No previous results to create the .lig file."
                if self.mess:
                    self.mess.add_mess("LigFile", "critic", txt)
                return None
            value = self.mdb.select(
                "results",
                "var = {} AND id_runs = {}  " "AND time = {}".format(idz, id_run, t_max),
                "pknum",
                ["val"],
            )
            result["Z"] = value["val"]
            value = self.mdb.select(
                "results",
                "var = {} AND id_runs = {} " "AND time = {}".format(idq, id_run, t_max),
                "pknum",
                ["val"],
            )
            result["Q"] = value["val"]
    
            value = self.mdb.select(
                "results_sect", "id_runs = {}".format(id_run), "pk", ["pk", "branch", "section"]
            )
            result["X"] = []
            result["section"] = []
            result["branche"] = []
            for idx, pk in enumerate(value["pk"]):
                result["X"] += pk
                result["section"] += value["section"][idx]
                result["branche"] += value["branch"] * len(pk)
            del value
        except Exception:
            txt = "No results for initialisation"
            if self.mess:
                self.mess.add_mess("LigFile", "critic", txt)
            return None
    
        return result
    
    # ************   Mobile Structur FILE   ********************************************************************
    
    def create_mobil_gate_file(self):
        """
        create the mobile dam file (Fichier_Barrage_Mobile.txt)
        """
    
        info = self.mdb.select(
            "weirs", where="active_mob = true", list_var=["method_mob", "gid", "name", "z_crest"], order="gid"
        )
        if info:
            try:
                nomfich = os.path.join(self.folder, "Fichier_Barrage_Mobile.txt")
    
                if os.path.isfile(nomfich):
                    os.remove(nomfich)
                fich = open(nomfich, "w")
    
                for i, idw in enumerate(info["gid"]):
                    if info["method_mob"][i] == "1":
                        rows = self.mdb.select(
                            "weirs_mob_val",
                            where="id_weirs= {} AND (name_var='TIMEZ' OR name_var='VALUEZ')".format(
                                idw
                            ),
                            order="name_var, id_order",
                        )
                        if len(rows["id_weirs"]) > 0:
                            nbt = max(rows["id_order"]) + 1
                            if nbt < 501:
                                fich.write("{} {}\n".format(info["name"][i].replace(" ", "_"), nbt))
                                fich.write("methode 1\n")
                                fich.write("T(s)\n")
                                for j in range(nbt):
                                    fich.write("{} ".format(rows["value"][j]))
                                fich.write("\n")
                                fich.write("Zcrete(ngf)\n")
                                for j in range(nbt):
                                    fich.write("{} ".format(rows["value"][j + nbt]))
                                fich.write("\n")
                            else:
                                txt = (
                                    "Value number is superior to 500 "
                                    "for {} weirs.\n"
                                    "The weir is ignored.".format(info["name"][i])
                                )
                                if self.mess:
                                    self.mess.add_mess(
                                        "MobGate_{}".format(info["name"][i]), "warning", txt
                                    )
                        else:
                            txt = "There aren't value in {} weirs".format(info["name"][i])
                            if self.mess:
                                self.mess.add_mess("MobGate_{}".format(info["name"][i]), "warning", txt)
    
                    elif info["method_mob"][i] == "2":
                        rows = self.mdb.select(
                            "weirs_mob_val",
                            where="id_weirs= {} AND name_var!='TIMEZ' AND name_var!='VALUEZ'".format(
                                idw
                            ),
                        )
                        if len(rows["id_weirs"]) > 0:
                            fich.write("{} {}\n".format(info["name"][i].replace(" ", "_"), idw))
                            fich.write("methode 2\n")
                            fich.write("Zregulation Zbas Zhaut (m ngf)\n")
                            fich.write(
                                "{} {} {}\n".format(
                                    rows["value"][rows["name_var"].index("VREGCLOS")],
                                    info["z_crest"][i],  # ZBAS
                                    rows["value"][rows["name_var"].index('ZMAXFG')],
                                )
                            )
                            fich.write("Vabaissement Vrehaussement m/s\n")
                            fich.write(
                                "{} {}\n".format(
                                    rows["value"][rows["name_var"].index("VELOFGOPEN")],
                                    rows["value"][rows["name_var"].index("VELOFGCLOSE")],
                                )
                            )
                    else:
                        txt = "There aren't value in {} weirs".format(info["name"][i])
                        if self.mess:
                            self.mess.add_mess("MobGate_{}".format(info["name"][i]), "warning", txt)
    
                fich.close()
                if self.mess:
                    self.mess.add_mess("MobGate", "info", "Creation the dam is done")
    
            except Exception as e:
                err = f"Error: save the dam file{str(e)}"
                if self.mess:
                    self.mess.add_mess("MobGateFile", "critic", err)
    
    
    def creat_file_no_keep_break(self, filename="no_keep_break.json"):
        """
        Get the weirs is no permanent break and create json
        Args:
            :param name: file name, default no_keep_break.json
         Return :
            :return: return value to create the no_keep_break file
    
        """
        name = os.path.join(self.folder,  filename)
    
        param = {}
        lst_get = [('weirs', 'gid'), ('struct_config', 'id')]
        for tab, var in lst_get:
            sql = (
                f"SELECT {var}, name, branchnum, abscissa, erase_flag FROM {self.mdb.SCHEMA}.{tab} "
                f"WHERE active ORDER BY {var};"
            )
            rows = self.mdb.run_query(sql, fetch=True)
            if rows:
                for row in rows:
                    # "name, branchnum, abscissa"
                    if row[4]:
                        param[row[0]] = ((row[1], row[2], row[3]), row[4])
        if param:
            with open(name, "w") as file:
                json.dump(param, file)
