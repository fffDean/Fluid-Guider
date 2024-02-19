from PySide6.QtWidgets import QToolBar, QFileDialog
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QAction
import os

rectMakeMode = 0
lineMakeMode = 1
holeMakeMode = 2


class Toolbar(QToolBar):
    def __init__(self, mainwidget, parent=None):
        super().__init__(parent)
        self.mainwidget = mainwidget
        self.initUI()

    def initUI(self):
        self.setIconSize(QSize(64, 64))

        self.addMyItems()

    def addMyItems(self):
        rect = QAction(QIcon('../graphic/add_rect.png'), 'add base_shape rect', self.mainwidget)
        line = QAction(QIcon('../graphic/make_line.png'), 'add line', self.mainwidget)
        hole = QAction(QIcon('../graphic/add_hole.png'), 'add hole', self.mainwidget)
        voluntary_default = QAction(QIcon('../graphic/voluntary.png'), 'voluntary_default', self.mainwidget)
        voluntary_static = QAction(QIcon('../graphic/voluntary.png'), 'voluntary_static', self.mainwidget)
        to_3DModel = QAction(QIcon('../graphic/to_3Dmodel.png'), 'to 3DModel', self.mainwidget)
        openFile = QAction(QIcon('../graphic/open.png'), 'open file', self.mainwidget)
        saveFile = QAction(QIcon('../graphic/save.png'), 'save file', self.mainwidget)
        self.addAction(rect)
        self.addAction(line)
        self.addAction(hole)
        self.addAction(voluntary_default)
        self.addAction(voluntary_static)
        self.addAction(to_3DModel)
        self.addAction(openFile)
        self.addAction(saveFile)
        rect.triggered.connect(self.add_rect)
        line.triggered.connect(self.add_line)
        hole.triggered.connect(self.add_hole)
        voluntary_default.triggered.connect(self.voluntary_default)
        voluntary_static.triggered.connect(self.voluntary_static)
        to_3DModel.triggered.connect(self.to_3DModel)
        openFile.triggered.connect(self.open_file)
        saveFile.triggered.connect(self.save_file)

    def add_rect(self):
        self.mainwidget.centralWidget().view.setMouseMode(rectMakeMode)

    def add_line(self):
        self.mainwidget.centralWidget().view.setMouseMode(lineMakeMode)

    def add_hole(self):
        self.mainwidget.centralWidget().view.setMouseMode(holeMakeMode)

    def voluntary_default(self):
        self.mainwidget.voluntary_default()

    def voluntary_static(self):
        self.mainwidget.voluntary_static()

    def to_3DModel(self):
        self.mainwidget.on3DModelSave()

    def open_file(self):
        self.mainwidget.onOpenFile()

    def save_file(self):
        self.mainwidget.onFileSave()
