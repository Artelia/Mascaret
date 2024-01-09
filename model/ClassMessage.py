# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 :  Mascaret
Description          : Mascaret tools for QGIS
Date                 : Juin 2023

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
import datetime

from qgis.PyQt.QtCore import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from qgis.PyQt.QtWidgets import *

from .ui.custom_control import ClassWarningBox

class ClassMessage:
    """Class contain  model files creation and run model mascaret"""

    def __init__(self):
        self.derror = {}
        # self.derror[code_err] = {'type':'type', 'message': txt}
        self.type_mes = ['debug', 'info', 'warning', 'critic']

    def clear_derror(self):
        self.derror = {}
        #

    def get_critic_status(self):
        """
        get critical status
         Returns:
            :return True if error stop model
        """
        if len(self.derror.keys()) > 0:
            for name_obj in self.derror.keys():
                if name_obj['type'] == 'critic':
                    return True
        else:
            return False

    def add_mess(self, code_err, type_mes, message ):
        """
        add element error
        Args:
            :param code_err : error code
            :param type_mes : message type
            :param message :message
        """
        self.derror[code_err] = {"type": type_mes, "message": message}

    def del_mess(self, code_err):
        """
        delete in error dict
        Args:
            :param code_err : error code
        """
        if code_err in self.derror.keys():
            del self.derror[code_err]

    def get_mess(self, code_err):
        """
        get txt in error dict
        Args:
            :param code_err : error code
        Returns:
            :return  message : message
        """
        return self.derror[code_err]["message"]

    def get_type(self, code_err):
        """
        get txt in error dict
        Args:
            :param code_err : error code
        Returns:
            :return  type : type
        """
        return self.derror[code_err]["type"]

