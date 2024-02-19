import json
import gc

from gui_test.scene_setting import GraphicScene
from gui_test.node_node import Node, Socket
from gui_test.edge_edge import Edge
from gui_test.item_group import Group
from gui_test.scene_history import SceneHistory


class Scene:

    def __init__(self, parent=None):
        self.nodes = []
        self.groups = []
        self.edges = []
        self.grScene = GraphicScene(self, parent)
        self.History = SceneHistory(self)
        self.has_been_saved = True
        self.HoleWindow_func = {}   # 用于储存HolwWindow中的函数

    def use_func(self, func):
        func()

    def clear(self):
        #self.grScene.clear()
        nodes = self.nodes.copy()
        for item in nodes:
            self.remove_node(item)

        groups = self.groups.copy()
        for item in groups:
            self.remove_group(item)

        gc.collect()

    def update(self):
        for grGroup in self.groups:
            grGroup.group.updateArea()
        for grEdge in self.edges:
            grEdge.edge.update_positions()

    def add_node(self, node):
        self.grScene.add_node(node)

    def remove_node(self, node):
        self.grScene.remove_node(node)

    def add_group(self, group):
        self.grScene.add_group(group)

    def remove_group(self, group):
        self.grScene.remove_group(group)

    def add_edge(self, edge):
        self.grScene.add_edge(edge)

    def remove_edge(self, edge):
        self.grScene.remove_edge(edge)

    def item_to_string(self):
        data = {}
        # data['graph_name'] = ''
        # data['time'] = ''
        data['nodes'] = []
        data['groups'] = []
        data['edges'] = []

        # 保存node
        for grNode in self.nodes:
            # print(node.node.to_string())  # debug
            data['nodes'].append(grNode.node.to_string())

        for grGroup in self.groups:
            data['groups'].append(grGroup.group.to_string())

        # 保存edge
        for grEdge in self.edges:
            data['edges'].append(grEdge.edge.to_string())

        return data

    def save_graph(self, filename):
        data = self.item_to_string()
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4))

    def string_to_item(self, data={}, hashmap={}):
        for node_message in data['nodes']:
            #node = Node(self, attribute=node_message['attribute'])
            node = globals()[node_message['Type']](self, attribute=node_message['attribute'])
            node.grNode.setPos(node_message['pos'][0], node_message['pos'][1])
            node.textGraphic.setText(node_message['text'])
            node.set_function(node_message['function'])
            node.to_hashmap(node_message, hashmap)

        for group_message in data['groups']:
            group = globals()[group_message['Type']](self)
            group.grGroup.setPos(group_message['pos'][0], group_message['pos'][1])
            group.setLoopTimes(group_message['loop_times'])
            for item_id in group_message['child_item_id']:
                group.addToGroup(hashmap[item_id].grNode)
            group.updateArea()
            group.to_hashmap(group_message, hashmap)

        # 遍历每条连线
        for edge_message in data['edges']:
            # 确定起始和终点的插口的id
            start_id = edge_message['side_sockets_id'][0]
            end_id = edge_message['side_sockets_id'][1]
            start_socket = hashmap[start_id].grSocket
            end_socket = hashmap[end_id].grSocket
            edge = Edge(self, start_socket, end_socket, attribute=edge_message['attribute'])
            edge.setWidth(edge_message['line_width'])
            edge.to_hashmap(edge_message, hashmap)
        #for node in self.nodes:
        #    node.node.set_id()
        #    for socket in node.node.sockets:
        #        socket.socket.set_id()

        return hashmap

    def open_graph(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf-8')
        self.string_to_item(data)
