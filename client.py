import socket

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    port = 61005

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.connect((server_ip, port))

while True:
    # Prompt for Sending string to the server.
    message = input("Enter your message: ")

    server.send(bytes(message, "utf-8"))

    if message == "END":
        break

