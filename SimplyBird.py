import pygame, random, os

pygame.init()

# ---------- Screen Setup ----------
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Simply Bird Ultimate")

clock = pygame.time.Clock()

# ---------- Scaling helpers ----------
sx = lambda x: int(x * W / 400)
sy = lambda y: int(y * H / 600)

# ---------- Colors ----------
SKY = (135,206,235)
GREEN = (0,200,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (255,220,0)
ORANGE = (255,160,0)
BROWN = (120,70,30)

# ---------- Fonts ----------
font_big = pygame.font.SysFont(None, sy(60))
font_mid = pygame.font.SysFont(None, sy(36))
font_small = pygame.font.SysFont(None, sy(28))

# ---------- Highscore ----------
HS_FILE = "highscore.txt"
highscore = 0
if os.path.exists(HS_FILE):
    try: highscore = int(open(HS_FILE).read())
    except: highscore=0

# ---------- Easter Egg ----------
death_pipe_3 = 0

# ---------- Bird Sprite ----------
def make_bird():
    surf = pygame.Surface((sx(34), sy(24)), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, YELLOW, (0,0,sx(30),sy(20)))
    pygame.draw.circle(surf, WHITE, (sx(22),sy(8)), sy(4))
    pygame.draw.circle(surf, BLACK, (sx(23),sy(9)), sy(2))
    pygame.draw.polygon(surf, ORANGE, [(sx(28),sy(10)),(sx(34),sy(12)),(sx(28),sy(14))])
    return surf
BIRD = make_bird()

# ---------- Poop Particle ----------
class Poop:
    def __init__(self,x,y):
        self.x,self.y = x,y
        self.vx = random.uniform(-2,2)
        self.vy = random.uniform(-4,-1)
        self.life = random.randint(30,60)
        self.size = random.randint(sx(4),sx(7))
    def update(self):
        self.vy += 0.3
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
    def draw(self):
        pygame.draw.circle(screen,BROWN,(int(self.x),int(self.y)),self.size)

# ---------- Fade ----------
def fade(speed=15):
    f = pygame.Surface((W,H))
    f.fill(BLACK)
    for a in range(0,255,speed):
        f.set_alpha(a)
        screen.blit(f,(0,0))
        pygame.display.update()
        clock.tick(60)

# ---------- Menu ----------
def menu():
    while True:
        screen.fill(SKY)
        title = font_big.render("SIMPLY BIRD",True,WHITE)
        tap = font_mid.render("Tap to Start",True,WHITE)
        hs = font_small.render(f"Highscore: {highscore}",True,WHITE)
        screen.blit(title,(W//2-title.get_width()//2,H*0.3))
        screen.blit(tap,(W//2-tap.get_width()//2,H*0.5))
        screen.blit(hs,(W//2-hs.get_width()//2,H*0.6))
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit();quit()
            if e.type in (pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN):
                fade();return
        pygame.display.update();clock.tick(60)

# ---------- Game ----------
def game():
    global highscore, death_pipe_3
    bird_y = H//2
    bird_vel = 0
    gravity = sy(0.35)
    jump = -sy(5.0)
    pipe_x = W
    pipe_w = sx(60)
    pipe_gap = sy(190)
    pipe_h = random.randint(sy(120),sy(360))
    speed = sx(2.3)
    score = 0
    pipe_index = 1
    died_pipe = 0
    poop_particles=[]
    dying=False
    death_timer=0

    while True:
        clock.tick(60)
        screen.fill(SKY)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit();quit()
            if not dying and e.type in (pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN):
                bird_vel = jump

        # Bird physics
        bird_vel += gravity
        bird_y += bird_vel
        bird_rect = BIRD.get_rect(center=(sx(90),int(bird_y)))

        # Pipes
        pipe_x -= speed
        if pipe_x<-pipe_w:
            pipe_x=W
            pipe_h=random.randint(sy(120),sy(360))
            score+=1
            pipe_index+=1

        top = pygame.Rect(pipe_x,0,pipe_w,pipe_h)
        bottom = pygame.Rect(pipe_x,pipe_h+pipe_gap,pipe_w,H)
        pygame.draw.rect(screen,GREEN,top)
        pygame.draw.rect(screen,GREEN,bottom)

        # Collision
        if not dying and (bird_rect.colliderect(top) or bird_rect.colliderect(bottom) or bird_y<0 or bird_y>H):
            dying=True
            died_pipe=pipe_index
            for _ in range(18):
                poop_particles.append(Poop(bird_rect.centerx,bird_rect.centery))

        # Draw bird
        screen.blit(BIRD,bird_rect)

        # Poop update
        if dying:
            death_timer+=1
            for p in poop_particles[:]:
                p.update();p.draw()
                if p.life<=0: poop_particles.remove(p)
            if death_timer>60: break

        # Score
        s = font_small.render(str(score),True,WHITE)
        screen.blit(s,(W//2,sy(30)))

        pygame.display.update()

    # Save highscore
    if score>highscore:
        highscore=score
        open(HS_FILE,"w").write(str(highscore))

    # Easter Egg
    if died_pipe==3: death_pipe_3+=1
    else: death_pipe_3=0

    fade()
    game_over(score)

# ---------- Game Over ----------
def game_over(score):
    while True:
        screen.fill(SKY)
        o = font_big.render("Game Over",True,WHITE)
        s = font_mid.render(f"Score: {score}",True,WHITE)
        h = font_small.render(f"Highscore: {highscore}",True,WHITE)
        screen.blit(o,(W//2-o.get_width()//2,H*0.3))
        screen.blit(s,(W//2-s.get_width()//2,H*0.45))
        screen.blit(h,(W//2-h.get_width()//2,H*0.55))

        if death_pipe_3>=4:
            egg = font_small.render("made by loafy ;3",True,WHITE)
            screen.blit(egg,(W//2-egg.get_width()//2,H*0.65))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit();quit()
            if e.type in (pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN):
                fade();return

        pygame.display.update();clock.tick(60)

# ---------- Main Loop ----------
while True:
    menu()
    game()