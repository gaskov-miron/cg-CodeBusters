import copy
from solution import Point


def forecast(targets, points):
    for point in points:
        for target in targets:
            if target.distance(point) <= 2200 ** 2:
                target.move_backward(point, 400)


def push(g):
    res = ''
    for i in g.my_ids:
        if g.my_id == 1:
            res += f'MOVE {g.base.x} {g.base.y}\n'
        else:
            H1 = 4400
            H2 = 2200
            if i == 0:
                if g.my_busters[i].y != H1:
                    res += f'MOVE {0} {H1}\n'
                elif g.my_busters[i].x != 16000:
                    targets = copy.deepcopy([gh for gh in g.ghosts.values() if gh.x is not None])
                    targets = [gh for gh in targets if (gh.x >= g.my_busters[i].x >= gh.x - 800) and (gh.y < g.my_busters[i].y)]
                    current_x, current_y = g.my_busters[i].x, g.my_busters[i].y
                    forecast(targets, [Point(current_x + 800*i, current_y) for i in range(4)])
                    not_pushed = [target.id for target in targets if target.y >= H2]
                    targets = copy.deepcopy([gh for gh in g.ghosts.values() if gh.x is not None])
                    forecast(targets, [Point(current_x + 800 * i, current_y) for i in range(1)])
                    targets = {tar.id: tar for tar in targets}
                    if len(not_pushed) != 0:
                        min_x = 800
                        min_id = not_pushed[0]
                        for id_ in not_pushed:
                            print(targets[id_].x, g.my_busters[i].x)
                            if abs(targets[id_].x - g.my_busters[i].x) < min_x:
                                min_x = targets[id_].x - g.my_busters[i].x
                                min_id = id_
                        res += f'MOVE {targets[min_id].x} {H1}\n'
                    else:
                        res += f'MOVE {16000} {H1}\n'
                else:
                    res += f'MOVE {g.my_busters[i].x} {g.my_busters[i].y}\n'
            if i == 1:
                if g.my_busters[0].x == 16000:
                    if g.my_busters[i].y != H2:
                        res += f'MOVE {0} {H2}\n'
                    elif g.my_busters[i].x != 16000:
                        targets = copy.deepcopy([gh for gh in g.ghosts.values() if gh.x is not None])
                        targets = [gh for gh in targets if
                                   (gh.x >= g.my_busters[i].x >= gh.x - 800) and (gh.y < g.my_busters[i].y)]
                        current_x, current_y = g.my_busters[i].x, g.my_busters[i].y
                        forecast(targets, [Point(current_x + 800 * i, current_y) for i in range(4)])
                        not_pushed = [target.id for target in targets if target.y > 0]
                        targets = copy.deepcopy([gh for gh in g.ghosts.values() if gh.x is not None])
                        forecast(targets, [Point(current_x + 800 * i, current_y) for i in range(1)])
                        targets = {tar.id: tar for tar in targets}
                        if len(not_pushed) != 0:
                            min_x = 800
                            min_id = not_pushed[0]
                            for id_ in not_pushed:
                                print(targets[id_].x, g.my_busters[i].x)
                                if abs(targets[id_].x - g.my_busters[i].x) < min_x:
                                    min_x = targets[id_].x - g.my_busters[i].x
                                    min_id = id_
                            res += f'MOVE {targets[min_id].x} {H2}\n'
                        else:
                            res += f'MOVE {16000} {H2}\n'
                    else:
                        res += f'MOVE {g.my_busters[i].x} {g.my_busters[i].y}\n'
                else:
                    res += f'MOVE {g.my_busters[i].x} {g.my_busters[i].y}\n'
    return res[:-1]