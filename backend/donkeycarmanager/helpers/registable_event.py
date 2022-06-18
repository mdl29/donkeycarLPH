from asyncio import Event, Lock
from typing import Callable, Set


class AsyncRegistableEvent(Event):
    """
    Enhanced threading.Event that can be hooked to listen on their changes.
    """

    def __init__(self):
        super(AsyncRegistableEvent, self).__init__()

        # Store all listeners that will be called at event change
        self._listeners: Set[Callable[[AsyncRegistableEvent], None]] = set()
        self._listeners_lock = Lock()  # Will be used to ensure listeners set thread safety

    async def set(self):
        """
        Set the event and call all listeners. Notify them of the change.
        """
        res = super(AsyncRegistableEvent, self).set()

        async with self._listeners_lock:
            for listener in self._listeners:
                await listener(self)

        return res

    async def is_set(self) -> bool:
        """
        Needs to be await as it is await in AsyncConditionalEvents.
        """
        return super(AsyncRegistableEvent, self).is_set()

    async def add_listener(self, changeCallable: Callable[['AsyncRegistableEvent'], None]):
        """
        Add listener that will be triggered at each event change (set)
        :param changeCallable: Will be called with the current triggered event.
        """
        async with self._listeners_lock:
            self._listeners.add(changeCallable)

    async def remove_listener(self, changeCallable: Callable[['AsyncRegistableEvent'], None]):
        """
        Remove listener
        :param changeCallable: Listener to be removed.
        """
        async with self._listeners_lock:
            self._listeners.discard(changeCallable)
