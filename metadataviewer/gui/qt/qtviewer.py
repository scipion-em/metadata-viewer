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

import numpy
import numpy as np

logger = logging.getLogger()

import os.path
import sys

from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QItemSelectionModel, QCoreApplication
from PyQt5.QtGui import (QIcon, QKeySequence, QPixmap, QPalette, QColor,
                         QFontMetrics)
from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QLabel,
                             QAction, QDialog, QVBoxLayout, QWidget, QScrollBar,
                             QDialogButtonBox, QTableWidget, QCheckBox,
                             QHBoxLayout, QTableWidgetItem, QComboBox,
                             QStatusBar, QAbstractItemView, QSpinBox,
                             QPushButton, QApplication,
                             QTableWidgetSelectionRange, QFrame, QDesktopWidget,
                             QFileDialog, QLineEdit, QGridLayout)

from metadataviewer.model.object_manager import IGUI
from .constants import *
from metadataviewer.gui import getImage


class ColumnPropertiesTable(QDialog):
    """ Class to handler the columns properties(visible, render, edit) """
    def __init__(self, parent, table):
        super().__init__()
        self.parent = parent
        self._table = table
        self.title = 'Columns'
        self.left = parent.x()
        self.top = parent.y()
        self.width = 600
        self.height = 240
        self.numCol = 4
        self.columns = None
        self.initUI()

    def initUI(self):
        self._loadFirstTime = True
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.createTable()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        # Creating buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)
        self.setLayout(self.layout)

    def createTable(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(self.numCol)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem(LABEL))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem(VISIBLE))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem(RENDER))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem(EDIT))
        self.tableWidget.move(0, 0)

    def setLoadFirstTime(self, loadFirstTime):
        self._loadFirstTime = loadFirstTime

    def InsertRows(self):
        """Method to insert the labels and the values to the visible, render
        and edit columns"""
        tableHeaderList = []
        for column in range(self._table.columnCount()):
            headerItem = self._table.horizontalHeaderItem(column)
            if not headerItem.checkState():
                tableHeaderList.append(headerItem.text())
            else:
                tableHeaderList.append('')

        for i in range(self.numRow):
            # checking visible column
            column = self.columns[i]
            if not column.getName() in tableHeaderList:
               self.visibleCheckBoxList[column.getIndex()].setChecked(False)

            # checking render column
            isImageColumn = column.getRenderer().renderType() == Image
            if self._loadFirstTime and isImageColumn:
                self.renderCheckBoxList[column.getIndex()].setChecked(True)
            elif not isImageColumn:
                self.renderCheckBoxList[column.getIndex()].setEnabled(False)

            visibleCheckbox = self._createCellWidget(self.visibleCheckBoxList[column.getIndex()])
            renderCheckbox = self._createCellWidget(self.renderCheckBoxList[column.getIndex()])
            editCheckbox = self._createCellWidget(self.editCheckBoxList[column.getIndex()])

            self.tableWidget.setCellWidget(column.getIndex(), 0, QLabel('_' + column.getName()))
            self.tableWidget.setCellWidget(column.getIndex(), 1, visibleCheckbox)
            self.tableWidget.setCellWidget(column.getIndex(), 2, renderCheckbox)
            self.tableWidget.setCellWidget(column.getIndex(), 3, editCheckbox)
        self.tableWidget.move(0, 0)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def _createCellWidget(self, widget):
        """Creating a widget in order to insert in a table cell"""
        cellWidget = QWidget()
        layoutCB = QHBoxLayout(cellWidget)
        layoutCB.addWidget(widget)
        layoutCB.setAlignment(Qt.AlignCenter)
        layoutCB.setContentsMargins(0, 0, 0, 0)
        cellWidget.setLayout(layoutCB)
        return cellWidget

    def registerColumns(self, columns):
        """Register the table columns"""
        self.columns = columns
        self.numRow = len(columns)
        self.tableWidget.setRowCount(self.numRow)
        self.visibleCheckBoxList = []
        self.renderCheckBoxList = []
        self.editCheckBoxList = []

        for i in range(self.numRow):
            self.visibleCheckBoxList.append(i)
            self.renderCheckBoxList.append(i)
            self.editCheckBoxList.append(i)

        for i in range(self.numRow):
            visibleCheckBox = QCheckBox()
            visibleCheckBox.setChecked(columns[i].isVisible())
            renderCheckBox = QCheckBox()
            editCheckBox = QCheckBox()
            editCheckBox.setEnabled(False)

            self.visibleCheckBoxList[columns[i].getIndex()] = visibleCheckBox
            self.renderCheckBoxList[columns[i].getIndex()] = renderCheckBox
            self.editCheckBoxList[columns[i].getIndex()] = editCheckBox
        self.InsertRows()

    def openTableDialog(self):
        """Open the columns properties dialog"""
        self.InsertRows()
        self.show()

    def hideColumns(self):
        """Method to hide a table columns """
        for column in range(self._table.columnCount()):
            if not self.visibleCheckBoxList[column].isChecked():
                self._table.horizontalHeaderItem(column).setCheckState(True)
            else:
                self._table.horizontalHeaderItem(column).setCheckState(False)

        for column, checkBox in enumerate(self.visibleCheckBoxList):
            display = not checkBox.isChecked()
            self._table.setColumnHidden(column, display)

    def hideColumn(self, column):
        """Hide a given column in the table"""
        self.visibleCheckBoxList[column].setChecked(False)
        self._table.setColumnHidden(column, True)

    def uncheckVisibleColumns(self, start):
        """Hide the table columns beginning from a given column index"""
        columnsCount = len(self.columns)
        if columnsCount > start:
            for i in range(start, columnsCount):
                isImageColumn = self.columns[i].getRenderer().renderType() == Image
                if not isImageColumn:
                    self.visibleCheckBoxList[i].setChecked(False)

    def editColums(self):
        pass

    def renderColums(self):
        """Method to render(or not) the selected columns"""
        self._table.setRowHeight(0, DEFAULT_ROW_HEIGHT)
        self._table._setRowHeight(DEFAULT_ROW_HEIGHT)
        self._table._fillTable()

    def accept(self):
        """Accept the changes in the column properties dialog"""
        self.hideColumns()
        self.renderColums()
        self.editColums()
        self.setLoadFirstTime(False)
        self.close()


class CustomScrollBar(QScrollBar):
    """Class to custom the scrollbar widget"""
    def __init__(self):
        super().__init__()
        self.setSingleStep(1)
        self.dragging = False
        self.start_value = 0
        self.start_pos = None

    def wheelEvent(self, event):
        """Handle the mouse wheel event"""
        step = 1
        delta = event.angleDelta().y() / 120  # Number of mouse wheel steps
        # If moved up, decreases the value of scroll
        if delta > 0:
            self.setValue(self.value() - step)
        # If it moves down, it increases the scroll value.
        elif delta < 0:
            self.setValue(self.value() + step)

        event.accept()


class CustomWidget(QWidget):
    """Class to  custom the table cell widget"""
    def __init__(self, data, id, imagePath='', addText=False, text=''):
        super().__init__()
        self._data = data
        self._id = id
        self._imagePath = imagePath
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel()
        self._adicinalText = QLabel(text)
        self._type = str

        if isinstance(data, bool):  # The data is a boolean
            self._label = QCheckBox()
            self._label.setChecked(data)
            self._label.setEnabled(False)
            self._layout.addWidget(self._label, alignment=Qt.AlignCenter)
            self._type = bool

        elif isinstance(data, int) or isinstance(data, float) or isinstance(data, str):  # The data is a int, float or str
            if not isinstance(data, str):
                self._type = int if isinstance(data, int) else float
            self._label.setText(str(data))
            self._layout.addWidget(self._label, alignment=Qt.AlignRight)

        elif isinstance(data, numpy.ndarray):  # The data is a Matrix
            self._type = numpy.ndarray
            tableArray = QTableWidget()
            numRows, numCols = data.shape
            tableArray.setRowCount(numRows)
            tableArray.setColumnCount(numCols)
            tableArray.horizontalHeader().hide()
            tableArray.verticalHeader().hide()
            tableArray.setEditTriggers(QTableWidget.NoEditTriggers)
            tableArray.setShowGrid(False)
            tableArray.setStyleSheet("QTableWidget { border: none; } "
                                     "QTableWidget::item { border: none; }")
            tableArray.setSelectionMode(QAbstractItemView.NoSelection)

            tableArray.setMaximumHeight(100)
            for i in range(numRows):
                for j in range(numCols):
                    item = QTableWidgetItem(str(data[i, j]))
                    tableArray.setItem(i, j, item)
                    tableArray.item(i, j).setTextAlignment(Qt.AlignRight)
            tableArray.resizeColumnsToContents()
            tableArray.resizeRowsToContents()
            self._layout.addWidget(tableArray, alignment=Qt.AlignCenter | Qt.AlignCenter)

        else:  # Assuming the data is a file path to an image
            try:
                im = data.convert("RGBA")
                data = im.tobytes("raw", "RGBA")
                qimage = QtGui.QImage(data, im.size[0], im.size[1],
                                      QtGui.QImage.Format_RGBA8888)

                pixmap = QPixmap.fromImage(qimage)
                self._label.setPixmap(pixmap)
                self._layout.addWidget(self._label, alignment=Qt.AlignCenter)
                self._type = Image

                if addText:
                    self._layout.addWidget(self._adicinalText, alignment=Qt.AlignCenter)
            except Exception as e:
                logger.error("Error loading the image:", e)

        self.setLayout(self._layout)

    def widgetType(self):
        """Return the type of the widget content"""
        return self._type

    def getWidgetContent(self):
        """Return the widget content"""
        return self._label

    def getData(self):
        """Return the content data"""
        return self._data

    def getImagePath(self):
        """Return the image path"""
        return self._imagePath

    def getId(self):
        """Return the widget id"""
        return self._id


class TableView(QTableWidget):
    """Class to represent the metadata in table mode"""
    def __init__(self, objectManager):
        super().__init__()
        self.propertiesTableDialog = ColumnPropertiesTable(self, self)
        self._pageNumber = 1  # First page
        self._pageSize = ZOOM_SIZE
        self._currentRow = 0
        self._currentColumn = 0
        self._lastSelectedColumn = None
        self._lastSelectedRow = 0
        self._orderAsc = True
        self._sortedColumn = 0
        self.objectManager = objectManager
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self._oldzoom = ZOOM_SIZE

    def _createTable(self, tableName):
        """Create the table structure"""
        self.setColumnCount(0)
        self._tableName = tableName
        self._rowsCount = self.objectManager.getTableRowCount(self._tableName)
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.verticalHeader().setVisible(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vScrollBar = CustomScrollBar()
        self.hScrollBar = QScrollBar()
        self._createHeader()
        self._table = self.objectManager.getTable(self._tableName)
        self.columns = self._table.getColumns()
        self._columnWithImages = self.getColumnWithImages()
        self.tableWithAdditionalInfo = self.objectManager.getTableWithAdditionalInfo()
        self._rowHeight = DEFAULT_ROW_HEIGHT  # Default row height
        self.propertiesTableDialog.registerColumns(self.columns)
        self.propertiesTableDialog.setLoadFirstTime(True)
        self.propertiesTableDialog.InsertRows()
        self.propertiesTableDialog.hideColumns()
        self.setVerticalScrollBar(self.vScrollBar)
        self.setHorizontalScrollBar(self.hScrollBar)
        self.vScrollBar.valueChanged.connect(lambda: self._loadRows())
        self.hScrollBar.valueChanged.connect(lambda: self._loadRows())
        self.cellClicked.connect(self.setCurrentRowColumn)
        self.horizontalHeader().sectionClicked.connect(self.setCurrentColumn)
        self.verticalHeader().sectionClicked.connect(self.setCurrentRow)
        # self.setCurrentCell(0, 0)

    def getTable(self):
        """Return the current table"""
        return self._table

    def getSortedColumn(self):
        return self._sortedColumn

    def getOldZoom(self):
        """Return the old table zoom value"""
        return self._oldzoom

    def setOldZoom(self, value):
        """Set the old table zoom value"""
        self._oldzoom = value

    def getRowHeight(self):
        """Return the row height"""
        return self._rowHeight

    def _setRowHeight(self, rowHeight):
        """Set the rowHeight"""
        self._rowHeight = rowHeight

    def setTableName(self, tableName):
        """Set the table name"""
        self._tableName = tableName

    def getTableName(self):
        """Return the table name"""
        return self._tableName

    def getColumns(self):
        """Return the table columns"""
        return self.columns

    def getColumnWithImages(self):
        """Return the index of the column that represent an image"""
        for i, col in enumerate(self.columns):
            if col.getRenderer().renderType() == Image:
                return i
        return None

    def orderByColumn(self, column, order):
        """Ordering a given column in a order mode(ASC, DESC)"""
        self._orderAsc = order
        self._sortedColumn = column
        if self._lastSelectedColumn is not None:
            self.horizontalHeaderItem(self._lastSelectedColumn).setIcon(QIcon(None))

        self._lastSelectedColumn = self._currentColumn
        self._currentColumn = column

        self.horizontalHeader().setSortIndicator(column, Qt.AscendingOrder if self._orderAsc else Qt.DescendingOrder)
        self.objectManager.sort(self._tableName, column, self._orderAsc)
        self.clearContents()
        self.vScrollBar.setValue(0)
        self._loadRows()

        icon = QIcon(getImage(DOWN_ARROW)) if self._orderAsc else QIcon(getImage(UP_ARROW))
        self.horizontalHeaderItem(column).setIcon(icon)

    def _createHeader(self):
        """Create the table header"""
        table = self.objectManager.getTable(self._tableName)
        self._columns = table.getColumns()
        self.setColumnCount(len(self._columns))
        for i, column in enumerate(self._columns):
            item = QTableWidgetItem(str(column.getName()))
            item.setTextAlignment(Qt.AlignCenter)
            self.setHorizontalHeaderItem(self._columns[i].getIndex(), item)

    def _fillTable(self):
        """Fill the table"""
        columns = self.objectManager.getTable(self._tableName).getColumns()
        self._rowsCount = self.objectManager.getTableRowCount(self._tableName)
        self.setColumnCount(len(columns))
        self.setRowCount(self._rowsCount)
        self._loadRows()

    def _calculateVisibleColumns(self):
        """Method tha calculate how many columns are visible"""
        viewportWidth = self.parent().width() if self.parent() else self.viewport().width()
        visibleCols = 0

        for col in range(self.columnCount()):
            columnaX = self.columnViewportPosition(col)
            widthColumna = self.columnWidth(col)
            if columnaX < viewportWidth and columnaX + widthColumna > 0:
                visibleCols += 1
        return visibleCols + 1

    def _calculateVisibleRows(self):
        """Method that calculate how many rows are visible"""
        viewportHeight = self.parent().height() if self.parent() else self.viewport().height()
        rowHeight = self._rowHeight if self._rowHeight else DEFAULT_ROW_HEIGHT  # row height (minumum size in case of the table is empty)
        visibleRows = viewportHeight // rowHeight + 1
        return visibleRows

    def _addRows(self, rows, currentRowIndex, currenctColumnIndex):
        """Add rows to the table"""
        columnsCount = self._calculateVisibleColumns()
        endColumn = currenctColumnIndex + columnsCount
        if endColumn > len(self._columns):
            endColumn = len(self._columns)

        for i in range(len(rows)):
            row = rows[i]
            values = row.getValues()
            if row.getId() in self._table.getSelection().getSelection():
                self.setRangeSelected(QTableWidgetSelectionRange(i + currentRowIndex,
                                                                 0, i + currentRowIndex,
                                                                 self.columnCount() - 1), True)
            for col in range(len(values)):
                column = self._columns[col]
                if self.propertiesTableDialog.visibleCheckBoxList[column.getIndex()]:
                    renderer = column.getRenderer()
                    if renderer.renderType() != Image:
                        item = renderer.render(values[col])
                        widget = CustomWidget(item, row.getId())
                    else:
                        if self.propertiesTableDialog.renderCheckBoxList[column.getIndex()].isChecked():
                            item = renderer.render(values[col])
                            if self.tableWithAdditionalInfo and self._tableName == self.tableWithAdditionalInfo[0]:
                                text = self.composeAdditionaInfo(row)
                                widget = CustomWidget(item, row.getId(), addText=True, text=text)
                            else:
                                widget = CustomWidget(item, row.getId())
                        else:
                            item = values[col]
                            widget = CustomWidget(item, row.getId())

                    if widget.sizeHint().height() > self._rowHeight:
                        self._rowHeight = widget.sizeHint().height()

                    width = self.calculateColumnWidth(widget, column.getIndex())

                    self.setCellWidget(i + currentRowIndex, column.getIndex(), widget)
                    self.setColumnWidth(column.getIndex(), width + 5)
            self.setRowHeight(i + currentRowIndex, self._rowHeight + 5)

    def calculateColumnWidth(self, widget, index):
        """Method to calculate the column width taking into account
        the header """
        width = widget.sizeHint().width()
        headerText = self.horizontalHeader().model().headerData(index,
                                                                Qt.Horizontal)
        font = self.horizontalHeader().font()
        fontMetrics = QFontMetrics(font)
        textWidth = fontMetrics.horizontalAdvance(headerText)

        if textWidth > width:
            width = textWidth
        return width + 5

    def composeAdditionaInfo(self, rowValues):
        """Create an additional description to a specific object"""
        text = ''
        columns = self.tableWithAdditionalInfo[1]
        values = rowValues.getValues()
        for i, column in enumerate(self.columns):
            if column.getName() in columns:
                text += column.getName() + '=' + str(values[i]) + ' '
        return text

    def _loadRows(self):
        """Load the table rows"""
        currentRowIndex = self.vScrollBar.value() - 1
        currenctColumnIndex = self.hScrollBar.value()
        visibleRows = self._calculateVisibleRows() + 1
        rows = self.objectManager.getRows(self._tableName, currentRowIndex,
                                         visibleRows)
        self.clearSelection()
        self._addRows(rows, currentRowIndex, currenctColumnIndex)

    def getCurrentColumn(self):
        """Get the current column"""
        return self._currentColumn

    def getCurrentRow(self):
        """Get the current row"""
        return self._currentRow

    def setCurrentRowColumn(self, row, column):
        """Update the current row and column"""
        self._lastSelectedRow = self._currentRow
        self._currentRow = row
        self._currentColumn = column

    def setCurrentColumn(self, column):
        """Update the current column"""
        self._currentColumn = column

    def setCurrentRow(self, row):
        """Update the current row"""
        self._currentRow = row
        
    def getLastSelectedRow(self):
        """Return the last selected row"""
        return self._lastSelectedRow


class GalleryView(QTableWidget):
    """Class to represent the metadata in gallery mode"""
    def __init__(self, objectManager):
        super().__init__()
        self._columnsCount = None
        self._rowsCount = None
        self.objectManager = objectManager
        self.tableNames = self.objectManager.getTableNames()
        self._table = self.objectManager.getTable(self.tableNames[0])
        self._tableName = self._table.getName()
        self._tableAlias = self._table.getAlias()
        self._currentRow = 0
        self._currentColumn = 0
        self._lastSelectedCell = 0
        self.cellClicked.connect(self.setCurrentRowColumn)
        self.setGeometry(0, 0, 600, 600)
        self._oldzoom = ZOOM_SIZE
        self._rowHeight = ZOOM_SIZE
        self._defineStyles()

    def setTableName(self, tableName):
        """Set the table name"""
        self._tableName = tableName

    def getColumns(self):
        """Return the table columns"""
        return self._columns

    def getCurrentColumn(self):
        """Get the current column"""
        return self._currentColumn

    def getCurrentRow(self):
        """Get the current row"""
        return self._currentRow

    def getColumnsCount(self):
        """Get the columns count"""
        return self._columnsCount

    def getRowsCount(self):
        """Get the rows count"""
        return self._rowsCount

    def getLastSelectedCell(self):
        """Get the last selected cell in the gallery"""
        return self._lastSelectedCell

    def _createGallery(self, tableName):
        """Creating the gallery for a given table"""
        self.setColumnCount(0)
        self._tableName = tableName
        self._table = self.objectManager.getTable(self._tableName)
        self._tableSize = self.objectManager.getTableRowCount(self._tableName)
        self._columns = self._table.getColumns()
        self._columnsCount = self._calculateVisibleColumns()
        self._rowsCount = self._calculateVisibleRows()
        self._columnWithImages = self.getColumnWithImages()
        self.tableWithAdditionalInfo = self.objectManager.getTableWithAdditionalInfo()
        if self._columnWithImages:
            self._renderer = self._columns[self._columnWithImages].getRenderer()
        else:
            self._renderer = None
        self._rowsCount = int(self._tableSize / self._columnsCount) + 1
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setVisible(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vScrollBar = CustomScrollBar()
        self.setVerticalScrollBar(self.vScrollBar)
        self.vScrollBar.setValue(0)
        self.vScrollBar.valueChanged.connect(self._loadImages)
        if self._columnWithImages:
            self._rowHeight = self.getOldZoom()

    def _defineStyles(self):
        """Define the gallery styles. Create a border to the selected image"""
        self.setStyleSheet(""" QTableWidget::item:selected { border: 1.5px dashed red; }"""
                           """ QTableWidget::item:focus { border: 1.5px dashed blue;} """)

    def getTable(self):
        """Get the table"""
        return self._table

    def getRenderer(self):
        """Get the renderer"""
        return self._renderer

    def getOldZoom(self):
        """Return the old gallery zoom value"""
        return self._oldzoom

    def setOldZoom(self, value):
        """Set the old gallery zoom value"""
        self._oldzoom = value

    def _calculateVisibleColumns(self):
        """Method that calculate how many columns are visible"""
        viewportWidth = self.parent().width() if self.parent() else self.viewport().width()
        visibleCols = 0
        columnaX = 0
        viewportWidth = viewportWidth - 100  # Ensuring that horizontal scrolling does not appear
        while columnaX < viewportWidth:
            columnaX += self.getOldZoom() + 5  # Making the cells a little larger than the contents
            visibleCols += 1
        return visibleCols

    def getColumnWithImages(self):
        """Return the index of the column of contain images"""
        self.table = self.objectManager.getTable(self._tableName)
        columns = self.table.getColumns()
        for i, col in enumerate(columns):
            if col.getRenderer().renderType() == Image:
                return i
        return None

    def _calculateVisibleRows(self):
        """Method that calculate how many rows are visible"""
        viewportHeight = self.parent().height() if self.parent() else self.viewport().height()
        visibleRows = viewportHeight // self.getOldZoom() + 1
        return visibleRows

    def _addImages(self, rows, currentValue, visibleRows, seekFirstImage):
        """Add images to the gallery"""
        renderer = self.getRenderer()
        rowsValues = [row.getValues()[self._columnWithImages] for row in rows]
        countImages = 0
        selection = self.getTable().getSelection().getSelection()
        if self._columnWithImages:
            for row in range(visibleRows):
                for col in range(self._columnsCount):
                    if seekFirstImage + countImages == self._tableSize:
                        break
                    value = rowsValues[countImages]
                    item = renderer.render(value)
                    currentRow = rows[countImages]
                    if self.tableWithAdditionalInfo and self._tableName == self.tableWithAdditionalInfo[0]:
                        text = self.composeAdditionaInfo(currentRow)
                        widget = CustomWidget(item, currentRow.getId(), imagePath=value,
                                              addText=True,
                                              text=text)
                    else:
                        widget = CustomWidget(item, currentRow.getId(), imagePath=value)

                    self.setCellWidget(currentValue + row, col, widget)
                    if rows[countImages].getId() in selection:
                        self.setRangeSelected(QTableWidgetSelectionRange(currentValue + row, col, currentValue + row, col),  True)

                    self.setColumnWidth(col, self.getOldZoom() + 5)
                    countImages += 1
                self.setRowHeight(currentValue + row, self.getOldZoom() + 5)
                if seekFirstImage + countImages == self._tableSize:
                    break

    def composeAdditionaInfo(self, rowValues):
        """Create an additional description to a specific object"""
        text = ''
        columnsWithInfo = self.tableWithAdditionalInfo[1]
        values = rowValues.getValues()
        table = self.objectManager.getTable(self._tableName)
        columns = table.getColumns()
        for i, column in enumerate(columns):
            if column.getName() in columnsWithInfo:
                text += column.getName() + '=' + str(values[i]) + ' '
        return text

    def _loadImages(self):
        """Load the gallery images"""
        currentValue = self.vScrollBar.value()
        visibleRows = self._calculateVisibleRows()
        seekFirstImage = currentValue * self._columnsCount
        seekLastImage = visibleRows * self._columnsCount
        rows = self.objectManager.getRows(self._tableName, seekFirstImage, seekLastImage)
        self._addImages(rows, currentValue, visibleRows, seekFirstImage)

    def _update(self):
        """Method to update the gallery when it is resize
           Initializating with a large number of columns. It is useful for
           the method that calculates the visible columns """

        self.setColumnCount(0)
        visibleColumns = self._calculateVisibleColumns() - 1
        self._columnsCount = visibleColumns if visibleColumns > 0 else 1
        self._rowsCount = int(self._rowsCount / self._columnsCount)
        if self._columnsCount > self._tableSize:
            self._columnsCount = self._tableSize
        auxRow = 0 if self._tableSize % self._columnsCount == 0 else 1
        self._rowsCount = int(self._tableSize / self._columnsCount) + auxRow

        self.setColumnCount(self._columnsCount)
        self.setRowCount(self._rowsCount)

        self._loadImages()

    def setCurrentRowColumn(self, row, column):
        """Update the current row and column"""
        columnsCount = len(self.table.getColumns())
        index = self._currentRow * columnsCount + self._currentColumn + 1
        self._lastSelectedCell = index

        self._currentRow = row
        self._currentColumn = column


class ImageViewer(QDialog):
    """Class to plot a selected image in the gallery"""
    def __init__(self, image):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.setModal(True)

        layout = QVBoxLayout(self)
        self.label = QLabel(self)
        layout.addWidget(self.label)
        self._image = image
        self.loadImage(image)
        self.setMouseTracking(True)

    def loadImage(self, image):
        pixmap = QPixmap(image)
        self.label.setPixmap(pixmap.scaledToWidth(600, Qt.SmoothTransformation))


class QTMetadataViewer(QMainWindow, IGUI):
    """Qt Metadata viewer window"""
    def __init__(self, **kwargs):
        QMainWindow.__init__(self)
        IGUI.__init__(self, **kwargs)
        self.tableNames = self.objectManager.getTableNames()
        self.tableName = self.tableNames[0]
        self.tableAliases = self.objectManager.getTableAliases()
        self._pageSize = PAGE_SIZE
        self._triggeredResize = False
        self._triggeredGotoItem = True
        self._rowsCount = self.objectManager.getTableRowCount(self.tableName)
        self.setWindowTitle("Metadata: " + os.path.basename(self._fileName) + " (%s items)" % self._rowsCount)
        self.setGeometry(100, 100, 1000, 600)
        self.center()
        self.setMinimumSize(800, 400)
        self._tableView = True
        self._galleryView = False
        # self._darktheme = args.darktheme
        # if self._darktheme:
        #     self.setDarkTheme()
        self.setWindowIcon(QIcon(getImage(TABLE_VIEW)))

        # Table view
        self.table = TableView(self.objectManager)
        self.table._createTable(self.tableName)
        self.table.verticalHeader().sectionClicked.connect(self.onVerticalHeaderClicked)
        self.table.horizontalHeader().sectionClicked.connect(self.onHorizontalHeaderClicked)
        self.table.cellClicked.connect(self._tableCellClicked)
        self.table.horizontalHeader().setContextMenuPolicy(3)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.showHorizontalContextMenu)
        self.table.verticalHeader().setContextMenuPolicy(3)
        self.table.verticalHeader().customContextMenuRequested.connect(self.showVerticalContextMenu)

        self._columnWithImages = self.table.getColumnWithImages()

        # GalleryView
        self.gallery = GalleryView(self.objectManager)
        self.gallery._createGallery(self.tableName)
        self.gallery.cellClicked.connect(self._galleryCellClicked)
        self.gallery.cellDoubleClicked.connect(self.showImage)

        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()

        if self._galleryView:
            self._loadGalleryView()
        else:
            self._loadTableView()

    def showHorizontalContextMenu(self, pos):
        """Show the contextual menu when a column is selected by right-click"""
        # Obtaining the column
        col = self.table.horizontalHeader().logicalIndexAt(pos.x())
        self.table.setCurrentColumn(col)
        # Creating the contextual menu
        contextMenu = QMenu(self)

        # Hide column action
        hideColumnAction = QAction(HIDE_COLUMN, self)
        hideColumnAction.setIcon(QIcon(getImage(HIDE)))
        hideColumnAction.triggered.connect(lambda: self.hideColumn(col))
        contextMenu.addAction(hideColumnAction)

        # Adding toolbar actions
        contextMenu.addAction(self.sortUp)
        contextMenu.addAction(self.sortDown)
        contextMenu.addAction(self.reduceDecimals)
        contextMenu.addAction(self.increaseDecimals)

        # Showing the menu
        contextMenu.exec_(self.table.mapToGlobal(pos))

    def showVerticalContextMenu(self, pos):
        """Show the contextual menu when a column is selected by right-click"""
        # Obtaining the column
        row = self.table.verticalHeader().logicalIndexAt(pos.y())
        self.table.setCurrentRow(row)
        # Creating the contextual menu
        contextMenu = QMenu(self)

        # SubMenu Select
        selectSubMenu = QMenu(self)
        selectSubMenu.setTitle(SELECT)

        # Select all action
        selectAllAction = QAction(SELECT_ALL, self)
        selectAllAction.setIcon(QIcon(getImage(TABLE)))
        selectAllAction.triggered.connect(lambda: self.selectAll())
        # Select from here
        selectFromHereAction = QAction(SELECT_FROM_HERE, self)
        selectFromHereAction.setIcon(QIcon(getImage(FROM_HERE)))
        selectFromHereAction.triggered.connect(lambda: self.selectFromHere())
        # Select to here
        selectToHereAction = QAction(SELECT_TO_HERE, self)
        selectToHereAction.setIcon(QIcon(getImage(TO_HERE)))
        selectToHereAction.triggered.connect(lambda: self.selectToHere())

        selectSubMenu.addAction(selectAllAction)
        selectSubMenu.addAction(selectFromHereAction)
        selectSubMenu.addAction(selectToHereAction)

        contextMenu.addMenu(selectSubMenu)

        # Showing the menu
        contextMenu.exec_(self.table.mapToGlobal(pos))

    def hideColumn(self, col):
        """ Hide the table column"""
        self.table.propertiesTableDialog.hideColumn(col)
        self.table._fillTable()

    def center(self):
        """Method for centering the viewer on the screen"""
        # Get the available geometry of the work area (desktop).
        screen_rect = QDesktopWidget().availableGeometry()
        # Get window size
        window_rect = self.frameGeometry()
        # Calculate the position for centering the window on the screen
        x = (screen_rect.width() - window_rect.width()) // 2
        y = (screen_rect.height() - window_rect.height()) // 2
        # Move the window to the centered position
        self.move(x, y)

    def setDarkTheme(self):
        """Dark theme"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

    def setLightTheme(self):
        """Default theme"""
        self.setPalette(self.style().standardPalette())

    def _createStatusBar(self):
        """Create the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(DEFAULT_STATUS_BAR_HEIGHT)
        self.permanentWidgets = []

        # Information of current row and column
        self.statusBarCurrentRowColumn = QLabel("", self)
        self.statusBar().addWidget(self.statusBarCurrentRowColumn)
        self.statusBar().addWidget(self.createSeparator())

        # Information of number of selected rows
        self.statusBarSelectedRows = QLabel("", self)
        self.statusBar().addWidget(self.statusBarSelectedRows)
        self.statusBar().addWidget(self.createSeparator())

        self._createActionButtons()

    def _createActionButtons(self):
        """Method that create the status bar buttons"""
        self.removePermanentWidgets()
        # Subsets buttons
        actions = self.table.getTable().getActions()
        for action in actions:
            actionButton = QPushButton(action.getName())
            actionButton.setIcon(QIcon(getImage(PLUS)))
            self.statusBar().addPermanentWidget(actionButton)
            self.permanentWidgets.append(actionButton)
            actionButton.clicked.connect(action._callback)

        # Export to .csv
        exportAction = QPushButton(EXPORT_TO_CSV)
        exportAction.setIcon(QIcon(getImage(EXPORT_CSV)))
        self.statusBar().addPermanentWidget(exportAction)
        self.permanentWidgets.append(exportAction)
        exportAction.clicked.connect(self.exportToCSV)

        # Close button
        closeButton = QPushButton(CLOSE_BUTTON_TEXT)
        closeButton.setIcon(QIcon(getImage(ERROR)))
        closeButton.clicked.connect(self.close)
        self.statusBar().addPermanentWidget(closeButton)
        self.permanentWidgets.append(closeButton)

    def removePermanentWidgets(self):
        """Delete all PermanentWidgets stored in list(status bar buttons)"""
        for widget in self.permanentWidgets:
            self.statusBar().removeWidget(widget)

    def createSeparator(self):
        """Create a separator in order to use it in the status bar"""
        separator = QFrame(self)
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        return separator

    def _updateStatusBarRowColumn(self):
        """Update the status bar information for the current row and column"""
        row = self.gallery.getCurrentRow() if self._galleryView else self.table.getCurrentRow()
        column = self.gallery.getCurrentColumn() if self._galleryView else self.table.getCurrentColumn()
        if self._galleryView:
            self.statusBarCurrentRowColumn.setText(f"Row: {row + 1}, Column: {column + 1}")
        else:
            self.statusBarCurrentRowColumn.setText(f"Row: {row + 1}, Column: {self.table.getColumns()[column].getName()}")

    def _updateStatusBarSelectedRows(self):
        """Update the status bar information for the number of selected rows"""
        self.statusBarSelectedRows.setStyleSheet(f"color: '' ;")
        selectedRows = self.table.getTable().getSelection().getCount()
        if self._galleryView:
            self.statusBarSelectedRows.setText(f"Selected images: {selectedRows}")
        else:
            self.statusBarSelectedRows.setText(f"Selected rows: {selectedRows}")

    def _updateStatusBarMessage(self, msg):
        """Update the status bar message"""
        self.statusBarSelectedRows.setText(msg)
        self.statusBarSelectedRows.setStyleSheet(f"color: {'red'};")
        QCoreApplication.processEvents()

    def writeMessage(self, msg):
        self._updateStatusBarMessage(msg)

    def getSaveFileName(self):
        filepath, _ = QFileDialog.getSaveFileName(self, 'Save CSV File', '',
                                                  'CSV Files (*.csv)')
        return filepath

    def getSubsetName(self, typeOfObjects, elementsCount):
        subsetNameDialog = QDialog()
        subsetNameDialog.setWindowTitle("Question")
        layout = QGridLayout()
        label = QLabel("Are you sure want to create a new subset of %s " % (typeOfObjects))
        labelRunName = QLabel("Run name: ")
        line_edit = QLineEdit('create subset')
        acceptButton = QPushButton(ACCEPT)
        acceptButton.setIcon(QIcon(getImage(OK)))
        cancelButton = QPushButton(CANCEL)
        cancelButton.setIcon(QIcon(getImage(ERROR)))
        acceptButton.clicked.connect(subsetNameDialog.accept)
        cancelButton.clicked.connect(subsetNameDialog.reject)

        layout.addWidget(label, 0, 0, 1, 4, Qt.AlignCenter)
        layout.addWidget(labelRunName, 1, 0, 1, 1)
        layout.addWidget(line_edit, 1, 1, 1, 3)
        layout.addWidget(acceptButton, 2, 2, Qt.AlignRight)
        layout.addWidget(cancelButton, 2, 3, Qt.AlignLeft)
        subsetNameDialog.setLayout(layout)
        if subsetNameDialog.exec_() == QDialog.Accepted:
            return line_edit.text()
        return None

    def exportToExcel(self):
        """Method that export"""
        filepath, _ = QFileDialog.getSaveFileName(self, 'Save XLSX File', '',
                                                  'XLSX Files (*.xlsx)')
        self.objectManager.exportToExcel(self.tableName, filepath)

    def exportToCSV(self):
        self.objectManager.exportToCSV(self.tableName)

    def _createActions(self):
        """Create a set of GUI actions"""
        # File actions
        self.openAction = QAction(self)
        self.openAction.setText("&Open...")
        self.openAction.setShortcut(QKeySequence("Ctrl+O"))
        self.openAction.setIcon(QIcon(getImage(FOLDER)))
        self.openAction.triggered.connect(self.openFile)

        self.exitAction = QAction(self)
        self.exitAction.setText("E&xit")
        self.exitAction.setShortcut(QKeySequence("Ctrl+X"))
        self.exitAction.setIcon(QIcon(getImage(EXIT)))
        self.exitAction.triggered.connect(sys.exit)

        # Display actions
        self.table.propertiesTableAction = QAction(COLUMNS, self)
        self.table.propertiesTableAction.triggered.connect(self.table.propertiesTableDialog.openTableDialog)
        self.table.propertiesTableAction.setShortcut(QKeySequence("Ctrl+C"))
        self.table.propertiesTableAction.setIcon(QIcon(getImage(PREFERENCES)))
        if self._galleryView:
            self.table.propertiesTableAction.setEnabled(False)

        # Toolbar action
        self.gotoTableAction = QAction(GO_TO_TABLE_VIEW, self)
        self.gotoTableAction.setIcon(QIcon(getImage(TABLE_VIEW)))
        self.gotoTableAction.setEnabled(False)
        self.gotoTableAction.triggered.connect(self._loadTableView)

        self.gotoGalleryAction = QAction(GO_TO_GALLERY_VIEW, self)
        self.gotoGalleryAction.setIcon(QIcon(getImage(GALLERY_VIEW)))
        self.gotoGalleryAction.triggered.connect(self._loadGalleryView)

        # Columns  Toolbar action
        self.reduceDecimals = QAction(REDUCE_DECIMALS_TEXT, self)
        self.reduceDecimals.setIcon(QIcon(getImage(REDUCE_DECIMALS)))
        self.reduceDecimals.setEnabled(False)
        self.reduceDecimals.triggered.connect(lambda:  self._redIncDecimals(True))

        self.increaseDecimals = QAction(INCREASE_DECIMALS_TEXT, self)
        self.increaseDecimals.setIcon(QIcon(getImage(INCREASE_DECIMALS)))
        self.increaseDecimals.setEnabled(False)
        self.increaseDecimals.triggered.connect(lambda: self._redIncDecimals(False))

        self.sortUp = QAction(SORT_ASC, self)
        self.sortUp.setIcon(QIcon(getImage(DOWN_ARROW)))
        self.sortUp.setShortcut(QKeySequence('A'))
        self.sortUp.triggered.connect(lambda: self.table.orderByColumn(self.table.getCurrentColumn(), True))

        self.sortDown = QAction(SORT_DESC, self)
        self.sortDown.setIcon(QIcon(getImage(UP_ARROW)))
        self.sortDown.setShortcut(QKeySequence('D'))
        self.sortDown.triggered.connect(lambda: self.table.orderByColumn(self.table.getCurrentColumn(), False))

    def _createMenuBar(self):
        """ Create the menu """

        menu_bar = QMenuBar(self)

        #  File menu
        fileMenu = QMenu("&File", self)
        menu_bar.addMenu(fileMenu)
        fileMenu.addAction(self.openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # Display menu
        displayMenu = QMenu("&Display", self)
        menu_bar.addMenu(displayMenu)
        displayMenu.addAction(self.table.propertiesTableAction)

        # Tools menu
        toolsMenu = QMenu("&Tools", self)
        menu_bar.addMenu(toolsMenu)

        # Help menu
        helpMenu = QMenu("&Help", self)
        menu_bar.addMenu(helpMenu)

        self.setMenuBar(menu_bar)

    def _createToolBars(self):
        """Create the Tool bar """
        toolBar = self.addToolBar("")
        toolBar.addAction(self.gotoTableAction)
        toolBar.addAction(self.gotoGalleryAction)

        self.blockLabelIcon = QLabel('\t')
        toolBar.addWidget(self.blockLabelIcon)
        self.blockLabel = QLabel(BLOCKS)
        icon = QIcon(getImage(TABLE_BLOCKS))
        self.blockLabel.setPixmap(icon.pixmap(16, 16))
        self.blockLabel.setToolTip(BLOCKS)
        toolBar.addWidget(self.blockLabel)
        self.bockTableName = QComboBox()
        self.bockTableName.setFixedWidth(200)
        for tableName in self.tableNames:
            self.bockTableName.addItem(self.tableAliases[tableName])
        for i in range(len(self.tableNames)):
            self.bockTableName.setItemIcon(i, QIcon(getImage(TABLE)))
            # Connect signals to the methods.
        self.bockTableName.activated.connect(self.selectTable)
        self.bockTableName.setToolTip(BLOCKS)
        toolBar.addWidget(self.bockTableName)

        # Columns tool bar
        columnsToolBar2 = self.addToolBar("")

        self.zoomLabel = QLabel(getImage(ZOOM))
        icon = QIcon(getImage(ZOOM_PLUS))
        self.zoomLabel.setPixmap(icon.pixmap(20, 20))
        self.zoomLabel.setToolTip(ZOOM)
        self.zoomLabel.setEnabled(False)

        self.zoom = QSpinBox()
        self.zoom.setMaximum(ZOOM_MAX_SIZE)
        self.zoom.setMinimum(ZOOM_MIN_SIZE)
        self.zoom.setValue(ZOOM_SIZE)
        self.zoom.setToolTip(ZOOM)
        self.zoom.setFixedWidth(70)
        self.zoom.setAlignment(Qt.AlignRight)
        self.zoom.setEnabled(False)
        self.zoom.valueChanged.connect(self._renderImage)

        self.gotoItemLabel = QLabel(GO_TO_ITEM)
        icon = QIcon(getImage(GOTO_ITEM))
        self.gotoItemLabel.setPixmap(icon.pixmap(20, 20))
        self.gotoItemLabel.setToolTip(GO_TO_ITEM)
        self.gotoItemLabel.setEnabled(True)
        self.goToItem = QSpinBox()
        self.goToItem.setMaximum(MAX_ITEMS_INDEX)
        self.goToItem.setMinimum(1)
        self.goToItem.setValue(1)
        self.goToItem.setToolTip(GO_TO_ITEM)
        self.goToItem.setFixedWidth(70)
        self.goToItem.setAlignment(Qt.AlignRight)
        self.goToItem.setEnabled(True)
        self.goToItem.valueChanged.connect(self._gotoCurrentItem)

        columnsToolBar2.addWidget(self.zoomLabel)
        columnsToolBar2.addWidget(self.zoom)
        columnsToolBar2.addAction(self.sortUp)
        columnsToolBar2.addAction(self.sortDown)
        columnsToolBar2.addSeparator()
        columnsToolBar2.addAction(self.reduceDecimals)
        columnsToolBar2.addAction(self.increaseDecimals)
        columnsToolBar2.addSeparator()
        columnsToolBar2.addWidget(self.gotoItemLabel)
        columnsToolBar2.addWidget(self.goToItem)

    def openFile(self):
        filepath, _ = QFileDialog.getOpenFileNames(self, 'Open metadata File',
                                                   '', '(*.sqlite *.star *.xmd)')

    def enableGalleryOption(self):
        """Preference of gallery mode"""
        self.zoom.setValue(self.gallery.getOldZoom())
        self.zoom.setEnabled(True)
        self.zoomLabel.setEnabled(True)
        self.reduceDecimals.setEnabled(False)
        self.increaseDecimals.setEnabled(False)
        self.sortUp.setEnabled(False)
        self.sortDown.setEnabled(False)
        self.table.propertiesTableAction.setEnabled(False)
        self._triggeredResize = False

    def enableTableOptions(self, row, column):
        """Preference of table mode"""
        self.zoom.setValue(self.table.getOldZoom())
        isSorteable = self.table.getColumns()[self.table.getCurrentColumn()].isSorteable()
        self.sortUp.setEnabled(isSorteable)
        self.sortDown.setEnabled(isSorteable)
        self.table.propertiesTableAction.setEnabled(True)
        self.table._triggeredResize = False
        self.gotoTableAction.setEnabled(False)
        self.gotoGalleryAction.setEnabled(True)
        galleryEnable = True if self.table.getColumnWithImages() else False
        self.gotoGalleryAction.setEnabled(galleryEnable)
        self._triggeredResize = False

        item = self.table.cellWidget(row, column)
        if item:
            itemType = item.widgetType()
            if itemType == float or itemType == np.ndarray:
                self.reduceDecimals.setEnabled(True)
                self.increaseDecimals.setEnabled(True)
            else:
                self.reduceDecimals.setEnabled(False)
                self.increaseDecimals.setEnabled(False)

            if item.widgetType() == Image:
                self.zoom.setEnabled(True)
                self.zoomLabel.setEnabled(True)
            else:
                self.zoom.setEnabled(False)
                self.zoomLabel.setEnabled(False)

    def toggleColumn(self, table_view, column):
        """Hide a given column"""
        self.table.setColumnHidden(column,
                                   not table_view.isColumnHidden(column))

    def _loadTableView(self):
        """Load the data in a table mode"""
        if self._galleryView:
            gallery = self.takeCentralWidget()
            if gallery:
                self.gallery = gallery
        self._galleryView = False
        self._tableView = True
        galleryEnable = True if self._columnWithImages else False
        self.gotoGalleryAction.setEnabled(galleryEnable)
        self.gotoTableAction.setEnabled(False)
        self.setCentralWidget(self.table)
        self.bockTableName.setEnabled(True)
        self.table._fillTable()
        self.table.setCurrentRowColumn(self.goToItem.value(),
                                      self.table.getCurrentColumn())
        self.enableTableOptions(self.table.getCurrentRow(),
                                self.table.getCurrentColumn())
        self._gotoItem(self.goToItem.value())

    def _loadGalleryView(self):
        """Load the data in the gallary mode"""
        if self._tableView:
            table = self.takeCentralWidget()
            if table:
                self.table = table

        self._galleryView = True
        self._tableView = False
        self.gotoTableAction.setEnabled(True)
        self.gotoGalleryAction.setEnabled(False)
        self.setCentralWidget(self.gallery)
        self.enableGalleryOption()
        self.gallery._update()
        self._gotoItem(self.goToItem.value())

    def selectTable(self):
        """Method that control the tables when are selected in the tables
           combobox """
        tableAlias = self.bockTableName.currentText()
        tableName = tableAlias
        for table, alias in self.tableAliases.items():
            if alias == tableAlias:
                tableName = table
                break
        if tableName != self.table.getTableName():
            self.goToItem.setValue(1)
            self.tableName = tableName
            self.zoom.setValue(ZOOM_SIZE)
            self.table._createTable(tableName)
            self.gallery._createGallery(tableName)

            if self._galleryView and self.table.getColumnWithImages():
                self.gallery.setCurrentRowColumn(0, 0)
                self._loadGalleryView()
            else:
                self.table.setCurrentRowColumn(0, 0)
                self._loadTableView()
                galleryEnable = True if self.gallery.getColumnWithImages() else False
                if galleryEnable:
                    self.gotoGalleryAction.setEnabled(True)
                else:
                    self.gotoGalleryAction.setEnabled(False)

            self._rowsCount = self.objectManager.getTableRowCount(tableName)
            self.setWindowTitle("Metadata: " + os.path.basename(self._fileName) + " (%s items)" % self._rowsCount)
            self._updateStatusBarRowColumn()
            self._createActionButtons()

    def onVerticalHeaderClicked(self, index):
        """Event that control when the vertical header is clicked"""
        self.table.setCurrentRow(index)
        self._tableCellClicked(index, self.table.getCurrentColumn())
        self.goToItem.setValue(index + 1)
        self._updateStatusBarRowColumn()
        self._updateStatusBarSelectedRows()

    def onHorizontalHeaderClicked(self, col):
        self.table.setCurrentRow(0)
        self.table.setCurrentColumn(col)
        self._updateStatusBarRowColumn()

    def resizeEvent(self, event):
        """Control the resize event"""
        if self._triggeredResize:
            if self._galleryView:
                self.gallery._update()
                self._gotoItem(self.goToItem.value(), moveScroll=False)
            else:
                self.table._loadRows()

        self._triggeredResize = True

    def showImage(self, row, column):
        """Plot a selected image """
        item = self.gallery.cellWidget(row, column)
        if item:
            viewer = ImageViewer(item._label.pixmap())
            viewer.exec_()

    def _renderImage(self):
        """Method tha control the images renderers"""
        zoom = self.zoom.value()
        self._triggeredResize = False
        if self._tableView:
            column = self.table._columnWithImages
            self.table.getColumns()[column].getRenderer().setSize(zoom)
            self.table.setOldZoom(zoom)
            self.table._setRowHeight(zoom)
            self.table._loadRows()

        if self._galleryView:
            self.gallery.getRenderer().setSize(zoom)
            self.gallery.setOldZoom(zoom)
            self.gallery.vScrollBar.setValue(0)
            self.gallery._update()
            self._gotoItem(self.goToItem.value())

    def selectAll(self):
        """Mark as selected all the table"""
        selection = QTableWidgetSelectionRange(0, 0, self._rowsCount - 1,
                                               self.table.columnCount() - 1)
        self.selectedRange(1, self._rowsCount)
        self.table.setRangeSelected(selection, True)

    def selectFromHere(self):
        """Mark as selected a range from the current row to the last row in
           the table"""
        selection = QTableWidgetSelectionRange(self.table.getCurrentRow(), 0,
                                               self._rowsCount - 1,
                                               self.table.columnCount() - 1)
        self.selectedRange(self.table.getCurrentRow() + 1, self._rowsCount)
        self.table.setRangeSelected(selection, True)

    def selectToHere(self):
        """Mark as selected a range from the first row to the current row in
           the table"""
        selection = QTableWidgetSelectionRange(0, 0,
                                               self.table.getCurrentRow(),
                                               self.table.columnCount() - 1)
        self.selectedRange(1, self.table.getCurrentRow() + 1)
        self.table.setRangeSelected(selection, True)

    def selectedRange(self, top, bottom):
        """Mark as selected a range of rows starting from 'top' to 'bottom' """
        if top > bottom:
            topAux = top
            top = bottom
            startRow = top
            numberOfRows = abs(top - topAux) - 1
        else:
            startRow = top
            numberOfRows = bottom - top

        self.objectManager.getSelectedRangeRowsIds(self.table.getTableName(),
                                                                   startRow, numberOfRows,
                                                                   self.table.getColumns()[self.table.getSortedColumn()].getName(),
                                                                   self.table._orderAsc)
        self._updateStatusBarSelectedRows()

    def _tableCellClicked(self, row, column):
        """Event that control when a table cell is selected.
           Here the selection is handled"""

        modifiers = QApplication.keyboardModifiers()
        rowId = self.table.cellWidget(row, 0).getId()
        if modifiers == Qt.NoModifier:  # Simple click
            self.table.getTable().getSelection().clear()
            self.table.getTable().getSelection().addRowSelected(rowId)
        elif modifiers == Qt.ControlModifier:  # ctrl+click
            self.table.getTable().getSelection().addRowSelected(rowId)
        elif modifiers == Qt.ShiftModifier:  # shift+click
            self.selectedRange(self.table.getLastSelectedRow(), row + 1)

        self.enableTableOptions(row, column)
        self._triggeredGotoItem = False
        self.goToItem.setValue(row + 1)
        self._triggeredGotoItem = True
        self._updateStatusBarRowColumn()
        self._updateStatusBarSelectedRows()
        self.table.setCurrentRowColumn(row + 1, self.table.getCurrentColumn())

    def _galleryCellClicked(self, row, column):
        """Event that control the gallery when click in a image"""
        columnsCount = self.gallery.getColumnsCount()
        index = row * columnsCount + column + 1
        if index <= self._rowsCount:
            modifiers = QApplication.keyboardModifiers()
            rowId = self.gallery.cellWidget(row, column).getId()
            if modifiers == Qt.NoModifier:  # Simple click
                self.gallery.getTable().getSelection().clear()
                self.gallery.getTable().getSelection().addRowSelected(rowId)
            elif modifiers == Qt.ControlModifier:  # ctrl+click
                self.table.getTable().getSelection().addRowSelected(rowId)
            elif modifiers == Qt.ShiftModifier:  # shift+click
                self.selectedRange(self.table.getLastSelectedRow() - 1, row + 1)

            self._triggeredGotoItem = False
            self.goToItem.setValue(index)
            self._triggeredGotoItem = True
            self.gallery.setCurrentRowColumn(row, self.gallery.getCurrentColumn())
            self._updateStatusBarRowColumn()
            self._updateStatusBarSelectedRows()

    def _gotoCurrentItem(self, itemIndex):
        if self._triggeredGotoItem:
            self._gotoItem(itemIndex)

    def _gotoItem(self, itemIndex, moveScroll=True):
        """Event that allows locating an item given the index  """
        if itemIndex > self._rowsCount:
            itemIndex = self._rowsCount
            self.goToItem.setValue(itemIndex)
        itemIndex -= 1

        if self._galleryView:
            columnsCount = self.gallery.getColumnsCount()
            col = itemIndex % columnsCount
            row = itemIndex // columnsCount
            if moveScroll:
                self.gallery.vScrollBar.setValue(row)
            newIndex = self.gallery.model().index(row, col)
            self.gallery.selectionModel().setCurrentIndex(newIndex, QItemSelectionModel.NoUpdate)
            self.gallery.scrollTo(newIndex, QTableWidget.PositionAtCenter)
            self.gallery.setFocus()
            self.gallery.setCurrentRowColumn(row, col)

        else:
            col = self.table.getCurrentColumn()
            self.table.setCurrentRowColumn(itemIndex, col)
            if moveScroll:
                self.table.vScrollBar.setValue(itemIndex)
            self.table.setCurrentRowColumn(itemIndex,col)
        self._updateStatusBarRowColumn()
        self._updateStatusBarSelectedRows()

    def _redIncDecimals(self, flag):
        """Method that control the increments or reduce decimals when a float
        table cell is selected"""
        column = self.table.getCurrentColumn()
        decimals = self.table.getColumns()[column].getRenderer().getDecimalsNumber()
        redInc = -1 if flag else 1
        if decimals + redInc > 0:
            self.table.getColumns()[column].getRenderer().setDecimalNumber(decimals + redInc)
            self.table._loadRows()





