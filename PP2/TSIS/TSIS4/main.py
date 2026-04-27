import pygame, random, json, db, datetime

pygame.init()
W, H, TS = 640, 480, 20
screen = pygame.display.set_mode((W, H))
font = pygame.font.SysFont("Arial", 24)

try:
    with open("settings.json") as f: settings = json.load(f)
except: settings = {"snake_color": [0, 255, 0], "grid": True, "sound": True}
db.init_db()

def draw_text(t, x, y, c=(255,255,255)): screen.blit(font.render(t, True, c), (x, y))

class Game:
    def __init__(self, username):
        self.username = username
        self.pid = db.get_player_id(username)
        self.pb = db.get_personal_best(self.pid)
        self.reset()

    def reset(self):
        self.snake = [[100, 100], [80, 100], [60, 100]]
        self.dir = [TS, 0]
        self.score, self.level, self.speed, self.shield = 0, 1, 10, False
        self.walls = []
        self.food = self.spawn_item()
        self.poison = self.spawn_item()
        self.pu = None
        self.pu_time = 0
        self.running = True

    def spawn_item(self):
        while True:
            p = [random.randrange(0, W, TS), random.randrange(0, H, TS)]
            if p not in self.snake and p not in self.walls: return p

    def update(self):
        now = pygame.time.get_ticks()
        new_head = [self.snake[0][0] + self.dir[0], self.snake[0][1] + self.dir[1]]
        
        if self.shield and (new_head[0] < 0 or new_head[0] >= W or new_head[1] < 0 or new_head[1] >= H or new_head in self.snake[1:] or new_head in self.walls):
            self.shield = False
            return
        if new_head[0] < 0 or new_head[0] >= W or new_head[1] < 0 or new_head[1] >= H or new_head in self.snake[1:] or new_head in self.walls:
            self.running = False; return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            if self.score % 5 == 0: 
                self.level += 1; self.speed += 2
                if self.level >= 3:
                    self.walls = [self.spawn_item() for _ in range(self.level * 2)]
            self.food = self.spawn_item()
        elif new_head == self.poison:
            self.snake = self.snake[:-3]
            if len(self.snake) <= 1: self.running = False
            self.poison = self.spawn_item()
        elif self.pu and new_head == self.pu[0]:
            if self.pu[1] == 'S': self.speed += 5
            elif self.pu[1] == 'L': self.speed = max(5, self.speed - 5)
            elif self.pu[1] == 'H': self.shield = True
            self.pu, self.pu_time = None, now + 5000 if self.pu[1] != 'H' else 0
        else: self.snake.pop()

        if not self.pu and random.random() < 0.01:
            self.pu = [self.spawn_item(), random.choice(['S', 'L', 'H']), now]
        if self.pu and now - self.pu[2] > 8000: self.pu = None
        if self.pu_time and now > self.pu_time:
            self.speed = 10 + (self.level - 1) * 2
            self.pu_time = 0

    def draw(self):
        screen.fill((0, 0, 0))
        if settings["grid"]:
            for x in range(0, W, TS): pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, H))
            for y in range(0, H, TS): pygame.draw.line(screen, (40, 40, 40), (0, y), (W, y))
        for p in self.snake: pygame.draw.rect(screen, settings["snake_color"], (*p, TS, TS))
        pygame.draw.rect(screen, (255, 0, 0), (*self.food, TS, TS))
        pygame.draw.rect(screen, (100, 0, 0), (*self.poison, TS, TS))
        for w in self.walls: pygame.draw.rect(screen, (150, 150, 150), (*w, TS, TS))
        if self.pu: pygame.draw.rect(screen, (0, 0, 255), (*self.pu[0], TS, TS))
        draw_text(f"Score: {self.score} Level: {self.level} PB: {self.pb}", 5, 5)
        if self.shield: draw_text("SHIELD", 5, 30, (0, 255, 255))
        pygame.display.flip()

def menu():
    user = "Player"
    while True:
        screen.fill((0, 0, 0))
        draw_text("SNAKE GAME", 50, 20, (0, 255, 0))
        draw_text(f"Enter Nickname: {user}", 50, 80)
        draw_text("1. Play  2. Leaderboard  3. Settings  4. Quit", 50, 150)
        draw_text("(Type to change nickname, Backspace to delete)", 50, 200, (150, 150, 150))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: game_loop(user)
                elif e.key == pygame.K_2: leaderboard()
                elif e.key == pygame.K_3: settings_screen()
                elif e.key == pygame.K_4: return
                elif e.key == pygame.K_BACKSPACE: user = user[:-1]
                elif e.unicode.isalnum() or e.unicode in ' _-':
                    if len(user) < 15: user += e.unicode

def game_loop(user):
    g = Game(user)
    clock = pygame.time.Clock()
    while g.running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and g.dir[1] == 0: g.dir = [0, -TS]
                if e.key == pygame.K_DOWN and g.dir[1] == 0: g.dir = [0, TS]
                if e.key == pygame.K_LEFT and g.dir[0] == 0: g.dir = [-TS, 0]
                if e.key == pygame.K_RIGHT and g.dir[0] == 0: g.dir = [TS, 0]
        g.update()
        g.draw()
        clock.tick(g.speed)
    db.save_session(g.pid, g.score, g.level)
    game_over(g)

def game_over(g):
    while True:
        screen.fill((0, 0, 0))
        draw_text(f"GAME OVER! Score: {g.score} Level: {g.level}", 50, 50)
        draw_text(f"PB: {max(g.pb, g.score)}", 50, 80)
        draw_text("R. Retry  M. Main Menu", 50, 150)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: game_loop(g.username); return
                if e.key == pygame.K_m: return

def leaderboard():
    scores = db.get_top_10()
    while True:
        screen.fill((0, 0, 0))
        draw_text("LEADERBOARD (Top 10)", 50, 30)
        for i, s in enumerate(scores):
            draw_text(f"{i+1}. {s[0]} - {s[1]} (Lvl {s[2]})", 50, 70 + i*30)
        draw_text("C. Clear All  B. Back", 50, 400)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_b: return
                if e.key == pygame.K_c:
                    db.clear_leaderboard()
                    scores = []

def settings_screen():
    global settings
    while True:
        screen.fill((0, 0, 0))
        draw_text(f"G. Grid: {'ON' if settings['grid'] else 'OFF'}", 50, 50)
        draw_text(f"S. Sound: {'ON' if settings['sound'] else 'OFF'}", 50, 100)
        draw_text(f"C. Color: {settings['snake_color']}", 50, 150)
        draw_text("B. Save & Back", 50, 250)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_g: settings["grid"] = not settings["grid"]
                if e.key == pygame.K_s: settings["sound"] = not settings["sound"]
                if e.key == pygame.K_c: settings["snake_color"] = [random.randint(0,255) for _ in range(3)]
                if e.key == pygame.K_b:
                    with open("settings.json", "w") as f: json.dump(settings, f)
                    return

menu()
pygame.quit()
