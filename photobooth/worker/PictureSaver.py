#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

from .WorkerTask import WorkerTask


class PictureSaver(WorkerTask):

    def __init__(self, basedir):

        super().__init__()

        # Ensure directory exists
        if not os.path.exists(basedir):
            os.makedirs(basedir)

    def do(self, picture, filepath):

        logging.info('Saving picture as %s', filepath)
        with open(filepath, 'wb') as f:
            f.write(picture.getbuffer())
