#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hid
import atexit

"""

Inspired by https://github.com/jaketeater/Very-Simple-USB-Relay

This relay object uses the HID library instead of usb. 

Some scant details about the USB Relay
http://vusb.wikidot.com/project:driver-less-usb-relays-hid-interface

cython-hidapi module:
https://github.com/trezor/cython-hidapi

Installing the module:
sudo apt-get install python-dev libusb-1.0-0-dev libudev-dev
pip install --upgrade setuptools
pip install hidapi

A list of avaible methods for the hid object:
https://github.com/trezor/cython-hidapi/blob/6057d41b5a2552a70ff7117a9d19fc21bf863867/chid.pxd#L9

"""

from time import sleep

import logging
from .. import StateMachine
from ..Threading import Workers
from ..StateMachine import ErrorEvent

class Relay(object):
    """Relay class"""

    def __init__(self, idVendor=0x16c0, idProduct=0x05df):
        self.h = hid.device()
        try:
            self.h.open(idVendor, idProduct)
        except OSError as err:
            raise err

        self.h.set_nonblocking(1)
        atexit.register(self.cleanup)

    def cleanup(self):
        self.h.close()

    def get_switch_statuses_from_report(self, report):
        """

        The report returned is a 8 int list, ex:
        
        [76, 72, 67, 88, 73, 0, 0, 2]

        The ints are passed as chars, and this page can help interpret:
        https://www.branah.com/ascii-converter

        The first 5 in the list are a unique ID, in case there is more than one switch.

        The last three seem to be reserved for the status of the relays. The status should
        be interpreted in binary and in reverse order.  For example:

        2 = 00000010

        This means that switch 1 is off and switch 2 is on, and all others are off.

        """

        # Grab the 8th number, which is a integer
        switch_statuses = report[7]

        # Convert the integer to a binary, and the binary to a list.
        switch_statuses = [int(x) for x in list('{0:08b}'.format(switch_statuses))]

        # Reverse the list, since the status reads from right to left
        switch_statuses.reverse()

        # The switch_statuses now looks something like this:
        # [1, 1, 0, 0, 0, 0, 0, 0]
        # Switch 1 and 2 (index 0 and 1 respectively) are on, the rest are off.

        return switch_statuses

    def send_feature_report(self, message):
        self.h.send_feature_report(message)

    def get_feature_report(self):
        # If 0 is passed as the feature, then 0 is prepended to the report. However,
        # if 1 is passed, the number is not added and only 8 chars are returned.
        feature = 1
        # This is the length of the report. 
        length = 8
        return self.h.get_feature_report(feature, length)

    def set_state(self, relay = 0, on = False):
        """
        Set the state for a relay.
        
        If a relay is specified, then the relay status will be set.
        Either (or is 0 is specified), it will the state of both relays.

        on=True will turn the relay(s) on, on=False will turn them off.
        """
        if relay == 0:
            if on:
                self.send_feature_report([0xFF, 1])
                self.send_feature_report([0xFF, 2])
            else:
                self.send_feature_report([0xFD, 1])
                self.send_feature_report([0xFD, 2])
        else:
            # An integer can be passed instead of the a byte, but it's better to
            # use ints when possible since the docs use them, but it's not neccessary.
            # https://github.com/jaketeater/simpleusbrelay/blob/master/simpleusbrelay/__init__.py
            if on:
                self.send_feature_report([0xFF, relay])
            else:
                self.send_feature_report([0xFD, relay])

    def get_state(self, relay = 0):
        """
        Get the state for a relay. 

        If a relay is specified, then return its status. If no relay (or 0) specified, a list of all the statuses is returned.
        True = on, False = off.
        """
        if relay == 0:
            report = self.get_feature_report()
            switch_statuses = self.get_switch_statuses_from_report(report)
            status = []
            for s in switch_statuses:
                status.append(bool(s))
        else:
            report = self.get_feature_report()
            switch_statuses = self.get_switch_statuses_from_report(report)
            status = bool(switch_statuses[relay-1])

        return status

class LampWorker:

    def __init__(self, config, comm):

        super().__init__()

        self._comm = comm
        try:
            self._relay = Relay(idVendor=int(config.get('Relay', 'vendor_id'), 16), idProduct=int(config.get('Relay', 'product_id'), 16))
        except Exception as err:
            # Do not fail on error
            logging.exception('Lamp relay: Exception "{}"'.format(err))
            logging.error('unable to start the lamp relay')

        self._lampId = config.getInt('Relay', 'lamp_relay_id')

    def run(self):

        for state in self._comm.iter(Workers.LAMP):
            self.handleState(state)

        return True

    def handleState(self, state):

        if isinstance(state, StateMachine.StartupState):
            self._lampBlink(2)
        elif isinstance(state, StateMachine.CountdownState):
            self._turnOn()
        elif isinstance(state, StateMachine.AssembleState):
            self._turnOff()
        elif isinstance(state, StateMachine.TeardownState):
            self.teardown()

    def _lampBlink(self, count = 1, interval = 500):
        """
        Turn on and off lamp "count" times, with a defined ms interval.
        """
        for i in range(0, count):
            self._turnOn()
            sleep(interval/1000)
            self._turnOff()
            sleep(interval/1000)

    def _turnOn(self):
        """
        Turn on the lamp
        """
        try:
            self._relay.set_state(self._lampId, on=True)
        except Exception as err:
            logging.exception('Lamp relay: Exception "{}"'.format(err))

    def _turnOff(self):
        """
        Turn on the lamp
        """
        try:
            self._relay.set_state(self._lampId, on=False)
        except Exception as err:
            logging.exception('Lamp relay: Exception "{}"'.format(err))


    def teardown(self):
        self._turnOff()
        self._relay.cleanup()
