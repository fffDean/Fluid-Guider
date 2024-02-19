from gui_test.node_setting import GraphicNode, GraphicSocket
from gui_test.edge_setting import GraphicEdge
from gui_test.node_node import Node
from gui_test.edge_edge import Edge
from gui_test.item_group import GraphicItemGroup, Group

class ctrl_xcv:
    def __init__(self, widget):

        self.widget = widget
        self.widget.view.scenePosChanged.connect(self.get_changed_pos)

    def selecteditem_to_string(self):
        data = {}
        data['nodes'] = []
        data['groups'] = []
        data['edges'] = []
        for item in self.widget.scene.grScene.selectedItems():

            # 保存node
            if isinstance(item, GraphicNode):
                # print(node.node.to_string())  # debug
                node = item.node.to_string()
                data['nodes'].append(node)

            if isinstance(item, GraphicItemGroup):
                group = item.group.to_string()
                data['groups'].append(group)


            # 保存edge
            elif isinstance(item, GraphicEdge):
                edge = item.edge.to_string()
                data['edges'].append(edge)

            item.setSelected(False)

            print(data)

        return data

    def string_to_selecteditem(self, data={}, hashmap={}):
        count_x = 0
        count_y = 0
        number = len(data['nodes']) + len(data['groups'])
        for node_message in data['nodes']:
            count_x += node_message['pos'][0]
            count_y += node_message['pos'][1]
        for group_message in data['groups']:
            count_x += group_message['pos'][0]
            count_y += group_message['pos'][1]
        try:
            changed_x = self.x - count_x/number
            changed_y = self.y - count_y/number

        except:
            print('没有复制或剪切数据')

        for node_message in data['nodes']:
            #node = Node(self, attribute=node_message['attribute'])
            node = globals()[node_message['Type']](self.widget.scene, attribute=node_message['attribute'])
            node.grNode.setPos(node_message['pos'][0] + changed_x, node_message['pos'][1] + changed_y)
            node.grNode.setSelected(True)
            node.to_hashmap(node_message, hashmap)

        for group_message in data['groups']:
            group = globals()[group_message['Type']](self.widget.scene)
            group.grGroup.setPos(group_message['pos'][0] + changed_x, group_message['pos'][1] + changed_y)
            for item_id in group_message['child_item_id']:
                if item_id in hashmap:
                    group.addToGroup(hashmap[item_id].grNode)
            group.updateArea()
            group.grGroup.setSelected(True)
            group.to_hashmap(group_message, hashmap)

        # 遍历每条连线
        for edge_message in data['edges']:
            # 确定起始和终点的插口的id
            start_id = edge_message['side_sockets_id'][0]
            end_id = edge_message['side_sockets_id'][1]
            try:
                start_socket = hashmap[start_id].grSocket
                end_socket = hashmap[end_id].grSocket
                edge = Edge(self.widget.scene, start_socket, end_socket, attribute=edge_message['attribute'])
                edge.grEdge.setSelected(True)

            except:
                print('剪切或复制的不完全连线已删除')


    def get_changed_pos(self, x, y):
        self.x = x
        self.y = y


    def paste(self, data={}):
        for item in self.widget.scene.grScene.selectedItems():
            item.setSelected(False)
        self.string_to_selecteditem(data)

    def copy(self):
        data = self.selecteditem_to_string()
        return data

    def cut(self):
        selected = self.widget.scene.grScene.selectedItems().copy()
        data = self.selecteditem_to_string()
        for item in selected:
            if hasattr(item, 'node'):
                self.widget.scene.remove_node(item)

        return data
