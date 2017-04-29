#
# Simple generic rectangle that works with negative and positive
# float numbers
#
#    * A rectangle is made out of four points.
#    * Iterating over a rectangle iterates over its corner points.
#    * Screen coordinates are used (x grows from left to right, y
#      grows from top to bottom). You can still use negative numbers.
#

from math import sqrt, acos, pi


class Point():

    x = None
    y = None

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return "%6.1f, %6.1f" % (self.x, self.y)

    def __eq__(self, obj):
        return obj.x == self.x and obj.y == self.y

    def distance_to_point(self, p):
        return sqrt((self.x-p.x)**2+(self.y-p.y)**2)

    def faces_line(self, line):
        return point_faces_edge(line, self)



class Rect():

    # Screen coordinates
    l_top  = None
    r_top  = None
    l_bot  = None
    r_bot  = None
    center = None
    width  = None
    height = None

    def __init__(self, x, y, width, height):
        assert width>0
        assert height>0
        self.l_top  = Point(x, y)
        self.r_top  = Point(x+width, y)
        self.r_bot  = Point(x+width, y+height)
        self.l_bot  = Point(x, y+height)
        self.center = Point(x+width/float(2), y+height/float(2))
        self.width  = width
        self.height = height


    def __str__(self):
        str=("(%4d,%4d)              (%4d,%4d)\n"
             "      .-----------------------.\n"
             "      |                       |\n"
             "      |                %6.1f |\n"
             "      |       %6.1f          |\n"
             "      '-----------------------'\n"
             "(%4d,%4d)              (%4d,%4d)"
             )
        nums=( self.l_top.x, self.l_top.y,         self.r_top.x, self.r_top.y,
               self.height,
               self.width,
               self.l_bot.x, self.l_bot.y,         self.r_bot.x, self.l_bot.y  )
        return str % nums


    def __iter__(self):
        yield self.l_top
        yield self.r_top
        yield self.r_bot
        yield self.l_bot


    # Gives back a copy of this rectangle
    def copy(self):
        return Rect(self.l_top.x, self.l_top.y, self.width, self.height)


    # Check to see if two croner points belong to the same edge
    def corners_belong_to_edge(self, c1, c2):
        return True in [
            (c1==self.l_top and c2==self.r_top) or
            (c1==self.r_top and c2==self.l_top) or
            (c1==self.r_top and c2==self.r_bot) or
            (c1==self.r_bot and c2==self.r_top) or
            (c1==self.r_bot and c2==self.l_bot) or
            (c1==self.l_bot and c2==self.r_bot) or
            (c1==self.l_bot and c2==self.l_top) or
            (c1==self.l_top and c2==self.l_bot) ]


    # ______
    #|    . |
    #|______|
    def is_point_inside_rect(self, point):
        return (self.l_top.x <= point.x <= self.r_top.x and
                self.l_top.y <= point.y <= self.l_bot.y)


    #  ______
    # |     _|____
    # |____|      |
    #      |______|
    def overlaps_with(self, rect):
        for corner in rect:
            if self.is_point_inside_rect(corner):
                return True
        return False


    #  ______                ____ ______
    # |     _|____          |    |      |
    # |____|      |   -->   |____|______|
    #      |______|
    def align_with_top_edge_of(self, rect):
        self.l_top.y = self.r_top.y = rect.r_top.y
        self.l_bot.y = self.r_bot.y = self.l_top.y+self.height
        return self


    #  ______                ______
    # |     _|____          |______|
    # |____|      |   -->   |      |
    #      |______|         |______|
    def align_with_left_edge_of(self, rect):
        self.l_top.x = self.l_bot.x = rect.l_top.x
        self.r_top.x = self.r_bot.x = self.l_top.x+self.width
        return self


    # ______
    #|      |
    #|______|
    #    ______
    #   |      |
    #   |______|
    def overlaps_on_x_axis_with(self, rect):
        return self.copy().align_with_top_edge_of(rect).overlaps_with(rect)


    # ______
    #|      |   ______
    #|______|  |      |
    #          |______|
    def overlaps_on_y_axis_with(self, rect):
        return self.copy().align_with_left_edge_of(rect).overlaps_with(rect)


    # ______
    #|      |             The calculation includes
    #|______|             both edges and corners.
    #        \ d
    #         \ ______
    #          |      |
    #          |______|
    def distance_to_rect(self, rect):

        # 1. see if they overlap)
        if self.overlaps_with(rect):
            return 0

        # 2. draw line between rectangles
        line = (self.center, rect.center)
        #print "line=%s %s" % (line[0], line[1])

        # 3. find the two edges that intersect the line
        p1, p2 = None, None
        for corner in self:
            if corner.faces_line(line):
                if p1 is None:
                    p1=corner
                elif self.corners_belong_to_edge(corner, p1):
                    p2=corner
        edge1=(p1, p2)
        p1, p2 = None, None
        for corner in rect:
            if corner.faces_line(line):
                if p1 is None:
                    p1=corner
                elif rect.corners_belong_to_edge(corner, p1):
                    p2=corner
        edge2=(p1, p2)

        if edge1[0] is None or edge1[1] is None or edge1[0] is None or edge2[1] is None:
            return 0

        # 4. find shortest distance between these two edges
        distances=[
            distance_between_edge_and_point(edge1, edge2[0]),
            distance_between_edge_and_point(edge1, edge2[1]),
            distance_between_edge_and_point(edge2, edge1[0]),
            distance_between_edge_and_point(edge2, edge1[1]),
        ]
        return min(distances)


# ---------------------- Math primitive functions ----------------------

def distance_between_points(point1, point2):
    return point1.distance_to_point(point2)

def distance_between_rects(rect1, rect2):
    return rect1.distance_to_rect(rect2)

def triangle_area_at_points(p1, p2, p3):
    a=p1.distance_to_point(p2)
    b=p2.distance_to_point(p3)
    c=p1.distance_to_point(p3)
    s=(a+b+c)/float(2)
    area=sqrt(s*(s-a)*(s-b)*(s-c))
    return area

# Finds angle using cos law
def angle(a, b, c):
    divid=(a**2+b**2-c**2)
    divis=(2*a*b)
    if (divis)>0:
        result=float(divid)/divis
        if result<=1.0 and result>=-1.0:
            return acos(result)
        return 0
    else:
        return 0

# Checks if point faces edge
def point_faces_edge(edge, point):
    a=edge[0].distance_to_point(edge[1])
    b=edge[0].distance_to_point(point)
    c=edge[1].distance_to_point(point)
    ang1, ang2 = angle(b, a, c), angle(c, a, b)
    if ang1>pi/2 or ang2>pi/2:
        return False
    return True

# Gives distance if the point is facing edge, else False
def distance_between_edge_and_point(edge, point): # edge is a tupple of points
    if point_faces_edge(edge, point):
        area=triangle_area_at_points(edge[0], edge[1], point)
        base=edge[0].distance_to_point(edge[1])
        height=area/(0.5*base)
        return height
    return min(distance_between_points(edge[0], point),
               distance_between_points(edge[1], point))