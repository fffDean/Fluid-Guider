from gui_real.hole_setting import GraphicHoleSocket, GraphicSocket2
import cadquery as cq


class HoleSocket:
    def __init__(self, scene, socket1=None, socket2=None):

        self.id = id(self)
        self.scene = scene
        if socket1 and socket2:
            self.socket1 = socket1.socket
            self.socket2 = socket2.socket
            self.layerMin = min(self.socket1.layer, self.socket2.layer)
            self.layerMax = max(self.socket1.layer, self.socket2.layer)

            self.grHole = GraphicHoleSocket(self)
            self.mySocket1 = Socket(self)
            self.mySocket1.set_layer(self.socket1.layer)
            self.mySocket2 = Socket(self)
            self.mySocket2.set_layer(self.socket2.layer)
            self.scene.add_hole(self.grHole)
            for i in range(self.layerMin, self.layerMax + 1):
                self.scene.layers[i].append(self.grHole)
        else:
            self.grHole = GraphicHoleSocket(self)
            self.mySocket1 = Socket(self)
            self.mySocket2 = Socket(self)
            self.scene.add_hole(self.grHole)

        #self.grSocket.setPos(*self.node.getSocketPosition(index, position))

    # @----@--@----@
    # s1---m1-m2---s2
    def opSocket(self, grSocket):
        if grSocket == self.socket1.grSocket:
            return self.socket2.grSocket
        elif grSocket == self.socket2.grSocket:
            return self.socket1.grSocket

    def opMySocket(self, grSocket):
        if grSocket == self.mySocket1.grSocket:
            return self.mySocket2.grSocket
        elif grSocket == self.mySocket2.grSocket:
            return self.mySocket1.grSocket

    def set_socket(self, socket1, socket2):
        self.socket1 = socket1.socket
        self.socket2 = socket2.socket
        self.reset_layer()

    def reset_layer(self):
        self.mySocket1.set_layer(self.socket1.layer)
        self.mySocket2.set_layer(self.socket2.layer)
        '''
        for i in range(self.layerMin, self.layerMax + 1):
            self.scene.layers[i].remove(self.grHole)
        '''
        for layerC in self.scene.layers:
            if self.grHole in layerC:
                layerC.remove(self.grHole)
        self.layerMin = min(self.socket1.layer, self.socket2.layer)
        self.layerMax = max(self.socket1.layer, self.socket2.layer)
        for i in range(self.layerMin, self.layerMax + 1):
            self.scene.layers[i].append(self.grHole)

    def set_id(self):
        self.id = id(self)

    def to_string(self):
        hole = {}
        hole['id'] = self.id
        hole['Type'] = self.__class__.__name__
        hole['pos'] = [self.grHole.scenePos().x(), self.grHole.scenePos().y()]
        hole['sockets'] = []
        hole['sockets'].append(self.mySocket1.to_string())
        hole['sockets'].append(self.mySocket2.to_string())
        hole['side_sockets_id'] = []
        hole['side_sockets_id'].append(self.socket1.id)
        hole['side_sockets_id'].append(self.socket2.id)
        return hole

    def to_hashmap(self, data, hashmap={}):
        hashmap[data['id']] = self

        self.mySocket1.to_hashmap(data['sockets'][0], hashmap)
        self.mySocket2.to_hashmap(data['sockets'][1], hashmap)

    def get_3Dmodel(self):
        model = cq.Workplane()
        originPoint = [self.grHole.scenePos().x()/10, self.grHole.scenePos().y()/10, self.scene.getZValue(self.layerMin)/10+self.mySocket1.edge.width/20]
        thickness = self.scene.getZValue(self.layerMin) - self.scene.getZValue(self.layerMax)
        model += cq.Workplane(origin=originPoint).polygon(16, self.mySocket1.edge.width/5).extrude(
            -thickness/10-self.mySocket1.edge.width/10)
        return model


class Socket:
    def __init__(self, hole):

        self.id = id(self)
        self.hole = hole
        self.layer = 0

        self.edge = None
        self.op_st = True
        self.canCheck = True

        self.grSocket = GraphicSocket2(self, self.hole.grHole)

    def set_canCheck(self, Bool):
        self.canCheck = Bool

    def set_layer(self, layer):
        self.layer = layer

    def set_id(self):
        self.id = id(self)

    def set_edge(self, edge):
        self.edge = edge

    def to_string(self):
        socket = {}
        socket['id'] = self.id
        socket['Type'] = self.__class__.__name__
        socket['layer'] = self.layer
        return socket

    def to_hashmap(self, data, hashmap={}):
        hashmap[data['id']] = self
