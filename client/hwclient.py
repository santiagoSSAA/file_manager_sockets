import json
import hashlib
import sys, os
import zmq


# 50 mb -> 52428800 Bytes
#CHUNK_SIZE = 1024*1024*1024 # 1gb
CHUNK_SIZE = 50
ROUTE = "tcp://localhost:8001"
CHUNK_SIZE = 1024*1024*5

class SocketRequest():
    """SocketRequest class"""

    def __init__(self, **kwargs):
        self.is_file_beginning : bool = False
        self.is_sending_message : bool = False
        self.filename : str = None
        self.file_content : bytes = None
        self.file_chunks : int = None
        self.file_hash : str = None
        self.operation : str = kwargs.get("operation")
        self.sharelink : str = None
        self.username : str = kwargs.get("username")

    def set_filename(self, filename:str) -> None:
        self.filename = filename

    def set_file_content(self, file_content: bytes) -> None:
        self.file_content = file_content

    def set_file_chunks(self, file_chunks: int) -> None:
        self.file_chunks = file_chunks

    def set_file_hash(self, file_hash: str) -> None:
        self.file_hash = file_hash    

    def set_share_link(self, sharelink: str) -> None:
        self.sharelink = sharelink

    def get_file_size(self) -> int:
        return os.stat(self.filename).st_size

    def get_upload_message(self) -> dict:
        return {
            "is_file_beginning": self.is_file_beginning,
            "is_sending_message": self.is_sending_message,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "operation": self.operation
        }

def create_request(*args) -> SocketRequest:
    request = SocketRequest(
        username=args[1],
        operation=args[2]
    )
    if request.operation == "upload":
        request.set_filename(args[3])
    elif request.operation in ["download", "sharelink"] :
        request.set_share_link(args[3])
    else:
        raise Exception("operation {} not allowed".format(request.operation))
    return request

def get_file_hash(file):
    sha1.update(file)
    return sha1.hexdigest()

def main(socket, *args) -> None:
    request : SocketRequest = create_request(*args)
    multipart_message : list = [None, None]

    if request.operation == "upload":
        request.is_sending_message = True

        file_chunks = request.get_file_size() / CHUNK_SIZE
        if file_chunks != int(file_chunks):
            file_chunks = int(file_chunks) + 1

        with open(request.filename, "rb") as file:
            chunk = file.read(CHUNK_SIZE)
            request.is_file_beginning = True
            request.set_file_hash(get_file_hash(file))
            multipart_message[0] = json.dumps(request.get_upload_message()).encode("utf-8")
            multipart_message[1] = b""
            socket.send_multipart(multipart_message)
            request.is_file_beginning = False

            chunk_number : int = 1
            while chunk:
                server_response : dict = json.loads(socket.recv_multipart()[0])

                if server_response.get("message") == "ok":
                    multipart_message[0] = json.dumps(request.get_upload_message()).encode("utf-8")
                    multipart_message[1] = chunk
                    socket.send_multipart(multipart_message)

                chunk_number += 1
                chunk = file.read(CHUNK_SIZE)

        _ = socket.recv_multipart()

    else:
        multipart_message[1] = b""
        if request.operation == "download":
            request.set_file_chunks(0)

    multipart_message[1] = b""
    socket.send_multipart(multipart_message)
    server_response : dict = json.loads(socket.recv_multipart()[0])
    if server_response.get("message") in ["message", "list"]:
        print(server_response.get("response"))
    elif server_response.get("message") == "download": #TODO: THIS PART, AND THE SERVER
        path : str = "{}/{}".format(
            os.getcwd(),
            server_response.get("filename")
        )
    else:
        raise Exception("operation error {}".format(server_response))

if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:8001')

    main(socket, *sys.argv)
