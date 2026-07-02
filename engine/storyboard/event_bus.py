# engine/storyboard/event_bus.py
from typing import Callable, Dict, List, Any

class EventBus:
    """
    Subsystem: Internal Event Bus
    A simple pub-sub event broker to keep Movie OS components decoupled.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Subscribes a listener to a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def publish(self, event_type: str, data: Any):
        """Publishes an event to all subscribed listeners."""
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"[EventBus] Error in handler for {event_type}: {e}")
