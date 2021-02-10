"""
Copyright © 2008,2010,2011,2013 Jason R. Coombs
"""

import argparse
import io
import struct
import operator
import functools
from collections import namedtuple

import PIL.Image
import jaraco.clipboard
from importlib_resources import files


def calc_aspect(size):
    "aspect = size[0] / size[1] # width/height"
    return functools.reduce(operator.truediv, size)


Dimensions = namedtuple('Dimensions', 'width height')


def replace_height(size, new_height):
    return Dimensions(size.width, new_height)


def replace_width(size, new_width):
    return Dimensions(new_width, size.height)


def resize_with_aspect(image, max_size, *args, **kargs):
    """
    Resizes a PIL image to a maximum size specified while maintaining
    the aspect ratio of the image.

    >>> img = load_apng()
    >>> newimg = resize_with_aspect(img, Dimensions(10,15))
    >>> newdim = Dimensions(*newimg.size)
    >>> newdim.width <= 10 and newdim.height <= 15
    True
    """

    max_size = Dimensions(*max_size)
    aspect = calc_aspect(image.size)
    target_aspect = calc_aspect(max_size)

    if aspect >= target_aspect:
        # height is limiting factor
        new_height = int(round(max_size.width / aspect))
        new_size = replace_height(max_size, new_height)
    else:
        # width is the limiting factor
        new_width = int(round(max_size.height * aspect))
        new_size = replace_width(max_size, new_width)
    return image.resize(new_size, *args, **kargs)


def load_apng():
    apng = files('jaraco') / 'sample.png'
    return PIL.Image.open(io.BytesIO(apng.read_bytes()))


def get_image():
    """
    Stolen from lpaste. TODO: extract to jaraco.clipboard or similar.
    """
    result = jaraco.clipboard.paste_image()
    # construct a header (see http://en.wikipedia.org/wiki/BMP_file_format)
    offset = 54  # 14 byte BMP header + 40 byte DIB header
    header = b'BM' + struct.pack('<LLL', len(result), 0, offset)
    img_stream = io.BytesIO(header + result)
    return PIL.Image.open(img_stream)


def save_clipboard_image():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    filename = parser.parse_args().filename
    img = get_image()
    with open(filename, 'wb') as target:
        img.save(target, format='png')
