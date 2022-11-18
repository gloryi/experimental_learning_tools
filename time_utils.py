
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

def global_timer(pygame_instance):
    last_frame_timestamp = 0
    current_frame_timestamp = pygame_instance.time.get_ticks()
    frame_timedelta = 0
    while True:
        current_frame_timestamp = pygame_instance.time.get_ticks()
        frame_timedelta = (current_frame_timestamp - last_frame_timestamp)
        last_frame_timestamp = current_frame_timestamp
        yield frame_timedelta
