import socket

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    port = 61005

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, port))
    server.listen(5)

    while True:
        client, address = server.accept()
        # Once connected, display the address.
        print(f"Connection Started\nAt Address - {address[0]} :  {address[1]}")

        # Setting the number of bytes for the message that the server will receive
        while True:
            message = client.recv(1024)
            if not message:
                break

            message = message.decode("utf-8")
            print("Client: " + message)

            if message == "END":
                client.close()
                break