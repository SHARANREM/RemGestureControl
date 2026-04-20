from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class ActionModel:
    id: Optional[int]
    gesture_id: int
    action_type: str
    config_json: str
    execution_order: int

@dataclass
class GestureModel:
    id: Optional[int]
    app_id: Optional[int]
    gesture_name: str
    enabled: bool
    confirm: bool
    confirmation_message: Optional[str]
    actions: List[ActionModel]

@dataclass
class ApplicationModel:
    id: Optional[int]
    name: str
    gestures: List[GestureModel]
