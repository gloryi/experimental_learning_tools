from config import W, H

class UpperLayout():
    def __init__(self, pygame_instance, display_instance):
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
        self.font = pygame_instance.font.Font(font_file, 50)
        self.large_font = pygame_instance.font.Font(font_file, 80)
        self.combo = 1

        self.speed_index = 5000
        self.percent = 0.8
        self.progress_ratio = 0.0
        self.timing_ratio = 1.0
        self.mastered = 0
        self.to_master = 0

    def place_text(self, text, x, y, transparent = False, renderer = None, base_col = (80,80,80)):
        if renderer is None:
            renderer = self.font
        if not transparent:
            text = renderer.render(text, True, base_col, (150,150,151))
        else:
            text = renderer.render(text, True, base_col)
        textRect = text.get_rect()
        textRect.center = (x, y)
        self.display_instance.blit(text, textRect)


    def redraw(self):
        line_color = (int(255*(1-self.percent)),int(255*(self.percent)),0)
        self.pygame_instance.draw.rect(self.display_instance,
                                  line_color,
                                  ((320 + (250*3*(1-self.percent))/2),
                                   475,
                                   250*3*self.percent,
                                   25))

        self.place_text(str(self.combo)+"x", 420,
                        40,
                        transparent = True,
                        renderer = self.large_font,
                        base_col = (10,10,10))

        self.place_text(str(self.combo)+"x", 920,
                        40,
                        transparent = True,
                        renderer = self.large_font,
                        base_col = (10,10,10))

        #line_color = (int(255*(1-self.progress_ratio)),int(255*(self.progress_ratio)),0)
        #self.pygame_instance.draw.rect(self.display_instance,
                                  #line_color,
                                  #(0,
                                   #self.y1,
                                   #self.W*self.progress_ratio,
                                   #self.y2))
        
        clip_color = lambda _ : 0 if _ <=0 else 255 if _ >=255 else int(_)
        line_color = (clip_color(255*(1-self.timing_ratio)),clip_color(255*(self.timing_ratio)),0)
        self.pygame_instance.draw.rect(self.display_instance,
                                  line_color,
                                  ((570+25 + ((250-50)*(1-self.timing_ratio))/2),
                                   375,
                                   (250-50)*self.timing_ratio,
                                   50))

        #self.place_text(str(self.mastered)+"/"+str(self.to_master), self.W/2, (self.y1 + self.y2)/2)
        #self.place_text(str(self.speed_index)+"x", self.W - self.W//10, self.higher_center)
