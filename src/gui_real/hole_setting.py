from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtCore import QRectF


class GraphicHoleSocket(QGraphicsItem):
    def __init__(self, holeSocket, parent=None):
        super().__init__(parent)

        self.hole = holeSocket
        self.radius = 6
        self.outline_width = 1.0
        self._color_background = QColor("#FFFF7700")
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

        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

    def boundingRect(self):
        return QRectF(
            - 2*self.radius - 2*self.outline_width,
            - 2*self.radius - 2*self.outline_width,
            4 * (self.radius - self.outline_width),
            4 * (self.radius - self.outline_width),
        )

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # 如果图元被选中，就更新连线，这里更新的是所有。可以优化，只更新连接在图元上的。
        if self.isSelected():
            for grEdge in self.hole.scene.edges:
                grEdge.edge.update_positions()

    def setProhibit(self):
        self.setOpacity(0.25)
        self.setZValue(-11)
        self.setEnabled(False)
        self.hole.mySocket1.set_canCheck(False)
        self.hole.mySocket2.set_canCheck(False)

    def setEnable(self):
        self.setOpacity(1.0)
        self.setZValue(0)
        self.setEnabled(True)
        if self.hole.mySocket1.layer == self.hole.scene.currentLayer:
            self.hole.mySocket1.set_canCheck(True)
        if self.hole.mySocket2.layer == self.hole.scene.currentLayer:
            self.hole.mySocket2.set_canCheck(True)


class GraphicSocket2(QGraphicsItem):
    def __init__(self, socket, parent=None):
        super().__init__(parent)

        self.socket = socket
        self.radius = 6
        self.outline_width = 1.0
        self._color_background = QColor("#FFFF7700")
        self._color_outline_default = QColor("#FF000000")
        self._color_outline_selected = QColor("#ffffa637")

        self._pen_default = QPen(self._color_outline_default)
        self._pen_selected = QPen(self._color_outline_selected)

        self._pen_default.setWidthF(self.outline_width)
        self._pen_selected.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

        # self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):

        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

    def boundingRect(self):
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius - self.outline_width),
            2 * (self.radius - self.outline_width),
        )
