import json
from typing import List, Dict, Any, Optional
from persistence.database import Database
from persistence.models import ApplicationModel, GestureModel, ActionModel
from utils.logger import logger

class Repository:
    """
    Handles CRUD operations for applications, gestures, and actions.
    """
    def __init__(self, db: Database):
        self.db = db

    def get_all_applications(self) -> List[Dict[str, Any]]:
        """Returns all applications from the database."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM applications ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def add_application(self, name: str) -> int:
        """Adds a new application."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO applications (name) VALUES (?)", (name.lower(),))
            conn.commit()
            return cursor.lastrowid

    def delete_application(self, app_id: int) -> None:
        """Deletes an application and its associated gestures and actions."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
            conn.commit()

    def get_gestures_for_app(self, app_id: Optional[int]) -> List[Dict[str, Any]]:
        """Returns all gestures for a specific application."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if app_id is None:
                cursor.execute("SELECT * FROM gestures WHERE app_id IS NULL")
            else:
                cursor.execute("SELECT * FROM gestures WHERE app_id = ?", (app_id,))
            return [dict(row) for row in cursor.fetchall()]

    def add_gesture(self, app_id: Optional[int], gesture_name: str, enabled: bool, confirm: bool, confirmation_message: str) -> int:
        """Adds a new gesture."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO gestures (app_id, gesture_name, enabled, confirm, confirmation_message) VALUES (?, ?, ?, ?, ?)",
                (app_id, gesture_name, int(enabled), int(confirm), confirmation_message)
            )
            conn.commit()
            return cursor.lastrowid

    def update_gesture(self, gesture_id: int, gesture_name: str, enabled: bool, confirm: bool, confirmation_message: str) -> None:
        """Updates an existing gesture."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE gestures SET gesture_name = ?, enabled = ?, confirm = ?, confirmation_message = ? WHERE id = ?",
                (gesture_name, int(enabled), int(confirm), confirmation_message, gesture_id)
            )
            conn.commit()

    def delete_gesture(self, gesture_id: int) -> None:
        """Deletes a gesture and its associated actions."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gestures WHERE id = ?", (gesture_id,))
            conn.commit()

    def get_actions_for_gesture(self, gesture_id: int) -> List[Dict[str, Any]]:
        """Returns all actions for a specific gesture, ordered by execution_order."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM actions WHERE gesture_id = ? ORDER BY execution_order", (gesture_id,))
            return [dict(row) for row in cursor.fetchall()]

    def add_action(self, gesture_id: int, action_type: str, config_json: str, execution_order: int) -> int:
        """Adds a new action."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO actions (gesture_id, action_type, config_json, execution_order) VALUES (?, ?, ?, ?)",
                (gesture_id, action_type, config_json, execution_order)
            )
            conn.commit()
            return cursor.lastrowid

    def delete_action(self, action_id: int) -> None:
        """Deletes an action."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM actions WHERE id = ?", (action_id,))
            conn.commit()

    def update_action_order(self, action_id: int, execution_order: int) -> None:
        """Updates the execution order of an action."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE actions SET execution_order = ? WHERE id = ?", (execution_order, action_id))
            conn.commit()

    def get_full_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns the full configuration in a nested dictionary format
        compatible with the ActionRouter.
        """
        config = {}
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all apps
            cursor.execute("SELECT * FROM applications")
            apps = cursor.fetchall()
            
            for app in apps:
                app_name = app['name']
                app_id = app['id']
                config[app_name] = {}
                
                # Get all gestures for this app
                cursor.execute("SELECT * FROM gestures WHERE app_id = ?", (app_id,))
                gestures = cursor.fetchall()
                
                for gesture in gestures:
                    gesture_name = gesture['gesture_name']
                    gesture_id = gesture['id']
                    
                    # Get all actions for this gesture
                    cursor.execute("SELECT * FROM actions WHERE gesture_id = ? ORDER BY execution_order", (gesture_id,))
                    actions = cursor.fetchall()
                    
                    config[app_name][gesture_name] = {
                        "enabled": bool(gesture['enabled']),
                        "confirm": bool(gesture['confirm']),
                        "confirmation_message": gesture['confirmation_message'],
                        "actions": [
                            {
                                "type": action['action_type'],
                                **json.loads(action['config_json'])
                            } for action in actions
                        ]
                    }
            
            # Handle global gestures (where app_id is NULL)
            cursor.execute("SELECT * FROM gestures WHERE app_id IS NULL")
            global_gestures = cursor.fetchall()
            if global_gestures:
                if "global" not in config:
                    config["global"] = {}
                for gesture in global_gestures:
                    gesture_name = gesture['gesture_name']
                    gesture_id = gesture['id']
                    cursor.execute("SELECT * FROM actions WHERE gesture_id = ? ORDER BY execution_order", (gesture_id,))
                    actions = cursor.fetchall()
                    config["global"][gesture_name] = {
                        "enabled": bool(gesture['enabled']),
                        "confirm": bool(gesture['confirm']),
                        "confirmation_message": gesture['confirmation_message'],
                        "actions": [
                            {
                                "type": action['action_type'],
                                **json.loads(action['config_json'])
                            } for action in actions
                        ]
                    }
                    
        return config
