import websockets
import time
import asyncio


async def main():
    async for websocket in websockets.connect("ws://192.168.1.81:8000/workers/1/wsHeartbeat"):
        try:
            while True:
                async for message in websocket:
                    print('.')
                    time.sleep(2)
        except websockets.ConnectionClosed:
            continue


if __name__ == '__main__':
    asyncio.run(main())
