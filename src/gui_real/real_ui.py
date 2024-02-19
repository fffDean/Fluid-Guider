from PySide6.QtGui import Qt, QAction
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QDockWidget, QFileDialog
from gui_real.scene_setting import GraphicView
from gui_real.scene_scene import Scene
from gui_real.toolbar_setting import Toolbar
from gui_real.layer_scene_setting import LayerScene, LayerView, AttributeWidget
from gui_real.node_setting import GraphicNode, GraphicSocket
from gui_real.edge_setting import GraphicEdge, GraphicCantSeeSocket
from gui_real.hole_setting import GraphicSocket2
from gui_real.Item import GraphicItem
from gui_real.baseShape_setting import GraphicBaseShape
import os


class mainWindow(QWidget):
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

        self.setWindowTitle("Graphics Demo")


class RealMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = None
        self.realWindowList = []

        self.initUI()

    def initUI(self):
        real_editor = mainWindow(self)
        real_editor.view.itemPressSignal.connect(self.updateDataTree)
        real_editor.scene.openFileSignal.connect(self.layerSetting)
        self.setCentralWidget(real_editor)
        self.createToolBar()
        self.createDataTree()
        #self.centralWidget().scene.HoleWindow_func.append(self.changeTitle)
        self.show()

    def loading(self, data={}):
        self.centralWidget().scene.loading(data)

    def createToolBar(self):
        self.fileToolBar = Toolbar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.fileToolBar)

    def createDataTree(self):
        self.datatree = AttributeWidget(self.centralWidget().scene, self)
        self.datatree.layerChoice.onLayerCheckedSignal.connect(self.layerCkecked)
        self.datatree.layerChoice.onLayerNewSignal.connect(self.layerNew)
        self.datatree.layerChoice.onLayerDeleteSignal.connect(self.layerDelete)
        self.datatree.layerChoice.onLayerNewAfterSignal.connect(self.addLayerAfter)
        self.datatree.layerChoice.onLayerNewBeforeSignal.connect(self.addLayerBefore)
        self.datatree.layerChoice.layerValueChangedSignal.connect(self.layerValueChanged)
        self.dataDock = QDockWidget('Attribute')
        self.dataDock.setWidget(self.datatree)
        self.dataDock.setFloating(False)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dataDock)

    def updateDataTree(self, graphic_list):
        graphic = graphic_list[0]
        print(graphic_list)
        if graphic is None:
            self.datatree.attributeTree.graphic = None
            self.datatree.updateData()
        elif isinstance(graphic, GraphicBaseShape):
            self.datatree.attributeTree.graphic = graphic
            data = graphic.baseShape.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicNode):
            self.datatree.attributeTree.graphic = graphic
            data = graphic.node.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicSocket):
            self.datatree.attributeTree.graphic = None
            data = graphic.socket.to_string()
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicEdge):
            self.datatree.attributeTree.graphic = graphic
            data = graphic.edge.to_string()
            if isinstance(graphic.edge.start_socket, GraphicSocket2) and isinstance(graphic.edge.end_socket, GraphicSocket2):
                pass
            else:
                data['layer_enable'] = False
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicCantSeeSocket):
            self.datatree.attributeTree.graphic = graphic
            data = {
                "pos": [graphic.scenePos().x(), graphic.scenePos().y()]
            }
            self.datatree.updateData(data)
        elif isinstance(graphic, GraphicItem):
            self.datatree.attributeTree.graphic = graphic.parentItem()
            data = graphic.parentItem().node.to_string()
            self.datatree.updateData(data)

    def layerSetting(self):
        self.datatree.layerChoice.setLayers(len(self.centralWidget().scene.layers))

    def layerCkecked(self, layer):
        self.centralWidget().scene.setLayer(layer)
        self.datatree.attributeTree.updateData()

    def layerNew(self, layer):
        self.centralWidget().scene.add_layer()
        self.centralWidget().scene.setLayer(self.centralWidget().scene.currentLayer)
        self.datatree.layerChoice.setLayers(len(self.centralWidget().scene.layers))
        self.datatree.attributeTree.updateData()

    def layerDelete(self, layer):
        self.centralWidget().scene.remove_layer(layer)
        self.datatree.layerChoice.setLayers(len(self.centralWidget().scene.layers))
        self.datatree.attributeTree.updateData()

    def addLayerAfter(self, layer):
        self.centralWidget().scene.insertLayer(layer+1)
        self.centralWidget().scene.setLayer(self.centralWidget().scene.currentLayer)
        self.datatree.layerChoice.setLayers(len(self.centralWidget().scene.layers))
        self.datatree.attributeTree.updateData()

    def addLayerBefore(self, layer):
        self.centralWidget().scene.insertLayer(layer)
        self.centralWidget().scene.setLayer(self.centralWidget().scene.currentLayer)
        self.datatree.layerChoice.setLayers(len(self.centralWidget().scene.layers))
        self.datatree.attributeTree.updateData()

    def layerValueChanged(self, layer, value):
        self.centralWidget().scene.setLayerValue(layer, value)

    def voluntary_default(self):
        data = self.centralWidget().scene.item_to_string()
        realMainWindow = RealMainWindow()
        realMainWindow.centralWidget().scene.voluntary_default(data)
        self.realWindowList.append(realMainWindow)

    def voluntary_static(self):
        data = self.centralWidget().scene.item_to_string()
        realMainWindow = RealMainWindow()
        realMainWindow.centralWidget().scene.voluntary_static(data)
        self.realWindowList.append(realMainWindow)

    def on3DModelSave(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'save 3D Model to file')
        # 加了下面两行不报错
        if fname == '':
            return False
        self.centralWidget().scene.to_3DModel(fname)
        return self.filename

    def onFileSave(self):
        if self.filename is None:
            return self.onFileSaveAs()
        else:
            self.centralWidget().scene.save_graph(self.filename)
            # self.scene.has_been_saved = True
            # self.changeTitle()
        return self.filename

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'save graph to file')
        # 加了下面两行不报错
        if fname == '':
            return False
        self.filename = fname
        self.onFileSave()
        return self.filename

    def onOpenFile(self):
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file')
        for fname in fnames:
            if fname == '':
                return
            if os.path.isfile(fname):
                realMainWindow = RealMainWindow()
                realMainWindow.centralWidget().scene.open_graph(fname)
                self.realWindowList.append(realMainWindow)
