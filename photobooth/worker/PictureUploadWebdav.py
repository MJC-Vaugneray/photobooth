#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests

from pathlib import Path

from .WorkerTask import WorkerTask


class PictureUploadWebdav(WorkerTask):

    def __init__(self, config):

        super().__init__()

        self._baseurl = config.get('UploadWebdav', 'url')
        if config.getBool('UploadWebdav', 'use_auth'):
            self._auth = (config.get('UploadWebdav', 'user'),
                          config.get('UploadWebdav', 'password'))
        else:
            self._auth = None

    def do(self, picture, filename):

        url = self._baseurl + '/' + Path(filename).name
        logging.info('Uploading picture as %s', url)

        r = requests.put(url, data=picture.getbuffer(), auth=self._auth)
        if r.status_code in range(200, 300):
            logging.warn(('PictureUploadWebdav: Upload failed with '
                          'status code {}').format(r.status_code))
