import json

from cryptography.fernet import Fernet
from os import getcwd


def add_file(path: str,  bytes_content: bytes, db: list, **kwargs) -> list:
    is_file_beginning : str = kwargs.get("is_file_beginning")
    is_sending_message : str = kwargs.get("is_sending_message")
    filename : str = kwargs.get("filename")
    file_hash : str = kwargs.get("file_hash")
    username : str = kwargs.get("username")

    if is_sending_message:
        if is_file_beginning:
            open(path, "wb+").write(bytes_content)
            add_file_json(username, filename, file_hash, db)
            return [{"message": "ok"}]
        
        open(path, "ab").write(bytes_content)
        return [{"message": "ok"}]
    return [{"message": "message", "response": "archivo subido"}]

def add_file_json(username: str, filename: str, file_hash: str, db: list):
    for user in db:
        if user["username"] == username and not filename in user["file"]:
            user['file'][file_hash] = filename
        with open("db.json","w") as file:
            json.dump(db, file)

def add_user(username: str, db: list) -> None:
    db.append({"username": username, "file": dict()})
    with open("db.json","w") as db_file:
        json.dump(db, db_file)
    print("{} agregado".format(username))

def encrypt_message(message):
    key = open("secret.key", "rb").read()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message.decode()

def decrypt_message(encrypted_message):
    key = open("secret.key", "rb").read()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode()

def file_exists(username: str, db: list, filename: str):
    for user in db:
        if filename in user.get("file",{}).values():
            return user.get("file").values()
    pass

def generate_key() -> None:
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def get_file_content(db: list, path: str, **kwargs):
    filename : str = kwargs.get("filename")
    file_hash : str = kwargs.get("sharelink")
    file_chunks : int = kwargs.get("file_chunks")
    username : str = kwargs.get("username")

    for user in db:
        if user.get('username') == username:
            hash_name = "{}.{}".format(file_hash, filename.split(".")[1])
            if not file_chunks:
                return open(path, "rb").read()
            else:
                return open(path, "rb").read(1024*1024*50)

    return None

def get_file_name(username: str, file_hash: str, db: list) -> str:
    for user in db:
        if user.get('username') == username:
            if file_hash in user["file"].keys():
                return user.file.get(file_hash)
    return ""

def get_path(file_hash: str, filename: str):
    file_extension = filename.split(".")[1]
    return "{}/files/{}.{}".format(getcwd(), file_hash, file_extension)

def user_exists(username: str, db: list) -> bool:
    for user in db:
        if user.get('username') == username :
            return True
    return False

