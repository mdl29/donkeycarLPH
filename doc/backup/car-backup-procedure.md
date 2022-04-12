# Procédure de backup carte SD raspberry pi

Ce document présente la procédure de backup utilisée pour sauvegarder une carte SD de raspberry Pi tout en la compressant. Nous l'utilisons typiquement pour sauvegarder les car SD des raspberry pi des voiture à la fin de chaques séances.


## Création d'un backup


### Création d'une image de backup
Commencez par insérer la carte SD dans votre ordinateur, en utilisant un adaptateur SD -> micro SD. Identifiez le nom du périphérique :
```bash
$ lsblk
[.....]
sdc      8:32   1  29,1G  0 disk 
├─sdc1   8:33   1   256M  0 part /media/benjamin/boot
└─sdc2   8:34   1   4,2G  0 part /media/benjamin/rootfs
```

Ici le nom du device est **sdc**, nous allons l'utiliser pour créer une image de la carte SD, vous pouvez également calculer le block size (bs) idéal pour la lecture de votre carte.

*Nous devrions écrire un script qui trouve le meilleur bs (ibs / obs) on se basant sur cet [article ici](http://blog.tdg5.com/tuning-dd-block-size/) [#13](https://github.com/mdl29/donkeycarLPH/issues/13)*


```bash
export carName="dababycar"
export fullBackupFile=$(date +"%Y-%m-%d_%H:%m")"-rpibackup-"$carName".img"
sudo dd of=$fullBackupFile bs=4M if=/dev/sdc status=progress && sync
```

### Réduire l'image du backup

Il est probable que votre backup si vous avez étendu la taille de la raspberry pi soit très gros (surtout si vous avez une carte SD de grand capacitée). Nous allons réduire la taille de l'image à l'aide de [PiShrink](https://github.com/Drewsif/PiShrink).

Installer PiShrink ([source](https://github.com/Drewsif/PiShrink#installation)) :
```bash
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
sudo mv pishrink.sh /usr/local/bin
```

Réduire la taille de l'image :
```bash
sudo pishrink.sh -s -z -a $fullBackupFile $fullBackupFile-compressed.img
```

N'utilisez pas l'option `-p` elle va certe supprimer les logs mais aussi des clés SSH ce qui va vous empêcher de vous y connecter si vous restaurez ce backup.

### Archive de l'image sur S3
Les backup n'ont aucun intéret s'il nous sont pas bien sauvegardés après. Nous allons utiliser [AWS S3 (glacier)](https://aws.amazon.com/fr/s3/), pour archiver les backups. Vous devez d'abord installer le [CLI AWS](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html), vous pouvez vérifier qu'il est bien installé avec un `aws --version`.

Récupérer les credential AWS avec Benjamin. Faire un :
```bash
aws s3 cp 2022-03-26_14:03-rpibackup-dababycar-compressed.img.gz s3://donkeycar-lph-sd-backup/dababycar/2022-03-26_14:03-rpibackup-dababycar-compressed.img.gz
```

## Restoration du backup

```bash
gzip -c -d 2022-03-05_dababycar-debutSeanceLPH-compressed.img.gz | dd bs=2MB of="/dev/sdc" status=progress
sync
```