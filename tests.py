from lihao import Map
from unittest import TestCase

class MapTest(TestCase):
    def test_distrance(self):
        width = 100
        height = 100
        start = (0,0)
        end = (50,50)
        map = Map(width, height, [[[0,0]]], 0, [0,0])

        distance = map.distance(start, end)
        self.assertEqual(distance,100)

    def test_distrance2(self):
        width = 100
        height = 100
        start = (0, 0)
        end = (0, 10)
        map = Map(width, height, [[[0, 0]]], 0, [0, 0])

        distance = map.distance(start, end)
        self.assertEqual(distance, 10)

    def test_distrance3(self):
        width = 100
        height = 100
        start = (0,0)
        end = (0,51)
        map = Map(width, height, [[[0,0]]], 0, [0,0])

        distance = map.distance(start, end)
        self.assertEqual(distance,49)

    def test_dangerous(map):
        width = 100
        height = 100
        start = (0,0)
        end = (0,51)
        map = Map(width, height, [[[0,0]]], 0, [1,1])

        map.mark_dangerous()
        map.print_map()

    def test_route(self):
        width = 100
        height = 100
        start = (0,0)
        end = (0,51)
        map = Map(width, height, [[[0,0]]], 0, [10,10])

        start_room = map.rooms[(map.me.head.x, map.me.head.y)]

        map.mark_dangerous()

        routes = []

        # max_steps = (map.width + map.height) / 2 + 1
        max_steps = 20
        map.find_way_fast(start_room=start_room, end_room=map.np_room, routes=routes, max_steps=max_steps)

        # for i in range(len(routes)):
        #     route = routes[i]
        #     print 'route: %d, distance: %d, danger: %d,  %s' % (i, len(route), sum([y.danger for y in route]), route)

        if len(routes) > 0:
            print '%d fast routes found.' % len(routes)
            sorted(routes, lambda route1, route2: sum([x.danger for x in route1]) >= sum([y.danger for y in route2]))

            route = routes[0]
            print 'route: distance: %d, danger: %d,  %s' % (len(route), sum([y.danger for y in route]), route)

        else:
            print 'not fast route'

    def test_find_way_astar(self):
        width = 100
        height = 100
        map = Map(width, height, [[[0,0]]], 0, [10,10])
        start_room = map.rooms[(map.me.head.x, map.me.head.y)]

        route = map.find_way_astar(start_room=start_room, end_room=map.np_room)
        print route
        print len(route)

    def test_find_way_astar_with_block(self):
        width = 100
        height = 100
        map = Map(width, height, [[[1, 0]], [[0,3], [1,3], [2,3]]], 0, [1, 10])
        start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        route = map.find_way_astar(start_room=start_room, end_room=map.np_room)
        print route
        print len(route)

    def test_find_way_astar_with_block(self):
        width = 100
        height = 100
        map = Map(width, height, [[[1, 0]], [[0, 3], [1, 3], [2, 3]]], 0, [1, 10])
        start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        route = map.find_way_astar(start_room=start_room, end_room=map.np_room)
        print route
        print len(route)

    def test_find_way_astar_with_dangerous(self):
        width = 100
        height = 100
        map = Map(width, height, [[[1, 0]], [[0, 3], [1, 3], [2, 3]]], 0, [1, 10])
        map.mark_dangerous()
        start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        route = map.find_way_astar(start_room=start_room, end_room=map.np_room)
        print route
        print len(route)


    def test_find_way_astar_self_tail(self):
        width = 100
        height = 100
        map = Map(width, height, [[[1, 0], [1,1]], [[0, 3], [1, 3], [2, 3]]], 0, [1, 10])
        map.mark_dangerous()
        start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        route = map.find_way_astar(start_room=start_room, end_room=map.np_room)
        print route
        print len(route)

    def test_find_longest_way(self):
        width = 100
        height = 100
        map = Map(width, height, [[[1, 0], [1, 1]], [[0, 3], [1, 3], [2, 3]]], 0, [1, 10])
        map.mark_dangerous()
        start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        route = map.find_longest_way(start_room=start_room, end_room=map.me.body[-1], max_steps=30)
        print route

    def test_find_longest_way2(self):
        width = 5
        height = 5
        map = Map(width, height, [[[1, 0], [1, 1]], [[0, 3], [1, 3], [2, 3]]], 0, [1, 1])
        map.mark_dangerous()
        start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        route = map.find_longest_way(start_room=start_room, end_room=map.me.body[-1], max_steps=30)
        print route

    def test_safe_step(self):
        width = 5
        height = 5
        me = [[1,3], [1,4], [1,5]]
        snake1 = [[2,3], [2,2], [2,1], [2,0], [1,0], [0,0], [0,1], [0,2]]
        np = [1,1]
        map = Map(width, height, [me, snake1], 0, np)
        map.mark_dangerous()
        #map.print_map()
        #start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        next_step = map.rooms[(1,1)]
        is_safe = map.safe_step(next_step)
        self.assertFalse(is_safe)

    def test_safe_step2(self):
        width = 5
        height = 5
        me = [[1, 3], [1, 4], [1, 5]]
        np = [1, 1]
        map = Map(width, height, [me], 0, np)
        map.mark_dangerous()
        #map.print_map()
        # start_room = map.rooms[(map.me.head.x, map.me.head.y)]
        next_step = map.rooms[(1, 1)]
        is_safe = map.safe_step(next_step)
        self.assertTrue(is_safe)
