from quadtree import QuadTree, Point, Boundary
import random as rnd
rnd.seed(42)

qt = QuadTree(max_depth=8)
for i in range(0, 1000):
    x, y = rnd.random(), rnd.random()
    # print(x, y)
    qt.insert(Point(x, y))

for p in qt.query_range(Boundary(Point(0.5, 0.5), 0.2)):
    print(p)
# print(qt.root.boundary.intersects(Boundary(Point(0.5, 0.5), 0.1)))