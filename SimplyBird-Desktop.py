import pygame, random, json, os

pygame.init()

# ================== WINDOW ==================
BASE_W, BASE_H = 400, 600
W, H = 400, 600
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
    "red":    {"color": (255,80,80),  "price": 200},
    "blue":   {"color": (80,120,255), "price": 500},
    "purple": {"color": (180,80,255), "price": 1000},
    "black": {"color": (0,0,0), "price": 1000}
}

# ================== SAVE ==================
SAVE_FILE = "save.json"
def load_save():
    if os.path.exists(SAVE_FILE):
        return json.load(open(SAVE_FILE))
    return {"coins": 200, "skin": "yellow"}
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
        screen.blit(big.render("SHOP", True, WHITE), (W//2-40, 40))
        screen.blit(small.render(f"Coins: {save['coins']}", True, WHITE), (10, 10))

        y = 150
        for name, data in SKINS.items():
            rect = pygame.Rect(W//2-120, y, 240, 60)
            pygame.draw.rect(screen, WHITE, rect, 2)

            label = name.upper()
            if save["skin"] == name:
                label += " (EQUIPPED)"
            else:
                label += f" - {data['price']}c"

            screen.blit(small.render(label, True, WHITE), (rect.x+10, rect.y+18))
            y += 80

        screen.blit(small.render("ESC to return", True, WHITE), (W//2-70, H-40))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: quit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
            if e.type == pygame.MOUSEBUTTONDOWN:
                y_check = 150
                for name, data in SKINS.items():
                    rect = pygame.Rect(W//2-120, y_check, 240, 60)
                    if rect.collidepoint(e.pos):
                        if data["price"] <= save["coins"]:
                            save["coins"] -= data["price"]
                            save["skin"] = name
                            bird_frames = make_bird_frames(data["color"])
                            save_game()
                    y_check += 80

        pygame.display.update()
        clock.tick(60)

# ================== GAME ==================
def game():
    global bird_frame, bird_frames

    bird_y = H / 2
    vel = 0.0
    gravity = 0.45 * H / BASE_H
    jump = -8.0 * H / BASE_H

    pipe_w = int(sx(60))
    gap = int(sy(180))
    pipe_speed = 2.5 * W / BASE_W

    score = 0
    coins_gained = 0

    # Initial Pipes
    pipes = []
    pipe_timer = 0

    alive = True
    while True:
        clock.tick(60)
        screen.fill(SKY)

        # --- Events ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT: quit()
            if alive and e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                vel = jump

        # --- Bird Physics ---
        vel += gravity
        bird_y += vel
        bird_frame = (bird_frame+1)%len(bird_frames)
        bird = bird_frames[bird_frame]
        bird_rect = bird.get_rect(center=(int(sx(90)),int(bird_y)))

        # --- Pipes Timer & Generation ---
        pipe_timer += 1
        if pipe_timer > 90:
            height = random.randint(int(sy(120)), int(sy(360)))
            pipes.append({"rect": pygame.Rect(W, 0, pipe_w, height), "top": True})
            pipes.append({"rect": pygame.Rect(W, height+gap, pipe_w, H-height-gap), "top": False})
            pipe_timer = 0

        # --- Move Pipes & Check Collision ---
        for pipe in pipes:
            pipe["rect"].x -= pipe_speed

        # Remove off-screen pipes
        pipes = [p for p in pipes if p["rect"].right > 0]

        # --- Collision ---
        for pipe in pipes:
            if bird_rect.colliderect(pipe["rect"]):
                alive = False
        if bird_y < 0 or bird_y > H: alive = False

        # --- Draw Pipes Mario-Style ---
        for pipe in pipes:
            r = pipe["rect"]
            pygame.draw.rect(screen, GREEN, r, border_radius=12)
            # Mütze oben
            if pipe["top"]:
                pygame.draw.rect(screen, (0,180,0), (r.x, r.height-10, r.width, 10), border_radius=4)
            else:
                pygame.draw.rect(screen, (0,180,0), (r.x, r.y, r.width, 10), border_radius=4)

        # --- Draw Bird ---
        screen.blit(bird, bird_rect)

        # --- Score ---
        if alive:
            score += 0.01
        screen.blit(small.render(str(int(score)), True, WHITE), (W//2, 20))

        pygame.display.update()

        if not alive:
            save["coins"] += coins_gained
            save_game()
            game_over(int(score), coins_gained)
            return

# ================== GAME OVER ==================
def game_over(score, coins):
    while True:
        screen.fill(SKY)
        screen.blit(big.render("GAME OVER", True, WHITE), (W//2-110, 200))
        screen.blit(mid.render(f"Score: {score}", True, WHITE), (W//2-80, 270))
        screen.blit(mid.render(f"+{coins} coins", True, WHITE), (W//2-90, 310))
        screen.blit(small.render("SPACE retry | S shop", True, WHITE), (W//2-120, 380))

        for e in pygame.event.get():
            if e.type == pygame.QUIT: quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: return
                if e.key == pygame.K_s: shop()

        pygame.display.update()
        clock.tick(60)

# ================== MAIN MENU WITH DEMO ==================
def main_menu():
    bird = pygame.Rect(100, H//2, 30, 30)
    bird_vel = 0
    gravity = 0.5
    pipes = []
    pipe_width = 60
    gap = 150
    pipe_speed = 3
    pipe_timer = 0

    while True:
        screen.fill(SKY)
        screen.blit(big.render("SIMPLY BIRD", True, WHITE), (W//2-120, 260))
        screen.blit(mid.render("SPACE to start", True, WHITE), (W//2-110, 330))
        screen.blit(small.render("S = Shop", True, WHITE), (W//2-40, 370))

        pipe_timer += 1
        if pipe_timer > 90:
            height = random.randint(150, H-150)
            pipes.append(pygame.Rect(W, 0, pipe_width, height - gap//2))
            pipes.append(pygame.Rect(W, height + gap//2, pipe_width, H - (height + gap//2)))
            pipe_timer = 0

        # --- Events ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT: quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: game()
                if e.key == pygame.K_s: shop()

        # --- Demo Bird ---
        bird_vel += gravity
        bird.y += bird_vel

        for pipe in pipes:
            pipe.x -= pipe_speed
        pipes = [p for p in pipes if p.right > 0]

        for pipe in pipes:
            if bird.colliderect(pipe):
                bird.y = H//2
                bird_vel = 0
                pipes.clear()
                break
        if bird.top < 0 or bird.bottom > H:
            bird.y = H//2
            bird_vel = 0
            pipes.clear()

        pygame.draw.rect(screen, (255,255,0), bird)
        for pipe in pipes:
            pygame.draw.rect(screen, (0,200,0), pipe)

        pygame.display.update()
        clock.tick(60)

# ================== START ==================
main_menu()
