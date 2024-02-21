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

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


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
            for name_obj, obj in self.derror.items():
                if obj['type'] == 'critic':
                    return True
        return False

    def add_mess(self, code_err, type_mes, message):
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

    def message(self):
        txt = ''
        for key, item in self.derror.items():
            if item['type'] == 'debug':
                txt += item['message'] + '\n'
            elif item['type'] == 'info':
                txt += item['message'] + '\n'
            elif item['type'] == 'warning':
                txt += '** Warning ** : ' + item['message'] + '\n'
            elif item['type'] == 'critic':
                txt += '** Error ** : \n' + item['message'] + '\n'
        return txt

    def mess_fill_other_obj(self, obj_ori):
        """
        Transfet message of a message class object (obj_ori) at a  message class object target
        :param obj_ori : (object) ClassMessage object
        """
        fill = {}
        for key, item in obj_ori.derror.items():
            if key not in self.derror:
                self.derror[key] = item
                fill[key] = item
        return fill
