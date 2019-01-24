import pygame


def drawWindow():
    won.blit(bg, (0, 0))
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render('Second '+str(a_2), False, (255, 0, 0))
    won.blit(textsurface, (1450, 0))

    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render('First '+str(a_1), False, (255, 0, 0))
    won.blit(textsurface, (0, 0))

    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render('Time '+str(time_all), False, (255, 255, 0))
    won.blit(textsurface, (700, 0))

    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render('Pause, press p to continue', False, (0, 255, 0))

    pygame.draw.rect(won, (0, 255, 255), (x_1, y_1, weight, height))
    pygame.draw.rect(won, (0, 255, 255), (x_2, y_2, weight, height))
    pygame.draw.circle(won, (255, 255, 255), (ball_x, ball_y), 20)
    if p:
        won.blit(textsurface, (600, 400))
    pygame.display.update()


who_have_ball = 1
clock = pygame.time.Clock()
bg = pygame.image.load('pictures/fonee.jpg')
won = pygame.display.set_mode((1600, 900))
run = True
x_1, y_1 = 40, 300
x_2, y_2 = 1540, 300
height = 250
weight = 30
a_1, a_2 = 0, 0
is_play = False
time = 0
time_all = 0
p = False
while run:
    clock.tick(50)
    if not is_play:
        ball_x, ball_y = 800, 450
        speed_x = 5*who_have_ball
        speed_y = 5
        is_play = True
        time = 0
        time_all = 0
        pygame.time.delay(1000)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    keys = pygame.key.get_pressed()

    if keys[pygame.K_p] and p:
        p = False
    if keys[pygame.K_o] and not p:
        p = True

    if not p:
        if keys[pygame.K_w]:
            if y_1 > 10:
                y_1 -= 10
        if keys[pygame.K_s]:
            if y_1 < 900-10-height:
                y_1 += 10
        if keys[pygame.K_UP]:
            if y_2 > 10:
                y_2 -= 10
        if keys[pygame.K_DOWN]:
            if y_2 < 900-10 - height:
                y_2 += 10
        if ball_y < 30:
            speed_y = -1 * speed_y
        if ball_y > 900-20:
            speed_y = -1 * speed_y
        if ball_x <= -30:
            a_2 += 1
            is_play = False
            who_have_ball *= -1
        if ball_x >= 1630:
            a_1 += 1
            is_play = False
            who_have_ball *= -1

        ball_x += speed_x
        ball_y += speed_y

        if 40 <= ball_x <= 90 and 0 <= (ball_y - y_1) <= 250:
            if 0 > speed_x:
                speed_x = -1 * speed_x
        if not 1520 > ball_x and 1560 >= ball_x and 0 <= (ball_y - y_2) <= 250 and speed_x > 0:
            speed_x = -1 * speed_x
        time += 1
        time_all += 1
        if time == 1000:
            if speed_x < 0:
                speed_x = speed_x-1
            else:
                speed_x = speed_x+1
            if speed_y < 0:
                speed_y = speed_y - 1
            else:
                speed_y = speed_y + 1
            time = 0

    drawWindow()
pygame.quit()