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

from datetime import datetime
from time import localtime, strftime
import os.path

class PictureTracker:
    """
    A simple helper class.

    It provides the filenames for the shots and assembled pictures
    Also keeps count of taken and previously existing pictures.
    """

    def __init__(self, basedir, prefix):
        """
        Initialize filenames to the given basename and search for existing files. Set the counter accordingly.
        """
        # Set basename and extension
        self._basedir = strftime(basedir, localtime())
        self._prefix = prefix
        if not prefix:
            self._basename = os.path.join(self._basedir, "")
        else:
            self._basename = os.path.join(self._basedir, prefix + "_")

        self.extension = '.jpg'
        self.count_width = 5

        # Initialize tracker
        self._assembled_picture = None
        self._shots = []
        self._counter = 0

    def initializeNextPicture(self):
        """
        Reinitialize names, lists and counters for the next picture
        """
        self._picture_time = datetime.now().strftime("%y%m%d%H%M%S")
        self._assembled_picture = None
        self._shots = []
        self._counter = 0

    @property
    def basedir(self):
        """Return the base directory for the files"""
        return self._basedir

    @property
    def basename(self):
        """Return the basename for the files"""
        return self._basename

    @property
    def shots(self):
        """Return the list of current shots"""
        return self._shots

    @property
    def picture_time(self):
        """Return the time of the picture"""
        return self._picture_time

    @property
    def filename(self):
        """Return the filename of the assembled picture"""
        return self._picture_time + self.extension

    def getPicturePath(self):
        """
        Generate a filename for the picture path, and update local variable
        """
        self._assembled_picture = self._basename + self._picture_time + self.extension
        return self._assembled_picture

    def getShotPath(self, count):
        """
        Return the full path for a given shot number
        """
        return self.basename + self._picture_time + "_shot-" + str(count) + self.extension

    def getNextShot(self):
        """
        Generate a filename for the next shot, and update counter/shot list
        """
        self._counter += 1
        shot_path = self.getShotPath(self._counter)
        self._shots.append(shot_path)
        return shot_path
