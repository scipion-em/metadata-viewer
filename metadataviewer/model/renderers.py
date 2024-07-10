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
logger = logging.getLogger()

import numpy as np
import os.path
from functools import lru_cache

from PIL import Image
from abc import abstractmethod

from .constants import IMAGE_DEFAULT_SIZE


class Action:
    def __init__(self, text, icon, tooltip, callback):
        self._text = text
        self._icon = icon
        self._tooltip = tooltip
        self._callback = callback

    def open(self, path):
        self._callback(path)


class IRenderer:

    def __init__(self):
        self._extraActions = []

    def addAction(self, action: Action):
        self._extraActions.append(action)

    def getActions(self):
        return self._extraActions

    @abstractmethod
    def _render(self, value, row):
        pass

    def render(self, value, row):
        try:
            return self._render(value, row)
        except Exception as e:
            logger.info("It is not possible to assign a renderer to this "
                        "value. It will be rendered as a string: %s" % e)
            return str(value)

    @abstractmethod
    def renderType(self):
        pass


class StrRenderer(IRenderer):

    def _render(self, value, row):
        return str(value)

    def renderType(self):
        return str


class IntRenderer(IRenderer):

    def _render(self, value, row):
        return int(value)

    def renderType(self):
        return int


class FloatRenderer(IRenderer):

    def __init__(self, decimalNumber: int = 2):
        super().__init__()
        self._decimalNumber = decimalNumber

    def _render(self, value, row):
        return round(float(value), self._decimalNumber)

    def setDecimalNumber(self, decimalNumber):
        self._decimalNumber = decimalNumber

    def getDecimalsNumber(self):
        return self._decimalNumber

    def renderType(self):
        return float


class BoolRenderer(IRenderer):

    def _render(self, value, row):
        return bool(value)

    def renderType(self):
        return bool


class MatrixRender(IRenderer):

    def __init__(self, decimalNumber: int = 2):
        super().__init__()
        self._decimalNumber = decimalNumber

    def _render(self, value, row):
        # replace nan values by 0
        if isinstance(value, str):
            value = value.replace('nan', '0')
            value = np.array(eval(value))
        if value.shape == ():  # Case where eval works for value but is not a matrix or an array
            raise Exception("This value can be converted into a numpy array but it does not constitute a matrix or an array.")
        np.set_printoptions(precision=self._decimalNumber, suppress=True)
        return np.around(value, decimals=self._decimalNumber)

    def setDecimalNumber(self, decimalNumber):
        self._decimalNumber = decimalNumber

    def getDecimalsNumber(self):
        return self._decimalNumber

    def renderType(self):
        return np.ndarray


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
        return ['jpg', 'png', 'psd', 'xmp']


class ImageRenderer(IRenderer):
    _imageReaders = []

    def __init__(self, size=IMAGE_DEFAULT_SIZE, rotColumnIndex=None):
        super().__init__()
        self._size = size
        self._rotColumnIndex = rotColumnIndex  # index in the row values where rotation can be found
        self._applyTransformation = False

    def getSize(self):
        return self._size

    def setRotationColumnIndex(self, rotColumnIndex):
        self._rotColumnIndex = rotColumnIndex

    def setApplyTransformation(self, applyTransformation):
        self._applyTransformation = applyTransformation

    def hasTransformation(self):
        return self._rotColumnIndex is not None

    @classmethod
    def registerImageReader(cls, imageReader):
        cls._imageReaders.append(imageReader)

    @classmethod
    def getImageReader(cls, path):
        ext = os.path.basename(path).split('.')[-1]
        for imageReader in cls._imageReaders:
            if ext in imageReader.getCompatibleFileTypes():
                return imageReader
        # return None

    def setSize(self, size):
        self._size = size

    def _render(self, value, row):
        rotationAngle = 0
        if row and self._rotColumnIndex and self._applyTransformation:
            rotationAngle = row[self._rotColumnIndex]
        return self._renderWithSize(value, self._size, rotationAngle)

    @lru_cache
    def _renderWithSize(self, value, size, rotationAngle):
        imageReader = self.getImageReader(value)
        image = imageReader.open(value)
        sizeX, sizeY = image.size
        imageR = image.resize((size, int(size*sizeY/sizeX)))
        imageR.thumbnail((size, size))
        imageR = imageR.rotate(rotationAngle, fillcolor='gray')
        return imageR

    def renderType(self):
        return Image


ImageRenderer.registerImageReader(PILImageReader)
