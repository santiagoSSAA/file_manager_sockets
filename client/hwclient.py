import json
import hashlib
import sys, os
import zmq

from socket_class import SocketRequest


CHUNK_SIZE = 1024*1024*5
ROUTE = "tcp://localhost:8001"


def get_file_hash(file):
    sha1 = hashlib.sha1()
    sha1.update(file)
    return sha1.hexdigest()


def create_request(*args) -> SocketRequest:
    request = SocketRequest(
        username=args[1],
        operation=args[2]
    )
    if request.operation in ["upload", "sharelink"]:
        request.set_filename(args[3])
    elif request.operation == "download":
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
            request.set_file_hash(get_file_hash(chunk))
            request.set_multipart_message(
                request=request.get_upload_message(),
                content=b""
            )
            socket.send_multipart(request.multipart_message)
            request.is_file_beginning = False

            chunk_number = 1
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

    request.set_multipart_message(
        request=request.get_minimal_data(),
        content=b""
    )
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
