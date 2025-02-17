import pygame
import pygame_gui

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Entry Terminal")

# UI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Fonts
font = pygame.font.Font(None, 24)
header_font = pygame.font.Font(None, 28)
title_font = pygame.font.Font(None, 32)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (150, 0, 0)
GREEN = (0, 150, 0)
GRAY = (50, 50, 50)
BLUE = (0, 0, 255)

# User ID Counter
user_id_counter = 0

# Store players (ID, Codename)
red_team = [{"id": f"{i:08d}", "codename": ""} for i in range(20)]
green_team = [{"id": f"{i+20:08d}", "codename": ""} for i in range(20)]
selected_slot = None  # Currently selected slot

# UI Elements
input_field = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((370, 700), (280, 30)), manager=manager
)

# Function to draw the table
def draw_table():
    screen.fill(BLACK)

    # Title
    title_text = title_font.render("Entry Terminal", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - 100, 10))

    subtitle_text = header_font.render("Edit Current Game", True, BLUE)
    screen.blit(subtitle_text, (WIDTH // 2 - 100, 40))

    # Draw team headers
    red_header = header_font.render("RED TEAM", True, WHITE)
    green_header = header_font.render("GREEN TEAM", True, WHITE)
    pygame.draw.rect(screen, RED, (100, 80, 200, 30))
    pygame.draw.rect(screen, GREEN, (700, 80, 200, 30))
    screen.blit(red_header, (150, 85))
    screen.blit(green_header, (750, 85))

    # Draw player slots
    for i in range(20):
        pygame.draw.rect(screen, RED, (100, 120 + i * 30, 200, 30), 2)
        pygame.draw.rect(screen, GREEN, (700, 120 + i * 30, 200, 30), 2)

        # Display ID & codename
        red_text = font.render(f"[ ] {red_team[i]['id']} {red_team[i]['codename']}", True, WHITE)
        green_text = font.render(f"[ ] {green_team[i]['id']} {green_team[i]['codename']}", True, WHITE)

        screen.blit(red_text, (110, 125 + i * 30))
        screen.blit(green_text, (710, 125 + i * 30))

    # Draw Bottom Buttons
    draw_bottom_buttons()

# Function to draw bottom buttons
def draw_bottom_buttons():
    buttons = [
        ("F1 Edit Game", 100), ("F2 Game Parameters", 200),
        ("F3 Start Game", 300), ("F5 PreEntered Games", 400),
        ("F7", 500), ("F8 View Game", 600),
        ("F10 Flick Sync", 700), ("F12 Clear Game", 800),
    ]
    for text, x in buttons:
        pygame.draw.rect(screen, GRAY, (x, 720, 100, 30))
        button_text = font.render(text, True, GREEN)
        screen.blit(button_text, (x + 10, 725))

    instruction_text = font.render("<Del> to Delete Player, <Enter> to Confirm Codename", True, WHITE)
    screen.blit(instruction_text, (280, 680))

# Function to update a codename in the table
def update_codename():
    global selected_slot
    if selected_slot is None:
        return

    codename = input_field.get_text()
    if not codename:
        return

    team, index = selected_slot
    team[index]["codename"] = codename
    input_field.set_text("")  # Clear input field

# Function to delete a player
def delete_player():
    global selected_slot
    if selected_slot is None:
        return

    team, index = selected_slot
    team[index]["codename"] = ""

# Function to handle selecting a player slot
def select_slot(pos):
    global selected_slot
    x, y = pos

    for i in range(20):
        if 100 <= x <= 300 and 120 + i * 30 <= y <= 150 + i * 30:
            selected_slot = (red_team, i)
            return
        if 700 <= x <= 900 and 120 + i * 30 <= y <= 150 + i * 30:
            selected_slot = (green_team, i)
            return

    selected_slot = None  # If clicked outside, deselect

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(30) / 1000.0  # Limit FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Process UI events
        manager.process_events(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Press Enter to update codename
                update_codename()
            elif event.key == pygame.K_DELETE:
                delete_player()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                select_slot(event.pos)

    # Update UI
    manager.update(time_delta)

    # Draw everything
    draw_table()
    manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()
