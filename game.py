import pygame
import math
import sys

# Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(", Drive & Shoot")
clock = pygame.time.Clock()

# Colors
GREEN = (34, 139, 34)
GRAY = (50, 50, 50)
PLAYER_COLOR = (0, 0, 255)
CAR_COLOR = (255, 0, 0)
BULLET_COLOR = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)

# Game State Variables
is_driving = False

# Player Variables (Walking State)
player_x, player_y = 200, 500
player_speed = 4
player_angle = 0

# Car Variables
car_x, car_y = 500, 400
car_angle = 0
car_speed = 0
car_max_speed = 8
car_accel = 0.2
car_decel = 0.1
car_steer_speed = 3

# Bullets
bullets = [] # List of [x, y, dx, dy]

def draw_rotated_rect(surface, color, center, width, height, angle, front_indicator=False):
    """Helper to draw a rotated player or car looking at a specific angle"""
    rect_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rect_surf.fill(color)
    if front_indicator: # Add a headlight/front marker
        pygame.draw.rect(rect_surf, (255, 255, 255), (width - 10, 0, 10, height))
    rotated_surf = pygame.transform.rotate(rect_surf, -math.degrees(angle))
    new_rect = rotated_surf.get_rect(center=center)
    surface.blit(rotated_surf, new_rect.topleft)

# Main Game Loop
running = True
while running:
    clock.tick(60)
    screen.fill(GREEN)
    
    # Draw a simple road
    pygame.draw.rect(screen, GRAY, (0, 300, SCREEN_WIDTH, 200))
    
    # Mouse tracking for aiming
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = True
            pygame.quit()
            sys.exit()
            
        # Action Inputs
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f: # Enter / Exit Car
                if not is_driving:
                    # Check if close to the car to enter
                    dist = math.hypot(player_x - car_x, player_y - car_y)
                    if dist < 60:
                        is_driving = True
                else:
                    # Exit car and spawn player slightly to the side
                    is_driving = False
                    player_x = car_x + 50 * math.sin(car_angle)
                    player_y = car_y - 50 * math.cos(car_angle)
                    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click to Shoot
                if not is_driving: # Can only shoot while walking in this prototype
                    # Calculate bullet direction based on player angle
                    b_dx = math.cos(player_angle) * 12
                    b_dy = math.sin(player_angle) * 12
                    bullets.append([player_x, player_y, b_dx, b_dy])

    # --- PHYSICS & MOVEMENT ---
    keys = pygame.key.get_pressed()
    
    if not is_driving:
        # 🚶 WALKING MODE CONTROLS
        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_d]: move_x += 1
        
        if move_x != 0 or move_y != 0:
            # Normalize diagonal speed
            length = math.hypot(move_x, move_y)
            player_x += (move_x / length) * player_speed
            player_y += (move_y / length) * player_speed
            
        # Rotate player toward mouse cursor
        player_angle = math.atan2(mouse_y - player_y, mouse_x - player_x)
        
    else:
        # 🚗 DRIVING MODE CONTROLS
        if keys[pygame.K_w]:
            car_speed = min(car_speed + car_accel, car_max_speed)
        elif keys[pygame.K_s]:
            car_speed = max(car_speed - car_accel, -car_max_speed / 2)
        else:
            # Friction deceleration
            if car_speed > 0: car_speed = max(0, car_speed - car_decel)
            if car_speed < 0: car_speed = min(0, car_speed + car_decel)
            
        if car_speed != 0:
            # Can only steer if car is moving
            steer_dir = 1 if car_speed > 0 else -1
            if keys[pygame.K_a]:
                car_angle -= math.radians(car_steer_speed) * steer_dir
            if keys[pygame.K_d]:
                car_angle += math.radians(car_steer_speed) * steer_dir
                
        # Update Car position based on angle and speed
        car_x += car_speed * math.cos(car_angle)
        car_y += car_speed * math.sin(car_angle)
        
        # Keep player locked inside the car
        player_x, player_y = car_x, car_y

    # --- UPDATE BULLETS ---
    for bullet in bullets[:]:
        bullet[0] += bullet[2] # Update X
        bullet[1] += bullet[3] # Update Y
        # Remove bullet if it goes off screen
        if bullet[0] < 0 or bullet[0] > SCREEN_WIDTH or bullet[1] < 0 or bullet[1] > SCREEN_HEIGHT:
            bullets.remove(bullet)

    # --- RENDERING / DRAWING ---
    # 1. Draw Car
    draw_rotated_rect(screen, CAR_COLOR, (int(car_x), int(car_y)), 60, 35, car_angle, front_indicator=True)
    
    # 2. Draw Player (only if not driving)
    if not is_driving:
        draw_rotated_rect(screen, PLAYER_COLOR, (int(player_x), int(player_y)), 30, 20, player_angle, front_indicator=True)
        
    # 3. Draw Bullets
    for bullet in bullets:
        pygame.draw.circle(screen, BULLET_COLOR, (int(bullet[0]), int(bullet[1])), 4)
        
    # 4. Draw UI Texts
    font = pygame.font.SysFont(None, 28)
    txt_ui = "Status: WALKING | Press [W,A,S,D] to move | Mouse to aim | Left Click to shoot" if not is_driving else "Status: DRIVING | Press [W/S] Gas/Brake | [A/D] Steer"
    txt_prompt = "Press [F] to EXIT car" if is_driving else ("Press [F] to ENTER car" if math.hypot(player_x - car_x, player_y - car_y) < 60 else "")
    
    img_ui = font.render(txt_ui, True, TEXT_COLOR)
    img_prompt = font.render(txt_prompt, True, (255, 255, 0))
    screen.blit(img_ui, (20, 20))
    screen.blit(img_prompt, (20, 50))

    pygame.display.flip()
