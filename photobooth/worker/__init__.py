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

from .. import StateMachine
from ..Threading import Workers

from .PictureTracker import PictureTracker
from .PictureMailer import PictureMailer
from .PictureSaver import PictureSaver
from .PictureUploadWebdav import PictureUploadWebdav
from .PictureSSH import PictureSSH
from .PictureS3 import PictureS3

class Worker:

    def __init__(self, config, comm):

        self._comm = comm

        # Track the picture
        self._pic_tracker = PictureTracker(config.get('Storage', 'basedir'), config.get('Storage', 'prefix'))

        self.initPostprocessTasks(config)
        self.initPictureTasks(config)

    def initPostprocessTasks(self, config):

        self._postprocess_tasks = []

        # PictureSaver for assembled pictures
        self._postprocess_tasks.append(PictureSaver(self._pic_tracker.basedir))

        # PictureMailer for assembled pictures
        if config.getBool('Mailer', 'enable'):
            self._postprocess_tasks.append(PictureMailer(config))

        # PictureUploadWebdav to upload pictures to a webdav storage
        if config.getBool('UploadWebdav', 'enable'):
            self._postprocess_tasks.append(PictureUploadWebdav(config))

        # PictureSSH to upload pictures to an SSH server
        if config.getBool('SSH', 'enable'):
            self._postprocess_tasks.append(PictureSSH(config))

        # PictureS3 to upload pictures to a S3 bucket
        if config.getBool('S3', 'enable'):
            self._postprocess_tasks.append(PictureS3(config))

    def initPictureTasks(self, config):

        self._picture_tasks = []

        # PictureSaver for single shots
        self._picture_tasks.append(PictureSaver(self._pic_tracker.basedir))

    def run(self):

        for state in self._comm.iter(Workers.WORKER):
            self.handleState(state)

        return True

    def handleState(self, state):

        if isinstance(state, StateMachine.TeardownState):
            self.teardown(state)
        elif isinstance(state, StateMachine.GreeterState):
            self._pic_tracker.initializeNextPicture()
        elif isinstance(state, StateMachine.ReviewState):
            filepath = self._pic_tracker.getPicturePath()
            self.doPostprocessTasks(state.picture, filepath)
        elif isinstance(state, StateMachine.CameraEvent):
            if state.name == 'capture':
                filepath = self._pic_tracker.getNextShot()
                self.doPictureTasks(state.picture, filepath)
            else:
                raise ValueError('Unknown CameraEvent "{}"'.format(state))

    def teardown(self, state):

        pass

    def doPostprocessTasks(self, picture, filepath):

        for task in self._postprocess_tasks:
            if isinstance(task, PictureSSH) or isinstance(task, PictureS3):
                # For SSH and S3 task, send individual shots and assemble dpicture
                task.do([filepath] + self._pic_tracker.shots)
            else:
                task.do(picture, filepath)

    def doPictureTasks(self, picture, filepath):

        for task in self._picture_tasks:
            task.do(picture, filepath)
