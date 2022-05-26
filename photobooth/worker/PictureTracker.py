#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from time import localtime, strftime
import os

class PictureTracker:
    """
    A simple helper class.

    It provides the filenames for the shots and assembled pictures
    Also keeps count of taken and previously existing pictures.
    """

    def __init__(self):
        """
        Initialize filenames to the given basename and search for existing files. Set the counter accordingly.
        """
        self.extension = '.jpg'
        self.shots_count = 4

        # Initialize tracker
        self.initializeNextPicture()
        # TODO create date folder if not exists before any new image is created

    def initializeNextPicture(self):
        """
        Reinitialize names, lists and counters for the next picture
        """
        # Set basename
        self._basedir = strftime("%Y-%m-%d", localtime())
        self._initializeFolder()
        self._basename = os.path.join(self._basedir, "")

        self._picture_time = datetime.now().strftime("%y%m%d%H%M%S")
        self._assembled_picture = None
        self._shots = []
        self._counter = 0

    def _initializeFolder(self):
        if not os.path.isdir(self._basedir):
            os.mkdir(self._basedir)

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

    def checkAllFilesExists(self):
        """
        Check if all files (shots and assembled picture) exists on local filesystem
        """
        # Check for all shots
        for i in range(1, self.shots_count+1):
            shot_path = self.getShotPath(i)
            if not os.path.isfile(shot_path):
                return False
        # Check for the assembled picture
        if not os.path.isfile(self.getPicturePath()):
            return False
        return True
