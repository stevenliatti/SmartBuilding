# IoT Project - Smart Building

Projet Smart Building, avec KNX, OpenZWave, Beacons et Kafka.

## Configuration et déploiement
Le fichier `.env` contient toutes les variables d'environnement nécessaires au `docker-compose` et aux programmes python. Avant de lancer le système, il faut éditer ce fichier selon ses besoins. Ensuite, il faut démarrer dans l'ordre :

1. Une gateway KNX (que ce soit le simulateur actuasim ou une vraie gateway)
1. Les containers Docker avec le `docker-compose.yml` sur une machine accessible depuis internet avec les bons ports ouverts
1. Le module KNX (`knx`) avec le `makefile` associé : exécuter `make` dans le répertoire
1. Le module OpenZWave (`zwave`) sur un Raspberry Pi avec la configuration nécessaire (voir TP2 OpenZWave)


## Arborescence des fichiers
Le répertoire `android` contient le code de l'application. Le répertoire `db` contient la configuration et le script de création de la base de données. Le répertoire `knx` contient le code du module KNX ainsi qu'un `makefile` pour lancer le simulateur actuasim. Le répertoire `scripts` contient les modules python reliés à Kafka, ainsi qu'un simple exemple de consommateur et producteur (`consumer.py` et `producer.py`). Le répertoire `server` contient le serveur Flask avec un Dockerfile. Le répertoire `zwave` contient le code du module OpenZWave. On retrouve également le `docker-compose.yml` à la racine permettant de lancer en même temps le broker Kafka, la base de données, le serveur Flask et le contrôleur automatic. Il faut déployer ces containers sur une machine visible depuis Internet et exposant les ports mentionnés.
```
|-- android
|   |-- app
|   |-- ...
|-- db
|   |-- conf
|   |   |-- conf.cnf
|   |-- dump
|       |-- create.sql
|-- docker-compose.yml
|-- knx
|   |-- init_devices.py -> ../scripts/init_devices.py
|   |-- knx_lib.py
|   |-- knx.py
|   |-- makefile
|-- README.md
|-- scripts
|   |-- automatic_controller.py
|   |-- consumer.py
|   |-- db_to_kafka.py
|   |-- Dockerfile
|   |-- init_devices.py
|   |-- logs.py
|   |-- producer.py
|-- server
|   |-- Dockerfile
|   |-- server.py
|-- zwave
    |-- configpi.py
    |-- init_devices.py -> ../scripts/init_devices.py
    |-- zwave_lib.py
    |-- zwave.py
```
