from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QStyleOptionGraphicsItem
from PySide6.QtCore import QRectF, Signal
from PySide6.QtGui import QFont, Qt, QPen, QColor, QBrush, QPainterPath


class GraphicNode(QGraphicsItem):

    def __init__(self, node, attribute={}, parent=None):
        super().__init__(parent)

        self.node = node

        self._title_color = Qt.GlobalColor.white
        self._title_font = QFont("Ubuntu", 10)

        self.width = attribute['area'][0]
        self.height = attribute['area'][1]
        self.edge_size = attribute['roundsize']
        self.transformpoint = attribute['transformpoint']  # 旋转中心
        self._pen_default_picture = []
        if 'default_class' in attribute:
            if attribute['default_pen_width']:
                self.pen_width = attribute['default_pen_width']
                for width in self.pen_width:
                    pen = QPen(QColor("#ffeeaaaa"))
                    pen.setWidth(width)
                    self._pen_default_picture.append(pen)
                    self._brush_default_picture = Qt.BrushStyle.NoBrush
            else:
                self._pen_default_picture = [Qt.PenStyle.NoPen]
                self._brush_default_picture = QBrush(QColor("#ffeeaaaa"))
            self.default = True
        else:
            self.default = False
        self.title_height = 24
        self._padding = 4.0
        self.socket_spacing = 22

        #self.initTitle()
        #self.title = title

        self._pen_default = QPen(QColor("#aaffffff"))
        self._pen_default.setWidth(10)
        self._pen_selected = QPen(QColor("#aaffa637"))
        self._pen_selected.setWidth(10)

        self._brush_title = QBrush(QColor("#ff313131"))
        self._brush_background = QBrush(QColor("#aaaaaaaa"))

        self.setTransformOriginPoint(self.transformpoint[0], self.transformpoint[1])

        self.initUI()

    def set_attribute(self, attribute):
        self.width = attribute['area'][0]
        self.height = attribute['area'][1]
        self.edge_size = attribute['roundsize']
        self.transformpoint = attribute['transformpoint']  # 旋转中心
        self._pen_default_picture = []
        if 'default_class' in attribute:
            if attribute['default_pen_width']:
                self.pen_width = attribute['default_pen_width']
                for width in self.pen_width:
                    pen = QPen(QColor("#ffeeaaaa"))
                    pen.setWidth(width)
                    self._pen_default_picture.append(pen)
                self._brush_default_picture = Qt.BrushStyle.NoBrush
            else:
                self._pen_default_picture = [Qt.PenStyle.NoPen]
                self._brush_default_picture = QBrush(QColor("#ffeeaaaa"))
            self.default = True
        else:
            self.default = False

    def signalConnect(self):
        pass

    def boundingRect(self):
        return QRectF(
            0,
            0,
            self.width,
            self.height
        ).normalized()

    def initUI(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setZValue(1)

    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(
            self.width - 2 * self._padding
        )

    @property
    def padding(self):
        return self._padding

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)
    # 绘制
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # 边框
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        #painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_outline.simplified())

        if self.default:
            for i in range(len(self.node.default_path)):
                path = self.node.default_path[i]
                painter.setPen(self._pen_default_picture[i])
                painter.setBrush(self._brush_default_picture)
                # painter.setBrush(self._brush_background)
                painter.drawPath(path)


        '''
        # 标题

        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_size, self.edge_size)
        path_title.addRect(0, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.title_height - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(0, self.title_height, self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.title_height, self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())
        
        path_content = QPainterPath()
        path_content.setFillRule(Qt.FillRule.WindingFill)
        path_content.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())
        '''

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        # 如果图元被选中，就更新连线，这里更新的是所有。可以优化，只更新连接在图元上的。
        if self.isSelected():
            for grEdge in self.node.scene.edges:
                grEdge.edge.update_positions()

        '''
        if self.isSelected():
            for grEdge in self.node.scene.edges:
                if grEdge.edge.start_socket in self.node.sockets:
                    grEdge.edge.update_positions()
                elif grEdge.edge.end_socket in self.node.sockets:
                    grEdge.edge.update_positions()
        '''



class GraphicSocket(QGraphicsItem):
    def __init__(self, socket, parent=None):
        super().__init__(parent)

        self.socket = socket
        self.radius = 6
        self.outline_width = 1.0
        self._color_background = QColor("#FFFF7700")
        self._color_outline = QColor("#aa000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

        self.setZValue(10)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):

        # painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

    def boundingRect(self):
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
