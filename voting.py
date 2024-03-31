import threading
import time

class poll:
    def __init__(self, chats, question_packet, answer):
        self.vote_id = question_packet.vote_id
        self.respones = {}
        self.chats = chats
        self.end = False
        self.answer = answer

        self.result = 0
        global vote_manager 
        # Set the length of time of the poll.
        self.timer = time.time() + 5

        self.lock = threading.Lock()
        self.poll_timer_thread = threading.thread(target = self.poll_timer, )
        self.poll_timer_therad.start()

    def gather_result(self):
        yes = 0
        no = 0
        
        #for response in self.responses.values():


    def poll_timer(self):
        while(time.time() < self.timer):
            if len(self.responses) == len(self.chats):
                break
        self.end = True
        # After this loop has complete or everyone has voted, gather the results 
        # and broadcast them.
        result = self.gather_result()
        self.vote_manager.broadcast_result(self.vote_id, self.result)
        return
        
        
class VoteManager:
    def __init__(self, chats):
        self.chats = chats
        self.polls = {}

    def voting_main(self, received):
        # For a vote request.
        if received.vote_id == 2:
            self.prepare_poll(received)
        # Or a response to a poll.
        elif received.vote_id == 4:
            self.add_vote(received)
    
    # Get the answer if the received message is a question.
    def prepare_poll(self, received):
        question = received.question
        answer = eval(question)

        if len(self.chats) > 2:
            self.create_new_poll(self, answer, received)
        else:
            print(f"Not enough Clients to start a poll")

    # Add a vote to an existing poll.
    def add_vote(self, received):
        poll = self.polls[received.vote_id]
        poll.responses[received.client_id] = received.response

    # Create new poll after receiving a new question.
    def create_new_poll(self, answer, question_packet):
        new_poll = poll(self.chats, question_packet, answer)
        self.polls[question_packet.vote_id] = new_poll

