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

    # Fill the background with white

    screen.fill((255, 255, 255))
    surf.fill((215, 215, 215))
    screen.blit(surf, ((50, 50)))

    screen.blit(player.surf, player.rect)

    player.calculate_coords_from_memory()
    textsurface = myfont.render("x:{}, y:{}".format(str(player.rect.left - SPEC_SCREEN_LEFT), str(player.rect.top - SPEC_SCREEN_TOP)), False, (0, 0, 0))
    screen.blit(textsurface,(400,50))
    
    textsurface2 = myfont.render("Loc:{}, Value:{}".format(str(player.memory_location_offset + SCREEN_START), str(player.memory_location_value)), False, (0, 0, 0))
    screen.blit(textsurface2,(400,150))

    textsurface3 = myfont.render("x:{}, y:{}".format(str(player.x_coord), str(player.y_coord)), False, (0, 0, 0))
    screen.blit(textsurface3,(400,250))
    
    #surf.fill((215, 215, 215))
    

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
