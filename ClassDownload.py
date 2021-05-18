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
import posixpath

from qgis.core import QgsNetworkAccessManager
from qgis.PyQt.QtCore import qVersion

if int(qVersion()[0]) < 5:
    from PyQt4.QtCore import QUrl, QEventLoop, QTimer
    from PyQt4.QtNetwork import QNetworkRequest, QNetworkReply
else:
    from PyQt5.QtCore import QUrl, QEventLoop, QTimer
    from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply


class ClassDownloadMasc:
    """
    Class allowing to download needed files
    """

    def __init__(self, path_work=None, url_base=None, parent=None):
        self.masplug_path = None

        if url_base is None:
            self.url_base = ''
        else:
            self.url_base = url_base
        self.parent = parent
        if parent is None:
            self.dbg = True
        else:
            self.dbg = self.parent.DEBUG

        if path_work is None:
            self.masplug_path = ''
        else:
            self.masplug_path = path_work
        self.file_install = None
        self.url = None
        self.manager = QgsNetworkAccessManager()
        self.manager = self.manager.instance()

    def download_dir(self, dir):
        """
        download dir represitory
        :param dir : (dict)the keys are represitory and the element is list_file
        :return:
        """
        for rep in dir.keys():
            self.print_('Downloading executable file in "{}" directory\n'
                        'Download ...'.format(rep))
            url = posixpath.join(self.url_base, rep)
            os.makedirs(os.path.join(self.masplug_path, rep), exist_ok=True)
            for filen in dir[rep]:
                url2 = posixpath.join(url, filen)
                paht_file = os.path.join(self.masplug_path, rep, filen)
                self.download_file(url2, paht_file)
            self.print_('Downloading Done')

    def download_file(self, url, path_file):
        """
        download function
        :param url: url path of file
        :param path_file: path to save file
        :return:
        """
        self.file_install = path_file
        self.url = url
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: loop.exit(1))
        timer.start(100000)  # 10 second time-out
        # req = QNetworkRequest(QUrl('https://www.python.org/'))
        req = QNetworkRequest(QUrl(url))
        result = self.manager.get(req)
        result.finished.connect(lambda: self.fin_req(loop, result))
        self.print_('fetching request...', self.dbg)
        if loop.exec_() == 0:
            timer.stop()
            self.print_('{} is received: {}'.format(os.path.basename(path_file),
                                                    result.readAll().count()),
                        self.dbg)
        else:
            self.print_('request timed-out')

    def print_(self, txt, dbg=True):
        if self.parent is None and dbg:
            print(txt)
        else:
            if dbg:
                self.parent.add_info(txt)

    def fin_req(self, loop, result):
        """
        action when received the request
        :param loop (obj)
        :param result (obj) reply in request
        :return:
        """
        if result.error() != QNetworkReply.NoError:
            self.print_("Error of request : {}".format(self.url))
            loop.exit(1)
            return
        loop.exit()
        # save file
        self.save_file(result.readAll())

    def save_file(self, data):
        """
        Save file
        :param data: data in file
        :return:
        """
        fch = open(self.file_install, 'wb')
        with fch:
            fch.write(data)
