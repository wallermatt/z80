# Simple pygame program

# Import and initialize the pygame library
import pygame
import math

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_m,
    K_k,
    K_q,
    K_a,
    KEYDOWN,
    QUIT,
)

SPEC_SCREEN_LEFT = 50
SPEC_SCREEN_TOP = 50
SPEC_SCREEN_RIGHT = 306
SPEC_SCREEN_BOTTOM = 242

SCREEN_START = 16384
SCREEN_END = 22528

pygame.init()

pygame.font.init()
myfont = pygame.font.SysFont('Arial', 30)

COLOURS = {
    0: {0: "#000000", 1: "#000000"},
    1: {0: "#0000D7", 1: "#0000FF"},
    2: {0: "#D70000", 1: "#FF0000"},
    3: {0: "#D700D7", 1: "#FF00FF"},
    4: {0: "#00D700", 1: "#00FF00"},
    5: {0: "#00D7D7", 1: "#00FFFF"},
    6: {0: "#D7D700", 1: "#FFFF00"},
    7: {0: "#D7D7D7", 1: "#FFFFFF"},
}

SCR_MEMORY = [[0 for _ in range(32)] for _ in range(192)]

SCR_ATTRIBUTES = [[8 * i for i in range(32)] for _ in range(24)]


def get_screen_attributes(value):
    flash = value // 128
    flash_offset = value % 128
    bright = flash_offset // 64
    bright_offset = flash_offset % 64
    paper = bright_offset // 8
    ink = bright_offset % 8
    paper_colour = COLOURS[paper][bright]
    ink_colour = COLOURS[ink][bright]
    return flash, paper_colour, ink_colour


def get_grid_from_coords(x, y):
    x -= SPEC_SCREEN_LEFT
    y -= SPEC_SCREEN_TOP
    grid_x = x // 8
    grid_y = y // 8
    return grid_x, grid_y


def get_coords_from_grid(grid_x, grid_y):
    x = grid_x * 8 + SPEC_SCREEN_LEFT
    y = grid_y * 8 + SPEC_SCREEN_TOP
    return x, y


def set_screen_paper():
    for grid_y, row in enumerate(SCR_ATTRIBUTES):
        for grid_x, attribute in enumerate(row):
            _, paper_colour, _ = get_screen_attributes(attribute)
            x,y = get_coords_from_grid(grid_x, grid_y)
            pygame.draw.rect(screen, (paper_colour), (x, y, 8, 8), 0)


def get_current_attribute_value(x, y):
    grid_x, grid_y = get_grid_from_coords(x, y)
    attribute_value = SCR_ATTRIBUTES[grid_y][grid_x]
    return attribute_value


def manaual_attribute_update(pressed_keys, player):
    current_attribute_value = get_current_attribute_value(player.rect.left, player.rect.top)
    if pressed_keys[K_q]:
        current_attribute_value += 1
    elif pressed_keys[K_a]:
        current_attribute_value -= 1
    if current_attribute_value < 0:
        current_attribute_value = 0
    elif current_attribute_value > 255:
        current_attribute_value = 255
    grid_x, grid_y = get_grid_from_coords(player.rect.left, player.rect.top)
    SCR_ATTRIBUTES[grid_y][grid_x] = current_attribute_value


def convert_memory_value_to_binary_string(value):
    return bin(value)[2:]


def get_memory_value_at_coords(x, y):
    return SCR_MEMORY[y][x // 8]


def set_memory_value_at_coords(value, x, y):
    SCR_MEMORY[y][x // 8] = value


def write_memory_location_at_coords_to_screen(x, y):
    value = get_memory_value_at_coords(x, y)
    binary_value = convert_memory_value_to_binary_string(value)
    current_attribute_value = get_current_attribute_value(x, y)
    _,_, ink_colour = get_screen_attributes(current_attribute_value)
    for i, bit in enumerate(binary_value):
        if bit == "1":
            pygame.draw.rect(screen, (ink_colour), (x + i, y, 1, 1), 0


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.Surface((1, 1))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect()
        self.rect.x = SPEC_SCREEN_LEFT
        self.rect.y = SPEC_SCREEN_TOP
        self.memory_location_offset = 0
        self.memory_location_value = 128
        self.x_coord = 0
        self.y_coord = 0

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -1)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 1)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-1, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(1, 0)
        if pressed_keys[K_m]:
            self.change_memory('inc')
        if pressed_keys[K_k]:
            self.change_memory('dec')

            # Keep player on the screen
        if self.rect.left < SPEC_SCREEN_LEFT:
            self.rect.left = SPEC_SCREEN_LEFT
        if self.rect.right > SPEC_SCREEN_RIGHT:
            self.rect.right = SPEC_SCREEN_RIGHT
        if self.rect.top <= SPEC_SCREEN_TOP:
            self.rect.top = SPEC_SCREEN_TOP
        if self.rect.bottom >= SPEC_SCREEN_BOTTOM:
            self.rect.bottom = SPEC_SCREEN_BOTTOM

        self.calculate_memory()

    def calculate_memory(self):
        x = self.rect.left - SPEC_SCREEN_LEFT
        y = self.rect.top - SPEC_SCREEN_TOP
        block = y // 64
        block_offset = y % 64
        row = block_offset % 8
        row_offset = block_offset // 8
        self.memory_location_offset = block * 2048 + row * 256 + row_offset * 32
        self.memory_location_offset += x // 8
        remainder = x % 8
        power = 7 - remainder
        self.memory_location_value = 2 ** power


    def change_memory(self, action):
        if action == "inc":
            self.memory_location_offset += 1
        elif action == "dec":
            self.memory_location_offset -= 1
        if self.memory_location_offset < 0:
            self.memory_location_offset = 0
        elif self.memory_location_offset > (SCREEN_END - SCREEN_START):
            self.memory_location_offset = SCREEN_END - SCREEN_START

        self.calculate_coords_from_memory()

    def calculate_coords_from_memory(self):
        block = self.memory_location_offset // 2048
        block_offset = self.memory_location_offset % 2048
        line = block_offset // 256
        line_offset = block_offset % 256
        row = line_offset // 32
        column = block_offset % 32
        self.x_coord = column * 8 + (7 - int(math.log(self.memory_location_value) / math.log(2)))
        self.y_coord = block * 64 + row * 8 + line
        self.rect.left = self.x_coord + SPEC_SCREEN_LEFT
        self.rect.top = self.y_coord + SPEC_SCREEN_TOP



# Set up the drawing window
screen = pygame.display.set_mode([1000, 1000])

player = Player()

screen.fill((255, 255, 255))

# Draw a solid blue circle in the center
#pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)

surf = pygame.Surface((256, 192))
surf.fill((215, 215, 215))
rect = surf.get_rect()

screen.blit(player.surf, player.rect)
screen.blit(surf, ((SPEC_SCREEN_LEFT, SPEC_SCREEN_RIGHT)))

pygame.key.set_repeat(1, 500)

# Run until the user asks to quit
running = True
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False

        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)

        manaual_attribute_update(pressed_keys, player)

    # Fill the background with white

    screen.fill((255, 255, 255))
    
    #surf.fill((215, 215, 215))
    
    screen.blit(surf, ((50, 50)))
    set_screen_paper()

    #pygame.draw.rect(screen, ("#000000"), (90, 90, 8, 8), 0)

    screen.blit(player.surf, player.rect)

    player.calculate_coords_from_memory()
    textsurface = myfont.render("x:{}, y:{}".format(str(player.rect.left - SPEC_SCREEN_LEFT), str(player.rect.top - SPEC_SCREEN_TOP)), False, (0, 0, 0))
    screen.blit(textsurface,(400,50))
    
    textsurface2 = myfont.render("Loc:{}, Value:{}".format(str(player.memory_location_offset + SCREEN_START), str(player.memory_location_value)), False, (0, 0, 0))
    screen.blit(textsurface2,(400,150))

    textsurface3 = myfont.render("x:{}, y:{}".format(str(player.x_coord), str(player.y_coord)), False, (0, 0, 0))
    screen.blit(textsurface3,(400,250))
    
    current_attribute_value = get_current_attribute_value(player.rect.left, player.rect.top)
    textsurface4 = myfont.render("Current Attribute Value: {}".format(str(current_attribute_value)), False, (0, 0, 0))
    screen.blit(textsurface4,(400,350))
    #surf.fill((215, 215, 215))
    

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
