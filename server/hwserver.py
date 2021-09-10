import zmq
import json
import re
import os.path as path
import os
from cryptography.fernet import Fernet

ROUTE = "tcp://*:8001"

def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Load the previously generated key
    """
    return open("secret.key", "rb").read()

def encrypt_message(message):
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message.decode()

def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()

def folder_exists(name:str) -> bool:
    return path.isdir("files/{}".format(name))

def upload(**kwargs):
    username : str = kwargs.get("username","NoName")
    filename : str = kwargs.get("parameter", "None.none")
    content : str = kwargs.get("content", "None")
    
    if not folder_exists(username):
        os.makedirs("files/{}".format(username))
    
    with open("files/{}/{}".format(username,filename),"wb") as file:
        file.write(content.encode("latin-1"))
    return {"message": "uploaded"}

def sharelink(**kwargs):
    username : str = kwargs.get("username","NoName")
    filename : str = kwargs.get("parameter", "None.none")
    route = "files/{}/{}".format(username,filename)
    
    if not path.isfile(route):
        return {"message": "no file 404"}
    
    sharelink = "ElPaseo5.com/{}".format(encrypt_message(route))
    return {"message": sharelink}
    
def download(**kwargs):
    link : str = kwargs.get("parameter", "None.none")
    code = link.split("/")[1].encode()
    route = decrypt_message(code)
    filename = route.split("/")[2]
    
    if not path.isfile(route):
        return {"message": "error file 404"}
    
    with open(route,"rb") as file:
        content = file.read().decode("latin-1")
    
    return {
        "message": {
            "filename": filename,
            "content": content
        }
    }

def list_files(**kwargs):
    username : str = kwargs.get("username","NoName")
    route = "files/{}".format(username)
    
    if not path.isdir(route):
        return {"message": "folder 404"}
    
    return {
        "message": [f for f in os.listdir(route) if path.isfile(path.join(route, f))]
    }


if __name__ == "__main__":
    if not path.isfile("secret.key"):
        generate_key()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(ROUTE)

    while True:
        print('Esperando solicitud')
        message = socket.recv_json()
        print("Conectado: {}".format(message.get("username", "NoName")))

        if message.get("operation","") == "upload":
            response = upload(**message)
        elif message.get("operation","") == "sharelink":
            response = sharelink(**message)
        elif message.get("operation","") == "download":
            response = download(**message)
        elif message.get("operation","") == "list":
            response = list_files(**message)
        else:
            print("error")
            response = {"message": "error"}
        
        
        socket.send_json(response)