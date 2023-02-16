from utils import raw_extracter
from learning_model import ChainedFeature, FeaturesChain, ChainedModel, ChainUnit, ChainUnitType
from collections import OrderedDict
from math import sqrt
from itertools import compress, groupby
import random
import re
from config import W, H, CYRILLIC_FONT, CHINESE_FONT, H_OFFSET, W_OFFSET, META_SCRIPT, META_MINOR, META_ACTION
from config import HAPTIC_CORRECT_CMD, HAPTIC_ERROR_CMD
from config import META_ACTION_STACK
from colors import col_bg_darker, col_wicked_darker
from colors import col_active_darker, col_bg_lighter
from colors import col_wicked_lighter, col_active_lighter
from colors import col_correct, col_error
import colors
import subprocess

from text_morfer import textMorfer

LAST_EVENT = "POSITIVE"
NEW_EVENT = False
morfer = textMorfer()

######################################
### DATA PRODUCER
######################################

class ChainedsProducer():
    def __init__(S, label, csv_path, meta_path = None, meta_action_stack = None,
                 minor_meta = None, meta_actions = None,
                 ui_ref = None):
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

    
    def extract_meta(S, meta_path):
        meta = []
        header = None

        with open(meta_path, "r") as metafile:
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
        for key, group in groupby(list(_ for _ in data_extractor), key = lambda _ : _[0]):
            features = []
            for item in group:
                entity,  *key_features = item[1:]
                features.append(ChainedFeature(entity, key_features))
            chains.append(FeaturesChain(key, features))
        return ChainedModel(chains)

    def produce_chain(S):
        S.active_chain = S.chains.get_active_chain()
        return S.active_chain

    def produce_next_feature(S):
        return S.chains.get_next_feature()

    def is_burning(S):
        return S.chains.is_burning()

    def get_burning_features_list(S):
        return S.chains.get_burning_features_list()


    def produce_meta(S):
        if S.meta_lines:
            minor_idx = random.randint(0, len(S.meta_lines)-5)
            return "*".join(S.meta_lines[minor_idx:minor_idx+4])
        return ""

    def produce_meta_minor(S):
        if S.minor_lines:
            minor_idx = random.randint(0, len(S.minor_lines)-4)
            lines = S.minor_lines[minor_idx:minor_idx+3]

            if any(S.meta_stack.values()):
                ordered_meta = []
                for key, stk in S.meta_stack.items():
                    if stk:
                        ordered_meta.append(key+" "+random.choice(stk))
                    else:
                        ordered_meta.append(key+" " + "---"*5)
                lines = ordered_meta + lines

            elif S.action_lines:
                lines = [random.choice(S.action_lines)] + lines

            return lines
        return ""

######################################
### ENTITIES HANDLER TEXT_AND_POSE
######################################


class ChainedEntity():
    def __init__(S,
                 chained_feature,
                 features_chain,
                 chains,
                 pygame_instance,
                 W,
                 H):

        S.W, S.H = W, H

        S.x_positions = [S.W//7*(i+1) - S.W//14 for i in range(7)]

        S.chained_feature = chained_feature
        S.features_chain = features_chain
        S.chains = chains
        S.main_title = S.chained_feature.get_main_title()
        S.context = sorted(S.chained_feature.get_context(), key = lambda _ : _.order_no)
        S.order_in_work = 0

        S.pygame_instance = pygame_instance

        S.correct = False
        S.error = False

        S.feedback = None
        S.done = True
        S.locked = False
        S.time_perce_reserved = 0.0

        S.options = None
        S.active_question = None
        S.questions_queue = S.extract_questions()
        S.constant_variation = random.randint(0, 10)

        if S.questions_queue:
            S.time_estemated = S.chained_feature.get_timing() / (len(S.questions_queue)+1)
            S.done = False
        else:
            #S.time_estemated = S.chained_feature.get_timing() / (len(S.context)//2 +1)
            S.time_estemated = S.chained_feature.get_timing() / (len(S.context) +1)


    def extract_questions(S):
        questions = list(filter(lambda _ : _.mode == ChainUnitType.mode_question, S.context))
        if questions:
            S.active_question = questions[0]
            S.active_question.mode = ChainUnitType.mode_active_question
            S.generate_options()
        return questions

    def generate_options(S):
        if S.active_question:
            S.options = S.chains.get_options_list(S.active_question)

    def delete_options(S):
        S.options = ["" for _ in range(6)]

    def register_answers(S):
        is_solved = len(S.questions_queue) == 0
        S.chained_feature.register_progress(is_solved = is_solved)
        return is_solved

    def match_correct(S):
        if S.locked:
            return
        global LAST_EVENT
        global NEW_EVENT
        LAST_EVENT = "POSITIVE"
        NEW_EVENT = True
        S.order_in_work += 1
        if S.questions_queue:
            S.questions_queue.pop(0)
            S.active_question.mode = ChainUnitType.mode_open

        if S.questions_queue:
            S.active_question.mode = ChainUnitType.mode_open
            S.active_question = S.questions_queue[0]
            S.generate_options()
        else:
            S.delete_options()
            S.active_question = None
            S.done = True
            S.order_in_work = 0

    def match_error(S):
        global LAST_EVENT
        global NEW_EVENT
        LAST_EVENT = "ERROR"
        NEW_EVENT = True
        S.locked = True
        S.chained_feature.register_error(S.active_question.order_no)
        S.features_chain.update_errors(register_new=True)


    def register_keys(S, key_states, time_percent, time_based = False):
        if S.active_question and not time_based:
            S.time_perce_reserved = time_percent
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
                time_p = (time_p - S.time_perce_reserved)/(1.0 - S.time_perce_reserved)

            #n_pairs = len(S.context)/2
            n_pairs = len(S.context)
            pair_perce = 1/(n_pairs + 1)

            pair_to_show = int(time_p/pair_perce)
            S.order_in_work = pair_to_show


    def produce_geometries(S):
        graphical_objects = []
        set_color = lambda _ : colors.col_active_lighter if _.extra else col_wicked_darker if _.type == ChainUnitType.type_key else colors.feature_text_col if _.type == ChainUnitType.type_feature  else colors.col_correct if _.mode == ChainUnitType.mode_highligted else colors.col_black
        set_bg_color = lambda _ : colors.col_bt_down if _.extra else col_active_darker if _.type == ChainUnitType.type_key else colors.feature_bg
        get_text  = lambda _ : _.text if S.done or _.mode == ChainUnitType.mode_open else "???"
        get_position_x = lambda _ : S.x_positions[_.order_no+1]
        get_y_position = lambda _ : S.H//2 - S.H//4 + S.H//16 if _.position == ChainUnitType.position_subtitle else S.H//2 - S.H//16 if _.position == ChainUnitType.position_keys else S.H//2 + S.H//16
        set_font = lambda _ : ChainUnitType.font_cyrillic if not re.search(u'[\u4e00-\u9fff]', _.text) else ChainUnitType.font_utf
        set_size = lambda _ : 10 if len(_.text)>=15 else 20 if len(_.text)>=10 else 30 if len(_.text)>=5 else 40

        ctx_len = len(S.context)
        ctx_y_origin = H//2 - 150
        ctx_x_origin = W//2

        out_positions = []
        w,h = int(W*0.95), int(H*0.95)
        if ctx_len == 1:
            out_positions.append([w//2,   5*h//6 - h//6])
        if ctx_len == 2:
            out_positions.append([w//6 +w//6,   h//6 + h//6])
            out_positions.append([5*w//6 -w//6 , 5*h//6 - h//6])
        if ctx_len == 3:
            out_positions.append([w//6 + w//6,   h//6 + h//6])
            out_positions.append([w//2,   5*h//6 - h//6])
            out_positions.append([5*w//6 - w//6, h//6 + h//6])
        if ctx_len == 4:
            out_positions.append([w//6 + w//6,   h//6+h//6])
            out_positions.append([w//6 + w//6,   5*h//6 - h//6])
            out_positions.append([5*w//6 -w//6, 5*h//6 - h//6])
            out_positions.append([5*w//6 -w//6, h//6+h//6])
        if ctx_len >= 5:
            out_positions.append([w//6 ,   h//6 + h//12])
            out_positions.append([w//6 ,   5*h//6 - h//12])
            out_positions.append([w//2,   5*h//6 - h//12])
            out_positions.append([5*w//6 , 5*h//6 - h//12])
            out_positions.append([5*w//6 , h//6 + h//12])

        for ctx in S.context:
            order_y_origin = ctx_y_origin
            ctx_x = ctx_x_origin
            ctx_h = 50
            ctx_w = 250
            ctx_order = ctx.order_no
            ctx_type = ctx.type

            order_delta = S.order_in_work - ctx_order

            if order_delta < 0:
                ctx_x -= ctx_w//2
                order_y_origin -= 25
            elif order_delta > 0:
                order_y_origin += 200 + 25
                #if ctx_type == ChainUnitType.type_feature:
                    #ctx_x += 250/2
            elif order_delta == 0:
                ctx_x -= ctx_w//2
                #else:
                    #ctx_x += 250/2

            if ctx_type == ChainUnitType.type_feature:
                ctx_y = order_y_origin + order_delta * 50
                #ctx_x += 250

            else:
                ctx_y = order_y_origin + order_delta * 50
                #ctx_x += 250

            cx, cy = ctx_x + ctx_w/2, ctx_y + ctx_h/2

            if order_delta > 0:

                if S.constant_variation%2:
                    pos_no = ctx.order_no
                    pos_no %= len(out_positions)
                    ctx_x, ctx_y = out_positions[pos_no]
                else:
                    pos_no = ctx_len -1 - ctx.order_no
                    pos_no%=len(out_positions)
                    ctx_x, ctx_y = out_positions[pos_no]
                cx, cy = ctx_x, ctx_y

                ctx_x -= ctx_w/2
                ctx_y -= ctx_h/2

                ctx_x += int(W*0.05/2)
                cx += int(W*0.05/2)
                ctx_y += int(H*0.05/2)
                cy += int(H*0.05/2)

            graphical_objects.append(WordGraphical(get_text(ctx),
                                                   cx,
                                                   cy,
                                                   set_color(ctx),
                                                   set_bg_color(ctx),
                                                   font = set_font(ctx),
                                                   font_size = set_size(ctx),
                                                   rect = [ctx_x, ctx_y, ctx_w, ctx_h]))

        options_x1 = W//2-250
        options_y1 = 325
        options_w = 200
        options_h = 50
        options_x_corners = [W//2-250-options_w//2, W//2-250-options_w//2, W//2-250-options_w//2,
                             W//2+250-options_w//2, W//2+250-options_w//2, W//2+250-options_w//2]
        options_y_corners = [H//2-80-options_h//2, H//2-options_h//2, H//2+80-options_h//2,
                             H//2-80-options_h//2, H//2-options_h//2, H//2+80-options_h//2]
        set_font = lambda _ : ChainUnitType.font_cyrillic if not re.search(u'[\u4e00-\u9fff]', _) else ChainUnitType.font_utf
        #set_size = lambda _ : 30 if not re.search(u'[\u4e00-\u9fff]', _) else 40
        set_size = lambda _ : 15 if len(_)>=15 else 25 if len(_)>=10 else 30 if len(_)>=5 else 40
        if S.options:
            for i, (x1, y1) in enumerate(zip(options_x_corners, options_y_corners)):
                xc, yc = x1 + options_w / 2, y1 + options_h / 2

                graphical_objects.append(WordGraphical(S.options[i],
                                                       xc,
                                                       yc,
                                                       colors.col_bt_text, transparent = True,
                                                       font = set_font(S.options[i]),
                                                       font_size = set_size(S.options[i]),
                                                        rect = [x1, y1, options_w, options_h] if S.options[i] else []))


        large_notion_w = 250
        large_notion_h = 200
        large_notions_x_corners = [W//2]
        large_notions_y_corners = [H//2]
        for i, (x1,y1) in enumerate(zip(large_notions_x_corners, large_notions_y_corners)):
            xc, yc = x1, y1

            tlen = len(S.chained_feature.entity)
            graphical_objects.append(WordGraphical(S.chained_feature.entity,
                                     xc, yc,
                                     colors.col_black,
                                     bg_color = None if i == 0 else col_correct if LAST_EVENT == "POSITIVE" else col_error,
                                    font_size = 120 if tlen == 1 else 90 if tlen == 2 else 60 if tlen == 3 else 40 if tlen < 5 else 30 if tlen < 10 else 20,
                                    font = ChainUnitType.font_utf if re.findall(r'[\u4e00-\u9fff]+', S.chained_feature.entity) else ChainUnitType.font_cyrillic,
                                     rect = [x1-large_notion_w//2, y1-large_notion_h//2, large_notion_w, large_notion_h]))


        return graphical_objects

    def fetch_feedback(S):
        to_return = S.feedback
        S.feedback = None
        return to_return

######################################
### LINES HANDLER GRAPHICS
######################################

class WordGraphical():
    def __init__(S, text, x, y, color, bg_color = (150,150,150),
                 font = ChainUnitType.font_utf,
                 font_size = None,
                 rect = [], transparent = False):
        S.rect = rect
        S.text = text
        S.x = x
        S.y = y
        S.color = color
        S.bg_color = bg_color
        S.font = font
        S.font_size = font_size
        S.transparent = transparent

class ChainedDrawer():
    def __init__(S, pygame_instance, display_instance, W, H):
        S.pygame_instance = pygame_instance
        S.display_instance = display_instance
        S.W = W
        S.H = H
        S.cyrillic_10 = S.pygame_instance.font.Font(CYRILLIC_FONT, 10, bold = True)
        S.cyrillic_15 = S.pygame_instance.font.Font(CYRILLIC_FONT, 15, bold = True)
        S.cyrillic_20 = S.pygame_instance.font.Font(CYRILLIC_FONT, 20, bold = True)
        S.cyrillic_25 = S.pygame_instance.font.Font(CYRILLIC_FONT, 25, bold = True)
        S.cyrillic_30 = S.pygame_instance.font.Font(CYRILLIC_FONT, 30, bold = True)
        S.cyrillic_40 = S.pygame_instance.font.Font(CYRILLIC_FONT, 40, bold = True)
        S.cyrillic_60 = S.pygame_instance.font.Font(CYRILLIC_FONT, 60, bold = True)
        S.cyrillic_120 = S.pygame_instance.font.Font(CYRILLIC_FONT, 120, bold = True)

        S.utf_10 = S.pygame_instance.font.Font(CHINESE_FONT, 10, bold = True)
        S.utf_15 = S.pygame_instance.font.Font(CHINESE_FONT, 15, bold = True)
        S.utf_20 = S.pygame_instance.font.Font(CHINESE_FONT, 20, bold = True)
        S.utf_25 = S.pygame_instance.font.Font(CHINESE_FONT, 25, bold = True)
        S.utf_30 = S.pygame_instance.font.Font(CHINESE_FONT, 30, bold = True)
        S.utf_40 = S.pygame_instance.font.Font(CHINESE_FONT, 40, bold = True)
        S.utf_60 = S.pygame_instance.font.Font(CHINESE_FONT, 60, bold = True)
        S.utf_120 = S.pygame_instance.font.Font(CHINESE_FONT, 120, bold = True)

    def pick_font(S, font_type = ChainUnitType.font_utf, size = 40):
        if font_type == ChainUnitType.font_utf:
            if not size:
                return S.utf_30
            elif size <= 15:
                return S.utf_15
            elif size <= 20:
                return S.utf_20
            elif size <= 25:
                return S.utf_25
            elif size <= 30:
                return S.utf_30
            elif size <= 40:
                return S.utf_40
            elif size <= 60:
                return S.utf_60
            else:
                return S.utf_120
        else:
            if not size:
                return S.cyrillic_30
            elif size <= 15:
                return S.cyrillic_15
            elif size <= 20:
                return S.cyrillic_20
            elif size <= 25:
                return S.cyrillic_25
            elif size <= 30:
                return S.cyrillic_30
            elif size <= 40:
                return S.cyrillic_40
            elif size <= 60:
                return S.cyrillic_60
            else:
                return S.cyrillic_120

    def draw_line(S, line):
        geometries = line.produce_geometries()
        color = (128,128,128)
        S.pygame_instance.draw.rect(S.display_instance,
                              (10,10,10),
                              (W//2 - 1,
                               0,
                               2,
                               H))

        S.pygame_instance.draw.rect(S.display_instance,
                              (10,10,10),
                              (0,
                               H//2 - 1,
                               W,
                               2))

        for geometry in geometries:
            message = geometry.text
            if not re.findall(r'[\u5e00-\u9fff]+', message):
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
                S.pygame_instance.draw.rect(S.display_instance,
                                  (50,50,50),
                                  (x,y,w,h),
                                   width = 2, border_radius = 15)

            S.display_instance.blit(text, textRect)

    def display_keys(S, keys, line):
        if line.done:
            return
        options_x1 = W//2-250
        options_y1 = 325
        options_w = 200
        options_h = 50
        options_x_corners = [W//2-250-options_w//2, W//2-250-options_w//2, W//2-250-options_w//2,
                             W//2+250-options_w//2, W//2+250-options_w//2, W//2+250-options_w//2]
        options_y_corners = [H//2-80-options_h//2, H//2-options_h//2, H//2+80-options_h//2,
                             H//2-80-options_h//2, H//2-options_h//2, H//2+80-options_h//2]

        for i, (x1, y1) in enumerate(zip(options_x_corners, options_y_corners)):
            key_state = keys[i]
            xc, yc = x1 + options_w / 2, y1 + options_h / 2

            color = (255,255,255)
            if key_state == "up":
                color = colors.col_bt_down if LAST_EVENT == "POSITIVE" else colors.col_error
            elif key_state == "down":
                color = colors.col_bt_pressed if LAST_EVENT == "POSITIVE" else colors.col_active_lighter
            else:
                color = (0,150,100)

            S.pygame_instance.draw.rect(S.display_instance,
                                  color,
                                  (x1, y1, options_w, options_h), border_radius=15)



######################################
### SIX MODE CONTROLLER
######################################

class KeyboardChainModel():
    def __init__(S, pygame_instance):
        S.pygame_instance = pygame_instance
        S.up = 'up'
        S.down = 'down'
        S.pressed = 'pressed'
        S.mapping = OrderedDict()
        S.mapping[S.pygame_instance.K_e]         = S.up
        S.mapping[S.pygame_instance.K_d]         = S.up
        S.mapping[S.pygame_instance.K_c]         = S.up
        S.mapping[S.pygame_instance.K_i]         = S.up
        S.mapping[S.pygame_instance.K_k]         = S.up
        S.mapping[S.pygame_instance.K_COMMA]     = S.up

        S.keys = [S.up for _ in range(6)]

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
        for control_key in S.mapping:
            if keys[control_key]:
                S.mapping[control_key] = S.process_button(S.mapping[control_key], S.down)
            else:
                S.mapping[control_key] = S.process_button(S.mapping[control_key], S.up)

    def get_keys(S):
        S.get_inputs()
        S.prepare_inputs()
        return S.keys


class ChainedProcessor():
    def __init__(S, pygame_instance, display_instance, ui_ref, data_label, data_path, beat_time = 1):
        S.W = W
        S.H = H
        S.producer = ChainedsProducer(data_label, data_path, meta_path = META_SCRIPT,
                                      minor_meta = META_MINOR, meta_actions = META_ACTION, meta_action_stack = META_ACTION_STACK,
                                      ui_ref = ui_ref)
        S.drawer = ChainedDrawer(pygame_instance, display_instance, W, H)
        S.control = KeyboardChainModel(pygame_instance)
        S.active_line = None
        S.pygame_instance = pygame_instance
        S.display_instance = display_instance
        S.active_beat_time = beat_time
        S.time_elapsed_cummulative = 0
        S.ui_ref = ui_ref
        S.active_entity = ChainedEntity(S.producer.produce_next_feature(),
                                           S.producer.produce_chain(),
                                           S.producer.chains,
                                           S.pygame_instance, S.W, S.H)
        S.ui_ref.constant_variation = S.active_entity.constant_variation
        S.ui_ref.set_image(S.active_entity.chained_feature.ask_for_image())
        S.ui_ref.randomize()
        S.ui_ref.global_progress = S.producer.chains.get_chains_progression()
        S.ui_ref.tiling = S.active_entity.main_title
        S.ui_ref.show_less = False

    def add_line(S):

        if S.active_entity:
            is_solved = S.active_entity.register_answers()

        S.active_entity = ChainedEntity(S.producer.produce_next_feature(),
                                           S.producer.produce_chain(), S.producer.chains,
                                           S.pygame_instance, S.W, S.H)

        S.ui_ref.constant_variation = S.active_entity.constant_variation
        S.ui_ref.set_image(S.active_entity.chained_feature.ask_for_image())
        S.ui_ref.randomize()
        S.ui_ref.global_progress = S.producer.chains.get_chains_progression()
        S.ui_ref.tiling = S.active_entity.main_title
        S.ui_ref.bg_color = colors.col_black
        S.ui_ref.show_less = False
        S.time_elapsed_cummulative = 0
        S.active_beat_time = (60*1000)/S.active_entity.time_estemated

        return S.active_entity.time_estemated, S.producer.produce_meta(), S.producer.produce_meta_minor()


    def redraw(S):
        S.drawer.draw_line(S.active_entity)

    def get_pressed(S, key_states):
        mark_pressed = lambda _ : True if _ == "pressed" else False
        return [mark_pressed(_) for _ in key_states]

    def get_feedback(S):
        global NEW_EVENT
        if LAST_EVENT == "POSITIVE" and NEW_EVENT:
            S.ui_ref.bg_color = colors.dark_green

            if random.randint(0,10) > 8 and HAPTIC_CORRECT_CMD:
                subprocess.Popen(["bash", HAPTIC_CORRECT_CMD])

            NEW_EVENT = False
            return 1
        elif LAST_EVENT == "ERROR" and NEW_EVENT:
            NEW_EVENT = False
            S.ui_ref.bg_color = colors.dark_red
            if random.randint(0,10) > 8 and HAPTIC_ERROR_CMD:
                subprocess.Popen(["bash", HAPTIC_ERROR_CMD])
            return -1
        else:
            return 0


    def process_inputs(S, time_elapsed = 0):
        key_states = S.control.get_keys()
        if S.active_entity:
            S.drawer.display_keys(key_states, S.active_entity)

        pressed_keys = S.get_pressed(key_states)

        if S.active_entity and any(pressed_keys):
            S.active_entity.register_keys(pressed_keys, S.time_elapsed_cummulative / S.active_beat_time)
        elif S.active_entity:
            S.active_entity.register_keys(pressed_keys,
                                             S.time_elapsed_cummulative / S.active_beat_time,
                                             time_based = True)
            if S.active_entity.done:
                S.ui_ref.set_image(S.active_entity.chained_feature.attached_image)
                S.ui_ref.show_less = True



    def is_burning(S):
        return S.producer.is_burning()

    def get_burning_features_list(S):
        return S.producer.get_burning_features_list()

    def tick(S, beat_time, time_elapsed):

        S.time_elapsed_cummulative += time_elapsed

        S.process_inputs(time_elapsed)
        S.redraw()

        feedback = S.get_feedback()
        return feedback
