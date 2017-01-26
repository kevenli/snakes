import itertools
import logging
import datetime
import copy
import random

logger = logging.getLogger(__name__)


class Snake(object):
    def __init__(self, map, points):
        self.head = map.get_point_yx(*points[0])
        self.body = [map.get_point_yx(*point) for point in points[1:]]

    def get_points(self):
        points = [self.head]
        if self.body:
            points += self.body
        return points

    @property
    def length(self):
        return 1 + len(self.body)


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __setattr__(self, key, value):
        self.__dict__.__setitem__(key, value)

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__.__getitem__(item)


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

        self.rooms = {(x, y): Room(x, y) for x, y in itertools.product(list(range(width)), list(range(height)), repeat=1)}
        self.np_room = self.rooms[(self.np.x, self.np.y)]
        for position, room in list(self.rooms.items()):
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

    # def print_map(self):
    #     import color_console
    #     for j in range(self.height):
    #         for i in range(self.width):
    #             # point = self.get_point(i,j)
    #             point = self.rooms[(i, j)]
    #             if point.danger == 0:
    #                 color_console.set_text_attr(color_console.FOREGROUND_GREEN)
    #             elif point.danger < 1:
    #                 color_console.set_text_attr(color_console.FOREGROUND_YELLOW)
    #             else:
    #                 color_console.set_text_attr(color_console.FOREGROUND_RED)
    #
    #             if point.has_snake:
    #                 print 'x',
    #             elif point.has_bean:
    #                 print 'o',
    #             else:
    #                 print '.',
    #         print
    #     color_console.set_text_attr(color_console.FOREGROUND_INTENSITY)

    def route_directions(self, route):
        directions = []
        current_dir = None
        dirs = ['west', 'north', 'south', 'east']
        for i, step in enumerate(route[0:-1]):
            next_step = route[i + 1]
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

    # @tail_call_optimized
    def find_way_fast(self, start_room, end_room, routes, route=None, max_steps=150, depth=0):
        min_distance = self.distance(start_room, end_room)
        if route is None:
            route = []

        if len(self.route_directions(route)) >= 6:
            return

        if depth >= max_steps:
            return

        for exit in list(start_room.exits.values()):
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
            # logger.debug(exit)
            route_copy = copy.copy(route)
            # logger.debug(route_copy)
            route_copy.append(exit)
            if exit == end_room:
                routes.append(route_copy)
            else:
                # check if not walked
                self.find_way_fast(exit, end_room, routes, route_copy, max_steps=max_steps, depth=depth + 1)

    def find_way_slow(self, start_room, end_room, routes, route=None, max_steps=150, depth=0):
        pass

    def find_way_astar(self, start_room, end_room):
        if isinstance(end_room, tuple):
            end_room = self.rooms[end_room]
        # initialize
        for room in list(self.rooms.values()):
            room.f = None
            room.g = None
            room.h = None
            room.parent = None

        open_list = [start_room]
        close_list = []

        while len(open_list) > 0:
            for node in open_list:
                if node.f is None:
                    node.g = 1
                    node.h = self.distance(node, end_room)
                    node.f = node.g + node.h
            current_node = sorted(open_list, key = lambda a: a.f)[0]
            open_list.remove(current_node)
            close_list.append(current_node)

            for exit in list(current_node.exits.values()):
                if exit.has_snake:
                    continue

                if exit in close_list:
                    continue

                try:
                    if exit.danger >= 1:
                        continue
                except AttributeError as e:
                    logger.warn(e)

                if exit not in open_list:
                    exit.parent = current_node
                    exit.g = current_node.g + 1
                    exit.h = self.distance(exit, end_room)
                    exit.f = exit.g + exit.h
                    open_list.append(exit)
                else:
                    if exit.g < current_node.g + 1:
                        exit.parent = current_node
                        exit.g = current_node.g + 1

            if end_room in open_list:
                path = [end_room]
                node = end_room
                while node.parent is not None:
                    path.insert(0, node.parent)
                    node = node.parent
                return path[1:]

    def mark_dangerous(self, snake_heads=None, depth=0, max_depth=5):
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
            all_exits += list(snake_head.exits.values())
        # all_exits = [snake_head.exits.values() for snake_head in snake_heads]
        for exit in all_exits:
            exit.danger += (1.0 / 4 ** depth)

        self.mark_dangerous(all_exits, depth + 1, max_depth=max_depth)

    def safe_step(self, next_step):
        if len(self.me.body) == 0:
            return True
        return self.find_longest_way(next_step, self.me.body[-1], max_steps=self.me.length) is not None


    def find_longest_way(self, start_room, end_room, route=None, max_steps=10):
        if route is None:
            route = []
        for exit in start_room.exits.values():
            if len(route) > max_steps:
                return route

            if exit.has_snake:
                continue

            if exit.danger >= 1:
                continue

            if exit in route:
                continue

            if exit == end_room:
                continue

            route_copy = copy.copy(route)
            route_copy.append(exit)

            exit_route = self.find_longest_way(exit, end_room, route_copy, max_steps=max_steps)
            if exit_route is not None:
                return exit_route


def hli(width, height, snakes, i, np):
    game_map = Map(width, height, copy.copy(snakes), i, copy.copy(np))
    game_map.mark_dangerous()
    start_room = game_map.rooms[(game_map.me.head.x, game_map.me.head.y)]
    end_rooms = [game_map.np_room, ((game_map.me.head.x + game_map.width/2) % game_map.width,
                    (game_map.me.head.y + game_map.height/2) % game_map.height),
                 (game_map.width/2, game_map.height/2)]


    dirs = {'north' : 0, 'east': 1, 'south': 2, 'west': 3}
    for end_room in end_rooms:
        route = game_map.find_way_astar(start_room=start_room, end_room=end_room)

        if route is not None:
            next_step = route[0]

            if not game_map.safe_step(next_step):
                continue

            for dir in list(dirs.keys()):
                if start_room.exits[dir] == next_step:
                    return dirs[dir]

    safe_exits = [exit for exit in start_room.exits.values() if exit.danger < 1 and not exit.has_snake]
    if not safe_exits:
        return random.choice([0,1,2,3])
    next_step = random.choice(safe_exits)
    for dir in list(dirs.keys()):
        if start_room.exits[dir] == next_step:
            return dirs[dir]

def test_routes(map):
    start_room = map.rooms[(map.me.head.x, map.me.head.y)]

    map.mark_dangerous()

    routes = []

    # max_steps = (map.width + map.height) / 2 + 1
    max_steps = 15
    map.find_way_fast(start_room=start_room, end_room=map.np_room, routes=routes, max_steps=max_steps)

    # for i in range(len(routes)):
    #     route = routes[i]
    #     print 'route: %d, distance: %d, danger: %d,  %s' % (i, len(route), sum([y.danger for y in route]), route)

    if len(routes) > 0:
        #print '%d fast routes found.' % len(routes)
        sorted(routes, key = lambda x : x.danger)

        route = routes[0]
        #print 'route: distance: %d, danger: %d,  %s' % (len(route), sum([y.danger for y in route]), route)

    else:
        pass
        #print 'not fast route'


def test_dangerous(map):
    map.mark_dangerous()
    map.print_map()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # hli(100, 100, [[[0,0],[0,1]], [[2,2], [3,2]]], 1, [0,42])
    # hli(4, 4, [[[0, 0], [0, 1]], [[1, 1], [1, 2]]], 1, [0, 3])

    width = 60
    height = 60

    # map = Map(width, height, [[[0, 0], [0, 1]], [[1, 1], [1, 2]]], 1, [0, 3])
    # map = Map(width, height, [[[0, 0], [0, 1]], [[10, 10], [10, 11]]], 0, [10, 15])
    map = Map(width, height, [[[0, 0], [0, 1]]], 0, [10, 15])
    map = Map(width, height, [[[0, 0]]], 0, [30, 30])

    start = datetime.datetime.now()
    # test_dangerous(map)
    test_routes(map)

    end = datetime.datetime.now()
    #print '%f seconds.' % (end - start).total_seconds()
