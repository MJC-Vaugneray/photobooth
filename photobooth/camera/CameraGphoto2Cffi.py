#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import logging

from PIL import Image

import gphoto2cffi as gp

from .CameraInterface import CameraInterface


class CameraGphoto2Cffi(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = True

        logging.info('Using gphoto2-cffi bindings')

        self._setupCamera()

    def cleanup(self):

        try:
            self._cap.config['imgsettings']['imageformat'].set(self._imgfmt)
            self._cap.config['imgsettings']['imageformatsd'].set(
                self._imgfmtsd)
            # self._cap.config['settings']['autopoweroff'].set(
            #     self._autopoweroff)
        except BaseException as e:
            logging.warn('Error while changing camera settings: {}.'.format(e))

    def _setupCamera(self):

        self._cap = gp.Camera()
        logging.info('Supported operations: %s',
                     self._cap.supported_operations)

        try:
            # make sure camera format is not set to raw
            imgfmt = 'Large Fine JPEG'
            self._imgfmt = self._cap.config['imgsettings']['imageformat'].value
            if 'raw' in self._imgfmt.lower():
                self._cap.config['imgsettings']['imageformat'].set(imgfmt)
            self._imgfmtsd = (
                self._cap.config['imgsettings']['imageformatsd'].value)
            if 'raw' in self._imgfmtsd.lower():
                self._cap.config['imgsettings']['imageformatsd'].set(imgfmt)

            # make sure autopoweroff is disabled
            # this doesn't seem to work
            # self._autopoweroff = int(
            #     self._cap.config['settings']['autopoweroff'].value)
            #  if self._autopoweroff > 0:
            #      self._cap.config['settings']['autopoweroff'].set("0")
        except BaseException as e:
            logging.warn('Error while changing camera settings: {}.'.format(e))

        # print current config
        self._printConfig(self._cap.config)

    @staticmethod
    def _configTreeToText(config, indent=0):

        config_txt = ''

        for k, v in config.items():
            config_txt += indent * ' '
            config_txt += k + ': '

            if hasattr(v, '__len__') and len(v) > 1:
                config_txt += '\n'
                config_txt += CameraGphoto2Cffi._configTreeToText(v,
                                                                  indent + 4)
            else:
                config_txt += str(v) + '\n'

        return config_txt

    @staticmethod
    def _printConfig(config):
        config_txt = 'Camera configuration:\n'
        config_txt += CameraGphoto2Cffi._configTreeToText(config)
        logging.info(config_txt)

    def setActive(self):

        try:
            self._cap._get_config()['actions']['viewfinder'].set(True)
            self._cap._get_config()['settings']['output'].set('PC')
        except BaseException as e:
            logging.warn('Cannot set camera output to active: {}.'.format(e))

    def setIdle(self):

        try:
            self._cap._get_config()['actions']['viewfinder'].set(False)
            self._cap._get_config()['settings']['output'].set('Off')
        except BaseException as e:
            logging.warn('Cannot set camera output to idle: {}.'.format(e))

    def getPreview(self):

        return Image.open(io.BytesIO(self._cap.get_preview()))

    def getPicture(self):

        return Image.open(io.BytesIO(self._cap.capture()))
