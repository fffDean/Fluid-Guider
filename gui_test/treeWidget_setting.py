from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QLineEdit, QComboBox
from PySide6.QtGui import QIcon, QDoubleValidator, QIntValidator
from PySide6.QtCore import Signal

class SettingTree(QTreeWidget):
    textChangedSignal = Signal(str)
    posChangedSignal = Signal(float, float)

    def __init__(self, data={}, parent=None):
        super().__init__(parent)
        self.graphic = None
        self.data = data
        self.items = {}
        self.initUI()
        self.addChildren()

    def initUI(self):
        # 设置行数与列数
        self.setColumnCount(2)
        self.setHeaderLabels(['Item', 'Value'])
        self.setColumnWidth(0, 100)  # 第一列列宽设为100
        # self.tree.itemClicked.connect(self.change_func)

    def addChildren(self):
        if 'id' in self.data:
            item = QTreeWidgetItem(self)
            item.setText(0, 'id')  # 0代表第一列，即Key列
            item.setText(1, str(self.data['id']))
            # self.setItemWidget(self.mainitem, 1, self.inteditor())
            item.setIcon(0, QIcon('Model.png'))  # 为节点设置图标

        if 'Type' in self.data:
            item = QTreeWidgetItem(self)
            item.setText(0, 'Type')  # 0代表第一列，即Key列
            item.setText(1, self.data['Type'])
            # self.setItemWidget(self.mainitem, 1, self.inteditor())
            item.setIcon(0, QIcon('Model.png'))  # 为节点设置图标

        if 'function' in self.data:
            box = QComboBox()
            box.addItems(['None', 'inflow', 'outflow'])
            box.textActivated.connect(self.setFunction)

            item = QTreeWidgetItem(self)
            item.setText(0, 'function')
            self.setItemWidget(item, 1, box)
            self.itemWidget(item, 1).setCurrentText(str(self.data['function']))
            self.items['function'] = item

        if 'text' in self.data:
            colorval = QLineEdit()
            colorval.setMaxLength(15)
            colorval.editingFinished.connect(self.updateNodeText)

            item = QTreeWidgetItem(self)
            item.setText(0, 'text')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(self.data['text'])
            # self.setItemWidget(self.mainitem, 1, self.inteditor())
            item.setIcon(0, QIcon('Model.png'))  # 为节点设置图标
            self.items['text'] = item

        if 'pos' in self.data:

            '''
            item = QTreeWidgetItem(self)
            item.setText(0, 'pos_x')
            item.setText(1, str(self.data['pos'][0]))

            item = QTreeWidgetItem(self)
            item.setText(0, 'pos_y')
            item.setText(1, str(self.data['pos'][1]))
            '''

            colorval = QLineEdit()
            # 设置精度，小数点3位
            colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.nodePosChanged)

            item = QTreeWidgetItem(self)
            item.setText(0, 'pos_x')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['pos'][0]))
            self.items['pos_x'] = item

            colorval = QLineEdit()
            colorval.setValidator(QDoubleValidator(-64000.000, 64000.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.nodePosChanged)

            item = QTreeWidgetItem(self)
            item.setText(0, 'pos_y')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['pos'][1]))
            self.items['pos_y'] = item

        if 'line_width' in self.data:
            colorval = QLineEdit()
            colorval.setValidator(QDoubleValidator(0, 6400.000, 3))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(self.updateEdgeWidth)

            item = QTreeWidgetItem(self)
            item.setText(0, 'line width')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['line_width']))
            self.items['line_width'] = item

        if 'loop_times' in self.data:
            colorval = QLineEdit()
            colorval.setValidator(QIntValidator(1, 64000))
            colorval.editingFinished.connect(self.updateGroupLoopTimes)

            item = QTreeWidgetItem(self)
            item.setText(0, 'loop times')
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['loop_times']))
            self.items['loop_times'] = item

        def addFloatChild(name: str, function, Min, Max, i):
            colorval = QLineEdit()
            colorval.setValidator(QDoubleValidator(Min, Max, i))
            colorval.validator().setNotation(QDoubleValidator.Notation.StandardNotation)
            colorval.editingFinished.connect(function)

            item = QTreeWidgetItem(self)
            item.setText(0, name)
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['attribute']['default_'+name]))
            self.items['default_'+name] = item

        def addIntChild(name: str, function, Min, Max):
            colorval = QLineEdit()
            colorval.setValidator(QIntValidator(Min, Max))
            colorval.editingFinished.connect(function)

            item = QTreeWidgetItem(self)
            item.setText(0, name)
            self.setItemWidget(item, 1, colorval)
            self.itemWidget(item, 1).setText(str(self.data['attribute']['default_'+name]))
            self.items['default_'+name] = item

        if 'attribute' in self.data:
            if 'default_diameter' in self.data['attribute']:
                addFloatChild('diameter', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_height' in self.data['attribute']:
                addFloatChild('height', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_distance' in self.data['attribute']:
                addFloatChild('distance', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_total_way' in self.data['attribute']:
                addFloatChild('total_way', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_line_length' in self.data['attribute']:
                addFloatChild('line_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_r' in self.data['attribute']:
                addFloatChild('r', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_step' in self.data['attribute']:
                addIntChild('step', self.nodeMarkChanged, 1, 360)

            if 'default_N' in self.data['attribute']:
                addIntChild('N', self.nodeMarkChanged, 1, 360)

            if 'default_main_path_length' in self.data['attribute']:
                addFloatChild('main_path_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_sub_path_d' in self.data['attribute']:
                addFloatChild('sub_path_d', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_sub_path_length' in self.data['attribute']:
                addFloatChild('sub_path_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_sub_path_number' in self.data['attribute']:
                addIntChild('sub_path_number', self.nodeMarkChanged, 0, 360)

            if 'default_sub_distance' in self.data['attribute']:
                addFloatChild('sub_distance', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_bolt_length' in self.data['attribute']:
                addFloatChild('bolt_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_bolt_diameter' in self.data['attribute']:
                addFloatChild('bolt_diameter', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_line_diameter' in self.data['attribute']:
                addFloatChild('line_diameter', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_flow_length' in self.data['attribute']:
                addFloatChild('flow_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_body_length' in self.data['attribute']:
                addFloatChild('body_length', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_flow_width' in self.data['attribute']:
                addFloatChild('flow_width', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_flow_height' in self.data['attribute']:
                addFloatChild('flow_height', self.nodeMarkChanged, 0.000, 64000.000, 3)

            if 'default_level' in self.data['attribute']:
                addIntChild('level', self.nodeMarkChanged, 1, 360)

        if 'side_sockets_id' in self.data:
            item = QTreeWidgetItem(self)
            item.setText(0, 'sockets')
            item.setText(1, 'id')

            item1 = QTreeWidgetItem(item)
            item1.setText(0, 'side socket-1')
            item1.setText(1, str(self.data['side_sockets_id'][0]))
            item1.setIcon(0, QIcon('../graphic/socket.png'))  # 为节点设置图标

            item2 = QTreeWidgetItem(item)
            item2.setText(0, 'side socket-2')
            item2.setText(1, str(self.data['side_sockets_id'][1]))
            item2.setIcon(0, QIcon('../graphic/socket.png'))  # 为节点设置图标

    def setFunction(self):
        function = self.itemWidget(self.items['function'], 1).currentText()
        self.graphic.node.set_function(function)

    def updateNodeText(self):
        text = self.itemWidget(self.items['text'], 1).text()
        self.graphic.node.textGraphic.setText(text)
        self.textChangedSignal.emit(text)

    def nodePosChanged(self):
        pos_x = float(self.itemWidget(self.items['pos_x'], 1).text())
        pos_y = float(self.itemWidget(self.items['pos_y'], 1).text())
        if self.graphic.parentItem() != None:
            pos_x = self.graphic.pos().x() + pos_x - self.graphic.scenePos().x()
            pos_y = self.graphic.pos().y() + pos_y - self.graphic.scenePos().y()
        self.graphic.setPos(pos_x, pos_y)
        self.posChangedSignal.emit(pos_x, pos_y)

    def nodeMarkChanged(self):
        if self.graphic.node.attribute['name'] == 'U_way':
            self.graphic.node.attribute["default_diameter"] = float(self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_height"] = float(self.itemWidget(self.items["default_height"], 1).text())
            self.graphic.node.attribute["default_distance"] = float(self.itemWidget(self.items["default_distance"], 1).text())
            self.graphic.node.attribute["default_total_way"] = float(self.itemWidget(self.items["default_total_way"], 1).text())
        elif self.graphic.node.attribute['name'] == 'O_way':
            self.graphic.node.attribute["default_diameter"] = float(self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_line_length"] = float(self.itemWidget(self.items["default_line_length"], 1).text())
            self.graphic.node.attribute["default_r"] = float(self.itemWidget(self.items["default_r"], 1).text())
            self.graphic.node.attribute["default_step"] = int(self.itemWidget(self.items["default_step"], 1).text())
            self.graphic.node.attribute["default_N"] = int(self.itemWidget(self.items["default_N"], 1).text())
        elif self.graphic.node.attribute['name'] == 'T_way':
            self.graphic.node.attribute["default_diameter"] = float(self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_main_path_length"] = float(self.itemWidget(self.items["default_main_path_length"], 1).text())
            self.graphic.node.attribute["default_sub_path_d"] = float(self.itemWidget(self.items["default_sub_path_d"], 1).text())
            self.graphic.node.attribute["default_sub_path_length"] = float(self.itemWidget(self.items["default_sub_path_length"], 1).text())
            self.graphic.node.attribute["default_sub_path_number"] = int(self.itemWidget(self.items["default_sub_path_number"], 1).text())
            self.graphic.node.attribute["default_sub_distance"] = float(self.itemWidget(self.items["default_sub_distance"], 1).text())
        elif self.graphic.node.attribute['name'] == 'Door_way':
            self.graphic.node.attribute["default_bolt_length"] = float(
                self.itemWidget(self.items["default_bolt_length"], 1).text())
            self.graphic.node.attribute["default_bolt_diameter"] = float(
                self.itemWidget(self.items["default_bolt_diameter"], 1).text())
            self.graphic.node.attribute["default_line_length"] = float(
                self.itemWidget(self.items["default_line_length"], 1).text())
            self.graphic.node.attribute["default_line_diameter"] = float(
                self.itemWidget(self.items["default_line_diameter"], 1).text())
        elif self.graphic.node.attribute['name'] == 'K_way':
            self.graphic.node.attribute["default_flow_length"] = float(
                self.itemWidget(self.items["default_flow_length"], 1).text())
            self.graphic.node.attribute["default_body_length"] = float(
                self.itemWidget(self.items["default_body_length"], 1).text())
            self.graphic.node.attribute["default_diameter"] = float(
                self.itemWidget(self.items["default_diameter"], 1).text())
        elif self.graphic.node.attribute['name'] == 'Fork_way':
            self.graphic.node.attribute["default_flow_width"] = float(
                self.itemWidget(self.items["default_flow_width"], 1).text())
            self.graphic.node.attribute["default_flow_height"] = float(
                self.itemWidget(self.items["default_flow_height"], 1).text())
            self.graphic.node.attribute["default_diameter"] = float(
                self.itemWidget(self.items["default_diameter"], 1).text())
            self.graphic.node.attribute["default_level"] = int(
                self.itemWidget(self.items["default_level"], 1).text())
        self.graphic.node.setup()

    def updateGroupLoopTimes(self):
        times = int(self.itemWidget(self.items['loop_times'], 1).text())
        self.graphic.group.setLoopTimes(times)
        self.graphic.update()

    def updateEdgeWidth(self):
        width = float(self.itemWidget(self.items['line_width'], 1).text())
        self.graphic.edge.setWidth(width)

    def updateData(self, data={}):
        self.clear()
        self.data = data
        self.initUI()
        self.addChildren()

    def restart(self):
        self.graphic = None
        self.updateData()
