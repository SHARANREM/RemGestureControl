import time
import subprocess
import webbrowser
import threading
import numpy as np
from typing import Any, Dict, List
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController
from automation.safe_python_executor import SafePythonExecutor
from utils.logger import logger
from config import settings

class ActionExecutor:
    """
    Responsible for executing various types of actions with non-blocking logic.
    """
    def __init__(self, keyboard: KeyboardController, mouse: MouseController):
        self.keyboard = keyboard
        self.mouse = mouse
        self.python_executor = SafePythonExecutor(keyboard, mouse)
        self._mouse_lock = threading.Lock()
        
        # Modifier persistence state
        self._held_modifiers = {} # key -> release_time
        self._modifier_lock = threading.Lock()
        self._persistence_duration = getattr(settings, 'MODIFIER_PERSISTENCE_MS', 500) / 1000.0
        
        # Start modifier release thread
        threading.Thread(target=self._modifier_releaser, daemon=True).start()

    def _modifier_releaser(self):
        """Background thread to release modifiers after timeout."""
        while True:
            now = time.time()
            with self._modifier_lock:
                to_release = [m for m, t in self._held_modifiers.items() if now >= t]
                for m in to_release:
                    logger.debug(f"Releasing persistent modifier: {m}")
                    self.keyboard.release(m)
                    del self._held_modifiers[m]
            time.sleep(0.05)

    def execute_actions(self, actions: List[Dict[str, Any]]) -> None:
        """Executes a list of actions sequentially in a non-blocking manner."""
        for action in actions:
            action_type = action.get("type")
            try:
                logger.info(f"Executing action type: {action_type}")
                self.dispatch(action)
            except Exception as e:
                logger.error(f"Failed to execute action {action_type}: {e}")

    def dispatch(self, action: Dict[str, Any]) -> None:
        """Dispatches the action to the appropriate handler."""
        action_type = action.get("type")
        
        handlers = {
            "hotkey": self.execute_hotkey,
            "keypress": self.execute_keypress,
            "mouse_scroll": self.execute_scroll,
            "mouse_move": self.execute_mouse_move,
            "open_app": self.execute_open_app,
            "open_url": self.execute_open_url,
            "run_command": self.execute_run_command,
            "custom_python": self.execute_custom_python
        }
        
        handler = handlers.get(action_type)
        if handler:
            handler(action)
        else:
            logger.warning(f"Unknown action type: {action_type}")

    def _get_key(self, key_str: str) -> Any:
        """Converts string key name to pynput Key object if necessary."""
        if hasattr(Key, key_str):
            return getattr(Key, key_str)
        return key_str

    def execute_hotkey(self, action: Dict[str, Any]) -> None:
        """Executes hotkey sequences with proper modifier handling and persistence."""
        sequence = action.get("sequence", [])
        repeats = action.get("repeats", 1)
        repeat_delay = action.get("repeat_delay", 0.05)
        step_delay = action.get("interval_between_steps", 0.05)
        
        modifiers = {Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.alt, Key.alt_l, Key.alt_r, Key.shift, Key.shift_l, Key.shift_r, Key.cmd, Key.cmd_l, Key.cmd_r}

        for _ in range(repeats):
            for step in sequence:
                keys = [self._get_key(k) for k in step] if isinstance(step, list) else [self._get_key(step)]
                
                # Separate modifiers and normal keys
                step_mods = [k for k in keys if k in modifiers]
                step_keys = [k for k in keys if k not in modifiers]
                
                # Press modifiers and update persistence
                with self._modifier_lock:
                    for m in step_mods:
                        if m not in self._held_modifiers:
                            self.keyboard.press(m)
                        self._held_modifiers[m] = time.time() + self._persistence_duration
                
                # Small delay for system to register
                time.sleep(0.01)
                
                # Press and release normal keys
                for k in step_keys:
                    self.keyboard.press(k)
                    time.sleep(0.01)
                    self.keyboard.release(k)
                
                if step_delay > 0:
                    time.sleep(step_delay)
            if repeat_delay > 0:
                time.sleep(repeat_delay)

    def execute_keypress(self, action: Dict[str, Any]) -> None:
        """Presses a key N times."""
        key_str = action.get("key")
        repeats = action.get("repeats", 1)
        interval = action.get("interval", 0.05)
        
        key = self._get_key(key_str)
        for _ in range(repeats):
            self.keyboard.press(key)
            self.keyboard.release(key)
            if interval > 0:
                time.sleep(interval)

    def execute_scroll(self, action: Dict[str, Any]) -> None:
        """Scrolls the mouse."""
        amount = action.get("amount", 1)
        repeats = action.get("repeats", 1)
        for _ in range(repeats):
            self.mouse.scroll(0, amount)

    def execute_mouse_move(self, action: Dict[str, Any]) -> None:
        """Smoothly moves the mouse to a relative or absolute position."""
        dx = action.get("dx", 0)
        dy = action.get("dy", 0)
        absolute = action.get("absolute", False)
        
        threading.Thread(target=self._smooth_move, args=(dx, dy, absolute), daemon=True).start()

    def _smooth_move(self, target_x, target_y, absolute=False):
        """Interpolated mouse movement using linear interpolation."""
        with self._mouse_lock:
            current_x, current_y = self.mouse.position
            
            if not absolute:
                target_x += current_x
                target_y += current_y
                
            steps = settings.MOUSE_SMOOTHNESS
            speed = settings.MOUSE_SPEED
            
            # Linear interpolation for smooth path
            path_x = np.linspace(current_x, target_x, steps)
            path_y = np.linspace(current_y, target_y, steps)
            
            for x, y in zip(path_x, path_y):
                self.mouse.position = (int(x), int(y))
                time.sleep(0.01 / speed)

    def execute_open_app(self, action: Dict[str, Any]) -> None:
        """Launches an executable."""
        path = action.get("path")
        if path:
            subprocess.Popen(path, shell=True)

    def execute_open_url(self, action: Dict[str, Any]) -> None:
        """Opens a URL in the default browser."""
        url = action.get("url")
        if url:
            webbrowser.open(url)

    def execute_run_command(self, action: Dict[str, Any]) -> None:
        """Executes a shell command."""
        command = action.get("command")
        if command:
            subprocess.run(command, shell=True, check=False)

    def execute_custom_python(self, action: Dict[str, Any]) -> None:
        """Executes custom Python code."""
        code = action.get("code", "")
        self.python_executor.execute(code)
