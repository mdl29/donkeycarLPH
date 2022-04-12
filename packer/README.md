# Building custom DonkeyCar Image

## Install packer

* Follow the procedure at : https://www.packer.io/downloads
* Check that you have the command `packer` in a terminal

For developers :
* install HCL support extension : https://marketplace.visualstudio.com/items?itemName=wholroyd.HCL


## Building the image

Packer ARM plugin need root privileges to run. To build the images use the following commands :
```bash
sudo packer init .
sudo packer build donkeycar.pkr.hcl
```

Then grab some ☕️☕️☕️

## Testing the image on a raspberry pi

Simply dd the image present in `output-raspbian/image` onto your raspberry pi :
```bash
$ lsblk # Find your raspbery pi device name
...
sde      8:64   1  29,1G  0 disk 
├─sde1   8:65   1   256M  0 part /media/benjamin/boot
└─sde2   8:66   1  28,9G  0 part /media/benjamin/rootfs
# For me it's /dev/sde, 30 GB sd card
$ sudo dd if=output-raspbian/image bs=4M of=/dev/sde status=progress && sync
```

# Current issue
We didn't manage to use packer Ansible-remote (due to this issue [packer-builder-arm#169](https://github.com/mkaczanowski/packer-builder-arm/issues/169), so we need to install ansible on the raspberry pi it self.