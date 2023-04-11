import subprocess
from collections import OrderedDict
from itertools import groupby
import random
import re
from math import sin, cos, pi

from utils import raw_extracter
from learning_model import ChainedFeature, FeaturesChain, ChainedModel, ChainUnitType
from config import W, H, CYRILLIC_FONT, CHINESE_FONT
from config import META_SCRIPT, META_MINOR, META_ACTION
from config import META_ACTION_STACK
from colors import col_wicked_darker
from colors import col_active_darker
import colors

from text_morfer import textMorfer

LAST_EVENT = "POSITIVE"
NEW_EVENT = False
morfer = textMorfer()

######################################
# DATA PRODUCER
######################################


class ChainedsProducer:
    def __init__(
        S,
        label,
        csv_path,
        meta_path=None,
        meta_action_stack=None,
        minor_meta=None,
        meta_actions=None,
        ui_ref=None,
    ):
        S.csv_path = csv_path
        S.label = label
        S.meta_path = meta_path
        S.minor_meta = minor_meta
        S.meta_stack = meta_action_stack

        S.meta_lines = S.extract_meta(S.meta_path) if S.meta_path else []
        S.minor_lines = S.extract_meta(S.minor_meta) if S.minor_meta else []
        S.action_lines = S.extract_meta(meta_actions) if meta_actions else []
        S.chains = S.prepare_data()
        S.active_chain = S.chains.get_active_chain()
        S.ui_ref = ui_ref
        S.chain_alter_notify = False

    def extract_meta(S, meta_path):
        meta = []
        header = None

        with open(meta_path, "r", encoding="UTF-8") as metafile:
            for line in metafile:
                line = line[:-1]
                if S.meta_stack and line in S.meta_stack:
                    header = line
                    continue
                if header:
                    S.meta_stack[header].append(line)

                meta.append(line.upper())

        return meta

    def prepare_data(S):
        data_extractor = raw_extracter(S.csv_path)
        chains = []
        for key, group in groupby(list(_ for _ in data_extractor), key=lambda _: _[0]):
            features = []
            for item in group:
                interactive = list(_ for _ in item if "***" not in _)
                info = list(_ for _ in item if "***" in _)
                info = info[0] if len(info) > 0 else ""
                entity, *key_features = interactive[1:]
                features.append(ChainedFeature(entity, key_features))
                features[-1].original_len = len(key_features)
                features[-1].info = info.replace("***", "")

            for i1 in range(len(features)):
                i2 = (i1 + 1) % len(features)

                if len(features[i1].features) < 5:
                    l1 = len(features[i1].features)
                    l2 = len(features[i2].features) + 1

                    if l1 + l2 <= 5:
                        features[i1].features += [features[i2].entity] + features[
                            i2
                        ].features[:]
                    else:
                        extra_len = 5 - l1 - 1
                        if extra_len <= 0:
                            features[i1].features += [features[i2].entity]
                        else:
                            features[i1].features += [features[i2].entity] + features[
                                i2
                            ].features[:extra_len]

            chains.append(FeaturesChain(key, features))

        return ChainedModel(chains)

    def produce_chain(S):
        S.active_chain = S.chains.get_active_chain()
        return S.active_chain

    def produce_next_feature(S):
        feature = S.chains.get_next_feature()
        if S.chains.chain_alter_notify:
            S.chain_alter_notify = True
            S.chains.chain_alter_notify = False

        return feature

    def is_burning(S):
        return S.chains.is_burning()

    def get_burning_features_list(S):
        return S.chains.get_burning_features_list()

    def produce_meta(S):
        if S.meta_lines:
            minor_idx = random.randint(0, len(S.meta_lines) - 5)
            return "*".join(S.meta_lines[minor_idx : minor_idx + 4])
        return ""

    def produce_meta_minor(S):
        if S.minor_lines:
            minor_idx = random.randint(0, len(S.minor_lines) - 4)
            lines = S.minor_lines[minor_idx : minor_idx + 3]

            if any(S.meta_stack.values()):
                ordered_meta = []
                for key, stk in S.meta_stack.items():
                    if random.randint(0, 10) > 4:
                        continue
                    if stk:
                        ordered_meta.append(key + " " + random.choice(stk))
                    else:
                        ordered_meta.append(key + " " + "---" * 5)
                lines = ordered_meta + lines

            elif S.action_lines:
                lines = [random.choice(S.action_lines)] + lines

            return lines
        return ""


######################################
# ENTITIES HANDLER TEXT_AND_POSE
######################################


class ChainedEntity:
    def __init__(S, chained_feature, features_chain, chains, pygame_instance, W, H):

        S.W, S.H = W, H

        S.chained_feature = chained_feature
        S.features_chain = features_chain
        S.chains = chains
        S.main_title = S.chained_feature.get_main_title()
        S.context = sorted(S.chained_feature.get_context(), key=lambda _: _.order_no)
        S.order_in_work = 0

        S.pygame_instance = pygame_instance

        S.correct = False
        S.error = False

        S.feedback = None

        S.done = True
        S.locked = False
        S.tries = 3


        S.time_perce_reserved = 0.0
        S.time_perce_active = 0.0

        S.options = None
        S.active_question = None

        S.keyboard_input = ""
        S.input_mode = False
        S.forgive_typo = True
        #S.input_mode = True

        S.reinput_positive_keyboard = False
        S.reinput_positive_mouse = False
        S.drop = False

        S.questions_queue = S.extract_questions()
        S.constant_variation = random.randint(0, 10)

        S.idle_coursor_x = None
        S.idle_coursor_y = None
        S.hint_circles_queue = []


        if S.questions_queue:

            for_input = list(_ for _ in S.chained_feature.features if not re.search(r"[^\x00-\x7F]", _))
            total_inp_len = len("".join(for_input))/5
            # 10 symbols per se
            if total_inp_len > 4:
                S.time_estemated = S.chained_feature.get_timing() / (
                    total_inp_len*2 )
            else:
                S.time_estemated = S.chained_feature.get_timing() / (
                    len(S.questions_queue) + 1 )
            
            S.done = False
        else:
            S.time_estemated = S.chained_feature.get_timing() / (len(S.context) + 1)

    def extract_questions(S):
        questions = list(
            filter(lambda _: _.mode == ChainUnitType.mode_question, S.context)
        )
        if questions:
            S.active_question = questions[0]
            S.active_question.mode = ChainUnitType.mode_active_question
            S.generate_options()

            if re.search(r"[^\x00-\x7F]", S.active_question.text):
                S.input_mode = False
            else:
                S.input_mode = True

        return questions

    def generate_options(S):
        if S.active_question:
            S.options = S.chains.get_options_list(S.active_question)

    def delete_options(S):
        S.options = ["" for _ in range(10)]

    def register_answers(S):
        is_solved = (len(S.questions_queue) == 0 and not S.locked) or S.reinput_positive_keyboard
        S.chained_feature.register_progress(is_solved=is_solved)
        return is_solved

    def match_correct(S):

        # if S.locked:
        # return

        global LAST_EVENT
        global NEW_EVENT

        if not S.locked:
            LAST_EVENT = "POSITIVE"
            NEW_EVENT = True
            S.forgive_typo = True
        else:
            LAST_EVENT = "POST_POSITIVE"
            NEW_EVENT = True
            S.tries = 3

        S.keyboard_input = ""

        S.order_in_work += 1
        if S.questions_queue:
            S.questions_queue.pop(0)
            S.active_question.mode = ChainUnitType.mode_open


        if S.questions_queue:
            S.active_question.mode = ChainUnitType.mode_open
            S.active_question = S.questions_queue[0]

            if re.search(r"[^\x00-\x7F]", S.active_question.text):
                S.input_mode = False
            else:
                S.input_mode = True

            S.generate_options()
        else:
            S.delete_options()
            S.active_question = None
            S.done = True

            if S.reinput_positive_keyboard:
                S.drop = True
                return
            
            if S.time_perce_reserved <= 0.5:
                S.reinput_positive_keyboard = True
                S.context = sorted(S.chained_feature.get_context(), key=lambda _: _.order_no)
                S.questions_queue = S.extract_questions()
                S.active_question = S.questions_queue[0]
                S.generate_options()
                S.locked = True
                S.done = False
            #  else:
            #      S.reinput_positive_mouse = True
                
            S.order_in_work = 0

    def match_error(S, minor_error = False):
        global LAST_EVENT
        global NEW_EVENT
        LAST_EVENT = "ERROR"

        S.keyboard_input = ""

        if S.forgive_typo and minor_error and not S.locked:
            S.forgive_typo = False
            return

        if not S.locked:
            NEW_EVENT = True
            S.chained_feature.register_error(S.active_question.order_no)
            S.features_chain.update_errors(register_new=True)

        S.locked = True

        if S.locked:
            S.tries -= 1
            if S.tries == 1:
                S.input_mode = False
            if S.tries == 0:
                S.drop = True

    def register_mouse(S, mouse_poses):

        if not S.done:
            return

        mouse_position = S.pygame_instance.mouse.get_pos()

        LMB, RMB = 0, 2

        if mouse_poses[LMB]:
            index = S.order_in_work

            # if index == 0:
            #    return
            index -= 1

            if index < len(S.context) and index >= 0 and S.context[index]:

                rel_x = mouse_position[0] / W
                rel_y = mouse_position[1] / H

                S.chained_feature.register_hint(S.context[index].order_no, rel_x, rel_y)
                S.context[index].hint = [rel_x, rel_y]
                S.features_chain.update_hints()
        
        if mouse_poses[RMB]:
            S.drop = True
            #  index = S.order_in_work
            #  if index < len(S.context) and S.context[index].hint:
            #      S.order_in_work += 1

    def register_idle_mouse(S):

        mouse_position = S.pygame_instance.mouse.get_pos()
        S.idle_coursor_x = mouse_position[0]
        S.idle_coursor_y = mouse_position[1]

    def check_keyboard_input(S):
        if S.active_question:
            if S.keyboard_input.lower().strip() == S.active_question.text.lower().strip():
                S.match_correct()
            else:
                unique_letters_inp = len(set(S.keyboard_input.lower()))
                unique_letters_ans = len(set(S.active_question.text.lower()))
                if abs(unique_letters_inp - unique_letters_ans) <= 2:
                    S.match_error(minor_error = True)
                else:
                    S.match_error(minor_error = False)


    def process_keyboard_input(S, keyboard):

        if any(keyboard):
            key_states = [_[0] for _ in keyboard if _[1]=="pressed" and not (_[0] == "lshift" or _[0]=="rshift" or _[0]=="\t")]
            down_keys = [_[0] for _ in keyboard if _[1]=="down"]

            if not key_states:
                return

            if key_states[0] == "backspace":
                if S.keyboard_input:
                    S.keyboard_input = S.keyboard_input[:-1]
                    return

            elif key_states[0] == "return":
                S.check_keyboard_input()

            else:
                shift = False
                if "lshift" in down_keys or "rshift" in down_keys:
                    shift = True

                new_key = key_states[0]
                if shift:
                    shift_mapping = {a:b for (a,b) in zip("1234567890-=qwertyuiop[]\\asdfghjkl;\'zxcvbnm,./ ",
                                                          "!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>? ")}
                    new_key = shift_mapping[new_key]
                    S.keyboard_input += new_key
                else:
                    S.keyboard_input += new_key



    def register_keys(S, key_states, keys_extended, time_percent, time_based=False):
        S.time_perce_active = time_percent
        if S.active_question and not time_based:
            S.time_perce_reserved = time_percent

            if S.input_mode:
                S.process_keyboard_input(keys_extended)
            else:
                for i, key in enumerate(key_states):
                    if key:
                        if S.options[i] == S.active_question.text:
                            S.match_correct()
                        else:
                            S.match_error()

        elif time_based and not S.active_question:
            time_p = time_percent

            if not S.done:
                S.time_perce_reserved = time_percent

            if S.done:
                time_p = (time_p - S.time_perce_reserved) / (
                    1.0 - S.time_perce_reserved
                )

            # n_pairs = len(S.context)/2
            n_pairs = len(S.context)
            pair_perce = 1 / (n_pairs + 1)

            pair_to_show = int(time_p / pair_perce)

            if not S.reinput_positive_mouse:
                S.order_in_work = pair_to_show

    def produce_geometries(S):
        graphical_objects = []

        inter_color = lambda v1, v2, p: v1 + (v2 - v1) * p
        interpolate = lambda col1, col2, percent: (
            inter_color(col1[0], col2[0], percent),
            inter_color(col1[1], col2[1], percent),
            inter_color(col1[2], col2[2], percent),
        )
        clip_color = lambda _: 0 if _ <= 0 else 255 if _ >= 255 else int(_)
        validate_color = lambda col : (clip_color(col[0]), clip_color(col[1]), clip_color(col[2]))

        def set_color(_):
            if _.order_no < S.chained_feature.original_len:
                return validate_color(interpolate(colors.feature_bg, colors.col_active_lighter, sin(S.time_perce_active*(pi*2*3) ) ) )
            return validate_color(interpolate(colors.feature_bg, colors.col_active_lighter, cos(S.time_perce_active*(pi*2*3) ) ) )


        def set_bg_color(_):
            return (
                colors.col_bt_down
                if _.extra
                else col_active_darker
                if _.type == ChainUnitType.type_key
                else colors.feature_bg
            )

        def get_text(_):
            return _.text if S.done or _.mode == ChainUnitType.mode_open else "???"

        def get_y_position(_):
            return (
                S.H // 2 - S.H // 4 + S.H // 16
                if _.position == ChainUnitType.position_subtitle
                else S.H // 2 - S.H // 16
                if _.position == ChainUnitType.position_keys
                else S.H // 2 + S.H // 16
            )

        def set_font(_):
            return (
                ChainUnitType.font_cyrillic
                if not re.search(u"[\u4e00-\u9fff]", _.text)
                else ChainUnitType.font_utf
            )

        def set_size(_):
            return (
                10
                if len(_.text) >= 15
                else 20
                if len(_.text) >= 10
                else 30
                if len(_.text) >= 5
                else 40
            )

        ctx_len = len(S.context)
        ctx_y_origin = H // 2 - 150
        ctx_x_origin = W // 2

        out_positions = []
        w, h = int(W * 0.95), int(H * 0.95)
        if ctx_len == 1:
            out_positions.append([w // 2, 5 * h // 6 - h // 6])
        if ctx_len == 2:
            out_positions.append([w // 6 + w // 6, h // 6 + h // 6])
            out_positions.append([5 * w // 6 - w // 6, 5 * h // 6 - h // 6])
        if ctx_len == 3:
            out_positions.append([w // 6 + w // 6, h // 6 + h // 6])
            out_positions.append([w // 2, 5 * h // 6 - h // 6])
            out_positions.append([5 * w // 6 - w // 6, h // 6 + h // 6])
        if ctx_len == 4:
            out_positions.append([w // 6 + w // 6, h // 6 + h // 6])
            out_positions.append([w // 6 + w // 6, 5 * h // 6 - h // 6])
            out_positions.append([5 * w // 6 - w // 6, 5 * h // 6 - h // 6])
            out_positions.append([5 * w // 6 - w // 6, h // 6 + h // 6])
        if ctx_len >= 5:
            out_positions.append([w // 6, h // 6 + h // 12])
            out_positions.append([w // 6, 5 * h // 6 - h // 12])
            out_positions.append([w // 2, 5 * h // 6 - h // 12])
            out_positions.append([5 * w // 6, 5 * h // 6 - h // 12])
            out_positions.append([5 * w // 6, h // 6 + h // 12])

        for ctx in S.context:
            order_y_origin = ctx_y_origin
            ctx_x = ctx_x_origin
            ctx_h = 50
            ctx_w = 250
            ctx_order = ctx.order_no
            ctx_type = ctx.type

            order_delta = S.order_in_work - ctx_order

            if order_delta < 0:
                ctx_x -= ctx_w // 2
                order_y_origin -= 25
            elif order_delta > 0:
                order_y_origin += 200 + 25
            elif order_delta == 0:
                ctx_x -= ctx_w // 2

            if ctx_type == ChainUnitType.type_feature:
                ctx_y = order_y_origin + order_delta * 50

            else:
                ctx_y = order_y_origin + order_delta * 50

            cx, cy = ctx_x + ctx_w / 2, ctx_y + ctx_h / 2

            if order_delta > 0:

                if int(S.features_chain.chain_no) % 2:
                    pos_no = ctx.order_no
                    pos_no %= len(out_positions)
                    ctx_x, ctx_y = out_positions[pos_no]
                    if ctx.hint:
                        rel_x, rel_y = ctx.hint
                        ctx_x, ctx_y = rel_x * W, rel_y * H

                    if ctx.order_no >= len(out_positions):
                        ctx_y += ctx.order_no // len(out_positions) * 100
                else:
                    pos_no = ctx_len - 1 - ctx.order_no
                    pos_no %= len(out_positions)
                    ctx_x, ctx_y = out_positions[pos_no]
                    if ctx.hint:
                        rel_x, rel_y = ctx.hint
                        ctx_x, ctx_y = rel_x * W, rel_y * H

                    if ctx.order_no >= len(out_positions):
                        ctx_y += ctx.order_no // len(out_positions) * 100

                cx, cy = ctx_x, ctx_y
                cx, cy = ctx_x - ctx_w // 4, ctx_y - ctx_h

                # ctx_x -= ctx_w/2
                # ctx_y -= ctx_h/2

                ctx_x += int(W * 0.05 / 2)
                cx += int(W * 0.05 / 2)
                ctx_y += int(H * 0.05 / 2)
                cy += int(H * 0.05 / 2)

            if order_delta <= 0:
                continue

            graphical_objects.append(
                WordGraphical(
                    get_text(ctx),
                    cx,
                    cy,
                    set_color(ctx),
                    None,
                    font=set_font(ctx),
                    font_size=set_size(ctx) * 3,
                    rect=None,
                    morph = False
                )
            )

        options_w = 250
        options_h = 75

        options_x_corners = [
            W // 2 - W // 5 - options_w // 2 + 100,
            W // 2 - W // 5 - options_w // 2 + 50,
            W // 2 - W // 5 - options_w // 2,
            W // 2 - W // 5 - options_w // 2 + 50,
            W // 2 - W // 5 - options_w // 2 + 100,
            W // 2 + W // 5 - options_w // 2 - 100,
            W // 2 + W // 5 - options_w // 2 - 50,
            W // 2 + W // 5 - options_w // 2,
            W // 2 + W // 5 - options_w // 2 - 50,
            W // 2 + W // 5 - options_w // 2 - 100,
        ]

        options_y_corners = [
            1 * H // 12 - options_h // 2 + H // 4,
            2 * H // 12 - options_h // 2 + H // 4,
            3 * H // 12 - options_h // 2 + H // 4,
            4 * H // 12 - options_h // 2 + H // 4,
            5 * H // 12 - options_h // 2 + H // 4,
            1 * H // 12 - options_h // 2 + H // 4,
            2 * H // 12 - options_h // 2 + H // 4,
            3 * H // 12 - options_h // 2 + H // 4,
            4 * H // 12 - options_h // 2 + H // 4,
            5 * H // 12 - options_h // 2 + H // 4,
        ]

        def set_font(_):
            return (
                ChainUnitType.font_cyrillic
                if not re.search(u"[\u4e00-\u9fff]", _)
                else ChainUnitType.font_utf
            )

        # set_size = lambda _ : 30 if not re.search(u'[\u4e00-\u9fff]', _) else 40
        def set_size(_):
            return (
                15
                if len(_) >= 15
                else 25
                if len(_) >= 10
                else 30
                if len(_) >= 5
                else 40
            )

        if S.options and not S.input_mode:
            for i, (x1, y1) in enumerate(zip(options_x_corners, options_y_corners)):
                xc, yc = x1 + options_w / 2, y1 + options_h / 2

                graphical_objects.append(
                    WordGraphical(
                        S.options[i],
                        xc,
                        yc,
                        colors.col_bt_text,
                        transparent=True,
                        font=set_font(S.options[i]),
                        font_size=int(set_size(S.options[i]) * 1.5),
                        rect=None,
                    )
                )

        large_notion_w = 250
        large_notion_h = 200
        large_notions_x_corners = [W // 2]
        large_notions_y_corners = [H // 2]
        large_notion_col = validate_color(interpolate(colors.feature_text_col, colors.col_bg_lighter, sin(S.time_perce_active*(pi*2*4))))
        for i, (x1, y1) in enumerate(
            zip(large_notions_x_corners, large_notions_y_corners)
        ):
            xc, yc = x1, y1

            tlen = len(S.chained_feature.entity)
            graphical_objects.append(
                WordGraphical(
                    S.chained_feature.entity + ("+" if S.forgive_typo else ""),
                    xc,
                    yc,
                    large_notion_col,
                    bg_color=None,
                    font_size=300
                    if tlen == 1
                    else 250
                    if tlen == 2
                    else 200
                    if tlen == 3
                    else 150
                    if tlen < 5
                    else 100
                    if tlen < 10
                    else 50,
                    font=ChainUnitType.font_utf
                    if re.findall(r"[\u4e00-\u9fff]+", S.chained_feature.entity)
                    else ChainUnitType.font_cyrillic,
                    rect=None,
                )
            )
        large_notion_w = 250
        large_notion_h = 200
        large_notions_x_corners = [W // 2]
        large_notions_y_corners = [H // 2 - H//4]
        large_notion_col = validate_color(interpolate(colors.feature_text_col, colors.col_bg_lighter, sin(S.time_perce_active*(pi*2*4))))
        for i, (x1, y1) in enumerate(
            zip(large_notions_x_corners, large_notions_y_corners)
        ):
            if not S.chained_feature.info:
                break
            xc, yc = x1, y1

            tlen = len(S.chained_feature.info)
            graphical_objects.append(
                WordGraphical(
                    S.chained_feature.info,
                    xc,
                    yc,
                    large_notion_col,
                    bg_color=None,
                    font_size=300
                    if tlen == 1
                    else 250
                    if tlen == 2
                    else 200
                    if tlen == 3
                    else 150
                    if tlen < 5
                    else 100
                    if tlen < 10
                    else 50,
                    font=ChainUnitType.font_utf
                    if re.findall(r"[\u4e00-\u9fff]+", S.chained_feature.info)
                    else ChainUnitType.font_cyrillic,
                    rect=None,
                )
            )


        ## KEYBOARD INPUT INITIAL
        index = S.order_in_work

        def set_size(_):
            return (
                15
                if len(_) >= 15
                else 25
                if len(_) >= 10
                else 30
                if len(_) >= 5
                else 40
            )
        if not S.done:
            if index < len(S.context) and index >= 0 and S.context[index].hint:
                rel_x, rel_y = S.context[index].hint
                abs_x, abs_y = rel_x * W, rel_y * H

            else:
                abs_x, abs_y = out_positions[index]

            large_notion_w = 250
            large_notion_h = 200
            large_notions_x_corners = [abs_x]
            large_notions_y_corners = [abs_y]

            large_notion_col = validate_color(interpolate(colors.feature_text_col, colors.col_bg_lighter, sin(S.time_perce_active*(pi*2*4))))
            for i, (x1, y1) in enumerate(
                zip(large_notions_x_corners, large_notions_y_corners)
            ):
                xc, yc = x1, y1

                tlen = len(S.keyboard_input)
                graphical_objects.append(
                    WordGraphical(
                        S.keyboard_input,
                        xc,
                        yc,
                        large_notion_col,
                        bg_color=None,
                        font_size = set_size(S.keyboard_input),
                        font=ChainUnitType.font_utf
                        if re.findall(r"[\u4e00-\u9fff]+", S.keyboard_input)
                        else ChainUnitType.font_cyrillic,
                        rect=None,
                    )
                )


        return graphical_objects

    def produce_hints(S):
        hints = []
        index = S.order_in_work

        # if S.locked:
        if S.done or S.reinput_positive_mouse:
            if (
                index >= 0
                and index < len(S.context)
                and S.idle_coursor_x
                and S.idle_coursor_y
            ):
                hints.append(
                    [S.idle_coursor_x, S.idle_coursor_y, H // 25, 3, colors.col_bg_lighter]
                )


        if not S.done:
            if index < len(S.context) and index >= 0 and S.context[index].hint:
                rel_x, rel_y = S.context[index].hint
                abs_x, abs_y = rel_x * W, rel_y * H
                hints.append([abs_x, abs_y, H // 20, 3, colors.feature_bg])
            return hints

        index -= 1


        if index < len(S.context) and index >= 0 and S.context[index].hint:
            rel_x, rel_y = S.context[index].hint
            abs_x, abs_y = rel_x * W, rel_y * H
            hints.append([abs_x, abs_y, H // 20, 3, colors.feature_bg])

        for ctx in S.context:
            if ctx.hint:
                rel_x, rel_y = ctx.hint
                abs_x, abs_y = rel_x * W, rel_y * H
                hints.append([abs_x, abs_y, H // 22, 3, colors.col_bt_pressed])

        return hints

    def fetch_feedback(S):
        to_return = S.feedback
        S.feedback = None
        return to_return


######################################
# LINES HANDLER GRAPHICS
######################################


class WordGraphical:
    def __init__(
        S,
        text,
        x,
        y,
        color,
        bg_color=(150, 150, 150),
        font=ChainUnitType.font_utf,
        font_size=None,
        rect=[],
        transparent=False,
        morph = True
    ):
        S.rect = rect
        S.text = text
        S.x = x
        S.y = y
        S.color = color
        S.bg_color = bg_color
        S.font = font
        S.font_size = font_size
        S.transparent = transparent
        S.morph = morph


class ChainedDrawer:
    def __init__(S, pygame_instance, display_instance, W, H):
        S.pygame_instance = pygame_instance
        S.display_instance = display_instance
        S.W = W
        S.H = H
        S.fonts_a = 10
        S.fonts_b = 500
        S.fonts_step = 10
        S.cyrillic_fonts = [
            S.pygame_instance.font.Font(CYRILLIC_FONT, i)
            for i in range(S.fonts_a, S.fonts_b, S.fonts_step)
        ]
        S.utf_fonts = [
            S.pygame_instance.font.Font(CHINESE_FONT, i)
            for i in range(S.fonts_a, S.fonts_b, S.fonts_step)
        ]

    def pick_font(S, font_type=ChainUnitType.font_utf, size=40):
        fonts_size_idx = (size - S.fonts_a) // S.fonts_step

        if fonts_size_idx < 0:
            fonts_size_idx = 0

        if font_type == ChainUnitType.font_utf:
            if fonts_size_idx >= len(S.utf_fonts):
                fonts_size_idx = len(S.utf_fonts) - 1

            return S.utf_fonts[fonts_size_idx]

        else:
            if fonts_size_idx >= len(S.cyrillic_fonts):
                fonts_size_idx = len(S.cyrillic_fonts) - 1

            return S.cyrillic_fonts[fonts_size_idx]

    def draw_keyboard_input(S, line):
        key_input_text = line.keyboard_input

    def draw_hints(S, line):
        circles = line.produce_hints()

        if not circles:
            return

        for circle in circles:
            x, y, r, w, col = circle
            S.pygame_instance.draw.circle(S.display_instance, col, (x, y), r, width=w)

    def draw_line(S, line):
        geometries = line.produce_geometries()
        S.pygame_instance.draw.rect(
            S.display_instance, (10, 10, 10), (W // 2 - 1, 0, 2, H)
        )

        S.pygame_instance.draw.rect(
            S.display_instance, (10, 10, 10), (0, H // 2 - 1, W, 2)
        )

        for geometry in geometries:
            message = geometry.text
            if not re.findall(r"[\u5e00-\u9fff]+", message) and geometry.morph:
                message = morfer.morf_text(message)
            font = S.pick_font(geometry.font, geometry.font_size)

            if not geometry.transparent:
                text = font.render(message, True, geometry.color, geometry.bg_color)
            else:
                text = font.render(message, True, geometry.color)

            textRect = text.get_rect()
            textRect.center = (geometry.x, geometry.y)

            if geometry.rect:

                x, y, w, h = geometry.rect
                S.pygame_instance.draw.rect(
                    S.display_instance,
                    (50, 50, 50),
                    (x, y, w, h),
                    width=2,
                    border_radius=15,
                )

            S.display_instance.blit(text, textRect)

        S.draw_hints(line)

    def display_keys(S, keys, line):
        if line.done or line.input_mode:
            return

        options_x1 = W // 2 - 250
        options_y1 = 325
        options_w = 250
        options_h = 75

        options_x_corners = [
            W // 2 - W // 5 - options_w // 2 + 100,
            W // 2 - W // 5 - options_w // 2 + 50,
            W // 2 - W // 5 - options_w // 2,
            W // 2 - W // 5 - options_w // 2 + 50,
            W // 2 - W // 5 - options_w // 2 + 100,
            W // 2 + W // 5 - options_w // 2 - 100,
            W // 2 + W // 5 - options_w // 2 - 50,
            W // 2 + W // 5 - options_w // 2,
            W // 2 + W // 5 - options_w // 2 - 50,
            W // 2 + W // 5 - options_w // 2 - 100,
        ]

        options_y_corners = [
            1 * H // 12 - options_h // 2 + H // 4,
            2 * H // 12 - options_h // 2 + H // 4,
            3 * H // 12 - options_h // 2 + H // 4,
            4 * H // 12 - options_h // 2 + H // 4,
            5 * H // 12 - options_h // 2 + H // 4,
            1 * H // 12 - options_h // 2 + H // 4,
            2 * H // 12 - options_h // 2 + H // 4,
            3 * H // 12 - options_h // 2 + H // 4,
            4 * H // 12 - options_h // 2 + H // 4,
            5 * H // 12 - options_h // 2 + H // 4,
        ]

        for i, (x1, y1) in enumerate(zip(options_x_corners, options_y_corners)):
            key_state = keys[i]
            xc, yc = x1 + options_w / 2, y1 + options_h / 2

            color = (255, 255, 255)
            if key_state == "up":
                color = (
                    colors.col_bt_down
                    if LAST_EVENT == "POSITIVE"
                    else colors.col_error
                    if LAST_EVENT == "ERROR"
                    else colors.dark_red
                )
            elif key_state == "down":
                color = (
                    colors.col_bt_pressed
                    if LAST_EVENT == "POSITIVE"
                    else colors.col_active_lighter
                )
            else:
                color = (0, 150, 100)

            S.pygame_instance.draw.rect(
                S.display_instance,
                color,
                (x1, y1, options_w, options_h),
                border_radius=15,
            )


######################################
# SIX MODE CONTROLLER
######################################
class KeyboardRawModel:
    def __init__(S, pygame_instance):
        S.pygame_instance = pygame_instance

        S.keys_mapping = {}
        S.keys_mapping["q"] = S.pygame_instance.K_q 
        S.keys_mapping["w"] = S.pygame_instance.K_w 
        S.keys_mapping["e"] = S.pygame_instance.K_e 
        S.keys_mapping["r"] = S.pygame_instance.K_r 
        S.keys_mapping["t"] = S.pygame_instance.K_t 
        S.keys_mapping["y"] = S.pygame_instance.K_y 
        S.keys_mapping["u"] = S.pygame_instance.K_u 
        S.keys_mapping["i"] = S.pygame_instance.K_i 
        S.keys_mapping["o"] = S.pygame_instance.K_o 
        S.keys_mapping["p"] = S.pygame_instance.K_p 
        S.keys_mapping["a"] = S.pygame_instance.K_a 
        S.keys_mapping["s"] = S.pygame_instance.K_s 
        S.keys_mapping["d"] = S.pygame_instance.K_d 
        S.keys_mapping["f"] = S.pygame_instance.K_f 
        S.keys_mapping["g"] = S.pygame_instance.K_g 
        S.keys_mapping["h"] = S.pygame_instance.K_h 
        S.keys_mapping["j"] = S.pygame_instance.K_j 
        S.keys_mapping["k"] = S.pygame_instance.K_k 
        S.keys_mapping["l"] = S.pygame_instance.K_l 
        S.keys_mapping["z"] = S.pygame_instance.K_z 
        S.keys_mapping["x"] = S.pygame_instance.K_x 
        S.keys_mapping["c"] = S.pygame_instance.K_c 
        S.keys_mapping["v"] = S.pygame_instance.K_v 
        S.keys_mapping["b"] = S.pygame_instance.K_b 
        S.keys_mapping["n"] = S.pygame_instance.K_n 
        S.keys_mapping["m"] = S.pygame_instance.K_m 
        S.keys_mapping[" "] = S.pygame_instance.K_SPACE
        S.keys_mapping["return"] = S.pygame_instance.K_RETURN
        S.keys_mapping["backspace"] = S.pygame_instance.K_BACKSPACE
        S.keys_mapping["rshift"] = S.pygame_instance.K_RSHIFT
        S.keys_mapping["lshift"] = S.pygame_instance.K_LSHIFT
        S.keys_mapping["\t"] = S.pygame_instance.K_TAB
        S.keys_mapping["!"] = S.pygame_instance.K_EXCLAIM
        S.keys_mapping["\""] = S.pygame_instance.K_QUOTEDBL
        S.keys_mapping["\'"] = S.pygame_instance.K_QUOTE
        S.keys_mapping["#"] = S.pygame_instance.K_HASH
        S.keys_mapping["$"] = S.pygame_instance.K_DOLLAR
        S.keys_mapping["%"] = S.pygame_instance.K_AMPERSAND
        S.keys_mapping["("] = S.pygame_instance.K_LEFTPAREN
        S.keys_mapping[")"] = S.pygame_instance.K_RIGHTPAREN
        S.keys_mapping["*"] = S.pygame_instance.K_ASTERISK
        S.keys_mapping["+"] = S.pygame_instance.K_PLUS
        S.keys_mapping[","] = S.pygame_instance.K_COMMA
        S.keys_mapping["-"] = S.pygame_instance.K_MINUS
        S.keys_mapping["."] = S.pygame_instance.K_PERIOD
        S.keys_mapping["/"] = S.pygame_instance.K_SLASH
        S.keys_mapping["0"] = S.pygame_instance.K_0
        S.keys_mapping["1"] = S.pygame_instance.K_1
        S.keys_mapping["2"] = S.pygame_instance.K_2
        S.keys_mapping["3"] = S.pygame_instance.K_3
        S.keys_mapping["4"] = S.pygame_instance.K_4
        S.keys_mapping["5"] = S.pygame_instance.K_5
        S.keys_mapping["6"] = S.pygame_instance.K_6
        S.keys_mapping["7"] = S.pygame_instance.K_7
        S.keys_mapping["8"] = S.pygame_instance.K_8
        S.keys_mapping["9"] = S.pygame_instance.K_9
        S.keys_mapping[":"] = S.pygame_instance.K_COLON
        S.keys_mapping[";"] = S.pygame_instance.K_SEMICOLON
        S.keys_mapping["<"] = S.pygame_instance.K_LESS
        S.keys_mapping["="] = S.pygame_instance.K_EQUALS
        S.keys_mapping[">"] = S.pygame_instance.K_GREATER
        S.keys_mapping["?"] = S.pygame_instance.K_QUESTION
        S.keys_mapping["@"] = S.pygame_instance.K_AT
        S.keys_mapping["["] = S.pygame_instance.K_LEFTBRACKET
        S.keys_mapping["\\"] = S.pygame_instance.K_BACKSLASH
        S.keys_mapping["]"] = S.pygame_instance.K_RIGHTBRACKET
        S.keys_mapping["^"] = S.pygame_instance.K_CARET
        S.keys_mapping["_"] = S.pygame_instance.K_UNDERSCORE
        S.keys_mapping["`"] = S.pygame_instance.K_BACKQUOTE

        S.up = "up"
        S.down = "down"
        S.pressed = "pressed"
        S.mapping = OrderedDict()
        keys = S.keys_mapping.keys() 
        for key in keys:
            S.mapping[S.keys_mapping[key]] = [key, S.up]

    def process_button(S, current_state, new_state):
        if current_state == S.up and new_state == S.down:
            return S.down
        elif current_state == S.down and new_state == S.down:
            return S.down
        elif current_state == S.down and new_state == S.up:
            return S.pressed
        elif current_state == S.pressed and new_state == S.up:
            return S.up
        else:
            return S.up

    def prepare_inputs(S):
        S.keys = list(S.mapping.values())

    def get_inputs(S):
        keys = S.pygame_instance.key.get_pressed()
        #keys = {}
        #  for event in S.pygame_instance.event.get():
            #  if event.type == S.pygame_instance.KEYDOWN:
                #  print(event.key, event.unicode)
                #  print()
#
        for control_key in S.mapping:
            if keys[control_key]:
                S.mapping[control_key][1] = S.process_button(
                    S.mapping[control_key][1], S.down
                )
            else:
                S.mapping[control_key][1] = S.process_button(
                    S.mapping[control_key][1], S.up
                )

    def get_keys(S):
        S.get_inputs()
        S.prepare_inputs()
        return S.keys


class ChainedProcessor:
    def __init__(
        S, pygame_instance, display_instance, ui_ref, data_label, data_path, beat_time=1
    ):
        S.W = W
        S.H = H
        S.producer = ChainedsProducer(
            data_label,
            data_path,
            meta_path=META_SCRIPT,
            minor_meta=META_MINOR,
            meta_actions=META_ACTION,
            meta_action_stack=META_ACTION_STACK,
            ui_ref=ui_ref,
        )
        S.chain_alter_notify = False

        S.drawer = ChainedDrawer(pygame_instance, display_instance, W, H)
        S.control_ex = KeyboardRawModel(pygame_instance)
        S.active_line = None
        S.pygame_instance = pygame_instance
        S.display_instance = display_instance
        S.active_beat_time = beat_time
        S.time_elapsed_cummulative = 0
        S.ui_ref = ui_ref
        S.active_entity = ChainedEntity(
            S.producer.produce_next_feature(),
            S.producer.produce_chain(),
            S.producer.chains,
            S.pygame_instance,
            S.W,
            S.H,
        )
        S.ui_ref.constant_variation = S.active_entity.constant_variation
        S.ui_ref.chain_no = int(S.active_entity.features_chain.chain_no)
        S.ui_ref.set_image(S.active_entity.chained_feature.ask_for_image())
        S.ui_ref.randomize()
        S.ui_ref.global_progress = S.producer.chains.get_chains_progression()
        S.ui_ref.tiling = S.active_entity.main_title
        S.ui_ref.co_variate()
        S.ui_ref.show_less = False

    def add_line(S):

        if S.active_entity:
            is_solved = S.active_entity.register_answers()

        S.active_entity = ChainedEntity(
            S.producer.produce_next_feature(),
            S.producer.produce_chain(),
            S.producer.chains,
            S.pygame_instance,
            S.W,
            S.H,
        )

        S.ui_ref.constant_variation = S.active_entity.constant_variation
        S.ui_ref.chain_no = int(S.active_entity.features_chain.chain_no)
        S.ui_ref.set_image(S.active_entity.chained_feature.ask_for_image())
        S.ui_ref.randomize()
        S.ui_ref.global_progress = S.producer.chains.get_chains_progression()
        S.ui_ref.tiling = S.active_entity.main_title
        S.ui_ref.co_variate()
        S.ui_ref.bg_color = colors.col_black
        S.ui_ref.show_less = False
        S.time_elapsed_cummulative = 0
        S.active_beat_time = (60 * 1000) / S.active_entity.time_estemated

        return (
            S.active_entity.time_estemated,
            S.producer.produce_meta(),
            S.producer.produce_meta_minor(),
        )

    def redraw(S):
        S.drawer.draw_line(S.active_entity)

    def get_feedback(S):
        global NEW_EVENT
        if LAST_EVENT == "POSITIVE" and NEW_EVENT:
            S.ui_ref.bg_color = colors.dark_green


            NEW_EVENT = False
            return 1
        elif LAST_EVENT == "ERROR" and NEW_EVENT:
            NEW_EVENT = False
            S.ui_ref.bg_color = colors.dark_red
            return -1
        else:
            return 0

    def get_pressed(S, key_states):
        def mark_pressed(_):
            return True if _ == "pressed" else False

        return [mark_pressed(_) for _ in key_states]

    def reduce_keys(S, key_states):
        active_keys = ["g","f","d","s","a","h","j","k","l",";"]
        reduced = []
        for selector in active_keys:
            key_exists = False
            for key in key_states:
                if key[0]==selector:
                    reduced.append(key[1])
                    key_exists = True
                    break
            if not key_exists:
                reduced.append("up")

        #reduced = list(key_states[_][1] for _ in active_keys)
        return reduced

    def filter_keys(s, key_states):
        return list(_ for _ in key_states if _[1] == "pressed")

    def filter_up_keys(s, key_states):
        return list(_ for _ in key_states if _[1] != "up")

    def process_inputs(S):
        #key_states = S.control.get_keys()
        key_states = S.filter_up_keys(S.control_ex.get_keys())
        reduced = S.reduce_keys(S.filter_keys(key_states))

        if S.active_entity:
            S.drawer.display_keys(reduced, S.active_entity)

        pressed_keys = S.get_pressed(reduced)
        #keys_extended = S.control_ex.get_keys()

        if S.active_entity and any(key_states):
            S.active_entity.register_keys(
                pressed_keys, key_states, S.time_elapsed_cummulative / S.active_beat_time
            )
        elif S.active_entity:
            S.active_entity.register_keys(
                pressed_keys,
                key_states,
                S.time_elapsed_cummulative / S.active_beat_time,
                time_based=True,
            )
            if S.active_entity.done:
                S.ui_ref.set_image(S.active_entity.chained_feature.attached_image)
                S.ui_ref.show_less = True

        pressed_mouse = S.pygame_instance.mouse.get_pressed()
        if S.active_entity and any(pressed_mouse):
            S.active_entity.register_mouse(pressed_mouse)
        elif S.active_entity:
            S.active_entity.register_idle_mouse()

    def is_burning(S):
        return S.producer.is_burning()

    def get_burning_features_list(S):
        return S.producer.get_burning_features_list()

    def is_dropped(S):
        if S.active_entity and S.active_entity.drop:
            return True
        return False

    def tick(S, time_elapsed):

        S.time_elapsed_cummulative += time_elapsed

        S.process_inputs()
        S.redraw()

        feedback = S.get_feedback()

        if S.producer.chain_alter_notify:
            S.producer.chain_alter_notify = False
            S.chain_alter_notify = True

        return feedback
