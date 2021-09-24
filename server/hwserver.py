import json
import os
import os.path as path
import zmq

from helper import (
    add_file,
    add_user,
    decrypt_message,
    encrypt_message,
    file_exists,
    generate_key,
    get_file_content,
    get_file_name,
    get_path,
    user_exists
)


ROUTE = "tcp://*:8001"
DB = json.load(open('db.json','r'))


def upload(bytes_content: bytes, **message) -> list:
    filename : str = message.get("filename", "NoName")
    file_hash : str = message.get("file_hash", "123123")
    username : str = message.get("username", "NoName")

    if not user_exists(username, DB):
        add_user(username, DB)

    response : list = add_file(
        get_path(file_hash, filename),
        bytes_content,
        DB,
        **message
    )
    return response

def sharelink(**message) -> list:
    filename : str = message.get("filename", "NoName")
    file_hash : str = message.get("file_hash", "123123")
    username : str = message.get("username","NoName")

    if not user_exists(username, DB):
        return [{"message": "message", "response": "user 404"}, b""]

    if not file_exists(username, DB, filename):
        return [{"message": "message", "response": "file 404"}, b""]

    sharelink = encrypt_message(get_path(file_hash, filename))
    return [{"message": "message", "response": sharelink}]

def download(**message) -> list:
    file_chunks : int = message.get("file_chunks")
    sharelink : str = message.get("sharelink")
    username : str = message.get("username","NoName")
    
    if not user_exists(username, DB):
        return [{"message": "message", "response": "user 404"}, b""]

    message["filename"] = get_file_name(username, sharelink, DB)
    if not message["filename"]:
        return [{"message": "message", "response": "file 404"}, b""]

    path : str = decrypt_message(sharelink)
    if file_chunks:
        file_content = get_file_content(DB, path, **message)
        return [{
            "message": "download",
            "file_chunks": file_chunks,
            "filename": message["filename"]
        }, file_content]
    else:
        file_size = os.stat(path).st_size
        file_chunks = file_size / (1024 * 1024 * 50)

        if file_chunks != int(file_chunks):
            file_chunks = int(file_chunks) + 1

    if not file_chunks:
        message["file_chunks"] = 0
        file_content = get_file_content(DB, path, **message)
        return [{
            "message": "download",
            "file_chunks": file_chunks,
            "filename": message["filename"]
        }, file_content]
    
    return [{
            "message": "download",
            "file_chunks": file_chunks,
            "filename": message["filename"]
        }, b""]

def list_files(**message) -> list:
    username : str = message.get("username")
    for user in DB:
        if user["username"] == username:
            files = user["file"].values()
            return [{'message': 'message', 'response': files}, b'']

    return [{'message': 'message', 'response': 'user 404'}, b'']

if __name__ == "__main__":
    if not path.isfile("secret.key"):
        generate_key()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(ROUTE)

    count = 1
    while True:
        print('Esperando solicitud {}'.format(count))
        message, bytes_content = socket.recv_multipart()
        message = json.loads(message.decode("utf-8"))
        
        if message.get("operation","") == "upload":
            response : list = upload(bytes_content, **message)
        elif message.get("operation","") == "sharelink":
            response : list = sharelink(**message)
        elif message.get("operation","") == "download":
            response : list = download(**message)
        elif message.get("operation","") == "list":
            response : list = list_files(**message)
        else:
            print("error")
            response : list = [{"message": "error"}]

        if len(response) < 2:
            bytes_content = b""
            response.append(bytes_content)

        response[0] = json.dumps(response[0]).encode('utf-8')
        socket.send_multipart(response)
        count += 1