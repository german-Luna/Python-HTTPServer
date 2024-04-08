import socket
import threading
import mimetypes

from typing import Any, BinaryIO, Optional
import socket
import threading
import mimetypes


class HTTPServer:
    def __init__(self, ip: str = "127.0.0.1", port: int = 5053) -> None:
        self.ip: str = ip
        self.port: int = port

    def connection_handler(self, connection: socket.socket) -> None:
        while True:
            data: bytes = connection.recv(1024)
            if not data:
                break

            get_path: str = data.decode("utf-8").split(" ")[1]
            print(get_path)

            if get_path == "/":
                get_path = "index.html"

            path: str = f"./{get_path}"

            mime_type: Optional[str] = mimetypes.guess_type(path)[0]
            if not mime_type:
                mime_type = "text/html"

            try:
                with open(path, "rb") as f:  # type: BinaryIO
                    body: bytes = f.read()
                    response: bytes = (
                        f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\n"
                        f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
                    ) + body
                    connection.sendall(response)

            except FileNotFoundError:
                response: bytes = (
                    "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n"
                    "Content-Length: 0\r\n\r\n".encode("utf-8")
                )
                connection.sendall(response)

    def connection_acceptor(self, sock: socket.socket) -> None:
        while True:
            connection, address = sock.accept()
            threading.Thread(
                target=self.connection_handler, args=(connection,)
            ).start()

    def start(self) -> None:
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen(100)
        self.connection_acceptor(sock)


server = HTTPServer(port=5050)
server.start()