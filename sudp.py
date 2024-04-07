import socket
import threading
import handlers
import Chat
import voting
import random
import globals

# Initialise array of chats.
chats = {}

# Declared globally here so that the server can be accessed by all the fucntions.
host = '0.0.0.0'
port = 8080

server_id = 1234

sequence = 0
# Create a UDP socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Instantiate the vote manager.
vote_manager = voting.VoteManager(chats, globals.magic, sequence)

# Function to send a message to all connected clients.
def broadcast(message, sequence):
    for client in chats.values():
        id = client.client_id
        sequence = client.sequence
        to_send = handlers.create_message(globals.magic, server_id, sequence, 0, True, 0, message)
        chats[id].chat_sender(to_send)
        
    print(f"Broadcast Sent")

# Direct an incoming message to the correct client.
def handle_client(addr, packet, chats):

    dec_pack = handlers.decode_packet(packet)
    chat_number = chats.get(dec_pack.client_id)

    # First perform magic and checksum check.
    if(globals.magic != dec_pack.magic):
        print(f"{dec_pack.client_id} Magic Does Not Match")

    corrupted = handlers.corruption_check(packet, dec_pack)
    if(corrupted):
        print(f"{packet.client_id} w/ Seq {packet.pack_num} Corrupted")

    # If there is a chat matching this ID send it to the SR ARQ handler.
    if chat_number:
        chats[dec_pack.client_id].chat_receiver(dec_pack)
        
    else:
        # If the chat doesn't exist 
        dec_pack.client_id = random.randint(8000, 9000)
        print(f"New Connecton from {addr} with ID: {dec_pack.client_id}")
        
        chats[dec_pack.client_id] = Chat.Chat(addr, dec_pack, server, server_id, globals.magic, vote_manager)
        # Send the packet.
        #chats[addr].chat_loop(data)
    print(f"Number of Clients: {len(chats)}")

#----------------------------------------------------------------------------#

def server_listener():
    
    # Bind the socket to the host and port
    server.bind((host, port))
    print("Server listening on {} : {}".format(host, port))

    while True:

        # Receiving the UDP packet.
        packet, addr = server.recvfrom(1024)   
        handle_client(addr, packet, chats)

# Sender function can send a message to any client.
def server_sender():

    while True:
        message = input("\nEnter Message: ")

        broadcast(message, sequence)
        print("Sent message to clients: {}".format(message))

def main():

    # Sender and receiver are started on separated threads,
    # server can therefore received and send at the same time.

    listen_thread = threading.Thread(target=server_listener, )
    listen_thread.start()

    send_thread = threading.Thread(target=server_sender, )
    send_thread.start()


if __name__ == "__main__":
    main()
