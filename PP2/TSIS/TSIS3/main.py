import pygame, random, json, os

pygame.init()
W, H = 400, 600
screen = pygame.display.set_mode((W, H))
font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

def load_j(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d

settings = load_j("settings.json", {"sound": True, "color": (0, 0, 255), "diff": 1})
leaderboard = load_j("leaderboard.json", [])

def save_j(p, d):
    with open(p, "w") as f: json.dump(d, f)

def draw_t(t, x, y, c=(255, 255, 255)): screen.blit(font.render(t, True, c), (x, y))

class Obj(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, c, s, t):
        super().__init__()
        self.image = pygame.Surface((w, h)); self.image.fill(c)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed, self.type = s, t
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > H: self.kill()

class Game:
    def __init__(self, name):
        self.name, self.score, self.dist, self.level = name, 0, 0, 1
        self.player = Obj(W//2, H-50, 30, 50, settings["color"], 0, 'P')
        self.sprites = pygame.sprite.Group(self.player)
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.shield = False; self.nitro = 0

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return False
            
            keys = pygame.key.get_pressed()
            move = 5 + (3 if self.nitro > 0 else 0)
            if keys[pygame.K_LEFT] and self.player.rect.left > 0: self.player.rect.x -= move
            if keys[pygame.K_RIGHT] and self.player.rect.right < W: self.player.rect.x += move
            
            if random.random() < 0.02 * self.level:
                x, t = random.choice([50, 150, 250, 350]), random.choice(['E', 'O', 'C', 'N', 'S', 'R'])
                if t == 'E': o = Obj(x, -50, 30, 50, (255, 0, 0), 4 + self.level, 'enemy')
                elif t == 'O': o = Obj(x, -50, 40, 40, (100, 100, 100), 3 + self.level, 'enemy')
                elif t == 'C': o = Obj(x, -50, 20, 20, (255, 215, 0), 3, 'coin')
                elif t == 'N': o = Obj(x, -50, 20, 20, (0, 255, 0), 3, 'nitro')
                elif t == 'S': o = Obj(x, -50, 20, 20, (0, 255, 255), 3, 'shield')
                else: o = Obj(x, -50, 20, 20, (255, 0, 255), 3, 'repair')
                
                if not any(o.rect.colliderect(s.rect) for s in self.sprites):
                    self.sprites.add(o)
                    if o.type == 'enemy': self.enemies.add(o)
                    else: self.items.add(o)

            for s in self.sprites:
                if s != self.player: s.update()
            
            if pygame.sprite.spritecollide(self.player, self.enemies, True):
                if self.shield: self.shield = False
                else: break
            
            for it in pygame.sprite.spritecollide(self.player, self.items, True):
                if it.type == 'coin': self.score += 10
                elif it.type == 'nitro': self.nitro = 180
                elif it.type == 'shield': self.shield = True
                elif it.type == 'repair': self.enemies.empty()
            
            if self.nitro > 0: self.nitro -= 1
            self.dist += 1
            if self.dist % 1000 == 0: self.level += 1

            screen.fill((50, 50, 50))
            for i in range(1, 4): pygame.draw.line(screen, (100, 100, 100), (i*100, 0), (i*100, H), 2)
            self.sprites.draw(screen)
            draw_t(f"Score: {self.score} Dist: {self.dist//10}m Lvl: {self.level}", 10, 10)
            if self.shield: draw_t("SHIELD ACTIVE", 10, 30, (0, 255, 255))
            if self.nitro > 0: draw_t(f"NITRO: {self.nitro//60}s", 10, 50, (0, 255, 0))
            pygame.display.flip()
            clock.tick(60)
        
        leaderboard.append({"name": self.name, "score": self.score, "dist": self.dist//10})
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        save_j("leaderboard.json", leaderboard[:10])
        return self.game_over()

    def game_over(self):
        while True:
            screen.fill((0, 0, 0))
            draw_t("GAME OVER", 150, 200, (255, 0, 0))
            draw_t(f"Score: {self.score} Dist: {self.dist//10}m", 130, 250)
            draw_t("Press R to Retry or M for Menu", 80, 350)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r: return Game(self.name).run()
                    if e.key == pygame.K_m: return True

def main():
    global settings
    name = "Player"
    while True:
        screen.fill((0, 0, 0))
        draw_t("RACER GAME", 140, 100, (255, 255, 0))
        draw_t(f"Name: {name}", 140, 150)
        draw_t("1. Play  2. Leaderboard  3. Settings  4. Quit", 50, 250)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: 
                    if not Game(name).run(): return
                elif e.key == pygame.K_2:
                    while True:
                        screen.fill((0, 0, 0)); draw_t("LEADERBOARD", 140, 50)
                        for i, x in enumerate(leaderboard[:10]):
                            draw_t(f"{i+1}. {x['name']}: {x['score']} ({x['dist']}m)", 80, 100+i*30)
                        draw_t("Press B for Back", 130, 500); pygame.display.flip()
                        ev = pygame.event.wait()
                        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_b: break
                elif e.key == pygame.K_3:
                    while True:
                        screen.fill((0, 0, 0)); draw_t("SETTINGS", 150, 100)
                        draw_t(f"C. Color: {settings['color']}", 80, 200)
                        draw_t(f"S. Sound: {'ON' if settings['sound'] else 'OFF'}", 80, 250)
                        draw_t("B. Back", 80, 350); pygame.display.flip()
                        ev = pygame.event.wait()
                        if ev.type == pygame.KEYDOWN:
                            if ev.key == pygame.K_c: settings["color"] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                            elif ev.key == pygame.K_s: settings["sound"] = not settings["sound"]
                            elif ev.key == pygame.K_b: save_j("settings.json", settings); break
                elif e.key == pygame.K_4: return
                elif e.key == pygame.K_BACKSPACE: name = name[:-1]
                elif len(name) < 10 and e.unicode.isalnum(): name += e.unicode

if __name__ == "__main__": main(); pygame.quit()
