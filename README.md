<div align="center">
<h1> donkeycar LPH </h1>

![repo-size](https://img.shields.io/github/repo-size/mdl29/donkeycarLPH?style=flat-square)
![contributor](https://img.shields.io/github/contributors/mdl29/donkeycarLPH?style=flat-square)
![commitActivity](https://img.shields.io/github/commit-activity/m/mdl29/donkeycarLPH?logo=github&style=flat-square)
![mainLanguage](https://img.shields.io/github/languages/top/mdl29/donkeycarLPH?color=yellow&style=flat-square)

### In this project we present you a solution to industrialize the production of donkeycar cars, allow to everyone to install easily donkeycar environnement. We have also added some tools like our manager to make publics demonstrations, races during events to allow public to drive, race and understand the process of machine learning
</div>
<br>

 > 💡 A fork of the original [donkeycar project](https://github.com/autorope/donkeycar)
 
 <br>

<details>	
  <summary><b> 🚀 How to use our project</b></summary>
    
## 🧪 Create your ansible recipe

*** 

First you should create your own recipe book with your wanted recipes. Indeed, ansible have a configuration file where we specifie what options ( recipe ) we want, so you have to modifie the [donkeycar.yml](ansible/donkeycar.yml) file and comments recipe who you don't want

```yml
 roles:
    - role: raspi-config #rasperry pi configuration role
      become: yes # This role need root privileges
    - role: car-config # car configurations (ntp, hostname, ds4drv...)
      become: yes # This role need root privileges
    - role: shutdown-btn # shutdown button service
      become: yes # This role need root privileges
    - role: ps4-controller # install and configure ds4drv
      become: no # This role no need root privileges
    - role: openCV # Install openCV (optional)
      become: yes # This role need root privileges
    - role: donkeycar # Donkeycar installation 
      become: no # This role doesn't need root privileges
    - role: mycar # create car with configurations
      become: no # This role no need root privileges
    - role: IR-lap-timer # install dependencies for take charge IR counter
      become: yes # This role need root privileges
```
> 📒 [ansible/donkeycar.yml](ansible/donkeycar.yml) preview

* `raspi-config` : defaults installations like wifi credentials, ssh ...
* `car-config` : car configurations (ntp, hostname, ds4drv...)
* `shutdown-btn` : add scripts for the shutdown button ( see [documentation](doc/boutton/Boutton_poussoir.md) and [shematic](doc/schema/schema-electronique.png) )
* `ps4-controller` : installation of ds4drv and configuration for ps4 bluetooth controllers
* `openCV` : install openCV according to donkeycar documentation
* `donkeycar` : install [donkeycar project](https://github.com/autorope/donkeycar) and his requirements 
* `mycar` : create mycar folder with its files
* `IR-lap-timer` : Infrared installation and configuration

**Don't comment obligatory recipes (raspi-config, car-config, donkeycar, mycar ), this action can avoid the proper functioning of installations or configurations**

## ⚙️ Modifie default car configurations

***

- modifie configuration for single car

  Before launch your recipe, you should modifie config var with your configurations like `wpa_suplicant`, donkeycar sterring and throttle configuration
  > 📒 [ansible/group_vars/all](ansible/group_vars/all)

- modifie configuration for multiple cars with the same image

  You can choice configuration for multiples cars. For example we made this in our repo for our 4 cars ( see [ansible/config](ansible/config)).
  For make this, first you should specifie car folder with its mac address :
  > 📒 [ansible/config/hostnames](ansible/config/hostnames)
  ```text
  e4:5f:01:68:17:2c	exampleCar
  ```
  afterwards, just create a folder with the car name at `ansible/config`. For our example we should create exampleCar folder at `ansible/config/exampleCar`.

  In this folder we should to create two file :
   - `ds4drv.env` --> ps4 controller color
   - `myconfig.py` --> donkeycar myconfig

   example :
   > 📒 [ansible/config/dababycar/ds4drv.env](ansible/config/dababycar/ds4drv.env)
   ```env
  CONTROLLER_LED_COLOR=A103FC
   ```
  
  > 📒 [ansible/config/dababycar/myconfig.py](ansible/config/dababycar/myconfig.py)
   ```python
  DRIVE_TRAIN_TYPE = "PIGPIO_PWM" # SERVO_ESC|DC_STEER_THROTTLE|DC_TWO_WHEEL|SERVO_HBRIDGE_PWM|PIGPIO_PWM|MM1|MOCK

  STEERING_CHANNEL = 12           #channel on the 9685 pwm board 0-15
  STEERING_LEFT_PWM = 739         #pwm value for full left steering
  STEERING_RIGHT_PWM = 400        #pwm value for full right steering
  
  STEERING_PWM_PIN = 12           #Pin numbering according to Broadcom numbers
  STEERING_PWM_FREQ = 75          #Frequency for PWM
  STEERING_PWM_INVERTED = False   #If PWM needs to be inverted

  THROTTLE_CHANNEL = 13           #channel on the 9685 pwm board 0-15
  THROTTLE_FORWARD_PWM = 575      #pwm value for max forward throttle max 750
  THROTTLE_STOPPED_PWM = 470      #pwm value for no movement
  THROTTLE_REVERSE_PWM = 400      #pwm value for max reverse throttle

  THROTTLE_PWM_PIN = 13           #Pin numbering according to Broadcom numbers
  THROTTLE_PWM_FREQ = 75          #Frequency for PWM
  THROTTLE_PWM_INVERTED = False   #If PWM needs to be inverted

  AUTO_RECORD_ON_THROTTLE = False #if true, we will record whenever throttle is not zero. if false, you must manually toggle recording with some other trigger. Usually circle button on joystick.
  CONTROLLER_TYPE='custom' # Set the controller to be used to be our custom one ()

  LOGGING_LEVEL='DEBUG'
  ```

## 🚀 Launch ansible recipe

***

After have create your ansible playbook, you can launch it with these two options :
- install it by ssh but you should configure manually internet, ssh and install ansible on your raspberry pi. Follow this [tutorial](ansible/README.md)
- generate your raspian image with donkeycar installed, follow this [tutorial](packer/README.md)

  <br/>	
</details>

<details>	
  <summary><b>✨ Our features</b></summary>
  <br/>	
 
## Software 

***

### Ansible remote installation documentation : 
  > we have made a ansible book for automate our donleycar and raspberry pi installation remotely (ssh).
    Indeed, these recipes allow us to have one single clean installation and be able to repeat it to infinity. <br>
    <b>ℹ️ Read [documentation](ansible/README.md) !! </b>

### Generate raspian image with donkeycar installation :
 > With ansible and packer, we can also generate a raspian image with our donkeycar installation. This feature is very usefull if we want to share it with people and don't use ssh. <br>
 <b>ℹ️ Read [documentation](ansible/README.md) !! </b>

### Generate raspian image with donkeycar installation :
 > With ansible and packer, we can also generate a raspian image with our donkeycar installation. This feature is very usefull if we want to share it with people and don't use ssh. <br>
 <b>ℹ️ Read [documentation](packer/README.md) !! </b>

### Donkeycar manager :
 > We have created a donkeycar manager. This manager is separated in to parts : a backend ( with database, api ...) and a frontend ( vuejs 2), it allow us to see cars who running, stopped, manage players who race... <br>
 <b>ℹ️ For more informations about how it works, you can see our documentation [here](doc/donkeycarManager/manager-features.md)</b>

## Hardware 

***

<br>

### Our shematic : 

![Fichier Fritzing](doc/schema/schema-electronique.png)

### Shutdown button :
> we have made a shutdown button, for shutdown car manually because when ssh crash we can't make a clean shutdown and we risk to damage the SD card

### Led indicator :
 > This led indcator allow us to know if the car is up or not. If the led is up, the car working.


## 3D designs 

***

### Anti-theft for ps4 controllers :
 >ℹ️ see [documentation](3dDesigns/car-chassis/README.md)

### Camera cap holder :
>ℹ️ see [documentation](3dDesigns/camera-cover/README.md)
