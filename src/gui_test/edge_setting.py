from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class GraphicEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge

        self._color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        # 虚线样式
        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.PenStyle.DashDotLine)

        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen.setWidth(2)
        self._pen_selected.setWidth(2)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        self.setZValue(3)

        self.posSource = [0, 0]
        self.posDestination = [0, 0]

    def set_posSource(self, x, y):
        self.posSource = [x, y]

    def set_posDestination(self, x, y):
        self.posDestination = [x, y]

    def paint(self, painter, QStyleOptionGraphicsItem, widge=None):
        self.setPath(self.updatePath_Bezier())  # 设置路径
        path = self.path()

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
            painter.drawPath(path)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        strocker = QPainterPathStroker()
        strocker.setWidth(5)
        path = strocker.createStroke(self.updatePath_Bezier())
        return path

    def updatePath_Direct(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path

    def updatePath_Bezier(self):
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5
        if s[0] > d[0]:
            dist *= -1

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0] + dist, s[1], d[0] - dist, d[1],
                     self.posDestination[0], self.posDestination[1])
        return path
