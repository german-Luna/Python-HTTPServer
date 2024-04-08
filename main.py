import socket
import threading
import mimetypes

class HTTPServer:
    def __init__(self, ip="127.0.0.1", port=5053,):
        self.ip = ip
        self.port = port
    
    def connection_handler(self,connection: socket.socket):
        while True:
            data = connection.recv(1024)
            if not data:
                break

            get_path = data.decode("utf-8").split(" ")[1]
            print(get_path)

            if get_path == "/":
                get_path == "index.html"
            
            path = f"./{get_path}"
            
            mime_type = mimetypes.guess_type(path)[0]
            if not mime_type:
                mime_type = "text/html"

            try:
                with open(path, "rb") as f:
                    body = f.read()
                    response = bytes(f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(body)}\r\n\r\n".encode("utf-8")) + body
                    connection.sendall(response)

            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: 0\r\n\r\n".encode("utf-8")
                connection.sendall(response)


    def connection_acceptor(self,sock):
        while True:
            connection, address = sock.accept()
            threading.Thread(target=self.connection_handler, args=(connection,)).start()
    
    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen(100)
        self.connection_acceptor(sock)


server = HTTPServer()
server.start()