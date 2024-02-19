from PySide6.QtGui import Qt, QColor, QPen, QPainter, QMouseEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtCore import QLine, Signal, QEvent

from gui_real.node_setting import GraphicNode, GraphicSocket
from gui_real.hole_hole import HoleSocket
from gui_real.hole_setting import GraphicSocket2
from gui_real.edge_edge import Edge
from gui_real.edge_setting import GraphicEdge, GraphicCantSeeSocket
from gui_real.baseShape_baseShape import baseShape, Rect
from gui_real.baseShape_setting import GraphicBaseShape
from gui_real.hole_setting import GraphicHoleSocket
import math
import gc
import copy

rectMakeMode = 0
lineMakeMode = 1
holeMakeMode = 2


class GraphicScene(QGraphicsScene):

    def __init__(self, scene, parent=None):
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
        self.setGrScene(64000, 64000)
        # self.setSceneRect(-32000, -32000, 64000, 64000)
        # self.scene_width, self.scene_height = 64000, 64000
        # self.setSceneRect(-self.scene_width // 2, -self.scene_height // 2, self.scene_width, self.scene_height)

        self.scene = scene

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
        self.scene.nodes.remove(grNode)
        self.removeItem(grNode)
        del grNode.node
        del grNode
        gc.collect()

    def add_hole(self, grHole):
        self.scene.holes.append(grHole)
        self.addItem(grHole)

    def remove_hole(self, grHole):
        for i in range(grHole.hole.layerMin, grHole.hole.layerMax + 1):
            self.scene.layers[i].remove(grHole)
        self.scene.holes.remove(grHole)
        self.removeItem(grHole)

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
        self.zoomRange = [0, 7]    # 缩放区间

        self.edge_enable = False  # 用来记录目前是否可以画线条
        self.drag_edge = None  # 记录拖拽时的线
        self.drag_start_item = None

        #self.pointMoveStart = False
        self.leftCurrentCatchPoint = None
        self.rightCurrentCatchPoint = None

        self.mouseMode = None
        self.graphicDrawing = False
        self.currentEdge = None
        self.currentSocket = None

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

    def setMouseMode(self, mode):
        self.mouseMode = mode

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

    def mouseMoveEvent(self, event):
        if self.mouseMode == rectMakeMode:
            if self.graphicDrawing:
                pos = event.pos()
                point = self.mapToScene(pos)
                graphic = self.scene.baseShape.shapes[-1]
                graphic.mouseEnd(point.x(), point.y())
                self.scene.baseShape.grBaseShape.update()
        elif self.mouseMode == lineMakeMode:
            pos = event.pos()
            point = self.mapToScene(pos)
            if self.currentEdge:
                cant_see_socket = GraphicCantSeeSocket(self.currentEdge.grEdge)
                cant_see_socket.setPos(point)
                self.currentEdge.move_point = [cant_see_socket]
                self.currentEdge.grEdge.update()
                self.scene.grScene.removeItem(cant_see_socket)

            super().mouseMoveEvent(event)

        else:
            super().mouseMoveEvent(event)

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

    def leftMouseButtonPress(self, event):
        item = self.get_item_at_click(event)
        if isinstance(item, GraphicCantSeeSocket):
            # 是否是左右端点
            if item.parentItem().left_catch_point == item:
                self.leftCurrentCatchPoint = item
            elif item.parentItem().right_catch_point == item:
                self.rightCurrentCatchPoint = item

        if self.mouseMode == rectMakeMode:
            pos = event.pos()
            start_point = self.mapToScene(pos)
            graphic = Rect()
            graphic.mouseStart(start_point.x(), start_point.y())
            self.scene.baseShape.addSceneRect(graphic)
            self.scene.baseShape.grBaseShape.update()
            self.graphicDrawing = True

        elif self.mouseMode == holeMakeMode:
            if isinstance(item, GraphicEdge):
                if item.edge.start_socket.socket.layer + 1 <= len(self.scene.layers) - 1:
                    i = item.edge.start_socket.socket.layer + 1
                elif item.edge.start_socket.socket.layer - 1 >= 0:
                    i = item.edge.start_socket.socket.layer - 1
                else:
                    i = None
                if i:
                    socket_start = item.edge.start_socket
                    socket_end = item.edge.end_socket
                    pos = event.pos()
                    point = self.mapToScene(pos)
                    hole1 = HoleSocket(self.scene, socket_start, socket_end)
                    hole1.grHole.setPos(point)
                    hole2 = HoleSocket(self.scene, hole1.mySocket2.grSocket, socket_end)
                    hole2.grHole.setPos(point.x() + 5, point.y() + 5)
                    hole1.set_socket(socket_start, hole2.mySocket1.grSocket)
                    hole1.mySocket2.set_layer(i)
                    hole2.mySocket1.set_layer(i)
                    hole1.reset_layer()
                    hole2.reset_layer()
                    self.scene.add_hole(hole1.grHole)
                    self.scene.add_hole(hole2.grHole)
                    width = item.edge.width
                    self.scene.remove_edge(item)
                    edge1 = Edge(self.scene, socket_start, hole1.mySocket1.grSocket)
                    edge1.setWidth(width)
                    edge2 = Edge(self.scene, hole1.mySocket2.grSocket, hole2.mySocket1.grSocket)
                    edge2.setWidth(width)
                    edge3 = Edge(self.scene, hole2.mySocket2.grSocket, socket_end)
                    edge3.setWidth(width)
            self.scene.setLayer(self.scene.currentLayer)

            self.mouseMode = None

        else:
            self.itemPressSignal.emit([item])
            super().mousePressEvent(event)


    def leftMouseButtonRelease(self, event):
        item = self.get_item_at_click(event)
        if self.leftCurrentCatchPoint:
            if item == self.leftCurrentCatchPoint.parentItem().edge.start_socket:
                self.leftCurrentCatchPoint.setPos(self.leftCurrentCatchPoint.parentItem().edge.start_socket.scenePos())
                self.leftCurrentCatchPoint = None
            else:
                self.leftCurrentCatchPoint = None
        elif self.rightCurrentCatchPoint:
            if item == self.rightCurrentCatchPoint.parentItem().edge.end_socket:
                self.rightCurrentCatchPoint.setPos(self.rightCurrentCatchPoint.parentItem().edge.end_socket.scenePos())
                self.rightCurrentCatchPoint = None
            else:
                self.rightCurrentCatchPoint = None

        if self.mouseMode == rectMakeMode:
            pos = event.pos()
            end_point = self.mapToScene(pos)
            graphic = self.scene.baseShape.shapes[-1]
            graphic.mouseEnd(end_point.x(), end_point.y())
            self.scene.baseShape.grBaseShape.update()
            self.graphicDrawing = False
            self.mouseMode = None
        elif self.mouseMode == lineMakeMode:
            super().mouseReleaseEvent(event)
            items = self.get_items_at_click(event)
            socket = self.get_first_socket(items)
            pos = event.pos()
            point = self.mapToScene(pos)
            if self.currentEdge is None and socket and socket.socket.edge is not None:
                self.currentSocket = socket
                self.currentEdge = socket.socket.edge
                self.currentEdge.restart()

                if self.currentEdge.start_socket == self.currentSocket:
                    cant_see_socket = GraphicCantSeeSocket(self.currentEdge.grEdge)
                    cant_see_socket.setPos(self.currentSocket.scenePos())
                    self.currentEdge.start_point_list.append(cant_see_socket)
                elif self.currentEdge.end_socket == self.currentSocket:
                    cant_see_socket = GraphicCantSeeSocket(self.currentEdge.grEdge)
                    cant_see_socket.setPos(self.currentSocket.scenePos())
                    self.currentEdge.end_point_list.append(cant_see_socket)
                self.currentEdge.grEdge.update()

            elif self.currentEdge:
                if self.currentEdge.start_socket == self.currentSocket:
                    if socket == self.currentEdge.end_socket:
                        cant_see_socket = GraphicCantSeeSocket(self.currentEdge.grEdge)
                        cant_see_socket.setPos(socket.scenePos())
                        self.currentEdge.start_point_list.append(cant_see_socket)
                        self.currentEdge.move_point = []
                        self.currentEdge.grEdge.update()
                        self.currentEdge = None
                        self.currentSocket = None
                        self.mouseMode = None
                    else:
                        cant_see_socket = GraphicCantSeeSocket(self.currentEdge.grEdge)
                        cant_see_socket.setPos(point)
                        self.currentEdge.start_point_list.append(cant_see_socket)
                        self.currentEdge.grEdge.update()
                elif self.currentEdge.end_socket == self.currentSocket:
                    if socket == self.currentEdge.start_socket:
                        cant_see_socket = GraphicCantSeeSocket(self.currentEdge.grEdge)
                        cant_see_socket.setPos(socket.scenePos())
                        self.currentEdge.end_point_list.append(cant_see_socket)
                        self.currentEdge.move_point = []
                        self.currentEdge.grEdge.update()
                        self.currentEdge = None
                        self.currentSocket = None
                        self.mouseMode = None
                    else:
                        cant_see_socket = GraphicCantSeeSocket(self.currentEdge.grEdge)
                        cant_see_socket.setPos(point)
                        self.currentEdge.end_point_list.append(cant_see_socket)
                        self.currentEdge.grEdge.update()

        else:
            super().mouseReleaseEvent(event)


    def rightMouseButtonPress(self, event):
        return super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        return super().mouseReleaseEvent(event)


    def middleMouseButtonPress(self, event):
        # 当鼠标中键按下时，将产生一个假的鼠标按键松开的事件
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)

        # 变为抓取手势
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # 产生一个鼠标按下左键的假事件
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def get_items_at_click(self, event):
        pos = event.pos()
        items = self.items(pos)
        return items

    def get_first_socket(self, items):
        for item in items:
            if isinstance(item, GraphicSocket) and item.isEnabled():
                return item
            elif isinstance(item, GraphicSocket2) and item.socket.canCheck and item.socket.layer == self.scene.currentLayer:
                return item
        return None

    def get_item_at_click(self, event):
        """ 获取点击位置的图元，无则返回None. """
        pos = event.pos()
        item = self.itemAt(pos)
        if item is not None and item.isEnabled():
            return item
        else:
            return None
