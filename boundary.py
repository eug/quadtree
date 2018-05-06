from common import NO_QUADRANT, NORTH_EAST, NORTH_WEST, SOUTH_EAST, SOUTH_WEST


class Boundary:
    def __init__(self, center, dimension):
        self.center = center
        self.dimension = dimension

    def __eq__(self, obj):
        return self.center == obj.center and \
               self.dimension == obj.dimension

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

    def quadrants(self, point):
        """ Find in which quadrant the point belongs to """
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

        return NO_QUADRANT

    def intersects(self, boundary):
        """ Check if the given boundary intersects this boundary """
        if not boundary:
            return False

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
