# JSFW documentation :

## How install it : 

> clone github repository :
```bash
git clone https://github.com/viandoxdev/jsfw.git
```
> Go to jsfw directory :
```bash
cd jsfw
```
> Go to the good commit 
```bash
git checkout 749c8f6c01ec891fa344cf532e686ca7b44cad96
```
> Build jsfw executable :
```bash
make
```
## How use it :

> You may need to run jsfw as root, or use the udev rules in 50-donkeycar.rules

If you are the jsfw server centralizing all PS4 controllers, run this command to launch it (specify the path to the config in this directory relative to where you built jsfw):
> The port used in donkeycar manager is 7776
```bash
./jsfw server 7776 <path to jsfw/server.json>
```
