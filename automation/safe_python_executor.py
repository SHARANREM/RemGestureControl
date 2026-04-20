import time
import subprocess
from typing import Any, Dict
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
from utils.logger import logger

class SafePythonExecutor:
    """
    Executes user-provided Python code in a restricted scope for safety.
    """
    def __init__(self, keyboard: KeyboardController, mouse: MouseController):
        self.keyboard = keyboard
        self.mouse = mouse

    def execute(self, code: str) -> None:
        """
        Executes code with a restricted set of globals.
        """
        if not code:
            return

        # Restricted scope
        local_scope = {
            "keyboard": self.keyboard,
            "mouse": self.mouse,
            "time": time,
            "subprocess": subprocess,
            "Key": Key,
            "Button": Button,
            "logger": logger
        }
        
        # Block dangerous builtins
        safe_builtins = {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "str": str,
            "list": list,
            "dict": dict,
            "set": set,
            "bool": bool,
            "float": float,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "enumerate": enumerate,
            "zip": zip,
            "Exception": Exception,
            "TypeError": TypeError,
            "ValueError": ValueError,
            "RuntimeError": RuntimeError
        }

        try:
            # We use a copy of builtins to prevent modification of the real ones
            exec(code, {"__builtins__": safe_builtins}, local_scope)
            logger.info("Custom Python code executed successfully.")
        except Exception as e:
            logger.error(f"Error in custom Python action: {e}")
