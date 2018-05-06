from common import Point
from node import TreeNode


class QuadTree:

    def __init__(self, dimension=1, max_points=1, max_depth=4):
        self.max_points = max_points
        self.max_depth = max_depth
        self.root = TreeNode(Point(0, 0), dimension, max_points, max_depth, 0)

    def __len__(self):
        return len(self.root)

    def __iter__(self):
        return iter(self.root)

    def __contains__(self, point):
        return self.root.exist(point)

    def insert(self, point):
        return self.root.insert(point)

    def remove(self, point):
        return self.root.remove(point)

    def update(self, new_point, old_point):
        return self.root.update(new_point, old_point)

    def query_range(self, boundary):
        return self.root.query_range(boundary)

    def knn(self, point, k):
        return self.root.knn(point, k)
