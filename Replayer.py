import pygame
from engine import Entity, Engine
import copy as c


def drawWindow():
    win.blit(bg, (0, 0))
    for i in g.busters:
        pygame.draw.circle(win, (0, 0, 255), (g.busters[i].x//10, g.busters[i].y//10), 15)
    for i in g.ghosts:
        pygame.draw.circle(win, (0, 255, 0), (g.ghosts[i].x//10, g.ghosts[i].y//10), 15)
    pygame.display.update()


blocks = []
current_block = None
file_name_new = '/home/miron/work/cg-CodeBusters/tests/game_v2_1.txt'
block_starters = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n']
block_stoppers = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n', '\n']
win = pygame.display.set_mode((1600, 900))
bg = pygame.image.load('pictures/pesok-volnami-melkiy-priroda.jpg')


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
g = Engine(busters_count, ghosts_count, busters, ghosts)
i = 0
list_of_g = []

while i < len(steps1):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                list_of_g.append(c.deepcopy(g))
                g.do(steps1[i][1], steps2[i][1])
                i += 1
            if event.key == pygame.K_LEFT:
                if i > 0:
                    i -= 1
                    g = list_of_g[i]
                    del list_of_g[i]
    if i == len(steps1) - 1:
        pygame.quit()
    drawWindow()