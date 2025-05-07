"""
Copyright © 2008,2010,2011,2013 Jason R. Coombs
"""

import argparse
import functools
import io
import operator
import struct
from typing import Iterable, NamedTuple, Tuple, Union

import PIL.Image
from importlib_resources import files

import jaraco.clipboard


def calc_aspect(size: Iterable[int]) -> float:
    "aspect = size[0] / size[1] # width/height"
    return functools.reduce(operator.truediv, size)


class Dimensions(NamedTuple):
    width: int
    height: int


def replace_height(size: Dimensions, new_height: int) -> Dimensions:
    return Dimensions(size.width, new_height)


def replace_width(size: Dimensions, new_width: int) -> Dimensions:
    return Dimensions(new_width, size.height)


_PILImageParams = Union[int, Tuple[float, float, float, float], float, None]


def resize_with_aspect(
    image: PIL.Image.Image,
    max_size: Iterable[int],
    *args: _PILImageParams,
    **kargs: _PILImageParams,
) -> PIL.Image.Image:
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
    return image.resize(new_size, *args, **kargs)  # type: ignore[arg-type] # Assume the user passed correct parameters or let it fail


def load_apng() -> PIL.Image.Image:
    apng = files() / 'sample.png'
    return PIL.Image.open(io.BytesIO(apng.read_bytes()))


def get_image() -> PIL.Image.Image:
    """
    Stolen from lpaste. TODO: extract to jaraco.clipboard or similar.
    """
    result = jaraco.clipboard.paste_image()
    # construct a header (see http://en.wikipedia.org/wiki/BMP_file_format)
    offset = 54  # 14 byte BMP header + 40 byte DIB header
    header = b'BM' + struct.pack('<LLL', len(result), 0, offset)
    img_stream = io.BytesIO(header + result)
    return PIL.Image.open(img_stream)


def save_clipboard_image() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    filename = parser.parse_args().filename
    img = get_image()
    with open(filename, 'wb') as target:
        img.save(target, format='png')
