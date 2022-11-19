
class Counter():
    def __init__(self, drop_time):
        self.drop_time = drop_time
        self.time_elapsed = 0

    def is_tick(self, time_delta):
        self.time_elapsed += time_delta
        if self.time_elapsed >= self.drop_time:
            self.time_elapsed = 0
            return True
        else:
            return False

    def update_drop(self, new_drop):
        self.drop_time = new_drop

def global_timer(pygame_instance):
    last_frame_timestamp = 0
    current_frame_timestamp = pygame_instance.time.get_ticks()
    frame_timedelta = 0
    while True:
        current_frame_timestamp = pygame_instance.time.get_ticks()
        frame_timedelta = (current_frame_timestamp - last_frame_timestamp)
        last_frame_timestamp = current_frame_timestamp
        yield frame_timedelta

class Progression():
    def __init__(self,
                 value_constraint,
                 time_to_see,
                 time_to_update,
                 update_counter):

        self.correct = 24
        self.missed  = 6
        self.offset  = 30 
        self.amortization_margin = 1
        self.amortization = 0
        self.is_amortization =  False
        self.new_event = False

        self.value_constraint = value_constraint
        self.time_to_see = time_to_see
        self.time_to_update = time_to_update
        self.update_counter = update_counter

        self.speed = value_constraint / time_to_see

    def get_percent(self):
        return self.correct / (self.correct + self.missed)

    def register_correct(self):
        self.correct += 1
        self.new_event = True

    def register_miss(self):
        self.missed += 1
        self.new_event = True

    def register_event(self, value):
        if value > 0:
            self.register_correct()
        elif value < 0:
            self.register_miss()


    def set_amortization(self):
        self.amortization = self.amortization_margin
        self.is_amortization = True

    def cehck_amortization(self):
        if self.is_amortization and self.amortization <= 0:
            self.amortization = 0
            self.is_amortization = False
            return False

        if self.is_amortization:
            self.amortization -= 1
            return True
        else:
            return False

    def is_more_intense_required(self):

        if self.get_percent() > 0.95:
            self.set_amortization()
            return True

        return False

    def is_less_intense_required(self):

        if self.get_percent() < 0.75:
            self.set_amortization()
            return True

        return False

    def synchronize_speed(self):
        if self.new_event:
            self.new_event = False

            if not self.cehck_amortization():
                if self.is_more_intense_required():
                    self.time_to_see -= 250 
                    self.time_to_update -= 250 

                elif self.is_less_intense_required():
                    self.time_to_see += 250
                    self.time_to_update += 250

                self.speed = self.value_constraint / self.time_to_see    
                self.update_counter.update_drop(self.time_to_update)
        return self.speed

