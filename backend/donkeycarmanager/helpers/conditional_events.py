from enum import Enum
from typing import List

from donkeycarmanager.helpers.registable_event import AsyncRegistableEvent


class AsyncCondEventsOperator(str, Enum):
    AND = "and"
    OR = "or"


class AsyncConditionalEvents(AsyncRegistableEvent):

    def __init__(self, events: List[AsyncRegistableEvent], operator: AsyncCondEventsOperator):
        super(AsyncConditionalEvents, self).__init__()

        self._events = events
        self._operator = operator

        self._is_inited = False

    async def _defer_init(self):
        """
        As __init__ can't be async, defer first check
        """
        if not self._is_inited:
            for event in self._events:
                await event.add_listener(self.on_event_changed)

            await self.on_event_changed(self)  # Set initial flag state
            self._is_inited = True

    async def _remove_listeners(self):
        for event in self._events:
            await event.remove_listener(self.on_event_changed)

    async def on_event_changed(self, event: AsyncRegistableEvent):
        """
        Hook run each times an event changes.
        :param event: event that is calling the hook
        """
        bools = [await e.is_set() for e in self._events]
        is_ok = False

        if self._operator == AsyncCondEventsOperator.AND:
            is_ok = all(bools)

        if self._operator == AsyncCondEventsOperator.OR:
            is_ok = any(bools)

        if is_ok:
            await self.set()

    async def wait(self):
        await self._defer_init()
        await super(AsyncConditionalEvents, self).wait()

    async def is_set(self) -> bool:
        await self._defer_init()
        return await super(AsyncConditionalEvents, self).is_set()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._remove_listeners()
