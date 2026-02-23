# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret – CreatModelAssim façade
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
from pathlib import Path

from .ClassCtrlKS import CtrlKs
from .ClassCtrlLaw import CtrlLaw


class CreatModelAssim(CtrlKs, CtrlLaw):
    """Façade aggregating :class:`CtrlKs` and :class:`CtrlLaw`.

    Use this class as the single entry point to maintain backward
    compatibility with existing callers.

    ``self.data`` is an :class:`~assim_data.AssimData` instance, loaded via
    :meth:`read_data_js`.
    """

    def __init__(self, mess=None) -> None:
        """Initialise the aggregated assimilation model.

        :param mess: Optional messaging callable passed to the base class.
        """
        super().__init__(mess=mess)
     
    def fill_assim_folder(self, type_ctrl):
        d_scen = self.data.dscen
        d_folder = self.data.get_folder()
        path_instance = Path(d_scen.get("path_instance", '.'))
        path_ref = path_instance / d_scen.get("folder_ref", 'run_ref')
        
        if  type_ctrl == "ctrlLaw"   and self.data.get('CtrlKS', False):
            path_ref = Path(d_folder.get('Analyse_ctrlKS', path_ref))
             
        if  d_scen.get("folder_init", '') != '':
            path_init = path_instance / d_scen.get("folder_ref", 'run_ref') / d_scen.get("folder_init")
  
        for name, folder in d_folder.items():
            if name in ['ref', 'init']:
                continue
            elif name.startswith("Analyse"):
                continue
            instance = self.data.get_instance(name)
            if name.endswith('_init'):
                self.clone_model(path_init, folder)
            else:
                self.clone_model(path_ref, folder)

            if 'ctrlKS' == instance.get('type_ctrl', '') and not name.startswith("Analyse"):
                self.fill_assim_folder_ks(instance, folder)

            if 'ctrlLaw' == instance.get('type_ctrl', '') and not name.startswith("Analyse"):
                self.fill_assim_folder_law(instance, folder)

    def fill_analyse(self, type_ctrl):
        """Placeholder: fill analysis folder for Ks assimilation.

        .. todo:: Implement folder filling logic.
        """
        pass
        # d_scen = self.data.dscen
        # d_folder = self.data.get_folder()
        # path_instance = Path(d_scen.get("path_instance", '.'))
        # path_ref = path_instance / d_scen.get("folder_ref", 'run_ref')
        #
        # if type_ctrl == "ctrlLaw" and self.data.get('CtrlKS', False):
        #     path_ref = Path(d_folder.get('Analyse_ctrlKS', path_ref))
        #
        # if d_scen.get("folder_init", '') != '':
        #     path_init = path_instance / d_scen.get("folder_ref", 'run_ref') / d_scen.get("folder_init")
        #
        # for name, folder in d_folder.items():
        #     if not name.startswith("Analyse"):
        #         continue
        #     instance = self.data.get_instance(name)
        #     if name.endswith('_init'):
        #         self.clone_model(path_init, folder)
        #     else:
        #         self.clone_model(path_ref, folder)
        #
        #     if 'ctrlKS' == instance.get('type_ctrl', '') and not name.startswith("Analyse"):
        #         self.fill_folder_ana_ks(instance, folder)
        #
        #     if 'ctrlLaw' == instance.get('type_ctrl', '') and not name.startswith("Analyse"):
        #         self.fill_folder_ana_law(instance, folder)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    assimil = CreatModelAssim()
    assimil.read_data_js(".", "data_assim.json")

    print(assimil.data)          # AssimData(file=..., sections=[...])
    print(assimil.data.dscen)    # scenario dict
    print(assimil.data.drun)     # run config dict
    assimil.lst_instance_run_ctrlks_js()
    assimil.lst_instance_run_ctrl_law_js()
    assimil.fill_assim_folder(type_ctrl='ctrlLaw')

