from collections import deque
import time

class Clock:
    def __init__(self, max_entries = 10):
        """
        Custom clock object for timing microsecond processes that can calculate the FPS from the average time between ticks
        (literally a copy of pygame.time.Clock but with time.perf_counter)
        
        args:
        (int) max_entries: the maximum number of entries to store in the clock to be used when averaging
        """
        self.max_entries = max_entries
        self.times = deque(maxlen = max_entries)
        self.last_time = time.perf_counter()
        self.fps = 0
        self.dt = 0

    def tick(self):
        """
        Tick the clock once, and calculate the average time between ticks to calculate the FPS
        """
        current_time = time.perf_counter()
        self.dt = current_time - self.last_time
        self.last_time = current_time
        self.times.append(self.dt)
        
        if len(self.times) > 1:
            average_time = sum(self.times) / len(self.times)
            self.fps = 1 / average_time
        else:
            self.fps = 0  
    
    def get_fps(self):
        """
        Return the FPS of the clock
        """
        return self.fps    
    
    def get_time(self):
        return time.perf_counter()
    
    def get_dt(self):
        """
        Return the delta time of the clock
        """
        return self.dt