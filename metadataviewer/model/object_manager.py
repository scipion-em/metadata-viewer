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
import os
from functools import lru_cache

from metadataviewer.dao import StarFile, SqliteFile
from metadataviewer.model import Table, Page


class ObjectManager:
    def __init__(self, fileName: str):
        self._fileName = fileName
        self._tables = {}
        self._pageNumber = 1
        self._pageSize = 50
        self._registeredDAO = []
        self._registeredRenderers = []
        self.__registerterOwnDAOs()
        self._dao = None

    def __registerterOwnDAOs(self):
        self.registerDAO(StarFile)
        self.registerDAO(SqliteFile)

    def getRegisteredDAO(self):
        return self._registeredDAO

    def registerDAO(self, dao):
        self._registeredDAO.append(dao)

    def selectDAO(self):
        for dao in self._registeredDAO:
            # instance = getattr(sys.modules[__name__], dao)(self._fileName)
            instance = dao(self._fileName)
            ext = os.path.basename(self._fileName).split('.')[1]
            if ext in instance.getCompatibleFileTypes():
                 self._dao = instance
                 break

        return self._dao

    def getDAO(self):
        return self._dao

    def getFileName(self):
        return self._fileName

    def getPageSize(self):
        return self._pageSize

    def getPageNumber(self):
        return self._pageNumber

    def createTable(self, tableName: str):
        self._tableName = tableName
        table = Table(tableName)
        self._dao.fillTable(table)
        return table

    @lru_cache
    def getPage(self, tableName: str, pageNumber: int, pageSize: int,
                actualColumn = 0,  orderAsc = True):
        """
        Method to retrieve a specific page from the tableName
        :param tableName: name of the table(block) in the file
        :param pageNumber: page number
        :param pageSize: page size
        :param actualColumn: this parameter is used by the cache
        :param orderAsc: this parameter is used by the cache
        """
        table = self.getTable(tableName)
        self.page = Page(table, pageNumber=pageNumber, pageSize=pageSize)
        self._dao.fillPage(self.page, actualColumn, orderAsc)
        table.setSortingChanged(False)
        return self.page

    def getNumberPageFromRow(self, row):
        """Get the number of the page on wich  the row is located"""
        pageSize = self.getPageSize()
        pageNumber = int((row + 1) / pageSize)
        if (row + 1) % pageSize > 0:
            pageNumber += 1

        return pageNumber

    def getCurrentRow(self, table, currentRow):
        """This method return a row given a position in the table"""
        # Calculating the page to which that row belongs
        pageNumber = self.getNumberPageFromRow(currentRow)
        page = self.getPage(table.getName(), pageNumber, self._pageSize,
                            table.getSortingColumnIndex(),
                            table.isSortingAsc())
        rowPosition = currentRow % self.getPageSize()
        if rowPosition == page.getSize():
            return None
        row = page.getRows()[rowPosition]
        return row

    def getRows(self, tableName, firstRow, visibleRows):
        """Return a range of rows"""
        rows = []
        table = self.getTable(tableName)
        for i in range(visibleRows):
            row = self.getCurrentRow(table, firstRow)
            if row:
                rows.append(row)
                firstRow += 1
            else:
                break
        return rows

    def getTableNames(self):
        return self._dao.getTableNames()

    def getTableRowCount(self, tableName: str):
        return self._dao.getTableRowCount(tableName)

    def getNextPage(self, pageNumber: int):
        self._pageNumber = pageNumber
        return self.getPage(self._tableName, self._pageNumber, self._pageSize)

    def getTable(self, tableName: str):
        if tableName not in self._tables:
            table = self.createTable(tableName)
            self._tables[tableName] = table
        else:
            table = self._tables[tableName]

        return table

    def sort(self, tableName, column, reverse=True):
        table = self.getTable(tableName)
        table.setSortingColumnIndex(column)
        table.setSortingAsc(reverse)








