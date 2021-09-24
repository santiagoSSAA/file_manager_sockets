import json
import hashlib
import sys, os
import zmq

from socket_class import SocketRequest


CHUNK_SIZE = 1024*1024*50
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
        file = open(request.filename, "rb")
        chunk = file.read(CHUNK_SIZE)
        request.is_file_beginning = True
        request.set_file_hash(get_file_hash(chunk))
        request.set_multipart_message(
            request=request.get_upload_message(),
            content=b""
        )
        socket.send_multipart(request.multipart_message)
        request.is_file_beginning = False

        file_size = os.stat(request.filename).st_size
        file_chunks = file_size / (1024 * 1024 * 50)
        if file_chunks != int(file_chunks):
            file_chunks = int(file_chunks) + 1

        chunk_number = 1
        while bool(chunk):
            if file_chunks > 0:
                print(str(int((chunk_number/file_chunks)*100))+'%')
            server_response : dict = json.loads(
                socket.recv_multipart()[0]
            )

            if server_response.get("message") == "ok":
                request.set_multipart_message(
                    request=request.get_upload_message(),
                    content=chunk
                )
                socket.send_multipart(request.multipart_message)
                
            chunk_number += 1
            chunk = file.read(CHUNK_SIZE)

        _ = socket.recv_multipart()
        request.is_sending_message = False
    else:
        request.set_multipart_message(content=b"")
        if request.operation == "download":
            request.set_file_chunks(0)

    request.set_multipart_message(
        request=request.get_upload_message(),
        content=b""
    )
    socket.send_multipart(request.multipart_message)
    socket_response = socket.recv_multipart()
    server_response : dict = json.loads(socket_response[0])

    if server_response.get("message") in ["message", "list"]:
        print(server_response.get("response"))
    elif server_response.get("message") == "download": 
        path : str = "{}/{}".format(
            os.getcwd(),
            server_response.get("filename")
        )
        open(path,"wb").write(b"")
        
        chunks = server_response.get("file_chunks")
        for i in range(0, chunks+1):
            if chunks >= 0:
                print(str(int((i/chunks)*100))+'%')
            
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
