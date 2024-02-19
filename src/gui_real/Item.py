from PySide6.QtWidgets import QGraphicsItem, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QColor, QPen, QBrush, QImage
from PySide6.QtCore import Qt, QSize


class GraphicItem(QGraphicsPixmapItem):
    def __init__(self, attribute={}, parent=None):
        super().__init__(parent)

        self.id = id(self)

        self.way = attribute['way']     # 图片路径
        self.pix = QPixmap(self.way)
        self.width = attribute['area'][0]   # 图元宽
        self.height = attribute['area'][1]   # 图元高
        self.offset = attribute['offset']   # 偏移量
        self.transformpoint = attribute['transformpoint']   # 旋转中心

        self.setPixmap(self.pix.scaled(QSize(self.width, self.height), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))  # 设置图元
        # self.setShapeMode(self.ShapeMode.MaskShape)
        self.setOffset(self.offset[0] - self.transformpoint[0], self.offset[1] - self.transformpoint[1])  # 设置偏移量
        #self.setTransformOriginPoint(self.transformpoint[0], self.transformpoint[1])
        #self.setRotation(15)
        #self.setFlag(QGraphicsItem.ItemIsSelectable)  # ***设置图元是可以被选择的





