import socket
import threading
import handlers
import timeout
import Chat
import functions

# Initialise array of chats.
chats = {}

# Declared globally here so that the server can be accessed by all the fucntions.
host = '0.0.0.0'
port = 61000
server_id = 1234
magic = 17109271

math_funcs = functions.MathFunctions()
math_funcs.add_function("function1", "4 + 5 * 3 + 4")
math_funcs.add_function("function2", "x**2 + 3*x + 2")
math_funcs.add_function("function3", "sin(x)")

# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def broadcast(message):

    if message == "add function":
        num = input("\nEnter function number: ")
        equ = input("\nEnter function: ")
        math_funcs.functions[num] = math_funcs.add_function(num, equ)
    elif message == "vote":
        equ = input("\nEnter function: ")
        for client in chats.values():
            id = client.client_id
            to_send = handlers.create_packet(magic, 1, 5, 0, 4, equ)
            chats[id].chat_sender(to_send)
        print(f"Broadcasted Vote Sent")
    else:
        for client in chats.values():
            id = client.client_id
            to_send = handlers.create_packet(magic, 1, 5, 0, 0, message)
            chats[id].chat_sender(to_send)
        print(f"Broadcast Sent")

def handle_client(addr, packet, chats):

    dec_pack = handlers.decode_packet(packet)
    chat_number = chats.get(dec_pack.client_id)

    # If there is a chat matching this ID send it to the SR ARQ handler.
    if chat_number:
        chats[dec_pack.client_id].chat_receiver(dec_pack)
        
    else:
        # If the chat doesn't exist 
        print(f"New Connecton from {addr} with ID: {dec_pack.client_id}")

        chats[dec_pack.client_id] = Chat.Chat(addr, dec_pack, server, server_id, magic)
        # Send the packet.
        #chats[addr].chat_loop(data)
    print(f"Number of Clients: {len(chats)}")


def server_listener():
    
    # Bind the socket to the host and port
    server.bind((host, port))
    print("Server listening on {} : {}".format(host, port))

    while True:

        # Receiving the UDP packet.
        packet, addr = server.recvfrom(1024)   
        handle_client(addr, packet, chats)

def server_sender():

    while True:
        message = input("\nEnter Message: ")

        broadcast(message)
        print("Sent message to clients: {}".format(message))


def main():

    listen_thread = threading.Thread(target=server_listener, )
    listen_thread.start()

    send_thread = threading.Thread(target=server_sender, )
    send_thread.start()


if __name__ == "__main__":
    main()
