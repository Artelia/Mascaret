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


class ClassDownloadMasc():
    def __init__(self, parent=None):

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

        self.url = 'https://raw.githubusercontent.com/Artelia/Mascaret/{}/'.format(self.branch)
    def load_bin(self):
        dir = 'bin'
        file_list = [    'mascaret.exe',
                          'mascaret_linux']
        url2=self.url+'{}/'.format(dir)
        os.makedirs(dir, exist_ok=True)
        self.download_rep(url2, file_list)

    def download_rep(self, url,file_list, typ_w='wb'):
        """
        Download file in directory
        :param url:
        :param file_list:
        :return:
        """
        for filen in file_list:
            s = requests.Session()
            s.proxies = self.prox
            result = s.get(url + filen, timeout=2)
            with open(os.path.join(dir,filen), typ_w) as fil:
                fil.write(result.content)
            s.close()

    def main(self):
        self.load_bin()

if __name__ == "__main__":
    cl_load = ClassDownloadMasc()
    cl_load.main()