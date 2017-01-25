import itertools
import logging
import datetime

logger = logging.getLogger(__name__)
import copy

import sys
class TailRecurseException:
   def __init__(self, args, kwargs):
     self.args = args
     self.kwargs = kwargs

def tail_call_optimized(g):
   def func(*args, **kwargs):
     f = sys._getframe()
     if f.f_back and f.f_back.f_back and f.f_back.f_back.f_code == f.f_code:
       raise TailRecurseException(args, kwargs)
     else:
       while 1:
         try:
           return g(*args, **kwargs)
         except TailRecurseException, e:
           args = e.args
           kwargs = e.kwargs
   func.__doc__ = g.__doc__
   return func

class Snake(object):
    def __init__(self, map, points):
        #points = copy.copy(points)
        #map(lambda x: x.reverse(), points)
        self.head = map.get_point_yx(*points[0])
        self.body = [map.get_point_yx(*point) for point in points[1:]]

    def get_points(self):
        points = [self.head]
        if self.body:
            points += self.body
        return points


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __setattr__(self, key, value):
        self.__dict__.__setitem__(key, value)

    def __getattr__(self, item):
        if self.__dict__.has_key(item):
            return self.__dict__.__getitem__(item)

class DummyPoint(object):
    def __init__(self, x, y, source_point):
        if not isinstance(source_point, Point):
            raise Exception('Invalid type')
        self.x = x
        self.y = y
        self.source_point = source_point


class Room(object):
    north = None
    south = None
    west = None
    east = None

    has_snake = False
    has_bean = False
    danger = 0.0
    walked = False

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def exits(self):
        return [self.north, self.west, self.south, self.east]

    def __str__(self):
        return '(%d,%d)' % (self.x, self.y)

    def __repr__(self):
        return '(%d,%d)' % (self.x, self.y)


class Map(object):
    def __init__(self, width, height, snakes, me, np):
        self.martix = [[Point(i, j) for j in range(height)] for i in range(width)]
        self.height = height
        self.width = width
        self.np = self.get_point_yx(*np)
        self.me = Snake(self, snakes.pop(me))
        self.snakes = [Snake(self, snake) for snake in snakes]

        self.rooms = {(x,y):Room(x,y) for x,y in itertools.product(range(width), range(height), repeat=1)}
        for position, room in self.rooms.items():
            position_x, position_y = position
            room.north = self.rooms[((position_x) % width, (position_y - 1) % height)]
            room.south = self.rooms[((position_x) % width, (position_y + 1) % height)]
            room.west = self.rooms[((position_x - 1) % width, (position_y) % height)]
            room.east = self.rooms[((position_x + 1) % width, (position_y) % height)]

        for snake in self.snakes + [self.me]:
            for point in [snake.head] + snake.body:
                point.has_snake = True

        for snake in self.snakes + [self.me]:
            for point in [snake.head] + snake.body:
                room = self.rooms[(point.x, point.y)]
                room.has_snake = True
                room.danger = 1.0

        self.np.has_bean = True
        self.rooms[(self.np.x, self.np.y)].has_bean = True


    def get_point(self, x, y):
        return self.martix[x % self.width][y % self.height]

    def get_point_yx(self, y, x):
        return self.martix[x % self.width][y % self.height]

    def print_map(self):
        for j in range(self.height):
            for i in range(self.width):
                #point = self.get_point(i,j)
                point = self.rooms[(i,j)]
                if point.has_snake:
                    print 'x',
                elif point.has_bean:
                    print 'o',
                else:
                    print ' ',
            print

    def expend_map(self):
        self.expend_matrix = [[DummyPoint(i,j, self.get_point(i,j)) for j in range(self.height*3)] for i in range(self.width*3)]

    #@tail_call_optimized
    def find_way(self, start_room, end_room, routes, route=None, max_steps=150, depth=0):
        min_distance = min(abs(start_room.x - end_room.x), abs(start_room.x + self.width - end_room.x)) + \
            min(abs(start_room.y - end_room.y), abs(start_room.y + self.height - end_room.y))
        if route is None:
            route = []

        #if len(route) >= max_steps:
        #    return
        if depth >= max_steps:
            return

        for exit in start_room.exits:
            if exit in route:
                continue

            if exit.has_snake:
                continue
            #logger.debug(exit)
            route_copy = copy.copy(route)
            #logger.debug(route_copy)
            route_copy.append(exit)
            if exit == end_room:
                routes.append(route_copy)
            else:
                # check if not walked
                self.find_way(exit, end_room, routes, route_copy, max_steps=max_steps, depth=depth+1)





def hli(width, height, snakes, i, np):
    map = Map(width, height, snakes, i, np)

    # for snake in map.snakes:
    #     for point in snake.get_points():
    #         map.get_point(point.x, point.y).has_shake=True

    bean_y = np[0]
    bean_x = np[1]

    map.expend_map()




    map.print_map()
    #map.find_way(map.me)



#def nearest_distance(map, p_snake_head, p_bean):



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #hli(100, 100, [[[0,0],[0,1]], [[2,2], [3,2]]], 1, [0,42])
    #hli(4, 4, [[[0, 0], [0, 1]], [[1, 1], [1, 2]]], 1, [0, 3])

    width = 7
    height = 7
    #max_steps = 15
    max_steps = width + height + 1
    map = Map(width, height, [[[0, 0], [0, 1]], [[1, 1], [1, 2]]], 1, [0, 3])
    start_room = map.rooms[(0,0)]
    end_room = map.rooms[(3,2)]


    routes = []

    start = datetime.datetime.now()
    map.find_way(start_room=start_room, end_room=end_room, routes=routes, max_steps=max_steps)
    #print list(routes)
    end = datetime.datetime.now()


    for i in range(len(routes)):
        route = routes[i]
        print 'route: %d, distance: %d' % (i, len(route))

    print (end - start).total_seconds()
    print len(routes)
    print routes[0]

