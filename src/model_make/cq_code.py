import math

import cadquery as cq
from PySide6.QtGui import QPainterPath
from PySide6.QtCore import QPointF
from math import sqrt, atan2, degrees, sin, cos, radians

bian = 16


# diameter是一个列表，与get***path返回的列表一一对应
class U_way:
    def __init__(self, diameter=10, height=100, distance=25, total_way=500):
        self.diameter = diameter
        self.height = height
        self.distance = distance
        self.total_way = total_way
        self.path_point = [[0, 0]]
        self.setup()

    def setup(self):
        self.path_point = [[0, 0], [5, 5]]
        count = self.total_way // (self.height + self.distance)
        for i in range(int(count)):
            self.path_point.append([5 + i * self.distance, 5 + self.height / 2 + self.height * (-1) ** i / 2])
            self.path_point.append([5 + i * self.distance + self.distance, 5 + self.height / 2 + self.height * (-1) ** i / 2])
        self.path_point.append([self.path_point[-1][0] + 5, self.path_point[-1][1] + 5])
        # path = cq.Workplane().polyline(self.path_point)
        # self.way = cq.Workplane('XZ').polygon(bian, self.diameter).sweep(path)

    def set_attribute(self, attribute):
        self.diameter = attribute['default_diameter']
        self.height = attribute['default_height']
        self.distance = attribute['default_distance']
        self.total_way = attribute['default_total_way']
        self.setup()

    def get_area(self):
        count = self.total_way // (self.height + self.distance)
        width = count*self.distance + 10
        height = self.height+self.diameter + 10
        area = [width, height]
        return area

    def get_bluemap_path(self):
        path = QPainterPath(QPointF(0, 0))
        for point in self.path_point:
            path.lineTo(QPointF(point[0], point[1]))
        return [path]

    def get_real_path(self):
        path = QPainterPath(QPointF(0, 0))
        for point in self.path_point:
            path.lineTo(QPointF(point[0], point[1]))
        return [path]

    def get_attribute(self):
        attribute = {
        "default_class": self.__class__.__name__,
        "default_pen_width":[self.diameter],
        "default_diameter": self.diameter,
        "default_height": self.height,
        "default_distance": self.distance,
        "default_total_way": self.total_way,
        "name": "U_way",
        "area": self.get_area(),
        "real_area": self.get_area(),
        "roundsize": 10.0,
        "transformpoint": [
            0,
            0
        ],
        "zValue_upper": self.diameter/2,
        "zValue_lower": self.diameter/2,
        "3DModel": "",
        "sockets": [],
        "pixmaps": []}
        socket_message = {}
        socket_message['position'] = [-1, 0]
        socket_message['pos'] = [0, 0]
        socket_message['real_pos'] = [0, 0]
        attribute['sockets'].append(socket_message)
        socket_message = {}
        socket_message['position'] = [1, 0]
        socket_message['pos'] = self.path_point[-1]
        socket_message['real_pos'] = self.path_point[-1]
        attribute['sockets'].append(socket_message)

        return attribute

    def get_model(self):
        p_list = []
        for pos in self.path_point:
            p_list.append([pos[0]/10, pos[1]/10])
        main_pos = p_list[1].copy()
        R = sqrt(main_pos[0] ** 2 + main_pos[1] ** 2)
        R_sin = main_pos[1] / R
        R_cos = main_pos[0] / R
        deg = degrees(atan2(main_pos[1], main_pos[0]))
        for pos in p_list:
            pos_copy = pos.copy()
            pos[0] = R_cos * pos_copy[0] + R_sin * pos_copy[1]
            pos[1] = R_cos * pos_copy[1] - R_sin * pos_copy[0]
        path = cq.Workplane().polyline(p_list)
        self.way = cq.Workplane('YZ').polygon(bian, self.diameter/10).sweep(path).rotate([0, 0, 1], [0, 0, 0], -deg)
        return self.way

class T_way:
    def __init__(self, main_path_d=10, main_path_length=20, sub_path_d=10, sub_path_length=40, sub_path_number=1, sub_distance=40):
        self.main_path_d = main_path_d
        self.main_path_length = main_path_length
        self.sub_path_d = sub_path_d
        self.sub_path_length = sub_path_length
        self.sub_path_number = sub_path_number
        self.sub_distance = sub_distance
        self.setup()

    def setup(self):
        pass

    def set_attribute(self, attribute):
        self.main_path_d = attribute['default_diameter']
        self.main_path_length = attribute['default_main_path_length']
        self.sub_path_d = attribute['default_sub_path_d']
        self.sub_path_length = attribute['default_sub_path_length']
        self.sub_path_number = attribute['default_sub_path_number']
        self.sub_distance = attribute['default_sub_distance']
        self.setup()

    def get_area(self):
        width = self.sub_path_number*(self.sub_path_d+self.sub_distance)+2*self.main_path_length
        height = 2*self.sub_path_length
        area = [width, height]
        return area

    def get_bluemap_path(self):
        path1 = QPainterPath(QPointF(0, self.sub_path_length))
        path1.lineTo(self.sub_path_number * (self.sub_path_d + self.sub_distance) + 2 * self.main_path_length, self.sub_path_length)

        path2 = QPainterPath()
        for i in range(self.sub_path_number):
            sub_path = QPainterPath(QPointF(self.main_path_length + (i + 0.5) * (self.sub_path_d + self.sub_distance), self.sub_path_length))
            sub_path.lineTo(self.main_path_length + (i + 0.5) * (self.sub_path_d + self.sub_distance), 2*self.sub_path_length)
            path2.addPath(sub_path)

        return [path1, path2]

    def get_real_path(self):
        path1 = QPainterPath(QPointF(0, 0))
        path1.lineTo(self.sub_path_number*(self.sub_path_d+self.sub_distance)+2*self.main_path_length, 0)

        path2 = QPainterPath()
        for i in range(self.sub_path_number):
            sub_path = QPainterPath(QPointF(self.main_path_length+(i+0.5)*(self.sub_path_d+self.sub_distance), 0))
            sub_path.lineTo(self.main_path_length+(i+0.5)*(self.sub_path_d+self.sub_distance), self.sub_path_length)
            path2.addPath(sub_path)

        return [path1, path2]

    def get_attribute(self):
        attribute = {
        "default_class": self.__class__.__name__,
        "default_pen_width":[self.main_path_d, self.sub_path_d],
        "default_diameter": self.main_path_d,
        "default_main_path_length": self.main_path_length,
        "default_sub_path_d": self.sub_path_d,
        "default_sub_path_length": self.sub_path_length,
        "default_sub_path_number": self.sub_path_number,
        "default_sub_distance":self.sub_distance,
        "name": "T_way",
        "area": self.get_area(),
        "real_area": self.get_area(),
        "roundsize": 10.0,
        "transformpoint": [
            0,
            self.sub_path_length
        ],
        "zValue_upper": max(self.sub_path_d/2, self.main_path_d/2),
        "zValue_lower": max(self.sub_path_d/2, self.main_path_d/2),
        "3DModel": "",
        "sockets": [],
        "pixmaps": []}
        socket_message = {}
        socket_message['position'] = [-1, 0]
        socket_message['pos'] = [0, self.sub_path_length]
        socket_message['real_pos'] = [0, self.sub_path_length]
        attribute['sockets'].append(socket_message)
        for i in range(self.sub_path_number):
            socket_message = {}
            socket_message['position'] = [0, 1]
            socket_message['pos'] = [self.main_path_length + (i + 0.5) * (self.sub_path_d + self.sub_distance), 2*self.sub_path_length]
            socket_message['real_pos'] = [self.main_path_length + (i + 0.5) * (self.sub_path_d + self.sub_distance), 2*self.sub_path_length]
            attribute['sockets'].append(socket_message)
        socket_message = {}
        socket_message['position'] = [1, 0]
        socket_message['pos'] = [self.sub_path_number * (self.sub_path_d + self.sub_distance) + 2 * self.main_path_length,self.sub_path_length]
        socket_message['real_pos'] = [self.sub_path_number * (self.sub_path_d + self.sub_distance) + 2 * self.main_path_length,self.sub_path_length]
        attribute['sockets'].append(socket_message)

        return attribute

    def get_model(self):
        self.way = cq.Workplane('YZ').polygon(bian, self.main_path_d/10).extrude(self.sub_path_number * (self.sub_path_d/10 + self.sub_distance/10) + 2 * self.main_path_length/10)
        for i in range(self.sub_path_number):
            self.way += cq.Workplane('ZX', origin=(self.main_path_length/10 + (i + 0.5) * (self.sub_path_d/10 + self.sub_distance/10), 0)).polygon(bian, self.sub_path_d/10).extrude(self.sub_path_length/10)

        return self.way


class O_way:
    def __init__(self, line_length=10, r=20, d=5, step=15, N=9):
        self.line_length = line_length
        self.r = r
        self.d = d
        self.step = step
        self.N = N
        self.setup()

    def setup(self):
        if self.N * self.step > 360:
            self.N = (self.N * self.step) % 360 // self.step
        rad = radians(90 + self.N * self.step / 2)

        # 在 XZ 平面為基礎建立路徑R_cos * pos_copy[0] + R_sin * pos_copy[1]
        self.path_list = [
            [self.r * cos(radians(a)) - self.r, self.r * sin(radians(a))]
            for a in range(0, (self.N + 1) * self.step, self.step)
        ]

        for pos in self.path_list:
            pos_copy = pos.copy()
            pos[0] = cos(rad) * pos_copy[0] + sin(rad) * pos_copy[1] + self.line_length
            pos[1] = cos(rad) * pos_copy[1] - sin(rad) * pos_copy[0]
        self.path_list.insert(0, [0, 0])
        self.path_list.append([self.path_list[-1][0] + self.line_length, 0])

    def set_attribute(self, attribute):
        self.line_length = attribute['default_line_length']
        self.r = attribute['default_r']
        self.d = attribute['default_diameter']
        self.step = attribute['default_step']
        self.N = attribute['default_N']
        self.setup()

    def get_area(self):
        width = self.path_list[-1][0]
        height = 2*self.r + self.d
        area = [width, height]
        return area

    def get_bluemap_path(self):
        path1 = QPainterPath(QPointF(0, self.r + self.d/2))
        for point in self.path_list:
            path1.lineTo(QPointF(point[0], point[1] + self.r + self.d/2))
        path2 = QPainterPath(QPointF(0, self.r + self.d/2))
        for point in self.path_list:
            path2.lineTo(QPointF(point[0], -point[1] + self.r + self.d/2))
        path1.addPath(path2)
        return [path1]

    def get_real_path(self):
        path1 = QPainterPath(QPointF(0, 0))
        for point in self.path_list:
            path1.lineTo(QPointF(point[0], point[1]))
        path2 = QPainterPath(QPointF(0, 0))
        for point in self.path_list:
            path2.lineTo(QPointF(point[0], -point[1]))
        path1.addPath(path2)
        return [path1]

    def get_attribute(self):
        attribute = {
        "default_class": self.__class__.__name__,
        "default_pen_width": [self.d],
        "default_line_length": self.line_length,
        "default_r": self.r,
        "default_diameter": self.d,
        "default_step": self.step,
        'default_N': self.N,
        "name": "O_way",
        "area": self.get_area(),
        "real_area": self.get_area(),
        "roundsize": 10.0,
        "transformpoint": [
            0,
            self.r + self.d/2
        ],
        "zValue_upper": self.d/2,
        "zValue_lower": self.d/2,
        "3DModel": "",
        "sockets": [],
        "pixmaps": []}
        socket_message = {}
        socket_message['position'] = [-1, 0]
        socket_message['pos'] = [0, self.r + self.d/2]
        socket_message['real_pos'] = [0, self.r + self.d/2]     # pos + transformPoint
        attribute['sockets'].append(socket_message)
        socket_message = {}
        socket_message['position'] = [1, 0]
        socket_message['pos'] = [self.path_list[-1][0], self.r + self.d/2]
        socket_message['real_pos'] = [self.path_list[-1][0], self.r + self.d/2]
        attribute['sockets'].append(socket_message)

        return attribute

    def get_model(self):
        p_list = []
        for pos in self.path_list:
            p_list.append([pos[0] / 10, pos[1] / 10])
        path = cq.Workplane('XY').polyline(p_list)
        arc3d = cq.Workplane('YZ').polygon(bian, self.d/10).sweep(path)
        self.way = arc3d.mirror('XZ') + arc3d
        return self.way


class Door_way:
    def __init__(self, bolt_length=100, bolt_diameter=60, line_length=10, line_diameter=30):
        self.bolt_length = bolt_length
        self.bolt_diameter = bolt_diameter
        self.line_length = line_length
        self.line_diameter = line_diameter
        self.setup()

    def setup(self):
        pass

    def set_attribute(self, attribute):
        self.bolt_length = attribute['default_bolt_length']
        self.bolt_diameter = attribute['default_bolt_diameter']
        self.line_length = attribute['default_line_length']
        self.line_diameter = attribute['default_line_diameter']
        self.setup()

    def get_area(self):
        width = self.bolt_diameter
        height = self.bolt_diameter
        area = [width, height]
        return area

    def get_bluemap_path(self):
        path = QPainterPath()
        path.addEllipse(QPointF(self.bolt_diameter/2, self.bolt_diameter/2), self.bolt_diameter/2, self.bolt_diameter/2)
        path.addRect(self.bolt_diameter+20, 0, self.bolt_length, self.bolt_diameter)
        path.addRect(self.bolt_diameter + self.bolt_length + 20, self.bolt_diameter/2-self.line_diameter/2, self.line_length, self.line_diameter)

        return [path]

    def get_real_path(self):
        path = QPainterPath()
        path.addEllipse(QPointF(0, 0), self.bolt_diameter/2, self.bolt_diameter/2)
        path.addEllipse(QPointF(0, 0), self.bolt_diameter/4, self.bolt_diameter/4)

        return [path]

    def get_attribute(self):
        attribute = {
        "default_class": self.__class__.__name__,
        "default_pen_width": [],
        "default_bolt_length": self.bolt_length,
        "default_bolt_diameter": self.bolt_diameter,
        "default_line_length": self.line_length,
        "default_line_diameter": self.line_diameter,
        "name": "Door_way",
        "area": [self.bolt_diameter + self.bolt_length + self.line_length + 40, self.bolt_diameter],
        "real_area": self.get_area(),
        "roundsize": 10.0,
        "transformpoint": [
            self.bolt_diameter/2,
            self.bolt_diameter/2
        ],
        "zValue_upper": self.bolt_length + self.line_length,
        "zValue_lower": 0,
        "3DModel": "",
        "sockets": [],
        "pixmaps": []}
        socket_message = {}
        socket_message['position'] = [1, 0]
        socket_message['pos'] = [self.bolt_diameter + self.bolt_length + self.line_length + 20, self.bolt_diameter/2]
        socket_message['real_pos'] = [self.bolt_diameter/2, self.bolt_diameter/2]
        attribute['sockets'].append(socket_message)

        return attribute

    def get_model(self):
        model1 = cq.Workplane('YX').polygon(bian, self.line_diameter/10).extrude(self.line_length/10)
        model2 = cq.Workplane('YX', origin=[0, 0, -self.line_length/10]).polygon(bian, self.bolt_diameter/10).extrude(self.bolt_length/10)
        self.way = model1 + model2
        return self.way


class K_way:
    def __init__(self, flow_length=40, body_length=70, diameter=10):
        self.flow_length = flow_length
        self.body_length = body_length
        self.diameter = diameter
        self.setup()

    def setup(self):
        pass

    def set_attribute(self, attribute):
        self.flow_length = attribute['default_flow_length']
        self.body_length = attribute['default_body_length']
        self.diameter = attribute['default_diameter']
        self.setup()

    def get_area(self):
        width = 2*self.flow_length + self.body_length
        height = 2*self.flow_length
        area = [width, height]
        return area

    def get_bluemap_path(self):
        path = QPainterPath(QPointF(0, 10))
        path.lineTo(self.flow_length/sqrt(2), 10+self.flow_length/sqrt(2))
        path.lineTo(self.flow_length/sqrt(2)+self.body_length, 10+self.flow_length/sqrt(2))
        path.lineTo(self.flow_length*sqrt(2)+self.body_length, 10)
        path2 = QPainterPath(QPointF(0, 10+self.flow_length*sqrt(2)))
        path2.lineTo(self.flow_length/sqrt(2), 10+self.flow_length/sqrt(2))
        path2.lineTo(self.flow_length/sqrt(2)+self.body_length, 10+self.flow_length/sqrt(2))
        path2.lineTo(self.flow_length*sqrt(2)+self.body_length, 10+self.flow_length*sqrt(2))
        path.addPath(path2)

        return [path]

    def get_real_path(self):
        path = QPainterPath(QPointF(0, 0))
        path.lineTo(self.flow_length / sqrt(2), self.flow_length / sqrt(2))
        path.lineTo(self.flow_length / sqrt(2) + self.body_length, self.flow_length / sqrt(2))
        path.lineTo(self.flow_length * sqrt(2) + self.body_length, 0)
        path2 = QPainterPath(QPointF(0, self.flow_length * sqrt(2)))
        path2.lineTo(self.flow_length / sqrt(2), self.flow_length / sqrt(2))
        path2.lineTo(self.flow_length / sqrt(2) + self.body_length, self.flow_length / sqrt(2))
        path2.lineTo(self.flow_length * sqrt(2) + self.body_length, self.flow_length * sqrt(2))
        path.addPath(path2)

        return [path]

    def get_attribute(self):
        attribute = {
        "default_class": self.__class__.__name__,
        "default_pen_width": [self.diameter],
        "default_flow_length": self.flow_length,
        "default_body_length": self.body_length,
        "default_diameter": self.diameter,
        "name": "K_way",
        "area": [self.flow_length*sqrt(2) + self.body_length, self.flow_length*sqrt(2) + 20],
        "real_area": self.get_area(),
        "roundsize": 10.0,
        "transformpoint": [
            0,
            0
        ],
        "zValue_upper": self.diameter/2,
        "zValue_lower": self.diameter/2,
        "3DModel": "",
        "sockets": [],
        "pixmaps": []}
        socket_message = {}
        socket_message['position'] = [-1, 0]
        socket_message['pos'] = [0, 10]
        socket_message['real_pos'] = [0, 0]
        attribute['sockets'].append(socket_message)
        socket_message = {}
        socket_message['position'] = [-1, 0]
        socket_message['pos'] = [0, 10+self.flow_length*sqrt(2)]
        socket_message['real_pos'] = [0, self.flow_length*sqrt(2)]
        attribute['sockets'].append(socket_message)
        socket_message = {}
        socket_message['position'] = [1, 0]
        socket_message['pos'] = [self.flow_length*sqrt(2)+self.body_length, 10]
        socket_message['real_pos'] = [self.flow_length*sqrt(2)+self.body_length, 0]
        attribute['sockets'].append(socket_message)
        socket_message = {}
        socket_message['position'] = [1, 0]
        socket_message['pos'] = [self.flow_length*sqrt(2)+self.body_length, 10+self.flow_length*sqrt(2)]
        socket_message['real_pos'] = [self.flow_length*sqrt(2)+self.body_length, self.flow_length*sqrt(2)]
        attribute['sockets'].append(socket_message)

        return attribute

    def get_model(self):
        point_list1 = [[0, 0, 0], [self.flow_length / sqrt(2), self.flow_length / sqrt(2), 0], [self.flow_length / sqrt(2) + self.body_length, self.flow_length / sqrt(2), 0], [self.flow_length * sqrt(2) + self.body_length, 0, 0]]
        point_list2 = [[0, self.flow_length * sqrt(2), 0], [self.flow_length / sqrt(2), self.flow_length / sqrt(2), 0], [self.flow_length / sqrt(2) + self.body_length, self.flow_length / sqrt(2), 0], [self.flow_length * sqrt(2) + self.body_length, self.flow_length * sqrt(2), 0]]
        for point in point_list1:
            point[0] = point[0] / 10
            point[1] = point[1] / 10
            point[2] = point[2] / 10
        for point in point_list2:
            point[0] = point[0] / 10
            point[1] = point[1] / 10
            point[2] = point[2] / 10
        model1 = getEdgeModel(point_list1, self.diameter/10)
        model2 = getEdgeModel(point_list2, self.diameter/10)
        self.way = model1 + model2
        return self.way


class Fork_way:
    def __init__(self, flow_width=50, flow_height=70, diameter=10, level=2):
        self.flow_width = flow_width
        self.flow_height = flow_height
        self.diameter = diameter
        self.level = level
        self.setup()

    def setup(self):
        pass

    def set_attribute(self, attribute):
        self.flow_width = attribute['default_flow_width']
        self.flow_height = attribute['default_flow_height']
        self.diameter = attribute['default_diameter']
        self.level = attribute['default_level']
        self.setup()

    def get_area(self):
        width = 2*(self.level + 1)*self.flow_width
        height = (2**self.level - 1)*self.flow_height
        area = [width, height]
        return area

    def get_bluemap_path(self):
        main_path = QPainterPath()
        path = QPainterPath(QPointF(0, (2**self.level - 1)*self.flow_height/2))
        path.lineTo(self.flow_width, (2**self.level - 1)*self.flow_height/2)
        main_path = main_path.united(path)
        path = QPainterPath(QPointF(2*(self.level + 1)*self.flow_width, (2**self.level - 1)*self.flow_height/2))
        path.lineTo(2*(self.level + 1)*self.flow_width-self.flow_width, (2**self.level - 1)*self.flow_height/2)
        main_path = main_path.united(path)
        for level in range(self.level):
            for i in range(2**(self.level-level)):
                path = QPainterPath(QPointF((self.level + 1)*self.flow_width-level*self.flow_width, i*self.flow_height*(2**level) + (2**(level-1) - 1/2)*self.flow_height))
                path.lineTo((self.level + 1)*self.flow_width-(level+1)*self.flow_width, i*self.flow_height*(2**level) + (2**(level-1) - 1/2)*self.flow_height)
                main_path = main_path.united(path)
                path = QPainterPath(QPointF((self.level + 1) * self.flow_width + level * self.flow_width, i * self.flow_height * (2**level) + (2**(level-1) - 1/2)*self.flow_height))
                path.lineTo((self.level + 1) * self.flow_width + (level + 1) * self.flow_width, i * self.flow_height * (2**level) + (2**(level-1) - 1/2)*self.flow_height)
                main_path = main_path.united(path)
            for i in range(2**(self.level-level-1)):
                path = QPainterPath(QPointF((self.level + 1)*self.flow_width-(level+1)*self.flow_width, i*self.flow_height*(2**level)*2 + (2**(level-1) - 1/2)*self.flow_height))
                path.lineTo((self.level + 1)*self.flow_width-(level+1)*self.flow_width, i*self.flow_height*(2**level)*2 + self.flow_height*(2**level) + (2**(level-1) - 1/2)*self.flow_height)
                main_path = main_path.united(path)
                path = QPainterPath(QPointF((self.level + 1) * self.flow_width + (level + 1) * self.flow_width, i * self.flow_height * (2**level) * 2 + (2**(level-1) - 1/2)*self.flow_height))
                path.lineTo((self.level + 1) * self.flow_width + (level + 1) * self.flow_width, i * self.flow_height * (2**level) * 2 + self.flow_height * (2**level) + (2**(level-1) - 1/2)*self.flow_height)
                main_path = main_path.united(path)
        return [main_path]

    def get_real_path(self):
        main_path = QPainterPath()
        path = QPainterPath(QPointF(0, (2 ** self.level - 1) * self.flow_height / 2 -(2 ** self.level - 1) * self.flow_height / 2))
        path.lineTo(self.flow_width, (2 ** self.level - 1) * self.flow_height / 2 -(2 ** self.level - 1) * self.flow_height / 2)
        main_path = main_path.united(path)
        path = QPainterPath(
            QPointF(2 * (self.level + 1) * self.flow_width, (2 ** self.level - 1) * self.flow_height / 2 -(2 ** self.level - 1) * self.flow_height / 2))
        path.lineTo(2 * (self.level + 1) * self.flow_width - self.flow_width,
                    (2 ** self.level - 1) * self.flow_height / 2 -(2 ** self.level - 1) * self.flow_height / 2)
        main_path = main_path.united(path)
        for level in range(self.level):
            for i in range(2 ** (self.level - level)):
                path = QPainterPath(QPointF((self.level + 1) * self.flow_width - level * self.flow_width,
                                            i * self.flow_height * (2**level) + (
                                                        2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2))
                path.lineTo((self.level + 1) * self.flow_width - (level + 1) * self.flow_width,
                            i * self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2)
                main_path = main_path.united(path)
                path = QPainterPath(QPointF((self.level + 1) * self.flow_width + level * self.flow_width,
                                            i * self.flow_height * (2**level) + (
                                                        2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2))
                path.lineTo((self.level + 1) * self.flow_width + (level + 1) * self.flow_width,
                            i * self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2)
                main_path = main_path.united(path)
            for i in range(2 ** (self.level - level - 1)):
                path = QPainterPath(QPointF((self.level + 1) * self.flow_width - (level + 1) * self.flow_width,
                                            i * self.flow_height * (2**level) * 2 + (
                                                        2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2))
                path.lineTo((self.level + 1) * self.flow_width - (level + 1) * self.flow_width,
                            i * self.flow_height * (2**level) * 2 + self.flow_height * (2**level) + (
                                        2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2)
                main_path = main_path.united(path)
                path = QPainterPath(QPointF((self.level + 1) * self.flow_width + (level + 1) * self.flow_width,
                                            i * self.flow_height * (2**level) * 2 + (
                                                        2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2))
                path.lineTo((self.level + 1) * self.flow_width + (level + 1) * self.flow_width,
                            i * self.flow_height * (2**level) * 2 + self.flow_height * (2**level) + (
                                        2 ** (level - 1) - 1 / 2) * self.flow_height-(2 ** self.level - 1) * self.flow_height / 2)
                main_path = main_path.united(path)
        return [main_path]

    def get_attribute(self):
        attribute = {
        "default_class": self.__class__.__name__,
        "default_pen_width": [self.diameter],
        "default_flow_width": self.flow_width,
        "default_flow_height": self.flow_height,
        "default_diameter": self.diameter,
        "default_level": self.level,
        "name": "Fork_way",
        "area": self.get_area(),
        "real_area": self.get_area(),
        "roundsize": 10.0,
        "transformpoint": [
            0,
            (2 ** self.level - 1) * self.flow_height/2
        ],
        "zValue_upper": self.diameter/2,
        "zValue_lower": self.diameter/2,
        "3DModel": "",
        "sockets": [],
        "pixmaps": []}
        socket_message = {}
        socket_message['position'] = [-1, 0]
        socket_message['pos'] = [0, (2**self.level - 1)*self.flow_height/2]
        socket_message['real_pos'] = [0, (2**self.level - 1)*self.flow_height/2]
        attribute['sockets'].append(socket_message)
        socket_message = {}
        socket_message['position'] = [1, 0]
        socket_message['pos'] = [2*(self.level + 1)*self.flow_width, (2**self.level - 1)*self.flow_height/2]
        socket_message['real_pos'] = [2*(self.level + 1)*self.flow_width, (2**self.level - 1)*self.flow_height/2]
        attribute['sockets'].append(socket_message)

        return attribute

    def get_model(self):
        self.way = cq.Workplane()
        per_path = []
        path = []
        path.append([0, (2 ** self.level - 1) * self.flow_height / 2])
        path.append([self.flow_width, (2 ** self.level - 1) * self.flow_height / 2])
        per_path.append(path)
        path = []
        path.append([2 * (self.level + 1) * self.flow_width, (2 ** self.level - 1) * self.flow_height / 2])
        path.append([2 * (self.level + 1) * self.flow_width - self.flow_width, (2 ** self.level - 1) * self.flow_height / 2])
        per_path.append(path)
        for level in range(self.level):
            for i in range(2 ** (self.level - level)):

                path = []
                path.append([(self.level + 1) * self.flow_width - level * self.flow_width, i * self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                path.append([(self.level + 1) * self.flow_width - (level + 1) * self.flow_width,i * self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                per_path.append(path)
                path = []
                path.append([(self.level + 1) * self.flow_width + level * self.flow_width,i * self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                path.append([(self.level + 1) * self.flow_width + (level + 1) * self.flow_width, i * self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                per_path.append(path)

            for i in range(2 ** (self.level - level - 1)):

                path = []
                path.append([(self.level + 1) * self.flow_width - (level + 1) * self.flow_width, i * self.flow_height * (2**level) * 2 + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                path.append([(self.level + 1) * self.flow_width - (level + 1) * self.flow_width, i * self.flow_height * (2**level) * 2 + self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                per_path.append(path)
                path = []
                path.append([(self.level + 1) * self.flow_width + (level + 1) * self.flow_width, i * self.flow_height * (2**level) * 2 + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                path.append([(self.level + 1) * self.flow_width + (level + 1) * self.flow_width, i * self.flow_height * (2**level) * 2 + self.flow_height * (2**level) + (2 ** (level - 1) - 1 / 2) * self.flow_height])
                per_path.append(path)

        for point_list in per_path:
            originPoint = []
            points = []
            originPoint.append([point_list[0][0]/10, (point_list[0][1] - (2 ** self.level - 1) * self.flow_height/2)/10, -self.diameter/20])
            originPoint.append([point_list[1][0] / 10, (point_list[1][1] - (2 ** self.level - 1) * self.flow_height / 2) / 10, -self.diameter/20])
            points.append([point_list[0][0]/10, (point_list[0][1] - (2 ** self.level - 1) * self.flow_height/2)/10, 0])
            points.append([point_list[1][0]/10, (point_list[1][1] - (2 ** self.level - 1) * self.flow_height/2)/10, 0])
            self.way += getEdgeModel(points, self.diameter/10)
            self.way += cq.Workplane(origin=originPoint[0]).polygon(bian, self.diameter/10).extrude(self.diameter/10)
            self.way += cq.Workplane(origin=originPoint[1]).polygon(bian, self.diameter/10).extrude(self.diameter/10)

        return self.way


def getEdgeModel(p_list, width=1.0):
    d = width*0.4
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
