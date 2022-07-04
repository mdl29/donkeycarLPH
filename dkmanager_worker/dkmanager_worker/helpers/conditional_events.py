from enum import Enum
from typing import List

from dkmanager_worker.helpers.RegistableEvents import RegistableEvent

class CondEventsOperator(str, Enum):
    AND = "and"
    OR = "or"

class ConditionalEvents(RegistableEvent):

    def __init__(self, events: List[RegistableEvent], operator: CondEventsOperator):
        super(ConditionalEvents, self).__init__()

        self._events = events
        self._operator = operator

        for event in events:
            event.add_listener(self.on_event_changed)

        self.on_event_changed(self)  # Set initial flag state

    def _remove_listeners(self):
        for event in self._events:
            event.remove_listener(self.on_event_changed)

    def on_event_changed(self, event: RegistableEvent):
        """
        Hook run each times an event changes.
        :param event: event that is calling the hook
        """
        bools = [e.is_set() for e in self._events]
        is_ok = False

        if self._operator == CondEventsOperator.AND:
            is_ok = all(bools)

        if self._operator == CondEventsOperator.OR:
            is_ok = any(bools)

        if is_ok:
            self.set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._remove_listeners()

    def __del__(self):
        self._remove_listeners()