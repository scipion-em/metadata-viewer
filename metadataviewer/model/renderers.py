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

import os.path
from functools import lru_cache

from PIL import Image
from abc import abstractmethod


class IRenderer:

    @abstractmethod
    def _render(self, value):
        pass

    def render(self, value):
        try:
            return self._render(value)
        except Exception as e:
            logger.error("It is not possible to assign a renderer to this "
                         "value. It will be rendered as a string: %s" % e)
            return str(value)


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

    def __init__(self, decimalNumber : int = 4):
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

    def _render(self, value, size=None):
        return value

    def renderType(self):
        return bool


class MatrixRender(IRenderer):

    def _render(self, value, size=None):
        return eval(value)

    def renderType(self):
        return list


class ImageRenderer(IRenderer):

    def __init__(self, size=100):
        self._size = size

    def getSize(self):
        return self._size

    def setSize(self, size):
        self._size = size

    def _render(self, value):
        return self._renderWithSize(value, self._size)

    @lru_cache
    def _renderWithSize(self, value, size):
        path = os.path.abspath(value)
        image = Image.open(path)
        image.thumbnail((size, size))
        return image

    def renderType(self):
        return Image
