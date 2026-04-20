import os
import sys
import threading
import time
from pynput import mouse, keyboard
from config import settings

# Ensure root directory is in path for utils/config imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import logger

class GestureListener:
    def __init__(self, trigger_key, on_gesture_complete, cooldown_seconds=0):
        self.trigger_key = trigger_key
        self.on_gesture_complete = on_gesture_complete
        
        self.is_recording = False
        self.current_points = []
        self.trigger_pressed = False
        self.last_move_time = 0
        self.pause_threshold = getattr(settings, 'SEGMENTATION_PAUSE_MS', 250) / 1000.0
        
        self.mouse_listener = None
        self.key_listener = None
        self._segment_timer = None

    def start(self):
        self.mouse_listener = mouse.Listener(on_move=self.on_move)
        self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        
        self.mouse_listener.start()
        self.key_listener.start()
        logger.info(f"Listeners started. Hold '{self.trigger_key}' to record gestures.")

    def stop(self):
        if self.mouse_listener: self.mouse_listener.stop()
        if self.key_listener: self.key_listener.stop()
        if self._segment_timer: self._segment_timer.cancel()
        logger.info("Listeners stopped.")

    def on_press(self, key):
        try:
            # Handle both special keys and character keys
            k = key.name if hasattr(key, 'name') else key.char
            if k == self.trigger_key:
                if not self.trigger_pressed:
                    self.trigger_pressed = True
                    self.is_recording = True
                    self.current_points = []
                    self.last_move_time = time.time()
                    logger.info("Recording started...")
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            k = key.name if hasattr(key, 'name') else key.char
            if k == self.trigger_key:
                self.trigger_pressed = False
                if self.is_recording:
                    self._finalize_segment()
        except AttributeError:
            pass

    def on_move(self, x, y):
        if self.is_recording:
            self.current_points.append((x, y))
            self.last_move_time = time.time()
            
            # Reset segmentation timer
            if self._segment_timer:
                self._segment_timer.cancel()
            
            self._segment_timer = threading.Timer(self.pause_threshold, self._finalize_segment)
            self._segment_timer.start()

    def _finalize_segment(self):
        """Finalizes the current gesture segment and processes it."""
        if not self.is_recording:
            return
            
        points = self.current_points.copy()
        
        # If the key is still pressed, we start a new segment
        if self.trigger_pressed:
            self.current_points = []
            # We don't set is_recording to False here
        else:
            self.is_recording = False
            self.current_points = []
            
        if len(points) >= 5:
            logger.info(f"Segment captured. Points: {len(points)}")
            # Call the callback in a separate thread to avoid blocking the listener
            threading.Thread(
                target=self.on_gesture_complete, 
                args=(points,), 
                daemon=True
            ).start()
