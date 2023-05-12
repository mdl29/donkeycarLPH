# JSFW documentation

## Installation

> clone the repository
```bash
git clone https://github.com/viandoxdev/jsfw.git
```
> Go to jsfw directory
```bash
cd jsfw
```
> Checkout the correct version
```bash
git checkout 6f76aef7976ec472566a4dc6a60fa25742161288
```
> Build the binary
```bash
make jsfw
```
## Usage

> You may need to run jsfw as root, or use the udev rules in 50-donkeycar.rules

The jsfw server should run on the same computer as the donkeycar backend (this can be changed by editing the ip used in the jsfw.service file), and all controllers should be plugged in that computer as well. To start it:

```bash
./jsfw server 7776 <path to jsfw/server.json>
```
