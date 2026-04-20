import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, List, Callable
from ui.widgets import ScrollableFrame, LabeledEntry

class ActionBuilder(tk.Toplevel):
    """
    A dialog for building and editing a gesture rule with multiple actions.
    """
    def __init__(self, parent, gesture_name: str, rule: Dict[str, Any], on_save: Callable):
        super().__init__(parent)
        self.title(f"Edit Rule: {gesture_name}")
        self.geometry("600x700")
        self.gesture_name = gesture_name
        self.on_save = on_save
        
        # Initial state
        self.enabled_var = tk.BooleanVar(value=rule.get("enabled", True))
        self.confirm_var = tk.BooleanVar(value=rule.get("confirm", False))
        self.confirm_msg_var = tk.StringVar(value=rule.get("confirmation_message", ""))
        self.actions = rule.get("actions", [])[:] # Copy

        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Basic Settings
        settings_frame = ttk.LabelFrame(main_frame, text="General Settings", padding=10)
        settings_frame.pack(fill="x", pady=5)

        ttk.Checkbutton(settings_frame, text="Enabled", variable=self.enabled_var).pack(anchor="w")
        ttk.Checkbutton(settings_frame, text="Require Confirmation", variable=self.confirm_var).pack(anchor="w")
        
        ttk.Label(settings_frame, text="Confirmation Message:").pack(anchor="w", pady=(5, 0))
        ttk.Entry(settings_frame, textvariable=self.confirm_msg_var).pack(fill="x", pady=2)

        # Actions List
        actions_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        actions_frame.pack(fill="both", expand=True, pady=5)

        self.scroll_frame = ScrollableFrame(actions_frame)
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.action_container = self.scroll_frame.scrollable_window

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Add Action", command=self._add_action_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Rule", command=self._save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)

        self._refresh_actions()

    def _refresh_actions(self):
        for widget in self.action_container.winfo_children():
            widget.destroy()

        for i, action in enumerate(self.actions):
            self._render_action_item(i, action)

    def _render_action_item(self, index, action):
        frame = ttk.Frame(self.action_container, padding=5, relief="groove", borderwidth=1)
        frame.pack(fill="x", pady=2, padx=2)

        header = ttk.Frame(frame)
        header.pack(fill="x")
        
        ttk.Label(header, text=f"#{index+1} - {action['type'].upper()}", font=("TkDefaultFont", 9, "bold")).pack(side="left")
        ttk.Button(header, text="X", width=2, command=lambda i=index: self._remove_action(i)).pack(side="right")

        # Render fields based on type
        atype = action['type']
        if atype == "hotkey":
            ttk.Label(frame, text=f"Sequence: {action.get('sequence', [])}").pack(anchor="w")
        elif atype == "keypress":
            ttk.Label(frame, text=f"Key: {action.get('key')} | Repeats: {action.get('repeats')}").pack(anchor="w")
        elif atype == "open_url":
            ttk.Label(frame, text=f"URL: {action.get('url')}").pack(anchor="w")
        elif atype == "open_app":
            ttk.Label(frame, text=f"Path: {action.get('path')}").pack(anchor="w")
        elif atype == "run_command":
            ttk.Label(frame, text=f"Cmd: {action.get('command')}").pack(anchor="w")
        elif atype == "custom_python":
            ttk.Label(frame, text="Custom Python Code").pack(anchor="w")

    def _remove_action(self, index):
        del self.actions[index]
        self._refresh_actions()

    def _add_action_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Action")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Select Action Type:").pack(pady=10)
        type_var = tk.StringVar(value="hotkey")
        types = ["hotkey", "keypress", "mouse_scroll", "open_app", "open_url", "run_command", "custom_python"]
        combo = ttk.Combobox(dialog, textvariable=type_var, values=types, state="readonly")
        combo.pack(pady=5)

        def proceed():
            atype = type_var.get()
            dialog.destroy()
            self._configure_new_action(atype)

        ttk.Button(dialog, text="Next", command=proceed).pack(pady=20)

    def _configure_new_action(self, atype):
        config_win = tk.Toplevel(self)
        config_win.title(f"Configure {atype}")
        config_win.geometry("400x400")

        fields_frame = ttk.Frame(config_win, padding=20)
        fields_frame.pack(fill="both", expand=True)

        inputs = {}

        if atype == "hotkey":
            ttk.Label(fields_frame, text="Enter sequence (e.g. [['ctrl', 'c']] or [['ctrl', 'k'], ['ctrl', 'o']]):").pack()
            txt = tk.Text(fields_frame, height=4)
            txt.pack(fill="x")
            inputs["sequence"] = txt
        elif atype == "keypress":
            inputs["key"] = LabeledEntry(fields_frame, "Key:")
            inputs["key"].pack(fill="x")
            inputs["repeats"] = LabeledEntry(fields_frame, "Repeats:", "1")
            inputs["repeats"].pack(fill="x")
        elif atype == "open_url":
            inputs["url"] = LabeledEntry(fields_frame, "URL:")
            inputs["url"].pack(fill="x")
        elif atype == "open_app":
            inputs["path"] = LabeledEntry(fields_frame, "Path:")
            inputs["path"].pack(fill="x")
            def pick():
                p = filedialog.askopenfilename()
                if p: inputs["path"].entry.delete(0, tk.END); inputs["path"].entry.insert(0, p)
            ttk.Button(fields_frame, text="Browse", command=pick).pack()
        elif atype == "run_command":
            inputs["command"] = LabeledEntry(fields_frame, "Command:")
            inputs["command"].pack(fill="x")
        elif atype == "custom_python":
            ttk.Label(fields_frame, text="Python Code:").pack()
            txt = tk.Text(fields_frame, height=10)
            txt.pack(fill="both", expand=True)
            inputs["code"] = txt

        def save_action():
            new_action = {"type": atype}
            try:
                if atype == "hotkey":
                    new_action["sequence"] = eval(inputs["sequence"].get("1.0", tk.END).strip())
                elif atype == "keypress":
                    new_action["key"] = inputs["key"].get()
                    new_action["repeats"] = int(inputs["repeats"].get())
                elif atype == "open_url":
                    new_action["url"] = inputs["url"].get()
                elif atype == "open_app":
                    new_action["path"] = inputs["path"].get()
                elif atype == "run_command":
                    new_action["command"] = inputs["command"].get()
                elif atype == "custom_python":
                    new_action["code"] = inputs["code"].get("1.0", tk.END).strip()
                
                self.actions.append(new_action)
                config_win.destroy()
                self._refresh_actions()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        ttk.Button(config_win, text="Add", command=save_action).pack(pady=10)

    def _save(self):
        rule = {
            "enabled": self.enabled_var.get(),
            "confirm": self.confirm_var.get(),
            "confirmation_message": self.confirm_msg_var.get(),
            "actions": self.actions
        }
        self.on_save(self.gesture_name, rule)
        self.destroy()
