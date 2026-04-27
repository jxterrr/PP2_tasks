import pygame
import datetime

# Constants
W, H = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Paint TSIS2")
canvas = pygame.Surface((W, H))
canvas.fill(WHITE)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

current_tool = 'pencil'
color = BLACK
brush_size = 2
start_pos = None
drawing = False
text_mode = False
text_pos = (0, 0)
current_text = ""

def flood_fill(surf, pos, fill_color):
    target_color = surf.get_at(pos)
    if target_color == fill_color: return
    
    stack = [pos]
    while stack:
        x, y = stack.pop()
        if not (0 <= x < W and 0 <= y < H): continue
        if surf.get_at((x, y)) != target_color: continue
        
        surf.set_at((x, y), fill_color)
        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])

def draw_shape(surf, tool, start, end, color, size):
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    
    if tool == 'line':
        pygame.draw.line(surf, color, start, end, size)
    elif tool == 'rect':
        pygame.draw.rect(surf, color, (min(x1, x2), min(y1, y2), abs(dx), abs(dy)), size)
    elif tool == 'circle':
        r = int(((dx)**2 + (dy)**2)**0.5)
        pygame.draw.circle(surf, color, start, r, size)
    elif tool == 'square':
        side = max(abs(dx), abs(dy))
        pygame.draw.rect(surf, color, (x1 if dx>0 else x1-side, y1 if dy>0 else y1-side, side, side), size)
    elif tool == 'r_tri':
        pygame.draw.polygon(surf, color, [(x1, y1), (x1, y2), (x2, y2)], size)
    elif tool == 'e_tri':
        h = int(abs(dx) * (3**0.5) / 2)
        pygame.draw.polygon(surf, color, [(x1, y1), (x2, y1), ((x1+x2)//2, y1 - h if dy < 0 else y1 + h)], size)
    elif tool == 'rhombus':
        pygame.draw.polygon(surf, color, [(x1 + dx//2, y1), (x2, y1 + dy//2), (x1 + dx//2, y2), (x1, y1 + dy//2)], size)

running = True
while running:
    screen.fill((200, 200, 200))
    screen.blit(canvas, (0, 0))
    
    info = font.render(f"Tool: {current_tool} | Size: {brush_size} | Color: {color} | Ctrl+S to Save", True, BLACK)
    screen.blit(info, (10, H - 30))

    pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if text_mode:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    txt_surf = font.render(current_text, True, color)
                    canvas.blit(txt_surf, text_pos)
                    text_mode = False
                    current_text = ""
                elif event.key == pygame.K_ESCAPE:
                    text_mode = False
                    current_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    current_text = current_text[:-1]
                else:
                    current_text += event.unicode
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_tool == 'fill':
                flood_fill(canvas, event.pos, color)
            elif current_tool == 'text':
                text_mode = True
                text_pos = event.pos
                current_text = ""
            else:
                drawing = True
                start_pos = event.pos
                if current_tool == 'pencil' or current_tool == 'eraser':
                    pygame.draw.circle(canvas, color if current_tool=='pencil' else WHITE, event.pos, brush_size)

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                if current_tool not in ['pencil', 'eraser']:
                    draw_shape(canvas, current_tool, start_pos, event.pos, color, brush_size)
                drawing = False
        
        if event.type == pygame.MOUSEMOTION and drawing:
            if current_tool == 'pencil' or current_tool == 'eraser':
                pygame.draw.line(canvas, color if current_tool=='pencil' else WHITE, start_pos, event.pos, brush_size * 2)
                start_pos = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                fname = f"save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                pygame.image.save(canvas, fname)
                print(f"Saved as {fname}")
            elif event.key == pygame.K_1: brush_size = 2
            elif event.key == pygame.K_2: brush_size = 5
            elif event.key == pygame.K_3: brush_size = 10
            elif event.key == pygame.K_p: current_tool = 'pencil'
            elif event.key == pygame.K_l: current_tool = 'line'
            elif event.key == pygame.K_r: current_tool = 'rect'
            elif event.key == pygame.K_c: current_tool = 'circle'
            elif event.key == pygame.K_q: current_tool = 'square'
            elif event.key == pygame.K_t: current_tool = 'r_tri'
            elif event.key == pygame.K_e: current_tool = 'e_tri'
            elif event.key == pygame.K_h: current_tool = 'rhombus'
            elif event.key == pygame.K_f: current_tool = 'fill'
            elif event.key == pygame.K_x: current_tool = 'text'
            elif event.key == pygame.K_z: current_tool = 'eraser'
            # Colors
            elif event.key == pygame.K_v: color = RED
            elif event.key == pygame.K_g: color = GREEN
            elif event.key == pygame.K_b: color = BLUE
            elif event.key == pygame.K_k: color = BLACK
            elif event.key == pygame.K_w: color = WHITE

    if drawing and current_tool not in ['pencil', 'eraser']:
        draw_shape(screen, current_tool, start_pos, pos, color, brush_size)
    
    if text_mode:
        txt_surf = font.render(current_text + "|", True, color)
        screen.blit(txt_surf, text_pos)

    # Help text
    help_text = [
        "P:Pencil L:Line R:Rect C:Circle Q:Square T:R-Tri E:E-Tri H:Rhombus",
        "F:Fill X:Text Z:Eraser | 1,2,3:Size | V:Red G:Green B:Blue K:Black W:White",
        "Ctrl+S:Save"
    ]
    for i, line in enumerate(help_text):
        h_surf = font.render(line, True, BLACK)
        screen.blit(h_surf, (10, 10 + i*20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
