from numpy import *
from numpy.linalg import *
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FFMpegWriter

###### Flow definition #########################################################
maxIter = 2000  # Total number of time iterations.
Re = 5.0  # Reynolds number.
nx = 720
ny = 355
ly = ny - 1.0
q = 9  # Lattice dimensions and populations.
cx = nx / 4
cy = ny / 2
r = ny / 9  # Coordinates of the cylinder.
uLB = 0.04  # 入口速度
nulb = uLB * r / Re     # 粘性系数
omega = 1.0 / (3. * nulb + 0.5);  # Relaxation parameter.
images = []

###### Lattice Constants #######################################################
c = array([(x, y) for x in [0, -1, 1] for y in [0, -1, 1]])  # Lattice velocities.
print(c)
t = 1. / 36. * ones(q)  # Lattice weights.
print(t)
t[asarray([norm(ci) < 1.1 for ci in c])] = 1. / 9.;
t[0] = 4. / 9.
print(t)
c = array([[0, 0], [0, -1], [0, 1], [-1, 0], [-1, -1], [-1, 1], [1, 0], [1, -1], [1, 1]])
t = [0.44444444, 0.11111111, 0.11111111, 0.11111111, 0.02777778, 0.02777778, 0.11111111, 0.02777778, 0.02777778]
noslip = [c.tolist().index((-c[i]).tolist()) for i in range(q)]     # 获取相反方向在c中的位置
print(noslip)
i1 = arange(q)[asarray([ci[0] < 0 for ci in c])]  # Unknown on right wall.
print(asarray([ci[0] < 0 for ci in c]))
print(i1)
i2 = arange(q)[asarray([ci[0] == 0 for ci in c])]  # Vertical middle.
i3 = arange(q)[asarray([ci[0] > 0 for ci in c])]  # Unknown on left wall.

###### Function Definitions ####################################################
def sumpop(fin):
    # 将每一行加起来
    return sum(fin, axis=0)  # Helper function for density computation.


def equilibrium(rho, u):  # Equilibrium distribution function.
    cu = 3.0 * dot(c, u.transpose(1, 0, 2))
    usqr = 3. / 2. * (u[0] ** 2 + u[1] ** 2)
    feq = zeros((q, nx, ny))
    for i in range(q):
        feq[i, :, :] = rho * t[i] * (1. + cu[i] + 0.5 * cu[i] ** 2 - usqr)
    return feq


###### Setup: cylindrical obstacle and velocity inlet with perturbation ########
def U_way():
    l = 333
    Nx = 720
    Ny = 22 + l
    way = zeros((nx, ny), dtype=bool)
    way[:, 0] = True
    way[:, ny - 1] = True
    way[0:100, 21:121] = True
    way[0:120, 141:ny] = True
    way[120:220, 21:ny] = True
    for i in range(5):
        way[220 + 20 * (i + 1) + 80 * i:220 + 100 * (i + 1), 11 - (-1) ** i * 10:ny - 1 - 10 - (-1) ** i * 10] = True
    return way
obstacle = fromfunction(lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < r ** 2, (nx, ny))
obstacle = U_way()

# vel用于初始化速度，d的取值是0，1，代表x方向和y方向，ulb后面的代表微小偏量
# 其实直接全部赋值0.04也没关系
vel = fromfunction(lambda d, x, y: (1-d)*uLB*(1.0+1e-4*sin(y/ly*2*pi)), (2, nx, ny))
print(vel)
vel = fromfunction(lambda d, x, y: (1 - d) * uLB, (2, nx, ny))
u = zeros((2, nx, ny))
u[:, 0, :] = vel[:, 0, :]
rho = ones((nx, ny))
#rho[obstacle] = 1
#rho[0:10, :] = 1
feq = equilibrium(rho, u)
fin = feq.copy()

# w = zeros((9, nx, ny))
# w[:, obstacle] = 1

###### Main time loop ##########################################################
for time in range(maxIter):

    fin[i1, -1, :] = fin[i1, -2, :]  # 出口边界条件，充分发展的流动格式即出口未知的分布函数与上一个节点相同

    rho = sumpop(fin)  # 计算宏观密度

    u = dot(c.transpose(), fin.transpose((1, 0, 2))) / rho  #
    u = nan_to_num(u, nan=0)

    u[:, 0, :] = vel[:, 0, :]  #
    rho[0, :] = 1. / (1. - u[0, 0, :]) * (sumpop(fin[i2, 0, :]) + 2. * sumpop(fin[i1, 0, :]))
    feq = equilibrium(rho, u)  #
    fin[i3, 0, :] = fin[i1, 0, :] + feq[i3, 0, :] - fin[i1, 0, :]
    # fin[i3, 0, :] = feq[i3, 0, :]
    fout = fin - omega * (fin - feq)  # 碰撞过程

    for i in range(q):
        fout[i, obstacle] = fin[noslip[i], obstacle]

    for i in range(q):  # 扩散过程

        fin[i, :, :] = roll(roll(fout[i, :, :], c[i, 0], axis=0), c[i, 1], axis=1)

    #images.append(sqrt(u[0] ** 2 + u[1] ** 2).transpose())
    #images.append(sqrt(u[0] ** 2 + u[1] ** 2))
    images.append(rho)
    #plt.clf()
    #plt.imshow(sqrt(u[0] ** 2 + u[1] ** 2).transpose(), cmap=cm.Reds)
    # plt.savefig("vel." + str(time / 10000).zfill(4) + ".png")

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
with writer.saving(figure, 'out6.mp4', 100):
    traverse_imgs(writer, images)