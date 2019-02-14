from solution import Game, Point, Buster, GHOST_STEP, DISTANCE_SEE
import copy
import numpy as np


class Line:
    def __init__(self, a, b):
        self.a, self.b = a, b

    @property
    def is_horizontal(self):
        return self.a.y == self.b.y

    @property
    def is_vertical(self):
        return self.a.x == self.b.x

    @staticmethod
    def is_between_ex_in(a, b, c):
        if a < b:
            return a < c <= b
        elif b < a:
            return b <= c < a
        else:
            raise Exception('is_between_ex_in')

    def get_orthogonal(self, point: Point) -> 'Line':
        if self.is_horizontal:
            return Line(Point(point.x, 0), Point(point.x, 9000))
        elif self.is_vertical:
            return Line(Point(0, point.y), Point(16000, point.y))
        else:
            raise Exception('get_orthogonal')

    def project(self, point: Point) -> Point:
        if self.is_horizontal:
            return Point(point.x, self.a.y)
        elif self.is_vertical:
            return Point(self.a.x, point.y)
        else:
            raise Exception('get_orthogonal')

    def is_point_between(self, point: Point, another_line: 'Line') -> bool:
        if self.is_horizontal and another_line.is_horizontal:
            return Line.is_between_ex_in(self.a.y, another_line.a.y, point.y)
        elif self.is_vertical and another_line.is_vertical:
            return Line.is_between_ex_in(self.a.x, another_line.a.x, point.x)
        else:
            raise Exception('is_point_between')

    def is_point_behind(self, point: Point, another_line: 'Line') -> bool:
        if self.is_horizontal and another_line.is_horizontal:
            return self.a.y > another_line.a.y > point.y or self.a.y < another_line.a.y < point.y
        elif self.is_vertical and another_line.is_vertical:
            return self.a.x > another_line.a.x > point.x or self.a.x < another_line.a.x < point.x
        else:
            raise Exception('is_point_behind')


class TaskBase:
    def __init__(self, game, buster):
        self.game = game
        self.buster = buster

    def step(self):
        pass

    @property
    def is_finished(self):
        return False


class GoToBase(TaskBase):
    def __init__(self, game, buster):
        TaskBase.__init__(self, game, buster)

    def step(self):
        return f'MOVE {self.game.base.x} {self.game.base.y}'

    @property
    def is_finished(self):
        return False


class GoToPoint(TaskBase):
    def __init__(self, game, buster, target):
        TaskBase.__init__(self, game, buster)
        self.target = target

    def step(self):
        return f'MOVE {self.target.x} {self.target.y}'

    @property
    def is_finished(self):
        return (self.buster.x, self.buster.y) == (self.target.x, self.target.y)


class Wait(TaskBase):
    def __init__(self, game, buster, delay):
        TaskBase.__init__(self, game, buster)
        self.delay = delay

    def step(self):
        self.delay -= 1
        return f'MOVE {self.buster.x} {self.buster.y}'

    @property
    def is_finished(self):
        return self.delay == 0


class PushLine(TaskBase):
    move_line: Line
    push_line: Line
    buster: Buster
    game: Game

    def __init__(self, game, buster, move_line, push_line):
        TaskBase.__init__(self, game, buster)
        self.move_line, self.push_line = move_line, push_line

    @staticmethod
    def forecast(ghosts, points):
        for point in points:
            for ghost in ghosts:
                if point.distance(ghost) <= DISTANCE_SEE:
                    ghost.move_backward(point, GHOST_STEP)

    def step(self):
        ghosts = copy.deepcopy(list(self.game.ghosts.values()))
        orth1 = self.move_line.get_orthogonal(self.buster)
        orth2 = self.move_line.get_orthogonal(copy.deepcopy(self.buster).move_toward(self.move_line.b, 801)) # TODO
        ghosts = [g for g in ghosts
                  if g.is_visible and self.move_line.is_point_between(g, self.push_line)
                  and orth2.is_point_between(g, orth1)]
        for ghost in ghosts:
            if ghost.danger_point is not None and ghost.busters_cnt == 0:
                ghost.move_backward(ghost.danger_point, GHOST_STEP)
        forecast_ghosts = copy.deepcopy(ghosts)
        points = [copy.deepcopy(self.buster).move_toward(self.move_line.b, 800*i) for i in range(1, 5)]
        PushLine.forecast(forecast_ghosts, points)
        bad_ids = set([g.id for g in forecast_ghosts if not self.move_line.is_point_behind(g, self.push_line)])
        if any(bad_ids):
            closest_point, min_distance = None, np.inf
            for ghost in ghosts:
                prj = self.move_line.project(ghost)
                if ghost.id in bad_ids and self.buster.distance(prj) < min_distance:
                    closest_point, min_distance = prj, self.buster.distance(prj)
            return f'MOVE {closest_point.x} {closest_point.y}'
        return f'MOVE {self.move_line.b.x} {self.move_line.b.y}'

    @property
    def is_finished(self):
        return (self.buster.x, self.buster.y) == (self.move_line.b.x, self.move_line.b.y)


class CombinedTask(TaskBase):
    def __init__(self, game, buster, tasks):
        TaskBase.__init__(self, game, buster)
        self.tasks = tasks
        self.task_index = 0

    def step(self):
        if self.tasks[self.task_index].is_finished:
            self.task_index += 1
        return self.tasks[self.task_index].step()

    @property
    def is_finished(self):
        return self.task_index >= len(self.tasks)


class Mind:
    def __init__(self, game):
        self.game = game
        self.tasks = [
            CombinedTask(game, game.busters[0], [
                GoToPoint(game, game.busters[0], Point(0, 4400)),
                PushLine(game, game.busters[0], Line(Point(0, 4400), Point(16000, 4400)), Line(Point(0, 2200), Point(16000, 2200))),
                GoToPoint(game, game.busters[0], Point(16000, 2200)),
                PushLine(game, game.busters[0], Line(Point(16000, 2200), Point(0, 2200)), Line(Point(16000, 1), Point(0, 1))),
                Wait(game, game.busters[0], 100)
            ]),
            CombinedTask(game, game.busters[1], [
                GoToPoint(game, game.busters[1], Point(6600, 4400)),
                PushLine(game, game.busters[1], Line(Point(6600, 4400), Point(6600, 9000)), Line(Point(4400, 4400), Point(4400, 9000))),
                GoToPoint(game, game.busters[1], Point(4400, 9000)),
                PushLine(game, game.busters[1], Line(Point(4400, 9000), Point(4400, 4400)), Line(Point(2200, 9000), Point(2200, 4400))),
                GoToPoint(game, game.busters[1], Point(2200, 4400)),
                PushLine(game, game.busters[1], Line(Point(2200, 4400), Point(2200, 9000)), Line(Point(1, 4400), Point(1, 9000))),
                Wait(game, game.busters[1], 100)
            ]),
        ]

    def step(self):
        return '\n'.join([t.step() for t in self.tasks])


def go_to_base(game):
    res = ''
    for _ in game.my_ids:
        res += f'MOVE {game.base.x} {game.base.y}\n'
    return res[:-1]


