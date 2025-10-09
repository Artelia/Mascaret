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

from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.core import QgsApplication
from qgis.gui import *
from qgis.utils import *

from .ClassCreatModel import ClassCreatModel
from ..Function import TypeErrorModel
from ..Function import copy_dir_to_dir
from ..Structure.ClassLinkFGParam import ClassLinkFGParam
from ..Structure.ClassMobilWeirsParam import ClassMobilWeirsParam
from ..Structure.ClassPostPreFG import ClassPostPreFG
from ..WaterQuality.ClassMascWQ import ClassMascWQ
from ...ui.custom_control import ClassWarningBox


class ClassMascaret:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, main, rep_run=None):
        self.mgis = main
        self.dbg = main.DEBUG
        self.mdb = self.mgis.mdb
        self.iface = self.mgis.iface
        self.cond_api = self.mgis.cond_api
        if not rep_run:
            # default folder
            self.run_folder= os.path.join(self.mgis.masplugPath, "mascaret")
        else:
            self.run_folder = rep_run

        # if not os.path.isdir(self.run_folder):
        #     os.mkdir(self.run_folder)
        self.dossier_file_masc_ori = os.path.join(self.mgis.masplugPath, "template_file")
        self.dossierFile_bin = os.path.join(self.mgis.masplugPath, "bin")
        self.box = ClassWarningBox()
        # state list
        self.listeState = ["Steady", "Unsteady", "Transcritical unsteady"]
        # kernel list
        self.Klist = ["steady", "unsteady", "transcritical"]

        self.wq = ClassMascWQ(self.mgis, self.run_folder)

        self.save_res_struct = None

        self.err_model = {}
        self.err_model["timeLaw"] = TypeErrorModel("timeLaw", " ERROR : Law Time", stop=True)
        self.err_model["lInflowPos"] = TypeErrorModel("lInflowPos", "WARNING : the inflow position")

        self.clmod = ClassCreateModel(
            self.mdb, self.run_folder, self.cond_api, self.dbg
        )