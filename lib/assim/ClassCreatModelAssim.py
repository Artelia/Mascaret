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
import numpy as np
import shutil
import json
from pathlib import Path
import traceback
from datetime import datetime

class CreatModelAssim:
    """Class Assimilation gestion base donneee"""
    DATA_ASSIM_FILE = "data_assim.json"
    def __init__(self, mess= None):
        """Initialize the initializer.
        """
        self.data = {}
        self.mess=mess
        self.num_mess = 0


    def add_info(self, txt):
        if self.mess:
            self.mess('clAssim{}'.format(self.num_mess), 'info', txt)
            self.num_mess += 1
        else:
            print(txt)

    def clone_model(self, source_folder=None, target_folder=None):
        """Copy initialization files from source to target folder.
        :return: True if operation succeeded, False otherwise.
        :rtype: bool
        """
        ignore = ['.opt', '.lis']
        source = Path(source_folder)
        target = Path(target_folder)
        #
        # # Validate source folder
        if not source.exists() or not source.is_dir():
            self.add_info(f"Invalid source folder: {source}")
            return False
        #
        # # Validate target folder
        if not target.exists() or not target.is_dir():
            self.add_info(f"Invalid target folder: {target}")
            return False

        copied_count = 0
        for file_path in source.iterdir():
            if not file_path.is_file():
                continue

        #     # Check if file has a valid suffix
            if file_path.suffix in ignore:
                continue
            try:
                target_path = target / file_path.name
                shutil.copy2(file_path, target_path)  # copy2 preserves metadata
                copied_count += 1
            except Exception as e:
                self.add_info(
                    f"Failed to copy file '{file_path.name}': {str(e)}",
                )
        return True

    def read_data_js(self, filein=None):
        
        filein = filein or self.DATA_ASSIM_FILE
        

        with open(filein, "r") as file:
            self.data = json.load(file)

        # Convertir les starttime en datetime
        self.convert_starttime(self.data.get('instance', []))

        if self.data.get('generate_instance'):
            dscen = self.data['generate_instance'].get('dscen')
            if dscen:
                self.convert_starttime([dscen])

    def convert_starttime(self, instances):
        """Convertit les starttime ISO en objets datetime"""
        for instance in instances:
            if instance.get("starttime"):
                try:
                    instance["starttime"] = datetime.fromisoformat(instance["starttime"])
                except ValueError:
                    pass
