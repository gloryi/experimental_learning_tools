from utils import extract_bijection_csv, get_lines_with_context
from learning_model import SemanticUnit
from collections import OrderedDict
from math import sqrt
from itertools import compress
import random
from config import W, H
from colors import col_bg_darker, col_wicked_darker
from colors import col_active_darker, col_bg_lighter
from colors import col_wicked_lighter, col_active_lighter
from colors import col_correct, col_error
from config import TEST_CONTEXT_FILE

THREE_PAIRS = 3
LAST_EVENT = "POSITIVE"
######################################
### DATA PRODUCER
######################################

class SixtletsProducer():
    def __init__(self, label, csv_path, ui_ref = None):
        self.csv_path = csv_path
        self.label = label 
        self.semantic_units = self.prepare_data()
        self.batch = random.sample(self.semantic_units, 20)

        self.ui_ref = ui_ref

    def prepare_data(self):
        context_based_extractor = get_lines_with_context(TEST_CONTEXT_FILE, extract_bijection_csv(self.csv_path))
        #return [SemanticUnit(bijection) for bijection in extract_bijection_csv(self.csv_path)]
        return [SemanticUnit(bijection) for bijection in context_based_extractor]

    def update_progress(self):
        if not self.ui_ref is None:
            target_min_score = 101
            all_units = len(self.batch)
            units_before_score  = len([_ for _ in self.batch if _.learning_score >= target_min_score])

            if units_before_score + 3 >= all_units:
                self.ui_ref.progress_ratio = 0.0
                self.ui_ref.mastered = 0
                self.ui_ref.all_units = all_units
                self.resample()

            ratio = units_before_score / all_units

            self.ui_ref.progress_ratio = ratio
            self.ui_ref.mastered = units_before_score
            self.ui_ref.to_master = all_units

    def resample(self):
        self.semantic_units.sort(key = lambda _ : _.learning_score)
        self.batch = random.sample(self.semantic_units[:len(self.semantic_units)//3], 20)



    def produce_three_pairs(self):
        self.update_progress()
        #selected = random.sample(self.semantic_units, THREE_PAIRS)
        average = sum(_.learning_score for _ in self.batch)/len(self.batch)
        worst_perfomance = list(filter(lambda _ : _.learning_score < average, self.batch))
        best_perfomance = list(filter(lambda _ : _.learning_score >= average, self.batch))

        worst_picks = 0
        best_picks = 0

        if len(worst_perfomance) < 4:
            worst_picks = len(worst_perfomance)
            best_picks = 3 - worst_picks
        else:
            worst_picks = 3
            best_picks = 0

        selected = []

        if worst_picks != 0:
            selected += random.sample(worst_perfomance, worst_picks)
        if best_picks != 0:
            selected += random.sample(best_perfomance, best_picks)

        for unit in selected:
            unit.activated = False

        active = random.choice(selected)
        active.activate()
        three_pairs = []

        for unit in selected:
            three_pairs += unit.produce_pair()
        random.shuffle(three_pairs)

        return three_pairs

######################################
### LINES HANDLER TEXT_AND_POSE
######################################


class SemanticsLine():
    def __init__(self,
                 semantic_units,
                 pygame_instance,
                 W,
                 H,
                 init_y,
                 velocity):

        self.W, self.H = W, H
        self.position_y = init_y

        self.x_positions = [self.W//6*(i+1) - self.W//12 for i in range(6)]

        self.semantic_units = semantic_units
        self.pygame_instance = pygame_instance

        self.active = False
        self.correct = False
        self.error = False
        self.triggered = False
        
        self.keys_assotiated = [False for i in range(6)]

        self.feedback = None
        self.velocity = velocity

    def move_vertically(self, time_elapsed):
        self.position_y += self.velocity * time_elapsed

    def produce_geometries(self):
        graphical_objects = []
        if not self.triggered:
            for unit, position_x in zip(self.semantic_units, self.x_positions):
                if unit.active:
                    color = (255,0,0) 
                else:
                    color = (0,0,255)
                graphical_objects.append(WordGraphical(unit.content,
                                                       position_x,
                                                       self.position_y,
                                                       color))
        else:
            active_unit = None
            for unit in self.semantic_units:
                if unit.active:
                    active_unit = unit
            color = (0,0,255)
            for unit, position_x in zip(self.semantic_units, self.x_positions):
                if unit.key == active_unit.key:
                    graphical_objects.append(WordGraphical(unit.content,
                                                           position_x,
                                                           self.position_y,
                                                           color))
        return graphical_objects

    def activate(self):
        self.active = True

    def deactivate(self):
        self.register_error()

    def register_keys(self, key_codes):
        self.keys_assotiated = [a or b for (a,b) in zip(key_codes, self.keys_assotiated)]
        self.validate_keys()

    def check_answers(self):
        selected_units = list(compress(self.semantic_units, self.keys_assotiated))
        if len(selected_units) != 2:
            return False
        first_unit, second_unit = selected_units
        if not any([first_unit.active, second_unit.active]):
            return False
        if not first_unit.key == second_unit.key:
            return False
        return True

    def register_event(self):
        self.triggered = True
        self.active = False

    def feedback_positive(self):
        for unit in self.semantic_units:
            if unit.active:
                unit.register_match()
                break
        self.feedback = 1

    def feedback_negative(self):
        for unit in self.semantic_units:
            if unit.active:
                unit.register_error()
        self.feedback = -1
        
    def register_error(self):
        self.correct = False
        self.error = True
        self.register_event()
        self.feedback_negative()
        
    def register_correct(self):
        self.correct = True
        self.error = False
        self.register_event()
        self.feedback_positive()

    def validate_keys(self):

        if self.keys_assotiated.count(True) == 2:
            if(self.check_answers()):
                self.register_correct()
            else:
                self.register_error()

        elif self.keys_assotiated.count(True) >= 3:
            self.register_error()

    def fetch_feedback(self):
        to_return = self.feedback
        self.feedback = None
        return to_return


######################################
### LINES HANDLER GRAPHICS
######################################

class WordGraphical():
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color

class SixtletDrawer():
    def __init__(self, pygame_instance, display_instance, W, H):
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance
        self.W = W
        self.H = H
        #self.pygame_instance.font.init()
        #self.font = self.pygame_instance.font.SysFont("malgungothic", 50)
        #self.font = self.pygame_instance.font.SysFont("Ms_Song.ttf", 50)

    def draw_static_ui_elements(self, horisontals):
        for i in range(1,8):
            self.pygame_instance.draw.line(self.display_instance,
                                  (10,10,10),
                                  (self.W//6*i,0),
                                  (self.W//6*i,self.H),
                                           width = 3)

        self.pygame_instance.draw.line(self.display_instance,
                                  (20,20,20),
                                  (self.W//6*3-5,0),
                                  (self.W//6*3-5,self.H),
                                       width=2)
        self.pygame_instance.draw.line(self.display_instance,
                                  (20,20,20),
                                  (self.W//6*3+5,0),
                                  (self.W//6*3+5,self.H),
                                       width=2)
        for line_y in horisontals:
            self.pygame_instance.draw.line(self.display_instance,
                                  (10,10,10),
                                  (0,line_y),
                                  (self.W,line_y),
                                           width=3)


    def draw_line(self, line):
        geometries = line.produce_geometries()
        color = (128,128,128)
        if line.active and  line.triggered:
            color = (0,128,128)
        elif line.correct:
            color = (0,200,0)
        elif line.error:
            color = (200,0,0)

        for geometry in geometries:
            message = geometry.text
            font_size = 60 if len(message) == 1 else 30 if len(message) < 6 else 25
            font_file = self.pygame_instance.font.match_font("setofont")
            self.pygame_instance.font.Font(font_file, font_size)
            self.font = self.pygame_instance.font.Font("simhei.ttf", font_size)
            if len(message) >1:
                text = self.font.render(message, True, geometry.color, color)
            else:
                is_inner_color = False if line.triggered else True
                if is_inner_color:
                    text = self.font.render(message, True, geometry.color)
                else:
                    text = self.font.render(message, True, color)
            textRect = text.get_rect()
            textRect.center = (geometry.x, geometry.y)

            self.display_instance.blit(text, textRect)

    def display_keys(self, keys):
        for i, key_state in enumerate(keys):
            color = (255,255,255)
            if key_state == "up":
                if i in [0,2,3,5]:
                    color = col_bg_darker if LAST_EVENT == "POSITIVE" else col_wicked_darker 
                else:
                    color = col_bg_lighter if LAST_EVENT == "POSITIVE" else col_wicked_lighter
            elif key_state == "down":
                if i in [0,2,3,5]:
                    color = col_active_darker if LAST_EVENT == "POSITIVE" else col_active_darker 
                else:
                    color = col_active_lighter if LAST_EVENT == "POSITIVE" else col_active_lighter
            else:
                color = (0,150,100)
            
            self.pygame_instance.draw.rect(self.display_instance,
                                  color,
                                  (self.W//6*i,0,self.W//6*(i+1),self.H))


######################################
### SIX MODE CONTROLLER
######################################

class KeyboardSixModel():
    def __init__(self, pygame_instance):
        self.pygame_instance = pygame_instance
        self.up = 'up'
        self.down = 'down'
        self.pressed = 'pressed'
        self.mapping = OrderedDict()
        self.mapping[self.pygame_instance.K_s] = self.up
        self.mapping[self.pygame_instance.K_d] = self.up
        self.mapping[self.pygame_instance.K_f] = self.up
        self.mapping[self.pygame_instance.K_j] = self.up
        self.mapping[self.pygame_instance.K_k] = self.up
        self.mapping[self.pygame_instance.K_l] = self.up

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
                

class SixtletsProcessor():
    def __init__(self, pygame_instance, display_instance, ui_ref, data_label, data_path):
        self.W = W
        self.H = H
        self.cast_point = 0 - self.H//8
        self.despawn_point = self.H + self.H//8
        self.exit_trigger = self.H - self.H//4 - self.H//8 - self.H//16 + self.H//8
        self.entry_trigger  = self.H - self.H//4 - self.H//4 + self.H//8
        self.action_trigger = (self.entry_trigger + self.exit_trigger)//2
        self.producer = SixtletsProducer(data_label, data_path, ui_ref)
        self.drawer = SixtletDrawer(pygame_instance, display_instance, W, H)
        self.control = KeyboardSixModel(pygame_instance)
        self.stack = []
        self.active_line = None
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance
        self.active_beat_time = 1

    def add_line(self):
        line_units = self.producer.produce_three_pairs()
        speed_px_ms = (self.action_trigger - self.cast_point)/self.active_beat_time
        self.stack.append(SemanticsLine(line_units,
                                        self.pygame_instance,
                                        self.W,
                                        self.H,
                                        self.cast_point,
                                        speed_px_ms))

    def update_positions(self, time_elapsed):
        for line in self.stack:
            line.move_vertically(time_elapsed)

    def select_active_line(self, key_states):

        if not "down" in key_states and len(self.stack):
            halfway = list(filter(lambda _ : _.position_y > self.entry_trigger, self.stack))
            active = min(list(filter(lambda _ : not _.triggered,
                                halfway)),
                         key = lambda _ : sqrt((self.action_trigger - _.position_y)**2),
                         default = None)

            if not active is None:
                active.activate()
                self.active_line = active

        for passed in filter(lambda _ : _.position_y > self.exit_trigger and not _.triggered,
                             self.stack):
            passed.deactivate()
            if self.active_line == passed:
                self.active_line = None

    def redraw(self):
        for line in self.stack:
            self.drawer.draw_line(line)
        self.drawer.draw_static_ui_elements([self.entry_trigger,
                                             self.exit_trigger,
                                             self.action_trigger])
    
    def clean(self):
        self.stack = list(filter(lambda _ : _.position_y < self.despawn_point,
                                 self.stack))

    def get_pressed(self, key_states):
        mark_pressed = lambda _ : True if _ == "pressed" else False
        return [mark_pressed(_) for _ in key_states]

    def get_feedback(self):
        feedback = sum(_.fetch_feedback() for _ in self.stack if not _.feedback is None)
        global LAST_EVENT
        if feedback > 0:
            LAST_EVENT = "POSITIVE"
        elif feedback <0:
            LAST_EVENT = "NEGATIVE"
        return feedback

    def process_inputs(self):
        key_states = self.control.get_keys()
        self.drawer.display_keys(key_states)
        self.select_active_line(key_states)

        pressed_keys = self.get_pressed(key_states)

        if not self.active_line is None and any(pressed_keys):
            self.active_line.register_keys(pressed_keys)

    def tick(self, beat_time, time_elapsed):

        self.active_beat_time = beat_time

        self.update_positions(time_elapsed)
        self.clean()
        self.process_inputs()
        self.redraw()

        feedback = self.get_feedback()
        return feedback
