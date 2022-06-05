DRIVE_TRAIN_TYPE = "PIGPIO_PWM" # SERVO_ESC|DC_STEER_THROTTLE|DC_TWO_WHEEL|SERVO_HBRIDGE_PWM|PIGPIO_PWM|MM1|MOCK

STEERING_CHANNEL = 12           #channel on the 9685 pwm board 0-15
STEERING_LEFT_PWM = 740         #pwm value for full left steering
STEERING_RIGHT_PWM = 400        #pwm value for full right steering
 
STEERING_PWM_PIN = 12           #Pin numbering according to Broadcom numbers
STEERING_PWM_FREQ = 75          #Frequency for PWM
STEERING_PWM_INVERTED = False   #If PWM needs to be inverted

THROTTLE_CHANNEL = 13           #channel on the 9685 pwm board 0-15
THROTTLE_FORWARD_PWM = 750      #pwm value for max forward throttle
THROTTLE_STOPPED_PWM = 470      #pwm value for no movement
THROTTLE_REVERSE_PWM = 370      #pwm value for max reverse throttle

THROTTLE_PWM_PIN = 13           #Pin numbering according to Broadcom numbers
THROTTLE_PWM_FREQ = 75          #Frequency for PWM
THROTTLE_PWM_INVERTED = False   #If PWM needs to be inverted

AUTO_RECORD_ON_THROTTLE = False #if true, we will record whenever throttle is not zero. if false, you must manually toggle recording with some other trigger. Usually circle button on joystick.
CONTROLLER_TYPE='custom' # Set the controller to be used to be our custom one ()

LOGGING_LEVEL='DEBUG'