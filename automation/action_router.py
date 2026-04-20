import os
import sys
from typing import Any, Dict, Optional

# Ensure root directory is in path for utils/config imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
from automation.action_executor import ActionExecutor
from automation.confirmation_dialog import ConfirmationDialog
from persistence.repository import Repository
from utils.logger import logger

class ActionRouter:
    """
    Routes gestures to their defined actions, querying the database for configuration.
    """
    def __init__(self, repository: Repository):
        self.repository = repository
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.executor = ActionExecutor(self.keyboard, self.mouse)
        self._config_cache: Dict[str, Any] = {}
        self.manual_override_app_name: Optional[str] = None
        self.reload_config()

    def reload_config(self) -> None:
        """
        Refreshes the internal configuration cache from the database.
        """
        try:
            self._config_cache = self.repository.get_full_config()
            logger.info("ActionRouter configuration reloaded from database.")
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")

    def set_manual_override(self, app_name: Optional[str]):
        self.manual_override_app_name = app_name

    def execute(self, app_name: str, gesture_name: str) -> None:
        """
        Main entry point for gesture execution.
        """
        # 1. Find the rule (App-specific or Global)
        # Determine which app context to use
        if self.manual_override_app_name:
            active_app = self.manual_override_app_name
        else:
            active_app = app_name

        app_rules = self._config_cache.get(active_app, {})
        rule = app_rules.get(gesture_name)
        
        if not rule:
            # Fallback to global
            global_rules = self._config_cache.get("global", {})
            rule = global_rules.get(gesture_name)
            
        if not rule:
            logger.info(f"No rule found for gesture '{gesture_name}' in app '{active_app}' or global.")
            return

        # 2. Check if enabled
        if not rule.get("enabled", True):
            logger.info(f"Gesture '{gesture_name}' is disabled. Skipping.")
            return

        # 3. Handle confirmation
        if rule.get("confirm", False):
            confirmed = ConfirmationDialog.show(
                active_app,   # ✅ correct context
                gesture_name,
                rule.get("confirmation_message")
            )
            if not confirmed:
                logger.info(f"User cancelled execution for gesture '{gesture_name}'.")
                return

        # 4. Delegate execution
        actions = rule.get("actions", [])
        logger.info(f"Routing {len(actions)} actions for gesture '{gesture_name}'")
        self.executor.execute_actions(actions)
        print("Detected app_name:", app_name)
        print("Manual override:", self.manual_override_app_name)
        print("Available apps:", list(self._config_cache.keys()))
