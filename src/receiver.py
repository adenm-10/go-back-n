from channel import Channel, Packet
from PyQt5.QtCore import QTimer
import time

class GBN_Receiver:
    def __init__(self,
                 channel: Channel,):
        self.cur_ack = 0        # The highest ack sent at any point in time
        self.channel = channel
        self.text_buffer = {}   # {time -> log message} map

    def connect_sender(self, 
                       sender):
        self.sender = sender

    def receive_packet(self, 
                       packet: Packet):
        self.text_buffer[time.time()] = f"Received Packet {packet.seq_num}"
        print(f"\t\t\t\tReceived Packet {packet.seq_num}")

        # If the received ack is the one we are expecting, increment current ack
        # Else, retransmit the same current ack we are waiting for, in accordance with Go-Back-N
        if (packet.seq_num == self.cur_ack): 
            self.cur_ack += 1

        # Construct ack
        ack = Packet(seq_num=self.cur_ack-1,
                     payload=0,
                     is_ack=True)

        # Send ack into unreliable channel
        self.text_buffer[time.time()] = f"Sending Ack {self.cur_ack-1}"
        print(f"\t\t\t\tSending Ack {self.cur_ack-1}")
        self.channel.transmit(packet=ack, 
                              destination_callback=self.sender.receive_ack)
        
    def get_text_buffer(self):
        return self.text_buffer