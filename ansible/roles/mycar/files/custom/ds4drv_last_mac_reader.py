import os, sys
import threading
import time
from typing import Callable, NoReturn, TextIO, Optional
import logging


class Ds4drvLastMacReader(threading.Thread):

    def __init__(self, devices_pipe_path: str,
                 on_new_mac_addr: Callable[[str], NoReturn],
                 last_device_addr_file: Optional[str]):
        """
        :param last_device_addr_file: Read first mac addr from this file if specified, and trigger on_new_mac_addr.
        :param devices_pipe_path: File path to ds4drv fifo pipe file.
        :param on_new_mac_addr: Event that will be trigger with the new mac_addr
                                Each time a new address is read
        """
        super(Ds4drvLastMacReader, self).__init__()

        self._last_device_addr_file = last_device_addr_file
        self._devices_pipe_path = devices_pipe_path
        self._on_new_mac_addr = on_new_mac_addr

        self._running = False
        self._ds4drv_fifo: Optional[TextIO] = None

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

        self.read_first_mac()

    def read_first_mac(self) -> NoReturn:
        """
        Read mac address form last mac address file if specified at init.
        Might trigger the event if a mac addr is found.
        """
        if self._last_device_addr_file:
            with open(self._last_device_addr_file, 'r', encoding='utf-8') as f:
                mac_addr = f.readline()
                self._on_new_mac_addr(mac_addr)

    def read_until_line_break_or_stop(self, file: TextIO) -> Optional[str]:
        """
        Read until line end and return line, or stop if self._running is false
        :param file: Opened file to read
        :return: The first line read or None if there is nothing to read
        """
        line = ""
        while self._running:
            r = file.read(1)

            if len(r) == 0:
                return None

            if r == "\n":
                return line
            else:
                line += r

    def run(self) -> NoReturn:
        """
        Run until .stop() is called.
        """
        self._running = True

        while self._running:
            try:
                self._ds4drv_fifo = open(self._devices_pipe_path, "r", encoding='utf-8')

                while self._running:
                    mac_addr = self.read_until_line_break_or_stop(file=self._ds4drv_fifo)

                    if mac_addr is not None:
                        self.logger.info("Read new mac addr : %s, executing event", mac_addr)
                        self._on_new_mac_addr(mac_addr)

            except Exception as e:
                self.logger.error("Failled to open file %s .. retry in 2sec", self._devices_pipe_path)
                self.logger.error(e)
                time.sleep(2)

    def stop(self) -> NoReturn:
        """
        Stop the thread when it can.
        """
        self._running = False
        self._ds4drv_fifo.close()
