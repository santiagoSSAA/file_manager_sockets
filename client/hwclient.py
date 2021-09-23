import json
import hashlib
import sys, os
import zmq


CHUNK_SIZE = 1024*1024*50
ROUTE = "tcp://localhost:8001"


def get_file_hash(file):
    sha1.update(file)
    return sha1.hexdigest()

class SocketRequest():
    """SocketRequest class"""

    def __init__(self, **kwargs):
        self.is_file_beginning : bool = False
        self.is_sending_message : bool = False
        self.filename : str = None
        self.file_content : bytes = None
        self.file_chunks : int = None
        self.file_hash : str = None
        self.multipart_message : list = [None, None]
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

    def set_multipart_message(request: dict={}, content:bytes = None):
        if request:
            self.multipart_message[0] = json.dumps(request).encode("utf-8")
        elif content:
            self.multipart_message[1] = content

    def set_share_link(self, sharelink: str) -> None:
        self.sharelink = sharelink

    def get_upload_message(self) -> dict:
        return {
            "is_file_beginning": self.is_file_beginning,
            "is_sending_message": self.is_sending_message,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "operation": self.operation,
            "username": self.username
        }

    def get_download_message(self) -> dict:
        return {}


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


def main(socket, *args) -> None:
    request : SocketRequest = create_request(*args)

    if request.operation == "upload":
        request.is_sending_message = True

        with open(request.filename, "rb") as file:
            chunk = file.read(CHUNK_SIZE)
            request.is_file_beginning = True
            request.set_file_hash(get_file_hash(file))
            request.set_multipart_message(
                request=request.get_upload_message(),
                content=b""
            )
            socket.send_multipart(request.multipart_message)
            request.is_file_beginning = False

            while chunk:
                server_response : dict = json.loads(socket.recv_multipart()[0])

                if server_response.get("message") == "ok":
                    request.set_multipart_message(
                        request=request.get_upload_message(),
                        content=chunk
                    )
                    socket.send_multipart(request.multipart_message)
                chunk = file.read(CHUNK_SIZE)

        _ = socket.recv_multipart()

    else:
        request.set_multipart_message(content=b"")
        if request.operation == "download":
            request.set_file_chunks(0)

    request.set_multipart_message(content=b"")
    socket.send_multipart(request.multipart_message)
    server_response : dict = json.loads(socket.recv_multipart()[0])

    if server_response.get("message") in ["message", "list"]:
        print(server_response.get("response"))
    elif server_response.get("message") == "download": 
        path : str = "{}/{}".format(
            os.getcwd(),
            server_response.get("filename")
        )
        with open(path,"wb") as file:
            file.write(b"")

        chunks = request.file_chunks
        for i in range(chunks):
            request.set_file_chunks(i)
            request.set_multipart_message(
                request=request.get_download_message(),
                content=b""
            )
            socket.send_multipart(request.multipart_message)
            socket_response = socket.recv_multipart()

            with open(path, "ab") as file:
                file.write(socket_response[1])
        print("downloaded")

    else:
        raise Exception("operation error {}".format(server_response))

if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:8001')

    main(socket, *sys.argv)
