from collections import namedtuple

NO_QUADRANT = -1
NORTH_WEST = 1
NORTH_EAST = 2
SOUTH_EAST = 3
SOUTH_WEST = 4

Point = namedtuple('Point', ['x', 'y'])
Boundary = namedtuple('Boundary', ['center', 'dimension'])

def belongs(boundary, point):
    """ Check if the point belongs to the boundary """
    if not point:
        return False

    d = boundary.dimension
    cx, cy = boundary.center
    px, py = point

    return (py <= cy + d and py >= cy - d) and (px <= cx + d and px >= cx - d)

def quadrants(boundary, point):
    """ Find in which quadrant the point belongs to """
    if not boundary or not point:
        return False
    
    d = boundary.dimension
    cx, cy = boundary.center
    px, py = point

    if (py <= cy + d and py >= cy) and (px >= cx - d and px <= cx):
        return NORTH_WEST

    if (py <= cy + d and py >= cy) and (px <= cx + d and px >= cx):
        return NORTH_EAST

    if (py >= cy - d and py <= cy) and (px <= cx + d and px >= cx):
        return SOUTH_EAST

    if (py >= cy - d and py <= cy) and (px >= cx - d and px <= cx):
        return SOUTH_WEST

    return NO_QUADRANT

def intersects(boundary0, boundary1):
    """ Check if the given boundary intersects this boundary """
    if not boundary0 or not boundary1:
        return False

    ad = boundary0.dimension
    aleft = boundary0.center.x - ad
    aright = boundary0.center.x + ad
    atop = boundary0.center.y + ad
    abottom = boundary0.center.y - ad

    bd = boundary1.dimension
    bleft = boundary1.center.x - bd
    bright = boundary1.center.x + bd
    btop = boundary1.center.y + bd
    bbottom = boundary1.center.y - bd

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
