from utils import extract_bijection_csv
from learning_model import SemanticUnit
import random

THREE_PAIRS = 3
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
        selected = random.sample(self.semantic_units, THREE_PAIRS)
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

        self.x_positions = [self.W//6*(i+1) - self.W//12 for i in range(6)]

        self.semantic_units = semantic_units
        self.pygame_instance = pygame_instance

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
        self.font = pygame_instance.font.Font('freesansbold.ttf', 32)

    def draw_line(self, line):
        geometries = line.produce_geometries()

        for geometry in geometries:
            text = self.font.render(geometry.text, True, geometry.color, (128,128,100))
            textRect = text.get_rect()
            textRect.center = (geometry.x, geometry.y)

            self.display_instance.blit(text, textRect)

######################################
### SIX MODE CONTROLLER
######################################



class SixtletsProcessor():
    def __init__(self, W, H, pygame_instance, display_instance, data_label, data_path):
        self.W = W
        self.H = H
        self.cast_point = 0 - self.H//8
        self.despawn_point = self.H + self.H//8
        self.producer = SixtletsProducer(data_label, data_path)
        self.drawer = SixtletDrawer(pygame_instance, display_instance, W, H)
        self.stack = []
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

    def redraw(self):
        for line in self.stack:
            self.drawer.draw_line(line)
    
    def clean(self):
        self.stack = list(filter(lambda _ : _.position_y < self.despawn_point,
                                 self.stack))

    def tick(self, delta_y):
        self.update_positions(delta_y)
        self.clean()
        self.redraw()

