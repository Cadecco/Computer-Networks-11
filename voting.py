import threading
import time

class poll:
    def __init__(self, chats, question_packet, answer, vote_manager):
        self.vote_id = question_packet.vote_id
        self.respones = {}
        self.chats = chats
        self.end = False
        self.answer = answer

        self.result = 0
        self.vote_manager = vote_manager
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

    # Get the answer if the received message is a question.
    def get_answer(self, received):
        question = received.decode()
        answer = eval(question)

        self.create_new_poll(self, answer, received)


    def add_vote(self, received):
        poll = self.polls[received.vote_id]
        poll.responses[received.client_id] = received.response

    def create_new_poll(self, answer, question_packet):
        new_poll = poll(self.chats, question_packet, answer, self)
        self.polls[question_packet.vote_id] = new_poll

