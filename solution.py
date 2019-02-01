import sys
import itertools
import numpy as np


MAX_X = 16000
MAX_Y = 9000

DISTANCE_RELEASE = 1600 ** 2
DISTANCE_SEE = 2200 ** 2
DISTANCE_STUN = 1760 ** 2
DISTANCE_BUST = 1760 ** 2
DISTANCE_BUST_MIN = 900 ** 2

STATE_IDLE = 0
STATE_CARRYING = 1
STATE_STUNNED = 2

GHOST_STEP = 400

RESEARCH_DIRECTIONS = [[[(1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)],
                        [(3, 1), (3, 1), (3, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)],
                        [(2, 1), (3, 2), (1, 2), (0, 1), (0, 1), (0, 1), (0, 1), (1, 1), (1, 1)],
                        [(1, 2), (2, 1), (1, 2), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, -1)]],
                       [[(4, 3), (4, 3), (5, 4), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)],
                        [(1, 2), (1, 2), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0)],
                        [(2, 1), (2, 1), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1), (1, 1), (1, 0)]],
                       [[(1, 1), (3, 4), (0, 1), (0, 1), (0, 1), (0, 1), (3, 2), (1, 0), (1, -1)],
                        [(1, 1), (4, 3), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0), (1, 0)]]]


def fight(my_busters, enemy_busters):
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


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def is_filled(self):
        return self.x is not None and self.y is not None

    def find_all_nearest(self, targets):
        filled_targets = [i for i in targets if i.is_filled()]
        if len(filled_targets) == 0:
            return None
        min_distance = min([self.distance(i) for i in filled_targets])
        return [i for i in filled_targets if self.distance(i) == min_distance]

    def distance(self, b):
        return (self.x - b.x) ** 2 + (self.y - b.y) ** 2

    def symmetry(self):
        return MAX_X - self.x, MAX_Y - self.y

    def move_toward(self, point, distance):
        target = np.array([point.x, point.y])
        current = np.array([self.x, self.y])
        direction = target - current
        direction_norm = direction / np.sqrt(direction @ direction)
        new_point = np.round(current + direction_norm * distance)
        x = max(0, min(new_point[0], MAX_X))
        y = max(0, min(new_point[1], MAX_Y))
        self.x, self.y = int(x), int(y)

    def move_backward(self, point, distance):
        self.move_toward(Point(2 * self.x - point.x, 2 * self.y - point.y), distance)


class Base(Point):
    def __init__(self, x, y):
        Point.__init__(self, x, y)

    def can_release(self, buster):
        return self.distance(buster) <= DISTANCE_RELEASE


class Buster(Point):
    def __init__(self, buster_id, x, y):
        Point.__init__(self, x, y)
        self.id = buster_id
        self.is_visible = False
        self.reload = 0
        self.state = STATE_IDLE
        self.carry_ghost_id = None
        self.turns_to_stay = 0
        self.is_mine = False

    def can_stun(self, buster):
        return not self.is_stunned() and buster.is_visible and not buster.is_stunned() and \
               self.distance(buster) <= DISTANCE_STUN and self.reload == 0

    def is_carrying(self):
        return self.state == STATE_CARRYING

    def is_stunned(self):
        return self.state == STATE_STUNNED

    def is_idle(self):
        return self.state == STATE_IDLE

    def entities_in_range(self, objects, min_dist, max_dist):
        return [i for i in objects if i.is_filled() and min_dist <= self.distance(i) <= max_dist]

    def update(self, x, y, state, value):
        self.is_visible = True
        self.x = x
        self.y = y
        self.state = state
        self.reload -= 1 * (self.reload > 0)
        if self.is_stunned():
            self.carry_ghost_id = None
            self.turns_to_stay = value
        elif self.is_carrying():
            self.carry_ghost_id = value
            self.turns_to_stay = 0
        else:
            self.carry_ghost_id = None
            self.turns_to_stay = 0

    def update_invisible(self):
        self.turns_to_stay -= 1 * (self.turns_to_stay > 0)
        self.reload -= 1 * (self.reload > 0)
        if self.turns_to_stay == 0:
            self.x = None
            self.y = None
            self.state = STATE_IDLE
            self.carry_ghost_id = None


class Ghost(Point):
    def __init__(self, ghost_id, x, y):
        Point.__init__(self, x, y)
        self.is_found = False
        self.id = ghost_id
        self.is_visible = False
        self.danger_point = None
        self.stamina = None
        self.busters_cnt = None

    def update(self, x, y, state, value):
        self.is_found = True
        self.x = x
        self.y = y
        self.is_visible = True
        self.stamina = state
        self.busters_cnt = value

    def update_invisible(self, busters):
        # update busters_cnt and stamina appropriately
        self.busters_cnt = None
        if not self.is_filled():
            return
        for i in busters:
            if i.carry_ghost_id == self.id or i.is_mine and self.distance(i) <= DISTANCE_BUST: # fix to DISTANCE_SEE
                self.x, self.y = None, None
                break
        if self.is_filled() and self.danger_point is not None:
            self.move_backward(self.danger_point, GHOST_STEP)
            self.danger_point = None

    def update_danger_point(self, busters):
        self.danger_point = None
        nearest_busters = self.find_all_nearest(busters)
        if 0 < self.distance(nearest_busters[0]) <= 2200**2 and len(nearest_busters) == 1:
            self.danger_point = Point(nearest_busters[0].x, nearest_busters[0].y)


class Game:
    @staticmethod
    def fill_objects_dic(object_type, ids):
        return {i: object_type(i, None, None) for i in ids}

    def __init__(self, init_lines):
        busters_cnt, ghosts_cnt, my_id = init_lines.split('\n')
        self.points_to_see = [(0, 4500), (0, 9000), (8000, 9000), (4000, 9000), (8000, 0), (4000, 0)]
        self.points_to_see = [Point(*p) for p in self.points_to_see]
        self.my_id = int(my_id)
        self.enemy_id = int(not self.my_id)
        if self.my_id:
            self.points_to_see = [Point(*i.symmetry()) for i in self.points_to_see]
        self.busters_cnt = int(busters_cnt)
        self.ghosts_cnt = int(ghosts_cnt)
        self.base = Base(MAX_X * self.my_id, MAX_Y * self.my_id)
        self.enemy_base = Base(*self.base.symmetry())
        self.my_ids = list(range(self.busters_cnt * self.my_id, self.busters_cnt * (self.my_id + 1)))
        self.enemy_ids = list(range(self.busters_cnt * self.enemy_id, self.busters_cnt * (self.enemy_id + 1)))
        self.my_busters = Game.fill_objects_dic(Buster, self.my_ids)
        self.enemy_busters = Game.fill_objects_dic(Buster, self.enemy_ids)
        self.ghosts = Game.fill_objects_dic(Ghost, range(self.ghosts_cnt))
        self.entities = {self.my_id: self.my_busters, self.enemy_id: self.enemy_busters, -1: self.ghosts}
        for i in self.my_busters.values():
            i.is_mine = True
        self.busters = list(self.my_busters.values()) + list(self.enemy_busters.values())
        self.visited_points = []
        self.ghosts[0].update(MAX_X//2, MAX_Y//2, 0, 0)
        self.step = 0

    def update(self, lines):
        self.step += 1
        for i in list(self.enemy_busters.values()) + list(self.ghosts.values()):
            i.is_visible = False
        found_ghosts = []
        for l in lines.split('\n'):
            _id, x, y, _type, state, value = list(map(int, l.split()))
            point = Point(x, y)
            if _type == self.my_id:
                self.visited_points.append(point)
                self.points_to_see = [p for p in self.points_to_see
                                      if point.distance(p) > DISTANCE_SEE]
            if _type == -1 and not self.ghosts[_id].is_found:
                found_ghosts.append(_id)
            self.entities[_type][_id].update(x, y, state, value)
            if _type != -1 and state == STATE_CARRYING:
                self.ghosts[value].is_found = True

        self.apply_symmetry(found_ghosts)
        for i in self.enemy_busters.values():
            if not i.is_visible:
                i.update_invisible()
        for i in self.ghosts.values():
            if not i.is_visible:
                i.update_invisible(self.busters)
            elif self.step > 1: # change elif with if
                i.update_danger_point(self.busters)

    def apply_symmetry(self, found_ghosts):
        for _id in found_ghosts:
            op_id = _id + (-1, 1)[_id % 2]
            if not self.ghosts[op_id].is_found:
                op_x, op_y = self.ghosts[_id].symmetry()
                op_point = Point(op_x, op_y)
                position_was_seen = any([p.distance(op_point) < DISTANCE_SEE
                                         for p in self.visited_points])
                if not position_was_seen:
                    self.ghosts[op_id].x = op_x
                    self.ghosts[op_id].y = op_y
                    self.ghosts[op_id].is_found = True


def init(init_lines):
    return Game(init_lines)


def step(g):
    res = ''
    attacks = fight(g.my_busters, g.enemy_busters)
    for i in g.my_ids:
        buster = g.my_busters[i]
        #if i in attacks:
        #    res += f'STUN {attacks[i]}\n'
        #    g.my_busters[i].reload = 20
        #    continue
        if buster.is_carrying() and g.base.can_release(buster):
            res += 'RELEASE\n'
            continue
        if buster.is_carrying():
            res += f'MOVE {g.base.x} {g.base.y}\n'
            continue
        if g.step <= 9:
            dx, dy = get_research_direction(g.my_id, g.step, i, g.busters_cnt)
            res += f'MOVE {g.my_busters[i].x + dx} {g.my_busters[i].y + dy}\n'
            continue
        can_catch_ghosts = buster.entities_in_range(g.ghosts.values(), DISTANCE_BUST_MIN, DISTANCE_BUST)
        if len(can_catch_ghosts) != 0:
            res += f'BUST {can_catch_ghosts[0].id}\n'
            continue
        close_ghosts = buster.entities_in_range(g.ghosts.values(), 0, DISTANCE_BUST_MIN)
        if len(close_ghosts) != 0:
            res += f'MOVE {buster.x} {buster.y}\n'
            continue
        if len(g.ghosts) != 0:
            nearest_ghosts = buster.find_all_nearest(g.ghosts.values())
            if nearest_ghosts is not None:
                res += f'MOVE {nearest_ghosts[0].x} {nearest_ghosts[0].y}\n'
                continue
        if len(g.points_to_see) != 0:
            nearest_points = buster.find_all_nearest(g.points_to_see)
            res += f'MOVE {nearest_points[0].x} {nearest_points[0].y}\n'
        else:
            res += f'MOVE {g.enemy_base.x - 2000 * (g.my_id == 0) + 2000 * g.my_id} {g.enemy_base.y - 2200 * (g.my_id == 0) + 2200 * g.my_id}\n'
    return res[:-1]


def get_research_direction(my_id, step_id, buster_id, busters_cnt):
    if my_id == 0:
        return RESEARCH_DIRECTIONS[4-busters_cnt][buster_id][step_id - 1][0] * 1000, \
               RESEARCH_DIRECTIONS[4-busters_cnt][buster_id][step_id - 1][1] * 1000
    else:
        return -RESEARCH_DIRECTIONS[4-busters_cnt][buster_id - busters_cnt][step_id - 1][0] * 1000, \
               -RESEARCH_DIRECTIONS[4-busters_cnt][buster_id - busters_cnt][step_id - 1][1] * 1000


def step_research(g):
    res = ''
    for i in g.my_ids:
        x, y = g.my_busters[i].x, g.my_busters[i].y
        if g.step > 9:
            res += f'MOVE {g.base.x} {g.base.y}\n'
        else:
            dx, dy = get_research_direction(g.my_id, g.step, i, g.busters_cnt)
            res += f'MOVE {x + dx} {y + dy}\n'
    return res[:-1]


if __name__ == '__main__':
    init_line = input() + '\n' + input() + '\n' + input()
    game = init(init_line)
    print('INIT:\n' + init_line, file=sys.stderr)
    while True:
        entities = int(input())
        update = '\n'.join([' '.join([j for j in input().split()]) for i in range(entities)])
        print('INPUT:\n' + update, file=sys.stderr)
        game.update(update)
        out = step(game)
        print('OUTPUT:\n' + out, file=sys.stderr)
        print(out)