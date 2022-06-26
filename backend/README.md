# Donkey Car Manager

A tool to manage multiple donkeycars.

## Install

Create a python3.6 (at least), virtual env :
```
python3 -m venv venv
source venv/bin/activate
```

Install donkeycarmanager :
```
python setup.py install
```

## Starting the server

Starting postgres database :
```
 export SERVER_LOCAL_IP_ADDR=$(ip a s wlp2s0 | awk '/inet / {print$2}' | cut -d/ -f1) # Adapt to your interface
 docker-compose up -d --build
```

Pretty easy, just run :
```
NETWORK_INTERFACE=wlp2s0 donkeycar-manager
```

Take a look at the OpenAPI/SwaggerUI at : http://127.0.0.1:8000/docs

### Environment variables

* `NETWORK_INTERFACE` : interface that will be used to find server IP addr, use for ZeroConf. Eg: eth0, ...