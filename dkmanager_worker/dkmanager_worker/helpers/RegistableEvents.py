from threading import Event, Lock
from typing import Callable, Set


class RegistableEvent(Event):
    """
    Enhanced threading.Event that can be hooked to listen on their changes.
    """

    def __init__(self):
        super(RegistableEvent, self).__init__()

        # Store all listeners that will be called at event change
        self._listeners: Set[Callable[[RegistableEvent], None]] = set()
        self._listeners_lock = Lock()  # Will be used to ensure listeners set thread safety

    def set(self):
        """
        Set the event and call all listeners. Notify them of the change.
        """
        res = super(RegistableEvent, self).set()

        with self._listeners_lock:
            for listener in self._listeners:
                listener(self)

        return res

    def add_listener(self, changeCallable: Callable[['RegistableEvent'], None]):
        """
        Add listener that will be triggered at each event change (set)
        :param changeCallable: Will be called with the current triggered event.
        """
        with self._listeners_lock:
            self._listeners.add(changeCallable)

    def remove_listener(self, changeCallable: Callable[['RegistableEvent'], None]):
        """
        Remove listener
        :param changeCallable: Listener to be removed.
        """
        with self._listeners_lock:
            self._listeners.discard(changeCallable)
