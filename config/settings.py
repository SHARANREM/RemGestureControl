import os

# Gesture Settings
NUM_POINTS = 64
CONFIDENCE_THRESHOLD = 0.50
DEBOUNCE_INTERVAL = 0.3
TRIGGER_KEY = 'ctrl_l' # Use specific key name for pynput
SEGMENTATION_PAUSE_MS = 250 # Pause in movement to trigger mid-hold

# Mouse Settings
MOUSE_SMOOTHNESS = 10
MOUSE_SPEED = 1

# Automation Settings
MODIFIER_PERSISTENCE_MS = 500 # Keep modifiers pressed for X ms

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'data', 'Collection')
MODEL_PATH = os.path.join(BASE_DIR, 'data', 'model.pkl')
MODEL_INFO_PATH = os.path.join(BASE_DIR, 'data', 'model_info.npy')
ACTIONS_CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'actions.json')

# Feature Extraction
MIN_POINTS_THRESHOLD = 10
