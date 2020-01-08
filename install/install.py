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
import requests
import os
from urllib.parse import urljoin
import posixpath


class ClassDownloadMasc:
    def __init__(self, local_install=None):
        self.masplug_path = local_install
        self.http_proxy = "http://proxy.arteliagroup.com:3128"
        self.https_proxy = "http://proxy.arteliagroup.com:3128"
        self.ftp_proxy = ""
        self.prox = {"http": self.http_proxy,
                     "https": self.https_proxy,
                     "ftp": self.ftp_proxy}
        self.version = 'master'
        if self.version == 'experimental':
            self.branch = 'dev_hyd_struct'
        else:
            self.branch = 'master'
        self.url_base = 'https://raw.githubusercontent.com/Artelia/Mascaret/'

    def load_bin(self):
        rep = 'bin'
        file_list = ['mascaret.exe',
                     'mascaret_linux']
        url_path = posixpath.join(self.branch, rep)
        url2 = urljoin(self.url_base, url_path)

        os.makedirs(os.path.join(self.masplug_path, rep), exist_ok=True)

        print(url2, os.path.realpath(rep))
        self.download_rep(url2, rep, file_list)

    def download_rep(self, url, rep, file_list, typ_w='wb'):
        """
        Download file in directory
        :param rep
        :param url:
        :param file_list:
        :param typ_w:
        :return:
        """
        for filen in file_list:
            with requests.Session() as s:
                s.proxies = self.prox
                result = s.get(urljoin(url, filen), timeout=2)
                with open(os.path.join(self.masplug_path, rep, filen), typ_w) as fil:
                    fil.write(result.content)

    def main(self):
        self.load_bin()


if __name__ == "__main__":
    cl_load = ClassDownloadMasc()
    cl_load.branch = 'download_exe'
    cl_load.main()
