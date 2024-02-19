from gui_real.edge_setting import GraphicEdge
from math import pi, sqrt, degrees, atan2, sin, cos
import cadquery as cq

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2


class Edge:
    def __init__(self, scene, start_socket, end_socket, attribute={}):

        self.id = id(self)
        self.layer = None
        self.start_point_list = []
        self.end_point_list = []
        self.move_point = []
        self.point_list = []

        self.scene = scene
        self.start_socket = start_socket    # grSocket or None
        self.end_socket = end_socket    # grSocket or None

        self.attribute = attribute
        self.width = 6

        self.grEdge = GraphicEdge(self)

        self.close_sockets()
        self.set_layer()
        self.store()

        if self.start_socket is not None:
            self.update_positions()

    def opSocket(self, grSocket):
        if grSocket == self.start_socket:
            return self.end_socket
        elif grSocket == self.end_socket:
            return self.start_socket

    def set_layer(self):
        self.layer = self.start_socket.socket.layer

    def close_sockets(self):
        if self.start_socket is not None and self.end_socket is not None:
            self.start_socket.socket.op_st = False
            self.end_socket.socket.op_st = False
            self.start_socket.socket.set_edge(self)
            self.end_socket.socket.set_edge(self)

    def setWidth(self, width):
        self.width = width
        self.grEdge.update()

    # 最终保存进scene
    def store(self):
        self.scene.add_edge(self.grEdge)

    def restart(self):
        for item in self.point_list:
            self.scene.grScene.removeItem(item)
        self.start_point_list = []
        self.end_point_list = []
        self.move_point = []
        self.point_list = []
        self.grEdge.left_catch_point = None
        self.grEdge.right_catch_point = None
        self.grEdge.update()

    def getPointList(self):
        self.point_list = self.start_point_list + self.move_point + self.end_point_list[::-1]
        return self.point_list

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
            self.end_socket.socket.op_st = True
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
        edge['layer'] = self.layer
        edge['line_width'] = self.width
        edge['attribute'] = self.attribute
        edge['side_sockets_id'] = []
        edge['side_sockets_id'].append(self.start_socket.socket.id)
        edge['side_sockets_id'].append(self.end_socket.socket.id)
        edge['start_point_list'] = []
        for grSocket in self.start_point_list:
            edge['start_point_list'].append([grSocket.scenePos().x(), grSocket.scenePos().y()])
        edge['end_point_list'] = []
        for grSocket in self.end_point_list:
            edge['end_point_list'].append([grSocket.scenePos().x(), grSocket.scenePos().y()])
        edge['move_point'] = []
        for grSocket in self.move_point:
            edge['move_point'].append([grSocket.scenePos().x(), grSocket.scenePos().y()])

        return edge

    def to_hashmap(self, data, hashmap={}):
        hashmap[data['id']] = self

    def getZValue(self):
        z_value = -self.scene.layersValue[self.layer]/2
        for i in range(self.layer):
            z_value -= self.scene.layersValue[i]
        return z_value

    def get_path(self):
        point_list = self.getPointList()
        path_point = []
        z_value = self.getZValue()
        for grSocket in point_list:
            path_point.append([grSocket.scenePos().x()/10, grSocket.scenePos().y()/10, z_value/10])
        return path_point

    def getEdgeModel(self, p_list, width=1.0):
        d = 1*0.3
        for i in range(len(p_list)-1):
            new_d = sqrt((p_list[i+1][0] - p_list[i][0])**2 + (p_list[i+1][1] - p_list[i][1])**2)/2
            if new_d <= d:
                d = new_d
        source = p_list[0].copy()
        for pos in p_list:
            pos[0] -= source[0]
            pos[1] -= source[1]
        # 旋转矩阵
        main_pos = p_list[1].copy()
        R = sqrt(main_pos[0] ** 2 + main_pos[1] ** 2)
        R_sin = main_pos[1] / R
        R_cos = main_pos[0] / R
        deg = degrees(atan2(main_pos[1], main_pos[0]))
        R_A = [[R_cos, R_sin], [-R_sin, R_cos]]

        p_list[0] = [p_list[0][0] - 2 * R_cos, p_list[0][1] - 2 * R_sin]
        translatePos = [source[0] + p_list[0][0], source[1] + p_list[0][1], source[2]]
        source = p_list[0].copy()
        for pos in p_list:
            pos[0] -= source[0]
            pos[1] -= source[1]

        for pos in p_list:
            pos_copy = pos.copy()
            pos[0] = R_cos * pos_copy[0] + R_sin * pos_copy[1]
            pos[1] = R_cos * pos_copy[1] - R_sin * pos_copy[0]
        path = cq.Workplane('XY')
        for i in range(1, len(p_list) - 1):  # if len(p_list)>=3
            rad1 = atan2(p_list[i - 1][1] - p_list[i][1], p_list[i - 1][0] - p_list[i][0])
            rad2 = atan2(p_list[i + 1][1] - p_list[i][1], p_list[i + 1][0] - p_list[i][0])
            circle_start = [p_list[i][0] + d * cos(rad1), p_list[i][1] + d * sin(rad1)]
            circle_end = [p_list[i][0] + d * cos(rad2), p_list[i][1] + d * sin(rad2)]
            print(rad1, rad2)
            if round(abs(rad1 - rad2), 2) != 3.14:
                path = path.lineTo(circle_start[0], circle_start[1]).tangentArcPoint(circle_end, relative=False)
            else:
                path = path.lineTo(circle_start[0], circle_start[1]).lineTo(circle_end[0], circle_end[1])
        path = path.lineTo(p_list[-1][0], p_list[-1][1])
        # result = cq.Workplane('YZ').polygon(16, width).sweep(path).rotate([0, 0, 1], [0, 0, 0], -deg).translate(source)
        result = cq.Workplane('YZ').polygon(16, width).sweep(path).rotate([0, 0, 1], [0, 0, 0], -deg)
        cutResult = cq.Workplane('YZ').polygon(16, width).extrude(2).rotate([0, 0, 1], [0, 0, 0], -deg)
        result = result - cutResult
        result = result.translate(translatePos)
        return result

    def get_3Dmodel(self):
        model = cq.Workplane()
        path_point = self.get_path()
        if path_point:
            model += self.getEdgeModel(path_point, self.width/10)
            return model
        else:
            return False
