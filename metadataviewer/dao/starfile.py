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

from .model import IDAO


class StarFile(IDAO):
    """
    Class to handle STAR files.
    """
    def __init__(self, inputFile):
        self._file = self.__loadFile(inputFile)
        self._tableCount = {}
        self._tableData = {}
        self._labels = {}
        self._names = []

    def __loadFile(self, inputFile):
        return open(inputFile, 'r')

    def fillTable(self, table):
        self._loadStarFileInfo(table)

    def fillPage(self, page):
        """
        Read the given table from the start file and parse columns definition
        and data rows.
        """
        tableName = page.getTable().getName()
        for row in self._iterRowLines(tableName, page.getPageNumber(),
                                      page.getPageSize()):
            if row:
                page.addRow(row)

    def getTableRowCount(self, tableName):
        return self._tableCount[tableName]

    def getTableNames(self):
        """ Return all the names of the data_ blocks found in the file and
            fill all labels and data of every table name """
        if not self._names:  # scan for ALL table names
            f = self._file
            line = f.readline()
            while line:
                # While searching for a data line, we will store the offsets
                # for any data_ line that we find
                if line.startswith('data_'):
                    tn = line.strip().replace('data_', '')
                    self._names.append(tn)
                    data = self._getData()
                    self._tableCount[tn] = data[0]
                    self._labels[tn] = data[1]
                    self._tableData[tn] = data[2]
                line = f.readline()

        return list(self._names)

    def _getData(self):
        """ Method to get all information of the table"""
        self._findLabelLine()
        data = {}
        line, labels = self._getLabels()
        count = 0
        f = self._file
        while line and not line.startswith('\n'):
            data[count] = line
            count += 1
            line = f.readline().strip()
        return count, labels, data

    def _getLabels(self):
        line = self._line
        labels = []
        while line.startswith('\n'):
            line = self._file.readline()
        while line.startswith('_'):
            parts = line.split()
            labels.append(parts[0][1:])
            line = self._file.readline()
        while line.startswith('\n'):
            line = self._file.readline()
        return line, labels

    def _loadStarFileInfo(self, table):
        colNames = self._labels[table.getName()]
        values = self._tableData[table.getName()][0].split()
        table.createColumns(colNames, values)

    def _findLabelLine(self):
        line = ''
        foundLoop = False

        rawLine = self._file.readline()
        while rawLine:
            if rawLine.startswith('_'):
                line = rawLine
                break
            elif rawLine.startswith('loop_'):
                foundLoop = True
            rawLine = self._file.readline()

        self._line = line.strip()
        self._foundLoop = foundLoop

    def _iterRowLines(self, tableName, pageNumber, pageSize):
        # moving to the first row of the page
        firstRow = pageNumber * pageSize - pageSize
        endRow = pageNumber * pageSize + 30  # getting 30 rows more
        if self._tableCount[tableName] == 1:
            yield 1, self._tableData[tableName][0].strip().split()
            return
        if firstRow + pageSize + 30 > self._tableCount[tableName]:
            endRow = self._tableCount[tableName]
        for i in range(firstRow, endRow):
            values = self._tableData[tableName][i].strip()
            yield i+1, values.split()

    def close(self):
        if getattr(self, '_file', None):
            self._file.close()
            self._file = None

    def getCompatibleFileTypes(self):
        return ['star', 'xmd']
