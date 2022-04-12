
# Donkey Car Ansible installation book for raspbery pi

This book can be used in 2 different ways :

* deploy it on a running raspberry pi thought SSH, your raspberry pi needs internet access and should be connected to the same network as your host computer
* build a raspbian image based on this book, you should then take a look at our [packer instructions](../README.md)

## Deploys book on a booted raspberry pi

### Requirements

Install Ansible :
```
python3 -m venv venv
source venv/bin/activate
pip install Ansible
```

Install sshpass as we will use ssh with user/password access :
```bash
sudo apt-get install sshpass
```

Flash raspbian on your raspberry pi SD card :
```bash
cd /tmp
curl https://downloads.raspberrypi.org/raspios_oldstable_lite_armhf/images/raspios_oldstable_lite_armhf-2021-12-02/2021-12-02-raspios-buster-armhf-lite.zip -o 2021-12-02-raspios-buster-armhf-lite.zip
unzip 2021-12-02-raspios-buster-armhf-lite.zip
# Find your DEVICE_NAME
lsblk #
export DEVICE_NAME=/dev/YOUR_DEVICE_NAME
sudo dd if=2021-12-02-raspios-buster-armhf-lite.img of=$DEVICE_NAME bs=4MB status=progress && sync
```

Enable SSH, re-insert the SD card on your computeur go to the /boot partition and create `ssh` file :
```bash
touch ssh
```

Insert your SD card on the raspberry pi, plugin ethernet connexion, wait for 2-3 min (as the raspberry pi reboot at first startup to expend it's partition). Then try to reach it using :
```bash
ping raspberrypi.local
```

### Play book on the booted raspberry pi

Frist ensure you don't have any existing key fingerprint associated to `raspberrypi.local`, remove then using :
```bash
ssh-keygen -f ~/.ssh/known_hosts -R "raspberrypi.local"
```

Use the following command inside this folder and in your virtualenv, we will ping the `dev` inventory :
```bash
$ ansible dev -i hosts -m ping
raspberrypi.local | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```

Run the book :
```bash
ansible-playbook -i hosts -l dev donkeycar.yml
```

### Play book on multiple raspberry pi / donkeycars at the same time

Take a look as the `hosts` file, reference all your raspberry pi IPs or hostnames in the `[cars]` section. Then run :
```
ansible-playbook -i hosts -l cars donkeycar.yml
```