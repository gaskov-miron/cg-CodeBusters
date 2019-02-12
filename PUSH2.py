from solution import Point, GHOST_STEP, DISTANCE_SEE
import copy
import numpy as np


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
        ghosts = [g for g in ghosts
                  if g.is_visible and self.push_line <= g.y < self.move_line
                  and self.buster.x <= g.x <= self.buster.x + 800]
        for ghost in ghosts:
            if ghost.danger_point is not None and ghost.busters_cnt == 0:
                ghost.move_backward(ghost.danger_point, GHOST_STEP)
        forecast_ghosts = copy.deepcopy(ghosts)
        points = [Point(self.buster.x + 800*i, self.buster.y) for i in range(1, 5)]
        PushLine.forecast(forecast_ghosts, points)
        bad_ids = set([g.id for g in forecast_ghosts if g.y > self.push_line])
        if any(bad_ids):
            min_x = np.inf
            for ghost in ghosts:
                if ghost.id in bad_ids and ghost.x < min_x:
                    min_x = ghost.x
            return f'MOVE {min_x} {self.move_line}'
        return f'MOVE {16000} {self.move_line}'

    @property
    def is_finished(self):
        return self.buster.x == 16000


class Push(TaskBase):
    def __init__(self, game, buster, move_line, push_line, delay=0):
        TaskBase.__init__(self, game, buster)
        self.move_line, self.push_line = move_line, push_line
        self.tasks = [GoToPoint(game, buster, Point(0, move_line)), PushLine(game, buster, move_line, push_line),
                      Wait(game, buster, 1000)]
        if delay > 0:
            self.tasks = [Wait(game, buster, delay)] + self.tasks
        self.task_index = 0

    def step(self):
        if self.tasks[self.task_index].is_finished:
            self.task_index += 1
        return self.tasks[self.task_index].step()


class Mind:
    def __init__(self, game):
        self.game = game
        self.tasks = [Push(game, game.busters[0], 4400, 2200),
                      Push(game, game.busters[1], 2200, 1, 10)]

    def step(self):
        return '\n'.join([t.step() for t in self.tasks])


def go_to_base(game):
    res = ''
    for _ in game.my_ids:
        res += f'MOVE {game.base.x} {game.base.y}\n'
    return res[:-1]


