from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsLineItem
from gui_real.baseShape_setting import GraphicBaseShape
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPainterPath, QPainterPathStroker
from PySide6.QtCore import QPointF, QRect, QRectF, Qt, QObject
import math


class baseShape():
    def __init__(self, scene):
        self.scene = scene
        self.layer = 0
        self.grBaseShape = GraphicBaseShape(self)
        self.scene.grScene.addItem(self.grBaseShape)
        self.shapes = []

    def addSceneRect(self, rect):
        self.shapes.append(rect)

    def removeSceneRect(self, rect):
        self.shapes.remove(rect)

    def to_string(self):
        data = {}
        data['shapes'] = []
        for shape in self.shapes:
            shape_data = {}
            shape_data['Type'] = shape.__class__.__name__
            shape_data['pos'] = shape.posSource
            shape_data['area'] = [shape.width, shape.height]
            shape_data['thickness'] = shape.thickness
            data['shapes'].append(shape_data)
        return data


class Rect:
    def __init__(self):
        self.posSource = [0, 0]
        self.width = 0
        self.height = 0
        self.thickness = 40

    def reset(self, x, y, w, h, t):
        self.posSource = [x, y]
        self.width = w
        self.height = h
        self.thickness = t

    def mouseStart(self, x, y):
        self.posSource = [x, y]

    def mouseEnd(self, x, y):
        self.width = x - self.posSource[0]
        self.height = y - self.posSource[1]

    def getPath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posSource[0] + self.width, self.posSource[1])
        path.lineTo(self.posSource[0] + self.width, self.posSource[1] + self.height)
        path.lineTo(self.posSource[0], self.posSource[1] + self.height)
        path.closeSubpath()
        return path.simplified()

    def boundingRect(self):
        return self.getPath().boundingRect()


class Ellipse:
    def __init__(self):
        self.posSource = [0, 0]
        self.rx = 0
        self.ry = 0

    def mouseStart(self, x, y):
        self.posSource = [x, y]

    def mousEnd(self, x, y):
        self.rx = math.sqrt((x-self.posSource[0])**2 + (y-self.posSource[1])**2)
        self.ry = self.rx

    def getPath(self):
        path = QPainterPath()
        path.addEllipse(self.posSource, self.rx, self.ry)
        return path.simplified()
