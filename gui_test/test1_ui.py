import os
import sys

from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from gui_test.scene_setting import GraphicScene, GraphicView
from gui_test.node_setting import GraphicNode
from gui_test.edge_edge import Edge
from gui_test.scene_scene import Scene
from gui_test.scene_xcv import ctrl_xcv

# from gui_equation.equation import EquationWindow
from gui_real.real_ui import RealMainWindow


class MainWindow(QWidget):
    realMainWindowList = []
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None


        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scene = Scene(self) #GraphicScene()的托管
        self.view = GraphicView(self.scene, self)
        # 有view就要有scene
        self.view.setScene(self.scene.grScene)
        # 设置view可以进行鼠标的拖拽选择
        self.view.setDragMode(self.view.DragMode.RubberBandDrag)
        self.layout.addWidget(self.view)

        self.ctrl_xcv = ctrl_xcv(self)

        #self.setGeometry(200, 200, 800, 600)
        #self.setMinimumHeight(500)
        #self.setMinimumWidth(500)
        #self.setCentralWidget(self.view)
        self.setWindowTitle("Graphics Demo")
        self.scene.HoleWindow_func['changeTitle'] = self.changeTitle

    def getUserFriendlyFilename(self) -> str:
        """Get user friendly filename. Used in the window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if not self.isSaved() else "")

    def isFilenameSet(self) -> bool:
        return self.filename is not None

    def isSaved(self) -> bool:
        return self.scene.has_been_saved

    def closeEvent(self, event):
        if self.maybesave():
            event.accept()
        else:
            event.ignore()

    def maybesave(self):
        if self.isSaved():
            return True
        res = QMessageBox.warning(self, 'you forgot to save your graph', 'you forgot to save your graph',  QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if res == QMessageBox.StandardButton.Save:
            return self.onFileSave()
        elif res == QMessageBox.StandardButton.Discard:
            return True
        elif res == QMessageBox.StandardButton.Cancel:
            return False

    def changeTitle(self):
        title = 'node editor ---- '

        if self.filename == None:
            title += 'New'
        else:
            title = os.path.basename(self.filename)
        if not self.scene.has_been_saved:
            title += '*'

        self.setWindowTitle(title)

    def onFileSave(self):
        if self.filename is None:
            return self.onFileSaveAs()
        else:
            self.scene.save_graph(self.filename)
            self.scene.has_been_saved = True
            self.changeTitle()
        # self.centralWidget().scene.save_graph('graph.json.txt')
        return self.filename

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'save graph to file')
        # 加了下面两行不报错
        if fname == '':
            return False
        self.filename = fname
        self.onFileSave()
        return self.filename

    def onFileEquationView(self):
        pass
        # equationView = EquationWindow()
        # MainWindow.realMainWindowList.append(equationView)

    def onFileToRealMap(self):
        data = self.scene.item_to_string()
        realMainWindow = RealMainWindow()
        realMainWindow.raise_()
        realMainWindow.activateWindow()
        MainWindow.realMainWindowList.append(realMainWindow)
        realMainWindow.loading(data)
        #realMainWindow.move(self.x() + 40, self.y() + 40)
        #realMainWindow.exec()


class HoleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filename = None

        self.initUI()

    def initUI(self):
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(self.createact('&New', 'Ctrl+N', 'Creat new graph', self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createact('&Open', 'Ctrl+O', 'Open file', self.onFileOpen))
        fileMenu.addAction(self.createact('&Save', 'Ctrl+S', 'Save file', self.onFileSave))
        fileMenu.addAction(self.createact('Save &As...', 'Ctrl+Shift+S', 'Save file as...', self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createact('E&xit', 'Ctrl+Q', 'Exit application', self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createact('&Undo', 'Ctrl+Z', 'Undo last operation', self.onEditUndo))
        editMenu.addAction(self.createact('&Redo', 'Ctrl+Shift+Z', 'Redo last operation', self.onEditRedo))
        editMenu.addSeparator()
        editMenu.addAction(self.createact('&Delete', 'Del', 'Delete selected item', self.onEditDelete))
        editMenu.addAction(self.createact('&Paste', 'Ctrl+V', 'Paste what you selected', self.onEditPaste))
        editMenu.addAction(self.createact('&Copy', 'Ctrl+C', 'Copy what you selected', self.onEditCopy))
        editMenu.addAction(self.createact('&Cut', 'Ctrl+X', 'Cut what you selected', self.onEditCut))

        node_editor = MainWindow(self)
        self.setCentralWidget(node_editor)
        self.centralWidget().scene.HoleWindow_func.append(self.changeTitle)

        #显示鼠标坐标
        self.statusBar().showMessage('')
        self.status_mouse_pos = QLabel('')
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        node_editor.view.scenePosChanged.connect(self.onScenePosChanged)

        self.setGeometry(200, 200, 800, 600)
        self.changeTitle()
        self.show()

    def changeTitle(self):
        title = 'node editor ---- '

        if self.filename == None:
            title += 'New'
        else:
            title = os.path.basename(self.filename)
        if not self.centralWidget().scene.has_been_saved:
            title += '*'

        self.setWindowTitle(title)

    def createact(self, actname, shortcut, tooltip, callback):
        act = QAction(actname, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act

    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText('mouse pos:[%d, %d]' % (x, y))

    def closeEvent(self, event):
        if self.maybesave():
            event.accept()
        else:
            event.ignore()

    def isSaved(self):
        return self.centralWidget().scene.has_been_saved

    def maybesave(self):
        if self.isSaved():
            return True
        res = QMessageBox.warning(self, 'you forgot to save your graph', 'you forgot to save your graph',  QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if res == QMessageBox.StandardButton.Save:
            return self.onFileSave()
        elif res == QMessageBox.StandardButton.Discard:
            return True
        elif res == QMessageBox.StandardButton.Cancel:
            return False

    def onFileNew(self):
        if self.maybesave():
            self.centralWidget().scene.clear()
            self.centralWidget().scene.History.restart()
            self.centralWidget().scene.has_been_saved = True
            self.filename = None
            self.changeTitle()
            return True
        else:
            return False


    def onFileOpen(self):
        if self.onFileNew():
            fname, filter = QFileDialog.getOpenFileName(self, 'open graph from file')
            if fname == '':
                return
            if os.path.isfile(fname):
                self.centralWidget().scene.open_graph(fname)
                self.centralWidget().scene.History.storeHistory()
                self.centralWidget().scene.has_been_saved = True
            self.filename = fname
            self.changeTitle()


    def onFileSave(self):
        if self.filename is None:
            return self.onFileSaveAs()
        else:
            self.centralWidget().scene.save_graph(self.filename)
            self.statusBar().showMessage('saved in '+ self.filename)
            self.centralWidget().scene.has_been_saved = True
            self.changeTitle()
        # self.centralWidget().scene.save_graph('graph.json.txt')
        return True

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'save graph to file')
        # 加了下面两行不报错
        if fname == '':
            return False
        self.filename = fname
        self.onFileSave()
        return True

    def onEditUndo(self):
        self.centralWidget().scene.History.Undo()


    def onEditRedo(self):
        self.centralWidget().scene.History.Redo()

    def onEditDelete(self):
        print('ON FILE NEW CLICKED')

    def onEditPaste(self):
        self.centralWidget().ctrl_xcv.paste(self.data)
        self.centralWidget().scene.History.storeHistory()
        print('paste')

    def onEditCopy(self):
        self.centralWidget().scene.History.storeHistory()
        self.data = self.centralWidget().ctrl_xcv.copy()

        print('copy')

    def onEditCut(self):
        self.centralWidget().scene.History.storeHistory()
        self.data = self.centralWidget().ctrl_xcv.cut()

        print('cut')
