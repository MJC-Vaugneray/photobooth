#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .. import StateMachine
from ..Threading import Workers

from .PictureTracker import PictureTracker
from .PictureMailer import PictureMailer
from .PictureSaver import PictureSaver
from .PictureUploadWebdav import PictureUploadWebdav
from .PictureSSH import PictureSSH
from .PictureS3 import PictureS3
from .QRCode import QRCode

import time

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

        # QRCode to print a qrcode link
        if config.getBool('QRCode', 'enable'):
            self._postprocess_tasks.append(QRCode(config))

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
            self.doPostprocessTasks(state.picture)
            # Wait until all files are saved
            while not self._pic_tracker.checkAllFilesExists():
                time.sleep(0.5)
            self._comm.send(Workers.MASTER, StateMachine.WorkerEvent('idle'))
        elif isinstance(state, StateMachine.CameraEvent):
            if state.name == 'capture':
                filepath = self._pic_tracker.getNextShot()
                self.doPictureTasks(state.picture, filepath)
            else:
                raise ValueError('Unknown CameraEvent "{}"'.format(state))

    def teardown(self, state):

        pass

    def doPostprocessTasks(self, picture):

        for task in self._postprocess_tasks:
            if isinstance(task, PictureSSH) or isinstance(task, PictureS3):
                # For SSH and S3 task, send individual shots and assembled picture
                task.do([self._pic_tracker.getPicturePath()] + self._pic_tracker.shots)
            elif isinstance(task, QRCode):
                task.do(picture, self._pic_tracker)
            else:
                task.do(picture, self._pic_tracker.getPicturePath())

    def doPictureTasks(self, picture, filepath):

        for task in self._picture_tasks:
            task.do(picture, filepath)
