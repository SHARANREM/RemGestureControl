import time

class Cooldown:
    def __init__(self, seconds):
        self.seconds = seconds
        self.last_time = 0
        
    def is_ready(self):
        current_time = time.time()
        if current_time - self.last_time >= self.seconds:
            return True
        return False
        
    def reset(self):
        self.last_time = time.time()
