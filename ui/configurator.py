import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from automation.config_manager import ConfigManager
from ui.action_builder import ActionBuilder

class Configurator(tk.Tk):
    """
    Main GUI window for configuring gesture mappings.
    """
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.title("RemGesture Configurator")
        self.geometry("1000x600")
        
        self.selected_app: Optional[str] = None
        
        self._setup_ui()
        self._refresh_app_list()

    def _setup_ui(self):
        # Main Layout: Left (Apps), Center (Gestures), Right (Info/Actions)
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Left Panel: Apps
        left_frame = ttk.Frame(paned, padding=10)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Applications", font=("TkDefaultFont", 10, "bold")).pack(pady=(0, 5))
        
        self.app_listbox = tk.Listbox(left_frame)
        self.app_listbox.pack(fill="both", expand=True)
        self.app_listbox.bind("<<ListboxSelect>>", self._on_app_select)
        
        app_btn_frame = ttk.Frame(left_frame)
        app_btn_frame.pack(fill="x", pady=5)
        ttk.Button(app_btn_frame, text="+ Add App", command=self._add_app).pack(side="left", fill="x", expand=True)

        # Center Panel: Gestures
        center_frame = ttk.Frame(paned, padding=10)
        paned.add(center_frame, weight=2)
        
        ttk.Label(center_frame, text="Gesture Rules", font=("TkDefaultFont", 10, "bold")).pack(pady=(0, 5))
        
        self.gesture_tree = ttk.Treeview(center_frame, columns=("Enabled", "Actions"), show="headings")
        self.gesture_tree.heading("Enabled", text="Enabled")
        self.gesture_tree.heading("Actions", text="Actions Count")
        self.gesture_tree.pack(fill="both", expand=True)
        
        gest_btn_frame = ttk.Frame(center_frame)
        gest_btn_frame.pack(fill="x", pady=5)
        ttk.Button(gest_btn_frame, text="+ Add Rule", command=self._add_rule).pack(side="left", padx=2)
        ttk.Button(gest_btn_frame, text="Edit", command=self._edit_rule).pack(side="left", padx=2)
        ttk.Button(gest_btn_frame, text="Delete", command=self._delete_rule).pack(side="left", padx=2)
        ttk.Button(gest_btn_frame, text="Toggle", command=self._toggle_rule).pack(side="left", padx=2)

    def _refresh_app_list(self):
        self.app_listbox.delete(0, tk.END)
        apps = self.config_manager.get_apps()
        for app in apps:
            self.app_listbox.insert(tk.END, app)

    def _on_app_select(self, event):
        selection = self.app_listbox.curselection()
        if not selection:
            return
        
        self.selected_app = self.app_listbox.get(selection[0])
        self._refresh_gesture_list()

    def _refresh_gesture_list(self):
        for item in self.gesture_tree.get_children():
            self.gesture_tree.delete(item)
            
        if not self.selected_app:
            return
            
        gestures = self.config_manager.get_gestures_for_app(self.selected_app)
        for gname, rule in gestures.items():
            enabled = "Yes" if rule.get("enabled", True) else "No"
            count = len(rule.get("actions", []))
            self.gesture_tree.insert("", tk.END, iid=gname, values=(enabled, count))

    def _add_app(self):
        app_name = tk.simpledialog.askstring("Add App", "Enter executable name (e.g. chrome.exe):")
        if app_name:
            self.config_manager.add_app(app_name.lower())
            self._refresh_app_list()

    def _add_rule(self):
        if not self.selected_app:
            messagebox.showwarning("Warning", "Select an application first.")
            return
        
        gname = tk.simpledialog.askstring("Add Rule", "Enter gesture name (e.g. Circle, Up):")
        if gname:
            rule = {"enabled": True, "confirm": False, "actions": []}
            ActionBuilder(self, gname, rule, self._save_rule_callback)

    def _edit_rule(self):
        selected = self.gesture_tree.selection()
        if not selected:
            return
        
        gname = selected[0]
        rule = self.config_manager.get_gestures_for_app(self.selected_app).get(gname)
        ActionBuilder(self, gname, rule, self._save_rule_callback)

    def _save_rule_callback(self, gname, rule):
        self.config_manager.add_rule(self.selected_app, gname, rule)
        self._refresh_gesture_list()

    def _delete_rule(self):
        selected = self.gesture_tree.selection()
        if not selected:
            return
        
        gname = selected[0]
        if messagebox.askyesno("Confirm", f"Delete rule for '{gname}'?"):
            self.config_manager.remove_rule(self.selected_app, gname)
            self._refresh_gesture_list()

    def _toggle_rule(self):
        selected = self.gesture_tree.selection()
        if not selected:
            return
        
        gname = selected[0]
        self.config_manager.toggle_rule(self.selected_app, gname)
        self._refresh_gesture_list()
