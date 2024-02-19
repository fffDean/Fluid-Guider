from numpy import *
from matplotlib import cm
from matplotlib.animation import FFMpegWriter
import matplotlib.pyplot as plt

images = []
for i in range(54601):
    if i%100 == 0:
        # density1, density2, velocity
        data = loadtxt('D:/c++code/data_n5_L&d16.65_D0.003000_rho1&rho21.000000_Re110.000000_Re210.000000_uLB10.020000_uLB20.020000/density1_'+str(i)+'.dat', dtype=float64)
        data = reshape(data, (720, 357))
        images.append(data)

def traverse_imgs(writer, images):
    # 遍历所有图片，并且让writer抓取视频帧
    for img in images:
        plt.imshow(img, cmap=cm.Reds)
        writer.grab_frame()
        plt.pause(0.01)
        plt.clf()

metadata = dict(title='01', artist='Matplotlib', comment='depth prediiton')
writer = FFMpegWriter(fps=6, metadata=metadata)

# 读出自己的所有图片

figure = plt.figure(figsize=(10.8, 7.2))
plt.ion()  # 为了可以动态显示
plt.tight_layout()  # 尽量减少窗口的留白
with writer.saving(figure, 'out5_.mp4', 100):
    traverse_imgs(writer, images)
