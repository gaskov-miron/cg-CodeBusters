from solution import Game, Point, Buster, GHOST_STEP, DISTANCE_SEE
import copy
import numpy as np
import itertools


class Line:
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.d = np.array([self.a.x, self.a.y])
        self.v = np.array([self.b.x, self.b.y]) - self.d
        self.bt = np.array([self.v[1], self.v[0]])

    def project(self, point: Point) -> Point:
        x = np.array([point.x, point.y]) - self.d
        prj = (self.v@x)/(self.v@self.v)*self.v + self.d
        return Point(prj[0], prj[1])

    def dist(self, point: Point):
        x = np.array([point.x, point.y]) - self.d
        return (self.bt@x)/np.sqrt(self.bt@self.bt)

    def is_point_between(self, point: Point, another_line: 'Line') -> bool:
        sd = self.dist(point)
        ad = another_line.dist(point)
        return sd != 0 and (ad == 0 or np.sign(sd) != np.sign(ad))

    def is_point_behind(self, point: Point, another_line: 'Line') -> bool:
        return not self.is_point_between(point, another_line) and \
               np.abs(self.dist(point)) > np.abs(another_line.dist(point))


class TaskBase:
    buster: Buster

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


class PushLineToBase(TaskBase):
    def __init__(self, game, buster):
        TaskBase.__init__(self, game, buster)

    def step(self):
        ghosts = copy.deepcopy(list(self.game.ghosts.values()))
        ghosts = [g for g in ghosts if g.is_visible and g.busters_cnt == 0]
        for ghost in ghosts:
            if ghost.danger_point is not None and ghost.busters_cnt == 0:
                ghost.move_backward(ghost.danger_point, GHOST_STEP)
        ghosts = [g for g in ghosts if
                  (g.x, g.y) != (self.game.base.x, self.game.base.y)
                  and min(self.buster.x, self.game.base.x) <= g.x <= max(self.buster.x, self.game.base.x)
                  and min(self.buster.y, self.game.base.y) <= g.y <= max(self.buster.y, self.game.base.y)]
        if len(ghosts) > 0:
            nearest_ghost = self.buster.find_all_nearest(ghosts)[0]
            p = Point(self.buster.x, self.buster.y)
            p.move_toward(nearest_ghost, np.sqrt(self.buster.distance(nearest_ghost))-1)
        else:
            p = self.game.base
        return f'MOVE {p.x} {p.y}'

    @property
    def is_finished(self):
        return (self.buster.x, self.buster.y) == (self.game.base.x, self.game.base.y)


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
        next_buster = copy.deepcopy(self.buster).move_toward(self.move_line.b, 800)
        ghosts = [g for g in ghosts
                  if g.is_visible and self.move_line.is_point_between(g, self.push_line)
                  and min(self.buster.x, next_buster.x) <= self.move_line.project(g).x <= max(self.buster.x, next_buster.x)
                  and min(self.buster.y, next_buster.y) <= self.move_line.project(g).y <= max(self.buster.y, next_buster.y)]
        for ghost in ghosts:
            if ghost.danger_point is not None and ghost.busters_cnt == 0:
                ghost.move_backward(ghost.danger_point, GHOST_STEP)
        forecast_ghosts = copy.deepcopy(ghosts)
        points = []
        for i in range(1, 5):
            s = copy.deepcopy(self.buster).move_toward(self.move_line.b, 800 * i)
            points.append(s)
            if (s.x, s.y) == (self.move_line.b.x, self.move_line.b.y):
                break
        PushLine.forecast(forecast_ghosts, points)
        bad_ids = set([g.id for g in forecast_ghosts if not self.move_line.is_point_behind(g, self.push_line)])
        if len(bad_ids) > 0:
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
    def __init__(self, game, buster):
        TaskBase.__init__(self, game, buster)
        self.tasks = []
        self.task_index = 0
        self.x, self.y = buster.x, buster.y

    def step(self):
        if self.tasks[self.task_index].is_finished:
            self.task_index += 1
        return self.tasks[self.task_index].step()

    @property
    def is_finished(self):
        return self.task_index >= len(self.tasks)

    def go_to_point(self, x, y):
        self.x, self.y = x, y
        self.tasks.append(GoToPoint(self.game, self.buster, Point(x, y)))
        return self

    def push_line_to_base(self):
        self.x, self.y = self.game.base.x, self.game.base.y
        self.tasks.append(PushLineToBase(self.game, self.buster))
        return self

    def push_v_line(self, y, px):
        self.tasks.append(
            PushLine(self.game, self.buster,
                     Line(Point(self.x, self.y), Point(self.x, y)),
                     Line(Point(px, self.y), Point(px, y))))
        self.y = y
        return self

    def push_h_line(self, x, py):
        self.tasks.append(
            PushLine(self.game, self.buster,
                     Line(Point(self.x, self.y), Point(x, self.y)),
                     Line(Point(self.x, py), Point(x, py))))
        self.x = x
        return self

    def wait(self, steps):
        self.tasks.append(Wait(self.game, self.buster, steps))
        return self


class Mind:
    def __init__(self, game):
        self.game = game
        if self.game.busters_cnt == 2:
            self.tasks = [
                CombinedTask(game, game.busters[0])
                    .go_to_point(0, 2200)
                    .push_h_line(6000, 4400)
                    .push_h_line(16000, 1)
                    .go_to_point(16000, 0)
                    .push_line_to_base()
                    .go_to_point(16000, 9000)
                    .wait(1000),
                CombinedTask(game, game.busters[1])
                    .go_to_point(6000, 2200)
                    .push_v_line(9000, 3800)
                    .go_to_point(4000, 9000)
                    .push_v_line(2800, 1800)
                    .go_to_point(2000, 2800)
                    .push_v_line(9000, 1)
                    .go_to_point(0, 9000)
                    .push_line_to_base()
                    .go_to_point(16000, 9000)
                    .wait(1000)]
        if self.game.busters_cnt == 3:
            self.tasks = [
                CombinedTask(game, game.busters[0])
                    .go_to_point(2200, 2200)
                    .push_h_line(16000, 1)
                    .go_to_point(16000, 0)
                    .push_line_to_base()
                    .go_to_point(16000, 9000)
                    .wait(1000),
                CombinedTask(game, game.busters[1])
                    .go_to_point(0, 2200)
                    .go_to_point(8200, 4400)
                    .go_to_point(6000, 2200)
                    .push_v_line(9000, 3800)
                    .go_to_point(4000, 9000)
                    .push_v_line(2800, 1800)
                    .go_to_point(2000, 2800)
                    .push_v_line(9000, 1)
                    .go_to_point(0, 9000)
                    .push_line_to_base()
                    .go_to_point(16000, 9000)
                    .wait(1000),
                CombinedTask(game, game.busters[2])
                    .go_to_point(8200, 2200)
                    .push_v_line(9000, 6000)
                    .wait(1000)]
        if self.game.busters_cnt == 4:
            self.tasks = [
                CombinedTask(game, game.busters[0])
                    .go_to_point(2200, 2200)
                    .push_h_line(16000, 1)
                    .go_to_point(16000, 0)
                    .push_line_to_base()
                    .go_to_point(16000, 9000)
                    .wait(1000),
                CombinedTask(game, game.busters[1])
                    .go_to_point(0, 2200)
                    .go_to_point(8200, 4400)
                    .go_to_point(6000, 2200)
                    .push_v_line(9000, 3800)
                    .go_to_point(4000, 9000)
                    .push_v_line(2800, 1800)
                    .go_to_point(2000, 2800)
                    .push_v_line(9000, 1)
                    .go_to_point(0, 9000)
                    .push_line_to_base()
                    .go_to_point(16000, 9000)
                    .wait(1000),
                CombinedTask(game, game.busters[2])
                    .go_to_point(8200, 2200)
                    .push_v_line(9000, 6000)
                    .wait(1000),
                CombinedTask(game, game.busters[3])
                    .go_to_point(4400, 4400)
                    .go_to_point(16000, 2200)
                    .go_to_point(16000, 0)
                    .push_line_to_base()
                    .go_to_point(16000, 9000)
                    .wait(1000)]

    def fight(self):
        my_busters, enemy_busters = self.game.my_busters, self.game.enemy_busters
        targets = []
        best_var, best_score = None, None
        for i in sorted(my_busters):
            targets.append([-1] + [j for j in enemy_busters if my_busters[i].can_stun(enemy_busters[j])])
        for i in itertools.product(*targets):
            stunned_enemies_ids = [j for j in i if j != -1]
            if len(set(stunned_enemies_ids)) != len(stunned_enemies_ids):
                continue
            stunned_enemies_cnt = len(stunned_enemies_ids)
            released_ghosts_cnt = sum([enemy_busters[j].is_carrying() for j in stunned_enemies_ids])
            if (best_var is None) or (released_ghosts_cnt, stunned_enemies_cnt) > best_score:
                best_var = i
                best_score = (released_ghosts_cnt, stunned_enemies_cnt)
        dic = {i: best_var[j] for j, i in enumerate(sorted(my_busters))
               if best_var[j] != -1}
        return dic

    def step(self):
        result = []
        attack = self.fight()
        for task in self.tasks:
            if task.buster.id in attack:
                result.append(f'STUN {attack[task.buster.id]}')
                task.buster.reload = 20
            else:
                result.append(task.step())
        return '\n'.join(result)


def go_to_base(game):
    res = ''
    for _ in game.my_ids:
        res += f'MOVE {game.base.x} {game.base.y}\n'
    return res[:-1]
