from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QRectF, QPointF, QDataStream, QIODevice, Qt
from PySide6.QtGui import QPainterPath, QPen, QColor, QBrush, QFont

from gui_test.node_setting import GraphicNode
from gui_test.node_node import Node, Socket
import json


class Group:
    def __init__(self, scene):
        self.id = id(self)

        self.sockets = []
        self.nodes = []
        self.edges = []
        self.loopTimes = 1

        self.scene = scene
        self.grGroup = GraphicItemGroup(self)
        self.scene.add_group(self.grGroup)

        self.socket1_outside = Socket(node=self, position=[-1, 0])
        self.socket1_outside.grSocket.setPos(-11, self.grGroup.height/2)
        self.sockets.append(self.socket1_outside.grSocket)
        self.socket1_inside = Socket(node=self, index=1, position=[1, 0])
        self.socket1_inside.grSocket.setPos(11, self.grGroup.height/2)
        self.sockets.append(self.socket1_inside.grSocket)
        self.socket2_outside = Socket(node=self, position=[1, 0])
        self.socket2_outside.grSocket.setPos(self.grGroup.width + 11, self.grGroup.height / 2)
        self.sockets.append(self.socket2_outside.grSocket)
        self.socket2_inside = Socket(node=self, index=1, position=[-1, 0])
        self.socket2_inside.grSocket.setPos(self.grGroup.width - 11, self.grGroup.height / 2)
        self.sockets.append(self.socket2_inside.grSocket)

    def intersects(self, *poses_or_rect):
        outline = QPainterPath()
        outline.addRoundedRect(self.grGroup.scenePos().x() - 5, self.grGroup.scenePos().y() - 5, self.grGroup.width + 10, self.grGroup.height + 10, self.grGroup.edge_size, self.grGroup.edge_size)
        inside = QPainterPath()
        inside.addRoundedRect(self.grGroup.scenePos().x() + 5, self.grGroup.scenePos().y() + 5, self.grGroup.width - 10, self.grGroup.height - 10, self.grGroup.edge_size, self.grGroup.edge_size)
        outline = outline.subtracted(inside)
        if len(poses_or_rect) == 2:
            start_pos = poses_or_rect[0]
            end_pos = poses_or_rect[1]
            path = QPainterPath(QPointF(start_pos[0], start_pos[1]))
            path.lineTo(QPointF(end_pos[0], end_pos[1]))
            return outline.intersects(path)
        elif len(poses_or_rect) == 1:
            rect = poses_or_rect[0]
            return outline.intersects(rect)


    def updateArea(self):
        old_x = self.grGroup.scenePos().x()
        old_y = self.grGroup.scenePos().y()
        if self.nodes == []:
            self.grGroup.width = 200
            self.grGroup.height = 200
            self.socket1_outside.grSocket.setPos(-11, self.grGroup.height / 2)
            self.socket1_inside.grSocket.setPos(11, self.grGroup.height / 2)
            self.socket2_outside.grSocket.setPos(self.grGroup.width + 11, self.grGroup.height / 2)
            self.socket2_inside.grSocket.setPos(self.grGroup.width - 11, self.grGroup.height / 2)
        else:
            x, y, length_x, length_y = 64000, 64000, 0, 0
            for node in self.nodes:
                x = node.scenePos().x() if node.scenePos().x() <= x else x
                y = node.scenePos().y() if node.scenePos().y() <= y else y
            for node in self.nodes:
                distance_x = node.scenePos().x() + node.width - x
                length_x = distance_x if distance_x >= length_x else length_x
                distance_y = node.scenePos().y() + node.height - y
                length_y = distance_y if distance_y >= length_y else length_y

            self.grGroup.setPos(x - 50, y - 50 - 40)
            self.grGroup.width = length_x + 100
            self.grGroup.height = length_y + 100 + 40

            self.socket1_outside.grSocket.setPos(-11, self.grGroup.height/2)
            self.socket1_inside.grSocket.setPos(11, self.grGroup.height/2)
            self.socket2_outside.grSocket.setPos(self.grGroup.width + 11, self.grGroup.height/2)
            self.socket2_inside.grSocket.setPos(self.grGroup.width - 11, self.grGroup.height/2)

            for grNode in self.nodes:
                node_x = grNode.pos().x() - (x - 50 - old_x)
                node_y = grNode.pos().y() - (y - 50 - 40 - old_y)
                grNode.setPos(node_x, node_y)
            for grEdge in self.scene.edges:
                grEdge.edge.update_positions()

    def addToGroup(self, item):
        self.nodes.append(item)
        # 需要对原位置做出修正（设置父项后的坐标=设置前坐标+父项坐标）
        item.setPos(item.pos().x() - self.grGroup.pos().x(), item.pos().y() - self.grGroup.pos().y())
        item.setParentItem(self.grGroup)

    def removeFromGroup(self, item):
        self.nodes.remove(item)
        item.setParentItem(None)
        # 需要对原位置做出修正（删除父项后的坐标=删除前坐标-父项坐标）
        item.setPos(item.pos().x() + self.grGroup.pos().x(), item.pos().y() + self.grGroup.pos().y())

    def setLoopTimes(self, times):
        self.loopTimes = times

    def to_string(self):
        group = {}
        group['id'] = self.id
        group['Type'] = self.__class__.__name__
        group['pos'] = [self.grGroup.pos().x(), self.grGroup.pos().y()]
        group['loop_times'] = self.loopTimes
        group['sockets'] = []
        for grSocket in self.sockets:
            group['sockets'].append(grSocket.socket.to_string())
        group['child_item_id'] = []
        for grNode in self.nodes:
            group['child_item_id'].append(grNode.node.id)

        return group

    def to_hashmap(self, data, hashmap={}):
        hashmap[data['id']] = self

        for socket_data in data['sockets']:
            number = data['sockets'].index(socket_data)
            self.sockets[number].socket.to_hashmap(socket_data, hashmap)


class GraphicItemGroup(QGraphicsItem):
    def __init__(self, group, parent=None):
        super().__init__(parent)
        self.group = group

        self._pen_title = QPen(QColor("#55FF7700"))
        self._pen_title.setWidth(10)
        self._pen_default = QPen(QColor("#aaffffff"))
        self._pen_default.setWidth(10)
        self._pen_selected = QPen(QColor("#aaffa637"))
        self._pen_selected.setWidth(10)
        self._pen_socket = QPen(QColor("#aaFF7700"))
        self._pen_socket.setWidth(1)

        self._brush_title = QBrush(QColor("#ff313131"))
        self._brush_text = QBrush(QColor("#ffffffff"))
        self._brush_background = QBrush(QColor("#aaaaaaaa"))
        self._brush_socket = QBrush(QColor("#FFFF7700"))

        self._text_font = QFont()
        self._text_font.setFamily('Microsoft YaHei')
        self._text_font.setPointSize(15)

        self.initUI()
        #self.setBoundingRegionGranularity()

        self.width = 200
        self.height = 200
        self.edge_size = 5

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()


    def paint(self, painter, option, widget=None):

        self.path_outline = QPainterPath()
        self.path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(self._brush_background)
        painter.drawPath(self.path_outline.simplified())

        self.socket_connector = QPainterPath()
        self.socket_connector.addRect(-11, self.height/2 - 6, 22, 12)
        self.socket_connector.addRect(self.width - 11, self.height/2 - 6, 22, 12)
        painter.setPen(self._pen_socket)
        painter.setBrush(self._brush_socket)
        painter.drawPath(self.socket_connector.simplified())

        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, 40, self.edge_size, self.edge_size)
        path_title.addRect(0, 40 - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, 40 - self.edge_size, self.edge_size,
                           self.edge_size)
        painter.setPen(self._pen_title)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        path_text = QPainterPath()
        path_text.addText(10, 27, self._text_font, '·Loop [{}] times'.format(self.group.loopTimes))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_text)
        painter.drawPath(path_text.simplified())

    def initUI(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setZValue(2)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # 如果图元被选中，就更新连线，这里更新的是所有。可以优化，只更新连接在图元上的。
        if self.isSelected():
            for grEdge in self.group.scene.edges:
                grEdge.edge.update_positions()
