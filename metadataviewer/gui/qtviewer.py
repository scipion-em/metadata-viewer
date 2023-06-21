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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QColor, QPixmap
from PyQt5.QtWidgets import (QMainWindow, QMenuBar, QMenu, QLabel,
                             QAction, QDialog, QVBoxLayout, QWidget, QScrollBar,
                             QDialogButtonBox, QTableWidget, QCheckBox,
                             QHBoxLayout, QTableWidgetItem, QComboBox,
                             QStatusBar, QAbstractItemView, QSizePolicy)

from metadataviewer.model.object_manager import ObjectManager


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
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Label"))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("Visible"))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem("Render"))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem("Edit"))
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

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        if isinstance(data, int) or isinstance(data, float) or isinstance(data, str):
            label = QLabel(str(data))
            layout.addWidget(label, alignment=Qt.AlignCenter)
        else:  # Assuming the data is a file path to an image
            try:
                im = data.convert("RGBA")
                data = im.tobytes("raw", "RGBA")
                qimage = QtGui.QImage(data, im.size[0], im.size[1],
                                      QtGui.QImage.Format_RGBA8888)

                pixmap = QPixmap.fromImage(qimage)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter)
                layout.addWidget(label)

                if addText:
                    textLabel = QLabel(text)
                    textLabel.setAlignment(Qt.AlignTop)
                    layout.addWidget(textLabel)
            except Exception as e:
                print("Error loading the imagen:", e)

        self.setLayout(layout)


class TableView(QTableWidget):
    """Class to represent the metadata in table mode"""
    def __init__(self, objectManager):
        super().__init__()
        self.propertiesTableDialog = ColumnPropertiesTable(self, self)
        self._pageNumber = 1
        self._pageSize = 100
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
        self.scrollBar = CustomScrollBar()
        self._createHeader()
        columns = self.objecManager.getTable(self._tableName).getColumns()
        self.propertiesTableDialog.registerColumns(columns)
        self.propertiesTableDialog.setLoadFirstTime(True)
        self.propertiesTableDialog.InsertRows()
        self._fillTable()
        self.setVerticalScrollBar(self.scrollBar)
        self.scrollBar.valueChanged.connect(lambda: self._loadRows())
        self.setCurrentCell(0, 0)

    def setTableName(self, tableName):
        self._tableName = tableName

    def orderByColumn(self, column, order):

        self._orderAsc = order
        if self.oldColumn is not None:
            self.horizontalHeaderItem(self.oldColumn).setIcon(QIcon(None))

        self.oldColumn = self._actualColumn
        self._actualColumn = column

        self.horizontalHeader().setSortIndicator(column, Qt.AscendingOrder if self._orderAsc else Qt.DescendingOrder)
        self.objecManager.sort(self._tableName, column, self._orderAsc)
        self.clearContents()
        self.scrollBar.setValue(0)
        self._loadRows()

        icon = QIcon('resources/up-arrow.png') if self._orderAsc else QIcon('resources/down-arrow.png')
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

    def _calculateVisibleRows(self):
        viewportHeight = self.viewport().height()
        rowHeight = self.rowHeight(0) if self.rowHeight(0) else 30  # row height (minumum size in case of the table is empty)
        visibleRows = viewportHeight // rowHeight + 1
        return visibleRows

    def _addRows(self, rows, currentValue):
        columnsCount = len(rows[0].getValues())
        for i in range(len(rows)):
            rowValues = rows[i]
            if rowValues.getValues():
                values = rowValues.getValues()
                for col in range(columnsCount):
                    if self._columns[col].getRenderer().renderType() != Image:
                        item = self._columns[col].getRenderer().render(
                            values[col])
                    else:
                        if self.propertiesTableDialog.renderCheckBoxList[col].isChecked():
                            item = self._columns[col].getRenderer().render(values[col])
                        else:
                            item = values[col]

                    widget = CustomWidget(item)
                    self.setCellWidget(i + currentValue, col, widget)
                    self.resizeColumnToContents(col)
                self.resizeRowToContents(i + currentValue)

    def _loadRows(self):
        currentValue = self.scrollBar.value()
        visibleRows = self._calculateVisibleRows()
        rows = self.objecManager.getRows(self._tableName, currentValue,
                                         visibleRows)
        self._addRows(rows, currentValue)

    def getActualColumn(self):
        return self._actualColumn

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
        self._tableName = self.objecManager.getTable(self.tableNames[0]).getName()
        self._columns = self.objecManager.getTable(self._tableName).getColumns()
        self._columnWithImages = self.getColumnWithImages()
        self.setGeometry(0, 0, 600, 600)

    def setTableName(self, tableName):
        self._tableName = tableName

    def _createGallery(self, tableName):
        # Creating the gallery
        self._tableName = tableName
        self.setColumnCount(10)
        self._tableSize = self.objecManager.getTableRowCount(self._tableName)
        self._columnsCount = self._calculateVisibleColumns()
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
        self.scrollBar = CustomScrollBar()
        self._loadImages()
        self.setVerticalScrollBar(self.scrollBar)
        self.scrollBar.valueChanged.connect(self._loadImages)
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
        self._columnWithImages = self.getColumnWithImages()
        if self._columnWithImages:
            for row in range(visibleRows):
                for col in range(self._columnsCount):
                    if seekFirstImage + countImages == self._tableSize:
                        break
                    values = rows[countImages]
                    item = self._columns[self._columnWithImages].getRenderer().render(values.getValues()[self._columnWithImages])
                    widget = CustomWidget(item, True, str(seekFirstImage + countImages + 1))
                    self.setCellWidget(currentValue + row, col, widget)
                    self.resizeColumnToContents(col)
                    countImages += 1
                self.resizeRowToContents(currentValue + row)
                if seekFirstImage + countImages == self._tableSize:
                    break

    def _loadImages(self):
        currentValue = self.scrollBar.value()
        visibleRows = self._calculateVisibleRows()
        seekFirstImage = currentValue * self._columnsCount
        seekLastImage = visibleRows * self._columnsCount
        rows = self.objecManager.getRows(self._tableName, seekFirstImage, seekLastImage)
        self._addImages(rows, currentValue, visibleRows, seekFirstImage)

    def resizeEvent(self, event):
        if self._triggeredResize:
            super().resizeEvent(event)
            # Initializating with a large number of columns. It is useful for
            # the method that calculates the visible columns
            self.setColumnCount(20)
            self._columnsCount = self._calculateVisibleColumns() - 1
            # Verifying that there is at least one column
            if self._columnsCount < 1:
                self._columnsCount = 1
            self.setColumnCount(self._columnsCount)
            self._rowsCount = int(self._rowsCount / self._columnsCount)
            # Verifying that there is at least one row
            if self._rowsCount < 1:
                self._rowsCount = 1
            self._loadImages()
        self._triggeredResize = True


class QTMetadataViewer(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self._fileName = os.path.abspath(args.fileName)
        self.objecManager = ObjectManager(args.fileName)
        self.objecManager.selectDAO()
        self.tableNames = self.objecManager.getTableNames()
        self._pageSize = 100
        self._triggeredResize = False
        self._rowsCount = self.objecManager.getTableRowCount(self.tableNames[0])
        self.setWindowTitle("Metadata: " + os.path.basename(args.fileName) + " (%s items)" % self._rowsCount)
        self.setGeometry(100, 100, 800, 400)
        self._tableView = args.tableview
        self._galleryView = args.galleryview

        # Table view
        self.table = TableView(self.objecManager)
        self.table._createTable(self.tableNames[0])
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
        self.newAction.setIcon(QIcon("resources/folder.png"))

        self.exitAction = QAction(self)
        self.exitAction.setText("E&xit")
        self.exitAction.setShortcut(QKeySequence("Ctrl+X"))
        self.exitAction.setIcon(QIcon("resources/exit.png"))
        self.exitAction.triggered.connect(sys.exit)

        # Display actions
        self.table.propertiesTableAction = QAction("Columns...", self)
        self.table.propertiesTableAction.triggered.connect(self.table.propertiesTableDialog.openTableDialog)
        self.table.propertiesTableAction.setShortcut(QKeySequence("Ctrl+C"))
        self.table.propertiesTableAction.setIcon(QIcon("resources/table.png"))
        if self._galleryView:
            self.table.propertiesTableAction.setEnabled(False)

        # Toolbar action
        self.gotoTableAction = QAction("Go to TABLE view", self)
        self.gotoTableAction.setIcon(QIcon("resources/table-view.png"))
        self.gotoTableAction.setEnabled(False)
        self.gotoTableAction.triggered.connect(self._loadTableView)

        self.gotoGalleryAction = QAction("Go to GALLERY view", self)
        self.gotoGalleryAction.setIcon(QIcon("resources/gallery.png"))
        self.gotoGalleryAction.triggered.connect(self._loadGalleryView)

        # Columns  Toolbar action
        self.reduceDecimals = QAction("Reduce decimals", self)
        self.reduceDecimals.setIcon(QIcon("resources/reducedecimals.png"))
        self.reduceDecimals.setEnabled(False)

        self.increaseDecimals = QAction("Increase decimals", self)
        self.increaseDecimals.setIcon(QIcon("resources/increasedecimals.png"))
        self.increaseDecimals.setEnabled(False)

        self.sortUp = QAction("Sort ascending", self)
        self.sortUp.setIcon(QIcon("resources/up-arrow.png"))
        self.sortUp.triggered.connect(lambda : self.table.orderByColumn(self.table.getActualColumn(), True))

        self.sortDown = QAction("Sort descending", self)
        self.sortDown.setIcon(QIcon("resources/down-arrow.png"))
        self.sortDown.triggered.connect(lambda: self.table.orderByColumn(self.table.getActualColumn(), False))

    def _loadTableView(self):
        galleryEnable = True if self.gallery.getColumnWithImages() else False
        self.gotoGalleryAction.setEnabled(galleryEnable)
        self.gotoTableAction.setEnabled(False)
        widget = self.takeCentralWidget()
        if widget:
            self.gallery = widget
        self.table.setVisible(True)
        self.setCentralWidget(self.table)
        self.bockTableName.setEnabled(True)
        self._galleryView = False
        self._tableView = True

    def _loadGalleryView(self):
        self.gotoTableAction.setEnabled(True)
        self.gotoGalleryAction.setEnabled(False)
        widget = self.takeCentralWidget()
        if widget:
            self.table = widget
        tableName = self.bockTableName.currentText()
        self.gallery.setTableName(tableName)
        self.gallery.setVisible(True)
        self.setCentralWidget(self.gallery)
        self._galleryView = True
        self._tableView = False

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
        self.blockLabel = QLabel('Block')
        icon = QIcon('resources/sections.png')
        self.blockLabel.setPixmap(icon.pixmap(16, 16))
        self.blockLabel.setToolTip('Blocks')
        toolBar.addWidget(self.blockLabel)
        self.bockTableName = QComboBox()
        self.bockTableName.setFixedWidth(200)
        for tableName in self.tableNames:
            self.bockTableName.addItem(tableName)
            # Connect signals to the methods.
        self.bockTableName.activated.connect(self.selectTable)
        self.bockTableName.setToolTip('Blocks')
        toolBar.addWidget(self.bockTableName)

        # Columns tool bar
        columnsToolBar2 = self.addToolBar("")
        columnsToolBar2.addAction(self.sortUp)
        columnsToolBar2.addAction(self.sortDown)
        columnsToolBar2.addAction(self.reduceDecimals)
        columnsToolBar2.addAction(self.increaseDecimals)
        self.zoom = QComboBox()
        self.zoom.setToolTip('Zoom')
        self.zoom.setFixedWidth(70)
        self.zoom.setEnabled(False)
        zoomValues = ['50%', '75%', '90%', '100%', '125%', '150%', '200%']
        for zoomValue in zoomValues:
            self.zoom.addItem(zoomValue)
        self.zoom.setCurrentIndex(3)
        columnsToolBar2.addWidget(self.zoom)

    def toggleColumn(self, table_view, column):
        self.table.setColumnHidden(column,
                                   not table_view.isColumnHidden(column))

    def selectTable(self):
        tableName = self.bockTableName.currentText()
        self.table._createTable(tableName)
        self.gallery.setTableName(tableName)
        galleryEnable = True if self.gallery.getColumnWithImages() else False
        if galleryEnable:
            self.gallery._createGallery(tableName)
            self.gotoGalleryAction.setEnabled(True)
        else:
            self.gotoGalleryAction.setEnabled(False)

        self._rowsCount = self.objecManager.getTableRowCount(tableName)
        self.setWindowTitle("Metadata: " + os.path.basename(self._fileName) + " (%s items)" % self._rowsCount)


