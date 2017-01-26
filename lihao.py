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
        return {'north': self.north,
                'west': self.west,
                'south': self.south,
                'east': self.east
                }

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
        if me is not None:
            self.me = Snake(self, snakes.pop(me))
        self.snakes = [Snake(self, snake) for snake in snakes]

        self.rooms = {(x,y):Room(x,y) for x,y in itertools.product(range(width), range(height), repeat=1)}
        self.np_room = self.rooms[(self.np.x, self.np.y)]
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
        import color_console
        for j in range(self.height):
            for i in range(self.width):
                #point = self.get_point(i,j)
                point = self.rooms[(i,j)]
                if point.danger == 0:
                    color_console.set_text_attr(color_console.FOREGROUND_GREEN)
                elif point.danger < 1:
                    color_console.set_text_attr(color_console.FOREGROUND_YELLOW)
                else:
                    color_console.set_text_attr(color_console.FOREGROUND_RED)


                if point.has_snake:
                    print 'x',
                elif point.has_bean:
                    print 'o',
                else:
                    print '.',
            print
        color_console.set_text_attr(color_console.FOREGROUND_INTENSITY)


    def route_directions(self, route):
        directions = []
        current_dir = None
        dirs = ['west', 'north', 'south', 'east']
        for i, step in enumerate(route[0:-1]):
            next_step = route[i+1]
            for dir in dirs:
                if step.exits[dir] == next_step:
                    if dir != current_dir:
                        current_dir = dir
                        directions.append(current_dir)
                    break

        return directions

    def distance(self, start_room, end_room):
        if isinstance(start_room, tuple):
            start_room = self.rooms[start_room]
        if isinstance(end_room, tuple):
            end_room = self.rooms[end_room]
        min_distance = min(abs(start_room.x - end_room.x),
                           abs(start_room.x - self.width - end_room.x),
                           abs(start_room.x + self.width - end_room.x)) + \
                        min(abs(start_room.y - end_room.y),
                            abs(start_room.y - self.height - end_room.y),
                            abs(start_room.y + self.height - end_room.y))
        return min_distance

    #@tail_call_optimized
    def find_way_fast(self, start_room, end_room, routes, route=None, max_steps=150, depth=0):
        min_distance = self.distance(start_room, end_room)
        if route is None:
            route = []

        if len(self.route_directions(route))>=6:
            return

        if depth >= max_steps:
            return

        for exit in start_room.exits.values():
            if exit in route:
                # circle
                continue

            if exit.has_snake:
                # snake blocked
                continue

            if self.distance(exit, end_room) > min_distance:
                # check only shortest way
               continue

            # if exit.danger >= 1:
            #     continue
            #logger.debug(exit)
            route_copy = copy.copy(route)
            #logger.debug(route_copy)
            route_copy.append(exit)
            if exit == end_room:
                routes.append(route_copy)
            else:
                # check if not walked
                self.find_way_fast(exit, end_room, routes, route_copy, max_steps=max_steps, depth=depth+1)

    def find_way_slow(self, start_room, end_room, routes, route=None, max_steps=150, depth=0):
        pass

    def render_dangerous(self, snake_heads=None, depth=0, max_depth=5):
        '''
            compute oppotunity of blocks each snake will go

        :param snake_heads:  snake head blocks, pass None for the first cursive, it will load snakes from map.
        :param depth: current recursive depth
        :param max_depth: the round count to forecast
        :return:
        '''
        if depth >= max_depth:
            return

        if snake_heads is None:
            snake_heads = [self.rooms[(snake.head.x, snake.head.y)] for snake in self.snakes]

        all_exits = []
        for snake_head in snake_heads:
            all_exits += snake_head.exits.values()
        #all_exits = [snake_head.exits.values() for snake_head in snake_heads]
        for exit in all_exits:
            exit.danger += (1.0/4**depth)

        self.render_dangerous(all_exits, depth+1, max_depth=max_depth)


def hli(width, height, snakes, i, np):
    map = Map(width, height, snakes, i, np)
    map.render_dangerous()


def test_routes(map):
    start_room = map.rooms[(map.me.head.x, map.me.head.y)]

    map.render_dangerous()

    routes = []

    #max_steps = (map.width + map.height) / 2 + 1
    max_steps = 15
    map.find_way_fast(start_room=start_room, end_room=map.np_room, routes=routes, max_steps=max_steps)

    # for i in range(len(routes)):
    #     route = routes[i]
    #     print 'route: %d, distance: %d, danger: %d,  %s' % (i, len(route), sum([y.danger for y in route]), route)

    if len(routes)>0:
        print '%d fast routes found.' % len(routes)
        sorted(routes, lambda route1, route2: sum([x.danger for x in route1]) >= sum([y.danger for y in route2]))

        route = routes[0]
        print 'route: distance: %d, danger: %d,  %s' % (len(route), sum([y.danger for y in route]), route)

    else:
        print 'not fast route'

def test_dangerous(map):
    map.render_dangerous()
    map.print_map()



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #hli(100, 100, [[[0,0],[0,1]], [[2,2], [3,2]]], 1, [0,42])
    #hli(4, 4, [[[0, 0], [0, 1]], [[1, 1], [1, 2]]], 1, [0, 3])

    width = 60
    height = 60

    #map = Map(width, height, [[[0, 0], [0, 1]], [[1, 1], [1, 2]]], 1, [0, 3])
    #map = Map(width, height, [[[0, 0], [0, 1]], [[10, 10], [10, 11]]], 0, [10, 15])
    map = Map(width, height, [[[0, 0], [0, 1]]], 0, [10, 15])
    map = Map(width, height, [[[0, 0]]], 0, [30, 30])

    start = datetime.datetime.now()
    #test_dangerous(map)
    test_routes(map)

    end = datetime.datetime.now()
    print '%f seconds.' % (end - start).total_seconds()


