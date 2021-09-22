import zmq
import sys, os
import json


# 50 mb -> 52428800 Bytes
#CHUNK_SIZE = 1024*1024*1024 # 1gb
CHUNK_SIZE = 50
ROUTE = "tcp://localhost:8001"


def get_size(filename : str) -> int:
    st = os.stat(filename)
    return st.st_size


def get_file_total_chunks(file_name : str):
    chunk : float = get_size(filename)/CHUNK_SIZE
    if not chunk == int(chunk):
        chunk += 1
    return chunk


if __name__ == "__main__":
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:8001')
    
    data = {
        "username": sys.argv[1],
        "operation": sys.argv[2],
        "is_writing_file": False,
        "is_listening_server": False
    }
    
    bytes_content = None
    if data["operation"] in ["upload","sharelink","download"]:
        data["parameter"] = sys.argv[3]

        if data["operation"] == "upload":
            data["is_listening_server"] = True

            file = open(data["parameter"], "rb")
            file_chunk = file.read(CHUNK_SIZE)
            total_chunks = get_file_total_chunks(data["parameter"])
            
            # Initial message
            message = [
                json.dumps(data).encode('utf-8'),
                b''
            ]
            socket.send_multipart(message)
            data["is_writing_file"] = True

            # Iterative chunk sending message
            file_number = 0
            while chunk: # TODO: CHECK THIS WHILE, NOT FORWARDING IN FILE
                if not chunk:
                    os.system('clear')
                    percentage = "{}%".format(int(file_number/total_chunks) *100)
                    print("--- {} ---".format(percentage))

                server_response_multipart = socket.recv_multipart()
                server_response_json = json.loads(server_response_multipart[0])
                
                if server_response_json["message"] == "ok":
                    message = [
                        json.dumps(data).encode('utf-8'),
                        chunk
                    ]
                    socket.send_multipart(message)

                file_number += 1
                chunk = file.read(CHUNK_SIZE)
            
            file.close()
            server_response_multipart = socket.recv_multipart()
            server_response_json = json.loads(server_response_multipart[0])
            data["is_listening_server"] = False

            if server_response_json["message"] == "ok":
                message = [
                    json.dumps(data).encode('utf-8'),
                    chunk
                ]
                socket.send_multipart(message)

        else:
            pass

    """
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
    """
    