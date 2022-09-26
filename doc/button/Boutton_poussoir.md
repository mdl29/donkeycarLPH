# Boutton poussoir pour donkeycar

Méthode d'emploi pour installer et utiliser un bouton poussoir permettant d'éteindre une donkeycar

# Installation
Wiring Pi est une bibliothèque libre en C permettant de gérer et d'accéder aux PINs GPIO de la raspeberry

## Pour l'installer
Sur un système Raspian-Lite :
```
# apt-get install wiringpi
```
## Créer le script bash
A l'aide d'un logiciel de traitement de texte comme nano, créer un fichier nommé pin-shutdown.sh dans le dossier root
```
# nano /root/pin-shutdown.sh
```
Dans votre fichier sh, mettez les lignes suivantes :
```bash
#!/bin/bash

pin=29  # pin 40 (internal: 21) on raspi layout
gpio mode $pin in
gpio wfi $pin both
logger Shutdown button pressed
shutdown -h now
```

Enregistrez le fichier, puis rendez-le exécutable avec chmod +x
```
# chmod +x /root/pin-shutdown.sh
```
Vous pouvez tester votre script en l'exécutant de la manière suivante :
```
# sudo /root/pin-shutdown.sh
```
## Créer le service
Il vout faut maintenant créer un service pour qu'au démarrage, le script soit lancé en arrière-plan, afin qu'il puissse détecter n'importe quand le boutton poussoir.

Premièrement, il faut créer le fichier de notre service. Pour cela, on réutilise un logiciel de traitement de texte. On va enregistrer notre service dans le fichier /etc/systemd/system/
```
# nano /etc/systemd/system/button-shutdown.service
```
Dans votre fichier, écrivez :
```bash
[Unit]
Description=button shutdown service

[Service]
ExecStart=/root/pin-shutdown.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
Enrengistrez enfin le fichier.

# Usage
## Activer le script au démarrage
Premièrement, on doit mettre à jour les services de systemctl pour y ajouter le nôtre :
```
# systemctl daemon-reload 
```
Ensuite, on active le service pour que le script se lance à chaque démarrage :
```
# systemctl enable button-shutdown.service 
```
Si vous ne voulez pas redémarrer votre ordinateur, lancez dès maintenant le service :
```
# systemctl start button-shutdown.service 
```
Enfin, pour être sûr que votre service est lancé :
```
# systemctl status button-shutdown.service
```
