from enum import Enum
from asyncio import Event
from typing import List


class AsyncCondEventsOperator(str, Enum):
    AND = "and"
    OR = "or"


class AsyncCondEvents(Event):

    def __init__(self, events: List[Event], operator: AsyncCondEventsOperator):
        """
        :param events: List of events.
        """
        super(AsyncCondEvents, self).__init__()

        self._events = events
        self._operator = operator

        for event in events:
            self._override_event(event)

        # Run a first pool, if in any case some events are already set
        self.change_callback()

    def change_callback(self):
        """
        Called for each event set or clear, used to see if we should set the global OrEvent.
        """
        bools = [e.is_set() for e in self._events]
        is_ok = False

        if self._operator == AsyncCondEventsOperator.AND:
            is_ok = all(bools)

        if self._operator == AsyncCondEventsOperator.OR:
            is_ok = any(bools)

        if is_ok:  # One event was set we need to trigger OrEvents
            self.set()
        else:  # No events set we need to clear OrEvents
            self.clear()

    def _override_event(self, event: Event):
        """
        Override an event set and clear methods, but keeps them somewhere else.
        :param event:
        :return:
        """
        event_set = event.set
        even_clear = event.clear

        # Keeping original event set method, handle multiple chaining of OrEvent
        if not hasattr(event, '_cond_event_original_sets'):
            event._cond_event_original_sets = []

        event._cond_event_original_sets.append(event_set)

        # Keeping oiginal event clear method, handle mutliple chaining of OrEvent
        if not hasattr(event, '_cond_event_original_clears'):
            event._cond_event_original_clears = []

        event._cond_event_original_clears.append(even_clear)

        # Register change callback, might have multiples if we have OrEvent chaining
        if not hasattr(event, '_cond_event_original_change_callback'):
            event._cond_event_original_change_callback = []

        event._cond_event_original_change_callback.append(self.change_callback)

        # Now we can override them with generic function that call all event sets and clears
        event.set = lambda: AsyncCondEvents._set_event_orverride(event)
        event.clear = lambda: AsyncCondEvents._clear_event_orverride(event)

    @staticmethod
    def _set_event_orverride(event):
        """
        Function use when overriding set on an event.
        :param event: the event that is overwritten
        """
        for event_set in event._cond_event_original_sets:
            event_set()
        for change_callback in event._cond_event_original_change_callback:
            change_callback()

    @staticmethod
    def _clear_event_orverride(event):
        """
        Function use when overriding clear on an event.
        :param event: the event that is overwritten
        """
        for event_clear in event._cond_event_original_clears:
            event_clear()
        for change_callback in event._cond_event_original_change_callback:
            change_callback()
