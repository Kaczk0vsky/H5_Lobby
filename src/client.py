import socket
import threading

from src.global_vars import env_dict


class Client:
    def __init__(self):
        self.server_url = env_dict["SERVER_URL"]
        self.server_port = env_dict["SERVER_PORT"]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((self.server_url, self.server_port))
        except ConnectionRefusedError:
            print("Connection Refused!")

        receive_thread = threading.Thread(target=self.receive_msg, daemon=True)
        receive_thread.start()

    def disconnect(self):
        self.socket.close()

    def receive_msg(self):
        try:
            while True:
                msg = self.socket.recv(1024)
                if not msg:
                    print("Serwer zakończył połączenie.")
                    break
                print("Odebrano:", msg.decode())
        except OSError:
            print("Connection aborted!")
        finally:
            self.disconnect()

    def send_msg(self, msg):
        try:
            self.socket.send(msg.encode())
        except BrokenPipeError:
            print("Cannot send the message, connection refused.")


if __name__ == "__main__":
    c = Client()
    c.connect()
    c.receive_msg()

    # while True:
    #     c.send_msg("Hello!")
