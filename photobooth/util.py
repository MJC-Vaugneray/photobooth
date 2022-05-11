#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib

from PIL import Image


def lookup_and_import(module_list, name, package=None):

    result = next(((mod_name, class_name)
                   for config_name, mod_name, class_name in module_list
                   if name == config_name), None)

    if package is None:
        import_module = importlib.import_module('photobooth.' + result[0])
    else:
        import_module = importlib.import_module(
            'photobooth.' + package + '.' + result[0])

    if result[1] is None:
        return import_module
    else:
        return getattr(import_module, result[1])


def pickle_image(image):

    if image is None:
        return None
    else:
        image_data = (image.mode, image.size, image.tobytes())
        return image_data


def unpickle_image(image_data):

    if image_data is None:
        return None
    else:
        image = Image.frombytes(*image_data)
        return image
