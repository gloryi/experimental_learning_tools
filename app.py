import pygame
from time_utils import global_timer, Counter, Progression
from six_words_mode import SixtletsProcessor
from feature_chain_mode import ChainedProcessor
from config import TEST_LANG_DATA, W, H
from colors import white
from ui_elements import UpperLayout
 
pygame.init()
 
display_surface = pygame.display.set_mode((W, H))

time_to_cross_screen = 16000
time_to_appear = 4000
beat_time = 0 

delta_timer = global_timer(pygame)
upper_stats = UpperLayout(pygame, display_surface)
new_line_counter = Counter(upper_stats)

game = ChainedProcessor(pygame, display_surface, upper_stats, "hanzi chineese", TEST_LANG_DATA)


progression = Progression(new_line_counter,
                          upper_stats)

beat_time = new_line_counter.drop_time 
 
for time_delta in delta_timer:
    display_surface.fill(white)

    if new_line_counter.is_tick(time_delta):
        next_tick_time = game.add_line()
        new_line_counter.modify_bpm(next_tick_time)

    feedback = game.tick(beat_time, time_delta)

    resume_game = progression.register_event(feedback)
    if not resume_game:
        break

    beat_time = progression.synchronize_tick()

    upper_stats.redraw()

    pygame.display.update()
 
    for event in pygame.event.get():
 
        if event.type == pygame.QUIT:
            pygame.quit()
 
            quit()
pygame.quit() 
