#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import cups
import qrcode
from urllib.parse import urlparse, urlunparse
import os
import posixpath
import barcode
from barcode.writer import ImageWriter

from PIL import Image, ImageQt

class QRCode:

    def __init__(self, cfg):
        # Open CUPS connection
        self._cups = cups.Connection()

        # Read config
        self._base_url = cfg.get('QRCode', 'url_prefix')
        self._printer_name = cfg.get('QRCode', 'printer_name')
        self._header_file = cfg.get('QRCode', 'qrcode_header')
        self._header_width = cfg.getInt('QRCode', 'qrcode_header_width')
        self._header_height = cfg.getInt('QRCode', 'qrcode_header_height')
        self._barcode_enable = cfg.getBool('QRCode', 'barcode_enable')

        # Prepare temporary variables
        if os.access('/dev/shm', os.W_OK):
            self._tmp_result_file = '/dev/shm/print.jpg'
            self._tmp_barcode_file = '/dev/shm/barcode.jpg'
        else:
            self._tmp_result_file = '/tmp/print.jpg'
            self._tmp_barcode_file = '/tmp/barcode.jpg'
        self._qrcode_img = None

        # Load header image
        if self._header_file is None or self._header_file == "":
            self._header_img = None
        else:
            self._header_img = Image.open(self._header_file).convert('RGB')
            self._header_img = self._header_img.resize((self._header_width, self._header_height))

        # Check for printer
        if self._printer_name not in self._cups.getPrinters().keys():
            raise Exception('Unable to get the printer ' + self._printer_name)

    def do(self, picture, picture_tracker):
        # Generate the URL
        parsed_base_url = urlparse(self._base_url)
        generated_url = urlunparse(parsed_base_url._replace(path=posixpath.join(parsed_base_url.path,picture_tracker.picture_time)))

        # Generate QRCode and Barcode
        self._generate_qrcode(generated_url)
        self._generate_barcode(picture_tracker.picture_time)

        # Generate result file
        self._generate_full_image()

        # Print
        try:
            self.print(self._tmp_result_file)
        except Exception as err:
            logging.error("Unable to print QRCode", err)

    def print(self, filepath):
        self._cups.printFile(self._printer_name, filepath, "photobooth", {})

    def _generate_qrcode(self, text):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        self._qrcode_img = qr.make_image(fill_color="black", back_color="white").get_image()

    def _generate_barcode(self, text):
        EAN = barcode.get_barcode_class('ean13')
        writer = ImageWriter()
        writer.set_options({"quiet_zone": 0})
        # dirty disabling of text
        writer._callbacks['paint_text'] = None
        ean = EAN(text, writer=writer)
        f = open(self._tmp_barcode_file, 'wb')
        ean.write(f, {"paint_text": None})

    def _generate_full_image(self):
        # Generate images list
        imgs = []
        if self._header_file is not None:
             imgs.append(self._header_img)
        imgs.append(self._qrcode_img)
        imgs.append(Image.open(self._tmp_barcode_file).convert('RGB'))

        widths, heights = zip(*(i.size for i in imgs))
        total_width = max(widths)
        max_height = sum(heights)
        concatenateImage = Image.new('RGB', (total_width, max_height), (255,255,255))
        y_offset = 0
        for im in imgs:
            concatenateImage.paste(im, (int((total_width - im.size[0]) / 2), y_offset))
            y_offset += im.size[1]
        concatenateImage.save(self._tmp_result_file)
