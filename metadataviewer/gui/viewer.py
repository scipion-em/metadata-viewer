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

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QColor, QPixmap, QImage
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu,
                             QAction, QDialog, QVBoxLayout, QWidget,
                             QDialogButtonBox, QTableWidget, QCheckBox,
                             QHBoxLayout, QTableWidgetItem, QLabel,
                             QComboBox, QPushButton, QStatusBar, QScrollBar,
                             QAbstractItemView)

from metadataviewer.model.object_manager import ObjectManager


class ColumnPropertiesTable(QDialog):
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
            if self.columns[i].getName() in tableHeaderList:
                self.visibleCheckBoxList[i].setChecked(True)
            else:
               self.visibleCheckBoxList[i].setChecked(False)

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
        pass

    def accept(self):
        self.hiddeColumns()
        self.renderColums()
        self.editColums()
        self.close()


class CustomScrollBar(QScrollBar):
    def __init__(self, parent=None):
        super().__init__(parent)
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


class MetadataTable(QMainWindow):
    def __init__(self, fileName):
        super().__init__()
        self._fileName = os.path.abspath(fileName)
        self.objecManager = ObjectManager(fileName)
        self.objecManager.selectDAO()
        self.tableNames = self.objecManager.getTableNames()
        self._tableName = self.tableNames[0]
        self.objecManager.createTable(self._tableName)
        self._pageNumber = 1
        self._pageSize = 10
        self._actualColumn = None
        self._orderAsc = True
        self.page = self.objecManager.getPage(self.tableNames[0], self._pageNumber,
                                              self._pageSize,
                                              self._actualColumn,  self._orderAsc)
        self._rowsCount = self.objecManager.getTableRowCount(self.tableNames[0])
        self.setWindowTitle("Metadata: " + os.path.basename(fileName) + " (%s items)" % self._rowsCount)
        self.setGeometry(100, 100, 700, 300)
        self.table = QTableWidget()
        self.propertiesTableDialog = ColumnPropertiesTable(self, self.table)
        self.table.horizontalHeader().sortIndicatorOrder()
        self._createActions()
        self._createMenuBar()
        self._createToolBars(1, 100)
        self._createStatusBar()
        self._createTable()

    def _createTable(self):
        # Creating the table
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._createHeader()
        self._fillTable()
        self.propertiesTableDialog.registerColumns(self.page.getTable().getColumns())
        self.table.horizontalHeader().sectionClicked.connect(self.orderByColumn)

    def orderByColumn(self, column):
        # Alternate ascending and descending order
        oldColumn = self._actualColumn
        if column == self._actualColumn:
            self._orderAsc = not self._orderAsc
        else:
            oldColumn = self._actualColumn
            self._actualColumn = column
            self._orderAsc = True

        self.table.horizontalHeader().setSortIndicator(column, Qt.AscendingOrder if self._orderAsc else Qt.DescendingOrder)
        if oldColumn is not None:
            self.table.horizontalHeaderItem(oldColumn).setIcon(QIcon(None))

        icon = QIcon('resources/up-arrow.png') if self._orderAsc else QIcon(
            'resources/down-arrow.png')
        self.table.horizontalHeaderItem(column).setIcon(icon)
        self.objecManager.sort(self._tableName, column, self._orderAsc)
        self.table.setRowCount(0)
        self.scrollBar.setValue(0)
        self.page = self.objecManager.getPage(self._tableName, 1,  self._pageSize,
                                              self._actualColumn,  self._orderAsc)
        self._fillTable()

    def _createHeader(self):
        # Creating the header
        self._columns = self.page.getTable().getColumns()
        self.table.setColumnCount(len(self._columns))
        for i, column in enumerate(self._columns):
            item = QTableWidgetItem(str(column.getName()))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setHorizontalHeaderItem(i, item)

    def _fillTable(self):
        rows = self.page.getRows()
        columns = self.page.getTable().getColumns()
        self.table.setColumnCount(len(columns))
        self.table.setRowCount(self._rowsCount)
        # Set prototype item to improve loading speed
        prototype_item = QTableWidgetItem()
        self.table.setItemPrototype(prototype_item)

        # Inserting rows into the table
        self._addRows(rows, 0)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self._rowsCount = self.objecManager.getTableRowCount(self.bockTableName.currentText())
        self.setCentralWidget(self.table)
        self.scrollBar = CustomScrollBar(self.table)
        self.table.setVerticalScrollBar(self.scrollBar)
        self.scrollBar.valueChanged.connect(lambda: self._loadRows())

    def _addRows(self, rows, activeRow):
        columnsCount = len(rows[0].getValues())
        for row, rowValues in enumerate(rows):
            color = QColor(245, 245, 220)
            if row % 2 == 0:
                color = QColor(255, 255, 255)
            if rowValues.getValues():
                values = rowValues.getValues()
                for col in range(columnsCount):
                    item = self._columns[col].getRenderer().render(values[col])
                    widget = CustomWidget(item)
                    # widget.setBackground()
                    self.table.setCellWidget(activeRow + row, col, widget)

    def mouseWheelEvent(self, event):
        # Handle the mouse wheel event
        step = 1
        delta = event.angleDelta().y() / 120  # Number of mouse wheel steps

        # If moved up, decreases the value of scroll
        if delta > 0:
            self.scrollBar.setValue(self.scrollBar.value() - step)
        # If it moves down, it increases the scroll value.
        elif delta < 0:
            self.scrollBar.setValue(self.scrollBar.value() + step)

        event.accept()

    def _loadRows(self):
        # getting current value
        scrollBar = self.scrollBar
        currentValue = scrollBar.value()
        pageSize = self.page.getPageSize()

        if currentValue % pageSize == 0:
            self.page.setPageNumber(int(currentValue / pageSize) + 1)  # next or previous page
            pageNumber = self.page.getPageNumber()
            page = self.objecManager.getPage(self._tableName, pageNumber,
                                             pageSize, self._actualColumn,
                                             self._orderAsc)
            rows = page.getRows()
            if rows:
                self._addRows(rows, currentValue)
                self.table.resizeColumnsToContents()
                self.table.resizeRowsToContents()

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
        self.propertiesTableAction = QAction("Columns...", self)
        self.propertiesTableAction.triggered.connect(self.propertiesTableDialog.openTableDialog)
        self.propertiesTableAction.setShortcut(QKeySequence("Ctrl+C"))
        self.propertiesTableAction.setIcon(QIcon("resources/table.png"))


        # Toolbar action
        self.goto_table_action = QAction("Go to TABLE view", self)
        self.goto_table_action.setIcon(QIcon("resources/table-view.png"))
        self.goto_table_action.setEnabled(False)
        self.goto_table_action.triggered.connect(self._loadTableView)

        self.goto_gallery_action = QAction("Go to GALLERY view", self)
        self.goto_gallery_action.setIcon(QIcon("resources/gallery.png"))
        self.goto_gallery_action.triggered.connect(self._loadGalleryView)

    def _loadTableView(self):
        self.goto_table_action.setEnabled(False)
        self.goto_gallery_action.setEnabled(True)

    def _loadGalleryView(self):
        self.goto_gallery_action.setEnabled(False)
        self.goto_table_action.setEnabled(True)


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
        displayMenu.addAction(self.propertiesTableAction)

        # Tools menu
        toolsMenu = QMenu("&Tools", self)
        menu_bar.addMenu(toolsMenu)

        # Help menu
        helpMenu = QMenu("&Help", self)
        menu_bar.addMenu(helpMenu)

        self.setMenuBar(menu_bar)

    def _createToolBars(self, pageNumber=1, pageSize=100):
        # Using a title
        toolBar = self.addToolBar("")
        toolBar.addAction(self.goto_table_action)
        toolBar.addAction(self.goto_gallery_action)

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
        toolBar.addWidget(self.bockTableName)

    def toggleColumn(self, table_view, column):
        self.table.setColumnHidden(column,
                                   not table_view.isColumnHidden(column))

    def selectTable(self):
        self.table.setRowCount(0)
        self._tableName = self.bockTableName.currentText()
        self._rowsCount = self.objecManager.getTableRowCount(self._tableName)
        self._actualColumn = 1
        self._orderAsc = True
        self.page = self.objecManager.getPage(self._tableName,
                                              self._pageNumber, self._pageSize,
                                              self._actualColumn,
                                              self._orderAsc)
        if self.page:
            self._createHeader()
            self._fillTable()
            self.propertiesTableDialog.registerColumns(self.page.getTable().getColumns())
            self._rowsCount = self.objecManager.getTableRowCount(self._tableName)
            self.setWindowTitle("Metadata: " + os.path.basename(fileName) + " (%s items)" % self._rowsCount)


def main(fileName):
    app = QApplication(sys.argv)
    window = MetadataTable(fileName)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    fileName = sys.argv[1]
    main(fileName)
