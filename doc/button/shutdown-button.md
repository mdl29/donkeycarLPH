# Shutdown button for donkeycar
 
> 🇫🇷 **You can read this documentation in [french](doc/button/Boutton_poussoir.md)**

Method of use for installing and using a push button to turn off a donkeycar

> ⚠️ If you using our raspberry pi image generate by ansible and packer. All software requirements are already installed and configured on your car.
You should just follow our [electronic shematic](doc/schema/schema-electronique.png) for install it 

## Install requirements :

install Wiring Pi
```
# apt-get install wiringpi
```

## Create script bash :
Create `pin-shutdown.sh` file at `/root` folder
```
# nano /root/pin-shutdown.sh
```
In this file you should add those lines :
```bash
#!/bin/bash

pin=29  # pin 40 (internal: 21) on raspi layout
gpio mode $pin in
gpio wfi $pin both
logger Shutdown button pressed
shutdown -h now
```

Save the file, afterward make it executable with chmod +x
```
# chmod +x /root/pin-shutdown.sh
```

## Create systemd service

You must now create a service so that at startup, the script is launched in the background, so that it can detect the push button at any time.

First, we need to create our service file. 
```
# touch /etc/systemd/system/button-shutdown.service
```
and write in it :
```bash
[Unit]
Description=button shutdown service

[Service]
ExecStart=/root/pin-shutdown.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Launch service

First, we need to update the systemctl services to add ours:
```
# systemctl daemon-reload 
```
Then, we activate the service so that the script is launched at each start:
```
# systemctl enable button-shutdown.service 
```
If you do not want to restart your computer, you can start the service now:
```
# systemctl start button-shutdown.service 
```
Finally, to make sure your service is running:
```
# systemctl status button-shutdown.service
```