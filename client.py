import socket

if __name__ == "__main__":
    server_ip = "192.168.1.2"
    port = 61005

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.connect((server_ip, port))

while True:
    # Prompt for Sending string to the server.
    message = input("Enter your message: ")

    server.send(bytes(message, "utf-8"))

    received = server.recv(1024)

    print(received)

    if message == "END":
        break

