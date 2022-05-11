#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from colorsys import hsv_to_rgb

from PIL import Image

from .CameraInterface import CameraInterface


class CameraDummy(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = False
        self._size = (1920, 1280)

        self._hue = 0

        logging.info('Using CameraDummy')

    def getPreview(self):

        return self.getPicture()

    def getPicture(self):

        self._hue = (self._hue + 1) % 360
        r, g, b = hsv_to_rgb(self._hue / 360, .2, .9)
        return Image.new('RGB', self._size, (int(r * 255), int(g * 255),
                                             int(b * 255)))
