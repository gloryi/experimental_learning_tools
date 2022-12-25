from utils import raw_extracter 
from learning_model import ChainedFeature, FeaturesChain, ChainedModel, ChainUnit, ChainUnitType
from collections import OrderedDict
from math import sqrt
from itertools import compress, groupby
import random
import re
from config import W, H, CYRILLIC_FONT, CHINESE_FONT, H_OFFSET, W_OFFSET, META_SCRIPT, META_MINOR
from colors import col_bg_darker, col_wicked_darker
from colors import col_active_darker, col_bg_lighter
from colors import col_wicked_lighter, col_active_lighter
from colors import col_correct, col_error
import colors

LAST_EVENT = "POSITIVE"
NEW_EVENT = False
######################################
### DATA PRODUCER
######################################

class ChainedsProducer():
    def __init__(self, label, csv_path, meta_path = None, minor_meta = None, ui_ref = None):
        self.csv_path = csv_path
        self.label = label 
        self.meta_path = meta_path
        self.minor_meta = minor_meta
        self.meta_lines = self.extract_meta(self.meta_path) if self.meta_path else []
        self.minor_lines = self.extract_meta(self.minor_meta) if self.minor_meta else []
        self.chains = self.prepare_data()
        self.active_chain = self.chains.get_active_chain()
        self.ui_ref = ui_ref

    def extract_meta(self, meta_path):
        meta = []
        with open(meta_path, "r") as metafile:
            for line in metafile:
                meta.append(line[:-1].upper())
        return meta

    def prepare_data(self):
        data_extractor = raw_extracter(self.csv_path) 
        chains = []
        for key, group in groupby(list(_ for _ in data_extractor), key = lambda _ : _[0]):
            features = []
            for item in group:
                entity,  *key_features = item[1:]
                features.append(ChainedFeature(entity, key_features))
            chains.append(FeaturesChain(key, features))
        return ChainedModel(chains)

    def produce_chain(self):
        self.active_chain = self.chains.get_active_chain()
        return self.active_chain

    def produce_next_feature(self):
        return self.chains.get_next_feature()

    def is_burning(self):
        return self.chains.is_burning()

    def get_burning_features_list(self):
        return self.chains.get_burning_features_list()
        

    def produce_meta(self):
        if self.meta_lines:
            return random.choice(self.meta_lines)
        return ""

    def produce_meta_minor(self):
        if self.minor_lines:
            minor_idx = random.randint(0, len(self.minor_lines)-17)
            return self.minor_lines[minor_idx:minor_idx+16] 
        return ""



######################################
### ENTITIES HANDLER TEXT_AND_POSE
######################################


class ChainedEntity():
    def __init__(self,
                 chained_feature,
                 features_chain,
                 chains,
                 pygame_instance,
                 W,
                 H):

        self.W, self.H = W, H

        self.x_positions = [self.W//7*(i+1) - self.W//14 for i in range(7)]

        self.chained_feature = chained_feature
        self.features_chain = features_chain
        self.chains = chains
        self.main_title = self.chained_feature.get_main_title() 
        self.context = sorted(self.chained_feature.get_context(), key = lambda _ : _.order_no)
        self.order_in_work = 0 
        
        self.pygame_instance = pygame_instance

        self.correct = False
        self.error = False
        
        self.feedback = None
        self.done = True
        self.locked = False
        self.time_perce_reserved = 0.0

        self.options = None
        self.active_question = None
        self.questions_queue = self.extract_questions()
        self.constant_variation = random.randint(0, 10)

        if self.questions_queue:
            self.time_estemated = self.chained_feature.get_timing() / (len(self.questions_queue)+1) 
            self.done = False
        else:
            #self.time_estemated = self.chained_feature.get_timing() / (len(self.context)//2 +1) 
            self.time_estemated = self.chained_feature.get_timing() / (len(self.context) +1) 


    def extract_questions(self):
        questions = list(filter(lambda _ : _.mode == ChainUnitType.mode_question, self.context))
        if questions:
            self.active_question = questions[0]
            self.active_question.mode = ChainUnitType.mode_active_question
            self.generate_options()
        return questions

    def generate_options(self):
        if self.active_question:
            self.options = self.chains.get_options_list(self.active_question)

    def delete_options(self):
        self.options = ["" for _ in range(6)]

    def register_answers(self):
        is_solved = len(self.questions_queue) == 0
        self.chained_feature.register_progress(is_solved = is_solved)
        return is_solved 

    def match_correct(self):
        if self.locked:
            return
        global LAST_EVENT
        global NEW_EVENT
        LAST_EVENT = "POSITIVE"
        NEW_EVENT = True
        self.order_in_work += 1
        if self.questions_queue:
            self.questions_queue.pop(0)
            self.active_question.mode = ChainUnitType.mode_open

        if self.questions_queue:
            self.active_question.mode = ChainUnitType.mode_open
            self.active_question = self.questions_queue[0]
            self.generate_options()
        else:
            self.delete_options()
            self.active_question = None
            self.done = True
            self.order_in_work = 0

    def match_error(self):
        global LAST_EVENT
        global NEW_EVENT
        LAST_EVENT = "ERROR"
        NEW_EVENT = True
        self.locked = True
        self.chained_feature.register_error(self.active_question.order_no)
        self.features_chain.update_errors(register_new=True)


    def register_keys(self, key_states, time_percent, time_based = False):
        if self.active_question and not time_based:
            self.time_perce_reserved = time_percent
            for i, key in enumerate(key_states):
                if key:
                    if self.options[i] == self.active_question.text:
                        self.match_correct()
                    else:
                        self.match_error()

        elif time_based and not self.active_question:
            time_p = time_percent

            if not self.done:
                self.time_perce_reserved = time_percent

            if self.done:
                time_p = (time_p - self.time_perce_reserved)/(1.0 - self.time_perce_reserved)

            #n_pairs = len(self.context)/2
            n_pairs = len(self.context)
            pair_perce = 1/(n_pairs + 1)

            pair_to_show = int(time_p/pair_perce)
            self.order_in_work = pair_to_show


    def produce_geometries(self):
        graphical_objects = []
        set_color = lambda _ : colors.col_active_lighter if _.extra else col_wicked_darker if _.type == ChainUnitType.type_key else colors.feature_text_col if _.type == ChainUnitType.type_feature  else colors.col_correct if _.mode == ChainUnitType.mode_highligted else colors.col_black 
        set_bg_color = lambda _ : colors.col_bt_down if _.extra else col_active_darker if _.type == ChainUnitType.type_key else colors.feature_bg 
        get_text  = lambda _ : _.text if self.done or _.mode == ChainUnitType.mode_open else "???"
        get_position_x = lambda _ : self.x_positions[_.order_no+1]  
        get_y_position = lambda _ : self.H//2 - self.H//4 + self.H//16 if _.position == ChainUnitType.position_subtitle else self.H//2 - self.H//16 if _.position == ChainUnitType.position_keys else self.H//2 + self.H//16
        set_font = lambda _ : ChainUnitType.font_cyrillic if not re.search(u'[\u4e00-\u9fff]', _.text) else ChainUnitType.font_utf
        set_size = lambda _ : 10 if len(_.text)>=17 else 20 if len(_.text)>=10 else 30 if len(_.text)>=5 else 40

        ctx_len = len(self.context)
        ctx_y_origin = 275 - 50 
        ctx_x_origin = 500 - 50 

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

        for ctx in self.context:
            order_y_origin = ctx_y_origin
            ctx_x = ctx_x_origin 
            ctx_h = 50
            ctx_w = 250
            ctx_order = ctx.order_no
            ctx_type = ctx.type

            order_delta = self.order_in_work - ctx_order 

            if order_delta < 0:
                ctx_x += 250/2
                order_y_origin -= 25
            elif order_delta > 0:
                order_y_origin += 200 + 25 
                if ctx_type == ChainUnitType.type_feature:
                    ctx_x += 250/2
            else:
                if order_delta == 0:
                    ctx_x += 250/2
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

                if self.constant_variation%2:
                    pos_no = ctx.order_no
                    pos_no %= len(out_positions)
                    ctx_x, ctx_y = out_positions[pos_no]
                else:
                    pos_no = ctx_len -1 - ctx.order_no
                    pos_no%=len(out_positions)
                    ctx_x, ctx_y = out_positions[pos_no]
                cx, cy = ctx_x - W_OFFSET, ctx_y - H_OFFSET 

                ctx_x -= ctx_w/2 + W_OFFSET
                ctx_y -= ctx_h/2 + H_OFFSET

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

        options_x1 = 320
        options_y1 = 325
        options_x_corners = [320+55-5, 320+55-15, 320+55-5, 320+250*2+5+5, 320+250*2+5+15, 320+250*2+5+5]
        options_y_corners = [275, 275+75, 275+150, 275, 275+75, 275+150]
        options_w = 200
        options_h = 50
        set_font = lambda _ : ChainUnitType.font_cyrillic if not re.search(u'[\u4e00-\u9fff]', _) else ChainUnitType.font_utf
        #set_size = lambda _ : 30 if not re.search(u'[\u4e00-\u9fff]', _) else 40
        set_size = lambda _ : 15 if len(_)>=15 else 25 if len(_)>=10 else 30 if len(_)>=5 else 40
        if self.options:
            for i, (x1, y1) in enumerate(zip(options_x_corners, options_y_corners)):
                xc, yc = x1 + options_w / 2, y1 + options_h / 2
 
                graphical_objects.append(WordGraphical(self.options[i],
                                                       xc,
                                                       yc,
                                                       colors.col_bt_text, transparent = True,
                                                       font = set_font(self.options[i]),
                                                       font_size = set_size(self.options[i]),
                                                        rect = [x1, y1, options_w, options_h] if self.options[i] else []))


        large_notions_x_corners = [575]
        large_notions_y_corners = [275]
        large_notion_w = 250
        large_notion_h = 200
        for i, (x1,y1) in enumerate(zip(large_notions_x_corners, large_notions_y_corners)):
            xc, yc = x1 + large_notion_w/2, y1 + large_notion_h/2

            graphical_objects.append(WordGraphical(self.chained_feature.entity,
                                     xc, yc,
                                     colors.col_black,
                                     bg_color = None if i == 0 else col_correct if LAST_EVENT == "POSITIVE" else col_error,
                                    font_size = 120,
                                   font = ChainUnitType.font_utf,
                                     rect = [x1, y1, large_notion_w, large_notion_h]))


        return graphical_objects

    def fetch_feedback(self):
        to_return = self.feedback
        self.feedback = None
        return to_return

######################################
### LINES HANDLER GRAPHICS
######################################

class WordGraphical():
    def __init__(self, text, x, y, color, bg_color = (150,150,150),
                 font = ChainUnitType.font_utf,
                 font_size = None,
                 rect = [], transparent = False):
        self.rect = rect
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.bg_color = bg_color
        self.font = font
        self.font_size = font_size
        self.transparent = transparent

class ChainedDrawer():
    def __init__(self, pygame_instance, display_instance, W, H):
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance
        self.W = W
        self.H = H
        self.cyrillic_10 = self.pygame_instance.font.Font(CYRILLIC_FONT, 10, bold = True)
        self.cyrillic_15 = self.pygame_instance.font.Font(CYRILLIC_FONT, 15, bold = True)
        self.cyrillic_20 = self.pygame_instance.font.Font(CYRILLIC_FONT, 20, bold = True)
        self.cyrillic_25 = self.pygame_instance.font.Font(CYRILLIC_FONT, 25, bold = True)
        self.cyrillic_30 = self.pygame_instance.font.Font(CYRILLIC_FONT, 30, bold = True)
        self.cyrillic_40 = self.pygame_instance.font.Font(CYRILLIC_FONT, 40, bold = True)
        self.cyrillic_60 = self.pygame_instance.font.Font(CYRILLIC_FONT, 60, bold = True)
        self.cyrillic_120 = self.pygame_instance.font.Font(CYRILLIC_FONT, 120, bold = True)

        self.utf_10 = self.pygame_instance.font.Font(CHINESE_FONT, 10, bold = True)
        self.utf_15 = self.pygame_instance.font.Font(CHINESE_FONT, 15, bold = True)
        self.utf_20 = self.pygame_instance.font.Font(CHINESE_FONT, 20, bold = True)
        self.utf_25 = self.pygame_instance.font.Font(CHINESE_FONT, 25, bold = True)
        self.utf_30 = self.pygame_instance.font.Font(CHINESE_FONT, 30, bold = True)
        self.utf_40 = self.pygame_instance.font.Font(CHINESE_FONT, 40, bold = True)
        self.utf_60 = self.pygame_instance.font.Font(CHINESE_FONT, 60, bold = True)
        self.utf_120 = self.pygame_instance.font.Font(CHINESE_FONT, 120, bold = True)

    def pick_font(self, font_type = ChainUnitType.font_utf, size = 40):
        if font_type == ChainUnitType.font_utf:
            if not size:
                return self.utf_30
            elif size <= 15:
                return self.utf_15
            elif size <= 20:
                return self.utf_20
            elif size <= 25:
                return self.utf_25
            elif size <= 30:
                return self.utf_30
            elif size <= 40:
                return self.utf_40
            elif size <= 60:
                return self.utf_60
            else:
                return self.utf_120
        else:
            if not size:
                return self.cyrillic_30 
            elif size <= 15:
                return self.cyrillic_15
            elif size <= 20:
                return self.cyrillic_20
            elif size <= 25:
                return self.cyrillic_25
            elif size <= 30:
                return self.cyrillic_30
            elif size <= 40:
                return self.cyrillic_40
            elif size <= 60:
                return self.cyrillic_60
            else:
                return self.cyrillic_120

    def draw_line(self, line):
        geometries = line.produce_geometries()
        color = (128,128,128)
        for geometry in geometries:
            message = geometry.text
            font = self.pick_font(geometry.font, geometry.font_size)

            if not geometry.transparent:
                text = font.render(message, True, geometry.color, geometry.bg_color)
            else:
                text = font.render(message, True, geometry.color)

            textRect = text.get_rect()
            textRect.center = (geometry.x + W_OFFSET, geometry.y + H_OFFSET)

            if geometry.rect:

                x, y, w, h = geometry.rect 
                self.pygame_instance.draw.rect(self.display_instance,
                                  (50,50,50),
                                  (x+W_OFFSET,y+H_OFFSET,w,h),
                                   width = 2, border_radius = 15)

            self.display_instance.blit(text, textRect)

    def display_keys(self, keys, line):
        if line.done:
            return
        options_x1 = 320
        options_y1 = 325
        options_x_corners = [320+55-5, 320+55-15, 320+55-5, 320+250*2+5+5, 320+250*2+5+15, 320+250*2+5+5]
        options_y_corners = [275, 275+75, 275+150, 275, 275+75, 275+150]
        options_w = 200
        options_h = 50

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

            self.pygame_instance.draw.rect(self.display_instance,
                                  color,
                                  (x1+W_OFFSET, y1+H_OFFSET, options_w, options_h), border_radius=15)
 
            

######################################
### SIX MODE CONTROLLER
######################################

class KeyboardChainModel():
    def __init__(self, pygame_instance):
        self.pygame_instance = pygame_instance
        self.up = 'up'
        self.down = 'down'
        self.pressed = 'pressed'
        self.mapping = OrderedDict()
        self.mapping[self.pygame_instance.K_e]         = self.up
        self.mapping[self.pygame_instance.K_d]         = self.up
        self.mapping[self.pygame_instance.K_c]         = self.up
        self.mapping[self.pygame_instance.K_i]         = self.up
        self.mapping[self.pygame_instance.K_k]         = self.up
        self.mapping[self.pygame_instance.K_COMMA]     = self.up

        self.keys = [self.up for _ in range(6)]

    def process_button(self, current_state, new_state):
        if current_state == self.up and new_state == self.down:
            return self.down
        elif current_state == self.down and new_state == self.down:
            return self.down
        elif current_state == self.down and new_state == self.up:
            return self.pressed
        elif current_state == self.pressed and new_state == self.up:
            return self.up
        else:
            return self.up

    def prepare_inputs(self):
        self.keys = list(self.mapping.values())

    def get_inputs(self):
        keys = self.pygame_instance.key.get_pressed()
        for control_key in self.mapping:
            if keys[control_key]:
                self.mapping[control_key] = self.process_button(self.mapping[control_key], self.down)
            else:
                self.mapping[control_key] = self.process_button(self.mapping[control_key], self.up)
    
    def get_keys(self):
        self.get_inputs()
        self.prepare_inputs()
        return self.keys
                

class ChainedProcessor():
    def __init__(self, pygame_instance, display_instance, ui_ref, data_label, data_path, beat_time = 1):
        self.W = W
        self.H = H
        self.producer = ChainedsProducer(data_label, data_path, meta_path = META_SCRIPT, minor_meta = META_MINOR, ui_ref = ui_ref)
        self.drawer = ChainedDrawer(pygame_instance, display_instance, W, H)
        self.control = KeyboardChainModel(pygame_instance)
        self.active_line = None
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance
        self.active_beat_time = beat_time 
        self.time_elapsed_cummulative = 0
        self.ui_ref = ui_ref
        self.active_entity = ChainedEntity(self.producer.produce_next_feature(),
                                           self.producer.produce_chain(),
                                           self.producer.chains,
                                           self.pygame_instance, self.W, self.H)
        self.ui_ref.constant_variation = self.active_entity.constant_variation
        self.ui_ref.set_image(self.active_entity.chained_feature.ask_for_image())
        self.ui_ref.randomize()
        self.ui_ref.global_progress = self.producer.chains.get_chains_progression()
        self.ui_ref.tiling = self.active_entity.main_title
        self.ui_ref.show_less = False

    def add_line(self):

        if self.active_entity:
            is_solved = self.active_entity.register_answers()
            
        self.active_entity = ChainedEntity(self.producer.produce_next_feature(),
                                           self.producer.produce_chain(), self.producer.chains,
                                           self.pygame_instance, self.W, self.H)

        self.ui_ref.constant_variation = self.active_entity.constant_variation
        self.ui_ref.set_image(self.active_entity.chained_feature.ask_for_image())
        self.ui_ref.randomize()
        self.ui_ref.global_progress = self.producer.chains.get_chains_progression()
        self.ui_ref.tiling = self.active_entity.main_title
        self.ui_ref.bg_color = colors.col_black
        self.ui_ref.show_less = False
        self.time_elapsed_cummulative = 0
        self.active_beat_time = (60*1000)/self.active_entity.time_estemated

        return self.active_entity.time_estemated, self.producer.produce_meta(), self.producer.produce_meta_minor()


    def redraw(self):
        self.drawer.draw_line(self.active_entity)
    
    def get_pressed(self, key_states):
        mark_pressed = lambda _ : True if _ == "pressed" else False
        return [mark_pressed(_) for _ in key_states]

    def get_feedback(self):
        global NEW_EVENT
        if LAST_EVENT == "POSITIVE" and NEW_EVENT:
            self.ui_ref.bg_color = colors.dark_green
            NEW_EVENT = False
            return 1
        elif LAST_EVENT == "ERROR" and NEW_EVENT:
            NEW_EVENT = False
            self.ui_ref.bg_color = colors.dark_red
            return -1
        else:
            return 0


    def process_inputs(self, time_elapsed = 0):
        key_states = self.control.get_keys()
        if self.active_entity:
            self.drawer.display_keys(key_states, self.active_entity)

        pressed_keys = self.get_pressed(key_states)

        if self.active_entity and any(pressed_keys):
            self.active_entity.register_keys(pressed_keys, self.time_elapsed_cummulative / self.active_beat_time)
        elif self.active_entity:
            self.active_entity.register_keys(pressed_keys,
                                             self.time_elapsed_cummulative / self.active_beat_time, 
                                             time_based = True)
            if self.active_entity.done:
                self.ui_ref.set_image(self.active_entity.chained_feature.attached_image)
                self.ui_ref.show_less = True



    def is_burning(self):
        return self.producer.is_burning()

    def get_burning_features_list(self):
        return self.producer.get_burning_features_list()

    def tick(self, beat_time, time_elapsed):

        self.time_elapsed_cummulative += time_elapsed

        self.process_inputs(time_elapsed)
        self.redraw()

        feedback = self.get_feedback()
        return feedback
