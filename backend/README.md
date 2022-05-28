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
docker-compose up -d
```

Pretty easy, just run :
```
donkeycar-manager
```

Take a look at the OpenAPI/SwaggerUI at : http://127.0.0.1:8000/docs