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

from PIL.ImageQt import ImageQt

logger = logging.getLogger()

import os.path
import sys

from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QPalette, QColor, QImage
from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QLabel,
                             QAction, QDialog, QVBoxLayout, QWidget, QScrollBar,
                             QDialogButtonBox, QTableWidget, QCheckBox,
                             QHBoxLayout, QTableWidgetItem, QComboBox,
                             QStatusBar, QAbstractItemView, QSpinBox)

from metadataviewer.model.object_manager import ObjectManager
from .constants import *


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
            if self.columns[i].getName() in tableHeaderList:
                self.visibleCheckBoxList[i].setChecked(True)
            else:
               self.visibleCheckBoxList[i].setChecked(False)

            # checking render column
            isImageColumn = self.columns[i].getRenderer().renderType() == Image
            if self._loadFirstTime and isImageColumn:
                self.renderCheckBoxList[i].setChecked(True)
                self.visibleCheckBoxList[i].setChecked(True)
                self.setLoadFirstTime(False)
            elif not isImageColumn:
                self.renderCheckBoxList[i].setEnabled(False)

            visibleCheckbox = self._createCellWidget(self.visibleCheckBoxList[i])
            renderCheckbox = self._createCellWidget(self.renderCheckBoxList[i])
            editCheckbox = self._createCellWidget(self.editCheckBoxList[i])
            self.tableWidget.setCellWidget(i, 0, QLabel('_' + self.columns[i].getName()))
            self.tableWidget.setCellWidget(i, 1, visibleCheckbox)
            self.tableWidget.setCellWidget(i, 2, renderCheckbox)
            self.tableWidget.setCellWidget(i, 3, editCheckbox)
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
            ckbox = QCheckBox()
            ckbox1 = QCheckBox()
            ckbox2 = QCheckBox()
            ckbox2.setEnabled(False)
            self.visibleCheckBoxList.append(ckbox)
            self.renderCheckBoxList.append(ckbox1)
            self.editCheckBoxList.append(ckbox2)
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
            self._table._loadRows()

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
        self._table.setRowHeight(0, 10)
        self._table._fillTable()

    def accept(self):
        """Accept the changes in the column properties dialog"""
        self.hideColumns()
        self.renderColums()
        self.editColums()
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
    def __init__(self, data, imagePath='', addText=False, text=''):
        super().__init__()
        self._data = data
        self._imagePath = imagePath
        self._layout = QHBoxLayout()
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

        else:  # Assuming the data is a file path to an image
            try:
                im = data.convert("RGBA")
                data = im.tobytes("raw", "RGBA")
                qimage = QtGui.QImage(data, im.size[0], im.size[1],
                                      QtGui.QImage.Format_RGBA8888)

                pixmap = QPixmap.fromImage(qimage)
                self._label.setPixmap(pixmap)
                self._label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
                self._layout.addWidget(self._label)
                self._type = Image

                if addText:
                    self._adicinalText.setAlignment(Qt.AlignBottom)
                    self._layout.addWidget(self._adicinalText)
            except Exception as e:
                logger.error("Error loading the image:", e)

        self.setLayout(self._layout)

    def widgetType(self):
        return self._type

    def widgetContent(self):
        return self._label

    def getData(self):
        return self._data

    def getImagePath(self):
        return self._imagePath


class TableView(QTableWidget):
    """Class to represent the metadata in table mode"""
    def __init__(self, objectManager):
        super().__init__()
        self.propertiesTableDialog = ColumnPropertiesTable(self, self)
        self._pageNumber = 1  # First page
        self._pageSize = ZOOM_SIZE
        self._actualRow = 0
        self._actualColumn = 0
        self.oldColumn = None
        self._orderAsc = True
        self.objecManager = objectManager
        self.cellClicked.connect(self.setActualRowColumn)
        self.horizontalHeader().sectionClicked.connect(self.setActualColumn)
        self._oldzoom = ZOOM_SIZE

    def _createTable(self, tableName):
        """Create the table structure"""
        self.setColumnCount(0)
        self._tableName = tableName
        self._rowsCount = self.objecManager.getTableRowCount(self._tableName)
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.verticalHeader().setVisible(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vScrollBar = CustomScrollBar()
        self.hScrollBar = QScrollBar()
        self._createHeader()
        self.columns = self.objecManager.getTable(self._tableName).getColumns()
        self._columnWithImages = self.getColumnWithImages()
        self._rowHeight = DEFAULT_ROW_HEIGHT  # Default row height
        self.propertiesTableDialog.registerColumns(self.columns)
        self.propertiesTableDialog.setLoadFirstTime(True)
        self.propertiesTableDialog.InsertRows()
        self.propertiesTableDialog.uncheckVisibleColumns(8)
        self.propertiesTableDialog.hideColumns()
        self.setVerticalScrollBar(self.vScrollBar)
        self.setHorizontalScrollBar(self.hScrollBar)
        self.vScrollBar.valueChanged.connect(lambda: self._loadRows())
        self.hScrollBar.valueChanged.connect(lambda: self._loadRows())
        self.setCurrentCell(0, 0)

    def getOldZoom(self):
        """Return the old table zoom value"""
        return self._oldzoom

    def setOldZoom(self, value):
        """Set the old table zoom value"""
        self._oldzoom = value

    def getRowHeight(self):
        return self._rowHeight

    def _setRowHeight(self, rowHeight):
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
        if self.oldColumn is not None:
            self.horizontalHeaderItem(self.oldColumn).setIcon(QIcon(None))

        self.oldColumn = self._actualColumn
        self._actualColumn = column

        self.horizontalHeader().setSortIndicator(column, Qt.AscendingOrder if self._orderAsc else Qt.DescendingOrder)
        self.objecManager.sort(self._tableName, column, self._orderAsc)
        self.clearContents()
        self.vScrollBar.setValue(0)
        self._loadRows()

        icon = QIcon(DOWN_ARROW) if self._orderAsc else QIcon(UP_ARROW)
        self.horizontalHeaderItem(column).setIcon(icon)

    def _createHeader(self):
        """Create the table header"""
        table = self.objecManager.getTable(self._tableName)
        self._columns = table.getColumns()
        self.setColumnCount(len(self._columns))
        for i, column in enumerate(self._columns):
            item = QTableWidgetItem(str(column.getName()))
            item.setTextAlignment(Qt.AlignCenter)
            self.setHorizontalHeaderItem(i, item)

    def _fillTable(self):
        """Fill the table"""
        columns = self.objecManager.getTable(self._tableName).getColumns()
        self._rowsCount = self.objecManager.getTableRowCount(self._tableName)
        self.setColumnCount(len(columns))
        self.setRowCount(self._rowsCount)
        if self._columnWithImages:
            self._rowHeight = self.getOldZoom()
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
        return visibleCols

    def _calculateVisibleRows(self):
        """Method that calculate how many rows are visible"""
        viewportHeight = self.parent().height() if self.parent() else self.viewport().height()
        rowHeight = self.rowHeight(0) if self.rowHeight(0) else DEFAULT_ROW_HEIGHT  # row height (minumum size in case of the table is empty)
        visibleRows = viewportHeight // rowHeight + 1
        return visibleRows

    def _addRows(self, rows, currentRowIndex, currenctColumnIndex):
        """Add rows to the table"""
        columnsCount = self._calculateVisibleColumns()
        endColumn = currenctColumnIndex + columnsCount
        if endColumn > len(self._columns):
            endColumn = len(self._columns)

        for i in range(len(rows)):
            rowValues = rows[i]
            values = rowValues.getValues()
            for col in range(currenctColumnIndex, endColumn):
                if self._columns[col].getRenderer().renderType() != Image:
                    item = self._columns[col].getRenderer().render(values[col])
                else:
                    if self.propertiesTableDialog.renderCheckBoxList[col].isChecked():
                        item = self._columns[col].getRenderer().render(values[col])
                    else:
                        item = values[col]

                widget = CustomWidget(item)
                self.setCellWidget(i + currentRowIndex, col, widget)
                self.resizeColumnToContents(col)
                self.setColumnWidth(col, self.columnWidth(col) + 5)
            self.setRowHeight(i + currentRowIndex, self._rowHeight + 5)

    def _loadRows(self):
        """Load the table rows"""
        currentRowIndex = self.vScrollBar.value()
        currenctColumnIndex = self.hScrollBar.value()
        visibleRows = self._calculateVisibleRows()
        rows = self.objecManager.getRows(self._tableName, currentRowIndex,
                                         visibleRows)
        self._addRows(rows, currentRowIndex, currenctColumnIndex)

    def getActualColumn(self):
        """Get the current column"""
        return self._actualColumn

    def getActualRow(self):
        """Get the current row"""
        return self._actualRow

    def setActualRowColumn(self, row, column):
        """Update the current row and column"""
        self._actualRow = row
        self._actualColumn = column

    def setActualColumn(self, column):
        self._actualColumn = column


class GalleryView(QTableWidget):
    """Class to represent the metadata in gallery mode"""
    def __init__(self, objectManager):
        super().__init__()
        self._columnsCount = None
        self._rowsCount = None
        self.objecManager = objectManager
        self.objecManager.selectDAO()
        self.tableNames = self.objecManager.getTableNames()
        table = self.objecManager.getTable(self.tableNames[0])
        self._tableName = table.getName()
        self._tableAlias = table.getAlias()
        self._actualRow = 0
        self._actualColumn = 0
        self.cellClicked.connect(self.setActualRowColumn)
        self.setGeometry(0, 0, 600, 600)
        self._oldzoom = ZOOM_SIZE
        self._rowHeight = ZOOM_SIZE

    def setTableName(self, tableName):
        """Set the table name"""
        self._tableName = tableName

    def getColumns(self):
        """Return the table columns"""
        return self._columns

    def getActualColumn(self):
        """Get the current column"""
        return self._actualColumn

    def getActualRow(self):
        """Get the current row"""
        return self._actualRow

    def getColumnsCount(self):
        return self._columnsCount

    def getRowsCount(self):
        return self._rowsCount

    def _createGallery(self, tableName):
        """Creating the gallery for a given table"""
        self.setColumnCount(0)
        self._tableName = tableName
        self._tableSize = self.objecManager.getTableRowCount(self._tableName)
        self._columns = self.objecManager.getTable(self._tableName).getColumns()
        self._columnsCount = self._calculateVisibleColumns()
        self._rowsCount = self._calculateVisibleRows()
        self._columnWithImages = self.getColumnWithImages()
        self._renderer = self._columns[self._columnWithImages].getRenderer()
        self._rowsCount = int(self._tableSize / self._columnsCount) + 1
        self._tableName = tableName
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

    def getRenderer(self):
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
        self.table = self.objecManager.getTable(self._tableName)
        columns = self.table.getColumns()
        for i, col in enumerate(columns):
            if col.getRenderer().renderType() == Image:
                return i
        return None

    def _calculateVisibleRows(self):
        """Method that calculate how many rows are visible"""
        viewportHeight = self.parent().height() if self.parent() else self.viewport().height()
        visibleRows = viewportHeight // self._rowHeight + 1
        return visibleRows

    def _addImages(self, rows, currentValue, visibleRows, seekFirstImage):
        """Add images to the gallary"""
        renderer = self.getRenderer()
        rowsValues = [row.getValues()[self._columnWithImages] for row in rows]
        countImages = 0

        if self._columnWithImages:
            for row in range(visibleRows):
                for col in range(self._columnsCount):
                    if seekFirstImage + countImages == self._tableSize:
                        break
                    value = rowsValues[countImages]
                    item = renderer.render(value)
                    self.setCellWidget(currentValue + row, col,
                                       CustomWidget(item, imagePath=value))
                    self.setColumnWidth(col, self.getOldZoom() + 5)
                    countImages += 1
                self.setRowHeight(currentValue + row, self.getOldZoom() + 5)
                if seekFirstImage + countImages == self._tableSize:
                    break

    def _loadImages(self):
        """Load the gallery images"""
        currentValue = self.vScrollBar.value()
        visibleRows = self._calculateVisibleRows()
        seekFirstImage = currentValue * self._columnsCount
        seekLastImage = visibleRows * self._columnsCount
        rows = self.objecManager.getRows(self._tableName, seekFirstImage, seekLastImage)
        self._addImages(rows, currentValue, visibleRows, seekFirstImage)

    def _update(self):
        """Method to update the gallery when it is resize
           Initializating with a large number of columns. It is useful for
           the method that calculates the visible columns """

        self.setColumnCount(0)
        self._columnsCount = self._calculateVisibleColumns() - 1
        self._rowsCount = int(self._rowsCount / self._columnsCount)
        if self._columnsCount > self._tableSize:
            self._columnsCount = self._tableSize
        auxRow = 0 if self._tableSize % self._columnsCount == 0 else 1
        self._rowsCount = int(self._tableSize / self._columnsCount) + auxRow

        self.setColumnCount(self._columnsCount)
        self.setRowCount(self._rowsCount)

        self._loadImages()

    def setActualRowColumn(self, row, column):
        """Create a border to the selected image"""
        self.setStyleSheet("""
                            QTableWidget::item:selected {
                                border: 1.5px dashed red;
                            }
                        """)
        self._actualRow = row
        self._actualColumn = column


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


class QTMetadataViewer(QMainWindow):
    """Qt Metadata viewer window"""
    def __init__(self, args):
        super().__init__()
        self._fileName = os.path.abspath(args.fileName)
        self.objecManager = ObjectManager(args.fileName)
        self.objecManager.selectDAO()
        self.tableNames = self.objecManager.getTableNames()
        self.tableName = self.tableNames[0]
        self.tableAliases = self.objecManager.getTableAliases()
        self._pageSize = PAGE_SIZE
        self._triggeredResize = False
        self._rowsCount = self.objecManager.getTableRowCount(self.tableName)
        self.setWindowTitle("Metadata: " + os.path.basename(args.fileName) + " (%s items)" % self._rowsCount)
        self.setGeometry(100, 100, 800, 400)
        self.setMinimumSize(800, 400)
        self._tableView = args.tableview
        self._galleryView = args.galleryview
        self._darktheme = args.darktheme
        if self._darktheme:
            self.setDarkTheme()

        # Table view
        self.table = TableView(self.objecManager)
        self.table._createTable(self.tableName)
        self.table.cellClicked.connect(self._tableCellClicked)
        self.table.verticalHeader().sectionClicked.connect(self.onVerticalHeaderClicked)
        self._columnWithImages = self.table.getColumnWithImages()

        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()

        # GalleryView
        self.gallery = GalleryView(self.objecManager)
        self.gallery._createGallery(self.tableName)
        self.gallery.cellClicked.connect(self._galleryCellClicked)
        self.gallery.cellDoubleClicked.connect(self.showImage)

        if self._galleryView:
            self._loadGalleryView()
        else:
            self._loadTableView()

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
        self.statusbar.setFixedHeight(DEFAULT_ROW_HEIGHT)

    def _createActions(self):
        """Create a set of GUI actions"""
        # File actions
        self.newAction = QAction(self)
        self.newAction.setText("&Open...")
        self.newAction.setShortcut(QKeySequence("Ctrl+O"))
        self.newAction.setIcon(QIcon(FOLDER))

        self.exitAction = QAction(self)
        self.exitAction.setText("E&xit")
        self.exitAction.setShortcut(QKeySequence("Ctrl+X"))
        self.exitAction.setIcon(QIcon(EXIT))
        self.exitAction.triggered.connect(sys.exit)

        # Display actions
        self.table.propertiesTableAction = QAction(COLUMNS, self)
        self.table.propertiesTableAction.triggered.connect(self.table.propertiesTableDialog.openTableDialog)
        self.table.propertiesTableAction.setShortcut(QKeySequence("Ctrl+C"))
        self.table.propertiesTableAction.setIcon(QIcon(PREFERENCES))
        if self._galleryView:
            self.table.propertiesTableAction.setEnabled(False)

        # Toolbar action
        self.gotoTableAction = QAction(GO_TO_TABLE_VIEW, self)
        self.gotoTableAction.setIcon(QIcon(TABLE_VIEW))
        self.gotoTableAction.setEnabled(False)
        self.gotoTableAction.triggered.connect(self._loadTableView)

        self.gotoGalleryAction = QAction(GO_TO_GALLERY_VIEW, self)
        self.gotoGalleryAction.setIcon(QIcon(GALLERY_VIEW))
        self.gotoGalleryAction.triggered.connect(self._loadGalleryView)

        # Columns  Toolbar action
        self.reduceDecimals = QAction(REDUCE_DECIMALS_TEXT, self)
        self.reduceDecimals.setIcon(QIcon(REDUCE_DECIMALS))
        self.reduceDecimals.setEnabled(False)
        self.reduceDecimals.triggered.connect(lambda:  self._redIncDecimals(True))

        self.increaseDecimals = QAction(INCREASE_DECIMALS_TEXT, self)
        self.increaseDecimals.setIcon(QIcon(INCREASE_DECIMALS))
        self.increaseDecimals.setEnabled(False)
        self.increaseDecimals.triggered.connect(lambda: self._redIncDecimals(False))

        self.sortUp = QAction(SORT_ASC, self)
        self.sortUp.setIcon(QIcon(DOWN_ARROW))
        self.sortUp.triggered.connect(lambda: self.table.orderByColumn(self.table.getActualColumn(), True))

        self.sortDown = QAction(SORT_DESC, self)
        self.sortDown.setIcon(QIcon(UP_ARROW))
        self.sortDown.triggered.connect(lambda: self.table.orderByColumn(self.table.getActualColumn(), False))

    def _loadTableView(self):
        """Load the data in a table mode"""
        if self._galleryView:
            widget = self.takeCentralWidget()
            if widget:
                self.gallery = widget
        self._galleryView = False
        self._tableView = True
        self.table.setActualRowColumn(0, 0)
        galleryEnable = True if self._columnWithImages else False
        self.gotoGalleryAction.setEnabled(galleryEnable)
        self.gotoTableAction.setEnabled(False)
        self.setCentralWidget(self.table)
        self.bockTableName.setEnabled(True)
        self.table._fillTable()
        self.enableTableOptions(self.table.getActualRow(),
                                self.table.getActualColumn())
        self._gotoItem(self.goToItem.value())

    def _loadGalleryView(self):
        """Load the data in a gallary mode"""
        if self._tableView:
            widget = self.takeCentralWidget()
            if widget:
                self.table = widget

        self._galleryView = True
        self._tableView = False
        self.gotoTableAction.setEnabled(True)
        self.gotoGalleryAction.setEnabled(False)
        self.setCentralWidget(self.gallery)
        self.enableGalleryOption()
        self.gallery._update()
        self._gotoItem(self.goToItem.value())

    def _createMenuBar(self):
        """ Create the menu """

        menu_bar = QMenuBar(self)

        #  File menu
        fileMenu = QMenu("&File", self)
        menu_bar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # Display menu
        displayMenu = QMenu("&Display", self)
        menu_bar.addMenu(displayMenu)
        if self._tableView:
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
        icon = QIcon(TABLE_BLOCKS)
        self.blockLabel.setPixmap(icon.pixmap(16, 16))
        self.blockLabel.setToolTip(BLOCKS)
        toolBar.addWidget(self.blockLabel)
        self.bockTableName = QComboBox()
        self.bockTableName.setFixedWidth(200)
        for tableName in self.tableNames:
            self.bockTableName.addItem(self.tableAliases[tableName])
        for i in range(len(self.tableNames)):
            self.bockTableName.setItemIcon(i, QIcon(TABLE))
            # Connect signals to the methods.
        self.bockTableName.activated.connect(self.selectTable)
        self.bockTableName.setToolTip(BLOCKS)
        toolBar.addWidget(self.bockTableName)

        # Columns tool bar
        columnsToolBar2 = self.addToolBar("")

        self.zoomLabel = QLabel(ZOOM)
        icon = QIcon(ZOOM_PLUS)
        self.zoomLabel.setPixmap(icon.pixmap(20, 20))
        self.zoomLabel.setToolTip(ZOOM)
        self.zoomLabel.setEnabled(False)

        self.zoom = QSpinBox()
        self.zoom.setMaximum(2000)
        self.zoom.setMinimum(ZOOM_SIZE)
        self.zoom.setValue(ZOOM_SIZE)
        self.zoom.setToolTip(ZOOM)
        self.zoom.setFixedWidth(70)
        self.zoom.setAlignment(Qt.AlignRight)
        self.zoom.setEnabled(False)
        self.zoom.valueChanged.connect(self._renderImage)

        self.gotoItemLabel = QLabel(GO_TO_ITEM)
        icon = QIcon(GOTO_ITEM)
        self.gotoItemLabel.setPixmap(icon.pixmap(20, 20))
        self.gotoItemLabel.setToolTip(GO_TO_ITEM)
        self.gotoItemLabel.setEnabled(True)
        self.goToItem = QSpinBox()
        self.goToItem.setMaximum(8000000)
        self.goToItem.setMinimum(1)
        self.goToItem.setValue(1)
        self.goToItem.setToolTip(GO_TO_ITEM)
        self.goToItem.setFixedWidth(70)
        self.goToItem.setAlignment(Qt.AlignRight)
        self.goToItem.setEnabled(True)
        self.goToItem.valueChanged.connect(self._gotoItem)

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

    def toggleColumn(self, table_view, column):
        """Hide a given column"""
        self.table.setColumnHidden(column,
                                   not table_view.isColumnHidden(column))

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
                self.gallery.setActualRowColumn(0, 0)
                self._loadGalleryView()
            else:
                self.table.setActualRowColumn(0, 0)
                self._loadTableView()
                galleryEnable = True if self.gallery.getColumnWithImages() else False
                if galleryEnable:
                    self.gotoGalleryAction.setEnabled(True)
                else:
                    self.gotoGalleryAction.setEnabled(False)

            self._rowsCount = self.objecManager.getTableRowCount(tableName)
            self.setWindowTitle("Metadata: " + os.path.basename(self._fileName) + " (%s items)" % self._rowsCount)

    def _tableCellClicked(self, row, column):
        """Event that control when a table cell is selected"""
        self.goToItem.setValue(row + 1)
        self.enableTableOptions(row, column)

    def onVerticalHeaderClicked(self, index):
        """Event that control when the vertical header is clicked"""
        self.goToItem.setValue(index + 1)

    def resizeEvent(self, event):
        """Control the resize event"""
        if self._triggeredResize:
            if self._galleryView:
                self.gallery._update()
                self._gotoItem(self.goToItem.value())
            else:
                self.table._loadRows()
                self._gotoItem(self.goToItem.value())

        self._triggeredResize = True

    def showImage(self, row, column):
        """Plot a selected image """
        item = self.gallery.cellWidget(row, column)
        if item:
            viewer = ImageViewer(item._label.pixmap())
            viewer.exec_()

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
        isSorteable = self.table.getColumns()[self.table.getActualColumn()].isSorteable()
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
            if item.widgetType() == float:
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
            self.gallery._update()
        self._gotoItem(self.goToItem.value())

    def _galleryCellClicked(self, row, column):
        """Event that control the gallery when click in a image"""
        columnsCount = self.gallery.getColumnsCount()
        index = row * columnsCount + column + 1
        self.goToItem.setValue(index)

    def _gotoItem(self, itemIndex):
        """Event that allows locating an item given the index  """
        if itemIndex > self._rowsCount:
            itemIndex = self._rowsCount
            self.goToItem.setValue(itemIndex)
        itemIndex -= 1

        self.table.selectRow(itemIndex)

        columnsCount = self.gallery.getColumnsCount()
        col = itemIndex % columnsCount
        row = itemIndex // columnsCount
        model = self.gallery.model()
        index = model.index(row, col)
        self.gallery.setCurrentCell(index.row(), index.column())
        self.gallery.setActualRowColumn(row, col)

    def _redIncDecimals(self, flag):
        """Method that control the increments or reduce decimals when a float
        table cell is selected"""
        column = self.table.getActualColumn()
        decimals = self.table.getColumns()[column].getRenderer().getDecimalsNumber()
        redInc = -1 if flag else 1
        if decimals + redInc > 0:
            self.table.getColumns()[column].getRenderer().setDecimalNumber(decimals + redInc)
            self.table._loadRows()





