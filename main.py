import random as rnd

import matplotlib.pyplot as plt
import numpy as np

from common import Point, Boundary
from quadtree import DynamicQuadTree


def plot_partitions(node):
    x, y = node.boundary.center
    d = node.boundary.dimension

    xmin = x - d
    xmax = x + d
    ymin = y - d
    ymax = y + d

    plt.plot([xmin, xmax], [ymax, ymax], lw=.5, color='black')
    plt.plot([xmax, xmax], [ymin, ymax], lw=.5, color='black')
    plt.plot([xmax, xmin], [ymin, ymin], lw=.5, color='black')
    plt.plot([xmin, xmin], [ymin, ymax], lw=.5, color='black')

    for region in node._nodes:
        plot_partitions(node._nodes[region])

def plot_boundaries(boundary):
    x, y = boundary.center
    d = boundary.dimension

    xmin = x - d
    xmax = x + d
    ymin = y - d
    ymax = y + d

    plt.plot([xmin, xmax], [ymax, ymax], lw=1, color='gray', linestyle='dotted')
    plt.plot([xmax, xmax], [ymin, ymax], lw=1, color='gray', linestyle='dotted')
    plt.plot([xmax, xmin], [ymin, ymin], lw=1, color='gray', linestyle='dotted')
    plt.plot([xmin, xmin], [ymin, ymax], lw=1, color='gray', linestyle='dotted')
    
k = 10
target_point = 22
qt = DynamicQuadTree(max_depth=6)
rnd.seed(42)

points = []
for _ in range(0, 1000):
    x, y = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
    points.append(Point(x, y))
    qt.insert(Point(x, y))

x, y = [], []
for p in sorted(points):
    x.append(p.x)
    y.append(p.y)

lim = qt.root.boundary.dimension + .25

points_count = 0
dimension = 0
boundary = Boundary(points[target_point], dimension)
while points_count <= k:
    dimension += 0.1
    boundary = Boundary(points[target_point], dimension)
    points_count = qt.root._count_points(boundary)


plt.ylim(-lim, lim)
plt.xlim(-lim, lim)
plot_partitions(qt.root)
plot_boundaries(boundary)
plt.plot(x, y, 'o', markersize=2, color='blue')
plt.plot(points[target_point].x, points[target_point].y, 'o', markersize=2, color='red')

for _dist, _point in qt.knn(points[target_point], k):
    plt.plot(_point.x, _point.y, 'o', markersize=2, color='green')

plt.show()
