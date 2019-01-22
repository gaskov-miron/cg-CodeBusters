import pygame


class snaryad():
    def __init__(self, x, y, r, color, facing):
        self.x = x
        self.y = y
        self.radius = r
        self.color = color
        self.facing = facing
        self.vel = 32*facing
    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)


pygame.init()
win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Cubes game")

x = 50
y = 400
weight = 60
height = 71
speed = 5
is_jump = False
jump_count = 7
run = True
left = False
right = False
animCount = 0
last_move = 1

def drawWindow():
    global animCount
    win.blit(bg, (0, 0))
    if animCount + 1 >= 30:
        animCount = 0
    for i in bullets:
        i.draw(win)
    if left:
        win.blit(walkLeft[animCount // 5], (x, y))
        animCount += 1
    elif right:
        win.blit(walkRight[animCount // 5], (x, y))
        animCount += 1
    else:
        win.blit(playerStand, (x, y))

    pygame.display.update()

clock = pygame.time.Clock()
walkLeft = [pygame.image.load('pictures/pygame_left_'+str(i)+'.png') for i in range(1, 7)]
walkRight = [pygame.image.load('pictures/pygame_right_'+str(i)+'.png') for i in range(1, 7)]
playerStand = pygame.image.load('pictures/pygame_idle.png')
bg = pygame.image.load('pictures/pygame_bg.jpg')
bullets = []
while run:
    pygame.draw.rect(win, (0, 0, 255), (x, y, weight, height))
    clock.tick(50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    for i in bullets:
        if i.x > i.radius and i.x < 500:
            i.x += i.vel
        else:
            bullets.pop(bullets.index(i))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_f]:
        if last_move == 1:
            facing = 1
        else:
            facing = -1
        if len(bullets) < 5:
            bullets.append(snaryad(round(x+weight//2), round(y+height//2), 5, (255, 255, 255), facing))

    if keys[pygame.K_LEFT] and 5 < x:
        x -= speed
        left = True
        right = False
        last_move = -1
        if is_jump:
            x -= speed
    elif keys[pygame.K_RIGHT] and 495-weight > x:
        x += speed
        left = False
        right = True
        last_move = 1
        if is_jump:
            x += speed

    else:
        left = False
        right = False
        animCount = 0
    if not is_jump:
        if keys[pygame.K_UP]:
            is_jump = True
    else:
        if jump_count >= -7:
            if jump_count > 0:
                y -= (jump_count**2 / 2)
            else:
                y += (jump_count ** 2 / 2)
            jump_count -= 1
        else:
            is_jump = False
            jump_count = 7
    drawWindow()
pygame.quit()