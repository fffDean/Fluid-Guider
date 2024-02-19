"""

入口
|
————————————————
                |<--- corner
————————————————
|
————————————————
                |
————————————————
|
出口
|————height————|
"""



from numpy import *
from numpy.linalg import *
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.animation import FFMpegWriter

# seterr(divide='ignore', invalid='ignore')

    ########    真实参数    #########
diameter = 0.0006   # m
height = 0.02       # m
u_star = 0.001            # m/s  入口速度
viscosity1_star = 10**(-6)   # m^2/s   液体1运动粘度
viscosity2_star = 10**(-6)   # m^2/s   液体2运动粘度
D_star = 3*10**(-6)              # m^2/s   两液体的互相扩散系数（速率）
    #######     格子参数    ########
d = 2   # 使用D2Q9模型
q = 9
u_s = 0.04#0.1*math.sqrt(3)    # Ma*Cs     格子单位的速度
Cu = u_star/u_s           # 速度转换系数
Nx = 720  # 格子单位的x方向长度
Ny = 355      # 格子单位的y方向长度
Cl = diameter/20        # 长度转换系数（1个格子的实际长度）
Ct = Cl/Cu              # 时间转换系数
Cv = Cl**2/Ct           # 运动粘度转换系数（互相扩散系数转换系数）
v1 = viscosity1_star/Cv     # 格子单位粘度
v2 = viscosity2_star/Cv
t1 = 3*v1 + 0.5         # 流体1的弛豫时间
t2 = 3*v2 + 0.5
D = D_star/Cv           # 格子单位的互相扩散系数
tD = 3*D + 0.5
    ########    准备      #########
c = array([(x, y) for x in [0, -1, 1] for y in [0, -1, 1]])  # Lattice velocities.
t = 1. / 36. * ones(q)  # Lattice weights.
t[asarray([norm(ci) < 1.1 for ci in c])] = 1. / 9.
t[0] = 4. / 9.
c = array([[0, 0], [0, -1], [0, 1], [-1, 0], [-1, -1], [-1, 1], [1, 0], [1, -1], [1, 1]])
t = [0.44444444, 0.11111111, 0.11111111, 0.11111111, 0.02777778, 0.02777778, 0.11111111, 0.02777778, 0.02777778]
noslip = [c.tolist().index((-c[i]).tolist()) for i in range(q)]     # 获取相反方向在c中的位置
i1 = arange(q)[asarray([ci[0] < 0 for ci in c])]  # Unknown on right wall.
i2 = arange(q)[asarray([ci[0] == 0 for ci in c])]  # Vertical middle.
i3 = arange(q)[asarray([ci[0] > 0 for ci in c])]  # Unknown on left wall.
i4 = arange(q)[asarray([ci[1] < 0 for ci in c])]  # Unknown on left wall.
i5 = arange(q)[asarray([ci[1] == 0 for ci in c])]  # Unknown on left wall.
i6 = arange(q)[asarray([ci[1] > 0 for ci in c])]  # Unknown on left wall.

def equilibrium(rho, u):  # Equilibrium distribution function.
    u_total = sum(u*rho, axis=1)/sum(rho, axis=0)
    u_total = nan_to_num(u_total, nan=0)
    cu = 3.0 * dot(c, u_total.transpose(1, 0, 2))
    usqr = 3. * (u_total[0] ** 2 + u_total[1] ** 2)
    feq = zeros((q, 2, Nx, Ny))
    for i in range(q):
        feq[i, 0, :, :] = rho[0, :, :] * t[i] * (1. + cu[i] + 0.5 * cu[i] ** 2 - usqr)
        feq[i, 1, :, :] = rho[1, :, :] * t[i] * (1. + cu[i] + 0.5 * cu[i] ** 2 - usqr)
    return feq

def collision(feq, fin, rho, u):
    rho_total_ = sum(rho, axis=0)
    u_total_ = sum(rho*u, axis=1)/rho_total_
    u_total_ = nan_to_num(u_total_, nan=0)
    cu1 = 3. * dot(c, u[:, 0, :, :].transpose(1, 0, 2))
    cu2 = 3. * dot(c, u[:, 1, :, :].transpose(1, 0, 2))
    cu_total = 3.0 * dot(c, u_total_.transpose(1, 0, 2))
    uu1 = 3. * (u[0, 0, :, :]*u_total_[0] + u[1, 0, :, :]*u_total_[1])
    uu2 = 3. * (u[0, 1, :, :]*u_total_[0] + u[1, 1, :, :]*u_total_[1])
    usqr = 3. * (u_total_[0] ** 2 + u_total_[1] ** 2)

    f01 = feq[:, 0, :, :] * (1 + cu1-uu1-cu_total+usqr)
    j11 = -1 / t1 * (fin[:, 0, :, :] - f01)
    j12 = -3. / tD * (rho[1, :, :]/rho_total_)*(feq[:, 0, :, :] * (cu1-uu1-cu_total+uu2))
    j12 = nan_to_num(j12, nan=0)
    f02 = feq[:, 1, :, :] * (1 + cu2-uu2-cu_total+usqr)
    j22 = -1 / t2 * (fin[:, 1, :, :] - f02)
    j21 = -3. / tD * (rho[0, :, :]/rho_total_)*(feq[:, 1, :, :] * (cu2-uu2-cu_total+uu1))
    j21 = nan_to_num(j21, nan=0)
    omega = zeros((q, 2, Nx, Ny))
    omega[:, 0, :, :] = j11 + j12
    omega[:, 1, :, :] = j22 + j21
    return omega



    ###### Setup: cylindrical obstacle and velocity inlet with perturbation ########
def U_way():
    l = 333
    nx = 720
    ny = 22 + l
    way = zeros((nx, ny), dtype=bool)
    way[:, 0] = True
    way[:, ny - 1] = True
    way[0:100, 21:121] = True
    way[0:120, 141:ny] = True
    way[120:220, 21:ny] = True
    for i in range(5):
        way[220 + 20 * (i + 1) + 80 * i:220 + 100 * (i + 1), 11 - (-1) ** i * 10:ny - 1 - 10 - (-1) ** i * 10] = True
    return way

way = U_way()
way_cal = ~way

    #######初始化速度#######
u = ones((2, 2, Nx, Ny))
# u[0, 0, 0:100, 1:21] = u_s
# u[0, 1, 0:100, 121:141] = u_s
u[0] *= u_s
u[1] *= 0.01*u_s
u[:, :, way] = 0
vel = u[:, :, 0, :].copy()
rho = zeros((2, Nx, Ny))
rho[0, :, :] = 1.5
rho[0, 0:120, 21:141] = 0
rho[0, way] = 0.5
rho[1, 0:120, 21:141] = 1
rho[1, way] = 0.5
rhoo = rho[:, 0, :]
feq = equilibrium(rho, u)
fin = feq.copy()
feqqq = feq[:, :, 0, :]

images = []

###### Main time loop ##########################################################
for time in range(100):
    fin[i1, :, -1, :] = fin[i1, :, -2, :]
    # feq = equilibrium(rho, u)
    # fin[i3, :, 0, :] = feq[i3, :, 0, :]
    # fin[i6, :, :, 0] = feq[i6, :, :, 0]

    # fin[i1, :, -1, :] = fin[i1, :, -2, :]  # 出口边界条件，充分发展的流动格式即出口未知的分布函数与上一个节点相同

    rho = sum(fin, axis=0)  # 计算宏观密度

    u = dot(c.transpose(), fin.transpose((1, 2, 0, 3))) / rho
    u = nan_to_num(u, nan=0)
    # u[:, :, way] = 0
    u[:, :, 0, :] = vel
    # rho[:, 0, :] = 1. / (1. - u[1, :, 0, :]) * (sum(fin[i2, :, 0, :], axis=0) + 2. * sum(fin[i1, :, 0, :], axis=0))
    rho[0, 0, 1:21] = 1.5
    rho[1, 0, 1:21] = 0
    rho[1, 0, 121:141] = 1
    rho[0, 0, 121:141] = 0
    # rho[1, 0, :] = 1. / (1. - u[1, 1, 0, :]) * (sum(fin[i2, 1, 0, :], axis=0) + 2. * sum(fin[i1, 1, 0, :], axis=0))
    # rho[0, :, 0] = 1. / (1. - u[0, 0, :, 0]) * (sum(fin[i5, 0, :, 0], axis=0) + 2. * sum(fin[i4, 0, :, 0], axis=0))
    # rho[:, 0, :] = 1. / (1. - u[1, :, 0, :]) * (sum(fin[i2, :, 0, :], axis=0) + 2. * sum(fin[i1, :, 0, :], axis=0))
    # rho[:, :, 0] = 1. / (1. - u[0, :, :, 0]) * (sum(fin[i5, :, :, 0], axis=0) + 2. * sum(fin[i4, :, :, 0], axis=0))
    # rho[:, :, 0] = rho[:, :, 1]
    # rho[:, 0, :] = rho[:, 1, :]
    # u[1, :, 100:120, 0] = u_s
    # u[0, :, 0, 100:120] = u_s
    # rho[:, Nx - 1, :] = rho[:, Nx - 2, :]

    feq = equilibrium(rho, u)

    # u_total = sum(rho*u, axis=1)/sum(rho, axis=0)
    fout = fin + collision(feq, fin, rho, u)  # 碰撞过程
    for i in range(q):
        fout[i, :, way] = fin[noslip[i], :, way]

    #fout[:, :, 0, :] = feq[:, :, 0, :] + fout[:, :, 1, :] - feq[:, :, 1, :]
    #fout[:, :, :, 0] = feq[:, :, :, 0] + fout[:, :, :, 1] - feq[:, :, :, 1]
    #fout[:, :, -1, :] = feq[:, :, -1, :] + fout[:, :, -2, :] - feq[:, :, -2, :]

    for i in range(q):  # 扩散过程
        fin[i, :, :, :] = roll(roll(fout[i, :, :, :], c[i, 0], axis=1), c[i, 1], axis=2)
    fin[:, :, 0, :] = feqqq

    rho_total = sum(rho, axis=0)
    u_total = sum(rho * u, axis=1) / rho_total
    u_total = nan_to_num(u_total, nan=0)
    # images.append(sqrt(u_total[0] ** 2 + u_total[1] ** 2).transpose())
    images.append(rho[0].transpose())
    # print(rho[0])
    # images.append(rho[0])
    # plt.clf()
    # plt.imshow(sqrt(u[0] ** 2 + u[1] ** 2).transpose(), cmap=cm.Reds)
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
with writer.saving(figure, 'out.mp4', 100):
    traverse_imgs(writer, images)
