import bisect

from scipy.spatial.distance import euclidean

from common import (NO_QUADRANT, NORTH_EAST, NORTH_WEST, SOUTH_EAST,
                    SOUTH_WEST, Boundary, Point, belongs, intersects,
                    quadrants)
from node import TreeNode

BOUNDARY = 0
POINTS = 1

class StaticQuadTree:

    def __init__(self, dimension=1, max_depth=4):
        self.max_depth = max_depth
        self._quadrants = [0] * int(((4 ** (max_depth + 1))-1)/3)
        self._quadrants[0] = (Boundary(Point(0, 0), dimension), set([]))
        self._decompose(self._quadrants[0][BOUNDARY], 0, 0)

    def _decompose(self, boundary, depth, parent):
        if depth == self.max_depth:
            return
        
        x, y = boundary.center
        dm = boundary.dimension / 2

        index0 = 4 * parent + NORTH_WEST
        index1 = 4 * parent + NORTH_EAST
        index2 = 4 * parent + SOUTH_EAST
        index3 = 4 * parent + SOUTH_WEST

        self._quadrants[index0] = (Boundary(Point(x - dm, y + dm), dm), set([]))
        self._quadrants[index1] = (Boundary(Point(x + dm, y + dm), dm), set([]))
        self._quadrants[index2] = (Boundary(Point(x + dm, y - dm), dm), set([]))
        self._quadrants[index3] = (Boundary(Point(x - dm, y - dm), dm), set([]))

        self._decompose(self._quadrants[index0][BOUNDARY], depth + 1, index0)
        self._decompose(self._quadrants[index1][BOUNDARY], depth + 1, index1)
        self._decompose(self._quadrants[index2][BOUNDARY], depth + 1, index2)
        self._decompose(self._quadrants[index3][BOUNDARY], depth + 1, index3)

    def index(self, point):
        idx = 0
        for _ in range(0, self.max_depth):
            q = quadrants(self._quadrants[idx][BOUNDARY], point)
            if q == NO_QUADRANT: return
            idx = 4 * idx + q
        return idx

    def __len__(self):
        return sum(len(q[1]) for q in self._quadrants)

    def __iter__(self):
        return (point for quad in self._quadrants for point in quad[POINTS])

    def __contains__(self, point):
        return point in self._quadrants[self.index(point)][POINTS]

    def insert(self, point):
        self._quadrants[self.index(point)][POINTS].add(point)

    def remove(self, point):
        try:
            self._quadrants[self.index(point)][POINTS].remove(point)
            return True
        except:
            return False

    def update(self, new_point, old_point):
        try:
            self._quadrants[self.index(old_point)][POINTS].remove(old_point)
            self._quadrants[self.index(new_point)][POINTS].add(new_point)
            return True
        except:
            return False

    def query_range(self, boundary):
        points = []
        for quadrant in self._quadrants:
            if intersects(quadrant[BOUNDARY], boundary):
                for point in quadrant[POINTS]:
                    if belongs(boundary, point):
                        points.append(point)
        return points

    def knn(self, point, k, factor=.1):
        if len(self) < k:
            points = self.query_range(self._quadrants[BOUNDARY])
            return self._compute_knn(points, point, k)
        
        points_count = 0
        dimension = factor

        while points_count <= k:
            dimension += factor
            points_count = self._count_points(Boundary(point, dimension)) - 1
            # Note: subtracts 1 to ignore the point itself

        points = self.query_range(Boundary(point, dimension))
        return self._compute_knn(points, point, k)

    def _count_points(self, boundary):
        count = 0
        for quadrant in self._quadrants:
            if intersects(quadrant[BOUNDARY], boundary):
                count += len(quadrant[POINTS])
        return count

    def _compute_knn(self, points, point, k):
        neighbors = []
        distant_neighbor = None

        for p in points:
            if p == point: continue

            dist = euclidean(point, p)
            neighbor = (dist, p)

            if len(neighbors) < k:
                if not distant_neighbor:
                    distant_neighbor = neighbor
                if neighbor[0] > distant_neighbor[0]:
                    distant_neighbor = neighbor
                bisect.insort(neighbors, neighbor)
                continue

            if neighbor[0] < distant_neighbor[0]:
                del neighbors[-1]
                bisect.insort(neighbors, neighbor)
                distant_neighbor = neighbors[-1]

        return neighbors


class DynamicQuadTree:

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
