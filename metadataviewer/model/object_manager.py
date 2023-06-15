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

from metadataviewer.dao import StarFile
from metadataviewer.model import Table, Page


class ObjectManager:
    def __init__(self, fileName: str):
        self._fileName = fileName
        self._tables = {}
        self._pageNumber = 1
        self._pageSize = 100
        self._registeredDAO = []
        self.__registerterOwnDAOs()

    def __registerterOwnDAOs(self):
        self.registerDAO(StarFile)

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

    def getFileName(self):
        return self._fileName

    def createTable(self, tableName: str):
        self._tableName = tableName
        table = Table(tableName)
        self._dao.fillTable(table)
        return table

    # @lru_cache
    def getPage(self, tableName: str, pageNumber: int, pageSize: int):
        if tableName not in self._tables:
            table = self.createTable(tableName)
            self._tables[tableName] = table
        else:
            table = self._tables[tableName]
        self.page = Page(table, pageNumber=pageNumber, pageSize=pageSize)
        self._dao.fillPage(self.page)
        return self.page

    def getTableNames(self):
        return self._dao.getTableNames()

    def getTableRowCount(self, tableName: str):
        return self._dao.getTableRowCount(tableName)

    def getNextPage(self, pageNumber: int):
        self._pageNumber = pageNumber
        return self.getPage(self._tableName, self._pageNumber, self._pageSize)

    def getRows(self, pageNumber: int, pageSize: int):
        self._pageNumber = pageNumber
        self._pageSize = pageSize
        return self.getPage(self._tableName, self._pageNumber, self._pageSize).getRows()

    def getTable(self, tableName: str):
        if tableName != self._tableName:
            self.page.getTable().clear()
            self.page.clear()
            return self.getPage(tableName, self._pageNumber, self._pageSize)
        return None

    def sort(self, tableName, column, reverse=True):
        self._dao.sort(tableName, column, reverse)







