class UpperLayout():
    def __init__(self, pygame_instance, display_instance, W, H):
        self.W = W
        self.H = H
        self.y1 = 0
        self.y2 = self.H//8
        self.y3 = self.H - self.H//16
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance
        self.backgroudn_color = (130, 130, 130)
        self.speed_index = 0
        font_file = pygame_instance.font.match_font("setofont")
        self.font = pygame_instance.font.Font(font_file, 40)

    def redraw(self):
        self.pygame_instance.draw.rect(self.display_instance,
                                  self.backgroudn_color,
                                  (0,self.y1,self.W,self.y2))

        self.pygame_instance.draw.rect(self.display_instance,
                                  self.backgroudn_color,
                                  (0,self.y3,self.W,self.H))

    def set_speed_index(self, speed_index):
        self.speed_index
