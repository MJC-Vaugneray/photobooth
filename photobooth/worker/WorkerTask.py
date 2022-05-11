#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class WorkerTask:

    def __init__(self, **kwargs):

        assert not kwargs

    def do(self, picture):

        raise NotImplementedError()
