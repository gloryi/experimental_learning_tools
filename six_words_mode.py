from utils import extract_bijection_csv
from learning_model import SemanticUnit
from collections import OrderedDict
from math import sqrt
from itertools import compress
import random

THREE_PAIRS = 4
######################################
### DATA PRODUCER
######################################

class SixtletsProducer():
    def __init__(self, label, csv_path):
        self.csv_path = csv_path
        self.label = label 
        self.semantic_units = self.prepare_data()

    def prepare_data(self):
        return [SemanticUnit(bijection) for bijection in extract_bijection_csv(self.csv_path)]

    def produce_three_pairs(self):
        #selected = random.sample(self.semantic_units, THREE_PAIRS)
        average = sum(_.learning_score for _ in self.semantic_units)/len(self.semantic_units)
        worst_perfomance = list(filter(lambda _ : _.learning_score < average, self.semantic_units))
        best_perfomance = list(filter(lambda _ : _.learning_score >= average, self.semantic_units))

        worst_picks = 0
        best_picks = 0

        if len(worst_perfomance) < 4:
            worst_picks = len(worst_perfomance)
            best_picks = 4 - worst_picks
        else:
            worst_picks = 4
            best_picks = 0

        selected = []

        if worst_picks != 0:
            selected += random.sample(worst_perfomance, worst_picks)
        if best_picks != 0:
            selected += random.sample(best_perfomance, best_picks)


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
    def __init__(self, semantic_units, pygame_instance, W, H, init_y):
        self.W, self.H = W, H
        self.position_y = init_y

        self.x_positions = [self.W//8*(i+1) - self.W//16 for i in range(8)]

        self.semantic_units = semantic_units
        self.pygame_instance = pygame_instance

        self.active = False
        self.correct = False
        self.error = False
        self.triggered = False
        
        self.keys_assotiated = [False for i in range(8)]

        self.feedback = None

    def move_vertically(self, delta_y):
        self.position_y += delta_y

    def produce_geometries(self):
        graphical_objects = []
        for unit, position_x in zip(self.semantic_units, self.x_positions):
            if unit.active:
                color = (255,0,0) 
            else:
                color = (0,0,255)
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
                unit.deactivate()
                unit.register_match()
                break
        self.feedback = 1

    def feedback_negative(self):
        for unit in self.semantic_units:
            if unit.active:
                unit.deactivate()
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
        font_file = pygame_instance.font.match_font("setofont")  # Select and 
        self.font = pygame_instance.font.Font(font_file, 30)

    def draw_static_ui_elements(self, horisontals):
        for i in range(1,8):
            self.pygame_instance.draw.line(self.display_instance,
                                  (10,10,10),
                                  (self.W//8*i,0),
                                  (self.W//8*i,self.H))

        self.pygame_instance.draw.line(self.display_instance,
                                  (20,20,20),
                                  (self.W//8*4-5,0),
                                  (self.W//8*4-5,self.H))
        self.pygame_instance.draw.line(self.display_instance,
                                  (20,20,20),
                                  (self.W//8*4+5,0),
                                  (self.W//8*4+5,self.H))
        for line_y in horisontals:
            self.pygame_instance.draw.line(self.display_instance,
                                  (10,10,10),
                                  (0,line_y),
                                  (self.W,line_y))


    def draw_line(self, line):
        geometries = line.produce_geometries()
        color = (128,128,128)
        if line.active and not line.triggered:
            color = (0,128,128)
        elif line.correct:
            color = (0,200,0)
        elif line.error:
            color = (200,0,0)

        for geometry in geometries:
            text = self.font.render(geometry.text, True, geometry.color, color)
            textRect = text.get_rect()
            textRect.center = (geometry.x, geometry.y)

            self.display_instance.blit(text, textRect)

    def display_keys(self, keys):
        for i, key_state in enumerate(keys):
            color = (255,255,255)
            if key_state == "up":
                if i in [0,2,5,7]:
                    color = (200,170,200)
                else:
                    color = (170,200,200)
            elif key_state == "down":
                if i in [0,2,5,7]:
                    color = (150, 0, 150)
                else:
                    color = (0, 150, 150)
            else:
                color = (0,150,100)
            
            self.pygame_instance.draw.rect(self.display_instance,
                                  color,
                                  (self.W//8*i,0,self.W//8*(i+1),self.H))


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
        self.mapping[self.pygame_instance.K_a] = self.up
        self.mapping[self.pygame_instance.K_s] = self.up
        self.mapping[self.pygame_instance.K_d] = self.up
        self.mapping[self.pygame_instance.K_f] = self.up
        self.mapping[self.pygame_instance.K_j] = self.up
        self.mapping[self.pygame_instance.K_k] = self.up
        self.mapping[self.pygame_instance.K_l] = self.up
        self.mapping[self.pygame_instance.K_SEMICOLON] = self.up

        self.keys = [self.up for _ in range(8)]

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
    def __init__(self, W, H, pygame_instance, display_instance, data_label, data_path):
        self.W = W
        self.H = H
        self.cast_point = 0 - self.H//8
        self.despawn_point = self.H + self.H//8
        self.exit_trigger = self.H - self.H//4
        self.entry_trigger  = self.H - self.H//4 - self.H//8
        self.action_trigger = (self.entry_trigger + self.exit_trigger)//2
        self.producer = SixtletsProducer(data_label, data_path)
        self.drawer = SixtletDrawer(pygame_instance, display_instance, W, H)
        self.control = KeyboardSixModel(pygame_instance)
        self.stack = []
        self.active_line = None
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance

    def add_line(self):
        line_units = self.producer.produce_three_pairs()
        self.stack.append(SemanticsLine(line_units,
                                        self.pygame_instance,
                                        self.W,
                                        self.H,
                                        self.cast_point))

    def update_positions(self, delta_y):
        for line in self.stack:
            line.move_vertically(delta_y)

    def select_active_line(self, key_states):

        if not "down" in key_states and len(self.stack):
            halfway = list(filter(lambda _ : _.position_y > self.H//2, self.stack))
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
        return feedback

    def process_inputs(self):
        key_states = self.control.get_keys()
        self.drawer.display_keys(key_states)
        self.select_active_line(key_states)

        pressed_keys = self.get_pressed(key_states)

        if not self.active_line is None and any(pressed_keys):
            self.active_line.register_keys(pressed_keys)

    def tick(self, delta_y):
        self.update_positions(delta_y)
        self.clean()
        self.process_inputs()
        self.redraw()

        feedback = self.get_feedback()
        return feedback
