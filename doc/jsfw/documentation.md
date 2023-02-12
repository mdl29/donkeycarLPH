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
git checkout a4b69eb0a115e7fd862dd5e3bc20a3561ea9bcc6
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
