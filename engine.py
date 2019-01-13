import math


class Entity:
    def __init__(self, string):
        id, _type, x, y, state, value = string.split()
        self.id = int(id)
        self.x = int(x)
        self.y = int(y)
        self.type = int(_type)
        self.state = int(state)
        self.value = int(value)

    def to_string(self):
        return str(self.id)+' '+str(self.x)+' '+str(self.y)+' '+str(self.type)+' '+str(self.state)+' '+str(self.value)+'\n'


def close_ghost(bust, x1, y1, i):
    for g in bust:
        x2 = bust[g].x
        y2 = bust[g].y
        if (x2 - x1) ** 2 + (y2 - y1) ** 2 < 2200 ** 2:
            return i
    return None


def who_is_visible():
    a, b = '', ''
    a_id = []
    b_id = []
    global g_bust0, g_bust1, g_ghost, was_seen
    for i in g_bust0: a += g_bust0[i].to_string()
    for i in g_bust1: b += g_bust1[i].to_string()
    for i in g_ghost:
        x1 = g_ghost[i].x
        y1 = g_ghost[i].y
        ans0 = close_ghost(g_bust0, x1, y1, i)
        ans1 = close_ghost(g_bust1, x1, y1, i)
        if ans0 is not None: a_id.append(ans0)
        if ans1 is not None: b_id.append(ans1)
    seen_enemy_bust0 = []
    seen_enemy_bust1 = []
    for i in g_bust0:
        x1 = g_bust0[i].x
        y1 = g_bust0[i].y
        for g in g_bust1:
            x2 = g_bust1[g].x
            y2 = g_bust1[g].y
            if (x2 - x1) ** 2 + (y2 - y1) ** 2 < 2200 ** 2:
                seen_enemy_bust0.append(int(g))
                seen_enemy_bust1.append(int(i))
                break
    for i in sorted(seen_enemy_bust0): a += g_bust1[i].to_string()
    for i in sorted(seen_enemy_bust1): b += g_bust0[i].to_string()
    for i in sorted(a_id): a += g_ghost[i].to_string()
    for i in sorted(b_id): b += g_ghost[i].to_string()
    return a, b


def cut(x, y):
    if x > 16000: x = 16000
    if y > 9000: y = 9000
    if x < 0: x = 0
    if y < 0: y = 0
    return x, y


def init(busters0, busters1, ghosts):
    global g_bust0, g_bust1, g_ghost, was_seen
    was_seen = []
    g_bust0 = {}
    g_bust1 = {}
    g_ghost = {}
    for i in busters0:
        g_bust0[int(i)] = Entity(i+' 0 '+busters0[i])
    for i in busters1:
        g_bust1[int(i)] = Entity(i+' 1 '+busters1[i])
    for i in ghosts:
        g_ghost[int(i)] = Entity(i+' -1 '+ghosts[i])
    return who_is_visible()


def step(step1, step2, n):
    global g_bust0, g_bust1, g_ghost, was_seen
    c = []
    for i in list(g_bust0.values())+list(g_bust1.values()):
        c.append((i.x, i.y))
    for i in range(len(step1.split('\n'))):
        act = step1.split('\n')[i].split()
        x1, y1 = int(act[1]), int(act[2])
        x0 = g_bust0[i].x
        y0 = g_bust0[i].y
        if x0 != x1 or y0 != y1:
            A = math.sqrt((800**2)/(((x0-x1)**2)+((y0-y1)**2)))
            new_x = round(x0 + A*(x1-x0))
            new_y = round(y0 + A*(y1-y0))
            if (x1-x0)**2+(y1-y0)**2 < 800**2:
                g_bust0[i].x = int(act[1])
                g_bust0[i].y = int(act[2])
            else:
                g_bust0[i].x = new_x
                g_bust0[i].y = new_y
    l = i + 1
    for i in range(len(step2.split('\n'))):
        act = step2.split('\n')[i].split()
        x1, y1 = int(act[1]), int(act[2])
        x0 = g_bust1[i+l].x
        y0 = g_bust1[i+l].y
        if x0 != x1 or y0 != y1:
            A = math.sqrt((800**2)/(((x0-x1)**2)+((y0-y1)**2)))
            new_x = round(x0 + A*(x1-x0))
            new_y = round(y0 + A*(y1-y0))
            if (x1-x0)**2+(y1-y0)**2 < 800**2:
                g_bust1[i+l].x = int(act[1])
                g_bust1[i+l].y = int(act[2])
            else:
                g_bust1[i+l].x = new_x
                g_bust1[i+l].y = new_y
    for i in g_ghost:
        if i in was_seen:
            k = True
            x1 = g_ghost[i].x
            y1 = g_ghost[i].y
            x0, y0 = x1, y1
            min_d = 25000**2
            for g in c:
                d = (x0-g[0])**2+(y0-g[1])**2
                if min_d > d:
                    k = True
                    min_d = d
                    x1, y1 = x0+x0-g[0], y0+y0-g[1]
                elif min_d == d:
                    k = False
            if k and min_d <= 2200**2 and ((x0-x1) != 0 or (y0-y1) != 0):
                A = math.sqrt(400**2/(((x1-x0)**2)+((y1-y0)**2)))
                x, y = cut(round(x0+A*(x1-x0)), round(y0+A*(y1-y0)))
                g_ghost[i].x = x
                g_ghost[i].y = y
    was_seen = []
    for i in g_ghost:
        x1 = g_ghost[i].x
        y1 = g_ghost[i].y
        ans0 = close_ghost(g_bust0, x1, y1, i)
        ans1 = close_ghost(g_bust1, x1, y1, i)
        if ans0 is not None: was_seen.append(ans0)
        if ans1 is not None: was_seen.append(ans1)
    return who_is_visible()
