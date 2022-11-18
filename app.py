import pygame
from time_utils import global_timer, Counter
from six_words_mode import SixtletsProcessor
from config import TEST_LANG_DATA
 
pygame.init()
 
# define the RGB value for white,
#  green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
 
X = 1080
Y = 720
 
display_surface = pygame.display.set_mode((X, Y))
pygame.display.set_caption('Experimental')


delta_timer = global_timer(pygame)
new_line_counter = Counter(500)
sixtlets = SixtletsProcessor(X, Y, pygame, display_surface, "latvian_words", TEST_LANG_DATA)

# TODO: move into time
time_to_cross_screen = 5000
pixels_per_ms = Y/time_to_cross_screen

 
for time_delta in delta_timer:
    display_surface.fill(white)

    if new_line_counter.is_tick(time_delta):
        sixtlets.add_line()

    sixtlets.tick(pixels_per_ms * time_delta)
    pygame.display.update()
 
    for event in pygame.event.get():
 
        if event.type == pygame.QUIT:
            pygame.quit()
 
            quit()
 
