import time
import asyncio
import threading
import websockets
from .schemas import Worker
from urllib.parse import urlparse

class WorkerHeartBeat(threading.Thread):

    def __init__(self, api_origin: str, worker: Worker):
        """
        :param api_origin: API location, eg: http://192.168.1.81:8000
        :param worker: The current worker.
        """
        super(WorkerHeartBeat, self).__init__()
        self.daemon = True

        self.worker = worker
        parsed_uri = urlparse(api_origin)
        self.ws_url = f"ws://{parsed_uri.hostname}:{parsed_uri.port}/workers/{self.worker.worker_id}/wsHeartbeat"

    async def heartbeat_loop(self):
        """
        Async loop used to maintain socket activity.
        :return:
        """
        async for websocket in websockets.connect(self.ws_url):
            try:
                while True:
                    async for message in websocket:
                        time.sleep(2)
            except websockets.ConnectionClosed:
                continue

    def run(self):
        asyncio.run(self.heartbeat_loop())
