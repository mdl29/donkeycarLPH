from donkeycar.parts.controller import Joystick, JoystickController

class MyJoystick(Joystick):
    '''
    Totally not a copy of the xbox one joystick (because the ps4 one doesn't work on ps4 controllers)
    '''
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)

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

class MyJoystickController(JoystickController):
    '''
    A Controller object that maps inputs to actions
    credit:
    https://github.com/Ezward/donkeypart_ps3_controller/blob/master/donkeypart_ps3_controller/part.py
    '''
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        '''
        attempt to init joystick
        '''
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def magnitude(self, reversed = False):
        def set_magnitude(axis_val):
            '''
            Maps raw axis values to magnitude.
            '''
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
        '''
        init set of mapping from buttons to function calls
        '''

        self.button_down_trigger_map = {
            'a_button': self.toggle_mode,
            'b_button': self.toggle_manual_recording,
            'x_button': self.erase_last_N_records,
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

