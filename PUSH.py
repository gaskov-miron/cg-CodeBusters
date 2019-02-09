from solution import get_research_direction


def end(ghost):
    return 0 < ghost.x < 16000 and 0 < ghost.y < 9000


def find_pushed(my_busters, ghosts):
    dic = []
    list_of_used = []
    for i in ghosts:
        if i.x is not None and not end(i):
            dic[i.find_all_nearest([my_busters[b] for b in my_busters if b not in list_of_used])[0]] = i
            list_of_used.append(i.find_all_nearest([my_busters[b] for b in my_busters if b not in list_of_used])[0])
    return dic


def push(g):
    res = ''
    for i in g.my_ids:
        if g.step > 9:
            res = ''
            ghosts = [i for i in g.ghosts.values() if i.x is not None and i.distance(g.base) < 5470 ** 2]
            targets = find_pushed(g.my_busters, ghosts)
            if i in targets:
                if g.my_id == 0:
                    ghost = targets[i]
                    if ghost.x < g.my_busters[i].x:
                        res += f'MOVE {ghost.x + 800} {ghost.y}\n'
                    elif ghost.y >= g.my_busters[i].y:
                        res += f'MOVE {ghost.x} {ghost.y + 800}\n'

                else:
                    ghost = targets[i]
                    if ghost.x > g.my_busters[i].x:
                        res += f'MOVE {ghost.x - 800} {ghost.y}\n'
                    elif ghost.y <= g.my_busters[i].y:
                        res += f'MOVE {ghost.x} {ghost.y - 800}\n'

            else:
                res += f'MOVE {g.base.x} {g.base.y}\n'
        else:
            dx, dy = get_research_direction(g.my_id, g.step, i, g.busters_cnt)
            res += f'MOVE {g.my_busters[i].x + dx} {g.my_busters[i].y + dy}\n'
    return res[:-1]