import os
import sys
import threading
import time
import signal
from typing import List, Tuple

# Ensure the app directory is in the path for modular imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from gesture_engine.gesture_listener import GestureListener
from gesture_engine.feature_extractor import FeatureExtractor
from gesture_engine.model_manager import ModelManager
from gesture_engine.app_detector import AppDetector
from persistence.database import Database
from persistence.repository import Repository
from automation.action_router import ActionRouter
from ui.main_window import MainWindow
from utils.logger import logger

class GestureApp:
    """
    Main application class that orchestrates the gesture engine and the GUI.
    """
    def __init__(self):
        # 1. Initialize Persistence Layer
        self.db = Database(settings.DB_PATH if hasattr(settings, 'DB_PATH') else "gesture_config.db")
        self.repository = Repository(self.db)
        
        # 2. Initialize Automation Components
        self.action_router = ActionRouter(self.repository)
        
        # 3. Initialize Gesture Engine Components
        self.feature_extractor = FeatureExtractor(num_points=settings.NUM_POINTS)
        self.model_manager = ModelManager(
            settings.MODEL_PATH, 
            settings.DATASET_PATH, 
            settings.CONFIDENCE_THRESHOLD
        )
        self.app_detector = AppDetector()
        
        # Debounce state
        self.last_gesture_name = None
        self.last_gesture_time = 0
        self.debounce_interval = getattr(settings, 'DEBOUNCE_INTERVAL', 0.15)
        
        # Auto-train if model is missing
        if self.model_manager.model is None:
            logger.info("Model missing. Attempting automatic training...")
            X, y, labels = self.model_manager.load_dataset()
            if X is not None and len(X) > 0:
                self.model_manager.train(X, y, labels)
            else:
                logger.error("Failed to load dataset. Automatic training aborted.")

        # 4. Initialize Listener
        self.listener = GestureListener(
            trigger_key=settings.TRIGGER_KEY,
            on_gesture_complete=self.process_gesture,
            cooldown_seconds=0 # Cooldown handled by debounce
        )
        
        self.running = True

    def process_gesture(self, points: List[Tuple[int, int]]) -> None:
        """
        Callback triggered when a gesture is completed.
        """
        features = self.feature_extractor.extract_features(points)
        if features is not None:
            gesture_name, confidence = self.model_manager.predict(features)
            
            if gesture_name:
                current_time = time.time()
                
                # Smart Debounce: Prevent rapid re-triggering of the same gesture
                if gesture_name == self.last_gesture_name:
                    if current_time - self.last_gesture_time < self.debounce_interval:
                        logger.debug(f"Debounced gesture: {gesture_name}")
                        return
                
                self.last_gesture_name = gesture_name
                self.last_gesture_time = current_time
                
                app_name = self.app_detector.get_active_app_name()
                logger.info(f"Detected Gesture: {gesture_name} (Conf: {confidence:.2f}) in {app_name}")
                
                # Execute in a separate thread to keep engine non-blocking
                threading.Thread(
                    target=self.action_router.execute, 
                    args=(app_name, gesture_name), 
                    daemon=True
                ).start()
            else:
                logger.debug(f"Low confidence prediction ({confidence:.2f}). Gesture ignored.")
        else:
            logger.warning("Gesture too short or invalid.")

    def start_engine(self) -> None:
        """
        Starts the gesture listener in a background thread.
        """
        logger.info("Starting gesture engine thread...")
        self.listener.start()

    def stop_engine(self) -> None:
        """
        Stops the gesture listener.
        """
        logger.info("Stopping gesture engine...")
        self.listener.stop()
        self.running = False

    def run_gui(self) -> None:
        """
        Launches the MainWindow GUI (Main Thread).
        """
        app_gui = MainWindow(self.repository, self.action_router)
        
        # Handle window close
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit the entire application?"):
                self.stop_engine()
                app_gui.destroy()
                sys.exit(0)
        
        from tkinter import messagebox
        app_gui.protocol("WM_DELETE_WINDOW", on_closing)
        
        logger.info("Launching Control Panel GUI...")
        app_gui.mainloop()

def main():
    # Setup signal handlers for clean exit
    def signal_handler(sig, frame):
        logger.info("Signal received, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    app = GestureApp()
    
    # Start engine in background
    engine_thread = threading.Thread(target=app.start_engine, daemon=True)
    engine_thread.start()
    
    # Start GUI in main thread
    app.run_gui()

if __name__ == "__main__":
    main()
