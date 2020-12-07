# Simple pygame program

# Import and initialize the pygame library
import pygame

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SPEC_SCREEN_LEFT = 50
SPEC_SCREEN_TOP = 50
SPEC_SCREEN_RIGHT = 306
SPEC_SCREEN_BOTTOM = 242




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

    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -1)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 1)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-1, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(1, 0)

            # Keep player on the screen
        if self.rect.left < SPEC_SCREEN_LEFT:
            self.rect.left = SPEC_SCREEN_LEFT
        if self.rect.right > SPEC_SCREEN_RIGHT:
            self.rect.right = SPEC_SCREEN_RIGHT
        if self.rect.top <= SPEC_SCREEN_TOP:
            self.rect.top = SPEC_SCREEN_TOP
        if self.rect.bottom >= SPEC_SCREEN_BOTTOM:
            self.rect.bottom = SPEC_SCREEN_BOTTOM

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

    textsurface = myfont.render("x:{}, y:{}".format(str(player.rect.left - SPEC_SCREEN_LEFT), str(player.rect.top - SPEC_SCREEN_TOP)), False, (0, 0, 0))
    screen.blit(textsurface,(400,50))
    
    #surf.fill((215, 215, 215))
    

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()