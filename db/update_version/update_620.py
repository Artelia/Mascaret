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
from db import MasObject as Maso

class ClassUpdate620:

    def __init__(self, check_tab):
        self.mdb = check_tab.mdb
        self.mgis = check_tab.mgis
        self.cht = check_tab

    def update620(self):
        self.mgis.add_info("*** Update 6.2.0  ***")
        valide = True
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        if "weirs_mob_val" in tabs:
            sql = f"ALTER TABLE {self.mdb.SCHEMA}.weirs_mob_val RENAME TO weirs_mob_val_old;"
            self.mdb.execute(sql)
        if "links_mob_val" in tabs:
            sql = f"ALTER TABLE {self.mdb.SCHEMA}.links_mob_val RENAME TO links_mob_val_old;"
            self.mdb.execute(sql)
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        lst_add_tab = ["links_mob_val", "weirs_mob_val"]
        valide = True
        for attr in lst_add_tab:
            if attr not in tabs:
                valid_add, _ = self.cht.add_tab(getattr(Maso, attr))
                if not valid_add:
                    self.mgis.add_info(f"Create  the {attr} table - ERROR")
                    valide = False
        d_conv_w = {
            "var_conv": {'TIME': 'TIMEZ',
                         'ZVAR': 'VALUEZ',
                         "ZHAUT": 'ZMAXFG',
                         "ZREG": "VREGCLOS",
                         "VDESC": "VELOFGOPEN",
                         "VMONT": "VELOFGCLOSE",
                         "UNITVD": "UNITVELO",
                         "UNITVH": "UNITVELC",
                         },
            "default": {
                "DIRFG": "'D'",
                "VREG": "'Z'",
                "CRITDTREG": "'NDTREG'",
                "NDTREG": 1,
                "DTREG": 0,
                "ZINCRFG": 9999.,
                "TOLREG": 0.05,
            },
            "get_value":
                {
                    "ZINITREG": "z_crest",
                    "ZFINALREG": "z_crest",
                    "PK": "abscissa",
                },
            "dbl_value":
                {
                    "VREGCLOS": ["VREGOPEN"],
                },
        }
        d_conv_l = {
            "var_conv": {
                "TYPE_TIME_VELO": "UNITVELO",
                "CRITDTREG": "CRITDTREG",
                "NDTREG": "NDTREG",
                "DTREG": "DTREG",
                "VELOFG": "VELOFCLOSE",
                "VREG": "VREG",
                "DIRFG": "DIRFG",
                "ZINCRFG": "ZINCRFG",
                "VREGCLOS": "VREGCLOS",
                "VREGOPEN": "VREGOPEN",
                "TOLREG": "TOLREG",
                "PK": "PK",
                "ZINITREG": "ZINITREG",
                "ZMAXFG": "ZMAXFG"
            },
            "default": {
                "USEBASIN": False,
                "NUMBASINREG": '',
                "VBREAKREG": 99999.,
                "BPERMREG": False,
            },
            "get_value":
                {
                    "ZFINALREG": "level"
                },
            "dbl_value": {
                "UNITVELO": ["UNITVELC"],
                "VELOFCLOSE": ["VELOFGOPEN"],
            },

        }

        for typ,d_conv in [("weirs",d_conv_w), ("links",d_conv_l)]:
            if valide:
                valide = self.conv_tab(typ, d_conv)

        if valide:
            lst_alt = [
                "ALTER TABLE {0}.struct_config ADD COLUMN IF NOT EXISTS  zbreak DOUBLE PRECISION DEFAULT 10000;",
                "ALTER TABLE {0}.struct_config ADD COLUMN IF NOT EXISTS  erase_flag boolean NOT NULL  DEFAULT FALSE;",
                "ALTER TABLE {0}.links ADD COLUMN IF NOT EXISTS method_mob text;",
                "ALTER TABLE {0}.links ADD COLUMN IF NOT EXISTS active_mob BOOLEAN;",
                "ALTER TABLE {0}.weirs ADD COLUMN IF NOT EXISTS erase_flag boolean NOT NULL   DEFAULT FALSE;",
            ]
            # Alter colonne value en text
            for sql in lst_alt:
                self.mdb.execute(sql.format(self.mdb.SCHEMA))
        return  valide

    def conv_tab(self, typ, d_conv):
        """
        :param typ (str): type 'weirs' or  'links'
        :param d_conv(dict): dictionnary of conversion
        :return:
        """
        valide = True
        cols = ['name_var', f'id_{typ}', 'id_order', 'value']
        tabs = self.mdb.list_tables(self.mdb.SCHEMA)
        if f"{typ}_mob_val_old" not in tabs:
            return valide
        dsrc = self.mdb.select(f"{typ}_mob_val_old", order=f'id_{typ}, id_order')
        dtarget = {col: [] for col in cols}
        if len(dsrc["name_var"]) > 0:
            id_typ = list(set(dsrc[f'id_{typ}']))
            lst_id = ','.join([f"'{id}'" for id in id_typ])
            if typ == 'weirs':
                lst_typ = ["gid", "name", "abscissa", "z_crest"]
            else:
                lst_typ = ["gid", "name", "level"]

            info_value = self.mdb.select(f"{typ}", where=f"gid IN ({lst_id})", order="gid",
                                         list_var=lst_typ)
            # ***************** Convert values ********************
            d_zbas = {}
            for idx, nvar in enumerate(dsrc["name_var"]):
                if nvar in d_conv["var_conv"].keys():
                    for col in cols:
                        if col == "name_var":
                            dtarget[col].append(f"'"+f'{d_conv["var_conv"][nvar]}'+"'")
                        else:
                            if col == "value" and dsrc["name_var"][idx] in ["TYPE_TIME_VELO", "UNITVD", "UNITVH"]:
                                dtarget[col].append('{:.0f}'.format(dsrc[col][idx]))
                            else:
                                dtarget[col].append(dsrc[col][idx])
                if f"{typ}" == "weirs" and nvar == "ZBAS":
                    d_zbas[idx] = dsrc[col][idx]

            # ***************** Default values ********************
            for idx in id_typ:
                for key, value in d_conv["default"].items():
                    dtarget[f'id_{typ}'].append(idx)
                    dtarget['id_order'].append(0)
                    dtarget['value'].append(value)
                    dtarget["name_var"].append(f"'{key}'")
                    if key in d_conv["dbl_value"]:
                        for var in d_conv["dbl_value"][key]:
                            dtarget[f'id_{typ}'].append(idx)
                            dtarget['id_order'].append(0)
                            dtarget['value'].append(value)
                            dtarget["name_var"].append(f"'{var}'")
                #***************** Get values ********************
                for key, get_var in d_conv["get_value"].items():
                    pos = info_value['gid'].index(idx)
                    dtarget[f'id_{typ}'].append(idx)
                    dtarget['id_order'].append(0)
                    dtarget['value'].append(info_value[get_var][pos])
                    dtarget["name_var"].append(f"'{key}'")


            print(d_zbas)
            if f"{typ}" == "weirs" and len(d_zbas)>0 :
                for idx, val in d_zbas.items():
                    err = self.mdb.update(f"{typ}", {idx: {"z_crest": val}}, var="gid")
                    if err:
                        print('iiiii')
                        break
            if err:
                err = self.mdb.insert2(f"{typ}_mob_val", dtarget)
            if err:
                self.mgis.add_info(f"Convert the {typ}_mob_val - ERROR")
                valide = False
                self.cht.del_tab(f"{typ}_mob_val")
                sql = f"ALTER TABLE {self.mdb.SCHEMA}.{typ}_mob_val_old RENAME TO {typ}_mob_val;"
                self.mdb.execute(sql)
            else:
                self.cht.del_tab(f"{typ}_mob_val_old")
            return valide