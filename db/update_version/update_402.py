# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : Aprile, 2025
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
from HydroLawsDialog import dico_typ_law
from db import MasObject as Maso

class ClassUpdate402:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab


    def update402(self):
        """add new table law and convert"""
        try:
            lst_tab = self.mdb.list_tables()
            if "laws" in lst_tab:
                info = self.mdb.select("laws")
            else:
                info = {}
            # conv_dict = {'time': 'time',
            #              'Q': 'flowrate',
            #              'Z': 'z',
            #              'Zup': 'z_upstream',
            #              'Zdown': 'z_downstream',
            #              'Zlow': 'z_lower',
            #              'Zupp': 'z_up',
            #              }

            if "law_config" not in lst_tab:
                vconf, _ = self.cht.add_tab(Maso.law_config, False)
                if not vconf:
                    self.mgis.add_info("Error  add table: law_config")
                    return False
                if "id" in info.keys():
                    # law_config
                    tab = {id: {"comment": ""} for id in range(len(info["name"]))}
                    cmpt = 1
                    for key, item in info.items():
                        if key in [
                            "z",
                            "flowrate",
                            "time",
                            "z_upstream",
                            "z_downstream",
                            "z_lower",
                            "z_up",
                        ]:
                            pass
                        elif key in ["starttime", "endtime"]:
                            for id, val in enumerate(item):
                                if val:
                                    tab[id][key] = val.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    tab[id][key] = None
                        elif key in ["active"]:
                            for id, val in enumerate(item):
                                tab[id][key] = val
                        elif key == "name":
                            for id, val in enumerate(item):
                                if val in [
                                    tmp["name"] for tmp in tab.values() if "name" is tmp.keys()
                                ]:
                                    tab[id]["name"] = val + "{}".format(cmpt)
                                    cmpt += 1
                                else:
                                    tab[id]["name"] = val
                                tab[id]["geom_obj"] = val
                        elif key == "type":
                            for id, val in enumerate(item):
                                tab[id]["id_law_type"] = val

                    listimport = [
                        "id",
                        "name",
                        "geom_obj",
                        "starttime",
                        "endtime",
                        "id_law_type",
                        "active",
                        "comment",
                    ]

                    if len(tab.keys()) > 0:
                        err = self.mdb.insert("law_config", tab, listimport)
                        if len(tab.keys()) > 0:
                            maxk = max(tab.keys())
                            sql = "ALTER SEQUENCE {}.law_config_id_seq " "RESTART WITH {};".format(
                                self.mdb.SCHEMA, maxk + 1
                            )
                            self.mdb.run_query(sql)
                        if err:
                            self.mgis.add_info("Error: Insert law_config")
                            self.cht.del_tab("law_config")
                            return False

            if "law_values" not in lst_tab:
                vval, _ = self.cht.add_tab(Maso.law_values, False)
                if not vval:
                    self.mgis.add_info("Error  add table: law_values")
                    return False

                if "id" in info.keys():
                    # law_value
                    valinsert = {"id_law": [], "id_var": [], "id_order": [], "value": []}
                    for id_loi in range(len(info["name"])):
                        id_type = info["type"][id_loi]
                        lst_var = [tmp["code"] for tmp in dico_typ_law[id_type]["var"]]

                        for id_var, var in enumerate(lst_var):
                            # lst_val = info[conv_dict[var]][id_loi].split()
                            lst_val = info[var][id_loi].split()
                            for id_val, val in enumerate(lst_val):
                                valinsert["id_law"].append(id_loi)
                                valinsert["id_var"].append(id_var)
                                valinsert["id_order"].append(id_val)
                                valinsert["value"].append(float(val))
                    if len(valinsert["id_law"]) > 0:
                        err = self.mdb.insert2("law_values", valinsert)
                        if err:
                            self.mgis.add_info("Error  Insert law_values")
                            self.cht.del_tab("law_values")
                            return False
            return True
        except Exception as e:
            self.mgis.add_info("Error laws_to_new: {}".format(str(e)))
            return False