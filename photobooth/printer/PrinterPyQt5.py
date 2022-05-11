#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from PyQt5 import QtCore, QtGui
from PyQt5.QtPrintSupport import QPrinter

from . import Printer


class PrinterPyQt5(Printer):

    def __init__(self, page_size, print_pdf=False):

        super().__init__(page_size)

        self._printer = QPrinter(QPrinter.HighResolution)
        self._printer.setFullPage(True)
        self._printer.setPageSize(QtGui.QPageSize(QtCore.QSizeF(*page_size),
                                                  QtGui.QPageSize.Millimeter))
        self._printer.setColorMode(QPrinter.Color)

        logging.info('Using printer "%s"', self._printer.printerName())

        self._print_pdf = print_pdf
        if self._print_pdf:
            logging.info('Using PDF printer')
            self._counter = 0
            self._printer.setOutputFormat(QPrinter.PdfFormat)

    def print(self, picture):

        if self._print_pdf:
            self._printer.setOutputFileName('print_%d.pdf' % self._counter)
            self._counter += 1

        logging.info('Printing picture')
        logging.debug('Page Size: {}, Print Size: {}, PictureSize: {} '.format(
            self._printer.paperRect(), self._printer.pageRect(),
            picture.rect()))

        painter = QtGui.QPainter(self._printer)
        painter.drawImage(self._printer.pageRect(), picture, picture.rect())
        painter.end()
