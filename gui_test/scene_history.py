'''
在存储箱中存储历史中的scene
history_box --> &[ | | | | | | | ]
存储箱中有history_max（在这里是8）个位置，存储不同时间的scene的情况
history_current_step作为指针,此处用&表示，表示处于目前的位置的scene的状态中
（1）开始时，history_box为空，当我们做过一个操作（一般第一个scene状态就是初始状态）：
    history_box --> [A&| | | | | | | ]
（2）若继续做一个操作：
    history_box --> [A|B&| | | | | | ]
    该状态：
        可以撤回
        不可回撤
（3）此时我们若想撤回：
    应做对history_current_step做出判断，看其是否是在box外状态（是否大于0）
    若小于等于0则这撤回将是被禁止的
    history_box --> [A&|B| | | | | | ]
    该状态：
        不可撤回
        可以回撤
（4）在（2）状态下若想回撤：
    应对history_current_step作出判断， 看其是否小于box中history的数量
    若小于则可以回撤
    若等于则不可回撤
（5）当我们的操作将box填满（[A|B|C|D|E|F|G|H&]）,再次操作时：
    应对history_current_step作出判断，判断其是否到头了（等于8）
    history_box --> A[B|C|D|E|F|G|H|I&]
    A被挤出box应删去，不再记忆这个状态的scene
    history_box --> [B|C|D|E|F|G|H|I&]
    该状态：
        可以撤回
        不可回撤
（6）若进行撤回：
    history_box --> [B|C|D|E|F|G|H&|I]
    该状态：
        可以撤回
        可以回撤
'''

class SceneHistory:
    def __init__(self, scene):
        self.scene = scene

        # 建立存储箱用于存储scene的历史记录
        self.history_box = []
        self.history_current_step = -1
        self.history_max = 8

    def restart(self):
        self.history_box = []
        self.history_current_step = -1
        self.history_max = 8

    def Undo(self):
        if self.history_current_step > 0:
            self.history_current_step -= 1
            self.restoreHistory()
        # print(self.history_box, self.history_current_step)

    def Redo(self):
        if self.history_current_step + 1 < len(self.history_box):
            self.history_current_step += 1
            self.restoreHistory()
        # print(self.history_box, self.history_current_step)

    def restoreHistory(self):
        self.restoreHistoryStep(self.history_box[self.history_current_step])

    def storeHistory(self):
        if self.scene.has_been_saved == True:
            self.scene.has_been_saved = False
            try:
                self.scene.use_func(self.scene.HoleWindow_func['changeTitle'])
            except:
                pass
        # 创建新的历史记录
        history = self.createHistorystep()
        # 如果指针位置后还有历史记录
        if self.history_current_step + 1 < len(self.history_box):
            self.history_box = self.history_box[0:self.history_current_step + 1]
        # 如果指针位置在存储箱的最后位置
        elif self.history_current_step + 1 == self.history_max:
            self.history_box = self.history_box[1:]

        self.history_box.append(history)
        self.history_current_step += 1

        # print(self.history_box, self.history_current_step)

    def restoreHistoryStep(self, history_data):
        self.scene.clear()

        hashmap = self.scene.string_to_item(history_data['graph_data'])
        for node_id in history_data['selected_items']['nodes_id']:
            node = hashmap[node_id]
            node.grNode.setSelected(True)

        for edge_id in history_data['selected_items']['edges_id']:
            edge = hashmap[edge_id]
            edge.grEdge.setSelected(True)

    def createHistorystep(self):
        selected_dict = {
            'nodes_id': [],
            'edges_id': []
        }

        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                selected_dict['nodes_id'].append(item.node.id)
            elif hasattr(item, 'edge'):
                selected_dict['edges_id'].append(item.edge.id)
        self.history_data = {
            'graph_data': self.scene.item_to_string(),
            'selected_items': selected_dict
        }
        return self.history_data
