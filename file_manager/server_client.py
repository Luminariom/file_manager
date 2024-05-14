import socket

DATA_SIZE = 1024

class Connection:
    def __init__(self, port):
        self.host = "localhost"
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen()

            self.sender, addr = self.server.accept()
        except OSError as e:
            print(e)

    def connect(self, host, port):
        self.client.connect((host, port))

    def send_filetree(self, filetree):
        self.server.sendall(filetree)

    def receive_filetree(self):
        return self.client.recv(DATA_SIZE)

    def close(self):
        self.server.close()
        self.client.close()