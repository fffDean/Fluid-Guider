from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import*

from gui_test.nodeslist_setting import*
from gui_test.node_setting import GraphicNode, GraphicSocket
from gui_test.edge_setting import GraphicEdge
from gui_test.Item import GraphicItem
from gui_test.item_group import GraphicItemGroup
from gui_test.test1_ui import MainWindow, HoleWindow
from gui_test.treeWidget_setting import SettingTree

import os

class mdiWindow(HoleWindow):

    def initUI(self):

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mappedObject.connect(self.setActiveSubWindow)

        self.createNodesWindow()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()
        self.createDataTree()

        self.readSettings()

        self.setWindowTitle("MDI")

        self.show()

    def onFileNew(self):
        subwindow = self.createMdiChild()
        subwindow.widget().filename = None
        subwindow.widget().scene.History.storeHistory()
        subwindow.show()
        return True

    def onFileOpen(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file')
        for fname in fnames:
            if fname == '':
                return
            if os.path.isfile(fname):
                subwindow = self.createMdiChild()
                subwindow.widget().filename = fname
                subwindow.widget().scene.open_graph(fname)
                subwindow.widget().scene.History.storeHistory()
                subwindow.widget().scene.has_been_saved = True
                subwindow.widget().changeTitle()
                subwindow.show()

    def onFileSave(self):
        self.activeMdiChild().onFileSave()

    def onFileSaveAs(self):
        self.activeMdiChild().onFileSaveAs()

    def onFileEquationView(self):
        self.activeMdiChild().onFileEquationView()

    def onFileToRealMap(self):
        self.activeMdiChild().onFileToRealMap()

    def onEditUndo(self):
        self.activeMdiChild().scene.History.Undo()


    def onEditRedo(self):
        self.activeMdiChild().scene.History.Redo()

    def onEditDelete(self):
        self.datatree.restart()
        for item in self.activeMdiChild().scene.grScene.selectedItems():
            if isinstance(item, GraphicNode):
                self.activeMdiChild().scene.remove_node(item)
            elif isinstance(item, GraphicItemGroup):
                self.activeMdiChild().scene.remove_group(item)
            elif isinstance(item, GraphicEdge):
                item.edge.remove()
        self.activeMdiChild().scene.History.storeHistory()

    def onEditPaste(self):
        self.activeMdiChild().ctrl_xcv.paste(self.data)
        self.activeMdiChild().scene.History.storeHistory()
        print('paste')

    def onEditCopy(self):
        self.activeMdiChild().scene.History.storeHistory()
        self.data = self.activeMdiChild().ctrl_xcv.copy()

        print('copy')

    def onEditCut(self):
        self.activeMdiChild().scene.History.storeHistory()
        self.data = self.activeMdiChild().ctrl_xcv.cut()

        print('cut')

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        self.FileToRealMap.setEnabled(hasMdiChild)
        self.FileSave.setEnabled(hasMdiChild)
        self.FileSaveAs.setEnabled(hasMdiChild)
        self.EditCut.setEnabled(hasMdiChild)
        self.EditCopy.setEnabled(hasMdiChild)
        self.EditPaste.setEnabled(hasMdiChild)
        self.EditUndo.setEnabled(hasMdiChild)
        self.EditRedo.setEnabled(hasMdiChild)
        self.EditDelete.setEnabled(hasMdiChild)
        self.FileClose.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)

        hasSelection = (self.activeMdiChild() is not None)
        self.EditCut.setEnabled(hasSelection)
        self.EditCopy.setEnabled(hasSelection)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        self.windowMenu.addAction(self.nodesList)

        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)


        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.CurrentActiveWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def CurrentActiveWidget(self):
        """ we're returning NodeEditorWidget here... """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def createActions(self):
        self.FileNew = QAction("&New", self, shortcut='Ctrl+N', statusTip="Create a new file", triggered=self.onFileNew)
        self.FileOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
        # self.FileEquationView = QAction('&Equation View', shortcut='ctrl+j', statusTip='Edit Equation View', triggered=self.onFileEquationView)
        self.FileToRealMap = QAction("&To RealMap", self, shortcut='ctrl+k', statusTip='Translate to Real map', triggered=self.onFileToRealMap)
        self.FileSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip='Save file', triggered=self.onFileSave)
        self.FileSaveAs = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip='Save file as...', triggered=self.onFileSaveAs)
        self.FileClose = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip='Exit application', triggered=self.close)

        self.EditUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip='Undo last operation', triggered=self.onEditUndo)
        self.EditRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip='Redo last operation', triggered=self.onEditRedo)
        self.EditDelete = QAction('&Delete', self, shortcut='Del', statusTip='Delete selected item', triggered=self.onEditDelete)
        self.EditPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip='Paste what you selected', triggered=self.onEditPaste)
        self.EditCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip='Copy what you selected', triggered=self.onEditCopy)
        self.EditCut = QAction('&Cut', self, shortcut='Ctrl+X', statusTip='Cut what you selected', triggered=self.onEditCut)

        self.closeAct = QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.closeAllAct = QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.tileAct = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.cascadeAct = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.nextAct = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.previousAct = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)
        self.nodesList = QAction('NodesList', self, statusTip='NodesList', triggered=self.onWindowNodesToolbar)

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.FileNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.FileOpen)
        # self.fileMenu.addAction(self.FileEquationView)
        self.fileMenu.addAction(self.FileToRealMap)
        self.fileMenu.addAction(self.FileSave)
        self.fileMenu.addAction(self.FileSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.FileClose)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.EditUndo)
        self.editMenu.addAction(self.EditRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.EditDelete)
        self.editMenu.addAction(self.EditPaste)
        self.editMenu.addAction(self.EditCopy)
        self.editMenu.addAction(self.EditCut)

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        #self.helpMenu = self.menuBar().addMenu("&Help")
        #self.helpMenu.addAction(self.aboutAct)
        #self.helpMenu.addAction(self.aboutQtAct)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def createToolBars(self):
        pass

    def createStatusBar(self):
        pass

    def createNodesWindow(self):
        self.listwidget = DragListbox()
        #item = QListWidgetItem('Model.png', QIcon(QPixmap('Model.png')))
        #self.listwidget.addItem(item)
        #self.listwidget.addItem('add')

        self.nodesDock = QDockWidget('Nodes')
        self.nodesDock.setWidget(self.listwidget)
        self.nodesDock.setFloating(False)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.nodesDock)
        self.nodesDock.setVisible(False)

    def createDataTree(self):
        self.datatree = SettingTree()
        self.dataDock = QDockWidget('Attribute')
        self.dataDock.setWidget(self.datatree)
        self.dataDock.setFloating(False)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dataDock)

    def createMdiChild(self):
        child = MainWindow()
        subwindow = self.mdiArea.addSubWindow(child)
        child.view.itemPressSignal.connect(self.updateDataTree)
        self.datatree.restart()
        self.datatree.posChangedSignal.connect(child.scene.update)
        #subwindow.widget().scene.HoleWindow_func.append(self.changeTitle)
        #subwindow.showMaximized()
        #subwindow.setWindowFlags(Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        #subwindow.setWindowState(Qt.WindowState.WindowMaximized)
        #subwindow.setWindowFlag(Qt.WindowType.SubWindow)
        #subwindow.setWindowState(Qt.WindowState.WindowMaximized)
        #subwindow.show()
        return subwindow

    def updateDataTree(self, graphic_list):
        graphic = graphic_list[0]
        if graphic is None:
            self.datatree.graphic = None
            self.datatree.updateData()
        elif isinstance(graphic, GraphicNode):
            self.datatree.graphic = graphic
            data = graphic.node.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicSocket):
            self.datatree.graphic = None
            data = graphic.socket.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicEdge):
            self.datatree.graphic = graphic
            data = graphic.edge.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicItem):
            self.datatree.graphic = graphic.parentItem()
            data = graphic.parentItem().node.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, QGraphicsSimpleTextItem):
            self.datatree.graphic = graphic.parentItem()
            data = graphic.parentItem().node.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicItemGroup):
            self.datatree.graphic = graphic
            data = graphic.group.to_string()
            self.datatree.updateData(data)

    def readSettings(self):
        settings = QSettings('Trolltech', 'MDI Example')
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings('Trolltech', 'MDI Example')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)
