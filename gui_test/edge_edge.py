from gui_test.edge_setting import GraphicEdge
from gui_test.node_setting import GraphicNode, GraphicSocket

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2


class Edge:
    def __init__(self, scene, start_socket, end_socket, attribute={}):

        self.id = id(self)

        self.scene = scene
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.attribute = attribute
        self.width = 10

        self.grEdge = GraphicEdge(self)

        self.close_sockets()

        self.store()

        if self.start_socket is not None:
            self.update_positions()

    def close_sockets(self):
        if self.start_socket is not None and self.end_socket is not None:
            self.start_socket.socket.op_st = False
            self.start_socket.socket.edge = self
            self.end_socket.socket.op_st = False
            self.end_socket.socket.edge = self

    def setWidth(self, width):
        self.width = width

    # 最终保存进scene
    def store(self):
        self.scene.add_edge(self.grEdge)

    def update_positions(self):
        self.grEdge.set_posSource(self.start_socket.scenePos().x(),
                                  self.start_socket.scenePos().y())

        # 如果结束位置图元也存在，则做同样操作
        if self.end_socket is not None:
            self.grEdge.set_posDestination(self.end_socket.scenePos().x(),
                                           self.end_socket.scenePos().y())
        self.grEdge.update()

    def remove_from_current_items(self):
        if self.end_socket is not None:
            # 与删除图元相连的线被删除时开启线两端的插口
            self.start_socket.socket.op_st = True
            self.start_socket.socket.edge = None
            self.end_socket.socket.op_st = True
            self.end_socket.socket.edge = None
        self.end_socket = None
        self.start_socket = None

    # 移除线条
    def remove(self):
        self.remove_from_current_items()
        self.scene.remove_edge(self.grEdge)
        self.grEdge = None

    def to_string(self):
        edge = {}
        edge['id'] = self.id
        edge['Type'] = self.__class__.__name__
        edge['line_width'] = self.width
        edge['attribute'] = self.attribute
        edge['side_sockets_id'] = []
        edge['side_sockets_id'].append(self.start_socket.socket.id)
        edge['side_sockets_id'].append(self.end_socket.socket.id)
        return edge

    def to_hashmap(self, data, hashmap={}):
        hashmap[data['id']] = self