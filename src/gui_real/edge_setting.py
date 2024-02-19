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
        self._pen_real = QPen(self._color)
        self._pen.setWidth(2)
        self._pen_selected.setWidth(2)
        self._pen_real.setWidth(self.edge.width)

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        self.setZValue(-10)

        self.posSource = [0, 0]
        self.posDestination = [0, 0]

        self.left_catch_point = None
        self.right_catch_point = None

    def set_posSource(self, x, y):
        self.posSource = [x, y]

    def set_posDestination(self, x, y):
        self.posDestination = [x, y]

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.shape())  # 设置路径
        path = self.update_realPath()
        self._pen_real.setWidth(self.edge.width)
        painter.setPen(self._pen_real)
        painter.drawPath(path)

        path = self.update_sidePath()
        painter.setPen(self._pen_dragging)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        strocker = QPainterPathStroker()
        strocker.setWidth(5)
        path = strocker.createStroke(self.update_sidePath())
        path += strocker.createStroke(self.update_realPath())
        return path

    def update_sidePath(self):
        point_list = self.edge.getPointList()
        if point_list != []:
            path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
            path.lineTo(point_list[0].scenePos())
            path2 = QPainterPath(QPointF(self.posDestination[0], self.posDestination[1]))
            path2.lineTo(point_list[-1].scenePos())
            path.addPath(path2)

        else:
            path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
            path.lineTo(self.posDestination[0], self.posDestination[1])
        return path

    def update_realPath(self):
        point_list = self.edge.getPointList()
        if point_list != []:
            path = QPainterPath(self.edge.point_list[0].scenePos())
            for catch_point in point_list:
                path.lineTo(catch_point.scenePos())
            self.left_catch_point = point_list[0]
            self.right_catch_point = point_list[-1]
        else:
            path = QPainterPath(QPointF(-100, -100))

        return path

    def setProhibit(self):
        self.setOpacity(0.25)
        self.setZValue(-11)
        self.setEnabled(False)
        for child in self.childItems():
            child.setEnabled(False)

    def setEnable(self):
        self.setOpacity(1.0)
        self.setZValue(-10)
        self.setEnabled(True)
        for child in self.childItems():
            child.setEnabled(True)


class GraphicCantSeeSocket(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.radius = parent.edge.width/2 + 1
        self.outline_width = 1.0
        self._color_background = QColor("#77000000")
        self._color_outline_default = QColor("#FF000000")
        self._color_outline_selected = QColor("#ffffa637")

        self._pen_default = QPen(self._color_outline_default)
        self._pen_selected = QPen(self._color_outline_selected)

        self._pen_default.setWidthF(self.outline_width)
        self._pen_selected.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.radius = self.parent.edge.width / 2 + 1
        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(Qt.PenStyle.NoPen if not self.isSelected() else self._pen_selected)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)


    def boundingRect(self):
        self.radius = self.parent.edge.width / 2 + 1
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
