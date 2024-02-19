from PySide6.QtGui import Qt
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog
from gui_real.scene_setting import GraphicScene
from gui_real.node_node import Node, Socket
from gui_real.edge_edge import Edge
from gui_real.hole_hole import HoleSocket
from gui_real.edge_setting import GraphicCantSeeSocket
from gui_real.baseShape_baseShape import baseShape, Rect
from model_make.voluntary import Layout

import json
import cadquery as cq


class Scene(QObject):
    openFileSignal = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model3D_baseShape = cq.Workplane()
        self.model3D_way = cq.Workplane()
        self.nodes = []
        self.edges = []
        self.holes = []
        self.layer_setup()
        self.grScene = GraphicScene(self, parent)
        self.baseShape = baseShape(self)
        #self.History = SceneHistory(self)
        self.has_been_saved = True
        self.HoleWindow_func = []   # 用于储存HolwWindow中的函数

    def updateEdges(self):
        for grEdge in self.edges:
            grEdge.edge.update_positions()


    def layer_setup(self, number=0):
        self.currentLayer = 0
        self.layers = [[]]
        self.layersValue = [300]
        for i in range(number - 1):
            self.add_layer()

    def add_layer(self):
        self.layers.append([])
        self.layersValue.append(300)

    def remove_layer(self, i):
        items = self.layers[i].copy()
        for item in items:
            if hasattr(item, 'node'):
                item.node.set_layer(i-1)
        for grHole in self.holes:
            grHole.hole.reset_layer()
        self.layers.pop(i)
        self.layersValue.pop(i)

    def insertLayer(self, i):
        self.layers.insert(i, [])
        self.layersValue.insert(i, 300)
        self.updateLayers()

    def updateLayers(self):
        for i in range(len(self.layers)):
            for item in self.layers[i]:
                item.node.layer = i

    def add_node(self, node):
        self.grScene.add_node(node)

    def remove_node(self, node):
        self.grScene.remove_node(node)

    def add_hole(self, hole):
        self.grScene.add_hole(hole)

    def remove_hole(self, hole):
        self.grScene.remove_hole(hole)

    def add_edge(self, edge):
        self.grScene.add_edge(edge)

    def remove_edge(self, edge):
        self.grScene.remove_edge(edge)

    def setLayer(self, layer):
        self.currentLayer = layer
        for grNode in self.nodes:
            grNode.node.set_layer(grNode.node.layer)
            grNode.setProhibit()
        for grHole in self.holes:
            grHole.setProhibit()
        for grEdge in self.edges:
            if grEdge.edge.layer == layer:
                grEdge.setEnable()
            else:
                grEdge.setProhibit()
        for grItem in self.layers[layer]:
            grItem.setEnable()
        for i in self.layers:
            print(len(i))

    def setLayerValue(self, layer, value):
        self.layersValue[layer] = value
        self.setLayer(self.currentLayer)

    def loading(self, data):
        # 记录所有对象，使用它们在gui_test阶段时的id，对应gui_real阶段时的对象
        # 形如{old_id:item}
        hashmap = {}
        # 记录group里node的所有克隆的node，id使用原node的gui_real环境下的id
        # 形如{node_id:[node1, node1_clone1, node1_clone2]}
        group_node_op = {}
        # 记录group里的socket信息，id使用gui_test阶段时的id，对外socket和对内socket是相连接的，但我们不需要将它们画出来，也不需要连起来
        # group_id对应略去group的socket后应当连接的两socket，socket_id对应socket所在的group的id
        # socket的父项为item（node）
        # 形如{group_id:{'LEFT':[start_socket_id, end_socket_id], 'RIGHT':[start_socket_id, end_socket_id]}}
        group_socket_op = {}
        # socket的父类为为group
        # 形如{socket1_id:[group_id, 'LEFT'], socket2_id:[group_id, 'LEFT']}
        socket_group_op = {}
        # 记录存在group子socket的edge的线宽
        # 形如{socket_id:line_width}
        line_width = {}

        item_left = None    # 记录group中最左侧的item（node）
        item_right = None   # 记录group中最右侧的item（node）

        pos_count_x = 0
        pos_count_y = 0
        max_y = 0
        for node_message in data['nodes']:
            if pos_count_x >= 4000:
                pos_count_x = 0
                pos_count_y = max_y
                max_y = 0
            node = globals()[node_message['Type']](self, attribute=node_message['attribute'])
            node.grNode.setPos(pos_count_x, pos_count_y)
            node.set_function(node_message['function'])
            pos_count_x += node.grNode.boundingRect().width() + 50
            if node.grNode.boundingRect().height() >= pos_count_y - 50:
                max_y = node.grNode.boundingRect().height() + 50
            node.to_hashmap(node_message, hashmap)

        for group_message in data['groups']:
            self.socketId_group_op(group_message, group_socket_op, socket_group_op)
            for item_id in group_message['child_item_id']:
                group_node_op[hashmap[item_id].id] = [hashmap[item_id]]
                for i in range(group_message['loop_times'] - 1):
                    if pos_count_x >= 4000:
                        pos_count_x = 0
                        pos_count_y = max_y
                        max_y = 0
                    node = Node(self, attribute=hashmap[item_id].attribute)
                    node.grNode.setPos(pos_count_x, pos_count_y)
                    node.set_function(hashmap[item_id].function)
                    pos_count_x += node.grNode.boundingRect().width() + 50
                    if node.grNode.boundingRect().height() >= pos_count_y - 50:
                        max_y = node.grNode.boundingRect().height() + 50
                    group_node_op[hashmap[item_id].id].append(node)
            self.group_to_hashmap(group_message, hashmap)

        for edge_message in data['edges']:
            start_id = edge_message['side_sockets_id'][0]
            end_id = edge_message['side_sockets_id'][1]
            if hashmap[start_id] and hashmap[end_id]:
                start_item = hashmap[start_id].grSocket.parentItem().node
                end_item = hashmap[end_id].grSocket.parentItem().node
                if start_item.id in group_node_op and end_item.id in group_node_op:
                    start_index = start_item.sockets.index(hashmap[start_id].grSocket)
                    end_index = end_item.sockets.index(hashmap[end_id].grSocket)
                    for i in range(len(group_node_op[start_item.id])):
                        start_socket = group_node_op[start_item.id][i].sockets[start_index]
                        end_socket = group_node_op[end_item.id][i].sockets[end_index]
                        edge = Edge(self, start_socket, end_socket, attribute=edge_message['attribute'])
                        edge.setWidth(edge_message['line_width'])
                        edge.to_hashmap(edge_message, hashmap)

                else:
                    start_socket = hashmap[start_id].grSocket
                    end_socket = hashmap[end_id].grSocket
                    edge = Edge(self, start_socket, end_socket, attribute=edge_message['attribute'])
                    edge.setWidth(edge_message['line_width'])
                    edge.to_hashmap(edge_message, hashmap)

            elif hashmap[start_id]:
                group_id = socket_group_op[end_id][0]
                position = socket_group_op[end_id][1]
                group_socket_op[group_id][position].append(start_id)
                line_width[start_id] = edge_message['line_width']

            elif hashmap[end_id]:
                group_id = socket_group_op[start_id][0]
                position = socket_group_op[start_id][1]
                group_socket_op[group_id][position].append(end_id)
                line_width[end_id] = edge_message['line_width']

        for side_sockets in group_socket_op.values():
            if side_sockets['LEFT'] and side_sockets['RIGHT']:
                socket_start_id = side_sockets['LEFT'][0]
                socket_end_id = side_sockets['LEFT'][1]
                start_item = hashmap[socket_start_id].grSocket.parentItem().node
                end_item = hashmap[socket_end_id].grSocket.parentItem().node
                if start_item.id in group_node_op:
                    item_left = start_item
                    index_left = start_item.sockets.index(hashmap[socket_start_id].grSocket)
                    socket1 = group_node_op[start_item.id][0].sockets[index_left]
                    socket2 = hashmap[socket_end_id].grSocket
                    edge = Edge(self, socket1, socket2)
                    edge.setWidth(line_width[socket_end_id])
                elif end_item.id in group_node_op:
                    item_left = end_item
                    index_left = end_item.sockets.index(hashmap[socket_end_id].grSocket)
                    socket1 = group_node_op[end_item.id][0].sockets[index_left]
                    socket2 = hashmap[socket_start_id].grSocket
                    edge = Edge(self, socket1, socket2)
                    edge.setWidth(line_width[socket_start_id])

                socket_start_id = side_sockets['RIGHT'][0]
                socket_end_id = side_sockets['RIGHT'][1]
                start_item = hashmap[socket_start_id].grSocket.parentItem().node
                end_item = hashmap[socket_end_id].grSocket.parentItem().node
                if start_item.id in group_node_op:
                    item_right = start_item
                    index_right = start_item.sockets.index(hashmap[socket_start_id].grSocket)
                    socket1 = group_node_op[start_item.id][-1].sockets[index_right]
                    socket2 = hashmap[socket_end_id].grSocket
                    edge = Edge(self, socket1, socket2)
                    edge.setWidth(line_width[socket_end_id])
                elif end_item.id in group_node_op:
                    item_right = end_item
                    index_right = end_item.sockets.index(hashmap[socket_end_id].grSocket)
                    socket1 = group_node_op[end_item.id][-1].sockets[index_right]
                    socket2 = hashmap[socket_start_id].grSocket
                    edge = Edge(self, socket1, socket2)
                    edge.setWidth(line_width[socket_start_id])

                for i in range(len(group_node_op[item_right.id]) - 1):
                    socket1 = group_node_op[item_right.id][i].sockets[index_right]
                    socket2 = group_node_op[item_left.id][i + 1].sockets[index_left]
                    edge = Edge(self, socket1, socket2)
                    if start_item.id in group_node_op:
                        edge.setWidth(line_width[socket_end_id])
                    elif end_item.id in group_node_op:
                        edge.setWidth(line_width[socket_start_id])

    def group_to_hashmap(self, group_message, hashmap={}):
        for socket_message in group_message['sockets']:
            hashmap[socket_message['id']] = None

    def socketId_group_op(self, group_message, group_socket_op={}, socket_group_op={}):
        group_socket_op[group_message['id']] = {}
        group_socket_op[group_message['id']]['LEFT'] = []
        group_socket_op[group_message['id']]['RIGHT'] = []
        socket_message_list = group_message['sockets']
        socket_group_op[socket_message_list[0]['id']] = [group_message['id'], 'LEFT']
        socket_group_op[socket_message_list[1]['id']] = [group_message['id'], 'LEFT']
        socket_group_op[socket_message_list[2]['id']] = [group_message['id'], 'RIGHT']
        socket_group_op[socket_message_list[3]['id']] = [group_message['id'], 'RIGHT']

    def item_to_string(self):
        data = {}
        # data['graph_name'] = ''
        # data['time'] = ''
        data['layers'] = len(self.layers)
        data['layer_value'] = self.layersValue
        data['base_shapes'] = self.baseShape.to_string()['shapes']
        data['nodes'] = []
        data['holes'] = []
        data['edges'] = []

        # 保存node
        for grNode in self.nodes:
            # print(node.node.to_string())  # debug
            data['nodes'].append(grNode.node.to_string())

        for grHole in self.holes:
            data['holes'].append(grHole.hole.to_string())

        # 保存edge
        for grEdge in self.edges:
            data['edges'].append(grEdge.edge.to_string())

        return data

    def save_graph(self, filename):
        data = self.item_to_string()
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4))

    def string_to_item(self, data={}, hashmap={}):
        for shape_message in data['base_shapes']:
            rect = Rect()
            rect.reset(shape_message['pos'][0], shape_message['pos'][1], shape_message['area'][0], shape_message['area'][1], shape_message['thickness'])
            self.baseShape.addSceneRect(rect)

        self.layer_setup(data['layers'])
        self.layersValue = data['layer_value']
        for node_message in data['nodes']:
            #node = Node(self, attribute=node_message['attribute'])
            node = globals()[node_message['Type']](self, attribute=node_message['attribute'])
            node.set_function(node_message['function'])
            node.grNode.setRotation(node_message['rotation'])
            node.grNode.setPos(node_message['pos'][0], node_message['pos'][1])
            for grSocket in node.sockets:
                count = node.sockets.index(grSocket)
                grSocket.socket.set_layer(node_message['sockets'][count]['layer'])
            node.layer = node_message['layer']
            node.to_hashmap(node_message, hashmap)

        for hole_message in data['holes']:
            hole = HoleSocket(self)
            hole.grHole.setPos(hole_message['pos'][0], hole_message['pos'][1])
            hole.mySocket1.set_layer(hole_message['sockets'][0]['layer'])
            hole.mySocket2.set_layer(hole_message['sockets'][1]['layer'])
            hole.to_hashmap(hole_message, hashmap)

        for grHole in self.holes:
            count = self.holes.index(grHole)
            socket1 = hashmap[data['holes'][count]['side_sockets_id'][0]].grSocket
            socket2 = hashmap[data['holes'][count]['side_sockets_id'][1]].grSocket
            grHole.hole.set_socket(socket1, socket2)

        # 遍历每条连线
        for edge_message in data['edges']:
            # 确定起始和终点的插口的id
            start_id = edge_message['side_sockets_id'][0]
            end_id = edge_message['side_sockets_id'][1]
            start_socket = hashmap[start_id].grSocket
            end_socket = hashmap[end_id].grSocket
            edge = Edge(self, start_socket, end_socket, attribute=edge_message['attribute'])
            edge.setWidth(edge_message['line_width'])

            for pos in edge_message['start_point_list']:
                grSocket = GraphicCantSeeSocket(edge.grEdge)
                grSocket.setPos(pos[0], pos[1])
                edge.start_point_list.append(grSocket)
            for pos in edge_message['end_point_list']:
                grSocket = GraphicCantSeeSocket(edge.grEdge)
                grSocket.setPos(pos[0], pos[1])
                edge.end_point_list.append(grSocket)
            for pos in edge_message['move_point']:
                grSocket = GraphicCantSeeSocket(edge.grEdge)
                grSocket.setPos(pos[0], pos[1])
                edge.move_point.append(grSocket)
            edge.to_hashmap(edge_message, hashmap)

        for grNode in self.nodes:
            grNode.node.set_layer(grNode.node.layer)
        self.setLayer(0)
        print(123)

        self.openFileSignal.emit()
        print('end')

        return hashmap

    def open_graph(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf-8')
        self.string_to_item(data)

    def getZValue(self, layer):
        z_value = -self.layersValue[layer]/2
        for i in range(layer):
            z_value -= self.layersValue[i]
        return z_value

    def to_3DModel(self, fname):
        self.model3D_baseShape = cq.Workplane()
        self.model3D_way = cq.Workplane()
        thickness = 0
        for i in self.layersValue:
            thickness += i
        for shape in self.baseShape.shapes:
            self.model3D_baseShape += cq.Workplane().box(shape.width/10, shape.height/10, shape.thickness/10).translate([shape.posSource[0]/10+shape.width/20, shape.posSource[1]/10+shape.height/20, -shape.thickness/20]).edges('|Z').fillet(4)
            # self.model3D_baseShape += cq.Workplane().box(shape.width/10 + 20, shape.height/10 + 20, 0.4).translate([shape.posSource[0]/10+shape.width/20, shape.posSource[1]/10+shape.height/20, 0.2]).edges('|Z').fillet(5)
        for grEdge in self.edges:
            if grEdge.edge.get_3Dmodel():
                self.model3D_baseShape -= grEdge.edge.get_3Dmodel()
                self.model3D_way += grEdge.edge.get_3Dmodel()
        for grNode in self.nodes:
            if self.baseShape.shapes:
                self.model3D_baseShape -= grNode.node.get_3Dmodel()
            self.model3D_way += grNode.node.get_3Dmodel()
        for grHole in self.holes:
            if self.baseShape.shapes:
                self.model3D_baseShape -= grHole.hole.get_3Dmodel()
            self.model3D_way += grHole.hole.get_3Dmodel()
        if self.baseShape.shapes:
            cq.exporters.export(self.model3D_baseShape, fname)
            # cq.exporters.export(self.model3D_way, fname)
        else:
            cq.exporters.export(self.model3D_way, fname)

    def voluntary_default(self, data):
        a = Layout(data, angle_change=True)
        self.string_to_item(a.get_data())

    def voluntary_static(self, data):
        a = Layout(data, angle_change=False)
        self.string_to_item(a.get_data())

