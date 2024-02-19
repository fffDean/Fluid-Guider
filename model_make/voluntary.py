from model_make.Astar import AStarSearch, Map

import math
import copy


LEFT = [-1, 0]
RIGHT = [1, 0]
TOP = [0, -1]
BOTTOM = [0, 1]

class Layout:
    def __init__(self, data, angle_change=False):
        self.data = data
        self.inflowNode = []
        self.outflowNode = []
        self.topological_group = []
        self.nodes = []
        self.lump_width_value = []
        self.lump_distance = []
        self.lump_list = []
        self.layers = 1
        self.length_x = 0
        self.length_y = 0
        self.length_z = 0
        self.other_maps = []
        self.holes = []
        self.edges = []
        self.loading(angle_change)
        self.make_map()
        self.draw_up()

    def loading(self, angle_change=False):
        self.hashmap = {}
        self.socket_op_map = {}
        self.socket_node_map = {}
        nodes = []
        for edge_message in self.data['edges']:
            id1 = edge_message['side_sockets_id'][0]
            id2 = edge_message['side_sockets_id'][1]
            self.socket_op_map[id1] = id2
            self.socket_op_map[id2] = id1
        for node_message in self.data['nodes']:
            message = {}
            message['id'] = node_message['id']
            message['Type'] = node_message['Type']
            message['function'] = node_message['function']
            message['rotation'] = node_message['rotation']
            message['layer'] = node_message['layer']
            message['area'] = node_message['attribute']['real_area']
            message['pos'] = [0, 0]
            message['transformpoint'] = node_message['attribute']['transformpoint']
            message['zValue_upper'] = node_message['attribute']['zValue_upper']
            message['zValue_lower'] = node_message['attribute']['zValue_lower']
            message['attribute'] = node_message['attribute']
            for i in range(len(node_message['sockets'])):
                node_message['sockets'][i]['pos'] = node_message['attribute']['sockets'][i]['real_pos']
                node_message['sockets'][i]['position'] = node_message['attribute']['sockets'][i]['position']
            message['sockets'] = node_message['sockets']
            for socket_message in node_message['sockets']:
                self.socket_node_map[socket_message['id']] = message
                self.hashmap[socket_message['id']] = socket_message
            if len(node_message['sockets']) == 1:
                if node_message['function'] == 'inflow':
                    self.inflowNode.append(message)
                elif node_message['function'] == 'outflow':
                    self.outflowNode.append(message)
            else:
                nodes.append(message)

        def degree(position, standard):
            if position == standard:
                return 0
            elif standard == intRotate(position, 180):
                return 180
            elif standard == intRotate(position, -90):
                return -90
            elif standard == intRotate(position, 90):
                return 90

        def nodeRotate(_node, _angle):
            _node['area'] = absRotate(_node['area'], _angle)
            _node['transformpoint'] = rotate(_node['transformpoint'], _angle)
            _node['rotation'] = _angle
            for _socket in _node['sockets']:
                _socket['position'] = intRotate(_socket['position'], _angle)
                _socket['pos'] = rotate(_socket['pos'], _angle)
            if _angle == 180:
                _node['transformpoint'] = [_node['transformpoint'][0] + _node['area'][0], _node['transformpoint'][1] + _node['area'][1]]
                for _socket in _node['sockets']:
                    _socket['pos'] = [_socket['pos'][0]+_node['area'][0], _socket['pos'][1]+_node['area'][1]]
            elif _angle == 90:
                _node['transformpoint'] = [_node['transformpoint'][0] + _node['area'][0],
                                           _node['transformpoint'][1]]
                for _socket in _node['sockets']:
                    _socket['pos'] = [_socket['pos'][0] + _node['area'][0], _socket['pos'][1]]
            elif _angle == -90:
                _node['transformpoint'] = [_node['transformpoint'][0],
                                           _node['transformpoint'][1] + _node['area'][1]]
                for _socket in _node['sockets']:
                    _socket['pos'] = [_socket['pos'][0], _socket['pos'][1] + _node['area'][1]]
            return _node

        def intRotate(pos, _angle):
            _angle = math.radians(_angle)
            x = pos[0]
            y = pos[1]
            new = [round(x * math.cos(_angle) - y * math.sin(_angle)), round(x * math.sin(_angle) + y * math.cos(_angle))]
            return new

        def rotate(pos, _angle):
            _angle = math.radians(_angle)
            x = pos[0]
            y = pos[1]
            new = [x*math.cos(_angle) - y*math.sin(_angle), x*math.sin(_angle) + y*math.cos(_angle)]
            return new

        def absRotate(pos, _angle):
            _angle = math.radians(_angle)
            x = pos[0]
            y = pos[1]
            new = [abs(x * math.cos(_angle) - y * math.sin(_angle)), abs(x * math.sin(_angle) + y * math.cos(_angle))]
            return new

        self.currentNodes = []
        for node_message in self.inflowNode + self.outflowNode:

            socket_message = node_message['sockets'][0]
            angle = degree(socket_message['position'], [1, 0])
            node_message = nodeRotate(node_message, angle)

            self.currentNodes.append(node_message)
            self.nodes.append(node_message)


        while True:
            currentNodes = []
            for node_message in self.currentNodes:
                for socket_message in node_message['sockets']:
                    if socket_message['id'] in self.socket_op_map:
                        op_socket_id = self.socket_op_map[socket_message['id']]
                        node = self.socket_node_map[op_socket_id]
                        socket = self.hashmap[op_socket_id]
                        if node not in self.nodes:
                            if angle_change:
                                standard = [-socket_message['position'][0], -socket_message['position'][1]]
                                angle = degree(socket['position'], standard)
                                node = nodeRotate(node, angle)
                            else:
                                node = nodeRotate(node, node['rotation'])
                            self.nodes.append(node)
                            currentNodes.append(node)
            self.currentNodes = currentNodes
            if not self.currentNodes:
                break
            else:
                self.topological_group.append(currentNodes)

        y_count = 0
        x_count = 0
        y_distance = 100
        x_distance = 40
        for node_message in self.inflowNode + self.outflowNode:
            socket_message = node_message['sockets'][0]
            delta_y = node_message['transformpoint'][1]
            node_message['pos'] = [node_message['transformpoint'][0], y_count + y_distance + delta_y]
            y_count += y_distance + node_message['area'][1]
            if node_message['area'][0] + x_distance > x_count:
                x_count = node_message['area'][0] + x_distance
        self.length_y = y_count + y_distance

        for node_message in self.nodes:
            up = node_message['zValue_upper']
            down = node_message['zValue_lower']
            if not node_message['function'] and max(up, down) > self.length_z/2:
                self.length_z = 2 * max(up, down)
            if node_message['area'][1] + y_distance > self.length_y:
                self.length_y = node_message['area'][1] + y_distance

        # print(self.nodes[-2]['pos'], self.nodes[-2]['transformpoint'])

        for group in self.topological_group:
            m = 0
            distance = self.length_y
            max_width = 0
            y_count = 0

            lump = []
            for node_message in group:
                if distance >= node_message['area'][1] + (m+1)*y_distance/2:
                    m += 1
                    distance -= node_message['area'][1]
                    lump.append(node_message)
                    if node_message['area'][0] > max_width:
                        max_width = node_message['area'][0]
                else:
                    self.lump_width_value.append(max_width)
                    self.lump_distance.append(distance/(m+1))
                    self.lump_list.append(lump)
                    m = 0
                    lump = []
                    m += 1
                    lump.append(node_message)
                    distance = self.length_y - node_message['area'][1] - y_distance/2
                    max_width = node_message['area'][0]
            self.lump_width_value.append(max_width)
            self.lump_distance.append(distance / (m+1))
            self.lump_list.append(lump)

        # self.lump_list.reverse()
        # self.lump_distance.reverse()
        # self.lump_width_value.reverse()
        for i in range(len(self.lump_width_value)):
            distance = self.lump_distance[i]
            max_width = self.lump_width_value[i]
            y_count = 0
            for node_message in self.lump_list[i]:
                node_message['pos'] = [x_count+node_message['transformpoint'][0], y_count+node_message['transformpoint'][1]+distance]
                y_count += distance+node_message['area'][1]
            x_count += max_width + 40
        self.length_x = x_count

    def make_map(self):
        self.other_maps = []
        self.map = [[0 for i in range(int(self.length_y/10)+1)] for j in range(int(self.length_x/10)+1)]
        self.map_edge = [[0 for i in range(int(self.length_y/10)+1)] for j in range(int(self.length_x/10)+1)]
        for node_message in self.nodes:
            if node_message['attribute']['name'] == 'Door_way':
                pass
            else:
                width = int(node_message['area'][0]/10) + 1
                height = int(node_message['area'][1]/10) + 1
                print(width, height)
                x = int(node_message['pos'][0]/10 - node_message['transformpoint'][0]/10)
                y = int(node_message['pos'][1]/10 - node_message['transformpoint'][1]/10)
                print(x, y)
                for i in range(x, x+width+1):
                    for j in range(y, y+height+1):
                        self.map[i][j] = 1
                        # self.map_edge[i][j] = 2


    def draw_up(self):
        for edge_message in self.data['edges']:
            id1 = edge_message['side_sockets_id'][0]
            id2 = edge_message['side_sockets_id'][1]
            socket1 = self.hashmap[id1]
            socket2 = self.hashmap[id2]
            node1 = self.socket_node_map[id1]
            node2 = self.socket_node_map[id2]
            source = (int(node1['pos'][0]/10 - node1['transformpoint'][0]/10 + socket1['pos'][0]/10), int(node1['pos'][1]/10 - node1['transformpoint'][1]/10 + socket1['pos'][1]/10))
            dest = (int(node2['pos'][0]/10 - node2['transformpoint'][0]/10 + socket2['pos'][0]/10), int(node2['pos'][1]/10 - node2['transformpoint'][1]/10 + socket2['pos'][1]/10))
            for i in range(2):
                x1 = source[0] + i*socket1['position'][0]
                y1 = source[1] + i*socket1['position'][1]
                x2 = dest[0] + i*socket2['position'][0]
                y2 = dest[1] + i*socket2['position'][1]
                if self.map_edge[x1][y1] == 0:
                    self.map[x1][y1] = 0
                if self.map_edge[x2][y2] == 0:
                    self.map[x2][y2] = 0
            _map = Map(self.map)
            way = AStarSearch(_map, source, dest)
            if way:
                way_r = copy.deepcopy(way)

                source_r = [int(node1['pos'][0] - node1['transformpoint'][0] + socket1['pos'][0]) / 10,
                            int(node1['pos'][1] - node1['transformpoint'][1] + socket1['pos'][1]) / 10]
                dest_r = [int(node2['pos'][0] - node2['transformpoint'][0] + socket2['pos'][0]) / 10,
                          int(node2['pos'][1] - node2['transformpoint'][1] + socket2['pos'][1]) / 10]
                '''
                way_r[0] = source_r
                way_r[-1] = dest_r
                '''
                self.get_edge(id1, id2, 0, edge_message['line_width'], source_r, dest_r, way_r)
                if len(way) > 1:
                    direction = [0, 0]
                    for i in range(len(way) - 1):
                        x1 = way[i][0]
                        y1 = way[i][1]
                        x2 = way[i][0] + direction[0]
                        y2 = way[i][1] + direction[1]
                        try:
                            self.map[x1][y1] = 1
                            self.map_edge[x1][y1] = 1
                        except:
                            pass
                        try:
                            self.map[x1][y2] = 1
                            self.map_edge[x1][y2] = 1
                        except:
                            pass
                        try:
                            self.map[x2][y2] = 1
                            self.map_edge[x2][y2] = 1
                        except:
                            pass
                        try:
                            self.map[x2][y1] = 1
                            self.map_edge[x2][y1] = 1
                        except:
                            pass
                        direction = [way[i + 1][0] - way[i][0], way[i + 1][1] - way[i][1]]

                _map.showMap()
            count = 0
            while not way:
                count += 1
                for other_map in self.other_maps:
                    index = self.other_maps.index(other_map) + 1
                    _other_map = Map(other_map)
                    if other_map[source[0]][source[1]] != 1 and other_map[dest[0]][dest[1]] != 1:
                        way = AStarSearch(_other_map, source, dest)
                    else:
                        pass
                    if way:
                        # edge_message['way'] = way
                        if len(way) > 1:
                            direction = [0, 0]
                            for i in range(len(way) - 1):
                                x1 = way[i][0]
                                y1 = way[i][1]
                                x2 = way[i][0] + direction[0]
                                y2 = way[i][1] + direction[1]
                                try:
                                    other_map[x1][y1] = 1
                                except:
                                    pass
                                try:
                                    other_map[x1][y2] = 1
                                except:
                                    pass
                                try:
                                    other_map[x2][y2] = 1
                                except:
                                    pass
                                try:
                                    other_map[x2][y1] = 1
                                except:
                                    pass
                                direction = [way[i + 1][0] - way[i][0], way[i + 1][1] - way[i][1]]
                        _other_map.showMap()

                        source_r = [int(node1['pos'][0] - node1['transformpoint'][0] + socket1['pos'][0])/10, int(node1['pos'][1] - node1['transformpoint'][1] + socket1['pos'][1])/10]
                        dest_r = [int(node2['pos'][0] - node2['transformpoint'][0] + socket2['pos'][0])/10, int(node2['pos'][1] - node2['transformpoint'][1] + socket2['pos'][1])/10]
                        '''
                        way[0] = source_r
                        way[-1] = dest_r
                        '''
                        self.get_hole(id1, id2, index, source_r, dest_r)
                        self.get_edge(id1, str(id1) + 'hole1', 0, edge_message['line_width'])
                        self.get_edge(id2, str(id2) + 'hole2', 0, edge_message['line_width'])
                        self.get_edge(str(id2) + 'hole1', str(id1) + 'hole2', index, edge_message['line_width'], source_r, dest_r, way)

                if not way:
                    map_data = [[0 for i in range(int(self.length_y/10)+1)] for j in range(int(self.length_x/10)+1)]
                    self.other_maps.append(map_data)
                if count == 5:
                    break

    def arc_node_angle(self, _node):
        _angle = _node['rotation']
        if _angle == 180:
            _node['pos'] = [_node['pos'][0] + _node['area'][0],
                                       _node['pos'][1] + _node['area'][1]]
        if _angle == 90:
            _node['pos'] = [_node['pos'][0] + _node['area'][0],
                                       _node['pos'][1]]
        if _angle == -90:
            _node['pos'] = [_node['pos'][0],
                                       _node['pos'][1] + _node['area'][1]]
        return _node

    def get_edge(self, id1, id2, layer, width, src=[], dst=[], way_list=[]):
        edge = {}
        edge['id'] = str(id1) + str(id2) + 'edge'
        edge['Type'] = 'Edge'
        edge['layer'] = layer
        edge['line_width'] = width
        edge['attribute'] = {}
        edge['side_sockets_id'] = []
        edge['side_sockets_id'].append(id1)
        edge['side_sockets_id'].append(id2)
        edge['start_point_list'] = []
        direction = []
        if len(way_list) > 2:
            for i in range(len(way_list)-1):
                if [way_list[i+1][0]-way_list[i][0], way_list[i+1][1]-way_list[i][1]] != direction:
                    edge['start_point_list'].append([way_list[i][0]*10, way_list[i][1]*10])
                    direction = [way_list[i+1][0]-way_list[i][0], way_list[i+1][1]-way_list[i][1]]
            edge['start_point_list'].append([way_list[-1][0]*10, way_list[-1][1]*10])
        else:
            for pos in way_list:
                edge['start_point_list'].append([pos[0]*10, pos[1]*10])
        if way_list:
            edge['start_point_list'][0] = [src[0]*10, src[1]*10]
            edge['start_point_list'][-1] = [dst[0]*10, dst[1]*10]
        if len(way_list) > 2:
            length = (edge['start_point_list'][0][0]-edge['start_point_list'][1][0])**2 + (edge['start_point_list'][0][1]-edge['start_point_list'][1][1])**2
            if length < 100:
                edge['start_point_list'].pop(1)
        edge['end_point_list'] = []
        edge['move_point'] = []
        self.edges.append(edge)

    def get_hole(self, id1, id2, layer, source, dest):
        hole = {}
        hole['id'] = str(id1) + str(id2) +'hole'
        hole['Type'] = 'HoleSocket'
        hole['pos'] = [source[0]*10, source[1]*10]
        hole['sockets'] = []
        socket1 = {}
        socket1['id'] = str(id1)+'hole1'
        socket1['Type'] = 'Socket'
        socket1['layer'] = 0
        hole['sockets'].append(socket1)
        socket2 = {}
        socket2['id'] = str(id2) + 'hole1'
        socket2['Type'] = 'HoleSocket'
        socket2['layer'] = layer
        hole['sockets'].append(socket2)
        hole['side_sockets_id'] = []
        hole['side_sockets_id'].append(id1)
        hole['side_sockets_id'].append(str(id1) + 'hole2')
        self.holes.append(hole)
        hole = {}
        hole['id'] = str(id2) + str(id1)
        hole['Type'] = 'HoleSocket'
        hole['pos'] = [dest[0]*10, dest[1]*10]
        hole['sockets'] = []
        socket1 = {}
        socket1['id'] = str(id2) + 'hole2'
        socket1['Type'] = 'Socket'
        socket1['layer'] = 0
        hole['sockets'].append(socket1)
        socket2 = {}
        socket2['id'] = str(id1) + 'hole2'
        socket2['Type'] = 'Socket'
        socket2['layer'] = layer
        hole['sockets'].append(socket2)
        hole['side_sockets_id'] = []
        hole['side_sockets_id'].append(id2)
        hole['side_sockets_id'].append(str(id2) + 'hole1')
        self.holes.append(hole)

    def get_data(self):
        layersValue = [self.length_z+10]
        for layer in self.other_maps:
            layersValue.append(20)
        base_shapes = []
        shape_data = {}
        shape_data['Type'] = 'Rect'
        shape_data['pos'] = [0, 0]
        shape_data['area'] = [self.length_x, self.length_y]
        shape_data['thickness'] = self.length_z+10+len(self.other_maps)*20
        base_shapes.append(shape_data)
        for node in (self.inflowNode+self.outflowNode):
            shape_data = {}
            shape_data['Type'] = 'Rect'
            shape_data['pos'] = [node['pos'][0] - node['transformpoint'][0]-30, node['pos'][1] - node['transformpoint'][1]-30]
            shape_data['area'] = [node['area'][0]+60, node['area'][1]+60]
            shape_data['thickness'] = self.length_z + 10 + 100
            base_shapes.append(shape_data)
        data = {}
        data['layers'] = len(self.other_maps) + 1
        data['layer_value'] = layersValue
        data['base_shapes'] = base_shapes
        data['holes'] = self.holes
        data['edges'] = self.edges
        data['nodes'] = self.nodes

        return data
