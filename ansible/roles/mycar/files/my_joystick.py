import os
import logging
from time import sleep

from donkeycar.parts.controller import Joystick, JoystickController
from typing import NoReturn

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RECORDING_BLINK_LED_ON = 0.04
RECORDING_BLINK_LED_OFF = 0.11

def write_to_controller(color_hex, led_on, led_off):
    w = open("/tmp/jsfw_fifo", "w")
    w.write(f'{{"index": 0, "led_color": "#{color_hex}", "flash": [{led_on}, {led_off}]}}')
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

        self.initialized = False

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
            0x134: 'a_button',
            0x131: 'b_button',
            0x130: 'x_button',
            0x133: 'y_button',
            0x13a: 'share',
            0x13b: 'options',
            0x138: 'left_shoulder',
            0x139: 'right_shoulder',
            0x137: 'R1',
            0x136: 'L1',
        }

    def init(self):
        self.initialized = super().init()

    def cleanup(self):
        if self.initialized:
            self.jsdev.close()
            self.initialized = False

    def poll(self):
        button, button_state, axis, axis_val = super().poll()
        if button is not None and button_state != 0:
            button_state = 1
        return button, button_state, axis, axis_val

class MyJoystickController(JoystickController):
    """
    A Controller object that maps inputs to actions
    credit:
    https://github.com/Ezward/donkeypart_ps3_controller/blob/master/donkeypart_ps3_controller/part.py
    """
    def __init__(self, *args, **kwargs):
        self.easy_drive_mode = False
        self.inverted = False
        super(MyJoystickController, self).__init__(*args, **kwargs)
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
            self.js.initialized = False
        return self.js.initialized


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
    
    def invert_controls(self):
        self.inverted = not self.inverted
        self.init_trigger_maps()

    
    def go_easy_mode(self):
        self.easy_drive_mode = not self.easy_drive_mode
        self.init_trigger_maps()
        
    def backward_throttle(self):
        self.set_throttle(-1)
    
    def forward_throttle(self):
        self.set_throttle(1)
    
    def throttle_stop(self):
        self.set_throttle(0)

    def init_trigger_maps(self):
        """
        init set of mapping from buttons to function calls
        """

        self.button_down_trigger_map = {
            'b_button': self.go_easy_mode,
            'a_button': self.invert_controls,
            'x_button': self.x_button_pressed,
            'y_button': self.emergency_stop,
            'right_shoulder': self.increase_max_throttle,
            'left_shoulder': self.decrease_max_throttle,
            'options': self.toggle_constant_throttle,
        }

        self.button_up_trigger_map = { }

        self.axis_trigger_map = {
            'left_stick_horz':  self.set_steering,
            'right_stick_vert': self.set_throttle,
            # Forza Mode
            'right_trigger': self.magnitude(),
            'left_trigger': self.magnitude(reversed = True),
        }

        if self.easy_drive_mode: 

            self.button_down_trigger_map = {
                **self.button_down_trigger_map,
                'right_shoulder': self.backward_throttle,
                'left_shoulder': self.forward_throttle,
                "R1" : self.increase_max_throttle,
                "L1" : self.decrease_max_throttle,
            }
            
            self.button_up_trigger_map = {
                **self.button_up_trigger_map,
                'right_shoulder': self.throttle_stop,
                'left_shoulder': self.throttle_stop,
            }

            self.axis_trigger_map = {
                **self.axis_trigger_map,
                'right_trigger': self.magnitude(),
                'left_trigger': self.magnitude(reversed = True),
            }
        
            del self.axis_trigger_map['right_stick_vert']

        elif self.inverted : 

            self.axis_trigger_map = {
                **self.axis_trigger_map,
                'left_stick_vert':  self.set_throttle,
                'right_stick_horz': self.set_steering,
            }

            del self.axis_trigger_map['right_stick_vert']
            del self.axis_trigger_map['left_stick_horz']

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
            write_to_controller(self.js._led_color, RECORDING_BLINK_LED_ON, RECORDING_BLINK_LED_OFF)
        else:
            write_to_controller(self.js._led_color, 0, 0)

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

    def update(self):
        while True:
            if self.js is None:
                self.js = MyJoystick(self.dev_fn)

            # init_js is called by super on update
            while not self.js.initialized:
                self.js.init()

                if self.js.initialized: # Ensure color is up to date
                    self._update_led_recording_sate()

                sleep(2)

            if self.js is not None and self.js.initialized: # Otherwise super.update wait infinitly
                try:
                    super().update()
                except OSError:
                    logger.info("Lost joystick")
                    self.js.cleanup()


