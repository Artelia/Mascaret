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

from .ClassMobilWeirsParam import ClassMobilWeirsParam

class ClassMobilWeirs:
    """Class Flood Gate

    This class manages the moving Weirs in the Mascaret model.
    """

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
        self.break_w = False

        self.cl_param = ClassMobilWeirsParam()
        self.cl_param.get_param(parent=main.mgis)
        self.actif_mobil_weir = self.cl_param.fg_actif_weirs()
        self.param_fg = self.cl_param.param_fg
        self.dmeth = self.cl_param.dmeth
        # resultats du mouvement de la vanne
        self.results_fg_weirs_mv = {}

        self.cl_regul = ClassMethRegul(self)
        self.cl_time = ClassMethTime(self)

    def init_fg_weirs(self):
        """
        Initialize floodgate weirs by gathering necessary information, validating parameters,
        and preparing variables for computation. This includes searching for control sections,
        linking parameters to the model, and initializing results.
        """
        # Get Section
        self.search_sec_control()
        self.search_weirs_to_param_fg()
        if not self.check_param():
            self.add_info("***** ERROR: the gates for the weirs\n COMPUTATION STOP")
            self.arret_comput = False
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
            if (param["level"] != param["level-dt"] or force):
                id_mas = param["id_mas"]
                updates = {
                    "Model.Weir.CrestLevel": param["level"],
                }
                for key, value in updates.items():
                    self.masc.set(key, value, id_mas)

    def init_res(self):
        """
        Initialize the results dictionary (`results_fg_weirs_mv`) for storing floodgate movement data.
        This includes time, level, cross-section, width, and regulation variable values.
        """
        self.results_fg_weirs_mv = {
            id_weir: {
                "TIME": [params["TIME"]],
                "ZSTR": [params["level"]],
                "REGVAR": [params["REGVAR_VAL"]],
            }
            for id_weir, params in self.param_fg.items()
        }

    def finalize(self, tfin):
        """
        Finalize the floodgate results by appending the final time and parameter values
        to the results dictionary for each link.

        :param tfin: Final time of the simulation.
        """
        if len(self.results_fg_weirs_mv) > 0:
            for id_weir, param in self.param_fg.items():
                res = self.results_fg_weirs_mv[id_weir]
                res["TIME"].append(tfin)
                res["ZSTR"].append(param["level"])
                res["REGVAR"].append(param["REGVAR_VAL"])

    def iter_fg(self, time, dtp):
        """
        Perform mobile weirs treatment during a simulation iteration.
        Depending on the mobility method (`method_mob`), it applies regulation, time-based,
        or fusible logic to compute new parameter values.

        :param time: Current simulation time.
        :param dtp: Time step.
        """
        for id_weir, param in self.param_fg.items():
            # effacement status
            status = self.masc.get("Model.Weir.State", param['id_mas'])
            if status:
                continue
            val_check = self.masc.get(param['CHECK_VAR'],
                                      param["SECCON"])
            if self.clapet(param):
                param["OPEN_CLOSE"] = "CLOSE"
                dnew = {"level": round(param["ZLIMITGATE"], 4)}
                self.fill_res_and_update(id_weir, time, param, dnew, val_check)
            elif param["method_mob"] == self.dmeth["meth_regul"]:
                if self.cl_regul.check_dt_regul(param, dtp):
                    self.cl_regul.state_regul(val_check, param)
                    dnew = self.cl_regul.law_gate_regul(param, time)
                    self.fill_res_and_update(id_weir, time, param, dnew, val_check)
            elif param["method_mob"] == self.dmeth["meth_time"]:
                dnew = self.cl_time.law_mth_time(param, time)
                self.fill_res_and_update(id_weir, time, param, dnew, val_check)

    def clapet(self, param):
        if param['CLAPMAREE'] and param["node"] + 1 <= self.model_size:
            aval = self.masc.get("State.Z", param["node"])
            amont = self.masc.get("State.Z", param["node"] + 1)
            if aval > amont:
                return True
        return False

    def fill_res_and_update(self, id_weir, time, param, dnew, val_check):
        """
        Update  mobile weirs parameters and fill the results dictionary with the new values.
        :param id_weir: Link ID.
        :param time: Current simulation time.
        :param param:  mobile weirs parameters dictionary.
        :param dnew: New computed values for the  mobile weirs.
        :param val_check: Regulation variable value to check.
        """
        param.update({
            # var time-dt
            "level-dt": param["level"],
            "TIME-dt": param["TIME"],
            "REGVAR_VAL-dt": param["REGVAR_VAL"],
            # var update in run
            "REGVAR_VAL": val_check,
            "level": dnew['level'],
            "TIME": time
        })
        self.fill_results_fg_mv(id_weir, param)
        self.update_var_mas()

    def check_param(self):
        """
        Validate the  mobile weirs parameters to ensure consistency.
        Returns True if all parameters are valid, otherwise False.
        """
        for id_weir, param in self.param_fg.items():
            if param["method_mob"] == self.dmeth["meth_regul"]:
                # check cas non possible
                if not self.cl_regul.check_param(param, id_weir):
                    return False
        return True

    def search_sec_control(self):
        """
        Identify the control section for each  mobile weirse link and determine the variable
        to be checked for regulation. This involves mapping model coordinates to parameters.
        """
        self.model_size, _, _ = self.masc.get_var_size("Model.X")
        coords = []
        for i in range(self.model_size):
            coords.append(self.masc.get("Model.X", i))
        coords = np.array(coords)
        for id_weir, param in self.param_fg.items():
            param['CHECK_VAR'] = "State.Z"
            # 2 valeur
            # 'PK' regule
            # 'abscissa' pk link
            if param["method_mob"] == self.dmeth["meth_regul"]:
                var = "PK"
                param['CHECK_VAR'] = ("State.Z" if param["VREG"] == "Z" else "State.Q")
            elif param["method_mob"] == self.dmeth["meth_time"]:
                var = "abscissa"
                param['CHECK_VAR'] = "State.Z"
            else:
                var = None
                self.add_info(f"Method {param['method_mob']} doesn't exist for numWeir {id_weir}")
                continue
            idx = (np.abs(coords - param[var])).argmin()
            if idx:
                param["SECCON"] = idx
            else:
                self.add_info("Regulation point not found for numWeirs {}.".format(id_weir))
        del coords

    def search_weirs_to_param_fg(self):
        """
        Establish weirs between the Mascaret model and the mobile weirs parameters.
        This includes retrieving initial values and preparing parameters for computation.
        """

        size_sing = self.masc.get_var_size("Model.Weir.Name")[0]
        tini = self.masc.get("Model.InitTime")
        coords = []
        lst_node = []
        lst_info = []
        for id_mas_weir in range(size_sing):
            typ = self.masc.get("Model.Weir.Type", id_mas_weir)
            if typ in [1,2,3, 4]: # filtre les type
                node = self.masc.get("Model.Weir.Node", id_mas_weir) - 1
                lst_node.append(node)
                abs = self.masc.get("Model.Weir.RelAbscissa", id_mas_weir)
                lst_info.append(id_mas_weir)
                coords.append(abs)

        coords = np.array(coords)
        for id_weir, param in self.param_fg.items():
            idx = (np.abs(coords - param["abscissa"])).argmin()
            if idx:
                id_mas = lst_info[idx]
                node = lst_node[idx]
                param.update({
                    "node" : node,
                    "id_mas":  id_mas,
                    "TIME0": tini,
                    "TIME": tini
                })
                if param["method_mob"] == self.dmeth["meth_regul"]:
                    self.cl_regul.init_meth_regul(param, id_weir)
                elif param["method_mob"] == self.dmeth["meth_time"]:
                    self.cl_time.init_meth_time(param)

                # inti var time-dt
                param.update({
                    "level-dt": param["level0"],
                    "TIME-dt": tini,
                    "REGVAR_VAL-dt": param["REGVAR_VAL"]
                })
            else:
                self.add_info("Id_mas not found for ID weirs {}.".format(id_weir))
        del coords


    def fill_results_fg_mv(self, id_weir, param):
        """
        Populate the results dictionary (`results_fg_weirs_mv`) with updated mobile weirs parameters
        if any changes occurred during the simulation.
        :param id_weir: Link ID.
        :param param: mobile weirs parameters dictionary.
        """
        res = self.results_fg_weirs_mv[id_weir]

        # Check if any parameter has changed
        zweir_var_dt = 'level-dt'
        zweir_var = 'level'

        if (param["level"] != param["level-dt"]) and( (res["TIME"][-1],res["ZSTR"][-1]) !=
                                                      (param["TIME-dt"], param[zweir_var_dt])):

            res["TIME"].append(param["TIME-dt"])
            res["REGVAR"].append(round(param["REGVAR_VAL-dt"], 3))
            res["ZSTR"].append(param[zweir_var_dt])

        # Update with new values
        res["TIME"].append(param["TIME"])
        res["REGVAR"].append(round(param["REGVAR_VAL"], 3))
        res["ZSTR"].append(param[zweir_var])

class ClassMethRegul:
    """Class for handling mobile weirs regulation logic."""

    def __init__(self, parent):
        """
        Initialize the regulation class.
        :param parent: Reference to the parent `ClassMobilWeirs` instance.
        """
        self.prt = parent
        self.arret_comput = parent.arret_comput
        self.add_info = parent.add_info
        self.masc = parent.masc
        self.compt_dt = 0
        self.break_weir = False

    def init_meth_regul(self, param, id_weir):
        """
        Initialize the regulation parameters for a mobile weirs.
        :param param: Dictionary of mobile weirs parameters.
        :param id_weir: Link ID.
        """
        param.update({
            "rup_level": param["level0"],
            'CLAPMAREE' : param["CLAPET"],
            "ZLIMITGATE" : param["ZMAXFG"],
            "level" :  max(param["ZINITREG"], param["level0"]),
            "REGVAR_VAL": self.masc.get(param['CHECK_VAR'], param["SECCON"]),
            "OPEN_CLOSE": "INIT"
        })
        # info de la vanne
        if param["DIRFG"] != "D":
            self.add_info(f"Non-consistency type mobile weirs with the moving part {id_weir}.")


    def check_param(self, param, id_weir):
        """
        Validate the consistency of regulation parameters, specifically `VREGOPEN` and `VREGCLOS`.
        :param param: Dictionary of mobile weirs parameters.
        :param id_weir: Link ID.
        :return: True if parameters are valid, False otherwise.
        """
        valo = param["VREGOPEN"]
        valf = param["VREGCLOS"]
        tol = param["TOLREG"]
        if valf + tol > valo - tol:
            if valf > valo:
                self.add_info(
                    "***** ERROR: "
                    "Closing level value must be lower opening level value\n"
                    " for the {} link ".format(id_weir)
                )
                return False
            else:
                param["TOLREG"] = 0
        return True

    def check_break(self, param, val_check):
        """
        Check if the mobile weirs should break.
        :param param: Dictionary of mobile weirs parameters.
        :param val_check: Current value of the regulation variable.
        """
        if val_check >= param["VBREAKREG"] :
            self.break_weir = True
            param.update({
                "rup_level": param["level"],
            })
        else:
            # reveient à l'état avant rupture
            if not param["BPERMREG"]:
                self.break_weir = False
                param.update({
                    "level": param["rup_level"],
                })


    def state_regul(self, val_check, param_fg):
        """
        Determine the state of the mobile weirs (OPEN, CLOSE, or MAINTAIN) based on the regulation variable.

        :param val_check: Current value of the regulation variable.
        :param param_fg: Dictionary of mobile weirs parameters.
        """
        tol = param_fg["TOLREG"]
        key = param_fg["OPEN_CLOSE"]
        # conditions
        conditions = {
            # fermeture par le bas
            ("INIT"): [(val_check >= param_fg["VREGOPEN"] - tol, "OPEN")],
            ("OPEN"): [
                (val_check <= param_fg["VREGCLOS"] + tol, "CLOSE"),
                (param_fg["VREGOPEN"] > val_check > param_fg["VREGCLOS"], "MAINT"),

            ],
            ("CLOSE"): [
                (val_check >= param_fg["VREGOPEN"] - tol, "OPEN"),
                (param_fg["VREGOPEN"] > val_check > param_fg["VREGCLOS"], "MAINT"),
            ],
            ("MAINT"): [
                (val_check >= param_fg["VREGOPEN"] - tol, "OPEN"),
                (val_check <= param_fg["VREGCLOS"] + tol, "CLOSE"),
                (param_fg["VREGOPEN"] > val_check > param_fg["VREGCLOS"], "MAINT"),
            ],
        }

        for condition, action in conditions.get(key, []):
            print(condition, key)
            if condition:
                param_fg["OPEN_CLOSE"] = action
                break
        print('val_check', 'action', 'param_fg["VREGOPEN"]', 'param_fg["VREGCLOS"]', 'tol')
        print(val_check,param_fg["OPEN_CLOSE"],  param_fg["VREGOPEN"], param_fg["VREGCLOS"],tol)
        return val_check

    def law_gate_regul(self, param, time):
        """
        Compute the new mobile weirs parameters.
        :param param: Dictionary of mobile weirs parameters.
        :param time: Current simulation time.
        :return: Dictionary of updated mobile weirs parameters.
        """

        if self.break_weir:
            return {
                "level": param["ZFINALREG"],
            }

        status = param["OPEN_CLOSE"]
        print(param["level"], status)
        if status in [None, "INIT", "MAINT"]:
            return {
                "level": param["level"],
            }
        dt = time - param["TIME"]
        dz_open = self.comput_dz(param["VELOFGOPEN"], dt, param["ZINCRFG"])
        dz_close = self.comput_dz(param["VELOFGCLOSE"], dt, param["ZINCRFG"])
        level, level0 = param["level"], param["level0"]
        zlimit_gate = param["ZLIMITGATE"]
        if status == "CLOSE":
            new_level = min(level + dz_close, zlimit_gate)
        elif status == "OPEN":
            new_level = max(level - dz_open, level0)
        print('new_level', 'dz_open', 'dz_close')
        print( new_level, dz_open, dz_close)
        return {
            "level": round(new_level,4),
        }

    def comput_dz(self, vit, dt, dzlimit=0):
        """
        Compute the displacement of the mobile weirs over a time step.
        :param vit: Velocity of the mobile weirs movement.
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
        Check if the mobile weirs should be treated during the current time step.
        :param param_fg: Dictionary of mobile weirs parameters.
        :param dtp: Time step.
        :return: True if the mobile weirs should be treated, False otherwise.
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
    """Class for handling time-based mobile weirs."""

    def __init__(self, parent):
        """
        Initialize the time-based movable "link" class 
        :param parent: Reference to the parent `ClassMobilWeirs` instance.
        """
        self.arret_comput = parent.arret_comput
        self.add_info = parent.add_info
        self.masc = parent.masc
        self.break_weir = False

    def init_meth_time(self, param):
        """
        Initialize the time-based parameters for a mobile weirs.
        :param param: Dictionary of mobile weirs parameters.
        """
        param.update({
            "TIMEZ": np.array(param["TIMEZ"]),
            "VALUEZ": np.array(param["VALUEZ"]),
            "REGVAR_VAL" : self.masc.get(param['CHECK_VAR'], param["SECCON"]),
            'CLAPMAREE': param["CLAPET"],
            "rup_level": param["level0"],
        })
        param["level"] = np.interp(param["TIME"], param["TIMEZ"], param["VALUEZ"])
        param["ZLIMITGATE"] = np.max(param["TIMEZ"])


    # def check_break(self, param, val_check):
    #     """
    #     Check if the mobile weirs should break.
    #     :param param: Dictionary of mobile weirs parameters.
    #     :param val_check: Current value of the regulation variable.
    #     """
    #     if val_check >= param["VBREAKT"]:
    #         self.break_weir = True
    #         param.update({
    #             "rup_level": param["level"],
    #         })
    #     else:
    #         # reveient à l'état avant rupture
    #         if not  param["BPERMT"]:
    #             self.break_weir = False
    #             param.update({
    #                 "level": param["rup_level"],
    #             })

    def law_mth_time(self, param, time):
        """
        Compute the new mobile weirs parameters.
        :param param: Dictionary of mobile weirs parameters.
        :param time: Current simulation time.
        :return: Dictionary of updated mobile weirs parameters.
        """
        # if self.break_weir:
        #     return {
        #         "level": param["ZFINALT"],
        #     }
        dnew = { "level": np.interp(time, param["TIMEZ"], param["VALUEZ"])}
        return dnew
