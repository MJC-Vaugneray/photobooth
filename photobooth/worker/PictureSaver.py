#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

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
