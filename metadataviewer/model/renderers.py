# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import logging

import numpy as np

from .constants import IMAGE_DEFAULT_SIZE

logger = logging.getLogger()

import os.path
from functools import lru_cache

from PIL import Image
import mrcfile
from abc import abstractmethod


class IRenderer:

    @abstractmethod
    def _render(self, value):
        pass

    def render(self, value):
        try:
            return self._render(value)
        except Exception as e:
            logger.info("It is not possible to assign a renderer to this "
                         "value. It will be rendered as a string: %s" % e)
            return str(value)

    @abstractmethod
    def renderType(self):
        pass


class StrRenderer(IRenderer):

    def _render(self, value):
        return str(value)

    def renderType(self):
        return str


class IntRenderer(IRenderer):

    def _render(self, value):
        return int(value)

    def renderType(self):
        return int


class FloatRenderer(IRenderer):

    def __init__(self, decimalNumber: int = 2):
        self._decimalNumber = decimalNumber

    def _render(self, value):
        return round(float(value), self._decimalNumber)

    def setDecimalNumber(self, decimalNumber):
        self._decimalNumber = decimalNumber

    def getDecimalsNumber(self):
        return self._decimalNumber

    def renderType(self):
        return float


class BoolRenderer(IRenderer):

    def _render(self, value):
        return bool(value)

    def renderType(self):
        return bool


class MatrixRender(IRenderer):

    def _render(self, value):
        return eval(value)

    def renderType(self):
        return list


class ImageReader:
    @abstractmethod
    def open(self, path):
        pass

    @abstractmethod
    def getCompatibleFileTypes(self) -> list:
        pass


class PILImageReader(ImageReader):
    @classmethod
    def open(cls, path):
        path = os.path.abspath(path)
        image = Image.open(path)
        return image

    @classmethod
    def getCompatibleFileTypes(cls) -> list:
        return ['jpg', 'png']


class MRCImageReader(ImageReader):
    @classmethod
    def open(cls, path):
        filePath = path.split('@')
        if len(filePath) > 1:
            index = int(filePath[0])
            fileName = filePath[-1]
            mrc_img = mrcfile.open(fileName, permissive=True)
            if mrc_img.is_volume():
                imfloat = mrc_img.data[0, :, :]
            else:
                imfloat = mrc_img.data

            iMax = imfloat.max()
            iMin = imfloat.min()
            im255 = ((imfloat - iMin) / (iMax - iMin) * 255).astype(np.uint8)
            img = Image.fromarray(im255[index-1])

            return img
        return None

    @classmethod
    def getCompatibleFileTypes(cls) -> list:
        return ['mrc', 'mrcs', 'em', 'rec', 'ali']


class STKImageReader(ImageReader):
    IMG_BYTES = None
    stk_handler = None
    header_info = None
    HEADER_OFFSET = 1024
    FLOAT32_BYTES = 4
    TYPE = None

    @classmethod
    def open(cls, path):
        stk = path.split('@')
        if len(stk) > 1:
            image = cls.read(stk[-1], int(stk[0]))
            return image

    @classmethod
    def read(cls, filename, id):
        """
        Reads a given image
           :param filename (str) --> Image to be read
        """
        cls.stk_handler = open(filename, "rb")
        cls.header_info = cls.readHeader()
        cls.IMG_BYTES = cls.FLOAT32_BYTES * cls.header_info["n_columns"] ** 2
        image = cls.readImage(id - 1)
        iMax = image.max()
        iMin = image.min()
        image = ((image - iMin) / (iMax - iMin) * 255).astype('uint8')
        image = Image.fromarray(image)
        return image

    @classmethod
    def readHeader(cls):
        """
        Reads the header of the current file as a dictionary
            :returns The current header as a dictionary
        """
        header = cls.readNumpy(0, cls.HEADER_OFFSET)

        header = dict(img_size=int(header[1]), n_images=int(header[25]),
                      offset=int(header[21]),
                      n_rows=int(header[1]), n_columns=int(header[11]),
                      n_slices=int(header[0]),
                      sr=float(header[20]))

        cls.TYPE = "stack" if header["n_images"] > 1 else "volume"

        return header

    @classmethod
    def readNumpy(cls, start, end):
        """
        Read bytes between start and end as a Numpy array
            :param start (int) --> Start byte
            :param end (int) --> End byte
            :returns decoded bytes as Numpy array
        """
        return np.frombuffer(cls.readBinary(start, end), dtype=np.float32)

    @classmethod
    def readBinary(cls, start, end):
        """
        Read bytes between start and end
            :param start (int) --> Start byte
            :param end (int) --> End byte
            :returns the bytes read
        """
        cls.seek(start)
        return cls.stk_handler.read(end)

    @classmethod
    def readImage(cls, iid):
        """
        Reads a given image in the stack according to its ID
            :param iid (int) --> Image id to be read
            :returns Image as Numpy array
        """

        if cls.TYPE == "stack":
            start = 2 * cls.header_info["offset"] + iid * (
                    cls.IMG_BYTES + cls.header_info["offset"])
        else:
            start = cls.header_info["offset"] + iid * cls.IMG_BYTES

        img_size = cls.header_info["n_columns"]
        return cls.readNumpy(start, cls.IMG_BYTES).reshape([img_size, img_size])

    @classmethod
    def seek(cls, pos):
        """
        Move file pointer to a given position
            :param pos (int) --> Byte to move the pointer to
        """
        cls.stk_handler.seek(pos)

    @classmethod
    def getCompatibleFileTypes(cls) -> list:
        return ['stk', 'vol']


class ImageRenderer(IRenderer):
    _imageReaders = []

    def __init__(self, size=IMAGE_DEFAULT_SIZE):
        self._size = size

    def getSize(self):
        return self._size

    @classmethod
    def _registerImageReader(cls, imageReader):
        cls._imageReaders.append(imageReader)

    @classmethod
    def getImageReader(cls, path):
        ext = os.path.basename(path).split('.')[-1]
        for imageReader in cls._imageReaders:
            if ext in imageReader.getCompatibleFileTypes():
                return imageReader

    def setSize(self, size):
        self._size = size

    def _render(self, value):
        return self._renderWithSize(value, self._size)

    @lru_cache
    def _renderWithSize(self, value, size):
        imageReader = self.getImageReader(value)
        image = imageReader.open(value)
        imageR = image.resize((size, size))
        imageR.thumbnail((size, size))
        return imageR

    def renderType(self):
        return Image

ImageRenderer._registerImageReader(PILImageReader)
ImageRenderer._registerImageReader(MRCImageReader)
ImageRenderer._registerImageReader(STKImageReader)
