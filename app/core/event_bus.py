from collections import defaultdict
from typing import Callable, Dict, List, Any


class EventBus:
    """
    Simple in-memory pub/sub event bus.
    Used to decouple watcher, UI, ingestion, logging, etc.
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable[[Any], None]):
        self.subscribers[event_type].append(handler)

    def emit(self, event_type: str, data=None):
        if event_type not in self.subscribers:
            return

        for handler in self.subscribers[event_type]:
            try:
                handler(data)
            except Exception as e:
                print(f"[EVENT BUS ERROR] {event_type}: {e}")


# Global singleton (simple V1 approach)
event_bus = EventBus()