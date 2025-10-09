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

import datetime
import json
import os
import re
import shutil
import pandas as pd
from xml.etree.ElementTree import ElementTree, Element, SubElement
from xml.etree.ElementTree import parse as et_parse

from ..ClassMessage import ClassMessage
from ..Function import del_symbol
from ..Function import str2bool, del_accent
from ..HydroLawsDialog import dico_typ_law


class ClassCreatFilesModels:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self, mdb, dossier_file_masc, cond_api, dbg):
        self.dbg = dbg
        self.mdb = mdb
        self.cond_api = cond_api
        self.dossier_file_masc = dossier_file_masc
        self.basename = "mascaret"
        self.mess = ClassMessage()
        self.geo_file = self.basename + ".geo"
        self.casier_file = self.basename + ".casier"
        self.dico_basinnum = {}
        self.dico_linknum = {}



