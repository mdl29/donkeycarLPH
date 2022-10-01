import os
import logging

from donkeycar.parts.controller import Joystick, JoystickController
from typing import NoReturn

logger = logging.getLogger(__name__)

RECORDING_BLINK_LED_ON = 0.04
RECORDING_BLINK_LED_OFF = 0.11

def write_to_controller(color_hex, led_on, led_off):
    w = open("/tmp/jsfw_fifo", "w")
    w.write(f'{{"led_color": "#{color_hex}", "flash": [{led_on}, {led_off}]}}')
    w.flush()
    w.close()

class MyJoystick(Joystick):
    """
    Totally not a copy of the xbox one joystick (because the ps4 one doesn't work on ps4 controllers)
    """
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)
        self._led_color = "FFFFFF" # default color
        controller_color_hex = os.getenv('CONTROLLER_LED_COLOR')
        if controller_color_hex:
            self._led_color = controller_color_hex
            write_to_controller(self._led_color, 0, 0)

        self.axis_names = {
            0x00 : 'left_stick_horz',
            0x01 : 'left_stick_vert',
            0x04 : 'right_stick_vert',
            0x03 : 'right_stick_horz',
            0x0a : 'left_trigger',
            0x09 : 'right_trigger',
            0x10 : 'dpad_horiz',
            0x11 : 'dpad_vert'
        }

        self.button_names = {
            0x130: 'a_button',
            0x133: 'b_button',
            0x131: 'x_button',
            0x134: 'y_button',
            0x13b: 'options',
            0x136: 'left_shoulder',
            0x137: 'right_shoulder',
        }

class MyJoystickController(JoystickController):
    """
    A Controller object that maps inputs to actions
    credit:
    https://github.com/Ezward/donkeypart_ps3_controller/blob/master/donkeypart_ps3_controller/part.py
    """
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)
        self.inverted = False
        self.state_x_button = False

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
    
    def set_axis_lh(self, axis_val):
        if self.inverted:
            self.set_steering(axis_val)
    def set_axis_lv(self, axis_val):
        if not self.inverted:
            self.set_throttle(axis_val)
    def set_axis_rh(self, axis_val):
        if not self.inverted:
            self.set_steering(axis_val)
    def set_axis_rv(self, axis_val):
        if self.inverted:
            self.set_throttle(axis_val)

    def invert_controls(self):
        self.inverted = not self.inverted

    def init_trigger_maps(self):
        """
        init set of mapping from buttons to function calls
        """

        self.button_down_trigger_map = {
            'a_button': self.invert_controls,
            #'b_button': self.toggle_manual_recording,
            'x_button': self.x_button_pressed,
            'y_button': self.emergency_stop,
            'right_shoulder': self.increase_max_throttle,
            'left_shoulder': self.decrease_max_throttle,
            'options': self.toggle_constant_throttle,
        }

        self.axis_trigger_map = {
            'left_stick_horz':  self.set_axis_lh,
            'left_stick_vert':  self.set_axis_lv,
            'right_stick_horz': self.set_axis_rh,
            'right_stick_vert': self.set_axis_rv,
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
            write_to_controller(self._led_color, RECORDING_BLINK_LED_ON, RECORDING_BLINK_LED_OFF)
        else:
            write_to_controller(self._led_color, 0, 0)

    def x_button_pressed(self):
        """
        X button was pressed, could be used for confirmation.
        """
        self.state_x_button = True

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
        o_angle, o_throttle, o_mode, o_recording = super(MyJoystickController, self).run_threaded(img_arr=img_arr, mode=mode, recording=recording)

        # Check for changes, doing it like this we don't need to understand the update logic
        controller_recording_after = self.recording
        # 4th element of the output tuple is the recording sent to other parts
        other_parts_recording_after = o_recording
        controller_recording_changed = controller_recording_before != controller_recording_after
        other_parts_recording_changed = other_parts_recording_before != other_parts_recording_after
        if controller_recording_changed or other_parts_recording_changed: # Internal or external mutation sate
            self._on_recording_change()

        o_x_pressed = self.state_x_button
        if o_x_pressed:
            self.state_x_button = False # resetting it for next turns

        return o_angle, o_throttle, o_mode, o_recording, o_x_pressed, self.inverted, self.throttle_scale
