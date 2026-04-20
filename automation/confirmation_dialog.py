import tkinter as tk
from tkinter import messagebox

class ConfirmationDialog:
    """
    Handles confirmation popups before executing gestures.
    """
    @staticmethod
    def show(app_name: str, gesture_name: str, message: str = None) -> bool:
        """
        Shows a modal confirmation dialog.
        """
        root = tk.Tk()
        root.withdraw()  # Hide main window
        root.attributes("-topmost", True)
        
        title = f"Gesture Triggered: {gesture_name}"
        msg = message if message else f"Execute actions for '{gesture_name}' in '{app_name}'?"
        
        result = messagebox.askokcancel(title, msg)
        root.destroy()
        return result
