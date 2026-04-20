import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Dict, Any
from persistence.repository import Repository
from ui.gesture_editor import GestureEditor
from ui.action_editor import ActionEditor
from automation.action_router import ActionRouter

class MainWindow(tk.Tk):
    """
    Main application window for managing gesture configurations.
    """
    def __init__(self, repository: Repository, action_router: ActionRouter):
        super().__init__()
        self.repository = repository
        self.action_router = action_router
        
        self.title("RemGesture Control Panel")
        self.geometry("1100x700")
        
        self.selected_app_id: Optional[int] = None
        self.selected_gesture_id: Optional[int] = None
        
        self._setup_ui()
        self._refresh_apps()

    def _setup_ui(self):
        # Main Paned Window
        self.paned = ttk.PanedWindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True)

        # --- Left Panel: Applications ---
        left_frame = ttk.Frame(self.paned, padding=10)
        self.paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Applications", font=("TkDefaultFont", 11, "bold")).pack(pady=(0, 10))
        
        self.app_listbox = tk.Listbox(left_frame, font=("TkDefaultFont", 10))
        self.app_listbox.pack(fill="both", expand=True)
        self.app_listbox.bind("<<ListboxSelect>>", self._on_app_select)
        
        app_btn_frame = ttk.Frame(left_frame)
        app_btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(app_btn_frame, text="Add App", command=self._add_app).pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(app_btn_frame, text="Remove App", command=self._remove_app).pack(side="left", fill="x", expand=True, padx=(2, 0))

        # --- Center Panel: Gestures ---
        center_frame = ttk.Frame(self.paned, padding=10)
        self.paned.add(center_frame, weight=2)
        
        ttk.Label(center_frame, text="Gestures", font=("TkDefaultFont", 11, "bold")).pack(pady=(0, 10))
        
        self.gesture_tree = ttk.Treeview(center_frame, columns=("Enabled", "Confirm"), show="headings")
        self.gesture_tree.heading("Enabled", text="Enabled")
        self.gesture_tree.heading("Confirm", text="Confirm")
        self.gesture_tree.pack(fill="both", expand=True)
        self.gesture_tree.bind("<<TreeviewSelect>>", self._on_gesture_select)
        
        gest_btn_frame = ttk.Frame(center_frame)
        gest_btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(gest_btn_frame, text="Add Gesture", command=self._add_gesture).pack(side="left", padx=2)
        ttk.Button(gest_btn_frame, text="Edit", command=self._edit_gesture).pack(side="left", padx=2)
        ttk.Button(
            gest_btn_frame,
            text="Manual Mode",
            command=self.enable_manual_mode
        ).pack(side="left", padx=2)

        ttk.Button(
            gest_btn_frame,
            text="Auto Mode",
            command=self.enable_auto_mode
        ).pack(side="left", padx=2)

        # --- Right Panel: Actions ---
        right_frame = ttk.Frame(self.paned, padding=10)
        self.paned.add(right_frame, weight=2)
        
        ttk.Label(right_frame, text="Actions", font=("TkDefaultFont", 11, "bold")).pack(pady=(0, 10))
        
        self.action_listbox = tk.Listbox(right_frame, font=("TkDefaultFont", 10))
        self.action_listbox.pack(fill="both", expand=True)
        
        act_btn_frame = ttk.Frame(right_frame)
        act_btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(act_btn_frame, text="Add Action", command=self._add_action).pack(side="left", padx=2)
        ttk.Button(act_btn_frame, text="Remove", command=self._remove_action).pack(side="left", padx=2)
        ttk.Button(act_btn_frame, text="Up", command=lambda: self._move_action(-1)).pack(side="left", padx=2)
        ttk.Button(act_btn_frame, text="Down", command=lambda: self._move_action(1)).pack(side="left", padx=2)

    # --- App Methods ---
    def _refresh_apps(self):
        self.app_listbox.delete(0, tk.END)
        self.apps = self.repository.get_all_applications()
        for app in self.apps:
            self.app_listbox.insert(tk.END, app['name'])
        self.selected_app_id = None
        self._refresh_gestures()

    def _on_app_select(self, event):
        selection = self.app_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_app_id = self.apps[index]['id']
            self._refresh_gestures()

    def _add_app(self):
        name = simpledialog.askstring("Add Application", "Enter application executable name (e.g. chrome.exe):")
        if name:
            try:
                self.repository.add_application(name)
                self._refresh_apps()
            except Exception as e:
                messagebox.showerror("Error", f"Could not add application: {e}")

    def _remove_app(self):
        if self.selected_app_id:
            app_name = self.app_listbox.get(tk.ACTIVE)
            if app_name == "global":
                messagebox.showwarning("Warning", "Cannot remove the 'global' application.")
                return
            if messagebox.askyesno("Confirm", f"Delete all rules for '{app_name}'?"):
                self.repository.delete_application(self.selected_app_id)
                self._refresh_apps()

    # --- Gesture Methods ---
    def _refresh_gestures(self):
        for item in self.gesture_tree.get_children():
            self.gesture_tree.delete(item)
        
        if self.selected_app_id is not None:
            self.gestures = self.repository.get_gestures_for_app(self.selected_app_id)
            for g in self.gestures:
                enabled = "Yes" if g['enabled'] else "No"
                confirm = "Yes" if g['confirm'] else "No"
                self.gesture_tree.insert("", tk.END, iid=str(g['id']), text=g['gesture_name'], values=(enabled, confirm))
        
        self.selected_gesture_id = None
        self._refresh_actions()

    def _on_gesture_select(self, event):
        selection = self.gesture_tree.selection()
        if selection:
            self.selected_gesture_id = int(selection[0])
            self._refresh_actions()

    def _add_gesture(self):
        if self.selected_app_id is not None:
            GestureEditor(self, self.repository, self.selected_app_id, on_save=self._on_config_change)

    def _edit_gesture(self):
        if self.selected_gesture_id:
            gesture_data = next(g for g in self.gestures if g['id'] == self.selected_gesture_id)
            GestureEditor(self, self.repository, self.selected_app_id, gesture_data, on_save=self._on_config_change)

    def _delete_gesture(self):
        if self.selected_gesture_id:
            if messagebox.askyesno("Confirm", "Delete this gesture rule?"):
                self.repository.delete_gesture(self.selected_gesture_id)
                self._on_config_change()

    # --- Action Methods ---
    def _refresh_actions(self):
        self.action_listbox.delete(0, tk.END)
        if self.selected_gesture_id:
            self.actions = self.repository.get_actions_for_gesture(self.selected_gesture_id)
            for a in self.actions:
                self.action_listbox.insert(tk.END, f"{a['action_type'].upper()}")

    def _add_action(self):
        if self.selected_gesture_id:
            ActionEditor(self, self.repository, self.selected_gesture_id, on_save=self._on_config_change)

    def _remove_action(self):
        selection = self.action_listbox.curselection()
        if selection:
            action_id = self.actions[selection[0]]['id']
            if messagebox.askyesno("Confirm", "Remove this action?"):
                self.repository.delete_action(action_id)
                self._on_config_change()

    def _move_action(self, direction: int):
        selection = self.action_listbox.curselection()
        if not selection: return
        
        index = selection[0]
        new_index = index + direction
        
        if 0 <= new_index < len(self.actions):
            action1 = self.actions[index]
            action2 = self.actions[new_index]
            
            self.repository.update_action_order(action1['id'], new_index)
            self.repository.update_action_order(action2['id'], index)
            self._on_config_change()
            self.action_listbox.selection_set(new_index)

    def _on_config_change(self):
        """Called whenever data is modified to refresh UI and reload router."""
        self._refresh_gestures()
        self._refresh_actions()
        self.action_router.reload_config()

    def enable_auto_mode(self):
        self.action_router.set_manual_override(None)
        print("Auto detect mode enabled")

    def enable_manual_mode(self):
        selected_app = self.app_listbox.get(tk.ACTIVE)

        if not selected_app:
            print("Select an app first!")
            return

        self.action_router.set_manual_override(selected_app.lower())
        print("Manual mode enabled for:", selected_app)