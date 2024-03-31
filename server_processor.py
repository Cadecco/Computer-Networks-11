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

def server_processor(packet):
    global ack_packets
    global recv_packets
    global sent_packets
    global server
    global server_addr
    global client_id 

    # Data
    if (packet.type == 0):
        if packet.packet_id == 0:
            recv_packets[packet.seq_num] = packet
            print(f"Received Hello Packet from Client {packet.client_id} : {packet.question}")
            handlers.send_ack(server, server_addr, packet, client_id)

        elif packet.packet_id == 2:
            recv_packets[packet.seq_num] = packet
            print(f"Received Vote Request from Client: {packet.client_id} Question: {packet.question}")
            handlers.send_ack(server, server_addr, packet, client_id)
            #compute_answer(packet)

        elif packet.packet_id == 4:
            recv_packets[packet.seq_num] = packet
            print(f"Received Resposne to Question from Client: {packet.client_id} {packet.vote_id}\n Result {packet.result}")
            handlers.send_ack(server, server_addr, packet, client_id)

        elif packet.packet_id == 6:
            recv_packets[packet.seq_num] = packet
            print(f"From Client {packet.client_id} : {packet.message}")
            handlers.send_ack(server, server_addr, packet, client_id)

     # ACK
    elif (packet.type == 1):
        ack_packets[packet.seq_num] = packet
        print(f"From Client {packet.client_id}: ACK {packet.seq_num}")

    # NACK
    elif packet.type == 2:
        print(f"From Client {packet.client_id}: NACK {packet.seq_num}")
