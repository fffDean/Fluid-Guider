from PySide6.QtGui import Qt, QColor, QPen, QBrush, QPainter, QMouseEvent, QIcon, QDoubleValidator, QIntValidator, QPainterPath, QCursor, QAction
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLineEdit, QSplitter, QComboBox, QRadioButton, QMenu
from PySide6.QtCore import QLine, Signal, QEvent, QRectF
from gui_real.edge_edge import Edge
from gui_real.hole_setting import GraphicSocket2
import math


class AttributeWidget(QWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.layout.addWidget(self.splitter)

        self.LayerScene = LayerScene()
        self.LayerView = LayerView(self.LayerScene, self.splitter)
        self.layerChoice = LayerChoice(scene, self.splitter)
        #self.layout.addWidget(self.LayerView)
        self.attributeTree = AttributeTree(self.splitter)      # LayerView(self.LayerScene)
        #self.layout.addWidget(self.attributeTree)

    def clear(self):
        self.attributeTree.updateData()

    def updateData(self, data={}):
        self.attributeTree.updateData(data)


class LayerChoice(QTreeWidget):
    onLayerCheckedSignal = Signal(int)
    onLayerNewSignal = Signal(int)
    onLayerNewAfterSignal = Signal(int)
    onLayerNewBeforeSignal = Signal(int)
    onLayerDeleteSignal = Signal(int)
    layerValueChangedSignal = Signal(int, float)
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.layers = len(self.scene.layers)
        self.createEditMenu()
        self.initUI()

    def setLayers(self, layers):
        self.layers = layers
        self.clear()
        self.initUI()

    def initUI(self):
        self.setColumnCount(2)
        self.setHeaderLabels(['layers', 'thickness'])
        self.setColumnWidth(0, 100)  # 第一列列宽设为100
        for i in range(self.layers):
            radio = QRadioButton('layer{}'.format(i))
            radio.toggled.connect(self.onLayerCheck)
            layer = QTreeWidgetItem(self)
            layer.setData(0, Qt.UserRole, i)
            self.setItemWidget(layer, 0, radio)

            colorval = QLineEdit()
            # 设置精度，小数点3位
            colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.layerValueChanged)
            colorval.setText(str(self.scene.layersValue[i]))
            self.setItemWidget(layer, 1, colorval)


    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.updateEditMenu(event)
            self.menu.popup(QCursor.pos())

    def createEditMenu(self):
        self.menu = QMenu(self)
        self.layerNew = QAction("&New Node", self.menu, shortcut='Ctrl+Shift+N', statusTip="Create a new node", triggered=self.onLayerNew)
        self.addLayerAfter = QAction("&New Node After", self.menu, shortcut='Ctrl+Shift+M', statusTip="Create a new node", triggered=self.onLayerNewAfter)
        self.addLayerBefore = QAction("&New Node Before", self.menu, shortcut='Ctrl+Shift+B', statusTip="Create a new node", triggered=self.onLayerNewBefore)
        self.layerDelete = QAction('&Delete', self.menu, shortcut='Ctrl+Del', statusTip='Delete node', triggered=self.onLayerDelete)
        self.menu.addAction(self.layerNew)
        self.menu.addAction(self.addLayerAfter)
        self.menu.addAction(self.addLayerBefore)
        self.menu.addAction(self.layerDelete)

    def updateEditMenu(self, event):
        hasItem = (self.get_item_at_click(event) is not None)
        self.layerDelete.setEnabled(hasItem)
        self.addLayerBefore.setEnabled(hasItem)
        self.addLayerAfter.setEnabled(hasItem)
        if self.currentItem() is not None and self.currentItem().data(0, Qt.UserRole) == 0:
            self.layerDelete.setEnabled(False)

    def get_item_at_click(self, event):
        """ 获取点击位置的图元，无则返回None. """
        pos = event.pos()
        item = self.itemAt(pos)
        return item

    def onLayerCheck(self, checked):
        if checked:
            self.onLayerCheckedSignal.emit(self.currentItem().data(0, Qt.UserRole))

    def onLayerNew(self):
        self.onLayerNewSignal.emit(self.currentItem().data(0, Qt.UserRole))

    def onLayerDelete(self):
        self.onLayerDeleteSignal.emit(self.currentItem().data(0, Qt.UserRole))

    def onLayerNewAfter(self):
        self.onLayerNewAfterSignal.emit(self.currentItem().data(0, Qt.UserRole))

    def onLayerNewBefore(self):
        self.onLayerNewBeforeSignal.emit(self.currentItem().data(0, Qt.UserRole))

    def layerValueChanged(self):
        self.layerValueChangedSignal.emit(self.currentItem().data(0, Qt.UserRole), float(self.itemWidget(self.currentItem(), 1).text()))


class AttributeTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graphic = None
        self.data = {}
        self.items = {}
        self.initUI()
        self.addChildren()
        self.createEditMenu()

    def initUI(self):
        # 设置行数与列数
        self.setColumnCount(2)
        self.setHeaderLabels(['Item', 'Value'])
        self.setColumnWidth(0, 100)  # 第一列列宽设为100
        # self.tree.itemClicked.connect(self.change_func)

    def updateData(self, data={}):
        try:
            self.clear()
            self.data = data
            self.initUI()
            self.addChildren()
        except:
            pass

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.updateEditMenu(event)
            self.menu.popup(QCursor.pos())

    def createEditMenu(self):
        self.menu = QMenu(self)
        self.rectDelete = QAction('&Delete', self.menu, shortcut='Ctrl+Del', statusTip='Delete node', triggered=self.onRectDelete)
        self.menu.addAction(self.rectDelete)

    def updateEditMenu(self, event):
        item = self.get_item_at_click(event)
        hasItem = (item is not None)
        self.rectDelete.setEnabled(False)
        if 'shapes' in self.data and item.data(0, Qt.UserRole + 1) is not None:
            self.rectDelete.setEnabled(True)

    def onRectDelete(self):
        number = self.currentItem().data(0, Qt.UserRole + 1)
        self.graphic.baseShape.shapes.pop(number)
        self.updateData()
        self.graphic.baseShape.scene.grScene.update()

    def get_item_at_click(self, event):
        """ 获取点击位置的图元，无则返回None. """
        pos = event.pos()
        item = self.itemAt(pos)
        return item

    def layerBox(self):
        box = QComboBox()
        for i in range(len(self.graphic.scene().scene.layers)):
            box.addItem(str(i))
        box.textActivated.connect(self.layerChanged)
        return box

    def addChildren(self):
        if 'shapes' in self.data:
            mainItem = QTreeWidgetItem(self)
            mainItem.setText(0, 'base shape')
            shape_list = []
            for shape in self.data['shapes']:
                shapeItem = QTreeWidgetItem(mainItem)
                shapeItem.setText(0, shape['Type'])
                shapeItem.setData(0, Qt.UserRole + 1, self.data['shapes'].index(shape))
                shapeData = {}
                if 'area' in shape:
                    colorval = QLineEdit()
                    # 设置精度，小数点3位
                    colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
                    colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
                    colorval.editingFinished.connect(self.baseShapeUpdate)

                    item = QTreeWidgetItem(shapeItem)
                    item.setText(0, 'width')
                    self.setItemWidget(item, 1, colorval)
                    self.itemWidget(item, 1).setText(str(shape['area'][0]))
                    shapeData['width'] = item

                    colorval = QLineEdit()
                    colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
                    colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
                    colorval.editingFinished.connect(self.baseShapeUpdate)

                    item = QTreeWidgetItem(shapeItem)
                    item.setText(0, 'height')
                    self.setItemWidget(item, 1, colorval)
                    self.itemWidget(item, 1).setText(str(shape['area'][1]))
                    shapeData['height'] = item

                if 'thickness' in shape:
                    colorval = QLineEdit()
                    # 设置精度，小数点3位
                    colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
                    colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
                    colorval.editingFinished.connect(self.baseShapeUpdate)

                    item = QTreeWidgetItem(shapeItem)
                    item.setText(0, 'thickness')
                    self.setItemWidget(item, 1, colorval)
                    self.itemWidget(item, 1).setText(str(shape['thickness']))
                    shapeData['thickness'] = item

                if 'pos' in shape:
                    colorval = QLineEdit()
                    # 设置精度，小数点3位
                    colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
                    colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
                    colorval.editingFinished.connect(self.baseShapeUpdate)

                    item = QTreeWidgetItem(shapeItem)
                    item.setText(0, 'pos_x')
                    self.setItemWidget(item, 1, colorval)
                    self.itemWidget(item, 1).setText(str(shape['pos'][0]))
                    shapeData['pos_x'] = item

                    colorval = QLineEdit()
                    colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
                    colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
                    colorval.editingFinished.connect(self.baseShapeUpdate)

                    item = QTreeWidgetItem(shapeItem)
                    item.setText(0, 'pos_y')
                    self.setItemWidget(item, 1, colorval)
                    self.itemWidget(item, 1).setText(str(shape['pos'][1]))
                    shapeData['pos_y'] = item

                shape_list.append(shapeData)

            self.items['base_shape'] = shape_list


        if 'pos' in self.data:
            colorval = QLineEdit()
            # 设置精度，小数点3位
            colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.posChanged)

            item = QTreeWidgetItem(self)
            item.setText(0, 'pos_x')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['pos'][0]))
            self.items['pos_x'] = item

            colorval = QLineEdit()
            colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.posChanged)

            item = QTreeWidgetItem(self)
            item.setText(0, 'pos_y')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['pos'][1]))
            self.items['pos_y'] = item

        if 'rotation' in self.data:
            colorval = QLineEdit()
            # 设置精度，小数点3位
            colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.rotationChanged)

            item = QTreeWidgetItem(self)
            item.setText(0, 'rotation')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['rotation']))
            self.items['rotation'] = item

        if 'layer' in self.data:
            layer = QTreeWidgetItem(self)
            layer.setText(0, 'position')
            layerBox = self.layerBox()
            self.setItemWidget(layer, 1, layerBox)
            self.itemWidget(layer, 1).setCurrentText(str(self.data['layer']))
            self.items['layer'] = layer
            if 'layer_enable' in self.data:
                layerBox.setEnabled(False)

        if 'line_width' in self.data:
            colorval = QLineEdit()
            # 设置精度，小数点3位
            colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.widthChanged)

            item = QTreeWidgetItem(self)
            item.setText(0, 'line_width')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['line_width']))
            self.items['line_width'] = item

        if 'attribute' in self.data:
            self.addAttributeChildren()

    def addAttributeChildren(self):
        attribute = QTreeWidgetItem(self)
        attribute.setText(0, 'attribute')
        def addFloatChild(name: str, function, Min, Max, i):
            colorval = QLineEdit()
            colorval.setValidator(QDoubleValidator(Min, Max, i))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(function)

            item = QTreeWidgetItem(attribute)
            item.setText(0, name)
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['attribute']['default_'+name]))
            self.items['default_'+name] = item

        def addIntChild(name: str, function, Min, Max):
            colorval = QLineEdit()
            colorval.setValidator(QIntValidator(Min, Max))
            colorval.editingFinished.connect(function)

            item = QTreeWidgetItem(attribute)
            item.setText(0, name)
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['attribute']['default_'+name]))
            self.items['default_'+name] = item

        if 'default_diameter' in self.data['attribute']:
            addFloatChild('diameter', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_height' in self.data['attribute']:
            addFloatChild('height', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_distance' in self.data['attribute']:
            addFloatChild('distance', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_total_way' in self.data['attribute']:
            addFloatChild('total_way', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_line_length' in self.data['attribute']:
            addFloatChild('line_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_r' in self.data['attribute']:
            addFloatChild('r', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_step' in self.data['attribute']:
            addIntChild('step', self.nodeMarkChanged, 1, 360)

        if 'default_N' in self.data['attribute']:
            addIntChild('N', self.nodeMarkChanged, 1, 360)

        if 'default_main_path_length' in self.data['attribute']:
            addFloatChild('main_path_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_sub_path_d' in self.data['attribute']:
            addFloatChild('sub_path_d', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_sub_path_length' in self.data['attribute']:
            addFloatChild('sub_path_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_sub_path_number' in self.data['attribute']:
            addIntChild('sub_path_number', self.nodeMarkChanged, 0, 360)

        if 'default_sub_distance' in self.data['attribute']:
            addFloatChild('sub_distance', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_bolt_length' in self.data['attribute']:
            addFloatChild('bolt_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_bolt_diameter' in self.data['attribute']:
            addFloatChild('bolt_diameter', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_line_diameter' in self.data['attribute']:
            addFloatChild('line_diameter', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_flow_length' in self.data['attribute']:
            addFloatChild('flow_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_body_length' in self.data['attribute']:
            addFloatChild('body_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_flow_width' in self.data['attribute']:
            addFloatChild('flow_width', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_flow_height' in self.data['attribute']:
            addFloatChild('flow_height', self.nodeMarkChanged, 0.000, 64000.000, 3)

        if 'default_level' in self.data['attribute']:
            addIntChild('level', self.nodeMarkChanged, 1, 360)

    def nodeMarkChanged(self):
        if self.graphic.node.attribute['name'] == 'U_way':
            self.graphic.node.attribute["default_diameter"] = float(
                self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_height"] = float(
                self.itemWidget(self.items["default_height"], 1).text())
            self.graphic.node.attribute["default_distance"] = float(
                self.itemWidget(self.items["default_distance"], 1).text())
            self.graphic.node.attribute["default_total_way"] = float(
                self.itemWidget(self.items["default_total_way"], 1).text())
        elif self.graphic.node.attribute['name'] == 'O_way':
            self.graphic.node.attribute["default_diameter"] = float(
                self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_line_length"] = float(
                self.itemWidget(self.items["default_line_length"], 1).text())
            self.graphic.node.attribute["default_r"] = float(self.itemWidget(self.items["default_r"], 1).text())
            self.graphic.node.attribute["default_step"] = int(self.itemWidget(self.items["default_step"], 1).text())
            self.graphic.node.attribute["default_N"] = int(self.itemWidget(self.items["default_N"], 1).text())
        elif self.graphic.node.attribute['name'] == 'T_way':
            self.graphic.node.attribute["default_diameter"] = float(
                self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_main_path_length"] = float(
                self.itemWidget(self.items["default_main_path_length"], 1).text())
            self.graphic.node.attribute["default_sub_path_d"] = float(
                self.itemWidget(self.items["default_sub_path_d"], 1).text())
            self.graphic.node.attribute["default_sub_path_length"] = float(
                self.itemWidget(self.items["default_sub_path_length"], 1).text())
            self.graphic.node.attribute["default_sub_path_number"] = int(
                self.itemWidget(self.items["default_sub_path_number"], 1).text())
            self.graphic.node.attribute["default_sub_distance"] = float(
                self.itemWidget(self.items["default_sub_distance"], 1).text())
        elif self.graphic.node.attribute['name'] == 'Door_way':
            self.graphic.node.attribute["default_bolt_length"] = float(
                self.itemWidget(self.items["default_bolt_length"], 1).text())
            self.graphic.node.attribute["default_bolt_diameter"] = float(
                self.itemWidget(self.items["default_bolt_diameter"], 1).text())
            self.graphic.node.attribute["default_line_length"] = float(
                self.itemWidget(self.items["default_line_length"], 1).text())
            self.graphic.node.attribute["default_line_diameter"] = float(
                self.itemWidget(self.items["default_line_diameter"], 1).text())
        elif self.graphic.node.attribute['name'] == 'K_way':
            self.graphic.node.attribute["default_flow_length"] = float(
                self.itemWidget(self.items["default_flow_length"], 1).text())
            self.graphic.node.attribute["default_body_length"] = float(
                self.itemWidget(self.items["default_body_length"], 1).text())
            self.graphic.node.attribute["default_diameter"] = float(
                self.itemWidget(self.items["default_diameter"], 1).text())
        elif self.graphic.node.attribute['name'] == 'Fork_way':
            self.graphic.node.attribute["default_flow_width"] = float(
                self.itemWidget(self.items["default_flow_width"], 1).text())
            self.graphic.node.attribute["default_flow_height"] = float(
                self.itemWidget(self.items["default_flow_height"], 1).text())
            self.graphic.node.attribute["default_diameter"] = float(
                self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_level"] = int(
                self.itemWidget(self.items["default_level"], 1).text())
        self.graphic.node.setup()
        self.graphic.scene().scene.updateEdges()

    def posChanged(self):
        x = float(self.itemWidget(self.items['pos_x'], 1).text())
        y = float(self.itemWidget(self.items['pos_y'], 1).text())
        self.graphic.setPos(x, y)
        self.graphic.scene().scene.updateEdges()

    def rotationChanged(self):
        rotation = float(self.itemWidget(self.items['rotation'], 1).text())
        self.graphic.setRotation(rotation)
        self.graphic.scene().scene.updateEdges()

    def widthChanged(self):
        width = float(self.itemWidget(self.items['line_width'], 1).text())
        self.graphic.edge.setWidth(width)

    def layerChanged(self):
        print(1)
        if hasattr(self.graphic, 'node'):
            self.graphic.node.set_layer(int(self.itemWidget(self.items['layer'], 1).currentIndex()))
            self.graphic.node.scene.setLayer(self.graphic.node.scene.currentLayer)
        elif hasattr(self.graphic, 'edge'):
            scene = self.graphic.edge.scene
            self.graphic.edge.layer = int(self.itemWidget(self.items['layer'], 1).currentIndex())
            self.graphic.edge.start_socket.socket.set_layer(self.graphic.edge.layer)
            self.graphic.edge.end_socket.socket.set_layer(self.graphic.edge.layer)
            hole1 = self.graphic.edge.start_socket.parentItem().hole
            hole2 = self.graphic.edge.end_socket.parentItem().hole
            hole1.reset_layer()
            hole2.reset_layer()
            insideSocket1 = self.graphic.edge.start_socket.socket
            insideSocket2 = self.graphic.edge.end_socket.socket
            outsideSocket1 = hole1.opMySocket(insideSocket1.grSocket).socket
            outsideSocket2 = hole2.opMySocket(insideSocket2.grSocket).socket
            edge1 = outsideSocket1.edge
            edge2 = outsideSocket2.edge
            if hole1.layerMin == hole1.layerMax and hole2.layerMin == hole2.layerMax:
                width = self.graphic.edge.width
                hole1.scene.remove_edge(self.graphic)
                hole1.scene.remove_edge(edge1.grEdge)
                hole1.scene.remove_hole(hole1.grHole)
                hole2.scene.remove_edge(edge2.grEdge)
                hole2.scene.remove_hole(hole2.grHole)
                edge = Edge(hole1.scene, edge1.opSocket(outsideSocket1.grSocket), edge2.opSocket(outsideSocket2.grSocket))
                edge.setWidth(width)
                if isinstance(edge1.opSocket(outsideSocket1.grSocket), GraphicSocket2):
                    hole = edge1.opSocket(outsideSocket1.grSocket).parentItem()
                    hole.set_socket(hole.opSocket(outsideSocket1.grSocket), edge2.opSocket(outsideSocket2.grSocket))
                if isinstance(edge2.opSocket(outsideSocket2.grSocket), GraphicSocket2):
                    hole = edge2.opSocket(outsideSocket2.grSocket).parentItem()
                    hole.set_socket(edge1.opSocket(outsideSocket1.grSocket), hole.opSocket(outsideSocket2.grSocket))

            elif hole1.layerMin == hole1.layerMax:
                width = self.graphic.edge.width
                hole1.scene.remove_edge(self.graphic)
                hole1.scene.remove_edge(edge1.grEdge)
                hole1.scene.remove_hole(hole1.grHole)
                edge = Edge(hole1.scene, edge1.opSocket(outsideSocket1.grSocket), insideSocket2.grSocket)
                edge.setWidth(width)
                hole2.set_socket(edge1.opSocket(outsideSocket1.grSocket), hole2.opSocket(self.graphic.edge.start_socket))
                if isinstance(edge1.opSocket(outsideSocket1.grSocket), GraphicSocket2):
                    hole = edge1.opSocket(outsideSocket1.grSocket).parentItem()
                    hole.set_socket(hole.opSocket(outsideSocket1.grSocket), insideSocket1.grSocket)
            elif hole2.layerMin == hole2.layerMax:
                width = self.graphic.edge.width
                hole2.scene.remove_edge(self.graphic)
                hole2.scene.remove_edge(edge2.grEdge)
                hole2.scene.remove_hole(hole1.grHole)
                edge = Edge(hole2.scene, self.graphic.edge.start_socket, edge2.opSocket(outsideSocket2.grSocket))
                edge.setWidth(width)
                hole1.set_socket(edge2.opSocket(outsideSocket2.grSocket), hole1.opSocket(insideSocket2.grSocket))
                if isinstance(edge2.opSocket(outsideSocket2.grSocket), GraphicSocket2):
                    hole = edge1.opSocket(outsideSocket2.grSocket).parentItem()
                    hole.set_socket(hole.opSocket(outsideSocket2.grSocket), insideSocket1.grSocket)
            else:
                pass
            scene.setLayer(scene.currentLayer)
            self.updateData()

    def areaChanged(self):
        width = float(self.itemWidget(self.items['width'], 1).text())
        height = float(self.itemWidget(self.items['height'], 1).text())
        self.graphic.setArea(width, height)

    def baseShapeUpdate(self):
        for i in range(len(self.items['base_shape'])):
            shapeData = self.items['base_shape'][i]
            width = float(self.itemWidget(shapeData['width'], 1).text())
            height = float(self.itemWidget(shapeData['height'], 1).text())
            pos_x = float(self.itemWidget(shapeData['pos_x'], 1).text())
            pos_y = float(self.itemWidget(shapeData['pos_y'], 1).text())
            thickness = float(self.itemWidget(shapeData['thickness'], 1).text())
            self.graphic.baseShape.shapes[i].reset(pos_x, pos_y, width, height, thickness)

        self.graphic.update()


class LayerScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)

        # 一些关于网格背景的设置
        self.grid_size = 10  # 一块网格的大小 （正方形的）
        self.grid_squares = 20  # 网格中正方形的区域个数

        # 一些颜色
        self._color_background = QColor('#393939')
        self._color_light = QColor('#2f2f2f')
        self._color_dark = QColor('#292929')
        # 一些画笔
        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        # 设置画背景的画笔
        self.setBackgroundBrush(self._color_background)
        self.setGrScene(64, 64)
        # self.setSceneRect(-32000, -32000, 64000, 64000)
        # self.scene_width, self.scene_height = 64000, 64000
        # self.setSceneRect(-self.scene_width // 2, -self.scene_height // 2, self.scene_width, self.scene_height)

        self.addLayers(3)

    def setGrScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    # override
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # 获取背景矩形的上下左右的长度，分别向上或向下取整数
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        # 从左边和上边开始
        first_left = left - (left % self.grid_size)  # 减去余数，保证可以被网格大小整除
        first_top = top - (top % self.grid_size)

        # 分别收集明、暗线
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if x % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

            # 最后把收集的明、暗线分别画出来
        painter.setPen(self._pen_light)
        if lines_light:
            painter.drawLines(lines_light)

        painter.setPen(self._pen_dark)
        if lines_dark:
            painter.drawLines(lines_dark)

    def addLayers(self, n):
        op = [1, 0]
        for item in self.items():
            self.removeItem(item)
        item = Layer(0)
        item.setArea(1000, 10)
        self.addItem(item)
        for i in range(n-1):
            index = op[item.index]
            item = Layer(index)
            item.setArea(1000, 10)
            item.setPos(0, (i+1)*20)
            self.addItem(item)


class LayerView(QGraphicsView):

    def __init__(self, grScene, parent=None):
        super().__init__(parent)

        self.grScene = grScene  # 将scene传入此处托管，方便在view中维护
        self.parent = parent

        self.initUI()

    def initUI(self):
        self.setScene(self.grScene)
        # 设置渲染属性
        self.setRenderHints(QPainter.Antialiasing |                    # 抗锯齿
                            QPainter.TextAntialiasing |                # 文字抗锯齿
                            QPainter.SmoothPixmapTransform |           # 使图元变换更加平滑
                            QPainter.LosslessImageRendering)           # 不失真的图片渲染
        # 视窗更新模式
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        # 设置以鼠标为中心缩放
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        # 设置拖拽模式
        self.setDragMode(self.DragMode.RubberBandDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def leftMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def middleMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def leftMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)


class Layer(QGraphicsItem):
    def __init__(self, index=0, parent=None):
        super().__init__(parent)
        self.width = 100
        self.height = 10
        self.index = index

        self._pen0 = QPen(QColor("#aaffffff"))
        self._pen0.setWidth(10)
        self._pen1 = QPen(QColor("#aaffa637"))
        self._pen1.setWidth(10)

        self._brush0 = QBrush(QColor("#ff313131"))
        self._brush1 = QBrush(QColor("#aa121212"))

    def setArea(self, w, h):
        self.width = w
        self.height = h
        self.update()

    def paint(self, painter, option, widget=None):
        path_outline = QPainterPath()
        path_outline.addRect(-self.width/2, 0, self.width, self.height)
        painter.setPen(self._pen0 if self.index == 0 else self._pen1)
        # painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setBrush(self._brush0 if self.index == 0 else self._brush1)
        painter.drawPath(path_outline.simplified())

    def boundingRect(self):
        return QRectF(
            -self.width/2,
            0,
            self.width,
            self.height
        ).normalized()
