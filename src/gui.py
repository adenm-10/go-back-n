import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton
)

import time

from channel  import Channel
from receiver import GBN_Receiver
from sender   import GBN_Sender

class NetworkSimGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Go-Back-N Simulation")

        # Main window, and three sub columns:
        # 1. Input boxes
        # 2. Sender terminal output
        # 3. Receiver terminal output
        main_layout = QHBoxLayout()
        input_layout = QVBoxLayout()
        terminal1_layout = QVBoxLayout()
        terminal2_layout = QVBoxLayout()

        # Input parameter fields
        self.inputs = {}
        input_fields = {
            "Window Size": "Enter window size (int)",
            "Sequence Number Space": "Enter sequence number space (int)",
            "Timer Duration": "Enter timer duration (float)",
            "Propagation Delay": "Enter propagation delay (float)",
            "Data Sequence Number Drops": "e.g. 2,4,5",
            "ACK Sequence Number Drops": "e.g. 1,3"
        }

        # Input boxes for parameter fields
        for label, placeholder in input_fields.items():
            input_label = QLabel(label)
            input_box = QLineEdit()
            input_box.setPlaceholderText(placeholder)
            self.inputs[label] = input_box
            input_layout.addWidget(input_label)
            input_layout.addWidget(input_box)

        # Run simualtion button
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_simulation)
        input_layout.addWidget(run_button)

        # Sender terminal (1) output
        self.terminal1 = QTextEdit()
        self.terminal1.setReadOnly(True)
        self.terminal1.setPlaceholderText("Sender Terminal Output")
        terminal1_layout.addWidget(QLabel("Sender Terminal"))
        terminal1_layout.addWidget(self.terminal1)

        # Recever terminal (2) output
        self.terminal2 = QTextEdit()
        self.terminal2.setReadOnly(True)
        self.terminal2.setPlaceholderText("Receiver Terminal Output")
        terminal2_layout.addWidget(QLabel("Receiver Terminal"))
        terminal2_layout.addWidget(self.terminal2)

        # Main window organization
        main_layout.addLayout(input_layout)
        main_layout.addLayout(terminal1_layout)
        main_layout.addLayout(terminal2_layout)

        self.setLayout(main_layout)
        self.setMinimumSize(900, 400)

        self.log_receiver(f"[NOTE] Logs only print after full simulation, can be observed in real time in terminal")
        self.log_sender(f"[NOTE] Logs only print after full simulation, can be observed in real time in terminal")

    def run_simulation(self):

        # Text-based parameter input and parsing
        window_size   = self.inputs["Window Size"].text()
        seq_num_space = self.inputs["Sequence Number Space"].text()
        timer_dur     = self.inputs["Timer Duration"].text()
        prop_delay    = self.inputs["Propagation Delay"].text()
        
        window_size   = 5   if window_size   == "" else int(window_size)
        seq_num_space = 8   if seq_num_space == "" else int(seq_num_space)
        timer_dur     = 3.0 if timer_dur     == "" else float(timer_dur)
        prop_delay    = 1.0 if prop_delay    == "" else float(prop_delay)

        # Convert comma-separated string to list of ints
        data_drops = ''.join(self.inputs["Data Sequence Number Drops"].text().split())
        ack_drops  = ''.join(self.inputs["ACK Sequence Number Drops"].text().split())

        data_drops = [] if data_drops == "" else [
            int(x.strip())
            for x in data_drops.split(",")
            if x.strip().isdigit()
        ]

        ack_drops = [] if ack_drops == "" else [
            int(x.strip())
            for x in ack_drops.split(",")
            if x.strip().isdigit()
        ]

        self.log_sender(f"Window Size: {window_size}")
        self.log_sender(f"Seq Number Space: {seq_num_space}")
        self.log_sender(f"Timer: {timer_dur}") 
        self.log_sender(f"Propogation Delay: {prop_delay}")
        self.log_sender(f"Drops: Data={data_drops}")
        self.log_sender(f"ACK={ack_drops}")

        self.log_receiver(f"Window Size: {window_size}")
        self.log_receiver(f"Seq Number Space: {seq_num_space}")
        self.log_receiver(f"Timer: {timer_dur}") 
        self.log_receiver(f"Propogation Delay: {prop_delay}")
        self.log_receiver(f"Drops: Data={data_drops}")
        self.log_receiver(f"ACK={ack_drops}")

        # Set-up simulation
        channel = Channel(prop_delay=prop_delay,
                          data_seq_num_drops=data_drops,
                          ack_seq_num_drops=ack_drops)
        
        sender = GBN_Sender(channel=channel,
                            window_size=window_size,
                            seq_num_space=seq_num_space,
                            timer_dur=timer_dur)
        
        receiver = GBN_Receiver(channel=channel)
    
        sender.connect_receiver(receiver)
        receiver.connect_sender(sender)

        time.sleep(1.0)

        # Run simulation
        sender.send()

        # Receieve complete text logs
        sender_text = sender.get_text_buffer()
        receiver_text = receiver.get_text_buffer()

        sorted_sender = sorted(sender_text.keys())
        sorted_receiver = sorted(receiver_text.keys())
        index = 0

        # Print text logs in order of time
        while sorted_sender and sorted_receiver:
            if not sorted_receiver or sorted_sender[0] < sorted_receiver[0]:
                self.log_sender(f"({index}) {sender_text[sorted_sender[0]]}")
                self.log_receiver(f"({index})")
                sorted_sender.pop(0)
            else:
                self.log_receiver(f"({index}) {receiver_text[sorted_receiver[0]]}")
                self.log_sender(f"({index})")
                sorted_receiver.pop(0)
            index += 1

    def log_sender(self, message: str):
        self.terminal1.append(message)

    def log_receiver(self, message: str):
        self.terminal2.append(message)

def gui_main():
    app = QApplication(sys.argv)
    window = NetworkSimGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    gui_main()