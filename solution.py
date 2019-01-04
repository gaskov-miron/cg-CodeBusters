import math
import sys
import itertools
import pickle
import codecs


def fight(my_busters, enemy_ids):
    a = []
    b = {-1: False}
    for i in my_busters:
        can_stun = [-1]
        for j in enemy_ids:
            if g.enemy_busters[j].is_visible and g.enemy_busters[j].state != 2:
                if distance(g.my_busters[i], g.enemy_busters[j]) <= 1760 and g.my_busters[i].reload == 0:
                    can_stun += [j]
                    if j not in b:
                        if g.enemy_busters[j].state == 1:
                            b[j] = True
                        else:
                            b[j] = False
        a.append(can_stun)
    return a, b


def attack(a, b, ids, delta):
    lis = [i for i in itertools.product(*a) if len(set(i)) + ''.join(map(str, i)).count('-1') - 1 == len(i)]
    best_var = lis[0]
    for i in lis:
        num_carry_1 = 0
        num_carry_2 = 0
        for j in i:
            num_carry_1 += b[j]
        for g in best_var:
            num_carry_2 += b[g]
        if num_carry_1 > num_carry_2:
            best_var = i[:]
        elif num_carry_1 == num_carry_2:
            st_1 = ''.join(map(str, i))
            st_2 = ''.join(map(str, best_var))
            if st_1.count('-1') < st_2.count('-1'):
                best_var = i[:]

    dic = {i: best_var[i - delta] for i in ids if best_var[i - delta] != -1}
    return dic


def distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def squared_distance(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


class Base:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def can_release(self, buster):
        return distance(self, buster) <= 1600


class Buster:
    def __init__(self, buster_id, x, y):
        self.id = buster_id
        self.x = x
        self.y = y
        self.is_visible = False
        self.reload = 0
        # 0: idle or moving buster.
        # 1: buster carrying a ghost.
        # 2: stunned buster.
        self.state = 0
        self.carry_ghost_id = None
        self.turns_to_stay = 0

    def entities_in_range(self, enties, min_dist, max_dist):
        result = []
        for i in enties:
            if i.is_visible:
                dist = distance(i, self)
                if min_dist <= dist <= max_dist:
                    result.append(i)
        return result

    def update(self, x, y, state, value):

        self.is_visible = True
        self.x = x
        self.y = y
        self.state = state
        self.reload -= 1 * (self.reload > 0)
        if state == 2:
            self.carry_ghost_id = None
            self.turns_to_stay = value
        elif state == 1:
            self.carry_ghost_id = value
            self.turns_to_stay = 0
        else:
            self.carry_ghost_id = None
            self.turns_to_stay = 0

    def update_invisible(self):
        self.x = None
        self.y = None
        self.state = 0
        self.carry_ghost_id = None
        self.turns_to_stay = 0


class Ghost:

    def __init__(self, ghost_id, x, y):
        self.found = False
        self.id = ghost_id
        self.x = x
        self.y = y
        self.is_visible = False

    def update(self, x, y, state, value):
        self.found = True
        self.x = x
        self.y = y
        self.is_visible = True

    def update_invisible(self, my_busters, enemy_busters):
        for i in list(my_busters.values()) + list(enemy_busters.values()):
            if i.carry_ghost_id == self.id:
                self.x = None
                self.y = None
                break
        for i in list(my_busters.values()):
            if (self.x != None and self.y != None) and distance(i, self) <= 1760:
                self.x = None
                self.y = None
                break


class Game:
    def fill_busters(dic, ids):
        for i in ids:
            dic[i] = Buster(i, None, None)

    def __init__(self, init_lines):
        busters_cnt, ghosts_cnt, my_id = init_lines.split('\n')
        self.points_to_see = [[(0, 4500), (0, 9000), (8000, 9000), (4000, 9000), (8000, 0), (4000, 0)],
                              [(16000, 0), (16000, 4500), (8000, 0), (12000, 0), (12000, 9000), (8000, 9000)]]
        self.my_id = int(my_id)
        self.points_to_see = self.points_to_see[self.my_id][:]
        self.busters_cnt = int(busters_cnt)
        self.ghosts_cnt = int(ghosts_cnt)
        self.enemy_id = int(self.my_id == 0)
        self.base = Base(16000 * self.my_id, 9000 * self.my_id)
        self.enemy_base = Base(16000 * (self.my_id == 0), 9000 * (self.my_id == 0))
        self.my_busters = {}
        self.enemy_busters = {}
        self.ghosts = {}
        self.entities = {self.my_id: self.my_busters, self.enemy_id: self.enemy_busters, -1: self.ghosts}
        self.my_ids = list(range(self.busters_cnt * self.my_id, self.busters_cnt * (self.my_id + 1)))
        self.enemy_ids = list(range(self.busters_cnt * self.enemy_id, self.busters_cnt * (self.enemy_id + 1)))
        self.visited_points = []
        Game.fill_busters(self.my_busters, self.my_ids)
        Game.fill_busters(self.enemy_busters, self.enemy_ids)
        for i in range(self.ghosts_cnt):
            self.ghosts[i] = Ghost(i, None, None)
        self.ghosts[0].update(8000, 4500, 0, 0)

    def update(self, lines):
        for i in list(self.enemy_busters.values()) + list(self.ghosts.values()):
            i.is_visible = False
        found_ghosts = []
        for l in lines.split('\n'):
            _id, x, y, _type, state, value = list(map(int, l.split()))
            if _type == self.my_id:
                self.visited_points.append((x, y))
                new_points = []
                for point in self.points_to_see[:]:
                    if squared_distance(point, (x, y)) > 1760 ** 2:
                        new_points.append(point)
                self.points_to_see = new_points[:]
            if _type == -1 and not self.ghosts[_id].found:
                found_ghosts.append(_id)
            self.entities[_type][_id].update(x, y, state, value)
            if _type != -1 and state == 1:
                self.ghosts[value].found = True

        self.apply_symmetry(found_ghosts)
        for i in self.enemy_busters.values():
            if not i.is_visible:
                i.update_invisible()
        for i in self.ghosts.values():
            if not i.is_visible:
                i.update_invisible(self.my_busters, self.enemy_busters)

    def apply_symmetry(self, found_ghosts):
        for _id in found_ghosts:
            if _id % 2 == 0:
                op_id = _id - 1
            else:
                op_id = _id + 1
            if not self.ghosts[op_id].found:
                gh = True
                op_x = self.enemy_base.x + (self.base.x - self.ghosts[_id].x)
                op_y = self.enemy_base.y + (self.base.y - self.ghosts[_id].y)
                for x_y in self.visited_points:
                    if squared_distance(x_y, (op_x, op_y)) < 1760 ** 2:
                        gh = False
                        break
                if gh:
                    self.ghosts[op_id].x = op_x
                    self.ghosts[op_id].y = op_y
                    self.ghosts[op_id].found = True


def init(init_lines):
    global g
    g = Game(init_lines)


def step(update_lines):
    global g
    res = ''
    g.update(update_lines)
    a, b = fight(g.my_busters, g.enemy_ids)
    attacks = attack(a, b, g.my_ids, g.busters_cnt * g.my_id)
    for i in g.my_ids:
        buster = g.my_busters[i]
        if i in attacks:
            res += 'STUN' + ' ' + str(attacks[i]) + '\n'
            g.my_busters[i].reload = 20
            continue
        if buster.state == 1 and g.base.can_release(buster):
            res += 'RELEASE' + '\n'
            continue
        if buster.state == 1:
            res += 'MOVE' + ' ' + str(g.base.x) + ' ' + str(g.base.y) + '\n'
            continue
        can_catch_ghosts = buster.entities_in_range(g.ghosts.values(), 900, 1760)
        if len(can_catch_ghosts) != 0:
            res += 'BUST' + ' ' + str(can_catch_ghosts[0].id) + '\n'
            continue
        close_ghosts = buster.entities_in_range(g.ghosts.values(), 0, 900)
        if len(close_ghosts) != 0:
            res += 'MOVE' + ' ' + str(buster.x) + ' ' + str(buster.y) + '\n'
            continue
        if len(g.ghosts) != 0:
            m_dist = math.sqrt(16000 ** 2 + 9000 ** 2)
            min_i = -1
            for h in g.ghosts:
                if g.ghosts[h].x != None and g.ghosts[h].y != None:
                    if m_dist > distance(g.ghosts[h], buster):
                        m_dist = distance(g.ghosts[h], buster)
                        min_i = h
            if min_i != -1:
                res += 'MOVE' + ' ' + str(g.ghosts[min_i].x) + ' ' + str(g.ghosts[min_i].y) + '\n'  #
                continue
        if len(g.points_to_see) != 0:
            nearest_point = g.points_to_see[0]
            min_distance = squared_distance(nearest_point, (g.my_busters[i].x, g.my_busters[i].y))
            for point in g.points_to_see:
                _distance = squared_distance(point, (g.my_busters[i].x, g.my_busters[i].y))
                if _distance < min_distance:
                    nearest_point = point
                    min_distance = _distance
            res += 'MOVE' + ' ' + ' '.join(map(str, nearest_point)) + '\n'
        else:
            res += 'MOVE' + ' ' + str(g.enemy_base.x - 2000 * (g.my_id == 0) + 2000 * g.my_id) + ' ' + str(
                g.enemy_base.y - 2200 * (g.my_id == 0) + 2200 * g.my_id) + '\n'
    return res[:-1]


if __name__ == '__main__':
    init_line = input() + '\n' + input() + '\n' + input()
    init(init_line)
    print(init_line + '\n---', file=sys.stderr)
    while True:
        entities = int(input())
        update = '\n'.join([' '.join([j for j in input().split()]) for i in range(entities)])
        print(update + '\n---', file=sys.stderr)
        out = step(update)
        print(out, file=sys.stderr)
        print(out)
