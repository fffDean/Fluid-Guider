from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsLineItem
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPainterPath, QPainterPathStroker
from PySide6.QtCore import QPointF, QRect, QRectF, Qt


class GraphicBaseShape(QGraphicsItem):
    def __init__(self, baseShape, parent=None):
        super().__init__(parent)
        self.baseShape = baseShape

        self._pen = QPen(QColor('#aa117777'))
        self._pen.setWidth(2)
        self._pen_select = QPen(QColor('#aaff7777'))
        self._pen_select.setWidth(4)
        self._brush = QBrush(QColor('#55777777'))

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.setZValue(-10)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        path = QPainterPath(QPointF(-1, -1))
        path.lineTo(QPointF(1, 1))
        path.lineTo(QPointF(1, -1))
        path.lineTo(QPointF(-1, 1))
        path.closeSubpath()
        for graphic in self.baseShape.shapes:
            path = path.united(graphic.getPath())
        return path.simplified()

    def paint(self, painter, option, widget=None):
        # path = self.shape()
        shape_list = self.baseShape.shapes.copy()
        shape_list.sort(key=lambda sh: sh.thickness)
        a = []
        x = []
        for i in range(0, len(shape_list)):
            if i + 1 < len(shape_list):
                if shape_list[i].thickness == shape_list[i + 1].thickness:
                    x.append(shape_list[i])
                else:
                    x.append(shape_list[i])
                    a.append(x)
                    x = []
            else:
                x.append(shape_list[len(shape_list) - 1])
                a.append(x)
        for s_l in a:
            path = QPainterPath()
            for shape in s_l:
                path = path.united(shape.getPath())
            if self.isSelected():
                painter.setPen(self._pen_select)
                painter.setBrush(self._brush)
            else:
                painter.setPen(self._pen)
                painter.setBrush(self._brush)
            painter.drawPath(path)
