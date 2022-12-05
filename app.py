import pygame
from time_utils import global_timer, Counter, Progression
#from six_words_mode import SixtletsProcessor
from feature_chain_mode import ChainedProcessor
from config import TEST_LANG_DATA, W, H, BPM, CYRILLIC_FONT
from colors import white
import colors
import time
import random
from ui_elements import UpperLayout
 
pygame.init()
 
display_surface = pygame.display.set_mode((W, H))

time_to_cross_screen = 16000
time_to_appear = 4000
beat_time = 0 
paused = True
is_pause_displayed = False

delta_timer = global_timer(pygame)
upper_stats = UpperLayout(pygame, display_surface)
new_line_counter = Counter(upper_stats)
pause_counter = Counter(bpm = 1/5)

game = ChainedProcessor(pygame, display_surface, upper_stats, "hanzi chineese", TEST_LANG_DATA,
                        (60*1000)/BPM)


progression = Progression(new_line_counter,
                          upper_stats)

beat_time = new_line_counter.drop_time 

font = pygame.font.Font(CYRILLIC_FONT, 200, bold = True)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
fpsClock = pygame.time.Clock()

 
for time_delta in delta_timer:
    fpsClock.tick(30)

    if paused and not is_pause_displayed:
        display_surface.fill(white)
        text = font.render("PAUSED", True, colors.col_bg_darker)
        textRect = text.get_rect()
        textRect.center = (W//2, H//2)
        display_surface.blit(text, textRect)
        is_pause_displayed = True

    if paused:
        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            paused = False
            is_pause_displayed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
 
                quit()
        continue

    display_surface.fill(white)

    if pause_counter.is_tick(time_delta):
        paused = True

    if new_line_counter.is_tick(time_delta):
        next_tick_time = game.add_line()
        new_line_counter.modify_bpm(next_tick_time)

    upper_stats.redraw()
    feedback = game.tick(beat_time, time_delta)

    resume_game = progression.register_event(feedback)
    if not resume_game:
        pause_counter.drop_elapsed()
        paused = True

    beat_time = progression.synchronize_tick()


    pygame.display.update()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_v]:
        paused = True
 
    for event in pygame.event.get():
 
        if event.type == pygame.QUIT:
            pygame.quit()
 
            quit()
pygame.quit() 
