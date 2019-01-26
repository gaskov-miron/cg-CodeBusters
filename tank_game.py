import pygame


class snaryad():
    def __init__(self, x, y, r, color, facing_x, facing_y):
        self.x = x
        self.y = y
        self.radius = r
        self.color = color
        self.facing_x = facing_x
        self.facing_y = facing_y
        self.vel_x = 32*facing_x
        self.vel_y = 32*facing_y

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)


def drawWindow():
    global animCount
    win.blit(bg, (0, 0))
    for i in bullets:
        i.draw(win)
    if animCount + 1 >= 30:
        animCount = 0
    if left:
        win.blit(walkLeft[animCount // 5], (x, y))
        animCount += 1
        animCount = animCount // 5
    elif right:
        win.blit(walkRight[animCount // 5], (x, y))
        animCount += 1
        animCount = animCount // 5
    else:
        win.blit(playerStand, (x, y))
    pygame.display.update()


pygame.init()
win = pygame.display.set_mode((1023, 680))
pygame.display.set_caption("strelalka")

bg = pygame.image.load('pictures/fonefortanks.jpg')
walkLeft = [pygame.image.load('pictures/pygame_left_'+str(i)+'.png') for i in range(1, 7)]
walkRight = [pygame.image.load('pictures/pygame_right_'+str(i)+'.png') for i in range(1, 7)]
playerStand = pygame.image.load('pictures/pygame_idle.png')
x = 100
y = 100
run = True
left = False
right = False
animCount = 0
bullets = []
weight = 60
height = 71
speed = 5
is_jump = False
clock = pygame.time.Clock()
last_move = 1

while run:
    clock.tick(50)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()

    for i in bullets:
        if i.x > i.radius and i.x < 1500 and i.y > i.radius and i.y < 1500:
            i.x += i.vel_x
            i.y += i.vel_y
        else:
            bullets.pop(bullets.index(i))

    if keys[pygame.K_f]:
        if last_move == 1:
            facing_x = 1
            facing_y = 0
        if last_move == -1:
            facing_x = -1
            facing_y = 0
        if last_move == -2:
            facing_x = 0
            facing_y = -1
        if last_move == 2:
            facing_x = 0
            facing_y = 1
        if len(bullets) < 5:
            bullets.append(snaryad(round(x + weight // 2), round(y + height // 2), 5, (0, 0, 0), facing_x, facing_y))

    if keys[pygame.K_LEFT] and 5 < x:
        x -= speed
        left = True
        right = False
        last_move = -1
        if is_jump:
            x -= speed
    elif keys[pygame.K_RIGHT] and 1013 - weight > x:
        x += speed
        left = False
        right = True
        last_move = 1
        if is_jump:
            x += speed
    else:
        left = False
        right = False

    if keys[pygame.K_UP] and 5 < y:
        y -= speed
        last_move = -2
        if is_jump:
            y -= speed
    elif keys[pygame.K_DOWN] and 680 - height > y:
        y += speed
        last_move = 2
        if is_jump:
            y += speed
        animCount = 0
    drawWindow()
pygame.quit()