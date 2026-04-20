import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from typing import Optional, Dict, Any, Callable

class ActionEditor(tk.Toplevel):
    """
    Window for adding or editing an action for a gesture.
    """
    def __init__(self, parent, repository, gesture_id: int, action_data: Optional[Dict[str, Any]] = None, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.repository = repository
        self.gesture_id = gesture_id
        self.action_data = action_data
        self.on_save = on_save
        
        self.title("Edit Action" if action_data else "Add Action")
        self.geometry("500x600")
        self.grab_set()
        
        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Action Type
        ttk.Label(main_frame, text="Action Type:").pack(anchor="w", pady=(0, 5))
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, state="readonly")
        self.type_combo['values'] = ("hotkey", "keypress", "mouse_scroll", "open_app", "open_url", "run_command", "custom_python")
        self.type_combo.pack(fill="x", pady=(0, 15))
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        # Dynamic Config Area
        self.config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=15)
        self.config_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

        if self.action_data:
            self.type_var.set(self.action_data['action_type'])
            self._on_type_change()
            self._load_config(json.loads(self.action_data['config_json']))
        else:
            self.type_var.set("hotkey")
            self._on_type_change()

    def _on_type_change(self, event=None):
        # Clear config frame
        for widget in self.config_frame.winfo_children():
            widget.destroy()

        atype = self.type_var.get()
        self.inputs = {}

        if atype == "hotkey":
            ttk.Label(self.config_frame, text="Sequence (e.g. [['ctrl', 'c']] or [['ctrl', 'k'], ['ctrl', 'o']]):").pack(anchor="w")
            self.inputs["sequence"] = tk.Text(self.config_frame, height=4)
            self.inputs["sequence"].pack(fill="x", pady=5)
            
            ttk.Label(self.config_frame, text="Interval between steps (s):").pack(anchor="w")
            self.inputs["interval"] = ttk.Entry(self.config_frame)
            self.inputs["interval"].insert(0, "0.1")
            self.inputs["interval"].pack(fill="x", pady=5)

        elif atype == "keypress":
            ttk.Label(self.config_frame, text="Key:").pack(anchor="w")
            self.inputs["key"] = ttk.Entry(self.config_frame)
            self.inputs["key"].pack(fill="x", pady=5)
            
            ttk.Label(self.config_frame, text="Repeats:").pack(anchor="w")
            self.inputs["repeats"] = ttk.Entry(self.config_frame)
            self.inputs["repeats"].insert(0, "1")
            self.inputs["repeats"].pack(fill="x", pady=5)
            
            ttk.Label(self.config_frame, text="Interval (s):").pack(anchor="w")
            self.inputs["interval"] = ttk.Entry(self.config_frame)
            self.inputs["interval"].insert(0, "0.1")
            self.inputs["interval"].pack(fill="x", pady=5)

        elif atype == "mouse_scroll":
            ttk.Label(self.config_frame, text="Amount:").pack(anchor="w")
            self.inputs["amount"] = ttk.Entry(self.config_frame)
            self.inputs["amount"].insert(0, "1")
            self.inputs["amount"].pack(fill="x", pady=5)
            
            ttk.Label(self.config_frame, text="Repeats:").pack(anchor="w")
            self.inputs["repeats"] = ttk.Entry(self.config_frame)
            self.inputs["repeats"].insert(0, "1")
            self.inputs["repeats"].pack(fill="x", pady=5)

        elif atype == "open_app":
            ttk.Label(self.config_frame, text="App Path:").pack(anchor="w")
            path_frame = ttk.Frame(self.config_frame)
            path_frame.pack(fill="x", pady=5)
            self.inputs["path"] = ttk.Entry(path_frame)
            self.inputs["path"].pack(side="left", fill="x", expand=True)
            ttk.Button(path_frame, text="Browse", command=self._browse_file).pack(side="left", padx=5)

        elif atype == "open_url":
            ttk.Label(self.config_frame, text="URL:").pack(anchor="w")
            self.inputs["url"] = ttk.Entry(self.config_frame)
            self.inputs["url"].pack(fill="x", pady=5)

        elif atype == "run_command":
            ttk.Label(self.config_frame, text="Command:").pack(anchor="w")
            self.inputs["command"] = ttk.Entry(self.config_frame)
            self.inputs["command"].pack(fill="x", pady=5)

        elif atype == "custom_python":
            ttk.Label(self.config_frame, text="Python Code:").pack(anchor="w")
            self.inputs["code"] = tk.Text(self.config_frame, height=15, font=("Courier", 10))
            self.inputs["code"].pack(fill="both", expand=True, pady=5)

    def _browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.inputs["path"].delete(0, tk.END)
            self.inputs["path"].insert(0, filename)

    def _load_config(self, config: Dict[str, Any]):
        atype = self.type_var.get()
        try:
            if atype == "hotkey":
                self.inputs["sequence"].insert("1.0", str(config.get("sequence", [])))
                self.inputs["interval"].delete(0, tk.END)
                self.inputs["interval"].insert(0, str(config.get("interval_between_steps", 0.1)))
            elif atype == "keypress":
                self.inputs["key"].insert(0, config.get("key", ""))
                self.inputs["repeats"].delete(0, tk.END)
                self.inputs["repeats"].insert(0, str(config.get("repeats", 1)))
                self.inputs["interval"].delete(0, tk.END)
                self.inputs["interval"].insert(0, str(config.get("interval", 0.1)))
            elif atype == "mouse_scroll":
                self.inputs["amount"].delete(0, tk.END)
                self.inputs["amount"].insert(0, str(config.get("amount", 1)))
                self.inputs["repeats"].delete(0, tk.END)
                self.inputs["repeats"].insert(0, str(config.get("repeats", 1)))
            elif atype == "open_app":
                self.inputs["path"].insert(0, config.get("path", ""))
            elif atype == "open_url":
                self.inputs["url"].insert(0, config.get("url", ""))
            elif atype == "run_command":
                self.inputs["command"].insert(0, config.get("command", ""))
            elif atype == "custom_python":
                self.inputs["code"].insert("1.0", config.get("code", ""))
        except Exception as e:
            print(f"Error loading config into UI: {e}")

    def _save(self):
        atype = self.type_var.get()
        config = {}
        
        try:
            if atype == "hotkey":
                config["sequence"] = eval(self.inputs["sequence"].get("1.0", tk.END).strip())
                config["interval_between_steps"] = float(self.inputs["interval"].get())
            elif atype == "keypress":
                config["key"] = self.inputs["key"].get().strip()
                config["repeats"] = int(self.inputs["repeats"].get())
                config["interval"] = float(self.inputs["interval"].get())
            elif atype == "mouse_scroll":
                config["amount"] = int(self.inputs["amount"].get())
                config["repeats"] = int(self.inputs["repeats"].get())
            elif atype == "open_app":
                config["path"] = self.inputs["path"].get().strip()
            elif atype == "open_url":
                config["url"] = self.inputs["url"].get().strip()
            elif atype == "run_command":
                config["command"] = self.inputs["command"].get().strip()
            elif atype == "custom_python":
                config["code"] = self.inputs["code"].get("1.0", tk.END).strip()
            
            config_json = json.dumps(config)
            
            if self.action_data:
                # For simplicity in this UI, we delete and re-add or just update if we had an update_action method
                # Repository doesn't have update_action yet, let's add it or just delete/re-add
                self.repository.delete_action(self.action_data['id'])
                self.repository.add_action(self.gesture_id, atype, config_json, self.action_data['execution_order'])
            else:
                # Get current actions to determine order
                existing = self.repository.get_actions_for_gesture(self.gesture_id)
                order = len(existing)
                self.repository.add_action(self.gesture_id, atype, config_json, order)

            if self.on_save:
                self.on_save()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Invalid configuration: {e}")
