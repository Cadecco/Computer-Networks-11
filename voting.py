import threading
import time
import handlers
import statistics as stat # For counting votes.

# Poll object that controls the receving of responses and tally for a specific poll.
class poll:
    def __init__(self, chats, question_packet, vote_manager):
        self.vote_id = question_packet.vote_id
        self.responses = {}
        self.chats = chats
        self.question = question_packet.question
        self.voters = {}
        self.end = False
        self.risky = []

        self.result = 0
        self.vote_manager = vote_manager
        # Set the length of time of the poll.
        self.timer = time.time() + 5

        self.lock = threading.Lock()
        self.poll_timer_thread = threading.Thread(target = self.poll_timer, )
        self.poll_timer_thread.start()

    def gather_result(self):
        # Using the mode to find the highest vote.
        try:
            result = stat.mode(self.responses.values())
        except:
            print(f"No Data to Get Result of Poll")
    
        if result:
            return result
        else:
            print(f"No Result Found")

    def poll_timer(self):
        print(f"\nNew Poll Started {self.vote_id}")
        while(time.time() < self.timer):
            if len(self.responses) == len(self.chats):
                break
        self.end = True
        # After this loop has complete or everyone has voted, gather the results 
        # and broadcast them.
        result = self.gather_result()
        if result == 1:
            message = "True"
        elif result == 0:
            message = "False"
        else:
            message = str(result)

        if not result:
            result = 0
        print(f"--------------------\n\nRESULT OF POLL\n{self.vote_id}\n{self.question} : {message}\n\n--------------------")
        self.vote_manager.broadcast_result(self.vote_id, result)
        return
        
        
class VoteManager:
    def __init__(self, chats, magic, sequence):
        self.chats = chats
        self.magic = magic
        self.sequence = sequence
        self.polls = {}

    # Direct the incoming packet to the appropriate location.
    def voting_main(self, received):
        # For a vote request.
        if received.vote_id == 2:
            # Start a new poll if the packet is of type 2, vote request.
            self.prepare_poll(received)
        # Or a response to a poll.
        elif received.vote_id == 4:
            self.add_vote(received)
    
    # Get the answer if the received message is a question.
    def prepare_poll(self, received):
        question = received.question
        answer = get_answer(question)

        if len(self.chats) >= 1:
            self.create_new_poll(answer, received)
            self.broadcast_vote(received)
        else:
            print(f"Not enough Clients to start a poll")

    # Add a vote to an existing poll.
    def add_vote(self, received):
        poll = self.polls[received.vote_id]
        poll.responses[received.client_id] = received.response

    # Create new poll after receiving a new question.
    def create_new_poll(self, answer, question_packet):
        # for key, value in self.chats.items():
        #     print("\n, key "\n")
        #     if 1 in value.features:
        #     self.voters[key] = value

        new_poll = poll(self.chats, question_packet, self)
        self.polls[question_packet.vote_id] = new_poll

    # Send out the question to all the clients involved.
    def broadcast_vote(self, received):
        for client in self.chats.values():
            id = client.client_id
            seq = client.sequence
            to_send = handlers.create_question_broadcast(self.magic, id, seq, 0, True, 0, received.vote_id, received.question)
            self.chats[id].chat_sender(to_send)
        
        print(f"Vote Broadcast Sent")

    # Send out the results of the vote to all the clients involved.
    def broadcast_result(self, vote_id, result):
        for client in self.chats.values():
            id = client.client_id
            seq = client.sequence
            to_send = handlers.create_result_broadcast(self.magic, id, seq, 0, True, 0, vote_id, result)
            self.chats[id].chat_sender(to_send)
        
        print(f"Vote {vote_id} Resulsts Dispersed")

#-----------------------------------------------------#

# Get the answer to the question using the eval function.
def get_answer(question):
    # Split the equation question at the equals sign.
    try:

        return eval(question.strip())
    
    except:
        print(f"No '=' present in equation")
        return 2


