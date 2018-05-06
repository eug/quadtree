import bisect
from collections import namedtuple

from scipy.spatial.distance import euclidean

Point = namedtuple('Point', ['x', 'y'])

NO_REGION = -1
NORTH_WEST = 0
NORTH_EAST = 1
SOUTH_EAST = 2
SOUTH_WEST = 3

class Boundary:
    def __init__(self, center, dimension):
        self.center = center
        self.dimension = dimension

    def __str__(self):
        s  = 'Center=({}, {})\t'
        s += 'Dimension={}'
        return s.format(self.center.x, self.center.y, self.dimension)

    def belongs(self, point):
        """ Check if the point belongs to this boundary """
        if not point:
            return False

        d = self.dimension
        cx, cy = self.center
        px, py = point
    
        return  py <= cy + d and py >= cy - d and \
                px <= cx + d and px >= cx - d

    def find(self, point):
        """ Find in which region the point belongs to """
        if not point:
            return False
        
        d = self.dimension
        cx, cy = self.center
        px, py = point

        if py <= cy + d and py >= cy and \
           px >= cx - d and px <= cx:
            return NORTH_WEST

        if py <= cy + d and py >= cy and \
           px <= cx + d and px >= cx:
            return NORTH_EAST

        if py >= cy - d and py <= cy and \
           px <= cx + d and px >= cx:
            return SOUTH_EAST

        if py >= cy - d and py <= cy and \
           px >= cx - d and px <= cx:
            return SOUTH_WEST

        return NO_REGION

    def intersects(self, boundary):
        ad = self.dimension
        aleft = self.center.x - ad
        aright = self.center.x + ad
        atop = self.center.y + ad
        abottom = self.center.y - ad

        bd = boundary.dimension
        bleft = boundary.center.x - bd
        bright = boundary.center.x + bd
        btop = boundary.center.y + bd
        bbottom = boundary.center.y - bd

        intersect_left  = bright > aleft and bleft < aleft
        intersect_right = bleft < aright and bright > aright
        intersect_top   = bbottom < atop and btop > atop
        intersect_bottom= btop > abottom and bbottom < abottom

        intersect_inside = (atop > btop and abottom < bbottom) or\
                           (aleft < bleft and aright > bright)

        return intersect_top and intersect_left  or\
               intersect_top and intersect_right or\
               intersect_bottom and intersect_left  or\
               intersect_bottom and intersect_right or\
               intersect_inside

class TreeNode:
    def __init__(self, center, dimension, max_points, max_depth, depth):
        self.boundary = Boundary(center, dimension)
        self.max_depth = max_depth
        self.max_points = max_points
        self._depth = depth
        self._points = set([])
        self._nodes = {}

    @property
    def _splitted(self):
        return len(self._nodes) > 0

    def __len__(self):
        if not self._splitted:
            return len(self._points)
        return sum(len(v) for v in self._nodes.values() if v)

    def __str__(self):
        s  = 'Depth={}\t'
        s += 'Length={}\t'
        s += 'Partitions={}'
        return s.format(self._depth, len(self._points, len(self._splitted)))

    def __iter__(self):
        points = []
        stack = [self]
        while stack:
            node = stack.pop()
            for n in node._nodes.values():
                stack.append(n)
            points += node._points
        return iter(points)

    def subdivide(self, region):
        x, y = self.boundary.center
        dm = self.boundary.dimension / 2
        mp = self.max_points
        md = self.max_depth
        dp = self._depth + 1

        if region == NORTH_WEST:
            center = Point(x - dm, y + dm)
        elif region == NORTH_EAST:    
            center = Point(x + dm, y + dm)
        elif region == SOUTH_EAST:
            center = Point(x + dm, y - dm)
        elif region == SOUTH_WEST:
            center = Point(x - dm, y - dm)

        self._nodes[region] = TreeNode(center, dm, mp, md, dp)

    @property
    def _has_max_points(self):
        return len(self._points) >= self.max_points

    @property
    def _is_max_depth(self):
        return self._depth == self.max_depth

    def _insert_at(self, point, region):
        if region not in self._nodes:
            self._points.add(point)
        else:
            self._nodes[region].insert(point)

    def insert(self, point):
        region = self.boundary.find(point)

        if region == NO_REGION:
            return False

        if not self._has_max_points or self._is_max_depth:
            self._insert_at(point, region)
            return True
        
        if region not in self._nodes:
            self.subdivide(region)

        for p in self._points.copy():
            if self.boundary.find(p) == region:
                self._points.remove(p)
                self._nodes[region].insert(p)

        return self._nodes[region].insert(point)

    def remove(self, point):
        region = self.boundary.find(point)

        if region == NO_REGION:
            return False

        if region in self._nodes:
            return self._nodes[region].remove(point)

        try:
            self._points.remove(point)
            return True
        except: pass

        return False

    def update(self, new_point, old_point):
        region = self.boundary.find(old_point)

        if region == NO_REGION:
            return False

        if region not in self._nodes:
            try:
                self._points.remove(old_point)
                self._points.add(new_point)
                return True
            except:
                return False

        return self._nodes[region].update(new_point, old_point)

    def exist(self, point):
        region = self.boundary.find(point)

        if region == NO_REGION:
            return False

        if region not in self._nodes:
            return point in self._points

        return self._nodes[region].exist(point)

    def find(self, point):
        return self.boundary.find(point)

    def depth(self, point):
        region = self.boundary.find(point)

        if region == NO_REGION:
            return False

        if region not in self._nodes:
            return self._depth if point in self._points else -1

        return self._nodes[region].depth(point)

    def query_range(self, boundary):
        points = set([])

        if not self.boundary.intersects(boundary):
            return points

        for region in self._nodes:
            for p in self._nodes[region].query_range(boundary):
                if boundary.belongs(p):
                    points.add(p)

        for p in self._points:
            if boundary.belongs(p):
                points.add(p)

        return points

    def _count_points(self, boundary):
        if not self.boundary.intersects(boundary):
            return 0

        count = 0
        for region in self._nodes:
            count += self._nodes[region]._count_points(boundary)

        return sum(1 for p in self._points if boundary.belongs(p)) + count

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

    def knn(self, point, k, factor=.1):
        if len(self) < k:
            points = self.query_range(self.boundary)
            return self._compute_knn(points, point, k)

        points_count = 0
        dimension = factor

        while points_count <= k:
            dimension += factor
            points_count = self._count_points(Boundary(point, dimension)) - 1
            # Note: subtracts 1 to ignore the point itself

        points = self.query_range(Boundary(point, dimension))
        return self._compute_knn(points, point, k)


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

    def depth(self, point):
        return self.root.depth(point)

    def query_range(self, boundary):
        return self.root.query_range(boundary)

    def knn(self, point, k):
        return self.root.knn(point, k)
