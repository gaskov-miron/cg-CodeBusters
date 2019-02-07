import itertools
from solution import get_research_direction


def find_pushed(my_busters, ghosts):
    dic = []
    if
    return dic


def push(g):
    for i in g.my_ids:
        if g.step > 9:
            res = ''
            ghosts = [i for i in g.ghosts.values() if i.distance(g.base) < 5470 ** 2]
            targets = find_pushed(g.my_busters, ghosts)
            if i in targets:
                if g.my_id == 0 :
                    need_x, need_y = 0, 0
                    no_x, no_y = 16000, 9000
                else:
                    need_x, need_y = 16000, 9000
                    no_x, no_y = 0, 0
            else:
                res += f'MOVE {g.base.x} {g.base.y}\n'
        else:
            dx, dy = get_research_direction(g.my_id, g.step, i, g.busters_cnt)
            res += f'MOVE {g.my_busters[i].x + dx} {g.my_busters[i].y + dy}\n'
    return res[:-1]