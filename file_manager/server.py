import socket
import os
import sys
import threading

#HOST = 'localhost'  # The server's hostname or IP address
#PORT = 65432        # The port used by the server

def handle_client(connection):
    while True:
        try:
            data = connection.recv(1024)
            if not data:
                break
            command = data.decode('utf-8')
            response = f"Received command: {command}"
            os.system(f"{command}")
            connection.sendall(response.encode('utf-8'))
        except ConnectionResetError:
            break
    connection.close()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 65432))
    server_socket.listen()
    print("Server is listening on", 65432)

    while True:
        client_socket, addr = server_socket.accept()
        print('Connected by', addr)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

def receive_file():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 65433))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if data == b'SEND_FILE':
                with open('received_file.txt', 'wb') as f:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        f.write(data)
                print("File received successfully.")

def main():
    receive_file()

if __name__ == '__main__':
    server_thread = threading.Thread(target=server)
    server_thread.start()
    main()