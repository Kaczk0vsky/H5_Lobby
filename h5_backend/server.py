import socket
import threading
import time

from src.global_vars import env_dict


class Server:
    _max_connections = 5

    def __init__(self):
        self.server_url = env_dict["SERVER_LISTEN_ON"]
        self.server_port = env_dict["SERVER_PORT"]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.server_url, self.server_port))
        self.socket.listen(self._max_connections)
        self.clients = []
        self.running = True

    def start(self):
        broadcast_thread = threading.Thread(target=self.broadcast_message, daemon=True)
        broadcast_thread.start()

        try:
            while True:
                client_socket, client_address = self.socket.accept()
                print(f"Connected with - {client_address}")
                self.clients.append(client_socket)

                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket,)
                )
                client_thread.start()
        except KeyboardInterrupt:
            self.running = False
            print("\nStopped server...")
        finally:
            self.socket.close()

    def handle_client(self, client_socket):
        try:
            while True:
                msg = client_socket.recv(1024)
                if not msg:
                    print("Client ended connection...")
                    break
                print(msg.decode())

                response = "Hello from server!"
                client_socket.send(response.encode())

        except ConnectionResetError:
            self.clients.remove(client_socket)
            print("Client closed connection unexpectedly.")
        finally:
            client_socket.close()

    def broadcast_message(self):
        while self.running:
            time.sleep(5)
            message = "Message from server :)"
            for client in self.clients:
                try:
                    client.send(message.encode())
                except BrokenPipeError:
                    print("Client ended connection...")
                    self.clients.remove(client)


if __name__ == "__main__":
    server = Server()
    server.start()
