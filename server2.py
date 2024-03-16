# Server Multi Threading

import socket
import threading

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    port = 61005

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, port))
    server.listen(5)

    message = "Message Received"

    def listener(client, address):
        print(f"New connection from {client=} {address=}")
        while True:
            buffer = client.recv(1024)
            if not buffer:
                print(f"Closing connection to {client=} {address=}")
                break

            buffer = buffer.decode("utf-8")
            print(f"Client {address}: + {buffer}")

            client.send(bytes(message, "utf-8"))
        

    while True:
        client, address = server.accept()
        threading.Thread(target=listener, args=(client, address)).start()