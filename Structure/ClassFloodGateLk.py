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
import math

from .ClassLinkFGParam import ClassLinkFGParam


class ClassFloodGateLk:
    """Class Flood Gate"""

    def __init__(self, main):
        self.clapi = main
        self.add_info = self.clapi.add_info
        self.masc = main.masc
        self.clmas = main.clmas
        self.debug = main.DEBUG
        self.model_size = 0
        self.size_link = 0
        self.new_z = 99
        self.arret_comput = False

        self.cl_param = ClassLinkFGParam()
        self.cl_param.get_param(parent=main.mgis)
        self.actif_mobil_lk = self.cl_param.fg_actif_lk()
        self.param_fg = self.cl_param.param_fg
        # resultats du mouvement de la vanne
        self.results_fg_lk_mv = {}

        self.cl_regul= ClassMethRegul(self)
        self.cl_time = ClassMethTime(self)
        self.cl_fusible = ClassMethFusible(self)

    def init_fg_links(self):
        """Get information for floodgate"""

        # Get Section

        self.search_sec_control()

        self.search_link_to_param_fg()
        if not self.check_param():
            self.add_info("***** ERROR: the gates for the links\n COMPUTATION STOP")
            self.arret_comput = False

        self.init_res()
        self.update_var_mas(force=True)

        return

    def update_var_mas(self, force=False):
        """
        Update valu in Mascaret
        """
        for param in self.param_fg.values():
            if ((param["level"], param["CSection"], param["width"]) !=
                    (param["level-dt"], param["CSection-dt"], param["width-dt"]) or force):
                id_mas = param["id_mas"]
                updates = {
                    "Model.Link.Level": param["level"],
                    "Model.Link.CSection": param["CSection"],
                    "Model.Link.Width": param["width"]
                }
                for key, value in updates.items():
                    self.masc.set(key, value, id_mas)

    def init_res(self):
        """Init. the results dico"""
        self.results_fg_lk_mv = {
            id_link: {
                "TIME": [params["TIME"]],
                "ZLINK": [params["level"]],
                "CSECLINK": [params["CSection"]],
                "WIDTHLINK": [params["width"]],
                "REGVAR": [params["REGVAR_VAL"]],
            }
            for id_link, params in self.param_fg.items()
        }

    def finalize(self, tfin):
        if len(self.results_fg_lk_mv) > 0:
            for id_link, param in self.param_fg.items():
                res = self.results_fg_lk_mv[id_link]
                res["TIME"].append(tfin)
                res["ZLINK"].append(param["level"])
                res["CSECLINK"].append(param["CSection"])
                res["WIDTHLINK"].append(param["width"])
                res["REGVAR"].append(param["REGVAR_VAL"])

    def iter_fg(self, time, dtp):
        """
        Floodgate treatment during an iteration
        :param dtp : time step
        :param time: time
        """
        for id_lk, param in self.param_fg.items():
            if param["method_mob"] == "meth_regul":
                if self.cl_regul.check_dt_regul(param, dtp):
                    val_check = self.masc.get(param['CHECK_VAR'],
                                              param["SECCON"])
                    self.cl_regul.state_regul(val_check, param)
                    self.cl_regul.check_break(param, val_check)
                    dnew = self.cl_regul.law_gate_regul(param, time)
                    self.fill_res_and_update(id_lk, time, param, dnew, val_check)
            elif param["method_mob"] == "meth_time":
                val_check = self.masc.get(param['CHECK_VAR'], param["SECCON"])
                self.cl_time.check_break(param,val_check)
                dnew = self.cl_time.law_mth_time(param, time, val_check)
                self.fill_res_and_update(id_lk, time, param, dnew, val_check)
            elif param[id_lk]["method_mob"] == "meth_fus":
                val_check = self.masc.get(param['CHECK_VAR'],
                                          param["SECCON"])
                self.cl_fusible.check_break_fus(param, val_check, time)
                if self.cl_fusible.break_lk:
                    dnew = self.cl_fusible.law_mth_fus(param, time)
                    self.fill_res_and_update(id_lk, time, param, dnew, val_check)

    def fill_res_and_update(self, id_lk, time, param, dnew, val_check):
        param.update({
            # var time-dt
            "CSection-dt": param["CSection"],
            "level-dt": param["level"],
            "width-dt": param["width"],
            "TIME-dt": param["TIME"],
            "ZmaxSection-dt": param["ZmaxSection"],
            "REGVAR_VAL-dt": param["REGVAR_VAL"],
            # var update in run
            "REGVAR_VAL": val_check,
            "level": dnew['level'],
            "CSection": dnew["CSection"],
            "width": dnew["width"],
            "ZmaxSection": dnew["ZmaxSection"],
            "TIME": time
        })
        self.fill_results_fg_mv(id_lk, param)
        self.update_var_mas()

    def check_param(self):
        """'"""
        # check cas non possible
        cond = True
        for id_lk,  param in self.param_fg.items():
            if param["method_mob"]== "meth_regul":
                cond = self.cl_regul.check_param(param, id_lk)

        return cond

    def search_sec_control(self):
        """
        Get control section to compare the regulation variable
        And Get variable to check
        """

        self.model_size, _, _ = self.masc.get_var_size("Model.X")
        coords = []
        for i in range(self.model_size):
            coords.append(self.masc.get("Model.X", i))
        coords = np.array(coords)
        for id_lk, param in self.param_fg.itmes():
            param['CHECK_VAR'] = "State.Z"
            # 2 valeur
            # 'PK' regule
            # 'abscissa' pk link
            if param["method_mob"] == "meth_regul":
                if param["USEBASIN"]:
                    param["SECCON"] = param["NUMBASINREG"]
                    param['CHECK_VAR'] = "State.StoArea.Level"
                    continue
                var = "PK"
                param['CHECK_VAR'] = ("State.Z" if param["VREG"] == "Z" else "State.Q")
            elif param["method_mob"] == "meth_time":
                var = "abscissa"
                param['CHECK_VAR'] = "State.Z"
            elif param["method_mob"] == "meth_fus":
                if param["USEBASINFUS"]:
                    param["SECCON"] = param["NUMBASINFUS"]
                    param['CHECK_VAR'] = "State.StoArea.Level"
                    continue
                var = "PKFUS"
                param['CHECK_VAR'] = ("State.Z" if param["VFUS"] == "Z" else "State.Q")
            idx = (np.abs(coords - param[var])).argmin()
            if idx:
                param["SECCON"] = idx
            else:
                self.add_info("Regulation point not found for numlink {}.".format(id_lk))
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

        for id_lk, param in self.param_fg.items():
            idx = (np.abs(coords - param["abscissa"])).argmin()
            if idx:
                id_mas = lst_info[idx]
                param.update({
                    "id_mas": id_mas,
                    "CSection0": self.masc.get("Model.Link.CSection", id_mas),
                    "level0": self.masc.get("Model.Link.Level", id_mas),
                    "width0": self.masc.get("Model.Link.Width", id_mas),
                    "TIME0": tini,
                    "TIME": tini
                })
                param["ZmaxSection0"] = param["level0"] + param["CSection0"] / param["width0"]

                if param["method_mob"] == "meth_regul":
                    self.cl_regul.init_meth_regul(param,id_lk)
                elif param["method_mob"] == "meth_time":
                    self.cl_time.init_meth_time(param)
                elif param["method_mob"] == "meth_fus":
                    self.cl_fusible.init_meth_fusible(param)
            else:
                self.add_info("Id_mas not found for numlink {}.".format(id_lk))

            # inti var time-dt
            param.update({
                "CSection-dt": param["CSection0"],
                "level-dt": param["level0"],
                "width-dt": param["width0"],
                "TIME-dt": tini,
                "ZmaxSection-dt": param["ZmaxSection0"],
                "REGVAR_VAL-dt":param("REGVAR_VAL")
            })
        del coords, lst_info

    def fill_results_fg_mv(self, id_lk, param):
        """
        fill the results_fg_mv dico
        :param id_lk: link id
        :param dnew: dico fo new value
        :param param : dico of flood gate paramter
        :return:
        """
        res = self.results_fg_lk_mv[id_lk]

        # Check if any parameter has changed
        if ((param["level"], param["CSection"], param["width"]) !=
            (param["level-dt"], param["CSection-dt"], param["width-dt"])):
                res["TIME"].append(param["TIME-dt"])
                res["CSECLINK"].append(param["CSection-dt"])
                res["WIDTHLINK"].append(param["width-dt"])
                res["REGVAR"].append(round(param["REGVAR_VAL-dt"], 3))
                if param["method_mob"] == "meth_regul":
                    if param["DIRFG"] == "D":
                        res["ZLINK"].append(param['level-dt'])
                    else:
                        res["ZLINK"].append(param["ZmaxSection-dt"])
                else:
                    res["ZLINK"].append(param['level-dt'])
        # Update with new values
        res["TIME"].append(param["TIME"])
        res["CSECLINK"].append(param["CSection"])
        res["WIDTHLINK"].append(param["width"])
        res["REGVAR"].append(round(param["REGVAR_VAL"], 3))
        if param["method_mob"] == "meth_regul":
            if param["DIRFG"] == "D":
                res["ZLINK"].append(param['level'])
            else:
                res["ZLINK"].append(param["ZmaxSection"])
        else:
            res["ZLINK"].append(param['level'])


class ClassMethRegul:
    """Class Flood Gate"""

    def __init__(self, parent):
        self.prt = parent
        self.arret_comput =  parent.arret_comput
        self.add_info =parent.add_info
        self.masc = parent.masc
        self.compt_dt = 0
        self.break_lk = False

    def init_meth_regul(self, param, id_lk):
        """ Initialise the regulation variable
        :param parameters: parameters dict """

        param.update({
            "width": param["width0"],
            "CSection": param["CSection0"],
            "REGVAR_VAL": self.masc.get(param['CHECK_VAR'], param["SECCON"]),
            "OPEN_CLOSE": "INIT"
        })
        # info de la vanne
        if param["DIRFG"] == "D":
            param["level"] = max(param["ZINITREG"], param["level0"])
            param["ZmaxSection"] = param["ZmaxSection0"]
            if param["type"] == 4:
                # section rectangulaire
                param["ZLIMITGATE"] = min(param["ZMAXFG"], param["ZmaxSection0"])
                param["CSection"] = param["width"] *min((param["ZmaxSection"] - param["level"]),0)
            else:
                param["ZLIMITGATE"] = param["ZMAXFG"]
                param["CSection"] = 0

        elif param["DIRFG"] == "U" and param["type"] == 4:
            param["level"] = param["level0"]
            param["ZmaxSection"] = min(param["ZINITREG"], param["ZmaxSection0"])
            param["CSection"] = param["width0"] * min((param["ZmaxSection"] - param["level"]),0)
            param["ZLIMITGATE"] = min(param["ZMAXFG"], param["level0"])
        else:
            self.add_info(f"Non-consistency type floodgate with the moving part {id_lk}.")

    def check_param(self, param, id_lk):
        """Check if  'VREGOPEN' and 'VREGCLOS are consistent"""

        valo = param["VREGOPEN"]
        valf = param["VREGCLOS"]
        tol = param["TOLREG"]

        if param["DIRFG"] == "D":  # bas
            if valf + tol > valo - tol:
                self.add_info(
                    "***** ERROR: "
                    "Closing level value must be lower opening level value\n"
                    " for the {} link ".format(id_lk)
                )
                cond = False
        else:
            if valo - tol > valf + tol:
                self.add_info(
                    "***** ERROR:"
                    "Opening level value must be lower closing level value\n"
                    " for the {} link ".format(id_lk)
                )
                cond = False

    def check_break(self,param, val_check):
        """
        Check Break
        :param param: parameters
        :param val_check: value to check
        :return:
        """
        if  val_check >= param["VBREAKREG"] or (self.break_lk and param["BPERMREG"]):
            self.break_lk = True
        else:
            self.break_lk = False
            param.update({
                "level": param["level0"],
                "CSection": param["CSection0"],
                "ZmaxSection": param["ZmaxSection0"],
                "width": param["width0"]
            })

    def state_regul(self, val_check, param_fg):
        """
        check if OPEN or CLOSE the flood Gate with maintains
        between  param_fg["VREGOPEN"] et param_fg["VREGCLOS"]
        """
        tol = param_fg["TOLREG"]
        key = (param_fg["OPEN_CLOSE"], param_fg["DIRFG"])
        # conditions
        conditions = {
            # fermeture par le bas
            ("INIT", "D"): [(val_check >= param_fg["VREGOPEN"] - tol, "OPEN")],
            ("OPEN", "D"): [
                (val_check <= param_fg["VREGCLOS"] + tol, "CLOSE"),
                (param_fg["VREGOPEN"] > val_check > param_fg["VREGCLOS"], "MAINT"),
            ],
            ("CLOSE", "D"): [
                (val_check >= param_fg["VREGOPEN"] - tol, "OPEN"),
                (param_fg["VREGOPEN"] > val_check > param_fg["VREGCLOS"], "MAINT"),
            ],
            ("MAINT", "D"): [
                (val_check >= param_fg["VREGOPEN"] - tol, "OPEN"),
                (val_check <= param_fg["VREGCLOS"] + tol, "CLOSE"),
                (param_fg["VREGOPEN"] > val_check > param_fg["VREGCLOS"], "MAINT"),
            ],
            # fermeture par le haut
            ("INIT", "U"): [(val_check >= param_fg["VREGCLOS"] - tol, "CLOSE")],
            ("CLOSE", "U"): [
                (val_check <= param_fg["VREGOPEN"] + tol, "OPEN"),
                (param_fg["VREGOPEN"] < val_check < param_fg["VREGCLOS"], "MAINT"),
            ],
            ("OPEN", "U"): [
                (val_check >= param_fg["VREGCLOS"] - tol, "CLOSE"),
                (param_fg["VREGOPEN"] < val_check < param_fg["VREGCLOS"], "MAINT"),
            ],
            ("MAINT", "U"): [
                (val_check <= param_fg["VREGOPEN"] + tol, "OPEN"),
                (val_check >= param_fg["VREGCLOS"] - tol, "CLOSE"),
                (param_fg["VREGOPEN"] < val_check < param_fg["VREGCLOS"], "MAINT"),
            ]
        }

        for condition, action in conditions.get(key, []):
            if condition:
                param_fg["OPEN_CLOSE"] = action
                break

        return val_check

    def law_gate_regul(self, param, time):
        """
        :return: new value
        """
        if self.break_lk:
            return {
                "level": param["ZFINALREG"],
                "CSection": param["width0"] * min((param["ZmaxSection0"] - param["ZFINALREG"]), 0),
                "ZmaxSection": param["ZmaxSection0"],
                "width": param["width0"]
            }

        status = param["OPEN_CLOSE"]

        if status in [None, "INIT", "MAINT"]:
            return {
            "level": param["level"],
            "CSection": param["CSection"],
            "ZmaxSection": param["ZmaxSection"],
            "width": param["width"]
            }
        dt = time - param["TIME"]
        dz_open = self.comput_dz(param["VELOFGOPEN"], dt, param["ZINCRFG"])
        dz_close = self.comput_dz(param["VELOFGCLOSE"], dt, param["ZINCRFG"])

        dir_fg = param["DIRFG"]
        level, level0 = param["level"], param["level0"]
        zmax_section, zmax_section0 = param["ZmaxSection"], param["ZmaxSection0"]
        zlimit_gate = param["ZLIMITGATE"]
        width = param["width0"]

        if dir_fg == "D":
            new_level_max = zmax_section0
            if status == "CLOSE":
                new_level = min(level + dz_close, zlimit_gate)
            elif status == "OPEN":
                new_level = max(level - dz_open, level0)
        elif dir_fg == "U":
            new_level = level0
            if status == "CLOSE":
                new_level_max = min(zmax_section + dz_close, zlimit_gate)
            elif status == "OPEN":
                new_level_max = max(zmax_section - dz_open, zmax_section0)

        new_section = width * (new_level_max - new_level)
        return {
            "level": new_level,
            "CSection": new_section,
            "ZmaxSection": new_level_max,
            "width": width
        }

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

class ClassMethTime:
    """Class Flood Gate"""
    # self.cl_time = ClassMethTime(self)

    def __init__(self, parent):
        self.arret_comput =  parent.arret_comput
        self.add_info =parent.add_info
        self.masc = parent.masc
        self.break_lk = False

    def init_meth_time(self, param):
        param.update({
            "width": param["width0"],
            "CSection": param["CSection0"],
            "ZmaxSection": param["ZmaxSection0"],
            "TIMEZ": np.array(param["TIMEZ"]),
            "VALUEZ": np.array(param["VALUEZ"])
        })
        param["level"] = np.interp(param["TIME"], param["TIMEZ"],param["VALUEZ"])
        if param["type"] == 4:
            param["CSection"] = param["width0"] * min((param["ZmaxSection0"] - param["level"]),0)
        else:
            param["CSection"] = 0

    def check_break(self,param, val_check):
        """
        Check Break
        :param param: parameters
        :param val_check: value to check
        :return:
        """
        self.break_lk = val_check >= param["VBREAKT"] or (self.break_lk and param["BPERMT"])

    def law_mth_time(self, param, time):
        """ compute new value"""
        if self.break_lk:
            return {
                "level": param["ZFINALT"],
                "CSection": param["width0"] * min((param["ZmaxSection0"] - param["ZFINALT"]), 0),
                "ZmaxSection": param["ZmaxSection0"],
                "width": param["width0"]
                }
        dnew = {"ZmaxSection": param["ZmaxSection0"], "width": param["width0"],
                "level": np.interp(time, param["TIMEZ"], param["VALUEZ"])}
        if param["type"] == 4:
            dnew["CSection"] = param["width0"] * min((param["ZmaxSection0"] - dnew["level"]), 0)
        else:
            dnew["CSection"] = 0

        return dnew



class ClassMethFusible:
    """Class Flood Gate"""
    # self.cl_fusible = ClassMethFusible(self)
    def __init__(self, parent):
        self.arret_comput =  parent.arret_comput
        self.add_info =parent.add_info
        self.masc = parent.masc
        self.break_lk = False

    def init_meth_fusible(self, param):
        param.update({
            "level": param["level0"],
            "width": param["width0"],
            "CSection": param["CSection0"],
            "ZmaxSection": param["ZmaxSection0"],
            "TIMEFUS": np.array(param["TIMEFUS"]),
            "WIDTHFUS": np.array(param["WIDTHFUS"]),
            "break_time": -9999
        })

    def check_break_fus(self, param, val_check, time):
        """
         Check if treat the flood gate
        :return: true or false
        """
        if self.break_lk:
            return
        if param["METHBREAK"] == 'regul' and val_check >= param["VBREAKFUS"]:
            self.break_lk = True
            param["break_time"] = time
        elif time >= param["TBREAKFUS"]:
            self.break_lk = True
            param["break_time"] = time

    def law_mth_fus(self, param, time):
        """ compute new value"""

        dnew = {"level": param["ZFINALFUS"],
                "ZmaxSection" : param["ZmaxSection0"]}

        rela_time = time - param["break_time"]
        new_width = np.interp(rela_time, param["TIMEZ"], param["VBREAKFUS"])
        dnew["width"] = min(0.05, new_width)

        if param["type"] == 4:
            dnew["CSection"] = dnew["width"] * min((param["ZmaxSection0"] - dnew["level"]), 0)
        else:
            dnew["CSection"] = 0

        return dnew
