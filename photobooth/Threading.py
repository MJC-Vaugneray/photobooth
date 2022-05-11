#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import IntEnum
from multiprocessing import Queue


class Communicator:

    def __init__(self):

        super().__init__()

        self._queues = [Queue() for _ in Workers]

    def bcast(self, message):

        for q in self._queues[1:]:
            q.put(message)

    def send(self, target, message):

        if not isinstance(target, Workers):
            raise TypeError('target must be a member of Workers')

        self._queues[target].put(message)

    def recv(self, worker, block=True):

        if not isinstance(worker, Workers):
            raise TypeError('worker must be a member of Workers')

        return self._queues[worker].get(block)

    def iter(self, worker):

        if not isinstance(worker, Workers):
            raise TypeError('worker must be a member of Workers')

        return iter(self._queues[worker].get, None)

    def empty(self, worker):

        if not isinstance(worker, Workers):
            raise TypeError('worker must be a member of Workers')

        return self._queues[worker].empty()


class Workers(IntEnum):

    MASTER = 0
    GUI = 1
    CAMERA = 2
    GPIO = 3
    WORKER = 4
    LAMP = 5
