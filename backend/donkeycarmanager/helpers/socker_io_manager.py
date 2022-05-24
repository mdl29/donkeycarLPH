import socketio
from typing import Union

from fastapi import FastAPI


class SocketIOManager:
    """
    Build the socket IO manager instance.
    Injected as get_sm from main.
    """

    def __init__(self,
                cors_allowed_origins: Union[str, list] = '*',
                async_mode: str = "asgi",
                mount_location: str = "/ws",
                socketio_path: str = "socket.io"
                ):
        """
        Init the socket IO server.
        Default mount location for SocketIO app is at `/ws`
        and defautl SocketIO path is `socket.io`.
        (e.g. full path: `ws://www.example.com/ws/socket.io/)

        :param socketio_path:
        :param cors_allowed_origins:
        :param async_mode:
        :param mount_location: Root path the the websocket.
        :param socketio_path: Socket IO path under the mount_location
        :return:
        """
        self._sio = socketio.AsyncServer(async_mode=async_mode, cors_allowed_origins=cors_allowed_origins)
        self._app = socketio.ASGIApp(
            socketio_server=self._sio, socketio_path=socketio_path
        )
        self._mount_location = mount_location

    def mount(self,
              fast_api_app: FastAPI) -> None:
        """
        Mount the socket application to the FastAPI app.

        :param app: FastAPI app.
        """
        fast_api_app.mount(self._mount_location, self._app)

    def getSocketIO(self) -> socketio.AsyncServer:
        """
        :return: The socket IO instance
        """
        return self._sio
