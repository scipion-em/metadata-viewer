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

from functools import lru_cache
import sqlite3
from .model import IDAO

EXTENDED_COLUMN_NAME = '_index@_filename'


class SqliteFile(IDAO):
    """  Class to manipulate Scipion Sqlite files. """
    def __init__(self, sqliteFile):
        self._names = []
        self._file = sqliteFile
        self._con = self.__loadDB(sqliteFile)
        self._con.row_factory = self._dictFactory
        self._tableCount = {}
        self._tables = {}
        self._labels = {}
        self._labelsTypes = {}
        self._aliases = {}
        self._columnsMap = {}
        self._extendedColumn = None

    def __loadDB(self, sqliteFile):
        try:
            return sqlite3.connect(f"file:{sqliteFile}?mode=ro", uri=True)
        except Exception as e:
            logger.error("The file could not be opened. Make sure the path is "
                         "correct: \n %s" % e)
            return None

    def hasExtendedColumn(self):
        return self._extendedColumn is not None

    def composeDataTables(self, tablesNames):
        tablesNames = sorted(tablesNames)
        for tableName in tablesNames:
            divTable = tableName.split('_')
            if len(divTable) > 1:
                if divTable[0].startswith('Class') and divTable[1].startswith('Class') and tableName not in self._tables:
                    objectTable = divTable[0] + '_Objects'
                    self._tables[objectTable] = tableName
                    self._names.append(objectTable)

    def composeTableAlias(self, tableName):
        firstRow = self.getTableRow(tableName, 0)
        className = firstRow['class_name']
        if tableName.__contains__('_'):
            alias = tableName.split('_')[0] + '_' + className
        else:
            alias = className
        return alias

    def getTableNames(self):
        """ Return all the table names found in the database. """
        if not self._names:
            self._tables = {'objects': 'classes'}
            self._names = ['objects']

            res = self._con.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablesNames = [row['name'] for row in res.fetchall()]
            self.composeDataTables(tablesNames)

            for tableName in self._names:
                # Getting the first row to identify the labels and theirs type
                firstRow = self.getTableRow(tableName, 0, classes=self._tables[tableName])
                self._labels[tableName] = list(firstRow.keys())
                alias = self.composeTableAlias(self._tables[tableName])
                self._aliases[tableName] = alias
                labelsTypes = []
                self._tableCount[tableName] = self.getTableRowCount(tableName)
                for key, value in firstRow.items():
                    labelsTypes.append(_guessType(value))
                self._labelsTypes[tableName] = labelsTypes

        return self._names

    def findColbyName(self, colNames, colName):
        for i, col in enumerate(colNames):
            if colName == col:
                return i
        return None

    def updateExtendColumn(self, table):
        tableName = table.getName()
        colNames = self._labels[tableName]
        indexCol = self.findColbyName(colNames, '_index')
        representativeCol = self.findColbyName(colNames, '_filename')

        if indexCol and representativeCol:
            logger.debug("The columns _index and _filename have been found. "
                         "We will proceed to create a new column with the "
                         "values of these columns.")
            self._extendedColumn = indexCol, representativeCol
        else:
            indexCol = self.findColbyName(colNames, '_representative._index')
            representativeCol = self.findColbyName(colNames,
                                                   '_representative._filename')
            if indexCol and representativeCol:
                logger.debug("The columns _representative._index and "
                             "_representative._filename have been found. "
                             "We will proceed to create a new column with the "
                             "values of these columns.")
                self._extendedColumn = indexCol, representativeCol

    def fillTable(self, table):
        tableName = table.getName()
        colNames = self._labels[tableName]
        self.updateExtendColumn(table)

        values = list(self.getTableRow(tableName, 0,
                                       classes=self._tables[tableName]).values())
        if self._extendedColumn:
            colNames.insert(self._extendedColumn[1] + 1, EXTENDED_COLUMN_NAME)
            values.insert(self._extendedColumn[1] + 1, str(values[self._extendedColumn[0]]) + '@' + values[self._extendedColumn[1]])
        table.createColumns(colNames, values)
        table.setAlias(self._aliases[tableName])

    def fillPage(self, page, actualColumn=0, orderAsc=True):
        """
        Read the given table from the sqlite and fill the page
        """
        tableName = page.getTable().getName()
        # moving to the first row of the page
        pageNumber = page.getPageNumber()
        pageSize = page.getPageSize()
        firstRow = pageNumber * pageSize - pageSize
        limit = pageSize

        column = self._labels[tableName][actualColumn]
        mode = 'ASC' if orderAsc else 'DESC'
        self.updateExtendColumn(page.getTable())

        for row in self.iterTable(tableName, start=firstRow, limit=limit,
                                  orderBy=column, mode=mode):
            if row:
                if 'id' in row.keys():
                    id = row['id']
                    values = list(row.values())
                    # Checking if exists an extended column
                    if self.hasExtendedColumn():
                        values.insert(self._extendedColumn[1] + 1,
                                      str(values[self._extendedColumn[0]]) + '@' + values[self._extendedColumn[1]])
                    page.addRow((int(id), values))

    @lru_cache
    def getTableRowCount(self, tableName):
        """ Return the number of elements in the given table. """
        logger.debug("Reading the table %s" %tableName)
        return self._con.execute(f"SELECT COUNT(*) FROM {tableName}").fetchone()['COUNT(*)']

    def iterTable(self, tableName, **kwargs):
        """
        Method to iterate over the table's rows
        :param tableName: the name of the table
        :param kwargs:
                limit: integer value to limit the number of elements
                start: start from a given element
                classes: read column names from a 'classes' table
                orderBy: clause to sort given a column name
                mode: sort direction ASC or DESC
        """
        query = f"SELECT * FROM {tableName}"

        if 'mode' in kwargs:
            if 'orderBy' in kwargs:
                if kwargs['orderBy']:
                    column = self._getColumnMap(tableName, kwargs['orderBy'])
                    if not column:
                        column = kwargs['orderBy']

                    query += f" ORDER BY {column}"

            if kwargs['mode']:
                query += f" {kwargs['mode']}"

        if 'start' in kwargs and 'limit' not in kwargs:
            kwargs['limit'] = -1

        if 'limit' in kwargs:
            query += f" LIMIT {kwargs['limit']}"

        if 'start' in kwargs:
            query += f" OFFSET {kwargs['start']}"

        if 'classes' not in kwargs:
            res = self._con.execute(query)
            while row := res.fetchone():
                yield row
        else:
            self._columnsMap[tableName] = {row['column_name']: row['label_property']
                          for row in self.iterTable(kwargs['classes'])}

            def _row_factory(cursor, row):
                fields = [column[0] for column in cursor.description]
                return {self._columnsMap[tableName].get(k, k): v for k, v in zip(fields, row)}

            # Modify row factory to modify column names
            self._con.row_factory = _row_factory
            res = self._con.execute(query)
            while row := res.fetchone():
                yield row
            # Restore row factory
            self._con.row_factory = self._dictFactory

    def getTableAliases(self):
        return self._aliases

    def _getColumnMap(self, tableName, column):
        for key, value in self._columnsMap[tableName].items():
            if value == column:
                return key
        return None

    def getTableRow(self, tableName, rowIndex, **kwargs):
        """ Get a given row by index. Extra args are passed to iterTable. """
        kwargs['start'] = rowIndex
        kwargs['limit'] = 1
        for row in self.iterTable(tableName, **kwargs):
            return row

    def close(self):
        if getattr(self, '_con', None):
            self._con.close()
            self._con = None

    def _dictFactory(self, cursor, row):
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row)}

    def getCompatibleFileTypes(self):
        logger.debug("Selected SqliteFile DAO")
        return ['sqlite']

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


# --------- Helper functions  ------------------------
def _guessType(strValue):
    if strValue is None:
        return str('None')
    try:
        int(strValue)
        return int
    except ValueError:
        try:
            float(strValue)
            return float
        except ValueError:
            return str

