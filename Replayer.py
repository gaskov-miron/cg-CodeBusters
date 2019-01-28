import pygame
from engine import Entity, Engine
from solution import Game, step_research
import copy as c


class State:
    def __init__(self, engine, player0, player1, action0, action1):
        self.engine = engine
        self.player0 = player0
        self.player1 = player1
        self.action0 = action0
        self.action1 = action1


def drawWindow():
    win.blit(bg, (0, 0))

    for i in current_step.player0.ghosts:
        if current_step.player0.ghosts[i].x != None:
            pygame.draw.circle(win, (100, 100, 100), (current_step.player0.ghosts[i].x // 10,current_step.player0.ghosts[i].y // 10), 16)
    #for state_ in states+[current_step]:
    #    for i in state_.engine.busters:
    #        pygame.draw.circle(win, (100, 100, 100), (state_.engine.busters[i].x // 10, state_.engine.busters[i].y // 10), 220)
    #        pygame.draw.circle(win, (100, 100, 100), (1600 - state_.engine.busters[i].x // 10, 900 - state_.engine.busters[i].y // 10), 220)
    pygame.draw.circle(win, (0, 0, 0), (0, 0), 160, 1)
    pygame.draw.circle(win, (0, 0, 0), (1600, 900), 160, 1)
    pygame.draw.line(win, (0, 0, 0), (547, 900), (1053, 0), 1)
    for i in current_step.engine.busters:
        pygame.draw.circle(win, (0, 0, 255), (current_step.engine.busters[i].x // 10, current_step.engine.busters[i].y // 10), 15)
    for i in current_step.engine.ghosts:
        pygame.draw.circle(win, (0, 255, 0), (current_step.engine.ghosts[i].x // 10, current_step.engine.ghosts[i].y // 10), 15)


        pygame.font.init()
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        textsurface = myfont.render(str(i), False, (255, 0, 0))
        win.blit(textsurface, (current_step.engine.ghosts[i].x // 10, current_step.engine.ghosts[i].y // 10))

    pygame.display.update()


blocks = []
current_block = None
file_name_new = '/home/miron/work/cg-CodeBusters/tests/game_v2_1.txt'
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
engine = Engine(busters_count, ghosts_count, busters, ghosts)
current_step = State(engine,
                     player0,
                     player1,
                     step_research(engine.get_info(0)[:-1], player0).split('\n'),
                     step_research(engine.get_info(1)[:-1], player1).split('\n'))

i = 0
while i < len(steps1):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                states.append(c.deepcopy(current_step))
                current_step.engine.do(current_step.action0, current_step.action1)
                current_step.action0 = step_research(current_step.engine.get_info(0)[:-1], current_step.player0).split('\n')
                current_step.action1 = step_research(current_step.engine.get_info(1)[:-1], current_step.player1).split('\n')
                i += 1
            if event.key == pygame.K_LEFT:
                if i > 0:
                    i -= 1
                    current_step = states[i]
                    del states[i]
    if i == len(steps1) - 1:
        pygame.quit()
    drawWindow()

