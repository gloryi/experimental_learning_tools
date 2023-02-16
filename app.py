import pygame
from time_utils import global_timer, Counter, Progression
from feature_chain_mode import ChainedProcessor
from config import TEST_LANG_DATA, W, H, BPM, CYRILLIC_FONT, CHINESE_FONT, BURNER_APP, BURNER_FILE
from config import HAPTIC_CORRECT_CMD, HAPTIC_ERROR_CMD
from colors import white
import colors
from text_morfer import textMorfer
import time
import random
import csv
import re
import subprocess

from ui_elements import UpperLayout

def hex_to_rgb(h, cache = False):
    h = h[1:]
    resulting =  tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return resulting

pygame.init()

quadra_r = 0
quadra_phase = "INHALE"
clip_color = lambda _ : 0 if _ <=0 else 255 if _ >=255 else int(_)
inter_color = lambda v1, v2, p: clip_color(v1 + (v2-v1)*p)
interpolate = lambda col1, col2, percent: (inter_color(col1[0], col2[0], percent),
                                           inter_color(col1[1], col2[1], percent),
                                           inter_color(col1[2], col2[2], percent))
feature_bg = hex_to_rgb("#2E849E")
col_bt_pressed = hex_to_rgb("#4E52AF")
red2 = hex_to_rgb("#700F3C")
option_fg = hex_to_rgb("#68A834")
quadra_col_1 = feature_bg 
quadra_col_2 = col_bt_pressed

display_surface = pygame.display.set_mode((W, H))

time_to_cross_screen = 16000
time_to_appear = 4000
beat_time = 0
paused = True
paused_manually = True
is_pause_displayed = False
burner_casted = False

trans_surface = pygame.Surface((H, H))
trans_surface_2 = pygame.Surface((W, H))
trans_surface.set_alpha(15)
trans_surface_2.set_alpha(70)
trans_surface.fill((40,0,40))
trans_surface_2.fill((40,0,40))

delta_timer = global_timer(pygame)
upper_stats = UpperLayout(pygame, display_surface)
new_line_counter = Counter(upper_stats)
quadra_timer = Counter(bpm = 10)
morfer_timer = Counter(bpm = 15)
pause_counter = Counter(bpm = 1/2)

timer_1m = Counter(bpm = 2)
haptic_timer = Counter(bpm = 15)
disable_haptic = False
timer_dropped = False

tokens_1m = []
tokens_key = pygame.K_k

game = ChainedProcessor(pygame, display_surface, upper_stats, "hanzi chineese", TEST_LANG_DATA,
                        (60*1000)/BPM)


progression = Progression(new_line_counter,
                          upper_stats)

beat_time = new_line_counter.drop_time

font = pygame.font.Font(CYRILLIC_FONT, 200, bold = True)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
fpsClock = pygame.time.Clock()
morfer = textMorfer()

meta = ""
meta_minor = []

base_font_hz = pygame.font.Font(CHINESE_FONT, 50, bold = True)
base_font_reg = pygame.font.Font(CYRILLIC_FONT, 50, bold = True)
minor_font_hz = pygame.font.Font(CYRILLIC_FONT, 25, bold = True)
minor_font_reg = pygame.font.Font(CYRILLIC_FONT, 25, bold = True)

def place_text(text, x, y, transparent = False, renderer = None, base_col = (80,80,80),forbid_morf=False):
    if not forbid_morf:
        text = morfer.morf_text(text)
    if renderer is None:
        renderer = base_font_reg if not re.findall(r'[\u4e00-\u9fff]+',text) else base_font_hz,

    if isinstance(renderer, tuple) or isinstance(renderer, list):
        renderer = renderer[0]
    if not transparent:
        text = renderer.render(text, True, base_col, (150,150,151))
    else:
        text = renderer.render(text, True, base_col)
    textRect = text.get_rect()
    textRect.center = (x, y)
    display_surface.blit(text, textRect)


for time_delta in delta_timer:
    fpsClock.tick(27)
    if morfer_timer.is_tick(time_delta):
        morfer.update_seed()

    if paused and not is_pause_displayed:
        display_surface.fill(white)

        timer_expired = timer_1m.is_tick(time_delta)

        if timer_expired and not timer_dropped:
            timer_dropped = True

        if timer_dropped:
            if haptic_timer.is_tick(time_delta):
                if HAPTIC_ERROR_CMD and not disable_haptic:
                    subprocess.Popen(["bash", HAPTIC_ERROR_CMD])

        if quadra_timer.is_tick(time_delta):
            if quadra_phase == "INHALE":
                quadra_phase = "HOLD_IN"
                quadra_col_1 = colors.col_bt_pressed
                quadra_col_2 = colors.red2
            elif quadra_phase == "HOLD_IN":
                quadra_phase = "EXHALE"
                quadra_col_1 = colors.red2
                quadra_col_2 = colors.option_fg
            elif quadra_phase == "EXHALE":
                quadra_phase = "HOLD_OUT"
                quadra_col_1 = colors.option_fg
                quadra_col_2 = colors.feature_bg
            else:
                quadra_phase = "INHALE"
                quadra_col_1 = colors.feature_bg
                quadra_col_2 = colors.col_bt_pressed

        if quadra_phase == "INHALE":
            quadra_w_perce1 = quadra_timer.get_percent()
            quadra_w_perce2 = 1.0
        elif quadra_phase == "HOLD_IN":
            quadra_w_perce1 = 1.0
            quadra_w_perce2 = 1 - quadra_timer.get_percent()
        elif quadra_phase == "EXHALE":
            quadra_w_perce1 = 1 - quadra_timer.get_percent()
            quadra_w_perce2 = 0.0
        else:
            quadra_w_perce1 = 0.0
            quadra_w_perce2 = quadra_timer.get_percent()

        trans_surface_2.fill(interpolate(quadra_col_1, quadra_col_2, (1.0-quadra_timer.get_percent())**3))

        pygame.draw.circle(trans_surface_2,
                              interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
                              (W//2, H//2),
                               (H//2-100)*quadra_w_perce1+100)
        pygame.draw.circle(trans_surface_2,
                              interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()**2),
                              (W//2, H//2),
                               (H//2-50)*quadra_w_perce2+50, width = 3)

        display_surface.blit(trans_surface_2, (0,0))

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
                            H//8 + 25*(i+1),
                            transparent = True,
                            renderer = minor_font_reg if not re.findall(r'[\u4e00-\u9fff]+',line) else minor_font_hz,
                            base_col = (colors.col_bt_pressed))

        if not timer_dropped:
            pygame.draw.rect(display_surface,
                                      interpolate(quadra_col_1, quadra_col_2, timer_1m.get_percent()**2),
                                      ((W//2 - ((W//2)*(1-timer_1m.get_percent()))),
                                       H//2 - 40,
                                       ((W)*(1 - timer_1m.get_percent())),
                                       80))

        tokens_repr = " ".join(str(i+1)+random.choice("+!$*=") for i,_ in enumerate(tokens_1m))
        place_text(tokens_repr,
                    W//2,
                    H//32,
                    transparent = True,
                    renderer = base_font_reg,
                    base_col = interpolate(quadra_col_1, quadra_col_2, 1-quadra_timer.get_percent()))

        #text = font.render(morfer.morf_text("PAUSED"), True, colors.col_bg_darker)
        #textRect = text.get_rect()
        #textRect.center = (W//2, H//2)
        #display_surface.blit(text, textRect)

        #is_pause_displayed = True

    if paused and not paused_manually:
        if not burner_casted:
            if game.is_burning():
                burning_list = game.get_burning_features_list()
                with open(BURNER_FILE, "w") as burning_file:
                    writer = csv.writer(burning_file)
                    writer.writerows(burning_list)

                subprocess.Popen(["python3", BURNER_APP])
                burner_casted = True
                disable_haptic = True

                pygame.quit()
                quit()

    if paused:
        pygame.display.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            paused = False
            is_pause_displayed = False
            burner_casted = False
            disable_haptic = False

        if keys[tokens_key] and not timer_dropped:
            if tokens_key == pygame.K_k:
                tokens_key = pygame.K_d
            else:
                tokens_key = pygame.K_k
            tokens_1m.append("*")
            if HAPTIC_CORRECT_CMD and not disable_haptic:
                subprocess.Popen(["bash", HAPTIC_CORRECT_CMD])
            if len(tokens_1m)>5:
                tokens_1m = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        continue

    #trans_surface.set_alpha(20)

    display_surface.fill(white)

    if pause_counter.is_tick(time_delta):
        paused = True
        paused_manually = False
        tokens_1m = []
        timer_1m.drop_elapsed()
        timer_dropped = False

    if new_line_counter.is_tick(time_delta):
        next_tick_time, meta, meta_minor = game.add_line()
        new_line_counter.modify_bpm(next_tick_time)

    upper_stats.redraw()
    feedback = game.tick(beat_time, time_delta)

    resume_game = progression.register_event(feedback)
    if not resume_game:
        pause_counter.drop_elapsed()
        paused = True
        timer_1m.drop_elapsed()
        timer_dropped = False

    beat_time = progression.synchronize_tick()

    if quadra_timer.is_tick(time_delta):
        if quadra_phase == "INHALE":
            quadra_phase = "HOLD_IN"
            quadra_col_1 = col_bt_pressed
            quadra_col_2 = red2
        elif quadra_phase == "HOLD_IN":
            quadra_phase = "EXHALE"
            quadra_col_1 = red2
            quadra_col_2 = option_fg
        elif quadra_phase == "EXHALE":
            quadra_phase = "HOLD_OUT"
            quadra_col_1 = option_fg
            quadra_col_2 = feature_bg
        else:
            quadra_phase = "INHALE"
            quadra_col_1 = feature_bg
            quadra_col_2 = col_bt_pressed

    if quadra_phase == "INHALE":
        quadra_w_perce1 = quadra_timer.get_percent()
        quadra_w_perce2 = 1.0
    elif quadra_phase == "HOLD_IN":
        quadra_w_perce1 = 1.0
        quadra_w_perce2 = 1 - quadra_timer.get_percent()
    elif quadra_phase == "EXHALE":
        quadra_w_perce1 = 1 - quadra_timer.get_percent()
        quadra_w_perce2 = 0.0
    else:
        quadra_w_perce1 = 0.0
        quadra_w_perce2 = quadra_timer.get_percent()

    trans_surface.fill((40,0,40))
    pygame.draw.circle(trans_surface,
                          interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
                          (H//2, H//2),
                           (H//2-100)*quadra_w_perce1+100)
    pygame.draw.circle(trans_surface,
                          interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()**2),
                          (H//2, H//2),
                           (H//2-50)*quadra_w_perce2+50, width = 3)

    display_surface.blit(trans_surface, (W//2-H//2,0))


    pygame.display.update()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_v]:
        paused = True
        paused_manually = True
        tokens_1m = []
        timer_1m.drop_elapsed()
        timer_dropped = False

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()

            quit()
pygame.quit()
