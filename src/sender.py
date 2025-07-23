import time
import threading
from PyQt5.QtCore import QTimer

from channel import Channel, Packet

class GBN_Sender:
    def __init__(self,
                 channel:   Channel,
                 window_size:   int = 5,
                 seq_num_space: int = 8,
                 timer_dur:   float = 3.0):
        self.window_size = window_size
        self.seq_num_space = seq_num_space
        self.timer_dur = timer_dur
        self.channel = channel

        self.base = 0               # next expected ack
        self.next_seq = 0           # next seq_num to be sent, usually the end of the window

        self.text_buffer = {}       # {time -> log message} map

    def connect_receiver(self,
                         receiver):
        self.receiver = receiver

    def send(self):
        while self.base < self.seq_num_space: # outer loop that will continue running until all packets are sent
            while self.next_seq < self.base + self.window_size and self.next_seq < self.seq_num_space: # inner loop that controls sliding window logic flow

                # Construct next packet to send
                packet = Packet(seq_num=self.next_seq,
                                payload=0,
                                is_ack=False)
                
                # Send it to the unreliable channel
                self.text_buffer[time.time()] = f"Sending packet {self.next_seq}"
                print(f"Sending packet {self.next_seq}")
                thread = threading.Thread(target=self.channel.transmit, args=(packet, self.receiver.receive_packet), daemon=True)
                thread.start()

                # Start the retransmission timer for this sequence number 
                thread = threading.Thread(target=self.start_timer, args=(self.next_seq,), daemon=True)
                thread.start()

                self.next_seq += 1
                time.sleep(0.1)

        self.text_buffer[time.time()] = f"All packets successfully delivered"
        print(f"All packets successfully delivered")

    def receive_ack(self,
                    ack: Packet):
        self.text_buffer[time.time()] = f"Received Ack {ack.seq_num}"
        print(f"Received Ack {ack.seq_num}")
        
        # If received ack is new, shift the base forward to unlock new sendable sequence numbers 
        if ack.seq_num >= self.base:
            self.base = ack.seq_num + 1

    def start_timer(self, 
                    seq: int):
        time.sleep(self.timer_dur)  # Timeout interval
        
        # If the base is equal to this sequence number when timer runs out, send retransmission signal by 
        #   resetting the next sequence number to the beginning of the window
        if self.base == seq:                 
            self.text_buffer[time.time()] = f"Timeout! Resending from seq {self.base}"
            print(f"Timeout! Resending from seq {self.base}")
            self.next_seq = self.base

    def get_text_buffer(self):
        return self.text_buffer

