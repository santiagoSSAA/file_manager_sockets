import zmq
import sys, os
import json


ROUTE = "tcp://localhost:8001"

def create_request(*args) -> dict:
    data = {
        "username": sys.argv[1],
        "operation": sys.argv[2]
    }
    
    bytes_content = None
    if data["operation"] in ["upload","sharelink","download"]:
        data["parameter"] = sys.argv[3]
        if data["operation"] in ["upload"]:
            with open(data["parameter"], "rb") as file:
                bytes_content = file.read()
    return [json.dumps(data).encode('utf-8'), bytes_content]

if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:8001')
    
    data = [(elem if elem else b'') for elem in create_request(sys.argv)]
    socket.send_multipart(data)
    message_result = socket.recv_multipart()
    if len(message_result) > 1:
        filename = message_result[0].decode("utf-8")
        content = message_result[1]
        with open(filename,"wb") as file:
            file.write(content)
        print("downloaded: {}".format(filename))
    else:
        print(message_result)