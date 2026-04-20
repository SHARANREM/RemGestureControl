import json
import os
from typing import Dict, Any, List, Optional
from utils.logger import logger

class ConfigManager:
    """
    Handles loading, saving, and validating the actions configuration JSON.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Loads the configuration from the JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self.config = {}
        else:
            logger.warning(f"Config file not found at {self.config_path}. Initializing empty config.")
            self.config = {}

    def save_config(self) -> bool:
        """Saves the current configuration to the JSON file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False

    def get_apps(self) -> List[str]:
        """Returns a list of applications in the config."""
        return list(self.config.keys())

    def get_gestures_for_app(self, app_name: str) -> Dict[str, Any]:
        """Returns the gesture mappings for a specific application."""
        return self.config.get(app_name, {})

    def add_app(self, app_name: str) -> None:
        """Adds a new application entry if it doesn't exist."""
        if app_name not in self.config:
            self.config[app_name] = {}
            self.save_config()

    def add_rule(self, app_name: str, gesture_name: str, rule: Dict[str, Any]) -> None:
        """Adds or updates a gesture rule for an application."""
        if app_name not in self.config:
            self.config[app_name] = {}
        self.config[app_name][gesture_name] = rule
        self.save_config()

    def remove_rule(self, app_name: str, gesture_name: str) -> None:
        """Removes a gesture rule from an application."""
        if app_name in self.config and gesture_name in self.config[app_name]:
            del self.config[app_name][gesture_name]
            self.save_config()

    def toggle_rule(self, app_name: str, gesture_name: str) -> None:
        """Toggles the enabled state of a gesture rule."""
        if app_name in self.config and gesture_name in self.config[app_name]:
            current = self.config[app_name][gesture_name].get("enabled", True)
            self.config[app_name][gesture_name]["enabled"] = not current
            self.save_config()

    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Validates the structure of a gesture rule.
        """
        required_fields = ["enabled", "actions"]
        if not all(field in rule for field in required_fields):
            return False
        
        actions = rule.get("actions", [])
        if not isinstance(actions, list):
            return False
            
        valid_types = ["hotkey", "keypress", "mouse_scroll", "open_app", "open_url", "run_command", "custom_python"]
        for action in actions:
            if action.get("type") not in valid_types:
                return False
                
        return True
