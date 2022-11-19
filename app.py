import pygame
from time_utils import global_timer, Counter, Progression
from six_words_mode import SixtletsProcessor
from config import TEST_LANG_DATA
 
pygame.init()
 
# define the RGB value for white,
#  green, blue colour .
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)
 
X = 1400
Y = 900 
 
display_surface = pygame.display.set_mode((X, Y))
pygame.display.set_caption('Experimental')

time_to_cross_screen = 12000
time_to_appear = 3000
pixels_per_ms = Y/time_to_cross_screen

delta_timer = global_timer(pygame)
new_line_counter = Counter(time_to_appear)
sixtlets = SixtletsProcessor(X, Y, pygame, display_surface, "latvian_words", TEST_LANG_DATA)

# TODO: move into time
progression = Progression(Y,
                          time_to_cross_screen,
                          time_to_appear,
                          new_line_counter)
 
for time_delta in delta_timer:
    display_surface.fill(white)

    if new_line_counter.is_tick(time_delta):
        sixtlets.add_line()

    feedback = sixtlets.tick(pixels_per_ms * time_delta)
    progression.register_event(feedback)
    pixels_per_ms = progression.synchronize_speed()

    pygame.display.update()
 
    for event in pygame.event.get():
 
        if event.type == pygame.QUIT:
            pygame.quit()
 
            quit()
 
