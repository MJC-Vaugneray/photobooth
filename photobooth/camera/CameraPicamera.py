#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import logging

from PIL import Image

from picamera import PiCamera

from .CameraInterface import CameraInterface


class CameraPicamera(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = True

        logging.info('Using PiCamera')

        self._cap = None

        self.setActive()
        self._preview_resolution = (self._cap.resolution[0] // 2,
                                    self._cap.resolution[1] // 2)
        self.setIdle()

    def setActive(self):

        if self._cap is None or self._cap.closed:
            self._cap = PiCamera()

    def setIdle(self):

        if self._cap is not None and not self._cap.closed:
            self._cap.close()
            self._cap = None

    def getPreview(self):

        self.setActive()
        stream = io.BytesIO()
        self._cap.capture(stream, format='jpeg', use_video_port=True,
                          resize=self._preview_resolution)
        stream.seek(0)
        return Image.open(stream)

    def getPicture(self):

        self.setActive()
        stream = io.BytesIO()
        self._cap.capture(stream, format='jpeg', resize=None)
        stream.seek(0)
        return Image.open(stream)
