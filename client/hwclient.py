import zmq
import sys, os
import json


ROUTE = "tcp://localhost:8001"

def create_request(*args) -> dict:
    data = {
        "username": sys.argv[1],
        "operation": sys.argv[2]
    }
    
    if data["operation"] in ["upload","sharelink","download"]:
        data["parameter"] = sys.argv[3]
        if data["operation"] in ["upload","sharelink"]:
            with open(data["parameter"], "rb") as file:
                data["content"] = file.read().decode("latin-1")
    return data

if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:8001')
    data = create_request(sys.argv)
    
    socket.send_json(data)
    message_result = socket.recv_json()
    if isinstance(message_result.get("message"), dict):
        filename : str = message_result.get("message").get("filename")
        content : str = message_result.get("message").get("content")
        with open(filename,"wb") as file:
            file.write(content.encode("latin-1"))
        print("downloaded: {}".format(filename))
    else:
        print(message_result)