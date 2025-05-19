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
        self.dmeth = self.cl_param.dmeth
        # resultats du mouvement de la vanne
        self.results_fg_lk_mv = {}

        self.cl_regul = ClassMethRegul(self)
        self.cl_time = ClassMethTime(self)
        self.cl_fusible = ClassMethFusible(self)

    def init_fg_links(self):
        """
        Initialize floodgate links by gathering necessary information, validating parameters,
        and preparing variables for computation. This includes searching for control sections,
        linking parameters to the model, and initializing results.
        """
        # Get Section
        self.search_sec_control()
        self.search_link_to_param_fg()
        if not self.check_param():
            self.add_info("***** ERROR: the gates for the links\n COMPUTATION STOP")
            self.arret_comput = False
            return
        self.init_res()
        self.update_var_mas(force=True)
        return

    def update_var_mas(self, force=False):
        """
        Update the Mascaret model variables with the current floodgate parameters.
       
        :param  force :  If `force` is True, updates are applied regardless of whether 
        the parameters have changed; by default False
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
        """
        Initialize the results dictionary (`results_fg_lk_mv`) for storing floodgate movement data.
        This includes time, level, cross-section, width, and regulation variable values.
        """
        self.results_fg_lk_mv = {
            id_link: {
                "TIME": [params['TIME']],
                "ZLINK": [params["level"]],
                "CSECLINK": [params["CSection"]],
                "WIDTHLINK": [params["width"]],
                "REGVAR": [params["REGVAR_VAL"]],
            }
            for id_link, params in self.param_fg.items()
        }

    def finalize(self, tfin):
        """
        Finalize the floodgate results by appending the final time and parameter values
        to the results dictionary for each link.
        :param tfin: Final time of the simulation.
        """
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
        Perform floodgate treatment during a simulation iteration.
        Depending on the mobility method (`method_mob`), it applies regulation, time-based,
        or fusible logic to compute new parameter values.
        :param time: Current simulation time.
        :param dtp: Time step.
        """
        for id_lk, param in self.param_fg.items():
            val_break = self.masc.get(param['CHECK_VAR_BREAK'],
                                      param["SEC_BREAK"])

            if param["method_mob"] == self.dmeth["meth_regul"]:
                if self.cl_regul.check_dt_regul(param, dtp):
                    val_check = self.masc.get(param['CHECK_VAR'],
                                              param["SECCON"])
                    self.cl_regul.state_regul(val_check, param)
                    self.cl_regul.check_break(param, val_break)
                    dnew = self.cl_regul.law_gate_regul(param, time)
                    self.fill_res_and_update(id_lk, time, param, dnew, val_check)
            elif param["method_mob"] == self.dmeth["meth_time"]:
                val_check = self.masc.get(param['CHECK_VAR'], param["SECCON"])
                self.cl_time.check_break(param, val_break)
                dnew = self.cl_time.law_mth_time(param, time)
                self.fill_res_and_update(id_lk, time, param, dnew, val_check)
            elif param["method_mob"] == self.dmeth["meth_fus"]:
                val_check = self.masc.get(param['CHECK_VAR'],
                                          param["SECCON"])
                self.cl_fusible.check_break_fus(param, val_check, time)
                if self.cl_fusible.break_lk:
                    dnew = self.cl_fusible.law_mth_fus(param, time)
                    self.fill_res_and_update(id_lk, time, param, dnew, val_check)
                param.update({"TIME": time,
                              "REGVAR_VAL": val_check})
        
    def fill_res_and_update(self, id_lk, time, param, dnew, val_check):
        """
        Update floodgate parameters and fill the results dictionary with the new values.
        :param id_lk: Link ID.
        :param time: Current simulation time.
        :param param: Floodgate parameters dictionary.
        :param dnew: New computed values for the floodgate.
        :param val_check: Regulation variable value to check.
        """
        param.update({
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
        """
        Validate the floodgate parameters to ensure consistency.
        Returns True if all parameters are valid, otherwise False.
        """
        for id_lk, param in self.param_fg.items():
            if param["method_mob"] == self.dmeth["meth_regul"]:
                # check cas non possible
                if not self.cl_regul.check_param(param, id_lk):
                    return False
        return True

    def search_sec_control(self):
        """
        Identify the control section for each floodgate link and determine the variable
        to be checked for regulation. This involves mapping model coordinates to parameters.
        """
        self.model_size, _, _ = self.masc.get_var_size("Model.X")
        coords = []
        for i in range(self.model_size):
            coords.append(self.masc.get("Model.X", i))
        coords = np.array(coords)
        for id_lk, param in self.param_fg.items():
            param['CHECK_VAR'] = "State.Z"
            param['CHECK_VAR_BREAK'] = "State.Z"
            # 2 valeur
            # 'PK' regule
            # 'abscissa' pk link
            if param["method_mob"] == self.dmeth["meth_regul"]:
                if param["USEBASIN"]:
                    param["SECCON"] = param["NUMBASINREG"]
                    param["SEC_BREAK"] = param["NUMBASINREG"]
                    param['CHECK_VAR'] = "State.StoArea.Level"
                    param['CHECK_VAR_BREAK'] = "State.StoArea.Level"
                    continue
                var = "PK"
                param['CHECK_VAR'] = ("State.Z" if param["VREG"] == "Z" else "State.Q")
            elif param["method_mob"] == self.dmeth["meth_time"]:
                var = "abscissa"
                param['CHECK_VAR'] = "State.Z"
            elif param["method_mob"] == self.dmeth["meth_fus"]:
                if param["USEBASINFUS"]:
                    param["SECCON"] = param["NUMBASINFUS"]
                    param["SEC_BREAK"] = param["NUMBASINFUS"]
                    param['CHECK_VAR'] = "State.StoArea.Level"
                    param['CHECK_VAR_BREAK'] = "State.StoArea.Level"
                    continue
                var = "PKFUS"
                param['CHECK_VAR'] = ("State.Z" if param["VFUS"] == "Z" else "State.Q")
            else:
                var = None
                self.add_info(f"Method {param['method_mob']} doesn't exist for numlink {id_lk}")
                continue
            idx = (np.abs(coords - param[var])).argmin()
            if idx:
                param["SECCON"] = idx
            else:
                self.add_info("Regulation point not found for numlink {}.".format(id_lk))
            idxb = (np.abs(coords - param["abscissa"])).argmin()
            if idxb:
                param["SEC_BREAK"] = idxb
            else:
                self.add_info("Abscissa point not found for numlink {}.".format(id_lk))
        del coords

    def search_link_to_param_fg(self):
        """
        Establish links between the Mascaret model and the floodgate parameters.
        This includes retrieving initial values and preparing parameters for computation.
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
            if isinstance(idx,np.int64):
                id_mas = lst_info[idx]
                param.update({
                    "id_mas": id_mas,
                    "TIME0": tini,
                    "TIME": tini,
                })
                param["ZmaxSection0"] = param["level0"] + param["CSection0"] / param["width0"]
                if param["method_mob"] == self.dmeth["meth_regul"]:
                    self.cl_regul.init_meth_regul(param, id_lk)
                elif param["method_mob"] == self.dmeth["meth_time"]:
                    self.cl_time.init_meth_time(param)
                elif param["method_mob"] == self.dmeth["meth_fus"]:
                    self.cl_fusible.init_meth_fusible(param)
                # inti var time-dt
                param.update({
                    "CSection-dt": param["CSection0"],
                    "level-dt": param["level0"],
                    "width-dt": param["width0"],
                    "TIME-dt": tini,
                    "ZmaxSection-dt": param["ZmaxSection0"],
                    "REGVAR_VAL-dt": param["REGVAR_VAL"]
                })
            else:
                self.add_info("Id_mas not found for numlink {}.".format(id_lk))
        del coords, lst_info

    def fill_results_fg_mv(self, id_lk, param):
        """
        Populate the results dictionary (`results_fg_lk_mv`) with updated floodgate parameters
        if any changes occurred during the simulation.
        :param id_lk: Link ID.
        :param param: Floodgate parameters dictionary.
        """
        res = self.results_fg_lk_mv[id_lk]

        # Check if any parameter has changed
        zlink_var_dt = 'level-dt'
        zlink_var = 'level'
        if param["method_mob"] == "meth_regul":
            if param["DIRFG"] == "D":
                zlink_var_dt = 'level-dt'
                zlink_var = 'level'
            else:
                zlink_var_dt  = "ZmaxSection-dt"
                zlink_var = "ZmaxSection"
        if ((param["level"], param["CSection"], param["width"]) !=
                (param["level-dt"], param["CSection-dt"], param["width-dt"])) and(
                (res["TIME"][-1], res["CSECLINK"][-1], res["WIDTHLINK"][-1],res["ZLINK"][-1]) !=
                (param["TIME-dt"],param["CSection-dt"],param["width-dt"], param[zlink_var_dt])) and param["TIME"]>0:

            res["TIME"].append(param["TIME-dt"])
            res["CSECLINK"].append(param["CSection-dt"])
            res["WIDTHLINK"].append(param["width-dt"])
            res["REGVAR"].append(round(param["REGVAR_VAL-dt"], 3))
            res["ZLINK"].append(param[zlink_var_dt])

        # Update with new values
        res["TIME"].append(param["TIME"])
        res["CSECLINK"].append(param["CSection"])
        res["WIDTHLINK"].append(param["width"])
        res["REGVAR"].append(round(param["REGVAR_VAL"], 3))
        res["ZLINK"].append(param[zlink_var])
        
        param.update({
            # var time-dt
            "CSection-dt": param["CSection"],
            "level-dt": param["level"],
            "width-dt": param["width"],
            "TIME-dt": param["TIME"],
            "ZmaxSection-dt": param["ZmaxSection"],
            "REGVAR_VAL-dt": param["REGVAR_VAL"], })

class ClassMethRegul:
    """Class for handling floodgate regulation logic."""

    def __init__(self, parent):
        """
        Initialize the regulation class.
        :param parent: Reference to the parent `ClassFloodGateLk` instance.
        """
        self.prt = parent
        self.arret_comput = parent.arret_comput
        self.add_info = parent.add_info
        self.masc = parent.masc
        self.compt_dt = 0
        self.break_lk = False

    def init_meth_regul(self, param, id_lk):
        """
        Initialize the regulation parameters for a floodgate.
        :param param: Dictionary of floodgate parameters.
        :param id_lk: Link ID.
        """
        param.update({
            "rup_level": param["level0"],
            "rup_CSection": param["CSection0"],
            "rup_ZmaxSection": param["ZmaxSection0"],
            "rup_width": param["width0"]
        })
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
                param["CSection"] = param["width"] * min((param["ZmaxSection"] - param["level"]), 0)
            else:
                param["ZLIMITGATE"] = param["ZMAXFG"]
                param["CSection"] = 0

        elif param["DIRFG"] == "U" and param["type"] == 4:
            param["level"] = param["level0"]
            param["ZmaxSection"] = min(param["ZINITREG"], param["ZmaxSection0"])
            param["CSection"] = param["width0"] * min((param["ZmaxSection"] - param["level"]), 0)
            param["ZLIMITGATE"] = min(param["ZMAXFG"], param["level0"])
        else:
            self.add_info(f"Non-consistency type floodgate with the moving part {id_lk}.")

    def check_param(self, param, id_lk):
        """
        Validate the consistency of regulation parameters, specifically `VREGOPEN` and `VREGCLOS`.
        :param param: Dictionary of floodgate parameters.
        :param id_lk: Link ID.
        :return: True if parameters are valid, False otherwise.
        """
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
                return False
        else:
            if valo - tol > valf + tol:
                self.add_info(
                    "***** ERROR:"
                    "Opening level value must be lower closing level value\n"
                    " for the {} link ".format(id_lk)
                )
                return False
        return True

    def check_break(self, param, val_check):
        """
        Check if the floodgate should break.
        :param param: Dictionary of floodgate parameters.
        :param val_check: Current value of the regulation variable.
        """
        if val_check >= param["VBREAKREG"] :
            self.break_lk = True
            param.update({
                "rup_level": param["level"],
                "rup_CSection": param["CSection"],
                "rup_ZmaxSection": param["ZmaxSection"],
                "rup_width": param["width"]
            })
        else:
            # reveient à l'état avant rupture
            if not param["BPERMREG"]:
                self.break_lk = False
                param.update({
                    "level": param["rup_level"],
                    "CSection": param["rup_CSection"],
                    "ZmaxSection": param["rup_ZmaxSection"],
                    "width": param["rup_width"]
                })


    def state_regul(self, val_check, param_fg):
        """
        Determine the state of the floodgate (OPEN, CLOSE, or MAINTAIN) based on the regulation variable.

        :param val_check: Current value of the regulation variable.
        :param param_fg: Dictionary of floodgate parameters.
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
        Compute the new floodgate parameters.
        :param param: Dictionary of floodgate parameters.
        :param time: Current simulation time.
        :return: Dictionary of updated floodgate parameters.
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
        Compute the displacement of the floodgate over a time step.
        :param vit: Velocity of the floodgate movement.
        :param dt: Time step.
        :param dzlimit: Maximum allowable displacement.
        :return: Computed displacement.
        """
        dz = 0.0
        if dt > 0:
            dz = vit * dt
        return min(dz, dzlimit)

    def check_dt_regul(self, param_fg, dtp):
        """
        Check if the floodgate should be treated during the current time step.
        :param param_fg: Dictionary of floodgate parameters.
        :param dtp: Time step.
        :return: True if the floodgate should be treated, False otherwise.
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
    """Class for handling time-based floodgate."""

    def __init__(self, parent):
        """
        Initialize the time-based movable "link" class 
        :param parent: Reference to the parent `ClassFloodGateLk` instance.
        """
        self.arret_comput = parent.arret_comput
        self.add_info = parent.add_info
        self.masc = parent.masc
        self.break_lk = False

    def init_meth_time(self, param):
        """
        Initialize the time-based parameters for a floodgate.
        :param param: Dictionary of floodgate parameters.
        """
        param.update({
            "width": param["width0"],
            "CSection": param["CSection0"],
            "ZmaxSection": param["ZmaxSection0"],
            "TIMEZ": np.array(param["TIMEZ"]),
            "VALUEZ": np.array(param["VALUEZ"]),
            "REGVAR_VAL" : self.masc.get(param['CHECK_VAR'], param["SECCON"])
        })
        # TODO test dans le cas hors zone interpol
        param["level"] = np.interp(param["TIME"], param["TIMEZ"], param["VALUEZ"])
        if param["type"] == 4:
            param["CSection"] = param["width0"] * min((param["ZmaxSection0"] - param["level"]), 0)
        else:
            param["CSection"] = 0

        param.update({
            "rup_level": param["level0"],
            "rup_CSection": param["CSection0"],
            "rup_ZmaxSection": param["ZmaxSection0"],
            "rup_width": param["width0"]
        })



    def check_break(self, param, val_check):
        """
        Check if the floodgate should break.
        :param param: Dictionary of floodgate parameters.
        :param val_check: Current value of the regulation variable.
        """
        if val_check >= param["VBREAKT"]:
            self.break_lk = True
            param.update({
                "rup_level": param["level"],
                "rup_CSection": param["CSection"],
                "rup_ZmaxSection": param["ZmaxSection"],
                "rup_width": param["width"]
            })
        else:
            # reveient à l'état avant rupture
            if not  param["BPERMT"]:
                self.break_lk = False
                param.update({
                    "level": param["rup_level"],
                    "CSection": param["rup_CSection"],
                    "ZmaxSection": param["rup_ZmaxSection"],
                    "width": param["rup_width"]
                })

    def law_mth_time(self, param, time):
        """
        Compute the new floodgate parameters.
        :param param: Dictionary of floodgate parameters.
        :param time: Current simulation time.
        :return: Dictionary of updated floodgate parameters.
        """
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
    """Class for handling fusible floodgate."""
    #NOK
    def __init__(self, parent):
        """
        Initialize the "fusible" class.
        :param parent: Reference to the parent `ClassFloodGateLk` instance.
        """
        self.arret_comput = parent.arret_comput
        self.add_info = parent.add_info
        self.masc = parent.masc
        self.break_lk = False

    def init_meth_fusible(self, param):
        """
        Initialize the "fusible" parameters for a floodgate.
        :param param: Dictionary of floodgate parameters.
        """
        param.update({
            "level": param["level0"],
            "width": param["width0"],
            "CSection": param["CSection0"],
            "ZmaxSection": param["ZmaxSection0"],
            "TIMEFUS": np.array(param["TIMEFUS"]),
            "WIDTHFUS": np.array(param["WIDTHFUS"]),
            "break_time": -9999,
            "REGVAR_VAL" : self.masc.get(param['CHECK_VAR'], param["SECCON"])

        })

    def check_break_fus(self, param, val_check, time):
        """
        Check if the floodgate should break.
        :param param: Dictionary of floodgate parameters.
        :param val_check: Current value of the regulation variable.
        :param time: Current simulation time.
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
        """
        Compute the new floodgate parameters.
        :param param: Dictionary of floodgate parameters.
        :param time: Current simulation time.
        :return: Dictionary of updated floodgate parameters.
        """
        dnew = {"level": param["ZFINALFUS"],
                "ZmaxSection": param["ZmaxSection0"]}

        rela_time = time - param["break_time"]
        if rela_time <= max(param["TIMEFUS"]):
            new_width = np.interp(rela_time, param["TIMEFUS"], param["WIDTHFUS"])
        else:
            new_width =  param["WIDTHFUS"]
        dnew["width"] = max(0.05, new_width)

        if param["type"] == 4:
            dnew["CSection"] = dnew["width"] * min((param["ZmaxSection0"] - dnew["level"]), 0)
        else:
            dnew["CSection"] = 0

        return dnew
