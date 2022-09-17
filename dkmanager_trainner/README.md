# IA Trainer

DonkeyCarManager AI Trainer, you should use a machine having GPU for it. In our event we used virtual machines
from paperspace to train the model.

## Install

```bash
# Workaround for dkmanager_worker dependency : 
pip install -e "git+https://github.com/mdl29/donkeycarLPH.git@159_training#egg=dev&subdirectory=dkmanager_worker"

# Install it 
python setup.py install
```

## Run it

### Locally

```bash
# TODO
```

### Remotely (on paperspace)

To run it on paperspace virtual machine as the trainer is a worker and needs access to the manager (Rest API and FTP),
we will be using a remote SSH tunnelling from the machine running the manager.

On the machine running the manager :
```bash
VM_IP=$1
ssh -o "StrictHostKeyChecking=no" paperspace@$VM_IP -R6666
```
The last command will open port `6666` on the paperspace machine that can be used as a sock proxy to access the manager.

Start the service 