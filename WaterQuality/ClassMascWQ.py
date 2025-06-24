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
comment:

"""
import os

from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from .ClassTableWQ import ClassTableWQ
from ..Function import interpole, del_symbol


class ClassMascWQ:
    def __init__(self, main, file):
        """

        :param main: main program
        :param mod: tracer mod
        :param file: repertory Mascaret
        """
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.schema = self.mdb.SCHEMA
        self.iface = self.mgis.iface

        self.tbwq = ClassTableWQ(self.mgis, self.mdb)
        self.dico_phy = self.tbwq.dico_phy
        self.dossier_file_masc = file

        sql = "SELECT {} FROM {}.parametres WHERE parametre = 'modeleQualiteEau'".format(
            "steady", self.schema
        )

        result = self.mdb.run_query(sql, fetch=True)
        if not result:
            val = 1
        else:
            val = result[0][0]
        self.cur_wq_mod = self.tbwq.dico_wq_mod[int(val)]
        self.cur_wq_mod_int = int(val)

    def create_filephy(self, dossier=None):
        """creation .phy file"""
        if dossier is None:
            dossier = self.dossier_file_masc
        where = "type = '{}'".format(self.cur_wq_mod)
        order = "id"
        result = self.mdb.select("tracer_physic", where, order)
        # entetfr = u": NOMBRE DE PARAMETRES PHYSIQUES"
        entet = ": NUMBER OF PHYSICAL PARAMETERS"
        # with open(os.path.join(self.dossier_file_masc, self.cur_wq_mod.lower() + '.phy'), 'w') as fich:
        with open(os.path.join(dossier, "mascaret.phy"), "w") as fich:
            fich.write("{} {}\n".format(len(self.dico_phy[self.cur_wq_mod]["physic"]), entet))
            for i, phy in enumerate(self.dico_phy[self.cur_wq_mod]["physic"]):
                idx = result["sigle"].index(phy["sigle"])
                fich.write("{} : {}\n".format(result["value"][idx], result["text"][idx]))

    def law_tracer(self, dossier=None):
        """creation of law file for tracer"""
        if dossier is None:
            dossier = self.dossier_file_masc
        # init_case=True

        extrem = self.mdb.select("extremities")
        lateral = self.mdb.select("tracer_lateral_inflows")
        dict_loi_tr = {}
        list_loi = []

        for i, cond in enumerate(extrem["active"]):
            if cond:
                list_loi.append(extrem["law_wq"][i])
                dict_loi_tr[extrem["law_wq"][i]] = {
                    "source": False,
                    "type": extrem["tracer_boundary_condition_type"][i],
                }

        for i, cond in enumerate(lateral["active"]):
            if cond:
                list_loi.append(lateral["law_wq"][i])
                dict_loi_tr[extrem["law_wq"][i]] = {
                    "source": True,
                    "type": lateral["typesources"][i],
                }

        if list_loi:
            where = "type = '{}'".format(self.cur_wq_mod)
            order = "id"
            list_trac = self.mdb.select("tracer_name", where, order)
            for name in list_loi:
                order = "id"
                where = "type = '{}' AND name = '{}'".format(self.cur_wq_mod_int, name)
                loi_trac = self.mdb.select("tracer_config", where, order)
                if not loi_trac["id"]:
                    self.mgis.add_info(
                        "The <<{}>> law doesn't exist. Please check  laws. ".format(name)
                    )
                else:
                    order = 'ORDER BY "time",id_trac'
                    where = "WHERE id_config= '{}' ".format(loi_trac["id"][0])
                    sql = """SELECT DISTINCT id_trac,time,value FROM {0}.{1} {2} {3}"""
                    loi_val, col = self.mdb.run_query(
                        sql.format(self.mdb.SCHEMA, "laws_wq", where, order),
                        fetch=True,
                        namvar=True,
                    )
                    # write law
                    fich = open(os.path.join(dossier, del_symbol(name.lower()) + "_tra.loi"), "w")
                    header = "# {}\n".format(name)
                    header += "# Times (s) "
                    for sigle in list_trac["sigle"]:
                        header += "C_{} ".format(sigle)

                    header += "\n"
                    header += "         S\n"
                    fich.write(header)
                    t_pre = loi_val[0][1]
                    ligne = "{} ".format(t_pre)
                    for id, temps, val in loi_val:
                        if t_pre != temps:
                            fich.write(ligne + "\n")
                            t_pre = temps
                            ligne = "{} {} ".format(t_pre, val)
                        else:
                            ligne += "{} ".format(val)
                    fich.write(ligne)
                    fich.close()
                    # # case Steady
                    # if init_case:
                    #     # initial_ law with first value
                    #
                    #     fich = open(os.path.join(dossier, del_symbol(name.lower()) + '_init_tra.loi'), 'w')
                    #     header = '# {}\n'.format(name)
                    #     header += '# Times (s) '
                    #     for sigle in list_trac['sigle']:
                    #         header += 'C_{} '.format(sigle)
                    #
                    #     header += '\n'
                    #     header += '         S\n'
                    #     fich.write(header)
                    #     t_w=[0, 3600]
                    #     maxid=len(list_trac['sigle'])
                    #     vals=loi_val[0:maxid]
                    #     for time in t_w:
                    #         ligne = '{} '.format(time)
                    #         for id, temps, val in vals:
                    #             ligne += '{} '.format(val)
                    #         ligne += '\n'
                    #         fich.write(ligne)
                    #     fich.close()
        return dict_loi_tr

    def init_conc_tracer(self, dossier=None):
        """creation of initial concentration file for tracer"""
        if dossier is None:
            dossier = self.dossier_file_masc
        order = "id"
        where = "type = '{}' AND active=true".format(self.cur_wq_mod_int)
        init_trac = self.mdb.select("init_conc_config", where, order)
        if not init_trac["id"]:
            self.mgis.add_info("Warning: Please select the initial conditions for tracers")
            return
        order = "ORDER BY bief,abscissa,id_trac"
        where = "WHERE id_config= '{}' ".format(init_trac["id"][0])
        sql = """SELECT DISTINCT id_trac,bief,abscissa,value FROM {0}.{1} {2} {3}"""

        init_val, col = self.mdb.run_query(
            sql.format(self.mdb.SCHEMA, "init_conc_wq", where, order), fetch=True, namvar=True
        )
        if init_val == [] or init_val is None:
            self.mgis.add_info("Warning: Please fill the initial conditions for tracers")
            return
        # fich = open(os.path.join(self.dossier_file_masc, self.cur_wq_mod.lower() + '.conc'), 'w')
        fich = open(os.path.join(dossier, "mascaret.conc"), "w")

        fich.write("[variables]\n")
        for i, var in enumerate(self.dico_phy[self.cur_wq_mod]["tracer"]):
            fich.write('"{}";"C{}";"";11\n'.format(var["text"], i + 1))

        fich.write("[resultats]")
        id_pre = init_val[0][1]
        abs_pre = init_val[0][2]
        ligne = ""
        first = True
        for i, val in enumerate(init_val):
            if val[3] is None:
                val[3] = 0
            if id_pre != val[1] or abs_pre != val[2] or first:
                first = False
                fich.write(ligne + "\n")
                id_pre = val[1]
                abs_pre = val[2]
                ligne = '        0.0;"  {}";"   {}";  {};  {};'.format(
                    val[1], i + 1, val[2], val[3]
                )
            else:
                ligne += "  {};".format(val[3])
        fich.write(ligne)
        fich.close()

    def create_filemet(self, dossier=None, typ_time=None, datefirst=None, dateend=None):
        """creation .met file"""
        exit_satus = False
        if dossier is None:
            dossier = self.dossier_file_masc
        order = "id"
        where = "active=true"
        meteo_trac = self.mdb.select("meteo_config", where, order)
        if not meteo_trac["id"]:
            txt = ("Please select the meteo configuration for tracers")
            exit_satus = True
            return exit_satus, txt
        deb_time = None
        end_time = None
        if typ_time == "date" and meteo_trac["starttime"][0] is not None:
            duree = int((dateend - datefirst).total_seconds())
            if duree < 0:
                txt = ("Scenario date aren't correct.")
                exit_satus = True
                return exit_satus, txt
            dif_time = int((datefirst - meteo_trac["starttime"][0]).total_seconds())
            if dif_time < 0:
                txt = ("Date for meteo law aren't correct.")
                exit_satus = True
                return exit_satus, txt
            deb_time = dif_time
            end_time = dif_time + duree

        order = "ORDER BY time,id_var"
        where = "WHERE id_config= '{}' ".format(meteo_trac["id"][0])
        if deb_time is not None and end_time is not None:
            where += "AND time >= {} AND time < {} ".format(deb_time, end_time)
        else:
            deb_time = 0
        sql = """SELECT DISTINCT id_var,time,value FROM {0}.{1} {2} {3}"""
        #
        meteo_val, col = self.mdb.run_query(
            sql.format(self.mdb.SCHEMA, "laws_meteo", where, order), fetch=True, namvar=True
        )

        if meteo_val == [] or meteo_val is None:
            txt = ("Please fill the meteo conditions for tracers")
            exit_satus = True
            return exit_satus, txt

        fich = open(os.path.join(dossier, "mascaret.met"), "w")

        header = "# {}\n".format(meteo_trac["name"][0])
        header += "# Times (s) "
        for info in self.tbwq.dico_meteo:
            header += "{} ".format(info["name"])

        header += "\n"
        header += "         S\n"
        fich.write(header)

        t_pre = meteo_val[0][1] - deb_time
        if t_pre > 0:
            order = "ORDER BY time"
            sql = """SELECT DISTINCT time FROM {0}.{1} {2}"""
            #
            temps_list = self.mdb.run_query(
                sql.format(self.mdb.SCHEMA, "laws_meteo", order), fetch=True
            )
            time_inter = 0
            for i, time in enumerate(temps_list):
                if time[0] >= deb_time:
                    time_inter = temps_list[i - 1][0]
                    break
            where = "WHERE id_config= '{}' AND time= '{}'".format(meteo_trac["id"][0], time_inter)
            order = "ORDER BY id_var"
            sql = """SELECT DISTINCT  id_var,value FROM {0}.{1} {2} {3}"""

            val = self.mdb.run_query(
                sql.format(self.mdb.SCHEMA, "laws_meteo", where, order), fetch=True
            )
            list_val = []
            for id, valu in val:
                valf = interpole(deb_time, [time_inter, meteo_val[0][1]], [valu, meteo_val[0][2]])
                # valf= (deb_time-time_inter)/(meteo_val[0][1]-time_inter) *(meteo_val[0][2]-valu)+ valu
                list_val.append([id, deb_time, valf])
            meteo_val = list_val + meteo_val

        t_pre = meteo_val[0][1] - deb_time
        ligne = "{} ".format(t_pre)
        for id, temps, val in meteo_val:
            if t_pre != temps - deb_time:
                fich.write(ligne + "\n")
                t_pre = temps - deb_time
                ligne = "{} {} ".format(t_pre, val)
            else:
                ligne += "{} ".format(val)
        fich.write(ligne)
        fich.close()
        return exit_satus, ''
