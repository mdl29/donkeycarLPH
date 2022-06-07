#!/usr/bin/env python3

""" Example of resolving a service with a known name """

import logging
import sys
import socket

from zeroconf import Zeroconf

TYPE = '_http._tcp.local.'
NAME = '_donkeycarmanager'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    zeroconf = Zeroconf()

    try:
        service = zeroconf.get_service_info(TYPE, NAME + '.' + TYPE)
        print(service)
        print(socket.inet_ntoa(service.addresses[0]))
    finally:
        zeroconf.close()
