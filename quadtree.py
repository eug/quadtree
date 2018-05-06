from collections import namedtuple
from sortedcontainers import SortedList
from scipy.spatial.distance import euclidean

Point = namedtuple('Point', ['x', 'y'])

NO_REGION = -1
NORTH_WEST = 1
NORTH_EAST = 2
SOUTH_EAST = 3
SOUTH_WEST = 4

class Boundary:
    def __init__(self, center, dimension):
        self.center = center
        self.dimension = dimension

    def __str__(self):
        return 'Center=(%.4f, %.4f)\tDimension=%.4f' % (self.center.x, self.center.y, self.dimension)

    def contains(self, point):
        """ Check if the point contains in this boundary """
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
        self.is_splitted = []
        self.boundary = Boundary(center, dimension)
        self.max_depth = max_depth
        self.max_points = max_points
        self._depth = depth
        self.points = set([])
        self.nodes = {
            NORTH_WEST: None,
            NORTH_EAST: None,
            SOUTH_EAST: None,
            SOUTH_WEST: None
        }

    def __len__(self):
        if not self.is_splitted:
            return len(self.points)
        return sum(len(v) for v in self.nodes.values() if v)

    def __str__(self):
        return 'Depth=%d\t#Items=%d\t%s\t%s' % (self._depth, len(self.points), self.boundary, self.is_splitted)

    def __next__(self):
        raise StopIteration

    def subdivide(self, region):
        dm = self.boundary.dimension / 2
        mp = self.max_points
        md = self.max_depth
        dp = self._depth + 1
        x, y = self.boundary.center

        if region == NORTH_WEST:
            center = Point(x - dm, y + dm)
        elif region == NORTH_EAST:    
            center = Point(x + dm, y + dm)
        elif region == SOUTH_EAST:
            center = Point(x + dm, y - dm)
        elif region == SOUTH_WEST:
            center = Point(x - dm, y - dm)

        self.nodes[region] = TreeNode(center, dm, mp, md, dp)

    def insert(self, point):
        region = self.boundary.find(point)

        # Ignore objects that do not belong in this quad tree
        if region == NO_REGION:
            return False

        if len(self.points) < self.max_points or \
           self._depth == self.max_depth:

            if region not in self.is_splitted:
                self.points.add(point)
            else:
                self.nodes[region].insert(point)

            return True

        # otherwise, subdivide and then add the point
        # into its respective region
        if region not in self.is_splitted:
            self.is_splitted.append(region)
            self.subdivide(region)

        # Move all points to the child nodes (leaf)
        for p in self.points.copy():
            if self.boundary.find(p) == region:
                self.points.remove(p)
                self.nodes[region].insert(p)

        if self.nodes[region].insert(point):
            return True

        # This should never happen!
        return False

    def remove(self, point):
        region = self.boundary.find(point)

        if region == NO_REGION:
            return False

        if region in self.is_splitted:
            return self.nodes[region].remove(point)

        try:
            self.points.remove(point)
            return True
        except: pass

        return False

    def exist(self, point):
        region = self.boundary.find(point)

        if region == NO_REGION:
            return False

        if region not in self.is_splitted:
            return point in self.points

        return self.nodes[region].exist(point)

    def find(self, point):
        return self.boundary.find(point)

    def depth(self, point):
        region = self.boundary.find(point)

        if region == NO_REGION:
            return False

        if region not in self.is_splitted:
            return self._depth if point in self.points else -1

        return self.nodes[region].depth(point)

    def query_range(self, boundary):
        points = set([])
        
        if not self.boundary.intersects(boundary):
            return points

        for region in self.is_splitted:
            for p in self.nodes[region].query_range(boundary):
                if boundary.contains(p):
                    points.add(p)

        for p in self.points:
            if boundary.contains(p):
                points.add(p)

        return points

    def _count_points(self, boundary):
        if not self.boundary.intersects(boundary):
            return 0
        
        count = 0
        for region in self.is_splitted:
            count += self.nodes[region]._count_points(boundary)

        return len(self.points) + count

    def _compute_knn(self, points, point, k):
        neighbors = []
        for p in points:
            if p == point: continue
            dist = euclidean(point, p)
            neighbors.append((dist, p))
        return sorted(neighbors, key=lambda x: x[0])[:k]

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
        return self
    
    def __next__(self):
        return self.root.__next__()

    def insert(self, point):
        return self.root.insert(point)

    def remove(self, point):
        return self.root.remove(point)

    def exist(self, point):
        return self.root.exist(point)

    def find(self, point):
        return self.root.find(point)

    def depth(self, point):
        return self.root.depth(point)

    def query_range(self, boundary):
        return self.root.query_range(boundary)

    def knn(self, point, k):
        return self.root.knn(point, k)
