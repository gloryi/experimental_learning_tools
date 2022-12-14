from config import W, H, CHINESE_FONT, W_OFFSET, H_OFFSET
from colors import white
import colors
from itertools import islice
import random
import os

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
        self.bg_color = colors.col_black
        font_file = pygame_instance.font.match_font("setofont")
        self.font = pygame_instance.font.Font(font_file, 50)
        self.large_font = pygame_instance.font.Font(font_file, 80)
        self.utf_font1 = self.pygame_instance.font.Font(CHINESE_FONT, 150, bold = True)
        self.utf_font2 = self.pygame_instance.font.Font(CHINESE_FONT, 100, bold = True)
        self.utf_font3 = self.pygame_instance.font.Font(CHINESE_FONT, 50, bold = True)
        self.combo = 1
        self.tiling = ""
        self.tiling_utf = True
        self.show_less = False

        self.global_progress = ""

        self.speed_index = 5000
        self.percent = 0.8
        self.progress_ratio = 0.0
        self.timing_ratio = 1.0
        self.mastered = 0
        self.to_master = 0
        self.variation = 0
        self.variation_on_rise = True
        self.random_variation = 0
        self.constant_variation = 0

        self.images_cached = {} 
        self.image = None
        self.images_set = None
        self.images_set_cached = None

    def place_text(self, text, x, y, transparent = False, renderer = None, base_col = (80,80,80)):
        if renderer is None:
            renderer = self.font
        if not transparent:
            text = renderer.render(text, True, base_col, (150,150,151))
        else:
            text = renderer.render(text, True, base_col)
        textRect = text.get_rect()
        textRect.center = (x + W_OFFSET, y + H_OFFSET)
        self.display_instance.blit(text, textRect)

    def check_cached_image(self, path_to_image):
        if len(self.images_cached) > 100:
            self.images_cached = dict(islice(self.images_cached.items(), 50))

        if not path_to_image or not os.path.exists(path_to_image):
            self.images_cached[path_to_image] = None
            return

        if path_to_image in self.images_cached:
            return

        image_converted = self.pygame_instance.image.load(path_to_image).convert()
        image_converted.set_alpha(200)
        image_scaled = self.pygame_instance.transform.scale(image_converted, (int(W*0.95), int(H*0.95)))
        self.images_cached[path_to_image]  = image_scaled

    def set_image(self, path_to_image):

        if isinstance(path_to_image, list):
            if path_to_image == self.images_set_cached:
                return
            self.images_set = []
            self.images_set_cached = []
            self.image = None
            for image_name in path_to_image:
                self.check_cached_image(image_name)
                if image_name in self.images_cached and self.images_cached[image_name]:
                    self.images_set.append(self.pygame_instance.transform.scale(self.images_cached[image_name], (int((W*0.95)/3), int(H*0.95)/2)))
                else:
                    self.images_set.append(None)
            return

        else:
            self.images_set = None

        if not path_to_image in self.images_cached:
            self.check_cached_image(path_to_image)

        self.image = self.images_cached[path_to_image]


    def randomize(self):
        self.random_variation = random.choice([-1,0,1])


    def redraw(self):
        clip_color = lambda _ : 0 if _ <=0 else 255 if _ >=255 else int(_)
        tiling_len = len(self.tiling)
        tiling_font = self.utf_font1 if tiling_len==1 else self.utf_font2 if tiling_len <= 3 else self.utf_font3

        self.display_instance.fill(self.bg_color)
        tiling_step = 270 


        if self.images_set:
            set_locations = []
            set_locations.append((int(W*(0.05/2)), int(H*(0.05/6)))) # 0
            set_locations.append((int(W*(0.05/2) + (W*0.95/3)*(0)), int(H*(0.05/2)+H*0.95/2))) # 1
            set_locations.append((int(W*(0.05/2) + (W*0.95/3)*(1)), int(H*(0.05/2)+H*0.95/2))) # 2
            set_locations.append((int(W*(0.05/2) + (W*0.95/3)*(2)), int(H*(0.05/2)+H*0.95/2))) # 3
            set_locations.append((int(W*(0.05/2) + (W*0.95/3)*(2)), int(H*(0.05/6)))) # 5
            if self.constant_variation%2 == 0:
                set_locations = set_locations[::-1]
            for i in range(5):
                if i < len(self.images_set) and self.images_set[i]:
                    self.display_instance.blit(self.images_set[i], set_locations[i])

        elif self.image:
            self.display_instance.blit(self.image,
                                       (int(W*(0.05/2))+self.random_variation,
                                        int(H*(0.05/2))+self.random_variation))
            tiling_step = 400

        elif not self.images_set and not self.image:
            self.pygame_instance.draw.rect(self.display_instance,
                                  white,
                                  (W_OFFSET,
                                   H_OFFSET,
                                   W-W_OFFSET*2,
                                   H-H_OFFSET*2))


        if self.variation_on_rise:
            self.variation += 1
        else:
            self.variation -= 1

        if self.variation > 10:
            self.variation_on_rise = False
        elif self.variation < 0:
            self.variation_on_rise = True

        for x in range(100+self.random_variation,W,tiling_step):
            for y in range(100+self.random_variation,H,tiling_step):
                self.place_text(self.tiling,
                                x-W_OFFSET,
                                y-H_OFFSET,
                                transparent=True,
                                renderer = tiling_font,
                                base_col = (clip_color(225+self.variation*4+self.random_variation),
                                            225-self.variation+self.random_variation,
                                            225+self.random_variation))

        line_color = (int(255*(1-self.percent)),int(255*(self.percent)),0)

        self.place_text(str(self.combo)+"x", 420 - 100,
                        60,
                        transparent = True,
                        renderer = self.large_font,
                        base_col = (50,50,50))

        self.place_text(str(self.global_progress), 420 - 300,
                        40,
                        transparent = True,
                        renderer = self.font,
                        base_col = (50,50,50))

        self.place_text(str(self.combo)+"x", 920 + 100,
                        60,
                        transparent = True,
                        renderer = self.large_font,
                        base_col = (50,50,50))

        self.place_text(str(self.global_progress), 920 + 300,
                        40,
                        transparent = True,
                        renderer = self.font,
                        base_col = (50,50,50))

        

        line_color = (clip_color((178)*(1-self.timing_ratio)+self.random_variation),
                      clip_color((150)*(self.timing_ratio)+self.random_variation),
                      clip_color((150)*(1-self.timing_ratio)+self.random_variation))

        if self.random_variation == 0 or self.random_variation == -1:
            self.pygame_instance.draw.rect(self.display_instance,
                                  line_color,
                                  ((575+25 - 200 + ((200+400)*(1-self.timing_ratio))/2)+W_OFFSET,
                                   275+25+25+H_OFFSET,
                                   (200+400)*self.timing_ratio,
                                   200-50-50))

        if self.random_variation == 0 or self.random_variation == 1:
            self.pygame_instance.draw.rect(self.display_instance,
                                  line_color,
                                  (575+50+25+W_OFFSET,
                                   (275-200 + ((200+400)*(1-self.timing_ratio))/2)+H_OFFSET,
                                   200-50-50,
                                   (200+400)*self.timing_ratio))
        if self.show_less:
            return

        line_color = (int((235)*(1-self.percent)),int((235)*(self.percent)),0)
        self.pygame_instance.draw.rect(self.display_instance,
                                  line_color,
                                  ((320 + (250*3*(1-self.percent))/2)+W_OFFSET,
                                   475+H_OFFSET,
                                   250*3*self.percent,
                                   25))

        self.pygame_instance.draw.rect(self.display_instance,
                                  line_color,
                                  ((320 + (250*3*(1-self.percent))/2)+W_OFFSET,
                                   200+H_OFFSET,
                                   250*3*self.percent,
                                   25))
