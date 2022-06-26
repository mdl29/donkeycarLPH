import os
import logging

from donkeycar.parts.controller import Joystick, JoystickController
from typing import NoReturn

from custom.PS4_led_control import PS4LEDControl
from custom.ds4drv_last_mac_reader import Ds4drvLastMacReader

logger = logging.getLogger(__name__)

RECORDING_BLINK_LED_ON = 10 # 100ms on, 100ms off
RECORDING_BLINK_LED_OFF = 30 # 100ms on, 100ms off

DEVICES_PIPE = "/tmp/ds4drv-device.pipe"
DEVICES_LAST_ADDR = "/tmp/ds4drv-device.lastaddr"


class MyJoystick(Joystick):
    """
    Totally not a copy of the xbox one joystick (because the ps4 one doesn't work on ps4 controllers)
    """
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)

        self._led_control = PS4LEDControl()
        self._ds4drv_mac_reader = Ds4drvLastMacReader(devices_pipe_path=DEVICES_PIPE,
                                                      on_new_mac_addr=self._led_control.connect_to,
                                                      last_device_addr_file=DEVICES_LAST_ADDR)
        self._ds4drv_mac_reader.start()
        # self._led_control.set_led(0, 255, 0)  # Will be set when mac addr is known
        controller_color_hex = os.getenv('CONTROLLER_LED_COLOR')
        if controller_color_hex:
            self._led_control.set_led_hex(controller_color_hex)

        self.axis_names = {
            0x00 : 'left_stick_horz',
            0x01 : 'left_stick_vert',
            0x05 : 'right_stick_vert',
            0x02 : 'right_stick_horz',
            0x0a : 'left_trigger',
            0x09 : 'right_trigger',
            0x10 : 'dpad_horiz',
            0x11 : 'dpad_vert'
        }

        self.button_names = {
            0x130: 'a_button',
            0x131: 'b_button',
            0x133: 'x_button',
            0x134: 'y_button',
            0x13b: 'options',
            0x136: 'left_shoulder',
            0x137: 'right_shoulder',
        }

    def __del__(self):
        """
        Clearly disconnect.
        """
        if self._led_control is not None:
            self._led_control.disconnect()


class MyJoystickController(JoystickController):
    """
    A Controller object that maps inputs to actions
    credit:
    https://github.com/Ezward/donkeypart_ps3_controller/blob/master/donkeypart_ps3_controller/part.py
    """
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        """
        attempt to init joystick
        """
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def magnitude(self, reversed = False):
        def set_magnitude(axis_val):
            """
            Maps raw axis values to magnitude.
            """
            # Axis values range from -1. to 1.
            minimum = -1.
            maximum = 1.
            # Magnitude is now normalized in the range of 0 - 1.
            magnitude = (axis_val - minimum) / (maximum - minimum)
            if reversed:
                magnitude *= -1
            self.set_throttle(magnitude)
        return set_magnitude


    def init_trigger_maps(self):
        """
        init set of mapping from buttons to function calls
        """

        self.button_down_trigger_map = {
            #'a_button': self.toggle_mode,
            #'b_button': self.toggle_manual_recording,
            #'x_button': self.erase_last_N_records,
            'y_button': self.emergency_stop,
            'right_shoulder': self.increase_max_throttle,
            'left_shoulder': self.decrease_max_throttle,
            'options': self.toggle_constant_throttle,
        }

        self.axis_trigger_map = {
            'left_stick_horz': self.set_steering,
            'right_stick_vert': self.set_throttle,
            # Forza Mode
            'right_trigger': self.magnitude(),
            'left_trigger': self.magnitude(reversed = True),
        }

    def _on_recording_change(self) -> NoReturn:
        """
        Run when recording state changes, add here all stuff you want to update.
        """
        self._update_led_recording_sate()

    def _update_led_recording_sate(self) -> NoReturn:
        """
        Update LED recording state, run when recording change.
        """
        if self.recording:
            self.js._led_control.start_led_flash(RECORDING_BLINK_LED_ON, RECORDING_BLINK_LED_OFF)
        else:
            self.js._led_control.stop_led_flash()

    def run_threaded(self, img_arr=None, mode=None, recording=None, manager_job_name = None):
        """
        :param img_arr: current camera image or None
        :param mode: default user/mode
        :param recording: default recording mode
        """
        # Saving some internal states to know if they will change
        controller_recording_before = self.recording
        other_parts_recording_before = recording

        # Update I/O
        outputs = super(MyJoystickController, self).run_threaded(img_arr=img_arr, mode=mode, recording=recording)

        # Check for changes, doing it like this we don't need to understand the update logic
        controller_recording_after = self.recording
        # 4th element of the output tuple is the recording sent to other parts
        other_parts_recording_after = outputs[3]
        controller_recording_changed = controller_recording_before != controller_recording_after
        other_parts_recording_changed = other_parts_recording_before != other_parts_recording_after
        if controller_recording_changed or other_parts_recording_changed: # Internal or external mutation sate
            self._on_recording_change()

        return outputs
