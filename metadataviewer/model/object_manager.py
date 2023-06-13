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
from metadataviewer.dao import StarFile
from metadataviewer.model import Table, Page


class ObjectManager:
    def __init__(self, fileName: str):
        self._fileName = fileName
        self._pageNumber = 1
        self._pageSize = 100
        self._registeredDAO = []
        self._selectDAO()

    def getRegisteredDAO(self):
        return self._registeredDAO

    def registerDAO(self, dao):
        self._registeredDAO.append(dao)

    def _selectDAO(self):
        if self._fileName.endswith('.star'):
            self.pageFromStarFile = StarFile(self._fileName)

    def getFileName(self):
        return self._fileName

    def createTable(self, tableName):
        self._tableName = tableName
        self.table = Table(self._tableName)
        self.pageFromStarFile.fillTable(self.table)

    def getPage(self, tableName, pageNumber, pageSize):
        if tableName != self._tableName:
            self._tableName = tableName
            self.createTable(tableName)
        self.page = Page(self.table, pageNumber=pageNumber, pageSize=pageSize)
        self.pageFromStarFile.fillPage(self.page)
        return self.page

    def getTableNames(self):
        return self.pageFromStarFile.getTableNames()

    def getTableRowCount(self, tableName):
        return self.pageFromStarFile.getTableRowCount(tableName)

    def getNextPage(self, pageNumber):
        self._pageNumber = pageNumber
        self.page.clear()
        return self.getPage(self._tableName, self._pageNumber, self._pageSize)

    def getRows(self, pageSize):
        self._pageSize = pageSize
        self.page.clear()
        return self.getPage(self._tableName, self._pageNumber, self._pageSize)

    def getTable(self, tableName):
        if tableName != self._tableName:
            self.page.getTable().clear()
            self.page.clear()
            return self.getPage(tableName, self._pageNumber, self._pageSize)
        return None







