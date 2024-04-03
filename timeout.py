import time
import threading
import handlers

class timeout:
    def __init__(self, addr, seq_num, ack_packets, sent_packets, socket):
        self.seq_num = seq_num
        self.exceptions = 0

        self.socket = socket
        self.ack_packets = ack_packets
        self.sent_packets = sent_packets
        self.addr = addr

        self.timer = time.time() + 3
        self.lock = threading.Lock()
        self.timeout_thread = threading.Thread(target=self.timeout_loop, )
        self.timeout_thread.start()

    def timeout_loop(self):
        for x in range(3):
            self.timer = time.time() + 3
            while (time.time() < self.timer):
                    self.lock.acquire()
                    received = self.ack_packets.get(self.seq_num)
                    self.lock.release()
                    #print(f"{received}")
                    if received:
                        return
            handlers.resend(self.socket, self.addr, self.sent_packets, self.sent_packets[self.seq_num])
        return
