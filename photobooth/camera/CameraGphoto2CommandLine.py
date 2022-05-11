#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import subprocess

from PIL import Image

from .CameraInterface import CameraInterface


class CameraGphoto2CommandLine(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = False
        self.hasIdle = False

        logging.info('Using gphoto2 via command line')

        if os.access('/dev/shm', os.W_OK):
            logging.debug('Storing temp files to "/dev/shm/photobooth.jpg"')
            self._tmp_filename = '/dev/shm/photobooth.jpg'
        else:
            logging.debug('Storing temp files to "/tmp/photobooth.jpg"')
            self._tmp_filename = '/tmp/photobooth.jpg'

        self.setActive()

    def setActive(self):

        self._callGphoto('-a', '/dev/null')

    def getPicture(self):

        self._callGphoto('--capture-image-and-download', self._tmp_filename)
        return Image.open(self._tmp_filename)

    def _callGphoto(self, action, filename):

        cmd = 'gphoto2 --force-overwrite --quiet {} --filename {}'
        return subprocess.check_output(cmd.format(action, filename),
                                       shell=True, stderr=subprocess.STDOUT)
