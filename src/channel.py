import time
import threading

# Barebones packet struct
class Packet:
    def __init__(self,
                 seq_num: int,
                 payload: int,
                 is_ack: bool):
        self.seq_num = seq_num
        self.payload = payload
        self.is_ack = is_ack


class Channel:
    def __init__(self,
                 prop_delay:        float = 1.0,
                 data_seq_num_drops: list = [],
                 ack_seq_num_drops:  list = [],):
        self.prop_delay = prop_delay
        self.data_seq_num_drops = data_seq_num_drops
        self.ack_seq_num_drops = ack_seq_num_drops

    def transmit(self,
                 packet: Packet,
                 destination_callback):
        start = time.time()

        # Drop specified ack number once
        if (not packet.is_ack and packet.seq_num in self.data_seq_num_drops):
            self.data_seq_num_drops.remove(packet.seq_num)
            return
        
        # Drop specified sequence number once
        if (packet.is_ack and packet.seq_num in self.ack_seq_num_drops):
            self.ack_seq_num_drops.remove(packet.seq_num)
            return
        
        # Add artifical propogation delay
        delay = time.time() - start
        time.sleep(max(0, self.prop_delay - delay))
        thread = threading.Thread(target=destination_callback, args=(packet,), daemon=True)
        thread.start()

        

