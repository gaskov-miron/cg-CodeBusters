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
        self.score_1 = 0
        self.score_2 = 0
        self.step = 0

    def get_info(self, player_id):
        result = ''
        for i in sorted(self.players_busters[player_id]):
            result += self.busters[i].to_string()

        for i in sorted(self.players_busters[not player_id]):
            if self.players_busters[not player_id][i].is_visible_from(self.players_busters[player_id]):
                result += self.players_busters[not player_id][i].to_string()

        for i in sorted(self.ghosts):
            if self.ghosts[i].x is not None and self.ghosts[i].y is not None:
                if self.ghosts[i].is_visible_from(self.players_busters[player_id]):
                    result += self.ghosts[i].to_string()
        return result

    def do(self, player0, player1):
        self.step += 1
        for id_g in self.ghosts:
            self.ghosts[id_g].value = 0
            self.ghosts[id_g].time_not_bust += 1
            self.ghosts[id_g].time_not_eject += 1
        busters_positions = [(self.busters[i].x, self.busters[i].y) for i in self.busters]
        stun_bust_id = []
        for i in range(len(player0) + len(player1)):
            if self.busters[i].state != 2:
                action = (player0 + player1)[i].split()
                if action[0] == 'MOVE':
                    target_x, target_y = int(action[1]), int(action[2])
                    self.busters[i].move_to(target_x, target_y, 800)

                if action[0] == 'BUST':
                    target_id = int(action[1])
                    self.busters[i].state = 3
                    if self.ghosts[target_id].state > 0:
                        self.ghosts[target_id].state -= 1
                    self.ghosts[target_id].value += 1
                    self.ghosts[target_id].time_not_bust = 0
                    self.busters[i].value = target_id

                if action[0] == 'RELEASE':
                    released_ghost = self.ghosts[self.busters[i].value]
                    self.busters[i].value = -1
                    self.busters[i].state = 0
                    released_ghost.x = self.busters[i].x
                    released_ghost.y = self.busters[i].y
                    if released_ghost.distance_for_tuples((0, 0)) <= 1600**2:
                        self.score_1 += 1
                        released_ghost.x = None
                        released_ghost.y = None
                    elif 1600**2 >= released_ghost.distance_for_tuples((16000, 9000)):
                        self.score_2 += 1
                        released_ghost.x = None
                        released_ghost.y = None

                if action[0] == 'STUN':
                    self.busters[i].state = 0
                    self.busters[i].value = -1
                    stun_bust_id.append(int(action[1]))

                if action[0] == 'EJECT':
                    self.ghosts[self.busters[i].value].x = self.busters[i].x
                    self.ghosts[self.busters[i].value].y = self.busters[i].y
                    self.ghosts[self.busters[i].value].time_not_eject = 0
                    self.busters[i].state = 0
                    self.ghosts[self.busters[i].value].move_to(int(action[1]), int(action[2]), 1760)
                    self.busters[i].value = -1

        for id_b in self.busters:
            if self.busters[id_b].state == 2:
                if self.busters[id_b].value > 1:
                    self.busters[id_b].value -= 1
                else:
                    self.busters[id_b].state = 0
                    self.busters[id_b].value = -1

        for i in self.ghosts:
            if self.ghosts[i].time_not_bust > 1 and self.ghosts[i].was_seen and self.ghosts[i].value == 0 and self.ghosts[i].x is not None:
                closest_points = self.ghosts[i].find_closest_points(busters_positions)
                if self.ghosts[i].time_not_eject > 0 and len(closest_points) == 1 and self.ghosts[i].distance_for_tuples(closest_points[0]) > 0:
                    self.ghosts[i].move_from_point(*closest_points[0], 400)
            bust0 = []
            bust1 = []
            for b in self.busters:
                if self.busters[b].state == 3 and self.busters[b].value == i:
                    if self.busters[b].type == 0:
                        bust0 += [b]
                    else:
                        bust1 += [b]
            if self.ghosts[i].state == 0 and len(bust0) != len(bust1):
                team_caught_ghost = bust0
                if len(bust0) < len(bust1):
                    team_caught_ghost = bust1
                s = self.ghosts[i].find_closest_points([(self.busters[i].x, self.busters[i].y) for i in team_caught_ghost])[0]
                for b in bust0 + bust1:
                    if (self.busters[b].x, self.busters[b].y) == s:
                        self.busters[b].state = 1
                    else:
                        self.busters[b].state = 0
                        self.busters[b].value = -1
                self.ghosts[i].x = None
                self.ghosts[i].y = None
            if self.ghosts[i].x is not None and self.ghosts[i].y is not None:
                self.ghosts[i].was_seen = self.ghosts[i].is_visible_from(self.busters)
        for i in stun_bust_id:
            if self.busters[i].state == 1:
                self.ghosts[self.busters[i].value].x = self.busters[i].x
                self.ghosts[self.busters[i].value].y = self.busters[i].y
            self.busters[i].state = 2
            self.busters[i].value = 10


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
        self.time_not_bust = 0
        self.time_not_eject = 0

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

    def move_from_point(self, x, y, step):
        self.move_into_direction(2*self.x - x, 2*self.y - y, step)
