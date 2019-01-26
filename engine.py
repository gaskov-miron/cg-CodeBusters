import math
import numpy as np


class Engine:
    def __init__(self, busters_cnt, ghosts_cnt, busters, ghosts):
        self.bust_cnt = busters_cnt
        self.ghosts_cnt = ghosts_cnt
        self.busters = busters
        self.ghosts = ghosts
        self.busters0 = {i: self.busters[i] for i in list(range(busters_cnt))}
        self.busters1 = {i: self.busters[i] for i in list(range(busters_cnt, 2 * busters_cnt))}
        self.players_busters = {0: self.busters0, 1: self.busters1}

    def get_info(self, player_id):
        result = ''
        for i in sorted(self.players_busters[player_id]):
            result += self.busters[i].to_string()

        for i in sorted(self.players_busters[not player_id]):
            if self.players_busters[not player_id][i].is_visible_from(self.players_busters[player_id]):
                result += self.players_busters[not player_id][i].to_string()

        for i in sorted(self.ghosts):
            if self.ghosts[i].is_visible_from(self.players_busters[player_id]):
                result += self.ghosts[i].to_string()
        return result

    def do(self, player0, player1):
        busters_positions = [(self.busters[i].x, self.busters[i].y) for i in self.busters]
        for i in range(len(player0) + len(player1)):
            action = (player0 + player1)[i].split()
            target_x, target_y = int(action[1]), int(action[2])
            self.busters[i].move_to(target_x, target_y, 800)

        for i in self.ghosts:
            if self.ghosts[i].was_seen:
                target_x = self.ghosts[i].x
                target_y = self.ghosts[i].y
                current_x, current_y = target_x, target_y
                min_d = 25000 ** 2
                for g in busters_positions:
                    d = (current_x - g[0]) ** 2 + (current_y - g[1]) ** 2
                    if min_d > d:
                        k = True
                        min_d = d
                        target_x, target_y = current_x + current_x - g[0], current_y + current_y - g[1]
                    elif min_d == d:
                        k = False
                if k and min_d <= 2200 ** 2 and ((current_x - target_x) != 0 or (current_y - target_y) != 0):
                    A = math.sqrt(400 ** 2 / (((target_x - current_x) ** 2) + ((target_y - current_y) ** 2)))
                    x, y = cut(round(current_x + A * (target_x - current_x)),
                               round(current_y + A * (target_y - current_y)))
                    self.ghosts[i].x = x
                    self.ghosts[i].y = y

            self.ghosts[i].was_seen = self.ghosts[i].is_visible_from(self.busters)


class Entity:
    def __init__(self, string):
        id_, x, y, _type, state, value = string.split()
        self.id = int(id_)
        self.x = int(x)
        self.y = int(y)
        self.type = int(_type)
        self.state = int(state)
        self.value = int(value)
        self.was_seen = False

    def distance(self, entity):
        return (entity.x - self.x) ** 2 + (entity.y - self.y) ** 2

    def distance_for_tuples(self, entity):
        return (entity[0] - self.x) ** 2 + (entity[1] - self.y) ** 2

    def is_visible_from(self, busters):
        return any([self.distance(busters[g]) < 2200 ** 2 for g in busters])

    def to_string(self):
        return f'{self.id} {self.x} {self.y} {self.type} {self.state} {self.value}\n'

    def find_closest_points(self, points):
        min_distance = min([self.distance_for_tuples(i) for i in points])
        return [i for i in points if self.distance_for_tuples(i) == min_distance]

    def move_to(self, x, y, max_step):
        if (self.x - x) ** 2 + (self.y - y) ** 2 <= max_step ** 2:
            self.x, self.y = x, y
        else:
            self.move_into_direction(x, y, max_step)

    def move_into_direction(self, x, y, step):
        target = np.array([x, y])
        current = np.array([self.x, self.y])
        direction = target - current
        direction_norm = direction / np.sqrt(direction @ direction)
        new_point = np.round(current + direction_norm * step)
        x = max(0, min(new_point[0], 16000))
        y = max(0, min(new_point[1], 9000))
        self.x, self.y = int(x), int(y)


def cut(x, y):
    if x > 16000: x = 16000
    if y > 9000: y = 9000
    if x < 0: x = 0
    if y < 0: y = 0
    return x, y