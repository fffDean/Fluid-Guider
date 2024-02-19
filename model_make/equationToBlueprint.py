from model_make.cq_code import *
import json
import random


class EquationToBlueprint:
    def __init__(self, data):
        self.equationData = data
        self.endNode = None
        self.idToTestNode = {}
        self.edgeToWindowDict = {}
        self.continuousWindow = []
        self.subMainWindows = []
        self.setup()
        self.takeTogether(self.endNode)

    def setup(self):
        # 先处理节点的指向关系
        self.hashmap = {}
        self.node_PTM = {}  # value指向key的字典
        self.node_PTO = {}  # key指向value的字典
        for edge_message in self.equationData['edges']:
            self.hashmap[edge_message['id']] = edge_message
            id1 = edge_message['side_nodes_id'][0]
            id2 = edge_message['side_nodes_id'][1]
            self.node_PTO[id1] = id2
            if id2 not in self.node_PTM:
                self.node_PTM[id2] = [id1]
            else:
                self.node_PTM[id2].append(id1)

        for node_message in self.equationData['nodes']:
            self.hashmap[node_message['id']] = node_message

        # 查找有向图的终点， 即出度为零的节点（因为是化学方程式所以肯定存在出度为零的节点）
        for node in self.equationData['nodes']:
            if not node['ops']:
                self.endNode = node
                break
        # 从有向图的终点开始， 向前逐级查找
        current_nodes = [self.endNode]
        while current_nodes:
            next_nodes = []
            for current_node in current_nodes:
                nodes_list = []     # 指向current_node的节点的列表
                if current_node['id'] in self.node_PTM:     # 如果当前节点不是起始节点
                    for next_node_id in self.node_PTM[current_node['id']]:
                        next_node = self.hashmap[next_node_id]
                        nodes_list.append(next_node)
                        next_nodes.append(next_node)
                    child = self.makeBlueprint(nodes_list, current_node)
                    self.edgeToWindowDict[nodes_list[0]['ops']] = child
                    self.subMainWindows.append(child)
            current_nodes = next_nodes

    def makeBlueprint(self, inflows_list, current_node):
        child = {}
        nodes = []
        edges = []
        extract_mark = False
        filter_mark = False
        inflows = []
        outflow = None
        actions = []

        x_count = 0
        x_add = 0
        y_count = 0
        for node_message in inflows_list:
            way = Door_way()
            attribute = way.get_attribute()
            inflow_node = Node(attribute)
            inflow_node.set_function('inflow')
            inflow_node.grNode.setPos(x_count, y_count)
            inflows.append(inflow_node)
            nodes.append(inflow_node)
            self.idToTestNode[node_message['id']] = inflow_node.data

            ops_id = node_message['ops']
            action = self.hashmap[ops_id]['attribute']
            if action['heat'] or action['chill']:
                way = U_way()
                attribute = way.get_attribute()
                action_node = Node(attribute)
                action_node.grNode.setPos(x_count + inflow_node.attribute['area'][0] + 100, y_count)
                actions.append(action_node)
                nodes.append(action_node)
                edge = Edge(inflow_node.sockets[-1], action_node.sockets[0])
                edges.append(edge)
                inflows[-1] = action_node
                y_count += max(inflow_node.attribute['area'][1], action_node.attribute['area'][1]) + 100
            else:
                y_count += inflow_node.attribute['area'][1] + 100
            if inflows[-1].attribute['area'][0] + inflows[-1].grNode.x() > x_add:
                x_add = inflows[-1].attribute['area'][0] + inflows[-1].grNode.x()

            if action['extract']:
                extract_mark = True

            if action['filter']:
                filter_mark = True

        x_count += x_add + 100
        # 如果要萃取
        if extract_mark:
            way = K_way()
            attribute = way.get_attribute()
            action_node = Node(attribute)
            action_node.grNode.setPos(x_count, y_count/2)
            actions.append(action_node)
            nodes.append(action_node)
            edge = Edge(inflows[0].sockets[-1], action_node.sockets[0])
            edges.append(edge)
            edge = Edge(inflows[1].sockets[-1], action_node.sockets[1])
            edges.append(edge)
            x_count += attribute['area'][0] + 100

            # 排出废液节点
            way = Door_way()
            attribute = way.get_attribute()
            other_node = Node(attribute)
            other_node.grNode.setPos(x_count, 0)
            nodes.append(other_node)
            edge = Edge(action_node.sockets[2], other_node.sockets[0])
            edges.append(edge)

            inflows[-1] = action_node
        # 普通混合情况
        else:
            number = len(inflows_list)
            way = T_way(sub_path_number=number-1)
            attribute = way.get_attribute()
            action_node = Node(attribute)
            action_node.grNode.setPos(x_count, y_count / 2)
            actions.append(action_node)
            nodes.append(action_node)
            for i in range(number):
                edge = Edge(inflows[i].sockets[-1], action_node.sockets[i])
                edges.append(edge)
            inflows[-1] = action_node
            x_count += attribute['area'][0] + 100
            # 混合
            way = U_way()
            attribute = way.get_attribute()
            action_node = Node(attribute)
            action_node.grNode.setPos(x_count, y_count/2)
            nodes.append(action_node)
            edge = Edge(inflows[-1].sockets[-1], action_node.sockets[0])
            edges.append(edge)
            inflows[-1] = action_node
            x_count += attribute['area'][0] + 100
        # 输出节点
        way = Door_way()
        attribute = way.get_attribute()
        outflow = Node(attribute)
        outflow.set_function('outflow')
        outflow.grNode.setPos(0, y_count)
        nodes.append(outflow)
        edge = Edge(inflows[-1].sockets[-1], outflow.sockets[0])
        edges.append(edge)
        y_count += attribute['area'][1] + 100

        child['nodes'] = []
        for node in nodes:
            child['nodes'].append(node.data)
        child['edges'] = []
        for edge in edges:
            child['edges'].append(edge.data)
        child['groups'] = []
        child['width'] = x_count
        child['height'] = y_count
        if filter_mark:
            child['filter'] = True
        else:
            child['filter'] = False

        return child

    def takeTogether(self, last_node):
        current_nodes = [last_node]
        data = self.edgeToWindowDict[last_node['fr']].copy()
        count_x = 0
        count_y = 0
        while current_nodes:
            next_nodes = []
            for current_node in current_nodes:
                if current_node['id'] in self.node_PTM:  # 如果当前节点不是起始节点
                    if current_node != last_node:     # 如果当前节点不是终点
                        child = self.edgeToWindowDict[self.hashmap[self.node_PTM[current_node['id']][0]]['ops']].copy()
                        if child['filter']:
                            self.takeTogether(current_node)
                        else:
                            count_x += child['width']
                            count_y += child['height']
                            for node in child['nodes']:
                                node['pos'][0] -= count_x
                                node['pos'][1] -= count_y

                            inflow_node = self.idToTestNode[current_node['id']]
                            data['nodes'].remove(inflow_node)
                            middle_node = child['nodes'].pop()
                            for edge in data['edges']:
                                if edge['side_sockets_id'][0] == inflow_node['sockets'][-1]['id']:
                                    first_edge = edge.copy()
                                    data['edges'].remove(edge)
                            last_edge = child['edges'].pop()
                            data_id_mark = random.random()
                            edge_data = {
                                'id': id(data_id_mark),
                                'Type': self.__class__.__name__,
                                'line_width': 10,
                                'attribute': {},
                                'side_sockets_id': [last_edge['side_sockets_id'][0], first_edge['side_sockets_id'][1]]
                            }
                            child['edges'].append(edge_data)
                            data['nodes'] = child['nodes'] + data['nodes']
                            data['edges'] = child['edges'] + data['edges']
                            for next_node_id in self.node_PTM[current_node['id']]:
                                next_node = self.hashmap[next_node_id]
                                next_nodes.append(next_node)
                    else:
                        for next_node_id in self.node_PTM[current_node['id']]:
                            next_node = self.hashmap[next_node_id]
                            next_nodes.append(next_node)
            current_nodes = next_nodes
        self.continuousWindow.append(data)

    def getdata(self):
        with open('nodeslist.txt', 'r', encoding='utf-8') as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf-8')

            return data

    def makePart(self, cq_name, window):
        way = globals()[cq_name]()
        attribute = way.get_attribute()
        node = Node(attribute)
        return node


class Node:
    def __init__(self, attribute):
        self.attribute = attribute
        self.grNode = self
        self.sockets = []
        self.data = {
            'id': id(self),
            'Type': self.__class__.__name__,
            'function': None,
            'text': 'New Node',
            'pos': [0, 0],
            'attribute': self.attribute,
            'sockets': []
        }
        for socket_message in self.attribute['sockets']:
            socket = Socket(socket_message)
            self.data['sockets'].append(socket.data)
            self.sockets.append(socket.data)

    def setPos(self, x, y):
        self.data['pos'] = [x, y]

    def set_function(self, function):
        self.data['function'] = function

    def x(self):
        return self.data['pos'][0]

    def y(self):
        return self.data['pos'][1]


class Socket:
    def __init__(self, socketMessage):
        self.socket = socketMessage
        self.data = {
            'id': id(self.socket),
            'Type': self.__class__.__name__
        }


class Edge:
    def __init__(self, start_socket, end_socket, attribute={}):
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.data = {
            'id': id(self),
            'Type': self.__class__.__name__,
            'line_width': 10,
            'attribute': attribute,
            'side_sockets_id': [start_socket['id'], end_socket['id']]
        }

