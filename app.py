from ui_elements import UpperLayout
import pygame
from time_utils import global_timer, Counter, Progression
from feature_chain_mode import ChainedProcessor
from config import (
    TEST_LANG_DATA,
    W,
    H,
    BPM,
    CYRILLIC_FONT,
    CHINESE_FONT,
    BURNER_APP,
    BURNER_FILE,
)
from config import HAPTIC_FEEDBACK, TEST
from colors import white, hex_to_rgb
import colors
from text_morfer import textMorfer
import time
import random
import csv
import re
import subprocess
import pyautogui
import sys

SCREEN_X_0 = 3400
SCREEN_Y_0 = 0


pygame.init()

quadra_r = 0
quadra_phase = "INHALE"


def clip_color(_):
    return 0 if _ <= 0 else 255 if _ >= 255 else int(_)


def inter_simple(v1, v2, p):
    return v1 + (v2 - v1) * p

def inter_color(v1, v2, p):
    return clip_color(v1 + (v2 - v1) * p)


def interpolate(col1, col2, percent):
    return (
        inter_color(col1[0], col2[0], percent),
        inter_color(col1[1], col2[1], percent),
        inter_color(col1[2], col2[2], percent),
    )


feature_bg = hex_to_rgb("#2E849E")
col_bt_pressed = hex_to_rgb("#4E52AF")
red2 = hex_to_rgb("#700F3C")
option_fg = hex_to_rgb("#68A834")
quadra_col_1 = feature_bg
quadra_col_2 = col_bt_pressed

display_surface = pygame.display.set_mode((W, H))
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
trans_surface.fill((40, 0, 40))
trans_surface_2.fill((40, 0, 40))

delta_timer = global_timer(pygame)
upper_stats = UpperLayout(pygame, display_surface)
new_line_counter = Counter(upper_stats)
quadra_timer = Counter(bpm=15)
morfer_timer = Counter(bpm=12)
pause_counter = Counter(bpm=1 / 5)
# pause_counter = Counter(bpm=1)
wait_extra_time = False

timer_1m = Counter(bpm=1)
haptic_timer = Counter(bpm=60)
disable_haptic = False
timer_dropped = False

tokens_1m = []
tokens_key = pygame.K_k

game = ChainedProcessor(
    pygame,
    display_surface,
    upper_stats,
    "hanzi chineese",
    TEST_LANG_DATA,
    (60 * 1000) / BPM,
)

progression = Progression(new_line_counter, upper_stats)

beat_time = new_line_counter.drop_time

font = pygame.font.Font(CYRILLIC_FONT, 200)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
pygame.mouse.set_visible(False)
fpsClock = pygame.time.Clock()
morfer = textMorfer()

meta = ""
meta_minor = []

base_font_hz = pygame.font.Font(CHINESE_FONT, 50)
base_font_reg = pygame.font.Font(CYRILLIC_FONT, 50)
minor_font_hz = pygame.font.Font(CYRILLIC_FONT, 25)
minor_font_reg = pygame.font.Font(CYRILLIC_FONT, 25)


def place_text(
    text,
    x,
    y,
    transparent=False,
    renderer=None,
    base_col=(80, 80, 80),
    forbid_morf=False,
):
    if not forbid_morf:
        text = morfer.morf_text(text)
    if renderer is None:
        renderer = (
            base_font_reg
            if not re.findall(r"[\u4e00-\u9fff]+", text)
            else base_font_hz,
        )

    if isinstance(renderer, tuple) or isinstance(renderer, list):
        renderer = renderer[0]
    if not transparent:
        text = renderer.render(text, True, base_col, (150, 150, 151))
    else:
        text = renderer.render(text, True, base_col)
    textRect = text.get_rect()
    textRect.center = (x, y)
    display_surface.blit(text, textRect)


for time_delta in delta_timer:
    fpsClock.tick(40)
    if morfer_timer.is_tick(time_delta):
        morfer.update_seed()

    if paused and not is_pause_displayed:
        display_surface.fill(white)

        timer_expired = timer_1m.is_tick(time_delta)

        if timer_expired and not timer_dropped:
            timer_dropped = True

        if timer_dropped:
            if haptic_timer.is_tick(time_delta):
                if HAPTIC_FEEDBACK and not disable_haptic:
                    HAPTIC_FEEDBACK(higher_freq  = 40000, duration=500)

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

        trans_surface_2.fill(
            interpolate(
                quadra_col_1, quadra_col_2, (1.0 - quadra_timer.get_percent()) ** 3
            )
        )

        pygame.draw.circle(
            trans_surface_2,
            interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
            (W // 2, H // 2),
            (H // 2 - 100) * quadra_w_perce1 + 100,
        )
        pygame.draw.circle(
            trans_surface_2,
            interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent() ** 2),
            (W // 2, H // 2),
            (H // 2 - 50) * quadra_w_perce2 + 50,
            width=3,
        )

        if not timer_dropped:
            if haptic_timer.is_tick(time_delta):
                if HAPTIC_FEEDBACK and not disable_haptic:
                    inter_freq = int(inter_simple(0, 65000, quadra_w_perce1))
                    HAPTIC_FEEDBACK(higher_freq  = inter_freq)

        display_surface.blit(trans_surface_2, (0, 0))

        if meta:
            chunks = [meta[i : i + 50] for i in range(0, len(meta), 50)]
            for i, chunk in enumerate(chunks):
                place_text(
                    chunk,
                    W // 2,
                    H // 2 + 90 + 50 * (i + 1),
                    transparent=True,
                    renderer=None,
                    base_col=(colors.col_bt_pressed),
                )
        if meta_minor:
            back_t_found = False

            for i, line in enumerate(meta_minor):

                if "*** 1XTEXT ***" in line:
                    back_t_found = True

                if not back_t_found and not "#" in line:
                    continue

                place_text(
                    line,
                    W // 2,
                    H // 8 + 25 * (i + 1),
                    transparent=True,
                    renderer=minor_font_reg
                    if not re.findall(r"[\u4e00-\u9fff]+", line)
                    else minor_font_hz,
                    base_col=(colors.col_bt_pressed),
                )

        if not timer_dropped:
            pygame.draw.rect(
                display_surface,
                interpolate(quadra_col_1, quadra_col_2, timer_1m.get_percent() ** 2),
                (
                    (W // 2 - ((W // 2) * (1 - timer_1m.get_percent()))),
                    H // 2 - 40,
                    ((W) * (1 - timer_1m.get_percent())),
                    80,
                ),
            )

        tokens_repr = " ".join(
            str(i + 1) + random.choice("+!$*=") for i, _ in enumerate(tokens_1m)
        )
        place_text(
            tokens_repr,
            W // 2,
            H // 32,
            transparent=True,
            renderer=base_font_reg,
            base_col=interpolate(
                quadra_col_1, quadra_col_2, 1 - quadra_timer.get_percent()
            ),
        )

        # text = font.render(morfer.morf_text("PAUSED"), True, colors.col_bg_darker)
        # textRect = text.get_rect()
        # textRect.center = (W//2, H//2)
        # display_surface.blit(text, textRect)

        # is_pause_displayed = True

    if paused and not paused_manually:
        if not burner_casted:
            if game.is_burning() and not TEST:
                burning_list = game.get_burning_features_list()
                with open(BURNER_FILE, "a") as burning_file:
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
        if keys[pygame.K_RSHIFT]:
            if paused_manually or timer_dropped:
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
            if len(tokens_1m) > 5:
                tokens_1m = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        continue

    # trans_surface.set_alpha(20)

    display_surface.fill(white)

    pause_counter_ticked = pause_counter.is_tick(time_delta)
    chain_altered = game.chain_alter_notify

    if pause_counter_ticked and chain_altered: 
        print("chain processed")

        game.chain_alter_notify = False

        paused = True
        paused_manually = False
        tokens_1m = []
        timer_1m.drop_elapsed()
        timer_dropped = False
        pause_counter.overtime = 0

    if pause_counter_ticked and not chain_altered:
        print("overtime")
        pause_counter.set_overtime()

    if new_line_counter.is_tick(time_delta):
        next_tick_time, meta, meta_minor = game.add_line()
        new_line_counter.modify_bpm(next_tick_time)

        # pyautogui.moveTo(SCREEN_X_0//2+W//64, SCREEN_Y_0 + H//2, H//2)

    upper_stats.redraw()
    feedback = game.tick(time_delta)

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

    # HORISONTAL
    pygame.draw.rect(
        display_surface,
        interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
        (W // 2 - ((W // 2) * (quadra_w_perce1)), H - 20, (W) * quadra_w_perce1, 20),
    )

    pygame.draw.rect(
        display_surface,
        interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
        (W // 2 - ((W // 2) * (quadra_w_perce1)), 0, (W) * quadra_w_perce1, 20),
    )

    # VERTICAL
    pygame.draw.rect(
        display_surface,
        interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
        (W - 40, H // 2 - ((H // 2) * (quadra_w_perce1)), 40, (H) * quadra_w_perce1),
    )

    pygame.draw.rect(
        display_surface,
        interpolate(quadra_col_1, quadra_col_2, quadra_timer.get_percent()),
        (0, H // 2 - ((H // 2) * (quadra_w_perce1)), 40, (H) * quadra_w_perce1),
    )

    if haptic_timer.is_tick(time_delta):
        if HAPTIC_FEEDBACK and not disable_haptic:
            inter_freq = int(inter_simple(0, 65000, quadra_w_perce1))
            HAPTIC_FEEDBACK(higher_freq  = inter_freq)


    pygame.display.update()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_TAB]:
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
