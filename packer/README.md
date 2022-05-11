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
sudo packer build -on-error=abort donkeycar.pkr.hcl # Using on-error abort to keep the image if error occured
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
$ export DEVICE_NAME=/dev/sde # Adapt this line
$ sudo dd if=output-raspbian/image bs=4M of=$DEVICE_NAME status=progress && sync
```

## Mounting an image

To mount an image and read / write to it without having to write to it a physical drive first, you can use `losetup`:

To add the device
```
# losetup -Pf <image>
```

The image's 'drives' will then be of the form `/dev/loopX` (`/dev/loopXpY` for partitions).
(ex)
```
$ lsblk
NAME         MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
loop0          7:0    0   7.6G  0 loop 
├─loop0p1    259:13   0   256M  0 part
└─loop0p2    259:14   0   7.4G  0 part 
```

You can then mount these to any path on the computer.

To remove the device, first make sure to unmount the partitions
```
# umount /dev/loopXp0
# umount /dev/loopXp1
...
```

Then detach it using losetup
```
# losetup -d /dev/loopX
```

# Current issue
We didn't manage to use packer Ansible-remote (due to this issue [packer-builder-arm#169](https://github.com/mkaczanowski/packer-builder-arm/issues/169), so we need to install ansible on the raspberry pi it self.
