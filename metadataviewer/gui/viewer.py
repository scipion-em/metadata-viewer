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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableView, QMenuBar,
                             QMenu, QAction, QDialog, QVBoxLayout, QWidget,
                             QDialogButtonBox, QTableWidget, QCheckBox,
                             QHBoxLayout, QTableWidgetItem, QSpinBox, QLabel,
                             QComboBox, QPushButton, QStatusBar,
                             QAbstractItemView, QScrollArea, QScrollBar)

from metadataviewer.model.object_manager import ObjectManager


class ColumnPropertiesTable(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
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

    def InsertTable(self):
        for i in range(self.numRow):
            visibleCheckbox = self._createCellWidget(self.visibleCheckBoxList[i])
            renderCheckbox = self._createCellWidget(self.renderCheckBoxList[i])
            editCheckbox = self._createCellWidget(self.editCheckBoxList[i])
            self.tableWidget.setCellWidget(i, 0, QLabel('_' + self.columns[i].getName()))
            self.tableWidget.setCellWidget(i, 1, visibleCheckbox)
            self.tableWidget.setCellWidget(i, 2, renderCheckbox)
            self.tableWidget.setCellWidget(i, 3, editCheckbox)
        self.tableWidget.move(0, 0)
        self.tableWidget.resizeColumnsToContents()

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
            self.visibleCheckBoxList.append(ckbox)
            self.renderCheckBoxList.append(ckbox1)
            self.editCheckBoxList.append(ckbox2)
        self.InsertTable()

    def openTableDialog(self):
        self.show()


class MetadataTable(QMainWindow):
    def __init__(self, fileName):
        super().__init__()
        self._fileName = os.path.abspath(fileName)
        self.objecManager = ObjectManager(fileName)
        self.tableNames = self.objecManager.getTableNames()
        self.objecManager.createTable(self.tableNames[0])
        self.page = self.objecManager.getPage(self.tableNames[0], 1, 100)
        self._rowsCount = self.objecManager.getTableRowCount(self.tableNames[0])
        self.setWindowTitle("Metadata: " + os.path.basename(fileName) + " (%s items)" % self._rowsCount)
        self.setGeometry(100, 100, 700, 300)
        self.propertiesTableDialog = ColumnPropertiesTable(self)
        self.propertiesTableDialog.registerColumns(self.page.getTable().getColumns())
        self._createActions()
        self._createMenuBar()
        self._createToolBars(1, 100)
        self._createStatusBar()
        self._fillTable()

    def _fillTable(self):
        mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(mainWidget)

        # Creating the table
        self.table = QTableWidget()
        columns = self.page.getTable().getColumns()
        rows = self.page.getRows()
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Creating the header
        for i, column in enumerate(columns):
            self.table.setHorizontalHeaderItem(i, QTableWidgetItem(str(column.getName())))

        # Inserting rows into the table
        for row, rowValues in enumerate(rows):
            if rowValues:
                for col in range(len(columns)):
                    item = QTableWidgetItem(str(rowValues[col]))
                    self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

        # Calculating the minimum scrolling height(vertical)
        rowHeight = self.table.rowHeight(0)  # row height
        self._rowsCount = self.objecManager.getTableRowCount(self.bockTableName.currentText())
        minHeight = rowHeight * self._rowsCount  # height of the scroll

        # Calculating the minimum scrolling width (horizontal)
        minWidth = 0
        for i in range(len(columns)):
            minWidth += self.table.columnWidth(i)

        mainWidget.setMinimumHeight(minHeight)
        mainWidget.setMinimumWidth(minWidth)

        # Setting the height of main widget
        self.mainLayout.addWidget(self.table)

        # Creating the scroll area
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        # Setting the main widget as content of scrolling
        self.scrollArea.setWidget(mainWidget)
        # adding the scroll area to the main window
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.verticalScrollBar().valueChanged.connect(lambda: self._loadRows())

    def _loadRows(self):
        # getting current value
        scrollBar = self.table.verticalScrollBar()
        maxValue = scrollBar.maximum()
        currentValue = self.scrollArea.verticalScrollBar().value()
        activeRow = int(currentValue/self.table.rowHeight(0))

        if activeRow % 80 == 0:
            start = self.table.rowCount()
            end = start + 50
            self.table.setRowCount(activeRow + 100)
            self.page = self.objecManager.getRows(activeRow + 100)
            rows = self.page.getRows()
            columns = self.page.getTable().getColumns()
            for row, rowValues in enumerate(rows):
                if rowValues:
                    for col in range(len(columns)):
                        item = QTableWidgetItem(str(rowValues[col]))
                        self.table.setItem(row, col, item)

    def _createStatusBar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.setFixedHeight(30)
        closeButton = QPushButton('Close')
        closeButton.setIcon(QIcon("../resources/fa-close.png"))
        self.statusbar.addPermanentWidget(closeButton)

    def _createActions(self):
        # File actions
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        self.newAction.setIcon(QIcon("../resources/fa-list-ul.png"))
        # Edit actions
        self.propertiesTableAction = QAction("Columns...", self)
        self.propertiesTableAction.triggered.connect(self.propertiesTableDialog.openTableDialog)

        self.goto_gallery_action = QAction("Go to gallery view", self)
        self.goto_gallery_action.setIcon(QIcon("../resources/fa-list-ul.png"))

    def _createMenuBar(self):
        # Creating the menu
        menu_bar = QMenuBar(self)
        fileMenu = QMenu("&File", self)
        menu_bar.addMenu(fileMenu)
        displayMenu = QMenu("Display", self)
        menu_bar.addMenu(displayMenu)
        toolsMenu = QMenu("&Tools", self)
        menu_bar.addMenu(toolsMenu)
        helpMenu = QMenu("&Help", self)
        menu_bar.addMenu(helpMenu)

        displayMenu.addAction(self.propertiesTableAction)

        self.setMenuBar(menu_bar)

    def _createToolBars(self, pageNumber=1, pageSize=100):
        # Using a title
        toolBar = self.addToolBar("")
        # toolBar.addAction(self.goto_gallery_action)

        # Adding a combobox with the table names
        self.blockLabel = QLabel('\tBlock')
        toolBar.addWidget(self.blockLabel)
        self.bockTableName = QComboBox()
        self.bockTableName.setFixedWidth(170)
        for tableName in self.tableNames:
            self.bockTableName.addItem(tableName)
            # Connect signals to the methods.
        self.bockTableName.activated.connect(self.selectTable)
        toolBar.addWidget(self.bockTableName)

        # # Adding a label to the pageNumber toolbar
        # self.pageNumberLabel = QLabel('\tPage')
        # toolBar.addWidget(self.pageNumberLabel)
        # # Adding a SpinBox to the pageNumber toolbar
        # self.pageNumberSpinBox = QSpinBox()
        # self.pageNumberSpinBox.setFocusPolicy(Qt.NoFocus)
        # self.pageNumberSpinBox.setValue(pageNumber)
        # self.pageNumberSpinBox.setFixedWidth(70)
        # self.pageNumberSpinBox.setAlignment(Qt.AlignRight)
        # self.pageNumberSpinBox.valueChanged.connect(self.changePage)
        # toolBar.addWidget(self.pageNumberSpinBox)
        #
        # # Adding a label to the pageSize toolbar
        # self.pageSizeLabel = QLabel('\tRows')
        # toolBar.addWidget(self.pageSizeLabel)
        # # Adding a SpinBox to the pageNumber toolbar
        # self.pageSizeSpinBox = QSpinBox()
        # self.pageSizeSpinBox.setMaximum(4000000)
        # self.pageSizeSpinBox.setFocusPolicy(Qt.NoFocus)
        # self.pageSizeSpinBox.setValue(pageSize)
        # self.pageSizeSpinBox.setFixedWidth(70)
        # self.pageSizeSpinBox.setAlignment(Qt.AlignRight)
        # self.pageSizeSpinBox.valueChanged.connect(self.changeNumberOfRows)
        # toolBar.addWidget(self.pageSizeSpinBox)

    def toggleColumn(self, table_view, column):
        self.table.setColumnHidden(column,
                                   not table_view.isColumnHidden(column))

    def selectTable(self):
        self.page = self.objecManager.getTable(self.bockTableName.currentText())
        if self.page:
            self._fillTable()
            self.propertiesTableDialog.registerColumns(self.page.getTable().getColumns())
            self._rowsCount = self.objecManager.getTableRowCount(self.bockTableName.currentText())
            self.setWindowTitle("Metadata: " + os.path.basename(fileName) + " (%s items)" % self._rowsCount)

    def changePage(self):
        self.page = self.objecManager.getNextPage(self.pageNumberSpinBox.value())
        self._fillTable()

    def changeNumberOfRows(self):
        self.page = self.objecManager.getRows(self.pageSizeSpinBox.value())
        self._fillTable()


def main(fileName):
    app = QApplication(sys.argv)
    window = MetadataTable(fileName)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    fileName = sys.argv[1]
    main(fileName)
