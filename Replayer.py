import pygame
from engine import Entity, Engine
from solution import Game, step, step_old
#from PUSH import push
from PUSH2 import go_to_base, Mind
import copy as c
from Generator import generate


class State:
    def __init__(self, engine, player0, mind0, player1, mind1):
        self.engine = engine
        self.player0 = player0
        self.mind0 = mind0
        self.player1 = player1
        self.mind1 = mind1


def drawWindow():
    win.blit(bg, (0, 0))

    for i in current_step.player0.ghosts:
        if current_step.player0.ghosts[i].x is not None:
            pygame.draw.circle(win, (100, 100, 100), (current_step.player0.ghosts[i].x // 10,current_step.player0.ghosts[i].y // 10), 16)
    #for state_ in states+[current_step]:
    #    for i in state_.engine.busters:
    #        pygame.draw.circle(win, (100, 100, 100), (state_.engine.busters[i].x // 10, state_.engine.busters[i].y // 10), 220)
    #        pygame.draw.circle(win, (100, 100, 100), (1600 - state_.engine.busters[i].x // 10, 900 - state_.engine.busters[i].y // 10), 220)

    pygame.draw.circle(win, (0, 0, 0), (0, 0), 160, 1)
    pygame.draw.circle(win, (0, 0, 0), (1600, 900), 160, 1)
    pygame.draw.line(win, (0, 0, 0), (0, 440), (1600, 440), 1)
    pygame.draw.line(win, (0, 0, 0), (0, 220), (1600, 220), 1)
    pygame.draw.line(win, (0, 0, 0), (547, 900), (1053, 0), 1)
    for i in current_step.engine.busters0:
        buster = current_step.engine.busters0[i]
        pygame.draw.circle(win, (0, 0, 255), (buster.x // 10, buster.y // 10), 15)
        if buster.state == 2:
            pygame.draw.line(win, (0, 0, 0), (buster.x // 10 - 10, buster.y // 10 - 10), (buster.x // 10 + 10, buster.y // 10 + 10), 2)
            pygame.draw.line(win, (0, 0, 0), (buster.x // 10 + 10, buster.y // 10 - 10), (buster.x // 10 - 10, buster.y // 10 + 10), 2)
        if buster.state == 3:
            ghost = current_step.engine.ghosts[buster.value]
            pygame.draw.line(win, (255, 0, 0), (buster.x // 10, buster.y // 10), (ghost.x // 10, ghost.y // 10), 4)
        if buster.state == 1:
            pygame.draw.circle(win, (0, 255, 0), (buster.x // 10, buster.y // 10), 8)
    for i in current_step.engine.busters1:
        buster = current_step.engine.busters1[i]
        pygame.draw.circle(win, (200, 0, 255), (buster.x // 10, buster.y // 10), 15)
        if buster.state == 2:
            pygame.draw.line(win, (0, 0, 0), (buster.x // 10 - 10, buster.y // 10 - 10), (buster.x // 10 + 10, buster.y // 10 + 10), 2)
            pygame.draw.line(win, (0, 0, 0), (buster.x // 10 + 10, buster.y // 10 - 10), (buster.x // 10 - 10, buster.y // 10 + 10), 2)
        if buster.state == 3:
            ghost = current_step.engine.ghosts[buster.value]
            pygame.draw.line(win, (255, 0, 0), (buster.x // 10, buster.y // 10), (ghost.x // 10, ghost.y // 10), 4)
        if buster.state == 1:
            pygame.draw.circle(win, (0, 255, 0), (buster.x // 10, buster.y // 10), 8)
    for i in current_step.engine.ghosts:
        if current_step.engine.ghosts[i].x is not None:
            if current_step.engine.ghosts[i].value > 0:
                pygame.draw.circle(win, (255, 0, 0), (current_step.engine.ghosts[i].x // 10, current_step.engine.ghosts[i].y // 10), 20)
            pygame.draw.circle(win, (0, 255, 0), (current_step.engine.ghosts[i].x // 10, current_step.engine.ghosts[i].y // 10), 15)
            pygame.font.init()
            myfont = pygame.font.SysFont('Comic Sans MS', 20)
            textsurface = myfont.render(str(i), False, (0, 0, 0))
            win.blit(textsurface, (current_step.engine.ghosts[i].x // 10, current_step.engine.ghosts[i].y // 10))

            textsurface = myfont.render(str(current_step.engine.ghosts[i].state), False, (0, 0, 0))
            win.blit(textsurface, (current_step.engine.ghosts[i].x // 10, current_step.engine.ghosts[i].y // 10 - 30))
    #for i in player0.ghosts:
        #if current_step.engine.ghosts[i].x is not None:
            #textsurface = myfont.render(str(player0.ghosts[i].my_busters_cnt), False, (0, 0, 0))
            #win.blit(textsurface, (current_step.engine.ghosts[i].x // 10 - 20, current_step.engine.ghosts[i].y // 10 - 30))

    myfont = pygame.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render('SCORE '+str(current_step.engine.score_1), False, (0, 0, 0))
    win.blit(textsurface, (0, 0))
    myfont = pygame.font.SysFont('Comic Sans MS', 20)
    textsurface = myfont.render('SCORE '+str(current_step.engine.score_2), False, (0, 0, 0))
    win.blit(textsurface, (1500, 850))

    pygame.display.update()


blocks = []
current_block = None
file_name_new = '/home/miron/work/cg-CodeBusters/tests/game_v3_1.txt'
block_starters = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n']
block_stoppers = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n', '\n']
win = pygame.display.set_mode((1600, 900))
bg = pygame.image.load('pictures/pesok-volnami-melkiy-priroda.jpg').convert_alpha()


with open(file_name_new, 'r') as f:
    lines = f.readlines()
for line in lines:
    if line in block_stoppers and current_block is not None:
        current_block = None
    if line in block_starters:
        current_block = []
        blocks.append(current_block)
    if current_block is not None and line not in block_stoppers and line not in block_starters:
        current_block.append(line[:-1])
busters_count, ghosts_count = map(int, blocks[0][:2])
player0, player1 = Game('\n'.join(blocks[0])), Game('\n'.join(blocks[3]))
del blocks[0], blocks[2]
steps1 = list(zip(blocks[0::4], blocks[1::4]))
steps2 = list(zip(blocks[2::4], blocks[3::4]))
busters, ghosts = {}, {}
for step_ in zip(steps1, steps2):
    for j in range(2):
        for i in step_[j][0]:
            id_, x, y, type_, state, value = i.split()
            if type_ == '-1' and int(id_) not in ghosts:
                ghosts[int(id_)] = Entity(i)
            if type_ != '-1' and int(id_) not in busters:
                busters[int(id_)] = Entity(i)

states = []

#busters_count = 2
#ghosts_count = 501
#busters, ghosts = generate(busters_count, ghosts_count)

#player0, player1 = Game(str(busters_count)+"\n"+str(ghosts_count)+"\n0"), Game(str(busters_count)+"\n"+str(ghosts_count)+"\n1")

engine = Engine(busters_count, ghosts_count, busters, ghosts)
player0.update(engine.get_info(0)[:-1])
player1.update(engine.get_info(1)[:-1])
mind = Mind(player0)

current_step = State(engine, player0, mind, player1, None)


i = 0
while i < 400:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                states.append(c.deepcopy(current_step))
                action0 = current_step.mind0.step().split('\n') #push(current_step.player0).split('\n')
                #action1 = go_to_base(current_step.player1).split('\n') #push(current_step.player1).split('\n')
                action1 = step(current_step.player1).split('\n')
                current_step.engine.do(action0, action1)
                current_step.player0.update(current_step.engine.get_info(0)[:-1])
                current_step.player1.update(current_step.engine.get_info(1)[:-1])
                i += 1
            if event.key == pygame.K_LEFT:
                if i > 0:
                    i -= 1
                    current_step = states[i]
                    del states[i]

    drawWindow()

