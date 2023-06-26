# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *          Pablo Conesa Mingo         (pconesa@cnb.csic.es)
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

from .renderers import StrRenderer


class Column:
    def __init__(self, name, renderer=None):
        self._name = name
        self._alias = None
        self._renderer = renderer or StrRenderer

    def getName(self):
        return self._name

    def getAlias(self):
        return self._alias

    def setAlias(self, alias):
        self._alias = alias

    def getRenderer(self):
        return self._renderer

    def setRenderer(self, renderer):
        self._renderer = renderer

    def __str__(self):
        return 'Column: %s (renderer: %s)' % (self._name, self._renderer)

    def __cmp__(self, other):
        return (self.getName() == other.getName()
                and self.getRenderer() == other.getRenderer())

    def __eq__(self, other):
        return self.__cmp__(other)


class Row:
    def __init__(self, id, values):
        self._id = id
        self._values = values

    def getId(self):
        return self._id

    def getValues(self):
        return self._values


class Table:
    def __init__(self, name, columns=None):
        self._name = name
        self._alias = None
        self._columns = columns or list()
        self._sortingColumnIndex = -1
        self._sortingAsc = True
        self._sortingChanged = False

    def getName(self):
        return self._name

    def getAlias(self):
        return self._alias

    def setAlias(self, alias):
        self._alias = alias

    def hasSortingChanged(self):
        return self._sortingChanged

    def setSortingChanged(self, sortingChanged):
        self._sortingChanged = sortingChanged

    def getColumns(self):
        return self._columns

    def getSize(self):
        return len(self._columns)

    def getSortingColumnIndex(self):
        return self._sortingColumnIndex

    def isSortingAsc(self):
        return self._sortingAsc

    def setSortingColumnIndex(self, index):
        self._sortingColumnIndex = index
        self._sortingChanged = True

    def setSortingAsc(self, ascending):
        self._sortingAsc = ascending
        self._sortingChanged = True

    def addColumn(self, column):
        self._columns.append(column)

    def createColumns(self, columns, values):
        """
        Create the page columns
        :param columns: list of the column names
        :param values: list with the first line of data in order to determinate
                       the data renderer
        """
        for i in range(len(columns)):
            self.addColumn(Column(columns[i], _guessRender(values[i])))

    def clear(self):
        """ Remove all columns """
        self._columns.clear()

    def __iter__(self):
        for column in self._columns:
            yield column


class Page:
    def __init__(self, table: Table, pageNumber=1, pageSize=10):
        self._table = table
        self._rows = list()
        self._pageNumber = pageNumber
        self._pageSize = pageSize

    def getTable(self):
        return self._table

    def getRows(self):
        return self._rows

    def addRow(self, row):
        self._rows.append(Row(row[0], row[1]))

    def getSize(self):
        return len(self._rows)

    def getPageSize(self):
        """Return the page size"""
        return self._pageSize

    def setPageSize(self, pageSize):
        self._pageSize = pageSize

    def getPageNumber(self):
        return self._pageNumber

    def setPageNumber(self, pageNumber):
        self._pageNumber = pageNumber

    def getFirstPageRow(self):
        return self._pageSize * self._pageNumber

    def clear(self):
        """ Remove all the rows from the page, but keep its columns. """
        self._rows.clear()

    def __iter__(self):
        """
        Method to iterate over the rows of a given page.
        """
        for row in self._rows:
            yield row


# --------- Helper functions  ------------------------

def _guessRender(strValue):
    from .renderers import (IntRenderer, FloatRenderer, ImageRenderer, MatrixRender,
        StrRenderer)

    if strValue is None:
        return StrRenderer()

    try:
        logger.debug("Trying to convert the value to an integer...")
        renderer = IntRenderer()
        renderer._render(strValue)
        return renderer
    except ValueError:
        try:
            logger.debug("Integer conversion failed...")
            logger.debug("Trying to convert the value to a float...")
            renderer = FloatRenderer()
            renderer._render(strValue)
            return FloatRenderer()
        except ValueError:
            try:
                logger.debug("Float conversion failed...")
                logger.debug("Trying to convert the value to an image...")
                renderer = ImageRenderer()
                renderer._render(strValue)
                return renderer
            except Exception:
                logger.debug("Image conversion failed...")
                logger.debug("Trying to convert the value to a string...")
                return StrRenderer()


def _guessType(strValue):
    try:
        int(strValue)
        return int
    except ValueError:
        try:
            float(strValue)
            return float
        except ValueError:
            return str


def _guessTypesFromLine(line):
    return [_guessType(v) for v in line.split()]


def _formatValue(v):
    return '%0.6f' % v if isinstance(v, float) else str(v)


def _getFormatStr(v):
    return '.6f' if isinstance(v, float) else ''