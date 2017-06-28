import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
import numpy as np
from mpl_toolkits.mplot3d import proj3d

x = []
y = []
z = []

#Reading two sets of x, y, z coordinates from a txt file
with open('data.txt', 'r') as csvfile:
    coords = csv.reader(csvfile, delimiter=',')
    for row in coords:
        x.append(int(row[0]))
        y.append(int(row[1]))
        z.append(int(row[2]))

#Class defining x, y, z vectors and the vector arrow-head appearance/size
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)

#Defines figure as 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#Axis range & labels
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])
ax.set_zlim([0, 10])
ax.set_xlabel('x axis')
ax.set_ylabel('y axis')
ax.set_zlabel('z axis')

a = Arrow3D(x, y, z, mutation_scale=20, lw=1, arrowstyle="->",
            color="b")
#Draw line on plot
ax.add_artist(a)

plt.show()


#class Arrow3D(FancyArrowPatch):
#    def __init__(self, xs, ys, zs, *args, **kwargs):
#        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
#        self._verts3d = xs, ys, zs
#
#    def draw(self, renderer):
#        xs3d, ys3d, zs3d = self._verts3d
#        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
#        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
#        FancyArrowPatch.draw(self, renderer)


#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

#ax.set_xlim([0, 10])
#ax.set_ylim([0, 10])
#ax.set_zlim([0, 10])
#ax.set_xlabel('x axis')
#ax.set_ylabel('y axis')
#ax.set_zlabel('z axis')

#a = Arrow3D([5, 10], [0, 5], [3, 6], mutation_scale=20, lw=1, arrowstyle="->",
#            color="b")
#b = Arrow3D([0, 10], [0, 2], [2, 4], mutation_scale=20, lw=1, arrowstyle="->",
#            color="r")
#c = Arrow3D([5, 0], [10, 5], [10, 5], mutation_scale=20, lw=1, arrowstyle="->",
#            color="g")
#ax.add_artist(a)
#ax.add_artist(b)
#ax.add_artist(c)
#plt.show()
