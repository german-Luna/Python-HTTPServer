from typing import Optional
import socket
import threading
import mimetypes
import logging
import gzip

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    datefmt='[%d/%b/%Y:%H:%M:%S %z]',
    level=logging.INFO
)

class HTTPServer:
    def __init__(self, ip: str = "127.0.0.1", port: int = 5053,allow_gzip: bool = True) -> None:
        self.ip: str = ip
        self.port: int = port
        self.gzip: bool = allow_gzip

    def connection_handler(self, connection: socket.socket) -> None:
        try:
            log = logging.getLogger("http_server")
            while True:
                data: bytes = connection.recv(1024)
                if not data:
                    break
                
                #decode the http request into a dictionary
                http_header = {}

                #extract request type, path and http version
                request_type, get_path, http_version = data.decode("utf-8").split("\r\n")[0].split(" ")

                http_header["request_type"] = request_type
                http_header["get_path"] = get_path
                http_header["http_version"] = http_version

                for line in data.decode("utf-8").split("\r\n"):
                    if not line:
                        break
                    unpacked = line.split(": ")

                    if not len(unpacked) == 2:
                        continue

                    http_header[unpacked[0]] = unpacked[1]
                
                gzip_allowed: bool = False
                if self.gzip and "gzip" in http_header["Accept-Encoding"]:
                    gzip_allowed = True
                
                log.info('"%s %s HTTP/1.1" 200 %d', data.decode("utf-8").split(" ")[0], get_path, len(data))

                if get_path == "/":
                    get_path = "index.html"

                path: str = f"./{get_path}"

                mime_type: Optional[str] = mimetypes.guess_type(path)[0]
                if not mime_type:
                    mime_type = "text/html"

                try:
                    with open(path, "rb") as f:
                        body: bytes = f.read()

                        if gzip_allowed:
                            body = gzip.compress(body)

                        http_response_header = ""

                        http_response_header += f"HTTP/1.1 200 OK\r\n"
                        http_response_header += f"Content-Type: {mime_type}\r\n"
                        http_response_header += f"Content-Length: {len(body)}\r\n"

                        if gzip_allowed:
                            http_response_header += "Content-Encoding: gzip\r\n"

                        http_response_header += "\r\n"

                        response: bytes = http_response_header.encode("utf-8") + body

                        connection.sendall(response)
                except FileNotFoundError:
                    response: bytes = (
                        "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n"
                        "Content-Length: 0\r\n\r\n".encode("utf-8")
                    )
                    connection.sendall(response)

        except (ConnectionResetError, ConnectionAbortedError) as e:
            log = logging.getLogger("http_server")
            log.warning(f"{e.__class__.__name__} occurred", exc_info=True)

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
        print(f"Server running on http://{self.ip}:{self.port}")
        self.connection_acceptor(sock)


server = HTTPServer()
server.start()