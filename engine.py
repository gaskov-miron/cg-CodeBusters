import math


def cut(x, y):
    if x > 16000: x = 16000
    if y > 9000: y = 9000
    if x < 0: x = 0
    if y < 0: y = 0
    return str(x)+' '+str(y)


def init(busters0, busters1, ghosts):
    global g_bust0, g_bust1, g_ghost, was_seen

    a, b = '', ''
    for i in busters0:
        inf = busters0[i].split(' ')
        a += str(i)+' '+inf[0]+' '+inf[1]+' '+'0'+' '+inf[2]+' '+inf[3]+'\n'
    for i in busters1:
        inf = busters1[i].split(' ')
        b += str(i)+' '+inf[0]+' '+inf[1]+' '+'1'+' '+inf[2]+' '+inf[3]+'\n'
    for i in ghosts:
        if ghosts[i].split()[0] != 'None':
            inf = ghosts[i].split()
            x1, y1, hp, n_killers = int(inf[0]), int(inf[1]), inf[2], inf[3]
            for g in busters0:
                inf2 = busters0[g].split()
                x2, y2 = int(inf2[0]), int(inf2[1])
                if (x2-x1)**2+(y2-y1)**2 < 2200**2:
                    a += str(i)+' '+str(x1)+' '+str(y1)+' '+'-1'+' '+hp+' '+n_killers+'\n'
                    break
            for g in busters1:
                inf2 = busters1[g].split()
                x2, y2 = int(inf2[0]), int(inf2[1])
                if (x2-x1)**2+(y2-y1)**2 < 2200**2:
                    b += str(i)+' '+str(x1)+' '+str(y1)+' '+'-1'+' '+hp+' '+n_killers+'\n'
                    break
    was_seen = []
    g_bust0 = busters0
    g_bust1 = busters1
    g_ghost = ghosts
    return a, b


def step(step1, step2, n):
    global g_bust0, g_bust1, g_ghost, was_seen

    c = []
    for i in list(g_bust0.values())+list(g_bust1.values()):
        v1, v2, v3, v4 = i.split()
        c.append((int(v1), int(v2)))
    a, b = '', ''
    for i in range(len(step1.split('\n'))):
        act = step1.split('\n')[i].split()
        x1, y1 = int(act[1]), int(act[2])
        x0, y0, v3, v4 = g_bust0[str(i)].split()
        x0, y0 = int(x0), int(y0)
        if x0 != x1 or y0 != y1:
            A = math.sqrt((800**2)/(((x0-x1)**2)+((y0-y1)**2)))
            new_x = round(int(x0) + A*(x1-x0))
            new_y = round(int(y0) + A*(y1-y0))
            if (x1-x0)**2+(y1-y0)**2 < 800**2:
                g_bust0[str(i)] = act[1]+' '+act[2]+' '+v3+' '+v4
            else:
                g_bust0[str(i)] = str(new_x)+' '+str(new_y)+' '+v3+' '+v4
    l = i+1
    for i in range(len(step2.split('\n'))):
        act = step2.split('\n')[i].split()
        x1, y1 = int(act[1]), int(act[2])
        x0, y0, v3, v4 = g_bust1[str(i+l)].split()
        x0, y0 = int(x0), int(y0)
        if x0 != x1 or y0 != y1:
            A = math.sqrt((800**2)/(((x0-x1)**2)+((y0-y1)**2)))
            new_x = round(int(x0) + A*(x1-x0))
            new_y = round(int(y0) + A*(y1-y0))
            if (x1-x0)**2+(y1-y0)**2 < 800**2:
                g_bust1[str(i+l)] = act[1]+' '+act[2]+' '+v3+' '+v4
            else:
                g_bust1[str(i+l)] = str(new_x)+' '+str(new_y)+' '+v3+' '+v4
    for i in g_bust0:
        v1, v2, v3, v4 = g_bust0[i].split()
        a += i+' '+v1+' '+v2+' 0 '+v3+' '+v4+'\n'
    for i in g_bust1:
        v1, v2, v3, v4 = g_bust1[i].split()
        b += i+' '+v1+' '+v2+' 1 '+v3+' '+v4+'\n'
    print(was_seen)
    for i in g_ghost:
        if str(i) in was_seen:
            print(i)
            k = True
            if g_ghost[i].split()[0] != 'None':
                x0, y0, hp, n_killers = g_ghost[i].split()
                x1 = int(x0)
                y1 = int(y0)
                x0, y0 = int(x0), int(y0)
                min_d = 25000**2
                for g in c:
                    d = (x0-g[0])**2+(y0-g[1])**2
                    if min_d > d:
                        k = True
                        min_d = d
                        x1, y1 = x0+x0-g[0], y0+y0-g[1]
                    elif min_d == d:
                        k = False
                print(k, min_d, ((x0-x1) != 0 or (y0-y1) != 0))
                if k and min_d <= 2200**2 and ((x0-x1) != 0 or (y0-y1) != 0):

                    A = math.sqrt(400**2/(((x1-x0)**2)+((y1-y0)**2)))
                    g_ghost[i] = cut(round(x0+A*(x1-x0)), round(y0+A*(y1-y0)))+' '+hp+' '+n_killers
    new_was_seen = []
    for i in g_ghost:
        if g_ghost[i].split()[0] != 'None':
            inf = g_ghost[i].split()
            x1, y1, hp, n_killers = int(inf[0]), int(inf[1]), inf[2], inf[3]
            for g in g_bust0:
                inf2 = g_bust0[g].split()
                x2, y2 = int(inf2[0]), int(inf2[1])
                if (x2-x1)**2+(y2-y1)**2 < 2200**2:
                    new_was_seen.append(str(i))
                    break
            for g in g_bust1:
                inf2 = g_bust1[g].split()
                x2, y2 = int(inf2[0]), int(inf2[1])
                if (x2-x1)**2+(y2-y1)**2 < 2200**2:
                    new_was_seen.append(str(i))
                    break
    was_seen = new_was_seen[:]
    a_id = []
    b_id = []
    for i in g_ghost:
        if g_ghost[i].split()[0] != 'None':
            inf = g_ghost[i].split()
            x1, y1, hp, n_killers = int(inf[0]), int(inf[1]), inf[2], inf[3]
            for g in g_bust0:
                inf2 = g_bust0[g].split()
                x2, y2 = int(inf2[0]), int(inf2[1])
                if (x2-x1)**2+(y2-y1)**2 < 2200**2:
                    a_id.append(int(i))
                    break
            for g in g_bust1:
                inf2 = g_bust1[g].split()
                x2, y2 = int(inf2[0]), int(inf2[1])
                if (x2-x1)**2+(y2-y1)**2 < 2200**2:
                    b_id.append(int(i))
                    break
    seen_enemy_bust0 = []
    seen_enemy_bust1 = []
    for i in g_bust0:
        inf1 = g_bust0[i].split()
        x1, y1 = int(inf1[0]), int(inf1[1])
        for g in g_bust1:
            inf2 = g_bust1[g].split()
            x2, y2 = int(inf2[0]), int(inf2[1])
            if (x2-x1)**2+(y2-y1)**2 < 2200**2:
                seen_enemy_bust0.append(int(g))
                seen_enemy_bust1.append(int(i))
                break
    for i in sorted(seen_enemy_bust0):
        inf = g_bust1[str(i)].split()
        x1, y1, stat, value = int(inf[0]), int(inf[1]), inf[2], inf[3]
        a += str(i)+' '+str(x1)+' '+str(y1)+' '+'1'+' '+stat+' '+value+'\n'
    for i in sorted(seen_enemy_bust1):
        inf = g_bust0[str(i)].split()
        x1, y1, stat, value = int(inf[0]), int(inf[1]), inf[2], inf[3]
        b += str(i)+' '+str(x1)+' '+str(y1)+' '+'0'+' '+stat+' '+value+'\n'
    for i in sorted(a_id):
        inf = g_ghost[str(i)].split()
        x1, y1, hp, n_killers = int(inf[0]), int(inf[1]), inf[2], inf[3]
        a += str(i)+' '+str(x1)+' '+str(y1)+' '+'-1'+' '+hp+' '+n_killers+'\n'
    for i in sorted(b_id):
        inf = g_ghost[str(i)].split()
        x1, y1, hp, n_killers = int(inf[0]), int(inf[1]), inf[2], inf[3]
        b += str(i)+' '+str(x1)+' '+str(y1)+' '+'-1'+' '+hp+' '+n_killers+'\n'

    return a[:-1], b[:-1]