
from donkeycar.parts.controller import Joystick, JoystickController


class MyJoystick(Joystick):
    #An interface to a physical joystick available at /dev/input/js0
    def __init__(self, *args, **kwargs):
        super(MyJoystick, self).__init__(*args, **kwargs)

            
        self.button_names = {
            0x132 : 'circle',
            0x131 : 'cross',
            0x130 : 'square',
            0x133 : 'triangle',
            0x13c : 'ps4',
            0x139 : 'option',
            0x138 : 'share',
            0x135 : 'R1',
            0x134 : 'L1',
            0x136 : 'L2',
            0x137 : 'R2',
            0x13a : 'JSLC',
        }


        self.axis_names = {
            0x00 : 'left_stick_horz',
            0x01 : 'left_stick_vert',
            0x5 : 'right_stick_vert',
            0x2 : 'right_stick_horz',
        }



class MyJoystickController(JoystickController):
    #A Controller object that maps inputs to actions
    def __init__(self, *args, **kwargs):
        super(MyJoystickController, self).__init__(*args, **kwargs)


    def init_js(self):
        #attempt to init joystick
        try:
            self.js = MyJoystick(self.dev_fn)
            self.js.init()
        except FileNotFoundError:
            print(self.dev_fn, "not found.")
            self.js = None
        return self.js is not None


    def init_trigger_maps(self):
        #init set of mapping from buttons to function calls
            
        self.button_down_trigger_map = {
            'cross' : self.toggle_mode,
            'triangle' : self.erase_last_N_records,
            'L2' : self.emergency_stop,
            'L1' : self.increase_max_throttle,
            'R1' : self.decrease_max_throttle,
            'circle' : self.toggle_manual_recording,
            'R2' : self.toggle_constant_throttle,
        }


        self.axis_trigger_map = {
            'left_stick_horz' : self.set_steering,
            'right_stick_vert' : self.set_throttle,
        }


