import json

class SocketRequest():
    """SocketRequest class"""

    def __init__(self, **kwargs):
        self.operation : str = kwargs.get("operation")

        self.is_file_beginning : bool = False
        self.is_sending_message : bool = False
        self.filename : str = None
        self.file_content : bytes = None
        self.file_chunks : int = None
        self.file_hash : str = None
        self.multipart_message : list = [{}, b""]
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

    def set_multipart_message(self, content:bytes = None, request: dict = {}):
        if request:
            self.multipart_message[0] = json.dumps(request).encode("utf-8")
        if content:
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

    def get_minimal_data(self) -> dict:
        return {
            "file_chunks": self.file_chunks,
            "sharelink": self.sharelink,
            "operation": self.operation,
            "username": self.username
        }

    def get_download_message(self) -> dict:
        return {
            "file_chunks": self.file_chunks,
            "sharelink": self.sharelink,
            "operation": self.operation,
            "username": self.username
        }