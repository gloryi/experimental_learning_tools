import pygame
from time_utils import global_timer, Counter, Progression
from feature_chain_mode import ChainedProcessor
from config import TEST_LANG_DATA, W, H, BPM, CYRILLIC_FONT, CHINESE_FONT, BURNER_APP, BURNER_FILE
from colors import white
import colors
import time
import random
import csv
import subprocess

from ui_elements import UpperLayout

pygame.init()

display_surface = pygame.display.set_mode((W, H))

time_to_cross_screen = 16000
time_to_appear = 4000
beat_time = 0
paused = True
paused_manually = True
is_pause_displayed = False
burner_casted = False

delta_timer = global_timer(pygame)
upper_stats = UpperLayout(pygame, display_surface)
new_line_counter = Counter(upper_stats)
pause_counter = Counter(bpm = 1/2)

game = ChainedProcessor(pygame, display_surface, upper_stats, "hanzi chineese", TEST_LANG_DATA,
                        (60*1000)/BPM)


progression = Progression(new_line_counter,
                          upper_stats)

beat_time = new_line_counter.drop_time

font = pygame.font.Font(CYRILLIC_FONT, 200, bold = True)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
fpsClock = pygame.time.Clock()

meta = ""
meta_minor = []

base_font = pygame.font.Font(CHINESE_FONT, 50, bold = True)
minor_font = pygame.font.match_font("setofont")
minor_font = pygame.font.Font(minor_font, 22)

def place_text(text, x, y, transparent = False, renderer = None, base_col = (80,80,80)):
    if renderer is None:
        renderer = base_font
    if not transparent:
        text = renderer.render(text, True, base_col, (150,150,151))
    else:
        text = renderer.render(text, True, base_col)
    textRect = text.get_rect()
    textRect.center = (x, y)
    display_surface.blit(text, textRect)


for time_delta in delta_timer:
    fpsClock.tick(27)

    if paused and not is_pause_displayed:
        display_surface.fill(white)
        text = font.render("PAUSED", True, colors.col_bg_darker)
        textRect = text.get_rect()
        textRect.center = (W//2, H//2)
        display_surface.blit(text, textRect)
        if meta:
            chunks = [meta[i:i+50] for i in range(0, len(meta), 50)]
            for i, chunk in enumerate(chunks):
                place_text(chunk,
                            W//2,
                            H//2+90 + 50*(i+1),
                            transparent = True,
                            renderer = None,
                            base_col = (colors.col_bt_pressed))
        if meta_minor:
            for i, line in enumerate(meta_minor):
                place_text(line,
                            W//2,
                            H//2-400 + 16*(i+1),
                            transparent = True,
                            renderer = minor_font,
                            base_col = (colors.col_bt_pressed))

        is_pause_displayed = True

    if paused and not paused_manually:
        if not burner_casted:
            if game.is_burning():
                burning_list = game.get_burning_features_list()
                with open(BURNER_FILE, "w") as burning_file:
                    writer = csv.writer(burning_file)
                    writer.writerows(burning_list)

                subprocess.Popen(["python3", BURNER_APP])
                burner_casted = True


    if paused:
        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            paused = False
            is_pause_displayed = False
            burner_casted = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        continue

    display_surface.fill(white)

    if pause_counter.is_tick(time_delta):
        paused = True
        paused_manually = False

    if new_line_counter.is_tick(time_delta):
        next_tick_time, meta, meta_minor = game.add_line()
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
        paused_manually = True

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()

            quit()
pygame.quit()
