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
import sys

logger = logging.getLogger()

import os
import csv
from functools import lru_cache
from abc import abstractmethod

# from metadataviewer.dao import StarFile, SqliteFile
from metadataviewer.model import Table, Page


class IGUI:

    def __init__(self, fileName=None, objectManager=None):
        self._fileName = fileName
        self.objectManager = objectManager

    @abstractmethod
    def writeMessage(self, msg):
        """Write a non modal message like a status bar message"""
        pass

    @abstractmethod
    def getSaveFileName(self):
        """Get a path to save a fileName"""
        pass

    @abstractmethod
    def getSubsetName(self, typeOfObjects, elementsCount):
        """Get a name for the subset created by a action"""
        pass

    @abstractmethod
    def show(self):
        pass


class ObjectManager:
    """Class that represent the object manager. This class maintains
    communication with the GUIs and the DAOs. """
    def __init__(self):
        self._fileName = None
        self._tables = {}
        self._pageNumber = 1
        self._pageSize = 50
        self._registeredDAO = []
        self._registeredRenderers = []
        self.__registerterOwnDAOs()
        self._dao = None
        self._gui: IGUI = None

    def open(self, fileName):
        self._fileName = fileName
        self.selectDAO()
        if not self._gui:
            from metadataviewer.gui.qt.qtviewer import QTMetadataViewer
            from PyQt5.QtWidgets import QApplication
            app = QApplication(sys.argv)
            self._gui = QTMetadataViewer(fileName=self._fileName,
                                         objectManager=self)
            self._gui.show()
            app.exec_()

    def getGui(self):
        return self._gui

    def setGui(self, gui: IGUI):
        self._gui = gui

    def __registerterOwnDAOs(self):
        """Register the own DAOs"""
        # self.registerDAO(StarFile)
        # self.registerDAO(SqliteFile)
        pass

    def getRegisteredDAO(self):
        """return the registered DAOs"""
        return self._registeredDAO

    def registerDAO(self, dao):
        """Register a given DAO"""
        self._registeredDAO.append(dao)

    def selectDAO(self):
        """Select a DAO taking into account a file extension"""
        for dao in self._registeredDAO:
            instance = dao(self._fileName)
            ext = os.path.basename(self._fileName).split('.')[-1]
            if ext in instance.getCompatibleFileTypes():
                 self._dao = instance
                 break

        if self._dao is None:
            logger.error("There is no DAO registered to handle this type of file.")

        return self._dao

    def getDAO(self):
        """Return the selected DAO"""
        return self._dao

    def getFileName(self):
        """Return the filename"""
        return self._fileName

    def getPageSize(self):
        """Return the page size"""
        return self._pageSize

    def getPageNumber(self):
        """Return the page number"""
        return self._pageNumber

    def createTable(self, tableName: str):
        """Create a table"""
        self._tableName = tableName
        table = Table(tableName)
        self._dao.fillTable(table, self)
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
        """Return the number of the page on which the row is located"""
        pageSize = self.getPageSize()
        pageNumber = int((row + 1) / pageSize)
        if (row + 1) % pageSize > 0:
            pageNumber += 1

        return pageNumber

    def getCurrentRow(self, table, currentRow):
        """This method return a row given a position in the table"""
        # Calculating the page to which that row belongs
        if currentRow < 0:
            currentRow = 0
        pageNumber = self.getNumberPageFromRow(currentRow)
        page = self.getPage(table.getName(), pageNumber, self._pageSize,
                            table.getSortingColumnIndex(),
                            table.isSortingAsc())
        rowPosition = currentRow % self.getPageSize()
        if rowPosition == page.getSize():
            logger.info("The final row of the table has been reached.")
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

    def getSelectedRangeRowsIds(self, tableName, startRow, numberOfRows, column, reverse=True):
        """Return a range of rows starting at 'startRow' an amount of 'numberOfRows' """
        table = self.getTable(tableName)
        self._gui.writeMessage('Retrieving identifiers...')
        selectedRange = self._dao.getSelectedRangeRowsIds(tableName, startRow,
                                                          numberOfRows, column,
                                                          reverse)
        self._gui.writeMessage('Storing selection...')
        for i, id in enumerate(selectedRange):
            table.getSelection().addRowSelected(id, remove=False)

    def getTableNames(self):
        """Return the tables names"""
        return self._dao.getTableNames()

    def getTableAliases(self):
        """Return the tables aliases"""
        return self._dao.getTableAliases()

    def getTableRowCount(self, tableName: str):
        return self._dao.getTableRowCount(tableName)

    def getTable(self, tableName: str):
        """Returns a table if it is stored, otherwise a new table is
           created. """
        if tableName not in self._tables:
            table = self.createTable(tableName)
            self._tables[tableName] = table
        else:
            table = self._tables[tableName]

        return table

    def sort(self, tableName, column, reverse=True):
        """Store the table sort preferences"""
        table = self.getTable(tableName)
        table.setSortingColumnIndex(column)
        table.setSortingAsc(reverse)

    def getTableWithAdditionalInfo(self):
        return self._dao.getTableWithAdditionalInfo()

    def exportToCSV(self, tableName):
        """Export the table selection to a .csv file"""
        table = self.getTable(tableName)
        selection = table.getSelection().getSelection()
        columns = table.getColumns()
        filepath = self._gui.getSaveFileName()
        if filepath:
            with open(filepath, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                header_data = [col.getName() for col in columns]
                csv_writer.writerow(header_data)

                for row, rowId in enumerate(selection):
                    rowValues = self.getCurrentRow(table,  rowId - 1).getValues()
                    if rowValues is not None:
                        csv_writer.writerow(rowValues)







