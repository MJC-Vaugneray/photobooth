#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import logging

from PIL import Image

import gphoto2 as gp

from .CameraInterface import CameraInterface


class CameraGphoto2(CameraInterface):

    def __init__(self):

        super().__init__()

        self.hasPreview = True
        self.hasIdle = True

        logging.info('Using python-gphoto2 bindings')

        self._setupLogging()
        self._setupCamera()

    def cleanup(self):

        self._changeConfig('Shutdown')
        self._cap.exit(self._ctxt)

    def _setupLogging(self):

        gp.error_severity[gp.GP_ERROR] = logging.ERROR
        gp.check_result(gp.use_python_logging())

    def _setupCamera(self):

        self._ctxt = gp.Context()
        self._cap = gp.Camera()
        self._cap.init(self._ctxt)

        logging.info('Camera summary: %s',
                     str(self._cap.get_summary(self._ctxt)))

        # read model specific configuration
        config = self._cap.get_config()
        self.loadConfig(config.get_child_by_name('cameramodel').get_value())

        # set startup configuration
        self._changeConfig('Startup')

        #  print current config
        self._printConfig(self._cap.get_config())

    @staticmethod
    def _configTreeToText(tree, indent=0):

        config_txt = ''

        for chld in tree.get_children():
            config_txt += indent * ' '
            config_txt += chld.get_label() + ' [' + chld.get_name() + ']: '

            if chld.count_children() > 0:
                config_txt += '\n'
                config_txt += CameraGphoto2._configTreeToText(chld, indent + 4)
            else:
                config_txt += str(chld.get_value())
                try:
                    choice_txt = ' ('

                    for c in chld.get_choices():
                        choice_txt += c + ', '

                    choice_txt += ')'
                    config_txt += choice_txt
                except gp.GPhoto2Error:
                    pass
                config_txt += '\n'

        return config_txt

    @staticmethod
    def _printConfig(config):

        config_txt = 'Camera configuration:\n'
        config_txt += CameraGphoto2._configTreeToText(config)
        logging.info(config_txt)

    def _changeConfig(self, state):

        if self.config[state]:
            config = self._cap.get_config()

            for key in self.config[state]:
                val = config.get_child_by_name(key)
                if val.get_value().lower() != self.config[state][key].lower():
                    val.set_value(self.config[state][key])

            try:
                self._cap.set_config(config)
            except BaseException as e:
                logging.warn(('CameraGphoto2: Applying config for state '
                              '"{}" failed: {}').format(state, e))

    def setActive(self):

        self._changeConfig('Active')

    def setIdle(self):

        self._changeConfig('Idle')

    def getPreview(self):

        camera_file = self._cap.capture_preview()
        file_data = camera_file.get_data_and_size()
        return Image.open(io.BytesIO(file_data))

    def getPicture(self):

        file_path = self._cap.capture(gp.GP_CAPTURE_IMAGE)
        camera_file = self._cap.file_get(file_path.folder, file_path.name,
                                         gp.GP_FILE_TYPE_NORMAL)
        file_data = camera_file.get_data_and_size()
        return Image.open(io.BytesIO(file_data))
