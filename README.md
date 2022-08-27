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
    - role: car-config # ntp service
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
* `car-config` : configuration of ntp server (needed for send models to paperspace vm)
* `shutdown-btn` : add scripts for the shutdown button ( see [documentation](doc/boutton/Boutton_poussoir.md) and [shematic](doc/schema/schema-electronique.png) )
* `ps4-controller` : installation of ds4drv and configuration for ps4 bluetooth controllers
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
