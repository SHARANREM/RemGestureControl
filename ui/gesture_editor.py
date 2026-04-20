import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, Callable

class GestureEditor(tk.Toplevel):
    """
    Window for adding or editing a gesture rule.
    """
    def __init__(self, parent, repository, app_id: Optional[int], gesture_data: Optional[Dict[str, Any]] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.repository = repository
        self.app_id = app_id
        self.gesture_data = gesture_data
        self.on_save = on_save
        
        self.title("Edit Gesture" if gesture_data else "Add Gesture")
        self.geometry("400x350")
        self.resizable(False, False)
        self.grab_set() # Modal
        
        self._setup_ui()

    def _setup_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Gesture Name
        ttk.Label(frame, text="Gesture Name:").pack(anchor="w", pady=(0, 5))
        self.name_entry = ttk.Entry(frame)
        self.name_entry.pack(fill="x", pady=(0, 15))
        if self.gesture_data:
            self.name_entry.insert(0, self.gesture_data['gesture_name'])

        # Enabled
        self.enabled_var = tk.BooleanVar(value=bool(self.gesture_data['enabled']) if self.gesture_data else True)
        ttk.Checkbutton(frame, text="Enabled", variable=self.enabled_var).pack(anchor="w", pady=(0, 10))

        # Confirm
        self.confirm_var = tk.BooleanVar(value=bool(self.gesture_data['confirm']) if self.gesture_data else False)
        ttk.Checkbutton(frame, text="Confirm before execution", variable=self.confirm_var).pack(anchor="w", pady=(0, 5))

        # Confirmation Message
        ttk.Label(frame, text="Confirmation Message:").pack(anchor="w", pady=(0, 5))
        self.message_entry = ttk.Entry(frame)
        self.message_entry.pack(fill="x", pady=(0, 20))
        if self.gesture_data:
            self.message_entry.insert(0, self.gesture_data['confirmation_message'] or "")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Gesture name cannot be empty.")
            return

        enabled = self.enabled_var.get()
        confirm = self.confirm_var.get()
        message = self.message_entry.get().strip()

        try:
            if self.gesture_data:
                self.repository.update_gesture(self.gesture_data['id'], name, enabled, confirm, message)
            else:
                self.repository.add_gesture(self.app_id, name, enabled, confirm, message)
            
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save gesture: {e}")
