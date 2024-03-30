import handlers

# ////// PIP - Packet inside packet

# type PcktHeader struct {
# 	Magic  		uint32 // 4 bytes
# 	Checksum	unit32 // 4 bytes CRC32
# 	PcktID 		uint16 // 2 bytes
# }

# // Pckt IDs
# const (
# 	hello_c2s	  = 0 // from client to server, basically SYN
# 	hello_back_s2c    = 1 // from server to client, basically ACK
# 	vote_c2s_request_vote  = 2 // from client to server to begin vote
# 	vote_s2c_broadcast_question   = 3 // from server to all clients to vote on
# 	vote_c2s_response_to_question = 4 // from client to server
# 	vote_s2c_broadcast_result   = 5 // from server to all clients
# )

def client_processor(received):
    global ack_packets
    global recv_packets
    global sent_packets
    global server
    global server_addr
    global client_id 

    if (received.type == 0):
        # Deal with differnt data responses from the server.
        if received.packet_id == 1:
            recv_packets[received.seq_num] = received
            handlers.send_ack(server, server_addr, received, client_id)


        elif received.packet_id == 3:
            recv_packets[received.seq_num] = received
            print(f"Received Question from server: {received.question}")
            handlers.send_ack(server, server_addr, received, client_id)
            compute_answer(received)


        elif received.packet_id == 5:
            recv_packets[received.seq_num] = received
            print(f"Received Vote Result From Server: Vote ID {received.vote_id}\n Result {received.result}")
            handlers.send_ack(server, server_addr, received, client_id)

        
    elif (received.type == 1):
        ack_packets[received.seq_num] = received
        print(f"From Server: ACK {received.seq_num}")

    elif received.type == 2:
        print(f"From Server: NACK {received.seq_num}")


def compute_answer(received):
    
