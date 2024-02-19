from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QGraphicsSimpleTextItem, QGraphicsItem
from PySide6.QtGui import QFont, QBrush, QColor, QPainterPath
from gui_test.Item import GraphicItem
from gui_test.node_setting import GraphicNode, GraphicSocket
from gui_test.edge_edge import Edge
from model_make.cq_code import *


class Node:
    def __init__(self, scene, attribute={}):
        self.id = id(self)
        self.function = None
        self.default_mark = None
        self.default_path = []

        self.scene = scene

        self.attribute = attribute

        self.grNode = GraphicNode(self, attribute)

        self.scene.add_node(self.grNode)
        # self.scene.addItem(self.grNode)
        self.sockets = []
        self.pixmaps = []
        self.setup()

        self.textGraphic = QGraphicsSimpleTextItem(self.grNode)
        self.textGraphic.setText('new node')
        font = QFont()
        font.setPixelSize(30)
        self.textGraphic.setFont(font)
        self.textGraphic.setBrush(QBrush(QColor("#001000")))
        self.textGraphic.setPos(self.grNode.width / 4, self.grNode.height + 10)
        self.textGraphic.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def setup(self):
        edge_list = []
        for grSocket in self.sockets:
            if grSocket.socket.edge:
                width = grSocket.socket.edge.width
                if grSocket == grSocket.socket.edge.start_socket:
                    edge_list.append([self.sockets.index(grSocket), grSocket.socket.edge.end_socket, grSocket.socket.edge.attribute, width])
                else:
                    edge_list.append([grSocket.socket.edge.start_socket, self.sockets.index(grSocket), grSocket.socket.edge.attribute, width])
                grSocket.socket.edge.remove()
            self.scene.grScene.removeItem(grSocket)
        for grPixmap in self.pixmaps:
            self.scene.grScene.removeItem(grPixmap)

        if 'default_class' in self.attribute:
            name = self.attribute['default_class']
            default_mark = globals()[name]()
            default_mark.set_attribute(self.attribute)
            self.default_mark = default_mark
            self.default_path = default_mark.get_bluemap_path()
            self.attribute = self.default_mark.get_attribute()
        self.grNode.set_attribute(self.attribute)

        self.socket_spacing = 22

        self.sockets = []
        self.pixmaps = []

        for pixmap_message in self.attribute['pixmaps']:
            picture = GraphicItem(pixmap_message, self.grNode)
            picture.setPos(pixmap_message['pos'][0], pixmap_message['pos'][1])
            self.pixmaps.append(picture)

        # 插口设置项
        for socket_message in self.attribute['sockets']:
            socket = Socket(node=self, position=socket_message['position'])
            socket.grSocket.setPos(socket_message['pos'][0], socket_message['pos'][1])
            self.sockets.append(socket.grSocket)

        for edge_message in edge_list:
            if isinstance(edge_message[0], int):
                start_socket = self.sockets[edge_message[0]]
                end_socket = edge_message[1]
                attribute = edge_message[2]
                width = edge_message[3]
            else:
                start_socket = edge_message[0]
                end_socket = self.sockets[edge_message[1]]
                attribute = edge_message[2]
                width = edge_message[3]
            edge = Edge(self.scene, start_socket, end_socket, attribute)
            edge.setWidth(width)

    def set_default_mark(self, default_mark):
        self.attribute = default_mark.attribute()
        self.setup()

    def set_function(self, function):
        self.function = function

    def set_id(self):
        self.id = id(self)

    def set_text(self, text):
        self.text = text
    '''
    def getSocketPosition(self, index, position):
        if position in (LEFT_TOP, LEFT_BOTTON):
            x = 0
        else:
            x = self.grNode.width
        if position in (LEFT_BOTTON, RIGHT_BOTTON):
            y = -index * self.socket_spacing + self.grNode.height - self.grNode.padding - self.grNode.edge_size
        else:
            y = index * self.socket_spacing + self.grNode.title_height + self.grNode.padding + self.grNode.edge_size

        return [x, y]
    '''
    def to_string(self):
        node = {}
        node['id'] = self.id
        node['Type'] = self.__class__.__name__
        node['function'] = self.function
        node['text'] = self.textGraphic.text()
        node['pos'] = [self.grNode.scenePos().x(), self.grNode.scenePos().y()]
        node['attribute'] = self.attribute
        node['sockets'] = []
        for socket in self.sockets:
            node['sockets'].append(socket.socket.to_string())
        return node

    def to_hashmap(self, data, hashmap={}):

        hashmap[data['id']] = self

        for socket_data in data['sockets']:
            number = data['sockets'].index(socket_data)
            self.sockets[number].socket.to_hashmap(socket_data, hashmap)





LEFT = [-1, 0]
RIGHT = [1, 0]
TOP = [0, -1]
BOTTON = [0, 1]


# 标记：index=0表示节点正常的对外接口
#      index=1表示节点的对内接口，比如group的两个inside接口
class Socket():
    def __init__(self, node, index=0, position=LEFT):

        self.id = id(self)
        self.node = node
        self.edge = None
        self.index = index
        self.position = position

        self.op_st = True
        if hasattr(self.node, 'grNode'):
            self.grSocket = GraphicSocket(self, self.node.grNode)

        elif hasattr(self.node, 'grGroup'):
            self.grSocket = GraphicSocket(self, self.node.grGroup)

        #self.grSocket.setPos(*self.node.getSocketPosition(index, position))


    def set_id(self):
        self.id = id(self)

    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position)

    def setConnectedEdge(self, edge=None):
        self.edge = edge

    def to_string(self):
        socket = {}
        socket['id'] = self.id
        socket['Type'] = self.__class__.__name__
        return socket

    def to_hashmap(self, data, hashmap={}):

        hashmap[data['id']] = self




