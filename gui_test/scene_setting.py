import math, json
import gc, copy

from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QColor, QPen, QPainter, QMouseEvent, QPixmap, QIcon, QDrag
from PySide6.QtCore import Qt, QLine, QEvent, Signal, QDataStream, QIODevice, QObject

from gui_test.Item import GraphicItem
from gui_test.node_setting import GraphicNode, GraphicSocket
from gui_test.edge_setting import GraphicEdge
from gui_test.node_node import Node, Socket
from gui_test.edge_edge import Edge
from gui_test.item_group import Group, GraphicItemGroup
from model_make.cq_code import *


class GraphicScene(QGraphicsScene):

    def __init__(self, scene, parent=None):
        super().__init__(parent)

        # 一些关于网格背景的设置
        self.grid_size = 10  # 一块网格的大小 （正方形的）
        self.grid_squares = 10  # 网格中正方形的区域个数

        # 一些颜色
        self._color_background = QColor('#eaeaea')
        self._color_light = QColor('#d6d6d6')
        self._color_dark = QColor('#cccccc')
        # 一些画笔
        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        # 设置画背景的画笔
        self.setBackgroundBrush(self._color_background)
        self.setGrScene(64000, 64000)
        # self.setSceneRect(-32000, -32000, 64000, 64000)
        # self.scene_width, self.scene_height = 64000, 64000
        # self.setSceneRect(-self.scene_width // 2, -self.scene_height // 2, self.scene_width, self.scene_height)

        self.scene = scene

        #self.nodes = []
        #self.edges = []


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

        for y in range(first_top, bottom, self.grid_size):
            if y % (self.grid_size * self.grid_squares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

            # 最后把收集的明、暗线分别画出来
        painter.setPen(self._pen_light)
        if lines_light:
            painter.drawLines(lines_light)

        painter.setPen(self._pen_dark)
        if lines_dark:
            painter.drawLines(lines_dark)

    def add_node(self, node):
        self.scene.nodes.append(node)
        self.addItem(node)
        #print(self.scene.nodes)   # debug
        #print(self.scene.edges)

    def remove_node(self, grNode):
        edges = copy.copy(self.scene.edges)
        # 删除图元时，遍历与其连接的线，并移除
        for grEdge in edges:
            if grEdge.edge.start_socket in grNode.node.sockets or grEdge.edge.end_socket in grNode.node.sockets:
                grEdge.edge.remove()
        if isinstance(grNode.parentItem(), GraphicItemGroup):
            group = grNode.parentItem().group
            group.removeFromGroup(grNode)
            group.updateArea()
        self.scene.nodes.remove(grNode)
        self.removeItem(grNode)
        del grNode.node
        del grNode
        gc.collect()

    def add_group(self, group):
        self.scene.groups.append(group)
        self.addItem(group)

    def remove_group(self, grGroup):
        edges = copy.copy(self.scene.edges)
        # 删除图元时，遍历与其连接的线，并移除
        for grEdge in edges:
            if grEdge.edge.start_socket in grGroup.group.sockets or grEdge.edge.end_socket in grGroup.group.sockets:
                grEdge.edge.remove()
        nodes = copy.copy(grGroup.group.nodes)
        for grNode in nodes:
            grGroup.group.removeFromGroup(grNode)
        self.scene.groups.remove(grGroup)
        self.removeItem(grGroup)

    def add_edge(self, edge):
        self.scene.edges.append(edge)
        self.addItem(edge)

    def remove_edge(self, edge):
        self.scene.edges.remove(edge)
        self.removeItem(edge)
        del edge.edge
        del edge
        gc.collect()



class GraphicView(QGraphicsView):
    scenePosChanged = Signal(int, int)
    itemPressSignal = Signal(list)

    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene  # 将scene传入此处托管，方便在view中维护
        self.parent = parent

        self.initUI()

        # 缩放参数
        self.zoomInFactor = 2    # 缩放倍率
        self.zoom = 5   # 初始缩放等级
        self.zoomStep = 1   # 缩放步长
        self.zoomClamp = False  # 缩放是否锁定
        self.zoomRange = [2, 8]    # 缩放区间

        self.edge_enable = False  # 用来记录目前是否可以画线条
        self.drag_edge = None  # 记录拖拽时的线
        self.drag_start_item = None
        self.node_move_start = False
        self.node_moving = False

    def initUI(self):
        self.setScene(self.scene.grScene)
        # 设置渲染属性
        self.setRenderHints(QPainter.Antialiasing |                    # 抗锯齿
                            QPainter.TextAntialiasing |                # 文字抗锯齿
                            QPainter.SmoothPixmapTransform |           # 使图元变换更加平滑
                            QPainter.LosslessImageRendering)           # 不失真的图片渲染
        # 视窗更新模式
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        # 设置水平和竖直方向的滚动条不显示
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置以鼠标为中心缩放
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        # 设置拖拽模式
        self.setDragMode(self.DragMode.RubberBandDrag)

    def edge_drag_start(self, item):
        self.drag_start_item = item  # 拖拽开始时的图元，此属性可以不在__init__中声明

        self.drag_edge = Edge(self.scene, self.drag_start_item, None)  # 开始拖拽线条，注意到拖拽终点为None

    def edge_drag_end(self, item):
        new_edge = Edge(self.scene, self.drag_start_item, item)  # 拖拽结束
        self.drag_edge.remove()  # 删除拖拽时画的线
        self.drag_edge = None
        # 连接插口后应关闭被连接插口
        #self.drag_start_item.socket.op_st = False
        #item.socket.op_st = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:  # 判断鼠标右键点击
            self.rightMouseButtonPress(event)
        elif event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        elif event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)



    def mouseMoveEvent(self, event):
        # 实时更新线条
        pos = event.pos()
        self.Last_Scene_Pos = self.mapToScene(pos)
        if self.edge_enable and self.drag_edge is not None:
            self.drag_edge.grEdge.set_posDestination(self.Last_Scene_Pos.x(), self.Last_Scene_Pos.y())
            self.drag_edge.grEdge.update()
            edge_start = self.drag_edge.grEdge.posSource
            edge_end = self.drag_edge.grEdge.posDestination
            for grGroup in self.scene.groups:
                if grGroup.group.intersects(edge_start, edge_end):
                    self.drag_edge.remove()
                    self.drag_edge = None
                    self.edge_enable = False
                    break

        if self.node_move_start:
            self.node_move_start = False
            self.node_moving = True

        self.scenePosChanged.emit(self.Last_Scene_Pos.x(), self.Last_Scene_Pos.y())

        super().mouseMoveEvent(event)

    def leftMouseButtonPress(self, event):
        item = self.get_item_at_click(event)
        pos = event.pos()
        self.Last_Scene_Pos = self.mapToScene(pos)
        self.itemPressSignal.emit([item])
        if isinstance(item, GraphicSocket) and item.socket.op_st:
            self.edge_enable = True
            # 确认起点是插口后，开始拖拽
            self.edge_drag_start(item)
            self.drag_edge.grEdge.set_posDestination(self.Last_Scene_Pos.x(), self.Last_Scene_Pos.y())
            self.drag_edge.grEdge.update()
            #print('press GraphicSocket')
        elif isinstance(item, GraphicSocket) and not item.socket.op_st:
            super().mousePressEvent(event)
            self.node_move_start = True
            #print('press GraphicSocket')
        elif isinstance(item, GraphicItem):
            super().mousePressEvent(event)
            self.node_move_start = True
        elif isinstance(item, GraphicNode):
            super().mousePressEvent(event)
            self.node_move_start = True
            #print('press GraphicNode')
        else:
            super().mousePressEvent(event)



    def leftMouseButtonRelease(self, event):
        item = self.get_item_at_click(event)
        items = self.get_items_at_click(event)  # 获取在该点的所有item
        grGroup = self.get_first_group(items)  # 获取层数最高的group
        if self.edge_enable:
            self.edge_enable = False
            item = self.get_first_socket(items)
            # 判断结束插口是否打开（打开就向下判断，if，elif先后顺序不可改变）
            if isinstance(item, GraphicSocket) and item.socket.op_st is not True:
                self.drag_edge.remove()
                self.drag_edge = None
                self.itemPressSignal.emit([item])
                #print('release GraphicSocket')
            # 终点图元不能是起点图元，即无环图
            elif isinstance(item, GraphicSocket) and item is not self.drag_start_item:
                self.edge_drag_end(item)
                #print('release GraphicSocket')
                self.scene.History.storeHistory()   # 保存历史
                self.itemPressSignal.emit([item])
            else:
                self.drag_edge.remove()
                self.drag_edge = None

        # 节点的变化将会更新group
        if self.node_moving:
            self.node_move_start = False
            self.node_moving = False
            # 如果在事件发生点存在group（只取层数最高的group），则将item放入group
            if grGroup is not None:
                # 更新被选择的item的父项
                for item in self.scene.grScene.selectedItems():
                    if isinstance(item, GraphicNode) and item.parentItem() is None:
                        grGroup.group.addToGroup(item)
                        print(item.pos(), item.scenePos())
                        grGroup.group.updateArea()

                    elif isinstance(item, GraphicNode) and item.parentItem() is not grGroup:
                        parent = item.parentItem()
                        parent.group.removeFromGroup(item)
                        parent.group.updateArea()
                        grGroup.group.addToGroup(item)
                        grGroup.group.updateArea()

                    elif isinstance(item, GraphicNode) and item.parentItem() is grGroup:
                        grGroup.group.updateArea()

            # 如果在事件发生点不存在group，则将item取出group
            elif grGroup is None:
                for item in self.scene.grScene.selectedItems():
                    if isinstance(item, GraphicNode) and isinstance(item.parentItem(), GraphicItemGroup):
                        grGroup = item.parentItem()
                        grGroup.group.removeFromGroup(item)
                        grGroup.group.updateArea()

            # 更新所有连线
            self.update_group_edges()
            self.scene.History.storeHistory()
            self.itemPressSignal.emit([item])
            super().mouseReleaseEvent(event)
        else:
            self.itemPressSignal.emit([item])
            super().mouseReleaseEvent(event)

    def rightMouseButtonPress(self, event):
        return super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):

        # 当鼠标中键按下时，将产生一个假的鼠标按键松开的事件
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)

        # 变为抓取手势
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # 产生一个鼠标按下左键的假事件
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def get_item_at_click(self, event):
        """ 获取点击位置的图元，无则返回None. """
        pos = event.pos()
        item = self.itemAt(pos)
        return item

    def get_items_at_click(self, event):
        pos = event.pos()
        items = self.items(pos)
        return items

    def get_first_group(self, items):
        for item in items:
            if isinstance(item, GraphicItemGroup):
                return item
        return None

    def get_first_socket(self, items):
        for item in items:
            if isinstance(item, GraphicSocket):
                return item
        return None

    def get_items_at_rubber_select(self):
        area = self.rubberBandRect()
        return self.items(area)  # 返回一个所有选中图元的列表，对此操作即可

    def update_group_edges(self):
        edges = copy.copy(self.scene.edges)
        for grEdge in edges:
            if grEdge.edge.start_socket.parentItem().__class__ == grEdge.edge.end_socket.parentItem().__class__:
                if grEdge.edge.start_socket.parentItem().parentItem() != grEdge.edge.end_socket.parentItem().parentItem():
                    grEdge.edge.remove()
                else:
                    grEdge.edge.update_positions()
            elif grEdge.edge.start_socket.socket.index == 1 and grEdge.edge.start_socket.parentItem() != grEdge.edge.end_socket.parentItem().parentItem():
                grEdge.edge.remove()
            elif grEdge.edge.end_socket.socket.index == 1 and grEdge.edge.end_socket.parentItem() != grEdge.edge.start_socket.parentItem().parentItem():
                grEdge.edge.remove()
            else:
                grEdge.edge.update_positions()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('attribute') or event.mimeData().hasFormat('markSymbol'):
            event.acceptProposedAction()
        else:
            print(" ... denied drag enter event")
            event.setAccepted(False)

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        item = self.get_item_at_click(event)
        print(item)
        if event.mimeData().hasFormat('markSymbol'):
            eventData = event.mimeData().data('markSymbol')
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            markSymbol = dataStream.readQString()

            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            if markSymbol == 'Item Group':
                group = Group(self.scene)
                group.grGroup.setPos(scene_position.x(), scene_position.y())
                self.scene.History.storeHistory()

            else:
                way = globals()[markSymbol]()
                attribute = way.get_attribute()
                print(attribute)
                node = Node(self.scene, attribute)
                node.grNode.setPos(scene_position.x(), scene_position.y())
                self.scene.History.storeHistory()

        elif event.mimeData().hasFormat('attribute'):
            eventData = event.mimeData().data('attribute')
            dataStream = QDataStream(eventData, QIODevice.ReadOnly)
            attribute_str = dataStream.readQString()
            attribute = json.loads(attribute_str)

            mouse_position = event.pos()
            scene_position = self.scene.grScene.views()[0].mapToScene(mouse_position)

            node = Node(self.scene, attribute=attribute)
            node.grNode.setPos(scene_position.x(), scene_position.y())
            if isinstance(item, GraphicItemGroup):
                item.group.addToGroup(node.grNode)
                item.group.updateArea()
            self.scene.History.storeHistory()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_N:
            # item = GraphicItem()
            # item = GraphicNode(title='Node Graphics Item')
            item = Node(self.scene, attribute={'name': 'T_mixer', 'width': 200, 'hight': 100, 'roundsize': 10, 'sockets': [
                {'position': [0, 1], 'pos': [0, 50]}, {'position': [0, 1], 'pos':[100, 0]}
            ], 'pixmaps': [
                {'way': 'Model.png', 'pos': [100, 0]}, {'way': 'Model.png', 'pos':[0, 0]}
                           ]})
            self.scene.History.storeHistory()
            #item.setPos(100, 0)
            # self.gr_scene.add_node(item)
        if event.key() == Qt.Key_E:
            print(self.scene.nodes)
            for i in self.scene.nodes:
                print(i.node.to_string())
            print(self.scene.edges)
            for i in self.scene.edges:
                print(i.edge.to_string())


    def wheelEvent(self, event):
        # 计算缩放系数
        zoomOutFactor = 1 / self.zoomInFactor

        # 计算缩放
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]:
            self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]:
            self.zoom, clamped = self.zoomRange[1], True

        # 设置场景比例
        if not clamped or self.zoomClamp:
            self.scale(zoomFactor, zoomFactor)
