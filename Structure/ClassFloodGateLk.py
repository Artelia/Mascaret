# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : Janvier,2020
copyright            : (C) 2020 by Artelia
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
import numpy as np
import  math

from .ClassPostPreFGLk import ClassInfoParamFG_Lk


class ClassFloodGateLk:
    """Class Flood Gate"""

    def __init__(self, main):
        self.clapi = main
        self.masc = main.masc
        self.clmas = main.clmas
        self.debug = main.DEBUG
        self.model_size = 0
        self.size_link = 0
        self.new_z = 99
        self.compt_dt = 0
        self.cl_fg_l = ClassInfoParamFG_Lk()

        self.cl_fg_l.get_param(parent=main.mgis)
        self.actif_mobil_lk = self.cl_fg_l.fg_actif_lk()
        self.param_fg = self.cl_fg_l.param_fg
        # resultats du mouvement de la vanne
        self.results_fg_lk_mv = {}

    def init_fg_links(self):
        """Get information for floodgate"""
        # Get Section
        self.search_sec_control()
        self.search_link_to_param_fg()
        if not self.check_level_regul():
            self.clapi.add_info("***** ERROR: ignore the gates for the links")
            self.actif_mobil_lk = False
        self.update_var_mas()
        # for id_lk in self.param_fg.keys():
        #     print(self.masc.get("Model.Link.Level", self.param_fg[id_lk]["id_mas"]))


        self.init_res()

    def update_var_mas(self):
        """
        Update valu in Mascaret
        """
        for id_lk in self.param_fg.keys():
            id_mas = self.param_fg[id_lk]["id_mas"]
            self.masc.set("Model.Link.Level", self.param_fg[id_lk]["level"], id_mas)
            self.masc.set("Model.Link.CSection'", self.param_fg[id_lk]["CSection"], id_mas)

    def init_res(self):
        """Init. the results dico"""
        self.results_fg_lk_mv = {}
        for id_link in self.param_fg.keys():
            self.results_fg_lk_mv[id_link] = {"TIME": [], "ZLINK": [], "CSECLINK": [], "REGVAR": []}
            self.results_fg_lk_mv[id_link]["TIME"].append(self.param_fg[id_link]["TIME"])
            self.results_fg_lk_mv[id_link]["ZLINK"].append(self.param_fg[id_link]["level"])
            self.results_fg_lk_mv[id_link]["CSECLINK"].append(self.param_fg[id_link]["CSection"])
            self.results_fg_lk_mv[id_link]["REGVAR"].append(self.param_fg[id_link]["REGVAR_VAL"])


    def finalize(self, tfin):
        if len(self.results_fg_lk_mv) > 0:
            for id_link in self.param_fg.keys():
                self.results_fg_lk_mv[id_link]["TIME"].append(tfin)
                self.results_fg_lk_mv[id_link]["ZLINK"].append(self.param_fg[id_link]["level"])
                self.results_fg_lk_mv[id_link]["CSECLINK"].append(self.param_fg[id_link]["CSection"])
                self.results_fg_lk_mv[id_link]["REGVAR"].append(self.param_fg[id_link]["REGVAR_VAL"])

    def iter_fg(self, time, dtp):
        """
        Floodgate treatment during an iteration
        :param dtp : time step
        :param time: time

        """
        for id_lk in self.param_fg.keys():
            if self.check_dt_regul(self.param_fg[id_lk], dtp):
                val_check = self.check_regul(self.param_fg[id_lk])
                new_level, new_section, new_level_max = self.law_gate_regul(self.param_fg[id_lk], time)
                # fill before to have the old value and new
                self.fill_results_fg_mv(id_lk,new_level,new_section, new_level_max,val_check , time, dtp,  self.param_fg[id_lk])
                self.param_fg[id_lk]["REGVAR_VAL"] = val_check
                self.param_fg[id_lk]['level']= new_level
                self.param_fg[id_lk]["CSection"] = new_section
                self.param_fg[id_lk]["ZmaxSection"] = new_level_max
                self.param_fg[id_lk]["TIME"] = time
                self.update_var_mas()

    def check_level_regul(self):
        """Check if  'VREGOPEN' and 'VREGCLOS are consistent'"""
        # check cas non possible
        cond = True
        for id_lk in self.param_fg.keys():
            typ_g = self.param_fg[id_lk]["DIRFG"]
            valo = self.param_fg[id_lk]["VREGOPEN"]
            valf = self.param_fg[id_lk]["VREGCLOS"]
            tol = self.param_fg[id_lk]["TOLREG"]
            if typ_g == "D":  # bas
                if valf + tol > valo - tol:
                    self.clapi.add_info(
                        "***** ERROR: "
                        "Closing level value must be lower opening level value\n"
                        " for the {} link ".format(id_lk)
                    )
                    cond = False

            else:
                if valo - tol > valf + tol:
                    self.clapi.add_info(
                        "***** ERROR:"
                        "Opening level value must be lower closing level value\n"
                        " for the {} link ".format(id_lk)
                    )
                    cond = False
        return cond

    def check_regul(self, param_fg):
        """
        check if OPEN or CLOSE the flood Gate
        """
        if param_fg["VREG"] == "Z":
            val_mas = "State.Z"
        else:
            val_mas = "State.Q"
        val_check = self.masc.get(val_mas, param_fg["SECCON"])

        tol = param_fg["TOLREG"]
        #
        key = (param_fg["OPEN_CLOSE"], param_fg["DIRFG"])
        if key == ('INIT' ,'D'):
            if  val_check > param_fg['VREGOPEN']- tol :
                param_fg['OPEN_CLOSE'] = 'OPEN'
        elif key == ('OPEN' ,'D'):
            if val_check < param_fg["VREGCLOS"] + tol:
                param_fg['OPEN_CLOSE'] = 'CLOSE'
        elif key == ('CLOSE', 'D'):
            if val_check > param_fg['VREGOPEN'] - tol:
                param_fg['OPEN_CLOSE'] = 'OPEN'
        elif key == ('INIT', 'U'):
            if  val_check > param_fg["VREGCLOS"]- tol :
                param_fg['OPEN_CLOSE'] = 'CLOSE'
        elif key == ('CLOSE', 'U'):
            if val_check < param_fg['VREGOPEN'] + tol:
                param_fg['OPEN_CLOSE'] = 'OPEN'
        elif key == ('OPEN', 'U'):
            if val_check > param_fg["VREGCLOS"] - tol:
                param_fg['OPEN_CLOSE'] = 'CLOSE'
        return val_check

    def check_dt_regul(self, param_fg, dtp):
        """
         Check if treat the flood gate
        :return: true or false
        """
        crit = param_fg["CRITDTREG"]
        self.compt_dt += 1
        if crit == "NDTREG":
            if self.compt_dt == param_fg["NDTREG"]:
                self.compt_dt = 0
                return True
            return False
        elif crit == "DTREG":
            if self.compt_dt * dtp >= param_fg["DTREG"]:
                self.compt_dt = 0
                return True
            return False
        else:
            self.compt_dt = 0
            return False

    def search_sec_control(self):
        """
        Get control section to compare the regulation variable
        """
        self.model_size, _, _ = self.masc.get_var_size("Model.X")
        coords = []
        for i in range(self.model_size):
            coords.append(self.masc.get("Model.X", i))
        coords = np.array(coords)
        for id_lk in self.param_fg.keys():
            # 2 valeur
            # 'PK' regule
            # 'abscissa' pk link
            idx = (np.abs(coords - self.param_fg[id_lk]["PK"])).argmin()
            if idx:
                self.param_fg[id_lk]["SECCON"] = idx
            else:
                self.clapi.add_info("Regulation point not found for numlink {}.".format(id_lk))
        del coords

    def search_link_to_param_fg(self):
        """
        Link information between the model and the parameters file
        """
        self.size_link, _, _ = self.masc.get_var_size("Model.Link.Kind")
        tini = self.masc.get("Model.InitTime")
        lst_info = []
        coords = []
        for id_mas_lk in range(self.size_link):
            nature = self.masc.get("Model.Link.Kind", id_mas_lk)
            typ = self.masc.get("Model.Link.Type", id_mas_lk)
            if nature == 1 and typ in [1, 4]:  # narure 1: basin-reach, typ 1 weirs, 4 culvert
                abs = self.masc.get("Model.Link.StoR.Abscissa", id_mas_lk)
                lst_info.append(id_mas_lk)
                coords.append(abs)
        coords = np.array(coords)

        for id_lk in self.param_fg.keys():
            idx = (np.abs(coords - self.param_fg[id_lk]["abscissa"])).argmin()
            if idx:
                id_mas = lst_info[idx]
                self.param_fg[id_lk]["id_mas"] = id_mas
                # conserv variable initial
                self.param_fg[id_lk]["CSection0"] = self.masc.get("Model.Link.CSection", id_mas)
                self.param_fg[id_lk]["level0"] = self.masc.get("Model.Link.Level", id_mas)
                self.param_fg[id_lk]["width0"] = self.masc.get("Model.Link.Width", id_mas)
                self.param_fg[id_lk]["ZmaxSection0"] = (
                    self.param_fg[id_lk]["level0"]
                    + self.param_fg[id_lk]["CSection0"] / self.param_fg[id_lk]["width0"]
                )
                self.param_fg[id_lk]["TIME0"] = tini
                # variable qui evolura ********************************
                self.param_fg[id_lk]["TIME"] = tini
                if self.param_fg[id_lk]["VREG"] == "Z":
                    val_mas = "State.Z"
                else:
                    val_mas = "State.Q"
                self.param_fg[id_lk]["REGVAR_VAL"] = self.masc.get(val_mas, self.param_fg[id_lk]["SECCON"])
                self.param_fg[id_lk]["OPEN_CLOSE"] = "INIT"
                # info de la vanne
                if self.param_fg[id_lk]["DIRFG"] == "D":
                    # TODO mettre a jours mascaret
                    self.param_fg[id_lk]["level"] = max(
                        self.param_fg[id_lk]["ZINITREG"], self.param_fg[id_lk]["level0"]
                    )
                    self.param_fg[id_lk]["ZmaxSection"] = self.param_fg[id_lk]["ZmaxSection0"]
                    self.param_fg[id_lk]["CSection"] = self.param_fg[id_lk]["width0"] * (
                        self.param_fg[id_lk]["ZmaxSection"] - self.param_fg[id_lk]["level"]
                    )
                    self.param_fg[id_lk]["ZLIMITGATE"] = min(
                        self.param_fg[id_lk]["ZMAXFG"], self.param_fg[id_lk]["ZmaxSection0"]
                    )

                else:
                    self.param_fg[id_lk]["level"] = self.param_fg[id_lk]["level0"]
                    self.param_fg[id_lk]["ZmaxSection"] = min(
                        self.param_fg[id_lk]["ZINITREG"], self.param_fg[id_lk]["ZmaxSection0"]
                    )
                    self.param_fg[id_lk]["CSection"] = self.param_fg[id_lk]["width0"] * (
                        self.param_fg[id_lk]["ZmaxSection"] - self.param_fg[id_lk]["level"]
                    )
                    self.param_fg[id_lk]["ZLIMITGATE"] = min(
                        self.param_fg[id_lk]["ZMAXFG"], self.param_fg[id_lk]["level0"]
                    )
            else:
                self.clapi.add_info("Id_mas not found for numlink {}.".format(id_lk))
        del coords, lst_info



    def comput_dz(self, vit, dt, dzlimit=0):
        """
         comput_dx
        :param vit: velocity
        :param dt: step time
        :param dzlimit:  Limit dz max by dt
        :return: dz : displacement in a time dt
        """
        dz = 0.0
        if dt > 0:
            dz = vit * dt
        return min(dz, dzlimit)

    def law_gate_regul(self, param, time):
        """

        :return:  new position of flood gate, and new area, and if status is OPEN, CLOSE, NONE
        """
        old_time = param["TIME"]
        dt = time - old_time
        status = param["OPEN_CLOSE"]

        if status in [None, "INIT"]:
            return param["level"], param["CSection"],param["ZmaxSection"]

        dz = self.comput_dz(param["VELOFG"], dt, param["ZINCRFG"])
        dir_fg = param["DIRFG"]
        zmax_section0 = param["ZmaxSection0"]
        level0 = param["level0"]
        zlimit_gate = param["ZLIMITGATE"]
        width0 = param["width0"]
        if dir_fg == "D":
            level = param["level"]
            new_level_max = zmax_section0
            if status == "CLOSE":
                new_level = min(level + dz, zlimit_gate)
            elif status == "OPEN":
                new_level = max(level - dz, level0)
        elif dir_fg == "U":
            zmax_section = param["ZmaxSection"]
            new_level = level0
            if status == "CLOSE":
                new_level_max = min(zmax_section + dz, zlimit_gate)
            elif status == "OPEN":
                new_level_max = max(zmax_section - dz, zmax_section0)

        new_section = width0 * (new_level_max - new_level)
        return new_level, new_section , new_level_max

    def fill_results_fg_mv(self, id_lk, new_level,new_section, new_level_max, val_check, time, dtp, param):

        """
        fill the results_fg_mv dico
        :param id_lk: link id
        :param time: time
        :param new_level :  new Z
        :param new_section ! new sectino
        :param new_level_max:  new Z height of the culvert
        :param param : dico of flood gate paramter
        :param  val_check : regulation value
        :return:
        """
        dir_fg = param["DIRFG"]
        old_time = param["TIME"]
        dt = time - old_time
        typ_sav = 0
        for var , val in [('level',new_level), ("CSection", new_section), ('ZmaxSection', new_level_max)] :
            if param[var] != val :
                typ_sav = 1
        if typ_sav == 1 :
            if not math.isclose(dtp,  dt, rel_tol=1e-06) :
                self.results_fg_lk_mv[id_lk]["TIME"].append(time - dtp)
                self.results_fg_lk_mv[id_lk]["CSECLINK"].append(param["CSection"])
                self.results_fg_lk_mv[id_lk]["REGVAR"].append(round(param["REGVAR_VAL"], 3))
                if dir_fg == "D":
                    self.results_fg_lk_mv[id_lk]["ZLINK"].append(param['level'])
                else:
                    self.results_fg_lk_mv[id_lk]["ZLINK"].append(param["ZmaxSection"])


        self.results_fg_lk_mv[id_lk]["TIME"].append(time)
        self.results_fg_lk_mv[id_lk]["CSECLINK"].append(new_section)
        self.results_fg_lk_mv[id_lk]["REGVAR"].append(round(val_check,3))
        if dir_fg == "D":
            self.results_fg_lk_mv[id_lk]["ZLINK"].append(new_level)
        else:
            self.results_fg_lk_mv[id_lk]["ZLINK"].append(new_level_max)

