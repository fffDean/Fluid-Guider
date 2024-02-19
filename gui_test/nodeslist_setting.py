from PySide6.QtGui import QPixmap, QIcon, QDrag
from PySide6.QtCore import QSize, Qt, QByteArray, QDataStream, QMimeData, QIODevice, QPoint
from PySide6.QtWidgets import QListWidget, QAbstractItemView, QListWidgetItem
import json

class DragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = self.getdata()
        self.initUI()

    def initUI(self):
        # init
        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        self.addDefaultItems()
        self.addMyItems()

    def addDefaultItems(self):
        item = QListWidgetItem('Item Group', self)  # can be (icon, text, parent, <int>type)
        pixmap = QPixmap('../graphic/group.png')
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(48, 48))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, 'Item Group')
        item.setData(Qt.UserRole + 1, 1)    # 默认元件被标记为1
        item.setData(Qt.UserRole + 2, pixmap)
        # item1 = self.makeItem('Group')

        item2 = self.makeItem('U_way')
        item3 = self.makeItem('O_way')
        item4 = self.makeItem('T_way')
        item5 = self.makeItem('Door_way')
        item6 = self.makeItem('K_way')
        item7 = self.makeItem('Fork_way')

    def makeItem(self, name: str):
        item = QListWidgetItem('Item {}'.format(name), self)  # can be (icon, text, parent, <int>type)
        pixmap = QPixmap('../graphic/{}.png'.format(name))
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(48, 48))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, name)
        item.setData(Qt.UserRole + 1, 1)  # 默认元件被标记为1
        item.setData(Qt.UserRole + 2, pixmap)
        return item
        
    def addMyItems(self):
        for key in list(self.data.keys()):
            self.addMyItem(key, self.data[key]['pixmaps'][0]['way'])
            #self.addMyItem(node.op_title, node.icon, node.op_code)

    def addMyItem(self, name, icon=None, op_code=0):
        item = QListWidgetItem(name, self)      # can be (icon, text, parent, <int>type)
        pixmap = QPixmap(icon if icon is not None else ".")
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(48, 48))

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # setup data
        item.setData(Qt.UserRole, self.data[name])
        item.setData(Qt.UserRole + 1, op_code)  # 非默认元件标记为0


    def getdata(self):
        with open('../gui_test/nodeslist.txt', 'r', encoding='utf-8') as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf-8')

            return data

    def markdata(self):
        data = self.data
        with open('../gui_test/nodeslist.txt', 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4))

    def startDrag(self, *args, **kwargs):
        item = self.currentItem()
        if item.data(Qt.UserRole + 1) == 0:
            attribute = item.data(Qt.UserRole)
            attribute_str = json.dumps(attribute)
            pixmap = QPixmap(attribute['pixmaps'][0]['way'])

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream.writeQString(attribute_str)

            mimeData = QMimeData()
            mimeData.setData('attribute', itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec(Qt.MoveAction)

        elif item.data(Qt.UserRole + 1) == 1:
            markSymbol = item.data(Qt.UserRole)
            pixmap = item.data(Qt.UserRole + 2)
            # pixmap = QPixmap('Model.png')

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream.writeQString(markSymbol)

            mimeData = QMimeData()
            mimeData.setData('markSymbol', itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec(Qt.MoveAction)
