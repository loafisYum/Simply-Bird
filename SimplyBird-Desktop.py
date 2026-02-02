import pygame, random, json, os

pygame.init()

# ================== WINDOW ==================
BASE_W, BASE_H = 400, 600
W, H = 400, 600   # portrait by default
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Simply Bird Ultimate (PC)")
clock = pygame.time.Clock()

def sx(x): return x * W / BASE_W
def sy(y): return y * H / BASE_H

# ================== COLORS ==================
SKY = (135,206,235)
GREEN = (0,200,0)
WHITE = (255,255,255)
BLACK = (0,0,0)

SKINS = {
    "yellow": {"color": (255,220,0), "price": 0},
    "red":    {"color": (255,80,80),  "price": 500},
    "blue":   {"color": (80,120,255), "price": 1000},
}

# ================== SAVE ==================
SAVE_FILE = "save.json"

def load_save():
    if os.path.exists(SAVE_FILE):
        return json.load(open(SAVE_FILE))
    return {"coins": 0, "skin": "yellow"}

def save_game():
    json.dump(save, open(SAVE_FILE, "w"))

save = load_save()

# ================== FONTS ==================
def load_fonts():
    global big, mid, small
    big = pygame.font.SysFont(None, int(sy(56)))
    mid = pygame.font.SysFont(None, int(sy(34)))
    small = pygame.font.SysFont(None, int(sy(24)))

load_fonts()

# ================== BIRD ==================
def make_bird_frames(color):
    frames = []
    for wing in [-4, 0, 4]:
        surf = pygame.Surface((int(sx(34)), int(sy(24))), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, color, (0,0,int(sx(30)),int(sy(20))))
        pygame.draw.circle(surf, WHITE, (int(sx(22)),int(sy(8))), int(sy(4)))
        pygame.draw.circle(surf, BLACK, (int(sx(23)),int(sy(9))), int(sy(2)))
        pygame.draw.polygon(
            surf,(255,160,0),
            [(int(sx(28)),int(sy(12+wing))),
             (int(sx(34)),int(sy(12))),
             (int(sx(28)),int(sy(14-wing)))]
        )
        frames.append(surf)
    return frames

bird_frames = make_bird_frames(SKINS[save["skin"]]["color"])
bird_frame = 0

# ================== SHOP ==================
def shop():
    global bird_frames
    while True:
        screen.fill(SKY)
        screen.blit(big.render("SHOP",True,WHITE),(W//2-40,40))
        screen.blit(small.render(f"Coins: {save['coins']}",True,WHITE),(10,10))

        y = 150
        for name,data in SKINS.items():
            rect = pygame.Rect(W//2-120,y,240,60)
            pygame.draw.rect(screen,WHITE,rect,2)

            label = name.upper()
            if save["skin"] == name:
                label += " (EQUIPPED)"
            else:
                label += f" - {data['price']}c"

            screen.blit(small.render(label,True,WHITE),(rect.x+10,rect.y+18))

            for e in pygame.event.get():
                if e.type == pygame.QUIT: quit()
                if e.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(e.pos):
                    if data["price"] <= save["coins"]:
                        save["coins"] -= data["price"]
                        save["skin"] = name
                        bird_frames = make_bird_frames(data["color"])
                        save_game()
            y += 80

        screen.blit(small.render("ESC to return",True,WHITE),(W//2-70,H-40))
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return

        pygame.display.update()
        clock.tick(60)

# ================== GAME ==================
def game():
    global bird_frame

    bird_y = H / 2
    vel = 0.0

    gravity = 0.45 * H / BASE_H
    jump = -8.0 * H / BASE_H

    pipe_x = W
    pipe_w = int(sx(60))
    gap = int(sy(180))
    pipe_h = random.randint(int(sy(120)),int(sy(360)))
    speed = 2.5 * W / BASE_W

    score = 0
    coins_gained = 0
    alive = True

    while True:
        clock.tick(60)
        screen.fill(SKY)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: quit()
            if alive and e.type in (pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN):
                vel = jump

        # ---- PHYSICS (REAL GRAVITY) ----
        vel += gravity
        bird_y += vel

        bird_frame = (bird_frame+1)%len(bird_frames)
        bird = bird_frames[bird_frame]
        bird_rect = bird.get_rect(center=(int(sx(90)),int(bird_y)))

        # ---- PIPES ----
        pipe_x -= speed
        if pipe_x < -pipe_w:
            pipe_x = W
            pipe_h = random.randint(int(sy(120)),int(sy(360)))
            score += 1
            if score % 10 == 0:
                save["coins"] += 100
                coins_gained += 100
                save_game()

        top = pygame.Rect(pipe_x,0,pipe_w,pipe_h)
        bot = pygame.Rect(pipe_x,pipe_h+gap,pipe_w,H)

        pygame.draw.rect(screen,GREEN,top)
        pygame.draw.rect(screen,GREEN,bot)

        if bird_rect.colliderect(top) or bird_rect.colliderect(bot) or bird_y<0 or bird_y>H:
            break

        screen.blit(bird,bird_rect)
        screen.blit(small.render(str(score),True,WHITE),(W//2,20))

        pygame.display.update()

    game_over(score,coins_gained)

# ================== GAME OVER ==================
def game_over(score,coins):
    while True:
        screen.fill(SKY)
        screen.blit(big.render("GAME OVER",True,WHITE),(W//2-110,200))
        screen.blit(mid.render(f"Score: {score}",True,WHITE),(W//2-80,270))
        screen.blit(mid.render(f"+{coins} coins",True,WHITE),(W//2-90,310))
        screen.blit(small.render("SPACE retry | S shop",True,WHITE),(W//2-120,380))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: return
                if e.key == pygame.K_s: shop()

        pygame.display.update()
        clock.tick(60)

# ================== MAIN ==================
while True:
    screen.fill(SKY)
    screen.blit(big.render("SIMPLY BIRD",True,WHITE),(W//2-120,260))
    screen.blit(mid.render("SPACE to start",True,WHITE),(W//2-110,330))
    screen.blit(small.render("S = Shop",True,WHITE),(W//2-40,370))

    for e in pygame.event.get():
        if e.type == pygame.QUIT: quit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE: game()
            if e.key == pygame.K_s: shop()

    pygame.display.update()
    clock.tick(60)
