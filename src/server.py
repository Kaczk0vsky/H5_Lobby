import socket
import time

host = "10.0.0.4"
port = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(1)

print(f"Serwer nasłuchuje na {host}:{port}...")

# Akceptowanie połączenia
c, addr = s.accept()
print(f"Połączono z {addr}")

try:
    while True:
        message = "Hello World"
        c.send(message.encode())  # Wysyłanie wiadomości
        print(f"Wysłano: {message}")
        time.sleep(2)  # Odczekanie 2 sekundy przed kolejną wiadomością
except KeyboardInterrupt:
    print("\nZamykanie serwera...")
finally:
    c.close()  # Zamknięcie połączenia
    s.close()
