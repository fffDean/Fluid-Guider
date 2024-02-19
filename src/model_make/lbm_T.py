from numpy import *
from numpy.linalg import *
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FFMpegWriter
from numba import jit

###### Flow definition #########################################################
maxIter = 2000  # Total number of time iterations.
Re1 = 5  # Reynolds number.
Re2 = 5.1
nx = 321
ny = 220
q = 9  # Lattice dimensions and populations.
d = 20
uLB = 0.04  # 入口速度
nulb1 = uLB * d / Re1     # 粘性系数
nulb2 = uLB * d / Re2
D = 0.36
omega1 = 1.0 / (3. * nulb1 + 0.5)  # Relaxation parameter.
omega2 = 1.0 / (3. * nulb2 + 0.5)  # Relaxation parameter.
omegaD = 3.0/(3. * D + 0.5)

images = []

###### Lattice Constants #######################################################
c = array([(x, y) for x in [0, -1, 1] for y in [0, -1, 1]])  # Lattice velocities.
t = 1. / 36. * ones(q)  # Lattice weights.
t[asarray([norm(ci) < 1.1 for ci in c])] = 1. / 9.
t[0] = 4. / 9.
c = array([[0, 0], [0, -1], [0, 1], [-1, 0], [-1, -1], [-1, 1], [1, 0], [1, -1], [1, 1]])
t = [0.44444444, 0.11111111, 0.11111111, 0.11111111, 0.02777778, 0.02777778, 0.11111111, 0.02777778, 0.02777778]
noslip = array([c.tolist().index((-c[i]).tolist()) for i in range(q)])     # 获取相反方向在c中的位置
i1 = arange(q)[asarray([ci[0] < 0 for ci in c])]  # Unknown on right wall.
i2 = arange(q)[asarray([ci[0] == 0 for ci in c])]  # Vertical middle.
i3 = arange(q)[asarray([ci[0] > 0 for ci in c])]  # Unknown on left wall.
i4 = arange(q)[asarray([ci[1] < 0 for ci in c])]  # Unknown on left wall.
i5 = arange(q)[asarray([ci[1] == 0 for ci in c])]  # Unknown on left wall.
i6 = arange(q)[asarray([ci[1] > 0 for ci in c])]  # Unknown on left wall.

def sumpop(fin):
    # 将每一行加起来
    return sum(fin, axis=0)  # Helper function for density computation.

def equilibrium(rho1, rho2, u1, u2):  # Equilibrium distribution function.
    u_total = (rho1*u1+rho2*u2) / (rho1+rho2)
    u_total = nan_to_num(u_total, nan=0)
    cu = 3.0 * dot(c, u_total.transpose(1, 0, 2))
    usqr = 3./2 * (u_total[0] ** 2 + u_total[1] ** 2)
    feq1 = zeros((q, nx, ny))
    feq2 = zeros((q, nx, ny))
    for i in range(q):
        feq1[i, :, :] = rho1 * t[i] * (1. + cu[i] + 0.5 * cu[i] ** 2 - usqr)
        feq2[i, :, :] = rho2 * t[i] * (1. + cu[i] + 0.5 * cu[i] ** 2 - usqr)
    return feq1, feq2

def equilibrium_Wall(rho1, rho2, u1, u2):
    u_total = (rho1 * u1 + rho2 * u2) / (rho1 + rho2)
    u_total = nan_to_num(u_total, nan=0)
    cu = 3.0 * dot(c, u_total)
    usqr = 3./2 * (u_total[0] ** 2 + u_total[1] ** 2)
    in1 = zeros((q, nx))
    in2 = zeros((q, nx))
    for i in range(q):
        in1[i, :] = rho1 * t[i] * (1. + cu[i] + 0.5 * cu[i] ** 2 - usqr)
        in2[i, :] = rho2 * t[i] * (1. + cu[i] + 0.5 * cu[i] ** 2 - usqr)
    return in1, in2

def collision(feq1, feq2, fin1, fin2, rho1, rho2, u1, u2):
    rho_total_ = rho1+rho2
    u_total_ = (rho1 * u1 + rho2 * u2) / rho_total_
    u_total_ = nan_to_num(u_total_, nan=0)

    u1_u2 = u1-u2
    u1_u = u1 - u_total_
    u2_u = u2 - u_total_
    cu1_u2 = 3.0 * dot(c, u1_u2.transpose(1, 0, 2))
    cu1_u = 3.0 * dot(c, u1_u.transpose(1, 0, 2))
    cu2_u = 3.0 * dot(c, u2_u.transpose(1, 0, 2))
    uu1_u2 = 3. * (u1_u2[0]*u_total_[0] + u1_u2[1]*u_total_[1])
    uu1_u = 3. * (u1_u[0] * u_total_[0] + u1_u[1] * u_total_[1])
    uu2_u = 3. * (u2_u[0] * u_total_[0] + u2_u[1] * u_total_[1])

    f01 = feq1 * (1 + cu1_u - uu1_u)
    j11 = -omega1 * (fin1 - f01)
    j12 = -omegaD * (rho2/rho_total_)*feq1 * (cu1_u2 - uu1_u2)
    j12 = nan_to_num(j12, nan=0)
    f02 = feq2 * (1 + cu2_u - uu2_u)
    j22 = -omega2 * (fin2 - f02)
    j21 = -omegaD * (rho1/rho_total_)*feq2 * (uu1_u2 - cu1_u2)
    j21 = nan_to_num(j21, nan=0)
    O1 = j11 + j12
    O2 = j22 + j21
    return O1, O2


@jit(nopython=True)
def bounce_back_half_way(fout):
    fin_ = zeros((q, nx, ny))
    for i in range(q):
        for x in range(nx):
            for y in range(ny):
                if way[x, y]:
                    fin_[i, x, y] = fout[i, x, y]
                else:
                    if way[(x+c[i, 0])%nx, (y+c[i, 1])%ny]:
                        fin_[noslip[i], x, y] = fout[i, x, y]
                    else:
                        fin_[i, (x+c[i, 0])%nx, (y+c[i, 1])%ny] = fout[i, x, y]
    return fin_

def T_way():
    nx = 321
    ny = 220
    way = zeros((nx, ny), dtype=bool)
    way[21:nx, 0:100] = True
    way[21:nx, 120:220] = True
    way[0, :] = True
    return way

def T_way2():
    nx = 321
    ny = 220
    way = zeros((nx, ny), dtype=bool)
    way[22:nx, 0:99] = True
    way[22:nx, 121:220] = True
    #way[0, :] = True
    return way

way = T_way()
way2 = T_way2()

vel1 = zeros((2, nx, ny))
vel2 = zeros((2, nx, ny))
'''
for i in range(10):
    vel1[1, 11+i, 0] = uLB*(1-(0.05+0.1*i)**2)
    vel2[1, 10-i, 0] = uLB * (1 - (0.05 + 0.1 * i) ** 2)
    vel1[1, 11 + i, ny-1] = -uLB * (1 - (0.05 + 0.1 * i) ** 2)
    vel2[1, 10 - i, ny-1] = -uLB * (1 - (0.05 + 0.1 * i) ** 2)
'''
vel1[1, 1:21, 0] = uLB
vel1[1, 1:21, ny-1] = -uLB
vel2[1, 1:21, 0] = uLB
vel2[1, 1:21, ny-1] = -uLB
rho1_ = zeros((nx, ny))
rho2_ = zeros((nx, ny))
rho1_[1:nx, 0:110] = 1
rho1_[way] = 1
rho2_[1:nx, 110:220] = 1
rho2_[way] = 1
feq1, feq2 = equilibrium(rho1_, rho2_, vel1, vel2)
fin1 = feq1.copy()
fin2 = feq2.copy()

for time in range(maxIter):

    fin1[i1, -1, :] = fin1[i1, -2, :]  # 出口边界条件，充分发展的流动格式即出口未知的分布函数与上一个节点相同
    fin2[i1, -1, :] = fin2[i1, -2, :]  # 出口边界条件，充分发展的流动格式即出口未知的分布函数与上一个节点相同
    in1, in2 = equilibrium_Wall(rho1_[:, 0], rho2_[:, 0], vel1[:, :, 0], vel2[:, :, 0])
    in3, in4 = equilibrium_Wall(rho1_[:, ny-1], rho2_[:, ny-1], vel1[:, :, ny-1], vel2[:, :, ny-1])
    fin1[:, :, 0] = in1
    fin2[:, :, 0] = in2
    fin1[:, :, ny-1] = in3
    fin2[:, :, ny-1] = in4

    rho1 = sumpop(fin1)  # 计算宏观密度
    rho2 = sumpop(fin2)  # 计算宏观密度
    '''
    rho1[:, 0] = 1/(1-vel1[0, :, 0])*(sum(fin1[i5, :, 0], axis=0) + 2*sum(fin1[i4, :, 0], axis=0))
    rho2[:, 0] = 1/(1-vel2[0, :, 0])*(sum(fin2[i5, :, 0], axis=0) + 2*sum(fin2[i6, :, 0], axis=0))
    fin1[2, :, 0] = fin1[1, :, 0] + 2/3*rho1[:, 0]*vel1[1, :, 0]
    fin1[8, :, 0] = fin1[4, :, 0] - (fin1[6, :, 0] - fin1[3, :, 0])/2 + rho1[:, 0]*(1/6*vel1[1, :, 0] + 1/2*vel1[0, :, 0])
    fin1[5, :, 0] = fin1[7, :, 0] + (fin1[6, :, 0] - fin1[3, :, 0])/2 + rho1[:, 0]*(1/6*vel1[1, :, 0] - 1/2*vel1[0, :, 0])
    fin2[1, :, ny-1] = fin2[2, :, ny-1] + 2 / 3 * rho2[:, ny-1] * vel2[1, :, ny-1]
    fin2[4, :, ny-1] = fin2[8, :, ny-1] + (fin2[6, :, ny-1] - fin2[3, :, ny-1]) / 2 + rho2[:, ny-1] * (
                1 / 6 * vel2[1, :, ny-1] + 1 / 2 * vel2[0, :, ny-1])
    fin2[7, :, ny-1] = fin2[5, :, ny-1] - (fin2[6, :, ny-1] - fin2[3, :, ny-1]) / 2 + rho2[:, ny-1] * (
                1 / 6 * vel2[1, :, ny-1] - 1 / 2 * vel2[0, :, ny-1])
    '''

    '''
    rho1[0, :] = 1/(1-vel1[0, 0, :])*(sum(fin1[i2, 0, :], axis=0) + 2*sum(fin1[i1, 0, :], axis=0))
    rho2[0, :] = 1/(1-vel2[0, 0, :])*(sum(fin2[i2, 0, :], axis=0) + 2*sum(fin2[i1, 0, :], axis=0))
    fin1[6, 0, :] = fin1[3, 0, :] + feq1[6, 0, :] - feq1[3, 0, :]
    fin1[8, 0, :] = fin1[4, 0, :] + (fin1[1, 0, :] - fin1[2, 0, :])/2 + (rho1[0, :]*1/2*vel1[1, 0, :] - feq1[6, 0, :] + feq1[3, 0, :])
    fin1[7, 0, :] = fin1[5, 0, :] + (fin1[2, 0, :] - fin1[1, 0, :])/2 + (rho1[0, :]*1/2*vel1[1, 0, :] - feq1[6, 0, :] + feq1[3, 0, :])
    fin2[6, 0, :] = fin2[3, 0, :] + feq2[6, 0, :] - feq2[3, 0, :]
    fin2[8, 0, :] = fin2[4, 0, :] + (fin2[1, 0, :] - fin2[2, 0, :]) / 2 + (rho2[0, :]*1/2*vel2[1, 0, :] - feq2[6, 0, :] + feq2[3, 0, :])
    fin2[7, 0, :] = fin2[5, 0, :] + (fin2[2, 0, :] - fin2[1, 0, :]) / 2 + (rho2[0, :]*1/2*vel2[1, 0, :] - feq2[6, 0, :] + feq2[3, 0, :])
    '''
    u1 = dot(c.transpose(), fin1.transpose((1, 0, 2))) / rho1  #
    u2 = dot(c.transpose(), fin2.transpose((1, 0, 2))) / rho2  #
    u1 = nan_to_num(u1, nan=0)
    u2 = nan_to_num(u2, nan=0)
    feq1, feq2 = equilibrium(rho1, rho2, u1, u2)  #
    O1, O2 = collision(feq1, feq2, fin1, fin2, rho1, rho2, u1, u2)
    fout1 = fin1 + O1
    fout2 = fin2 + O2


    fin1 = bounce_back_half_way(fout1)
    fin2 = bounce_back_half_way(fout2)
    '''
    for i in range(q):
        fout1[i, way] = fin1[noslip[i], way]
        fout2[i, way] = fin2[noslip[i], way]

    for i in range(q):  # 扩散过程
        fin1[i, :, :] = roll(roll(fout1[i, :, :], c[i, 0], axis=0), c[i, 1], axis=1)
        fin2[i, :, :] = roll(roll(fout2[i, :, :], c[i, 0], axis=0), c[i, 1], axis=1)
        
        for x in range(nx-1):
            for y in range(ny-1):
                if not way[x, y]:
                    if way[x+c[i,0], y+c[i,0]]:
                        fin1[noslip[i], x, y] = fout1[i, x, y]
                        fin2[noslip[i], x, y] = fout2[i, x, y]
                    else:
                        fin1[i, x+c[i,0], y+c[i,0]] = fout1[i, x, y]
                        fin2[i, x+c[i,0], y+c[i,0]] = fout2[i, x, y]
        
    '''



    #images.append(sqrt(u1[0] ** 2 + u1[1] ** 2))
    images.append(rho1)

def traverse_imgs(writer, images):
    # 遍历所有图片，并且让writer抓取视频帧
    for img in images:
        plt.imshow(img, cmap=cm.Reds)
        writer.grab_frame()
        plt.pause(0.01)
        plt.clf()

# 创建video writer, 设置好相应参数，fps
metadata = dict(title='01', artist='Matplotlib', comment='depth prediiton')
writer = FFMpegWriter(fps=100, metadata=metadata)

# 读出自己的所有图片

figure = plt.figure(figsize=(10.8, 7.2))
plt.ion()  # 为了可以动态显示
plt.tight_layout()  # 尽量减少窗口的留白
with writer.saving(figure, 'out3_.mp4', 100):
    traverse_imgs(writer, images)