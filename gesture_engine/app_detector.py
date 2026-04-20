import os
import sys
import win32gui
import win32process
import psutil

# Ensure root directory is in path for utils/config imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import logger

class AppDetector:
    def get_active_app_name(self):
        """Returns the lowercase executable name of the foreground window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "unknown"
                
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            exe_name = process.name().lower()
            return exe_name
        except Exception as e:
            logger.error(f"Error detecting active app: {e}")
            return "unknown"
