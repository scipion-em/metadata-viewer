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
    Class to read STAR files.
    """
    def __init__(self, inputFile):
        self._file = self.__loadFile(inputFile)
        # While parsing the file, store the offsets for data_ blocks
        # for quick access when need to load data rows
        self._offsets = {}
        self._tableCount = {}
        self._tableData = {}
        self._names = []  # flag to check if we searched all tables

    def __loadFile(self, inputFile):
        return open(inputFile, 'r')

    def fillTable(self, table):
        self._loadStarFileInfo(table)

    def fillPage(self, page):
        """
        Read the given table from the start file and parse columns definition
        and data rows.
        args:
            tableName: the name of the table to read
            kwargs:
                page: number of the page to read
                getRows: number of rows the page will have
        """
        table = page.getTable()
        for row in self._iterRowLines(table.seek, page.getPageNumber(),
                                      page.getPageSize()):
            if row:
                page.addRow(row.split())

    def getTableRowCount(self, tableName):
        return self._tableCount[tableName]

    def getTableNames(self):
        """ Return all the names of the data_ blocks found in the file. """
        if not self._names:  # scan for ALL table names
            f = self._file
            f.seek(0)  # move file pointer to the beginning
            offset = 0
            line = f.readline()
            while line:
                # While searching for a data line, we will store the offsets
                # for any data_ line that we find
                if line.startswith('data_'):
                    tn = line.strip().replace('data_', '')
                    self._offsets[tn] = offset
                    self._names.append(tn)
                    data = self._getData()
                    self._tableCount[tn] = data[0]
                    self._tableData[tn] = data[1]

                offset = f.tell()
                line = f.readline()

        return list(self._names)

    def _getData(self):
        self._findLabelLine()
        data = []
        line = self._findValuesLine()
        count = 0
        f = self._file
        while line and not line.startswith('\n'):
            data.append(line)
            count += 1
            line = f.readline()
        return count, data

    def _findValuesLine(self):
        line = self._line
        while line.startswith('\n'):
            line = self._file.readline()
        while line.startswith('_'):
            line = self._file.readline()
        while line.startswith('\n'):
            line = self._file.readline()
        return line

    def _loadStarFileInfo(self, table):
        self._findDataLine(table.getName())
        # Find first column line and parse all columns
        self._findLabelLine()
        colNames = []
        values = []

        while self._line.startswith('_'):

            parts = self._line.split()
            colNames.append(parts[0][1:])
            if not self._foundLoop:
                values.append(parts[1])
            table.seek = self._file.tell()
            self._line = self._file.readline().strip()

        if self._foundLoop:
            values = self._line.split() if self._line else []
        table.createColumns(colNames, values)

    def _findDataLine(self, dataName):
        """ Raise an exception if the desired data string is not found.
        Move the line pointer after the desired line if found.
        """
        f = self._file

        # Check if we know the offset for this data line
        dataStr = 'data_' + dataName
        if dataStr in self._offsets:
            f.seek(self._offsets[dataStr])
            f.readline()
            return

        full_scan = False
        initial_offset = offset = f.tell()
        line = f.readline()
        # Iterate all lines once if necessary, going back to
        # the beginning of the file once
        while not full_scan:
            while line:
                # While searching for a data line, we will store the offsets
                # for any data_ line that we find
                if line.startswith('data_'):
                    ds = line.strip()
                    self._offsets[ds] = offset
                    if ds == dataStr:
                        return
                offset = f.tell()
                if offset == initial_offset:
                    full_scan = True
                    break
                line = f.readline()
            # Start from the beginning and scan until complete the full loop
            f.seek(0)
            offset = 0
            line = f.readline()

        raise Exception("'%s' block was not found" % dataStr)

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

    def _iterRowLines(self, seek, pageNumber, pageSize):
        self._lineCount = 0
        self._file.seek(seek)

        # moving to the first row of the page
        firstRow = pageNumber * pageSize - pageSize
        for i in range(firstRow):
            self._line = self._file.readline().strip()

        while self._line and self._lineCount < pageSize:
            self._lineCount += 1
            self._line = self._file.readline().strip()
            yield self._line

    def close(self):
        if getattr(self, '_file', None):
            self._file.close()
            self._file = None

    def getCompatibleFileTypes(self):
        return ['star', 'xmd']
