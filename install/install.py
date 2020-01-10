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
from PyQt5.QtCore import QUrl, QEventLoop, QTimer
from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsNetworkAccessManager


class ClassDownloadMasc():
    """
    Class allowing to download needed files
    """
    def __init__(self, local_install=None):
        self.masplug_path = local_install
        self.version = 'master'
        if self.version == 'experimental':
            self.branch = 'dev_hyd_struct'
        else:
            self.branch = 'master'
        self.url_base = 'https://raw.githubusercontent.com/Artelia/Mascaret/'

    def douwnload_bin_dir(self):
        """
        download "bin" represitory
        :return:
        """

        self.manager = QgsNetworkAccessManager()
        self.manager = self.manager.instance()

        rep = 'bin'
        file_list = ['mascaret.exe',
                     'mascaret_linux']
        url_path = posixpath.join(self.branch, rep)
        url = posixpath.join(self.url_base, url_path)

        os.makedirs(os.path.join(self.masplug_path, rep), exist_ok=True)
        for filen in file_list:
            url2 = posixpath.join(url, filen)
            paht_file = os.path.join(self.masplug_path, rep, filen)
            self.download(url2, paht_file)

    def download(self, url, path_file):
        """
        dowload function
        :param url: url path of file
        :param path_file: path to save file
        :return:
        """
        self.file_install = path_file
        self.url = url
        self.loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.loop.exit(1))
        timer.start(100000)  # 10 second time-out
        # req = QNetworkRequest(QUrl('https://www.python.org/'))
        req = QNetworkRequest(QUrl(url))
        self.result = self.manager.get(req)
        self.result.finished.connect(self.fin_req)
        print('fetching request...')
        if self.loop.exec_() == 0:
            timer.stop()
            print('received: ', self.result.readAll().count())
        else:
            print('request timed-out :(')

    def fin_req(self):
        """
        action when received the request
        :return:
        """
        if self.result.error() != QNetworkReply.NoError:
            self.loop.exit()
            return
        self.loop.exit()
        # save file
        self.save_file(self.result.readAll())

    def save_file(self, data):
        """
        Save file
        :param data: data in file
        :return:
        """
        fch = open(self.file_install, 'wb')
        with fch:
            fch.write(data)


if __name__ == "__main__":
    pass
