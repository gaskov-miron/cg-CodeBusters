from engine import Entity
import random


def generate(busters_cnt, ghosts_cnt):
    list_busters_pos = [[1176, 2024], [2024, 1176], [14824, 6976], [13976, 7824]]
    list_busters_types = [0, 0, 1, 1]
    list_ghosts_lives = [5, 15, 40]
    busters = {i: Entity(f"{i} {list_busters_pos[i][0]} {list_busters_pos[i][1]} {list_busters_types[i]} 5 0") for i in range(busters_cnt*2)}
    ghosts = {i: Entity(f"{i} 8000 4500 -1 5 0") for i in range(ghosts_cnt)}
    lives = list_ghosts_lives[round(random.uniform(0, 16000)) % 3]
    ghosts[0].state = lives
    for i in range(1, ghosts_cnt, 2):
        lives = list_ghosts_lives[round(random.uniform(0, 16000))%3]
        ghosts[i].state = lives
        ghosts[i+1].state = lives
        x = round(random.uniform(0, 16000))
        ghosts[i].x = x
        ghosts[i+1].x = 16000 - x
        y = round(random.uniform(0, 9000))
        ghosts[i].y = y
        ghosts[i+1].y = 9000 - y
    return busters, ghosts