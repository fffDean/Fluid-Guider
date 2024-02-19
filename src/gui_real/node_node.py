from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QPainterPath
from gui_real.Item import GraphicItem
from gui_real.node_setting import GraphicNode, GraphicSocket
from gui_real.hole_setting import GraphicHoleSocket, GraphicSocket2
from gui_real.hole_hole import HoleSocket
from gui_real.edge_edge import Edge
from model_make.cq_code import *

import cadquery as cq


class Node(QObject):
    symbolAttributeSignal = Signal()
    realAttributeSignal = Signal(dict)

    def __init__(self, scene, attribute):
        super().__init__()

        self.id = id(self)
        self.function = None
        self.default_mark = None
        self.default_path = QPainterPath()

        self.scene = scene
        self.layer = 0
        self.threeDModel = attribute['3DModel']
        self.transformpoint = attribute['transformpoint']  # 旋转中心

        self.attribute = attribute
        self.attribute_real = {}
        if 'default_class' in attribute:
            name = attribute['default_class']
            default_mark = globals()[name]()
            default_mark.set_attribute(self.attribute)
            self.default_mark = default_mark
            self.default_path = default_mark.get_real_path()
            self.attribute = self.default_mark.get_attribute()
        self.name = attribute['name']

        self.attribute_real['name'] = self.name
        self.attribute_real['default_pen_width'] = attribute['default_pen_width']
        self.attribute_real['area'] = [2, 2]
        self.attribute_real['roundsize'] = 0
        self.attribute_real['3DModel'] = attribute['3DModel']
        self.attribute_real['transformpoint'] = attribute['transformpoint']
        self.attribute_real['pixmaps'] = self.attribute['pixmaps']
        self.attribute_real['sockets'] = self.attribute['sockets']
        self.attribute_real['zValue_upper'] = self.attribute['zValue_upper']
        self.attribute_real['zValue_lower'] = self.attribute['zValue_lower']
        self.grNode = GraphicNode(self, self.attribute_real)

        self.scene.add_node(self.grNode)
        self.scene.layers[self.layer].append(self.grNode)

        # self.scene.addItem(self.grNode)

        self.socket_spacing = 22

        self.sockets = []
        self.graphics = []

        for pixmap_message in self.attribute['pixmaps']:
            pixmap_message_real = {'way': pixmap_message['way'],
                                   'area': pixmap_message['real_area'],
                                   'offset': pixmap_message['offset'],
                                   'transformpoint': self.transformpoint,
                                   'pos': pixmap_message['real_pos']
                                   }
            picture = GraphicItem(pixmap_message_real, self.grNode)
            picture.setPos(pixmap_message['real_pos'][0], pixmap_message['real_pos'][1])
            self.graphics.append(picture)

        # 插口设置项
        for socket_message in self.attribute['sockets']:
            socket = Socket(node=self)
            socket.grSocket.setPos(socket_message['real_pos'][0] - self.transformpoint[0], socket_message['real_pos'][1] - self.transformpoint[1])
            self.sockets.append(socket.grSocket)

    def setup(self):
        if 'default_class' in self.attribute:
            self.default_mark.set_attribute(self.attribute)
            self.default_path = self.default_mark.get_real_path()
            self.attribute = self.default_mark.get_attribute()
        self.threeDModel = self.attribute['3DModel']
        self.transformpoint = self.attribute['transformpoint']  # 旋转中心
        self.attribute_real = {}
        self.attribute_real['name'] = self.name
        self.attribute_real['default_pen_width'] = self.attribute['default_pen_width']
        self.attribute_real['area'] = [2, 2]
        self.attribute_real['roundsize'] = 0
        self.attribute_real['3DModel'] = self.attribute['3DModel']
        self.attribute_real['transformpoint'] = self.attribute['transformpoint']
        self.attribute_real['pixmaps'] = self.attribute['pixmaps']
        self.attribute_real['sockets'] = self.attribute['sockets']
        self.attribute_real['zValue_upper'] = self.attribute['zValue_upper']
        self.attribute_real['zValue_lower'] = self.attribute['zValue_lower']
        self.grNode.set_attribute(self.attribute_real)

        for i in range(len(self.sockets)):
            socket_message = self.attribute['sockets'][i]
            self.sockets[i].setPos(socket_message['real_pos'][0] - self.transformpoint[0], socket_message['real_pos'][1] - self.transformpoint[1])


    def set_id(self):
        self.id = id(self)

    def set_function(self, function):
        self.function = function

    def set_layer(self, layer):
        for layerC in self.scene.layers:
            if self.grNode in layerC:
                layerC.remove(self.grNode)
        self.layer = layer
        self.scene.layers[self.layer].append(self.grNode)
        count = 0
        countUpper = self.attribute['zValue_upper'] - self.scene.layersValue[self.layer]/2
        countLower = self.attribute['zValue_lower'] - self.scene.layersValue[self.layer]/2
        while True:
            count += 1
            if int(countUpper) >= 0 and self.layer - count >= 0 and int(countLower) >= 0 and self.layer + count <= len(self.scene.layers)-1:
                countUpper -= self.scene.layersValue[self.layer - count]
                self.scene.layers[self.layer - count].append(self.grNode)
                countLower -= self.scene.layersValue[self.layer + count]
                self.scene.layers[self.layer + count].append(self.grNode)
            elif int(countUpper) >= 0 and self.layer - count >= 0:
                countUpper -= self.scene.layersValue[self.layer - count]
                self.scene.layers[self.layer - count].append(self.grNode)
            elif int(countLower) >= 0 and self.layer + count <= len(self.scene.layers)-1:
                countLower -= self.scene.layersValue[self.layer + count]
                self.scene.layers[self.layer + count].append(self.grNode)
            else:
                break

        for grSocket in self.sockets:
            grSocket.socket.set_layer(self.layer)
        for grSocket in self.sockets:
            if grSocket.socket.edge is not None:
                opSocket = grSocket.socket.edge.opSocket(grSocket)
                opParent = opSocket.parentItem()
                if isinstance(opParent, GraphicHoleSocket):
                    opParent.hole.reset_layer()
                    if opParent.hole.layerMax == opParent.hole.layerMin:
                        if isinstance(opParent.hole.opSocket(grSocket), GraphicSocket):
                            width = opParent.hole.socket1.edge.width
                            opParent.hole.socket1.edge.remove()
                            opParent.hole.socket2.edge.remove()
                            self.scene.remove_hole(opParent)
                            edge = Edge(self.scene, opParent.hole.socket1.grSocket, opParent.hole.socket2.grSocket)
                            edge.setWidth(width)
                        elif isinstance(opParent.hole.opSocket(grSocket), GraphicSocket2):
                            print(opParent.hole.opSocket(grSocket).parentItem())
                            hole2 = opParent.hole.opSocket(grSocket).parentItem().hole
                            grSocket2 = hole2.opSocket(opParent.hole.opMySocket(opSocket))

                            if grSocket2.socket == hole2.socket1:
                                hole2.set_socket(grSocket2, grSocket)
                            elif grSocket2.socket == hole2.socket2:
                                hole2.set_socket(grSocket, grSocket2)

                            width = opParent.hole.socket1.edge.width
                            opParent.hole.socket1.edge.remove()
                            opParent.hole.socket2.edge.remove()
                            self.scene.remove_hole(opParent)
                            edge = Edge(self.scene, opParent.hole.socket1.grSocket, opParent.hole.socket2.grSocket)
                            edge.setWidth(width)

                elif isinstance(opParent, GraphicNode):
                    if opSocket.socket.layer != grSocket.socket.layer:
                        width = grSocket.socket.edge.width
                        self.scene.remove_edge(grSocket.socket.edge.grEdge)
                        hole = HoleSocket(self.scene, grSocket, opSocket)
                        x = grSocket.scenePos().x()/2 + opSocket.scenePos().x()/2
                        y = grSocket.scenePos().y()/2 + opSocket.scenePos().y()/2
                        hole.grHole.setPos(x, y)
                        edge1 = Edge(self.scene, grSocket, hole.mySocket1.grSocket)
                        edge1.setWidth(width)
                        edge2 = Edge(self.scene, opSocket, hole.mySocket2.grSocket)
                        edge2.setWidth(width)

    def get_3Dmodel(self):
        model = cq.Workplane()
        z_value = self.scene.getZValue(self.layer)
        if self.default_mark:
            model += self.default_mark.get_model().rotate([0, 0, 0], [0, 0, 1],
                                                                            self.grNode.rotation()).translate(
                [self.grNode.scenePos().x()/10, self.grNode.scenePos().y()/10, z_value/10])
        elif self.threeDModel != '':
            model += cq.importers.importStep(self.threeDModel).rotate([0, 0, 0], [0, 0, 1],
                                                                                        self.grNode.rotation()).translate(
                [self.grNode.scenePos().x()/10, self.grNode.scenePos().y()/10, z_value/10])
        for grSocket in self.sockets:
            if grSocket.socket.edge:
                width = grSocket.socket.edge.width
                model += cq.Workplane().polygon(16, width/10).extrude(width/10).translate(
                    [grSocket.scenePos().x()/10, grSocket.scenePos().y()/10, z_value/10 - width / 20])
        return model


    def to_string(self):
        node = {}
        node['id'] = self.id
        node['Type'] = self.__class__.__name__
        node['function'] = self.function
        node['pos'] = [self.grNode.scenePos().x(), self.grNode.scenePos().y()]
        node['rotation'] = self.grNode.rotation()
        node['layer'] = self.layer
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
BOTTOM = [0, 1]


class Socket:
    def __init__(self, node, index=0, position=LEFT):

        self.id = id(self)
        self.node = node
        self.index = index
        self.position = position
        self.layer = 0

        self.edge = None
        self.op_st = True

        self.grSocket = GraphicSocket(self, self.node.grNode)

        #self.grSocket.setPos(*self.node.getSocketPosition(index, position))

    def set_layer(self, layer):
        self.layer = layer

    def set_id(self):
        self.id = id(self)

    def set_edge(self, edge):
        self.edge = edge

    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position)

    def to_string(self):
        socket = {}
        socket['id'] = self.id
        socket['Type'] = self.__class__.__name__
        socket['layer'] = self.layer
        return socket

    def to_hashmap(self, data, hashmap={}):
        hashmap[data['id']] = self
