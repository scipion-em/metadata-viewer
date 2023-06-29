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
import os.path
import sys

from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QIntValidator, QPalette, \
    QColor
from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QLabel,
                             QAction, QDialog, QVBoxLayout, QWidget, QScrollBar,
                             QDialogButtonBox, QTableWidget, QCheckBox,
                             QHBoxLayout, QTableWidgetItem, QComboBox,
                             QStatusBar, QAbstractItemView, QLineEdit, QSpinBox,
                             QSizePolicy)

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
        self.width = 480
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

    def editColums(self):
        pass

    def renderColums(self):
        self._table.setRowHeight(0, 10)
        self._table._fillTable()

    def accept(self):
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
    def __init__(self, data, addText=False, text=""):
        super().__init__()
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel()
        self._adicinalText = QLabel(text)
        self._type = str

        if isinstance(data, bool):
            self._label = QCheckBox()
            self._label.setChecked(data)
            self._label.setEnabled(False)
            self._layout.addWidget(self._label, alignment=Qt.AlignCenter)

        elif isinstance(data, int) or isinstance(data, float) or isinstance(data, str):
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
                print("Error loading the image:", e)

        self.setLayout(self._layout)

    def widgetType(self):
        return self._type

    def widgetContent(self):
        return self._label


class TableView(QTableWidget):
    """Class to represent the metadata in table mode"""
    def __init__(self, objectManager):
        super().__init__()
        self.propertiesTableDialog = ColumnPropertiesTable(self, self)
        self._pageNumber = 1
        self._pageSize = 50
        self._actualRow = 0
        self._actualColumn = 0
        self.oldColumn = None
        self._orderAsc = True
        self.objecManager = objectManager
        self.cellClicked.connect(self.setActualRowColumn)
        self.horizontalHeader().sectionClicked.connect(self.setActualColumn)

    def _createTable(self, tableName):
        # Creating the table
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
        self.propertiesTableDialog.registerColumns(self.columns)
        self.propertiesTableDialog.setLoadFirstTime(True)
        self.propertiesTableDialog.InsertRows()
        self._fillTable()
        self.setVerticalScrollBar(self.vScrollBar)
        self.setHorizontalScrollBar(self.hScrollBar)
        self.vScrollBar.valueChanged.connect(lambda: self._loadRows())
        self.hScrollBar.valueChanged.connect(lambda: self._loadRows())
        self.setCurrentCell(0, 0)

    def setTableName(self, tableName):
        self._tableName = tableName

    def getTableName(self):
        return self._tableName

    def getColumns(self):
        return self.columns

    def getColumnWithImages(self):
        for i, col in enumerate(self.columns):
            if col.getRenderer().renderType() == Image:
                return i
        return None

    def orderByColumn(self, column, order):

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
        # Creating the header
        table = self.objecManager.getTable(self._tableName)
        self.setColumnCount(0)
        self._columns = table.getColumns()
        self.setColumnCount(len(self._columns))
        for i, column in enumerate(self._columns):
            item = QTableWidgetItem(str(column.getName()))
            item.setTextAlignment(Qt.AlignCenter)
            self.setHorizontalHeaderItem(i, item)

    def _fillTable(self):
        columns = self.objecManager.getTable(self._tableName).getColumns()
        self._rowsCount = self.objecManager.getTableRowCount(self._tableName)
        self.setColumnCount(len(columns))
        self.setRowCount(self._rowsCount)
        # Set prototype item to improve loading speed
        prototype_item = QTableWidgetItem()
        self.setItemPrototype(prototype_item)
        self._loadRows()

    def _calculateVisibleColumns(self):
        viewportWidth = self.viewport().width()
        visibleCols = 0

        for col in range(self.columnCount()):
            columnaX = self.columnViewportPosition(col)
            widthColumna = self.columnWidth(col)
            if columnaX < viewportWidth and columnaX + widthColumna > 0:
                visibleCols += 1
        return visibleCols

    def _calculateVisibleRows(self):
        viewportHeight = self.viewport().height()
        rowHeight = self.rowHeight(0) if self.rowHeight(0) else 30  # row height (minumum size in case of the table is empty)
        visibleRows = viewportHeight // rowHeight + 1
        return visibleRows

    def _addRows(self, rows, currentRowIndex, currenctColumnIndex):
        columnsCount = self._calculateVisibleColumns()
        endColumn = currenctColumnIndex + columnsCount
        if endColumn > len(self._columns):
            endColumn = len(self._columns)

        for i in range(len(rows)):
            rowValues = rows[i]
            if rowValues.getValues():
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
                self.resizeRowToContents(i + currentRowIndex)

    def _loadRows(self):
        currentRowIndex = self.vScrollBar.value()
        currenctColumnIndex = self.hScrollBar.value()
        visibleRows = self._calculateVisibleRows()
        rows = self.objecManager.getRows(self._tableName, currentRowIndex,
                                         visibleRows)
        self._addRows(rows, currentRowIndex, currenctColumnIndex)

    def getActualColumn(self):
        return self._actualColumn

    def getActualRow(self):
        return self._actualRow

    def setActualRowColumn(self, row, column):
        self._actualRow = row
        self._actualColumn = column

    def setActualColumn(self, column):
        self._actualColumn = column


class GalleryView(QTableWidget):
    """Class to represent the metadata in gallery mode"""
    def __init__(self, objectManager):
        super().__init__()
        self._actualCell = 0
        self._columnsCount = None
        self._rowsCount = None
        self.objecManager = objectManager
        self.objecManager.selectDAO()
        self.tableNames = self.objecManager.getTableNames()
        table = self.objecManager.getTable(self.tableNames[0])
        self._tableName = table.getName()
        self._tableAlias = table.getAlias()
        self._columns = self.objecManager.getTable(self._tableName).getColumns()
        self._actualRow = 0
        self._actualColumn = 0
        self._columnWithImages = self.getColumnWithImages()
        self.cellClicked.connect(self.setActualRowColumn)
        self.setGeometry(0, 0, 600, 600)

    def setTableName(self, tableName):
        self._tableName = tableName

    def getColumns(self):
        return self._columns

    def _createGallery(self, tableName):
        # Creating the gallery
        self._tableName = tableName
        self.setColumnCount(30)
        self._tableSize = self.objecManager.getTableRowCount(self._tableName)
        self._columnsCount = self._calculateVisibleColumns()
        self._columnWithImages = self.getColumnWithImages()
        self._rowsCount = int(self._tableSize / self._columnsCount) + 1
        self.setRowCount(self._rowsCount)
        self.setColumnCount(self._columnsCount)
        self._tableName = tableName
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setVisible(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vScrollBar = CustomScrollBar()
        self._loadImages()
        self.setVerticalScrollBar(self.vScrollBar)
        self.vScrollBar.valueChanged.connect(self._loadImages)
        self._triggeredResize = False

    def _calculateVisibleColumns(self):
        viewportWidth = self.viewport().width()
        visibleCols = 0

        for col in range(self.columnCount()):
            columnaX = self.columnViewportPosition(col)
            widthColumna = self.columnWidth(col)

            if columnaX < viewportWidth and columnaX + widthColumna > 0:
                visibleCols += 1
        return visibleCols

    def getColumnWithImages(self):
        self.table = self.objecManager.getTable(self._tableName)
        columns = self.table.getColumns()
        for i, col in enumerate(columns):
            if col.getRenderer().renderType() == Image:
                return i
        return None

    def _calculateVisibleRows(self):
        viewportHeight = self.viewport().height()
        rowHeight = self.rowHeight(0) if self.rowHeight(0) else 30  # row height (minumum size in case of the table is empty)
        visibleRows = viewportHeight // rowHeight + 1
        return visibleRows

    def _addImages(self, rows, currentValue, visibleRows, seekFirstImage):
        self._columns = self.objecManager.getTable(self._tableName).getColumns()
        self._rowsCount = int(self._tableSize / self._columnsCount) + 1
        self.setColumnCount(self._columnsCount)
        self.setRowCount(self._rowsCount)
        countImages = 0
        if self._columnWithImages:
            for row in range(visibleRows):
                for col in range(self._columnsCount):
                    if seekFirstImage + countImages == self._tableSize:
                        break
                    values = rows[countImages]
                    item = self._columns[self._columnWithImages].getRenderer().render(values.getValues()[self._columnWithImages])
                    widget = CustomWidget(item, False, str(seekFirstImage + countImages + 1))
                    self.setCellWidget(currentValue + row, col, widget)

                    self.resizeColumnToContents(col)
                    size = self.columnWidth(col)
                    self.setColumnWidth(col, size + 5)
                    countImages += 1
                self.resizeRowToContents(currentValue + row)
                size = self.rowHeight(currentValue + row)
                self.setRowHeight(currentValue + row, size + 5)
                if seekFirstImage + countImages == self._tableSize:
                    break

    def _loadImages(self):
        currentValue = self.vScrollBar.value()
        visibleRows = self._calculateVisibleRows()
        seekFirstImage = currentValue * self._columnsCount
        seekLastImage = visibleRows * self._columnsCount
        rows = self.objecManager.getRows(self._tableName, seekFirstImage, seekLastImage)
        self._addImages(rows, currentValue, visibleRows, seekFirstImage)

    def _update(self):
        # Initializating with a large number of columns. It is useful for
        # the method that calculates the visible columns
        self.setColumnCount(50)
        self._columnsCount = self._calculateVisibleColumns() - 1
        # Verifying that there is at least five column
        if self._columnsCount < 5:
            self._columnsCount = 5
        self.setColumnCount(self._columnsCount)
        self._rowsCount = int(self._rowsCount / self._columnsCount)
        # Verifying that there is at least one row
        if self._rowsCount < 5:
            self._rowsCount = 5
        self._loadImages()

    def resizeEvent(self, event):
        if self._triggeredResize:
            self._update()
        self._triggeredResize = True

    def setActualRowColumn(self, row, column):
        self.setStyleSheet("""
                            QTableWidget::item:selected {
                                border: 1.5px dashed red;
                            }
                        """)
        self._actualRow = row
        self._actualColumn = column


class QTMetadataViewer(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self._fileName = os.path.abspath(args.fileName)
        self.objecManager = ObjectManager(args.fileName)
        self.objecManager.selectDAO()
        self.tableNames = self.objecManager.getTableNames()
        self.tableAliases = self.objecManager.getTableAliases()
        self._pageSize = 50
        self._triggeredResize = False
        self._rowsCount = self.objecManager.getTableRowCount(self.tableNames[0])
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
        self.table._createTable(self.tableNames[0])
        self.table.cellClicked.connect(self._tableCellClicked)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()

        # GalleryView
        self.gallery = GalleryView(self.objecManager)
        self.gallery._createGallery(self.tableNames[0])

        if self._galleryView:
            self._loadGalleryView()
        else:
            self._loadTableView()

    def setDarkTheme(self):
        # Dark theme
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
        # default theme
        self.setPalette(self.style().standardPalette())

    def resizeEvent(self, event):
        if self._triggeredResize:
            self.table._loadRows()
        self._triggeredResize = True

    def _createStatusBar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(30)

    def _createActions(self):
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
        self._galleryView = False
        self._tableView = True
        self.zoom.setValue(100)
        row = self.table.getActualRow()
        column = self.table.getActualColumn()
        self.enableTableOptions(row, column)
        galleryEnable = True if self.gallery.getColumnWithImages() else False
        self.gotoGalleryAction.setEnabled(galleryEnable)
        self.gotoTableAction.setEnabled(False)
        newTableSize = self.size()
        widget = self.takeCentralWidget()
        if widget:
            self.gallery = widget
        self.table.setVisible(True)
        self.table.resize(newTableSize.width(), newTableSize.height())
        self.setCentralWidget(self.table)
        self.bockTableName.setEnabled(True)
        self.table._loadRows()

    def _loadGalleryView(self):
        self._galleryView = True
        self._tableView = False
        self.zoom.setValue(100)
        self.enableGalleryOption()
        self.gotoTableAction.setEnabled(True)
        self.gotoGalleryAction.setEnabled(False)
        widget = self.takeCentralWidget()
        if widget:
            self.table = widget
        tableName = self.bockTableName.currentText()
        for table, alias in self.tableAliases.items():
            if alias == tableName:
                tableName = table
                break
        self.gallery.setTableName(tableName)
        self.gallery.setVisible(True)
        self.setCentralWidget(self.gallery)

    def _createMenuBar(self):
        # Creating the menu
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
        # Tool bar
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
        columnsToolBar2.addWidget(self.zoomLabel)
        self.zoom = QSpinBox()
        self.zoom.setMaximum(2000)
        self.zoom.setMinimum(50)
        self.zoom.setValue(100)
        self.zoom.setToolTip(ZOOM)
        self.zoom.setFixedWidth(70)
        self.zoom.setAlignment(Qt.AlignRight)
        self.zoom.setEnabled(False)
        columnsToolBar2.addWidget(self.zoom)
        self.zoom.valueChanged.connect(self._renderImage)

        columnsToolBar2.addAction(self.sortUp)
        columnsToolBar2.addAction(self.sortDown)
        columnsToolBar2.addAction(self.reduceDecimals)
        columnsToolBar2.addAction(self.increaseDecimals)

    def toggleColumn(self, table_view, column):
        self.table.setColumnHidden(column,
                                   not table_view.isColumnHidden(column))

    def selectTable(self):
        tableAlias = self.bockTableName.currentText()
        tableName = tableAlias
        for table, alias in self.tableAliases.items():
            if alias == tableAlias:
                tableName = table
                break
        if tableName != self.table.getTableName():
            self.table.setTableName(tableName)
            self.gallery.setTableName(tableName)
            self.table._createTable(tableName)
            self.gallery._createGallery(tableName)
            galleryEnable = True if self.gallery.getColumnWithImages() else False
            if galleryEnable:
                self.gotoGalleryAction.setEnabled(True)
            else:
                self.gotoGalleryAction.setEnabled(False)

            self._rowsCount = self.objecManager.getTableRowCount(tableName)
            self.setWindowTitle("Metadata: " + os.path.basename(self._fileName) + " (%s items)" % self._rowsCount)

    def _tableCellClicked(self, row, column):
        self.enableTableOptions(row, column)

    def enableGalleryOption(self):
        self.zoom.setValue(100)
        self.zoom.setEnabled(True)
        self.zoomLabel.setEnabled(True)
        self.reduceDecimals.setEnabled(False)
        self.increaseDecimals.setEnabled(False)
        self.sortUp.setEnabled(False)
        self.sortDown.setEnabled(False)

    def enableTableOptions(self, row, column):
        isSorteable = self.table.getColumns()[self.table.getActualColumn()].isSorteable()
        self.sortUp.setEnabled(isSorteable)
        self.sortDown.setEnabled(isSorteable)

        item = self.table.cellWidget(row, column)
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

    def _galleryCellClicked(self):
        self.enableGalleryOption()

    def _renderImage(self):
        row = 0
        if self._tableView:
            column = self.table.getColumnWithImages()
            self.table.getColumns()[column].getRenderer().setSize(self.zoom.value())
            self.table.setRowHeight(row, self.zoom.value())
            self.table._loadRows()
        if self._galleryView:
            column = self.gallery.getColumnWithImages()
            self.gallery.getColumns()[column].getRenderer().setSize(self.zoom.value())
            self.gallery.setRowHeight(row, self.zoom.value())
            self.gallery._loadImages()

    def _redIncDecimals(self, flag):
        column = self.table.getActualColumn()
        decimals = self.table.getColumns()[column].getRenderer().getDecimalsNumber()
        if decimals > 1:
            redInc = -1 if flag else 1
            self.table.getColumns()[column].getRenderer().setDecimalNumber(decimals + redInc)
            self.table._loadRows()





