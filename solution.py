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
STATE_TRAPPING = 3

GHOST_STEP = 400
BUSTER_STEP = 800

META_R = 7000

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
    to_eject = []
    for i in sorted(my_busters):
        if my_busters[i].is_carrying():
            if len(my_busters[i].killers) > 0:
                to_eject.append(i)
            targets.append([-1])
        else:
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
    for i in to_eject:
        dic[i] = -1
    return dic


def find_targets(my_busters, ghosts, my_base, enemy_base):
    ghosts = {i.id: i for i in ghosts.values() if i.is_filled()}
    targets = []
    best_var, best_score = None, None
    busters_ids = list(sorted(my_busters))
    buster_ghost = {}
    for i in busters_ids:
        buster = my_busters[i]
        buster_targets = [-1]
        targets.append(buster_targets)
        if buster.is_carrying() or len(buster.killers) > 0:
            continue
        for ghost in ghosts.values():
            steps = buster.turns_to_stay + buster.turns_to_bust(ghost)
            if ghost.stamina <= 3 and ghost.time_to_live > steps:
                buster_ghost[(i, ghost.id)] = steps
                buster_targets.append(ghost.id)

    for i in itertools.product(*targets):
        bonus, loss = 0, 0
        ghost_busters_cnt = {}
        for k in range(len(i)):
            if i[k] == -1:
                continue
            loss += buster_ghost[(busters_ids[k], i[k])]
            if i[k] not in ghost_busters_cnt:
                ghost_busters_cnt[i[k]] = 0
            ghost_busters_cnt[i[k]] += 1
        for ghost_id in ghost_busters_cnt:
            ghost = ghosts[ghost_id]
            if ghost.enemy_busters_cnt >= ghost_busters_cnt[ghost_id]:
                continue
            bonus += 1 + ghost.enemy_busters_cnt
        if best_var is None or (bonus, -loss) > best_score:
            best_score = (bonus, -loss)
            best_var = i
    dic = {}
    for k in range(len(best_var)):
        if best_var[k] == -1:
            continue
        dic[busters_ids[k]] = best_var[k]
    return dic


class Point:
    def __init__(self, x, y):
        if x is not None:
            x = int(round(x))
        if y is not None:
            y = int(round(y))
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
        return self

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
        self.bust_ghost_id = None
        self.base = None
        self.killers = []

    def turns_to_bust(self, entity):
        if not entity.is_filled():
            return None
        if self.distance(entity) < DISTANCE_BUST:
            return 0
        return np.ceil((np.sqrt(self.distance(entity)) - np.sqrt(DISTANCE_BUST)) / BUSTER_STEP)

    def can_stun(self, buster):
        return not self.is_stunned() and self.is_visible and \
               buster.is_visible and not buster.is_stunned() and \
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
        if self.state == STATE_TRAPPING:
            self.bust_ghost_id = value
        else:
            self.bust_ghost_id = None
        self.reload -= 1 * (self.reload > 0)
        if self.is_stunned():
            self.carry_ghost_id = None
            self.turns_to_stay = value
            if self.turns_to_stay == 10 and len(self.killers) == 1:
                self.killers[0].reload = 20

        elif self.is_carrying():
            self.carry_ghost_id = value
            self.turns_to_stay = 0
        else:
            self.carry_ghost_id = None
            self.turns_to_stay = 0

    def update_invisible(self, busters):
        self.turns_to_stay -= 1 * (self.turns_to_stay > 0)
        self.reload -= 1 * (self.reload > 0)
        if self.is_carrying():
            if not self.base.can_release(self):
                self.move_toward(self.base, BUSTER_STEP)
            for i in busters:
                if i.is_mine and self.distance(i) <= DISTANCE_SEE:
                    self.x, self.y = None, None
                    self.state = STATE_IDLE
                    self.carry_ghost_id = None
                    break
        elif self.turns_to_stay == 0:
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
        self.busters_cnt = 0
        self.my_busters_cnt = 0

    @property
    def enemy_busters_cnt(self):
        return self.busters_cnt - self.my_busters_cnt

    @property
    def time_to_live(self):
        if self.enemy_busters_cnt == self.my_busters_cnt:
            return np.inf
        return self.stamina / self.busters_cnt

    def update(self, x, y, state, value):
        self.is_found = True
        self.x = x
        self.y = y
        self.is_visible = True
        self.stamina = state
        self.busters_cnt = value

    def update_invisible(self, busters):
        if not self.is_filled():
            return
        self.busters_cnt -= self.my_busters_cnt
        self.my_busters_cnt = 0
        self.stamina -= self.busters_cnt
        if self.stamina <= 0 and self.busters_cnt > 0:
            self.stamina, self.x, self.y = 0, None, None
            return
        if self.danger_point is not None and self.busters_cnt == 0:
            self.move_backward(self.danger_point, GHOST_STEP)
            self.danger_point = None
        for i in busters:
            if i.carry_ghost_id == self.id or i.is_mine and self.distance(i) <= DISTANCE_SEE:
                self.x, self.y = None, None
                break

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
        for b in self.my_busters.values():
            b.base = self.base
        self.enemy_busters = Game.fill_objects_dic(Buster, self.enemy_ids)
        for b in self.enemy_busters.values():
            b.base = self.enemy_base
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
                i.update_invisible(self.busters)

        for i in self.ghosts.values():
            if not i.is_visible:
                i.update_invisible(self.busters)
            if self.step > 1 and i.is_filled():
                i.update_danger_point(self.busters)

        for i in self.ghosts.values():
            if i.is_visible:
                i.my_busters_cnt = 0
                for b in self.my_busters.values():
                    if b.bust_ghost_id == i.id:
                        i.my_busters_cnt += 1
        for b in self.my_busters.values():
            b.killers = [e for e in self.enemy_busters.values() if e.can_stun(b)]

    def apply_symmetry(self, found_ghosts):
        for _id in found_ghosts:
            ghost = self.ghosts[_id]
            op_id = _id + (-1, 1)[_id % 2]
            if not self.ghosts[op_id].is_found:
                op_x, op_y = ghost.symmetry()
                op_point = Point(op_x, op_y)
                position_was_seen = any([p.distance(op_point) < DISTANCE_SEE
                                         for p in self.visited_points])
                if not position_was_seen and \
                        not(self.base.distance(ghost) < META_R ** 2 and ghost.stamina <= 3):
                    self.ghosts[op_id].x = op_x
                    self.ghosts[op_id].y = op_y
                    self.ghosts[op_id].is_found = True
                    self.ghosts[op_id].stamina = ghost.stamina


def init(init_lines):
    return Game(init_lines)


def step_old(g):
    res = ''
    attacks = fight(g.my_busters, g.enemy_busters)
    for i in g.my_ids:
        buster = g.my_busters[i]
        if i in attacks:
            res += f'STUN {attacks[i]}\n'
            g.my_busters[i].reload = 20
            continue
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


def step(g):
    res = ''
    attacks = fight(g.my_busters, g.enemy_busters)
    targets = find_targets(g.my_busters, g.ghosts, g.base, g.enemy_base)
    for i in g.my_ids:
        buster = g.my_busters[i]
        if i in attacks:
            if attacks[i] == -1:
                res += f'EJECT {g.base.x} {g.base.y}\n'
            else:
                res += f'STUN {attacks[i]}\n'
                g.my_busters[i].reload = 20
            continue
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
        list_of_targets = g.ghosts.values()
        if i in targets:
            list_of_targets = [g.ghosts[targets[i]]]

        best_target, min_steps = None, None
        for ghost in list_of_targets:
            if not ghost.is_filled():
                continue
            steps = buster.turns_to_stay + buster.turns_to_bust(ghost) + ghost.stamina
            if best_target is None or steps < min_steps:
                best_target, min_steps = ghost, steps
        if best_target is None:
            if len(g.points_to_see) != 0:
                nearest_points = buster.find_all_nearest(g.points_to_see)
                res += f'MOVE {nearest_points[0].x} {nearest_points[0].y}\n'
            else:
                res += f'MOVE {g.enemy_base.x - 2000 * (g.my_id == 0) + 2000 * g.my_id} {g.enemy_base.y - 2200 * (g.my_id == 0) + 2200 * g.my_id}\n'
            continue
        if buster.distance(best_target) > DISTANCE_BUST:
            res += f'MOVE {best_target.x} {best_target.y}\n'
            continue
        if DISTANCE_BUST_MIN <= buster.distance(best_target) <= DISTANCE_BUST:
            res += f'BUST {best_target.id}\n'
            continue
        if buster.distance(best_target) < DISTANCE_BUST_MIN and best_target.danger_point is None:
            res += f'MOVE {g.base.x} {g.base.y}\n'
            continue
        res += f'MOVE {buster.x} {buster.y}\n'
    return res[:-1]


def get_research_direction(my_id, step_id, buster_id, busters_cnt):
    if my_id == 0:
        return RESEARCH_DIRECTIONS[4-busters_cnt][buster_id][step_id - 1][0] * 1000, \
               RESEARCH_DIRECTIONS[4-busters_cnt][buster_id][step_id - 1][1] * 1000
    else:
        return -RESEARCH_DIRECTIONS[4-busters_cnt][buster_id - busters_cnt][step_id - 1][0] * 1000, \
               -RESEARCH_DIRECTIONS[4-busters_cnt][buster_id - busters_cnt][step_id - 1][1] * 1000


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