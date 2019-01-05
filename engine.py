def init(busters0, busters1, ghosts):
    a, b = '', ''
    for i in busters0:
        inf = busters0[i].split(' ')
        a += str(i)+' '+inf[0]+' '+inf[1]+' '+'0'+' '+inf[2]+' '+inf[3]+'\n'
    for i in busters1:
        inf = busters1[i].split(' ')
        b += str(i)+' '+inf[0]+' '+inf[1]+' '+'0'+' '+inf[2]+' '+inf[3]+'\n'
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
    return a, b
