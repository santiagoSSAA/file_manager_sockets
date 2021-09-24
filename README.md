# INTEGRANTES

- CESAR ALEJANDRO PIMIENTO HERNANDEZ
- SANTIAGO SANCHEZ PULGARIN

# REQUERIMIENTOS PREVIOS

- virtualenv
- ubuntu 18.04+
- python3.8+
- pip3

# INSTALACIÓN Y EJECUCIÓN

## CREAR ENTORNO VIRTUAL 

- virtualenv -python=python3 venv

## INSTALAR DEPENDENCIAS

- pip3 install -r requirements.txt

## EJECUTAR SERVIDOR

- cd server/

- python3 hwserver.py


## EJECUTAR CLIENTE

- cd client/

### EJECUTAR UPLOAD

- python3 hwclient.py <usuario> upload <archivo>

### EJECUTAR SHARELINK

- python3 hwclient.py <usuario> sharelink <archivo>

### EJECUTAR DOWNLOAD

- python3 hwclient.py <usuario> download <list>

### EJECUTAR LIST

- python3 hwclient.py <usuario> list

