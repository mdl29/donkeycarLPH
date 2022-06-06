import socket
import logging
import re
import sys
import subprocess
import time
from typing import NoReturn, List, Optional, Callable

L2CAP_PSM_HIDP_CTRL = 0x11
HIDP_TRANS_SET_REPORT = 0x50
HIDP_DATA_RTYPE_OUTPUT = 0x02


class PS4LEDControl:

    def __init__(self, addr: str = None):
        """
        Create the PS4LEDControl class.
        Will try to connect to the controller when needed.
        :param addr_fetcher: Callable that return the last connected device mac addr
        """
        self._ctl_sock: Optional[socket.socket]  = None  # will be initialized when needed if possible

        self._led = (0, 0, 0)
        self._led_flash = (0, 0) # To blink change this value, first is the time (in ms ??) the LED is on, second the time it's off
        self._led_flashing = False

        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)

    @classmethod
    def find_bluetooth_connected_devices(cls) -> List[str]:
        """
        Find all bluetooth connected devices and return their mac addresses.
        It simply uses hcitool and grep.
        """
        try:
            res = subprocess.check_output(["hcitool", "con"],
                                          stderr=subprocess.STDOUT) \
                .decode(sys.stdout.encoding)
        except subprocess.CalledProcessError:
            raise ConnectionError("'hcitool scan' returned error. Make sure "
                                  "your bluetooth device is powered up with "
                                  "'hciconfig hciX up'.")

        mac_re = re.compile(r'(?:[0-9a-fA-F]:?){12}')
        return re.findall(mac_re, res)

    def connect_to(self, addr: str) -> NoReturn:
        """
        Connect to a new device addr and update it with the current state.
        :param addr: Device mac address
        """
        self.logger.debug('connect_to %s', addr)

        if self._ctl_sock:
            self.logger.debug('Disconnected already opened controller socket')
            self.disconnect()

        try:
            self._ctl_sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET,
                                            socket.BTPROTO_L2CAP)
            self._ctl_sock.connect((addr, L2CAP_PSM_HIDP_CTRL))
            self._control()  # Apply last known state
        except:
            self.logger.warning('Connection to bluetooth controller %s failled, addr might be wrong', addr)
            self._ctl_sock = None

    def _control(self, **kwargs):
        self.control(led_red=self._led[0], led_green=self._led[1],
                     led_blue=self._led[2], flash_led1=self._led_flash[0],
                     flash_led2=self._led_flash[1], **kwargs)

    def control(self, big_rumble=0, small_rumble=0,
                led_red=0, led_green=0, led_blue=0,
                flash_led1=0, flash_led2=0):
        pkt = bytearray(77)
        pkt[0] = 128
        pkt[2] = 255
        offset = 2
        report_id = 0x11

        # Rumble
        pkt[offset+3] = min(small_rumble, 255)
        pkt[offset+4] = min(big_rumble, 255)

        # LED (red, green, blue)
        pkt[offset+5] = min(led_red, 255)
        pkt[offset+6] = min(led_green, 255)
        pkt[offset+7] = min(led_blue, 255)

        # Time to flash bright (255 = 2.5 seconds)
        pkt[offset+8] = min(flash_led1, 255)

        # Time to flash dark (255 = 2.5 seconds)
        pkt[offset+9] = min(flash_led2, 255)

        self.write_report(report_id, pkt)

    def write_report(self, report_id, data):
        hid = bytearray((HIDP_TRANS_SET_REPORT | HIDP_DATA_RTYPE_OUTPUT,
                         report_id))

        if self._ctl_sock:
            self._ctl_sock.sendall(hid + data)
        else:
            self.logger.warning('Trying to set controller LED state while not controller socket is initialized')
            self.logger.warning('Ensure that call to connect_to was are will be made')

    def set_led(self, red: int=0, green: int=0, blue: int=0) -> NoReturn:
        """Sets the LED color. Values are RGB between 0-255."""
        self._led = (red, green, blue)
        self._control()

    def set_led_hex(self, hex_color: str) -> NoReturn:
        """
        Set LED color using hex color code.
        :param hex_color: An hex color code
        """
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        self.set_led(red=rgb[0], green=rgb[1], blue=rgb[2])

    def start_led_flash(self, on, off):
        """Starts flashing the LED."""
        if not self._led_flashing:
            self._led_flash = (on, off)
            self._led_flashing = True
            self._control()

    def stop_led_flash(self):
        """Stops flashing the LED."""
        if self._led_flashing:
            self._led_flash = (0, 0)
            self._led_flashing = False
            # Call twice, once to stop flashing...
            self._control()
            # ...and once more to make sure the LED is on.
            self._control()

    def disconnect(self):
        if self._ctl_sock:
            try:
                self._ctl_sock.close()
            except:
                pass
            finally:
                self._ctl_sock = None

    def __del__(self):
        self.disconnect()