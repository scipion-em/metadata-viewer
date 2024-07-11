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

from .renderers import (IntRenderer, FloatRenderer, ImageRenderer, BoolRenderer,
                        MatrixRender, StrRenderer)


class Column:
    """Class that represent a column"""
    def __init__(self, name, renderer=None):
        self._name = name
        self._alias = None
        self._renderer = renderer or StrRenderer()
        self._isSorteable = True
        self._isVisible = True
        self._index = -1

    def getIndex(self):
        return self._index

    def setIndex(self, index):
        self._index = index

    def getName(self):
        """Return the column name"""
        return self._name

    def setName(self, name):
        self._name = name

    def getAlias(self):
        """Return the column alias"""
        return self._alias

    def setAlias(self, alias):
        """Set the column alias"""
        self._alias = alias

    def getRenderer(self):
        """Return the column renderer"""
        return self._renderer

    def setRenderer(self, renderer):
        """Set the column renderer"""
        self._renderer = renderer

    def isSorteable(self):
        """Return if the column is sorteable"""
        return self._isSorteable

    def setIsSorteable(self, isSorteable):
        """Set the sorteable parameter"""
        self._isSorteable = isSorteable

    def isVisible(self):
        """Return if the column is visible"""
        return self._isVisible

    def setIsVisible(self, isVisible):
        """Set the visible parameter"""
        self._isVisible = isVisible

    def __str__(self):
        return 'Column: %s (renderer: %s)' % (self._name, self._renderer)

    def __cmp__(self, other):
        return (self.getName() == other.getName()
                and self.getRenderer() == other.getRenderer())

    def __eq__(self, other):
        return self.__cmp__(other)


class Row:
    """Class that represent a row"""
    def __init__(self, id, values):
        self._id = id
        self._values = values

    def getId(self):
        """Return the row id"""
        return self._id

    def getValues(self):
        """Return the row values"""
        return self._values


class TableAction:
    def __init__(self, name, callback):
       self._name = name
       self._callback = callback

    def getName(self):
        return self._name


class Selection:
    """Class to represent a dictionary with the selected rows in a table"""
    def __init__(self):
        self._selection = {}
        self._count = 0

    def getSelection(self):
        return self._selection

    def getCount(self):
        return self._count

    def isEmpty(self):
        return self._count == 0

    def addRowSelected(self, rowId, remove=True):
        if not self.isRowSelected(rowId):
            self._selection[rowId] = True
            self._count += 1
        elif remove:
            self._selection.pop(rowId)
            self._count -= 1

    def isRowSelected(self, rowId):
        return rowId in self._selection

    def clear(self):
        self._selection.clear()
        self._count = 0

    def clone(self):
        newSelection = Selection()
        newSelection._count = self._count
        newSelection._selection = dict(self._selection)
        return newSelection


class Table:
    """Class that represent a table"""
    def __init__(self, name, columns=None):
        self._name = name
        self._alias = None
        self._columns = columns or list()
        self._sortingColumn = None
        self._sortingAsc = True
        self._sortingChanged = False
        self._actions = []
        self._selection = Selection()
        self._hasColumnId = True

    def hasColumnId(self):
        """Return True if column Id is present in the table,
        False in other case"""
        return self._hasColumnId

    def setHasColumnId(self, hasColumnId):
        self._hasColumnId = hasColumnId

    def getSelection(self):
        """Return a dictionary with the selected rows ids"""
        return self._selection

    def setSelection(self, selection):
        self._selection = selection

    def getActions(self):
        return self._actions

    def addAction(self, name, callback):
        self._actions.append(TableAction(name, callback))

    def getName(self):
        """Return the table name"""
        return self._name

    def getAlias(self):
        """Return the table alias"""
        return self._alias if self._alias is not None else self._name

    def setAlias(self, alias):
        """Set the table alias"""
        self._alias = alias

    def hasSortingChanged(self):
        """Returns if the column that has been sorted has changed"""
        return self._sortingChanged

    def setSortingChanged(self, sortingChanged):
        """Set the sorted column has changed"""
        self._sortingChanged = sortingChanged

    def getColumns(self):
        """Return the table columns"""
        return self._columns

    def getSize(self):
        """Return the table size"""
        return len(self._columns)

    def configured(self):
        """ Returns tru if it has any column defined"""
        return self.getSize() != 0

    def getSortingColumn(self):
        """Return the column that has been ordered"""
        return self._sortingColumn

    def isSortingAsc(self):
        """Return if the column has been ordered ascending"""
        return self._sortingAsc

    def setSortingColumn(self, column):
        """Update the sorted column"""
        self._sortingColumn = column
        self._sortingChanged = True

    def setSortingAsc(self, ascending):
        """Update the sort order"""
        self._sortingAsc = ascending
        self._sortingChanged = True

    def addColumn(self, column):
        """Add a given column"""
        self._columns.append(column)

    def getColumnIndexFromLabel(self, label):
        for index, column in enumerate(self._columns):
            if column.getName() == label:
                return index
        return -1

    def createColumns(self, columns, values):
        """
        Create the page columns
        :param columns: list of the column names
        :param values: list with the first line of data in order to determinate
                       the data renderer
        """
        for i in range(len(columns)):
            column = Column(columns[i], self.guessRenderer(values[i]))
            self.addColumn(column)

    @classmethod
    def guessRenderer(cls, value):
        """ Guess the renderer based on a value. This may not be accurate. You can always specify the renderer in the DAO."""
        return _guessRenderer(value)

    def clear(self):
        """ Remove all columns """
        self._columns.clear()

    def __iter__(self):
        for column in self._columns:
            yield column


class Page:
    """Class that represent a Page"""
    def __init__(self, table: Table, pageNumber=1, pageSize=10):
        self._table = table
        self._rows = list()
        self._pageNumber = pageNumber
        self._pageSize = pageSize

    def getTable(self):
        """Return the page table"""
        return self._table

    def getRows(self):
        """Return the page rows"""
        return self._rows

    def addRow(self, row):
        """Add a given row"""
        self._rows.append(Row(row[0], row[1]))

    def getSize(self):
        """Return the number of rows that the page has"""
        return len(self._rows)

    def getPageSize(self):
        """Return the page size"""
        return self._pageSize

    def setPageSize(self, pageSize):
        """Set the page size"""
        self._pageSize = pageSize

    def getPageNumber(self):
        """Return the page number"""
        return self._pageNumber

    def setPageNumber(self, pageNumber):
        """Set the page number"""
        self._pageNumber = pageNumber

    def getFirstPageRow(self):
        """Get the first row of the page"""
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

def _guessRenderer(strValue):
    """Return a render for a given value. This render is assigned to a column"""
    if strValue is None:
        return StrRenderer()

    try:
        logger.debug("Trying to convert the value to an integer...")
        renderer = IntRenderer()
        renderer._render(strValue, None)
        return renderer
    except ValueError:
        try:
            logger.debug("Integer conversion failed...")
            logger.debug("Trying to convert the value to a float...")
            renderer = FloatRenderer()
            renderer._render(strValue, None)
            return FloatRenderer()
        except ValueError:
            try:
                logger.debug("Float conversion failed...")
                logger.debug("Trying to convert the value to an image...")
                renderer = ImageRenderer()
                renderer._render(strValue, None)
                return renderer
            except Exception:
                try:
                    logger.debug("Image conversion failed...")
                    logger.debug("Trying to convert the value to a Matrix...")
                    renderer = MatrixRender()
                    renderer._render(strValue, None)
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