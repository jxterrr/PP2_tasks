import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

colors = [BLACK, RED, GREEN, BLUE, YELLOW]
current_color = BLACK

brush_sizes = [4, 8, 16]
current_size = brush_sizes[0]

eraser = False
mode = "brush"  # brush, rect, circle

drawing = False
last_pos = None
start_pos = None

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

font = pygame.font.SysFont(None, 24)

def draw_ui():
    # Color buttons
    for i, color in enumerate(colors):
        pygame.draw.rect(screen, color, (10 + i*50, 10, 40, 40))
    
    # Brush size buttons
    for i, size in enumerate(brush_sizes):
        pygame.draw.rect(screen, BLACK, (10 + i*50, 60, 40, 40), 2)
        pygame.draw.circle(screen, BLACK, (30 + i*50, 80), size)
    
    # Eraser button
    pygame.draw.rect(screen, (200, 200, 200), (10, 110, 100, 40))
    text = font.render("Eraser", True, BLACK)
    screen.blit(text, (20, 120))

    # Clear button
    pygame.draw.rect(screen, (220, 220, 220), (10, 160, 100, 40))
    text2 = font.render("Clear", True, BLACK)
    screen.blit(text2, (25, 170))

    # Rectangle button
    pygame.draw.rect(screen, (200, 200, 255), (10, 210, 100, 40))
    text3 = font.render("Rect", True, BLACK)
    screen.blit(text3, (30, 220))

    # Circle button
    pygame.draw.rect(screen, (200, 255, 200), (10, 260, 100, 40))
    text4 = font.render("Circle", True, BLACK)
    screen.blit(text4, (25, 270))

running = True
while running:
    screen.fill(WHITE)
    screen.blit(canvas, (0, 0))
    draw_ui()

    # Preview shape while drawing
    if drawing and start_pos and mode in ["rect", "circle"]:
        current_pos = pygame.mouse.get_pos()
        color = WHITE if eraser else current_color
        if mode == "rect":
            rect = pygame.Rect(start_pos, (current_pos[0]-start_pos[0], current_pos[1]-start_pos[1]))
            pygame.draw.rect(screen, color, rect, current_size)
        elif mode == "circle":
            radius = int(((current_pos[0]-start_pos[0])**2 + (current_pos[1]-start_pos[1])**2)**0.5)
            pygame.draw.circle(screen, color, start_pos, radius, current_size)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                eraser = not eraser
            if event.key == pygame.K_r:
                mode = "rect"
                eraser = False
            if event.key == pygame.K_c:
                mode = "circle"
                eraser = False
            if event.key == pygame.K_SPACE:
                running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            # Color selection
            for i, color in enumerate(colors):
                if pygame.Rect(10 + i*50, 10, 40, 40).collidepoint(x, y):
                    current_color = color
                    eraser = False
                    mode = "brush"
            
            # Brush size selection
            for i, size in enumerate(brush_sizes):
                if pygame.Rect(10 + i*50, 60, 40, 40).collidepoint(x, y):
                    current_size = size
            
            # Eraser
            if pygame.Rect(10, 110, 100, 40).collidepoint(x, y):
                eraser = True
                mode = "brush"

            # Clear canvas
            if pygame.Rect(10, 160, 100, 40).collidepoint(x, y):
                canvas.fill(WHITE)

            # Rectangle mode
            if pygame.Rect(10, 210, 100, 40).collidepoint(x, y):
                mode = "rect"
                eraser = False

            # Circle mode
            if pygame.Rect(10, 260, 100, 40).collidepoint(x, y):
                mode = "circle"
                eraser = False
            
            drawing = True
            last_pos = event.pos
            start_pos = event.pos
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing and start_pos:
                end_pos = event.pos
                color = WHITE if eraser else current_color
                if mode == "rect":
                    rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                    pygame.draw.rect(canvas, color, rect, current_size)
                elif mode == "circle":
                    radius = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5)
                    pygame.draw.circle(canvas, color, start_pos, radius, current_size)
            drawing = False
            last_pos = None
            start_pos = None
        
        elif event.type == pygame.MOUSEMOTION and drawing:
            if mode == "brush":
                if last_pos:
                    color = WHITE if eraser else current_color
                    pygame.draw.line(canvas, color, last_pos, event.pos, current_size)
                last_pos = event.pos
    
    pygame.display.flip()

pygame.quit()
sys.exit()