import pygame
import random
import sys

SC_WIDTH, SC_HEIGHT = 800, 800
FPS = 100
BG_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
BUTTON_COLOR = (64, 0, 20)  
BUTTON_HOVER_COLOR = (130, 0, 32) 
TEXT_COLOR = (204, 197, 182)

# --- Initialization ---
pygame.init()
pygame.display.set_caption("Adrenaline Highway")
window = pygame.display.set_mode((SC_WIDTH, SC_HEIGHT), pygame.DOUBLEBUF)
clock = pygame.time.Clock()

# --- Load assets (do this *once*, outside of any loops) ---
road = pygame.image.load('imgs/road.png').convert()
backG = pygame.transform.scale(road, (SC_WIDTH, SC_HEIGHT))

menu_bg = pygame.image.load('imgs/menu_bg.jpg').convert()  
menu_bg = pygame.transform.scale(menu_bg, (SC_WIDTH, SC_HEIGHT)) 

Car_p = pygame.image.load('imgs/Car.png').convert_alpha()
player_car = pygame.transform.scale(Car_p, (150, 150))
player_mask = pygame.mask.from_surface(player_car)
car_rect = player_car.get_rect()
car_rect.center = (SC_WIDTH // 2, SC_HEIGHT - 150)

# Enemy car images (loading and scaling) - do this *once*
Car = pygame.image.load('imgs/Mini_truck.png').convert_alpha()
car1 = pygame.transform.scale(Car, (150, 150))
Car = pygame.image.load('imgs/Black_viper.png').convert_alpha()
car2 = pygame.transform.scale(Car, (150, 150))
Car = pygame.image.load('imgs/Ambulance.png').convert_alpha()
car3 = pygame.transform.scale(Car, (150, 150))
Car = pygame.image.load('imgs/Mini_van.png').convert_alpha()
car4 = pygame.transform.scale(Car, (150, 150))
Car = pygame.image.load('imgs/taxi.png').convert_alpha()
taxi = pygame.transform.scale(Car, (150, 150))
Cars = [car1, car2, car3, car4, taxi]

# --- Sound Loading ---
pygame.mixer.init()
engine_sound = pygame.mixer.Sound('sounds/car_engine.wav')
engine_sound.set_volume(0.5)

crach_sound = pygame.mixer.Sound('sounds/crach.wav')
crach_sound.set_volume(.2)

Game_music = pygame.mixer.Sound('sounds/game_music.wav')
Game_music.set_volume(.2)
# --- Game Variables (Reset these for each new game) ---

def reset_game():
    """Resets all game variables to their initial state."""
    global game_over, score, time, computer_cars, bg1_y, bg2_y, car_rect, scroll_speed, FPS
    game_over = False
    score = 0
    time = 1
    computer_cars = []
    bg1_y = 0
    bg2_y = -SC_HEIGHT
    car_rect.center = (SC_WIDTH // 2, SC_HEIGHT - 150)  
    scroll_speed = 5
    FPS = 100


# --- Helper Functions ---

def draw_text(text, font, color, surface, x, y, centered=False):
    """Draws text to the screen.  Optionally centers it."""
    textobj = font.render(text, True, color)  
    textrect = textobj.get_rect()
    if centered:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def bg_move():
    global bg1_y, bg2_y, score, time, scroll_speed, FPS
    bg1_y += scroll_speed
    bg2_y += scroll_speed

    if bg1_y >= SC_HEIGHT:
        bg1_y = -SC_HEIGHT
        score += time
        time += 1
    if bg2_y >= SC_HEIGHT:
        bg2_y = -SC_HEIGHT
        score += time
        time += 1
        FPS += 1 

    window.blit(backG, (0, bg1_y))
    window.blit(backG, (0, bg2_y))

def move_player_car(key):
    adge = 100
    car_speed = 2 
    if key[pygame.K_LEFT] or key[pygame.K_a]:
        car_rect.x -= car_speed
    if key[pygame.K_RIGHT] or key[pygame.K_d]:
        car_rect.x += car_speed

    # Keep car within bounds. More readable this way.
    car_rect.left = max(car_rect.left, adge + 5)
    car_rect.right = min(car_rect.right, SC_WIDTH - adge - 5)



def Cars_frontD(cars_list):
    global computer_cars, craet_timer, creat_RATE, game_over, score
    craet_timer += 1
    if craet_timer >= creat_RATE:
        craet_timer = 0
        selected_car = random.choice(cars_list)
        new_car = {
            "rect": pygame.Rect(random.choice([150, 270, 390, 510]), -150, 150, 150),
            "image": selected_car,
            "mask": pygame.mask.from_surface(selected_car),
            "speed": scroll_speed + random.choice([1, 1.5, 2.5, 3.5]) #controle the speed
        }
        # so biscly here with some math we look for the distance between the created car
        # and the next one that we want to creat is it good or not (to avoid the stuck)
        min_distance = 100 #the distance bettwen each car
        if any(abs(new_car["rect"].x - c["rect"].x) < 100 and new_car["rect"].y > c["rect"].y - min_distance
               for c in computer_cars):
            pass
        else:
            computer_cars.append(new_car)

    for car in computer_cars[:]:
        window.blit(car["image"], car["rect"])
        car["rect"].y += car["speed"]

        if car["rect"].y > SC_HEIGHT:
            computer_cars.remove(car)
            #score += 1  # Score increases when a car passes, not per frame *per car*.

        offset_x = car["rect"].x - car_rect.x
        offset_y = car["rect"].y - car_rect.y
        if car["rect"].colliderect(car_rect):
            if player_mask.overlap(car["mask"], (offset_x, offset_y)):
                crach_sound.play()
                print("Game Over!")
                engine_sound.stop()  # Stop engine sound on game over
                Game_music.stop()
                game_over = True
                return  # Exit the function immediately

def draw_game_over():
    # Game Over Screen:  More visually appealing
    window.fill(BG_COLOR)  # Clear screen
    draw_text("Game Over", font, RED, window, SC_WIDTH // 2, SC_HEIGHT // 3, centered=True)
    draw_text(f"Final Score: {score}", font, WHITE, window, SC_WIDTH // 2, SC_HEIGHT // 2, centered=True)
    draw_text("Press SPACE to Restart", font, WHITE, window, SC_WIDTH//2, SC_HEIGHT * 2//3, centered=True)
    pygame.display.flip()  # Update the display *once* for the game over screen


# --- Button Class ---

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = pygame.font.Font(None, 48)  # Use a larger font for buttons
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        draw_text(self.text, self.font, TEXT_COLOR, surface, self.rect.centerx, self.rect.centery, centered=True)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # Left mouse button
                if self.action:
                    self.action()

# --- Menu Functions ---

def start_game():
    reset_game()
    engine_sound.play(-1)
    global main_menu_active
    main_menu_active = False  # Hide the main menu

def how_to_play_menu():
    running = True
    while running:
        window.fill(BG_COLOR)
        draw_text("How to Play", font, WHITE, window, SC_WIDTH // 2, 50, centered=True)
        instructions = [
            "Use arrow keys (or A/D) to move the car.",
            "Avoid colliding with other cars.",
            "The game gets faster as you score!",
            "Press ESC to return to the main menu."
        ]
        y_offset = 150
        for line in instructions:
            draw_text(line, font_small, WHITE, window, SC_WIDTH // 2, y_offset, centered=True)
            y_offset += 40

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Return to main menu

        pygame.display.flip()
        clock.tick(FPS)
        
def draw_score():
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # White color
    window.blit(score_text, (10, 10))  # Position of the score


def draw_high_score():
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    window.blit(high_score_text, (10, 50))  # Position of the high score


def main_menu():
    global main_menu_active  # Use the global variable
    main_menu_active = True
    Game_music.play(-1)

    # Create buttons (using our Button class)
    start_button = Button("Start Game", SC_WIDTH // 2 - 150, 200, 300, 60, BUTTON_COLOR, BUTTON_HOVER_COLOR, start_game)
    how_to_play_button = Button("How to Play", SC_WIDTH // 2 - 150, 300, 300, 60, BUTTON_COLOR, BUTTON_HOVER_COLOR, how_to_play_menu)
    quit_button = Button("Quit", SC_WIDTH // 2 - 150, 400, 300, 60, BUTTON_COLOR, BUTTON_HOVER_COLOR, sys.exit)

    buttons = [start_button, how_to_play_button, quit_button]

    while main_menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.handle_event(event)

        # Check for mouse hover
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.check_hover(mouse_pos)

        # --- Drawing ---
        window.blit(menu_bg, (0,0))
        draw_text("Adrenaline Highway", font_large, ORANGE, window, SC_WIDTH // 2, 100, centered=True)

        for button in buttons:
            button.draw(window)

        pygame.display.flip()
        clock.tick(FPS)



# --- Fonts ---
font = pygame.font.Font(None, 60)
font_small = pygame.font.Font(None, 36)  # Smaller font for instructions
font_large = pygame.font.Font(None, 100)

# High score handling
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except FileNotFoundError:
    high_score = 0
    
craet_timer = 0
creat_RATE = 100
# --- Main Game Loop ---
reset_game()
main_menu()  # Start with the main menu
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if game_over: #to let him back to the game by hit space
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    engine_sound.play(-1)
                    Game_music.play(-1)
                    
    if not game_over:
        window.fill(BG_COLOR)
        bg_move()
        keys = pygame.key.get_pressed()
        move_player_car(keys)
        window.blit(player_car, car_rect)
        draw_score()
        draw_high_score()
        Cars_frontD(Cars)
    else:
        draw_game_over() # dispaly the game over and the score 
        
    pygame.display.flip()
    clock.tick(FPS)
    
     # Save high score
    if score > high_score:
        high_score = score
        with open("highscore.txt", "w") as f:
            f.write(str(high_score))

pygame.quit()
sys.exit()