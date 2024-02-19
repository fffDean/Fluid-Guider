from numpy import *
import torch
import cv2
import time


l = 333
Nx = 720
Ny = 121+l
way = zeros((Nx, Ny))
way[0:100, 0:100] = 1
way[0:220, 120:Ny] = 1
way[:, Ny-1] = 1
way[120:Nx, 0:100] = 1
for i in range(5):
    way[220+20*(i+1)+80*i:220+100*(i+1), 110-(-1)**i*10:Ny-1-10-(-1)**i*10] = 1

a = array([[[1, 2, 3],
           [2, 3, 4],],
           [[2, 2, 2],
           [3, 3, 3]],
           [[4, 4, 4],
            [5, 5, 5]]])
b = array([[1, 4, 7],
           [2, 2, 2]])
b = expand_dims(b, 2).repeat(4, 2)
b = expand_dims(b, 3).repeat(4, 3)
a = array([[[1,2,3],
            [2,2,2]],
           [[3,3,3],
            [4,4,4]]])
b = array([[[1,2],
            [2,2]],
           [[3,3],
            [4,4]],
           [[5,5],
            [6,6]]])
a = array([1,2,3,4,5,6,7,8,9])
b = array([[1,2], [2,3], [3,4], [4,5], [5,6], [6,7], [7,8], [8,9], [9,1]])
a = ones((5,5))
b = ([2,1],[3,3])
def FloodFill(P, figure, target_pos, targetcolor):
    # function: the algorithm of grow
    # input: P is growing point (type is tuple)
    #        figure is 2D picture matrix (type is numpy.ndarray)
    #        target_pos is a set of position which we need
    #        targetcolor is the value of color which we want (type is int)
    # output: None
    adj_next = [P]  # 邻域列表
    while adj_next:
        adj = []
        # 如果在边界上，则不能越界添加邻域
        for x, y in adj_next:
            if x > 0:
                adj.append((x - 1, y))
            if x < figure.shape[0] - 1:
                adj.append((x + 1, y))
            if y > 0:
                adj.append((x, y - 1))
            if y < figure.shape[1] - 1:
                adj.append((x, y + 1))
        adj_next = []

        for xn, yn in adj:  # four邻域
            if target_pos[xn, yn]:  # 属于邻域且未遍历过
                if figure[xn][yn] == targetcolor:  # 如果该点为目标值，将该邻近点加入集合中
                    target_pos[xn, yn] = False
                    adj_next.append((xn, yn))
a[b] = 5
way = ones((5,5), dtype=bool)
FloodFill((0,0), a, way, 1)

#reward = sum(abs(a[~way]))/sum(a == 5)
a = torch.tensor([[[1,2,3], [5,6,7]],[[1,2,3], [5,6,7]]])
b = torch.reshape(a, (2, -1))
a = ones((2, 7))
a[:, :-1][b > 5] = 0

a = torch.FloatTensor([[[1, 1, 1, 4],
                        [3, 4, 7, 2]],
                       [[3, 4, 2, 3],
                        [7, 8, 5, 7]],
                       [[6, 4, 8, 3],
                        [9, 6, 4, 2]]])
b = torch.tensor([[0], [1], [0]])
a = torch.tensor([[1, 0, 0], [1, 1, 1]], dtype=torch.float64)
b = torch.tensor([[4, 5, 6], [3, 4, 5]])
# print(a/a.sum(-1, keepdim=True))
# print([int(x) for x in bin(11)[2:]])
# print(torch.matmul(a.unsqueeze(1).transpose(1, 2), b.unsqueeze(1)).reshape(a.size(0), -1))
# print(torch.gather(a, 1, b))
# print(torch.gather(a, 1, b.repeat(1, a.size(2)).unsqueeze(1)).resize(3, a.size(2)))


def num_exchange(num):
    if isinstance(num, int):
        ele = [int(x) for x in bin(num)[2:]]
        while len(ele) < 5:
            ele.insert(0, 0)
        new_num = torch.FloatTensor(asarray(ele)).unsqueeze(0)
        return new_num
    elif torch.is_tensor(num):
        new_num = []
        for i in range(num.size(0)):
            ele = [int(x) for x in bin(int(num[i, 0]))[2:]]
            while len(ele) < 5:
                ele.insert(0, 0)
            new_num.append(ele)
        new_num = torch.FloatTensor(asarray(new_num))
        return new_num
a = zeros((5, 5))
a[0, :] = 1
a[1, 1:] = 1
a[2, 2:] = 1
a[3, 3:] = 1
a[4, 4:] = 1
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
dilated = cv2.dilate(a, kernel, iterations=1)
eroded = cv2.erode(dilated, kernel, iterations=1)
a = asarray([[1, 2], [3, 4], [5, 6]])
print((2==1 and a[10]==1))
