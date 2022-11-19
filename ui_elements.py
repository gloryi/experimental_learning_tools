class UpperLayout():
    def __init__(self, pygame_instance, display_instance, W, H):
        self.W = W
        self.H = H
        self.y1 = 0
        self.y2 = self.H//8
        self.y3 = self.H - self.H//16
        self.higher_center = (self.y1 + self.y2)/2
        self.pygame_instance = pygame_instance
        self.display_instance = display_instance
        self.backgroudn_color = (60, 60, 60)
        font_file = pygame_instance.font.match_font("setofont")
        self.font = pygame_instance.font.Font(font_file, 40)

        self.speed_index = 5000
        self.percent = 0.8

    def place_text(self, text, x, y):
        text = self.font.render(text, True, (80,80,80), (150,150,151))
        textRect = text.get_rect()
        textRect.center = (x, y)
        self.display_instance.blit(text, textRect)


    def redraw(self):
        self.pygame_instance.draw.rect(self.display_instance,
                                  self.backgroudn_color,
                                  (0,self.y1,self.W,self.y2))

        self.pygame_instance.draw.rect(self.display_instance,
                                  self.backgroudn_color,
                                  (0,self.y3,self.W,self.H))

        self.place_text(str(self.speed_index), self.W//10, self.higher_center)
        self.place_text(str(int(self.percent*100))+"%", self.W//10*2, self.higher_center)
