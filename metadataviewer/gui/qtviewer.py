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
import argparse
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
                             QStatusBar, QAbstractItemView)

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

    def InsertRows(self):
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
            if self.columns[i].getRenderer().renderType() == Image:
                self.renderCheckBoxList[i].setChecked(True)

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

    def hiddeColumns(self):
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
        # rows = self._table.page.getRows()
        # currentRow = self._table.scrollBar.value()
        # self._table._addRows(rows, currentRow)
        pass

    def accept(self):
        self.hiddeColumns()
        self.renderColums()
        self.editColums()
        self.close()


class CustomScrollBar(QScrollBar):
    def __init__(self):
        super().__init__()
        self.setSingleStep(1)
        self.dragging = False
        self.start_value = 0
        self.start_pos = None

    def wheelEvent(self, event):
        # Handle the mouse wheel event
        step = 1
        delta = event.angleDelta().y() / 120  # Number of mouse wheel steps
        # If moved up, decreases the value of scroll
        if delta > 0:
            self.setValue(self.value() - step)
        # If it moves down, it increases the scroll value.
        elif delta < 0:
            self.setValue(self.value() + step)

        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.start_value = self.value()
            self.start_pos = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and self.start_pos is not None:
            delta = event.pos() - self.start_pos
            steps = int(delta.y() / self.singleStep())
            new_value = self.start_value + steps
            self.setValue(new_value)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.start_pos = None
            event.accept()


class CustomWidget(QWidget):
    def __init__(self, data):
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
                layout.addWidget(label, alignment=Qt.AlignCenter)
            except Exception as e:
                print("Error loading the imagen:", e)

        self.setLayout(layout)


class TableView(QTableWidget):
    def __init__(self, objectManager):
        super().__init__()
        self.propertiesTableDialog = ColumnPropertiesTable(self, self)
        self.horizontalHeader().sortIndicatorOrder()
        self._pageNumber = 1
        self._pageSize = 30
        self._seekPageRow = 0
        self._oldSeekPageRow = -1
        self._actualRow = 0
        self._actualColumn = 0
        self.oldColumn = None
        self._orderAsc = True
        self.objecManager = objectManager
        self.sortTriggered = False
        self.cellClicked.connect(self.setActualRowColumn)
        self.horizontalHeader().sectionClicked.connect(self.setActualColumn)

    def _createTable(self, tableName):
        # Creating the table
        self._tableName = tableName
        self.objecManager.createTable(self._tableName)
        self._seekPageRow = 0
        self.page = self.objecManager.getPage(self._tableName,
                                              self._pageNumber,
                                              self._pageSize,
                                              self._actualColumn,
                                              self._orderAsc)
        self._rowsCount = self.objecManager.getTableRowCount(self._tableName)

        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.verticalHeader().setVisible(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scrollBar = CustomScrollBar()
        self._createHeader()
        self.propertiesTableDialog.registerColumns(self.page.getTable().getColumns())
        self._fillTable()
        self.setVerticalScrollBar(self.scrollBar)
        self.scrollBar.valueChanged.connect(lambda: self._loadPage())
        self.setCurrentCell(0, 0)

    def setTableName(self, tableName):
        self._tableName = tableName

    def orderByColumn(self, column, order):
        if self._orderAsc != order:
            self._orderAsc = order
            if self.oldColumn is not None:
                self.horizontalHeaderItem(self.oldColumn).setIcon(QIcon(None))

            self.oldColumn = self._actualColumn
            self._actualColumn = column

            self.horizontalHeader().setSortIndicator(column, Qt.AscendingOrder if self._orderAsc else Qt.DescendingOrder)
            reverse = not self._orderAsc
            self.objecManager.sort(self._tableName, column, reverse)
            self.setRowCount(0)
            self.scrollBar.setValue(0)
            self.page = self.objecManager.getPage(self._tableName, 1,  self._pageSize,
                                                  self._actualColumn, self._orderAsc)
            self._fillTable()

        icon = QIcon('resources/up-arrow.png') if self._orderAsc else QIcon(
            'resources/down-arrow.png')
        self.horizontalHeaderItem(column).setIcon(icon)

    def _createHeader(self):
        # Creating the header
        self._columns = self.page.getTable().getColumns()
        self.setColumnCount(len(self._columns))
        for i, column in enumerate(self._columns):
            item = QTableWidgetItem(str(column.getName()))
            item.setTextAlignment(Qt.AlignCenter)
            self.setHorizontalHeaderItem(i, item)

    def _fillTable(self):
        rows = self.page.getRows()
        columns = self.page.getTable().getColumns()
        self._rowsCount = self.objecManager.getTableRowCount(self._tableName)
        self.setColumnCount(len(columns))
        self.setRowCount(self._rowsCount)
        # Set prototype item to improve loading speed
        prototype_item = QTableWidgetItem()
        self.setItemPrototype(prototype_item)

        # Inserting rows into the table
        self._seekPageRow = 0
        self._addRows(rows, 0)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def _calculateVisibleRows(self):
        viewportHeight = self.viewport().height()
        rowHeight = self.rowHeight(0) if self.rowHeight(0) else 30  # row height (minumum size in case of the table is empty)
        visibleRows = viewportHeight // rowHeight
        return visibleRows

    def _addRows(self, rows, activeTableRow):
        columnsCount = len(rows[0].getValues())
        visibleRows = self._calculateVisibleRows()

        row = 0
        rowsLen = len(rows)
        while row + self._seekPageRow < rowsLen and row <= visibleRows:
            color = QColor(245, 245, 220)
            if row % 2 == 0:
                color = QColor(255, 255, 255)
            rowValues = rows[row + self._seekPageRow]
            if rowValues.getValues():
                values = rowValues.getValues()
                for col in range(columnsCount):
                    if self._columns[col].getRenderer().renderType() != Image:
                        item = self._columns[col].getRenderer().render(values[col])
                    else:
                        if self.propertiesTableDialog.renderCheckBoxList[col].isChecked():
                            item = self._columns[col].getRenderer().render(values[col])
                        else:
                           item = values[col]

                    widget = CustomWidget(item)
                    self.setCellWidget(row + activeTableRow, col, widget)
            row += 1

    def _loadPage(self):
        # getting current value
        scrollBar = self.scrollBar
        currentValue = scrollBar.value()
        pageSize = self.page.getPageSize()
        pageNumber = self.page.getPageNumber()

        if currentValue and currentValue % pageSize == 0:
            if self._oldSeekPageRow < currentValue:
                pageNumber += 1
                self._seekPageRow = 0
            elif self._oldSeekPageRow > currentValue:
                pageNumber -= 1
                self._seekPageRow = pageSize

            self.page = self.objecManager.getPage(self._tableName, pageNumber,
                                             pageSize, self._actualColumn,
                                             self._orderAsc)

        else:
            if self._oldSeekPageRow < currentValue:
                self._seekPageRow += 1
            elif self._oldSeekPageRow > currentValue:
                self._seekPageRow -= 1
                if self._seekPageRow < 0:
                    self._seekPageRow = 0

        rows = self.page.getRows()
        self._oldSeekPageRow = currentValue
        self._addRows(rows, currentValue)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def getActualColumn(self):
        return self._actualColumn

    def setActualRowColumn(self, row, column):
        self._actualRow = row
        self._actualColumn = column

    def setActualColumn(self, column):
        self._actualColumn = column


class QTMetadataViewer(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self._fileName = os.path.abspath(args.fileName)
        self.objecManager = ObjectManager(args.fileName)
        self.objecManager.selectDAO()
        self.tableNames = self.objecManager.getTableNames()
        self._pageSize = 30
        self._rowsCount = self.objecManager.getTableRowCount(self.tableNames[0])
        self.setWindowTitle("Metadata: " + os.path.basename(args.fileName) + " (%s items)" % self._rowsCount)
        self.setGeometry(100, 100, 800, 400)
        self._tableView = args.tableview
        self._galleryView = args.galleryview
        if args.tableview:  # Table view
            self.table = TableView(self.objecManager)
        else:  # GalleryView
            self.gallery = None

        self.table._createTable(self.tableNames[0])
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()
        self.setCentralWidget(self.table)

    def resizeEvent(self, event):
        self.table._loadPage()

    def _createStatusBar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(30)
        # closeButton = QPushButton('Close')
        # closeButton.setIcon(QIcon("../resources/fa-close.png"))
        # self.statusbar.addPermanentWidget(closeButton)

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
        self.gotoGalleryAction.setEnabled(True)
        self.gotoTableAction.setEnabled(False)
        self.table.setVisible(True)
        self.bockTableName.setEnabled(True)

    def _loadGalleryView(self):
        self.gotoTableAction.setEnabled(True)
        self.gotoGalleryAction.setEnabled(False)
        self.table.setVisible(False)
        self.bockTableName.setEnabled(False)

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
        if self._tableView:
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
        self.table.setRowCount(0)
        tableName = self.bockTableName.currentText()
        self.table.setActualRowColumn(0, 0)
        page = self.objecManager.getPage(tableName, 1, self._pageSize, 1, True)
        if page:
            self.table._createTable(tableName)
            self._rowsCount = self.objecManager.getTableRowCount(tableName)
            self.setWindowTitle("Metadata: " + os.path.basename(self._fileName) + " (%s items)" % self._rowsCount)


