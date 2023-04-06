from config import W, H, CHINESE_FONT, CYRILLIC_FONT, W_OFFSET, H_OFFSET
from colors import white
import colors
from itertools import islice
import random
import os
import re


class UpperLayout:
    def __init__(S, pygame_instance, display_instance):
        S.W = W
        S.H = H
        S.y1 = 0
        S.y2 = S.H // 8
        S.y3 = S.H - S.H // 16
        S.higher_center = (S.y1 + S.y2) / 2
        S.pygame_instance = pygame_instance
        S.display_instance = display_instance
        S.backgroudn_color = (60, 60, 60)
        S.bg_color = colors.col_black
        font_file = pygame_instance.font.match_font("setofont")
        S.font = pygame_instance.font.Font(font_file, 50)
        S.large_font = pygame_instance.font.Font(font_file, 80)
        S.utf_font1 = S.pygame_instance.font.Font(CHINESE_FONT, 120)
        S.utf_font2 = S.pygame_instance.font.Font(CHINESE_FONT, 80)
        S.utf_font3 = S.pygame_instance.font.Font(CHINESE_FONT, 40)
        S.utf_font4 = S.pygame_instance.font.Font(CHINESE_FONT, 30)
        S.utf_font5 = S.pygame_instance.font.Font(CHINESE_FONT, 20)

        S.lat_font1 = S.pygame_instance.font.Font(CYRILLIC_FONT, 120)
        S.lat_font2 = S.pygame_instance.font.Font(CYRILLIC_FONT, 80)
        S.lat_font3 = S.pygame_instance.font.Font(CYRILLIC_FONT, 50)
        S.lat_font4 = S.pygame_instance.font.Font(CYRILLIC_FONT, 40)
        S.lat_font5 = S.pygame_instance.font.Font(CYRILLIC_FONT, 30)
        S.combo = 1
        S.tiling = ""
        S.tiling_utf = True
        S.show_less = False

        S.global_progress = ""

        S.speed_index = 5000
        S.percent = 0.8
        S.progress_ratio = 0.0
        S.timing_ratio = 1.0
        S.mastered = 0
        S.to_master = 0
        S.variation = 0
        S.variation_on_rise = True
        S.blink_flag = False
        # S.blink_flag = True

        S.random_variation = 0
        S.constant_variation = 0
        S.chain_no = 0

        S.images_cached = {}
        S.image = None
        S.images_set = None
        S.images_set_cached = None

        S.tiling_meta = "5 img feat"
        S.tiling_cooldown = 0
        S.tiling_var = lambda a, b: a == b

    def place_text(
        S, text, x, y, transparent=False, renderer=None, base_col=(80, 80, 80)
    ):
        if renderer is None:
            renderer = S.font
        if not transparent:
            text = renderer.render(text, True, base_col, (150, 150, 151))
        else:
            text = renderer.render(text, True, base_col)
        textRect = text.get_rect()
        textRect.center = (x, y)
        S.display_instance.blit(text, textRect)

    def check_cached_image(S, path_to_image):
        if len(S.images_cached) > 100:
            S.images_cached = dict(islice(S.images_cached.items(), 50))

        if not path_to_image or not os.path.exists(path_to_image):
            S.images_cached[path_to_image] = None
            return

        if path_to_image in S.images_cached:
            return

        image_converted = S.pygame_instance.image.load(path_to_image).convert()
        image_converted.set_alpha(200)
        image_scaled = S.pygame_instance.transform.scale(
            image_converted, (int(W * 0.95), int(H * 0.95))
        )
        S.images_cached[path_to_image] = image_scaled

    def co_variate(S):

        if S.tiling_cooldown:
            S.tiling_cooldown -= 1
        else:
            S.tiling_cooldown = random.randint(3, 8)
            S.tiling_meta = random.choice(
                [
                    "next/prev",
                    "feat",
                    "img feat",
                    "mnem story",
                    "img/feat stor.",
                    "example",
                ]
            )
            # S.tiling_meta += random.choice(["", " FP"])

        S.tiling_var = random.choice(
            [
                lambda a, b: a == b,
                lambda a, b: a == 1,
                lambda a, b: a == 2,
                lambda a, b: a == 3,
                lambda a, b: b == 1,
                lambda a, b: b == 2,
                lambda a, b: b == 3,
                lambda a, b: a == 4 - b,
                lambda a, b: b == 4 - a,
                lambda a, b: a == 3 - b,
                lambda a, b: b == 3 - a,
                lambda a, b: a == 2 - b,
                lambda a, b: b == 2 - a,
            ]
        )

    def set_image(S, path_to_image):
        # S.co_variate()

        if isinstance(path_to_image, list):
            if path_to_image == S.images_set_cached:
                return
            S.images_set = []
            S.images_set_cached = []
            S.image = None
            for image_name in path_to_image:
                S.check_cached_image(image_name)
                if image_name in S.images_cached and S.images_cached[image_name]:
                    if len(path_to_image) != 2:
                        S.images_set.append(
                            S.pygame_instance.transform.scale(
                                S.images_cached[image_name],
                                (int((W * 0.95) / 3), int(H * 0.95) / 2),
                            )
                        )
                    else:
                        S.images_set.append(S.images_cached[image_name])

                else:
                    S.images_set.append(None)
            return

        else:
            S.images_set = None

        if not path_to_image in S.images_cached:
            S.check_cached_image(path_to_image)

        S.image = S.images_cached[path_to_image]

    def randomize(S):
        S.random_variation = random.choice([-1, 0, 1])

    def redraw(S):
        clip_color = lambda _: 0 if _ <= 0 else 255 if _ >= 255 else int(_)
        tiling_len = len(S.tiling)
        if re.findall(r"[\u4e00-\u9fff]+", S.tiling):
            tiling_font = (
                S.utf_font1
                if tiling_len == 1
                else S.utf_font2
                if tiling_len == 2
                else S.utf_font3
                if tiling_len == 3
                else S.utf_font4
                if tiling_len < 5
                else S.utf_font5
            )
        else:
            tiling_font = (
                S.lat_font1
                if tiling_len == 1
                else S.lat_font2
                if tiling_len == 2
                else S.lat_font3
                if tiling_len == 3
                else S.lat_font4
                if tiling_len < 5
                else S.lat_font5
            )

        S.display_instance.fill(S.bg_color)
        tiling_step = 270

        if S.images_set:
            set_locations = []
            if len(S.images_set) != 2:
                set_locations.append((int(W * (0.05 / 2)), int(H * (0.05 / 6))))  # 0
                set_locations.append(
                    (
                        int(W * (0.05 / 2) + (W * 0.95 / 3) * (0)),
                        int(H * (0.05 / 2) + H * 0.95 / 2),
                    )
                )  # 1
                set_locations.append(
                    (
                        int(W * (0.05 / 2) + (W * 0.95 / 3) * (1)),
                        int(H * (0.05 / 2) + H * 0.95 / 2),
                    )
                )  # 2
                set_locations.append(
                    (
                        int(W * (0.05 / 2) + (W * 0.95 / 3) * (2)),
                        int(H * (0.05 / 2) + H * 0.95 / 2),
                    )
                )  # 3
                set_locations.append(
                    (int(W * (0.05 / 2) + (W * 0.95 / 3) * (2)), int(H * (0.05 / 6)))
                )  # 5

                if int(S.chain_no) % 2 == 0:
                    set_locations = set_locations[::-1]

            if len(S.images_set) == 2:
                set_locations.append((int(-1 * (W // 2) + 150), int(H * (0.05 / 2))))
                set_locations.append((int(W // 2), int(H * (0.05 / 2))))
                if int(S.chain_no) % 2 == 0:
                    set_locations = set_locations[::-1]

            for i in range(len(S.images_set)):
                if i < len(S.images_set) and S.images_set[i]:
                    S.display_instance.blit(S.images_set[i], set_locations[i])
            tiling_step = 400

        elif S.image:
            S.display_instance.blit(
                S.image,
                (
                    int(W * (0.05 / 2)) + S.random_variation,
                    int(H * (0.05 / 2)) + S.random_variation,
                ),
            )
            tiling_step = 400

        elif not S.images_set and not S.image:
            S.pygame_instance.draw.rect(
                S.display_instance,
                white,
                (W_OFFSET, H_OFFSET, W - W_OFFSET * 2, H - H_OFFSET * 2),
            )

        if S.variation_on_rise:
            S.variation += 1
        else:
            S.variation -= 1

        if S.variation > 10:
            S.variation_on_rise = False
            if random.randint(0, 10) > 7 and S.blink_flag:
                S.blink_flag = False

        elif S.variation < 0:
            S.variation_on_rise = True
            if random.randint(0, 100) > 95 and not S.blink_flag:
                S.blink_flag = False

        for i, x in enumerate(range(100 + S.random_variation, W, tiling_step)):
            for j, y in enumerate(range(100 + S.random_variation, H, tiling_step)):

                tiling_text = S.tiling
                t_font = tiling_font
                extra_text = ""

                if S.tiling_var(i, j):
                    t_font = S.utf_font4
                    tiling_text = S.tiling_meta
                    extra_text = f" {S.tiling_cooldown}"
                else:
                    continue

                S.place_text(
                    tiling_text + extra_text,
                    x,
                    y,
                    transparent=True,
                    renderer=t_font,
                    base_col=(
                        clip_color(225 + S.variation * 4 + S.random_variation),
                        225 - S.variation + S.random_variation,
                        225 + S.random_variation,
                    ),
                )

        line_color = (int(255 * (1 - S.percent)), int(255 * (S.percent)), 0)

        S.place_text(
            str(S.combo) + "x",
            W // 2 - 100,
            50,
            transparent=True,
            renderer=S.large_font,
            base_col=(70, 70, 70),
        )

        S.place_text(
            str(S.global_progress),
            W // 2 - 300,
            30,
            transparent=True,
            renderer=S.font,
            base_col=(70, 70, 70),
        )

        S.place_text(
            str(S.combo) + "x",
            W // 2 + 100,
            50,
            transparent=True,
            renderer=S.large_font,
            base_col=(70, 70, 70),
        )

        S.place_text(
            str(S.global_progress),
            W // 2 + 300,
            30,
            transparent=True,
            renderer=S.font,
            base_col=(70, 70, 70),
        )

        line_color = (
            clip_color((178) * (1 - S.timing_ratio) + S.random_variation),
            clip_color((150) * (S.timing_ratio) + S.random_variation),
            clip_color((150) * (1 - S.timing_ratio) + S.random_variation),
        )

        if (S.random_variation == 0 or S.random_variation == -1) and not (
            S.blink_flag and S.variation % 7 == 0
        ):
            S.pygame_instance.draw.rect(
                S.display_instance,
                line_color,
                (
                    (W // 2 - ((600) * (S.timing_ratio)) / 2),
                    H // 2 - 50,
                    (600) * S.timing_ratio,
                    100,
                ),
            )

        if (S.random_variation == 0 or S.random_variation == 1) and not (
            S.blink_flag and S.variation % 7 == 0
        ):
            S.pygame_instance.draw.rect(
                S.display_instance,
                line_color,
                (
                    W // 2 - 50,
                    (H // 2 - ((600) * (S.timing_ratio)) / 2),
                    100,
                    (600) * S.timing_ratio,
                ),
            )
        if S.show_less:
            return
