#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Provide installed photobooth version
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution('photobooth').version
except DistributionNotFound:
    __version__ = 'unknown'

import argparse
import gettext
import logging
import logging.handlers
import multiprocessing as mp

from . import camera, gui
from .Config import Config
from .gpio import Gpio
from .util import lookup_and_import
from .StateMachine import Context, ErrorEvent
from .Threading import Communicator, Workers
from .worker import Worker
from .lamp import LampWorker

# Globally install gettext for I18N
gettext.install('photobooth', 'photobooth/locale')


class CameraProcess(mp.Process):

    def __init__(self, argv, config, comm):

        super().__init__()
        self.daemon = True

        self._cfg = config
        self._comm = comm

    def run(self):

        logging.debug('CameraProcess: Initializing...')

        CameraModule = lookup_and_import(
            camera.modules, self._cfg.get('Camera', 'module'), 'camera')
        cap = camera.Camera(self._cfg, self._comm, CameraModule)

        while True:
            try:
                logging.debug('CameraProcess: Running...')
                if cap.run():
                    break
            except Exception as e:
                logging.exception('CameraProcess: Exception "{}"'.format(e))
                self._comm.send(Workers.MASTER, ErrorEvent('Camera', str(e)))

        logging.debug('CameraProcess: Exit')


class GuiProcess(mp.Process):

    def __init__(self, argv, config, comm):

        super().__init__()

        self._argv = argv
        self._cfg = config
        self._comm = comm

    def run(self):

        logging.debug('GuiProcess: Initializing...')
        Gui = lookup_and_import(gui.modules, self._cfg.get('Gui', 'module'),
                                'gui')
        logging.debug('GuiProcess: Running...')
        retval = Gui(self._argv, self._cfg, self._comm).run()
        logging.debug('GuiProcess: Exit')
        return retval


class WorkerProcess(mp.Process):

    def __init__(self, argv, config, comm):

        super().__init__()
        self.daemon = True

        self._cfg = config
        self._comm = comm

    def run(self):

        logging.debug('WorkerProcess: Initializing...')

        while True:
            try:
                logging.debug('WorkerProcess: Running...')
                if Worker(self._cfg, self._comm).run():
                    break
            except Exception as e:
                logging.exception('WorkerProcess: Exception "{}"'.format(e))
                self._comm.send(Workers.MASTER, ErrorEvent('Worker', str(e)))

        logging.debug('WorkerProcess: Exit')


class GpioProcess(mp.Process):

    def __init__(self, argv, config, comm):

        super().__init__()
        self.daemon = True

        self._cfg = config
        self._comm = comm

    def run(self):

        logging.debug('GpioProcess: Initializing...')

        while True:
            try:
                logging.debug('GpioProcess: Running...')
                if Gpio(self._cfg, self._comm).run():
                    break
            except Exception as e:
                logging.exception('GpioProcess: Exception "{}"'.format(e))
                self._comm.send(Workers.MASTER, ErrorEvent('Gpio', str(e)))

        logging.debug('GpioProcess: Exit')

class LampProcess(mp.Process):

    def __init__(self, argv, config, comm):

        super().__init__()
        self.daemon = True

        self._cfg = config
        self._comm = comm

    def run(self):

        logging.debug('LampProcess: Initializing...')

        while True:
            try:
                logging.debug('LampProcess: Running...')
                if LampWorker(self._cfg, self._comm).run():
                    break
            except Exception as e:
                logging.exception('LampProcess: Exception "{}"'.format(e))
                self._comm.send(Workers.MASTER, ErrorEvent('LampWorker', str(e)))
                return -1

        logging.debug('LampProcess: Exit')

def parseArgs(argv):

    # Add parameter for direct startup
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true',
                        help='omit welcome screen and run photobooth')
    parser.add_argument('--debug', action='store_true',
                        help='enable additional debug output')
    return parser.parse_known_args()


def mainloop(comm, context):

    while True:
        try:
            for event in comm.iter(Workers.MASTER):
                    exit_code = context.handleEvent(event)
                    if exit_code in (0, 123):
                        return exit_code
        except Exception as e:
            logging.exception('Main: Exception "{}"'.format(e))

def run(argv, is_run):

    logging.info('Photobooth version: %s', __version__)

    # Load configuration
    config = Config('photobooth.cfg')

    comm = Communicator()
    context = Context(comm, is_run)

    # Initialize processes: We use five/six processes here:
    # 1. Master that collects events and distributes state changes
    # 2. Camera handling
    # 3. GUI
    # 4. Postprocessing worker
    # 5. GPIO handler
    # 6. LampProcess (if enabled)
    proc_classes = (CameraProcess, WorkerProcess, GuiProcess, GpioProcess)
    if config.getBool('Relay', 'enable'):
        proc_classes += (LampProcess,)
    procs = [P(argv, config, comm) for P in proc_classes]

    for proc in procs:
        proc.start()

    # Enter main loop
    exit_code = mainloop(comm, context)

    # Wait for processes to finish
    for proc in procs:
        proc.join()

    logging.debug('All processes joined, returning code {}'. format(exit_code))

    return exit_code

def main(argv):

    # Parse command line arguments
    parsed_args, unparsed_args = parseArgs(argv)
    argv = argv[:1] + unparsed_args

    # Setup log level and format
    if parsed_args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create console handler and set format
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    # create file handler and set format
    fh = logging.handlers.TimedRotatingFileHandler('photobooth.log', when='d',
                                                   interval=1, backupCount=10)
    fh.setFormatter(formatter)

    # Apply config
    logging.basicConfig(level=log_level, handlers=(ch, fh))

    # Set of known status codes which trigger a restart of the application
    known_status_codes = {
        999: 'Initializing photobooth',
        123: 'Restarting photobooth and reloading config'
    }

    # Run the application until a status code not in above list is encountered
    status_code = 999

    while status_code in known_status_codes:
        logging.info(known_status_codes[status_code])

        status_code = run(argv, parsed_args.run)

    logging.info('Exiting photobooth with status code %d', status_code)

    return status_code
