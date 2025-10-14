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

import os
import shutil
import sys

from qgis.PyQt.QtWidgets import (
                        QInputDialog,
                        QWidget
                    )

# from .ClassCreatModel import ClassCreatModel
from ..Function import TypeErrorModel
from ..Function import copy_dir_to_dir
from ..Structure.ClassLinkFGParam import ClassLinkFGParam
from ..Structure.ClassMobilWeirsParam import ClassMobilWeirsParam

from ..WaterQuality.ClassMascWQ import ClassMascWQ
from ...ui.custom_control import ClassWarningBox
from .Fct_model_file import clear_folder
from .ClassDictRun import ClassDictRun

class ClassMascaret2:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main, obj_model):
        self.mgis = main
        self.mdb = self.mgis.mdb
        self.obj_model = obj_model

    def generate_models_folders(self):
        dgeneral = self.dmodel['general']

        # Clear repertoire
        err = clear_folder(dgeneral['path_runs'])
        if err:
            self.mgis.add_info(f"ERROR : {err}",box=True, btype='CRITICAL')

        # generation arbre de repertoire
        # génération des fichiers de modèle

        #

        # if not dgeneral['path_runs']:
        #
        #
        # try:
        #     os.makedirs(path, exist_ok=True)
        # except OSError as e:
        #     raise OSError(f"Failed to create folder at {path}: {e}")
        #
        # clear_folder(dgeneral['path_runs'])
        # self.
        # os.chdir(dgeneral['path_runs'])











