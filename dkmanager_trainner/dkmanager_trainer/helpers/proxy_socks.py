import socket
import logging
from typing import NoReturn

import socks


def set_sock_proxy(host: str, port: int) -> NoReturn:
    """
    Set socks proxy.
    :param host:
    :param port:
    """
    logger = logging.getLogger(__name__ + ".set_sock_proxy")
    socks.set_default_proxy(socks.SOCKS5, host, port)
    socket.socket = socks.socksocket

    logger.debug('Proxy socks setted for all connexing using host: %s, port: %i', host, port)

